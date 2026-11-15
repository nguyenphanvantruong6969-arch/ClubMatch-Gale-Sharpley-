# Dựng ứng dụng đăng ký câu lạc bộ — Mục lục

Bộ hướng dẫn này chia việc thành nhiều tệp nhỏ. Mỗi tệp chỉ làm một việc. Làm lần lượt từ trên xuống, xong tệp nào thì đánh dấu tệp đó.

## Cách đọc hướng dẫn

- **Chữ trong ngoặc «…»** là chữ in trên màn hình (bằng tiếng Anh, vì Microsoft để vậy). Tìm đúng chữ đó rồi bấm.
- **Ô màu xám** là phần để **sao chép và dán**. Đừng gõ tay. Cách làm:
  1. Đưa chuột vào ô xám. Nếu ở góc trên bên phải của ô hiện một nút hình hai tờ giấy chồng nhau: bấm nút đó là đã sao chép xong, bỏ qua bước 2. Nếu không hiện nút: kéo chuột bôi đen toàn bộ chữ trong ô.
  2. Bấm `Ctrl` + `C` để sao chép.
  3. Bấm chuột vào chỗ cần điền trên màn hình.
  4. Bấm `Ctrl` + `A` để chọn hết chữ đang có ở chỗ đó.
  5. Bấm `Ctrl` + `V` để dán đè lên.
- Mỗi ô xám chỉ chứa **một** thứ cần dán. Thấy nhiều ô xám liền nhau thì dán từng ô một, đúng thứ tự.
- 👀 là điều bạn phải thấy nếu làm đúng. **Chưa thấy thì đừng làm tiếp**, đọc dòng ⚠️ ngay bên dưới.
- ⚠️ là lỗi hay gặp và cách sửa.
- Microsoft thỉnh thoảng đổi tên nút. Chỗ nào có hai tên, hướng dẫn ghi cả hai, dạng: «tên này» (bản khác ghi «tên kia»).
- Mọi ví dụ về học sinh, câu lạc bộ đều là **ví dụ giả**.

## Bốn thứ phải ghi vào sổ tay

Trong lúc làm, bạn sẽ được nhắc ghi lại 4 thứ. Mở sẵn một tệp ghi chú (Notepad) để dán vào:

| Tên gọi trong hướng dẫn | Ghi ở tệp nào | Là gì |
|---|---|---|
| **NHÓM HỌC SINH** | SP01 | Tên nhóm gom tài khoản học sinh |
| **ĐỊA CHỈ TRANG** | SP02 | Địa chỉ trang SharePoint chứa dữ liệu |
| **KHU LÀM VIỆC** | PA01 | Tên ngăn chứa ứng dụng trong Power Apps |
| **ĐƯỜNG DẪN ỨNG DỤNG** | PA14 | Đường dẫn gửi cho học sinh |

## Phần A — Kho dữ liệu (SharePoint)

> **Có người quản trị Microsoft 365 của trường giúp?** Nhờ họ làm [SP00 — tệp lệnh tự động](sharepoint/SP00_tu_dong.md). Tệp lệnh làm thay toàn bộ SP02 đến SP09 (và bảng của PA16). Làm xong thì bỏ qua Phần A, sang thẳng PA01.

| Xong | Tệp | Việc |
|---|---|---|
| [ ] | [SP01](sharepoint/SP01_kiem_quyen.md) | Kiểm tra tài khoản và quyền |
| [ ] | [SP02](sharepoint/SP02_tao_site.md) | Tạo trang chứa dữ liệu |
| [ ] | [SP03](sharepoint/SP03_thao_tac_list_co_ban.md) | Học 5 thao tác cơ bản với bảng dữ liệu |
| [ ] | [SP04](sharepoint/SP04_list_CLB.md) | Tạo bảng câu lạc bộ |
| [ ] | [SP05](sharepoint/SP05_list_HocSinh.md) | Tạo bảng học sinh |
| [ ] | [SP06](sharepoint/SP06_list_NguyenVong.md) | Tạo bảng nguyện vọng |
| [ ] | [SP07](sharepoint/SP07_list_ChonThi.md) | Tạo bảng chọn câu lạc bộ thi (bỏ qua nếu không câu lạc bộ nào thi tuyển) |
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
| [ ] | [PA11](powerapps/PA11_man_chon_thi.md) | Trang chọn câu lạc bộ thi (bỏ qua nếu đã bỏ SP07) |
| [ ] | [PA12](powerapps/PA12_man_quan_tri.md) | Trang theo dõi cho giáo viên |
| [ ] | [PA17](powerapps/PA17_lam_dep.md) | Làm đẹp: màu trường, logo, phông chữ, bo góc, biểu tượng, hiệu ứng (làm sau PA12, trước PA13) |
| [ ] | [PA13](powerapps/PA13_man_dau_tien_va_chay_thu.md) | Chọn trang mở đầu, chạy thử |
| [ ] | [PA14](powerapps/PA14_phat_hanh_chia_se.md) | Phát hành, gửi đường dẫn, mã QR |
| [ ] | [PA15](powerapps/PA15_thu_3_hoc_sinh.md) | Thử với 3 học sinh, rồi dọn dẹp |

## Phần C — Thêm bài thi tuyển vào ứng dụng (chỉ khi có câu lạc bộ thi tuyển)

| Xong | Tệp | Việc |
|---|---|---|
| [ ] | [PA16](powerapps/PA16_bieu_mau_va_bai_thi.md) | Phiếu đăng ký và bài thi trắc nghiệm ngay trong ứng dụng: bảng câu hỏi, bảng đáp án, trang làm bài, nút chấm điểm |

## Thứ tự bắt buộc

- Làm xong Phần A rồi mới sang Phần B.
- PA17 làm sau PA12 (và sau PA16 nếu có), trước PA13.
- PA15 cần SP09 đã xong.
- PA16 cần SP07 và PA11 đã xong (không được bỏ qua hai tệp đó), và PA15 đã đạt.

## Khi bị kẹt

1. Chụp **nguyên màn hình** lúc báo lỗi (phím `Windows` + `Shift` + `S`, kéo chuột quanh cả màn hình).
2. Ghi tên tệp và số bước, ví dụ "PA08, bước 7".
3. Gửi ảnh và dòng ghi đó cho người phụ trách.
