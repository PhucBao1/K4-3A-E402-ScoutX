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

## Chi phí ước tính mỗi lần chạy

Dùng `gpt-4o-mini` cho mọi lượt gọi (rẻ nhất trong dòng model có vision + tool dùng được), gồm:
- 1 lượt web search (`web_search_preview`) tìm 2-3 nguồn
- 1-3 lượt sinh kịch bản chính (có retry nếu validate lỗi cấu trúc)
- 1 lượt "judge" chấm độ liên quan trích dẫn (Layer 7)

**Ước tính ~0,01-0,03 USD/lần chạy `/generate`** (không có slide thì rẻ hơn vì không gửi ảnh; có slide
kèm ảnh "low detail" thì nhỉnh hơn chút, vẫn dưới mức trên do dùng ảnh độ phân giải thấp cố định).
`render_video.py` (bonus dựng video) tốn thêm phí TTS (`tts-1`) theo độ dài lời đọc — với kịch bản 5 câu
(~30 giây audio) chi phí TTS dưới 0,01 USD.

*Số trên là ước tính dựa trên độ dài prompt/response thực tế quan sát khi test, không phải số chính thức
từ OpenAI — chạy thật và xem dashboard OpenAI để có số chính xác cho tài khoản của bạn.*

## Những gì hệ thống CHƯA làm được (trung thực, xem thêm `spec.md` §4 non-goals + §7)

- Chưa tự phát hiện khi 1 nguồn đã cũ/có bản cập nhật mới hơn.
- Chưa tự kiểm tra URL còn sống hay đã hỏng/yêu cầu đăng nhập (không tự fetch trang, chỉ dùng
  `web_search_preview` của OpenAI và nội dung người dùng tự dán ở `/add-source`).
- AI đôi khi trả lời chung chung thay vì liệt kê cụ thể khi được yêu cầu chi tiết (xem case #7, #18 trong
  `eval/golden-set.md`).
- Khi mục tiêu hoàn toàn ngoài phạm vi, AI cải thiện nhưng chưa từ chối tường minh 100% các lần.
- Chưa có UI để người duyệt CHỌN giữa 2 nguồn đang mâu thuẫn (`moTaMauThuan`) — mới có ở dạng dữ liệu, chưa
  có màn hình riêng.
- `render_video.py` chỉ tạo khung hình tĩnh (chữ trên nền màu), không có animation theo `yDoHinh`.
