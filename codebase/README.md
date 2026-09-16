# ScriptScout — codebase

## Chạy thử
- **Link demo live (CP2):** https://phucbao1.github.io/K4-3A-E402-ScoutX/codebase/index.html
- Hoặc mở trực tiếp `index.html` bằng trình duyệt (không cần server/build).

## Lát cắt đã chốt (khác bản gốc đề C3)
Đề gốc C3 yêu cầu agent **tự tìm tài liệu trên mạng**. Nhóm ScoutX đơn giản hoá cho vừa sức trong 47,5 giờ:
**input = slide bài giảng có sẵn** (nguồn chính, thay vì tự tìm web từ đầu), **AI bổ sung thêm nguồn ngoài**
(paper, tin/thông báo chính thức, biểu đồ, ví dụ thực tế) để kịch bản có chiều sâu hơn chỉ đọc slide,
**output = kịch bản** theo đúng mẫu `mau-kich-ban.md` của BTC — mỗi câu gắn đúng một nguồn (trang slide
hoặc nguồn ngoài), bấm câu hoặc bấm nguồn để xem lại đúng chỗ chứng minh, kèm hồ sơ nguồn có loại/độ tin
cậy/lý do tin cậy theo đúng tinh thần `ho-so-nguon-mau.json` của BTC.
Việc "tự tìm mọi nguồn từ đầu qua web search thật + tự chấm độ tin cậy bằng agent riêng" đưa vào
**non-goal** (ghi trong `spec.md` §4) — CP3 chỉ cần thay các bước mock bằng ≥1 lời gọi AI thật.

## Mức prototype: Mock (CP2)
Flow bấm hết được từ đầu đến cuối, nhưng **chưa có lời gọi AI thật**:

| Phần | Trạng thái |
|---|---|
| Form chọn slide / mục tiêu / đối tượng / thời lượng | Thật (input thật, chưa validate) |
| "Đọc slide + tìm thêm nguồn bổ sung" | **Mock** — trả về cố định: 3 trang slide (3,4,5) + 4 nguồn ngoài (1 paper, 1 tin chính thức, 1 biểu đồ, 1 ví dụ thực tế), sau độ trễ giả (1.4s) |
| "Viết kịch bản gắn nguồn" | **Mock** — 13 câu cố định (rút gọn từ nội dung slide + tư liệu công khai có thật), không đổi theo input |
| Bấm câu hoặc bấm một nguồn trong hồ sơ tài liệu → xem đúng chỗ chứng minh (kèm loại/độ tin cậy/lý do) | Thật (logic hiển thị thật, dữ liệu nguồn là mock) |

Nội dung mock: 3 trang slide lấy tay từ `data/vlearn-pack/slides/d1-slide-hackathon.pdf` (trang 3-5, rút
gọn); 4 nguồn ngoài (paper "Attention Is All You Need", thông báo ra mắt ChatGPT của OpenAI, biểu đồ dựng
lại từ mốc thời gian trang 5, ví dụ Gmail lọc spam) là thông tin công khai có thật, đơn giản hoá cho demo —
không commit file PDF gốc vào repo, đúng quy định bảo mật data.

## Xuất file (để dựng video / dùng ở bước sau)
Hai nút cuối bảng kết quả xuất **thật** (không mock) hai file JSON, đúng schema của BTC:

| Nút | File | Schema | Dùng để |
|---|---|---|---|
| Xuất kịch bản | `scriptscout-kich-ban.json` | `hackathon-kich-ban/1` (đúng `mau-kich-ban.md`) — có `loi`, `chuTrenManHinh`, `yDoHinh`, `nguon` | Gửi cho người dựng video, hoặc làm input cho C4 StoryboardAI |
| Xuất hồ sơ tài liệu | `scriptscout-ho-so-nguon.json` | `hackathon-ho-so-nguon/1` (đúng `ho-so-nguon-mau.json`) | Người duyệt xem lại toàn bộ nguồn + độ tin cậy ngoài giao diện |

`mucTieu`/`doiTuong`/`thoiLuongPhutDuKien` trong file xuất lấy từ ô input thật trên form, còn `cau`/`nguon` vẫn là data mock — CP3 nối AI thật thì hai nút này không cần đổi, chỉ đổi nguồn dữ liệu `MOCK`.

## Kế hoạch CP3
Thay phần mock "đọc slide" + "tìm nguồn bổ sung" + "viết câu" bằng ≥1 lời gọi AI thật (đọc slide/PDF +
tìm/thẩm định nguồn ngoài + LLM sinh kịch bản có cite), giữ nguyên UI/flow đã có ở CP2. Log/trace của lời
gọi thật sẽ lưu trong `eval/`.
