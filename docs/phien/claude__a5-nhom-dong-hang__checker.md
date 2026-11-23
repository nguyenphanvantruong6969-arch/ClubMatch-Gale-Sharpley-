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
