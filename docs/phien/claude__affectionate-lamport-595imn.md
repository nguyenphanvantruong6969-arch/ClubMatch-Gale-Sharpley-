# Branch handoff: claude/affectionate-lamport-595imn

> Read CLAUDE.md, then THIS file. English. Cap 150 lines. Reply to Truong in Vietnamese.

## Goal
Get CI fully green on the tip of this branch AND make the branch mergeable into `main` (no conflicts, CI green after
merging `main` in). Task type: CI debugging only. This is NOT feature work: do not start UX5B L2-L4 (see "Out of scope").
Do NOT open a PR and do NOT merge unless Truong says so explicitly in chat.

## Branch facts (2026-11-22, 16:20 UTC)
- Tip: `ba1e4ac` = merge of `origin/claude/ux5a-ket-qua-de-hieu` into the UX5B-L1 docs commit `0d02f6a` + one test fix.
- Content on top of `edf7526`: UX5B-L1 docs (audit, words table; no code) + all 16 UX5A fix commits.
- Relation to `main` (`2b5a87e`, MT2 merged as PR #28): 28 commits ahead, 43 behind.
  A trial `git merge --no-commit origin/main` (aborted) conflicts in: `CHANGELOG.md`, `docs/ke_hoach/CLAUDE_CHI_TIET.md`,
  `docs/ke_hoach/TIEN_DO.md` (docs: keep both sides) and **`index.html`, `style.css`** (real code: MT2 "Chia CLB theo
  loai" vs UX4/UX5A edits). Resolve those two by hand, keeping both features; run the related Chromium tests.
- Sibling branches: `claude/ux5b-nap-xep-nhap-tay` (same tip as `0d02f6a`, still red), `claude/ux5a-ket-qua-de-hieu`
  (green at run #1400, not in `main` yet). Do not push to them.

## What was found and fixed (run #1401, sha 0d02f6a, red on Linux 1-6 and Windows 3, 5)
Root cause: branch forked before the UX5A fixes; the UX4 base has new words ("So cho", "Mot buoi chung") while tests
want the old ones (Truong chose B2: keep "Chi tieu" / "Suat uu tien"). Failing tests, all fixed by the UX5A merge:
`test_giao_dien_ux2_nut`, `ux1_nhap_so`, `sg2_diem_quyet_tam`, `t3_l3`, `fa_quan_ly`, `ux1_tiep_theo`, `fg8_cau_chu`,
`test_t3_l1_chu_du_phong`, `test_a13_12_tai_lieu` (counts test files in docs).
Separate race fixed in `tests/test_giao_dien_a13_10_nhan.py::test_nhan_moi_en_co_mat_nhan_cu_het`: the table re-renders
after an API call on language switch; the test now waits for "By test score" in `#adminDiemChuanBlock`.

## Current state
- Run #1402 (sha `ba1e4ac`) was in progress at 16:20 UTC; result unknown when this file was written. Read it first.
- Local checks before the push: 63 + 14 related tests green, `ruff check .` clean, `kiem_nhanh.py` 7/7.
- Not done: full suite (CI only), the four manual tiers of the `soat-ma` skill, merging `main` in.

## Plan (tick as you go)
- [ ] 1. Read run #1402 for `ba1e4ac`. Red: fix by root cause, loop (protocol below).
- [ ] 2. When green: merge `origin/main` into this branch (never rebase, never force-push), resolve the 5 conflicts.
- [ ] 3. Loop until CI is green on the merge commit (Linux 1-6, Windows 1-9, Lint, coverage job `do-phu` >= 85 %).
- [ ] 4. Report to Truong: green run URL, `git rev-list --left-right --count HEAD...origin/main` = `N 0`, conflict-free
      trial merge. Stop. Truong decides about PR and merge.

## Loop protocol (each round)
1. `actions_list` runs for this branch, take the newest. `in_progress`: wait via ScheduleWakeup (600-900 s), never a
   tight poll. A new push cancels the running CI of the branch, so batch your fixes before pushing.
2. `completed` + failure: `actions_list` jobs of that run, `get_job_logs` of each failed job (`tail_lines` 80-100 and
   search the `FAILED` / `short test summary` lines). Group failures by root cause before touching code.
3. Reproduce locally with ONLY the related test files (never the full 22-minute suite). Fix the cause, not the symptom.
4. Before push: related tests, `ruff check .`, `python .claude/skills/soat-ma/scripts/kiem_nhanh.py` (7/7). Add a
   `CHANGELOG.md` entry per fix. Commit with the attribution lines, `git push -u origin claude/affectionate-lamport-595imn`
   (retry network errors up to 4 times with backoff).
5. Max 6 rounds. After that, or when a failure needs a product decision, stop and report to Truong.

## Rules that bite here
- Never skip, delete or loosen a test to get green; never push an empty commit; never rewrite history.
- A flaky test: reproduce it 3 times locally, then fix with a condition wait (`wait_for_function`), not a sleep.
- Windows-only failures: look for backslash paths, open file handles, reserved names; check CI log, you cannot run Windows.
- CLAUDE.md invariants 1-8 hold. Default results byte-identical (`kiem_nhanh.py` checks 15 cases). No subagents.
- Never run `git stash` during a merge: it drops `MERGE_HEAD` (happened once; recovered by redoing the merge).

## Test environment (cloud container)
- `python3.11 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt` (`.venv` is untracked; do not add it).
- Python Playwright wants Chromium build 1255; the container has 1243 under `/opt/pw-browsers`. Make a folder with
  symlinks `chromium-1255` and `chromium_headless_shell-1255` pointing to the 1243 dirs, plus `ffmpeg-1011`, and set
  `PLAYWRIGHT_BROWSERS_PATH` to it. Do not run `playwright install`.
- Run: `python -m pytest -q -p no:cacheprovider -n 4 --no-cov <files>`.

## Out of scope
UX5B L2 (Xep CLB), L3 (Nhap nguyen vong, Nhap diem), L4 (teacher view + tests) wait for Truong's MILESTONE 1 approval of
`docs/ke_hoach/ux/UX5B_TU_NGU.md` (words + D1-D6). Handoff for that: `docs/phien/claude__ux5b-nap-xep-nhap-tay.md`.

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Sonnet | Diagnosed run #1401, merged UX5A, fixed EN label race, pushed `ba1e4ac` | run #1402 pending |
| 2026-11-22 | Sonnet | Trial merge of `main`: 5 conflicts (2 in code); wrote this handoff and the loop prompt | not pushed, to avoid cancelling #1402 |
