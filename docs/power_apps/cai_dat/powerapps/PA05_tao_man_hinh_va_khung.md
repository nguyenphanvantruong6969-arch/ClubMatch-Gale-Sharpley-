# PA05 — Tạo các trang và khung tự co giãn

[← PA04](PA04_cong_thuc_app.md) · Tiếp theo: [PA06](PA06_man_khong_co_ten.md)

## Phần 1 — Tạo và đặt tên trang

Cách đổi tên bất kỳ thứ gì: ở cây bên trái, chuột phải vào tên → «Rename» → `Ctrl` + `A` → dán tên mới → `Enter`.

1. Đổi tên «Screen1» thành:
```
scrKhongCoTen
```
2. Thanh trên bấm «+ New screen» → «Blank». Đổi tên trang mới thành:
```
scrDangKy
```
3. Lặp lại bước 2, tên:
```
scrXacNhan
```
4. Lặp lại bước 2, tên:
```
scrQuanTri
```
5. Chỉ khi có câu lạc bộ thi tuyển: lặp lại bước 2, tên:
```
scrChonThi
```

👀 Cây bên trái có 4 (hoặc 5) trang đúng tên.

## Phần 2 — Khung tự co giãn cho trang đăng ký

Khung giúp nội dung **nằm giữa** trên máy tính và **trải rộng** trên điện thoại.

6. Cây bên trái: bấm `scrDangKy`.
7. Thanh trên bấm «+ Insert», dán vào ô tìm:
```
Vertical container
```
8. Bấm «Vertical container» (khung xếp dọc).
9. Đổi tên khung thành:
```
conKhung_DangKy
```
10. Điền từng mục cài đặt (cách dán ở PA04):

**«X»** — dán:
```
(Parent.Width - Self.Width) / 2
```
**«Y»** — dán:
```
0
```
**«Width»** — dán:
```
Min(Parent.Width - 32, 760)
```
**«Height»** — dán:
```
Parent.Height
```
**«LayoutGap»** — dán:
```
12
```
**«PaddingTop»** — dán:
```
16
```
**«PaddingBottom»** — dán:
```
16
```
**«LayoutOverflowY»** — dán:
```
LayoutOverflow.Scroll
```

(Không thấy mục nào trong ô thả xuống: tìm ở khung cài đặt bên phải, với tên «Gap», «Padding», «Vertical overflow».)

## Phần 3 — Chép khung sang các trang còn lại

11. Cây bên trái: chuột phải `conKhung_DangKy` → «Copy».
12. Bấm trang `scrXacNhan` → `Ctrl` + `V`. Đổi tên khung vừa dán thành:
```
conKhung_XacNhan
```
13. Bấm trang `scrKhongCoTen` → `Ctrl` + `V`. Đổi tên thành:
```
conKhung_KhongCoTen
```
14. Bấm trang `scrQuanTri` → `Ctrl` + `V`. Đổi tên thành:
```
conKhung_QuanTri
```
15. Riêng `conKhung_QuanTri`, mục **«Width»** — dán (rộng hơn cho giáo viên):
```
Min(Parent.Width - 32, 1200)
```
16. Có trang `scrChonThi`: bấm trang đó → `Ctrl` + `V`. Đổi tên thành:
```
conKhung_ChonThi
```
17. Bấm `Ctrl` + `S`.

## Quy tắc khi thêm thứ gì vào khung (dùng cho PA06 đến PA12)

- **Bấm tên khung ở cây bên trái trước**, rồi mới bấm «+ Insert». Kiểm tra: thứ vừa thêm nằm **thụt vào bên dưới** tên khung.
- Thêm **ô chữ**: «+ Insert» → dán `Text label` vào ô tìm → bấm «Text label».
- Thêm **nút bấm**: «+ Insert» → dán `Button` → bấm «Button».

- [ ] Đủ các trang, trang nào cũng có khung.
