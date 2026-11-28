# Báo cáo soát mã CT1 (Xem xét chỉ tiêu)

> **Cập nhật 2026-11-28 (CT1-FIX):** phát hiện 1, 2, 3 (phương án b), 4, 5 ĐÃ SỬA, xem `CHANGELOG.md`. Phát hiện 3 chọn (b) vì đó là đề xuất của báo cáo; Truong có thể đổi sang (a) hoặc (c). Phát hiện 6 giữ nguyên. Bảng dưới là bản gốc lúc soát.

Nhánh `claude/ct1-xem-xet-chi-tieu`, so với `main`. Dữ liệu thử là DỮ LIỆU MÔ PHỎNG. Soát bằng `soat-ma` (không subagent).

## Phạm vi
- Tệp mới: `chi_tieu_ct1.py`, `api_chi_tieu.py`, `js/20_xem_xet_chi_tieu.js`, 4 tệp test CT1, tài liệu. Tệp sửa: `api.py` (thêm mixin), `phan_quyen.py`, `i18n_errors.py`, `i18n_loi.js`, `index.html`, `i18n.js`, `style.css`, `tests/_ux5a_chung.py`, `tests/test_gt3_phan_quyen.py`, `tests/test_mt1_uoc_tinh.py`.
- Hàm cũ bị gọi (một bậc): `_giai_trong_bo_nho`, `cac_dong_match_results`, `run_chinh_thuc_moi_nhat`, `tieu_chi.so_sanh_lan_chay`, `_khoa_xuat`, `_duong_xuat`, `_ghi_csv`, `ux1aMoNangCao`, `chayXuat`. Không hàm nào bị sửa.
- Lệnh: `kiem_nhanh.py` → **7/7 ĐẠT** (ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, trung_khit 3 bộ × 5 seed, khong_sua_nhat_ky).
- Test đã chạy: CT1 (29 + 22 + 16 ca tay + 1 tài liệu + 13 Chromium), liên quan (gt3_phan_quyen, i18n_sync, mt1_uoc_tinh, gt2_chay_thu, test_api, ux5a l2/l3/l4, sfb_menu_hep, a14_the_xem, kich_ban_nhap_tay): xanh. Chưa chạy bộ đầy đủ (CI chạy). Test giao diện chạy xanh 2 lần liền; chưa chạy 10 lần.

## Tầng 1 — Lõi thuật toán
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| 1 Bất biến 2 | ĐẠT | `chi_tieu_ct1` chỉ được import bởi `api_chi_tieu.py`; không có đường nào vào `compute_club_priority`. Thứ hạng nguyện vọng chỉ dùng để ĐẾM nhu cầu hiển thị. |
| 3 Mặc định không đổi | ĐẠT | `trung_khit` 15 ca; CT1 chỉ đọc. |
| 6 Biên | ĐẠT | `kiem_buoc_tu_chon` từ chối `bool`, số thực, 0, âm, không phải danh sách, > 20 bước; 200 bộ ngẫu nhiên giữ Σ chỗ. |
| 7 Bất biến 3 | ĐẠT | chỉ đọc bộ số đã khoá; thiếu số thì `gt2_thu_stb_chua_day`, không bốc lại. |
Tầng 1: **Đạt**.

## Tầng 2 — Backend
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| 1 Bất biến 5 | không áp dụng | không ghi; `test_khong_ghi_gi_ca`: tệp CSDL nguyên byte, không `.bak-*`, `run_history` không thêm dòng. Đột biến `sao_luu=True` bị test bắt. |
| 2 Bất biến 4 | ĐẠT | không ghi `run_history`. |
| 3 Bất biến 6 | ĐẠT | mọi nhánh trả `{ok,data,errors}`; 7 mã `ct1_*` có vi + en. |
| 9 Quyền | ĐẠT | cả ba hàm trong `_QUAN_TRI`; đột biến bỏ khỏi bảng bị 3 test bắt. (Cổng chỉ hiệu lực khi có tài khoản, như mọi hàm khác.) |
| 10 Xuất | ĐẠT | từ chối khi chưa có kết quả hoặc không giải lại được. |
Hiệu năng đo trên `SO_NHAP_DQT_800HS_HOP_LE.xlsx` (800 học sinh, 4 buổi, 11 bước): **1,84 giây**, giữ khoá ghi suốt thời gian đó.
Tầng 2: **Đạt**.

## Tầng 3 — Giao diện
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| 2 XSS | ĐẠT | tên CLB / học sinh chứa `<img onerror>`: `window.__xss` không đặt, 0 thẻ `img` trong khung (mọi chữ qua `textContent`). |
| 3 Đổi ngôn ngữ / bấm đúp | ĐẠT | sang tiếng Anh: không còn `{tham_số}`, chỉ còn tên dữ liệu có dấu; nút "Xếp lại" bị khoá khi đang gọi, xuất dùng khoá `chayXuat`. |
| 5 Màu và chữ | ĐẠT một phần | màu luôn kèm chữ (test); xem phát hiện 4. |
| Hick / Von Restorff | ĐẠT | test từng khung: "Khuyến nghị" 1 điều khiển, "Tự thử" gập sẵn, 1 nút vàng mỗi khung, không nút đỏ, không "Áp dụng". |
| 390 px | ĐẠT | `scrollWidth ≤ innerWidth`. |
Chưa đo: chèn lỗi bằng `page.route` (HTTP 500 / đứt mạng) và phím mũi tên.
Tầng 3: **Cần sửa** (phát hiện 1, 2, 4).

## Tầng 4 — Vệ sinh, tài liệu, test
- ruff sạch; 0 khoá `ct1_*` thừa; CHANGELOG, TIEN_DO, sổ đăng ký (md + json), HUONG_DAN, NHAP_TAY, SO_LIEU đã cập nhật.
- Gây hỏng tạm 4 chỗ: bỏ ngưỡng `chua_dap` (**không bị bắt**, xem phát hiện 5), đảo luật hoà bên nhận (bị bắt, 4 test đỏ), `sao_luu=True` (bị bắt), bỏ hàm khỏi bảng quyền (bị bắt). Đã hoàn tác, `git status` sạch.
Tầng 4: **Đạt**, kèm phát hiện 5.

## Phát hiện
| # | Mức | Tệp | Vấn đề | Đường xảy ra | Đề xuất | Chắc chắn? |
|---|---|---|---|---|---|---|
| 1 | nên sửa | `api_chi_tieu.py` (`thong_ke_ket_qua`), `js/20_xem_xet_chi_tieu.js` | Khi trường có NHIỀU buổi, các số đếm là lượt (học sinh × buổi) nhưng chữ ghi "học sinh". | `SO_NHAP_DQT_800HS_HOP_LE`: `truoc.tong = 2836`, `so_hoc_sinh = 800`; ô hiện "/ 2836 học sinh", câu "xếp lại toàn bộ 2836 học sinh". | Nhiều buổi thì đổi đơn vị thành "lượt theo buổi" (hoặc đếm theo học sinh). | đã tái hiện |
| 2 | nên sửa | `api_chi_tieu.py` (`_buoc_ket_qua`, biến `o`) | `o_chua_co` lấy mọi khoá của kết quả không có CLB, kể cả (học sinh, buổi) KHÔNG có nguyện vọng. | cùng bộ 800: `len(o_chua_co) = 2280` ≠ `chua_co = 1916`; vẽ 2280 ô vuông. Bộ TEST một buổi không bị. | lọc theo khoá có trong `prefs`; chặn số ô vẽ. | đã tái hiện |
| 3 | cần bàn | luật đề xuất | Trên bộ 800 (đo "tại chỗ", cùng dữ liệu), 11 bước cho NV1 623 → 623, **21 tốt hơn / 23 kém hơn**. Luật được chọn bằng mô phỏng "năm sau", không bảo đảm có lợi trên chính dữ liệu kỳ này. Màn vẫn mở đầu bằng "Khuyến nghị" và nói số thật nên không sai, nhưng dễ bị đọc là "luôn có lợi". | như trên | (a) giữ nguyên, (b) thêm một dòng khi kém hơn > tốt hơn, (c) nghiên cứu lại luật cho nhiều buổi (mục riêng). | đã tái hiện |
| 4 | nhỏ | `style.css` `.ct1-doan.la-goc` | Chữ trắng "Hiện tại: 64" trên xám `#8A929B`: tương phản ≈ 3,2:1 (< 4,5:1 cho chữ 13 px). Giống bản mẫu. | tính từ mã màu | dùng nền xám đậm hơn hoặc chữ tối. | tính toán |
| 5 | nhỏ | `tests/test_ct1_khuyen_nghi.py` | Đổi ngưỡng `chua_dap >= 1` thành `>= 99` không làm test nào đỏ: bước cân ±1 bù lại nên kết quả bộ TEST không đổi (gần tương đương). | đột biến | thêm một ca mà cân bằng không che được (CLB nhu cầu 1–5 nằm cạnh CLB nhu cầu 0 lớn). | đã tái hiện |
| 6 | nhỏ | giao diện | Nhiều hơn 6 bước: hiện 5 bước + "Xem thêm bước" (kế hoạch ghi "hiện 6") để khung giữ ≤ 7 điều khiển. Đã ghi ở tệp nhánh. | — | giữ | — |

## Điểm tốt
- Không ghi gì, chứng minh bằng băm tệp CSDL (không chỉ băm bảng).
- Ba ca kiểm tay trên 8 học sinh giống hệt ở 5 seed; số hồi quy trên bộ TEST khớp kế hoạch (64→74, 12→8, 15/0).
- Danh sách em đổi chỗ dùng cùng hàm GT2, nên hai màn không thể nói khác nhau.

## Danh sách sửa (chờ Truong duyệt; trạng thái: **Đã sửa** ở CT1-FIX, riêng mục 3 chọn (b) chờ Truong xác nhận)
1. Đơn vị "học sinh" khi nhiều buổi (phát hiện 1).
2. Ô "chưa có CLB" chỉ tính lượt có nguyện vọng và chặn số ô (phát hiện 2).
3. Câu hỏi cần Truong quyết (phát hiện 3): (a) giữ, (b) thêm dòng cảnh báo khi kém hơn > tốt hơn — **em đề xuất (b)**, (c) mục nghiên cứu riêng.
4. Tương phản nhãn "Hiện tại" (phát hiện 4); ca test cân bằng (phát hiện 5).
