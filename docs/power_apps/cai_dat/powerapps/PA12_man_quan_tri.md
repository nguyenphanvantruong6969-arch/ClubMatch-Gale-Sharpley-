# PA12 — Trang theo dõi cho giáo viên

[← PA11](PA11_man_chon_thi.md) · Tiếp theo: [PA17](PA17_lam_dep.md) (làm đẹp), rồi [PA13](PA13_man_dau_tien_va_chay_thu.md)

Thêm 6 thứ vào `conKhung_QuanTri`, đúng thứ tự: số đã nộp, nút làm mới, tiêu đề, danh sách chưa nộp, bảng đếm, nút mở bảng.

Các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC: xem đầu tệp [PA05](PA05_tao_man_hinh_va_khung.md).

## 1. Số học sinh đã nộp

1. Cây bên trái: bấm mũi tên cạnh `scrQuanTri` để mở ra, rồi bấm `conKhung_QuanTri`.
2. THÊM ô chữ (`Text label`).
3. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblQTSoLieu
```
4. Bấm `lblQTSoLieu`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
CountRows(NguyenVong) & " / " & CountRows(HocSinh) & " học sinh đã nộp"
```
**«Size»** — dán:
```
26
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```

👀 Trên trang ở giữa hiện dòng chữ to dạng "0 / 812 học sinh đã nộp" (số sau là số học sinh trong bảng `HocSinh`).

## 2. Nút làm mới số liệu

5. Cây bên trái: bấm `conKhung_QuanTri`.
6. THÊM nút bấm (`Button`).
7. ĐỔI TÊN nút vừa thêm thành:
```
btnLamMoi
```
8. Bấm `btnLamMoi`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Làm mới số liệu"
```
**«OnSelect»** — dán:
```
Refresh(NguyenVong); Refresh(HocSinh)
```
**«Width»** — dán:
```
Min(Parent.Width, 280)
```
**«Height»** — dán:
```
48
```

## 3. Tiêu đề "Học sinh chưa nộp"

9. Cây bên trái: bấm `conKhung_QuanTri`.
10. THÊM ô chữ (`Text label`).
11. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblQTChuaNop
```
12. Bấm `lblQTChuaNop`, rồi ĐIỀN 3 MỤC sau:

**«Text»** — dán:
```
"Học sinh chưa nộp"
```
**«FontWeight»** — dán:
```
FontWeight.Semibold
```
**«Width»** — dán:
```
Parent.Width
```

## 4. Danh sách học sinh chưa nộp

13. Cây bên trái: bấm `conKhung_QuanTri`.
14. Trên thanh lệnh bấm «Insert», bấm vào ô tìm kiếm, dán:
```
Blank vertical gallery
```
15. Bấm dòng «Blank vertical gallery» (danh sách cuộn dọc, trống) trong kết quả.
16. Chỉ khi hiện bảng nhỏ «Select a data source»: bấm phím `Esc` để đóng bảng đó.

👀 Ở cây bên trái, dưới `conKhung_QuanTri` có thêm «Gallery1» (số có thể khác).

17. ĐỔI TÊN danh sách vừa thêm thành:
```
galChuaNop
```
18. Bấm `galChuaNop`, rồi ĐIỀN 5 MỤC sau:

**«Items»** — dán:
```
Filter(HocSinh, !(student_id in NguyenVong.student_id))
```
**«WrapCount»** — dán (máy tính hiện 3 cột):
```
If(App.Width < 900, 1, 3)
```
**«TemplateSize»** — dán:
```
50
```
**«Height»** — dán:
```
400
```
**«Width»** — dán:
```
Parent.Width
```

19. Cây bên trái: bấm `galChuaNop` (để ô chữ sắp thêm nằm **bên trong** danh sách).
20. THÊM ô chữ (`Text label`).

👀 Ở cây bên trái, ô chữ mới nằm thụt dưới `galChuaNop`. Trên trang ở giữa, mỗi dòng của danh sách đều có ô chữ đó.

21. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblChuaNopDong
```
22. Bấm `lblChuaNopDong`, rồi ĐIỀN 3 MỤC sau:

**«Text»** — dán:
```
ThisItem.student_id & " – " & ThisItem.name & " (" & ThisItem.class_id & ")"
```
**«Width»** — dán:
```
Parent.TemplateWidth
```
**«Height»** — dán:
```
Parent.TemplateHeight
```

👀 Danh sách hiện mã, họ tên, lớp của các học sinh chưa nộp (lúc này là tất cả).

⚠️ Không tìm thấy «Blank vertical gallery» ở bước 14: dán `Vertical gallery` thay vào, bấm «Vertical gallery». Danh sách này có sẵn vài thứ trong dòng mẫu: ở cây bên trái, mở `galChuaNop`, bấm chuột phải vào **từng** thứ bên trong → «Delete», cho đến khi bên trong trống. Rồi làm tiếp từ bước 17.
⚠️ Ở bước 20, ô chữ nằm ngoài danh sách (ngang hàng `galChuaNop`): bấm `Ctrl` + `Z`. Trên trang ở giữa, bấm vào **dòng đầu tiên** của danh sách (hiện hình cây bút ở góc trên bên trái danh sách), rồi làm lại bước 20.

## 5. Bảng đếm nguyện vọng 1 theo câu lạc bộ

23. Cây bên trái: bấm `conKhung_QuanTri`.
24. Làm lại bước 14 đến 16 để thêm một «Blank vertical gallery» nữa.
25. ĐỔI TÊN danh sách vừa thêm thành:
```
galThongKe
```
26. Bấm `galThongKe`, rồi ĐIỀN 4 MỤC sau:

**«Items»** — dán:
```
AddColumns(colCLB, NV1, With({ma: club_id}, CountRows(Filter(NguyenVong, pref_1 = ma))))
```
**«TemplateSize»** — dán:
```
50
```
**«Height»** — dán:
```
400
```
**«Width»** — dán:
```
Parent.Width
```

27. Cây bên trái: bấm `galThongKe`.
28. THÊM ô chữ (`Text label`).
29. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblThongKeDong
```
30. Bấm `lblThongKeDong`, rồi ĐIỀN 3 MỤC sau:

**«Text»** — dán:
```
ThisItem.name & ":  " & ThisItem.NV1 & " NV1 / chỉ tiêu " & ThisItem.capacity
```
**«Width»** — dán:
```
Parent.TemplateWidth
```
**«Height»** — dán:
```
Parent.TemplateHeight
```

👀 Mỗi dòng dạng "CLB Bóng rổ:  0 NV1 / chỉ tiêu 20".

⚠️ Ở bước 26, gạch đỏ ngay tại chữ `NV1` trong «Items»: Power Apps của bạn dùng cách viết cũ. Dán bản này thay thế (khác ở hai dấu ngoặc kép quanh `NV1`):
```
AddColumns(colCLB, "NV1", With({ma: club_id}, CountRows(Filter(NguyenVong, pref_1 = ma))))
```

## 6. Nút mở bảng để tải dữ liệu về

31. Cây bên trái: bấm `conKhung_QuanTri`.
32. THÊM nút bấm (`Button`).
33. ĐỔI TÊN nút vừa thêm thành:
```
btnMoList
```
34. Bấm `btnMoList`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Mở danh sách để xuất CSV"
```
**«Width»** — dán:
```
Min(Parent.Width, 280)
```
**«Height»** — dán:
```
48
```
**«OnSelect»** — dán:
```
Launch("https://truong.sharepoint.com/sites/CLB-2026/Lists/NguyenVong")
```

35. Trong ô dài của mục «OnSelect» vừa dán: bôi đen đoạn `https://truong.sharepoint.com/sites/CLB-2026` (từ `https` đến hết `CLB-2026`), dán ĐỊA CHỈ TRANG của bạn đè lên. Giữ nguyên đuôi `/Lists/NguyenVong` và hai dấu ngoặc kép.
36. Bấm `Ctrl` + `S`.

## Kiểm tra

1. Cây bên trái: bấm `scrQuanTri`, bấm **▶**.
2. Bấm nút "Mở danh sách để xuất CSV".

👀 Trình duyệt mở thẻ mới, hiện bảng `NguyenVong` trên SharePoint.

3. Quay lại thẻ Power Apps, bấm `Esc`.

- [ ] Đủ 6 thứ, đúng thứ tự.
- [ ] Nút mở đúng bảng `NguyenVong`.

> Hình tam giác vàng hiện cạnh `lblQTSoLieu`, `galChuaNop`, `galThongKe`: đây là lời nhắc rằng ứng dụng chỉ đếm đúng khi mỗi bảng có **không quá 2000 dòng** (đã cài ở PA02, Phần 5). Trường dưới 2000 học sinh thì bỏ qua lời nhắc. Trường đông hơn: báo người phụ trách.
