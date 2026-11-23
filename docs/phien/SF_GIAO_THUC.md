# SF protocol — fix every ST bug, loop until green (2 coders on the son branches)

> Truong (2026-11-23): debug everything the stress test found; loop until everything is green.
> Inputs: `ST_BAO_CAO_A.md` (branch `claude/happy-cerf-xvn495-st-a`), `ST_BAO_CAO_B.md` (`…-st-b`); the
> `xfail(strict)` tests in `tests_stress/a|b/`. Item code **SF** (sub-ids = bug ids). Budget: `_GIAO_THUC_GON.md` §3.
> Size L-lite: two Sonnet coders, no lead; each coder is the other's checker at the end (§5). No Agent tool.

## 0. Decisions (do not ask Truong again; anything outside → "Needs Truong" in your handoff file)
- Coder A works on `claude/happy-cerf-xvn495-st-a`, coder B on `claude/happy-cerf-xvn495-st-b`. Push only there.
- **File ownership** (prevents conflicts): A owns every root `*.py`, `i18n_errors.py` (+ `python tao_i18n_js.py`),
  `i18n_loi.js`, `tests/test_sf_a_*.py`. B owns `js/`, `index.html`, `style.css`, `i18n.js`, `recovery.html/.js`,
  `tests/test_giao_dien_sf_b_*.py`. Need a change in the other's files → one line in your handoff "Asks", the owner does it.
- Invariants 1–8 still rule. Default config must stay byte-identical (3 datasets × 20 seeds) after every lot.
- A fixed bug = its stress test passes with the `xfail` marker REMOVED, plus a small regression copy in `tests/`
  (CI runs `tests/`, not `tests_stress/`). Update the test-file count in `docs/ke_hoach/CLAUDE_CHI_TIET.md`.
- Never delete, skip or weaken a stress test to get green. A test you believe is wrong → "Needs Truong", keep it.
- Behaviour decisions (planner):
  - ST-B-003/ST-A-004: a Sổ with NO test/score columns (or a one-row header that loses them) must NOT wipe stored
    ticks/scores/medals: keep them and warn (new code). If the sheet does have the columns and would delete N stored
    scores, the preview warns with N. `import_so_nhap` takes a backup first (like the run pipeline).
  - ST-B-004: ids stay case-sensitive (rule of the software) but import preview, health report and Nhập tại chỗ
    warn when an id differs from an existing one only by case (kiosk asks to confirm).
  - ST-B-009: entering Chế độ học sinh with no admin account first asks to create one (existing account flow);
    while the flag is on, the backend refuses every admin write API, F5 included.
  - ST-A-005/ST-B-007: allow deleting a student/club that has preferences/results via two-step confirm; past
    `run_history` stays; current results are marked stale (existing stale banner). Needs a schema change → "Needs Truong".
  - ST-A-001: `update_workspace_config` returns a warning when the new mode lacks data dropped at import
    (reuse `get_san_sang_huy_chuong` / `get_san_sang_loai`); B shows it under the mode cards.
  - ST-A-006: `PRAGMA quick_check` before backup and before run; failing → refuse with a clear code, never rotate a
    corrupt copy over good backups. ST-A-008: whole-school PDF ≤ 30 s at 3 000 students (simulated).

## 1. Allocation and lots (A1/B1 must-ship first; ≤ 4 lots each)
| Lot | Coder A (backend) | Coder B (UI) |
|---|---|---|
| 1 | ST-B-003, ST-A-004, ST-A-002, ST-B-004 (backend part) — safe import | ST-B-001, ST-B-002, ST-B-008 — stale screens |
| 2 | ST-B-009 (backend lock), ST-A-006 — safety | ST-B-009 (UI), ST-B-004 (kiosk confirm), ST-B-011, ST-B-006 (field error) |
| 3 | ST-A-005 + ST-B-007, ST-A-003, ST-A-007, ST-B-006 (validation code), ST-A-001 | ST-A-001 (warning UI), ST-B-005, ST-B-010 |
| 4 | ST-A-008 (PDF speed) | ST-B-012, ST-B-013 — i18n toasts, 390 px |
Bugs found WHILE fixing: add to your report as `ST-<A|B>-1NN`, test first, same loop.

## 2. Start (once per coder)
1. `git fetch origin && git merge --no-edit origin/claude/happy-cerf-xvn495-st-<other>` (only tests_stress/docs
   differ, so no conflict) → both coders hold every stress test and both reports.
2. venv: `python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt -q` (no `playwright install`).
3. Add "Asks", "SF status" (one row per owned bug: open / fixed / Needs Truong) to your handoff file.

## 3. The loop (repeat until §4 holds; one bug per turn of the loop)
1. Pick the next open bug of the current lot. Remove its `xfail` → run that test → must FAIL (red).
2. Minimal fix in your own files → that test passes (green) → add the `tests/` regression copy.
3. Related tests only: your lot's stress files + ≤ 3 `tests/` files, `-q --tb=line 2>&1 | tail -15`.
4. End of lot: `kiem_nhanh.py | tail -10` 7/7; soat-ma four tiers (report-only on your own diff); CHANGELOG +
   TIEN_DO row `SF-<A|B><n>`; commit `SF-<A|B><n>: <ids>`; push; every 20 min check the CI run of your head
   (GitHub MCP `actions_list` → `get_job_logs` failed_only, ≤ 60 lines) — red → fix (counts as a loop turn).
5. Every ~2 lots: `git fetch && git merge --no-edit origin/claude/happy-cerf-xvn495-st-<other>`, rerun
   `tests_stress/` of BOTH folders that touch your files; resolve conflicts only in your own files; answer "Asks".
6. Usage limit near / ~400k tokens: update handoff "Current state", stop; the next session resumes at step 1.
A bug that fails 2 fix attempts → `git revert` that attempt, mark "Needs Truong", move on (never loop forever).

## 4. Exit = everything green (both coders, on the merged head)
- `pytest -q tests_stress/a tests_stress/b`: 0 failed, 0 xfailed, 0 xpassed (every non-"Needs Truong" bug fixed).
- CI `tests.yml` green on your head (full suite incl. Chromium, coverage ≥ 85 %); `kiem_nhanh.py` 7/7.
- Byte-identical default results 3 datasets × 20 seeds; `ruff check .` clean.
- Report files: each bug row gets `fixed <sha>` or `Needs Truong: <why>`; summary table updated.

## 5. Final cross-check and handoff
- When your §4 holds, write `SF-<A|B> DONE <sha>` in your handoff file, then review the OTHER branch's diff
  (`git diff 78bf5f8..origin/<other> -- . ':!tests_stress'`) against invariants 1–8 and §0; findings go to its
  "Asks" (max 2 rounds). Then B merges A (A is merged first), CI green, and B opens ONE PR into
  `claude/happy-cerf-xvn495` titled `SF: fix stress-test bugs` (repo PR template). Truong merges.
- After Truong merges: round 2 crash-hunting `docs/phien/ST2_GIAO_THUC.md` (prompts: `docs/phien/SF_ST2_PROMPTS.md`).
