# Tệp thử nạp Excel ở cổng đăng ký (quản trị → nạp danh sách HS / GV / phòng) — mục DK9

> DỮ LIỆU MÔ PHỎNG: tên do máy bịa, không phải học sinh hay giáo viên thật.

Tệp .xlsx có ba trang tính: «Học sinh» (Mã HS | Họ tên | Lớp), «Giáo viên» (Họ tên), «Phòng» (Tên phòng | Sức chứa). Dải khối mặc định 6–12.
Kết quả "xem trước" dưới đây đã kiểm bằng `dk_excel_xem_truoc` / `dk_excel_nap`.

| Tệp | Nội dung | Kết quả mong đợi |
|---|---|---|
| DK_01 | 60 HS (có mã `0123456`, `HS-0042`), 8 GV, 6 phòng | nạp sạch: 60 / 8 / 6 mới |
| DK_02 | 800 HS, chỉ trang Học sinh | nạp sạch; báo thiếu trang Giáo viên, Phòng |
| DK_03 | 12 GV + 10 phòng, không có HS | nạp sạch; báo thiếu trang Học sinh |
| DK_04 | tiêu đề viết khác, cột phụ, tên trang hoa/thường khác, trang «Hướng dẫn» | nạp sạch, trang Hướng dẫn bị bỏ qua |
| DK_05 | nạp SAU DK_01: 2 HS cũ đổi tên/lớp + 1 HS mới, 1 GV mới, phòng P101 (đã có) + P999 | HS: 1 mới, 2 cập nhật (giữ PIN); GV 1 mới; phòng 1 mới, 1 đã có |
| DK_06 | lỗi từng dòng: mã trống/sai/trùng, tên trống/dài, lớp trống, khối ngoài dải, sức chứa sai, tên trùng | dòng hợp lệ vẫn nạp, dòng lỗi được liệt kê kèm số dòng |
| DK_07 | toàn dòng lỗi | xem trước 0 dòng hợp lệ; nạp báo `dk_excel_khong_co_dong` |
| DK_08 | tiêu đề sai thứ tự cột | lỗi mức tệp `dk_excel_tieu_de_sai` |
| DK_09 | không trang nào đúng tên | lỗi `dk_excel_khong_co_sheet` |
| DK_10 | chỉ có hàng tiêu đề | không có dòng nào để nạp |
| DK_11 | 5 001 HS | lỗi `dk_excel_qua_nhieu_dong` (tối đa 5 000) |
| DK_12 | CSV đổi đuôi .xlsx | lỗi `dk_excel_khong_phai_xlsx` |
