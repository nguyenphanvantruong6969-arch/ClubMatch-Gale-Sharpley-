# Báo cáo soát mã UX5A (giai đoạn 2)

Phạm vi: `git diff edf7526..HEAD` (L1–L4 + sửa giai đoạn 2). Chỉ giao diện + chữ + test. Dữ liệu MÔ PHỎNG (sổ 120 học sinh, 4 lớp, seed 42).

## Máy
- `kiem_nhanh.py` 7/7 (cần `git fetch origin main`); `ruff check .` sạch.
- Test giao diện toàn nhóm (`test_giao_dien_*`, `test_ws_*`, `test_i18n_sync`, `test_gt4_cau_giai_trinh`, 4 tiến trình, Chromium thật): 1336 đạt, 14 đỏ. Chia ra: **2 do UX5A** (`test_giao_dien_xp1_xuat_pdf::test_menu_co_ba_muc…` nhãn menu; `test_giao_dien_fa_gap5_phan_hoi::test_cham_ba_cau_roi_gui` câu "khó nhất" nay trong nếp) → đã sửa; **12 có sẵn ở `edf7526`** (đã chạy lại trên bản gốc, đều đỏ): `fa_quan_ly` ×2, `fg8_cau_chu`, `ux2_nut` ×5 (nút `tkNutMoHop` 216×36 ở thanh bên), `ux1_tiep_theo`, `ux1_nhap_so`, `sg2_diem_quyet_tam`, `t3_l3` → ghi "còn mở", không thuộc UX5A.
- Các test UX5A (+ `test_ws_nhan`, `test_i18n_sync`): 98 đạt, chạy 2 lần liền không chập chờn.

## Tầng 1–2 (lõi, backend)
Không đụng: `git diff edf7526..HEAD --stat` không có tệp `.py` sản phẩm. `trung_khit` 15 ca trùng khít.

## Tầng 3 (giao diện)
| Mục | Kết quả |
|---|---|
| Chữ tiếng Anh: còn `{tham_số}` / chữ Việt | ĐẠT cả hai thẻ × hai vai (test `test_tieng_anh_…`) |
| XSS / `innerHTML` mới | Không có (JS chỉ thêm 3 dòng `.hidden`) |
| Lời gọi API mới | Không có |
| Bấm đúp xuất | Giữ `khoa.dangXuat` sẵn có |
| Giáo viên | không thấy `data-quyen="quan_tri"`, không nút chết |
| **Lỗi tìm được** | Menu "Báo cáo và phiếu in ▾" bị khung bên dưới đè (chữ "Theo CLB" lộ qua menu); dòng "Chọn thêm tệp để xuất" dính sát hàng nút. Sửa: `.panel:has(details.menu-khac[open]) {z-index}` + margin. Test hồi quy `tests/test_giao_dien_ux5a_loi.py` (7 ca). |

## Tầng 4
- Gây hỏng tạm 4 chỗ: bỏ vàng "Tải bảng này" (đỏ), vàng lại "Chạy vòng 2" (đỏ), bỏ ẩn nút hàng chọn (đỏ), mở sẵn nếp báo cáo (không đỏ: ứng dụng tự đóng menu khi bấm ra ngoài, không phải test yếu). Đã hoàn tác, `git status` sạch phần mã.
- Khoá i18n: `th_reserve_capacity`, `kpi_du_tru_thua` không còn chỗ dùng trực tiếp (giữ vì ảnh chụp `test_ws_nhan`).

## Số đo trước / sau (điều khiển nhìn thấy + bật, nếp đóng; gồm 5 nút tiêu đề cột của bảng ở thẻ Kết quả)
| Thẻ | Vai | Trước | Sau | Nút vàng trước → sau |
|---|---|---|---|---|
| Kết quả | Quản trị | 17 | 15 (10 không tính tiêu đề cột) | 0 → 1 (`btnKqTaiBang`) |
| Kết quả | Giáo viên | 16 | 14 (9) | 0 → 1 |
| Chi tiết và xuất tệp | Quản trị | 21 | 21 | 1 → 1 (`btnXuatTuyChon`) |
| Chi tiết và xuất tệp | Giáo viên | 19 | 19 | 1 → 1 |
Khung "Theo lớp và báo cáo": 5 → 3. Khung tra cứu mở "Mã tra cứu…": vàng 1 (`btnGtCheDoHs`) → 0. Hai nút FA (vòng 2, khiếu nại) và "Gửi" phản hồi: vàng → thường.

## Còn mở
1. 12 test đỏ có sẵn từ UX4 (danh sách trên).
2. Hai khung "Chọn lớp" (khung Theo lớp và bảng kết quả) cùng hiện một ô chọn đã nối với nhau: thiết kế cũ (UX1B), chưa gộp.
3. Tab đang chọn "Theo lớp" nền xanh đậm nổi gần bằng nút vàng (ghi chú checker; không vi phạm luật).
