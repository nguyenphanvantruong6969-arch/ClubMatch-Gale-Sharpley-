# Dựng ứng dụng đăng ký câu lạc bộ — Mục lục

Bộ hướng dẫn này chia việc thành nhiều tệp nhỏ. Mỗi tệp chỉ làm một việc. Làm lần lượt từ trên xuống, xong tệp nào thì đánh dấu tệp đó.

## Cách đọc hướng dẫn

- **Chữ trong ngoặc «…»** là chữ in trên màn hình (thường bằng tiếng Anh, vì Microsoft để vậy). Tìm đúng chữ đó rồi bấm.
- **Ô màu xám** là phần để **sao chép và dán**. Đừng gõ tay. Cách làm:
  1. Bôi đen toàn bộ chữ trong ô xám (hoặc bấm nút sao chép ở góc ô, nếu có).
  2. Bấm `Ctrl` + `C` để sao chép.
  3. Bấm vào chỗ cần điền trên màn hình.
  4. Bấm `Ctrl` + `A` để chọn hết chữ cũ (nếu có), rồi `Ctrl` + `V` để dán.
- 👀 là điều bạn sẽ thấy nếu làm đúng.
- ⚠️ là lỗi hay gặp và cách sửa.
- Tên nút có thể hơi khác vì Microsoft hay đổi giao diện. Mỗi chỗ đã ghi thêm tên khác có thể gặp.
- Mọi ví dụ về học sinh, câu lạc bộ đều là **ví dụ giả**.

## Phần A — Kho dữ liệu (SharePoint)

| Xong | Tệp | Việc |
|---|---|---|
| [ ] | [SP01](sharepoint/SP01_kiem_quyen.md) | Kiểm tra tài khoản và quyền |
| [ ] | [SP02](sharepoint/SP02_tao_site.md) | Tạo trang chứa dữ liệu |
| [ ] | [SP03](sharepoint/SP03_thao_tac_list_co_ban.md) | Học 5 thao tác cơ bản với bảng dữ liệu |
| [ ] | [SP04](sharepoint/SP04_list_CLB.md) | Tạo bảng câu lạc bộ |
| [ ] | [SP05](sharepoint/SP05_list_HocSinh.md) | Tạo bảng học sinh |
| [ ] | [SP06](sharepoint/SP06_list_NguyenVong.md) | Tạo bảng nguyện vọng |
| [ ] | [SP07](sharepoint/SP07_list_ChonThi.md) | Tạo bảng chọn câu lạc bộ thi (có thể bỏ qua) |
| [ ] | [SP08](sharepoint/SP08_nap_excel.md) | Đưa danh sách học sinh, câu lạc bộ từ Excel vào |
| [ ] | [SP09](sharepoint/SP09_phan_quyen.md) | Ai được xem, ai được sửa |

## Phần B — Ứng dụng cho học sinh (Power Apps)

| Xong | Tệp | Việc |
|---|---|---|
| [ ] | [PA01](powerapps/PA01_dang_nhap_moi_truong.md) | Đăng nhập, chọn đúng khu làm việc |
| [ ] | [PA02](powerapps/PA02_tao_app.md) | Tạo ứng dụng trống, chỉnh cho điện thoại và máy tính |
| [ ] | [PA03](powerapps/PA03_noi_du_lieu.md) | Nối ứng dụng với các bảng dữ liệu |
| [ ] | [PA04](powerapps/PA04_cong_thuc_app.md) | Điền hạn chót, số nguyện vọng, giáo viên phụ trách |
| [ ] | [PA05](powerapps/PA05_tao_man_hinh_va_khung.md) | Tạo các trang và khung tự co giãn |
| [ ] | [PA06](powerapps/PA06_man_khong_co_ten.md) | Trang báo "không có tên" |
| [ ] | [PA07](powerapps/PA07_dang_ky_phan_tren.md) | Trang đăng ký: lời chào, hạn chót, lời dặn |
| [ ] | [PA08](powerapps/PA08_dang_ky_o_chon.md) | Trang đăng ký: 10 ô chọn câu lạc bộ |
| [ ] | [PA09](powerapps/PA09_dang_ky_nut_nop.md) | Trang đăng ký: dòng báo lỗi và nút Nộp |
| [ ] | [PA10](powerapps/PA10_man_xac_nhan.md) | Trang xác nhận đã nộp |
| [ ] | [PA11](powerapps/PA11_man_chon_thi.md) | Trang chọn câu lạc bộ thi (có thể bỏ qua) |
| [ ] | [PA12](powerapps/PA12_man_quan_tri.md) | Trang theo dõi cho giáo viên |
| [ ] | [PA13](powerapps/PA13_man_dau_tien_va_chay_thu.md) | Chọn trang mở đầu, chạy thử |
| [ ] | [PA14](powerapps/PA14_phat_hanh_chia_se.md) | Phát hành, gửi đường dẫn, mã QR |
| [ ] | [PA15](powerapps/PA15_thu_3_hoc_sinh.md) | Thử với 3 học sinh, rồi dọn dẹp |

## Thứ tự bắt buộc

Làm xong Phần A trước rồi mới sang Phần B. Riêng PA15 cần SP09 đã xong.

## Khi bị kẹt

Chụp **nguyên màn hình** lúc báo lỗi, ghi tên tệp và số bước (ví dụ "PA08, bước 7"), gửi cho người phụ trách.
