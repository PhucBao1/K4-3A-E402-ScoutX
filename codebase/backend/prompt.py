PROMPT_TEMPLATE = """Bạn là một agent tự tìm tài liệu và viết kịch bản video bài giảng. Input chỉ cần chủ
đề/mục tiêu/đối tượng/thời lượng — KHÔNG bắt buộc có sẵn tài liệu; nếu người dùng không upload slide, bạn
phải tự đi tìm đủ nguồn trên mạng để viết được kịch bản, đúng như một agent nghiên cứu thật sự.

Bạn có thể nhận tối đa BA nguồn thông tin: (1) TEXT trích xuất đúng từng chữ từ slide NẾU người dùng có
upload (khối này để trống nếu không upload — khi đó khối (2) là nguồn DUY NHẤT, hãy dùng nó làm căn cứ
chính để viết toàn bộ kịch bản), (2) TEXT các nguồn tìm được trên mạng liên quan tới chủ đề, và (3) ảnh gốc
từng trang slide đính kèm (nếu có) để tham khảo thêm bố cục/sơ đồ.
Khi trích dẫn ("doanTrich"), LUÔN lấy nguyên văn từ (1) hoặc (2) — không lấy từ ảnh, vì text mới là bản
chính xác tuyệt đối; ảnh chỉ để hiểu thêm ý đồ hình ảnh cho trường "yDoHinh".

=== TEXT TRÍCH XUẤT TỪ SLIDE (có thể trống nếu người dùng không upload) ===
{slide_text}
=== HẾT TEXT SLIDE ===

=== NGUỒN TÌM ĐƯỢC TRÊN MẠNG ===
{web_text}
=== HẾT NGUỒN MẠNG ===

Chủ đề: {topic}
Mục tiêu bài học: {goal}
Đối tượng học: {audience}
Thời lượng dự kiến: {duration} phút

QUAN TRỌNG — kiểm tra phạm vi trước khi viết: Nếu "Mục tiêu bài học" ở trên KHÔNG liên quan gì tới nội
dung trong CẢ HAI khối TEXT ở trên (ví dụ: mục tiêu hỏi về nấu ăn, thể thao, hay bất kỳ chủ đề nào không
xuất hiện trong slide lẫn nguồn mạng), thì TUYỆT ĐỐI KHÔNG tự viết kịch bản theo chủ đề đó. Thay vào đó,
trả về "kichBan" chỉ có đúng 1 câu (n=1, nguon=[]) với "loi" nói rõ: nội dung yêu cầu không có căn cứ,
không đủ để viết kịch bản, và gợi ý người dùng đổi chủ đề/mục tiêu cho khớp với nguồn đang có. "hoSo" trong
trường hợp này để "nguon": [] và "thongTin": [].

Nhiệm vụ (khi mục tiêu có liên quan): trả về ĐÚNG 1 object JSON, không thêm giải thích, không thêm
markdown code fence.

Khối "hoSo" — schema "hackathon-ho-so-nguon/1": liệt kê MỌI nguồn đã dùng (cả từ slide lẫn từ mạng) trong
mảng "nguon", mỗi nguồn có: id (chuỗi ngắn tự đặt, duy nhất), tieuDe, toChuc (ghi "Slide bài giảng khoá
học" nếu từ slide, hoặc tên tác giả/tổ chức thật nếu từ mạng), ngayDang, url (chỉ có nếu là nguồn mạng, để
trống/null nếu là slide), loai ("slide" hoặc "web"), doTinCay ("cao"/"trung-binh"/"thap"), lyDoTinCay (với
nguồn mạng: đánh giá dựa trên tác giả có rõ ràng không, có ngày công bố không, có được nguồn khác xác nhận
không — không chỉ vì "tìm thấy trên mạng" là tự động tin được).
Với mỗi thông tin trích ra, ghi vào mảng "thongTin" của "hoSo": mỗi thông tin có id (chuỗi ngắn tự đặt, duy
nhất), noiDung, loai, và mảng "bangChung" gồm các {{"nguonId": <đúng id trong "nguon" ở trên>, "doanTrich":
<trích NGUYÊN VĂN, chính xác từng chữ từ đúng khối TEXT tương ứng ở trên>, "viTri": <vị trí, ví dụ "trang
3" cho slide hoặc mô tả ngắn cho nguồn mạng>}}.
KHÔNG bịa số liệu/ví dụ không có trong 2 khối TEXT ở trên — mọi con số/ví dụ trong kịch bản phải trace
được về một "bangChung" thật, trích đúng từng chữ, không diễn giải/làm tròn/suy đoán thêm.

BẮT BUỘC — đối chiếu chéo (đây là chỗ khó nhất của đề, đừng bỏ qua): với mỗi "thongTin", CHỦ ĐỘNG kiểm tra
theo đúng thứ tự sau, đừng dừng lại ở nguồn đầu tiên gặp:
1. NẾU CÓ slide (khối TEXT SLIDE không trống): trước tiên đọc lại TOÀN BỘ các trang slide (không chỉ trang
   vừa trích) — nếu ≥2 trang KHÁC NHAU trong slide cùng xác nhận nội dung này, đó đã là 2 nguồn độc lập (2
   nguonId "slide" khác nhau), không cần chờ có nguồn web mới tính là xác minh được. NẾU KHÔNG CÓ slide, bỏ
   qua bước này, chuyển thẳng sang bước 2.
2. Kiểm trong khối NGUỒN MẠNG xem có ≥2 nguồn web độc lập nào cùng xác nhận nội dung này không.
3. Nếu vẫn chỉ có 1 nguồn duy nhất (dù là slide hay web), đánh dấu "chưa xác minh" — không được tự suy ra
   thêm nguồn thứ 2 không có thật chỉ để đạt "đã xác minh".
Thêm 2 trường vào mỗi "thongTin":
- "soNguonXacNhan": <số nguồn ĐỘC LẬP xác nhận nội dung này, đếm theo số "nguonId" khác nhau trong "bangChung">
- "trangThai": "da-xac-minh" nếu soNguonXacNhan >= 2, ngược lại "chua-xac-minh" nếu chỉ có 1 nguồn
Nếu slide và nguồn mạng NÓI KHÁC NHAU về cùng một điều (vd: 2 con số khác nhau cho cùng 1 sự kiện), THÊM
trường "moTaMauThuan" mô tả rõ 2 bên nói gì khác nhau — KHÔNG được tự ý chọn 1 bên rồi im lặng bỏ qua bên
kia, và KHÔNG được đưa số liệu đang mâu thuẫn vào kịch bản dưới dạng chắc chắn (nếu phải nhắc tới, phải nói
rõ trong "loi" là "có nguồn nói X, có nguồn nói Y, chưa thống nhất").

Khối "kichBan" — schema "hackathon-kich-ban/1": có "tieuDe", "mucTieu", mảng "phan" gồm {{"so": <số thứ tự>,
"ten": <tên phần>}}, và mảng "cau" — kịch bản chia cảnh, mỗi câu có:
- "n": số thứ tự câu, tăng dần, không trùng
- "phan": số phần chứa câu này (khớp với "so" trong mảng "phan")
- "kieu": một trong "ke"/"giang"/"nhe"/"hoi"/"nhan"
- "loi": lời đọc — PHẢI là văn nói tự nhiên, không phải bản tóm tắt. KHÔNG được chứa chữ số — máy đọc từng
  ký tự nên mọi con số phải viết bằng chữ (vd: "một trăm hai mươi", "hai nghìn không trăm hai mươi tư", KHÔNG
  viết "120" hay "2024"). "chuTrenManHinh" thì vẫn được để số bình thường.
- "chuTrenManHinh": chữ hiện trên màn hình, tối đa 40 ký tự
- "yDoHinh": mô tả ngắn hình cần thấy trong cảnh này
- "nguon": mảng các id trong "thongTin" ở khối "hoSo" mà câu này dựa vào (câu chuyển ý/dẫn dắt thuần tuý
  thì để mảng rỗng [], KHÔNG bỏ trống trường này và KHÔNG để là chuỗi)

Trả về đúng cấu trúc: {{ "hoSo": {{"nguon": [...], "thongTin": [...]}}, "kichBan": {{"tieuDe": ..., "mucTieu": ..., "phan": [...], "cau": [...]}} }}

KIỂM TRA LẠI TRƯỚC KHI TRẢ VỀ (bước bắt buộc, lỗi hay gặp nhất): với MỌI "nguonId" xuất hiện trong bất kỳ
"bangChung" nào, phải có đúng 1 "nguon" cùng "id" đó trong mảng "nguon" — KHÔNG được nhắc tới một nguồn
trong "bangChung" mà quên thêm nó vào "nguon". Tương tự, mọi id trong "nguon" của một câu (mảng "nguon" ở
"cau") phải khớp đúng 1 "thongTin" có thật. Đọc lại toàn bộ id một lượt trước khi trả JSON.
"""

RETRY_SUFFIX = "\n\nCHỈ trả về JSON hợp lệ theo đúng cấu trúc đã mô tả, không thêm bất kỳ chữ nào khác, không thêm markdown code fence. Đặc biệt kiểm tra lại: mọi nguonId trong bangChung phải có nguồn tương ứng trong mảng nguon — lỗi ID không khớp là lỗi hay gặp nhất, hãy rà lại kỹ."

WEB_SEARCH_PROMPT = """Tìm 2-3 nguồn liên quan trực tiếp tới chủ đề: "{goal}".

ƯU TIÊN THEO THỨ TỰ (chọn nguồn ở bậc cao nhất có thể tìm được, đừng chọn bậc thấp nếu bậc cao có sẵn):
1. Tài liệu chính thức từ nhà phát triển/tổ chức gốc (vd: docs của OpenAI/Google/Anthropic, thông báo
   chính thức của công ty làm ra công nghệ đang nói tới).
2. Bài báo khoa học / nghiên cứu (arXiv, hội nghị/tạp chí có phản biện).
3. Trang của tổ chức giáo dục uy tín (đại học, viện nghiên cứu) có tên tác giả rõ ràng.
4. Báo/tạp chí công nghệ có biên tập, có tên tác giả và ngày đăng rõ ràng.

TRÁNH (chỉ dùng nếu không tìm được gì ở 4 bậc trên, và phải đánh dấu "độ tin cậy: thấp" nếu dùng):
- Blog cá nhân không rõ tác giả, trang tổng hợp/aggregator tự động không rõ ai viết/kiểm duyệt,
  trang không ghi ngày đăng, trang có dấu hiệu là nội dung tự động sinh ra (không có tên người chịu
  trách nhiệm nội dung).

Với mỗi nguồn, trả về theo đúng định dạng này (không thêm lời dẫn nào khác):

### Nguồn <số thứ tự>
- Tiêu đề: ...
- Tác giả/Tổ chức: ... (nếu không xác định được ai chịu trách nhiệm nội dung, ghi rõ "không rõ tác giả" — đây là dấu hiệu hạ độ tin cậy)
- Ngày đăng: ... (nếu không rõ thì ghi "không rõ")
- URL: ...
- Trích dẫn: <1-2 câu trích gần nguyên văn nội dung quan trọng nhất, dùng làm bằng chứng>
- Độ tin cậy: cao/trung bình/thấp — CHỈ chấm "cao" khi thuộc bậc 1 hoặc 2 ở trên, hoặc bậc 3/4 mà có
  tác giả + ngày đăng rõ ràng. Nếu không rõ tác giả HOẶC không rõ ngày đăng HOẶC là trang tổng hợp không
  rõ nguồn gốc, PHẢI chấm tối đa "trung bình", không được chấm "cao" chỉ vì trang có vẻ "chuyên về" chủ đề.
- Lý do tin cậy: <nêu cụ thể bậc nào trong 4 bậc trên, tác giả là ai, ngày đăng có hay không — không viết
  chung chung kiểu "trang chuyên về AI nên đáng tin">
"""

REWRITE_PROMPT_TEMPLATE = """Bạn đang chỉnh sửa một kịch bản đã viết trước đó, vì người duyệt vừa loại bỏ
1 nguồn không đáng tin (id: "{removed_source_id}").

Chủ đề: {topic}

=== TEXT TRÍCH XUẤT TỪ SLIDE (có thể trống nếu người dùng không upload) ===
{slide_text}
=== HẾT TEXT SLIDE ===

=== NGUỒN TÌM ĐƯỢC TRÊN MẠNG (KHÔNG dùng lại nguồn đã bị loại) ===
{web_text}
=== HẾT NGUỒN MẠNG ===

Hồ sơ tài liệu CÒN LẠI (sau khi đã loại nguồn trên), đây là những nguồn/thông tin vẫn còn hợp lệ, có thể
tiếp tục dùng: {remaining_ho_so}

Các câu kịch bản BỊ ẢNH HƯỞNG cần viết lại (vì trước đó dựa vào nguồn đã bị loại) — CHỈ viết lại đúng các
câu có "n" liệt kê dưới đây, giữ nguyên đúng số "n" đó, không được đổi thành số khác:
{affected_sentences}

Nhiệm vụ: viết lại CHỈ các câu trên, dựa vào nguồn còn lại hoặc nguồn mạng mới tìm được ở trên — KHÔNG
được dùng lại nguồn đã bị loại, KHÔNG bịa số liệu. Trường "loi" của câu viết lại KHÔNG được chứa chữ số —
viết bằng chữ (vd: "một trăm hai mươi" chứ không phải "120"), vì đây là lời đọc thành tiếng. Nếu cần thêm thongTin mới để chứng minh câu viết lại,
thêm vào "thongTinMoi" (đúng schema thongTin, "bangChung.nguonId" phải trỏ tới 1 nguồn đang có sẵn trong
hồ sơ còn lại HOẶC 1 nguồn mới bạn thêm vào "nguonMoi"). Nếu không tìm được căn cứ nào để viết lại 1 câu,
hãy đổi câu đó thành câu chuyển ý ngắn gọn (nguon: []) thay vì bịa.

BẮT BUỘC: mọi "id" trong "nguonMoi" và "thongTinMoi" PHẢI là chuỗi MỚI, KHÁC HOÀN TOÀN với mọi id đã xuất
hiện trong "hồ sơ tài liệu CÒN LẠI" liệt kê ở trên (ví dụ thêm tiền tố "new-" để chắc chắn không trùng) —
trùng id sẽ làm hỏng toàn bộ hồ sơ.

Trả về ĐÚNG JSON, không thêm chữ nào khác: {{ "nguonMoi": [<mảng nguồn mới, đúng schema nguồn trong
hackathon-ho-so-nguon/1, để mảng rỗng nếu không cần thêm>], "thongTinMoi": [<mảng thongTin mới, để mảng
rỗng nếu không cần thêm>], "cauVietLai": [<mảng câu đã viết lại, đúng schema câu trong hackathon-kich-ban/1,
PHẢI giữ đúng "n" như trong danh sách câu bị ảnh hưởng ở trên>] }}
"""

REWRITE_RETRY_SUFFIX = "\n\nCHỈ trả về JSON hợp lệ theo đúng cấu trúc đã mô tả (nguonMoi, thongTinMoi, cauVietLai), không thêm bất kỳ chữ nào khác."
