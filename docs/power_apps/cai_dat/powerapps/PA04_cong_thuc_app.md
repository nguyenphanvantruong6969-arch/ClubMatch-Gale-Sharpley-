# PA04 — Điền hạn chót, số nguyện vọng, giáo viên phụ trách

[← PA03](PA03_noi_du_lieu.md) · Tiếp theo: [PA05](PA05_tao_man_hinh_va_khung.md)

## Cách dán một mục cài đặt (dùng cho mọi tệp PA)

Mỗi thứ trên màn hình (trang, ô chữ, nút bấm…) có nhiều **mục cài đặt**. Cách điền một mục, luôn đủ 5 bước:

1. Ở **cây bên trái**, bấm một lần vào tên của thứ cần cài. Tên đó được tô sáng.
2. Ở **thanh công thức**, bấm **ô thả xuống nhỏ bên trái**, gõ vài chữ đầu của tên mục (ví dụ `Text`), rồi bấm đúng tên mục trong danh sách hiện ra.
3. Bấm vào **ô dài bên phải chữ «fx»**, bấm `Ctrl` + `A` để chọn hết chữ đang có.
4. Bấm `Ctrl` + `V` để dán đoạn đã sao chép từ ô xám.
5. Nhìn ngay dưới thanh công thức.

👀 Không có dòng chữ đỏ dưới thanh công thức, và trong ô dài không có đoạn nào bị gạch chân đỏ lượn sóng.

Các tệp sau chỉ ghi ngắn: **«Tên mục» — dán:** kèm một ô xám. Mỗi dòng như vậy là một lần làm đủ 5 bước trên.

**Mẹo:** đoạn dán dài quá, khó nhìn: bấm mũi tên nhỏ chỉ xuống ở đầu bên phải thanh công thức để mở rộng ô dài.

⚠️ **Không tìm thấy tên mục ở bước 2:** ở khung bên phải, bấm thẻ «Advanced», bấm vào ô «Search for a property», dán tên mục. Mục đó hiện ra kèm một ô; bấm vào ô đó, `Ctrl` + `A`, `Ctrl` + `V`.
⚠️ **Gạch chân đỏ ở tên một trang, một nút hay một bảng chưa tạo** (ví dụ `scrXacNhan`): bình thường, sẽ hết khi làm xong tệp tạo ra thứ đó.
⚠️ **Gạch chân đỏ ở chữ `club_id` hoặc `student_id`:** Power Apps của bạn vẫn gọi cột đó bằng tên cũ. Trong đoạn vừa dán, sửa chữ bị gạch đỏ thành `Title`. Phải làm vậy ở **mọi** đoạn dán về sau.
⚠️ **Dán vào thì gạch đỏ gần như toàn bộ, kể cả ở các dấu phẩy:** máy đang dùng kiểu viết số có dấu phẩy thập phân, nên công thức phải dùng dấu chấm phẩy. Cách sửa: trong trình duyệt, mở phần cài đặt ngôn ngữ (Edge: `edge://settings/languages`; Chrome: `chrome://settings/languages`), đưa «English (United States)» lên đầu danh sách, đóng hết cửa sổ trình duyệt, mở lại màn hình thiết kế rồi dán lại.

## Bước 1 — Thông tin chung của ứng dụng

1. Cây bên trái: bấm «App» (dòng trên cùng).
2. Ô thả xuống nhỏ của thanh công thức: chọn «Formulas».
3. Bấm vào ô dài, `Ctrl` + `A`, rồi dán:
```
HanChot = DateTimeValue("2026-12-01 17:00");
SoNguyenVongToiDa = 5;
DSQuanTri = ["gv.a@truong.edu.vn", "gv.b@truong.edu.vn"];
EmailToi = Lower(User().Email);
LaQuanTri = EmailToi in DSQuanTri;
HetHan = Now() > HanChot;
LaPhone = App.Width < 600;
```
4. Sửa **dòng 1**: trong ô dài, bôi đen đúng đoạn `2026-12-01 17:00` (không bôi hai dấu ngoặc kép), gõ ngày giờ hết hạn của trường theo đúng kiểu `năm-tháng-ngày giờ:phút`. Ví dụ 17 giờ 30 ngày 5 tháng 1 năm 2027 viết là `2027-01-05 17:30`.
5. Sửa **dòng 2**: bôi đen số `5`, gõ số câu lạc bộ tối đa một học sinh được chọn (từ 1 đến 10).
6. Sửa **dòng 3**: bôi đen `gv.a@truong.edu.vn`, gõ thư điện tử của giáo viên phụ trách thứ nhất, **toàn chữ thường**. Làm tương tự với `gv.b@truong.edu.vn`.
   - Chỉ có một giáo viên: xoá đoạn `, "gv.b@truong.edu.vn"` (cả dấu phẩy).
   - Có ba giáo viên trở lên: thêm `, "thư điện tử"` vào trước dấu `]` cho mỗi người.

👀 Không có gạch chân đỏ. Dòng nào cũng kết thúc bằng dấu chấm phẩy `;`.

⚠️ Ô thả xuống không có mục «Formulas»: bỏ qua bước 3 đến 6, và ở Bước 2 dùng **đoạn thay thế**.

## Bước 2 — Việc làm khi ứng dụng mở

7. Cây bên trái: bấm «App».
8. Ô thả xuống nhỏ: chọn «OnStart».
9. Bấm vào ô dài, `Ctrl` + `A`, rồi dán:
```
Set(varHS, LookUp(HocSinh, email = Lower(User().Email)));
Set(varNV, LookUp(NguyenVong, student_id = varHS.student_id));
ClearCollect(colCLB, SortByColumns(CLB, "name"))
```

**Đoạn thay thế** (chỉ dùng khi ở Bước 1 không có mục «Formulas»). Dán đoạn này vào «OnStart» **thay cho** đoạn ở bước 9, rồi sửa 3 dòng đầu y như bước 4, 5, 6:
```
Set(HanChot, DateTimeValue("2026-12-01 17:00"));
Set(SoNguyenVongToiDa, 5);
Set(DSQuanTri, ["gv.a@truong.edu.vn", "gv.b@truong.edu.vn"]);
Set(EmailToi, Lower(User().Email));
Set(LaQuanTri, EmailToi in DSQuanTri);
Set(HetHan, Now() > HanChot);
Set(LaPhone, App.Width < 600);
Set(varHS, LookUp(HocSinh, email = EmailToi));
Set(varNV, LookUp(NguyenVong, student_id = varHS.student_id));
ClearCollect(colCLB, SortByColumns(CLB, "name"))
```

10. Cây bên trái: đưa chuột vào dòng «App», bấm «⋯» hiện ra ở cuối dòng, bấm «Run OnStart».

👀 Phía trên trang ở giữa thoáng hiện các chấm chạy ngang rồi hết. Không hiện dải thông báo màu đỏ.

11. Bấm `Ctrl` + `S`.

⚠️ Dải đỏ báo không đọc được bảng: làm lại [PA03](PA03_noi_du_lieu.md), kiểm tra đủ tên bảng.
⚠️ **Mỗi lần mở lại màn hình thiết kế vào hôm khác, làm lại bước 10** trước khi làm việc khác. Nếu không, các ô chọn câu lạc bộ sẽ trống.

## Bảng tên dùng chung (để tra cứu)

Các tệp sau nhắc đến những tên này. Tất cả đã được tạo ở tệp này.

| Tên | Nghĩa |
|---|---|
| `HanChot` | Ngày giờ hết hạn nộp |
| `SoNguyenVongToiDa` | Số câu lạc bộ tối đa được chọn |
| `DSQuanTri` | Danh sách thư điện tử giáo viên phụ trách |
| `LaQuanTri` | Người đang mở ứng dụng là giáo viên phụ trách |
| `HetHan` | Đã qua hạn chót |
| `LaPhone` | Màn hình hẹp (điện thoại) |
| `varHS` | Dòng của học sinh đang mở ứng dụng trong bảng `HocSinh` |
| `varNV` | Phiếu nguyện vọng đã nộp của học sinh đó (trống nếu chưa nộp) |
| `colCLB` | Danh sách câu lạc bộ, xếp theo tên |

Trang mở đầu của ứng dụng sẽ cài ở [PA13](PA13_man_dau_tien_va_chay_thu.md), khi đã có đủ các trang.

- [ ] Xong Bước 1 (hoặc đoạn thay thế) và Bước 2.
