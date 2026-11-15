# PA10 — Trang xác nhận đã nộp

[← PA09](PA09_dang_ky_nut_nop.md) · Tiếp theo: [PA11](PA11_man_chon_thi.md)

Mọi thứ dưới đây thêm vào `conKhung_XacNhan`. Mỗi lần thêm: bấm `conKhung_XacNhan` ở cây bên trái trước.

## 1. Ô chữ tiêu đề

Thêm «Text label». Tên:
```
lblXNTieuDe
```
**«Text»**:
```
"Đã lưu nguyện vọng"
```
**«Size»**:
```
If(LaPhone, 22, 26)
```
**«Width»**:
```
Parent.Width
```

## 2. Ô chữ liệt kê các nguyện vọng

Thêm «Text label». Tên:
```
lblXNTomTat
```
**«Text»**:
```
"Lần lưu: " & Text(varNV.nop_luc, "dd/mm/yyyy hh:mm") & Char(10) &
Concat(
  Filter(Table(
    {k:1, c:varNV.pref_1},{k:2, c:varNV.pref_2},{k:3, c:varNV.pref_3},{k:4, c:varNV.pref_4},{k:5, c:varNV.pref_5},
    {k:6, c:varNV.pref_6},{k:7, c:varNV.pref_7},{k:8, c:varNV.pref_8},{k:9, c:varNV.pref_9},{k:10, c:varNV.pref_10}),
    !IsBlank(c)),
  k & ". " & LookUp(colCLB, club_id = c).name, Char(10))
```
**«Width»**:
```
Parent.Width
```
**«AutoHeight»**:
```
true
```
**«Size»**:
```
If(LaPhone, 16, 14)
```

## 3. Ô chữ nhắc nhở

Thêm «Text label». Tên:
```
lblXNNhac
```
**«Text»**:
```
"Em có thể sửa đến hạn chót. Lần lưu cuối cùng được tính."
```
**«Width»**:
```
Parent.Width
```
**«AutoHeight»**:
```
true
```

## 4. Nút "Sửa lại"

Thêm «Button». Tên:
```
btnSuaLai
```
**«Text»**:
```
"Sửa lại"
```
**«OnSelect»**:
```
Navigate(scrDangKy, ScreenTransition.Fade)
```
**«Visible»**:
```
!HetHan
```
**«Width»**:
```
Parent.Width
```
**«Height»**:
```
48
```

Bấm `Ctrl` + `S`.

- [ ] Xong 4 thứ trên.
