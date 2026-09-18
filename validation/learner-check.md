# Validation phụ với học viên — độ dễ hiểu của kịch bản

> Mục tiêu: kiểm tra kịch bản đầu ra của ScriptScout có dễ hiểu, tự nhiên và giúp học viên thấy được ý nghĩa của việc kiểm chứng nguồn hay không. Đây là **validation phụ với learner**, không thay thế validation chính với Lab Coach/Studio team về workflow viết kịch bản, duyệt nguồn, loại nguồn và viết lại phần liên quan.

## Cách chạy

- Đối tượng: 2 học viên ngoài nhóm.
- Task: đọc/xem một đoạn kịch bản ngắn do ScriptScout sinh về chủ đề kiểm chứng nguồn khi dùng AI viết bài giảng.
- Câu hỏi:
  1. Bạn hiểu nội dung chính là gì?
  2. Chỗ nào khó hiểu hoặc nghe sượng?
  3. Bạn đề xuất cải thiện gì để người học dễ hiểu hơn?

## Feedback 1 — Trướng, học viên

**Nội dung hiểu được:** Tôi hiểu được mục đích chính của kịch bản là nhấn mạnh việc cần kiểm chứng nguồn khi sử dụng AI để viết bài giảng. Đặc biệt, tôi hiểu rằng AI có thể đưa ra số liệu hoặc thông tin nghe có vẻ hợp lý nhưng chưa chắc đã chính xác, nên người viết cần kiểm tra lại nguồn trước khi sử dụng. Phần này giúp tôi hình dung được quy trình từ việc lấy thông tin từ AI đến việc kiểm tra và dẫn nguồn trong bài giảng.

**Chỗ khó hiểu:** Phần nói về **“nguồn độc lập xác nhận”** đối với tôi vẫn hơi trừu tượng. Tôi chưa hình dung rõ thế nào được xem là hai nguồn độc lập và tại sao việc hai nguồn cùng đưa ra một thông tin lại giúp tăng độ tin cậy. Nếu chỉ giải thích bằng khái niệm thì hơi khó liên hệ với thực tế.

**Gợi ý cải thiện:** Nên thêm một ví dụ cụ thể, chẳng hạn AI đưa ra thông tin “X% người dùng đã sử dụng công cụ AI trong năm 2025”, sau đó cho người học xem **hai nguồn khác nhau cùng đưa ra con số X%**. Có thể minh họa bằng cách đặt hai nguồn cạnh nhau và highlight phần số liệu giống nhau. Ngoài ra, nếu có một hình ảnh hoặc sơ đồ thể hiện **“Câu trong kịch bản → kiểm tra nguồn → đoạn trích từ nguồn”** thì tôi nghĩ người học sẽ dễ hiểu hơn cách một thông tin được xác minh trước khi đưa vào bài giảng.

## Feedback 2 — Khải, học viên

**Nội dung hiểu được:** Tôi hiểu rằng công cụ hỗ trợ người viết kịch bản không chỉ giúp tạo lời giảng nhanh hơn mà còn giúp người viết **đưa nguồn vào đúng chỗ và hạn chế việc sử dụng những số liệu chưa được kiểm chứng**. Tôi thấy phần này khá thực tế vì khi dùng AI để viết nội dung, người viết có thể dễ dàng lấy luôn những con số AI đưa ra mà không biết chúng xuất phát từ đâu.

**Chỗ khó hiểu:** Tôi vẫn chưa phân biệt rõ **câu nào chỉ là câu dẫn dắt của người giảng** và câu nào là thông tin thực tế cần phải kiểm chứng. Ví dụ, nếu trong kịch bản có nhiều câu liên tiếp thì người học có thể không biết câu nào đang đưa ra một dữ kiện, số liệu hoặc nhận định cần có nguồn, còn câu nào chỉ nhằm kết nối các ý. Nếu không phân biệt rõ thì người viết có thể kiểm tra nguồn quá nhiều hoặc ngược lại, bỏ sót những thông tin quan trọng.

**Gợi ý cải thiện:** Tôi đề xuất trên giao diện nên có nhãn trực quan cho từng câu có thông tin cần kiểm chứng, ví dụ **“Đã xác minh”**, **“Chưa xác minh”** hoặc **“Không cần nguồn”**. Với những câu có số liệu, có thể đánh dấu nổi bật và cho phép người viết bấm vào để xem nguồn tương ứng. Như vậy người học vừa biết câu nào đã được kiểm tra, vừa hiểu được mối liên hệ giữa **nội dung trong kịch bản – trạng thái xác minh – nguồn tham khảo**. Tôi nghĩ cách này sẽ giúp quy trình kiểm chứng rõ ràng và dễ áp dụng hơn.

## Kết luận & quyết định

- Cả 2/2 học viên hiểu được thông điệp chính: ScriptScout không chỉ viết nhanh hơn, mà còn giúp kiểm chứng nguồn và hạn chế số liệu chưa xác minh.
- Điểm còn khó hiểu lặp lại ở cả hai phản hồi: khái niệm/trạng thái xác minh cần được biểu diễn trực quan hơn, đặc biệt là “nguồn độc lập” và câu nào cần nguồn.
- Quyết định sản phẩm:
  - Giữ lại nhãn trạng thái ở cấp thông tin/câu: `da-xac-minh`, `chua-xac-minh`, và câu không cần nguồn (`nguon: []`).
  - Ưu tiên UI cho người duyệt: bấm vào câu để thấy đoạn trích nguồn, hiển thị cảnh báo khi thông tin chưa xác minh hoặc nguồn mâu thuẫn.
  - Trong vòng tiếp theo, thêm ví dụ/sơ đồ “Câu trong kịch bản → trạng thái xác minh → đoạn trích nguồn” vào demo/pitch để học viên hiểu nhanh hơn.
