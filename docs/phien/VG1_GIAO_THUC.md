# VG1 protocol (size M: coder + auto-spawned checker, NO lead) — from `_GIAO_THUC_GON.md`

> Source of work: `docs/phien/claude__charming-cray-2izyn6.md` (decisions D1–D5, lots L1–L4). Branch: `claude/charming-cray-2izyn6`.
> Truong's EXCEPTION (2026-11-27): CLAUDE.md rule 10 is lifted for this item ONLY: the coder spawns the checker session itself and loops until CI is green.
> Mechanics (message formats, quiet tests): `GT_GIAO_THUC.md` §7–8 with writer = coder. Where they differ, THIS file wins.

## 0. FULL AUTO (Truong, 2026-11-27): never wait for Truong's input; never end a turn with work or CI pending
- Every question has a default: pick the SAFER option (old behaviour kept, nothing deleted), write one line in the branch file "Decisions", go on.
- "Needs Truong" is a NOTE, never a stop: record it, finish everything else, continue the loop.
- To wait for CI or the checker do NOT end the turn idle: schedule a wake-up (`send_later` 6–10 min, or `ScheduleWakeup`/`Monitor` if present) and
  resume from the branch file. The only legal stop is §4 step 4 (green) or the usage limit.

## 0b. Decisions (do not ask Truong)
- Everything in the branch file "Decisions" D1–D5. No new library. No schema change (only a `dk_cai_dat` key).
- Defect 7 is out of scope. Anything outside L1–L4, an invariant conflict, or the L4 export check failing → "Needs Truong" line, continue.

## 1. Roles (exactly 2 sessions; no other agents)
| Role | Model | Does | Never |
|---|---|---|---|
| coder | Sonnet `claude-sonnet-5-5` | per lot: failing test → minimal code → related tests → CHANGELOG/TIEN_DO → commit `VG1-L<n>: …` → push; at each milestone spawns/messages the checker; runs the CI loop (§4) | marks own lot passed; edits CLAUDE.md invariants |
| checker | Opus `claude-opus-5-5` | reviews the milestone diff, runs related tests + own edge cases, writes verdict to `docs/phien/claude__charming-cray-2izyn6__checker.md` (the ONLY file it pushes), then `send_message` to the coder | edits product code or tests |
- The coder creates the checker ONCE at MILESTONE 1 with `create_session` (same repo, `source_revision` = this branch, `model: claude-opus-5-5`,
  prompt = §5), and reuses it with `send_message` at MILESTONE 2 and for every CI-fix re-review. Messages are one line: `REVIEW <k> <base>..<head>`;
  reply `CHECKER REPORT <k> NO BUGS | BUGS n (see file)`. Checker is auto-started by the coder (Truong never pastes anything); blocked item → note in branch file, continue.

## 2. Per-lot loop (coder)
1. Read branch file + the functions named (grep by name, `sed -n` ≤ 80 lines).
2. Write the lot's failing tests first; run only them + ≤ 3 related (`-q --tb=line | tail -15`).
3. Minimal code. Invariants: default config unchanged (new params default to old behaviour); `{ok,data,errors}` contract; errors only via `i18n_errors.py`.
4. UI lots: one Chromium file `tests/test_giao_dien_vg1.py`, one shared page fixture. Playwright is not in system python:
   `pip install playwright` matching the preinstalled browser, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
5. `.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10` must be 7/7; then commit + push; update "Current state".
- Max 2 FIX rounds per checker finding, then "Needs Truong" + `git revert` of that lot.

## 3. Checker (2 milestones) checks
- Every lot's boxes; invariants 1, 4, 5, 6, 7; ORIGINAL spelling of names/IDs preserved after normalisation.
- Security: lock cannot be bypassed by spelling variants; no PIN in logs/audit/errors; export denied to teacher/student; `xac_nhan` enforced.
- Back-step: data never deleted except the confirmed rejected-club wishes; `han_chot` cleared; forward jump cannot skip a gate.
- L4: close buttons truly `disabled` (keyboard too) while the constraint fails; auto-close at deadline then refuses to approve a non-Tự do club; turning OFF without `xac_nhan_rui_ro` fails and the risk text is shown.
- 3 own edge cases per milestone (e.g. 0 students, name with double space, session with only a rejected Tự do club, setting OFF then ON).

## 4. Final gate = CI LOOP (coder, after MILESTONE 2 is NO BUGS) — repeat until green
1. All 8 repro tests green; `python -m pytest -q tests/test_va_gap_tai_hien.py tests/test_dk3_api.py tests/test_dk4_l0b_khoa_dang_nhap.py tests/test_dk9_nap_excel.py tests/test_dk8_l1_dem_cong_khai.py`.
2. Push; read GitHub Actions `tests.yml` (incl. coverage ≥ 85 %) and `Build Windows executable (rbda-kiosk)` for the head commit (failed_only, ≤ 60 lines).
   Wait for the run to FINISH (never judge a cancelled/in-progress run). Use `subscribe_pr_activity` only if a PR exists; otherwise re-read Actions.
3. Red → find root cause, test first, minimal fix, related tests, push, `send_message` the checker `REVIEW CI-<n> <base>..<head>` for the fix, go to 2.
   No cap on CI rounds. Never skip, delete or quarantine a test, never loosen an assertion to pass, never push an empty commit.
4. Green on BOTH workflows → write branch file "Current state" (what is fixed, what is left = defect 7, `soat-ma` report, CI run ids) and stop.
- Usage limit near: update "Current state" with the exact next step, stop; a resumed session continues the loop from the branch file.

## 5. Checker prompt (coder pastes it into `create_session`)
"You are the CHECKER (Opus) for item VG1 on branch claude/charming-cray-2izyn6. Reply in Vietnamese only inside the verdict file. Read CLAUDE.md,
docs/phien/claude__charming-cray-2izyn6.md and docs/phien/VG1_GIAO_THUC.md §3. When the coder messages `REVIEW <k> <base>..<head>`: review that diff,
run the related tests, add 3 edge cases of your own, write the verdict (per-lot PASS/BUGS with file:function and a failing repro) to
docs/phien/claude__charming-cray-2izyn6__checker.md, push ONLY that file, then send_message the coder `CHECKER REPORT <k> NO BUGS` or `BUGS n`.
Never edit product code or tests. No subagents. Wait for the next message after each report."
