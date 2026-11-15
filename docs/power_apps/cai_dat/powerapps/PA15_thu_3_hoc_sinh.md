# PA15 — Thử với 3 học sinh, rồi dọn dẹp

[← PA14](PA14_phat_hanh_chia_se.md) · [Mục lục](../00_MUC_LUC.md)

**Cần có:** 3 tài khoản trường để thử (nhờ bộ phận tin học tạo, hoặc mượn 3 em tình nguyện), đều nằm trong nhóm học sinh. Đặt mã giả `HS901`, `HS902`, `HS903`. Mọi dữ liệu ở đây đều là dữ liệu thử.

**Chuẩn bị:** thêm 3 dòng vào bảng `HocSinh` với thư điện tử của 3 tài khoản thử.

| # | Ai làm | Làm gì | Kết quả đúng | Đạt |
|---|---|---|---|---|
| 1 | HS901 | Mở ĐƯỜNG DẪN ỨNG DỤNG trên **điện thoại** | Chào "HS901", ô chọn xếp 1 cột, không phải kéo ngang | [ ] |
| 2 | HS901 | Mở trên **máy tính** | Ô chọn xếp 2 cột, nằm giữa màn hình | [ ] |
| 3 | HS901 | Chọn ô 1 và ô 3, bỏ trống ô 2 → Nộp | Sang trang xác nhận. Trên bảng: `pref_1`, `pref_2` có mã, `so_lan_nop` là 1 | [ ] |
| 4 | HS901 | Sửa lại → Nộp | Vẫn **1 dòng**, `so_lan_nop` là 2 | [ ] |
| 5 | HS901 | Chọn cùng một câu lạc bộ ở 2 ô | Chữ đỏ báo trùng, nút Nộp mờ đi | [ ] |
| 6 | HS902 | Nộp phiếu, rồi mở thẳng bảng `NguyenVong` trên SharePoint | Chỉ thấy **phiếu của chính mình** | [ ] |
| 7 | Tài khoản không có trong bảng học sinh | Mở ĐƯỜNG DẪN ỨNG DỤNG | Trang báo "chưa có trong danh sách" | [ ] |
| 8 | Bạn | Đổi `HanChot` thành ngày hôm qua → phát hành → HS903 mở | Ô chọn bị khoá, nút mờ, chữ đỏ báo hết hạn | [ ] |
| 9 | Bạn | **Đổi `HanChot` về đúng ngày → phát hành lại** | | [ ] |
| 10 | Giáo viên phụ trách | Mở ĐƯỜNG DẪN ỨNG DỤNG | Trang theo dõi: "2 / 3 học sinh đã nộp", HS903 ở danh sách chưa nộp | [ ] |
| 11 | Bạn | Bảng `NguyenVong` → «Export» → «Export to CSV» | Tải được tệp, dòng đầu có `student_id`, `name`, `pref_1`… | [ ] |
| 12 | Bạn | Đưa tệp câu lạc bộ rồi tệp nguyện vọng vào phần mềm xếp câu lạc bộ, chạy xếp | Không báo lỗi, ra kết quả | [ ] |

## Dọn dẹp (bắt buộc trước khi mở cho cả trường)

- [ ] Xoá 3 dòng thử ở các bảng `HocSinh`, `NguyenVong`, `ChonThi`.
- [ ] Trong phần mềm xếp câu lạc bộ: xoá dữ liệu thử.
- [ ] Kiểm tra lại `HanChot`, `SoNguyenVongToiDa`, `DSQuanTri` (PA04) → phát hành lại.
- [ ] Gửi ĐƯỜNG DẪN ỨNG DỤNG và mã QR cho học sinh.

## Sau hạn chót

1. Khoá bảng lại (SP09, Phần 4).
2. Tải dữ liệu về và đưa vào phần mềm xếp câu lạc bộ: làm theo mục 8 của [hướng dẫn chi tiết](../../HUONG_DAN_POWER_APPS_DANG_KY.md).
