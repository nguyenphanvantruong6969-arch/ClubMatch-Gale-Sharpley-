> **Bản tham khảo do AI viết (Claude Sonnet, 20/11/2026), theo yêu cầu của Truong.** Mọi số liệu là **dữ liệu mô phỏng** do máy sinh, không phải khảo sát học sinh thật. Chỗ đánh dấu **[Truong kiểm lại]** là điều AI không biết chắc (cảm nhận, sự việc ở trường, tên trường) — Truong phải sửa cho đúng sự thật trước khi dùng.

# Bản tham khảo báo cáo đề tài

**Tên đề tài:** Xây dựng phần mềm sắp xếp học sinh vào câu lạc bộ bằng thuật toán chấp nhận trì hoãn (Gale–Shapley) có suất dự trữ, và công cụ giúp nhà trường chọn mục tiêu giáo dục **[Truong kiểm lại tên đề tài]**

**Tác giả:** [Truong kiểm lại: họ tên, lớp, trường]

**Cuộc thi:** [Truong kiểm lại: tên cuộc thi, bảng, năm]

**Trường:** [tên trường – Truong kiểm lại]

---

## Tóm tắt

Mỗi học kỳ, một trường phổ thông phải xếp khoảng 800 học sinh vào khoảng 20 câu lạc bộ (CLB) có số chỗ giới hạn. Xếp thủ công hoặc theo thứ tự đăng ký thì khó giải thích và dễ bị nghi ngờ thiên vị. Đề tài xây dựng một phần mềm chạy ngoại tuyến trên Windows, dùng thuật toán chấp nhận trì hoãn do học sinh đề nghị (Gale–Shapley), thêm suất dự trữ mềm hai lượt, một lần bốc thăm phá hoà khoá bằng seed, và ưu tiên hai tầng (có thi, không thi). Trên dữ liệu mô phỏng, kết quả không có cặp phá vỡ nào (0 trong mọi lần kiểm), tối ưu cho học sinh trong các kết quả ổn định (0 phản ví dụ trên 2.088 thể hiện vét cạn) và không em nào khai gian có lợi (0/1.400, trong khi cơ chế Boston là 258/1.400). Kết quả không tối ưu Pareto, và đề tài nêu rõ cái giá đó. Phần mới: ba "thẻ mục tiêu" cho nhà trường (theo năng lực, cơ hội như nhau, dành chỗ cho một nhóm); mô phỏng cho thấy nên công bố công thức giữ chỗ thay vì con số cố định, và giúp một em thì thường có 1 đến 1,3 em khác phải nhường chỗ. Phần mềm chưa được thử với học sinh thật, máy kiosk thật hay hệ thống Microsoft thật của trường.

---

## 1. Đặt vấn đề

### 1.1 Bài toán của nhà trường

Ở trường [tên trường – Truong kiểm lại], đầu mỗi đợt sinh hoạt câu lạc bộ, nhà trường có khoảng 800 học sinh và khoảng 20 CLB, mỗi CLB chỉ nhận một số em nhất định (nguồn: docs/ke_hoach/BOI_CANH_DU_AN.md, mục 1). Mỗi học sinh xếp hạng các CLB mình muốn vào (tối đa 10 nguyện vọng mỗi buổi) và chọn tối đa 5 CLB muốn dự thi tuyển mỗi buổi. Có CLB tổ chức thi tuyển, có CLB không. Nhà trường cần một danh sách cuối cùng: mỗi em vào đúng một CLB mỗi buổi, không CLB nào quá chỉ tiêu.

Đây là một bài toán ghép cặp hai phía (học sinh với CLB), cùng họ với bài toán ghép trường với học sinh ở các thành phố lớn.

### 1.2 Ai bị ảnh hưởng

- **Học sinh:** muốn vào CLB mình thích, và muốn hiểu vì sao được hoặc không được xếp. Nếu cách xếp cho phép "chơi chiêu" (ghi nguyện vọng khác với điều mình muốn để có lợi) thì em thật thà bị thiệt.
- **Giáo viên CLB:** cần chọn đúng em đã thi, tránh bị than phiền là chấm thiên vị. Giáo viên chấm bài mà không cần biết số bốc thăm hay thứ hạng nguyện vọng của em.
- **Nhà trường (người quản lý):** cần một kết quả công bằng, tái lập được (chạy lại ra đúng như cũ), có thể giải thích với phụ huynh, và có thể chọn mục tiêu của mình, chẳng hạn ưu tiên năng lực hay ưu tiên cơ hội như nhau.

### 1.3 Vì sao làm thủ công hoặc bằng biểu mẫu chưa đủ

Biểu mẫu (ví dụ Microsoft Forms) chỉ **thu** nguyện vọng; việc **xếp** vẫn phải làm bằng tay hoặc bằng một quy tắc đơn giản như "ai đăng ký trước được trước". Có ba chỗ yếu, theo mô tả bài toán trong tài liệu dự án:

1. Hai quy tắc đơn giản đều có thể tạo ra những cặp "cùng muốn đổi": một em và một CLB cùng thấy đổi chỗ có lợi hơn chỗ đang có. Kết quả như vậy không bền.
2. Khi một CLB đông người thích, cách xử lý hoà điểm thường không minh bạch.
3. Khi số liệu thay đổi (em đến muộn, em rút), làm lại bằng tay dễ làm đổi chỗ của những em đã được báo.

**[Truong kiểm lại: đoạn này nên thay bằng chuyện cụ thể ở trường em — trường đang xếp thế nào, ai phàn nàn điều gì. AI không biết thực tế ở trường.]**

---

## 2. Câu hỏi nghiên cứu và giả thuyết

### 2.1 Câu hỏi chính

> Có thể xếp học sinh vào câu lạc bộ theo cách vừa **ổn định**, vừa **khiến học sinh khai thật nguyện vọng là cách tốt nhất**, vừa **giải thích được**, đồng thời cho nhà trường **chọn mục tiêu giáo dục** của mình hay không?

### 2.2 Câu hỏi phụ

1. Khi một CLB có suất dự trữ thì CLB không còn một danh sách ưu tiên cố định. Phần mềm vẫn cho kết quả ổn định và tốt nhất cho học sinh (trong các kết quả ổn định) chứ?
2. So với các cơ chế khác (Boston, TTC, xét theo bốc thăm), phần mềm được gì và mất gì?
3. Nếu nhà trường muốn giữ chỗ cho một nhóm, thì cái giá là gì, và nên công bố công thức hay con số?

### 2.3 Giả thuyết (phát biểu để có thể bị bác bỏ)

Định lý Gale–Shapley (1962) chứng minh tính ổn định khi mỗi CLB có **một danh sách ưu tiên cố định**. Phần mềm này không thoả tiền đề đó khi có suất dự trữ: ví dụ CLB sức chứa 3, có 1 suất dự trữ, ưu tiên nền A > B > C > D, D thuộc diện dự trữ. Khi D có mặt, CLB chọn D, A, B (C bị loại dù xếp trên D); khi D vắng, CLB chọn A, B, C (nguồn: docs/CO_CHE_THUAT_TOAN.md, mục "Chỗ mô hình trong báo cáo không mô tả được phần mềm"). Vì vậy không thể chỉ trích dẫn định lý; phải đo. Các giả thuyết dưới đây có thể bị bác bỏ bằng một phản ví dụ:

- **H1 (ổn định):** với suất dự trữ, kết quả của phần mềm không có cặp phá vỡ nào ở mọi seed và mọi quy mô thử. *Bị bác bỏ nếu* tìm được dù chỉ một cặp phá vỡ.
- **H2 (tối ưu cho học sinh trong các kết quả ổn định):** không có kết quả ổn định nào mà học sinh thích hơn, kể cả khi có suất dự trữ. *Bị bác bỏ nếu* vét cạn một thể hiện nhỏ tìm được kết quả ổn định mà ít nhất một em được hơn và không em nào bị thiệt.
- **H3 (khai thật có lợi nhất):** không em nào được lợi khi khai sai thứ tự nguyện vọng. *Bị bác bỏ nếu* tìm được một em khai gian có lợi. Có đối chứng ngược: cơ chế Boston phải cho kết quả khác 0, nếu không thì bộ dò hỏng.
- **H4 (công bố công thức tốt hơn con số):** khi cơ cấu nhóm đổi sang năm sau, công thức giữ chỗ theo tỉ lệ đạt mục tiêu ở nhiều seed hơn con số cố định. *Bị bác bỏ nếu* con số cố định đạt bằng hoặc hơn.

Tôi cũng đặt trước một điều mà tôi **không** kỳ vọng: kết quả **không** tối ưu Pareto, tức có thể có nhóm em cùng đổi chỗ để cùng có lợi. Nếu thấy 0 chu trình đổi chỗ trên dữ liệu chật thì phải xem lại cách đo.

---

## 3. Phương pháp

### 3.1 Cơ chế xếp (RB-DA)

Phần mềm dùng bốn lớp, mô tả bằng lời thường (nguồn: docs/CO_CHE_THUAT_TOAN.md):

1. **Chấp nhận trì hoãn, học sinh đề nghị (Gale–Shapley, 1962).** Mỗi vòng, em chưa có chỗ đề nghị vào nguyện vọng kế tiếp. CLB giữ tạm những em tốt nhất đang có mặt, từ chối phần còn lại. Em bị từ chối đề nghị tiếp. "Trì hoãn" nghĩa là CLB chưa chốt ai cho tới vòng cuối, nên em giỏi đến sau vẫn đẩy được em kém hơn ra.
2. **Suất dự trữ mềm, hai lượt (Kominers & Sönmez, 2016).** Mỗi CLB có thể để một số suất cho một nhóm học sinh. Lượt 1: chỉ xét em thuộc nhóm, lấy tối đa số suất dự trữ. Lượt 2: xét tất cả em còn lại, lấp nốt sức chứa. "Mềm" nghĩa là nếu không đủ em thuộc nhóm thì suất thừa trở thành chỗ thường, CLB vẫn tuyển đủ. Việc phân lượt phải tính lại ở mỗi vòng theo đúng những em đang có mặt.
3. **Một lần bốc thăm phá hoà (single tie-breaking).** Mỗi em nhận **một** số bốc thăm dùng chung cho mọi CLB. Số này sinh từ seed bằng crc32 (không dùng hàm băm của Python nên chạy lại ra đúng cũ), được **khoá** sau lần chạy đầu. Em thêm vào sau khi khoá được chèn vào một vị trí ngẫu nhiên đều, thứ tự tương đối của em cũ giữ nguyên.
4. **Ưu tiên hai tầng.** Tầng 1: em có điểm thi ở CLB đó, xếp theo điểm giảm dần, hoà điểm mới xét số bốc thăm. Tầng 2: em có đăng ký nhưng không thi CLB đó, xếp thuần theo số bốc thăm. Tầng 1 luôn đứng trên Tầng 2.

### 3.2 Vì sao thứ hạng nguyện vọng không được dùng làm ưu tiên

Hàm tính ưu tiên của CLB **không nhận** thứ hạng nguyện vọng của học sinh và không đọc kết quả của đợt trước. Nếu CLB biết em xếp mình thứ mấy rồi ưu tiên theo đó, em sẽ có lý do nói dối về thứ hạng, và tính "khai thật là tốt nhất" bị phá. Điều này được kiểm bằng phép đo (mục 4.3), không chỉ là một dòng ghi chú trong mã (nguồn: docs/NGHIEN_CUU_TOI_UU.md, TN3).

Có một ngoại lệ có điều kiện cho cơ chế huy chương (mục 3.5): huy chương mặc định có thể lấy từ thứ tự nguyện vọng ở lớp đăng ký, **nhưng mọi học sinh đều đổi được**, và khoá ưu tiên vẫn chỉ đọc huy chương đã lưu, không đọc thứ hạng (nguồn: docs/ke_hoach/FA_DAA_VISION.md, mục 6; ngoại lệ do Truong duyệt ngày 08/11/2026, ghi ở CLAUDE.md).

### 3.3 Cách kiểm chứng

Mọi phép đo chạy trên **dữ liệu mô phỏng** do máy sinh (seed cố định), không phải học sinh thật (nguồn: du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md, đầu tệp):

- **Kiểm ổn định:** với mỗi cặp (em, CLB em thích hơn chỗ hiện tại), thêm em vào tập CLB đang giữ rồi chạy lại hàm lựa chọn của CLB; nếu em được nhận thì đó là cặp phá vỡ. Cách này đúng cả khi hàm lựa chọn không phải thứ tự tuyến tính. Pipeline huỷ cả lần chạy nếu có cặp phá vỡ.
- **Tính thay thế:** hàm lựa chọn có dự trữ được kiểm bằng máy trên 221.220 cặp nhóm, 0 vi phạm tính thay thế và 0 vi phạm luật cầu tổng (nguồn: docs/CO_CHE_THUAT_TOAN.md). Lý thuyết ghép cặp tổng quát chỉ cần các tính chất này để bảo đảm ổn định và chống khai gian.
- **Vét cạn ở quy mô nhỏ:** liệt kê mọi cách gán khả dĩ trên thể hiện 7 em / 4 CLB (nguồn: docs/NGHIEN_CUU_TOI_UU.md, TN1).
- **Dò khai gian:** thử mọi cách khai sai danh sách của từng em, so với cơ chế đối chứng Boston.
- **Quét seed:** chạy lại với 200 seed (1 đến 200) trên cùng dữ liệu (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3c); 40 seed cho phép đo cặp đôi cùng có lợi; 20 seed cho phép so hai bên đề xuất.
- **Thử tải:** lưới 204 cấu hình: 200 đến 5.000 học sinh, 10 đến 100 CLB, 3/5/10 nguyện vọng, chia chỉ tiêu đều hoặc theo nhu cầu (nguồn: du_lieu_test/thu_tai/README.md, ket_qua_thu_tai.csv).
- **Kiểm "trùng khít":** cấu hình mặc định phải cho từng dòng kết quả giống hệt bản trước thay đổi, trên 3 bộ dữ liệu × 20 seed.
- **Kiểm thử tự động:** theo thống kê mới nhất trong kho, chạy cả bộ trên Linux ngày 19/11/2026 cho 6.977 ca qua, 4 ca bỏ qua, trên 353 tệp kiểm thử (nguồn: CHANGELOG.md, mục "UX1I-I4 fix1"; docs/ke_hoach/CLAUDE_CHI_TIET.md, dòng tests/).

### 3.4 Hai con số trần: 10 và 5

Phần mềm có hai trần khác nhau: tối đa **10 nguyện vọng** mỗi buổi và tối đa **5 CLB được thi** mỗi buổi (nguồn: rbda_priority_pipeline.py, hằng TRAN_NGUYEN_VONG_MOI_BUOI = 10 và TRAN_CLB_THI_MOI_BUOI = 5). Con số 10 là giới hạn của câu hỏi xếp hạng (Ranking) trong Microsoft Forms, tức ràng buộc của công cụ chứ không phải của lý thuyết; con số 5 là chính sách nhà trường. Giới hạn độ dài danh sách làm cơ chế không còn chống khai gian trọn vẹn (Dur & Morrill, 2020), nên nới trần là có lợi (nguồn: docs/ke_hoach/BOI_CANH_DU_AN.md, mục 6).

### 3.5 Phần mềm

Phần mềm là một ứng dụng ngoại tuyến cho Windows (Python 3.11, cơ sở dữ liệu SQLite, giao diện HTML/JS trong cửa sổ pywebview, có chế độ trình duyệt dự phòng; đóng gói bằng PyInstaller) (nguồn: CLAUDE.md, mục Project; docs/giai_trinh/VAI_TRO_AI.md, mục 1). Các chức năng chính:

- Nhập từ sổ Excel (danh sách CLB, học sinh, nguyện vọng, điểm); kiểm dữ liệu trước khi chạy (ví dụ Excel cắt số 0 đầu, trùng mã, điểm bất thường).
- Chạy theo từng buổi độc lập; mỗi em tối đa một CLB mỗi buổi.
- **Giải trình từng học sinh:** phiếu giải trình và tra cứu cho em tự xem; xuất PDF danh sách thành viên và phiếu theo lớp.
- **Tài khoản và nhật ký thao tác:** quản trị và giáo viên có quyền khác nhau; nhật ký chỉ thêm, không sửa.
- **Quy trình một giao dịch:** sao lưu, kiểm dữ liệu, khoá seed, xếp, kiểm ổn định, ghi kết quả, xuất tệp; lỗi thì huỷ toàn bộ. Lịch sử các lần chạy không bao giờ bị ghi đè.
- **Cơ chế huy chương (FA-DAA):** mỗi em có ba huy chương vàng, bạc, đồng (60/30/10 điểm) cho mỗi ngày, mỗi CLB tối đa một huy chương; mặc định lấy theo thứ tự nguyện vọng nhưng em nào cũng đổi được (nguồn: docs/ke_hoach/FA_DAA_VISION.md, mục 6).

Phần mềm **không** chứa mô hình AI hay học máy; việc xếp là một thuật toán xác định (nguồn: docs/giai_trinh/VAI_TRO_AI.md, mục 1).

---

## 4. Kết quả

> Tất cả bảng trong mục này là **Dữ liệu mô phỏng**. Bộ `bo_sach` (140 em, 12 CLB) còn được **cố ý dựng cho chật** để thuật toán phải làm việc; nó không mô phỏng phân bố nguyện vọng tự nhiên (nguồn: du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md).

### 4.1 Một lần chạy trên bộ 120 học sinh

*Dữ liệu mô phỏng.*

| Đại lượng | Giá trị |
|---|---|
| Học sinh / CLB / tổng chỉ tiêu | 120 / 10 / 130 (trong đó 12 suất dự trữ) |
| Được xếp | 108/120 |
| Số vòng lặp | 7 |
| Thời gian chạy (cả 5 bước, gồm sao lưu và xuất tệp) | 0,011 giây |
| Nguyện vọng 1 / 2 / 3 / 4 | 64 / 28 / 10 / 6 em |
| Vào bằng suất dự trữ | 10 trong 12 suất được dùng |

(nguồn: du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md, mục 2; seed 42)

### 4.2 Ổn định

*Dữ liệu mô phỏng.*

| Phép đo | Kết quả |
|---|---|
| 200 seed × 3 bộ dữ liệu | 0 cặp phá vỡ ở mọi seed |
| Độ bền trước nhiễu (ba bộ dữ liệu) | 392 phép thử, 0 cặp phá vỡ |
| 500 em / 25 CLB | 0 cặp phá vỡ |
| 2.000 em / 50 CLB | 0 cặp phá vỡ |
| 5.000 em / 100 CLB | 0 cặp phá vỡ |

(nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3c; docs/NGHIEN_CUU_TOI_UU.md, TN6; du_lieu_test/thu_tai/bao_cao_thu_tai.html, phần kiểm ổn định)

Ba hàng cuối đo bằng một thí nghiệm khác (kiem_on_dinh.py), không cùng thí nghiệm với lưới thử tải ở mục 4.6. Hai phép đo này dùng các quy mô khác nhau, không mâu thuẫn nhau.

Phép kiểm này chỉ cho thấy **không tìm được** cặp phá vỡ trong các thể hiện đã thử, chưa phải chứng minh cho mọi dữ liệu.

### 4.3 Tối ưu cho học sinh trong các kết quả ổn định, và chống khai gian

*Dữ liệu mô phỏng.*

| Câu hỏi | Trả lời | Số đo |
|---|---|---|
| Có kết quả ổn định nào học sinh thích hơn? | Không | 0 phản ví dụ / 2.088 thể hiện vét cạn |
| Kể cả khi có suất dự trữ? | Không | 1.073/1.073 thể hiện có dự trữ đều tối ưu |
| Đổi bên đề nghị (CLB đề nghị) có đổi kết quả? | Không | 0/20 seed, cả ba bộ |
| Em khai gian có lợi dưới RB-DA | Không | 0/1.400 em |
| Em khai gian có lợi dưới Boston (đối chứng ngược) | Có | 258/1.400 (18,43%) |

(nguồn: docs/NGHIEN_CUU_TOI_UU.md, bảng tra nhanh, TN1 đến TN3)

Ghi chú về cách đọc: kết luận về vét cạn chỉ ở thể hiện nhỏ (7 em / 4 CLB), nên chính xác là "không tìm được phản ví dụ trong 2.088 thể hiện nhỏ", chưa phải chứng minh toán học cho mọi quy mô. Hai đầu của tập kết quả ổn định trùng nhau trên cả ba bộ dữ liệu, tức tập ổn định chỉ có một phần tử; đó là tính chất của dữ liệu (điểm thi làm ưu tiên rất phân tán), có một test dựng riêng để hai bên đề nghị cho kết quả khác nhau. Số 258/1.400 ở Boston là phép **đối chứng**: nếu bộ dò luôn báo 0 thì không biết là cơ chế tốt hay bộ dò hỏng; cột Boston khác 0 cho thấy bộ dò hoạt động.

Tập em **có suất** là bất biến ở mọi kết quả ổn định (240/240 thể hiện khó), nên đổi sang một cơ chế ổn định khác không cứu thêm được em nào đang trượt, chỉ đổi em nào vào CLB nào (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3e).

### 4.4 Không tối ưu Pareto

*Dữ liệu mô phỏng.*

| Bộ dữ liệu | Chu trình đổi chỗ cùng có lợi | Em cùng lên được | Cặp phá vỡ nếu đổi hết | Hạng trung bình |
|---|---|---|---|---|
| `vi_du_huong_dan` (10 em) | 0 | 0 | 0 → 0 | 1,222 → 1,222 |
| `bo_sach` (140 em) | 16 (độ dài 2, 3, 4) | 32 (22,9%) | 0 → 92 | 2,100 → 1,771 |
| `TEST_0*` (120 em) | 5 | 10 (8,3%) | 0 → 49 | 1,611 → 1,509 |

(nguồn: docs/NGHIEN_CUU_TOI_UU.md, TN5, seed 42)

Một cách đếm khác, chỉ tính hoán đổi giữa **hai** em, cho `bo_sach` ra 85 cặp đôi cùng có lợi, liên quan 34 em (24,3%); trên 40 seed số cặp đôi là 82 đến 103, trung bình 91,0 (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3d, 3d quét 40 seed). Hai cách đếm không cùng thước đo, nên hai bộ số khác nhau (xem ghi chú nguồn cuối tệp).

Đây là đánh đổi bắt buộc chứ không phải lỗi cài đặt: đổi chỗ theo cả 16 chu trình thì hạng trung bình tốt hơn nhưng sinh ra 92 cặp phá vỡ. Đặc điểm này gặp ở mọi cơ chế giữ tính ổn định khi ưu tiên của CLB (điểm thi) không trùng nguyện vọng của học sinh. Bộ `vi_du_huong_dan` đạt tối ưu Pareto ở mọi seed, nên đây không phải khuyết tật cố hữu mà phụ thuộc dữ liệu.

Tác động của bốc thăm lên phần "không Pareto" rất nhỏ: trên `bo_sach` seed 42, trong 85 cặp đôi, 18 cặp (21%) có bốc thăm tham gia, 67 cặp (79%) bốc thăm vô can (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3d).

### 4.5 So sánh với Boston, TTC và xét theo bốc thăm

*Dữ liệu mô phỏng. Bộ `bo_sach`, 140 em / 12 CLB, seed 42.*

| Cơ chế | NV1 | NV2 | NV3 trở đi | Trượt | Hạng TB | Cặp phá vỡ | Khai gian được |
|---|---|---|---|---|---|---|---|
| **RB-DA (phần mềm)** | 54 | 46 | 40 | 0 | 2,100 | **0** | 0% |
| DA do CLB đề nghị | 54 | 46 | 40 | 0 | 2,100 | 0 | không đo ở bảng này |
| Boston (nhận ngay) | **92** | 14 | 32 | 2 | **1,826** | 50 | 18,43% |
| Xét theo bốc thăm | 81 | 24 | 33 | 2 | 1,928 | 121 | 0% |
| TTC | 80 | 29 | 31 | 0 | 1,879 | 118 | 0% |

(nguồn: docs/NGHIEN_CUU_TOI_UU.md, TN3 và TN4; tỉ lệ khai gian là trên 1.400 lượt học sinh của bộ vét cạn, không phải trên `bo_sach`)

Boston cho nhiều em nguyện vọng 1 hơn hẳn (92 so với 54) và hạng trung bình tốt hơn. Nhưng có 50 cặp "em và CLB cùng muốn nhận nhau mà không được nhận", và 18,43% em khai gian được. Tỉ lệ nguyện vọng 1 một mình không phải thước đo chất lượng. Cơ chế nào cũng thắng vài cột và thua vài cột; không dòng nào tốt nhất mọi cột. Điểm đặc biệt của RB-DA là chỉ nó vừa có 0 cặp phá vỡ vừa 0% khai gian (TTC cũng 0% khai gian nhưng có 118 cặp phá vỡ).

### 4.6 Tốc độ và quy mô

*Dữ liệu mô phỏng.* Lưới thử tải gồm 204 cấu hình (nguồn: du_lieu_test/thu_tai/ket_qua_thu_tai.csv).

Thời gian bước phân bổ, 5.000 học sinh, 10 nguyện vọng, chỉ tiêu chia đều:

| Số CLB | Thời gian phân bổ | Số vòng | Tỉ lệ được xếp |
|---|---|---|---|
| 10 | 7,65 s | 31 | 100% |
| 25 | 5,91 s | 23 | 97,92% |
| 50 | 4,24 s | 22 | 95,80% |
| 100 | 3,58 s | 20 | 93,64% |

Lưới quét 4 mức CLB: 10, 25, 50, 100. Cấu hình **chậm nhất** là 5.000 em / 10 CLB / 10 nguyện vọng: nạp dữ liệu 3,67 s, **phân bổ 7,65 s**, xuất kết quả 0,20 s (cộng ba bước ≈ 11,52 s). Số 7,65 s chỉ là bước phân bổ, không phải từ lúc bấm nút đến lúc thấy bảng. Lần đo này bật theo dõi bộ nhớ (tracemalloc) nên chậm hơn bình thường; thời gian tăng gần tuyến tính theo số học sinh, và số CLB ảnh hưởng ít hơn (ở lưới này nhiều CLB hơn lại nhanh hơn). Tôi không đưa công thức độ phức tạp vào báo cáo vì kho không có phân tích độ phức tạp nào chống lưng (nguồn: BAO_VE_RA_SOAT_BAO_CAO.md, mục A5).

Thời gian phân bổ lớn nhất theo số học sinh trong lưới:

| Số học sinh | 200 | 500 | 1.000 | 2.000 | 5.000 |
|---|---|---|---|---|---|
| Lớn nhất (giây) | 0,076 | 0,236 | 0,516 | 1,418 | 7,654 |

Với quy mô một trường (khoảng 800 em, 20 CLB) thì thời gian là rất nhỏ; ở dữ liệu ngoài lưới, 500 em / 20 CLB mất 0,03 s phân bổ và 2.000 em / 40 CLB mất 0,14 s (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3).

### 4.7 Số vòng và độ dài danh sách nguyện vọng

*Dữ liệu mô phỏng.* Số vòng phụ thuộc độ dài danh sách nguyện vọng (nguồn: ket_qua_thu_tai.csv, 68 cấu hình mỗi mức; docs/ke_hoach/BOI_CANH_DU_AN.md, mục 5):

| Độ dài danh sách | Số vòng trung vị | Số vòng lớn nhất |
|---|---|---|
| 3 | 9 | 37 |
| 5 | 14 | 84 |
| 10 | 18 | 227 |

Tài liệu mô tả của mã nói số vòng bằng độ dài danh sách dài nhất; số đo thực tế lớn hơn nhiều. Trần `max_rounds` hiện là 1.000, gấp khoảng 4,4 lần mức cao nhất đã thấy (227); chạm trần thì chương trình báo lỗi (nguồn: BOI_CANH_DU_AN.md, mục 5).

**Nên cho học sinh xếp bao nhiêu nguyện vọng?** Thí nghiệm cắt danh sách của mọi em xuống k nguyện vọng, trên bộ dữ liệu "sạch" của tài liệu nguồn, cùng điểm, cùng chỉ tiêu, 50 seed mỗi mức:

*Dữ liệu mô phỏng.*

| Cắt còn | Em chưa được xếp (trung bình) |
|---|---|
| 1 nguyện vọng | 48,0 |
| 2 | 26,2 |
| 3 | 14,8 |
| 4 | 7,5 |
| 5 | 1,2 |
| 6 | 0,3 |

(nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3c)

Số em chưa được xếp giảm rất đều từ 48 xuống 0,3. Nhưng đừng đọc thành "bắt học sinh điền tối đa số CLB": thí nghiệm **cắt bớt** danh sách em vốn đã khai đủ, nên nó đo "em mất gì khi không khai hết những CLB mình **vẫn chấp nhận**"; nó không đo việc thêm CLB em không muốn, và thêm CLB không muốn thì em có thể bị xếp đúng vào đó (nguồn: cùng mục). Khuyến nghị dùng được: để học sinh khai đủ các CLB mình thực sự chấp nhận; số cụ thể thì **[Truong kiểm lại: em chọn con số gợi ý và giải thích]**. Cách nhà trường chia chỉ tiêu (đều hay theo độ hút) cũng làm đổi tỉ lệ em được xếp: ở 2.000 em, 10 nguyện vọng, trung bình 97,64% (chia đều) so với 99,81% (theo nhu cầu) (nguồn: ket_qua_thu_tai.csv, tính từ 8 cấu hình mỗi cách chia).

### 4.8 Ảnh hưởng của seed bốc thăm

*Dữ liệu mô phỏng.* Chạy lại 200 seed, lấy seed 42 làm mốc.

| Bộ dữ liệu | Số em | Không bao giờ đổi CLB | Đổi CLB (ít nhất / TB / nhiều nhất) | Cặp phá vỡ |
|---|---|---|---|---|
| `vi_du_huong_dan/` | 10 | 10 (100%) | 0 / 0,0 / 0 | 0 |
| `bo_sach/` | 140 | 127 (90,7%) | 0 / 6,0 / 11 | 0 |
| `TEST_0*` | 120 | 116 (96,7%) | 0 / 1,9 / 4 | 0 |

(nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3c)

Đổi seed **có** đổi kết quả của một số em. Cụ thể, em "bấp bênh" (lúc có suất, lúc không, tuỳ seed) chỉ có 3 trên 270 em, tức 1,1%. Điều đã đo không phải "seed không ảnh hưởng gì", mà là: đổi seed **không làm em nào được lợi hay bị thiệt một cách có hệ thống**. Trên 100 học sinh, 10.000 lần bốc, thứ hạng trung bình của mọi em lệch tối đa 1,44% so với lý thuyết; hệ số tương quan giữa mã học sinh và thứ hạng bốc đổi dấu qua 8 khối seed, tức là nhiễu thống kê chứ không phải thiên lệch (nguồn: docs/GIAI_DAP_BOC_THAM.md, Câu 1). Và đổi seed không làm mất ổn định: mọi seed đều cho 0 cặp phá vỡ. Thêm nữa, nhiễu điểm ±0,5 xáo 15,14% số em, trong khi đổi seed chỉ xáo 4,36%: bốc thăm chỉ đứng sau điểm (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3e). Trong mã, khoá ưu tiên là (điểm giảm dần, số bốc thăm), nên bốc thăm chỉ có tác dụng ở em hoà điểm và em dự tuyển CLB mà em không thi.

### 4.9 Ba thiết kế bốc thăm cho cả tuần

*Dữ liệu mô phỏng.* Bộ 5 buổi, 160 em có khai, 200 seed (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 3f).

| Thiết kế | Em trắng tay cả tuần | CLB TB mỗi em | Cặp phá vỡ |
|---|---|---|---|
| A1 bốc một lần cho cả tuần | 36,50 | 1,320 | 0 |
| A2 bốc lại mỗi buổi | 36,26 | 1,319 | 0 |
| A3 bốc có bù | 35,69 | 1,316 | 0 |

Chênh A1 − A2 là 0,245 em trên 160 em (0,15%), khoảng tin cậy 95% là [+0,020 ; +0,465]: phân biệt được về thống kê nhưng gần như không đáng kể thực tế. Nhưng A3 mở kênh khai gian: giấu bớt buổi có lợi cho 113/300 em dưới A3, và 0/300 dưới A1 và A2. Phần mềm vì vậy chỉ chạy A2; A1 và A3 giữ trong mã chỉ để đối chứng.

### 4.10 Em đến muộn

*Dữ liệu mô phỏng.* Thêm em sau khi đã xếp, chạy lại từ đầu, 2.000 học sinh (nguồn: docs/ke_hoach/BOI_CANH_DU_AN.md, mục 5; số đo bằng hàm thật nạp từ bản build, dữ liệu tự sinh):

| Tỉ lệ chỗ | Em đến muộn | Em cũ bị đổi (TB) | …mất hẳn chỗ | …tốt lên |
|---|---|---|---|---|
| 1 | 1 | 1,72 | 0,62 | 0 |
| 1 | 5 | 9,03 | 2,07 | 0 |
| 1 | 20 | 40,7 | 9,55 | 0 |
| 0,8 | 1 | 1,7 | 0,8 | 0 |
| 0,8 | 5 | 8,17 | 4 | 0 |
| 0,8 | 20 | 32,4 | 16,25 | 0 |

Thêm một người đề nghị chỉ có thể làm các em khác xấu đi hoặc giữ nguyên, không bao giờ tốt hơn (cột "tốt lên" là 0 ở mọi hàng). Điều này có nghĩa: "bốc thăm giữ nguyên" chỉ bảo đảm **số bốc thăm** của em cũ không đổi; **kết quả xếp** của em cũ vẫn có thể đổi khi chạy lại. Đây là lý do một phiên bản sau cần cơ chế bảo vệ em đã được báo (mục 8).

---

## 5. Ra quyết định theo mục tiêu giáo dục (phần mới)

> *Dữ liệu mô phỏng.* Phần này dựa trên memo MT0 (nguồn: docs/fable/08_MT0_MEMO.md): 800 học sinh, 20 CLB, 10 nguyện vọng, 5 CLB thi, 20 seed mỗi kịch bản, một nhóm G được giữ chỗ đều ở mọi CLB. Dữ liệu do máy sinh. Chạy lại bằng `python du_lieu_test/do_muc_tieu_mt0.py`.

### 5.1 Vì sao nhà trường cần chọn mục tiêu

Khi một CLB đông người thì **không có cách xếp nào trung lập**: hoặc ưu tiên điểm, hoặc bốc thăm, hoặc giữ chỗ cho một nhóm. Mỗi lựa chọn có cái giá và người được lợi khác nhau. Trước đây các lựa chọn này nằm trong nhiều cài đặt kỹ thuật; nhà trường khó thấy mình đang chọn điều gì. Vì thế phần mềm cho trường trả lời **một câu hỏi**: "Khi một CLB đông người, trường ưu tiên điều gì?", bằng cách bấm một trong **ba thẻ** (nguồn: docs/phien/claude__mt1-bo-muc-tieu.md):

| Thẻ | Ý nghĩa | Luật phần mềm đặt |
|---|---|---|
| Theo năng lực (mặc định) | CLB có thi chọn theo điểm; CLB không thi bốc thăm công bằng | Luật mặc định |
| Cơ hội như nhau | Mọi em có cơ hội như nhau: bốc thăm, không xét điểm thi | Chỉ bốc thăm |
| Dành chỗ cho một nhóm | Giữ một số chỗ ở mỗi CLB cho một nhóm (ví dụ khối 10) | Suất dự trữ ở mỗi CLB, tính theo công thức |

Ban đầu kế hoạch có 6 mẫu, rồi rút còn 3 thẻ: "năng khiếu" trùng với "theo năng lực" (CLB nào có thi là dữ liệu, không phải luật); "đam mê" chính là chế độ huy chương; "hoà nhập" và "khối đầu cấp" là cùng một cơ chế với nhóm khác nhau (cùng nguồn). **[Truong kiểm lại: giải thích vì sao em đồng ý với việc rút từ 6 còn 3.]**

### 5.2 Ba kịch bản đo

| Kịch bản | Độ lệch độ hút CLB | Chỗ / học sinh | Tỉ lệ nhóm G | Chênh điểm của G |
|---|---|---|---|---|
| S1 cân bằng | 0,5 | 1,05 | 15% | 0 |
| S2 CLB nóng | 1,2 | 1,00 | 15% | −0,5 độ lệch chuẩn |
| S3 thiếu chỗ, nhóm nhỏ | 1,0 | 0,90 | 8% | −0,8 độ lệch chuẩn |

Mục tiêu đo (M1): tỉ lệ nhóm G ở một CLB nóng (5 CLB được chọn nhiều nhất) phải đạt ít nhất 90% tỉ lệ của G trong toàn trường. (nguồn: docs/fable/08_MT0_MEMO.md, mục Setup)

### 5.3 Công thức hay con số cố định

Thử nghiệm: chốt chính sách từ dữ liệu năm trước, rồi áp vào năm sau mà tỉ lệ nhóm G lệch từ 0,5 đến 1,6 lần.

| Kịch bản | Con số cố định: số seed đạt M1 ở 5/5 CLB nóng | Công thức `ceil(tỉ lệ × chỉ tiêu)`: số seed đạt |
|---|---|---|
| S1 | 14/20 | **20/20** |
| S2 | 13/20 | **20/20** |
| S3 | 14/20 | **20/20** |

*Dữ liệu mô phỏng.* (nguồn: docs/fable/08_MT0_MEMO.md, F1)

Công thức chỉ đọc danh sách học sinh (nhóm nào), không đọc nguyện vọng hay kết quả đợt trước, nên không vi phạm nguyên tắc ở mục 3.2 và có thể công bố **trước khi mở đăng ký**. Công thức cũng gần như là mức dự trữ nhỏ nhất vẫn đạt mục tiêu: mức đều nhỏ nhất đạt M1 (trung vị các seed) là 6 ở S1 (công thức cho 7), 6 ở S2 (công thức 6) và 3 ở S3 (công thức 3). Đi quá mức đó lợi ít, hại nhiều: ở S3, tăng từ 8 lên 11 giúp thêm 2 em của nhóm G nhưng khiến thêm 12 em khác phải nhường chỗ (nguồn: F2).

### 5.4 Cách đọc "giúp 1 em, khoảng 1 đến 1,3 em khác nhường chỗ"

Ở mức công thức, số em ngoài nhóm bị đẩy ra trên mỗi em của nhóm được giúp là: S1 khoảng 26,3/23,2 ≈ 1,1; S2 khoảng 1,2; S3 khoảng 34,9/26,3 ≈ 1,3 (nguồn: F3). Giữ chỗ **chuyển** chỗ từ em này sang em khác chứ không tạo thêm chỗ: tỉ lệ em được nguyện vọng 1 toàn trường và số em chưa được xếp hầu như không đổi. Hệ quả cho giao diện: phải cho nhà trường thấy "ai nhường chỗ", không chỉ "ai được lợi". Đây là **chi phí thật** của mục tiêu, và nhà trường nên công bố nó cho phụ huynh.

### 5.5 Suất dự trữ "tượng trưng" không có tác dụng

Dự trữ 1 đến 2 chỗ thay đổi M1 bằng 0 điểm phần trăm (S1, S2), thậm chí giảm (S3). Một trường đặt "1 chỗ cho công bằng" chỉ có cái nhãn chứ không có hiệu quả. Vì vậy giao diện cảnh báo khi mức dự trữ quá thấp để có tác dụng (nguồn: F4, và kế hoạch mục UI contract).

### 5.6 Khoảng cách ngược

Ở S1, vốn **không** có chênh điểm giữa nhóm G và nhóm còn lại, tỉ lệ nhóm G vào top 3 nguyện vọng đã là 48,8% so với 44,8%. Sau khi áp công thức giữ chỗ thì lên 54,7% so với 43,7%: giữ chỗ tạo ra khoảng cách ngược khi chưa từng có khoảng cách (nguồn: F5). Vì thế phải hiển thị khoảng cách nền **trước khi** gợi ý giữ chỗ; nếu không có khoảng cách thì nói rõ như vậy.

### 5.7 Một đòn bẩy không đủ cho mọi mục tiêu

Dự trữ cho nhóm G không làm đổi số em chưa được xếp (S2 khoảng 115, S3 khoảng 135), số CLB còn trống chỗ, độ phân bố theo lớp, hay tỉ lệ khối 10 vào top 3. Số em chưa được xếp lớn ở S2 và S3 đến từ nhu cầu lệch cộng với danh sách chỉ 10 mục, chứ không đến từ cơ chế (nguồn: F6). Nên mỗi thẻ mục tiêu phải nói rõ đòn bẩy của nó (sức chứa, độ dài danh sách, mức tối thiểu) hoặc ghi "chỉ đo, chưa can thiệp".

### 5.8 Che số nhỏ

Số CLB có 1 đến 4 thành viên thuộc nhóm G: S1 từ 4 đến 6, S2 từ 3 đến 8, S3 từ 3 đến 18 (trong 20 CLB). Nếu in nguyên số thì có thể nhận ra từng em. Vì vậy bản công bố và bản thử phải hiển thị "dưới 5" thay vì số thật (nguồn: F7).

### 5.9 Ổn định vẫn giữ

Với mức công thức, mọi kịch bản và mọi seed đều cho 0 cặp phá vỡ (nguồn: F8).

### 5.10 Giao diện làm được gì trong 1 đến 2 cú bấm

Bản đánh giá cuối của lô MT1 (nhánh claude/mt1-bo-muc-tieu, do một phiên AI đóng vai hiệu trưởng trong buổi họp 30 phút, **không phải thử với người dùng thật**) ghi nhận:

*Dữ liệu mô phỏng (sổ nhập mẫu, trình duyệt Chromium).*

| Mục tiêu đặt ra | Đo được |
|---|---|
| Từ mở Cài đặt đến "đã áp dụng": tối đa 1 đến 2 cú bấm | Theo năng lực: 1; Cơ hội như nhau: 1; Dành chỗ (một nhóm): 1; Dành chỗ (hai nhóm): 2 |
| Hiện tác động mà không cần bấm thêm | Có: một dòng ước tính, ví dụ "28 học sinh được chỗ tốt hơn, 26 học sinh xuống nguyện vọng sau" |
| Ước tính khớp kết quả thật | Bộ 800 học sinh: ước tính 28/26, xếp thật 28 được giúp / 26 nhường chỗ (sau khi sửa) |
| Hoàn tác trả đúng, kể cả số chỗ từng CLB | Đạt |

(nguồn: MT1_DANH_GIA.md trên nhánh origin/claude/mt1-bo-muc-tieu, mục "Mục tiêu đặt ra và kết quả đo")

Bản đánh giá cũng nêu những lỗi đã gặp: lần đầu, ước tính 273 so với kết quả thật 28 vì thẻ "Cơ hội như nhau" tắt "Chia 100 điểm" mà không báo, nên ước tính lệch xa (đã sửa). Còn các vấn đề chưa sửa: dòng cảnh báo vàng ("chưa thấy nhóm này bị thiệt") đặt cạnh dòng kết quả ("đạt ở 5/5 CLB") dễ làm người đọc lúng túng; số ước tính chưa kèm tổng số em; sổ nhập không có điểm chia mà để mặc định "Chia 100 điểm" thì lần xếp đầu báo lỗi (nguồn: cùng tệp, mục "Vấn đề đã gặp").

### 5.11 Giới hạn của phép đo này

Dữ liệu do máy sinh, một nhóm G duy nhất, dự trữ đều ở mọi CLB, chỉ một buổi; dữ liệu thật có thể khác (nguồn: docs/fable/08_MT0_MEMO.md, mục Limits). Chế độ thử (`run_thu`) chưa hỗ trợ chế độ huy chương, nên ước tính ở chế độ này chưa có. Phần "bất ngờ" khi đọc bảng số là của người viết báo cáo: **[Truong kiểm lại: em viết điều gì làm em bất ngờ khi đọc các bảng ở mục 5.3 đến 5.8; AI không viết thay]**.

---

## 6. Thảo luận

*(Phần này là bản tham khảo; các câu cảm nhận cần Truong viết lại.)*

### 6.1 Câu hỏi đã được trả lời đến đâu

- **Câu hỏi phụ 1 (suất dự trữ):** trên dữ liệu mô phỏng, H1 và H2 **không bị bác bỏ**: 0 cặp phá vỡ ở mọi lần kiểm, 0 phản ví dụ tối ưu trên 1.073 thể hiện có dự trữ. Phép đo này khớp đúng dự đoán của lý thuyết tổng quát (hàm lựa chọn có tính thay thế), nên nó xác nhận **phần mềm cài đặt đúng**, chứ không phải một phát hiện lý thuyết mới. Giá trị còn lại là chỉ ra rằng không thể chỉ trích dẫn định lý Gale–Shapley dạng gốc.
- **H3:** không bị bác bỏ: 0/1.400, với đối chứng Boston 258/1.400.
- **Câu hỏi phụ 2 (so sánh):** RB-DA đổi số em được nguyện vọng 1 (54 so với 92 ở Boston) lấy tính ổn định và khả năng khai thật.
- **Câu hỏi phụ 3 và H4:** với dữ liệu mô phỏng, công thức đạt 20/20 seed còn con số cố định chỉ 13 đến 14/20. Mục tiêu giáo dục có cái giá khoảng 1 đến 1,3 em nhường chỗ cho mỗi em được giúp.
- **Câu hỏi chính:** trả lời "được" trong phạm vi dữ liệu mô phỏng; chưa trả lời được với học sinh thật.

### 6.2 Đánh đổi

- Ổn định hay Pareto: phần mềm chọn ổn định; cái giá là 22,9% em ở `bo_sach` có thể cùng lên hạng nếu bỏ ổn định, nhưng khi đó có 92 cặp phá vỡ.
- Điểm hay bốc thăm: ưu tiên điểm thì phân biệt được em, nhưng chỗ hoà điểm vẫn phải bốc thăm; bốc thăm thuần thì công bằng cơ hội nhưng bỏ qua năng lực.
- Giữ chỗ hay không giữ chỗ: giúp nhóm được chọn nhưng em ngoài nhóm nhường chỗ.
- Nới độ dài danh sách: ít em trắng tay hơn nhưng phụ thuộc công cụ thu phiếu (Forms giới hạn 10).

### 6.3 Điều sẽ làm khác nếu làm lại

**[Truong kiểm lại — AI không biết em sẽ làm khác điều gì. Gợi ý dựa trên tài liệu, em chọn điều thật sự đúng với em:]** (a) đo lại trên dữ liệu thật của trường ngay từ đầu, thay vì chỉ dùng dữ liệu máy sinh; (b) cho học sinh thử phần mềm sớm hơn; (c) viết phần giả thuyết đúng chỗ khó (suất dự trữ làm mất danh sách ưu tiên cố định) từ đầu thay vì phát biểu lại định lý đã có. Điều (c) khớp với mục B2 trong bản rà soát báo cáo cũ (nguồn: BAO_VE_RA_SOAT_BAO_CAO.md).

---

## 7. Giới hạn nghiên cứu

1. **Chỉ có dữ liệu mô phỏng.** Mọi bảng ở trên là số do máy sinh, không phải khảo sát học sinh thật. Bộ `bo_sach` còn được cố ý dựng chật. Trình bày các số này như khảo sát thật là bịa đặt dữ liệu (nguồn: docs/NGHIEN_CUU_TOI_UU.md, mục Giới hạn).
2. **Chưa triển khai thực tế.** Phần mềm **chưa** được thử với học sinh thật, trên máy kiosk thật hay trên hệ thống Microsoft thật của trường. Các phần chạy trên Microsoft ghi "TH" (chưa thử trên hệ thống thật) trong nhật ký (nguồn: docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md, giai đoạn 8, 9 và 11). Về cửa sổ ứng dụng Windows: tài liệu kiểm chứng ghi rằng đến 02/09/2026 cửa sổ gốc (pywebview) chưa được xác nhận dùng được trên Windows thật, còn chế độ trình duyệt dự phòng đã chạy trọn luồng nạp, xếp, xuất ngày 30/08 (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 7). **[Truong kiểm lại: tình trạng hiện nay của cửa sổ gốc trên máy Windows thật]**.
3. **Vét cạn chỉ ở quy mô nhỏ** (7 em / 4 CLB). "Không tìm được phản ví dụ" yếu hơn "chứng minh được". Dò khai gian trên bộ dữ liệu lớn có chặn không gian tìm kiếm; chỉ phần vét cạn (TN3a) là kết luận mạnh.
4. **Giả định của bộ sinh dữ liệu.** Độ hút CLB sinh theo trọng số Zipf (CLB thứ i hút khoảng 1/i) và mỗi em chỉ thi 4 CLB cố định, nên khi tăng số CLB thì số kỳ thi không tăng theo; 6 nguyện vọng còn lại rơi xuống Tầng 2 (nguồn: du_lieu_test/thu_tai/README.md). Số đo thời gian bật theo dõi bộ nhớ nên chậm hơn bình thường.
5. **Một nhóm, một cấu hình dự trữ, một buổi.** Phần MT0 chỉ thử một nhóm G, dự trữ đều ở mọi CLB, một buổi. Đổi nhóm hay chính sách thì phải đo lại (nguồn: NGHIEN_CUU_TOI_UU.md, giới hạn 4; 08_MT0_MEMO.md, Limits).
6. **Trần danh sách 10.** Với danh sách bị giới hạn, cơ chế không còn chống khai gian trọn vẹn (Dur & Morrill, 2020); trần 10 đến từ công cụ Microsoft Forms, không phải lý thuyết (nguồn: BOI_CANH_DU_AN.md).
7. **Phép dò khai gian giới hạn ở một số kênh.** Với bốc thăm cả tuần chỉ dò kênh giấu bớt buổi, nên "không tìm thấy" ở A1 và A2 yếu hơn "không tồn tại".
8. **Đánh giá giao diện không phải thử nghiệm người dùng.** Bản đánh giá MT1 do một phiên AI đóng vai người dùng; chưa có thử nghiệm với nhà trường thật.
9. **Phụ thuộc vào luật pháp địa phương.** Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 (hiệu lực từ 01/01/2026) liên quan đến dữ liệu học sinh; cần chuyên gia pháp lý kiểm, đề tài này không tư vấn pháp lý (nguồn: BOI_CANH_DU_AN.md, mục 7).

---

## 8. Kết luận và hướng phát triển

### 8.1 Ba điều chính rút ra

1. **Ổn định và khai thật được kiểm bằng đo, không chỉ trích dẫn định lý.** Khi có suất dự trữ, phần mềm không còn một danh sách ưu tiên cố định, nhưng trên dữ liệu mô phỏng vẫn không có cặp phá vỡ (0), không phản ví dụ tối ưu (0/2.088) và không em nào khai gian có lợi (0/1.400, Boston 258/1.400).
2. **Không có cơ chế nào tốt nhất mọi mặt.** RB-DA không tối ưu Pareto và cho ít em nguyện vọng 1 hơn Boston (54 so với 92); đổi lại không có cặp phá vỡ nào và không ai khai gian được.
3. **Mục tiêu giáo dục có cái giá nhìn thấy được.** Giữ chỗ cho một nhóm chuyển chỗ chứ không tạo chỗ: khoảng 1 đến 1,3 em nhường chỗ cho mỗi em được giúp; công bố công thức thay vì con số cố định cho kết quả ổn định hơn qua các năm (20/20 so với 13 đến 14/20 seed).

**[Truong kiểm lại: ba điều trên là AI tóm tắt từ số liệu; Truong viết lại bằng lời của em về điều em thật sự rút ra.]**

### 8.2 Hướng phát triển

- **Thay đổi theo thời gian (em đến muộn, rút, đổi sức chứa).** Mục 4.10 cho thấy chạy lại làm đổi kết quả em cũ; hướng thiết kế là tiếp tục thuật toán từ trạng thái đã lưu, và bảo vệ em đã được báo (nguồn: BOI_CANH_DU_AN.md, mục 6). Một phép đo ban đầu cho thấy tiếp tục từ trạng thái cũ nhanh hơn chạy lại 1,8 đến 3,9 lần với kết quả giống hệt (nguồn: BOI_CANH_DU_AN.md, mục 5).
- **Mở rộng sang ngành khác.** Phân tích ban đầu liệt kê 12 ngành (phân đề tài, ký túc xá, sự kiện, hoạt động ngoài trường, tuyển sinh cấp trường…) với mức việc cần làm khác nhau; một số ngành không phù hợp (tuyển sinh đại học toàn quốc, giao dịch tài chính, điều xe tức thời) (nguồn: BOI_CANH_DU_AN.md, mục 3 và 8). Điểm phù hợp là phán đoán, không phải số đo.
- **Công bố mục tiêu trước khi mở đăng ký.** Ý tưởng là trường công bố thẻ mục tiêu và công thức giữ chỗ trước, rồi mới thu nguyện vọng, để học sinh và phụ huynh biết luật chơi (các lô MT2 đến MT5 trong kế hoạch: công bố mục tiêu, "vì sao chưa đạt", báo cáo cho phụ huynh) (nguồn: docs/phien/claude__mt1-bo-muc-tieu.md).
- **Thử với dữ liệu thật** của trường, và thử nghiệm giao diện với người dùng thật.

---

## Tài liệu tham khảo

Danh sách dưới đây chỉ gồm tài liệu được nhắc trong tài liệu của dự án; **[Truong kiểm lại tác giả, năm, tên bài qua Crossref trước khi nộp]** (tài liệu dự án ghi rằng một số tên tác giả, tiêu đề trong danh sách cũ sai).

1. Gale, D., & Shapley, L. S. (1962). Thuật toán chấp nhận trì hoãn (deferred acceptance) và bài toán ghép cặp ổn định. [Truong kiểm lại tên bài đầy đủ]
2. Kominers, S. D., & Sönmez, T. (2016). Dự trữ mềm và thứ tự xét ưu tiên (soft reserves, precedence ordering). [Truong kiểm lại tên bài đầy đủ] (được trích trong mã nguồn `rbda_priority_pipeline.py`.)
3. Abdulkadiroğlu, A., Che, Y.-K., & Yasuda, Y. (2015). "Expanding Choice in School Choice" (cơ sở cho tín hiệu ưu tiên riêng khi hoà).
4. Abdulkadiroğlu, A., Pathak, P. A., & Roth, A. E. (2009). Bài về hệ thống ghép trường trung học ở New York (bốc thăm một lần). [Truong kiểm lại tên bài]
5. Abdulkadiroğlu, A., Pathak, P. A., Roth, A. E., & Sönmez, T. Bài về việc Boston chuyển sang thuật toán chấp nhận trì hoãn. [Truong kiểm lại năm: FA_DAA_VISION.md ghi 2006, báo cáo cũ ghi 2005]
6. Dur, U., & Morrill, T. (2020). Về giới hạn độ dài danh sách nguyện vọng và tính chống khai gian của chấp nhận trì hoãn. [Truong kiểm lại tên bài]
7. Roth, A. E. (1984); Abdulkadiroğlu, A., & Sönmez, T. (2003); Ashlagi, I., Nikzad, A., & Romm, A. Những tài liệu có trong danh mục của báo cáo cũ. [Truong kiểm lại tất cả thông tin]
8. Erdil, A., & Ergin, H. (2008). Chu trình cải thiện ổn định (stable improvement cycles); được nhắc như hướng mở trong FA_DAA_VISION.md.
9. Wilde, H. và cộng sự (2020). Thư viện Python `matching`; dự định đối chiếu `verify_stability` nhưng chưa làm (nguồn: BOI_CANH_DU_AN.md, mục 9).

---

## Phụ lục 1 — Nhật ký sử dụng AI

Xem `docs/nhat_ky_ai/NHAT_KY_AI.docx` (nhật ký AI, cập nhật đến 20/11/2026) và `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md` (bản đọc nhanh). Mô tả vai trò của AI: xem tệp đi kèm `docs/bao_cao/BAN_THAM_KHAO_VAI_TRO_AI.md`.

---

### Ghi chú nguồn cho người soát (xoá trước khi nộp)

- **Số ca kiểm thử:** SO_LIEU_DA_KIEM_CHUNG.md (mục 5) và BOI_CANH_DU_AN.md ghi 483 ca / 37 tệp, 25 lỗi tìm và sửa; CHANGELOG.md (19/11/2026) ghi 6.977 ca qua, 4 bỏ qua; CLAUDE_CHI_TIET.md ghi 353 tệp. Bản này dùng số **mới nhất** (6.977 ca, 353 tệp).
- **Cặp đôi `bo_sach`:** 85 cặp / 34 em (24,3%) (hoán đổi hai em, SO_LIEU mục 3d) khác với 16 chu trình / 32 em (22,9%) (mọi độ dài, NGHIEN_CUU TN5); hai thước đo khác nhau, bản này nêu cả hai.
- **Số "600 lần chạy"** trong CO_CHE_THUAT_TOAN.md không có script chống lưng (BAO_VE mục B7), nên không dùng.
- **Số 7,65 s:** BOI_CANH_DU_AN.md nghi phần lớn là bước kiểm; ket_qua_thu_tai.csv ghi là cột thời gian phân bổ; ghi chú trong BAO_VE (A5) nói đo khi bật tracemalloc. Bản này dùng số trong CSV, gắn với bước phân bổ.
- **Năm bài Abdulkadiroğlu–Pathak–Roth–Sönmez:** 2005 (báo cáo cũ) và 2006 (FA_DAA_VISION.md); chưa kiểm.
- **Mục MT0:** memo hiện có F1 đến F8; các mục được trích ở mục 5 của bản này.
