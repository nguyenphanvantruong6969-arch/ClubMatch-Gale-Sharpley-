# PA10 — Trang xác nhận đã nộp

[← PA09](PA09_dang_ky_nut_nop.md) · Tiếp theo: [PA11](PA11_man_chon_thi.md)

Thêm 4 thứ vào `conKhung_XacNhan`, đúng thứ tự: tiêu đề, danh sách nguyện vọng, lời nhắc, nút "Sửa lại".

Các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC: xem đầu tệp [PA05](PA05_tao_man_hinh_va_khung.md).

## 1. Ô chữ tiêu đề

1. Cây bên trái: bấm mũi tên cạnh `scrXacNhan` để mở ra, rồi bấm `conKhung_XacNhan`.
2. THÊM ô chữ (`Text label`).
3. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblXNTieuDe
```
4. Bấm `lblXNTieuDe`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Đã lưu nguyện vọng"
```
**«Size»** — dán:
```
If(LaPhone, 22, 26)
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```

## 2. Ô chữ liệt kê các nguyện vọng

5. Cây bên trái: bấm `conKhung_XacNhan`.
6. THÊM ô chữ (`Text label`).
7. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblXNTomTat
```
8. Bấm `lblXNTomTat`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Lần lưu: " & Text(varNV.nop_luc, "dd/mm/yyyy hh:mm") & Char(10) &
Concat(
  Filter(Table(
    {k:1, c:varNV.pref_1},{k:2, c:varNV.pref_2},{k:3, c:varNV.pref_3},{k:4, c:varNV.pref_4},{k:5, c:varNV.pref_5},
    {k:6, c:varNV.pref_6},{k:7, c:varNV.pref_7},{k:8, c:varNV.pref_8},{k:9, c:varNV.pref_9},{k:10, c:varNV.pref_10}),
    !IsBlank(c)),
  k & ". " & LookUp(colCLB, club_id = c).name, Char(10))
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```
**«Size»** — dán:
```
If(LaPhone, 16, 14)
```

## 3. Ô chữ nhắc nhở

9. Cây bên trái: bấm `conKhung_XacNhan`.
10. THÊM ô chữ (`Text label`).
11. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblXNNhac
```
12. Bấm `lblXNNhac`, rồi ĐIỀN 3 MỤC sau:

**«Text»** — dán:
```
"Em có thể sửa đến hạn chót. Lần lưu cuối cùng được tính."
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```

## 4. Nút "Sửa lại"

13. Cây bên trái: bấm `conKhung_XacNhan`.
14. THÊM nút bấm (`Button`).
15. ĐỔI TÊN nút vừa thêm thành:
```
btnSuaLai
```
16. Bấm `btnSuaLai`, rồi ĐIỀN 5 MỤC sau:

**«Text»** — dán:
```
"Sửa lại"
```
**«OnSelect»** — dán:
```
Navigate(scrDangKy, ScreenTransition.Fade)
```
**«Visible»** — dán:
```
!HetHan
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
48
```

17. Bấm `Ctrl` + `S`.

## Kiểm tra

👀 Trên trang ở giữa, từ trên xuống: chữ to "Đã lưu nguyện vọng"; dòng "Lần lưu:" (ngày giờ còn trống vì chưa có phiếu nào); lời nhắc; nút "Sửa lại".

- [ ] Đủ 4 thứ, đúng thứ tự, không gạch đỏ.
