import base64
import json
import os
import re

import pymupdf as fitz  # PyMuPDF
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

from prompt import (
    JUDGE_RELEVANCE_PROMPT,
    PROMPT_TEMPLATE,
    RETRY_SUFFIX,
    REWRITE_PROMPT_TEMPLATE,
    REWRITE_RETRY_SUFFIX,
    WEB_SEARCH_PROMPT,
)

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
app = FastAPI()

MAX_PAGES = 40  # đã test: slide thật(xem PLAN.md mục 6a)


def estimate_target_sentences(duration_minutes: int) -> int:
    """Theo mau-kich-ban.md: ~2,9 âm tiết/giây, 1 câu ~20 âm tiết ≈ 7 giây/câu. Phát hiện thật: kịch
    bản 4-5 câu không thể nào đủ 4 phút — prompt trước đó không hề tính số câu cần theo thời lượng."""
    return max(4, round(duration_minutes * 60 / 7))


MAX_MB = 15  # TBD — tương tự


def load_pdf(pdf_bytes: bytes) -> "fitz.Document":
    size_mb = len(pdf_bytes) / (1024 * 1024)
    if size_mb > MAX_MB:
        raise HTTPException(status_code=400, detail=f"File quá {MAX_MB}MB, không xử lý")
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        raise HTTPException(status_code=400, detail="File PDF không đọc được")
    if doc.page_count > MAX_PAGES:
        raise HTTPException(status_code=400, detail=f"File quá {MAX_PAGES} trang, không xử lý")
    return doc


def pdf_to_images_base64(doc: "fitz.Document", dpi: int = 100) -> list[str]:
    """Ảnh chỉ dùng làm NGỮ CẢNH THỊ GIÁC (bố cục/sơ đồ) cho "yDoHinh" — KHÔNG dùng để trích
    dẫn (đó là việc của text, xem extract_pdf_text). Luôn gửi kèm "detail": "low" khi gọi API
    (main.py call_openai) — ảnh "low" bị hạ về độ phân giải cố định, chi phí token nhỏ và CỐ
    ĐỊNH bất kể số trang, tránh lặp lại rate limit 200k TPM đã gặp khi test case 1 (do trước
    đó gửi ảnh "high" 150dpi, không set detail, tốn token tỉ lệ theo kích thước ảnh)."""
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        images.append(base64.b64encode(pix.tobytes("png")).decode())
    return images


def extract_pdf_text(doc: "fitz.Document") -> str:
    """Text trích xuất — NGUỒN SỰ THẬT DUY NHẤT để AI trích dẫn (xem prompt.py). Cũng dùng để
    tự động đối chiếu chặn bịa số liệu ở Layer 4 của validate_output() — xem case 1 trong
    eval/golden-set.md, nơi AI từng tự chế "40%" không hề có trên slide."""
    pages = []
    for i, page in enumerate(doc, start=1):
        pages.append(f"--- Trang {i} ---\n{page.get_text()}")
    return "\n\n".join(pages)


def search_web_sources(goal: str) -> str:
    """Tìm 2-3 nguồn ngoài liên quan tới mục tiêu bài học, dùng OpenAI Responses API +
    tool "web_search_preview" (cùng key hiện có, không cần API tìm kiếm riêng). Trả về TEXT
    thô (không phải JSON) — dùng làm khối "nguồn sự thật bổ sung" y hệt cách slide_text đang
    được dùng, để tái dùng toàn bộ validate_output() có sẵn mà không cần sửa gì thêm.

    Bọc try/except: nếu web search lỗi (mất mạng, quota, API đổi...), KHÔNG được chặn cả luồng
    chính — vẫn phải viết được kịch bản chỉ từ slide, đúng non-goal cũ vẫn còn giá trị làm
    phương án dự phòng."""
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            tools=[{"type": "web_search_preview"}],
            input=WEB_SEARCH_PROMPT.format(goal=goal),
        )
        return resp.output_text or ""
    except Exception:
        return ""  # không tìm được nguồn ngoài — prompt.py đã có câu dự phòng cho trường hợp này


NUMBER_PATTERN = re.compile(r"\d[\d.,]*\s*%?")
LEAD_IN_PREFIX = re.compile(r"^(Ví dụ|VD|Ghi chú|Lưu ý)\s*[:\-]\s*", re.IGNORECASE)


def _normalize_ws(s: str) -> str:
    """Chuẩn hoá để so khớp: gộp khoảng trắng/xuống dòng, bỏ dấu câu cuối câu AI hay tự thêm
    (source PDF thường ngắt dòng thay vì chấm câu — không phải dấu hiệu bịa nội dung)."""
    s = re.sub(r"\s+", " ", s or "").strip()
    return s.rstrip(".!?,;:")


def find_ungrounded_numbers(data: dict, source_text: str) -> list[str]:
    """Layer 4 — CHẶT HƠN bản đầu. Bản đầu chỉ kiểm số có xuất hiện ĐÂU ĐÓ trong cả tài liệu
    (dễ trùng ngẫu nhiên với văn bản dài — case 2 trong golden-set.md: AI bịa "công ty VN tiết
    kiệm 40% chi phí", gắn citation vào 1 thongTin THẬT nhưng nói chuyện khác (rút ngắn 90→30
    phút); "40%" tình cờ có thật ở TRANG KHÁC không liên quan nên lọt qua bản kiểm cũ).

    Bản này kiểm ĐÚNG NGỮ CẢNH: số liệu trong 1 câu phải xuất hiện trong chính đoạn "bangChung"
    mà câu đó trích dẫn — không phải chỉ cần có thật ở đâu đó trong tài liệu."""
    ho_so = data.get("hoSo", {})
    thongtin_by_id = {t["id"]: t for t in ho_so.get("thongTin", [])}
    source_loai_by_id = {s["id"]: s.get("loai") for s in ho_so.get("nguon", [])}
    norm_source = _normalize_ws(source_text)

    problems = []

    # Layer 4a — bắt buộc khớp nguyên văn khi đoạn trích có chứa SỐ LIỆU (rủi ro thật nằm ở số
    # bịa — case 1, 2), HOẶC khi nguồn trích là "web" (web_text có sẵn đầy đủ, không có rủi ro
    # false positive do slide ngắt dòng — phát hiện thật: chế độ không-slide để AI tự tìm nguồn,
    # AI từng gắn "doanTrich" hoàn toàn bịa, không liên quan gì tới nội dung thật của URL, cho một
    # nguồn web — không số nên lọt qua bản kiểm cũ). Đoạn trích thuần diễn giải khái niệm từ SLIDE
    # (không số) vẫn được nới lỏng vì test thật cho thấy AI hay nối 2 dòng slide bằng dấu chấm
    # (source ngắt dòng, không chấm câu) → false positive nếu bắt khớp tuyệt đối mọi đoạn trích.
    for t in ho_so.get("thongTin", []):
        for bc in t.get("bangChung", []):
            raw = bc.get("doanTrich", "") or ""
            is_web = source_loai_by_id.get(bc.get("nguonId")) == "web"
            if not NUMBER_PATTERN.search(raw) and not is_web:
                continue  # không có số, và không phải nguồn web → rủi ro thấp, không bắt buộc khớp tuyệt đối
            doan_trich = _normalize_ws(LEAD_IN_PREFIX.sub("", raw))
            if len(doan_trich) >= 4 and doan_trich not in norm_source:
                problems.append(f"thongTin {t.get('id')} trích dẫn không khớp text gốc (nguồn {'web' if is_web else 'slide'}): \"{doan_trich[:60]}...\"")

    # Layer 4b — số liệu trong LỜI ĐỌC của câu phải nằm trong đúng "doanTrich" mà câu đó trích
    # dẫn (không phải "noiDung" — vì noiDung là AI tự diễn giải, có thể lẫn số bịa vào đó)
    for cau in data.get("kichBan", {}).get("cau", []):
        loi = cau.get("loi", "") or ""
        # .rstrip(",.") — regex bắt số hay dính dấu phẩy/chấm cuối câu ("2017," thay vì "2017"),
        # phát hiện thật khi test case 9 (mốc lịch sử) khiến so khớp sai hàng loạt vì lỗi này
        numbers = {n.strip().rstrip(",.") for n in NUMBER_PATTERN.findall(loi)}
        numbers = {n for n in numbers if len(n) >= 2}
        if not numbers:
            continue

        cited_evidence = ""
        for tid in _as_list(cau.get("nguon")):
            t = thongtin_by_id.get(tid)
            if not t:
                continue
            for bc in t.get("bangChung", []):
                cited_evidence += " " + (bc.get("doanTrich", "") or "")
        cited_evidence = _normalize_ws(cited_evidence)

        for num in numbers:
            if num not in cited_evidence:
                problems.append(
                    f"Câu {cau.get('n')} nói số '{num}' nhưng đoạn trích dẫn của câu đó không có số này"
                )
    return problems


def call_openai(prompt_text: str, images_b64: list[str]) -> dict:
    content = [{"type": "text", "text": prompt_text}]
    for img in images_b64:
        # "detail": "low" — ảnh bị hạ về độ phân giải cố định trước khi tính token, chi phí
        # nhỏ và KHÔNG tỉ lệ theo kích thước ảnh gốc. Đây là điều đã thiếu ở lần chạy trước
        # (gửi ảnh 150dpi không set detail) và trực tiếp gây rate limit 200k TPM khi test.
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}", "detail": "low"}
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise HTTPException(status_code=429, detail=f"Không gọi được AI: {e}")

    return json.loads(response.choices[0].message.content)


def _as_list(value):
    """Guard: model đôi khi trả 'nguon': 't01' (string) thay vì ['t01'] (list).
    Nếu lặp thẳng qua string sẽ ra từng ký tự — chặn ở đây trước khi validate."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return value


def validate_output(data: dict, source_text: str) -> None:
    """4 lớp kiểm tra — raise ValueError nếu hỏng. JSON hợp lệ cú pháp KHÔNG có nghĩa
    là kịch bản đáng tin — đây là chỗ bảo vệ đúng tiêu chí nặng nhất của rubric C3
    (25%: "câu truy được về nguồn và trích dẫn chính xác"). Layer 4 (số liệu) thêm sau
    case 1 (AI bịa "40%"), rồi SIẾT LẠI sau case 2 (AI gắn citation thật vào câu nói
    chuyện khác, "40%" tình cờ có thật ở trang khác không liên quan) — xem
    eval/golden-set.md."""
    if "hoSo" not in data or "kichBan" not in data:
        raise ValueError("Thiếu khối hoSo hoặc kichBan")

    ho_so = data["hoSo"]
    kich_ban = data["kichBan"]

    source_ids = {s["id"] for s in ho_so.get("nguon", [])}
    thongtin_ids = {t["id"] for t in ho_so.get("thongTin", [])}

    # Layer 2 — referential integrity: mỗi bangChung.nguonId phải trỏ đúng 1 nguồn có thật
    for t in ho_so.get("thongTin", []):
        for bc in t.get("bangChung", []):
            if bc.get("nguonId") not in source_ids:
                raise ValueError(f"thongTin {t.get('id')} trỏ tới nguonId không tồn tại: {bc.get('nguonId')}")

    # Layer 3 — citation traceability: mỗi câu có "nguon" phải trỏ đúng 1 thongTin có thật
    for cau in kich_ban.get("cau", []):
        for nguon_id in _as_list(cau.get("nguon")):
            if nguon_id not in thongtin_ids:
                raise ValueError(f"Câu {cau.get('n')} trỏ tới thongTin không tồn tại: {nguon_id}")

    # Layer 4 — số liệu phải có thật trong slide (không chỉ có ID trích dẫn hợp lệ)
    ungrounded = find_ungrounded_numbers(data, source_text)
    if ungrounded:
        raise ValueError(f"Số liệu có thể bị bịa, không tìm thấy trong slide gốc: {ungrounded}")

    # Layer 5 — "soNguonXacNhan" (đối chiếu chéo slide/web, đúng chỗ khó nhất của đề C3 gốc:
    # "số liệu quan trọng cần ít nhất 2 nguồn độc lập xác nhận") không được TỰ NHẬN cao hơn số
    # nguồn ĐỘC LẬP thật sự có trong bangChung — chỉ kiểm khi trường này có mặt (không bắt buộc,
    # vì patch từ /rewrite có thể không kèm trường này).
    for t in ho_so.get("thongTin", []):
        so_nguon_xac_nhan = t.get("soNguonXacNhan")
        if so_nguon_xac_nhan is None:
            continue
        distinct_sources = {bc.get("nguonId") for bc in t.get("bangChung", [])}
        if so_nguon_xac_nhan > len(distinct_sources):
            raise ValueError(
                f"thongTin {t.get('id')} tự nhận soNguonXacNhan={so_nguon_xac_nhan} nhưng chỉ có "
                f"{len(distinct_sources)} nguồn độc lập thật sự trong bangChung — có thể khai khống mức xác minh"
            )

    # Layer 6 — "loi" (lời đọc) không được chứa chữ số, theo đúng mau-kich-ban.md của BTC
    # ("Không có chữ số" — máy đọc từng ký tự, số phải viết bằng chữ). "chuTrenManHinh" không bị
    # ràng buộc này.
    for cau in kich_ban.get("cau", []):
        loi = cau.get("loi")
        if loi and re.search(r"\d", loi):
            raise ValueError(f"Câu {cau.get('n')} có chữ số trong 'loi' (phải viết bằng chữ): {loi!r}")


def check_citation_relevance(data: dict) -> list[str]:
    """Layer 7 — kiểm ngữ nghĩa: "doanTrich" tồn tại thật trong nguồn (Layer 4a) không có nghĩa nó
    THỰC SỰ xác nhận đúng "noiDung" đang gắn vào. Phát hiện thật: khi 2 nguồn nói khác nhau về cùng
    1 sự kiện (vd năm ImageNet ra đời), AI từng gắn thêm 2 trích dẫn CÓ THẬT nhưng nói chuyện khác
    (AlexNet 2012, 1 câu tiếng Anh chung chung) làm "bằng chứng phụ" để tự nâng khống soNguonXacNhan
    lên "da-xac-minh" — không lớp nào trước đó bắt được vì trích dẫn không bịa, chỉ là không liên
    quan. Dùng 1 lượt AI riêng, độc lập, để chấm độ liên quan thật của từng cặp thongTin-bangChung."""
    ho_so = data.get("hoSo", {})
    pairs = []
    for t in ho_so.get("thongTin", []):
        for i, bc in enumerate(t.get("bangChung", [])):
            pairs.append({
                "thongTinId": t.get("id"), "noiDung": t.get("noiDung", ""),
                "index": i, "doanTrich": bc.get("doanTrich", ""),
            })
    if not pairs:
        return []

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": JUDGE_RELEVANCE_PROMPT.format(
                pairs_json=json.dumps(pairs, ensure_ascii=False))}],
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
    except Exception:
        return []  # judge lỗi thì bỏ qua, không chặn luồng chính — tránh single point of failure

    irrelevant = {(r.get("thongTinId"), r.get("index")) for r in result.get("khongLienQuan", [])}
    if not irrelevant:
        return []

    problems = []
    for t in ho_so.get("thongTin", []):
        bc_list = t.get("bangChung", [])
        remaining = {bc.get("nguonId") for i, bc in enumerate(bc_list) if (t.get("id"), i) not in irrelevant}
        declared = t.get("soNguonXacNhan")
        flagged = [i for i in range(len(bc_list)) if (t.get("id"), i) in irrelevant]
        if not flagged:
            continue
        if declared is not None and declared > len(remaining):
            problems.append(
                f"thongTin {t.get('id')}: trích dẫn tại index {flagged} bị chấm KHÔNG thực sự liên quan "
                f"tới nội dung '{t.get('noiDung', '')[:50]}...' nhưng vẫn tính vào soNguonXacNhan={declared}"
            )
        elif declared is None:
            problems.append(
                f"thongTin {t.get('id')}: trích dẫn tại index {flagged} không thực sự liên quan tới nội "
                f"dung '{t.get('noiDung', '')[:50]}...'"
            )
    return problems


@app.post("/generate")
async def generate(
    topic: str = Form(...),
    goal: str = Form(...),
    audience: str = Form(...),
    duration: int = Form(...),
    file: UploadFile | None = File(None),
):
    # Đúng bài toán gốc C3: input chỉ cần chủ đề/mục tiêu/đối tượng/thời lượng, KHÔNG bắt buộc đưa
    # sẵn tài liệu — slide là tuỳ chọn để bổ sung, không phải điều kiện bắt buộc để chạy.
    if file is not None:
        pdf_bytes = await file.read()
        doc = load_pdf(pdf_bytes)  # tự raise HTTPException nếu vượt giới hạn trang/dung lượng
        source_text = extract_pdf_text(doc)
        images_b64 = pdf_to_images_base64(doc)  # ảnh "low detail" — chỉ để hiểu bố cục/sơ đồ, không để trích dẫn
    else:
        source_text = ""
        images_b64 = []
    web_text = search_web_sources(f"{topic}. {goal}")  # đúng lát cắt gợi ý BTC: "AI tìm 3 nguồn, chấm tin cậy"
    all_source_text = source_text + "\n\n" + web_text  # dùng chung cho validate_output() Layer 4

    prompt_text = PROMPT_TEMPLATE.format(
        topic=topic, goal=goal, audience=audience, duration=duration,
        target_sentences=estimate_target_sentences(duration),
        slide_text=source_text or "(người dùng không upload slide — dùng nguồn mạng làm nguồn chính)",
        web_text=web_text or "(không tìm được nguồn ngoài, chỉ dùng slide)",
    )

    # 3 lần thử (không phải 2) — test thật cho thấy lỗi ID không khớp (nguonId trong bangChung
    # không có trong mảng nguon) xảy ra khá thường xuyên từ khi prompt phức tạp hơn (thêm web +
    # đối chiếu chéo), 2 lần retry cho tỷ lệ thành công ổn định hơn.
    last_error = None
    for attempt_prompt in (prompt_text, prompt_text + RETRY_SUFFIX, prompt_text + RETRY_SUFFIX):
        try:
            data = call_openai(attempt_prompt, images_b64)
            validate_output(data, all_source_text)
            relevance_problems = check_citation_relevance(data)
            if relevance_problems:
                raise ValueError(f"Trích dẫn không thực sự liên quan tới nội dung: {relevance_problems}")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            continue

    raise HTTPException(status_code=502, detail=f"AI_INVALID_JSON: {last_error}")


@app.post("/add-source")
async def add_source(
    topic: str = Form(...),
    goal: str = Form(...),
    audience: str = Form(...),
    duration: int = Form(...),
    source_url: str = Form(...),
    source_title: str = Form(...),
    source_excerpt: str = Form(...),
    source_org: str = Form(""),
    source_date: str = Form(""),
    file: UploadFile | None = File(None),
):
    """Đúng "Sản phẩm tối thiểu" C3: màn hình duyệt nguồn phải cho "thêm nguồn của mình". Người dùng
    tự dán URL + đoạn trích (không tự động cào trang — không có tầng fetch riêng), AI viết lại kịch
    bản với nguồn này được ép buộc đưa vào cùng slide/web như một nguồn thật, qua lại đúng validate
    đã test kỹ ở /generate thay vì viết logic vá riêng rủi ro hơn."""
    if file is not None:
        pdf_bytes = await file.read()
        doc = load_pdf(pdf_bytes)
        source_text = extract_pdf_text(doc)
        images_b64 = pdf_to_images_base64(doc)
    else:
        source_text = ""
        images_b64 = []
    web_text = search_web_sources(f"{topic}. {goal}")
    user_source_block = (
        "\n\n--- NGUỒN NGƯỜI DÙNG TỰ THÊM (coi như 1 nguồn web bình thường) ---\n"
        f"URL: {source_url}\nTiêu đề: {source_title}\nTác giả/Tổ chức: {source_org or 'không rõ'}\n"
        f"Ngày đăng: {source_date or 'không rõ'}\n"
        f"Trích dẫn: {source_excerpt}\n--- HẾT NGUỒN NGƯỜI DÙNG TỰ THÊM ---"
    )
    web_text_combined = (web_text or "") + user_source_block
    all_source_text = source_text + "\n\n" + web_text_combined

    prompt_text = PROMPT_TEMPLATE.format(
        topic=topic, goal=goal, audience=audience, duration=duration,
        target_sentences=estimate_target_sentences(duration),
        slide_text=source_text or "(người dùng không upload slide — dùng nguồn mạng làm nguồn chính)",
        web_text=web_text_combined,
    ) + (
        "\n\nLƯU Ý: khối NGUỒN TÌM ĐƯỢC TRÊN MẠNG có 1 đoạn đánh dấu '--- NGUỒN NGƯỜI DÙNG TỰ THÊM ---' — "
        "đây là nguồn người dùng tự cung cấp, hãy coi như một nguồn web bình thường và dùng nếu liên quan "
        "tới chủ đề, không được bỏ qua chỉ vì nó không do bạn tự tìm."
    )

    last_error = None
    for attempt_prompt in (prompt_text, prompt_text + RETRY_SUFFIX, prompt_text + RETRY_SUFFIX):
        try:
            data = call_openai(attempt_prompt, images_b64)
            validate_output(data, all_source_text)
            relevance_problems = check_citation_relevance(data)
            if relevance_problems:
                raise ValueError(f"Trích dẫn không thực sự liên quan tới nội dung: {relevance_problems}")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            continue

    raise HTTPException(status_code=502, detail=f"AI_INVALID_JSON: {last_error}")


@app.post("/rewrite")
async def rewrite(
    topic: str = Form(...),
    goal: str = Form(...),
    audience: str = Form(...),
    duration: int = Form(...),
    ho_so_json: str = Form(...),
    kich_ban_json: str = Form(...),
    removed_source_id: str = Form(...),
    file: UploadFile | None = File(None),
):
    """Đúng lát cắt gợi ý BTC: "người viết loại một nguồn → chỉ câu phụ thuộc viết lại".
    Chỉ viết lại đúng các câu phụ thuộc vào nguồn bị loại, giữ nguyên các câu khác — không phải
    chạy lại toàn bộ /generate (đó là hành vi "Correction" đã tự khai thiếu trong spec.md §6,
    giờ bù lại)."""
    ho_so = json.loads(ho_so_json)
    kich_ban = json.loads(kich_ban_json)

    affected_thongtin_ids = {
        t["id"] for t in ho_so.get("thongTin", [])
        if any(bc.get("nguonId") == removed_source_id for bc in t.get("bangChung", []))
    }
    remaining_ho_so = {
        "nguon": [s for s in ho_so.get("nguon", []) if s["id"] != removed_source_id],
        "thongTin": [t for t in ho_so.get("thongTin", []) if t["id"] not in affected_thongtin_ids],
    }
    affected_cau = [
        c for c in kich_ban.get("cau", [])
        if any(nid in affected_thongtin_ids for nid in _as_list(c.get("nguon")))
    ]

    if not affected_cau:
        # không câu nào phụ thuộc nguồn bị loại — chỉ cần bỏ nguồn khỏi hồ sơ, kịch bản giữ nguyên
        return {"hoSo": remaining_ho_so, "kichBan": kich_ban, "rewrittenNs": []}

    if file is not None:
        pdf_bytes = await file.read()
        doc = load_pdf(pdf_bytes)
        source_text = extract_pdf_text(doc)
        images_b64 = pdf_to_images_base64(doc)
    else:
        source_text = ""
        images_b64 = []
    web_text = search_web_sources(f"{topic}. {goal}")
    all_source_text = source_text + "\n\n" + web_text

    rewrite_prompt = REWRITE_PROMPT_TEMPLATE.format(
        topic=topic, goal=goal, audience=audience, duration=duration,
        slide_text=source_text or "(không có slide — dùng nguồn mạng làm nguồn chính)",
        web_text=web_text or "(không tìm được nguồn ngoài)",
        removed_source_id=removed_source_id,
        remaining_ho_so=json.dumps(remaining_ho_so, ensure_ascii=False),
        affected_sentences=json.dumps(affected_cau, ensure_ascii=False),
    )

    last_error = None
    for attempt_prompt in (rewrite_prompt, rewrite_prompt + REWRITE_RETRY_SUFFIX):
        try:
            patch = call_openai(attempt_prompt, images_b64)

            # Chặn ID trùng — bug thật đã gặp: AI đặt "thongTinMoi" trùng id với thongTin còn
            # lại (vd cả 2 đều "tt2"), làm hồ sơ có 2 bản ghi cùng id khác nội dung, hỏng dữ liệu
            existing_source_ids = {s["id"] for s in remaining_ho_so["nguon"]}
            existing_thongtin_ids = {t["id"] for t in remaining_ho_so["thongTin"]}
            for s in patch.get("nguonMoi", []):
                if s["id"] in existing_source_ids:
                    raise ValueError(f"nguonMoi id '{s['id']}' trùng với nguồn đã có sẵn")
            for t in patch.get("thongTinMoi", []):
                if t["id"] in existing_thongtin_ids:
                    raise ValueError(f"thongTinMoi id '{t['id']}' trùng với thongTin đã có sẵn")

            new_ho_so = {
                "nguon": remaining_ho_so["nguon"] + patch.get("nguonMoi", []),
                "thongTin": remaining_ho_so["thongTin"] + patch.get("thongTinMoi", []),
            }
            cau_by_n = {c["n"]: c for c in kich_ban.get("cau", [])}
            affected_ns = {c["n"] for c in affected_cau}
            for c in patch.get("cauVietLai", []):
                cau_by_n[c["n"]] = c
            new_kich_ban = dict(kich_ban)
            new_kich_ban["cau"] = [cau_by_n[n] for n in sorted(cau_by_n)]

            merged_data = {"hoSo": new_ho_so, "kichBan": new_kich_ban}
            validate_output(merged_data, all_source_text)
            relevance_problems = check_citation_relevance(merged_data)
            if relevance_problems:
                raise ValueError(f"Trích dẫn không thực sự liên quan tới nội dung: {relevance_problems}")
            return {"hoSo": new_ho_so, "kichBan": new_kich_ban, "rewrittenNs": sorted(affected_ns)}
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            last_error = e
            continue

    raise HTTPException(status_code=502, detail=f"AI_INVALID_JSON: {last_error}")


# Static files (frontend) — MOUNT SAU CÙNG, sau mọi route API, để không nuốt mất /generate
app.mount("/", StaticFiles(directory="static", html=True), name="static")
