# Reflection cá nhân — Nguyễn Văn Biển

- **Mã học viên:** 2A202602416
- **Vai trò:** Evidence + Spec/Validation; phụ trách nghiên cứu giải pháp tương tự, §3 và §8 trong `spec.md`, cùng chuẩn bị validation.

## 1. Phần việc tôi đã làm

Tôi cùng Nguyễn Việt Dũng phỏng vấn các Lab Coach kiêm thành viên Studio Team theo hướng Mom Test, tập trung vào quy trình viết và duyệt kịch bản thực tế. Tôi ghi nhận các pain point trong `eval/interview-guide.md`, đối chiếu thông tin phỏng vấn và hỗ trợ đưa bằng chứng vào phần §1-§2 của `spec.md`.

Điểm quan trọng tôi ghi nhận được là một video dài khoảng ba đến năm phút có thể cần khoảng ba mươi lăm đến năm mươi câu, nhưng quy trình hiện tại mất khoảng năm giờ viết và ba giờ duyệt. Người viết còn phải tự tra cứu thuật ngữ bên ngoài và kiểm tra lại nội dung bằng tay. Bằng chứng này giúp nhóm không chọn tính năng chỉ vì nghe có vẻ hữu ích, mà tập trung vào bài toán có chi phí thời gian cụ thể và có thể kiểm chứng.

Tôi phụ trách nghiên cứu các giải pháp tương tự trong §3, gồm NotebookLM, ChatGPT deep research và Descript. Với mỗi sản phẩm, tôi xem xét flow, điều đáng học, điều cần né và điểm khác biệt của ScriptScout. Tôi cũng tham gia viết §8 về phân công, willing users và kế hoạch validation; đồng thời chuẩn bị việc cho người dùng thử prototype. Các quyết định và kết quả liên quan được đối chiếu với `spec.md` §3, §8 và `eval/golden-set.md`.

Qua so sánh, tôi thấy NotebookLM đáng học ở việc đặt trích dẫn gần nội dung để người duyệt truy ngược nhanh, còn ChatGPT deep research đáng học ở khả năng mở rộng việc tìm kiếm nhiều nguồn. Ngược lại, một báo cáo nghiên cứu vẫn cần được kiểm tra trước khi dùng làm lời đọc video. Descript cho thấy việc thao tác trên văn bản có thể làm giảm công sức hậu kỳ, nhưng sản phẩm này không giải quyết bài toán truy nguồn từ tài liệu sang kịch bản. Những quan sát đó giúp nhóm xác định điểm khác biệt của ScriptScout: tạo kịch bản đúng định dạng sử dụng và gắn căn cứ ở mức từng câu hoặc từng thông tin.

## 2. AI đã hỗ trợ tôi như thế nào

AI hỗ trợ tôi hệ thống hóa ghi chú phỏng vấn, gợi ý cách so sánh các sản phẩm tương tự theo cùng một khung và giúp rà lại sự liên kết giữa bằng chứng, pain point và quyết định chọn ScriptScout. AI cũng giúp tôi phát hiện những chỗ mô tả còn chung chung để sửa thành flow và hành vi cụ thể hơn.

Tôi không dùng nội dung do AI tạo ra như bằng chứng thay cho phỏng vấn thật. Các quote, số liệu và nhận xét so sánh đều phải đối chiếu với log phỏng vấn hoặc kết quả dùng thử thực tế. AI chỉ giúp tổ chức và phản biện tài liệu; tôi chịu trách nhiệm kiểm tra nguồn và quyết định nội dung nào được đưa vào spec.

Trong quá trình làm việc nhóm, tôi dùng AI như một công cụ phản biện hơn là người quyết định. Khi AI gợi ý một kết luận, tôi kiểm tra lại kết luận đó với log phỏng vấn, mô tả sản phẩm hoặc kết quả golden set. Cách làm này đặc biệt quan trọng với phần evidence và nghiên cứu đối thủ, vì một câu diễn đạt nghe hợp lý nhưng không có nguồn sẽ làm yếu cả quyết định sản phẩm.

## 3. Bài học từ case fail của nhóm

Case 5 trong `eval/golden-set.md` khiến tôi chú ý nhất: hệ thống từng viết một kịch bản về nấu phở dù mục tiêu hoàn toàn nằm ngoài phạm vi nội dung nguồn. Lỗi này cho thấy việc có citation hoặc có output đúng schema chưa chứng minh được nội dung phù hợp với bài toán. Một hệ thống AI có thể trả lời rất trôi chảy nhưng vẫn sai về phạm vi và không nên được tin chỉ vì hình thức đầu ra đầy đủ.

Từ case đó, tôi rút ra rằng nghiên cứu và validation phải kiểm tra cả những tình huống người dùng yêu cầu ngoài phạm vi, không chỉ kiểm tra happy path. Khi ghi nhận kết quả, nhóm cần giữ nguyên quality bar đã chốt, nói rõ case chưa đạt và phân biệt phần đã sửa được với giới hạn còn tồn tại. Điều này giúp phần spec và phần demo trung thực hơn, đồng thời cho thấy quyết định cải tiến xuất phát từ bằng chứng thay vì cảm nhận.

Case này cũng làm rõ ranh giới giữa "có output" và "output dùng được". Một kịch bản đủ trường dữ liệu, có câu chữ tự nhiên hoặc có giao diện đẹp vẫn chưa đạt nếu không trả lời đúng nhiệm vụ và không có căn cứ phù hợp. Vì vậy, khi chuẩn bị validation, tôi muốn quan sát người dùng có truy được nguồn hay không, có hiểu lý do hệ thống chọn nguồn hay không, và họ sẽ làm gì khi gặp một câu chưa được xác minh. Đây là những hành vi có giá trị hơn một lời nhận xét chung rằng demo "ổn".

## 4. Điều tôi học được về làm việc nhóm

Phần evidence và phần build phụ thuộc lẫn nhau. Nếu chỉ nghiên cứu pain point mà không hiểu prototype có thể kiểm chứng như thế nào, nhóm dễ đặt yêu cầu quá rộng. Ngược lại, nếu chỉ tập trung vào code mà bỏ qua bằng chứng, nhóm có thể xây một tính năng chạy được nhưng không chứng minh được nó giải quyết vấn đề thật. Việc đối chiếu giữa phỏng vấn, nghiên cứu sản phẩm tương tự, spec và golden set giúp tôi hiểu rõ hơn cách biến một quan sát rời rạc thành quyết định có thể giải thích trước người dùng và giám khảo.

## 5. Điều tôi sẽ làm khác nếu có thêm thời gian

Tôi sẽ tổ chức thêm một vòng dùng thử có task cụ thể với willing users, ghi lại thời gian hoàn thành, chỗ do dự và quote nguyên văn. Sau đó tôi sẽ đối chiếu feedback người dùng với các failure trong golden set để ưu tiên những thay đổi có ảnh hưởng trực tiếp đến khả năng kiểm chứng nguồn và mức độ tin cậy của kịch bản.

Tôi cũng sẽ chuẩn bị một bảng đối chiếu ngắn giữa giả định ban đầu và bằng chứng sau khi dùng thử. Ví dụ, nếu người dùng không bấm vào nguồn dù tính năng đã có, nhóm cần kiểm tra lại cách trình bày và lý do tin cậy thay vì chỉ kết luận rằng người dùng không quan tâm. Cách này giúp các thay đổi sau demo có căn cứ và tránh mở rộng sản phẩm theo cảm tính.
