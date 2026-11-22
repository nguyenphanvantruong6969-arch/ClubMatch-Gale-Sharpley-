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

## L3 — range e50c4b6..58b7749 — VERDICT: FIX (one small user-facing text defect, F5; everything else PASS)

### Evidence
| Check | Result |
|---|---|
| `test_mt2_l3_backend.py` + `test_giao_dien_mt2.py` + L1/L2 files | 40 passed + 6 UI passed. NOTE: the UI file is silently SKIPPED without python `playwright`; I installed it (`pip install playwright`, `RBDA_TEST_CHROMIUM=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`) and ran it for real: 6/6 |
| Wider UI + backend regression (ws_nhan, gt3 phan_quyen + UI, all `*ux1*`, `giao_dien_mt1*`, `giao_dien_fa*`) | 287 passed, 0 skipped |
| `kiem_nhanh.py --co-so e50c4b6` | 7/7 (default byte-identical, no engine change in L3) |
| Teacher role | `update_workspace_config` and `dat_loai_clb` return `gt3_khong_du_quyen` for a teacher (test); panel has `data-quyen="quan_tri"`. `get_chia_loai`/`get_san_sang_loai` are read-only |
| OFF -> ON -> OFF -> ON keeps `clubs.loai` | backend test + UI test (GIOI_HAN pressed again after re-enable) |
| Health report type checks (limit b) | `get_data_health_report` runs `kiem_loai_tu_csdl` when ON and not `fa_daa`; blocking = high, warnings = medium; F4 covered by `test_canh_bao_khong_chan_...` |
| XSS | club name `<img src=x onerror=...>` shown as text, `window.__xss` undefined |
| Double click / backend `ok=false` | switch disabled while saving; on failure it returns to the saved state (UI tests) |
| Medal mode | switch checked + disabled, no duplicate table (id clash avoided) |
| Mutations (reverted, status clean) | health block off: red. list column `dung_chia_loai`->`dung_fa_daa`: red. `san_sang` always true: red. remove `cb.disabled=true`: red. remove `d.fa_daa` guard: red. remove `showErrorToast`: **no test red** (F6, minor) |
| Hick / Von Restorff (screenshots at 1280 px, DSF 1) | OFF: exactly 1 visible control in the block, 0 gold buttons (test). ON: 28 visible controls = 1 switch + 3 type buttons x 8 clubs + 3 info icons; 0 gold buttons inside the block (the page's single gold "Việc tiếp theo" button is outside it) |

### Findings
| # | Level | Where | Issue | Path | Fix |
|---|---|---|---|---|---|
| F5 | MUST FIX (small) | `i18n.js` `ux1a_ss_gt_GIOI_HAN` shown in the MT2 table | Tooltip says "xếp theo huy chương rồi bốc thăm" (EN: "ordered by medal, then a lottery") although MT2 modes have no medals | switch ON in "Chỉ xếp" or "Chia 100 điểm", hover the "i" next to "Giới hạn": text claims medals | In the MT2 call (`ux1aVeSanSang` option) use a neutral key, e.g. `mt2_gt_GIOI_HAN`: "Có chỉ tiêu, không xét điểm thi: xếp theo điểm quyết tâm (nếu có) rồi bốc thăm." plus the EN twin; keep the old key for Medal mode. Add one UI assertion that the tooltip text has no "huy chương" in MT2 mode |
| F6 | minor | `mt2KhoiTaoChiaLoai` | No test asserts the error toast text on `ok=false` | mutation survived | optional assertion on `#toast`/error element |
| F7 | minor (info) | layout | At 390 px the whole admin page already overflows (OFF: scrollWidth 631); ON widens it to 896 because of the table | kiosk is a desktop Windows app, so not blocking | none now |
| F8 | info for Truong | Hick budget | The plan says "<= 7 controls", but the per-club type table is data entry (8 clubs x 3 buttons). Reading the budget as "choices outside the table" it holds | accept; Truong may want a compact picker later | none |

### Rulings
- Settings-cards sentence (plan item 6 last sentence): NOT required for L3. The switch has its own note and Medal mode shows "on because Medal mode". Move to L4 as optional.
- Limit (a) from L2 (GIOI_HAN test tick): the new note `mt2_ghi_chu` says a Limited club ignores exam scores, which is enough for L3; the tick itself is still offered. Accepted.

After F5 the checker needs only: i18n key test + `kiem_nhanh` + the 6 UI tests; then L3 PASS.

## L3-FIX — range 33d232f..b364d17 — VERDICT: PASS (L3 now PASS)

| Check | Result |
|---|---|
| F5 | new key `mt2_gt_GIOI_HAN` (vi + en) used only via `tuyChon.khoaGt` from `mt2VeChiaLoai`; Settings/Medal mode still use `ux1a_ss_gt_GIOI_HAN` (old key unchanged; Settings UI tests green) |
| New UI assertion | `test_chu_i_cua_gioi_han_khong_nhac_huy_chuong` passes; mutation (remove `khoaGt`) makes it red |
| Playwright | `playwright` importable here; `test_giao_dien_mt2.py` 7/7 unskipped (-rs shows no skips); with `test_mt2_l3_backend`, `ux1_cai_dat`, `fa_cai_dat`, `ux1b_l5c`, `ws_nhan`: 88 passed |
| Engine | diff touches no `.py` file other than the test; no engine change, default byte-identical (`trung_khit` 15 cases pass) |
| kiem_nhanh 5/5 vs 7/7 | full run here is 7/7 (ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, trung_khit, khong_sua_nhat_ky); none failing. The coder's "5/5" was a subset (`--chi`), not a failure |
| Wording | EN says "commitment points"; no banned words (`chu_cam` pass) |

No new findings. F6, F7, F8 stay as minor/info. L4 (docs, optional): Settings-cards sentence, `SO_DANG_KY_33_MUC.md` row, `HUONG_DAN_SU_DUNG.md`, CHANGELOG/TIEN_DO; checker will verify invariant 7 (no column change) and the run_pipeline-level rank-permutation test if added.

## L4 — range 781edd6..cd6564f — VERDICT: PASS (docs only; 2 minor notes)

| Check | Result |
|---|---|
| Scope | `git diff --name-only`: CHANGELOG, HUONG_DAN_SU_DUNG, CLAUDE_CHI_TIET, SO_DANG_KY_33_MUC, TIEN_DO, branch file. No `.py/.js/.html/.csv/.xlsx`: invariant 7 untouched, default behaviour untouched |
| HUONG_DAN section 17 vs code | table of the three types matches `chay_fa_daa` / `kiem_truoc_fa` (Tự do never rejects + fallback; Giới hạn drops test score, points then lottery; Tuyển chọn floor, score, points, lottery). Blocking list matches `fa_thieu_clb_tu_do`, `fa_clb_thieu_loai`, `fa_clb_thieu_diem_san`, `fa_clb_tuyen_chon_chua_co_diem`; reservations are warning-only. Known limits (trial/estimate refusal, two-fund scale in Giới hạn) match my L2 rulings. Table of contents entry present |
| SO_DANG_KY row | 12 sector cells, TS = O, same shape as neighbouring rows; MT2 section lists the right files and acceptance |
| CLAUDE_CHI_TIET | `ls tests/test_*.py | wc -l` = 378: the coder's 372->378 edit is correct and makes `test_a13_12_tai_lieu.py` pass |
| Tests / lint | doc tests (`a13_12_tai_lieu`, `*tai_lieu*`, `*huong_dan*`): 66 passed; `ruff check .` clean; `kiem_nhanh.py` 7/7 |
| Academic integrity | stability numbers are labelled SIMULATED (HUONG_DAN limits, SO_DANG_KY risk, CHANGELOG); no report conclusions or interpretation drafted |
| Settings-cards sentence | recorded in CHANGELOG as not done (dynamic text); consistent with my L3 ruling (optional) |

Minor notes (not blocking): (1) SO_DANG_KY lists dependency "MT1" but that registry has no MT1 row; (2) section 17 does not mention the capacity (`fa_clb_thieu_suc_chua`) check for Giới hạn / Tuyển chọn clubs. Optional one-line fixes.

### MT2 overall (checker summary, all numbers SIMULATED)
L1, L2, L3 (+FIX 1), L4: PASS. Open minor items: F6 (error toast untested), F7 (phone overflow, pre-existing), F8 (28-control table, Truong may want a compact picker), the two L4 notes. Items for Truong (not for the checker): confirm the two-fund scale rule for Giới hạn under Chia 100 điểm, and that trial runs / estimates stay refused while the switch is ON. The checker never edited product code or tests.

## Stress test (head 6aaf992, code unchanged since L4; all data SIMULATED, scratch scripts only, no product/test edits)

Data: `du_lieu_test/SO_NHAP_DQT_800HS_HOP_LE.xlsx` (800 students, 20 clubs, 4 sessions of 5 clubs, 230 seats per session), `SO_NHAP_MAU_120HS_3BUOI.xlsx` (120 students, 9 clubs, 3 sessions), `SO_NHAP_FA_MAU_120HS.xlsx`. Base for identity = commit 117432d (code before L1), extracted with `git archive`.

| # | Scope | Result |
|---|---|---|
| 1 | OFF and legacy `fa_daa`, 5 dataset/mode combos x 20 seeds = 100 cases, base vs head, default config AND explicit `chia_loai=False`. Compared every `match_results` row, STB numbers (`students`, `stb_buoi`), run ok flag, stored `run_history.luat_xep` string, `fa_nhom` rows. Combos: 800 chi_xep, 800 chia_100, 120 3-session, FA120 OFF, FA120 legacy `fa_daa` (types set by SQL) | **100/100 identical in both variants; stored rule strings identical (0 differ)**. Note: legacy `fa_daa` sample had no rejected student, so `fa_nhom` stayed empty; identity of results and rule string still holds |
| 2 | ON x chi_xep and ON x chia_100 at 800x20, **150 seeds each**, random type layout per seed (1 TU_DO per session, rest GIOI_HAN/TUYEN_CHON; TUYEN_CHON present in 149/150 seeds, GIOI_HAN in 150/150; floors at 20/40/60 % quantile). Per run: pipeline ok (it runs `verify_stability`; blocking pair means rollback+error), 3200 rows = 800 x 4, no unmatched, capacity never exceeded (non TU_DO), TU_DO never rejects (no student ends worse than their best TU_DO), TUYEN_CHON members all have score >= floor, rerun same seed = identical `match_results` and STB, other seed on locked lottery is refused (`hat_giong_da_khoa`) and writes nothing, `run_history` append-only (1 -> 2 rows, old row unchanged, refusal adds nothing) | **0 violations, 0 failed runs in 300/300**. Extra independent blocking-pair check (own code, not the pipeline's) for chi_xep: 0 blocking pairs in 150/150; chia_100 relies on the pipeline's own `verify_stability` (0 failures). The checker itself was sanity-tested: a tampered row is reported (capacity and floor violations) |
| 2t | Timing, `run_pipeline` 800x20 | sequential, 20 runs each: chi_xep p50 0.61 s, max 0.84 s; chia_100 p50 0.42 s, max 0.50 s. Under 4 parallel processes (150 runs): chi_xep p50 0.74 / max 1.18 s; chia_100 p50 0.51 / max 0.80 s. Coverage note: about 47 % of rows are fallback to a Tự do club (800 students vs 230 seats per session), 36-37 % got rank 1 |
| 3 | Multi-session + late arrivals | 800 (4 sessions): 30 late students added after the locked first run, 10 seeds x 2 modes: **20/20 ok**, old students' relative STB order unchanged in every session, all late students got numbers, all constraints hold (chi_xep also the independent blocking check). In chia_100 the late students must also submit a 100-point profile per session and fund (otherwise `wharton_ho_so_chua_hop_le`, a clear blocking error; expected, not a bug). 120HS 3-session chi_xep ON: 20/20 seeds ok, constraints hold |
| 4 | Edge cases (11) | missing TU_DO in one of two sessions: blocked `fa_thieu_clb_tu_do`; TUYEN_CHON without `diem_san`: `fa_clb_thieu_diem_san`; single GIOI_HAN club only: `fa_thieu_clb_tu_do`; no clubs / no students: `chua_co_du_lieu_de_chay` (no crash); same two blocking cases under chia_100: same codes. Every blocked case: table row counts and stb lock identical before/after (**writes nothing**). Run OK: all clubs TU_DO (everyone gets 1st choice, 6 rows), empty preferences for some students (fallback to the Tự do club), one TU_DO club, TUYEN_CHON student without score (excluded, falls to TU_DO). |
| 5 | Toggle | OFF->ON->OFF x50 through `update_workspace_config` in a real workspace: `clubs.loai/diem_san` identical after every step (0 of 150 comparisons differ), `get_chia_loai` always matches. Rapid toggling: 8 threads x 40 calls = 320 calls, 0 errors, config readable, `loai` intact, a run afterwards ok. Teacher: `update_workspace_config`, `dat_loai_clb`, `run_pipeline` -> `gt3_khong_du_quyen`; read-only `get_chia_loai` allowed |
| 6 | Invariant 2 | Recorded the club priority list (`uu_tien_wharton`) while running: original vs one third of students with their preference order shuffled, 8 seeds x 2 modes: the initial priority list of every club is IDENTICAL in 16/16; the lists of later solver passes (after fallback adds students to a Tự do club) keep the same relative order. Results did change in 16/16 (the permutation has real effect), so the test is not vacuous |

**STRESS PASS.** No bug found, no failing seed. Caveats (not bugs): (a) chia_100 stability uses the pipeline's own `verify_stability` (independent check done for chi_xep only); (b) only 6 of the 20 clubs in the 800 sample have exam scores, so TUYEN_CHON sees few distinct clubs per run; (c) the legacy `fa_daa` identity case rejects nobody. Scripts: scratchpad `st_common.py`, `st_run.py`, `st_ident.py`, `st_misc.py` (not committed).
