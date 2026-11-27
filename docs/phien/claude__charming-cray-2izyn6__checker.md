# Checker — VG1 (nhánh claude/charming-cray-2izyn6)

## REVIEW 1 — `fea0230..6ff0354` (MILESTONE 1 = L1–L2, MILESTONE 2 = L3–L4) — 2026-11-27

**Kết luận: BUGS 2** (cả hai ở L4). L1, L2, L3: PASS.

### Đã chạy
- `tests/test_va_gap_tai_hien.py tests/test_vg1_cong_dang_nhap.py tests/test_vg1_tu_do.py tests/test_dk4_l0b_khoa_dang_nhap.py`: xanh.
- Mọi `tests/test_dk*.py`, `test_fa_*`, `test_vg1_*`, `test_dang_ky*` (trừ `test_vg2_tai_hien.py`, không thuộc VG1, không có UI):
  **2511 đạt, 2 HỎNG** (xem lỗi 2).
- Chromium: `tests/test_giao_dien_vg1.py` + `tests/test_giao_dien_dk8_l2.py`: 14 đạt.
- `kiem_nhanh.py`: 7/7 ĐẠT (gồm trùng khít 3 bộ × 5 seed → bất biến 1 giữ). `ruff check`: sạch.

### Theo lô
| Lô | Kết quả | Ghi chú |
|---|---|---|
| L1 cổng đăng nhập | PASS | NFC + gộp khoảng trắng + casefold; PIN sai dạng không tính lần sai; khoá theo tên chuẩn hoá (5 lần sai với 4 cách viết khác nhau → `dk_tam_khoa`); tên gốc giữ nguyên khi lưu (bất biến 7). |
| L2 phiếu PIN | PASS | `xac_nhan` bắt buộc; chỉ quản trị; nhật ký chỉ ghi số người (`tat_ca hs=0 gv=0`), không có PIN; phiên cũ bị huỷ; 0 người vẫn ra tệp. |
| L3 lùi nhiều bước | PASS | Lùi xoá `han_chot` đích + sau; tiến nhảy qua cổng từng ranh giới (chuẩn bị/GV → `hs_dang_ky`/`xuat` bị chặn `dk_thieu_clb_tu_do`); từ chối CLB có nguyện vọng cần `xac_nhan`, đánh lại `hang` 1..n, giữ `nop_luc`. |
| L4 CLB Tự do | **BUGS 2** | xem dưới. (c) nút khoá / (d) hết hạn / (e) tắt cần `xac_nhan_rui_ro` đều đúng. |

### Lỗi 1 — `api_dang_ky.py:dk_clb_sua_sau_mo` — dời CLB KHÔNG phải Tự do sang buổi chưa có CLB Tự do lọt ràng buộc (BẬT)
Chặn (b) chỉ xét buổi CŨ của CLB Tự do. Dời một CLB Giới hạn/Tuyển chọn sang buổi T3 trống thì T3 có CLB sống mà không có
CLB Tự do, trong khi `bat_buoc_tu_do` đang BẬT; bộ xếp sau đó dừng ở `fa_thieu_clb_tu_do`. Repro (dùng fixture `cd` của
`test_va_gap_tai_hien.py`, hai GV «Cô An», «Thầy Bình»):
```python
td = ok(api.dk_clb_luu(t["Cô An"], _clb(ten="Tự do", loai="Tự do", phong_id=1)))["clb_id"]
gh = ok(api.dk_clb_luu(t["Thầy Bình"], _clb(ten="Cờ vua", phong_id=2, chi_tieu=10)))["clb_id"]
ok(api.dk_chuyen_giai_doan(qt, "duyet")); ok(api.dk_clb_duyet(qt, td, "duyet")); ok(api.dk_clb_duyet(qt, gh, "duyet"))
ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1")); ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
assert ma(api.dk_clb_sua_sau_mo(qt, gh, buoi="T3", xac_nhan=True)) == "dk_thieu_clb_tu_do"
# THỰC TẾ: {'ok': True, 'data': {'anh_huong': 0}} ; dk_cai_dat_doc → buoi_thieu_tu_do == ['T3']
```
Gợi ý sửa: khi đổi buổi, BẬT, `r[4] != TU_DO` và `moi_buoi` không có CLB Tự do sống → `dk_thieu_clb_tu_do` (buoi=moi_buoi);
kiểm cả lúc chưa `xac_nhan` (như chặn hiện có).

### Lỗi 2 — `tests/test_dk3_api.py` — 2 test cũ đỏ sau L4 (handoff L1 ghi «`test_dk3_api` stay green»; CI sẽ đỏ)
- `test_mo_cho_hoc_sinh_can_clb_tu_do_moi_buoi_d2`: dòng 95 mong `dk_con_clb_cho_duyet`, nay nhận `dk_thieu_clb_tu_do`
  (chặn sớm (a) khi đi ngang ranh giới `duyet`).
- `test_toi_da_5_bai_thi_moi_buoi_d44`: `dk_clb_duyet` CLB Tuyển chọn trước khi có CLB Tự do → `dk_thieu_clb_tu_do` (chặn (d)).
Đây là thay đổi hành vi CÓ CHỦ Ý theo D4 (không chạm `match_results`, bất biến 1 vẫn giữ), nên cần sửa test cho khớp D4
(d2: mong `dk_thieu_clb_tu_do` rồi thêm CLB Tự do và mới thấy `dk_con_clb_cho_duyet`; d44: tạo + duyệt CLB «TD» trước vòng
lặp TC), ghi vào CHANGELOG lý do. Repro: `python -m pytest -q tests/test_dk3_api.py`.

### 3 ca biên của checker (bản nháp ở scratchpad, không commit)
1. Dời CLB Giới hạn sang buổi trống khi BẬT → **lỗi 1**.
2. Tên «Đặng  Văn Nam» (hai dấu cách): đăng nhập bằng « đặng văn  NAM » + PIN có dấu cách → đạt; danh sách vẫn hiện tên gốc;
   tạo «ĐẶNG VĂN NAM» → bỏ qua (trùng); 5 lần sai với 4 cách viết → khoá chung. PASS.
3. TẮT rồi BẬT khi chưa có CLB nào → đạt; xuất PIN `tat_ca` với 0 HS/0 GV → tệp rỗng, nhật ký không có PIN; `pham_vi` lạ →
   `dk_pham_vi_la`. PASS. (Thêm: từ chối CLB có nguyện vọng → `hang` [1, 2], `nop_luc` giữ. PASS.)

### Ghi chú (không tính là lỗi)
- `dk_cai_dat_doi(bat_buoc_tu_do="no")` trả `dk_khoi_sai` (thông điệp nói về khối) — mã lỗi lệch nghĩa, nên có mã riêng.
- Xem trước Excel (`_dk_excel_soat_gv` / `_dk_excel_soat_hs`) so trùng theo chữ gốc, không theo `_chuan_ten`: «Nam» và «nam»
  trong cùng tệp đều hiện «mới», lúc nạp một dòng bị bỏ qua. Dữ liệu đúng, chỉ số xem trước lệch.
- `dk_clb_sua_sau_mo(xoa=True)` xoá nguyện vọng nhưng không đánh lại `hang` (có từ trước VG1; khác cách làm của `tu_choi`).

## REVIEW 1b — `fea0230..c9760bf` — 2026-11-27

**Kết luận: BUGS 1.**
- Lỗi 2 (2 test cũ `tests/test_dk3_api.py`): **ĐÃ SỬA** ở c9760bf. Hai test viết lại đúng D4: d2 giờ kiểm cả chặn sớm (a) lẫn
  `dk_con_clb_cho_duyet` sau khi có CLB Tự do, rồi mở được cho học sinh; d44 duyệt CLB «TD» trước. `test_dk3_api.py`: 13 đạt. CHANGELOG có ghi.
- Lỗi 1 (`api_dang_ky.py:dk_clb_sua_sau_mo`, dời CLB không phải Tự do sang buổi chưa có Tự do): **CÒN** (c9760bf không chạm
  `api_dang_ky.py`). Repro như ở REVIEW 1.

## REVIEW 2 — `c9760bf..5087fb9` — 2026-11-27

**Kết luận: NO BUGS.** L1–L4: PASS (cả hai milestone).
- Lỗi 1 **ĐÃ SỬA** (c963a9f): `dk_clb_sua_sau_mo` trả `dk_thieu_clb_tu_do` khi dời CLB không Tự do sang buổi chưa có CLB Tự do
  sống; kiểm đặt TRƯỚC nhánh `can_xac_nhan`. Test mới `test_b_doi_buoi_clb_khong_tu_do_sang_buoi_chua_co_tu_do_bi_chan`.
- Đã chạy: `test_vg1_tu_do.py test_vg1_cong_dang_nhap.py test_va_gap_tai_hien.py test_dk3_api.py test_giao_dien_vg1.py`: 44 đạt;
  `kiem_nhanh.py` 7/7; `ruff` sạch.
- 3 ca biên mới của checker (đạt): (a) chưa `xac_nhan` cũng bị chặn và `buoi` không đổi; (b) TẮT từ trước (giai đoạn GV) thì
  dời sang T3 được; (c) cả 8 ca biên của checker từ REVIEW 1 vẫn đạt.
- Ghi chú (không chặn): dời sang buổi KHÔNG tồn tại («T9») khi BẬT trả `dk_thieu_clb_tu_do` thay vì `dk_clb_buoi_la`
  (kiểm Tự do chạy trước kiểm buổi hợp lệ) — thông báo lệch, dữ liệu không đổi. Nên đưa kiểm buổi lên trước nếu tiện.
