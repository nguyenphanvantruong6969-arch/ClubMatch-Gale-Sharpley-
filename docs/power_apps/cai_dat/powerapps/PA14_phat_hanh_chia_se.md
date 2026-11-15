# PA14 — Phát hành, gửi đường dẫn, mã QR

[← PA13](PA13_man_dau_tien_va_chay_thu.md) · Tiếp theo: [PA15](PA15_thu_3_hoc_sinh.md)

**Cần có:** NHÓM HỌC SINH (SP01 phần D), thư điện tử các giáo viên phụ trách.

## Phần 1 — Phát hành

Phát hành là đưa bản bạn vừa làm tới người dùng. Chưa phát hành thì chỉ mình bạn thấy.

1. Ở màn hình thiết kế, bấm `Ctrl` + `S`.
2. Ở đầu bên phải thanh lệnh có một hàng biểu tượng nhỏ. Đưa chuột vào từng biểu tượng sẽ hiện tên của nó. Bấm biểu tượng có tên «Publish» (nằm ngay bên phải biểu tượng lưu hình đĩa mềm).

👀 Hiện hộp «Publish».

3. Chỉ khi hộp có ô ghi chú phiên bản: bấm vào ô đó, dán:
```
Ban dau
```
4. Bấm nút «Publish this version».

👀 Hộp đóng lại; thoáng hiện thông báo màu xanh báo đã phát hành.

> **Mỗi lần sửa ứng dụng đều phải làm lại bước 1 đến 4.** Nếu không, học sinh vẫn thấy bản cũ.

## Phần 2 — Chia sẻ cho học sinh

5. Cũng ở hàng biểu tượng đó, bấm biểu tượng có tên «Share» (đưa chuột vào để thấy tên).

👀 Mở bảng chia sẻ, có ô nhập tên ở phía trên.

6. Bấm vào ô nhập tên, dán NHÓM HỌC SINH, ví dụ:
```
HS-CLB-2026
```
7. Bấm vào tên nhóm hiện ra ngay bên dưới ô.

👀 Tên nhóm được thêm vào danh sách người dùng trong bảng.

8. Nhìn dòng của nhóm học sinh:
   - Có ô đánh dấu «Co-owner»: **để trống**, không đánh dấu.
   - Có ô thả xuống quyền: chọn «User».

## Phần 3 — Chia sẻ cho giáo viên phụ trách

Làm lại bước 9 đến 11 cho từng giáo viên.

9. Bấm vào ô nhập tên, dán thư điện tử của giáo viên.
10. Bấm vào tên giáo viên hiện ra ngay bên dưới.
11. Ở dòng của giáo viên đó: đánh dấu ô «Co-owner» (hoặc chọn «Co-owner» trong ô thả xuống quyền). Giáo viên này sẽ sửa được ứng dụng.
12. Tìm ô đánh dấu «Send an email invitation to new users» ở cuối bảng, bấm để **bỏ** dấu tích.
13. Bấm nút «Share» ở cuối bảng.

👀 Thông báo đã chia sẻ thành công. Phần nói về quyền dữ liệu («Data permissions») trong bảng: không cần đụng tới, đã làm ở SP09.

14. Đóng bảng chia sẻ (dấu X).

⚠️ Ở bước 7, dán tên nhóm mà không hiện gì: nhóm chưa có, hoặc là loại nhóm chỉ để gửi thư. Hỏi bộ phận tin học (câu hỏi mẫu ở [SP09](../sharepoint/SP09_phan_quyen.md), Phần 2). Trong lúc chờ, để thử PA15 bạn dán thư điện tử của từng tài khoản thử thay cho tên nhóm.

## Phần 4 — Lấy đường dẫn

15. Mở thẻ trình duyệt mới, vào make.powerapps.com (nhìn đúng KHU LÀM VIỆC).
16. Ở cột bên trái, bấm «Apps».
17. Đưa chuột vào dòng `DangKyCLB`, bấm «⋯» hiện ra cạnh tên, bấm «Details».

👀 Trang thông tin của ứng dụng, có dòng «Web link» kèm một đường dẫn dạng `https://apps.powerapps.com/play/e/.../a/...`

18. Bôi đen cả đường dẫn ở dòng «Web link», bấm `Ctrl` + `C`.
19. Dán vào sổ tay, đặt tên **ĐƯỜNG DẪN ỨNG DỤNG**.

## Phần 5 — Kiểm trang mở đầu

20. Mở thẻ trình duyệt mới, dán ĐƯỜNG DẪN ỨNG DỤNG vào thanh địa chỉ, bấm `Enter`.
21. Chỉ khi hiện hộp xin quyền dùng SharePoint: bấm «Allow».

👀 Vì bạn là giáo viên phụ trách (có trong `DSQuanTri`): ứng dụng mở thẳng **trang theo dõi**, có dòng "… / … học sinh đã nộp".

⚠️ Mở ra trang báo "chưa có trong danh sách học sinh": thư điện tử của bạn trong `DSQuanTri` ([PA04](PA04_cong_thuc_app.md), bước 6) gõ sai hoặc có chữ hoa. Sửa, rồi phát hành lại (bước 1 đến 4).

## Phần 6 — Mã QR

22. Mở trang tạo mã QR mà trường cho phép dùng (chưa biết trang nào: hỏi bộ phận tin học).
23. Dán ĐƯỜNG DẪN ỨNG DỤNG vào ô nhập của trang đó. **Chỉ dán đường dẫn**, không nhập bất kỳ thông tin nào của học sinh.
24. Tải ảnh mã QR về máy.
25. Dùng điện thoại quét thử mã vừa tải.

👀 Điện thoại mở đúng ứng dụng (sau khi đăng nhập thư điện tử của trường).

26. In mã QR kèm dòng chữ sau:
```
Quét mã → đăng nhập bằng email trường → chọn câu lạc bộ theo thứ tự em thích.
```

## Học sinh mở ứng dụng thế nào

- **Điện thoại:** quét mã QR → trang mở trong trình duyệt → đăng nhập thư điện tử của trường → bấm «Allow» nếu được hỏi.
- **Điện thoại, cách khác:** cài ứng dụng «Power Apps» từ App Store hoặc Google Play → đăng nhập thư điện tử của trường → bấm `DangKyCLB` trong danh sách.
- **Máy tính:** mở ĐƯỜNG DẪN ỨNG DỤNG bằng Edge hoặc Chrome.

- [ ] Đã phát hành.
- [ ] Đã chia sẻ cho nhóm học sinh và giáo viên phụ trách.
- [ ] Có ĐƯỜNG DẪN ỨNG DỤNG và mã QR; trang mở đầu đúng.
