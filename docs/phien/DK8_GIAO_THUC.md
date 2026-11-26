# DK8 protocol — size M, AUTO (coder Sonnet runs its own checker sessions; NO human input)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 token rules apply; do not copy). Plan, gaps, acceptance:
> `docs/phien/claude__dk8-giong-ban-mau.md`. Truong (2026-11-26) authorised the whole loop below in advance.

## 0. Rules (never ask Truong; he is not watching)
- UI only: `dang_ky.html`, `js/dang_ky_*.js`, portal CSS (`.dk-*` in `style.css` or new `dang_ky.css`), new tests,
  `du_lieu_test/chup_dk8.py`, docs. Backend only for read-only COUNTS in `dk_trang_thai` (L1). No schema/CSV change, no new
  library, no algorithm change. Anything else → "Needs Truong" line in the branch file, skip it, continue.
- Branch `claude/dk8-giong-ban-mau`. Before each lot merge the three bases (branch file). Never rebase, force-push, tag,
  release, merge into main or open a PR. Max 2 FIX rounds per milestone, then "Needs Truong" + `git revert` of the
  failing part only if it breaks tests; otherwise leave it and note it.
- Blocked by an error you cannot fix in 3 tries → note it, move to the next lot. Never stop to ask.

## 1. Coder loop per lot (L1 → L2 → M1 → L3 → [L4] → [L5] → M2)
Failing test from the lot's boxes (one Chromium test file per lot: `tests/test_giao_dien_dk8_l<k>.py`, one shared page
fixture) → code → lot test + ≤ 3 related (`-q --tb=line 2>&1 | tail -15`) → grep tests for every changed UI text →
`ruff check .` → `.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10` (7/7) → CHANGELOG (`head -20` only) + TIEN_DO
row `DK8-L<k>` → commit `DK8-L<k>: …` → update "Current state" → push.
Wait for CI with `send_later` (25 min), never poll; read `failed_only` logs ≤ 60 lines; red → fix, never skip/disable/
weaken a test.

> L5 (optional, added 2026-11-26): portal input feedback; spec in the branch file Plan. Same loop, lot test `tests/test_giao_dien_dk8_l5.py`.

## 2. Milestones = automatic checker
At M1 (after L2) and M2 (after L3/L4), once CI is green on the head:
1. Write `MILESTONE <k> READY | head <sha> | base <sha>` in the branch file, push.
2. `create_session` (model sonnet, same repo, `source_revision` and `outcome_branch` = this branch) with the CHECKER
   prompt of §3, filling <k>, <base>, <head> and YOUR session id. The permission must be IN that initial prompt.
3. Wait with `send_later` 30 min (re-schedule until the verdict). Verdict arrives by `send_message` or in
   `docs/phien/claude__dk8-giong-ban-mau__checker.md`. FIX → fix, push, CI green, new checker session for the same
   milestone (round 2). PASS → continue. If `create_session` is not available: run the §3 checks yourself, write
   "self-checked (no checker session)" in the checker file.
After M2 PASS: `soat-ma` four tiers (report only), registry row DK8, test-file count, final CI gate (`tests.yml` +
*Build Windows executable* if it runs on push) → `Status: DONE <sha> CI green <date>` and a 5-line Vietnamese summary
for Truong at the top of the branch file.

## 3. Prompts
**Coder** (paste into a new Sonnet session, auto mode, branch `claude/dk8-giong-ban-mau`):
```
You are CODER for DK8 (size M, AUTO) on branch claude/dk8-giong-ban-mau. Read CLAUDE.md, then docs/phien/DK8_GIAO_THUC.md
and docs/phien/claude__dk8-giong-ban-mau.md and follow them exactly. Truong authorised the whole loop in advance and is not
watching: never ask, never wait for him. Set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt); Chromium is at /opt/pw-browsers/chromium. Do L1, L2, milestone 1 (start the checker session
yourself), L3, optional L4, milestone 2, CI gate, DONE. Blocked parts go under "Needs Truong". Reply in Vietnamese.
```
**Checker** (started by the coder with create_session; fill the <> fields):
```
You are CHECKER for DK8 milestone <k> on branch claude/dk8-giong-ban-mau. Truong authorised this review: you may commit and
push ONLY docs/phien/claude__dk8-giong-ban-mau__checker.md; never edit product code or tests; no PR/merge/tag. Read
CLAUDE.md, the branch file and docs/phien/DK8_GIAO_THUC.md. Review <base>..<head>. Set up the venv. Run the lot test files
plus tests/test_giao_dien_dkl_*.py tests/test_giao_dien_dk6_*.py tests/test_giao_dien_dk5_toan_trinh.py (tail only).
Run du_lieu_test/chup_dk8.py and look at ≤ 6 screenshot pairs against the acceptance list. Check: no test assertion
weakened (diff of tests/), main app look unchanged (index.html/non-.dk CSS untouched), dk_trang_thai exposes counts only,
medal override still reachable for students, auto-refresh guards intact, kiem_nhanh 7/7, CI green on <head> (never PASS
with CI pending). Write PASS or FIX <=10 lines in the checker file, push it, then send_message one line with the verdict
to <coder session id>. Reply in Vietnamese.
```
