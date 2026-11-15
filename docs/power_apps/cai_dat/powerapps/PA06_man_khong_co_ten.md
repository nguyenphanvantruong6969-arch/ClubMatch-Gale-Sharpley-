# PA06 — Trang báo "không có tên"

[← PA05](PA05_tao_man_hinh_va_khung.md) · Tiếp theo: [PA07](PA07_dang_ky_phan_tren.md)

Trang này hiện khi thư điện tử đăng nhập không có trong bảng học sinh.

1. Cây bên trái: bấm `conKhung_KhongCoTen`.
2. Thêm một ô chữ («+ Insert» → «Text label»).
3. Đổi tên ô chữ thành:
```
lblKhongCoTen
```
4. Điền các mục:

**«Text»** — dán:
```
"Email " & User().Email & " chưa có trong danh sách học sinh. Em liên hệ giáo viên chủ nhiệm."
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
If(LaPhone, 18, 16)
```
**«Color»** — dán:
```
Color.DarkRed
```

5. Bấm `Ctrl` + `S`.

- [ ] Xong.
