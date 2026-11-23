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
- In progress: A4 (API surface, roles, exports, timing).
- Tests: `.venv/bin/python -m pytest -q tests_stress/a/<file> --tb=line`.

## Decisions and gotchas
- Mode mapping (rules): chi_xep = wharton False; chia_100 = wharton True; huy_chuong = wharton True + fa_daa True;
  chia_loai separate bool. Set via `cau_hinh_ws.ghi_cau_hinh(db, {"rules": {...}})`.
- Shared Sổ must be imported in Huy chương mode.

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
