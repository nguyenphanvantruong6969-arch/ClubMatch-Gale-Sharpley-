# SP01 — Kiểm tra tài khoản và quyền

[← Mục lục](../00_MUC_LUC.md) · Tiếp theo: [SP02](SP02_tao_site.md)

**Cần có:** máy tính có trình duyệt Edge hoặc Chrome, địa chỉ thư điện tử của trường (dạng `ten@truong.edu.vn`) và mật khẩu.

## A. Tài khoản của trường

1. Mở trình duyệt Edge hoặc Chrome.
2. Bấm vào thanh địa chỉ (ô dài nằm trên cùng cửa sổ), dán:
```
https://www.office.com
```
3. Bấm phím `Enter`.
4. Bấm nút «Sign in» ở giữa trang. (Nếu trang mở ra đã có tên bạn ở góc trên bên phải thì bạn đã đăng nhập sẵn: nhảy tới dòng 👀.)
5. Gõ thư điện tử của trường vào ô đang nhấp nháy.
6. Bấm «Next».
7. Gõ mật khẩu.
8. Bấm «Sign in».
9. Trang hỏi «Stay signed in?»: máy dùng chung bấm «No», máy riêng bấm «Yes».

👀 Trang chủ Microsoft 365. Góc trên bên phải có hình tròn mang ảnh hoặc chữ cái đầu tên bạn.

⚠️ Báo sai mật khẩu hoặc tài khoản bị khoá: liên hệ bộ phận tin học của trường. Không làm tiếp được khi chưa đăng nhập.

- [ ] **Đạt A**

## B. Được dùng Power Apps

10. Bấm `Ctrl` + `T` để mở thẻ mới.
11. Bấm vào thanh địa chỉ, dán:
```
https://make.powerapps.com
```
12. Bấm phím `Enter`.
13. Chỉ khi hiện bảng hỏi quốc gia: bấm ô thả xuống, chọn «Vietnam», rồi bấm «Get started».

👀 Trang Power Apps. Cột bên trái có các chữ «Home», «Create», «Apps».

⚠️ Hiện «You need a license» hoặc «Your organization has not enabled Power Apps»: bạn **chưa được cấp quyền**. Đánh dấu mục 1 trong tin nhắn ở cuối tệp này, gửi cho bộ phận tin học, rồi làm tiếp phần C.

- [ ] **Đạt B**

## C. Được tạo trang SharePoint

14. Bấm vào thẻ office.com đã mở ở phần A.
15. Bấm hình **9 chấm vuông** ở góc trên cùng bên trái trang.

👀 Mở ra một bảng liệt kê các ứng dụng.

16. Bấm «SharePoint» trong bảng đó. Không thấy chữ «SharePoint»: bấm «More apps» (bản khác ghi «All apps» hoặc «Explore all your apps») ở cuối bảng, rồi bấm «SharePoint» trong danh sách đầy đủ.

👀 Trang SharePoint mở ra (có thể ở thẻ mới).

17. Tìm nút «+ Create site» ở phía trên bên trái trang, ngay dưới thanh màu trên cùng. Bấm vào. (Đây chỉ là bấm thử, chưa tạo gì.)

👀 Hiện bảng cho chọn «Team site» và «Communication site» → **bạn có quyền**.

18. Bấm dấu X ở góc trên bên phải bảng đó để đóng.

⚠️ Không có nút «+ Create site», hoặc bấm vào thì báo «Site is unavailable due to admin setting» → **bạn chưa có quyền tạo trang**. Không sao: đánh dấu "chưa đạt C" và làm tiếp. [SP02](SP02_tao_site.md) có phần "Khi bị chặn".

- [ ] **Đạt C** (hoặc ghi: chưa đạt C)

## D. Nhóm tài khoản học sinh (bổ sung sau cũng được)

Nhóm là một cái tên gom nhiều tài khoản học sinh lại, để về sau cấp quyền một lần cho tất cả.

19. Hỏi bộ phận tin học câu này: "Trường đã có nhóm gom tài khoản học sinh chưa, tên nhóm là gì?"
20. Đã có: ghi tên nhóm vào sổ tay, đặt tên là **NHÓM HỌC SINH**.
21. Chưa có: đánh dấu mục 3 trong tin nhắn ở cuối tệp này (xin tạo nhóm tên `HS-CLB-2026`), và ghi `HS-CLB-2026` vào sổ tay làm **NHÓM HỌC SINH**.

- [ ] **Đạt D** (hoặc đã gửi đề nghị)

## E. Chuẩn bị sẵn

- [ ] Danh sách học sinh, mỗi em có: mã học sinh, họ tên, lớp, thư điện tử của trường, nhóm ưu tiên (em nào không thuộc nhóm ưu tiên thì để trống).
- [ ] Danh sách câu lạc bộ, mỗi câu lạc bộ có: mã (viết liền, không dấu, ví dụ `clb_bongro`), tên, số chỗ, số chỗ ưu tiên, nhóm ưu tiên (không có thì để trống), có thi tuyển hay không.
- [ ] Hạn chót nộp (ngày, giờ, phút).
- [ ] Thư điện tử của các giáo viên phụ trách.

## Tin nhắn gửi bộ phận tin học

1. Sao chép cả ô xám dưới đây, dán vào thư điện tử hoặc tin nhắn.
2. Sửa các chỗ trong ngoặc vuông `[ ]` thành thông tin thật.
3. Xoá những dòng việc bạn **đã đạt** (ví dụ đã đạt B thì xoá dòng 1).

```
Kính gửi bộ phận tin học trường [tên trường],

Em là [họ tên], [chức vụ]. Em cần làm ứng dụng đăng ký câu lạc bộ cho học sinh
bằng Power Apps, lưu dữ liệu trên SharePoint (chỉ dùng phần có sẵn trong gói
Microsoft 365 Education, không mua thêm). Nhờ anh/chị cấp cho tài khoản
[thư điện tử của em] những mục còn thiếu dưới đây:

1. Quyền dùng Power Apps (gói "Power Apps for Microsoft 365").
2. Một trang SharePoint tên CLB-2026, em là chủ trang (Owner).
   Hiện tài khoản em báo "Site is unavailable due to admin setting" khi tạo trang.
3. Một nhóm bảo mật (security group) tên HS-CLB-2026 gồm tài khoản các học sinh tham gia.
4. Cho phép học sinh mở ứng dụng Power Apps trên điện thoại.

Em cần xong trước ngày [ngày]. Em cảm ơn anh/chị.
```

**Chỉ sang SP02 khi A và B đã đạt.** Chưa đạt C thì vẫn sang SP02, làm phần "Khi bị chặn".
