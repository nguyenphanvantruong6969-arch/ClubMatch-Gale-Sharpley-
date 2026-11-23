# ST-A bug report (backend stress test) — branch claude/happy-cerf-xvn495-st-a

All data SIMULATED. Production code untouched. Run: `.venv/bin/python -m pytest -q tests_stress/a/<file> --tb=short`.

## Summary (severity counts) — updated at end of each lot
| S1 | S2 | S3 | S4 | total |
|---|---|---|---|---|
| 0 | 4 | 3 | 1 | 8 |

## SF status (fixes) — updated by SF Coder A
| id | state |
|---|---|
| ST-A-001 | fixed a5beec0 (`update_workspace_config` data.warnings `che_do_thieu_du_lieu`; UI rendering = B) |
| ST-A-002 | fixed 5868c7e (`_cfg_ws` reads through the open transaction connection) |
| ST-A-003 | fixed a5beec0 (`TRAN_SUC_CHUA` = 2^31-1 in preview + import + form + CSV) |
| ST-A-004 | fixed 5868c7e (warning `so_nhap_canh_bao_o_bo_qua`; no test columns ⇒ stored ticks/scores kept) |
| ST-A-005 | fixed a5beec0 (`delete_student(id, xac_nhan_xoa_ket_qua)`; blank result rows no longer block) |
| ST-A-006 | fixed a29c97d (`integrity_check` at open / run / import / backup; recovery page uses it too) |
| ST-A-007 | fixed a5beec0 (`forms_dot.nap_mau_forms()` before every forms-module import) |
| ST-A-008 | Needs Truong: 3000 students 68-76 s → 32.4 s (Chia 100) / 38.4 s (Huy chương) (06ca113), target 30 s not met; see handoff |
| ST-B-003 | fixed 5868c7e |
| ST-B-004 (backend) | fixed 5868c7e (preview warns; kiosk confirm = B) |
| ST-B-006 (validation code) | fixed a5beec0 (inline field error = B) |
| ST-B-007 (backend) | fixed a5beec0 (`delete_club(id, xac_nhan_xoa_kem)`; UI confirm = B) |
| ST-B-009 (backend) | fixed a29c97d (`vao_che_do_hoc_sinh` → `can_tao_tai_khoan`; lock with account already refuses all but 3 methods) |

## Lot status
| Lot | State | Tests |
|---|---|---|
| A1 | done | test_a1_algo_props.py (520 random seeds + 120 brute-force + invariants 1-3), test_a1_modes.py, test_a1_fa.py, test_a1_findings.py |
| A2 | done | test_a2_xlsx_fuzz.py (69 mutation kinds + big-book), test_a2_raw_csv_zip.py (raw bytes, base64 args, 3 CSV kinds x 24 variants x 4 entry points, 14 zip abuses) |
| A3 | done | test_a3_faults.py (10 stage faults x fresh/after-run, BaseException, backup/export faults), test_a3_db.py (threads, external lock, corruption + recovery, schema x2, 6 random 30-step timelines) |
| A4 | done | test_a4_api_fuzz.py (168 methods x 20 hostile values, export path strings, workspace traversal sentinels), test_a4_roles.py, test_a4_exports_timing.py |

## Bugs
| id | sev | area | title | repro | invariant |
|---|---|---|---|---|---|
| ST-A-001 | S3 | import / settings | Switching mode after a lossy import gives no notice; Huy chương run then blocked until re-import | tests_stress/a/test_a1_findings.py::test_switch_after_lossy_import_gives_notice_or_stays_runnable | — |

| ST-A-002 | S2 | import / DB | Sổ with ~3 000 students fails `csdl_dang_ban` ("database is locked") in a single thread | tests_stress/a/test_a2_xlsx_fuzz.py::test_big_book_3000_rows | 5 |
| ST-A-003 | S3 | import | Capacity >= 2^63: preview OK, import fails with generic `error_importing_clubs_csv` + raw "Python int too large" | tests_stress/a/test_a2_xlsx_fuzz.py::test_capacity_beyond_int64_preview_matches_import | — |
| ST-A-004 | S3 | import | Sổ whose Học sinh sheet has a ONE-row header: 337 scores + all medals silently ignored, ok:true, 0 warnings | tests_stress/a/test_a2_xlsx_fuzz.py::test_one_row_header_does_not_silently_drop_points | — |
| ST-A-005 | S2 | quản lý | A student created after a run (kiosk typo id) can never be deleted: `cannot_delete_student_matched` after the next run; message says "run again" (circular) | tests_stress/a/test_a3_db.py::test_student_created_by_mistake_after_a_run_can_be_removed | — |
| ST-A-006 | S2 | DB / backup | DB failing `integrity_check` opens fine, run may report ok:true, corrupt copies rotate the good backups out | tests_stress/a/test_a3_db.py::test_run_on_page_corrupt_db_must_not_report_ok | — |
| ST-A-007 | S4 | forms | `ai_chua_dang_ky`, `chuyen_tep_forms`, `doi_chieu_hai_lan` raise raw ModuleNotFoundError when called in a fresh process before any call that adds `mau_forms_thi_clb` to sys.path (import precedes precondition check); UI order avoids it | tests_stress/a/test_a4_api_fuzz.py::test_method_contract_on_bad_args[ai_chua_dang_ky] (non-strict xfail) | — |
| ST-A-008 | S2 | export | `export_phieu_giai_trinh_pdf` (whole school, one PDF): 800 students 18 s, 3000 students 68-76 s (> 30 s) | tests_stress/a/test_a4_exports_timing.py::test_timing_scaled_book[*-3000] (xfail) | — |

### ST-A-001
Steps: new workspace; set Chia 100 (or Chỉ xếp); `import_so_nhap(SO_NHAP_DOI_CHE_DO_150HS.xlsx)` (warns `fa_cot_bo_qua`, and
`csv_wp_bo_qua` in Chỉ xếp); `update_workspace_config({"rules": huy_chuong})` → `ok:true`, no warning; `get_data_health_report`
→ n_high=16/17; `run_pipeline` → `ok:false`, errors `fa_thieu_clb_tu_do` ×2, `fa_clb_thieu_loai` ×14.
Expected: the switch (or Cài đặt UI via its response) says the sheet's Loại / points were dropped and a re-import is needed.
Actual: silent success; the import warning appeared only at import time. Recovery exists (re-import in the new mode),
so S3; in Chỉ xếp the 900 points are discarded irreversibly from the DB. Positive: error codes are clear; Chia 100 with
dropped points is caught by `wharton_ho_so_chua_hop_le`. Suspected: `update_workspace_config` (no readiness check), import
column filtering in `_doc_so_nhap` / `so_nhap.thanh_csv`.

## A1 negative results (no bug found)
- 520 random instances (3–800 students, 1–4 sessions): stability, capacity, reserve bound, ≤1 club/session, no placement
  in unranked club, determinism, base_rank invariant under input-order shuffle, `chi_buoi` = full-week slice.
- 120 brute-force instances (2–6 students, ≤3 clubs): DA outcome is stable and student-optimal (but only 1/120 had >1 stable
  matching — weak discriminating power).
- Invariant 3: crc32 / PYTHONHASHSEED independence, late arrivals keep order + uniform, input order irrelevant.
- 3 modes × chia_loai on/off and 50 random switches with a run after each: runs ok, deterministic, `run_history` +1 per run.
- FA-DAA: `so_toi_thieu` closure, Tự do fallback (nobody unplaced), `diem_san` floors respected.
- Low-level calls with capacity 0 / negative / float, reserve>capacity raise ValueError/TypeError from `club_choice_function`;
  must be stopped earlier by validation: checked in A2/A3.

### ST-A-002
Steps: workspace in Huy chương (or any) mode; Sổ = the shared file with 3 000 student rows (rows copied from DC001 with new ids);
`import_so_nhap`. 2 500 rows OK (2.3 s); 3 000 rows → `{ok:false, errors:[csdl_dang_ban]}` after ~3.4 s; 10 000 rows ~5 s. DB is
rolled back (unchanged) — verified. Expected: import succeeds (or a size-limit message). Actual: misleading "database busy,
retry" that can never succeed by retrying. Root cause (stack from a spy on `_cfg_ws`): `import_so_nhap` runs inside ONE write
transaction (`_mot_giao_dich`); once the transaction spills past SQLite's page cache (after the 40 k-row test-selection step) it
holds an exclusive lock, and `import_preferences_csv` then calls `self._luat_nghiem()` which opens a SECOND connection to read the
config → `CsdlBan` after the 3 s busy timeout. Suspected: `import_preferences_csv` (`luat = self._luat_nghiem()`), `_cfg_ws`.
Fix hint: read the config once at the start of `import_so_nhap` and pass it down.

### ST-A-003
Steps: Sổ with capacity 1e300 (or 10**30) in "1. CLB"; `xem_truoc_so_nhap` → ok, `loi: []`, no warning; `import_so_nhap` →
`error_importing_clubs_csv` with detail `Python int too large to convert to SQLite INTEGER` plus `xem_nhat_ky` (writes
`loi_ung_dung.txt`). DB unchanged. Expected: `so_nhap_chi_tieu_sai` in preview and import. Suspected: `so_nhap._doc_sheet_clb`
(no upper bound on capacity; also 1e9 is accepted silently — not logged as bug).

### ST-A-004
Steps: delete the sub-header row (row 2: CLB / Điểm thi / Huy chương) of "2. Học sinh"; import. Result `ok:true`,
`n_hoc_sinh=150`, `n_diem=0`, `warnings=[]`, 0 test ticks, 0 scores, 0 medals (preferences intact). The ~900 numeric cells in
unlabelled columns are ignored without a word; the loss shows only later (health / run errors in Huy chương mode, silent
quality loss in Chia 100 / Chỉ xếp). Expected: refuse (`so_nhap_cot_lech_nhom`-style) or at least warn "N cells ignored". May be
by design for prefs-only books; hence S3. Suspected: `so_nhap._tieu_de_hai_hang` / `_la_hai_hang` fallback to one-row mode.

### ST-A-005
Steps (workspace, shared Sổ imported, Chỉ xếp): `run_pipeline`; `create_student_if_missing("TYPO1","x")`; `run_pipeline` again;
`delete_student("TYPO1")` → `cannot_delete_student_matched` ("run the pipeline again first"). The rerun is what created the match
row (student with no preferences gets a blank row), so the advice is circular; `submit_preferences(id, [])` is refused, and the only
exit is `reset_data` which wipes ALL students. Same for any withdrawal (owner's goal "late arrivals, withdrawals"). Expected: a
delete/withdraw path that also removes the student's match rows (with a run_history/audit note) or at least a message that
names the real exit. Suspected: `delete_student` (api_quan_ly); `run_pipeline` writing blank rows for students without preferences.

### ST-A-006
Steps: run once (backup ring is created); flip 5 random bytes in the data half of `app.db` (rng seed 2); `PRAGMA integrity_check`
→ "row N missing from index ..."; `PipelineAPI(db)` constructs normally (no `quick_check` in `__init__`); `run_pipeline(seed=2)`
→ `ok:true` in 1 of 6 corruption seeds (others: `error_running_pipeline` + `xem_nhat_ky`, never a hint to use recovery); the
pre-run `_backup_db` copies the corrupt pages and the ring (`_MAX_BACKUPS`) rotates good copies out after N runs. Expected: startup
or run refuses with the recovery path when `quick_check` fails; do not rotate good backups out for a failing copy. Suspected:
`PipelineAPI.__init__`, `_backup_db` (no integrity check). Hardware-level corruption is rare, hence not S1.

## A2/A3 negative results (no bug found)
- 69 xlsx mutation kinds (missing/renamed/hidden sheets, header shapes, merged cells, NFC/NFD, spaces, case, duplicates, 0/negative/
  1e9/"9,5"/text capacity and scores, formulas, dates, 11 prefs one session -> `so_nhap_qua_tran_nv`, 6+ tests, SQL/HTML/zero-width
  text, 32 k-char cell, 300 clubs, 1 000 students): contract OK, all codes known in vi+en and renderable, DB byte-unchanged on
  every refusal, preview never writes. Accepted data normalised (NFD/space/case prefs give the same rows as the base).
- Raw bytes (empty, noise, truncated, flipped, OLE .xls, CSV/HTML renamed, 150 MB zip bomb, 30 MB noise), 10 bad base64 args, 24
  CSV variants x 3 kinds x 4 entry points, 14 workspace-zip abuses (zip-slip, abs path, dup names, NUL, bomb, 3 000 files): no
  traceback, no hang (> 60 s), nothing written outside the workspace root, no `_nhap-*` leftovers.
- Pipeline faults in 10 stages (fresh DB and after a first run) + KeyboardInterrupt / SystemExit / MemoryError / RecursionError:
  full rollback (DB byte-identical), backup exists, `run_history` unchanged on failure and +1 per good run, no orphan STB lock;
  backup and export failures do not block / lose committed results.
- 8 parallel `run_pipeline`, mixed import / run / config threads (no `csdl_dang_ban`), two API objects on one file, external
  EXCLUSIVE lock (busy error < 30 s, DB unchanged, recovers), corrupt headers / truncation -> init raises -> `RecoveryAPI`
  restores newest good backup and keeps the `.corrupt-` file, `start_fresh`, all-backups-corrupt keeps the original;
  `di_tru_schema` twice and on an older schema is idempotent; 6 random 30-step timelines keep invariant 3 (existing STB order),
  capacity bounds and `integrity_check == ok`.

### ST-A-007 / ST-A-008
007: fresh `PipelineAPI`, call `ai_chua_dang_ky(None)` -> `ModuleNotFoundError: danh_sach_chua_dang_ky`. After `get_forms_buoc_12` the path exists and calls work.
008: scaled shared Sổ (generator patched to n students), `export_phieu_giai_trinh_pdf` with no class filter: 18.4 s at 800, 68-76 s at 3000 (Huy chương and Chia 100). Everything else <= 6.3 s (3000: import 1.2-1.6 s, run 2-6 s, export_ket_qua 2 s). 800x20 / 3000x60 plain seed data: run 0.06 / 0.26 s, all exports <= 1.8 s. Numbers in `docs/phien/ST_A_TIMING.txt`.
Note: ST-A-002 did not reproduce on the scaled shared Sổ at 3000 (it depends on tick-row volume: the copied-row Sổ has ~40 k tick rows).

## A4 negative results
- 168 public methods x 20 hostile values (None, 0, -1, 10**30, NaN, 200 kB string, SQL, traversal, NUL, RTL/emoji, huge lists...): contract kept, no hang, DB integrity ok; only ST-A-007. `chuan_hoa_buoi`/`chuan_hoa_nhom_du_tru` are staticmethods returning str, outside the permission gate (pure helpers, harmless; some AttributeError on wrong types).
- Export path strings (13 kinds x 9 exports) and workspace slugs (`../SENTINEL`, absolute, NUL, encoded) never escaped the root; `mo_tep`/`mo_thu_muc` never exec shell metacharacters.
- Roles: every public method has a `QUYEN` entry; no session -> `gt3_can_dang_nhap` everywhere; teacher refused on all admin methods with no data change; teacher cannot create accounts or escalate; login lockout works; student kiosk lock refuses all but 3 methods, teacher cannot unlock, lookup errors identical for known/unknown ids.
- Exports (xlsx, CSV, PDF, zip, 3 modes) open; export -> re-import round trip gives identical clubs/prefs/scores and identical allocation.
