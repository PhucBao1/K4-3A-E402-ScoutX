# Reflection cá nhân — Nguyễn Văn Biển

- **Mã học viên:** 2A202602416
- **Vai trò:** Evidence + Spec/Validation; phụ trách nghiên cứu giải pháp tương tự, §3 và §8 trong `spec.md`, cùng chuẩn bị validation.

## 1. Phần việc tôi đã làm

Tôi cùng Nguyễn Việt Dũng phỏng vấn các Lab Coach kiêm thành viên Studio Team theo hướng Mom Test, tập trung vào quy trình viết và duyệt kịch bản thực tế. Tôi ghi nhận các pain point trong `eval/interview-guide.md`, đối chiếu thông tin phỏng vấn và hỗ trợ đưa bằng chứng vào phần §1-§2 của `spec.md`.

Tôi phụ trách nghiên cứu các giải pháp tương tự trong §3, gồm NotebookLM, ChatGPT deep research và Descript. Với mỗi sản phẩm, tôi xem xét flow, điều đáng học, điều cần né và điểm khác biệt của ScriptScout. Tôi cũng tham gia viết §8 về phân công, willing users và kế hoạch validation; đồng thời chuẩn bị việc cho người dùng thử prototype. Các quyết định và kết quả liên quan được đối chiếu với `spec.md` §3, §8 và `eval/golden-set.md`.

## 2. AI đã hỗ trợ tôi như thế nào

AI hỗ trợ tôi hệ thống hóa ghi chú phỏng vấn, gợi ý cách so sánh các sản phẩm tương tự theo cùng một khung và giúp rà lại sự liên kết giữa bằng chứng, pain point và quyết định chọn ScriptScout. AI cũng giúp tôi phát hiện những chỗ mô tả còn chung chung để sửa thành flow và hành vi cụ thể hơn.

Tôi không dùng nội dung do AI tạo ra như bằng chứng thay cho phỏng vấn thật. Các quote, số liệu và nhận xét so sánh đều phải đối chiếu với log phỏng vấn hoặc kết quả dùng thử thực tế. AI chỉ giúp tổ chức và phản biện tài liệu; tôi chịu trách nhiệm kiểm tra nguồn và quyết định nội dung nào được đưa vào spec.

## 3. Bài học từ case fail của nhóm

Case 5 trong `eval/golden-set.md` khiến tôi chú ý nhất: hệ thống từng viết một kịch bản về nấu phở dù mục tiêu hoàn toàn nằm ngoài phạm vi nội dung nguồn. Lỗi này cho thấy việc có citation hoặc có output đúng schema chưa chứng minh được nội dung phù hợp với bài toán. Một hệ thống AI có thể trả lời rất trôi chảy nhưng vẫn sai về phạm vi và không nên được tin chỉ vì hình thức đầu ra đầy đủ.

Từ case đó, tôi rút ra rằng nghiên cứu và validation phải kiểm tra cả những tình huống người dùng yêu cầu ngoài phạm vi, không chỉ kiểm tra happy path. Khi ghi nhận kết quả, nhóm cần giữ nguyên quality bar đã chốt, nói rõ case chưa đạt và phân biệt phần đã sửa được với giới hạn còn tồn tại. Điều này giúp phần spec và phần demo trung thực hơn, đồng thời cho thấy quyết định cải tiến xuất phát từ bằng chứng thay vì cảm nhận.

## 4. Điều tôi sẽ làm khác nếu có thêm thời gian

Tôi sẽ tổ chức thêm một vòng dùng thử có task cụ thể với willing users, ghi lại thời gian hoàn thành, chỗ do dự và quote nguyên văn. Sau đó tôi sẽ đối chiếu feedback người dùng với các failure trong golden set để ưu tiên những thay đổi có ảnh hưởng trực tiếp đến khả năng kiểm chứng nguồn và mức độ tin cậy của kịch bản.
