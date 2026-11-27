# VG1 protocol (size M: coder + checker, NO lead) — from `_GIAO_THUC_GON.md`

> Source of work: `docs/phien/claude__charming-cray-2izyn6.md` (decisions D1–D5, lots L1–L4). Branch: `claude/charming-cray-2izyn6`.
> Mechanics (message formats, quiet tests): `GT_GIAO_THUC.md` §7–8 with writer = coder. Where they differ, THIS file wins.

## 0. Decisions (do not ask Truong)
- Everything in the branch file "Decisions" D1–D5. No new library. No schema change (only a `dk_cai_dat` key).
- Defect 7 is out of scope. Anything outside L1–L4, an invariant conflict, or the L4 export check failing → "Needs Truong" line, continue.

## 1. Roles
| Role | Model | Does | Never |
|---|---|---|---|
| coder | Sonnet | per lot: failing test → minimal code → related tests → CHANGELOG/TIEN_DO → commit `VG1-L<n>: …` → push; runs the CI gate at the end | marks own lot passed; edits CLAUDE.md invariants |
| checker | Sonnet | Truong starts it when the coder writes `MILESTONE <k> READY` (k=1 after L2, k=2 after L4); verdict in `docs/phien/claude__charming-cray-2izyn6__checker.md` | edits product code or tests |

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

## 4. Final gate (coder, after L4 + checker OK)
- All 8 repro tests green; `python -m pytest -q tests/test_va_gap_tai_hien.py tests/test_dk3_api.py tests/test_dk4_l0b_khoa_dang_nhap.py tests/test_dk9_nap_excel.py tests/test_dk8_l1_dem_cong_khai.py`.
- Read GitHub Actions `tests.yml` + build for the head commit (failed_only, ≤ 60 lines); fix until green. Never skip/quarantine a test.
- Write branch file "Current state" with: what is fixed, what is left (defect 7), `soat-ma` report. Stop.
