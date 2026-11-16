# Branch handoff: claude/ecstatic-curie-cw61js

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Written by the session when context passes ~400k tokens (after finishing its current prompt).

## Feature / goal
New registry item **PA-HC** (Truong approved "mở mục mới", 2026-11-16): in the Power Apps kit for FA-DAA path A
(`mau_forms_thi_clb/tao_bo_dung_t4m.py --fa-daa`), an OPTIONAL medal mode with THREE dropdowns per day:
"Huy chương vàng trao cho CLB nào?", then silver, then bronze. Each lists the student's ranked clubs of that day
(no FREE club), a club picked above disappears below, bronze is hidden when only 2 eligible clubs (silver when 1).
Students choose directly; no rank-derived default (invariant 2 safe). Exam = path A as today (button
`Launch(FormUrl)` to the club's Microsoft Forms quiz; Truong chose "A rút gọn": no "Đã làm" flows needed).
Kiosk core, `match_results`, `run_history`, CSV contract: untouched. List columns unchanged (`WP1..WP7`, `HC_TuChinh`).
Everything is TH (not run on real Power Apps).

## Plan (written by Opus; ticked by Sonnet)
- [ ] 0. Registry: add PA-HC to `docs/ke_hoach/SO_DANG_KY_33_MUC.md` and `ke_hoach_thay_doi.json`, same format as
      existing items (state, change, risk, kiem_nhan = tests below). Do not reorder `nganh[].ke_hoach`.
- [ ] 1. Tests first: `tests/test_pa_hc_ba_dropdown.py` (pattern: `tests/test_fa_gap11_cong_thuc_fa.py`):
      a) `cong_thuc_fa.tao_dang_ky_fa(de, hc_ba_o=True)` contains blocks `ddVang.Items`, `ddBac.Items`, `ddDong.Items`,
         `.OnChange` of each, `ddBac.Visible`, `ddDong.Visible`; each Items filters `Loai <> "Tự do"`;
         `ddBac.Items` excludes `ddVang.Selected.ClubId`; `ddDong.Items` excludes both;
         visibility uses CountRows of eligible clubs `>= 2` / `>= 3`.
      b) hc_ba_o text has NO rank-derived default: no `CAP_NHAT_HC` block, no `Index(ds, 1)`, no per-row `ddHC`.
      c) every save in hc_ba_o writes `HC_TuChinh: "Có"` (so the converter's `ap_huy_chuong_duong_a` never fills
         rank defaults: blank = no medal).
      d) `tao_dang_ky_fa(de)` (default) byte-identical to before (store sha256 of current output in the test, computed
         BEFORE editing code); `tao_bo_dung(..., fa=True)` without the flag byte-identical too; default kit has no change.
      e) CLI: `--hc-ba-o` without `--fa-daa` -> error exit; with it -> `02_app/DangKyFA.txt` has the three dropdowns.
      f) Converter: ECA.csv (FA) row, all `WPk` blank + `HC_TuChinh = "Có"` -> no medal for that day
         (`ap_huy_chuong_duong_a`); same row with `WP2=60` -> gold on NV2. Probably passes already: then it is a
         regression guard, say so in CHANGELOG.
      g) Same `de` -> same bytes in hc_ba_o. Delegation check (`cong_thuc.soat_loc_uy_quyen`) returns [].
      Mutation to try: drop the `ddVang.Selected.ClubId` exclusion -> test a red.
- [ ] 2. Code (`mau_forms_thi_clb/bo_dung_t4m/cong_thuc_fa.py`): `tao_dang_ky_fa(de, hc_ba_o=False)`.
      When True: `_sau_thao_tac()` = TU_LUU only (no CAP_NHAT_HC); TU_LUU variant writes `HC_TuChinh: "Có"`;
      replace the "Widget huy chương" section by a new `_khoi_hc_ba_o()` section:
      `ds = Sort(Filter(colXep, Thu = varThu And Loai <> "Tự do"), ViTri)`;
      `ddVang.Items = ds`; `ddBac.Items = Filter(ds, ClubId <> ddVang.Selected.ClubId)`;
      `ddDong.Items = Filter(ds, ClubId <> ddVang.Selected.ClubId And ClubId <> ddBac.Selected.ClubId)`;
      `DefaultSelectedItems` = `LookUp(XEP_NGAY, HC = 60|30|10)` (restores saved state); note AllowEmptySelection = true;
      `OnChange` (gold, value 60): `UpdateIf(colXep, Thu = varThu And HC = 60, {HC: 0});
      If(!IsBlank(sel), UpdateIf(colXep, Thu = varThu And ClubId = sel, {HC: 60}))`, then the save block; same for 30, 10.
      Picking a club that held another medal overwrites it (that dropdown then shows blank: Default re-reads).
      Labels: question texts via `T("hc_hoi_vang")` etc., add to a NHAN list printed only in hc_ba_o
      (Vi: "Huy chương vàng trao cho CLB nào?" / En: "Which club gets your gold medal?"; same for bạc/đồng).
      Header note: "lọc trên collection cục bộ"; label TH.
- [ ] 3. Wiring: `sinh_bk1.ghi_tat_ca(..., hc_ba_o=False)`, `cong_thuc_fa.ghi_fa(ra_dir, de, hc_ba_o=False)`,
      `tao_bo_dung(..., hc_ba_o=False)`, CLI `--hc-ba-o` (requires `--fa-daa`; help text TH). README_BK1 line only
      when the flag is on (default README byte-identical).
- [ ] 4. IT guide (`bo_dung_t4m/huong_dan_it.py`, only when flag on): 3 Dropdown controls inside the day screen,
      names as in the kit; "Items hiện tên CLB: chọn trường Ten/ClubId" (HỎI-IT: real column name).
- [ ] 5. Related tests only: `tests/test_pa_hc_ba_dropdown.py tests/test_fa_gap11_cong_thuc_fa.py
      tests/test_fa_m5_bo_dung.py tests/test_t4m_bo_dung_bk1.py tests/test_t4m_bo_dung_bk34.py`; `ruff check .`.
- [ ] 6. CHANGELOG (PA-HC, files, tests), `docs/ke_hoach/TIEN_DO.md`, skill `soat-ma` (kiem_nhanh + 4 tiers,
      report only), push to this branch. No PR unless Truong asks.

## Current state (overwrite each handoff)
- Plan written (Opus, 2026-11-16). No code yet. Next session: Sonnet runs the Plan from step 0.
- Tests: none run yet on this branch.

## Decisions and gotchas (keep short)
- Exam channel = path A "rút gọn" (Truong, 2026-11-16): Forms quiz via `Launch(FormUrl)`, already in
  `cong_thuc.tao_thi_tuyen`; flows "Đã làm" optional. Path B (exam inside the app, offline grading of a `BaiLam`
  list in kiosk step 4) postponed. PowerShell cannot build a Power App (T4M_KET_QUA_TAI_LIEU.md §8.2); a later item
  `BUILD-PS` = one-line `CAI_DAT.txt` that installs the kiosk .exe from a GitHub Release.
- Flag, not replacement: old widget (rank defaults + swap, R48–R52) stays default (rule 4, invariant 1 for the kit).
- Defaults chosen by Opus, Truong may change: medals OPTIONAL (as `kiem_ho_so_huy_chuong` allows < 3); dropdowns
  start EMPTY; blank = no medal (hence `HC_TuChinh = "Có"` on save).
- FREE clubs never in dropdowns: `fa_daa.kiem_ho_so_huy_chuong` rejects medals on TU_DO (`fa_huy_chuong_clb_tu_do`).
- "Only show a day if ticked": `galNgayFA.Items` lists only the student's `ECA` rows, assumed to exist only for days
  the student ticked in the school's ECA app (HỎI-IT). No new code for this unless IT says otherwise.
- OPEN (ask Truong, not blocking PA-HC): in FA mode there is no `THIk` tick; the exam card screen
  (`tao_thi_tuyen`) filters by ticks (`colChon`). FA exam cards should come from ranked SELECTIVE clubs instead.
  Truong earlier described "tick chọn thi" per day: confirm before changing.

## Next steps (ordered)
1. Sonnet: Plan steps 0–6.
2. Opus/Truong: decide the FA exam-card question above; then item `BUILD-PS`.

## Files touched
- docs/phien/claude__ecstatic-curie-cw61js.md: this handoff (plan).

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Opus | War room with Truong: build, Power Apps, medals, exam channel; wrote PA-HC plan | No code |
