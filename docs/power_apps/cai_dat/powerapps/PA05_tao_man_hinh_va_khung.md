# PA05 — Tạo các trang và khung tự co giãn

[← PA04](PA04_cong_thuc_app.md) · Tiếp theo: [PA06](PA06_man_khong_co_ten.md)

## Ba thao tác dùng suốt từ đây (đọc một lần)

**ĐỔI TÊN** một thứ:
1. Ở cây bên trái, bấm chuột phải vào tên thứ đó.
2. Bấm «Rename».
3. Bấm `Ctrl` + `A`, rồi `Ctrl` + `V` để dán tên mới từ ô xám.
4. Bấm phím `Enter`.

**THÊM** một thứ vào một khung:
1. Ở cây bên trái, bấm một lần vào **tên khung** (tên được tô sáng). Bước này quyết định thứ mới nằm ở đâu, không được bỏ.
2. Trên thanh lệnh, bấm «Insert».
3. Bấm vào ô tìm kiếm của bảng vừa mở, dán tên loại (lấy từ ô xám, ví dụ `Text label`).
4. Bấm đúng dòng mang tên đó trong kết quả. Có hai dòng cùng tên: bấm dòng nằm dưới chữ «Classic».

👀 Ở cây bên trái, thứ mới xuất hiện **thụt vào, nằm bên dưới tên khung**, và đang được tô sáng. Trên trang ở giữa, nó nằm **dưới cùng** trong khung.

⚠️ Thứ mới nằm ngang hàng với khung (không thụt vào): bấm `Ctrl` + `Z` để bỏ, rồi làm lại từ bước 1.

Bốn loại sẽ dùng:

| Hướng dẫn ghi | Dán vào ô tìm | Là gì |
|---|---|---|
| THÊM ô chữ | `Text label` | Một dòng chữ |
| THÊM nút bấm | `Button` | Một nút |
| THÊM khung dọc | `Vertical container` | Khung xếp các thứ bên trong từ trên xuống |
| THÊM khung ngang | `Horizontal container` | Khung xếp các thứ bên trong từ trái sang |

**ĐIỀN MỤC**: là 5 bước "Cách dán một mục cài đặt" ở [PA04](PA04_cong_thuc_app.md). Nhớ bấm tên thứ cần cài ở cây bên trái trước.

## Phần 1 — Tạo và đặt tên trang

1. ĐỔI TÊN «Screen1» thành:
```
scrKhongCoTen
```
2. Trên thanh lệnh, bấm «New screen», rồi bấm «Blank».

👀 Cây bên trái có thêm «Screen2» (số có thể khác).

3. ĐỔI TÊN trang vừa tạo thành:
```
scrDangKy
```
4. Làm lại bước 2, rồi ĐỔI TÊN trang vừa tạo thành:
```
scrXacNhan
```
5. Làm lại bước 2, rồi ĐỔI TÊN trang vừa tạo thành:
```
scrQuanTri
```
6. Chỉ khi có bảng `ChonThi` (đã làm SP07): làm lại bước 2, rồi ĐỔI TÊN trang vừa tạo thành:
```
scrChonThi
```

👀 Cây bên trái có 4 trang `scrKhongCoTen`, `scrDangKy`, `scrXacNhan`, `scrQuanTri` (và `scrChonThi`).

## Phần 2 — Khung tự co giãn cho trang đăng ký

Khung giúp nội dung **nằm giữa** trên máy tính và **trải rộng** trên điện thoại.

7. Cây bên trái: bấm `scrDangKy`.
8. THÊM khung dọc (dán vào ô tìm):
```
Vertical container
```
9. ĐỔI TÊN khung vừa thêm thành:
```
conKhung_DangKy
```
10. Bấm `conKhung_DangKy` ở cây bên trái, rồi ĐIỀN 8 MỤC sau, từng mục một:

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

👀 Trên trang ở giữa, khung là một hình chữ nhật cao hết trang, nằm chính giữa theo chiều ngang.

## Phần 3 — Chép khung sang các trang còn lại

11. Cây bên trái: bấm chuột phải `conKhung_DangKy`, bấm «Copy».
12. Cây bên trái: bấm một lần vào `scrXacNhan`.
13. Bấm một lần vào vùng trắng của trang ở giữa, rồi bấm `Ctrl` + `V`.

👀 Dưới `scrXacNhan` ở cây bên trái có một khung tên `conKhung_DangKy_1`.

14. ĐỔI TÊN khung vừa dán thành:
```
conKhung_XacNhan
```
15. Làm lại bước 12 và 13 với trang `scrKhongCoTen`. ĐỔI TÊN khung vừa dán thành:
```
conKhung_KhongCoTen
```
16. Làm lại bước 12 và 13 với trang `scrQuanTri`. ĐỔI TÊN khung vừa dán thành:
```
conKhung_QuanTri
```
17. Bấm `conKhung_QuanTri`, ĐIỀN MỤC **«Width»** — dán (rộng hơn, vì giáo viên xem trên máy tính):
```
Min(Parent.Width - 32, 1200)
```
18. Chỉ khi có trang `scrChonThi`: làm lại bước 12 và 13 với trang `scrChonThi`. ĐỔI TÊN khung vừa dán thành:
```
conKhung_ChonThi
```
19. Bấm `Ctrl` + `S`.

⚠️ Bấm `Ctrl` + `V` mà không có gì xuất hiện: làm lại bước 11 (sao chép lại), rồi bước 12 và 13.
⚠️ Khung dán xong nằm lệch khỏi giữa trang: bấm tên khung, ĐIỀN lại hai mục «X» và «Y» như ở bước 10.

## Kiểm tra

👀 Ở cây bên trái, bấm mũi tên nhỏ cạnh từng tên trang để mở ra: mỗi trang có đúng một khung, tên khung khớp tên trang (`scrDangKy` chứa `conKhung_DangKy`, `scrXacNhan` chứa `conKhung_XacNhan`, …).

- [ ] Đủ các trang, trang nào cũng có đúng một khung.
