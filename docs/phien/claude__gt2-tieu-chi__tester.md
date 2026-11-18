# Branch handoff: claude/gt2-tieu-chi (CHECKER session)

> Purpose: a fresh CHECKER reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, docs/phien/claude__gt2-tieu-chi.md, then THIS file.
> Language: English. Cap: 150 lines. Verdicts per lot are condensed below (append only; full detail in git history).
> Lead session: session_01YVAyu3PPHv9SNntepRSLwh. Role file: .claude/phien_vai.json = {"vai":"tester","coord_id":<lead>,"nguong":200000} (gitignored; rewrite it).

## Feature / goal
CHECKER for GT2 (criteria in plain words, trial runs, compare runs, adopt criteria). Reviews ONE lot diff per
"REVIEW L<n> <base>..<head>", runs related tests, own edge cases, writes verdict here, pushes only this file, reports
to lead in protocol §7 format (send_message to the lead). Never edits product code or tests.

## Plan
- [x] L1 reviewed (3 rounds) -> NO BUGS at 48ad9d8
- [x] L2 reviewed: first review 1 minor bug + 1 note; fix1 (9613648..e36fc60) -> NO BUGS
- [x] L3 reviewed 5ae7003..1cca309 -> NO BUGS
- [x] L4 reviewed 0f157e0..20f396d -> 1 BUG (minor) reported to lead; awaiting `FIX L4` then re-REVIEW
- [x] L4 fix1 reviewed 20f396d..a41f7bc -> NO BUGS (BUG 4 fixed)

## Current state
- Done: L1-L3 closed. L4 first review reported (BUG 4 below).
- In progress: nothing; L4 closed NO BUGS. No further duty unless asked.
- Tests: `.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no tests/test_gt2_ap_dung.py
  tests/test_gt2_so_sanh.py tests/test_giao_dien_gt2_thu.py tests/test_gt2_tieu_chi.py tests/test_giao_dien_gt2_tieu_chi.py
  tests/test_gt2_chay_thu.py tests/test_ws_nhan.py` -> 214 passed at 20f396d.
  `.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so <base> --so-seed 20` -> 7/7.
- Open problem: BUG 4 (see L4 verdict). Not exercised: trial with Wharton ON (datasets lack Wharton profiles).

## Decisions and gotchas
- Use `git pull --no-rebase` (protocol forbids rebasing pushed branches); push only the verdict file. The session may start
  on a DETACHED HEAD: run `git checkout -B claude/gt2-tieu-chi` after merging FETCH_HEAD, then push.
- Workspace mode must be ON for update_workspace_config / apply / get_tieu_chi tests (else `ws_tat_che_do`): build as in
  tests/test_gt2_ap_dung.py `_mo` (ws.tao + copy db + PipelineAPI(db, thu_muc_goc_ws=goc)); for trial-only checks use
  tests/test_gt2_chay_thu.py `_mo(tmp, t.BO[i][2])`. Export paths must be FILE paths (a directory gives xuat_duong_la_thu_muc).
- Scratch scripts: /tmp/claude-0/-home-user-TESTING-DEV/22a6e6da-7952-5769-8ad0-29639eefdb11/scratchpad (l2f.py, l3.py, l3b.py,
  l3c.py, l4.py, l4b.py). Never commit throwaway tests.
- Best proofs: full-table before/after dump (all sqlite tables); twin workspace saving the same raw criteria directly (A/B).
- Existing Chromium tests mask UI bugs when they pre-set controls: add the "do not touch it" path.

## Next steps
0. (done by checker 3) L4 fix1 verified NO BUGS; lead runs CI gate. Old list below kept for reference.
1. Wait for `FIX L4` / `REVIEW L4 <base>..<head>` (fix1): re-run repro A (trial tier -> apply -> panel priority back to score:
   saved tier_mode must stay as before the trial, i.e. reserve) and repro B (score+tier reserve with groups -> apply -> saved
   keeps priority/tiers or stays equivalent); re-confirm `luat_xep_hieu_luc(saved) == trial's effective`, next official
   luat_xep + match_results == direct-save twin, apply writes only workspace_settings, kiem_nhanh 7/7.
2. After L4 NO BUGS the lead runs the CI gate (§6); checker has no further duty unless asked.

## Files touched
- docs/phien/claude__gt2-tieu-chi__tester.md: this handoff + condensed verdicts (only file the checker commits)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Sonnet (checker 1) | Setup; reviewed L1 (3 rounds -> NO BUGS) and L2 (1 minor bug + 1 note) | handoff at ~200k tokens |
| 2026-11-17 | Sonnet (checker 2) | L2 fix1 NO BUGS; L3 NO BUGS; L4 1 minor bug reported | handoff at ~200k tokens |
| 2026-11-17 | Sonnet (checker 3) | L4 fix1 NO BUGS | no handoff needed |

---
# Verdicts (condensed, append only)

## L1 | 1ff5794..48ad9d8 | NO BUGS after 3 rounds
- Allow-list/validation via `cau_hinh_ws._chuan_hoa` (code `ws_du_lieu_sai`); descriptions pinned over all combos; mandatory note shown.
- Fixed: BUG 1 (UI always sent wharton -> jargon error when priority=tier/per_person), BUG 2 (box not restored when switching back).
- Residual non-blocking: after a language switch, pending edits reset to saved values.

## L2 | 7162a5e..9613648 fix1 e36fc60 | NO BUGS after fix1
- Official readers filter trials (`loc_chinh_thuc`); full-table dump: a trial changes only run_history (+1 'thu') and ket_qua_thu.
- BUG 3 (FA refusal used saved rules not merged) and note (keys outside LUAT_XEP_MAC_DINH accepted) fixed and re-verified.

## L3 | 5ae7003..1cca309 | NO BUGS (208 passed, 7/7)
- 10-student fixture hand-recomputed (totals, cut-offs, per group/class) = API; changed list == direct SQL diff on 3 datasets;
  self-vs-self 0; stale official -> gt2_so_sanh_lan_cu; exports write nothing; HTML escaped/offline; CSV BOM; test diff insert-only.
- Notes: HTML export Vietnamese only; student list via admin API ungated until GT3 I1.

## L4 | 0f157e0..20f396d | 1 BUG (minor) (214 passed, 7/7)
- OK: saved==trial effective on 7 sets; next official luat_xep + match_results == direct-save twin; apply writes only
  workspace_settings; max_tests kept; bad/official ids -> gt2_lan_chay_khong_co, no writes; FA/wharton fine; confirm bar plain
  words, cancel writes nothing.
- BUG 4: `ap_dung_tieu_chi` saves normalised `luat_xep_hieu_luc` != what the L1 panel stores.
  A: trial priority=tier -> apply -> tier_mode="strict" (L1 keeps "reserve"); panel back to score + save keeps strict = hard groups.
  B: trial score+tier/reserve/tiers=[A,B] -> apply -> priority="score", tiers=[] (typed groups erased).
  Expected: keep raw criteria for inert keys; assert `luat_xep_hieu_luc(saved) == trial's effective`. Results unaffected.

## L4 fix1 | 20f396d..a41f7bc | NO BUGS (217 passed, 7/7)
- BUG 4 fixed: `_luat_ap_dung` starts from saved rules, overrides only active keys, keeps saved priority when equivalent.
- Brute force 28 valid saved x 28 trial rule sets (784 pairs): effective(saved after apply) == trial's, result valid for
  cau_hinh_ws, saved already-equivalent => unchanged. End-to-end (tier / score+tier strict / per_person): equal effective,
  apply changes only workspace_settings, next official match_results == direct-save twin, luat_xep == trial's.
- `gt2_ap_dung_khong_khop` forced via patch: not ok, config unchanged, vi/en plain, in i18n_loi.js.
- Not exercised: trial with Wharton/FA ON (datasets lack profiles; trial refused by existing codes).
