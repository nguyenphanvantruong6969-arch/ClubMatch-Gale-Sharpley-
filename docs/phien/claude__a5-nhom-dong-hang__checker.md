# A5 checker report (branch claude/a5-nhom-dong-hang)

> Checker session: Sonnet. Chỉ báo cáo; không sửa mã sản phẩm hay test. Dữ liệu là MÔ PHỎNG.

## L1 — range 6d29672..68341c9 (code commit 92da732) — VERDICT: NO BUGS (1 nhận xét "nhỏ")

### Phạm vi / hàm cũ bị chạm
`tach_nhom_clb` (mới), `xay_tier_rank`, `default_reserve_eligible_fn`. `compute_club_priority`, `club_choice_function`,
`uu_tien_theo_nhom`, `fa_daa.py` KHÔNG đổi (diff chỉ 3 hunk trong `rbda_priority_pipeline.py`).

### Ô của lot
| Ô | Kết quả | Bằng chứng |
|---|---|---|
| Helper `tach_nhom_clb` thuần, không chuẩn hoá | ĐẠT | `"a||b"`→(a,b); `" A | a "`→(A,a); `None`/`""`/`"|"`→() |
| `default_reserve_eligible_fn`: không `|` giữ nhánh `==` cũ | ĐẠT | nhánh `return nhom_hs == club_group` giữ nguyên; có `|` → `in` tập |
| `xay_tier_rank`: mỗi phần cùng chỉ số mục | ĐẠT | `["a|b","c"]`→a,b=0,c=1; mục không `|` đi đúng đường cũ |
| Test file L1 (7 ca, ≥200 ngẫu nhiên) | ĐẠT | 7 passed; 250 ca seed cố định substitutability + aggregate demand |
| Invariant 1: `kiem_nhanh --so-seed 20` | ĐẠT | tôi chạy lại: 7/7, "60 ca (3 bộ × 20 seed) trùng khít" so với origin/main |

### Bất biến
1 ĐẠT (trên). 2 ĐẠT (không chạm `compute_club_priority`; nhãn là thuộc tính người). 5, 6 không áp dụng cho L1 (không đổi
pipeline/API/i18n). 7 không áp dụng cho L1 (chưa đổi dữ liệu/CSV). 8 ĐẠT (test ngẫu nhiên ở trên; tôi không thay đổi hàm chọn).
Không có `LIKE` trên nhãn. Nhánh đơn nhãn giữ code cũ.

### Ca biên tôi tự chạy (đều đúng)
- tiers `["a||b","c"]` → s1,s2 = 0, c = 1; `[" A | a ","b"]` → a=0, b=1 (nhãn trùng a/A trong mục không gây lỗi ở lõi).
- tiers `["a|b","b"]` → b giữ hạng 0 (`setdefault`, mục sau không ghi đè). Việc báo lỗi nhãn ở hai hạng thuộc L2/L3 (`cau_hinh_ws`, `ws_v_tiers`).
- NBSP trong mục tier: `"a| Khối  12"` khớp nhãn "Khối 12".
- Nhãn `chinh_sach` KHÔNG khớp mục `chinh|sach` (có test).
- Ô CLB `"a|b"`, `"a||"`, `"|"`, `" |"`, `"a|b|"`, NBSP quanh nhãn → đúng; học sinh không nhãn / không có trong dict → False.
- CLB `a|b` với reserve 0 → `club_choice_function` không dùng dự trữ (kết quả cơ sở).
- DB rỗng / `{}` → không lỗi.
- FA on: không chạm `fa_daa.py` (chưa chạy FA; ngoài phạm vi L1).

### Test yếu (gây hỏng tạm, đã hoàn tác, `git status` sạch)
| Đột biến | Test L1 |
|---|---|
| `in` → `not in` trong reserve | ĐỎ (2 fail) |
| bỏ `.strip()` trong `tach_nhom_clb` | ĐỎ |
| reserve chỉ nhãn đầu | ĐỎ |
| mọi phần của mục tier nhận hạng 0 thay vì chỉ số mục | **KHÔNG đỏ** |

### Phát hiện
| # | Mức | Tệp | Vấn đề | Đề xuất |
|---|---|---|---|---|
| 1 | nhỏ | tests/test_a5_nhom_dong_hang.py | Mọi test tier đặt mục `a|b` ở chỉ số 0 (hoặc duy nhất) nên đột biến "gán 0 cho mọi phần" sống. Chưa có ca `["x","a|b","c"]` kiểm a,b = 1 và c = 2. | Thêm một ca khi sửa vòng sau / trong L2 (không chặn L1). Chắc chắn: đã tái hiện. |

### soat-ma bốn tầng (coder nói chưa đi đủ; tôi soát trên diff này)
- Tầng 1 (lõi): ĐẠT — mục 1 (không chạm khoá ưu tiên), 2, 3 (`trung_khit` 60 ca), 4 (250 ca ngẫu nhiên), 6 (biên ở trên). Mục 5/7 (`verify_stability`, STB) không bị chạm bởi diff.
- Tầng 2 (backend): không áp dụng cho L1 (không đổi API/ghi DB/i18n/schema); sẽ soát từ L2.
- Tầng 3 (UI): không áp dụng cho L1 (không đổi JS/HTML).
- Tầng 4: ruff sạch; i18n/chu_cam/ma_loi_js/i18n_loi_khop OK; test chủ đề + `-k "tier or reserve or priority or endogen"` = 80 passed, 1 skipped; CHANGELOG, TIEN_DO, CLAUDE_CHI_TIET (379→380 tệp test) khớp. `tach_nhom_clb` có 2 chỗ gọi trong mã sản phẩm (chưa dùng ở lớp backend — dự kiến L2). Kiểm thử đột biến: bảng trên.
- Chưa đo: toàn bộ bộ test (không yêu cầu), test giao diện Chromium (L1 không chạm).

### Kết luận L1
NO BUGS. Một nhận xét "nhỏ" (#1) không chặn.

## L2 — range fcd1cd9..2c224ce — VERDICT: BUGS (1 cần sửa, 1 nhỏ) → `FIX L2`

### Ô của lot
| Ô | Kết quả | Bằng chứng |
|---|---|---|
| `chuan_hoa_o_nhom_clb` (không `|` = đúng `chuan_hoa_nhom_du_tru`) | ĐẠT | `"B|a| a |"`→`a|b`; `"|"`→`""`; test so sánh 5 ô không `|` |
| Ghi ô CLB: `create_or_update_club`, `import_clubs_csv` (Sổ nhập đi qua đây) | ĐẠT | `c1 "a|b"`, `c2 "b|a|"` đều lưu `a|b` |
| Học sinh `|` bị từ chối, không ghi: `set_student_reserve_group` | ĐẠT | `ok=False`, `a5_nhom_hs_co_gach`, không đổi DB |
| Học sinh `|` ở CSV/Sổ nhập (2 hàm CSV) | ĐẠT (xem "Phán xét") | HS4 `a|b` không được tạo, cảnh báo; không có `a_b` |
| Học sinh `|` ở **`bulk_set_reserve_group`** | **KHÔNG ĐẠT** | xem phát hiện #1 |
| `csv_reserve_group_unknown`, `list_reserve_groups_in_use` | ĐẠT | gợi ý `['a','b','c']`, không có `a|b`; cảnh báo im lặng với `a` khi có CLB `a|b` |
| `cau_hinh_ws` tiers | ĐẠT | `["a|b","b"]`, `["A|a"]`, `["a","a|b"]`, NBSP `["a| Khối 12","khoi  12"]` → lỗi; `["a||b"]`, `["a|"]` → lỗi phần rỗng; `["a|b","c"]`, `["chinh|sach","chinh_sach"]` OK; tiers không `|` giữ nguyên |
| Báo cáo SQL dùng `instr`, không `LIKE` | ĐẠT | `get_suat_du_tru`: c1 `a|b` đếm 2 (a,b), CLB nhãn `a_b` đếm 1 (không lẫn); sức khoẻ dữ liệu (api.py) cũng `instr` + `NOT EXISTS`; `git grep LIKE` không dính nhãn |
| Danh sách `git grep reserve_group` trong `__coder.md` | ĐẠT một phần | thiếu `bulk_set_reserve_group` (đường học sinh duy nhất không được liệt kê) |
| Khoá mục tiêu `muc_tieu` | ĐẠT | CLB `a|b` ≠ khoá đơn → `clb_ghi_de`/`tuy_chinh` (có test) |
| CLB `a|b` reserve 0 | ĐẠT | lưu và đếm bình thường, không lỗi |
| DB rỗng | ĐẠT | `list_reserve_groups_in_use` → `[]`, ok |

### Bất biến
1: `kiem_nhanh --so-seed 20` tôi chạy lại: 7/7, 60 ca trùng khít. 2, 8: không chạm khoá ưu tiên / hàm chọn. 4, 5: không đổi pipeline hay `run_history`. 6: `a5_nhom_hs_co_gach` có trong `i18n_errors.py`, `i18n_loi_khop` ĐẠT (chạy lại `tao_i18n_js.py` không đổi gì). 7: chỉ ngoại lệ `a|b` đã duyệt; không đổi cột/schema. SQL tham số hoá.

### Phát hiện
| # | Mức | Tệp / hàm | Vấn đề | Đường xảy ra | Đề xuất | Chắc chắn? |
|---|---|---|---|---|---|---|
| 1 | **cần sửa (chặn acceptance 5)** | `api_quan_ly.py` `bulk_set_reserve_group` | Đường học sinh còn lại không kiểm `|`: gọi `chuan_hoa_nhom_du_tru` nên `a|b` bị lặng lẽ thành `a_b` — chính lỗi acceptance 5 cấm, và lot ghi rõ "student/bulk paths". | `api.bulk_set_reserve_group(["HS1","HS2"], "a|b")` → `ok=True`, DB: HS1=`a_b`, HS2=`a_b` (tái hiện bằng script, đầu ra: `bulk a|b: True [('HS1','a_b'),('HS2','a_b')]`). Sau đó cả HS mất diện dự trữ của CLB `a|b` và nhãn `a_b` hiện trong gợi ý nhóm. | Thêm ở đầu hàm: `if self.o_nhom_hs_co_gach(reserve_group): return _fail(err("a5_nhom_hs_co_gach", student_id="", reserve_group=reserve_group))` (hoặc tham số tương đương cho `student_id`, kiểm i18n có placeholder), + test: lỗi và DB không đổi. Gọi `chuan_hoa_nhom_du_tru` chỉ sau kiểm. | đã tái hiện |
| 2 | nhỏ | `tests/…_backend.py` | Đột biến "bỏ kiểm `o_nhom_hs_co_gach`" ở `bulk_set_reserve_group` sống vì không có test (cùng gốc #1). | Như #1. | Test của #1 sẽ khoá. | suy luận |

### Phán xét: CSV bỏ qua cả học sinh + cảnh báo `a5_nhom_hs_co_gach`
Chấp nhận được. Lý do: đúng quy ước sẵn có của hai hàm nạp (dòng lỗi → `row_errors`/`n_skipped`, nạp phần còn lại, trả cảnh báo kèm `student_id` và nhãn); không lưu `a_b`, không tạo học sinh dở dang; giáo viên thấy cảnh báo cụ thể. Phương án "từ chối cả tệp" khắt hơn nhưng lệch quy ước, và lot không bắt. Một điểm yếu để lead biết (không chặn): cảnh báo xuất hiện sau khi nạp, **xem trước Sổ nhập (`xem_truoc_so_nhap`) chưa báo trước** — nếu muốn, ghi vào L3/L4 hoặc "Needs Truong". Mã trả về `ok=True` dù có học sinh bị bỏ.

### soat-ma bốn tầng (tôi soát trên diff này)
- Tầng 1 lõi: không đổi trong L2 (diff không chạm `rbda_priority_pipeline.py`); `trung_khit` 60 ca ĐẠT.
- Tầng 2 backend: ĐẠT trừ #1 (mục 7 "ô bẩn": `|`, NBSP, `a||b`, `|` đơn, `a_b` hợp lệ đều xử lý; mục 5 "mọi đường đổi dữ liệu": #1 là đường bị bỏ sót). Mục 1/2/4/9/10: không đổi trong L2.
- Tầng 3 UI: không áp dụng cho L2 (không đổi JS/HTML; `i18n_loi.js` chỉ sinh lại).
- Tầng 4: ruff sạch, `chu_cam`/`ma_loi_js`/`i18n_*` ĐẠT; 33 test A5 + 235 test liên quan (`reserve/du_tru/muc_tieu/cau_hinh_ws/tiers/suc_khoe/i18n`) qua, 1 bị bỏ qua (đã biết); CHANGELOG/TIEN_DO/CLAUDE_CHI_TIET có cập nhật. Mutation của coder: 6 đột biến; tôi bổ sung #2 (sống).
- **Chưa đo:** pipeline chạy đầu-cuối với CLB `a|b` (`run_pipeline` đòi hồ sơ Wharton trong DB thử của tôi nên không dựng được nhanh); FA bật (không đổi code `fa_daa.py`, không chạy); test giao diện Chromium; toàn bộ bộ test.

### Kết luận L2
Cần `FIX L2`: sửa #1 (+ test #2). Còn lại ĐẠT. Vòng 1/2.
