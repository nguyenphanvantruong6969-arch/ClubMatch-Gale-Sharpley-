# PA13 — Chọn trang mở đầu, chạy thử

[← PA12](PA12_man_quan_tri.md) · Tiếp theo: [PA14](PA14_phat_hanh_chia_se.md)

## Phần 1 — Trang mở đầu

Khi mở ứng dụng: giáo viên phụ trách vào trang theo dõi; người không có trong bảng học sinh vào trang báo; học sinh vào trang đăng ký.

1. Cây bên trái: bấm «App».
2. Ô thả xuống nhỏ của thanh công thức: chọn «StartScreen».
3. Bấm vào ô dài, `Ctrl` + `A`, rồi dán:
```
If(LaQuanTri, scrQuanTri, IsBlank(LookUp(HocSinh, email = Lower(User().Email))), scrKhongCoTen, scrDangKy)
```

👀 Không có gạch chân đỏ.

4. Bấm `Ctrl` + `S`.

⚠️ Ở PA04 bạn đã dùng **đoạn thay thế** (không có mục «Formulas»): dán đoạn dưới đây thay cho đoạn ở bước 3, rồi sửa các thư điện tử giáo viên trong đó cho giống hệt danh sách đã điền ở PA04:
```
If(Lower(User().Email) in ["gv.a@truong.edu.vn", "gv.b@truong.edu.vn"], scrQuanTri, IsBlank(LookUp(HocSinh, email = Lower(User().Email))), scrKhongCoTen, scrDangKy)
```

> Trang mở đầu chỉ có tác dụng khi mở ứng dụng **đã phát hành**. Trong màn hình thiết kế, nút ▶ luôn chạy trang đang được chọn ở cây bên trái. Vì vậy trang mở đầu sẽ được kiểm ở [PA14](PA14_phat_hanh_chia_se.md), Phần 5.

## Phần 2 — Rà lỗi

5. Ở đầu bên phải thanh lệnh, bấm biểu tượng **hình ống nghe bác sĩ** (đưa chuột vào sẽ hiện tên «App checker»).

👀 Bên phải mở khung «App checker», có các mục «Formulas», «Runtime», «Accessibility», «Performance», «Data source», mỗi mục kèm một con số.

6. Nhìn con số cạnh «Formulas».

👀 Số đó là **0**. → Nhảy tới bước 9.

7. Số khác 0: bấm vào chữ «Formulas», rồi bấm vào dòng lỗi đầu tiên. Màn hình tự đưa bạn tới đúng thứ bị lỗi và đúng mục cài đặt bị lỗi.
8. Mở tệp hướng dẫn đã tạo ra thứ đó (tên thứ đó có trong tệp nào thì mở tệp ấy), dán lại đúng ô xám của mục đó. Xem thêm các dòng ⚠️ ở đầu [PA04](PA04_cong_thuc_app.md). Lặp lại bước 6.
9. Bấm dấu X ở góc trên bên phải khung «App checker» để đóng.

Các mục «Accessibility» và «Performance» có số khác 0 là bình thường, bỏ qua.

## Phần 3 — Thử trang đăng ký bằng chính tài khoản của bạn

Bạn sẽ tạm thêm chính mình vào bảng học sinh với mã `TEST01`, nộp thử, rồi xoá đi.

10. Mở thẻ trình duyệt mới, mở ĐỊA CHỈ TRANG → ⚙ → «Site contents» → bấm bảng `HocSinh`.
11. Bấm «+ New» (bản khác ghi «+ Add new item») ở thanh lệnh phía trên bảng.
12. Trong khung bên phải, bấm ô `student_id`, dán:
```
TEST01
```
13. Bấm ô `name`, dán:
```
Thu Nghiem
```
14. Bấm ô `email`, gõ thư điện tử của chính bạn, **toàn chữ thường**.
15. Bấm «Save».
16. Quay lại thẻ Power Apps. Cây bên trái: đưa chuột vào «App» → «⋯» → «Run OnStart».
17. Cây bên trái: bấm `scrDangKy`.
18. Bấm nút **▶** ở đầu bên phải thanh lệnh (hoặc phím `F5`).

👀 Trang đăng ký hiện "Chào Thu Nghiem (TEST01 – )".

19. Bấm ô "Nguyện vọng 1", chọn một câu lạc bộ.
20. Bấm ô "Nguyện vọng 2", chọn một câu lạc bộ **khác**.

👀 Dòng chữ đỏ biến mất, nút "Nộp nguyện vọng" sáng lên.

21. Bấm nút "Nộp nguyện vọng".

👀 Chuyển sang trang "Đã lưu nguyện vọng", liệt kê đúng 2 câu lạc bộ vừa chọn theo thứ tự 1, 2.

22. Bấm `Esc` để thoát chạy thử.
23. Sang thẻ SharePoint: ⚙ → «Site contents» → bấm bảng `NguyenVong`.

👀 Có đúng một dòng `TEST01`, cột `pref_1` và `pref_2` là **mã** của 2 câu lạc bộ đã chọn, `so_lan_nop` là 1.

**Trả lại như cũ:**

24. Ở bảng `NguyenVong`: bấm vào vòng tròn ở đầu dòng `TEST01` để đánh dấu, bấm «Delete» trên thanh lệnh, bấm «Delete» lần nữa để xác nhận.
25. Mở bảng `HocSinh`, tìm dòng `TEST01`, xoá y như bước 24.
26. Quay lại thẻ Power Apps, bấm `Ctrl` + `S`.

⚠️ Bước 18 hiện "Chào ( – )": chưa «Run OnStart», hoặc thư điện tử ở bước 14 gõ sai hay có chữ hoa. Sửa trên SharePoint rồi làm lại từ bước 16.
⚠️ Bước 21 báo "Lưu thất bại": xem dòng lỗi đỏ ở đầu trang. Lỗi nhắc đến quyền: tài khoản của bạn chưa có quyền ghi vào bảng `NguyenVong` ([SP09](../sharepoint/SP09_phan_quyen.md), Phần 1).

- [ ] «Formulas» trong «App checker» là 0.
- [ ] Nộp thử thành công, đã xoá `TEST01` ở cả hai bảng.
