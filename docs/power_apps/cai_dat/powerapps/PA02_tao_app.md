# PA02 — Tạo ứng dụng trống, chỉnh cho điện thoại và máy tính

[← PA01](PA01_dang_nhap_moi_truong.md) · Tiếp theo: [PA03](PA03_noi_du_lieu.md)

## Phần 1 — Tạo ứng dụng

1. Mở make.powerapps.com. Nhìn cái tên cạnh hình cái chuông: phải đúng KHU LÀM VIỆC.
2. Ở cột bên trái, bấm «Create».
3. Trên trang vừa mở, bấm ô «Blank app» (bản khác ghi «Start with a blank canvas» hoặc «Create from blank»).
4. Chỉ khi hiện bảng cho chọn kiểu ứng dụng: ở ô «Blank canvas app», bấm «Create».

👀 Hiện hộp nhỏ có ô «App name» và mục «Format».

5. Bấm vào ô «App name», dán:
```
DangKyCLB
```
6. Ở mục «Format», bấm chọn «Tablet». (Không chọn «Phone». Phần 3 sẽ chỉnh cho vừa cả điện thoại.)
7. Bấm «Create».
8. Chỉ khi hiện bảng chào «Welcome to Power Apps Studio»: bấm «Skip».

👀 **Màn hình thiết kế** mở ra. Từ giờ các tệp PA dùng 5 tên gọi sau, hãy nhìn và nhớ vị trí:

| Tên gọi trong hướng dẫn | Nằm ở đâu | Trông thế nào |
|---|---|---|
| **Trang ở giữa** | Giữa màn hình | Một hình chữ nhật trắng |
| **Cây bên trái** | Khung bên trái | Danh sách có «App» và «Screen1» |
| **Thanh công thức** | Ngay dưới thanh lệnh trên cùng, chạy ngang màn hình | Bên trái là một **ô thả xuống nhỏ**, giữa có chữ «fx», bên phải là một **ô dài** |
| **Khung bên phải** | Khung bên phải | Có tên thứ đang chọn và các thẻ «Properties», «Advanced» |
| **Thanh lệnh** | Hàng trên cùng | Có «Insert», «Add data», «New screen», và ở đầu bên phải có các biểu tượng lưu, phát hành, nút ▶ |

⚠️ Không thấy cây bên trái: ở dải biểu tượng dọc sát mép trái màn hình, bấm biểu tượng trên cùng (hình các lớp giấy xếp chồng, tên «Tree view»).

## Phần 2 — Lưu lần đầu

9. Bấm `Ctrl` + `S`.
10. Chỉ khi hiện hộp hỏi tên: dán `DangKyCLB` vào ô tên, bấm «Save».

👀 Ở đầu bên phải thanh lệnh thoáng hiện chữ «Saved» hoặc dấu tích.

## Phần 3 — Cho vừa cả điện thoại và máy tính

11. Trên thanh lệnh, bấm «Settings». Không thấy chữ «Settings»: bấm «⋯» ở cuối thanh lệnh, rồi bấm «Settings».

👀 Mở bảng «Settings», cột trái của bảng có «General», «Display», «Updates», «Support».

12. Ở cột trái của bảng, bấm «Display».
13. Tìm «Scale to fit», gạt công tắc sang **Off**.
14. Tìm «Lock aspect ratio», gạt công tắc sang **Off**.
15. Tìm «Lock orientation», gạt công tắc sang **Off**.
16. Bấm dấu X ở góc trên bên phải bảng để đóng.
17. Bấm `Ctrl` + `S`.

👀 Kéo mép cửa sổ trình duyệt cho hẹp lại: trang ở giữa hẹp theo.

## Phần 4 — Ba tuỳ chọn cần chỉnh

Bảng «Settings» có **ô tìm kiếm** ở phía trên. Dùng ô đó để tìm từng tuỳ chọn.

18. Bấm «Settings» trên thanh lệnh.
19. Bấm vào ô tìm kiếm của bảng, dán:
```
Formula-level error management
```
20. Thấy tuỳ chọn tên đó: gạt sang **On**. Không có kết quả nào: bỏ qua (bản mới đã bật sẵn).
21. Xoá chữ trong ô tìm kiếm, dán:
```
Named formulas
```
22. Thấy tuỳ chọn tên đó: gạt sang **On**. Không có kết quả nào: bỏ qua (bản mới đã bật sẵn).
23. Xoá chữ trong ô tìm kiếm, dán:
```
Modern controls and themes
```
24. Thấy tuỳ chọn tên đó: gạt sang **Off**. Không có kết quả nào: bỏ qua.

    Vì sao: Power Apps có hai bộ nút, bộ cũ («Classic») và bộ mới. Bộ hướng dẫn này viết cho **bộ cũ**. Tắt tuỳ chọn này thì chỉ còn bộ cũ, không chọn nhầm được.

25. Đóng bảng (dấu X), bấm `Ctrl` + `S`.

## Phần 5 — Cho phép đọc đủ danh sách dài

26. Bấm «Settings» trên thanh lệnh.
27. Bấm vào ô tìm kiếm của bảng, dán:
```
Data row limit
```
28. Bấm vào ô số của tuỳ chọn đó, bấm `Ctrl` + `A`, dán:
```
2000
```
29. Đóng bảng (dấu X), bấm `Ctrl` + `S`.

⚠️ Bảng «Settings» của bạn không có ô tìm kiếm: «Data row limit» nằm trong mục «General»; ba tuỳ chọn ở Phần 4 nằm trong mục «Updates» (bấm lần lượt các thẻ «New», «Preview», «Experimental», «Retired» để tìm). Không tìm thấy thì bỏ qua.

- [ ] Xong 5 phần.
