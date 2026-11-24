# Branch handoff: claude/great-edison-6ry675

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Integration/coordination branch for Truong (2026-11-23/24): report status of UX5, SF and UX1F work, open and unblock PRs into `main`, drive CI to green. PR #31 (this branch, "SF: fix stress-test bugs") is MERGED into `main` (60142c8). No registry item code of its own; item codes involved: SF, UX5A, UX5B, UX1F.

## Plan
- [x] Status report of UX5 / SF branches; record Truong approvals (UX5B six judgement calls, five new wordings, UI from screenshots)
- [x] PR #29 (SF) merged into `claude/happy-cerf-xvn495` only -> PR #31 brought SF + main(UX5) into `main` (MERGED)
- [x] PR #30 (UX5, `claude/ux5b-l3-l4-tu-dong`) MERGED into `main`
- [x] PR #32 (UX1F, `claude/ux1-tich-hop-vao-main`): CI green (run 45328982869 at 5818ce3) but now `dirty`; its content is already in `main` via #31 (verified, see below)
- [ ] Close PR #32 without merging (Truong has not said yes yet)
- [ ] Confirm CI of `main` at 60142c8 (run #1522 was still in progress when last seen)
- [ ] Follow-ups listed under Next steps

## Current state
- `main` = 60142c8 (merge of #31). It contains: UX5 (#30), SF (A1-A5, B1-B10), UX1F (all 20 commits of `claude/ux1-tich-hop`; head is an ancestor of main).
- Verified locally on main (Chromium via Playwright, scratch venv): 64 tests pass (ux1f_l2/l3/l4, sf_a_4/5, ux1i_i3, xp1_luu_pdf_mot_em, xp1_phieu_pdf, xp1_hieu_nang); `tests_stress/a` `test_timing_scaled_book[*-3000]` passes (both modes). Not run: full suite (CI does), Windows.
- PR #32 unique content vs main: one test line (main already has an equivalent) + 4 CHANGELOG lines. Trial merge conflicts only in CHANGELOG.md and `tests/test_giao_dien_ux1f_l4_mot_o_chon_lop.py` (both trivial). Recommendation given to Truong: close #32, do not merge.
- Another session (`nootnoot0607`) also pushes to #32's branch and to this branch (5905217 was pushed by it). Do not assume this file's branch has only this session's commits.
- Self-running prompt files exist on `main`: `docs/phien/claude__great-edison-6ry675__TU_CHAY.md`, `docs/phien/claude__ux1-tich-hop-vao-main__TU_CHAY.md` (can be deleted).

## Decisions and gotchas
- Truong approved (2026-11-24): the 5 new UX5B wordings, all six UX5B judgement calls, UX5 UI from six screenshots.
- UX4/UX5 fold fields behind closed sections, which breaks tests that fill/click them directly: "Thêm tuỳ chọn" (`#clubFormThemTuyChon` -> `#clubFormId`), tab `#qlTabCachXep` + "Tuỳ chỉnh thêm" (`#ux1aNangCao` -> `#ux1aHuyChuong`), `#ux5bTaoMoi > summary` -> `#newStudentId`, `#ux1bThemTom` -> `#btnUx1bPhieuLop`/`#btnUx1bBaoCaoPdf`. Open the fold only if closed.
- `tests_stress/b/` is NOT in CI (not in testpaths) and was written for the old UI: 19 tests in `test_b2_quan_ly.py` fail on the merged tree; other files in that folder not run.
- `test_a13_12_browser_host.py::test_tai_lai_trang_khong_tat_may_chu` failed once on Windows 8/9 in run 45302117321; passed in #32's run; browser_host.py unchanged by the PR -> likely timing flake (not proven).
- CI cancels the previous run on every push; full matrix ~12-20 min; push once per round.
- All numbers are SIMULATED data.

## Next steps (priority order)
1. Ask/confirm Truong: close PR #32 without merging. Tell the other session to stop work on it.
2. Check CI of `main` (run for 60142c8); if red, read failed job logs and fix on a new branch.
3. New small item: update `tests_stress/b/` selectors to the UX4/UX5 folded UI (own branch + `docs/phien/<branch>.md`, Opus plans per CLAUDE.md rule 12).
4. Truong decision (privacy): teachers are not class-scoped; any teacher can print every class's slips (with lookup codes). Keep as is, or add per-class teacher scoping as a new item.
5. Truong hand-tests UX3/UX4/UX5 UI (marked "chờ Truong thử tay"); decide `claude/ux1-tich-hop` is now fully merged (it is an ancestor of main).
6. Optional SF leftovers: progress-bar UI for `get_tien_do_xuat`, dedicated zip error code (ST-B-011), pypdf now in requirements-dev (done by UX1F).

## Files touched
- Docs/tests only by this session: docs/phien/*__TU_CHAY.md, tests/test_giao_dien_sf_b_lo2.py and lo5, tests_stress/b/test_b2_quan_ly.py (`_vao_clb`), CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md (test-file count), style.css (kept both blocks in merges), docs/phien/claude__ux5b-l3-l4-tu-dong.md (ticks and approvals).
- No product code changed by this session except conflict resolution carried by other sessions (xuat_pdf.py kept UX1F layout + SF-A5 speed).

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | Status reports; PRs #29/#30 recorded; UX5B approvals and ticks | docs only |
| 2026-11-24 | Sonnet | PR #31 (SF+UX5 merge, test fixes), PR #32 (UX1F), CI diagnosis, self-run prompts, deep check that #32 is redundant | context over 400k, handoff written |
