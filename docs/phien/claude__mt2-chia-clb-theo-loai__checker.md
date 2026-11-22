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
