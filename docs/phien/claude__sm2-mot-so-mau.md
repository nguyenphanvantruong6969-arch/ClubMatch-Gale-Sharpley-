# Branch handoff: claude/sm2-mot-so-mau

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

Status: DONE 8839a2a CI green (run 44913768207); checker NO BUGS after FIX1

## Feature / goal
Item **SM2 — one sample workbook** (approved by Truong 2026-11-21; tracked in `TIEN_DO.md`, not in the
33-item registry). Branch base: `origin/claude/ux2-phan-hoi-nut` (Truong, option A: plan not on main). Follows SO-MAU (`du_lieu_test/SO_NHAP_MAU_DAY_DU.xlsx`, `tao_so_nhap_day_du.py`).
(1) Stop the false `wharton_chua_dung_het` import warnings in FA workspaces (657 on the full sample, 434 on
`SO_NHAP_FA_MAU_120HS.xlsx`); (2) replace the two in-app buttons "Tải sổ mẫu" / "Tải sổ mẫu huy chương" with ONE
button whose workbook always has the full structure + the column dictionary.

## Decisions (Opus, 2026-11-21)
- Root cause (1): the import step calls `_soat_ho_so_wharton` whenever `bat_wharton` is on, also when FA is on.
  FA checks medals with `fa_daa.kiem_ho_so_huy_chuong` (preview) instead; the run itself already passes (120/120).
  Fix: skip `_soat_ho_so_wharton` when `dung_fa_daa(luat)`. Check the health report / Kiểm tra paths
  (`api_quan_ly.py`, callers of `kiem_ho_so_wharton`) for the same noise in FA; fix only if they show it.
- Full structure ALWAYS: Loại, Điểm sàn, Tối thiểu, Sức chứa phòng, Giờ, Địa điểm, Lớp, sheet Giữ chỗ (header
  only), column dictionary in Hướng dẫn. The third column of each NV group keeps following the MODE (FA →
  "Huy chương (60/30/10)", else "Điểm quyết tâm"): the same column means two things, so it cannot be unified.
- Column dictionary moves into `so_nhap.py` (single source of the format); `du_lieu_test/tao_so_nhap_day_du.py`
  calls it instead of its own `TU_DIEN`.
- `ghi_so_nhap` gets a new parameter `day_du=False`; default output stays BYTE-IDENTICAL (existing tests).
- API `tao_so_nhap_mau(output_path, kieu)` keeps its signature; `kieu` is accepted and ignored except
  `"huy_chuong"` still forces the medal label (old callers keep working). Contract `{ok,data,errors}` unchanged.
- Empty FA columns / empty Giữ chỗ sheet in a non-FA workspace must raise NO warning (`fa_cot_bo_qua`,
  `fa_giu_cho_bo_qua` only when a cell has a value). Verify first; fix only if needed.
- No algorithm, CSV contract, schema change (invariants 1, 6, 7). No new library.

## Plan (Opus writes; Sonnet ticks)
Lot L1 — no false warnings in FA (#3)
- [x] Test first `tests/test_sm2_canh_bao_fa.py`: FA workspace (`rules: fa_daa, wharton`) imports
      `SO_NHAP_MAU_DAY_DU.xlsx` and `SO_NHAP_FA_MAU_120HS.xlsx` → 0 warnings with code `wharton_chua_dung_het`;
      a DQT-only workspace importing a workbook with a blank fund still warns exactly as before (regression).
- [x] Fix in `api_nhap.py` at the `_soat_ho_so_wharton` call; same check for health report / Kiểm tra in FA.
- [x] `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7.
Lot L2 — one button, full structure (#2)
- [x] Test first `tests/test_sm2_mot_so_mau.py`: `tao_so_nhap_mau` in default, DQT and FA workspaces → sheet
      `1. CLB` has every header of `COT_CLB + COT_FA + COT_GIO`, sheet `2. Học sinh` has Lớp, sheet Giữ chỗ
      exists, Hướng dẫn has "TỪ ĐIỂN CỘT"; medal label only in FA; the template filled with 2 clubs + 3 students
      (FA columns empty) imports in a DEFAULT workspace with no new warning; `ghi_so_nhap` default unchanged.
- [x] `so_nhap.py`: `TU_DIEN_COT` + `_ghi_tu_dien_cot(wb)` + `day_du` param; `api_xuat.tao_so_nhap_mau`
      passes `day_du=True`; `tao_so_nhap_day_du.py` reuses it (regenerate the xlsx, content must not change
      except formatting).
- [x] UI: remove `btnTaiSoMauHuyChuong` (`index.html`, `js/02_van_hanh.js`, its i18n key); the wrong-mode
      prompt of UX1A-L5 stays. Update UX1A-L5 tests that use the removed button deliberately (list in CHANGELOG).
      One Chromium check: one sample button, click → `tao_so_nhap_mau` called once, UX2 ✓ shows.
- [x] `HUONG_DAN_SU_DUNG.md`, `mau_csv/HUONG_DAN_SO_NHAP.md` (one sample, column dictionary), CHANGELOG, TIEN_DO.

## Acceptance (kiem_nhan)
- Both lots' tests green; related: `test_so_nhap.py`, `test_so_mau_day_du.py`, `test_a13_8_so_mau.py`,
  `test_so_mau_co_cot_quyet_tam.py`, `test_fg2_xem_truoc_fa.py`, `test_ux1_l5_backend.py`,
  `test_giao_dien_ux1_nhap_so.py`, `test_i18n_sync.py`, `test_van_phong_tu_nhien.py`, `test_a13_12_tai_lieu.py`.
- Invariant 1: `kiem_nhanh.py` 7/7. CI green (Tests). No Windows build needed unless Truong asks.

## Current state
- Done: L1 (api_nhap skip in FA; list_wharton_canh_bao drops the code in FA; health report already FA-split).
- Done: L2 (`ghi_so_nhap(day_du=True)` from `tao_so_nhap_mau` and `mau_csv/tao_so_nhap.tao_mau_trong`; one button; ✓ on success).
- Done: FIX round 1 (checker bug 1): dictionary written only for default school vocabulary.
- Next: Truong reviews; PR to main only when Truong asks (one PR for SM2).

## Decisions and gotchas
- FIX1 chose the checker's minimal option (skip dictionary for custom vocabulary) rather than translating it: its notes also say "CLB", "học sinh", "CLB Tự do" and a label-aware rewrite is a larger change.
- i18n key `ux1a_btn_so_mau_huy_chuong` KEPT: the wrong-mode prompt button `ux1bSsTaiSoMau` (js/18_cai_dat.js) still uses it (plan said remove; removing would break the kept prompt).
- `mau_csv/SO_NHAP_CLB.xlsx` must equal the app sample (T1a) → `tao_mau_trong` also passes `day_du=True`; regenerated.
- Sheet Hướng dẫn may not say "em" (T1a/G3): dictionary rows reworded to "học sinh" (so `SO_NHAP_MAU_DAY_DU.xlsx` text changed in 4 cells).
- FA sample Hướng dẫn may not mention "Điểm quyết tâm"/"quỹ" (FG-2): `_ghi_tu_dien_cot(che_do_fa=bool)` swaps the third-column row per mode; `None` (du_lieu_test script) keeps the combined row.
- Import warnings are in `data.warnings`, not `errors`.
- `CLAUDE_CHI_TIET.md` counts test files (`370 tệp`); each new test file → update the count (CI checks docs).

## Needs Truong
- (not blocking) Should custom-vocabulary workspaces (company, dorm…) get a column dictionary written in their own labels? Today they get none (SM2-FIX1). Would be a new item.

## Files touched
- L2: so_nhap.py, api_xuat.py, index.html, js/02_van_hanh.js, i18n.js, mau_csv/tao_so_nhap.py + SO_NHAP_CLB.xlsx, du_lieu_test/tao_so_nhap_day_du.py + SO_NHAP_MAU_DAY_DU.xlsx, 2 guides, tests (1 new + 6 updated)
- L1: api_nhap.py, api_quan_ly.py, tests/test_sm2_canh_bao_fa.py, CHANGELOG.md, TIEN_DO.md, CLAUDE_CHI_TIET.md

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-21 | Opus (planner) | Goal, decisions, Plan L1–L2 | no product code |
| 2026-11-21 | coder | L1 done, kiem_nhanh 7/7 | import warnings live in data.warnings |
| 2026-11-21 | coder | L2 done, related tests 507 green, kiem_nhanh 7/7 | READY FOR REVIEW |
| 2026-11-21 | coder | FIX round 1: checker bug 1 (dictionary vocabulary), +2 tests, kiem_nhanh 7/7 | minimal fix |
| 2026-11-21 | coder | CI round 1: SUA_CO_Y entry for import_hint in test_ws_nhan (deliberate text change) | checker recheck FIX1 = NO BUGS |
| 2026-11-21 | coder | CI green on 8839a2a → DONE | |
