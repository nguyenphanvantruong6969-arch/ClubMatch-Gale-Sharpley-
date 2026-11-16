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

## L1 fix1 | re-checked 6fda292..2ccfd01 | verdict: NO BUGS
Bugs 1-3 fixed and covered by new tests (NO_CHOICES; gt1_lan_chay_cu; gt1_khong_tim_thay_lan_chay). On 2ccfd01:
test_gt1_giai_trinh + test_fa_ly_do + test_fa_n1_ly_do_mot_phan + test_i18n_khoa_dc_khong_chet + test_i18n_sync
= 72 passed; kiem_nhanh 7/7 (9 cases identical, i18n in sync, ruff clean).

## L2 | reviewed de39b20..0a57c37 | verdict: 1 BUG
OK: tests/test_giao_dien_gt1_tra_cuu.py 5 passed; `search_students(q)` / `(q, None)` unchanged (2 rows), `lop` filter ok
(`10A1`->1, unknown->0); XSS: student name `<img src=x onerror=...>` rendered as text (no img, no handler fired,
textContent only); EN mode: labels English, no internal codes (VI-only sentences accepted per lead); "All class"
label is singular (cosmetic, ignore).
Bug:
1. `js/14_giai_trinh.js:xem/tim` — stale search response repopulates the suggestion list AFTER a student is selected,
   so the panel holds another student's name. `xem()` clears `#gtDs` but the pending `callApiMoiNhat("gt_tim", ...)`
   is on a different channel and still resolves. Repro (Chromium, search request delayed 1.5 s via page.route on
   `**/__api__/search_students`): type "s" -> list shown; type "n" (slow) ; click s1 at once; after 2 s `#gtDs`
   contains "Nguyễn Văn Ánh (s1)" and the other student's name (s2). Expected: after selecting, DOM has only the
   chosen student (bump the `gt_tim` channel counter in `xem`, or ignore results until the next input).

## L2 fix1 | re-checked 0a57c37..2d2c947 | verdict: NO BUGS
Own repro (delayed search, type "s" then slow "n", click s1): `#gtDs` empty, no other student in panel. A-then-B
(first get_giai_trinh_hoc_sinh delayed 2 s, B picked meanwhile): card ends as B, A's late reply dropped. 8 passed
(my 2 temp tests + tests/test_giao_dien_gt1_tra_cuu.py incl. new regression); temp tests deleted.
