# Kịch bản trình diễn trực tiếp

> **Dữ liệu mô phỏng.** Trình diễn bằng sổ mẫu 120 học sinh do máy sinh; nói rõ điều này với người xem. Thời lượng dự kiến 10–12 phút.
> Bước nào có ghi **(sau tích hợp)** cần bản đã gộp các tính năng giải trình và tiêu chí; trước đó bỏ qua hoặc nói "sắp có".

Chuẩn bị: làm theo `HUONG_DAN_CHAY.md` mục 1; thư mục làm việc trống; tắt thông báo của máy.

1. **Mở phần mềm** (`main.py`). Màn hình: thẻ Xếp, vùng thả tệp trống. Nói: phần mềm chạy ngoại tuyến, không có mô hình AI (`VAI_TRO_AI.md` mục 1).
2. **Nạp sổ nhập có lỗi** `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx`. Màn hình: bảng năm lỗi kèm sheet, dòng, mã học sinh; "không nạp gì". Chỉ một lỗi, đọc thông báo.
3. **Nạp sổ đúng** `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx`. Màn hình: "Sẵn sàng nhập: 8 CLB · 2 buổi · 120 học sinh · 829 nguyện vọng · 194 lượt thi", không lỗi chặn.
4. **Bấm chạy xếp** (hạt giống 42). Màn hình: bị chặn với thông báo điểm quyết tâm chưa hợp lệ (120 học sinh). Nói: phần mềm dừng và nói rõ, không đoán.
5. **Thẻ Quản lý → Điểm quyết tâm → "Phóng cho đủ 100 theo tỉ lệ"**, xác nhận. Màn hình: 120 học sinh được phóng; có bản sao lưu. Chạy xếp lại.
6. **Xem kết quả.** Màn hình: các bước `backup → validate → stb_lottery → rbda_cascade → write_results → export` đều xong. Mở thẻ Kết quả.
7. **Tra cứu một học sinh nhận nguyện vọng 1**: gõ `FA001`. Màn hình: hai buổi, cả hai hạng nguyện vọng 1. Giải thích bằng câu cho học sinh này: **(sau tích hợp)**.
8. **Tra cứu một học sinh không nhận nguyện vọng 1** (chọn trong danh sách, ví dụ `FA002`: buổi Thứ 5 nhận nguyện vọng 4). Giải thích vì sao không nhận nguyện vọng cao hơn, bằng chính dữ liệu của em đó: **(sau tích hợp)**.
9. **In phiếu của một học sinh** và **tra cứu tại kiosk bằng mã tra cứu**: **(sau tích hợp)**.
10. **Đổi thử một tiêu chí** trong chế độ chạy thử, **so sánh** với kết quả chính thức (ai đổi chỗ, theo nhóm), rồi **áp dụng** hoặc bỏ: **(sau tích hợp)**. Nói: chạy thử không ghi đè kết quả chính thức.
11. **Chạy lại cùng hạt giống.** Màn hình: kết quả y hệt (số bốc thăm đã khoá). Mở lịch sử chạy: mỗi lần chạy một dòng, không dòng nào bị sửa.
12. **Bật tài khoản.** Hộp *Tài khoản* → tạo quản trị `quantri` (mật khẩu thử) → đăng xuất → đăng nhập bằng tài khoản giáo viên → thử thao tác dành cho quản trị; màn hình: "Tài khoản này không có quyền làm việc này. Hãy nhờ người quản trị."
13. **Xem nhật ký thao tác** (đăng nhập quản trị → hộp *Tài khoản* → *Nhật ký thao tác*). Màn hình: các dòng mới nhất trước, gồm cả thao tác bị từ chối; xuất CSV. Nói: mật khẩu và nội dung tệp không có trong nhật ký.
14. **Kết thúc.** Nói: toàn bộ số liệu là mô phỏng; nhận xét và kết luận của đề tài do học sinh tự viết.

Nếu hỏng giữa chừng: `docs/giai_trinh/HUONG_DAN_CHAY.md` mục 3 (chế độ trình duyệt dự phòng); khôi phục mật khẩu: mục 8.
