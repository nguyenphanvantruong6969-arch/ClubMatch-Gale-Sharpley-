# SP08 — Nạp danh sách học sinh và CLB từ Excel

⏱ 20 phút · [← SP07](SP07_list_ChonThi.md) · Tiếp: [SP09](SP09_phan_quyen.md)

**Cần có trước:** SP04, SP05 xong.

## Bước 1 — Chuẩn bị tệp Excel học sinh
1. Mở Excel, tạo tệp mới.
2. Dòng 1 gõ **đúng** 5 tiêu đề, mỗi ô một tiêu đề: `student_id` `name` `class_id` `email` `reserve_group`.
3. Từ dòng 2: dán dữ liệu. Ví dụ (giả):

| student_id | name | class_id | email | reserve_group |
|---|---|---|---|---|
| HS001 | Nguyễn Văn An | 10A1 | hs001@truong.edu.vn | |
| HS002 | Trần Thị Bình | 10A1 | hs002@truong.edu.vn | chinh_sach |

4. Chọn cột `email` → ô trống bên cạnh gõ `=LOWER(TRIM(D2))`, kéo xuống, copy → **Paste Values** đè lên cột D. (Đưa email về chữ thường, bỏ khoảng trắng.)
5. Làm tương tự `=TRIM(A2)` cho cột `student_id`.
6. **Data → Remove Duplicates** trên cột `student_id` để chắc không trùng.
7. Lưu tệp tên `HocSinh.xlsx`.

## Bước 2 — Chuẩn bị tệp Excel CLB
8. Tệp mới, dòng 1: `club_id` `name` `capacity` `reserve_capacity` `reserve_group` `mo_ta` `co_thi`.
9. Dán dữ liệu. Ví dụ (giả):

| club_id | name | capacity | reserve_capacity | reserve_group | mo_ta | co_thi |
|---|---|---|---|---|---|---|
| clb_bongro | CLB Bóng rổ | 20 | 0 | | Tập thứ 2 | No |
| clb_tienganh | CLB Tiếng Anh | 25 | 5 | chinh_sach | Giao tiếp | Yes |

10. Lưu tên `CLB.xlsx`.

## Bước 3 — Dán vào List (cách nhanh)
11. Mở List `HocSinh` trên site.
12. Bấm **Edit in grid view** (thanh trên). 👀 Bảng thành dạng ô như Excel.
13. Trong Excel: chọn dữ liệu **từ dòng 2** (không lấy tiêu đề), **tối đa 200 dòng một lần**, **Ctrl+C**.
14. Trong lưới SharePoint: bấm ô đầu tiên cột `student_id` của dòng trống cuối cùng, **Ctrl+V**.
15. Chờ đến khi hết biểu tượng đang lưu.
16. Lặp 13–15 đến hết danh sách.
17. Bấm **Exit grid view**.
18. Làm lại 11–17 cho List `CLB` với tệp `CLB.xlsx`. Cột `co_thi`: gõ `Yes`/`No` hoặc tick trong lưới.

⚠️ Cột trong Excel phải **đúng thứ tự** cột trong List, nếu không dữ liệu lệch cột.
⚠️ Dán báo lỗi một số dòng → thường do trùng `student_id`/`email` (Unique). Sửa trong Excel, dán lại dòng đó.

## Kiểm tra xong
- [ ] **⚙ → Site contents**: cột *Items* của `HocSinh` = số học sinh; `CLB` = số CLB.
- [ ] Mở ngẫu nhiên 3 dòng: email chữ thường, không lệch cột.
