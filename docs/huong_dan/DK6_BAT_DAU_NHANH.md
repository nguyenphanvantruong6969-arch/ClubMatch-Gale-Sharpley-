# Cổng Đăng ký CLB — bắt đầu nhanh (1 trang)

Dành cho người quản trị (thầy/cô phụ trách). Cổng chạy NGAY TRÊN máy cài phần mềm: giáo viên và học sinh đến máy đó để
đăng nhập (cổng chỉ nhận kết nối từ chính máy này). Dữ liệu trong ví dụ là MÔ PHỎNG.

## 1. Cài đặt
1. Tải `PhanBoCauLacBo-windows.zip` (xem `HUONG_DAN_CAI_DAT.md`), **giải nén cả thư mục**, chạy `PhanBoCauLacBo.exe`.
2. Windows hiện cảnh báo «không có chữ ký số»: bấm *Thông tin thêm* → *Vẫn chạy* (không phải lỗi hay virus).
3. Máy cần Microsoft Edge WebView2; thiếu thì phần mềm tự mở cửa sổ Edge/Chrome thay thế (xem `DK6_XU_LY_SU_CO.md`).

## 2. Thiết lập lần đầu
Trên màn đầu của phần mềm bấm **Mở Đăng ký CLB** (hoặc mục *Đăng ký CLB* ở thanh bên) → **Thiết lập lần đầu** → điền:
mật khẩu quản trị (≥ 4 ký tự, **ghi lại ở nơi an toàn**), mã trường (giáo viên dùng để tự đăng ký), các buổi, khối thấp nhất/cao nhất
→ **Thiết lập cổng**. Sau đó vào **Quản trị** bằng mật khẩu vừa đặt. Phiên quản trị tự khoá sau 2 phút không thao tác.

## 3. Sáu giai đoạn (đi lần lượt, mỗi bước một nút ở thẻ «Việc bây giờ»)
| # | Giai đoạn | Quản trị làm gì |
|---|---|---|
| 1 | **Chuẩn bị** | Thêm phòng (tên, sức chứa); dán danh sách học sinh «mã ⇥ họ tên ⇥ lớp» → in phiếu PIN (chỉ hiện một lần). Bấm *Mở đăng ký giáo viên*. |
| 2 | **Giáo viên đăng ký** | Tạo tài khoản giáo viên hàng loạt (phiếu PIN) hoặc để giáo viên tự đăng ký bằng mã trường; đặt hạn chót nếu muốn. Bấm *Đóng đăng ký giáo viên*. |
| 3 | **Duyệt CLB** | Duyệt hoặc từ chối từng CLB; sửa số nhận và phòng. Học sinh chỉ thấy CLB đã duyệt. Bấm *Mở cho học sinh*. |
| 4 | **Học sinh đăng ký** | Theo dõi tiến độ theo lớp (lớp chậm nhất ở trên); gia hạn nếu cần. Bấm *Đóng đăng ký học sinh*. |
| 5 | **Nhập điểm** | Nhập hoặc dán điểm bài thi cho CLB Tuyển chọn (mọi bài thi phải có điểm) → **Chốt và xếp**. |
| 6 | **Xuất** | Xem tóm tắt lần xếp, **Xuất Sổ nhập**, hoặc xem kết quả trong phần mềm. *Xếp lại (cùng hạt giống)* cho cùng kết quả. |

Màn quản trị tự cập nhật vài giây một lần ở «Việc bây giờ» và «Danh sách» (không tự cập nhật ở Cài đặt, Thêm, Chuẩn bị, Xuất).

## 4. Nên làm
- Bấm **Sao lưu ngay** (thẻ *Thêm*) trước mỗi giai đoạn quan trọng, nhất là trước **Chốt và xếp**. Phần mềm cũng tự sao lưu ngay trước khi xếp.
- Đổi mật khẩu quản trị ở thẻ **Cài đặt** → *Đổi mật khẩu quản trị* khi cần (các máy quản trị khác bị đăng xuất).
- Sự cố (quên PIN, mất điện, khôi phục bản sao lưu): xem `DK6_XU_LY_SU_CO.md`.
