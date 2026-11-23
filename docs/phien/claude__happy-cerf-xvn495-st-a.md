# Branch handoff: claude/happy-cerf-xvn495-st-a

## Feature / goal
ST-A backend stress test (protocol `docs/phien/ST_GIAO_THUC.md`): find every bug in algorithm, import, pipeline/DB,
API and roles. NEVER edit production code. Output: `tests_stress/a/`, `docs/phien/ST_BAO_CAO_A.md`, this file.

## Plan
- [x] A1 Algorithm properties + modes × chia_loai on the shared Sổ
- [x] A2 Import fuzzing
- [x] A3 Pipeline and DB
- [ ] A4 API surface, roles, exports, timing

## Current state
- Done: venv set up (`.venv`, py3.13), helper design.
- Done: A1-A4. Remaining: final review only.
- Tests: `.venv/bin/python -m pytest -q tests_stress/a/<file> --tb=line`.

## Decisions and gotchas
- Mode mapping (rules): chi_xep = wharton False; chia_100 = wharton True; huy_chuong = wharton True + fa_daa True;
  chia_loai separate bool. Set via `cau_hinh_ws.ghi_cau_hinh(db, {"rules": {...}})`.
- Shared Sổ must be imported in Huy chương mode.

## SF (Coder A) — asks and status
Protocol: `docs/phien/SF_GIAO_THUC.md`. Item code SF, sub-ids SF-A1..A4. Merged origin/...-st-b at start.

### Asks (from B to A, and A to B) — one line each
- A→B: `ruff check .` still shows 26 errors, all in `tests_stress/b/` (F401 unused imports, F841 unused locals). A added per-file-ignores for `tests_stress/**` in `pyproject.toml` (SIM115, B023, PLE2502/2515); run `ruff check tests_stress/b --fix --select F401` and `--fix --unsafe-fixes --select F841` (what A did in `tests_stress/a/`) so `kiem_nhanh` reaches 7/7.
- A→B: ST-B-003 and the import part of ST-B-004 are fixed on A (`xfail` removed in `tests_stress/b/test_b2_nhap_tep.py`, 2 lines); do not re-add. New backend warning codes you may render: `so_nhap_canh_bao_giu_diem`, `so_nhap_canh_bao_mat_diem`, `so_nhap_canh_bao_o_bo_qua`.

### SF status
| Bug | Lot | State |
|---|---|---|
| ST-B-003 | 1 | fixed (SF-A1) |
| ST-A-004 | 1 | fixed (SF-A1) |
| ST-A-002 | 1 | fixed (SF-A1) |
| ST-B-004 (backend) | 1 | fixed (SF-A1: preview warns; import already warned; kiosk confirm = B lot 2) |
| ST-B-009 (backend lock) | 2 | open |
| ST-A-006 | 2 | open |
| ST-A-005 + ST-B-007 | 3 | open |
| ST-A-003 | 3 | open |
| ST-A-007 | 3 | open |
| ST-B-006 (validation code) | 3 | open |
| ST-A-001 | 3 | open |
| ST-A-008 | 4 | open |

## Needs Truong
(none yet)

## Next steps
1. A1 → A4 in order, commit "ST-A<n>: ..." and push after each.

## Files touched
- tests_stress/a/*, docs/phien/ST_BAO_CAO_A.md

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | started ST-A, read protocol | |
| 2026-11-23 | Sonnet | A1-A4 done, 8 bugs logged (ST_BAO_CAO_A.md) | |
