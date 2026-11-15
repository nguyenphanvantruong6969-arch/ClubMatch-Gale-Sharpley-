# PA15 — Thử với 3 học sinh giả, rồi dọn dẹp

⏱ 30 phút · [← PA14](PA14_phat_hanh_chia_se.md) · [Mục lục](../00_MUC_LUC.md)

**Cần có:** 3 tài khoản trường dùng thử (nhờ IT tạo, hoặc 3 em tình nguyện), đều thuộc nhóm học sinh. Mã giả `HS901`, `HS902`, `HS903`. Dữ liệu hoàn toàn giả.

**Chuẩn bị:** thêm 3 dòng vào `HocSinh` với email của 3 tài khoản thử.

| # | Ai | Làm gì | Mong đợi | ✓ |
|---|---|---|---|---|
| 1 | HS901 | Mở LINK APP trên **điện thoại** | Chào "HS901", ô chọn 1 cột, không tràn ngang | [ ] |
| 2 | HS901 | Mở trên **laptop** | Ô chọn 2 cột, khung giữa màn hình | [ ] |
| 3 | HS901 | Chọn ô 1 và ô 3, bỏ ô 2 → Nộp | Sang màn xác nhận; List: `pref_1`, `pref_2` có mã, `so_lan_nop` = 1 | [ ] |
| 4 | HS901 | Sửa lại → Nộp | Vẫn **1 dòng**, `so_lan_nop` = 2 | [ ] |
| 5 | HS901 | Chọn cùng CLB ở 2 ô | Chữ đỏ "trùng", nút mờ | [ ] |
| 6 | HS902 | Nộp phiếu, rồi mở thẳng List `NguyenVong` trên SharePoint | Chỉ thấy **dòng của mình** | [ ] |
| 7 | Tài khoản không có trong `HocSinh` | Mở LINK APP | Màn "chưa có trong danh sách" | [ ] |
| 8 | Bạn | Đổi `HanChot` về hôm qua → Publish → HS903 mở | Ô khoá, nút mờ, chữ đỏ "hết hạn" | [ ] |
| 9 | Bạn | **Đặt lại `HanChot` đúng → Publish** | | [ ] |
| 10 | Giáo viên | Mở LINK APP | Màn quản trị: "2 / 3 đã nộp", HS903 trong danh sách chưa nộp | [ ] |
| 11 | Bạn | List `NguyenVong` → **Export → Export to CSV** | Tải được tệp, tiêu đề có `student_id, name, pref_1…` | [ ] |
| 12 | Bạn | Nạp CSV CLB rồi CSV nguyện vọng vào rbda-kiosk, chạy xếp | Nạp không lỗi, có kết quả | [ ] |

## Dọn dẹp (bắt buộc trước khi mở cho toàn trường)
- [ ] Xoá 3 dòng thử ở `HocSinh`, `NguyenVong`, `ChonThi`.
- [ ] Trong kiosk: xoá dữ liệu thử (Quản lý → Vùng nguy hiểm).
- [ ] Kiểm lại `HanChot`, `SoNguyenVongToiDa`, `DSQuanTri` đúng → Publish.
- [ ] Gửi LINK APP + QR cho học sinh.

## Sau hạn chót
1. Khoá quyền List (SP09 phần 4).
2. Xuất CSV, nạp kiosk: mục 8 [bản kỹ thuật](../../HUONG_DAN_POWER_APPS_DANG_KY.md).
