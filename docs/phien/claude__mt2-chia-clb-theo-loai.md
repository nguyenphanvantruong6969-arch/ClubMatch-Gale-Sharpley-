# Branch handoff: claude/mt2-chia-clb-theo-loai

> Read CLAUDE.md, then THIS file, then `docs/phien/MT2_GIAO_THUC.md`. English. Cap 150 lines.
> Status: PLANNED (2026-11-22). No product code yet. Planner note: written in a Sonnet session at Truong's
> request (rule 11 normally says Opus plans); the lead should re-check the Design section before GO L1.

## Feature / goal
Truong (2026-11-22): make "club types" (Tự do / Giới hạn / Tuyển chọn, `clubs.loai`) an adjustable setting in the
Quản lý tab: one on/off switch "Chia CLB theo loại". Truong's answers: (a) the type mode must COMBINE with BOTH
Điểm quyết tâm (`wharton`) and plain preference-order ranking, not only with Huy chương (`fa_daa`); (b) it can be
switched OFF; (c) the switch + per-club type choice live in sub-tab "Danh sách CLB" of Quản lý; (d) new item,
new branch (not merged into UX4). Item code **MT2** (MT1 family: club-type table). Size **L** (config key,
pipeline, invariants 1, 2, 8).

## Facts found (planner, 2026-11-22; read by function name)
- Types exist only inside Huy chương: `rules.fa_daa` requires `rules.wharton` (`dung_fa_daa`, `cau_hinh_ws.py`,
  error `FaTinhNangCanFa`). Settings has 3 cards (`UX1A_CACH` in `js/18_cai_dat.js`): `chi_xep` (wharton off),
  `chia_100` (wharton on), `huy_chuong` (fa_daa on). The type table is `ux1aVeSanSang`, shown only for `huy_chuong`.
- Type behaviour lives in `fa_daa.py` (`chay_fa_daa`): TU_DO never rejects (capacity = n students, reserve 0, used
  as session fallback); TUYEN_CHON filters by `diem_san`, key `(0,-score,(),-medal,stb,sid)`; GIOI_HAN drops the
  test score, key `(1,-medal,stb,sid)`. Validation: `fa_daa.kiem_dieu_kien`-style checks (every session needs a
  TU_DO club, every club has a type, TUYEN_CHON has `diem_san`).
- Save paths: `dat_loai_clb` (`api_quan_ly.py`), `update_workspace_config` (`cau_hinh_ws.py`). `LUAT_XEP_MAC_DINH`
  and `_luat_de_ghi_hoac_bam` (`rbda_priority_pipeline.py`) drop `wharton`/`fa_daa` from the stored rule and the
  fingerprint when False: a new key must do the same.

## Design (planner proposal; lead confirms or lists under "Needs Truong")
1. New rule key `chia_loai` (bool, default False). Effective switch = `chia_loai or fa_daa` (legacy Huy chương
   workspaces keep running unchanged, same stored rule string, same fingerprint). OFF = `loai` is IGNORED and
   hidden, never deleted; clubs run exactly as RB-DA does today.
2. ON with `chi_xep` (no points): TU_DO never rejects; GIOI_HAN ranked by STB; TUYEN_CHON filtered by `diem_san`,
   ranked by -test score then STB. No points/medal term.
3. ON with `chia_100` (Điểm quyết tâm): same, plus the student's points as the second key: GIOI_HAN
   `(1,-w,stb,sid)`, TUYEN_CHON `(0,-score,(),-w,stb,sid)` (the existing `khoa_uu_tien_wharton` shape).
4. ON with `huy_chuong`: unchanged (points = medals).
5. Invariant 2: no rank, no past outcome in any key. Invariant 8: modes 2 and 3 use a choice function the
   algorithm has not registered before: run the substitutability / aggregate-demand check (item A12 tool); if it
   fails, label "không bảo đảm ổn định" and use measurement mode. Report the measured result, do not hide it.
6. UI: in Quản lý → "Danh sách CLB" ONE switch "Chia CLB theo loại" (default OFF = pre-selected). ON reveals the
   per-club type buttons (reuse the MT1 table markup) and the pass-mark input; OFF hides them (Hick budget of
   UX4: ≤ 7 controls, one gold button). Settings keeps its 3 cards; their text says whether types are on.
   Keep ids; teacher role never sees the tab. i18n prefix `mt2_`; new error codes at END of `i18n_errors.py`.

## Plan (written by Planner; ticked by Sonnet coder)
- [ ] **L1 Config + switch (MUST).** `chia_loai` in `LUAT_XEP_MAC_DINH`, `cau_hinh_ws.py` validation,
      `_luat_de_ghi_hoac_bam` / `luat_xep_hieu_luc` (omit when False, true when `fa_daa`), `phan_quyen.py` entry,
      getter used by UI. Tests: OFF/legacy results byte-identical (3 datasets × 20 seeds, `kiem_nhanh.py` 7/7);
      stored rule string unchanged for old workspaces; `fa_daa` on implies effective types on.
- [ ] **L2 Pipeline (MUST, L-size).** Make `loai` handling in `fa_daa.chay_fa_daa` callable without medals:
      mode 2 and mode 3 above, via the existing key builders. Validation errors (missing type, no TU_DO per session,
      TUYEN_CHON without `diem_san`) apply whenever the switch is ON. Substitutability check (invariant 8) +
      report. Tests: failing first for each mode; STB lottery unchanged (invariant 3); `run_history` appended (4).
- [ ] **L3 UI (MUST).** Switch + reveal in "Danh sách CLB"; MT1 table reused; persists via the config path; the
      "Việc tiếp theo" bar and readiness (`get_san_sang_huy_chuong` or a renamed read) work for non-medal modes.
      Playwright: Hick/Von Restorff budgets on the sub-tab; ON/OFF round trip keeps stored `loai`.
- [ ] **L4 Docs (OPTIONAL-able).** CHANGELOG, TIEN_DO, `SO_DANG_KY_33_MUC.md` row MT2, `HUONG_DAN_SU_DUNG.md`,
      export contract: Sổ nhập already carries `loai`; do NOT change columns (invariant 7).

## Acceptance
- Switch OFF (default) and every existing workspace: `match_results` byte-identical, 3 datasets × 20 seeds.
- ON × {chi_xep, chia_100, huy_chuong} each runs end to end on simulated data (seed 3) and `verify_stability`
  result is reported (stable, or labelled "không bảo đảm ổn định" with the measured violation count).
- Round trip OFF → ON → OFF leaves `clubs.loai` values intact.
- All numbers are SIMULATED; never call them a real survey. Conclusions for the report are Truong's to write.

## Decisions and gotchas
- A type never reads preference rank (invariant 2). Medal defaults from rank stay confined to the FA-DAA
  registration layer as already authorised (D2).
- `tests/test_ws_nhan.py` snapshots UI strings: add intentional changes to `SUA_CO_Y` with a `MT2` comment.
- UX4 (branch `claude/ux4-quan-ly-de-hieu`) redesigns the same tab, not merged: keep ids; expect a small merge.

## Status
- LEAD started 2026-11-22. Design reviewed: accepted as written (no design change needed; lead = Sonnet).
- L1 PASS (checker 948f753) | L2 PASS (checker 6988b09) | L3 PASS (L3-FIX checker PASS) | L4 PASS | MT2 DONE (L1-L4 PASS) | STRESS PASS | R1 + R1-FIX PASS | PR #28 opened; CI-1 fix (tkNutMoHop 44px, UX3 CSS) pushed, CI rerun pending

## Sessions
| Role | Session id | Model | Notes |
|---|---|---|---|
| LEAD | session_01YVAyu3BTRoD9jYgVDEJ86g | Sonnet | this branch file only |
| CODER | session_01YVAytzKYmkQsmVJ6CvbkXT | Sonnet | |
| CHECKER | session_01YVAyu1qB1UHaWqW9cvwFqw | Sonnet | |

- L2 ruling (checker): chia_100 + GIOI_HAN mixes point scales (tier by tick); accepted. L3 must not offer the test tick for GIOI_HAN clubs, or document it. Health-report type checks via kiem_loai_tu_csdl are MANDATORY in L3; add a test for non-blocking type warnings (F4).

## Needs Truong
- RESOLVED (Truong, 2026-11-22): GIOI_HAN clubs have no exam, so nobody has a test score there and every student uses fund 2 (same scale); only the point fund decides. No scale mixing in normal use. DQ1 (one fund) NOT needed for this. Optional: non-blocking warning if a GIOI_HAN club has test scores; HUONG_DAN §17 'known limit' wording may be softened to say it only arises if a GIOI_HAN club has exam scores.
- Confirm trial runs and estimates stay refused (mt_thu_chua_ho_tro_loai) while the switch is ON.
- Decide whether a compact type picker is wanted later (28 controls when the switch is ON).
- Optional, not done: Settings-cards sentence saying whether types are on (plan item 6); F6 error-toast test; F7 phone overflow (pre-existing); SO_DANG_KY lists dependency MT1 with no registry row; HUONG_DAN §17 omits the capacity check for GIOI_HAN/TUYEN_CHON.

## Current state
- MT2 L1-L4 + R1 coded, reviewed, PASS; stress PASS. PR #28 open, awaiting Truong. Next: Truong tries the switch and answers "Needs Truong".

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Sonnet | Asked Truong 3 questions; wrote plan + protocol | no code |
