# ScriptScout backend

Agent tự tìm tài liệu và viết kịch bản video bài giảng có dẫn nguồn (đề C3). Chi tiết đầy đủ về thiết kế,
bằng chứng, golden set: xem `spec.md` và `eval/golden-set.md` ở gốc repo.

## Cách chạy

```bash
cd codebase/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền OPENAI_API_KEY thật vào .env
uvicorn main:app --port 8000
```

Mở `http://localhost:8000` — nhập **Chủ đề** (bắt buộc), slide PDF là **tuỳ chọn**. Không có slide thì AI
tự tìm nguồn trên mạng để viết toàn bộ kịch bản, đúng cơ chế đề gốc yêu cầu.

## Các endpoint

| Endpoint | Việc gì |
|---|---|
| `POST /generate` | Sinh hồ sơ tài liệu + kịch bản từ đầu (chủ đề, mục tiêu, đối tượng, thời lượng, slide tuỳ chọn) |
| `POST /add-source` | Người dùng tự thêm 1 nguồn (URL + đoạn trích tự dán), viết lại có dùng nguồn đó nếu liên quan |
| `POST /rewrite` | Loại 1 nguồn khỏi hồ sơ → chỉ viết lại đúng những câu phụ thuộc nguồn đó |
| `POST /expand-script` | Lượt AI riêng, chèn thêm câu minh hoạ (không trích dẫn) để kịch bản dài/phong phú hơn |
| `POST /qa-content` | Feature B (thử nghiệm) — gõ tay câu "lời trong video" để test AI phát hiện lệch nội dung |
| `POST /qa-content-from-audio` | Feature B thật — upload audio/video, Whisper tự nghe rồi đối chiếu với kịch bản |
| `POST /render-video` | Bonus — dựng video thật từ kịch bản (TTS + ảnh minh hoạ AI vẽ theo `yDoHinh`) |

## Chi phí ước tính mỗi lần chạy

Dùng `gpt-4o-mini` cho mọi lượt gọi (rẻ nhất trong dòng model có vision + tool dùng được), gồm:
- 1 lượt web search (`web_search_preview`) tìm 2-3 nguồn
- 1-3 lượt sinh kịch bản chính (có retry nếu validate lỗi cấu trúc)
- 1 lượt "judge" chấm độ liên quan trích dẫn (Layer 7)

**Ước tính ~0,01-0,03 USD/lần chạy `/generate`** (không có slide thì rẻ hơn vì không gửi ảnh; có slide
kèm ảnh "low detail" thì nhỉnh hơn chút, vẫn dưới mức trên do dùng ảnh độ phân giải thấp cố định).

`/render-video` (bonus) tốn thêm: TTS (`tts-1`) theo độ dài lời đọc (~5 câu dưới 0,01 USD) **+ ảnh minh
hoạ AI vẽ mỗi câu** (`gpt-image-1`, ~0,02-0,04 USD/ảnh) — kịch bản 10-12 câu tốn khoảng 0,3-0,5 USD cho
riêng phần ảnh. Vẽ lỗi thì tự rớt về khung chữ tĩnh, không tốn thêm phí.

`/qa-content-from-audio` tốn thêm phí Whisper (`whisper-1`, tính theo phút audio, rất rẻ) + 1 lượt
`gpt-4o-mini` so sánh.

*Số trên là ước tính dựa trên độ dài prompt/response thực tế quan sát khi test, không phải số chính thức
từ OpenAI — chạy thật và xem dashboard OpenAI để có số chính xác cho tài khoản của bạn.*

## Những gì hệ thống CHƯA làm được (trung thực, xem thêm `spec.md` §4 non-goals + §7)

- Chưa tự phát hiện khi 1 nguồn đã cũ/có bản cập nhật mới hơn.
- Chưa tự kiểm tra URL còn sống hay đã hỏng/yêu cầu đăng nhập (không tự fetch trang, chỉ dùng
  `web_search_preview` của OpenAI và nội dung người dùng tự dán ở `/add-source`).
- AI đôi khi trả lời chung chung thay vì liệt kê cụ thể khi được yêu cầu chi tiết (xem case #7, #18 trong
  `eval/golden-set.md`).
- Chủ đề ngoài phạm vi AI/công nghệ được guardrail độc lập chặn trước web search; đây vẫn là AI Judge nên
  cần giữ regression test và không xem là bảo đảm tuyệt đối ngoài phạm vi bộ test hiện tại.
- `render_video.py` vẽ ảnh minh hoạ TĨNH theo `yDoHinh` (không phải animation/chuyển động thật).
- `canhBao` (cảnh báo nguồn cũ) có trong schema nhưng AI áp dụng không đều — xem `eval/golden-set.md`.
- `/rewrite` gọi lại web search mỗi lần, có thể khiến trích dẫn cũ (câu không đổi) fail giả khi validate
  lại với kết quả search mới — xem `eval/golden-set.md` case 25.
