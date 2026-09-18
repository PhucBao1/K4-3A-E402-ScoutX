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
* **Đối tượng:** **Hải DM** — Lab Coach kiêm Thành viên Studio Team (Chuyên trách sản xuất nội dung bài giảng)
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
* **Đối tượng:** **Thành Phạm** — Lab Coach kiêm Thành viên Studio Team
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

### 1b. Mining bổ sung từ tài liệu C3 do BTC cấp

> Mục tiêu: bổ sung evidence chuẩn B cho Track C, vì nhóm mới phỏng vấn được 2 Lab Coach/Studio team, chưa đủ ngưỡng phỏng vấn riêng của Track C là ≥3 người. Mining này dùng tài liệu thật/fixture chính thức của BTC trong `K4-3A-Day05-06-AI-Product-Hackathon/data/studio-pack/c3-scriptscout/`, không commit dữ liệu gốc vào repo nộp bài.

**Nguồn mining & cách đếm kiểm lại được**

1. Đọc `data/studio-pack/c3-scriptscout/README.md` để lấy pain gốc, sản phẩm tối thiểu và các tình huống khó của đề C3.
2. Đếm bằng script Python trên 3 file fixture chính thức:
   - `vi-du/kich-ban-d1.md`
   - `vi-du/ho-so-nguon-mau.json`
   - `vi-du/kich-ban-co-nguon.json`
3. Command kiểm lại:

```bash
python3 - <<'PY'
from pathlib import Path
import json, re
base = Path("data/studio-pack/c3-scriptscout")
script_md = (base / "vi-du/kich-ban-d1.md").read_text()
print("script_sentences_md", len(re.findall(r"^### Câu ", script_md, re.M)))
print("stops_md", len(re.findall(r"^- \\*\\*Dừng:", script_md, re.M)))
source = json.loads((base / "vi-du/ho-so-nguon-mau.json").read_text())
print("sources", len(source["nguon"]))
print("thongTin", len(source["thongTin"]))
print("removed_sources", sum(1 for s in source["nguon"] if s.get("trangThai") == "bi-loai"))
print("low_trust", sum(1 for s in source["nguon"] if s.get("doTinCay") == "thap"))
print("warning_sources", sum(1 for s in source["nguon"] if s.get("canhBao")))
print("unverified_info", sum(1 for t in source["thongTin"] if t.get("trangThai") == "chua-xac-minh"))
linked = json.loads((base / "vi-du/kich-ban-co-nguon.json").read_text())
print("linked_sentences", len(linked.get("cau", [])))
print("linked_with_sources", sum(1 for c in linked.get("cau", []) if c.get("nguon")))
print("total_source_refs", sum(len(c.get("nguon") or []) for c in linked.get("cau", [])))
PY
```

**Kết quả đếm**

| Quan sát mining | Kết quả | Ý nghĩa với ScriptScout |
|---|---:|---|
| Kịch bản mẫu đã phát hành thật | 40 câu + 1 khoảng dừng | Sản phẩm cần ra kịch bản đọc thành lời theo từng cảnh, không phải báo cáo văn bản ngắn |
| Hồ sơ nguồn mẫu | 5 nguồn, 6 thông tin | Người duyệt cần một hồ sơ nguồn riêng, không chỉ danh sách link cuối bài |
| Nguồn bị loại trong hồ sơ mẫu | 1/5 nguồn | Workflow duyệt nguồn/loại nguồn là nhu cầu thật trong thiết kế đề |
| Nguồn độ tin cậy thấp | 1/5 nguồn | Không phải nguồn nào tìm được cũng đáng tin |
| Nguồn có cảnh báo lỗi thời | 1/5 nguồn | Chủ đề AI thay đổi nhanh, cần cảnh báo nguồn cũ |
| Thông tin chưa xác minh | 1/6 thông tin | Có thông tin chỉ có 1 nguồn, phải đánh dấu chưa xác minh thay vì nói chắc |
| Câu mẫu đã nối nguồn | 7/7 câu trong `kich-ban-co-nguon.json` có `nguon` | Tiêu chí "bấm vào câu thấy chứng minh" là thao tác chấm thật của C3 |

**Ví dụ nguyên văn từ tài liệu BTC**

1. *"Hiện nay người biên soạn phải tự đọc tài liệu, tự tra cứu trên mạng rồi tự viết."* — `data/studio-pack/c3-scriptscout/README.md`
2. *"khi đưa cho người khác duyệt thì không ai kiểm được câu nào lấy từ đâu, vì danh sách nguồn chỉ được liệt kê ở cuối tài liệu."* — `data/studio-pack/c3-scriptscout/README.md`
3. *"Thiếu tư liệu thì người viết dễ đưa vào những con số hoặc ví dụ không có thật."* — `data/studio-pack/c3-scriptscout/README.md`
4. *"Riêng chủ đề AI còn thay đổi từng tháng, nên một thông tin đúng lúc viết có thể đã cũ khi video lên sóng."* — `data/studio-pack/c3-scriptscout/README.md`
5. *"Số liệu quan trọng cần ít nhất hai nguồn độc lập xác nhận, nếu không thì phải đánh dấu là chưa kiểm chứng."* — `data/studio-pack/c3-scriptscout/README.md`
6. *"Mỗi câu có thể là khoảng lặng"* và *"Không có chữ số."* — `data/studio-pack/c3-scriptscout/mau-kich-ban.md`, cho thấy output cần đúng luật kịch bản đọc thành tiếng, không chỉ đúng nội dung.

**Kết luận mining:** tài liệu/fixture chính thức của BTC xác nhận đúng pain nhóm chọn: người viết cần kịch bản có nguồn truy từng câu, người duyệt cần xem/loại nguồn, và hệ thống phải xử lý nguồn cũ, nguồn kém tin cậy, thông tin chưa xác minh. Phần phỏng vấn n=2 cho số đo thời gian thật; phần mining này bổ sung bằng chứng kiểm lại được từ tài liệu/fixture C3.

### 2. Danh sách Trích dẫn nguyên văn (Verbatim Quotes cho `spec.md` §1)
1. *"Thời gian viết đến lúc duyệt — viết 5h (nhưng tầm 2.5h dựng chính) + duyệt 3h."* — (Lab Coach Hải DM)
2. *"Video 3-5p cần từ 35-50 câu kịch bản."* — (Lab Coach Hải DM)
3. *"Có dùng AI nhưng phải tự tìm kiếm thuật ngữ bên ngoài rồi chỉnh lại kịch bản."* — (Lab Coach Hải DM)
4. *"Review lại kịch bản: Claude tạo kịch bản + Codex review lại kịch bản chấm chéo."* — (Lab Coach Thành Phạm)
5. *"Quy trình hiện tại là làm hết từ đầu đến cuối mới feedback."* — (Lab Coach Thành Phạm)
6. *"Đoạn QA QC con người feedback + AI tự nghe và xử lý khi lỗi... cần luồng QA tự động hoá."* — (Lab Coach Thành Phạm)
