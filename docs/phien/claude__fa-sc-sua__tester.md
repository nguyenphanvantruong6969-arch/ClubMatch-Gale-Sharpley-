# FA-SC checker verdicts (tester)

## L2 — reviewed 3f44c3d..bca5941 — verdict: NO BUGS
- Tests: new `test_fa_sc_l2_can_xu_ly.py` + L1 file + `test_mau_forms_thi_clb`, `test_fa_m3_chuyen`, `test_fa_m2_forms_dang_ky`,
  `test_fa_m9_nap_tep_forms`, `test_a13_12_tai_lieu` -> 104 passed. `ruff check` clean.
- Drills (fake data): d04, d06, d07 now show one "Cần xử lý" row each (d06 merged to one row); d05 correctly stays
  unflipped (needs form change, on Needs Truong).
- Invariant 1: `demo_t4m.py` plain and `--day-du`, base 3f44c3d vs head: BANG_DIEM/SO_NHAP_CLB/lists/forms identical
  (xlsx cell values per sheet). `kiem_nhanh.py --co-so origin/main --so-seed 20`: 7/7, 60/60 identical.
- Invariant 2/6/7: report-only sheet, no kiosk/CSV/schema change. Privacy: rows only name the student's own ID/email.
- Own edge cases on `lap_can_xu_ly`: empty roster -> []; diacritic IDs/names fine; reservation for unknown ID -> one row;
  both unknown-email warning variants (with/without --co-so) -> one row each; unrelated warnings ignored.
- Notes (not bugs): (a) unknown-email rows rely on matching the warning text (`_MAU_EMAIL_LA`); if that wording changes the
  row silently disappears — the test would catch it. (b) `--can-xu-ly` without test files writes no sheet (help text says so).

## L3 — reviewed fa62f77..7c3d3b3 — verdict: NO BUGS
- Tests: new `test_fa_sc_l3_bao_cao_clb.py` + L1/L2 files + `test_mau_forms_thi_clb`, `test_fa_m3_chuyen`, `test_fa_m2_forms_dang_ky`,
  `test_fa_m9_nap_tep_forms`, `test_a13_12_tai_lieu` -> 110 passed. `ruff check` clean.
- Invariant 1: `demo_t4m.py` plain and `--day-du`, worktree fa62f77 vs head: 42 files each, xlsx cell values per sheet and
  csv/txt identical, no extra folder. `kiem_nhanh.py --co-so origin/main --so-seed 20`: 7/7, 60/60 identical.
- Invariant 2/6/7: report-only (`lap_bao_cao_clb` reads `bai_thi`/`nguyen_vong`, feeds nothing back); no kiosk/CSV/schema change.
- Privacy: file per club has only that club's dropped emails and student IDs who ranked that club; no score, no STB, no
  other club (test asserts forbidden words and membership). Teacher text is plain Vietnamese, no internal codes.
- Own edge cases on `lap_bao_cao_clb`/`ghi_bao_cao_clb`: empty students/None roster/None dropped -> empty lists, still one file;
  same email dropped twice and repeated club in ranking -> listed once; club not in exam config ignored; diacritic club_id
  (`CLB_Đặc_Biệt.xlsx`) written fine.
- Notes (not bugs): (a) `ghi_bao_cao_clb` needs `name` on every club in `de` (KeyError otherwise; `de` always has it today);
  (b) `club_id` is used as a file name without sanitising (`../x` would write outside the folder) — ids come from the admin's own
  exam config, not student input, so low risk; (c) with `--co-so` the "bỏ phiếu" reason may be "other base" but the file text
  says "not in the registration list" — acceptable wording. (d) L3 has no drill in the spec; none run.
