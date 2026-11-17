# Branch handoff: claude/gt2-tieu-chi (CHECKER session)

> Purpose: a fresh CHECKER reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, docs/phien/claude__gt2-tieu-chi.md, then THIS file.
> Language: English. Cap: 150 lines. Verdicts per lot are kept below the log (append only).
> Lead session: session_01YVAyu3PPHv9SNntepRSLwh. Role file: .claude/phien_vai.json = {"vai":"tester","coord_id":<lead>,"nguong":200000} (gitignored; rewrite it).

## Feature / goal
CHECKER for GT2 (criteria in plain words, trial runs, compare runs, adopt criteria). Reviews ONE lot diff per
"REVIEW L<n> <base>..<head>", runs related tests, own edge cases, writes verdict here, pushes only this file, reports
to lead in protocol §7 format. Never edits product code or tests.

## Plan
- [x] L1 reviewed: fix0 1 BUG (wharton box), fix1 1 BUG (not restored), fix2 NO BUGS (head 48ad9d8)
- [x] L2 reviewed 7162a5e..9613648: 1 BUG (minor) + 1 note, report sent; waiting for FIX/re-REVIEW
- [ ] L3 compare two runs, [ ] L4 adopt criteria (wait for REVIEW)

## Current state
- Done: L1 (3 rounds, closed NO BUGS), L2 first review reported.
- In progress: nothing; awaiting lead (`FIX L2` -> expect `REVIEW L2 <base>..<head>` re-check, or `REVIEW L3`).
- Tests: `.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no tests/test_gt2_tieu_chi.py
  tests/test_giao_dien_gt2_tieu_chi.py tests/test_gt2_chay_thu.py` -> 144 passed at 9613648.
  `.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so <base> --so-seed 20` -> 7/7.
- Open problems (L2, to re-verify after fix): (1) `_run_thu_da_khoa` refuses if SAVED fa_daa is on even when
  rules_thu turns it off; message tells the admin to do the impossible. (2) note: rules_thu accepts keys outside
  LUAT_XEP_MAC_DINH (max_tests, fa_duong) that are absent from run_history.luat_xep.
- Not exercised: trial with Wharton ON (du_lieu_test datasets lack Wharton profiles -> official run fails).

## Decisions and gotchas
- Use `git pull --no-rebase` (protocol forbids rebasing pushed branches) and push only the verdict file.
- Workspace mode must be ON for update_workspace_config/get_tieu_chi tests (else `ws_tat_che_do`): use
  `workspace.tao(goc, name, None)` + `PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=..., thu_muc_goc_ws=goc)`,
  or `d.nap_bo(tmp, tep)` from du_lieu_test/do_anh_huong_seed.py with `cau_hinh_ws.ghi_cau_hinh(db, {"rules":{"wharton":False}})`.
- Throwaway checks: scratch scripts in /tmp/claude-0/-home-user-TESTING-DEV/976575b9-a06d-5167-a224-b62bd5869d05/scratchpad
  (edge.py, edge2.py, l2.py, l2b.py); temporary test files in tests/ were deleted, never commit them.
- Full-table before/after dump (all sqlite tables) is the best proof that a feature writes only where allowed.
- Existing Chromium tests mask UI bugs when they pre-set checkboxes: always add the "do not touch the box" path.

## Next steps
1. Wait for `FIX L2` / `REVIEW L2 <base>..<head>`: re-run repro for bug 3 (saved FA on + rules_thu FA off) and the note.
2. `REVIEW L3`: check `so_sanh_lan_chay` numbers on a hand-made 10-student fixture, same-run-vs-itself = zero changes,
   changed list == direct diff, privacy (only aggregate/own data), HTML export opens offline, CSV contract unchanged.
3. `REVIEW L4`: saved rules == trial's, no result table changes until an official run, next official
   run_history.luat_xep == trial's; confirm dialog shows L1 description; never copies trial results.

## Files touched
- docs/phien/claude__gt2-tieu-chi__tester.md: this handoff + verdicts (only file the checker commits)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Sonnet (checker) | Setup; reviewed L1 (3 rounds -> NO BUGS) and L2 (1 minor bug + 1 note) | handoff at ~200k tokens |

---
# Verdicts (append only)


## L1 | reviewed 1ff5794..4738551 | verdict: 1 BUG (UI), rest OK

Tests: tests/test_gt2_tieu_chi.py + tests/test_giao_dien_gt2_tieu_chi.py -> 113 passed.
`kiem_nhanh.py --co-so 1ff5794 --so-seed 20` -> 7/7 DAT (60 cases identical, ruff, chu_cam, i18n, run_history untouched).

Verified:
- Writer's claim true: `cau_hinh_ws._chuan_hoa` (via `update_workspace_config`, workspace mode ON) rejects, with
  saved rules unchanged: unknown rules key, unknown top-level key, priority/tier_mode/score_scope bad values (string,
  list, dict), tiers non-list / non-string / empty / duplicate, wharton/fa_daa non-bool (incl. 1), rules list/None,
  priority=tier + wharton=true, fa_daa=true + wharton=false (`fa_can_diem_quyet_tam`). Code is `ws_du_lieu_sai`
  (existing), so no `gt2_tieu_chi_khong_hop_le` needed. Note: without workspace mode every call returns `ws_tat_che_do`.
- Allow-list key set pinned to LUAT_XEP_MAC_DINH + KHOA_NGOAI_LUAT_XEP; descriptions parametrised over all combos.
- Mandatory note present (`ghi_chu`, rendered in `#gt2TcGhiChu`); chu_cam/i18n checks pass; Vietnamese tier names with
  diacritics round-trip. get_tieu_chi is read-only; FA on/off descriptions covered by the enumerated combos.

BUG 1 (UI): js/15_tieu_chi.js `gt2TcLuatDangChon` always sends `wharton: el("gt2TcWharton").checked`.
- repro: fresh workspace (default wharton=true) -> panel -> choose "Chỉ theo nhóm ưu tiên" (priority=tier) or "Một điểm
  cho cả người" (score_scope=per_person) -> Save without touching the checkbox. Reproduced at API level with the exact
  payload: `ws_du_lieu_sai` "wharton chỉ dùng được khi priority là score hoặc score+tier và score_scope là per_slot
  (điểm Wharton cần biết em có thi CLB nào)" — jargon (`wharton`, `per_slot`) shown to the teacher. Explicit `wharton`
  also defeats the auto-off in `cau_hinh_ws.tron_len`/`_chuan_hoa`.
- expected: saving a combination that makes commitment points inactive works without an error (omit `wharton` from the
  payload or auto-uncheck + disable the box in the UI when priority==="tier" or scope==="per_person"; with FA on, say
  in plain words that FA turns off). 
- why tests missed it: `test_luu_khoa_diem_quyet_tam_khi_chi_xet_nhom_khong_loi` calls `.uncheck()` first. Add a
  case that does NOT uncheck.

## L1 fix1 | reviewed 4738551..9b67a95 | verdict: 1 BUG (minor)

Tests: 115 passed (L1 unit + Chromium). Original bug fixed: priority=tier / per_person -> box unchecked + disabled,
hint shown, save succeeds without .uncheck(); FA-on hint text present (vi + en).

BUG 2 (UI, minor): js/15_tieu_chi.js `gt2TcDongBoWharton` unchecks the box but never restores it.
- repro (Chromium, fresh workspace, saved wharton=true): choose priority "tier", then back to "score" -> box is
  ENABLED but UNCHECKED (same after per_person -> per_slot). Save now sends wharton=false: commitment points are
  silently turned off; with FA on the save is refused (fa_can_diem_quyet_tam) although the admin only toggled and
  reverted a select.
- expected: switching back to score + per_slot restores the box to the last state the admin chose (remember the
  pre-disable checked value, or reset to the saved value), hint hides.

Note (not blocking, pre-existing from L1): changing language re-runs gt2TcVeDieuKhien/gt2TcDatGiaTri, which resets
unsaved selects, textarea and box to the saved values.

## L1 fix2 | reviewed 9b67a95..48ad9d8 | verdict: NO BUGS

119 passed (L1 unit + Chromium incl. 4 new round-trip cases FA on/off). BUG 1 and BUG 2 repros no longer fail.
Own chain (box unchecked by admin -> tier -> per_person -> score -> per_slot): box re-enabled, stays unchecked (the
admin's own choice), saves wharton=false; tier+save+back to score: enabled, no error.
Residual (not a "Done when" item, not blocking): after a language switch, `gt2TcDongBoWharton` may reuse a stale
remembered value over the saved one in the rare case of pending edits; selects are reset to saved anyway.

## L2 | reviewed 7162a5e..9613648 (product 3f5957c) | verdict: 1 BUG (minor), 1 note

Tests: 144 passed (gt2 L1+L2 + Chromium) + 123 passed in 6 older files that touch run_history/get_run_history/di_tru_schema.
`kiem_nhanh.py --co-so 7162a5e --so-seed 20` -> 7/7 DAT (60 cases identical).

Verified (own scripts, fake data, dataset 0 of du_lieu_test, wharton off):
- Readers: re-grep of run_history / MAX(run_id) / ORDER BY run_id / COUNT(*) in all non-test .py. Official readers
  filtered via `loc_chinh_thuc`: api.get_run_history, api_xuat (FA reason lookup), fa_sau_xep.run_goc_theo_buoi,
  rbda.run_chinh_thuc_moi_nhat (used by run_thu). NOT filtered, judged safe: api.py MAX(run_id) x2 (read inside the
  official transaction right after its own INSERT), rbda `_chan_neu_la_du_lieu_that` COUNT(*) (CLI guard; a trial
  requires an official run first so it only ever counts MORE rows). api_quan_ly/api_bao_cao use run_meta only.
- Full-table dump before/after a trial: ONLY run_history (+1 row, loai_chay='thu') and ket_qua_thu changed;
  match_results, ket_qua_truoc, dau_van_tay_chay, stb_lock, stb_buoi, run_meta, fa_*, students untouched.
- Official -> 2 trials -> official vs control DB (official -> official): match_results identical; run_history ids
  1,2(thu),3(thu),4 vs 1,2; get_run_history shows [4,1] / [2,1] (trial rows hidden, id gap only).
- No official run yet / STB not locked -> gt2_chua_co_lan_chinh_thuc, no rows written. 9 bad rules_thu (unknown
  key, bad value, tiers str, list, None, fa_khieu_nai, max_choices=1 -> pref_too_many) leave run_history/ket_qua_thu counts
  unchanged. Rollback and double-migration covered by writer tests; trial with same rules == official (3x5 seeds).
- Not exercised by me: trial with Wharton ON (official run of that dataset needs Wharton profiles); reader code shows no writes.

BUG 3 (minor, message): api_tieu_chi.py `_run_thu_da_khoa` refuses when `dung_fa_daa(da_luu["rules"])` even if
rules_thu switches fa_daa/wharton OFF. repro: workspace with saved fa_daa=true (+wharton), official run done,
`run_thu({"fa_daa": False, "wharton": False})` -> gt2_thu_chua_ho_tro_fa, whose text says "Hãy tắt chế độ huy chương
trong tiêu chí thử" — impossible to follow. expected: either allow a trial whose merged rules have FA off (does not
touch fa_* tables) or change the message to "đang bật chế độ huy chương ở trường: chưa chạy thử được; dùng lần xếp
chính thức" for the saved-FA case.

Note (non-blocking, spec "bounded" D-GT1): rules_thu accepts non-criteria workspace keys (`max_tests`, `fa_duong`
accepted and run; `max_choices` rejected only by data check). They do not enter `run_history.luat_xep`, so a trial
label would not show them. Suggest rejecting any key outside LUAT_XEP_MAC_DINH with gt2_tieu_chi_khong_hop_le.

## L2 fix1 | reviewed 9613648..e36fc60 | verdict: NO BUGS

Tests: 148 passed (gt2 L1+L2+Chromium). `kiem_nhanh.py --co-so 7162a5e --so-seed 20` -> 7/7 DAT (60 cases identical).
Own full-table dump (dataset 0, wharton off) before/after run_thu:
- saved fa_daa+wharton ON, run_thu({fa_daa:False,wharton:False}) -> ok; changed tables ONLY run_history, ket_qua_thu (+sqlite_sequence); fa_* untouched. (bug 3 fixed)
- saved FA ON, run_thu({}) -> gt2_thu_chua_ho_tro_fa, nothing written; message now followable (merged rules still FA).
- saved FA ON, run_thu({wharton:False}) -> gt2_tieu_chi_khong_hop_le with plain reason, nothing written.
- keys max_tests / fa_duong / "điểm" -> gt2_tieu_chi_khong_hop_le naming the key, nothing written. (note fixed)
- empty trial and tiers with diacritics run fine. Saved FA + {fa_daa:False} on data without Wharton profiles fails with the
  same wharton_* data errors as the official run would (by design, no write).

## L3 | reviewed 5ae7003..1cca309 | verdict: NO BUGS

Tests: 208 passed (gt2 L1+L2+L3 incl. Chromium, test_ws_nhan). `kiem_nhanh.py --co-so 5ae7003 --so-seed 20` -> 7/7 DAT.
Verified (own scripts, fake data):
- Hand-recomputed 10-student fixture (2 clubs, 2 groups, 2 classes): totals A 8/10 assigned, 40% 1st, 70% top3, mean rank 1.88;
  B 8/10, 50%, 70%, 1.75; cut-offs C1 5->4, C2 3->3; per group G1/G2 and per class 10A/10B all equal my hand numbers.
  Percentages are over ALL slots (unassigned included); mean rank over assigned only (consistent, documented in code).
- Changed list == direct diff: pure fixture (assigned<->unassigned included) and real DB (3 datasets x 2 trials: 4/66/75/48/49
  changes; API list == SQL diff of match_results vs ket_qua_thu). Self vs self and official vs official = 0 changes.
  Sessions: only sessions present in BOTH runs are compared (buoi_chung); n counts only those. Empty rows -> None, no crash.
- Errors: unknown/bool/str/None run id -> gt2_lan_chay_khong_co; no official run -> gt2_chua_co_lan_chinh_thuc (also exports);
  old official id after a 2nd official run -> gt2_so_sanh_lan_cu (no invented numbers). list_lan_chay shows latest official + trials.
- Writes: full-table dump before/after compare + both exports: nothing changed. HTML: one file, no external refs, escaped
  (`<script>` + quotes + & in a name -> &lt;script&gt; in the changed-students table), labels "Chạy thử số n"/"Chính thức số n".
  CSV: UTF-8 BOM, header student_id,ho_ten,lop,buoi,clb_a,clb_b. UI uses textContent only; no internal codes in i18n text.
- Test fixes (item 6): diff 5ae7003..1cca309 on tests/ is INSERT-ONLY (new files + 7 added lines in test_ws_nhan = GT2 codes
  added to the expected set). index.html placeholder fix is product text, not a weakened test.
- FA on (saved fa_daa+wharton): list/compare run, read-only. No official run: refused cleanly.
Notes (non-blocking): (a) HTML export text is Vietnamese only (no English variant); (b) so_sanh_lan_chay returns the student
list to any caller of the admin API (same as other admin APIs; accounts/roles arrive with GT3 integration I1) — nothing in a
student-facing path calls it (grep: only js/15_tieu_chi.js admin panel).
