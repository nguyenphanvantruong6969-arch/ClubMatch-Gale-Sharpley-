# SP09 — Phân quyền

⏱ 20 phút · [← SP08](SP08_nap_excel.md) · Tiếp: [PA01](../powerapps/PA01_dang_nhap_moi_truong.md)

**Mục tiêu:** giáo viên xem hết; học sinh **chỉ đọc** `CLB`, `HocSinh` và **chỉ tạo/sửa phiếu của chính mình** ở `NguyenVong`, `ChonThi`.

**Cần có trước:** tên nhóm học sinh (SP01 phần D), email giáo viên quản trị.

## Phần 1 — Giáo viên quản trị
1. Mở "ĐỊA CHỈ SITE".
2. **⚙ → Site permissions**.
3. Bấm **Add members** → **Add members to group** (hoặc **Share site**).
4. Gõ email giáo viên → chọn tên.
5. Quyền: **Full control** hoặc **Edit**.
6. Bấm **Save** / **Add**.
   👀 Tên giáo viên trong *Site owners* hoặc *Site members*.
- [ ] Xong phần 1.

## Phần 2 — Học sinh đọc toàn site
7. **⚙ → Site permissions → Share site**.
8. Gõ tên nhóm học sinh (ví dụ `HS-CLB-2026`) → chọn.
9. Quyền: **Read**.
10. Bỏ tick **Send email**.
11. Bấm **Share** / **Add**.
    👀 Nhóm nằm trong *Site visitors*.
- [ ] Xong phần 2.

## Phần 3 — Học sinh ghi vào `NguyenVong` (làm lại y hệt cho `ChonThi`)
12. Mở List `NguyenVong`.
13. **⚙ → List settings**.
14. Bấm **Permissions for this list**.
15. Bấm **Stop Inheriting Permissions** → **OK**.
16. Bấm **Grant Permissions**.
17. Gõ tên nhóm học sinh → chọn.
18. Bấm **Show options** → chọn **Contribute**.
19. Bỏ tick **Send an email invitation** → **Share**.
20. Quay lại **⚙ → List settings** → **Advanced settings**.
21. Mục **Item-level Permissions**:
    - *Read access*: chọn **Read items that were created by the user**.
    - *Create and Edit access*: chọn **Create items and edit items that were created by the user**.
22. Kéo xuống cuối, bấm **OK**.
- [ ] Xong `NguyenVong`.
- [ ] Làm lại 12–22 cho `ChonThi` (nếu có).

⚠️ Không thấy *Item-level Permissions*: một số tenant ẩn mục này → hỏi IT. Không có nó, học sinh **có thể xem phiếu của bạn** qua SharePoint.
⚠️ Giáo viên quản trị vẫn thấy hết (quyền Full control/Edit ở site được thừa hưởng trước khi tách). Kiểm: mục **Permissions for this list** phải còn tên giáo viên / nhóm Owners. Thiếu → **Grant Permissions** thêm lại.

## Phần 4 — Ghi nhớ khi hết hạn
- Sau hạn chót: List `NguyenVong` → **Permissions for this list** → chọn nhóm học sinh → **Edit User Permissions** → đổi **Contribute** thành **Read**. (App chỉ khoá giao diện; bước này mới khoá thật.)

## Kiểm tra xong
- Kiểm thật bằng tài khoản học sinh ở [PA15](../powerapps/PA15_thu_3_hoc_sinh.md).
