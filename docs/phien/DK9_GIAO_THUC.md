# DK9 protocol — size M, AUTO (coder Sonnet runs its own checker session; NO human input)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 token rules apply; do not copy). Plan, design, acceptance:
> `docs/phien/claude__dk9-nap-excel-cong.md`. Truong (2026-11-26) authorised the whole loop below in advance.

## 0. Rules (never ask Truong; he is not watching)
- Allowed: new `api_dang_ky_excel.py` (+ its hook-up in the portal API class and `phan_quyen.py`), `i18n_errors.py` (append
  at the END) → `python tao_i18n_js.py`, `js/dang_ky_quan_tri_2.js`, portal CSS (`.dk-*`), new tests, docs.
  NOT allowed: schema/CSV change, new library, allocation code, the main app's look. → "Needs Truong" line, skip, continue.
- Branch `claude/dk9-nap-excel-cong`. Before each lot fetch and merge (`--no-edit`) `claude/dk8-giong-ban-mau` and `main`.
  Never rebase, force-push, tag, release, merge into main or open a PR. Max 2 FIX rounds, then "Needs Truong".
- Blocked by an error you cannot fix in 3 tries → note it, move on. Never stop to ask.

## 1. Coder loop per lot (L1 → L2 → MILESTONE)
Failing test from the lot's boxes → minimal code → lot test + ≤ 3 related (`-q --tb=line 2>&1 | tail -15`; related: the
`tests/test_dk3_api.py`, `tests/test_giao_dien_dk3_cong.py`, `tests/test_giao_dien_dk8_l2.py`) → grep tests for every
changed UI text → `ruff check .` → `git fetch origin main` then `.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10`
(7/7) → CHANGELOG (`head -20` only) + TIEN_DO row `DK9-L<k>` → commit `DK9-L<k>: …` → update "Current state" → push.
Wait for CI with `send_later` (25 min), never poll; read `failed_only` logs ≤ 60 lines; red → fix, never skip/disable/weaken a test.

## 2. Milestone = automatic checker (once, after L2, CI green on the head)
1. Write `MILESTONE 1 READY | head <sha> | base 1bb488d` in the branch file, push.
2. `create_session` (sonnet, same repo, `source_revision` and `outcome_branch` = this branch) with the CHECKER prompt of
   §3 (permission IN the initial prompt). Wait with `send_later` 30 min until the verdict (message or
   `docs/phien/claude__dk9-nap-excel-cong__checker.md`). FIX → fix, push, CI green, new checker session (round 2).
   If `create_session` is unavailable: run the §3 checks yourself, write "self-checked" in the checker file.
After PASS: `soat-ma` four tiers (report only), registry row DK9, test-file count, final CI gate (`tests.yml`) →
`Status: DONE <sha> CI green <date>` and a 5-line Vietnamese summary for Truong at the top of the branch file.

## 3. Prompts
**Coder** (new Sonnet session, auto mode, branch `claude/dk9-nap-excel-cong`):
```
You are CODER for DK9 (size M, AUTO) on branch claude/dk9-nap-excel-cong. Read CLAUDE.md, then docs/phien/DK9_GIAO_THUC.md
and docs/phien/claude__dk9-nap-excel-cong.md and follow them exactly. Truong authorised the whole loop in advance and is not
watching: never ask, never wait for him. Set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt); Chromium is at /opt/pw-browsers/chromium. Do L1 (tests first), L2, then the milestone (start the
checker session yourself), CI gate, DONE. Blocked parts go under "Needs Truong". Reply in Vietnamese.
```
**Checker** (started by the coder with create_session; fill the <> fields):
```
You are CHECKER for DK9 milestone 1 on branch claude/dk9-nap-excel-cong. Truong authorised this review: you may commit and
push ONLY docs/phien/claude__dk9-nap-excel-cong__checker.md; never edit product code or tests; no PR/merge/tag. Read
CLAUDE.md, the branch file and docs/phien/DK9_GIAO_THUC.md. Review <base>..<head>. Set up the venv. Run
tests/test_dk9_nap_excel.py, tests/test_giao_dien_dk9_l2.py and tests/test_giao_dien_dk8_l*.py (tail only). Check against
the Acceptance list: preview writes nothing (count DB rows before/after); re-upload keeps student PINs; error rows listed
with row numbers while valid rows load; teacher/student tokens refused; own edge cases (numeric cells like 10001.0, blank
rows between data, header typo, 5 001 rows, a .csv renamed .xlsx, diacritics in names); no test assertion weakened; main
app untouched (index.html, non-.dk CSS); no schema/CSV/allocation diff; error messages only via i18n_errors.py;
kiem_nhanh 7/7; CI green on <head> (never PASS with CI pending). Take ≤ 3 screenshots of the new block. Write PASS or
FIX ≤ 10 lines in the checker file, push it, then send_message one line with the verdict to <coder session id>. Reply in Vietnamese.
```
