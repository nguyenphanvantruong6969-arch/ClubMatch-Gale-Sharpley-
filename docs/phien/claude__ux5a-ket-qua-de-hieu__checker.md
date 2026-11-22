# UX5A checker — vòng 1 (`edf7526..29d70d2`)

Kết luận: **PASS** (0 mục bắt buộc sửa, 3 ghi chú không chặn).

## Chạy
- `tests/test_giao_dien_ux5a_*.py` + `test_ws_nhan.py` + `test_i18n_sync.py`: **90 passed**.
- `ruff check .` sạch; `kiem_nhanh.py` **7/7** (trùng khít 3 bộ × 5 seed).
- `git diff --stat`: không có tệp `.py` sản phẩm (chỉ `tests/`), không đổi backend.
- `test_giao_dien_t3_l3.py::..._khong_con_du_tru` đỏ: **xác nhận có sẵn** (cũng đỏ ở `edf7526`), không do UX5A.

## Số đo của checker (Chromium thật, 1280×900, dữ liệu MÔ PHỎNG 120 HS, 4 lớp, seed 42)
Điều khiển nhìn thấy + bật, không tính `thead`/`tbody`.

| Thẻ | Vai | Nếp đóng | Mở hết nếp | `.btn-primary` thấy được | `.btn-danger` thấy được |
|---|---|---|---|---|---|
| Kết quả | Quản trị | 10 (tra cứu 2, theo lớp 3, bảng 5) | 16 | 1 (`btnKqTaiBang`) | 0 |
| Kết quả | Giáo viên | 9 (tra cứu 1, theo lớp 3, bảng 5) | 12 | 1 (`btnKqTaiBang`) | 0 |
| Chi tiết và xuất tệp | Quản trị | 21 | 29 | 1 (`btnXuatTuyChon`) | 0 |
| Chi tiết và xuất tệp | Giáo viên | 19 | 23 | 1 (`btnXuatTuyChon`) | 0 |

Khớp bản đồ L1 (Kết quả 10/9, Chi tiết 21/19). Khung "Xuất dữ liệu" = 4 (QT) / 3 (GV) đúng ngân sách.

## Danh sách chấp nhận
- ≤ 1 nút vàng mỗi thẻ, không nút đỏ: ĐẠT (cả hai vai; banner "Xử lý…" là viền cảnh báo, không vàng).
- Không mất gì, id giữ nguyên: ĐẠT. So `id=` index.html trước/sau: chỉ **thêm** `chiTietNhomTieuDe, phThemY, ux1bThemMenu, ux1bThemTom, xuatHocSinhNhan`, không id nào bị xoá. Ba nút báo cáo vào `ux1bThemMenu` (2 lần bấm), `xuatFaAnGoiY` chuyển vào menu "Xuất tệp khác".
- D4 (ẩn nút theo hàng đã chọn): ĐẠT. Trước khi tick: `btnXuatHsDaChon`, `btnBoChonHs`, `xuatHocSinhNhan` ẩn; sau tick 1 em: hiện, thẻ 22 → 24 điều khiển, vẫn 1 vàng.
- Chữ cấm khi đã mở hết nếp (cả hai thẻ × hai vai): không thấy "cấu hình", "suất", "Chọi", "quỹ", "tier", "reserve", "CLB nguyện vọng", ngày ISO, hay `{placeholder}` còn sót. 0 lỗi JS (`pageerror`).
- EN phản chiếu VI: mọi khoá đổi/mới đều có cả hai tiếng (`i18n_khoa`, `test_i18n_sync` xanh); `SUA_CO_Y` có nhãn UX5A.
- Giáo viên: không thấy phần `data-quyen="quan_tri"`, không nút chết, vẫn tới tra cứu, "Theo lớp", "Xuất theo lớp", báo cáo.

## Ghi chú không chặn (coder tự quyết, không cần vòng 2)
1. **Lệch bảng từ ngữ đã duyệt** (đã ghi trong CHANGELOG L2/L3): `kq_desc` giữ "tra cứu… Bảng này" (do test GT4); `mt1_kq_nv1` = "Được vào {slot_sl} mình chọn đầu tiên: {pct}%" thay "{pct}% {person_l} được…"; `ux5a_xuat_canh_bao` là khoá mới (khoá cũ giữ cho thẻ khác); bỏ `ux5a_th_ti_le_choi`. Chấp nhận, nhưng nên để Truong thấy dòng `mt1_kq_nv1` vì nó đổi cấu trúc câu, không chỉ từ.
2. **Khoảng cách thẻ Chi tiết**: dòng "Chọn thêm tệp để xuất" (`<summary>`) nằm sát ngay trên hàng nút "Xuất kết quả (Excel) / Xuất theo lớp", nhìn giống nhãn của hàng nút. Chỉ là thẩm mỹ, nên thêm margin dưới `summary` nếu muốn. (Chưa biết có phải đã vậy từ trước UX5A.)
3. **Von Restorff nhẹ**: tab đang chọn "Theo lớp" (nền xanh đậm) ở thẻ Kết quả nổi gần bằng nút vàng. Không vi phạm luật (không phải `.btn-primary`), chỉ lưu ý nếu Truong thấy hai chỗ cùng nổi.
   Ngoài ra `{person_pl}` dùng trong VI (`ux1b_ma_tra_cuu`, `gt_che_do_hs`, `gt_buoc_3`, `fill_sap_xep_choi`) còn bảng duyệt ghi `{person_l}`; hiển thị ra "học sinh" đúng, không ảnh hưởng.

## Ảnh chụp (scratchpad, không commit)
quản trị Kết quả, quản trị Chi tiết, giáo viên Kết quả, giáo viên Chi tiết (1280×900, scale 1). Quan sát: một nút vàng mỗi thẻ, nếp "Báo cáo và phiếu in ▾" và "Xuất tệp khác ▾" đúng chỗ, giáo viên không còn nếp "Mã tra cứu…" / nút "Xuất tệp khác".
