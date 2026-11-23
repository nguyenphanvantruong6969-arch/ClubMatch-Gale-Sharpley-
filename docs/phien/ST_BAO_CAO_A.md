# ST-A bug report (backend stress test) — branch claude/happy-cerf-xvn495-st-a

All data SIMULATED. Production code untouched. Run: `.venv/bin/python -m pytest -q tests_stress/a/<file> --tb=short`.

## Summary (severity counts) — updated at end of each lot
| S1 | S2 | S3 | S4 | total |
|---|---|---|---|---|
| 0 | 0 | 1 | 0 | 1 |

## Lot status
| Lot | State | Tests |
|---|---|---|
| A1 | done | test_a1_algo_props.py (520 random seeds + 120 brute-force + invariants 1-3), test_a1_modes.py, test_a1_fa.py, test_a1_findings.py |
| A2 | – | |
| A3 | – | |
| A4 | – | |

## Bugs
| id | sev | area | title | repro | invariant |
|---|---|---|---|---|---|
| ST-A-001 | S3 | import / settings | Switching mode after a lossy import gives no notice; Huy chương run then blocked until re-import | tests_stress/a/test_a1_findings.py::test_switch_after_lossy_import_gives_notice_or_stays_runnable | — |

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
