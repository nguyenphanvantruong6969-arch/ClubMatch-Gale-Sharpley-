# SP01 — Kiểm tra tài khoản và quyền

Mất khoảng 10 phút · [← Mục lục](../00_MUC_LUC.md) · Tiếp theo: [SP02](SP02_tao_site.md)

**Cần có:** máy tính có trình duyệt Edge hoặc Chrome, địa chỉ thư điện tử của trường (dạng `ten@truong.edu.vn`).

## A. Tài khoản của trường

1. Mở trình duyệt. Bấm vào thanh địa chỉ ở trên cùng, dán:
```
https://www.office.com
```
2. Bấm `Enter`.
3. Bấm «Sign in» (Đăng nhập).
4. Gõ thư điện tử của trường, bấm «Next».
5. Gõ mật khẩu, bấm «Sign in».
6. Nếu hỏi «Stay signed in?»: máy dùng chung bấm «No», máy riêng bấm «Yes».

👀 Trang chủ Microsoft 365, có tên hoặc ảnh của bạn ở góc trên bên phải.

- [ ] **Đạt A**

## B. Được dùng Power Apps

7. Mở thẻ mới (`Ctrl` + `T`), dán vào thanh địa chỉ:
```
https://make.powerapps.com
```
8. Nếu hỏi quốc gia: chọn «Vietnam», bấm «Get started».

👀 Trang Power Apps, cột bên trái có chữ «Home», «Create», «Apps»…

⚠️ Nếu hiện «You need a license» hoặc «Your organization has not enabled Power Apps»: bạn **chưa được cấp quyền**. Gửi tin nhắn ở cuối tệp này cho bộ phận tin học.

- [ ] **Đạt B**

## C. Được tạo trang SharePoint

9. Quay lại thẻ office.com.
10. Bấm hình **9 chấm vuông** ở góc trên bên trái → bấm «SharePoint». Không thấy thì gõ chữ `SharePoint` vào ô tìm kiếm trên cùng.
11. Bấm «+ Create site» (chỉ để thử, chưa tạo thật).

👀 Hiện hộp chọn «Team site» / «Communication site» → **bạn có quyền**. Bấm dấu X để đóng lại.

⚠️ Không có nút «Create site», hoặc báo «Site is unavailable due to admin setting» → **bạn chưa có quyền**. Xem phần "Khi bị chặn" ở SP02.

- [ ] **Đạt C**

## D. Nhóm tài khoản học sinh (bổ sung sau cũng được)

12. Hỏi bộ phận tin học: trường đã có **nhóm** gom tài khoản học sinh chưa (ví dụ "HS-Khoi10")?
13. Có rồi: ghi tên nhóm vào sổ tay. Chưa có: xin tạo nhóm tên `HS-CLB-2026` (có trong tin nhắn mẫu bên dưới).

- [ ] **Đạt D** (hoặc đã gửi đề nghị)

## E. Chuẩn bị sẵn

- [ ] Danh sách học sinh: Mã học sinh, Họ tên, Lớp, thư điện tử của trường, Nhóm ưu tiên (nếu có).
- [ ] Danh sách câu lạc bộ: Mã (viết liền, không dấu, ví dụ `clb_bongro`), Tên, Số chỗ, Số chỗ ưu tiên, Nhóm ưu tiên.
- [ ] Hạn chót nộp (ngày, giờ).
- [ ] Thư điện tử của các giáo viên phụ trách.

## Tin nhắn gửi bộ phận tin học

Sao chép, rồi sửa các chỗ trong ngoặc vuông `[ ]`:

```
Kính gửi bộ phận tin học trường [tên trường],

Em là [họ tên], [chức vụ]. Em cần làm ứng dụng đăng ký câu lạc bộ cho học sinh
bằng Power Apps, lưu dữ liệu trên SharePoint (chỉ dùng phần có sẵn trong gói
Microsoft 365 Education, không mua thêm). Nhờ anh/chị cấp cho tài khoản
[thư điện tử của em] những mục còn thiếu dưới đây:

[ ] 1. Quyền dùng Power Apps (gói "Power Apps for Microsoft 365").
[ ] 2. Một trang SharePoint tên CLB-2026, em là chủ trang (Owner).
       Hiện tài khoản em báo "Site is unavailable due to admin setting" khi tạo trang.
[ ] 3. Một nhóm tên HS-CLB-2026 gồm tài khoản các học sinh tham gia.
[ ] 4. Cho phép học sinh mở ứng dụng Power Apps trên điện thoại.

Em cần xong trước ngày [ngày]. Em cảm ơn anh/chị.
```

**Chỉ sang SP02 khi A và B đã đạt.** Nếu thiếu C, SP02 có cách xử lý.
