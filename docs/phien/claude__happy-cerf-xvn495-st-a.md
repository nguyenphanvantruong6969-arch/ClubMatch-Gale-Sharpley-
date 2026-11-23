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
- SF-A lots 1-4 pushed (SF-A1 5868c7e, SF-A2 a29c97d, SF-A3 a5beec0, SF-A4 06ca113) + CI fixes (0913c56 i18n style/ws_nhan snapshot; 2c3e2ef merge of st-b + ruff; eba0a54 integrity check timeout 0.2 s for test_a13_11_stress).
- Verified locally on merged head: kiem_nhanh 7/7, `ruff check .` clean, byte-identical 3 datasets x 20 seeds (60 cases), `pytest tests_stress/a`: 1482 passed, 2 skipped, 2 xfailed (= ST-A-008, Needs Truong); `pytest tests_stress/b`: 60 passed, 1 flaky (B4 keyboard export, passes alone), 0 xfailed.
- Waiting: CI run of eba0a54 must be green (full matrix). If red: fix (loop turn), push, re-check.
- After CI green: write `SF-A DONE <sha>` below, then review B's diff (`git diff 78bf5f8..origin/claude/happy-cerf-xvn495-st-b -- . ':!tests_stress'`) against invariants 1-8; findings -> B's Asks (max 2 rounds).

## Decisions and gotchas
- Mode mapping (rules): chi_xep = wharton False; chia_100 = wharton True; huy_chuong = wharton True + fa_daa True;
  chia_loai separate bool. Set via `cau_hinh_ws.ghi_cau_hinh(db, {"rules": {...}})`.
- Shared Sổ must be imported in Huy chương mode.

## SF (Coder A) — asks and status
Protocol: `docs/phien/SF_GIAO_THUC.md`. Item code SF, sub-ids SF-A1..A4. Merged origin/...-st-b at start.

### Asks (from B to A, and A to B) — one line each
- A→B: `ruff check .` still shows 26 errors, all in `tests_stress/b/` (F401 unused imports, F841 unused locals). A added per-file-ignores for `tests_stress/**` in `pyproject.toml` (SIM115, B023, PLE2502/2515); run `ruff check tests_stress/b --fix --select F401` and `--fix --unsafe-fixes --select F841` (what A did in `tests_stress/a/`) so `kiem_nhanh` reaches 7/7.
- A→B: ST-B-003 and the import part of ST-B-004 are fixed on A (`xfail` removed in `tests_stress/b/test_b2_nhap_tep.py`, 2 lines); do not re-add. New backend warning codes you may render: `so_nhap_canh_bao_giu_diem`, `so_nhap_canh_bao_mat_diem`, `so_nhap_canh_bao_o_bo_qua`.

- A→B (ST-B-009): `vao_che_do_hoc_sinh` with NO account still returns ok, now with `data.can_tao_tai_khoan: true` (and `khoa: false`). In `js/14_giai_trinh.js` `moHs`, when `can_tao_tai_khoan` is true, open the existing create-admin-account flow first and only then (re-)call `vao_che_do_hoc_sinh`; keep the overlay open after F5 (`get_phien_dang_nhap().che_do_hs`). Update the imperative xfail in `tests_stress/b/test_b3_vai_tro.py` and the old `tests/test_giao_dien_gt3_hoc_sinh.py::test_khong_co_tai_khoan_thoat_nhu_cu` as your new flow needs.
- A→B: new error code `csdl_hong_can_khoi_phuc` (data file corrupt: run/import refuse; startup raises into recovery page). Recovery page now uses `integrity_check`.
- A→B (ST-B-007/ST-A-005): UI's two-click delete should, when the first call is refused with `cannot_delete_club_referenced` / `cannot_delete_student_matched`, offer a second confirm and then call `delete_club(club_id, true)` / `delete_student(student_id, true)` (returns `backup_path`; results become stale → stale banner). The refusal text now names this way out (keeps "xử lý", "nạp lại", "Dữ liệu" so `test_b2_xoa_clb_dang_co_nguyen_vong_khong_chi_duong` is green once its xfail is removed — A already removed it).
- A→B (ST-B-006): `create_or_update_club` returns `club_capacity_not_integer` / `capacity_too_large` (no more raw Python text). Show them inline on the capacity field; A removed the xfail of `test_b2_form_clb_chi_tieu_thap_phan_bao_loi_ky_thuat`, B verifies it passes.
- A→B (ST-A-001): `update_workspace_config` response now has `data.warnings` (`che_do_thieu_du_lieu` with n_thieu_loai, n_buoi_thieu_tu_do, n_thieu_diem_san, n_huy_chuong_sai, che_do); render it under the mode cards (js/18_cai_dat.js).

### SF status
| Bug | Lot | State |
|---|---|---|
| ST-B-003 | 1 | fixed (SF-A1) |
| ST-A-004 | 1 | fixed (SF-A1) |
| ST-A-002 | 1 | fixed (SF-A1) |
| ST-B-004 (backend) | 1 | fixed (SF-A1: preview warns; import already warned; kiosk confirm = B lot 2) |
| ST-B-009 (backend lock) | 2 | fixed backend (SF-A2): lock already refuses all but 3 methods when an account exists; no-account entry returns `can_tao_tai_khoan: true`. UI part = B lot 2 |
| ST-A-006 | 2 | fixed (SF-A2; uses integrity_check, not quick_check — quick_check missed the repro) |
| ST-A-005 + ST-B-007 | 3 | fixed backend (SF-A3): `delete_student(id, xac_nhan_xoa_ket_qua)`, `delete_club(id, xac_nhan_xoa_kem)`; UI confirm = B lot 3 |
| ST-A-003 | 3 | fixed (SF-A3) |
| ST-A-007 | 3 | fixed (SF-A3) |
| ST-B-006 (validation code) | 3 | fixed backend (SF-A3): codes `club_capacity_not_integer`, `capacity_too_large`; inline field error = B lot 2 |
| ST-A-001 | 3 | fixed (SF-A3): `update_workspace_config` data.warnings; B renders under mode cards |
| ST-A-008 | 4 | partly fixed (SF-A4): 800 students 18.8→9.1 s, 3000: 68-76→32.4 s (Chia 100) / 38.4 s (Huy chương) in the final stress run (40.6 s in a first run); target ≤30 s NOT met → Needs Truong |

## Needs Truong
- ST-A-008 (whole-school phieu PDF at 3000 students): after cached `Paragraph.wrap` + string table cells it is 32-41 s depending on the run (target ≤ 30 s). The rest is pure-Python reportlab (number formatting, `drawString`, PDF serialisation; `_rl_accel` C ext absent). Further options, each needs a decision: (a) split the whole-school PDF per class / chunk (the per-class export `theo_lop` already exists) and show progress; (b) add `pypdf`/qpdf to merge chunks built in parallel processes (new library); (c) a hand-written canvas flowable for the phieu page (big change). Not done.
- ST-A-005/ST-B-007 schema: no schema change was needed (deleting keeps `run_history`; current results go stale through the existing data fingerprint). Nothing to decide.
- `tests/test_xp1_*` PDF text tests need `pypdf`, which is not in `requirements-dev.txt`, so they skip locally and (apparently) on CI: the visible-text equivalence of the new string cells is covered only by `tests/test_sf_a_4.py` (cell text) and page count (1589 before/after at 800). A reviewer with `pypdf` may want to diff text of old/new PDFs.

## Next steps
1. A1 → A4 in order, commit "ST-A<n>: ..." and push after each.

## Files touched
- tests_stress/a/*, docs/phien/ST_BAO_CAO_A.md

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | started ST-A, read protocol | |
| 2026-11-23 | Sonnet | A1-A4 done, 8 bugs logged (ST_BAO_CAO_A.md) | |
