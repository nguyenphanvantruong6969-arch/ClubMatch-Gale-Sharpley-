# DC1 protocol (size S: one Sonnet coder, no lead, no checker)

> Lean rules: `docs/phien/_GIAO_THUC_GON.md` (budget §3 applies; not repeated here). Work spec, decisions D1–D6,
> gotchas, lots and acceptance: `docs/phien/claude__dc1-kiem-doc-lap.md`. Where they differ, THIS file wins.
> Truong asked for this session (CLAUDE.md rule 10/12 satisfied). Base: `origin/claude/dc1-kiem-doc-lap`.

## 0. Decisions already made (do not ask Truong again)
- Scope = option B: conservation checks only, one session, default (non-FA) workspace. No stability /
  priority-rule check, no lottery numbers, no hash recomputation. Option C is parked.
- No product code change, no export/CSV contract change (invariant 7), no new library (openpyxl already used).
- The script imports only the standard library + openpyxl; tests MAY use repo modules to build exports.
- The script prints facts and PASS/FAIL only; no commentary. All data is simulated.

## 1. Branch, lots
| Branch | Lots | Branch file |
|---|---|---|
| `claude/dc1-kiem-doc-lap` | L1 readers + K0–K6 → L2 table + `dau_vao_ket_qua.csv` → L3 docs → L4 (optional) K7 | `docs/phien/claude__dc1-kiem-doc-lap.md` |
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push.
- Commit per lot: `DC1-L<n>: …`; CHANGELOG (item DC1, files, new tests) + TIEN_DO row `DC1-L<n>` (`tail -5` only).

## 2. Role
| Role | Model | Does | Never |
|---|---|---|---|
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, docs, commit + push, ticks the Plan | edits product code, the registry, or other branches |
- One session. If usage is near the limit: finish the commit, update "Current state", stop (rule 9).
- Blocked (invariant conflict, need to touch product code, K5 not exact) → one line under "Needs Truong", go on.

## 3. Loop per lot
1. Failing tests from the lot's box (`tests/test_dc1_kiem_doc_lap.py`), run:
   `.venv/bin/python -m pytest -q --tb=line tests/test_dc1_kiem_doc_lap.py 2>&1 | tail -15`.
2. Minimal code in `du_lieu_test/kiem_doc_lap/kiem_doc_lap.py` until green.
3. Related tests only: the DC1 file + ≤ 2 export tests (e.g. `tests/test_du_lieu_ket_qua.py`).
4. `ruff check .`; `git fetch origin main` then `.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10` = 7/7;
   `soat-ma` four tiers (report only).
5. CHANGELOG + TIEN_DO → commit → push `git push -u origin claude/dc1-kiem-doc-lap` → tick the lot.

## 4. Self-check at the end (replaces checker)
- Run the script by hand on a fresh `SO_NHAP_TEST.xlsx` export (seed 3): paste the table (≤ 20 lines) into
  "Current state"; open `dau_vao_ket_qua.csv`, check 3 students against the Sổ nhập by eye (HS001–HS003).
- Read GitHub Actions `tests.yml` for the head commit (`mcp__github__actions_list`, `get_job_logs failed_only`,
  ≤ 60 lines; wait with `send_later` 30 min, no polling loop). Red → fix (max 2 rounds) → else Needs Truong.
- Write in the branch file: `Status: DONE <sha> CI <green|red> <date>` and a Vietnamese summary ≤ 8 lines:
  what was done, what was dropped, and 3 steps for Truong to try (export CSV, run script, read the table).

## 5. Session prompt (Truong pastes into a new Sonnet session; this is the "lead prompt" for size S)
```
You are CODER for DC1 on branch claude/dc1-kiem-doc-lap (size S, you are the only session). Read CLAUDE.md,
then docs/phien/DC1_GIAO_THUC.md and docs/phien/claude__dc1-kiem-doc-lap.md (on origin/claude/dc1-kiem-doc-lap)
and follow them exactly. Set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), check gotcha G2 first, then do lots L1 to L3 (L4 only if budget remains) with protocol §3,
then §4. Never edit product code or the registry; never ask Truong — blocked parts go under "Needs Truong".
```
