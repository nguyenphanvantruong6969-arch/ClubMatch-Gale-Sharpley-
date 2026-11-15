# PA13 — Chọn màn hình đầu tiên và chạy thử trong Studio

⏱ 10 phút · [← PA12](PA12_man_quan_tri.md) · Tiếp: [PA14](PA14_phat_hanh_chia_se.md)

## Phần 1 — StartScreen
1. Cây: bấm **App** → thuộc tính **StartScreen** → dán:
```
If(LaQuanTri, scrQuanTri, IsBlank(varHS), scrKhongCoTen, scrDangKy)
```
2. **Ctrl+S**.

## Phần 2 — Rà lỗi
3. Góc trên phải bấm biểu tượng **App checker** (ống nghe 🩺, hoặc tam giác cảnh báo).
4. Mục **Formulas**: phải **0 lỗi đỏ**. Cảnh báo vàng (delegation, accessibility) chấp nhận được.
5. Bấm từng lỗi → nó đưa đến chỗ sai → sửa theo ghi chú ⚠️ của tệp tương ứng.

## Phần 3 — Chạy thử bằng chính tài khoản bạn
6. **App → ⋯ → Run OnStart**.
7. Bấm **▶** (Preview) hoặc **F5**.
   👀 Email bạn trong `DSQuanTri` → `scrQuanTri`. Không có → `scrKhongCoTen`.
8. **Esc** thoát.
9. Thử màn đăng ký: thêm tạm email của bạn vào List `HocSinh` (một dòng, `student_id` = `TEST01`), bỏ email khỏi `DSQuanTri` tạm thời, **Run OnStart**, **F5**.
   👀 Thấy `scrDangKy`, chào "TEST01".
10. Chọn 2 CLB → **Nộp**. 👀 Sang `scrXacNhan`, List `NguyenVong` có dòng `TEST01`.
11. **Trả lại** `DSQuanTri`, **xoá** dòng `TEST01` ở cả `HocSinh` và `NguyenVong`.
12. **Ctrl+S**.

- [ ] App checker 0 lỗi đỏ.
- [ ] Đã nộp thử thành công và đã xoá dữ liệu thử.
