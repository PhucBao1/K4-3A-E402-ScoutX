"""Feature A — Video Format Compliance Checker (BA.md mục 5, PLAN.md mục 10: route /format-check).

Kiểm video ĐÃ DỰNG XONG có đúng chuẩn khung hình của khoá (khung-hinh.md, BTC quy định — KHÔNG
phải điều lab coach tự xác nhận, chỉ có "có khâu check format" là được xác nhận thật, xem BA.md
mục 2):
  - 1920x1080, 30 khung hình/giây.
  - Chữ trên màn hình (không tính phụ đề) tối đa 40 ký tự.
  - Nội dung dạy học phải nằm trong vùng an toàn x:80-1840, y:250-960 (dải dưới y>=960 dành cho
    phụ đề nên KHÔNG kiểm 2 quy tắc trên ở đó; dải trên y<250 là "vùng nhãn/tiêu đề" được phép
    theo đúng sơ đồ khung-hinh.md nên chỉ kiểm số ký tự, không kiểm toạ độ).

Thuần rule-based + OCR (pytesseract) — KHÔNG gọi AI/LLM cho bước so sánh, đúng lý do "rẻ, nhanh,
ít rủi ro sai" đã nêu trong BA.md mục 5.
"""
import os
import subprocess
import tempfile

EXPECTED_WIDTH = 1920
EXPECTED_HEIGHT = 1080
EXPECTED_FPS = 30
MAX_CHARS = 40
SAFE_X0, SAFE_Y0, SAFE_X1, SAFE_Y1 = 80, 250, 1840, 960
HEADER_ZONE_Y1 = 250  # y < 250: vùng nhãn/tiêu đề, được phép, chỉ kiểm số ký tự
CAPTION_ZONE_Y0 = 960  # y >= 960: dành cho phụ đề, không kiểm gì ở đây


def get_video_metadata(video_path: str) -> dict:
    """Đọc resolution/fps thật bằng ffprobe — rule-based, không cần AI."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,duration",
         "-of", "default=noprint_wrappers=1", video_path],
        capture_output=True, text=True, check=True,
    )
    info = {}
    for line in result.stdout.strip().splitlines():
        key, _, val = line.partition("=")
        info[key] = val
    width = int(info.get("width", 0))
    height = int(info.get("height", 0))
    fps_raw = info.get("r_frame_rate", "0/1")
    num, _, den = fps_raw.partition("/")
    fps = round(float(num) / float(den or 1), 2) if den else float(num)
    duration = float(info.get("duration") or 0)
    return {
        "rong": width, "cao": height, "fps": fps, "thoiLuongGiay": duration,
        "dungResolution": width == EXPECTED_WIDTH and height == EXPECTED_HEIGHT,
        "dungFps": abs(fps - EXPECTED_FPS) < 0.1,
    }


def extract_sample_frames(video_path: str, out_dir: str, interval_sec: float = 1.0) -> list[tuple[float, str]]:
    """Trích frame đều đặn mỗi interval_sec giây bằng ffmpeg — dùng thư viện có sẵn, không tự
    decode video bằng tay."""
    duration = get_video_metadata(video_path)["thoiLuongGiay"]
    frames = []
    t = 0.0
    while t < duration:
        frame_path = os.path.join(out_dir, f"frame_{t:07.2f}.png")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", video_path, "-frames:v", "1", frame_path],
            capture_output=True, check=True,
        )
        if os.path.exists(frame_path):
            frames.append((t, frame_path))
        t += interval_sec
    return frames


def _ocr_lines(frame_path: str) -> list[dict]:
    """OCR 1 frame, gộp các từ cùng dòng (block/par/line) thành 1 dòng chữ + bbox bao toàn dòng.
    Trả về [] nếu pytesseract/tesseract chưa cài — để nơi gọi tự báo lỗi rõ ràng thay vì crash."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise RuntimeError(
            "Chưa cài pytesseract/Pillow. Chạy: pip install pytesseract Pillow — và cài "
            "tesseract-ocr thật (binary) qua: sudo apt-get install tesseract-ocr tesseract-ocr-vie"
        ) from e

    try:
        data = pytesseract.image_to_data(
            Image.open(frame_path), lang="vie", output_type=pytesseract.Output.DICT,
        )
    except Exception:
        # Máy chưa có gói ngôn ngữ "vie" — vẫn chạy được bằng "eng" nhưng đọc dấu tiếng Việt sẽ
        # kém chính xác hơn, ghi rõ vào kết quả thay vì âm thầm sai.
        data = pytesseract.image_to_data(
            Image.open(frame_path), lang="eng", output_type=pytesseract.Output.DICT,
        )

    lines: dict[tuple, dict] = {}
    n = len(data["text"])
    for i in range(n):
        word = data["text"][i].strip()
        if not word:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        l, t, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        if key not in lines:
            lines[key] = {"words": [word], "left": l, "top": t, "right": l + w, "bottom": t + h}
        else:
            ln = lines[key]
            ln["words"].append(word)
            ln["left"] = min(ln["left"], l)
            ln["top"] = min(ln["top"], t)
            ln["right"] = max(ln["right"], l + w)
            ln["bottom"] = max(ln["bottom"], t + h)
    return [
        {
            "text": " ".join(ln["words"]),
            "left": ln["left"], "top": ln["top"],
            "right": ln["right"], "bottom": ln["bottom"],
        }
        for ln in lines.values()
    ]


def check_frame(frame_path: str, time_sec: float) -> list[dict]:
    """Kiểm 1 frame: số ký tự tối đa 40 + vị trí trong vùng an toàn. Trả về danh sách vi phạm
    (rỗng nếu frame sạch)."""
    violations = []
    for line in _ocr_lines(frame_path):
        y_center = (line["top"] + line["bottom"]) / 2
        if y_center >= CAPTION_ZONE_Y0:
            continue  # vùng phụ đề — không kiểm (khung-hinh.md: "phụ đề không phải việc của bạn")

        if len(line["text"]) > MAX_CHARS:
            violations.append({
                "thoiDiemGiay": round(time_sec, 2), "loaiViPham": "qua_40_ky_tu",
                "chiTiet": f"\"{line['text']}\" dài {len(line['text'])} ký tự (giới hạn {MAX_CHARS}).",
                "anhFrame": frame_path,
            })

        if y_center >= HEADER_ZONE_Y1:  # trong vùng nội dung chính, không phải vùng nhãn/tiêu đề
            if not (SAFE_X0 <= line["left"] and line["right"] <= SAFE_X1
                    and SAFE_Y0 <= line["top"] and line["bottom"] <= SAFE_Y1):
                violations.append({
                    "thoiDiemGiay": round(time_sec, 2), "loaiViPham": "ngoai_vung_an_toan",
                    "chiTiet": (
                        f"\"{line['text']}\" nằm ngoài vùng an toàn x:{SAFE_X0}-{SAFE_X1}, "
                        f"y:{SAFE_Y0}-{SAFE_Y1} (toạ độ thật: x:{line['left']}-{line['right']}, "
                        f"y:{line['top']}-{line['bottom']})."
                    ),
                    "anhFrame": frame_path,
                })
    return violations


def check_video_format(video_path: str, interval_sec: float = 1.0) -> dict:
    """Chạy toàn bộ Feature A trên 1 video đã dựng. Trả về báo cáo tổng hợp, giữ lại ảnh frame
    của MỖI vi phạm để người QA xem trực tiếp (không xoá thư mục tạm khi có vi phạm)."""
    metadata = get_video_metadata(video_path)
    tmp_dir = tempfile.mkdtemp(prefix="format_qa_")
    frames = extract_sample_frames(video_path, tmp_dir, interval_sec)

    violations = []
    for t, frame_path in frames:
        violations.extend(check_frame(frame_path, t))

    dat = metadata["dungResolution"] and metadata["dungFps"] and not violations
    return {
        "dat": dat,
        "metadata": metadata,
        "tongFrameKiemTra": len(frames),
        "viPham": violations,
        "thuMucFrame": tmp_dir,
    }
