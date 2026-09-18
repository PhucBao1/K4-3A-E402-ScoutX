# Reflection cá nhân - Nguyễn Việt Dũng

- **Họ và tên:** Nguyễn Việt Dũng
- **Mã học viên:** 2A202602533
- **Nhóm:** ScoutX
- **Track:** C3 - ScriptScout
- **Vai trò:** Lên ý tưởng ban đầu, thu thập bằng chứng (Evidence), xây dựng kỹ năng phụ trợ (Skill), và thực hiện Validation.

## 1. Vai trò và phần tôi trực tiếp thực hiện

Trong dự án ScriptScout, tôi đảm nhận các phần việc thiên về định hướng sản phẩm, xác thực nhu cầu người dùng và xây dựng công cụ hỗ trợ quy trình:
- **Đưa ra ý tưởng ban đầu** cho sản phẩm và tham gia định hình luồng hoạt động chính.
- **Tiến hành phỏng vấn thực tế:** Trực tiếp phỏng vấn 2 Lab Coach kiêm thành viên Studio Team theo chuẩn Mom Test để tìm ra pain point thật sự của họ. Toàn bộ log phỏng vấn được tôi ghi lại nguyên văn trong `eval/interview-guide.md`.
- **Viết Spec:** Chịu trách nhiệm chính soạn thảo phần Bằng chứng và Quyết định (§1-§2) trong file `spec.md` dựa trên dữ liệu phỏng vấn.
- **Xây dựng sản phẩm phụ (Skill):** Thiết kế và xây dựng một bộ "skill" (kỹ năng AI) chuyên biệt để tối ưu hóa quy trình từ lúc đọc tài liệu nguồn đến việc tự động tìm kiếm và trích xuất bằng chứng.
- **Validation (CP5):** Lên kế hoạch và chuẩn bị nhật ký kiểm thử người dùng (validation) với 5 người dùng ngoài, thu thập feedback để điều chỉnh sản phẩm.

## 2. AI đã hỗ trợ tôi như thế nào?

Trong quá trình làm việc, tôi đã sử dụng AI như một trợ lý đắc lực:
- **Thiết kế kịch bản phỏng vấn:** Tôi dùng AI để rà soát lại các câu hỏi phỏng vấn, đảm bảo chúng tuân thủ nguyên tắc Mom Test (không hỏi câu hỏi dẫn dắt, tập trung vào hành vi trong quá khứ).
- **Tổng hợp và phân tích dữ liệu:** AI giúp tôi bóc tách, lọc các keyword quan trọng từ bản ghi âm/ghi chép phỏng vấn để chuyển hóa thành các "Pain point" định lượng đưa vào Spec.
- **Xây dựng bộ Skill:** Khi phát triển tính năng phụ (bộ skill cho quy trình đọc tài liệu và tìm bằng chứng), tôi đã dùng AI để thiết kế luồng prompt, giúp trích xuất thông tin một cách có cấu trúc hơn. Tuy nhiên, tôi phải tự tay review và điều chỉnh lại prompt để đảm bảo AI không tự suy diễn (hallucinate) mà bám sát hoàn toàn vào tài liệu gốc.

## 3. Case fail quan trọng nhất và cách tôi xử lý

**Tình huống (Fail):** Trong những lần tiếp cận vấn đề đầu tiên, do quá hào hứng với ý tưởng của mình, tôi có xu hướng nghĩ đến giải pháp trước khi thực sự hiểu vấn đề của người dùng. Việc này dẫn đến rủi ro xây dựng những tính năng "nice-to-have" nhưng không giải quyết đúng điểm "đau" nhất. Hơn nữa, khi xây dựng bộ skill AI đọc tài liệu, lúc đầu tôi gặp lỗi AI tự suy diễn thông tin hoặc bỏ sót các bằng chứng quan trọng.

**Cách xử lý:** Tôi quyết định áp dụng triệt để Mom Test trong lúc phỏng vấn: không hỏi về giải pháp, chỉ hỏi về quá trình làm việc thực tế ("Lần gần nhất bạn viết kịch bản mất bao lâu? Đoạn nào chiếm nhiều thời gian nhất?"). Nhờ đó, tôi tìm ra insight cực kỳ đắt giá: "Mất 5h viết + 3h duyệt vì không kiểm soát được nguồn chứng minh cho từng câu", giúp nhóm pivot đúng hướng. Với bộ Skill phụ trợ, tôi xử lý lỗi bằng cách siết chặt lại prompt, yêu cầu AI phải trích xuất nguyên văn (verbatim) và kiểm tra lại chéo với nội dung gốc.

## 4. Kết quả và phần chưa đạt

- **Kết quả đạt được:** Bảng Evidence và Impact trong `spec.md` cực kỳ vững chắc do được back-up bằng dữ liệu phỏng vấn thật. Bộ skill đọc tài liệu và tìm bằng chứng tôi phát triển đã giúp hỗ trợ đắc lực cho việc định hình logic xử lý nguồn của dự án. Nhật ký Validation CP5 cũng được hoàn thành với các feedback thực tế hữu ích.
- **Phần chưa đạt:** Bộ skill phụ trợ đôi khi vẫn còn bỏ sót một số bằng chứng nếu tài liệu nguồn quá dài hoặc có cấu trúc phức tạp. Trong thời gian ngắn, tôi chưa kịp tối ưu hóa hoàn toàn khả năng chia nhỏ tài liệu để xử lý triệt để vấn đề này.

## 5. Bài học cá nhân

- **Nói chuyện với User là ưu tiên số 1:** Ý tưởng ban đầu dù hay đến mấy cũng vô nghĩa nếu nó không giải quyết nỗi đau thật sự của người dùng. Việc đi phỏng vấn sớm đã cứu nhóm khỏi việc lãng phí thời gian code một tính năng không ai cần.
- **Prompt Engineering là một quá trình liên tục:** Việc xây dựng một bộ skill AI không chỉ đơn giản là viết một đoạn văn ra lệnh, mà là quá trình thử nghiệm, fail, và tìm cách rào (guardrail) liên tục để kiểm soát tính ngẫu nhiên của model.

## 6. Nếu làm lại

Nếu được làm lại từ đầu, tôi sẽ:
1. **Validation sớm hơn nữa:** Không đợi đến CP5 mới cho người ngoài dùng thử sản phẩm. Tôi sẽ mang ngay các mock-up/bản nháp đầu tiên của giao diện đến hỏi các Lab Coach để tiết kiệm thời gian chỉnh sửa luồng làm việc.
2. **Quản lý log phỏng vấn hệ thống hơn:** Xây dựng một form mẫu (template) đánh giá thống nhất ngay từ đầu để việc tổng hợp dữ liệu giữa các thành viên diễn ra trơn tru hơn.
3. **Đào sâu hơn vào bộ skill AI:** Tôi sẽ dành thêm thời gian để hoàn thiện kỹ thuật trích xuất thông tin cho tài liệu dài, đảm bảo không bỏ sót bất kỳ bằng chứng nào.
