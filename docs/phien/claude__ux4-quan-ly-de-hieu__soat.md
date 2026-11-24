# Soát mã UX4 (rút gọn, chỉ báo cáo)

Phạm vi: `git diff 7e9d673..HEAD`, chỉ tệp giao diện (index.html, style.css, i18n.js, js/00, 03, 05, 09, 15, 18, 19_muc_tieu, 19_ux1b_gv) + tests + docs. Không có tệp backend (`*.py` sản phẩm) nào đổi.

- Máy (`kiem_nhanh.py --co-so 7e9d673`): 7/7 ĐẠT (ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, trung_khit 15 ca, khong_sua_nhat_ky). Máy không có `origin/main` nên so với nhánh gốc 7e9d673.
- Tầng 1–2 (lõi, backend): không đổi. Bất biến 1 giữ: cùng cấu hình thì cùng kết quả (kiem_nhanh trung_khit).
- Tầng 3 (giao diện): id cũ giữ; thẻ đổi sang `<details>`/tab chỉ ẩn hiện; ba ô chọn cũ vẫn gửi đúng `priority/tier_mode/score_scope` (test 4 tổ hợp); bất biến 2: dòng "Phần mềm không dùng thứ hạng nguyện vọng…" còn hiện ở Cách xếp (test). Mã CLB tự điền không ghi đè mã đã có (hậu tố _2…), chỉ tô ô Mã khi có tên mà vẫn không ra mã.
- Tầng 4 (vệ sinh): test cũ đã sửa có chủ đích và liệt kê ở CHANGELOG; không bỏ/yếu hoá assert, chỉ đổi chữ hoặc đường vào (menu Thêm ▾, tab Cách xếp, Thêm tuỳ chọn). `test_ux2_nut` đỏ từ trước (cũng đỏ ở 7e9d673).
- Chưa chạy toàn bộ test (CI chạy). Đã chạy ~36 tệp giao diện liên quan, 2 lượt song song, kết quả cuối xanh (một ca chớp đỏ ở a13_10_nhan, xanh khi chạy lại).
- Ngoài phạm vi (một dòng): `ql_tab_*` và khoá `ux1a_nang_cao` còn trong i18n.js nhưng không dùng nữa (khoá `ux1a_nang_cao`), để dành dọn ở lượt khác.
