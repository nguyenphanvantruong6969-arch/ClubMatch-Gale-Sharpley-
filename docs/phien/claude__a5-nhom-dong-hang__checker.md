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

## L2 (FIX1) — range 2c224ce..3b0f485 — VERDICT: NO BUGS (whole L2 = NO BUGS)

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| BUG #1 `bulk_set_reserve_group` | ĐÃ SỬA | kiểm `o_nhom_hs_co_gach` đặt TRƯỚC mọi lần ghi. Thử `"a|b"`, `"a |b"`, `"|"`, `"  |  "`, `" | "` → `ok=False`, mã `a5_nhom_hs_co_gach_hang_loat`, DB không đổi (H1=a, H2=b). Giá trị hợp lệ `"c"` và `""` vẫn gán/gỡ bình thường. |
| Mã lỗi mới | ĐẠT | có trong `i18n_errors.py` (vi+en, placeholder `reserve_group`, `person_l`, `slot_l` giống mã anh em, không `{student_id}` thừa); `i18n_loi_khop` ĐẠT; params trả `{reserve_group}` đúng. |
| Test mới (#2) | ĐẠT | đột biến "tắt kiểm bulk" (`if False`) → test ĐỎ (1 failed); đã hoàn tác, `git status` sạch. |
| `phan_quyen.py` `_GIAO_VIEN`, `nhat_ky.py` `_KHONG_GHI` | HỢP LÝ | chỉ thêm `chuan_hoa_o_nhom_clb` và `o_nhom_hs_co_gach` — hai hàm tĩnh thuần (không DB, không ghi), cùng loại với `chuan_hoa_nhom_du_tru` đã có ở đúng hai danh sách này. Không nới quyền cho hàm ghi; `bulk_set_reserve_group` vẫn thuộc nhóm quản trị. Lý do cần: mọi phương thức công khai mới phải được phân loại (test phân quyền / nhật ký). 299 test `phan_quyen/nhat_ky/reserve/du_tru/i18n/bulk` qua. |
| Đường ghi nhãn học sinh còn lại | ĐẠT | `grep "SET reserve_group\|INSERT INTO students"`: `set_student_reserve_group` (chặn), `bulk_set_reserve_group` (chặn), `_ghi_nhom_du_tru` qua hai hàm CSV (chặn ở trước), `UPDATE ... = NULL` (Sổ nhập, gỡ nhóm), hai `INSERT` với nhóm NULL, `api_muc_tieu` chỉ ghi CLB, `rbda_priority_pipeline` L3220 là dữ liệu mô phỏng nội bộ. Không còn đường nào lọt `|` thành `a_b`. |
| `kiem_nhanh --so-seed 20` | ĐẠT | 7/7, 60 ca (3 bộ × 20 seed) trùng khít. |
| Test A5 | ĐẠT | 34 passed. |

Phát hiện mới: không có. Các điểm đã nêu ở vòng 1 vẫn đúng: CSV bỏ qua cả học sinh `|` + cảnh báo (chấp nhận được); xem trước Sổ nhập chưa báo trước và import trả `ok=True` (ghi nhận cho L3/L4 hoặc "Needs Truong", không chặn). Chưa đo: `run_pipeline` đầu-cuối với CLB `a|b`, FA bật, Chromium, toàn bộ bộ test.

Kết luận: L2 NO BUGS sau FIX1.

## L3 — range e71790a..baa8dbd — VERDICT: NO BUGS (1 nhận xét nhỏ)

### Ô của lot
| Ô | Kết quả | Bằng chứng |
|---|---|---|
| `ws_v_tiers`: tách `|`, khoá như backend, lỗi trùng / phần rỗng | ĐẠT | `wsKhoaNhom` = đ→d, NFD bỏ dấu, lower-case, `split(/\s+/)` (NBSP, dấu cách kép) — khớp `xay_tier_rank` / `cau_hinh_ws`. Chỉ khác `toLowerCase` vs `casefold` (chữ như `ß`) — không liên quan nhãn tiếng Việt. |
| Chỉ báo lỗi khi CÓ dòng `|` (đường cũ không đổi) | ĐẠT | `wsLoiGachNhom` trả `""` ngay khi không dòng nào có `|`; kiểm cũ `new Set(tiers).size` giữ nguyên, kiểm mới chỉ ở nhánh `else`. Trình duyệt: `Khối 12 / Khối 11` → qua, hiển thị `Khối 12 › Khối 11`; `a` + `A` (không `|`) → qua như trước; `x / x` → "hai dòng trùng nhau" như cũ. |
| `rvTiers` hiện `a = b › c` | ĐẠT | `wsHienThiTiers`; đo trong Chromium: `" A | b \nc"` → `A = b › c`. |
| Gợi ý (hint) `a5_` + i18n vi/en | ĐẠT | 5 khoá, vi và en đủ; `i18n_khoa` ĐẠT; `chu_cam` ĐẠT. Hint: dưới ô tiers wizard (ghép vào `ws_r_tiers_chi_strict`), dưới ô nhóm CLB (`aria-describedby`), dưới ô tiers `gt2TcTiers`. Câu CLB nêu rõ "nhóm điểm cao hơn có thể lấy hết suất". |
| Chromium test `tests/test_a5_giao_dien.py` | ĐẠT | 10 passed, chạy 2 lần liên tiếp (2,45 s và 2,54 s) — không chập chờn; một fixture trang dùng chung (đúng yêu cầu lot). |
| Sai lệch coder: không có tóm tắt tiers chỉ-đọc trong `js/15_tieu_chi.js` nên thêm hint dưới textarea | CHẤP NHẬN | `15_tieu_chi.js` chỉ có textarea sửa được, `gt2TcLuatDangChon` gửi nguyên `a|b` lên `update_workspace_config`, `taiTieuChi` nạp lại `join("\n")` giữ `|`; kiểm tra ở đó do backend (`cau_hinh_ws`, đã duyệt L2) và lỗi hiện qua `feedbackErrors`. Ô `a = b` chỉ-đọc không tồn tại nên không có gì để sửa. |

### Ca biên tôi tự chạy trong Chromium (script ở thư mục tạm, không commit) — 10/10 đúng
`"a||b"`, `"x|  |y"`, `"|"` → lỗi "phần trống"; `" A | a "`, `"a|b\nb"`, `"a|b\nB"`, `"Khối 12|x\nkhoi 12"` (NBSP thật), `"Đ|x\nd"` → lỗi "MỘT hạng"; hợp lệ: `" A | b \nc"` → `A = b › c`; `"a|b\nchinh_sach|chinh sach"` → `a = b › chinh_sach = chinh sach` (nhãn có `_` ≠ nhãn có dấu cách, đúng như backend); `"a\nA"` (không `|`) → qua `a › A`. Không có `pageerror`.

### XSS / thoát chữ
Tên nhóm đi vào `wsEl("td", {text})` (`textContent`). Test của coder: `<img src=x onerror=window.__xss=1>|b` → hiện đúng chữ `<img …> = b`, `window.__xss` không đặt, không lỗi JS. ĐẠT. Hint là khoá i18n cố định, không chứa dữ liệu người dùng.

### soat-ma bốn tầng (trên diff này)
- Tầng 1/2: không đổi (diff không chạm `.py` sản phẩm); `kiem_nhanh --so-seed 20` 7/7, 60 ca trùng khít.
- Tầng 3 (UI, ba vai không áp dụng đầy đủ — chỉ vai quản trị/wizard bị chạm): đã đo như trên; không thêm lời gọi `window.pywebview.api.*` mới; không thêm `localStorage`; 32 test giao diện workspace hiện có (`test_ws_giao_dien`, `test_ws_luat_giao_dien`, `test_ws_nhan_giao_dien`) qua.
- Tầng 4: ruff sạch, i18n khớp, CHANGELOG/TIEN_DO/CLAUDE_CHI_TIET cập nhật.

### Phát hiện
| # | Mức | Tệp | Vấn đề | Đề xuất |
|---|---|---|---|---|
| 1 | nhỏ | index.html (hint `a5_gt2_tc_nhom_goi_y`) | Hint thứ hai dưới `gt2TcTiers` không có `id` và không nằm trong `aria-describedby` của textarea (chỉ hint cũ `gt2TcTiersGoiY` có), nên trình đọc màn hình không đọc nó. | Thêm id và nối vào `aria-describedby` (`"gt2TcTiersGoiY gt2TcTiersGoiY2"`). Không chặn. |

### Chưa đo
Đổi ngôn ngữ giữa chừng trên hint mới (chỉ kiểm tra khoá vi/en có đủ), bấm đúp, kiosk học sinh (không chạm), toàn bộ bộ test.

### Kết luận L3
NO BUGS; một nhận xét nhỏ (#1) không chặn.

## L4 — range 027407d..6a561f0 — VERDICT: NO BUGS (2 nhận xét nhỏ về chữ trong hướng dẫn)

### Độ chính xác mục 18 `HUONG_DAN_SU_DUNG.md` so với mã thật
| Câu trong hướng dẫn | Kết quả | Bằng chứng |
|---|---|---|
| Mỗi học sinh MỘT nhãn; không `|` thì kết quả y hệt | ĐÚNG | L1: nhánh `==` cũ giữ nguyên; `trung_khit` 60 ca |
| Cách 1: `a|b` cùng một hạng, trước hạng sau và trước em không nhóm; trong hạng: đã chấm điểm trước, điểm giảm dần, bốc thăm | ĐÚNG | `xay_tier_rank` + `uu_tien_theo_nhom`; test L1 ra `["s3","s2","s6","s1","s4","s5"]` |
| Xem lại hiện `Khối 12 = Học sinh giỏi › Khối 11` | ĐÚNG | `wsHienThiTiers`, đo ở L3 |
| Nhóm ở hai hạng / `a||b` bị chặn "ở màn hình và ở backend" | ĐÚNG | `ws_v_tiers` + `cau_hinh_ws`; thẻ Tiêu chí chỉ báo từ backend (nói "màn hình" vẫn đúng vì lỗi hiện ra) |
| Cách 2: `a|b` đủ điều kiện nếu nhãn thuộc tập; nhãn khác thì không; cảnh báo "nhóm điểm cao hơn có thể lấy hết suất dự trữ"; KHÔNG chia đều | ĐÚNG, TRUNG THỰC | `default_reserve_eligible_fn` pooled (`club_choice_function` không đổi); khung lưu ý đúng chữ lead yêu cầu |
| Xếp nghiêm ngặt thì bỏ qua suất dự trữ | ĐÚNG | `bo_qua_du_tru = True` khi `tier_rank` khác None (`rbda_priority_pipeline.py` ~L719) |
| Chuẩn hoá `Chính sách|Khối 10` → `chinh_sach|khoi_10`, sắp xếp, bỏ trùng | ĐÚNG | test `chuan_hoa_o_nhom_clb` L2 |
| Báo cáo suất dự trữ + cảnh báo dữ liệu hiểu `a|b` | ĐÚNG | L2: `instr`, `NOT EXISTS` |
| Học sinh `|`: lỗi `a5_nhom_hs_co_gach`, CSV bỏ qua + cảnh báo, gán tay / hàng loạt bị từ chối | ĐÚNG | L2 + FIX1 (mã hàng loạt là `a5_nhom_hs_co_gach_hang_loat` — hướng dẫn nêu một mã, không sai về ý) |
| Giới hạn: chỉ gộp, không chia đều; huy chương / chia loại không đổi; ổn định đo trên 250 ca mô phỏng | ĐÚNG | không có `reserve_group` trong mã huy chương / chia loại (grep); test L1 250 ca seed cố định |
| Không bịa nội dung đề cương, không kết luận cho báo cáo | ĐẠT | mục chỉ hướng dẫn vận hành; ghi "dữ liệu MÔ PHỎNG, không phải khảo sát thật" |

### Phát hiện (nhỏ, không chặn)
| # | Mức | Tệp:chỗ | Vấn đề | Đề xuất |
|---|---|---|---|---|
| 1 | nhỏ | `HUONG_DAN_SU_DUNG.md` mục 18, dòng về thẻ mục tiêu | Ghi tên thẻ là "Dành cho một nhóm", nhưng thẻ thật tên "Dành chỗ cho một nhóm" (`mt1_the_danh_cho_tt`). Chữ "Tuỳ chỉnh" là trạng thái nội bộ `tuy_chinh` của `muc_tieu.py`; tôi không tìm thấy thẻ nào hiện đúng chữ đó trong i18n. | Sửa thành "Dành chỗ cho một nhóm", và nói "không còn tương ứng thẻ nào (tuỳ chỉnh)" hoặc bỏ cụm "Tuỳ chỉnh". |
| 2 | nhỏ | cùng mục, dòng "Dùng cả hai cách … không hợp lệ" | Thực tế mã không báo lỗi: xếp nghiêm ngặt chỉ **bỏ qua** suất dự trữ (`bo_qua_du_tru`). Câu sau của chính hướng dẫn nói đúng, nhưng "không hợp lệ" nghe như bị chặn. | Đổi thành "không có tác dụng: xếp nghiêm ngặt thì bỏ qua suất dự trữ". |

### Các điểm khác lead nhờ soi
- **Sổ đăng ký A5:** ghi chú tiến độ trung thực: nêu phần nhỏ đã làm, "Chưa làm: bảng thuộc tính nhiều giá trị, bộ lọc cứng, chia đều suất", ngoại lệ bất biến 7 do Truong duyệt 22/11/2026. ĐẠT.
- **CHANGELOG / TIEN_DO:** khớp (L4 nêu mục 18, ghi chú sổ đăng ký, sửa `aria-describedby`, "112 ca tài liệu/giao diện đạt" — tôi chạy lại 66 ca tài liệu + 45 ca A5, đều xanh). ĐẠT.
- **`aria-describedby` (nhận xét L3 #1):** `index.html` nay có `id="gt2TcTiersGoiY2"` và `aria-describedby="gt2TcTiersGoiY gt2TcTiersGoiY2"`; test mới trong `test_a5_giao_dien.py` kiểm đúng hai id và cả hai phần tử tồn tại. ĐẠT.
- **Test tài liệu:** `test_a13_12_tai_lieu`, `test_fa_m6_tai_lieu`, `test_gt3_tai_lieu`, `test_tai_lieu_dong_bo`, `test_tai_lieu_du_lieu`, `test_vi_du_huong_dan` = 66 passed.
- **Toàn bộ test A5 cùng một lần** (`test_a5_nhom_dong_hang.py` + `_backend.py` + `test_a5_giao_dien.py`, có Chromium): 45 passed, 5,7 s.
- **`kiem_nhanh --so-seed 20`:** 7/7, 60 ca trùng khít. `git status` sạch.
- Chưa đo: toàn bộ bộ test, `run_pipeline` đầu-cuối với CLB `a|b`, FA bật, build Windows (CI gate lo).

### Kết luận L4
NO BUGS. Hai nhận xét chữ (#1, #2) nên sửa trong lượt tiếp nếu tiện, không chặn.

## CIFIX1 — range 1e07297..75cf192 — VERDICT: BUG (1) → `FIX CIFIX1`

### Đã đạt
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| Không test nào bị yếu đi | ĐẠT | `test_ws_nhan.py`: chỉ thêm 2 mã vào `MA_MOI_SAU_ANH_CHUP` (đúng cơ chế của chính tệp: "Chỉ THÊM mã", assert vẫn bắt mã lạ); `test_a5_giao_dien.py`: chỉ đổi chữ mong đợi `MỘT`→`một` cho khớp văn bản mới. Không xoá/ nới assert nào. |
| `a5_` đã chuyển lên trước khối MT1 | ĐẠT | `i18n_errors.py`: `=== A5 ===` ở dòng 1622–1631, trước `=== MT1 (L2) ===` (1632); `i18n_loi_khop` ĐẠT (regenerate khớp). |
| Bốn test CI đỏ | ĐẠT | `test_mt1_uoc_tinh`, `test_mt1_api`, `test_van_phong_tu_nhien`, `test_ws_nhan` + `test_i18n_sync` + `test_a5_*` + `test_gt3_phan_quyen`: 204 passed. |
| Chữ in hoa nhấn mạnh trong mã lỗi / `i18n.js` / HUONG_DAN | ĐẠT một phần | quét bằng script: `i18n_errors.py` mã `a5_*` và khoá `ws_v_tiers*`/`a5_*` trong `i18n.js` không còn từ in hoa. Mục 18 `HUONG_DAN_SU_DUNG.md`: còn "xếp CỨNG" (nhỏ, tệp này không bị test văn phong quét; xem #2). |
| `kiem_nhanh --so-seed 20` | ĐẠT | 7/7, 60 ca trùng khít. |

### Phát hiện
| # | Mức | Tệp | Vấn đề | Đường xảy ra | Đề xuất |
|---|---|---|---|---|---|
| 1 | **cần sửa (làm CI đỏ)** | `index.html` dòng ~1002 (`#clubFormReserveGroupGoiY`) | CIFIX1 đổi `MỘT`→`một` trong `i18n.js` (`a5_club_nhom_goi_y`) nhưng KHÔNG đổi chữ dự phòng cùng câu trong `index.html` ("Mỗi học sinh chỉ có MỘT nhóm."). | `pytest tests/test_t3_l1_chu_du_phong.py::test_chu_du_phong_trong_index_html_khop_catalog` → FAIL: `a5_club_nhom_goi_y` lệch catalog. Tôi chạy nhóm 61 tệp test quét `MESSAGES`/`i18n.js`/`HUONG_DAN`/`phan_quyen`/`SO_DANG_KY`/`CHANGELOG` (không Chromium nặng): chỉ đúng 1 test này đỏ (còn lại xanh, một số skip đã biết). Nên CI shard chứa test này sẽ đỏ tiếp. | Sửa `index.html`: "…Mỗi học sinh chỉ có một nhóm." (khớp từng chữ với `i18n.js` vi). Chạy lại `test_t3_l1_chu_du_phong`. Không đổi test. |
| 2 | nhỏ | `HUONG_DAN_SU_DUNG.md` §18 | Còn "xếp CỨNG theo nhóm" (in hoa nhấn mạnh). Không có test bắt, chỉ nhất quán văn phong. | Đổi "cứng" thường nếu tiện. |

### Săn thêm test toàn bộ bộ có thể vỡ do A5
Đã chạy: mọi tệp trong `tests/` có tham chiếu `MESSAGES`, `i18n_errors`, `i18n.js`, `i18n_loi`, `HUONG_DAN_SU_DUNG`, `phan_quyen`, `_KHONG_GHI`, `_GIAO_VIEN`, `SO_DANG_KY`, `CLAUDE_CHI_TIET`, `TIEN_DO`, `CHANGELOG` (61 tệp, ~3,7 phút, có Chromium). Kết quả: 1 FAIL (#1), phần còn lại pass. KHÔNG chạy: ~25 tệp `test_giao_dien_*` nặng (a13_8, chay, diem, gt, ux, wharton, xoa, upload, tran, thu_gon, bang, ux2, a14, t3) và `test_a13_11_stress`, `test_a13_12_browser_host` — chưa đo. Test phân quyền/nhật ký (`test_gt3_phan_quyen`, `test_gt3_nhat_ky`, `test_ws_registry`…) nằm trong nhóm đã chạy.

### Kết luận CIFIX1
Cần `FIX CIFIX1` (vòng 1): sửa chữ dự phòng ở `index.html` (#1). Phần còn lại ĐẠT.

## CIFIX1b — range 75cf192..321ad2b — VERDICT: NO BUGS
- Bug #1 và nhỏ #2 đã sửa: `index.html` hint `a5_club_nhom_goi_y` đã là "một"; `HUONG_DAN_SU_DUNG.md` §18 "xếp cứng". Diff chỉ chữ (index.html, HUONG_DAN, CHANGELOG), không đổi test.
- Chữ dự phòng vi trong `index.html` = `i18n.js` vi cho cả hai id A5 (`a5_club_nhom_goi_y`, `a5_gt2_tc_nhom_goi_y`); chữ en không có dự phòng trong HTML nên không có gì để so. 55 passed: `test_t3_l1_chu_du_phong`, `test_i18n_sync`, `test_a5_*` (có Chromium); `git status` sạch.
- Không chạy lại `kiem_nhanh` (diff không chạm `.py`); chưa chạy lại nhóm 25 tệp `test_giao_dien_*` nặng.
