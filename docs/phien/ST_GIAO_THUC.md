# ST protocol — deep stress test before field trial (2 implementers, no lead)

> Truong (2026-11-22): the software is feature-complete; trial phase starts. Goal: find ALL bugs, not fix them.
> Parent branch `claude/happy-cerf-xvn495`. Budget rules: `docs/phien/_GIAO_THUC_GON.md` §3, EXCEPT where this
> file says otherwise. Two Sonnet sessions, one sub-branch each, no lead, no checker, no Agent tool.

## 0. Decisions (do not ask Truong again)
- ST-A = backend, algorithm, data, API, DB: branch `claude/happy-cerf-xvn495-st-a`.
- ST-B = real UI end-to-end in Chromium (Playwright already installed; `browser_host.py`): `claude/happy-cerf-xvn495-st-b`.
- **Never edit production code** (`*.py` at repo root, `js/`, `index.html`, `style.css`, `i18n*`). Write only:
  `tests_stress/<a|b>/` (outside `testpaths`, so CI does not run it), `docs/phien/ST_BAO_CAO_<A|B>.md` (bug report),
  the branch handoff file, scratch scripts. No new library (no hypothesis): use `random.Random(seed)`.
- A test that exposes a bug stays, marked `@pytest.mark.xfail(strict=True, reason="ST-A-007")`: a later fix flips it.
- All numbers are SIMULATED data. Never draft report commentary for the student's project report.
- Shared fixture data: `du_lieu_test/SO_NHAP_DOI_CHE_DO_150HS.xlsx` (generator `du_lieu_test/tao_so_nhap_doi_che_do.py`).
  Known behaviour: import it while the workspace is in **Huy chương** mode (or "Chia CLB theo loại" on); importing
  in Chia 100 drops Loại columns (`fa_cot_bo_qua`), in Chỉ xếp also drops points (`csv_wp_bo_qua`). Decide and
  report whether this is a bug (S3 at least: no UI warning that switching later needs a re-import?).

## 1. Bug report format (`docs/phien/ST_BAO_CAO_<A|B>.md`, one table row + one block per bug)
`ST-A-001 | S1..S4 | area | one-line title | repro: tests_stress/a/test_x.py::test_y | invariant # or —`
Block: steps (≤ 8 lines), expected, actual (error code / traceback first line / screenshot path), suspected function
(by name). Severity: **S1** wrong allocation, data loss, invariant 1–8 broken, security/role bypass; **S2** crash,
traceback, hang > 30 s, blocked workflow with no way out; **S3** wrong/missing message, raw i18n key, UI mismatch
with backend; **S4** cosmetic. Reproduce every bug twice (fresh tmp dir) before logging. ST-B links an ST-A id when
the root cause is backend (check `git fetch origin claude/happy-cerf-xvn495-st-a` report first; no duplicates).

## 2. Lots (4 each; commit + push after each; all must-ship except A4/B4 second half)
**ST-A**
- A1 Algorithm properties (random instances, ≥ 500 seeds, sizes 3–800 students, 1–6 sessions): stability via
  `verify_stability`; capacity and reserve bounds; ≤ 1 club per student per session; brute-force student-optimal
  stable match for ≤ 6 students × 3 clubs; invariant 1 (same data+seed twice → identical `match_results`), 2
  (permute preference order → priority keys unchanged), 3 (STB lock, crc32, late arrivals keep relative order);
  every mode × "chia loại" (chi_xep / chia_100 / huy_chuong × on/off) incl. random toggle sequences of 50 switches
  with a run after each, on the shared Sổ; FA-DAA medals, Tự do fallback, floors (`diem_san`), `so_toi_thieu`.
- A2 Import fuzzing (`import_so_nhap`, CSV, Forms raw, workspace zip): ≥ 40 mutation kinds (empty / missing sheets,
  one-row header, merged cells, NFC vs NFD, spaces, case-different ids, duplicate names, 0 / negative / 1e9 capacity,
  "9,5" vs 9.5, formulas, dates, 10 000 rows, 11+ prefs, 6+ tests, corrupt zip, renamed .xls, BOM/UTF-16/cp1258
  CSV, zip path traversal, huge cell text). Expect `{ok:false, errors:[{code,params}]}` with a code that exists in
  `i18n_errors.py` (vi and en), never a traceback, and the DB byte-unchanged on any refusal.
- A3 Pipeline and DB (invariants 4, 5): monkeypatch a failure into each stage (backup, validate, lock, solve,
  verify, write, export) → full rollback, backup exists, `run_history` append-only; two threads calling
  `run_pipeline` / import / config update at once; locked DB; disk-full (`OSError` on write); corrupt `app.db` →
  `recovery.py`; `di_tru_schema` run twice; random 30-step timelines (add late student, withdraw, change capacity,
  edit points/medals, switch mode, rerun) checking invariant 3 and that results always pass verify.
- A4 API surface and roles: every public `PipelineAPI` method called with None / wrong type / huge / SQL-ish /
  path strings → contract `{ok,data,errors}`; teacher and student roles refused on every write path
  (`phan_quyen`); student kiosk lock; exports (xlsx, CSV, PDF) open and export→re-import round-trips; timing at
  800×20 and 3 000×60 (report seconds; > 30 s = S2).
**ST-B** (one Chromium test file per lot, one shared page fixture, console errors + unhandled rejections collected
on every page and asserted empty)
- B1 Navigation and Cài đặt: every tab / sub-tab; mode cards Chỉ xếp ↔ Chia 100 ↔ Huy chương clicked 50× in
  random order on the shared Sổ, "Chia CLB theo loại" toggled, run after each switch, Results tab consistent with
  backend; double-click every primary button; reload during a run; back/forward.
- B2 Data screens: import via UI (good + 10 bad files from A2), Quản lý → CLB CRUD edge values, Học sinh bulk
  ops and paging, Điểm quyết tâm / medals edit, Điểm chuẩn, Xoá dữ liệu two-step confirm, Chấm điểm, late arrival
  entry (Nhập tại chỗ), post-run actions (#ux1aSauXep) in Huy chương mode.
- B3 Roles and kiosk: login/logout, wrong password, teacher sees/does only allowed items, student self-lookup mode
  enter/exit/reload lock, recovery page, workspace create/switch/import/export.
- B4 Robustness and display: 3 000 students render; vi ↔ en on every screen (raw keys, overflow, untranslated
  text); widths 390, 768, 1366; keyboard-only path through import → run → export; downloads open.

## 3. Rules per session
- Setup: `python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt -q` (Chromium is preinstalled; do
  not run `playwright install`). Run your own `tests_stress/<x>/` files only; never the full suite.
- After each lot: report rows, commit `ST-<A|B><n>: …`, push to YOUR sub-branch only, update handoff file
  `docs/phien/claude__happy-cerf-xvn495-st-<a|b>.md` (from `_TEMPLATE.md`, English, ≤ 150 lines).
- Stop at ~400k tokens (rule 9). End: report summary table (count per severity) at the top of the report file.
