# Branch file: claude/ux5b-l3-l4-tu-dong (planned)

## Goal
Finish UX5B (Hick + Von Restorff) on tabs `Nhập nguyện vọng` and `Nhập điểm` (L3) plus teacher view and tests (L4),
then loop until CI is green. L1 and L2 are already on `claude/affectionate-lamport-595imn` (commit 8441218).

## Plan
- [x] B0 cut branch from origin/claude/affectionate-lamport-595imn; base CI was red (run #1443) -> fixed (UX5B-FIX-CI)
- [x] B1 merge origin/main: already up to date (main merged earlier, 3bd56d0); controls re-measured
- [x] B2 L3  - [x] B3 L4  - [x] B4 checker PASS (round 1 FIX x1, round 2 PASS)  - [x] B5 soat-ma  - [x] B6 CI green (run #1496 on 9540c7f: success)  - [x] B7 handoff, ahead/behind "N 0" (0 behind origin/main, 0 0 vs own remote before this docs commit)

## Current state
- B0-B5 done and pushed: checker PASS in round 2 (UX5B-FIX1 5a68872: unsaved-scores guard on the back button; its wording `ux5b_diem_chua_luu_canh_bao` is new text outside the approved table). B6 and B7 done (2026-11-23): CI run #1496 green on 9540c7f; branch is 0 behind origin/main and merges into main cleanly (git merge-tree). Plan complete; waiting on Truong for the six judgement calls below, then one PR into main.
- Truong approved the 5 new wordings (ux5b_tom_thi, ux5b_tom_nv, ux5b_tom_w, ux5b_tom_hc, ux5b_diem_chua_luu_canh_bao) on 2026-11-24 ("ok"). Calls (1)-(4) and (6) below not yet answered explicitly.
- Judgement calls for Truong: (1) Hick budget counts controls outside list data (search result cards + pagination, ranking rows, club grids)
  and ignores the per-step "Sua" (Edit) buttons (step navigation, like a tab strip): admin 7, teacher 6 with one student open (before: 27/23).
  (2) Saving step 2 auto-opens step 3 when it exists (its reminders - "chia lai diem", "huy chuong da chinh" - live inside step 3).
  (3) Teacher keeps the old description line (they cannot create); admin gets "Tim hoc sinh, ...".
  (4) Scoring: while one club is open the list panel is hidden; "Danh sach" button returns, asking once if scores are unsaved (FIX1).
  (5) New wording not in the approved table: summaries "4 CLB du thi" / "7 nguyen vong" / "diem quyet tam" / "huy chuong", EN "Score next", FIX1 warning. (6) The scoring-list Hick test measures 0 controls (all "Cham" buttons sit in tbody).
- Old tests changed only because the UI changed (open the right step first via tests/_mo_muc.py, wait grids as attached, T3-36 expects "Cham tiep").
- Env: venv /home/user/venv_ux5b, PLAYWRIGHT_BROWSERS_PATH=/home/user/pw (symlinks to 1243).
- Checker session id: session_01VfPzNrzpAVzD7j2CAfX6Xv (created 2026-11-23, reviews 8441218..b42cc57; coder session session_01VfPzNuDZRixo4pKedaMd5w)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | Wrote auto prompt + branch file | CI loop until green, safety stop on same root cause x3 |
| 2026-11-23 | Sonnet | B0 CI fix, L3, L4 implemented and pushed | tests: ux5b_l3 (13), ux5b_l4 (11) |
| 2026-11-23 | Sonnet | Checker round 1 FIX (unsaved scores), round 2 PASS; soat-ma report | CI loop next |
| 2026-11-23 | Sonnet | Ticked B6 (CI #1496 success) and B7 (0 behind main) | docs only; Truong asked for it |
| 2026-11-24 | Sonnet | Recorded Truong approval of the 5 new wordings | docs only |
