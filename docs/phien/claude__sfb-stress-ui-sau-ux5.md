# Branch handoff: claude/sfb-stress-ui-sau-ux5

> Purpose: a fresh session reads CLAUDE.md, then THIS file, then `docs/phien/SFB_GIAO_THUC.md`, and continues without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Item code **SFB** (tentative; Truong to confirm it in the registry): bring the stress-test folder `tests_stress/b/` back to green after the UX4/UX5 UI redesign, fix the one REAL UI bug that folder exposed (UX5A dropdown menus cut off at 390 px), and clean up leftovers of the SF/UX5/UX1F merges. Team size M, one autonomous coder session (no lead), loop until CI is green and the PR is mergeable. Analysis and verified patch are in `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.md` and `.patch` (copied here from `claude/great-edison-6ry675`).

## Plan (ticked by the coder)
- [ ] L1 (must) test-side: apply `ST_B_SUA_GIAO_DIEN_MOI.patch` (review it), run each `tests_stress/b/test_*.py` separately; expect 64 of 65 pass (the 2 width tests wait for L2)
- [ ] L2 (must) product CSS: dropdown menus fit narrow screens (candidate in the memo) + a CI test in `tests/` + 3 screenshots for Truong; own commit so it can be reverted alone
- [ ] L3 (optional) cleanup: delete the two `__TU_CHAY.md` files, sync TIEN_DO/CHANGELOG/test count, stress screenshots no longer overwrite tracked PNGs
- [ ] L4 (optional) leftovers from SF: PDF export progress UI (`get_tien_do_xuat`), dedicated zip error code (ST-B-011)
- [ ] CI gate: all jobs green on head, PR `mergeable_state` = clean, 0 behind main, final status line printed

## Current state
- Branch cut from main 60142c8 (CI run #1522 on it: success). Only planning files added: this file, `SFB_GIAO_THUC.md`, the memo and the patch. No product or test code changed yet.
- `tests_stress/b/` is not in CI (`testpaths = ["tests"]`): 54 of 65 tests fail on main (root causes in the memo).
- Known unrelated flake: `test_a13_12_browser_host.py::test_tai_lai_trang_khong_tat_may_chu` failed once on Windows 8/9 (timing, 5 s sleep vs 2 s threshold). Rerun the job; do not change the threshold.

## Decisions and gotchas
- Truong wants the coder to run unattended until CI is green and the PR is mergeable; do NOT merge, do NOT open a second PR, push only to this branch.
- Do not commit `docs/phien/anh_st_b/*.png` (the stress tests overwrite these tracked files): `git checkout -- docs/phien/anh_st_b` before every commit.
- Run `tests_stress/b` files one by one or at most 2 in parallel (4-way parallel made `test_b4_chi_ban_phim_nhap_chay_xuat` flaky; it passes alone 3/3).
- UI folds that tests must open only if closed (never auto-open every `<details>`): `#qlTabCachXep` + `#ux1aNangCao` summary (mode cards), `#qlNutThem` menu (`#qlTabWh/Dc/Db/DuLieu`), `#clubFormThemTuyChon` (club id, reserve capacity), `#ux5bTaoMoi > summary` (new student), `#ux1bThemTom` (report/print menu).
- All numbers are SIMULATED data. Invariants 1-8 of CLAUDE.md are not touched by this item.

## Next steps (ordered)
1. Coder: follow `docs/phien/SFB_GIAO_THUC.md` section 3 (lots) and section 4 (CI loop).
2. Truong: look at the 3 screenshots from L2 (`docs/ke_hoach/ux/anh/sfb/`); if the bottom-sheet menu is not wanted, revert the L2 commit only.
3. Truong: close PR #32 without merging (its content is already in main); privacy decision on teacher class scoping stays a separate item.

## Files touched
- (none yet beyond planning files: `docs/phien/claude__sfb-stress-ui-sau-ux5.md`, `docs/phien/SFB_GIAO_THUC.md`, `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.md`, `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.patch`)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-24 | Sonnet | Planned item SFB: branch, branch file, protocol, memo and patch | no code |
