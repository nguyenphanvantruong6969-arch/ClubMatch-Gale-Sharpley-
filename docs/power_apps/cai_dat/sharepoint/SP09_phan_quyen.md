# SP09 — Ai được xem, ai được sửa

[← SP08](SP08_nap_excel.md) · Tiếp theo: [PA01](../powerapps/PA01_dang_nhap_moi_truong.md)

**Mục tiêu:**
- Giáo viên phụ trách xem và sửa được tất cả.
- Học sinh chỉ **xem** bảng câu lạc bộ và bảng học sinh.
- Học sinh chỉ **tạo và sửa phiếu của chính mình**, không xem được phiếu của bạn khác.

**Cần có:** NHÓM HỌC SINH (SP01 phần D), thư điện tử giáo viên phụ trách.

⚠️ Nhóm học sinh chưa được tạo xong: vẫn làm được Phần 1. Phần 2 và 3 làm sau khi có nhóm. Để thử trước, ở bước 9 và 20 dán thư điện tử của từng tài khoản thử thay cho tên nhóm.

## Phần 1 — Giáo viên phụ trách

Làm lại cả phần này cho từng giáo viên.

1. Mở ĐỊA CHỈ TRANG.
2. Bấm ⚙ ở góc trên bên phải → bấm «Site permissions».

👀 Bên phải mở khung «Permissions», có 3 nhóm «Site owners», «Site members», «Site visitors».

3. Bấm nút «Add members» ở đầu khung, rồi bấm «Share site only». (Khung không có «Add members» mà có nút «Share site»: bấm «Share site».)
4. Bấm vào ô nhập tên, dán thư điện tử giáo viên, bấm vào tên giáo viên hiện ra ngay bên dưới.
5. Bấm ô thả xuống nằm bên phải tên vừa thêm, chọn «Full control».
6. Bấm vào ô đánh dấu «Send email» để bỏ dấu tích.
7. Bấm «Add».

👀 Bấm vào mũi tên cạnh chữ «Site owners» trong khung: có tên giáo viên vừa thêm.

- [ ] Xong phần 1.

## Phần 2 — Học sinh được xem cả trang

8. Bấm ⚙ → «Site permissions» → «Add members» → «Share site only» (hoặc «Share site», như bước 3).
9. Bấm vào ô nhập tên, dán NHÓM HỌC SINH, ví dụ:
```
HS-CLB-2026
```
10. Bấm vào tên nhóm hiện ra ngay bên dưới.
11. Bấm ô thả xuống bên phải tên nhóm, chọn «Read» (chỉ xem).
12. Bấm vào ô «Send email» để bỏ dấu tích.
13. Bấm «Add».

👀 Bấm vào mũi tên cạnh chữ «Site visitors»: có tên nhóm học sinh.

⚠️ Dán tên nhóm mà không hiện gì bên dưới: nhóm chưa được tạo, hoặc mới tạo nên chưa kịp hiện, hoặc là loại nhóm chỉ để gửi thư. Hỏi bộ phận tin học: "Nhóm HS-CLB-2026 đã là nhóm bảo mật (security group) chưa?"

- [ ] Xong phần 2.

## Phần 3 — Học sinh ghi phiếu vào bảng nguyện vọng

14. Bấm ⚙ → «Site contents» → bấm tên bảng `NguyenVong`.
15. Bấm ⚙ → «List settings».
16. Bấm dòng chữ «Permissions for this list» (ở cột giữa, dưới chữ «Permissions and Management»).
17. Trên dải lệnh phía trên, bấm «Stop Inheriting Permissions».
18. Hộp hỏi lại hiện ra: bấm «OK».

👀 Dải lệnh đổi, có thêm nút «Grant Permissions».

19. Bấm «Grant Permissions».
20. Bấm vào ô nhập tên, dán NHÓM HỌC SINH (như bước 9), bấm vào tên nhóm hiện ra bên dưới.
21. Bấm dòng chữ «Show options».
22. Bấm vào ô «Send an email invitation» để bỏ dấu tích.
23. Bấm ô thả xuống «Select a permission level», chọn «Contribute» (được thêm và sửa).
24. Bấm «Share».

👀 Trong danh sách trên trang, dòng của nhóm học sinh ghi «Contribute» ở cột «Permission Levels». Tên giáo viên phụ trách (hoặc nhóm có chữ «Owners») vẫn còn trong danh sách với «Full Control».

⚠️ Không còn dòng nào ghi «Full Control»: bấm «Grant Permissions», dán thư điện tử giáo viên, «Show options», chọn «Full Control», «Share».

25. Bấm chữ «Settings» ở dòng chữ nhỏ phía trên cùng trang (dạng `NguyenVong > Settings > Permissions`) để quay lại trang cài đặt của bảng. Không thấy dòng chữ đó: bấm nút quay lại của trình duyệt cho đến khi về trang «Settings».
26. Bấm dòng chữ «Advanced settings» (ở cột đầu, dưới chữ «General Settings»).
27. Tìm mục «Item-level Permissions». Ở phần «Read access», bấm chọn «Read items that were created by the user» (chỉ xem phiếu của mình).
28. Cũng trong mục đó, ở phần «Create and Edit access», bấm chọn «Create items and edit items that were created by the user» (chỉ sửa phiếu của mình).
29. Kéo xuống cuối trang, bấm «OK».

👀 Quay về trang «Settings», không báo lỗi.

⚠️ Không thấy mục «Item-level Permissions»: chụp màn hình, hỏi bộ phận tin học. Thiếu bước 27 và 28 thì học sinh **xem được phiếu của bạn khác**; đừng mở cho cả trường khi chưa xong.

- [ ] Xong bảng `NguyenVong`.
- [ ] Có bảng `ChonThi`: làm lại bước 14 đến 29, ở bước 14 bấm tên bảng `ChonThi`.

## Phần 4 — Khoá lại khi hết hạn (làm sau hạn chót, chưa làm bây giờ)

Ứng dụng chỉ khoá ô chọn trên màn hình. Phần này mới thực sự chặn học sinh sửa phiếu.

1. Mở bảng `NguyenVong` → ⚙ → «List settings» → «Permissions for this list».
2. Bấm vào ô đánh dấu ở đầu dòng của nhóm học sinh (dòng ghi «Contribute»).
3. Trên dải lệnh, bấm «Edit User Permissions».
4. Bấm bỏ dấu tích ở «Contribute».
5. Bấm đánh dấu «Read».
6. Bấm «OK».

👀 Dòng của nhóm học sinh ghi «Read».

7. Có bảng `ChonThi`: làm lại bước 1 đến 6 cho bảng `ChonThi`.

## Kiểm tra

Kiểm thật bằng tài khoản học sinh ở [PA15](../powerapps/PA15_thu_3_hoc_sinh.md), dòng 6.

## Điều cần biết

- Giáo viên có quyền «Full control» xem được mọi phiếu. Học sinh chỉ thấy phiếu của mình.
- Học sinh có quyền «Read» cả trang, nên **đọc được bảng `HocSinh`** (mã, họ tên, lớp, thư điện tử của các bạn) nếu biết mở thẳng bảng. Ứng dụng cần quyền này để nhận ra học sinh. Vì vậy đừng thêm vào bảng `HocSinh` thông tin nào không nên cho học sinh khác thấy.
