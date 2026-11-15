# PA13 — Chọn trang mở đầu, chạy thử

[← PA12](PA12_man_quan_tri.md) · Tiếp theo: [PA14](PA14_phat_hanh_chia_se.md)

## Phần 1 — Trang mở đầu

Giáo viên phụ trách vào trang theo dõi; người không có tên vào trang báo; học sinh vào trang đăng ký.

1. Cây bên trái: «App». Ô thả xuống: «StartScreen». Dán:
```
If(LaQuanTri, scrQuanTri, IsBlank(varHS), scrKhongCoTen, scrDangKy)
```
2. Bấm `Ctrl` + `S`.

## Phần 2 — Rà lỗi

3. Góc trên phải bấm biểu tượng **kiểm tra lỗi** (hình ống nghe, hoặc hình tam giác; tên «App checker»).
4. Phần «Formulas» phải là **0 lỗi đỏ**. Nhắc nhở màu vàng thì chấp nhận được.
5. Còn lỗi đỏ: bấm vào lỗi, nó đưa bạn tới đúng chỗ. Sửa theo các dòng ⚠️ trong tệp tương ứng.

## Phần 3 — Chạy thử bằng chính tài khoản của bạn

6. Cây bên trái: «⋯» cạnh «App» → «Run OnStart».
7. Bấm **▶** (hoặc phím `F5`).

👀 Thư điện tử của bạn có trong danh sách giáo viên → trang theo dõi. Không có → trang báo "chưa có trong danh sách".

8. Bấm `Esc` để thoát.
9. **Thử trang đăng ký:**
   - Thêm tạm một dòng vào bảng `HocSinh` trên SharePoint: mã `TEST01`, thư điện tử của bạn.
   - Trong `DSQuanTri` (PA04) tạm xoá thư điện tử của bạn.
   - «Run OnStart» → `F5`.

👀 Hiện trang đăng ký, chào "TEST01".

10. Chọn 2 câu lạc bộ → bấm Nộp.

👀 Sang trang xác nhận. Trên SharePoint, bảng `NguyenVong` có một dòng `TEST01`.

11. **Trả lại như cũ:** thêm lại thư điện tử của bạn vào `DSQuanTri`; xoá dòng `TEST01` ở cả `HocSinh` và `NguyenVong`.
12. Bấm `Ctrl` + `S`.

- [ ] Kiểm tra lỗi: 0 lỗi đỏ.
- [ ] Nộp thử thành công, đã xoá dữ liệu thử.
