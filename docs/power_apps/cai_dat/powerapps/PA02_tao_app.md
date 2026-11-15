# PA02 — Tạo ứng dụng trống, chỉnh cho điện thoại và máy tính

Mất khoảng 10 phút · [← PA01](PA01_dang_nhap_moi_truong.md) · Tiếp theo: [PA03](PA03_noi_du_lieu.md)

## Phần 1 — Tạo ứng dụng

1. Vào make.powerapps.com, kiểm tra góc trên phải đúng KHU LÀM VIỆC.
2. Cột trái bấm «Create».

👀 Trang «Create an app», có phần «Start from design».

3. Bấm ô «Create from blank». Tên khác có thể gặp: «Blank app» → «Blank canvas app», hoặc «Start from blank».
4. Bấm vào ô «App name», dán:
```
DangKyCLB
```
5. Ở «Format», chọn «Tablet» (máy tính bảng). Đừng chọn «Phone»; bước sau sẽ chỉnh cho vừa cả điện thoại.
6. Bấm «Create».
7. Nếu hiện bảng chào «Welcome to Power Apps Studio»: bấm «Skip».

👀 **Màn hình thiết kế**: giữa là một trang trắng; bên trái là **cây bên trái** có «App» và «Screen1»; phía trên có một **thanh công thức** gồm một ô thả xuống nhỏ bên trái và một ô dài có chữ «fx».

## Phần 2 — Lưu lần đầu

8. Bấm `Ctrl` + `S`.
9. Nếu hỏi tên: dán `DangKyCLB` → bấm «Save».

## Phần 3 — Cho vừa cả điện thoại và máy tính

10. Thanh trên cùng bấm «Settings» (hình bánh răng). Không thấy: bấm «⋯» → «Settings», hoặc «File» → «Settings».
11. Bấm mục «Display».
12. «Scale to fit»: gạt sang **tắt**.
13. «Lock aspect ratio»: gạt sang **tắt**.
14. «Lock orientation»: gạt sang **tắt**.
15. Đóng bảng (dấu X), bấm `Ctrl` + `S`.

👀 Thu nhỏ cửa sổ trình duyệt thì trang trắng co theo.

## Phần 4 — Bật hai tuỳ chọn cần dùng

16. «Settings» → mục «Updates» (có thể tên «Upcoming features»).
17. Tìm «Named formulas»: nếu có thì bật. Không thấy là bình thường (bản mới đã bật sẵn).
18. Tìm «Formula-level error management»: nếu có thì bật.
19. Đóng bảng, bấm `Ctrl` + `S`.

## Phần 5 — Cho phép đọc đủ danh sách dài

20. «Settings» → mục «General».
21. Tìm «Data row limit», bấm vào ô số, `Ctrl` + `A`, dán:
```
2000
```
22. Đóng bảng, bấm `Ctrl` + `S`.

- [ ] Xong. Không tìm thấy nút ở Phần 4 thì bỏ qua; PA04 có cách thay thế.
