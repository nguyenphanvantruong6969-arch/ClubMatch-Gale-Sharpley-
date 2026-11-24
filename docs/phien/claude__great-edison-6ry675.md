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
- [x] Confirm CI of `main` at 60142c8: run #1522 = success
- [ ] Follow-ups listed under Next steps

## Current state
- `main` = 60142c8 (merge of #31). It contains: UX5 (#30), SF (A1-A5, B1-B10), UX1F (all 20 commits of `claude/ux1-tich-hop`; head is an ancestor of main).
- Verified locally on main (Chromium via Playwright, scratch venv): 64 tests pass (ux1f_l2/l3/l4, sf_a_4/5, ux1i_i3, xp1_luu_pdf_mot_em, xp1_phieu_pdf, xp1_hieu_nang); `tests_stress/a` `test_timing_scaled_book[*-3000]` passes (both modes). Not run: full suite (CI does), Windows.
- PR #32 unique content vs main: one test line (main already has an equivalent) + 4 CHANGELOG lines. Trial merge conflicts only in CHANGELOG.md and `tests/test_giao_dien_ux1f_l4_mot_o_chon_lop.py` (both trivial). Recommendation given to Truong: close #32, do not merge.
- Another session (`nootnoot0607`) also pushes to #32's branch and to this branch (5905217 was pushed by it). Do not assume this file's branch has only this session's commits.
- Self-running prompt files exist on `main`: `docs/phien/claude__great-edison-6ry675__TU_CHAY.md`, `docs/phien/claude__ux1-tich-hop-vao-main__TU_CHAY.md` (can be deleted).

## Decisions and gotchas
- Priority correction (Truong asked, 2026-11-24): the app is an offline Windows kiosk on a computer, not a phone. The 390 px menu overflow is a stress-test finding, low priority; 768 px (half-screen window, ~12 px clip) is more realistic. Recommended (NOT yet applied to the SFB files): demote SFB lot L2 from must to optional, keep L1 as the main work; if L2 is dropped, record the two width tests as a known limitation (no xfail, no delete). Waiting for Truong's yes to rewrite `SFB_GIAO_THUC.md` and `docs/phien/claude__sfb-stress-ui-sau-ux5.md` accordingly.
- SFB lot L2 (menu CSS for max-width 800px) is verified by measurement only (no off-screen element at 390/768/1280; both b4 width tests pass with it); NOT yet reviewed visually, and close-on-outside-click behaviour of the fixed bottom-sheet menu is unchecked. Truong should look at the 3 screenshots the coder saves.
- Truong approved (2026-11-24): the 5 new UX5B wordings, all six UX5B judgement calls, UX5 UI from six screenshots.
- UX4/UX5 fold fields behind closed sections, which breaks tests that fill/click them directly: "Thêm tuỳ chọn" (`#clubFormThemTuyChon` -> `#clubFormId`), tab `#qlTabCachXep` + "Tuỳ chỉnh thêm" (`#ux1aNangCao` -> `#ux1aHuyChuong`), `#ux5bTaoMoi > summary` -> `#newStudentId`, `#ux1bThemTom` -> `#btnUx1bPhieuLop`/`#btnUx1bBaoCaoPdf`. Open the fold only if closed.
- `tests_stress/b/` is NOT in CI (not in testpaths) and was written for the old UI: 54 of 65 tests fail on main (19 of them in `test_b2_quan_ly.py`); see the memo; other files in that folder not run. Cause inferred (not checked per test): fields hidden behind UX4/UX5 folds; two sibling tests in CI failed for exactly that and passed once the fold was opened. Truong was asked whether to inspect each of the 19 or leave it to the next session (no answer yet); Truong said it is fine to leave everything visible in the handoff.
- `test_a13_12_browser_host.py::test_tai_lai_trang_khong_tat_may_chu` failed once on Windows 8/9 in run 45302117321; passed in #32's run; browser_host.py unchanged by the PR -> likely timing flake (not proven).
- CI cancels the previous run on every push; full matrix ~12-20 min; push once per round.
- All numbers are SIMULATED data.

## Next steps (priority order)
1. Ask/confirm Truong: close PR #32 without merging. Tell the other session to stop work on it.
2. Check CI of `main` (run for 60142c8); if red, read failed job logs and fix on a new branch.
3. DONE (planned, not coded): item SFB is planned on branch `claude/sfb-stress-ui-sau-ux5` (branch file `docs/phien/claude__sfb-stress-ui-sau-ux5.md`, protocol `docs/phien/SFB_GIAO_THUC.md`, cut from main 60142c8, commit 8127a0e). Truong starts ONE autonomous coder session there with: "Checkout branch claude/sfb-stress-ui-sau-ux5, read CLAUDE.md, the branch file and SFB_GIAO_THUC.md, run until CI green and PR mergeable, do not merge". Analysis behind it: `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.md` + `.patch`.
4. Truong decision (privacy): teachers are not class-scoped; any teacher can print every class's slips (with lookup codes). Keep as is, or add per-class teacher scoping as a new item.
5. Truong hand-tests UX3/UX4/UX5 UI (marked "chờ Truong thử tay"); decide `claude/ux1-tich-hop` is now fully merged (it is an ancestor of main).
6. Optional SF leftovers: progress-bar UI for `get_tien_do_xuat`, dedicated zip error code (ST-B-011), pypdf now in requirements-dev (done by UX1F).

## Files touched
- Added this turn: `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.md` (analysis: 54/65 tests_stress/b fail, causes, verified fixes, 390 px menu overflow bug + CSS candidate) and `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.patch` (test-only diff, applies on main; NOT applied to repo).
- Docs/tests only by this session: docs/phien/*__TU_CHAY.md, tests/test_giao_dien_sf_b_lo2.py and lo5, tests_stress/b/test_b2_quan_ly.py (`_vao_clb`), CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md (test-file count), style.css (kept both blocks in merges), docs/phien/claude__ux5b-l3-l4-tu-dong.md (ticks and approvals).
- No product code changed by this session except conflict resolution carried by other sessions (xuat_pdf.py kept UX1F layout + SF-A5 speed).

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | Status reports; PRs #29/#30 recorded; UX5B approvals and ticks | docs only |
| 2026-11-24 | Sonnet | PR #31 (SF+UX5 merge, test fixes), PR #32 (UX1F), CI diagnosis, self-run prompts, deep check that #32 is redundant | context over 400k, handoff written |
| 2026-11-24 | Sonnet | Explained the 19 failing tests_stress/b tests to Truong; handoff refreshed | context still over 400k; no new work |
| 2026-11-24 | Sonnet | Proposed how to fix the 19 tests_stress/b failures (option 1, recorded in Next steps) | handoff refreshed again; no new work |
| 2026-11-24 | Sonnet | Deep analysis of tests_stress/b (all 65 run), verified test fixes, found real 390 px menu overflow bug, saved memo+patch | context far over 400k; no product code changed |
| 2026-11-24 | Sonnet | Planned item SFB (branch, branch file, protocol with CI loop, optional checker prompt); main CI #1522 confirmed green | no product code; code `SFB` is tentative, Truong to confirm |
| 2026-11-24 | Sonnet | Answered whether the SFB prompt fixes the menu (yes via lot L2, verified by measurement, not visually) | no code |
| 2026-11-24 | Sonnet | Sent Truong before/after screenshots of the 390 px menu fix (bottom sheet, page visible behind, button detached); awaiting Truong's look | images only in the session scratchpad, not in repo; the coder re-creates 3 screenshots in SFB L2 |
| 2026-11-24 | Sonnet | Admitted the 390 px phone framing was overweighted; recommended demoting SFB L2 to optional | no files of SFB changed yet |
