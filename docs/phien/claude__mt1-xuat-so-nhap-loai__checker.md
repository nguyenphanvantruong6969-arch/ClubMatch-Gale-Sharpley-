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
