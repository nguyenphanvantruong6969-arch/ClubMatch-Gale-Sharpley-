# Branch handoff: claude/gt1-giai-trinh (CHECKER / tester)

> Purpose: a fresh checker reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, the branch file, THEN this file.
> Language: English. Cap: 150 lines. Protocol: GT_GIAO_THUC.md §5 steps 5-6, §7 formats. Never edit product code or tests.

## Feature / goal
Checker for GT1 (per-student explanation, parent C3). Reviews ONE lot diff per `REVIEW L<n> <base>..<head>` from the lead
(session_01TGThn8ujS9oohKhbgDiJgD), runs related tests + `kiem_nhanh.py`, tries own edge cases (temp test files, deleted
after), writes the verdict below, commits+pushes only this file, reports with send_message in §7 format.

## Plan (ticked by checker after reporting)
- [x] L1 reviewed -> 3 bugs -> fix1 re-check NO BUGS (2ccfd01)
- [x] L2 reviewed -> 1 bug -> fix1 re-check NO BUGS (2d2c947)
- [x] L3 reviewed -> NO BUGS (35a16d2)
- [x] L4 reviewed -> 1 BUG -> fix1 re-check NO BUGS (5facef0)

## Current state (overwrite each handoff)
- Done so far: L1-L3 closed with NO BUGS; L4 reported 1 bug to lead.
- In progress: waiting for `FIX L4` / `REVIEW L4 <base>..<head>` (re-check) from lead.
- Tests: last full related run on f4132a3: 578 passed (L1-L4 tests + all files mentioning delete_student/reset_data +
  i18n); kiem_nhanh 7/7 (60 cases identical).
- Open problems: L4 bug 1 (below) unfixed as of this handoff.

## Decisions and gotchas (keep short)
- `git pull --no-rebase` (protocol §1: never rebase a pushed branch) before push.
- Temp tests go in tests/test_zz_checker_tmp.py and are deleted before commit (git status must be clean except verdict).
- Chromium harness: reuse fixtures `mo` from tests/test_giao_dien_gt1_tra_cuu.py / _hoc_sinh.py; to delay API calls wrap
  `window.fetch` in-page (sync Playwright route handlers block other requests, giving false results).
- Student-id lockout is keyed on stripped id (case-sensitive); DB lookup is case-sensitive too (no bypass by case).
- Re-check of L4 fix: repro = delay first `tra_cuu_hoc_sinh` fetch 1.5 s in page, submit s1+code then 0.1 s later s2+code,
  wait 2.5 s: card must be s2's (or empty), never s1's.

## Next steps (ordered)
1. On `REVIEW L4 ... (fix1)`: pull, diff fix1 range, rerun tests/test_gt1_ma_tra_cuu.py, test_giao_dien_gt1_hoc_sinh.py,
   test_gt1_giai_trinh.py, test_gt1_phieu.py, test_giao_dien_gt1_tra_cuu.py, i18n tests; run the L4 repro above.
2. Append "L4 fix1" verdict below, commit+push, send CHECKER REPORT L4 (§7).
3. Then wait for CI-gate / later FIX requests from lead.

## Files touched
- docs/phien/claude__gt1-giai-trinh__tester.md: this file (verdicts). No product code or tests edited.
- .claude/phien_vai.json (gitignored): {"vai":"tester","coord_id":"session_01TGThn8ujS9oohKhbgDiJgD","nguong":200000}

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Sonnet checker | L1-L4 reviews; verdicts below; handoff at ~200k tokens | L4 bug 1 open |

# Verdicts (append only)
## (verdict history)

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

## L3 | reviewed 47b5751..35a16d2 | verdict: NO BUGS
53 passed (test_gt1_phieu, test_gt1_giai_trinh [L1 behaviour unchanged after refactor], test_giao_dien_gt1_tra_cuu,
i18n sync/khoa); kiem_nhanh 7/7. Own hostile-data test (temp, deleted): names with quotes, `<b>`, `&amp;`, `</td><script>`,
diacritics; per page exactly one `Mã:` id, no other student's escaped name or id, no script/http/src/link. Selection:
all -> 3 pages; lop `10a1` (lowercase) -> 2; ids with duplicate+unknown -> 1; `[]`, unknown class, bare string "s1"
-> `gt1_khong_co_hoc_sinh`; never-run -> `gt1_chua_chay` (tested by writer). Appeal days only when fa_khieu_nai ON (lead-accepted).

## L4 | reviewed 807499d..f4132a3 | verdict: 1 BUG
OK: 578 passed (L1-L4 tests + every test file mentioning delete_student/reset_data + i18n); kiem_nhanh 7/7 (60 cases);
match_results/stb_lock/run_history identical after tao_ma/tao_lai/tra_cuu (own snapshot test); old DB without
`ma_tra_cuu` reopened by two PipelineAPI instances -> table created, 2nd call idempotent; delete_student (new student)
and reset_data("hoc_sinh","XOA") remove codes, run_history untouched; codes 8 chars of the right alphabet, unique;
lockout: 5 wrong with " s1 "/"s1 "/"s1" variants share one key -> 6th = gt1_tam_khoa even with right code; "S1"
is a different (nonexistent) id -> gt1_ma_sai; unlock after 61 s; unknown id/None -> same gt1_ma_sai; code accepted
lowercase+spaces; response holds only that student; CSV UTF-8 BOM, diacritics ok, formula guard (`'=1+1`);
overlay: Tab cycles only gtHsMa/gtHsMaTra/btnGtHsXem/btnGtHsThoat (+BODY), Escape / Alt+Left do not exit, no admin
buttons in card, idle 61 s empties card DOM and both inputs.
Bug:
1. `js/14_giai_trinh.js` student-mode submit handler (`gtHsForm` -> `callApi("tra_cuu_hoc_sinh", ...)`): no
   latest-wins guard, so a slow reply for student A lands AFTER student B submitted and renders A's card next to B's
   inputs. Repro (Chromium; delay first `tra_cuu_hoc_sinh` fetch 1.5 s in-page): submit s1+code, 0.1 s later submit
   s2+code; after 2.5 s card = "Nguyễn Văn Ánh (s1)" while inputs show s2. Expected: only the latest submit renders
   (use `callApiMoiNhat("gt_hs", ...)` or a token like `luotTim`), so one student never sees another's card.

## L4 fix1 | re-checked f4132a3..5facef0 | verdict: NO BUGS
Fix: `luotHs` token in `js/14_giai_trinh.js` (bumped by submit, xoaThe, moHs, thoatHs; reply dropped if stale).
Own Chromium repro (temp test, deleted; first `tra_cuu_hoc_sinh` fetch delayed in-page, fake clock):
s1 slow then s2 -> card is s2's, no s1 name/id; s1 reply landing after 60 s idle clear -> card and both inputs stay
empty; s1 reply landing after exit (and after reopening) -> nothing rendered, overlay hidden; normal single lookup still
shows the card. Tests: gt1_ma_tra_cuu + giao_dien_gt1_hoc_sinh + giao_dien_gt1_tra_cuu + gt1_giai_trinh + gt1_phieu +
i18n_sync = 73 passed; kiem_nhanh 7/7 (60 cases identical).
