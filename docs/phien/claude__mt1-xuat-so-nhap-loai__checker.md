# Checker log — MT1-X1 (claude/mt1-xuat-so-nhap-loai)

## L1 f809b3f..2ea9193 — verdict: NO BUGS
- Xfail removed outright (no skip, assert untouched). Reverting `api_xuat.py` to f809b3f makes 3 tests RED
  (former xfail + 2 new FA tests); restored, all green.
- Gate = D1 exactly (`dung_fa_daa` OR any non-NULL of the 4 columns); no key added otherwise. Schema default of `loai` is NULL, so normal DBs stay gated off.
- Normal mode: 3 datasets (DQT_120HS_HOP_LE, MAU_120HS_3BUOI, test fixture) → no FA key, no FA column, no Giữ chỗ sheet; cell values equal old path.
- Related tests 71 passed; `ruff check .` clean.
- Own edge cases (scratch, not committed): FA off + only `diem_san` → columns present, round trip 7; FA on + duplicate/diacritic club names +
  loai/diem_san/so_toi_thieu/suc_chua_phong → all round trip; FA on all NULL → empty cells → NULL.
- Judgement on coder note: FA-off round trip imported into an FA-ON DB is acceptable (importer ignores Loại when FA off is pre-existing UX1A-L5).
- Observation (not a bug): the second caller (`tao_so_nhap_mau`, ~line 1530) also gets FA values now when FA on / clubs filled; harmless, mẫu is meant to carry them.

## L2 a39687f..2fd73ce — verdict: NO BUGS
- Related set run in full: 74 passed (coder's "74 expected" confirmed); `ruff check .` clean.
- Mutation: `api_xuat.py` reverted to a39687f → the 3 new L2 tests go RED; restored → green.
- Gate D2 correct: `giu_cho` passed only when `dung_fa_daa`; FA off → no sheet; FA on + empty table → header-only sheet.
- Round trip equal for loai/diem_san/so_toi_thieu/suc_chua_phong and the giu_cho SET; student with no preferences still round-trips.
- Own edge cases (scratch): header-only sheet imported over a DB holding a reserved seat clears it; export → import → export gives identical cell values on every sheet.
- `_du_lieu_so_nhap` tuple unchanged (D4); callers (2) unaffected.

## L3 bb2ba9b..902dcbb — verdict: NO BUGS
- Independent D5 (git worktree f809b3f vs HEAD, same import → `export_du_lieu_dau_vao`, sheet names + every cell): `SO_NHAP_DQT_120HS_HOP_LE`, `SO_NHAP_MAU_120HS_3BUOI`, `SO_NHAP_DQT_800HS_HOP_LE`, `SO_NHAP_TEST` → all IDENTICAL (sheets `1. CLB`, `2. Học sinh`, `Hướng dẫn`).
- Branch vs 05783a7: only `api_xuat.py` changed among product files (+18/-1); no solver, priority, run_history, schema, CSV header, i18n or UI change.
- Related set 74 passed; `ruff` clean; `kiem_nhanh.py` 7/7 incl. `trung_khit` (15 cases = 3 sets × 5 seeds).
- Docstring, CHANGELOG, TIEN_DO rows present and accurate. Note: `kiem_nhanh` uses 5 seeds, CLAUDE.md invariant 1 mentions 20 — solver untouched, so not a blocker.

## FIX L3 9f54f8c..3b05c35 — verdict: NO BUGS
- Diff is docs only (CHANGELOG.md, CLAUDE_CHI_TIET.md tests/ row 357→360 + branch/date text); no test or product file touched.
- `ls tests/test_*.py | wc -l` = 360 = documented count. `tests/test_a13_12_tai_lieu.py`: 8 passed.
