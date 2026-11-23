# Báo cáo soát mã UX5B-L3/L4 (nhánh claude/ux5b-l3-l4-tu-dong)

Phạm vi: `UX5B-FIX-CI`, `UX5B-L3`, `UX5B-L4` (đỉnh b42cc57, sau đó thêm một commit sửa tài liệu). Chỉ giao diện, chữ và test. Số đo là dữ liệu MÔ PHỎNG. Soát bằng tay, không subagent, chỉ báo cáo.

- `kiem_nhanh.py`: 7/7 ĐẠT (ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, trung_khit 15 ca, khong_sua_nhat_ky).
- `git diff origin/main...HEAD --stat` không có tệp backend (api*.py, db*.py, schema, pipeline): bất biến 1-8 không bị chạm.
- Test chạy: nhóm giao diện/nhãn/i18n bị ảnh hưởng (gồm 15 tệp test cũ đã chỉnh) và ba tệp UX5B: đạt.

## Phát hiện

| # | Mức | Tệp | Vấn đề | Đường xảy ra | Trạng thái |
|---|---|---|---|---|---|
| 1 | nên sửa | docs/ke_hoach/CLAUDE_CHI_TIET.md | Số tệp test trong bản đồ mã còn 387 trong khi thực tế 389 | `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` đỏ (đã tái hiện) | Đã sửa: 389 |
| 2 | nhỏ | tests/test_giao_dien_ux5b_l3.py, l4.py | Test viết sau mã (không test-first thật), nhưng mọi ca đều kiểm id/văn bản mới nên đỏ nếu bỏ mã | suy luận | Ghi nhận |

## Điểm cần Truong cân nhắc (không phải lỗi)

1. Cách đếm Hick: bỏ dữ liệu dạng danh sách và nút "Sửa" của mục gập. Quản trị 7, giáo viên 6 (trước: 27 và 23). Tính cả "Sửa" thì quản trị 9, giáo viên 7.
2. Lưu Bước 2 thì Bước 3 (nếu có) tự mở, vì các nhắc "chia lại điểm" và "huy chương đã chỉnh tay" nằm trong Bước 3.
3. Đang chấm điểm một CLB thì danh sách lui đi; nút "‹ Danh sách" về lại và bỏ điểm đã gõ chưa lưu (giống đổi tab).

## Tầng 3 (giao diện)

- Dữ liệu người dùng chỉ vào `textContent` (dòng tóm tắt, trạng thái); không thêm `innerHTML`.
- Không thêm lời gọi API; không thêm `localStorage`. Chữ tiếng Anh: không còn `{tham_số}` chưa điền, chữ có dấu chỉ ở tên dữ liệu (đã thử bằng Chromium).
- Giáo viên: không thấy "Tạo mới", mục điểm quyết tâm; thẻ Xếp CLB ẩn.
