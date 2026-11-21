# UX2 — Đánh giá cuối của lead (góc nhìn người dùng)

> Dữ liệu MÔ PHỎNG (bộ mẫu `NHIEUBUOI_*`, seed 9), Chromium 1400×1000, một lượt duy nhất theo §10 của
> `docs/phien/UX2_GIAO_THUC.md`. Chỉ là số đo vận hành, không phải khảo sát người dùng thật.
> Không chạy 800 HS (checker L8 đã đo). Ảnh: `docs/ke_hoach/ux/anh/ux2_danh_gia/`.

## Kết quả từng mục (quản trị + 1 lượt giáo viên)
| Mục | Đo được | Đạt? |
|---|---|---|
| #2/#13 nút bận | bấm → `aria-busy="true"`: 2,6 ms (yêu cầu ≤ 100 ms) | Đạt |
| #3 dấu ✓ | hiện 1 201 ms trên nút "Lưu CLB" (yêu cầu ≈ 1,2 s) | Đạt |
| #8 vùng bấm | nhỏ nhất quản trị: 44×34 px (nút "Xoá" trong bảng CLB, ngoại lệ ≥ 24 px đã chấp nhận); giáo viên: 44×44 px | Đạt (có ngoại lệ) |
| #7 lỗi tại ô | form CLB trống → con trỏ về ô đầu tiên `clubFormId`, 3 ô báo lỗi | Đạt |
| #11 tiến trình | sau khi chạy: Kiểm tra / Xếp / Ghi / Xuất đều "Xong" | Đạt |
| Hiệu ứng | vòng xoay `ux2Xoay` bình thường; `none` khi tắt "Hiệu ứng"; `none` khi hệ thống giảm chuyển động | Đạt |
| Phân quyền | giáo viên không thấy thẻ Xếp CLB và Quản lý | Đạt |
| Lỗi trang | 0 lỗi JavaScript ở cả hai vai | Đạt |

## Vấn đề nổi bật
1. **Lỗi tại ô bị lặp chữ** (ảnh `2_loi_o.png`): bấm "Lưu CLB" khi form trống, cùng một câu "Hãy nhập mã CLB, tên
   và chỉ tiêu." hiện 4 lần (3 ô + dòng phản hồi chung) và đẩy lệch lưới form. Đề xuất: mỗi ô nói đúng phần
   của nó ("Thiếu mã CLB") hoặc chỉ giữ một dòng chung và tô đỏ các ô.
2. Nút "Xoá" trong bảng dày chỉ 34 px chiều cao vùng bấm (ngoại lệ đã ghi trong "Needs Truong").
3. Ảnh `1_sau_chay.png`: bốn pha "Xong" rõ ràng; `3_giao_vien.png`: thanh bên gọn, không lộ nút quản trị.

## Đề xuất
- Mục nhỏ tiếp theo: tách câu báo lỗi theo từng ô cho form CLB và form học sinh (chỉ giao diện, `i18n.js`).
- Giữ nguyên các ngoại lệ 24 px trừ khi giáo viên bấm nhầm trên máy kiosk cảm ứng.
