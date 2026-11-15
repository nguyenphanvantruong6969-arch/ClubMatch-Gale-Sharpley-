# PA03 — Nối ứng dụng với các bảng dữ liệu

[← PA02](PA02_tao_app.md) · Tiếp theo: [PA04](PA04_cong_thuc_app.md)

**Cần có:** đã tạo các bảng ở SP04 đến SP07; có ĐỊA CHỈ TRANG; đang ở màn hình thiết kế của `DangKyCLB`.

(Đã đóng màn hình thiết kế: mở make.powerapps.com → cột trái bấm «Apps» → đưa chuột vào dòng `DangKyCLB` → bấm hình cây bút «Edit».)

1. Trên thanh lệnh, bấm «Add data».

👀 Mở một bảng nhỏ có ô tìm kiếm «Search».

2. Bấm vào ô tìm kiếm đó, dán:
```
SharePoint
```
3. Bấm dòng «SharePoint» (biểu tượng chữ S trên nền xanh lá) trong kết quả.
4. Chỉ khi hiện dòng «Add a connection» (hoặc «+ Add a connection»): bấm dòng đó; bên phải mở khung, để nguyên lựa chọn «Connect directly (cloud services)», bấm «Connect».
5. Chỉ khi hiện hộp xin quyền: bấm «Allow».

👀 Bên phải mở khung «Connect to a SharePoint site».

6. Bấm vào ô «Enter the SharePoint URL…» ở đầu khung, dán ĐỊA CHỈ TRANG.
7. Bấm «Connect».

👀 Khung đổi thành «Choose a list», liệt kê các bảng trong trang, mỗi bảng có một ô đánh dấu.

8. Bấm đánh dấu ô `CLB`.
9. Bấm đánh dấu ô `HocSinh`.
10. Bấm đánh dấu ô `NguyenVong`.
11. Có bảng `ChonThi` (đã làm SP07): bấm đánh dấu ô `ChonThi`.
12. Bấm «Connect» ở cuối khung.
13. Ở dải biểu tượng dọc sát mép trái màn hình, bấm hình **cái trụ tròn** (tên «Data»).

👀 Khung bên trái liệt kê `CLB`, `HocSinh`, `NguyenVong` (và `ChonThi`).

14. Bấm `Ctrl` + `S`.
15. Ở dải biểu tượng dọc, bấm biểu tượng trên cùng («Tree view») để quay lại cây bên trái.

⚠️ Ở bước 8, không thấy tên bảng trong danh sách: ĐỊA CHỈ TRANG dán sai. Bấm mũi tên quay lại ở đầu khung, làm lại bước 6. Vẫn không thấy: tài khoản đang đăng nhập Power Apps khác tài khoản đã tạo bảng.
⚠️ Ở bước 13, một bảng hiện thành `CLB_1`: bạn đã nối bảng đó hai lần. Đưa chuột vào dòng `CLB_1` → bấm «⋯» → «Remove».

- [ ] Khung «Data» có đủ tên các bảng, không có tên nào mang đuôi `_1`.
