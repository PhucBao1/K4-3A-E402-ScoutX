# Nhật ký Phỏng vấn & Bằng chứng Nhu cầu (Interview Logs & Evidence)

> **Mục đích:** Ghi nhận nguyên văn các cuộc phỏng vấn thật theo phương pháp **The Mom Test** để làm căn cứ bằng chứng (Evidence) cho AI Spec (§1, §2) của dự án **ScriptScout (Track C3)**.  
> **Người thực hiện:** Nguyễn Việt Dũng (2A202602533) & Nguyễn Văn Biển (2A202602416)  
> **Thời gian:** Tối 16/09/2026  
> **Đối tượng phỏng vấn:** Các Lab Coach kiêm thành viên Studio Team sản xuất bài giảng của khoá học AI Thực Chiến.

---

## 📌 Phương pháp phỏng vấn (The Mom Test)
- **Không** hỏi ý kiến tương lai ("Anh có thích một công cụ AI như thế này không?").
- **Tập trung** vào hành vi và chi phí thực tế trong quá khứ: Làm mất bao lâu? Bị kẹt ở đâu? Đã dùng những công cụ gì? Tốn bao nhiêu thời gian duyệt và sửa?

---

## 👤 Phỏng vấn #1: Khảo sát quy trình & Thời gian viết kịch bản

* **Thời gian:** 19:15, ngày 16/09/2026
* **Đối tượng:** Lab Coach kiêm Thành viên Studio Team (Chuyên trách sản xuất nội dung bài giảng)
* **Hình thức:** Phỏng vấn trực tiếp tại khu vực Lab / Studio

### Ghi chép chi tiết:
1. **Quy mô kịch bản video bài giảng:**
   - Một video bài giảng ngắn trung bình từ **3 – 5 phút**.
   - Độ dài kịch bản yêu cầu từ **35 – 50 câu kịch bản** (lời đọc rõ ràng, đúng nhịp giảng).
2. **Thời gian sản xuất thực tế:**
   - Tổng thời gian từ lúc bắt đầu viết đến khi duyệt xong: **~8 tiếng**.
   - **Thời gian viết kịch bản:** Mất **5 tiếng** (trong đó giai đoạn dựng khung và nội dung chính mất khoảng **2.5 tiếng**).
   - **Thời gian duyệt kịch bản:** Mất **3 tiếng**.
3. **Thực trạng sử dụng công cụ:**
   - Đã có ứng dụng AI để sinh văn bản nhưng vẫn phải chỉnh sửa thủ công rất nhiều.
   - **Nỗi đau lớn nhất khi viết:** Phải **tự tìm kiếm thuật ngữ bên ngoài** trên mạng, sau đó quay lại đối chiếu và chỉnh sửa kịch bản bằng tay vì AI không có nguồn đối chiếu tin cậy.
   - Về kiểm duyệt: Team có một đội riêng chuyên tự duyệt kịch bản.
4. **Trăn trở lớn nhất:**
   - *"Làm gì để cải thiện thời gian viết kịch bản?"* (Hiện tại 5h viết + 3h duyệt là quá dài so với tốc độ ra bài).

---

## 👤 Phỏng vấn #2: Khảo sát công cụ AI & Luồng QA/QC kiểm duyệt

* **Thời gian:** 19:30, ngày 16/09/2026
* **Đối tượng:** **Thái Hoàng** — Lab Coach kiêm Thành viên Studio Team
* **Hình thức:** Phỏng vấn trực tiếp tại khu vực Lab

### Ghi chép chi tiết:
1. **Công cụ AI đang sử dụng cho kịch bản:**
   - Dùng **Claude** để tạo kịch bản từ slide và ghi chú nội dung.
   - Để kiểm tra chéo: Dùng **Codex** review lại kịch bản do Claude viết để chấm chéo (cross-check), xem có mâu thuẫn hay sai sót thuật ngữ không.
2. **Quy trình duyệt và nhược điểm hiện tại:**
   - Quy trình phản hồi: *"Làm hết từ đầu đến cuối mới feedback"* $\rightarrow$ Nếu kịch bản bị lệch hoặc hiểu sai ý từ đầu thì toàn bộ công đoạn sau (dựng video, animation) phải làm lại, lãng phí tài nguyên.
3. **Toàn bộ pipeline sản xuất video hiện tại:**
   - **Đầu vào (Input):** File slide + Nội dung bài giảng + Prompt quy định thời lượng.
   - **Tạo video bằng AI:** AI viết kịch bản $\rightarrow$ AI tạo animation video $\rightarrow$ tổng hợp và render ra video hoàn chỉnh.
4. **Khâu kiểm soát chất lượng (QA/QC):**
   - Hiện tại: Vẫn phải có con người xem lại từng đoạn, feedback lỗi thủ công + AI tự nghe/kiểm tra lại để xử lý khi phát hiện lỗi lệch giữa âm thanh và kịch bản.
   - **Nhu cầu cấp thiết:** Cần xây dựng **luồng QA tự động hoá** để giải phóng sức người ở khâu hậu kiểm.

---

## 📊 Tổng hợp Bằng chứng (Evidence Synthesis cho R1)

### 1. Số liệu thực tế (Hard Metrics)
- **$n = 2$** thành viên Studio Team kiêm Lab Coach trực tiếp xác nhận 100% về nỗi đau thời gian sản xuất kịch bản.
- **Thời gian tốn kém:** Mỗi video 3-5 phút (35-50 câu) tiêu tốn **5 giờ viết** + **3 giờ duyệt** = **8 giờ/video**.
- **Điểm nghẽn:** Người viết phải tự tra cứu thuật ngữ ngoài mạng để sửa kịch bản; khâu kiểm duyệt phải dùng 2 AI (Claude + Codex) chấm chéo nhưng vẫn phải duyệt tay cuối cùng.

### 2. Danh sách Trích dẫn nguyên văn (Verbatim Quotes cho `spec.md` §1)
1. *"Thời gian viết đến lúc duyệt — viết 5h (nhưng tầm 2.5h dựng chính) + duyệt 3h."* — (Studio Team Coach)
2. *"Video 3-5p cần từ 35-50 câu kịch bản."* — (Studio Team Coach)
3. *"Có dùng AI nhưng phải tự tìm kiếm thuật ngữ bên ngoài rồi chỉnh lại kịch bản."* — (Studio Team Coach)
4. *"Review lại kịch bản: Claude tạo kịch bản + Codex review lại kịch bản chấm chéo."* — (Lab Coach Thái Hoàng)
5. *"Quy trình hiện tại là làm hết từ đầu đến cuối mới feedback."* — (Lab Coach Thái Hoàng)
6. *"Đoạn QA QC con người feedback + AI tự nghe và xử lý khi lỗi... cần luồng QA tự động hoá."* — (Lab Coach Thái Hoàng)
