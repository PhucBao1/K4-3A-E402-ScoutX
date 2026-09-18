# Reflection cá nhân - Nguyễn Phúc Bảo

- **Họ và tên:** Nguyễn Phúc Bảo
- **Mã học viên:** 2A202602925
- **Nhóm:** ScoutX
- **Track:** C3 - ScriptScout
- **Vai trò:** Đội trưởng, phụ trách build flow, prompt và golden set

## 1. Vai trò và phần tôi trực tiếp thực hiện

Trong dự án ScriptScout, tôi phụ trách phần kỹ thuật chính và điều phối phạm vi sản phẩm. Tôi xây backend FastAPI, nối lời gọi AI thật, tích hợp web search, xử lý PDF và thiết kế cấu trúc đầu ra gồm hồ sơ nguồn và kịch bản. Tôi cũng triển khai luồng correction: khi reviewer loại một nguồn, hệ thống xác định các thông tin dùng nguồn đó, tìm đúng những câu phụ thuộc và chỉ viết lại các câu bị ảnh hưởng thay vì sinh lại toàn bộ kịch bản.

Các file tôi trực tiếp phụ trách chính gồm:

- `codebase/backend/main.py`: endpoint generate, add-source, rewrite và các lớp validation.
- `codebase/backend/prompt.py`: prompt tạo kịch bản, rewrite, kiểm tra phạm vi và citation relevance.
- `eval/golden-set.md`: thiết kế case kiểm thử, ghi kết quả, phân tích failure và theo dõi các lần sửa.
- Phần thiết kế kỹ thuật, automation và kiểm thử trong `spec.md`.

Ngoài việc viết code, tôi là người quyết định giữ lát cắt chính ở mức tạo kịch bản có nguồn và human approval. Các phần QA hậu kỳ và dựng video chỉ là nhánh thử nghiệm, không thay đổi phạm vi lõi C3.

## 2. AI đã hỗ trợ tôi như thế nào?

Tôi sử dụng AI như một công cụ hỗ trợ lập trình, phân tích lỗi và tạo phương án thử nghiệm. AI giúp tôi:

- Gợi ý cấu trúc prompt và schema JSON cho hồ sơ nguồn, thông tin và câu kịch bản.
- Viết bản nháp cho một số hàm xử lý, regex và endpoint FastAPI.
- Đề xuất các edge case như số liệu không có trong nguồn, citation sai ID, nguồn mâu thuẫn và prompt injection.
- Hỗ trợ đọc log lỗi, so sánh output giữa các lần chạy và đề xuất vị trí cần siết validation.
- Tạo nhanh các biến thể prompt để tôi kiểm tra trên golden set.

Tôi không dùng output của AI như kết quả cuối mà không kiểm tra. Phần tôi chịu trách nhiệm là xác định invariant nào cần bảo vệ, chọn phần nào kiểm bằng code và phần nào cần AI Judge, đọc output thật, ghi cả case fail và quyết định có chấp nhận bản sửa hay không. Ví dụ, yêu cầu “không bịa số liệu” trong prompt không đủ để bảo đảm an toàn; tôi bổ sung validator đối chiếu số trong câu với đúng evidence. Tương tự, citation có tồn tại vẫn chưa chứng minh citation liên quan, nên tôi tách thêm một bước judge riêng.

Qua dự án, tôi nhận ra dùng AI để code nhanh không thay thế việc hiểu luồng dữ liệu. Tôi phải giải thích được quan hệ `câu -> thông tin -> bằng chứng -> nguồn`, lý do guardrail phạm vi chạy trước web search và cách endpoint rewrite giữ nguyên các câu không bị ảnh hưởng.

## 3. Case fail quan trọng nhất và cách tôi xử lý

Case cho tôi bài học lớn nhất là case hai nguồn mâu thuẫn về mốc thời gian ImageNet. Ban đầu, hệ thống tạo một kết luận rồi gắn các citation có thật nhưng nội dung trích dẫn không liên quan trực tiếp đến mốc thời gian. Vì các ID nguồn đều tồn tại và đoạn trích cũng có trong nguồn, những validator cấu trúc cũ vẫn cho output đi qua. Model còn dùng các citation đó để khai rằng thông tin đã được nhiều nguồn xác nhận.

Failure này nguy hiểm hơn một citation bịa hoàn toàn vì output nhìn rất thuyết phục: có URL, có đoạn trích và có số nguồn xác nhận. Reviewer có thể tin rằng claim đã được kiểm chứng dù evidence thực tế không hỗ trợ claim.

Tôi xử lý theo ba bước:

1. Giữ nguyên case fail trong golden set thay vì chỉ lưu kết quả sau khi sửa.
2. Phân biệt hai câu hỏi: “citation có tồn tại không?” và “citation có thực sự chứng minh claim không?”.
3. Thêm một AI Judge độc lập để chấm quan hệ ngữ nghĩa giữa từng `thongTin` và `bangChung`, đồng thời chỉ cho phép trạng thái nhiều nguồn xác nhận khi evidence liên quan còn đủ.

Sau khi sửa, case này bị chặn thay vì trả về một kịch bản có vẻ hợp lệ. Tuy nhiên, tôi không xem AI Judge là tuyệt đối đúng. Judge vẫn có thể false positive hoặc false negative, vì vậy hệ thống tiếp tục cần golden set và human approval.

## 4. Kết quả và phần chưa đạt

Quality bar nhóm chốt là ít nhất 70% golden set và 100% case thuộc lớp nguồn sự thật không chứa số liệu bịa. Clean run đầy đủ gần nhất đạt 13/20 case, tương đương 65%, gồm 3 case partial và 4 case fail. Điều kiện cứng của lớp nguồn sự thật đạt 100% trên bộ test hiện tại.

Một số lần chạy lại riêng sau khi vá đã chạm 14/20, tương đương 70%, nhưng tôi không dùng kết quả đó để thay thế clean run. Hệ thống vẫn có tính ngẫu nhiên và cần chạy lại toàn bộ bộ test trên cùng một phiên bản để xác nhận độ ổn định. Hai nhóm lỗi còn đáng chú ý là trả lời chưa đủ cụ thể và mixed hallucination, trong đó một chi tiết bịa có thể nằm giữa nhiều chi tiết đúng.

Tôi đánh giá prototype đã chứng minh được workflow và các cơ chế kiểm soát chính, nhưng chưa production-ready. Human vẫn phải duyệt cuối; latency, chi phí, source independence và độ ổn định của AI Judge vẫn cần đo thêm.

## 5. Bài học cá nhân

Bài học lớn nhất của tôi là không nên đặt tất cả kỳ vọng an toàn vào một prompt dài. Prompt có thể hướng dẫn model, nhưng các điều kiện cứng cần được tách thành validator hoặc judge độc lập để quan sát, kiểm thử và sửa riêng.

Tôi cũng học được rằng evaluation không phải bước làm sau khi sản phẩm hoàn thành. Golden set đã trực tiếp thay đổi kiến trúc của ScriptScout. Nếu chỉ demo vài happy path, tôi sẽ không phát hiện các lỗi như bịa số liệu, topic ngoài phạm vi vẫn được web search hợp thức hóa, ID trùng trong rewrite hay citation thật nhưng không liên quan.

Cuối cùng, báo cáo một kết quả chưa đạt nhưng có phương pháp đo rõ ràng hữu ích hơn việc chỉ chọn số đẹp. Con số 65% cho tôi biết sản phẩm đang thiếu gì và giúp nhóm đưa ra roadmap cụ thể: chạy lại clean run, kiểm tra claim ở mức nhỏ hơn, siết specificity và chỉ mở rộng pipeline video sau khi lõi đã ổn định.

## 6. Nếu làm lại

Nếu làm lại từ đầu, tôi sẽ:

1. Thiết kế data graph và invariant trước khi viết prompt.
2. Tạo golden set tối thiểu ngay từ phiên bản đầu, đặc biệt cho correction path và nguồn mâu thuẫn.
3. Cache snapshot nguồn của mỗi phiên để rewrite không bị thay đổi tập nguồn do web search chạy lại.
4. Ghi latency, token và chi phí theo từng bước ngay từ đầu.
5. Mời ít nhất hai Studio/Lab Coach dùng workflow thật sớm hơn, thay vì đợi gần thời điểm demo.

Những thay đổi này sẽ giúp vòng lặp build, đo và sửa ngắn hơn, đồng thời tách rõ hơn giữa một prototype chạy được và một hệ thống đủ tin cậy để dùng trong quy trình sản xuất nội dung.
