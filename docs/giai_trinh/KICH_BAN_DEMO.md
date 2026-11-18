# Kịch bản trình diễn trực tiếp

> **Dữ liệu mô phỏng.** Trình diễn bằng sổ mẫu 120 học sinh do máy sinh; nói rõ điều này với người xem. Thời lượng dự kiến 10–12 phút.
> Các bước 8–10 dùng tính năng giải trình và tiêu chí, có trong bản đã gộp. Ca mẫu có sẵn số liệu để đối chiếu: `CA_MAU.md`.

Chuẩn bị: làm theo `HUONG_DAN_CHAY.md` mục 1; thư mục làm việc trống; tắt thông báo của máy.

1. **Mở phần mềm** (`main.py`). Màn hình: thẻ Xếp, vùng thả tệp trống; thanh **Việc tiếp theo** ở đầu trang đang gợi ý "Nạp sổ". Nói: phần mềm chạy ngoại tuyến, không có mô hình AI (`VAI_TRO_AI.md` mục 1).
2. **Nạp sổ nhập có lỗi** `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx`. Màn hình: bảng năm lỗi kèm sheet, dòng, mã học sinh; "không nạp gì". Chỉ một lỗi, đọc thông báo.
3. **Tạo không gian làm việc bật chế độ huy chương** (chuẩn bị trước buổi trình diễn): màn chọn không gian → **Tạo mới** → ở bước 3 chọn lựa chọn **Huy chương** (hoặc mở không gian rồi chọn nó ở nhóm **Cài đặt**; bấm là lưu ngay, có Hoàn tác). Làm việc này **trước** khi nạp sổ; sổ mẫu là sổ huy chương và không chạy được ở không gian mặc định.
4. **Nạp sổ đúng** `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` (nếu nạp sổ huy chương khi chế độ còn tắt, phần xem trước nói rõ và có nút **Bật chế độ huy chương**). Màn hình: "Sẵn sàng nhập: 8 CLB · 2 buổi · 120 học sinh · 829 nguyện vọng · 194 lượt thi", không lỗi chặn.
5. **Bấm chạy xếp** (hạt giống 42). Màn hình: các bước `backup → validate → stb_lottery → rbda_cascade → write_results → export` đều xong, 120/120 học sinh có chỗ; không bị chặn, không cần "phóng" điểm.
6. **Xem kết quả.** Mở thẻ Kết quả; nói: phần mềm dừng và nói rõ khi hồ sơ sai (đã thấy ở bước 2), còn sổ đúng thì chạy thẳng.
7. **Tra cứu một học sinh nhận nguyện vọng 1 ở một buổi**: gõ `FA001`. Màn hình: Thứ 5 nhận nguyện vọng 1 (`THU_5_4`); Thứ 2 nhận nguyện vọng 2 (`THU_2_4`). Giải thích bằng câu cho học sinh này **đã có sẵn** ở chế độ huy chương (`get_ly_do_ket_qua`): đọc hai câu của buổi Thứ 2.
8. **Tra cứu một học sinh không nhận nguyện vọng 1**: gõ `FA002` (Thứ 2 nhận nguyện vọng 3, Thứ 5 nhận nguyện vọng 4). Màn hình: các câu giải thích nêu mốc điểm chưa đạt và các bạn có huy chương cao hơn được xét trước, bằng chính dữ liệu của em đó. Giải trình nâng cao: thẻ **Kết quả**, ô "Tra cứu một học sinh", gõ mã hoặc tên rồi chọn em đó; màn hình hiện từng nguyện vọng kèm điểm của em, điểm chuẩn, số chỗ đã nhận và câu giải thích.
9. **In phiếu của một học sinh** (nút "In phiếu cho học sinh này" ở ô tra cứu) và **tra cứu tại kiosk bằng mã tra cứu**: bấm "Tạo mã tra cứu" trước, rồi "Chế độ học sinh tra cứu"; học sinh gõ mã học sinh và mã tra cứu in trên phiếu, chỉ thấy phần của mình. Khi đã có tài khoản, thoát chế độ này cần đăng nhập quản trị.
10. **Đổi thử một tiêu chí** trong chế độ chạy thử, **so sánh** với kết quả chính thức (ai đổi chỗ, theo nhóm), rồi **áp dụng** hoặc bỏ: thẻ **Quản lý**, mục "Tiêu chí xếp" (xem tiêu chí bằng lời) và mục "Thử cấu hình" (đổi tiêu chí, bấm "Chạy thử", chọn hai lần chạy, bấm "So sánh", dùng "Dùng tiêu chí của một lần chạy thử" để áp dụng). Nói: chạy thử không ghi đè kết quả chính thức.
11. **Chạy lại cùng hạt giống.** Màn hình: kết quả y hệt (số bốc thăm đã khoá). Mở lịch sử chạy: mỗi lần chạy một dòng, không dòng nào bị sửa.
12. **Bật tài khoản.** Hộp *Tài khoản* → tạo quản trị `quantri` (mật khẩu thử) → đăng xuất → đăng nhập bằng tài khoản giáo viên → thử thao tác dành cho quản trị; màn hình: "Tài khoản này không có quyền làm việc này. Hãy nhờ người quản trị."
13. **Xem nhật ký thao tác** (đăng nhập quản trị → hộp *Tài khoản* → *Nhật ký thao tác*). Màn hình: các dòng mới nhất trước, gồm cả thao tác bị từ chối; xuất CSV. Nói: mật khẩu và nội dung tệp không có trong nhật ký.
14. **Kết thúc.** Nói: toàn bộ số liệu là mô phỏng; nhận xét và kết luận của đề tài do học sinh tự viết.

Nếu hỏng giữa chừng: `docs/giai_trinh/HUONG_DAN_CHAY.md` mục 3 (chế độ trình duyệt dự phòng); khôi phục mật khẩu: mục 8.
