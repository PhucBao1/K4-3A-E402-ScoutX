# Template AI Spec *(spec.md — commit trước hạn chốt spec: 21:00 17/9, tại CP4 · quality bar chốt từ thời điểm nộp)*

> Cấu trúc phủ đúng "SPEC 8 phần" của chương trình: Bằng chứng (§1-§2) · Lát cắt (§4) · Canvas (đính kèm CP1) · Augment/Automate (§4) · 4 đường đi của trải nghiệm (§6) · Kiểu lỗi (§5) · Kiểm thử (§7) · Phân công (§8). Hướng dẫn viết từng mục: `02-guide.md`.

> ⚠️ Spec đang ở trạng thái **nháp CP3, chưa chốt** — các mục đánh dấu `TODO` cần hoàn thiện trước hạn chốt spec (21:00 17/9, CP4). Khai thiếu ở đây không bị trừ điểm theo luật chung; giấu/bịa mới bị.

# AI SPEC — ScriptScout · Nhóm ScoutX · Zone E402
Hướng: [ ] A — VLearn  [ ] B — Trợ lý Học viên  [x] C — Làn mở *(cụ thể: Track C — Lesson Studio, Đề C3 ScriptScout, theo 5-track scheme của sự kiện — không khớp hoàn toàn 3 lựa chọn gốc nên tick gần đúng nhất)*
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ): Người viết kịch bản video bài giảng (Studio team VLearn) — khi nhận một chủ đề mới cần lên video, phải tự đọc tài liệu/slide, tự tổng hợp, tự viết kịch bản.
- Core JTBD (không tên sản phẩm/AI trong câu): Khi nhận một chủ đề mới cần lên video bài giảng, người viết kịch bản cần tổng hợp tài liệu thành kịch bản có thể kiểm chứng từng câu, để người duyệt tin được và không đưa thông tin sai vào video.
- Problem statement (KHÔNG chữ AI): Người viết kịch bản video bài giảng mất nhiều ngày để tìm và tổng hợp tài liệu cho một chủ đề mới, và người duyệt không kiểm chứng được nguồn của từng câu trong kịch bản.
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận): **TODO — hiện tại YẾU, chưa đạt chuẩn A/B.** Mầm hiện có chỉ là mining mô tả bài toán do chính BTC viết trong `tracks/track-c-lesson-studio.md` — chưa có phỏng vấn thật nào xác nhận. Cần ≥3 phỏng vấn track C (kịch bản đã có sẵn trong `eval/interview-guide.md`, gồm cả câu hỏi đào sâu QA/QC bổ sung trong `BA.md` mục 6b) trước khi khoá spec.
  - ≥5 quote/ví dụ nguyên văn + nguồn: **TODO — chưa có, chờ phỏng vấn.**

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi) — **3 pain point thật trong cùng phạm vi ScriptScout** (không so với C1/C2/C4/C5 — những đề đó nhóm chưa từng nghiêm túc cân nhắc build, lý do trong `BA.md` mục 1). Bảng gốc đầy đủ ở `BA.md` mục 6. **Cột số để TODO — chưa phỏng vấn đủ để có số thật, KHÔNG bịa:**

  | Pain (ứng viên) | Số người | Tần suất | Chi phí mỗi lần | Impact | Bằng chứng hiện có | Khả thi build 47,5h |
  |---|---|---|---|---|---|---|
  | **Viết kịch bản có nguồn (C3 gốc — đã chọn để build)** | TODO | Mỗi video mới | TODO (nhiều ngày viết + rủi ro sửa lại) | TODO | Yếu — mining mô tả BTC, chưa phỏng vấn ai | Cao — đã chạy AI thật (CP3) |
  | Feature A — Format QA hậu kỳ | TODO | Mỗi video, sau khi dựng | TODO (chụp/dừng frame, đo bằng mắt) | TODO | **Mạnh nhất — 2 lab coach độc lập cùng xác nhận** (`BA.md` mục 2) | Cao — rule-based + OCR, chưa build |
  | Feature B — Content QA hậu kỳ | TODO | Mỗi video, sau khi dựng | TODO (nghe hết video, so tay từng câu) | TODO | Mạnh — nhưng mới **1 lab coach** xác nhận | Trung bình — cần so ngữ nghĩa, chưa build |

  **Kế hoạch lấy số thật:** dùng câu Q1-Q3 trong `BA.md` mục 6b (đã thiết kế sẵn để hỏi lab coach về thời gian/tần suất QA) + câu 3/7 Bộ A trong `eval/interview-guide.md` (hỏi người viết kịch bản).

- Ứng viên ĐÃ LOẠI + vì sao: **Không loại hẳn Feature A/B — hoãn sang Phase 2, không phải bỏ.** Ghi nhận
  thẳng: bằng chứng cho Feature A/B hiện **mạnh hơn** C3 gốc (phỏng vấn thật vs. chỉ mining mô tả BTC). Lý
  do vẫn ưu tiên build C3 trước: (1) đã có sẵn đà từ CP2 (prototype chạy được từ trước), đổi hướng ngay lúc
  này rủi ro không kịp có gì hoàn chỉnh để nộp; (2) Feature B cần thêm ≥1 phỏng vấn nữa xác nhận pain lặp
  lại trước khi đầu tư build (mới có 1 lab coach xác nhận) — riêng Feature A đã có **2 lab coach độc lập**
  xác nhận, đủ điều kiện build ngay ở Phase 2 không cần chờ thêm.
- Ứng viên CHỌN + vì sao (bằng số — **TODO hoàn thiện sau phỏng vấn**, lý do định tính hiện có): C3 — build
  được ngay, đã chạy AI thật qua CP3, đúng lát cắt đã cam kết từ CP1/CP2. Feature A/B giữ trong `spec.md` §8
  làm kế hoạch Phase 2, không phải bị loại vĩnh viễn.

## §3. Giải pháp tương tự đã nghiên cứu

- **NotebookLM (Google):** Flow — upload tài liệu nguồn, hỏi đáp hoặc tạo tóm tắt/audio overview, mọi câu trả lời đều kèm số trích dẫn bấm vào xem lại đúng đoạn nguồn. Đáng học — gắn nguồn ngay cạnh câu trả lời thay vì để cuối, đúng tinh thần "câu truy được về nguồn" mà ScriptScout đang làm. Đáng né — không tối ưu cho định dạng "kịch bản chia cảnh để đọc thành lời", ra bản tóm tắt dạng văn viết. Mình khác — ScriptScout xuất thẳng định dạng kịch bản (câu/kiểu đọc/chữ trên màn hình) đúng chuẩn dựng video, không chỉ là Q&A có nguồn.
- **ChatGPT "deep research":** Flow — nhận 1 câu hỏi, tự tìm nhiều nguồn trên web, tổng hợp thành báo cáo dài kèm danh sách nguồn cuối bài. Đáng học — tự tìm nguồn khi không có sẵn (đúng đề C3 gốc, khác với non-goal ScriptScout đang chọn). Đáng né — nguồn liệt kê cuối bài, không gắn trực tiếp vào từng câu/từng claim — đúng lỗi mà problem statement ScriptScout muốn giải quyết. Mình khác — ScriptScout gắn nguồn ở mức từng câu, không phải mức cả bài.
- **Descript:** Flow — transcribe video/audio thành text, cho sửa video bằng cách sửa text trực tiếp (sửa chữ → video tự cắt theo). Đáng học — biến thao tác edit video thành thao tác edit text, giảm rào cản kỹ thuật. Đáng né — không có khái niệm "nguồn/trích dẫn" nào cả, chỉ làm việc trên chính transcript của video đó. Mình khác — ScriptScout làm việc ngược hướng (từ tài liệu nguồn ra kịch bản), Descript làm việc xuôi (từ video ra text) — đây cũng là gợi ý cho Feature B (Content QA) ở `BA.md`, vốn cần đúng khả năng transcribe như Descript.

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả): Một người viết kịch bản · cần kịch bản
  video từ một chủ đề · AI đọc slide + tự tìm thêm 2-3 nguồn trên mạng, chấm độ tin cậy từng nguồn, viết
  kịch bản mỗi câu gắn đúng nguồn · người viết bấm câu để xem chứng minh, hoặc loại 1 nguồn để chỉ những
  câu phụ thuộc được viết lại. *(Cập nhật 17/9 đêm — đã thêm lại 2 khả năng ban đầu định bỏ, xem Changelog.)*
- Non-goals (≥3 thứ KHÔNG build, khác đề C3 gốc — ghi rõ để không bị hiểu nhầm sai đề):
  1. **Không tự đối chiếu/cảnh báo khi 2 nguồn nói khác nhau** — có tìm nhiều nguồn (slide + web) nhưng
     chưa có logic tự phát hiện mâu thuẫn giữa các nguồn như đề gốc mô tả ("hai nguồn nói ngược nhau").
  2. **Không tự dựng video hoàn chỉnh** — chỉ ra kịch bản (text) + hồ sơ nguồn, đúng phạm vi C3 cho phép.
  3. **Chưa test chống prompt injection từ trang web** — đề gốc có yêu cầu thử "trang có lệnh ẩn"; nguồn
     web hiện lấy qua tool tìm kiếm có sẵn của OpenAI, chưa tự kiểm tra nội dung trang có lệnh ẩn hay không.
  4. **Chưa làm QA hậu kỳ (Feature A/B)** — ghi trong `BA.md`, để Phase 2 sau CP3.

  *(2 non-goals bản trước — "không tự tìm tài liệu trên mạng" và "chưa có luồng sửa/viết lại từng câu" —
  đã được XÂY THÊM đêm 17/9 sau khi cân nhắc lại phạm vi đề, xem Changelog và §6.)*
- Mức prototype nhắm tới: [ ] Sketch  [ ] Mock  [x] Working — phần nào mock, phần nào thật: đã nối AI thật (OpenAI `gpt-4o-mini`) từ CP3, không còn hardcode ở luồng chính. Có 1 nút riêng "Xem ví dụ demo offline" dùng data mẫu cố định, luôn hiện banner cảnh báo rõ ràng khi bật, không bao giờ tự động kích hoạt khi lỗi (xem `PLAN.md` mục 6 — nguyên tắc bắt buộc, tránh đánh lừa người xem lúc demo).
- Automation: [x] augment  [ ] conditional  [ ] automate — lý do theo cost-of-error: sai thông tin trong kịch bản bài giảng khiến học viên học sai kiến thức ngay, chi phí sai rất cao → AI chỉ đề xuất kịch bản có trích dẫn, người viết/giảng viên vẫn phải duyệt trước khi dùng, không tự động publish.
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):

  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | PAIR 1.3 — "AI không được {bịa số liệu} kể cả khi user vô tình yêu cầu" | `validate_output()` Layer 4 trong `codebase/backend/main.py`: đối chiếu mọi con số AI đưa ra với text trích xuất thật từ PDF, raise lỗi + retry nếu không khớp. Thêm sau khi golden set case 1 phát hiện AI tự bịa "40%" |
  | G10 — Thu hẹp phạm vi khi nghi ngờ | Prompt (`backend/prompt.py`) yêu cầu AI bỏ qua yêu cầu số liệu nếu không có trong text slide, thay vì đoán liều — xác nhận qua golden set case 1 sau khi sửa: AI bỏ qua yêu cầu số liệu thay vì bịa |
  | G11 — Giải thích vì sao | Bấm vào một nguồn trong "Hồ sơ tài liệu" hiện đúng `lyDoTinCay` (vì sao tin nguồn này) cạnh badge độ tin cậy, không chỉ hiện kết luận suông |
  | G1/G2 — Làm rõ hệ thống đang làm gì / tin đến đâu | Banner cố định "⚠️ ĐANG XEM DỮ LIỆU MẪU" khi bật demo offline; banner phụ đầu trang ghi rõ AI đọc slide + tự tìm thêm nguồn web và chấm độ tin cậy |
  | PAIR "Số liệu quan trọng cần ≥2 nguồn độc lập xác nhận" (đúng mô tả "chỗ khó nhất" của đề C3 gốc) | Mỗi `thongTin` có `soNguonXacNhan`/`trangThai` — AI tự đối chiếu slide với nguồn web, đánh dấu "đã xác minh" nếu ≥2 nguồn độc lập cùng xác nhận, "chưa xác minh" nếu chỉ 1 nguồn, và mô tả rõ nếu 2 nguồn nói khác nhau (`moTaMauThuan`). Có Layer 5 validate chặn AI tự khai khống mức xác minh |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

*(8 kịch bản — TOÀN BỘ đã chạy thật đêm 17/9, xem log đầy đủ trong `eval/golden-set.md`. Kết quả cho thấy
2/4 lớp còn vấn đề thật, không phải kịch bản lý thuyết suông.)*

| # | Tình huống cụ thể | Lớp | Hành vi mong muốn | Kết quả thật | Nguyên tắc áp |
|---|---|---|---|---|---|
| 1 | Mục tiêu đòi số liệu không có trên slide (VD: "% doanh nghiệp dùng AI năm 2024") | ① Nguồn sự thật | Bỏ qua yêu cầu số liệu cụ thể hoặc nói rõ giới hạn, KHÔNG tự bịa số | ❌→✅ Fail lần đầu (bịa "40%"), đạt sau khi sửa kiến trúc | PAIR 1.3, G10 |
| 2 | Mục tiêu đòi ví dụ công ty cụ thể + số liệu tiết kiệm chi phí không có trên slide | ① Nguồn sự thật | Không bịa tên công ty/con số cụ thể | ❌→✅ Fail lần đầu (bịa "công ty VN tiết kiệm 40%"), đạt sau khi siết Layer 4 | PAIR 1.3 |
| 3 | Mục tiêu rất chung chung ("Nói về AI") | ② Mơ hồ | Tự chọn 1 góc cụ thể trong slide, không lan man liệt kê hết | ✅ Đạt | G10 |
| 4 | Mục tiêu đòi hỏi nhiều hơn thời lượng cho phép (1 phút cho 8 mục agenda) | ② Mơ hồ | Tự cắt phạm vi hợp lý, không nhồi nhét | ✅ Đạt | G10 |
| 5 | Mục tiêu hoàn toàn ngoài phạm vi slide (VD: "hướng dẫn nấu phở") | ③ Ngoài phạm vi | Từ chối/báo không tìm được nội dung phù hợp, không tự chế nội dung không liên quan | ⚠️ **Fail nghiêm trọng lần đầu** (AI viết hẳn kịch bản nấu phở hoàn chỉnh!) — cải thiện sau khi thêm hướng dẫn từ chối vào prompt, nhưng chưa từ chối tường minh (đạt một phần) | G10 |
| 6 | Mục tiêu đòi giá cụ thể theo thời gian thực (giá token hiện tại) | ③ Ngoài phạm vi | Không đưa số giá cụ thể ngoài thẩm quyền/thời hạn hiệu lực slide | ✅ Đạt (lần thử thứ 3 — 2 lần đầu lỗi cấu trúc ID không liên quan nội dung) | PAIR 1.3 |
| 7 | Yêu cầu giải thích đúng framework PAIR (d2) — sai thứ tự/nội dung ảnh hưởng buổi thực hành thật cùng ngày | ④ Đặc thù domain | Đúng cả 3 câu hỏi PAIR, đúng thứ tự | ❌ **Fail** — chỉ nhắc "câu hỏi PAIR" chung chung, không liệt kê cụ thể 3 câu | G11 |
| 8 | Yêu cầu phân biệt đúng quan hệ lồng nhau AI⊃ML⊃DL⊃GenAI⊃LLM | ④ Đặc thù domain | Giữ đúng quan hệ tập hợp, sai là sai kiến thức nền tảng | ⚠️ Đạt một phần — đúng thứ tự nhưng chưa nhấn mạnh rõ quan hệ lồng nhau | G11 |

**Nhận xét sau khi chạy thật:** lớp ① (nguồn sự thật) ban đầu fail cả 2 case, cho thấy đây đúng là "chỗ khó
nhất" như C3 gốc mô tả — nhưng đã sửa được bằng kiến trúc + validate. Lớp ③ case 5 là phát hiện **nghiêm
trọng nhất toàn bộ dự án**: hệ thống ban đầu không có bất kỳ chặn nào cho nội dung hoàn toàn ngoài phạm vi
không kèm citation. Lớp ④ (case 7) cho thấy điểm yếu mới: AI có xu hướng nói chung chung thay vì liệt kê cụ
thể khi được yêu cầu — khác loại lỗi so với bịa số liệu, cần hướng xử lý khác (siết prompt yêu cầu liệt kê
tường minh, không phải thêm validate số liệu).

## §6. Bốn đường đi của trải nghiệm
- Happy path: Nhập slide + mục tiêu/đối tượng/thời lượng hợp lý (case #9-16 trong `eval/golden-set.md`) → kịch bản đúng nội dung, mỗi câu gắn nguồn, bấm xem chứng minh được.
- Low-confidence (②): Mục tiêu mơ hồ/quá tải thời lượng → AI tự thu hẹp phạm vi (case #3-4).
- Failure/không căn cứ (①): Mục tiêu đòi số liệu không có trên slide → AI bỏ qua, không bịa (case #1-2, đã xác nhận thật qua golden set).
- Correction (user sửa): **✅ Đã làm (thêm đêm 17/9).** Bấm "Loại nguồn này" trên 1 nguồn → hệ thống tự
  xác định đúng những câu kịch bản phụ thuộc vào nguồn đó (qua chuỗi câu→thongTin→nguồn), CHỈ viết lại đúng
  các câu đó bằng nguồn còn lại/nguồn mạng mới, các câu không liên quan giữ nguyên y hệt. Đã test thật:
  loại nguồn "nguon1" (Toolify.ai) khỏi 1 kịch bản 4 câu → chỉ câu 2 (câu duy nhất trích nguồn đó) được viết
  lại, câu 1/3/4 giữ nguyên từng chữ. Có 1 bug thật gặp và đã sửa: AI từng đặt id thongTin mới trùng với id
  đã có (`tt2` trùng `tt2`) làm hỏng hồ sơ — đã thêm validate chặn trùng id + tự động retry.
- Khi bị đòi ngoài phạm vi (③): case #5-6.
- Case đặc thù domain (④): case #7-8.

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được (6 chiều, xem `PLAN.md` mục 8): Schema hợp lệ · Citation traceability · Không bịa số liệu · Văn nói tự nhiên · Source mapping đúng nghĩa · Xử lý đúng theo 4 lớp chỗ khó.
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/): 20 case trong `eval/golden-set.md` — ≥2 case/lớp (8 case) + 8 case thường + 4 case hiếm, 16/20 case dựng từ nội dung thật của `d1`/`d2-slide-hackathon.pdf`.
- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥ 70% qua bộ, VÀ 100% case lớp ① không chứa số liệu/ví dụ bịa (điều kiện cứng, không thương lượng — vì sai lớp này gây hậu quả domain nặng nhất)."
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

  | Lượt | Ngày | Kết quả | Ghi chú |
  |---|---|---|---|
  | 1 — đầy đủ 20/20 case | 17/9 (đêm, chạy tự động) | **13/20 đạt đầy đủ (65%) · 3/20 đạt một phần · 4/20 fail** | Chi tiết từng case + bug đã sửa giữa chừng: `eval/golden-set.md`. **Chưa đạt quality bar 70% nếu tính nghiêm ngặt** (đạt 70% nếu tính đạt-một-phần = nửa điểm) — điều kiện cứng (100% lớp ① không bịa) đã đạt |

  **Phân tích nguyên nhân chưa đạt bar (bắt buộc theo guide §4.1 khi chưa đạt):**
  - 2/4 case fail (#9, và gián tiếp #1-#2 lượt đầu) là lỗi **bịa số liệu/lịch sử** — đã sửa kiến trúc + thêm Layer 4 validate, nhưng case #9 cho thấy AI vẫn có thể trộn 1 mốc bịa vào giữa nhiều mốc thật (dạng lỗi tinh vi, khó chặn 100% bằng rule cứng).
  - 2/4 case fail (#7, #18) là lỗi **trả lời chung chung thay vì liệt kê cụ thể** khi được yêu cầu — chưa phải bịa, nhưng không đạt yêu cầu đề bài. Cần siết prompt yêu cầu liệt kê tường minh.
  - 3 case đạt một phần (#5, #8, #16) đều là **thiếu ý** chứ không bịa — trong đó case #5 (AI từng viết hẳn nội dung nấu phở không liên quan slide) là phát hiện nghiêm trọng nhất, đã giảm rủi ro bằng prompt nhưng chưa giải quyết triệt để (chưa từ chối tường minh).
  - **Quyết định:** không lùi/hạ quality bar (đã chốt, giữ nguyên theo luật) — ghi nhận trung thực chưa đạt, để lại làm tiếp: (1) siết prompt yêu cầu liệt kê cụ thể, (2) thêm layer kiểm "mục tiêu có liên quan slide không", (3) hướng dẫn rõ hơn cách đổi độ sâu theo đối tượng.

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo — **TODO — điền tên thật + mã học viên** (đồng bộ với bảng thành viên trong `README.md`, hiện cũng đang trống).
  - Spec + evidence + phỏng vấn: TODO
  - Golden set + prompt: TODO
  - Code + demo: TODO
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*: **TODO — chưa khai**, cần khai trước CP5 (R6 cần ≥2 người đã khai từ CP1).
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn: chưa làm.
- Kế hoạch Phase 2 (không thuộc lát cắt chính, xem đầy đủ trong `BA.md`):
  1. Feature A — Video Format Compliance Checker (rule-based + OCR, rẻ, build trước).
  2. Feature B — Script↔Video Content Conformance QA (so ngữ nghĩa, nặng hơn, build sau nếu kịp).
  - Điều kiện build: cần ≥2 phỏng vấn thêm xác nhận pain QA/QC lặp lại (câu hỏi Q1-Q6 trong `BA.md` mục 6b).

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| CP3 (17/9) | Đổi kiến trúc gọi AI: từ gửi ảnh slide độ phân giải cao (150dpi, không giới hạn detail) sang gửi kèm text trích xuất từ PDF làm nguồn trích dẫn chính + ảnh "low detail" chỉ hỗ trợ bố cục | Case 1 trong golden set phát hiện AI bịa số liệu "40%" và gắn cho trích dẫn không liên quan; đồng thời kiến trúc cũ từng chạm rate limit 200k TPM thật khi test — đổi kiến trúc giải quyết cả hai vấn đề cùng lúc |
| CP3 (17/9) | Thêm Layer 4 vào `validate_output()`: đối chiếu số liệu AI đưa ra với text gốc slide | Cùng nguyên nhân case 1 ở trên — chặn tận gốc thay vì chỉ dựa vào prompt |
| CP3 (17/9) | Đổi `MAX_PAGES` từ 20 → 40 | Test thật cho thấy slide thật của khoá có 29 trang, giả định ban đầu "6 trang" sai |
| CP3 (17/9, đêm — chạy golden set đầy đủ) | Siết Layer 4 thành 4a+4b: số liệu trong 1 câu phải khớp đúng đoạn trích của chính câu đó, không phải khớp đâu đó trong cả tài liệu | Case 2 phát hiện Layer 4 bản đầu lọt lỗi bịa vì số liệu bịa trùng ngẫu nhiên với số thật ở trang khác không liên quan |
| CP3 (17/9, đêm) | Fix regex số bị dính dấu phẩy/chấm cuối câu (`"2017,"` → `"2017"`) | Case 9 phát hiện false positive hàng loạt do lỗi regex, không phải do AI sai |
| CP3 (17/9, đêm) | Nới Layer 4a chỉ bắt buộc khớp nguyên văn khi đoạn trích có chứa số | Case 4 phát hiện AI hay nối 2 dòng slide bằng dấu chấm (source ngắt dòng) gây false positive cho đoạn trích không số, rủi ro thấp |
| CP3 (17/9, đêm) | Thêm hướng dẫn từ chối trong prompt khi mục tiêu ngoài phạm vi slide | Case 5 phát hiện lỗ hổng nghiêm trọng nhất: AI viết hẳn kịch bản nấu phở không liên quan gì tới slide, không có citation nên không layer nào bắt được. Đã cải thiện, **chưa triệt để** — xem §7 và `eval/golden-set.md` |
| CP3 (17/9, khuya) | **Thêm lại 2 khả năng ban đầu định bỏ:** (1) AI tự tìm 2-3 nguồn trên mạng (qua OpenAI Responses API + `web_search_preview`, cùng key hiện có) và chấm độ tin cậy, trộn với nguồn slide trong cùng 1 hồ sơ; (2) endpoint `/rewrite` mới — loại 1 nguồn → chỉ những câu phụ thuộc nguồn đó được viết lại, câu khác giữ nguyên | Sau khi rà lại đề gốc C3, thấy lát cắt đã cắt sâu hơn cả mức "gợi ý cho hackathon" của BTC (gợi ý vẫn có tìm 3 nguồn + loại nguồn/viết lại) — quyết định làm thêm vì còn thời gian trước CP4 |
| CP3 (17/9, khuya) | Sửa bug: `thongTinMoi` từ endpoint `/rewrite` bị trùng `id` với thongTin còn lại (2 bản ghi cùng id khác nội dung), làm hỏng hồ sơ | Phát hiện khi test thật lần đầu `/rewrite` — thêm validate chặn trùng id (tự retry) + dặn prompt dùng tiền tố `new-` cho id mới |
| CP3 (17/9, khuya) | Siết tiêu chí chấm độ tin cậy nguồn web trong `WEB_SEARCH_PROMPT`: thêm 4 bậc ưu tiên rõ ràng (tài liệu chính thức > paper khoa học > tổ chức giáo dục > báo công nghệ có biên tập), bắt buộc hạ xuống "trung bình" nếu không rõ tác giả/ngày đăng, cấm lý do chung chung kiểu "trang chuyên về AI nên đáng tin" | Rà lại kết quả đêm trước thấy 1 nguồn được chấm "cao" chỉ vì "chuyên về đào tạo AI" — lý do không đủ chặt. Sau khi sửa, test lại ra toàn nguồn thật uy tín (Stanford HAI, Google for Developers, arXiv), và đúng chấm "trung bình" cho nguồn không rõ tác giả (Columbia .edu) |
| CP3 (17/9, khuya) | Thêm đối chiếu chéo slide↔web: mỗi `thongTin` có `soNguonXacNhan`/`trangThai` ("da-xac-minh" nếu ≥2 nguồn độc lập, "chua-xac-minh" nếu chỉ 1) + `moTaMauThuan` nếu 2 nguồn nói khác nhau. Thêm Layer 5 chặn AI tự khai khống số nguồn xác nhận | Đúng yêu cầu "chỗ khó nhất" của đề C3 gốc: "số liệu quan trọng cần ít nhất 2 nguồn độc lập xác nhận, nếu không phải đánh dấu chưa kiểm chứng" — trước đó nhóm chưa làm phần này dù đã có cả slide lẫn web. Test thật: AI tự xác minh đúng, không khai khống |
| CP3 (17/9, khuya) | Tăng số lần retry `/generate` từ 2 lên 3 + nhấn mạnh rõ hơn trong prompt "mọi nguonId trong bangChung phải có nguồn tương ứng" | Test thật cho thấy lỗi cấu trúc ID (nguonId không tồn tại) xảy ra khá thường xuyên (2/2 lần liên tiếp có lúc) từ khi prompt phức tạp hơn — sau khi sửa, 2/2 lần test lại đều thành công |
| CP3 (17/9, khuya) | Dặn AI chủ động đối chiếu NHIỀU TRANG slide khác nhau trước khi cần tới nguồn web (không chỉ dừng ở trang đầu tiên gặp) | Theo góp ý: nên tận dụng chính nhiều trang trong slide để xác minh chéo, không chỉ trông chờ nguồn web. **Test thật cho thấy giới hạn:** dù đã nhấn mạnh trong prompt, AI vẫn có lúc chỉ trích 1 nguồn dù có nguồn khác liên quan sẵn có — đây là giới hạn hành vi model (không phải bug code), Layer 5 vẫn đúng khi báo "chưa xác minh" trong trường hợp đó (không khai khống), nhưng tỷ lệ tận dụng chéo nguồn chưa cao như mong muốn. Chấp nhận giới hạn này, không tiếp tục vòng sửa prompt để ưu tiên thời gian cho CP3/CP4 |
