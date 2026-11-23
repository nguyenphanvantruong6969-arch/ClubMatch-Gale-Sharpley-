# Branch handoff: claude/happy-cerf-xvn495-st-b

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.

## Feature / goal
ST-B: deep UI end-to-end stress test (real Chromium via Playwright, driving `browser_host.py`) before the field
trial. Find every bug a user can hit; NEVER edit production code. Protocol: `docs/phien/ST_GIAO_THUC.md`. Report:
`docs/phien/ST_BAO_CAO_B.md` (ids ST-B-NNN). Tests: `tests_stress/b/` (one file per lot, shared fixture in
`conftest.py`, not in `testpaths`). All data SIMULATED.

## Plan
- [x] B1 Navigation + Cài đặt (mode cards x50, chia_loai toggle, double-click, reload during run, back/forward)
- [x] B2 Data screens (import good+bad files, CLB CRUD, students, wharton/medals, Điểm chuẩn, reset, chấm điểm, nhập tại chỗ, #ux1aSauXep)
- [x] B3 Roles + kiosk (login, teacher, student mode, recovery, workspace CRUD)
- [x] B4 Robustness + display (3000 students, vi/en, widths 390/768/1366, keyboard-only, downloads)

## Current state
- Done: setup (.venv), conftest fixture (`mo()` -> Ui with .page/.api/.loi/.kiem_loi()), helpers `ho_tro.py` (chon_cach, nap_so_150, chay_ui, ket_qua_db/ui, khoa_tho), lot B1 (2 bugs S3: ST-B-001, ST-B-002). B2 done (ST-B-003..008). B3 done (ST-B-009..011). B4 done (ST-B-012, 013). ALL LOTS DONE: final report ST_BAO_CAO_B.md (13 bugs: S1 1, S2 1, S3 6, S4 5).
- Tests: `.venv/bin/python -m pytest -q --tb=line tests_stress/b/<file> 2>&1 | tail -15`

## Decisions and gotchas
- Mode cards (#ux1aChiXep/#ux1aChia100/#ux1aHuyChuong) live in view-admin (#ux1aCaiDat); chia_loai switch is `#mt2CongTac` in Quản lý > CLB.
- Import the shared Sổ in Huy chương mode first (set via card), then UI import (#fileAny + #btnImportAll).

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | setup, fixture | |
| 2026-11-23 | Sonnet | B1 done, report started | 50-switch test ~2 min; full B1 file ~3.5 min |
| 2026-11-23 | Sonnet | B2 done | full B2 ~4 min; helpers in ho_tro.py / ho_tro_tep.py |
| 2026-11-23 | Sonnet | B3 done | B3 files ~100 s |
| 2026-11-23 | Sonnet | B4 done, final report | B4 file ~2 min |
