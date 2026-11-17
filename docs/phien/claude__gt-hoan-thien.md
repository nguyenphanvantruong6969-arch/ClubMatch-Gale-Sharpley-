# Branch handoff: claude/gt-hoan-thien

> Fresh session: read CLAUDE.md, then `docs/ke_hoach/gt/GT4_HOAN_THIEN.md` (lot specs, rules, decisions), then THIS file.
> English. Cap 150 lines. WRITER owns this file (rewrites "Lot ledger"/"Current state", appends "Session log").
> CHECKER never edits this file; it writes `docs/phien/claude__gt-hoan-thien__tester.md` only. No lead session.

Status: IN PROGRESS (L0-L7 READY, waiting for checker)   (writer sets `DONE <sha> CI green <date>` at the very end)

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
| L7 criteria + comparison polish (R8) | READY cc7aa23 | cc7aa23 | 1 | Layout redone with .club-field pattern; 2 columns >=1000px; compare view (summary, 2 run cards, deltas +/−, collapsed list, no __mac_dinh__); HTML export same structure; degenerate-config hint; .gt-ui rhythm for lookup/account/student screens. Screenshots before/after: docs/phien/anh_gt4/l7_{truoc,sau}_*_1280.png. Try: 1024px width, trial with priority=tier, EN language, multi-session dataset. |
| L8 stretch: vocabulary-aware sentences | TODO | | 0 | |
| Gate: ruff + kiem_nhanh + tests + CI green | TODO | | 0 | |

## Current state (overwrite each handoff)
- Done: L0-L7 all READY and pushed (see ledger shas). Ruff clean, kiem_nhanh 7/7 at last run. New tests: test_gt4_* (chay_thu_giai_trinh, nhat_ky, khoi_phuc, cau_giai_trinh, mo_tep, nhat_ky_doc, so_sanh) and test_giao_dien_gt4_* (vai, tai_khoan, giai_trinh, man_hoc_sinh, nhat_ky, tieu_chi).
- No checker file (docs/phien/claude__gt-hoan-thien__tester.md) existed at last fetch (~17:20 UTC 2026-11-17). A send_later was set for 17:40 UTC.
- Not done: L8 (only if L0-L7 CHECKED); GATE. At the gate also rebuild docs/giai_trinh GOI_MINH_CHUNG.docx/.pdf (`python docs/giai_trinh/tao_goi_minh_chung.py`) because HUONG_DAN_CHAY.md changed in L6.
- Open: JS-generated buttons (xu_ly_khieu_nai, tra_loi_moi) not hidden for teachers (refused + logged). Workspace has no logo field (student screen shows name only).

## Next steps (ordered)
1. git fetch origin claude/gt-hoan-thien; read the checker file; for each lot with BUGS set State=FIX, test first, fix, Round+1, commit `GT4-L<n> fix<k>: ...`.
2. If nothing pending: wait via send_later 20 min (give up after 6h from 17:20 UTC, note under Needs Truong).
3. GATE: ruff; kiem_nhanh --so-seed 20; all tests/test_gt*.py + tests/test_giao_dien_gt*.py; rebuild GOI_MINH_CHUNG; push; CI green (mcp__github__actions_list, tests.yml); set Status DONE; final Vietnamese summary + 3-5 manual steps (incl. Windows exe recovery) + AI-log draft.

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
| 2026-11-17 | Sonnet (writer) | L0-L7 implemented, tested, pushed; waiting for checker; handoff at ~400k context | branch claude/gt-hoan-thien |
