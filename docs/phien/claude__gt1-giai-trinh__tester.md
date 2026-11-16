# Checker verdicts — GT1 (branch claude/gt1-giai-trinh)

## L1 | reviewed a75a02b..6fda292 | verdict: 3 BUGS (all minor, none touches run paths)
Verified OK: `tests/test_gt1_giai_trinh.py` 24 passed; `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7 DAT
(60 cases identical, ruff, i18n, no UPDATE/DELETE on run_history); read-only (no writes in `_giai_trinh_hoc_sinh`,
`_ket_noi_doc` only; test snapshots stable); FULL_GROUP/FULL_WHARTON sentences plain Vietnamese, no internal codes,
no "Wharton" word, consistent in tests' valid set; Wharton-ON default workspace replays identical (test passes);
privacy test ok (FA path uses only that student's `fa_rows`).
Bugs:
1. `giai_trinh.giai_trinh_mot_hoc_sinh` — student with NO preferences and no seat gets `cau_tom_tat` "các CLB em chọn
   đều đã đủ chỗ" (false: chose none). Repro: FA workspace, students s1,s2,s3; s3 has no prefs -> buoi thu_2
   UNASSIGNED with that sentence, `cac_lua_chon` = []. Expected: separate sentence/code (e.g. no choices submitted)
   or no claim of "full".
2. `api_xuat._giai_trinh_hoc_sinh` with `run_id` = older run (same data, same seed run twice): returns
   `du_lieu_da_doi True` (false "data changed" warning) while FA path explains LATEST run's `match_results`/`fa_ly_do`
   under the older run's label. Repro: run_pipeline(seed=1) twice; `get_giai_trinh_hoc_sinh(sid, run_id=1)`.
   Expected: either reject non-latest `run_id` with an explicit error, or use a distinct flag/wording ("lần chạy cũ")
   and never mix latest results with old run metadata.
3. `api_xuat._giai_trinh_hoc_sinh` — unknown `run_id` (9999) returns `gt1_chua_chay` ("chưa có lần xếp nào") though
   runs exist. Expected: a distinct message (e.g. run not found).
Edge cases tried: empty/None/diacritic unknown id -> `gt1_khong_co_hoc_sinh` ok; never-run -> `gt1_chua_chay` ok.
