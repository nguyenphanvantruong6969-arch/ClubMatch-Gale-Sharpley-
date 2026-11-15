# PA06 — Trang báo "không có tên"

[← PA05](PA05_tao_man_hinh_va_khung.md) · Tiếp theo: [PA07](PA07_dang_ky_phan_tren.md)

Trang này hiện khi thư điện tử đăng nhập không có trong bảng học sinh.

Các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC: xem đầu tệp [PA05](PA05_tao_man_hinh_va_khung.md).

1. Cây bên trái: bấm mũi tên cạnh `scrKhongCoTen` để mở ra, rồi bấm `conKhung_KhongCoTen`.
2. THÊM ô chữ (dán vào ô tìm):
```
Text label
```
3. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblKhongCoTen
```
4. Bấm `lblKhongCoTen` ở cây bên trái, rồi ĐIỀN 5 MỤC sau:

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

👀 Trên trang ở giữa có dòng chữ đỏ sẫm, bắt đầu bằng "Email" kèm thư điện tử của chính bạn, chữ tự xuống dòng trong khung.

5. Bấm `Ctrl` + `S`.

- [ ] Xong.
