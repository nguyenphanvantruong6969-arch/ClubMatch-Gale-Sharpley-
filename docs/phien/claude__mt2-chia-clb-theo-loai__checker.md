# MT2 checker verdicts (English, append only)

## L1 — range 117432d..732f995 — VERDICT: PASS (2 non-blocking test gaps, see F1–F2)

Scope: config key `chia_loai`, `dung_chia_loai`, `get_chia_loai`, rule-string/fingerprint handling. No algorithm change (L2).

### Evidence
| Check | Result |
|---|---|
| `tests/test_mt2_l1_cau_hinh.py` | 18 passed |
| Related suites (gt2/gt3/ws_luat/ws_cau_hinh/wharton_luat/ws_nhan/a13_13) | 369 passed |
| `kiem_nhanh.py --co-so 117432d` | 7/7 PASS |
| Invariant 1: `trung_khit`, 3 datasets × 20 seeds vs base | 60 cases byte-identical (SIMULATED data) |
| Legacy `fa_daa` stored rule string | no `chia_loai` key added (test + code read: `_luat_de_ghi_hoac_bam` drops it when False) |
| Fingerprint for OFF and legacy `fa_daa` | unchanged: `fa_clb` part still included for `fa_daa` (`dung_chia_loai` = `chia_loai or fa_daa`) |
| Invariants 2–5, 7 | untouched by diff (no key builder, STB, pipeline, `run_history` or CSV change) |
| Invariant 6 | `get_chia_loai` returns `{ok,data,errors}`; no new error code |
| Roles | `update_workspace_config` and `dat_loai_clb` stay admin-only; `get_chia_loai` is read-only, same group as `get_san_sang_huy_chuong` |
| OFF→ON→OFF keeps `clubs.loai` | L1 never touches `clubs`; getter round trip tested. Re-test in L3 |
| soat-ma tiers | T1: N/A (no algorithm). T2: items 3, 5, 9 read OK. T3: N/A (no UI yet). T4: ruff clean, CHANGELOG + TIEN_DO row present. Mutations: below |

### Mutation results (reverted, `git status` clean)
| Mutation | Tests red? |
|---|---|
| `dung_chia_loai` -> `bat` only (drop `or fa_daa`) | yes |
| drop `chia_loai` from `_luat_de_ghi_hoac_bam` list | yes |
| fingerprint uses `dung_fa_daa` instead of `dung_chia_loai` | **NO (survived)** |
| drop `chia_loai` from `_luat_ap_dung` loop (`api_tieu_chi.py`) | **NO (survived)** |

### Findings
| # | Level | Where | Issue | Path | Suggested fix |
|---|---|---|---|---|---|
| F1 | should fix (L2) | `dau_van_tay_du_lieu` | No test that `chia_loai` ON (fa_daa OFF) puts `fa_clb` in the fingerprint | change a club's `loai` with `chia_loai` ON: stale-result detection would silently not fire, and no test notices | add test in L2: change `clubs.loai`, expect fingerprint change when ON, no change when OFF |
| F2 | should fix (L2/L3) | `_luat_ap_dung` | No test that applying a trial run's rule carries `chia_loai` | `ap_dung_tieu_chi` of a trial with `chia_loai` True | add one round-trip test with `ap_dung_tieu_chi` |
| F3 | minor | `get_chia_loai` | Corrupt stored `chia_loai` reports the unrelated code `error_reading_club_list` | hand-edited DB value `"yes"` | acceptable; optional dedicated code in `i18n_errors.py` (end of file) |

No blocking finding. L2 may start; carry F1 and F2 into the L2 test list. For L2 the checker will run: invariant 8 evidence for chi_xep+types and chia_100+types, rank-permutation test (invariant 2), STB lottery (3), 3×20 seed identity for OFF and `fa_daa`, and the missing-TU_DO workspace error.

## L2 — range 5c05848..0944994 (code ae6078c) — VERDICT: PASS (3 coder limits accepted with conditions; 1 minor test gap)

### Evidence
| Check | Result |
|---|---|
| `test_mt2_l1_cau_hinh.py` + `test_mt2_l2_chay.py` | 33 passed |
| `tests/test_fa_*.py`, gt2, mt1*, ws_luat, nhieu_buoi (legacy `fa_daa`, trial, estimate) | all passed, no failure |
| `kiem_nhanh.py --co-so 5c05848 --so-seed 20` | 7/7; invariant 1 byte-identical 3 datasets x 20 seeds (60 cases) for OFF |
| Legacy `fa_daa` identity | `loai_bat = dung_chia_loai and not fa_bat`, so the old branch is untouched; FA suites green |
| Inv 2 | `diem_wharton_hieu_luc` gives the same output for permuted preferences (my scratch test); `khoa_uu_tien_wharton` takes no rank; no rank/outcome reaches `chay_fa_daa(diem_wharton=...)` |
| Inv 3 | no change to `generate_stb_lottery` / lock; seeds re-run give identical results (coder test + mine) |
| Inv 4 / 5 | new checks run BEFORE lock/draw and `return _fail_co_buoc`; blocking error leaves `run_history`, `match_results`, `stb_lock` untouched (test). Write transaction unchanged (`kq_fa is not None` paths) |
| Inv 6 | new code `mt_thu_chua_ho_tro_loai` at END of `i18n_errors.py`, `i18n_loi.js` regenerated, `i18n_loi_khop` PASS |
| Inv 8 | `verify_stability` runs inside `run_pipeline` (rollback on blocking pair). My independent sim, SIMULATED data: 60 seeds x 2 modes (chi_xep, chia_100), 40 students, 4 clubs incl. 2 GIOI_HAN + 1 TUYEN_CHON + 1 TU_DO: 0 violations (120/120 ok). Coder's own: 24/24 |
| Trial / estimate | `run_thu` and `uoc_tinh_muc_tieu` (nang_luc, co_hoi) return `mt_thu_chua_ho_tro_loai` when ON; legacy `fa_daa` keeps its older codes (guards run first). `danh_cho` returns `mt_khong_co_nhom` (no group) as before |
| Missing TU_DO / missing `loai` / TUYEN_CHON without `diem_san` | clear blocking codes (`fa_thieu_clb_tu_do`, `fa_clb_thieu_loai`, `fa_clb_thieu_diem_san`), no crash, nothing written |
| Mutations (reverted, status clean) | drop `diem_wharton` pass-through: red. Disable validation return: red. Disable trial guard: red. Drop loai warnings into `canh_bao_wharton`: **no test red** (F4) |

### Rulings on the coder's known limits
| Limit | Ruling |
|---|---|
| (a) chia_100 + GIOI_HAN: points of two funds compared in one club (tier by test tick, scale differs) | ACCEPT for L2. Cause: a student who ticked a test for a GIOI_HAN club keeps fund-1 points while others use fund-2 points; the test score itself is dropped. Same shape as the existing A13 rule and the `fa_diem_bo_qua` warning already exists. Conditions: record it in the branch file Decisions; L3 should not offer the test tick for GIOI_HAN clubs, or the guide must say so. Truong may decide a stricter rule later (Needs Truong, informational) |
| (b) `get_data_health_report` lacks type checks for chia_loai-only | ACCEPT, but MANDATORY in L3: with the switch ON, readiness and the "next step" bar must report missing TU_DO / type / `diem_san` before Run, via `kiem_loai_tu_csdl` |
| (c) inv. 2 rank-permutation test only at `chay_fa_daa` level | ACCEPT. The pipeline adds no rank-dependent input (checked by reading `api.py` and by my permutation test on `diem_wharton_hieu_luc`). Optional: add a `run_pipeline`-level check in L4 |

### Findings
| # | Level | Where | Issue | Suggestion |
|---|---|---|---|---|
| F4 | minor | `api.py` `run_pipeline` (`canh_bao_wharton` from `kiem_loai_tu_csdl`) | Non-blocking type warnings (`MA_CANH_BAO`) reaching the result are untested | add one test in L3: a warning code appears in `warnings` when ON |
| F1, F2 (from L1) | closed | | now covered by `test_dau_van_tay_theo_loai_...` and `test_ap_dung_tieu_chi_mang_theo_chia_loai` | |
| note | info | `chia_100` ly_do | `huy_chuong` dict is reused to carry points to `ly_do_ket_qua`; reasons may use the word medal | check wording in L3/L4 |

L3 checker focus: UI switch default OFF, Hick/Von Restorff budgets, teacher role cannot see/call the write paths, OFF -> ON -> OFF keeps `clubs.loai`, readiness via `kiem_loai_tu_csdl` (limit b), XSS (club names with `<img onerror>`), API error rendering (`ok=false`), double-click, i18n vi/en.
