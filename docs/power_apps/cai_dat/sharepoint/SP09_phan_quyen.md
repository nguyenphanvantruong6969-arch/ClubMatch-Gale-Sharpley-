# SP09 — Ai được xem, ai được sửa

[← SP08](SP08_nap_excel.md) · Tiếp theo: [PA01](../powerapps/PA01_dang_nhap_moi_truong.md)

**Mục tiêu:**
- Giáo viên phụ trách xem được tất cả.
- Học sinh chỉ **xem** bảng câu lạc bộ và bảng học sinh.
- Học sinh chỉ **tạo và sửa phiếu của chính mình**, không xem được phiếu của bạn khác.

**Cần có:** tên nhóm tài khoản học sinh (SP01 phần D), thư điện tử giáo viên phụ trách.

## Phần 1 — Giáo viên phụ trách

1. Mở ĐỊA CHỈ TRANG.
2. Bấm ⚙ → «Site permissions».
3. Bấm «Add members» → «Add members to group» (hoặc «Share site»).
4. Dán thư điện tử giáo viên → chọn tên hiện ra.
5. Chọn quyền «Full control» hoặc «Edit».
6. Bấm «Save» (hoặc «Add»).

👀 Tên giáo viên hiện trong «Site owners» hoặc «Site members».

- [ ] Xong phần 1.

## Phần 2 — Học sinh được xem cả trang

7. Bấm ⚙ → «Site permissions» → «Share site».
8. Dán tên nhóm học sinh, ví dụ:
```
HS-CLB-2026
```
9. Chọn nhóm hiện ra. Chọn quyền «Read» (chỉ xem).
10. Bỏ đánh dấu «Send email».
11. Bấm «Share» (hoặc «Add»).

👀 Nhóm hiện trong «Site visitors».

- [ ] Xong phần 2.

## Phần 3 — Học sinh ghi phiếu vào bảng nguyện vọng

12. Mở bảng `NguyenVong`.
13. Bấm ⚙ → «List settings».
14. Bấm «Permissions for this list».
15. Bấm «Stop Inheriting Permissions» → «OK».
16. Bấm «Grant Permissions».
17. Dán tên nhóm học sinh (như bước 8) → chọn nhóm.
18. Bấm «Show options» → chọn «Contribute» (được thêm và sửa).
19. Bỏ đánh dấu «Send an email invitation» → bấm «Share».
20. Quay lại ⚙ → «List settings» → bấm «Advanced settings».
21. Ở mục «Item-level Permissions»:
    - Phần «Read access»: chọn «Read items that were created by the user» (chỉ xem phiếu của mình).
    - Phần «Create and Edit access»: chọn «Create items and edit items that were created by the user» (chỉ sửa phiếu của mình).
22. Kéo xuống cuối trang, bấm «OK».

- [ ] Xong bảng `NguyenVong`.
- [ ] Làm lại bước 12 đến 22 cho bảng `ChonThi` (nếu có).

⚠️ Không thấy mục «Item-level Permissions»: một số trường ẩn mục này. Hỏi bộ phận tin học. Nếu thiếu bước này, học sinh **có thể xem phiếu của bạn khác**.

⚠️ Ở trang «Permissions for this list» (bước 14), phải còn tên giáo viên phụ trách hoặc nhóm «Owners». Thiếu thì bấm «Grant Permissions» thêm lại.

## Phần 4 — Ghi nhớ: khóa lại khi hết hạn

Sau hạn chót: mở bảng `NguyenVong` → ⚙ → «List settings» → «Permissions for this list» → đánh dấu nhóm học sinh → «Edit User Permissions» → đổi «Contribute» thành «Read» → «OK».

Ứng dụng chỉ khóa ô chọn trên màn hình. Bước này mới thực sự chặn học sinh sửa phiếu.

## Kiểm tra

Kiểm thật bằng tài khoản học sinh ở [PA15](../powerapps/PA15_thu_3_hoc_sinh.md).
