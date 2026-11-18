# Branch handoff: claude/gt2-tieu-chi (writer / impl)

> Purpose: a fresh writer session reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, docs/phien/claude__gt2-tieu-chi.md, then THIS file.
> Language: English. Lead session: session_01YVAyu3PPHv9SNntepRSLwh. Lot specs: docs/ke_hoach/gt/GT2_TIEU_CHI.md.

## Feature / goal
GT2 writer role: implement lots L1-L4 (criteria in plain words, trial runs, compare, adopt), one lot per `GO L<n>` from the lead.

## Plan (lead ticks after checker NO BUGS)
- [x] L1 Criteria in plain words (passed)
- [x] L2 Trial runs (passed; fix1 passed, lead ticked at 5ae7003)
- [~] L3 Compare two runs: code, UI, tests, docs pushed at 1cca309; `WRITER DONE L3` sent; awaiting REVIEW/FIX
- [ ] L4 Adopt a trial's criteria

## Current state (overwrite each handoff)
- L3 done and pushed (base 5ae7003, head 1cca309): `tieu_chi.so_sanh_lan_chay` + `dung_html_so_sanh`; API `list_lan_chay`, `so_sanh_lan_chay(run_a, run_b=None)`, `export_so_sanh_html`, `export_so_sanh_csv` in api_tieu_chi.py; UI panel `gt2ThuPanel` (index.html, js/15_tieu_chi.js, style.css, i18n.js keys gt2_thu_* / gt2_ss_*); error codes gt2_lan_chay_khong_co, gt2_so_sanh_lan_cu.
- Verified: tests/test_gt2_so_sanh.py 9, tests/test_giao_dien_gt2_thu.py 4, related run 99 files all pass, kiem_nhanh 7/7, ruff clean. Not run: full suite (CI).
- Extra fixes made in L3 commit: tests/test_ws_nhan.py GT2 code block (all gt2_* codes), index.html placeholder = catalog text, no `ORDER BY ... buoi` in SQL, no em dash in UI sentences.

## Decisions and gotchas
- Official run comparison only for the LATEST official run (match_results holds only that); older -> gt2_so_sanh_lan_cu.
- Only sessions present in both runs are compared. Cut-off = lowest club test score among admitted students who have one.
- `hidden` attribute is overridden by `display:grid/flex`: needs CSS `[hidden]{display:none}` per id (done for gt2ThuChon, gt2ThuNut).
- Repo checks that bite new UI/i18n: no dash joining sentences in i18n.js; index.html placeholder must equal the catalog; every new error code goes in tests/test_ws_nhan.py MA_MOI block.
- Local branch can end up detached/stale after session restart: `git checkout claude/gt2-tieu-chi` then merge origin before pushing.
- Env: .venv ready; .claude/phien_vai.json written (impl).

## Next steps (ordered)
1. Wait for `REVIEW L3` / `FIX L3` or `GO L4` from the lead (spec: "Lot L4" in docs/ke_hoach/gt/GT2_TIEU_CHI.md).
2. L4: button "Dung tieu chi nay..." saving a trial's `luat_xep` via `update_workspace_config` after a confirm showing the L1 description; tests/test_gt2_ap_dung.py; never copy trial results into match_results.

## Files touched (L3)
- tieu_chi.py, api_tieu_chi.py, index.html, js/15_tieu_chi.js, style.css, i18n.js, i18n_errors.py, i18n_loi.js
- tests/test_gt2_so_sanh.py, tests/test_giao_dien_gt2_thu.py, tests/test_ws_nhan.py
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md (303 files / 6.478 cases)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Sonnet (writer) | L1 implemented, tested, pushed, reported | context >200k, handed off |
| 2026-11-17 | Sonnet (writer 2) | L1 fix1+fix2 passed; L2 coded and tested (25 new), WIP committed | related-test run unfinished; context >200k, handed off |
| 2026-11-17 | Sonnet (writer 3) | L2 related run + fix1 passed; L3 coded, tested, pushed, reported | context >200k, handed off |
