# SP01 — Kiểm tra tài khoản và quyền

⏱ 10 phút · [← Mục lục](../00_MUC_LUC.md) · Tiếp: [SP02](SP02_tao_site.md)

**Cần có trước:** máy tính có Edge hoặc Chrome, email trường (dạng `ten@truong.edu.vn`).

## A. Tài khoản Microsoft 365
1. Mở trình duyệt.
2. Gõ `https://www.office.com` vào thanh địa chỉ, nhấn Enter.
3. Bấm **Sign in**.
4. Gõ email trường, bấm **Next**.
5. Gõ mật khẩu, bấm **Sign in**.
6. Nếu hỏi *Stay signed in?*: bấm **No** (máy dùng chung) hoặc **Yes** (máy riêng).
   👀 Trang chủ Microsoft 365, tên/ảnh của bạn ở góc trên phải.
- [ ] **Đạt A**

## B. Giấy phép Power Apps
7. Mở tab mới, gõ `https://make.powerapps.com`, Enter.
8. Nếu hỏi quốc gia: chọn **Vietnam**, bấm **Get started**.
   👀 Trang **Power Apps**, menu trái có *Home, Create, Learn, Apps…*
   ⚠️ Nếu thấy *You need a license* / *Your organization has not enabled Power Apps* → **thiếu B**.
- [ ] **Đạt B**

## C. Quyền tạo SharePoint site
9. Quay lại tab office.com.
10. Bấm **ô 9 chấm** (góc trên trái) → **SharePoint**. (Không thấy: gõ `SharePoint` vào ô tìm kiếm trên cùng.)
    👀 Trang **SharePoint** với nút **+ Create site** ở trên trái.
11. Bấm **+ Create site** (chỉ để thử, chưa tạo).
    👀 Hộp chọn *Team site / Communication site* → **có quyền C**. Bấm **X** đóng lại.
    ⚠️ Không có nút, hoặc báo *Site is unavailable due to admin setting* → **thiếu C**. Xem SP02 phần "Khi bị chặn".
- [ ] **Đạt C**

## D. Nhóm học sinh (có thể bổ sung sau)
12. Hỏi IT: trường đã có nhóm Microsoft 365 / nhóm bảo mật chứa tài khoản học sinh chưa (ví dụ `HS-Khoi10`)?
13. Ghi tên nhóm vào sổ tay. Chưa có → xin IT tạo nhóm `HS-CLB-2026` (mẫu tin nhắn bên dưới).
- [ ] **Đạt D** (hoặc đã gửi yêu cầu)

## E. Chuẩn bị thông tin (ghi vào sổ tay)
- [ ] Danh sách học sinh: Mã HS, Họ tên, Lớp, email trường, Nhóm ưu tiên.
- [ ] Danh sách CLB: Mã CLB (không dấu, ví dụ `clb_bongro`), Tên, Chỉ tiêu, Suất ưu tiên, Nhóm ưu tiên.
- [ ] Hạn chót nộp (ngày, giờ).
- [ ] Email các giáo viên quản trị.

## Tin nhắn gửi IT (copy, sửa phần `[ ]`)
```
Kính gửi bộ phận CNTT trường [tên trường],
Em là [họ tên], [chức vụ]. Em cần dựng app đăng ký câu lạc bộ bằng Power Apps,
lưu dữ liệu ở SharePoint (chỉ dùng tính năng có sẵn trong Microsoft 365 Education).
Nhờ anh/chị cấp cho tài khoản [email] các mục còn thiếu:
[ ] Giấy phép Power Apps (Power Apps for Microsoft 365)
[ ] Một SharePoint site tên CLB-2026, em là Owner (tài khoản em hiện báo
    "Site is unavailable due to admin setting")
[ ] Nhóm Microsoft 365 / bảo mật HS-CLB-2026 chứa tài khoản học sinh tham gia
[ ] Cho phép học sinh mở app Power Apps trên điện thoại
Hạn cần: [ngày]. Em cảm ơn ạ.
```

**Chỉ sang SP02 khi A và B đạt.** Nếu C thiếu, SP02 có cách xử lý.
