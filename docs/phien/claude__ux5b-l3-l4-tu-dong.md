# Branch file: claude/ux5b-l3-l4-tu-dong (planned)

## Goal
Finish UX5B (Hick + Von Restorff) on tabs `Nhập nguyện vọng` and `Nhập điểm` (L3) plus teacher view and tests (L4),
then loop until CI is green. L1 and L2 are already on `claude/affectionate-lamport-595imn` (commit 8441218).

## Plan
- [x] B0 cut branch from origin/claude/affectionate-lamport-595imn; base CI was red (run #1443) -> fixed (UX5B-FIX-CI)
- [x] B1 merge origin/main: already up to date (main merged earlier, 3bd56d0); controls re-measured
- [x] B2 L3  - [x] B3 L4  - [ ] B4 checker PASS  - [ ] B5 soat-ma  - [ ] B6 CI green  - [ ] B7 handoff, ahead/behind "N 0"

## Current state
- B0-B3 done and pushed (L3 41cf5b3; L4 next commit). Now at B4: checker session to be created (id recorded below), then B5 soat-ma, B6 CI loop, B7 close.
- Judgement calls for Truong: (1) Hick budget counts controls outside list data (search result cards + pagination, ranking rows, club grids)
  and ignores the per-step "Sua" (Edit) buttons (step navigation, like a tab strip): admin 7, teacher 6 with one student open (before: 27/23).
  (2) Saving step 2 auto-opens step 3 when it exists (its reminders - "chia lai diem", "huy chuong da chinh" - live inside step 3).
  (3) Teacher keeps the old description line (they cannot create); admin gets "Tim hoc sinh, ...".
  (4) Scoring: while one club is open the list panel is hidden; "Danh sach" button returns (typed but unsaved scores are dropped, as on tab switch).
- Old tests changed only because the UI changed (open the right step first via tests/_mo_muc.py, wait grids as attached, T3-36 expects "Cham tiep").
- Env: venv /home/user/venv_ux5b, PLAYWRIGHT_BROWSERS_PATH=/home/user/pw (symlinks to 1243).
- Checker session id: (fill in)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | Wrote auto prompt + branch file | CI loop until green, safety stop on same root cause x3 |
| 2026-11-23 | Sonnet | B0 CI fix, L3, L4 implemented and pushed | tests: ux5b_l3 (13), ux5b_l4 (11) |
