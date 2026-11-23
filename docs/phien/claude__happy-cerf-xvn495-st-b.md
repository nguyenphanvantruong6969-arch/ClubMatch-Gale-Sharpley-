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

## SF-B (fix coder) — Asks (to coder A; one line each)
- A: `ruff check .` was red from ST files (tests_stress/a: 34 errors, F841/SIM115 etc.). B fixed tests_stress/b and added `"tests_stress/**" = ["SIM115", "B023"]` to pyproject.toml per-file-ignores; please run `ruff check tests_stress/a --fix` (+ F841 by hand) and keep that pyproject line when merging.
- A: ST-B-004 / ST-B-009 UI parts wait for your backend warning/lock; tell me the field/code names in your handoff.
- Note: tests_stress/b/ho_tro.py `_doc_bang` now ignores skeleton rows `.ux2-khung-hang` (loading frame is not data; stale data still fails).

## SF status (coder B, owned bugs)
| Bug | Lot | State |
|---|---|---|
| ST-B-001 | 1 | fixed (SF-B1) |
| ST-B-002 | 1 | fixed (SF-B1) |
| ST-B-008 | 1 | fixed (SF-B1) |
| ST-B-009 (UI) | 2 | fixed (SF-B2) |
| ST-B-004 (kiosk confirm) | 2 | fixed (SF-B2; UI-only via search_students; A may add exact backend check, optional) |
| ST-B-011 | 2 | fixed (SF-B2, UI wording; A may add a dedicated zip error code) |
| ST-B-006 (field error) | 2 | fixed (SF-B2, client-side integer check; A still owes validation code in lot 3) |
| ST-A-001 (warning UI) | 3 | open |
| ST-B-005 | 3 | fixed (SF-B3) |
| ST-B-010 | 3 | fixed (SF-B3) |
| ST-B-012 | 4 | fixed (SF-B4) |
| ST-B-013 | 4 | fixed (SF-B4) |
Merged origin/…-st-a at start (§2 done). venv ready.

## SF notes (coder B)
- Env flake at BASE HEAD too (not from SF): `test_b4_moi_nut_xuat_tep_mo_duoc` fails ('btnPdfPhieuLop … .pdf.tmp tệp rỗng': fixed 2.5 s wait, PDF slower in this container). `test_b2_hoc_sinh_phan_trang_tim_kiem_gan_nhom` failed once (8≠50 rows, render race), passed 2 reruns. Neither touched; marked for Truong/CI check.
- Still open for B (need A first): ST-A-001 warning UI, ST-B-007 UI (A's delete flow), ST-B-006 validation code (A, lot 3). Resume: merge origin/…-st-a, read A's handoff for field/code names.

## Current state (B, end of this session)
- B lots 1-4 done except items needing A: ST-A-001 warning UI, ST-B-007 UI, ST-B-006 validation code. Head pushed; CI run on it is the next thing to check (run 45127725794 was red for the `zip` word in vi UI: fixed; also Linux 5/6 shard exit 1 with '215 passed' - check log head for cause).
- Next: fetch/merge origin/...-st-a, read A's handoff Asks, do the 3 open items, then §4 checks and §5 (review A diff, wait 'SF-A DONE', PR into claude/happy-cerf-xvn495 titled 'SF: fix stress-test bugs').
