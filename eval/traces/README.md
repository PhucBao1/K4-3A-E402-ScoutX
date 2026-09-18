# AI trace samples

Thư mục này lưu trace đã rút gọn từ các lần chạy thật của ScriptScout để chứng minh quyết định trung tâm
có sử dụng AI thật. Trace không chứa API key, chain-of-thought hoặc toàn bộ provider response.

- `generate-transformer-2026-09-18.json`: chạy luồng `/generate` không có slide, gồm scope check, web
  search, sinh hồ sơ nguồn/kịch bản và validation.
- `execution.method` ghi rõ cách gọi. Gọi trực tiếp hàm endpoint và gọi qua HTTP sử dụng cùng code path;
  cách trực tiếp được dùng khi môi trường kiểm thử không cho hai process kết nối local socket.
- `output.sample` là dữ liệu nguyên văn rút gọn từ response thật; `output.summary` là số đếm từ response.

Không commit `.env` hoặc log request header của OpenAI vào repo.
