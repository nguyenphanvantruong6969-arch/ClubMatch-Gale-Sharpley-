# PA04 — Điền hạn chót, số nguyện vọng, giáo viên phụ trách

[← PA03](PA03_noi_du_lieu.md) · Tiếp theo: [PA05](PA05_tao_man_hinh_va_khung.md)

## Cách dán một đoạn cài đặt (dùng cho mọi tệp PA)

Mỗi thứ trên màn hình (trang, ô chữ, nút bấm…) có nhiều **mục cài đặt**. Cách điền một mục:

1. Ở **cây bên trái**, bấm tên của thứ cần cài.
2. Ở **thanh công thức** phía trên, bấm **ô thả xuống nhỏ bên trái** → chọn tên mục cài đặt (ví dụ «Text», «OnSelect»).
3. Bấm vào **ô dài có chữ «fx»** bên phải, bấm `Ctrl` + `A` để chọn hết chữ cũ.
4. Bấm `Ctrl` + `V` để dán đoạn đã sao chép từ ô xám.
5. Bấm ra chỗ trống bên ngoài.

Các tệp sau chỉ ghi ngắn: **«Tên mục» — dán:** kèm một ô xám.

⚠️ Có gạch chân đỏ vì nhắc đến trang hoặc nút **chưa tạo**: bình thường, sẽ hết khi làm xong các tệp sau.
⚠️ Báo lỗi ở chữ `club_id` hoặc `student_id`: ở **mọi** đoạn đã dán, thay chữ đó bằng `Title`.
⚠️ Dán vào báo lỗi gần như toàn bộ: có thể máy đang để ngôn ngữ dùng dấu chấm phẩy. Đổi ngôn ngữ trình duyệt sang tiếng Anh, tải lại trang, dán lại.

## Bước 1 — Thông tin chung của ứng dụng

1. Cây bên trái: bấm «App».
2. Ô thả xuống: chọn «Formulas».
3. Dán đoạn dưới. Sau đó **sửa 3 dòng đầu** cho đúng trường bạn:
```
HanChot = DateTimeValue("2026-12-01 17:00");
SoNguyenVongToiDa = 5;
DSQuanTri = ["gv.a@truong.edu.vn", "gv.b@truong.edu.vn"];
EmailToi = Lower(User().Email);
LaQuanTri = EmailToi in DSQuanTri;
HetHan = Now() > HanChot;
LaPhone = App.Width < 600;
```

Sửa thế nào:
- Dòng 1: ngày giờ hết hạn, viết theo kiểu `năm-tháng-ngày giờ:phút`.
- Dòng 2: số câu lạc bộ tối đa học sinh được chọn, từ 1 đến 10.
- Dòng 3: thư điện tử giáo viên phụ trách, **chữ thường**, mỗi địa chỉ trong ngoặc kép, cách nhau dấu phẩy.

⚠️ Không có mục «Formulas» trong ô thả xuống: bỏ qua Bước 1, làm **Bước 2 – cách thay thế**.

## Bước 2 — Việc làm khi ứng dụng mở

4. Cây bên trái: «App». Ô thả xuống: «OnStart». Dán:
```
Set(varHS, LookUp(HocSinh, email = Lower(User().Email)));
Set(varNV, LookUp(NguyenVong, student_id = varHS.student_id));
ClearCollect(colCLB, SortByColumns(CLB, "name"))
```

**Bước 2 – cách thay thế** (chỉ dùng khi không có mục «Formulas»). Dán đoạn này vào «OnStart» thay cho đoạn trên, rồi sửa 3 dòng đầu như hướng dẫn ở Bước 1:
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

5. Cây bên trái: bấm «⋯» cạnh chữ «App» → «Run OnStart».

👀 Không có gạch đỏ ở «OnStart».

6. Bấm `Ctrl` + `S`.

## Bước 3 — Trang mở đầu

**Để sau.** Làm ở [PA13](PA13_man_dau_tien_va_chay_thu.md), khi đã có đủ các trang.

- [ ] Xong Bước 1 (hoặc cách thay thế) và Bước 2.
