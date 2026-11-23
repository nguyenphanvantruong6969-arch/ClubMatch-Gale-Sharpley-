# Branch handoff: claude/happy-cerf-xvn495-st-a

## Feature / goal
SF-A (fix coder A, backend): fix the ST-A / ST-B stress-test bugs owned by A, per `docs/phien/SF_GIAO_THUC.md`. Item code SF, commits SF-A1..A4. Branch `claude/happy-cerf-xvn495-st-a`.

## Plan
- [x] §2 start (merge st-b, venv, Asks/status)
- [x] Lot 1 SF-A1 (5868c7e), lot 2 SF-A2 (a29c97d), lot 3 SF-A3 (a5beec0), lot 4 SF-A4 (06ca113)
- [x] CI fixes (0913c56, 2c3e2ef, eba0a54); §4 holds, CI green on eba0a54; SF-A DONE written
- [x] §5 review of B diff, round 1 (in this file, b0fff37)
- [x] SF-A5 = ST-A-008 (Truong chose option (a)): see below
- [x] §5 round 2 done (2026-11-23): B's head is still e50cc52, the 3 UI items are still open (see "Review of B")
- [ ] B does its 3 UI items, merges A, CI green; B opens ONE PR into `claude/happy-cerf-xvn495` titled `SF: fix stress-test bugs` (only if Truong asks)

## Current state
- Done: all of A's lots incl. SF-A5; every owned bug fixed (ST-A-008 now fixed: 3000 students 24-26 s). CI full matrix green on eba0a54; later commits (docs + SF-A5) not yet run on CI.
- Verified on head after SF-A5: kiem_nhanh 7/7, ruff clean, byte-identical 3 datasets x 20 seeds (60 cases), `tests/test_sf_a_*.py` + xp1/gt1/gt3/ux1 phieu tests (289 pass, 19 skip). tests_stress/a and /b: see "SF-A5 verification" below.
- In progress: nothing on A's side. Waiting on B: ST-B-007 confirm UI, ST-A-001 warning UI, inline code for ST-B-006, optional progress bar for `get_tien_do_xuat` (see "Review of B" and Asks).
- Tests: `.venv/bin/python -m pytest -q --tb=line tests/test_sf_a_*.py`; stress folders must be run separately (`tests_stress/a`, `tests_stress/b`: conftest clash).

## Decisions and gotchas
- Used `PRAGMA integrity_check` (not quick_check: quick_check missed the ST-A-006 repro); filter CHECK/NOT NULL lines (old data); wait only 0.2 s on lock (test_a13_11_stress needs csdl_dang_ban < 7 s).
- ST-B-009 backend: no-account `vao_che_do_hoc_sinh` stays ok with `can_tao_tai_khoan: true` (a hard refusal broke an old UI test).
- Deletes: default refuse as before; confirm flags `xac_nhan_xoa_ket_qua` / `xac_nhan_xoa_kem`; no schema change.
- New i18n text must pass `tests/test_van_phong_tu_nhien.py` (no raw `{detail}`, no ALL-CAPS) and intended text changes go in `tests/test_ws_nhan.py` SUA_CO_Y / MA_MOI_SAU_ANH_CHUP.
- CI cancels the previous run on every push; full matrix ~10-12 min. Do not run heavy local tests concurrently with stress runs (flaky UI timing).

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

- A→B (ST-A-008 / SF-A5, optional): new read-only API `get_tien_do_xuat()` → `{dang_xuat, xong, tong, ten}` (students done / total, accumulated across classes when `theo_lop=true`; `ten` = class being built). It does not take the write lock, so poll it (e.g. every 500 ms) while `export_phieu_giai_trinh_pdf` runs from `chayXuatPdf` (js/03_ket_qua.js, button `btnPdfPhieuLop` and the whole-school item) and show "xong/tong" instead of a frozen button. New i18n text is B's (i18n.js); no new error code.

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
| ST-A-008 | 4-5 | fixed (SF-A5): 3000 students 68-76 s → 26.3 s (Huy chương) / 24.3 s (Chia 100), 800 → 6.5 / 5.8 s; page count and cell text unchanged; progress API `get_tien_do_xuat`. Margin ~12 % under 30 s on a 4-core container |

## SF-A5 (ST-A-008) — what was done
- Measured first (container, 4 cores, no other load): whole-school PDF at 3000 = 30.6 s after SF-A4. cProfile at 800: `_py_asciiBase85Encode` ~10 %, reportlab drawing (`drawString`, `_py_fp_str`) ~60 %, and `giai_trinh` data prep grew QUADRATICALLY (0.4 s at 800 → 4.7 s at 3000 Chia 100; 0.6 → 6.8 s Huy chương): `_nguoi_nhan_cuoi`, `sum(... assign ...)` and `_chuan_clb_fa` rescanned all assignments for every preference of every student.
- Fixes: (1) per-club memo in the per-buoi dict `b` (`_nhan_cuoi_nho`, `_so_nhan`, `_chuan_clb_fa`); phieu data for 800 and 3000 students x 2 modes compared field by field before/after = identical (except `run_at`). (2) `dung_pdf` builds with `rl_config.useA85 = 0` (restored in `finally`). (3) `get_tien_do_xuat` + `khi_xong_em` callback (marker page break + `afterFlowable`).
- Result: 3000 → 26.3 s (Huy chương) / 24.3 s (Chia 100); stress test `test_timing_scaled_book[*-3000]` now asserts ≤ 30 s (xfail branch removed). GC off, per-class sequential split: tried / measured, no gain.

## Review of B's diff (SF §5, round 1) — findings for B's "Asks"
Scope: B's own commits 497b018, dedfd44, cdc36c4, edb987a, 681228a, 1f06b1e, a324d59, afe28c7 (JS / i18n.js / index.html / style.css / recovery.js / tests). Invariants 1-8: nothing touched (no allocation, STB, run_history, pipeline, schema or CSV code); UI keeps the `{ok,data,errors}` contract. ST-B-009 uses `data.can_tao_tai_khoan` correctly.
1. [should fix] ST-B-006 (`js/05_quan_ly.js`): the client check `Number.isInteger(Number(capacity))` reports `capacity_must_be_positive` ("must be > 0") for 1.5 — wrong text. The backend now returns `club_capacity_not_integer` / `capacity_too_large`; map those two codes in `UX2_LOI_CLB` as inline capacity-field errors (and drop or re-code the client check).
2. [open] ST-B-007 UI is not on B's head: `js/05_quan_ly.js:423` still calls `delete_club(id)` only. Add the second confirm and call `delete_club(club_id, true)`; same for `delete_student(student_id, true)` in `js/04_nhap_tai_cho.js`. (A already removed the xfail of the stress test; its message check passes today.)
2b. [open] ST-A-001 UI: `js/18_cai_dat.js` must render `data.warnings` (`che_do_thieu_du_lieu`: n_thieu_loai, n_buoi_thieu_tu_do, n_thieu_diem_san, n_huy_chuong_sai, che_do) under the mode cards after `update_workspace_config`.
3. [nit] ST-B-012 closes every toast on `langchange` (also toasts with an "Hoàn tác" button): acceptable, say so in the changelog.
Merge hint for B: merge `origin/claude/happy-cerf-xvn495-st-a` (head after this file) first; conflicts are expected only in CHANGELOG.md, TIEN_DO.md and the test-file count line of `docs/ke_hoach/CLAUDE_CHI_TIET.md` (A resolved it once at 386 = actual count after both branches; recount with `ls tests/test_*.py | wc -l`). CI needs `tests/test_ws_nhan.py` (already updated on A) and `tests/test_van_phong_tu_nhien.py` (no raw `{detail}`, no ALL-CAPS emphasis in new i18n text).
### Round 2 (2026-11-23, report only; this was the last round allowed by SF §5)
B's head is unchanged since round 1 (`e50cc52`, already merged into A). Re-checked the three UI items by grep on the merged tree:
1. [still open] ST-B-006 `js/05_quan_ly.js:1161-1193`: the map `UX2_LOI_CLB` has only `capacity_must_be_positive`; the client check `Number.isInteger(Number(capacity))` still shows the wrong text for 1.5. Map `club_capacity_not_integer` and `capacity_too_large` (backend codes) to `clubFormCapacity`, drop or re-code the client check.
2. [still open] ST-B-007: `js/05_quan_ly.js:423` calls `delete_club` with the id only; `js/04_nhap_tai_cho.js:432` calls `delete_student` with the id only. No code handles `cannot_delete_club_referenced` / `cannot_delete_student_matched` with a second confirm and a call with `true`.
3. [still open] ST-A-001: `js/18_cai_dat.js` has no mention of `warnings` / `che_do_thieu_du_lieu`.
No new invariant problem seen (B's diff touches no allocation, STB, run_history, pipeline, schema or CSV code). A does not edit B's files (SF §0); the three items stay B's. Optional: dedicated zip error code for ST-B-011 (B's note) is NOT done on A; B's wording fix stands.

## Needs Truong
- ST-A-008: RESOLVED by SF-A5 (below), nothing to decide. One optional follow-up if the school kiosk is much slower than this container (4 cores, ~12 % margin): build per-class parts in worker processes (stdlib `multiprocessing`; needs `freeze_support()` in the PyInstaller entry point and a Windows test, so not done). Sequential splitting per class does NOT speed things up (time is linear in the number of slips; the stress data has a single class).
- Pure-reportlab remainder (number formatting, `drawString`, PDF serialisation) is now ~85 % of the time.
- ST-A-005/ST-B-007 schema: no schema change was needed (deleting keeps `run_history`; current results go stale through the existing data fingerprint). Nothing to decide.
- `tests/test_xp1_*` PDF text tests need `pypdf`, which is not in `requirements-dev.txt`, so they skip locally and (apparently) on CI: the visible-text equivalence of the new string cells is covered only by `tests/test_sf_a_4.py` (cell text) and page count (1589 before/after at 800). A reviewer with `pypdf` may want to diff text of old/new PDFs.

## Next steps
0. DONE (SF-A5): ST-A-008. Truong's option (a) asked for per-class split + progress; measured result: per-class split alone gives no speed-up, so SF-A5 removed the real costs (quadratic `giai_trinh` scans, ASCII85) and added the progress API; per-class export (`theo_lop`) already existed and now reports accumulated progress.
1. Fetch; merge B if it has new commits; read B's handoff Asks; answer any new Ask to A (review rounds are used up: only re-check that B's 3 items landed).
2. (none)
3. B merges A first, CI green, B opens the single PR; Truong merges. Then ST2 round (`docs/phien/ST2_GIAO_THUC.md`).

## Files touched
- Production: api.py, api_chung.py, api_nhap.py, api_quan_ly.py, api_tai_khoan.py, api_workspace.py, api_forms.py, api_forms_nap.py, cau_hinh_ws.py, so_nhap.py, recovery.py, xuat_pdf.py, giai_trinh.py, phieu_giai_trinh.py, phan_quyen.py, i18n_errors.py (+ i18n_loi.js), pyproject.toml
- Tests: tests/test_sf_a_1..5.py, test_gt_tich_hop.py, test_ws_nhan.py; xfail markers removed in tests_stress/
- Docs: CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, CLAUDE_CHI_TIET.md (test count), ST_BAO_CAO_A.md (fixed shas)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-23 | Sonnet | started ST-A, read protocol | |
| 2026-11-23 | Sonnet | A1-A4 done, 8 bugs logged (ST_BAO_CAO_A.md) | |
| 2026-11-23 | Sonnet | SF-A lots 1-4, CI fixes, SF-A DONE eba0a54, review of B round 1 | context ~400k, handoff |
| 2026-11-23 | Sonnet | SF-A5 (ST-A-008), review of B round 2, handoff | context well under 400k |
