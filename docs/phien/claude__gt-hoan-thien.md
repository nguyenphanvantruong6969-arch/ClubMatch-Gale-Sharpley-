# Branch handoff: claude/gt-hoan-thien

> Fresh session: read CLAUDE.md, then `docs/ke_hoach/gt/GT4_HOAN_THIEN.md` (lot specs, rules, decisions), then THIS file.
> English. Cap 150 lines. WRITER owns this file (rewrites "Lot ledger"/"Current state", appends "Session log").
> CHECKER never edits this file; it writes `docs/phien/claude__gt-hoan-thien__tester.md` only. No lead session.

Status: IN PROGRESS   (writer sets `DONE <sha> CI green <date>` at the very end)

## Feature / goal
GT4: fix the problems found by the review of `claude/gt-tich-hop` (`docs/ke_hoach/gt/GT4_RA_SOAT.md`, R0-R10) without touching
the allocation core. Base: `origin/claude/admiring-fermat-yf077m` (= `claude/gt-tich-hop` c9e3830 + plan files). Truong merges to
`main` himself. No PR.

## Sessions (exactly two; nobody creates more sessions or subagents)
| Role | Model | Session id | Notes |
|---|---|---|---|
| writer | Sonnet | session_01VfPzNuryTWQ7HDGsXwVf1g | writes code/tests, owns this file |
| checker | Sonnet | (fill at start) | reviews + plays the user in Chromium, owns `__tester.md` |

## Lot ledger (writer updates; states: TODO / READY <sha> / FIX / CHECKED <sha> / BLOCKED <why>)
| Lot | State | Head sha | Round | Note |
|---|---|---|---|---|
| L0 official-only reader (R0) | READY 9546761 | 9546761 | 1 | `_giai_trinh_dung_lai` now filters via loc_chinh_thuc; test fails on old code (4/4). Try: other readers of run_history (list in CHANGELOG), trial then lookup/slip. |
| L1 audit log hygiene (R1) | READY 5605535 | 5605535 | 1 | lookup rows: only student_id (guarded: real id only), nguoi/vai NULL; `ma` hidden everywhere; get_giai_trinh_hoc_sinh logged. Try: scan nhat_ky CSV after wrong/right codes, teacher view = 1 row. |
| L2 controls match the role (R3) | READY 8316d81 | 8316d81 | 1 | vao_che_do_hoc_sinh now quan_tri; data-quyen on GT3 buttons + create-student row, btnChayVong2, wharton save, reset/delete student. Sweep test fails on old code. Skipped: JS-generated list buttons (xu_ly_khieu_nai, tra_loi_moi). Try: teacher walk-through of every tab. |
| L3 account setup + recovery (R2, R4) | READY d824937 | d824937 | 1 | retype+show/hide in 3 forms, next-steps card, warning; `main.py --xoa-tai-khoan` (recovery.chay_xoa_tai_khoan_dong_lenh) + QUEN_MAT_KHAU.bat, copied by build_windows.bat + workflow. Exe/bat NOT testable on Linux. Try: wrong confirmation, no-path default scan of workspaces. |
| L4 explanations cannot be misread (R5, R6) | READY bceb2f5 | bceb2f5 | 1 | RESERVED rows: no numeric cut, cell 'Chỗ dành riêng' + fixed sentence fa_ly_do.CAU_GIU_CHO; giong arg (default byte-identical, teacher panel = neutral); kq_desc reworded; CA_MAU.md + GOI_MINH_CHUNG regenerated. Try: slip vs panel vs student screen for a RESERVED student. |
| L5 student screen + lookup placement (R9) | READY 6ecf9cb | 6ecf9cb | 1 | labels, school name (no logo field in workspace), lang toggle, Enter, focus, countdown (backend gives `giay`), row click, jump link, 4-step helper (admin only), new `mo_tep` API (allow-list of ext, export roots) + button. Try: lock out a student id and watch the countdown; click a results row; export slips then 'Mở tệp'. |
| L6 readable audit log (R7) | READY f59862a | f59862a | 1 | log in its own tab; dictionary nkhd_* (all 87 logged functions) vi+en; select/refused-only/date (server side, gt4_ngay_sai); null actor = 'Học sinh tự tra cứu'; CSV stays raw. Try: change language while the log tab is open; unknown action shows raw name. |
| L7 criteria + comparison polish (R8) | TODO | | 0 | |
| L8 stretch: vocabulary-aware sentences | TODO | | 0 | |
| Gate: ruff + kiem_nhanh + tests + CI green | TODO | | 0 | |

## Current state (overwrite each handoff)
- Done so far: L0-L6 READY.
- In progress:
- Tests: baseline on the base commit = `tests/test_gt*` + `tests/test_giao_dien_gt*` green, ruff clean, kiem_nhanh 7/7.
- Open problems:

## Needs Truong (writer appends, each with a recommendation)
1. Windows `.exe` + `QUEN_MAT_KHAU.bat` recovery cannot be tested on Linux (L3). Recommend: Truong tries it once on Windows.
2. Existing DBs used before GT4 may hold lookup codes in old audit rows (append-only). Recommend: regenerate all codes before real use.
(carry-overs from `claude__gt-tich-hop.md` Needs Truong 1-10 stay open.)

## Decisions and gotchas
- D4-1..D4-5 in the spec. Rounds per lot: max 3, then BLOCKED + move on.
- Reproduction of R0 (49/120 students mismatch after a trial) is the failing test of L0.

## Next steps (ordered)
1. Writer: set up venv, baseline, L0 ... L7 (L8 if time), gate. 2. Checker: review each READY lot, then final persona walk-through.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Sonnet (reviewer) | review of gt-tich-hop; plan + prompts written | files: GT4_RA_SOAT.md, GT4_HOAN_THIEN.md, GT4_PROMPT_*.md |
