# DKL checker report (Sonnet) — head 348f6d4, branch claude/loving-babbage-8yqo7d, 2026-11-26

**VERDICT: FIX (not PASS).** Reasons: (a) CI of head 348f6d4 = run 45719263842 still `queued`, so no Linux+Windows result; (b) 3 confirmed defects on the
admin "Xuất" screen; (c) TIEN_DO has no DKL-H / DKL-I rows. Everything below was run locally (Python 3.11, Chromium): the 5 DKL test files = **25 passed**;
`ruff check .` clean; `kiem_nhanh.py` 6/7 (`trung_khit` cannot run here: no `origin/main` in this clone, environment not code — CI must cover it).
No source change outside the DKL files: `rbda_priority_pipeline.py`, `dang_ky_schema.py`, `so_nhap.py`, `dk2_so_nhap.py`, `fa_daa.py`, `api.py` untouched since 42b93af
→ no schema / CSV / algorithm change; `compute_club_priority` unchanged (invariant 2 intact; the DKL code never reads rank for priority).

## Row by row (test = file `tests/test_giao_dien_dkl_*.py` unless noted; all PASS locally)
| Row | Result | Test |
|---|---|---|
| S1 Forms link after submit | PASS (link only for ticked Tuyển chọn; the test has one club so "unticked → no link" is not asserted: weak) | hoc_sinh `test_2_gui_roi_bien_nhan_co_link_bai_thi…` |
| S2 "Dưới sàn" chip + rule line | PASS | hoc_sinh `test_2` ("thì không xét", "Không làm bài, hoặc dưới mốc điểm") |
| S3 card info, no demand (D26) | PASS | hoc_sinh `test_1_the_clb_co_mo_ta…khong_lo_so_dong` |
| S4 deadline + expired message | PASS | hoc_sinh `test_3`, `test_4_het_han…` |
| S5 empty submit warning | PASS | hoc_sinh `test_3_nop_rong…` |
| S6 "Đã gửi lúc" + "Xong, thoát" | PASS | hoc_sinh `test_2` |
| S7 separate steps | PASS (DK4-UI; exercised by `test_2` steps, no dedicated test) | — |
| S8 teacher edit/delete own pending club | PASS | giao_vien `test_2`, `test_3` |
| S9 per-step errors, https, rooms free per buổi | PASS | giao_vien `test_1`, `test_2`; `test_dkl_cai_dat.py::test_clb_xoa_va_phong_trong_theo_buoi` |
| A1 Đóng ngay / Gia hạn / deadline | PASS | quan_tri `test_2` |
| A2 score entry (comma+dot, Dưới sàn, paste, Chốt điểm) | PASS: "8,5" → Đạt, "4" → Dưới sàn, paste "9,5" saved = 9.5. **Dot not asserted in UI test** (FIX-minor: add "8.5") | quan_tri `test_4`; `test_dkl_cai_dat.py::test_bang_diem_xem_truoc_…` |
| A3 PIN slips | PASS: only from the just-created/reset list (`hienPin`); DOM has no `pin_bam`/`pin_muoi` (real column names, verified in `api_dang_ky.py`); `dk_hs_danh_sach` returns no hash | quan_tri `test_1` |
| A4 replace whole list + lock | PASS | quan_tri `test_1` |
| A5 delete room | PASS | quan_tri `test_1` |
| A6 approve with quota/room, edit after open | PASS | quan_tri `test_2`, `test_7` |
| A7 demand per club (admin only) + not-registered | PASS; students never see demand (S3 test) | quan_tri `test_3` |
| A8 phase-1 checklist with reasons | PASS | quan_tri `test_1` |
| A9 Cài đặt tab | PASS | quan_tri `test_5`; `test_cai_dat_doi_*` |
| A10 export preview + version counter | PASS for data; **FIX defect 3** (collapsed) | quan_tri `test_6`; `test_bang_diem_xem_truoc_va_phien_ban_xuat` |
| A11 backup now | PASS (restore not built = Truong decision A, 2026-11-26) | `test_sao_luu_tao_tep_va_ghi_gio` |
| A12 2-min lock text + timeout message | PASS | quan_tri `test_8` |
| G1 identity "Đúng là em chứ?" | PASS | hoc_sinh `test_3b` |
| G2 admin lock 120 s = server 120 s | PASS | quan_tri `test_8` |
| G3 timeout message test | PASS | quan_tri `test_8` |
| G4 ≤7 cards + "Xem thêm (N)" | PASS | hoc_sinh `test_3c` |
| H limit text per buổi | PASS vs Truong's request. Note: v8 has no such sentence, so it is a new text, not a v8 copy | hoc_sinh `test_3d_gioi_han_nguyen_vong…` |
| I hint to open Đăng ký CLB when no data | PASS (shows only in `nap_so`; click → "Thiết lập lần đầu"; hidden when data exists) | `test_giao_dien_dkl_loi_dan_cong.py` (2 cases) |

## Cross-checks
- i18n: `i18n_errors.py` not changed in 42b93af..HEAD; `kiem_nhanh` `i18n_loi_khop`, `i18n_khoa` PASS.
- `nkhd_` labels: all 7 new `dk_*` functions (`dk_phong_danh_sach`, `dk_clb_xoa`, `dk_diem_danh_sach`, `dk_cai_dat_doc`, `dk_cai_dat_doi`, `dk_xuat_xem_truoc`, `dk_sao_luu`) have vi + en labels in `i18n.js`.
- CHANGELOG: rows for DKL, DKL-G, DKL-H, DKL-I present. **TIEN_DO: rows for DKL and DKL-G only; DKL-H and DKL-I MISSING → FIX.**
- soat-ma: coder ran tier 1 only (`kiem_nhanh`); tiers 2–4 were not run by the coder. Not run by me beyond the checks above.
- Not verified (cannot here): pywebview/WebView2, `window.print()`, `confirm()`; full suite; `trung_khit` vs main.

## Three known defects — all CONFIRMED
Repro: script `/tmp/claude-0/-home-user-ClubMatch-Gale-Sharpley-/53f1bac6-aa5e-5a5d-aad1-6f86fd6d1447/scratchpad/test_repro.py`
(copy into `tests/`, uses `test_dk4_chot_va_xep._dang_ky_va_cham`; 3 SIMULATED students H1 H2 H3, H3 sends no preference), run `dk_chot_va_xep(qt, 7)`.

**1. "NVNone: N"** — CONFIRMED. Output: `theo_nguyen_vong: {"None": 1, "1": 2}`; `match_results` row `('H3','thu_2','CLB001','general', rank NULL)`.
- WHY: H3 submitted no preferences (`preferences` has no row for H3), so the allocator placed H3 in the Tự do club by fallback (mode `fa_daa` is auto-enabled by `dk_chot_va_xep`). A fallback placement has `rank_in_student_pref = NULL` by design — NOT an algorithm bug. `api_bao_cao.py` (SG-3 block) already treats exactly this case as "xếp bằng phương án dự phòng, đếm riêng, không tính là nguyện vọng nào".
- CAUSE: `_dk_tom_tat_xep` (`dang_ky_sang_xep.py`) does `hang[str(h)]` → "None"; `bangKetQua` (`js/dang_ky_quan_tri.js`) prints `"NV"+key`.
- FIX: in `_dk_tom_tat_xep` key NULL as `"ngoai"` (or add field `ngoai_nguyen_vong`); in `bangKetQua` print `"Ngoài nguyện vọng: N"` for that key, sorted last. Label must read «Ngoài nguyện vọng» (placed outside the list), nothing more.
- Failing test: `tests/test_giao_dien_dk4_chot_xep.py::test_tom_tat_khong_in_NVNone` (HS with no preference placed → summary text has no "NVNone", has "Ngoài nguyện vọng: 1"; backend variant in `test_dk4_chot_va_xep.py::test_tom_tat_xep_hang_null_la_ngoai_nguyen_vong`).

**2. Buổi shows `thu_2`, `thu_3`** — CONFIRMED. `match_results.buoi = 'thu_2'` because the import runs `so_nhap.ma_buoi("T2") → "thu_2"`; the portal names are the strings stored in `dk_cai_dat['buoi']` ("T2","T3"). The portal does not load `js/05_quan_ly.js` (`nhanBuoi`), so no display mapping exists there.
- FIX (display layer only): in `_dk_tom_tat_xep` add `ten_buoi` per row: map `so_nhap.ma_buoi(b) → b` over `self._dk_buoi_khoi(cur)[0]`, fall back to the raw code; `bangKetQua` prints `x.ten_buoi || x.buoi`. Do NOT touch `match_results`.
- Failing test: `tests/test_giao_dien_dk4_chot_xep.py::test_tom_tat_hien_ten_buoi_cua_cong_khong_hien_thu_2` (settings buổi ["T2","T3"] → column shows "T2", never "thu_2"); backend `test_dk4_chot_va_xep.py::test_tom_tat_xep_co_ten_buoi`.

**3. "Xem trước Sổ nhập (N CLB, M học sinh)" with no table** — CONFIRMED, NOT timing. `DK.QT2.xemTruoc` (`js/dang_ky_quan_tri_2.js`) builds `h("details#dkXemTruoc", {}, h("summary"…), tables…)` without `open`, so the `<details>` is collapsed: only the `<summary>` is visible until clicked. Backend `dk_xuat_xem_truoc` returns full data (3 CLB, 3 students in the repro). The existing test `test_6` hides this by clicking `#dkXemTruoc summary` first (line ~216).
- FIX: `h("details#dkXemTruoc", { open: true }, …)` (same as the "Phòng" block in `danhSach`), or keep collapsed but show a one-line hint "Bấm để xem". Recommend open.
- Failing test: `tests/test_giao_dien_dkl_quan_tri.py::test_6b_xem_truoc_so_nhap_hien_san_bang_khong_can_bam` (after «Chốt và xếp» the "1. CLB" table is visible without clicking; wait for the selector so timing is excluded).

## FIX list for the coder (round 1 of 2 for this milestone)
1. Defects 1, 2, 3 above (3 failing tests named; commit as one lot `DKL-J`).
2. TIEN_DO rows for DKL-H and DKL-I (+ DKL-J).
3. Add dot decimal ("8.5") to `quan_tri test_4`; add "unticked Tuyển chọn → no Forms link" to `hoc_sinh test_2` (one extra Tuyển chọn club left unticked).
4. Run soat-ma tiers 2–4 on the diff; push, wait for CI green on Linux AND Windows (run for the new head); only then READY.
5. Head 348f6d4 CI (run 45719263842) must not be judged yet: it will be cancelled by the next push anyway.
