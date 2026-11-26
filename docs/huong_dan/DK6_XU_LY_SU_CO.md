# Cổng Đăng ký CLB — xử lý sự cố

## 1. Học sinh hoặc giáo viên quên PIN
Quản trị → thẻ **Danh sách** → mở «Học sinh» (theo khối) hoặc «Giáo viên» → **Đặt lại PIN** cạnh tên → PIN mới hiện một lần ở
thông báo (ghi lại ngay, màn sẽ không hiện lại). PIN cũ hết hiệu lực.
Nhập sai PIN 5 lần liên tiếp thì tài khoản bị khoá 5 phút; quản trị có thể bấm **Mở khoá** ở cùng dòng để mở ngay.

## 2. Quên mật khẩu quản trị của cổng
- **Đang đăng nhập** và muốn đổi: thẻ **Cài đặt** → *Đổi mật khẩu quản trị* (cần mật khẩu hiện tại).
- **Đã quên hẳn:** hiện KHÔNG có cách đặt lại trong phần mềm. `QUEN_MAT_KHAU.bat` chỉ xoá tài khoản của phần mềm xếp (màn đăng nhập
  chính), KHÔNG đụng mật khẩu của cổng đăng ký. Dữ liệu `app.db` vẫn nguyên; đừng chạy lại «Thiết lập lần đầu» (không làm được khi cổng đã
  thiết lập). Báo cho người phát triển để được hỗ trợ — việc này được ghi là điểm còn thiếu của DK6.

## 3. Mất điện hoặc máy treo giữa chừng
Mở lại `PhanBoCauLacBo.exe`. Mọi thao tác ghi dữ liệu là một giao dịch SQLite: hoặc xong trọn vẹn hoặc không có gì thay đổi; giai đoạn hiện
tại được lưu trong `app.db`. Phiên đăng nhập nằm trong bộ nhớ nên bị mất: đăng nhập lại.
- Mất điện lúc **Chốt và xếp**: kết quả cũ còn nguyên (hoàn nguyên). Vào lại giai đoạn Nhập điểm và bấm lại; hạt giống đã khoá cho cùng
  kết quả. `run_history` (lịch sử các lần chạy) chỉ được thêm dòng, không bao giờ bị xoá.
- Nghi ngờ dữ liệu sai: khôi phục thủ công như mục 4.

## 4. Khôi phục bản sao lưu BẰNG TAY
Hiện **không có nút khôi phục** trong cổng; việc này làm bằng tay (có chủ ý, để tránh ghi đè nhầm).
1. **Đóng** phần mềm (không để cửa sổ nào còn mở).
2. Mở thư mục dữ liệu: `workspaces\<tên workspace>\` cạnh `PhanBoCauLacBo.exe` (workspace mặc định: `workspaces\truong-hoc\`).
3. Tìm tệp `app.db.bak-YYYYMMDD_HHMMSS_xxxxxx` (mỗi lần *Sao lưu ngay* hoặc *Chốt và xếp* tạo một bản; tên chứa giờ tạo).
   Chọn bản có giờ ngay trước thời điểm muốn quay về (giờ «Chốt và xếp» xem ở *Thêm → Nhật ký*).
4. **Chép `app.db` hiện tại sang nơi khác** (đặt tên `app.db.hong`) — đừng xoá.
5. Chép bản sao lưu đã chọn ra cùng thư mục và đổi tên thành `app.db`. Xoá `app.db-journal`, `app.db-wal`, `app.db-shm` nếu có.
6. Mở lại phần mềm, kiểm tra giai đoạn và dữ liệu.
Lưu ý: phần mềm chỉ giữ 10 bản sao lưu gần nhất; sao lưu nhiều lần liên tiếp có thể đẩy bản «trước khi xếp» ra khỏi danh sách. Muốn giữ,
chép bản đó sang nơi khác ngay sau khi bấm **Chốt và xếp**. Bản khôi phục làm mất mọi thay đổi sau thời điểm sao lưu (kể cả bài nộp của học sinh).

## 5. Máy thiếu WebView2
Phần mềm cần *Microsoft Edge WebView2 Runtime*. Nếu thiếu, phần mềm tự ghi lỗi vào tệp chẩn đoán cạnh `.exe` và mở giao diện trong cửa
sổ Edge/Chrome. Để dùng cửa sổ riêng như bình thường, cài WebView2 Runtime từ trang của Microsoft rồi mở lại. Không cần làm gì với dữ liệu.
