# Branch handoff: claude/mt1-bang-loai-clb

## Feature / goal
Rebuild the Settings block "To use Medals, choose a type for each club" (`ux1aVeSanSang`, `js/18_cai_dat.js`) as a
TABLE: one row per club, three type buttons with a pressed state, pass mark inline for Selective, rows grouped by
session with a "has / needs a Free club" mark, a progress counter, one-line explanations of the three types, and no
dropdown (it duplicated the Free button). Registry: grouped into MT1 (Truong, 2026-11-21). UI only: saves still go
through `dat_loai_clb`; no new save path, no CSV/schema change. Branched from `claude/pensive-turing-s02bgi` @ 6c97791
(MT1 is not merged to `main` yet; `main` is an ancestor, so this branch carries all MT1 work).
Truong explicitly told this session to code now, so the planning-Opus step of rule 12 was skipped for this small item.

## Plan (written by Opus; ticked by Sonnet) -- plan reconstructed from the design Truong approved ("B")
- [x] Failing tests first: `tests/test_giao_dien_mt1_bang_loai.py` (6 cases).
- [x] Table markup + counter + explanations; focus returns to the pressed control after the redraw.
- [x] i18n vi+en: `ux1a_ss_con_thieu` (reworded), new `ux1a_ss_dem`, `ux1a_ss_gt_*`, `ux1a_ss_buoi_*`; removed `ux1a_ss_chon_tu_do`, `ux1a_ss_thieu_tu_do`.
- [x] CSS (`style.css`, `.ux1a-ss-*`).
- [x] Update the old test that assumed rows vanish and a dropdown (`test_giao_dien_ux1_cai_dat.py`).
- [ ] Checker pass (rule 12 asks for a separate Sonnet checker) and Truong's visual review.

## Current state
- Done: all of the above. Tests run: `test_giao_dien_ux1_cai_dat.py`, `test_giao_dien_ux1b_l5c.py`,
  `test_giao_dien_mt1.py`, `test_giao_dien_mt1_bang_loai.py`, `test_i18n_sync.py`, `test_i18n_khoa_dc_khong_chet.py`: 66 passed. `ruff check .` clean.
- Not run: the full suite (CI runs it); `soat-ma` tiers beyond `kiem_nhanh.py` (its `trung_khit` item cannot run here: no `origin/main` ref).
- Open: the "Sẵn sàng" state hides the table once every club has a type (existing behaviour); changing a type afterwards is done in Quản lý -> Câu lạc bộ.

## Decisions and gotchas
- The table lists ALL clubs (needed for the counter and per-session marks); the old panel listed only clubs missing a type.
- Type buttons follow the `loai` column, never the club name (a test renames clubs to include "(Giới hạn A)").
- `.text-input { min-width: 240px }` and `.data-table td:first-child` (monospace) leak into the block: overridden in `.ux1a-ss-*` rules.
- `luu` also calls `loadAdminClubs()` and `capNhatViecTiepTheo()` (earlier commit 6c97791) so the club table and the next-step bar refresh.

## Next steps
1. Truong reviews the screenshots; adjust wording/layout if asked.
2. Run the rule-12 checker (Sonnet) on the diff; run the full suite in CI.

## Files touched
- js/18_cai_dat.js: table markup, counter, inline pass mark, focus restore
- i18n.js: new/changed strings (vi+en)
- style.css: `.ux1a-ss-*` table styles
- tests/test_giao_dien_mt1_bang_loai.py (new), tests/test_giao_dien_ux1_cai_dat.py (updated)

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-21 | Sonnet | Built the table, tests, i18n, CSS | Truong approved design B and said to code now |
