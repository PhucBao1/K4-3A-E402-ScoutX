# ScriptScout - Codebase

Prototype cuối ở mức **Working**. Luồng chính dùng FastAPI và OpenAI thật để nhận chủ đề, tự tìm nguồn,
tạo kịch bản có provenance theo từng câu và hỗ trợ loại nguồn/viết lại câu phụ thuộc.

## Bản nào dùng để demo?

- **Working prototype:** `backend/main.py` + `backend/static/index.html`.
- **Snapshot CP2:** `index.html` ở thư mục này là bản Mock cũ, giữ lại để chứng minh checkpoint; không dùng
  làm demo cuối và không đại diện trạng thái hiện tại.

## Chạy Working prototype

```bash
cd codebase/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Điền OPENAI_API_KEY vào .env
uvicorn main:app --port 8000
```

Mở `http://localhost:8000`.

## Lát cắt đang chạy

Người viết nhập bốn trường bắt buộc: chủ đề, mục tiêu bài học, đối tượng học và thời lượng. Slide PDF là
tùy chọn; nếu không có slide, agent tự tìm nguồn web. Sau khi tạo kịch bản, reviewer có thể:

- Bấm một câu để mở đúng thông tin, đoạn trích và tài liệu gốc.
- Thêm một nguồn của mình bằng URL và đoạn trích.
- Loại một nguồn; hệ thống chỉ viết lại câu phụ thuộc và giữ nguyên câu khác.
- Xuất kịch bản và hồ sơ nguồn theo schema của BTC.

AI tạo draft và gắn nguồn; con người duyệt cuối trước khi sử dụng. Hệ thống không tự publish.

## Trạng thái tính năng

| Phần | Trạng thái |
|---|---|
| `/generate`: topic → research → script có nguồn | Working, AI thật |
| Slide PDF tùy chọn | Working |
| Web search và chấm độ tin cậy | Working, AI thật |
| Bấm câu xem evidence | Working |
| `/add-source`: thêm nguồn người dùng | Working |
| `/rewrite`: loại nguồn và chỉ sửa câu phụ thuộc | Working |
| Demo offline có banner | Working, dữ liệu mẫu được ghi nhãn |
| Content QA hậu kỳ | Prototype bonus qua `/qa-content*` |
| Format QA hậu kỳ | Prototype bonus qua `/format-check`, `/qa-full` |
| Render video | Prototype bonus, không thuộc lát cắt C3 chính |

## Validation và guardrail chính

Trước khi trả output, backend kiểm:

1. ID evidence phải trỏ tới nguồn có thật.
2. ID ở từng câu phải trỏ tới thông tin có thật.
3. Số liệu trong lời đọc/chữ màn hình phải có đúng evidence.
4. Trích dẫn web phải tồn tại trong source text.
5. Số nguồn xác nhận không được khai khống.
6. Lời đọc không chứa chữ số theo chuẩn kịch bản BTC.
7. Citation phải thực sự liên quan tới claim.
8. Topic ngoài phạm vi AI/công nghệ bị chặn trước web search.

Chi tiết implementation: `backend/main.py`, `backend/prompt.py`. Kết quả kiểm thử và failure được giữ tại
`../eval/golden-set.md`; quality bar chính thức nằm trong `../spec.md` §7.

## Phần thật và phần mock

- Luồng chính không dùng hardcode khi bấm Generate.
- Nút `Xem ví dụ demo offline` dùng dữ liệu cố định và luôn hiện banner cảnh báo.
- API lỗi không tự chuyển sang dữ liệu mẫu.
- `codebase/index.html` là Mock CP2 riêng, không được dùng để tuyên bố kết quả Working.

## Giới hạn hiện tại

- Chưa tự fetch URL bất kỳ để kiểm link sống/freshness; `/add-source` dùng đoạn trích người dùng dán.
- Chưa xác minh source lineage để biết hai publisher có sao chép cùng nguồn gốc hay không.
- `/rewrite` tìm web lại, nên tập nguồn có thể thay đổi giữa hai lượt.
- Chưa có tài khoản, phân quyền, lưu phiên, hàng đợi hay benchmark nhiều người dùng.
- Clean run chính thức gần nhất đạt 65%, chưa đạt quality bar 70%; xem `eval/golden-set.md`.
