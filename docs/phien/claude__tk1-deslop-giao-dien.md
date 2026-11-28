# Branch handoff: claude/tk1-deslop-giao-dien

## Feature / goal
TK1 (NEW item, proposed 2026-11-28, pending Truong's approval — running the lead prompt = approval): make the kiosk UI
calm and steady ("deslop"). UI only: `style.css`, `index.html`, `js/*.js`, `i18n.js` labels. No backend, algorithm,
CSV or schema change (invariants 1–8 untouched by construction). Audit + numbers: `docs/ke_hoach/TK1_DESLOP_GIAO_DIEN.md`.
Out of scope: registration portal `dang_ky.html` (VG3 just redesigned it).

## Plan (written by Opus; ticked by Sonnet)
- [x] L0 Register TK1 in `docs/ke_hoach/SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json` (one row, sectors "–").
- [x] L1 (must) Tokens on `:root`: type scale (12/13/14/16/20/28 px as rem), space scale (4·8·12·16·24·32·48),
      `--control-h-sm: 36px`, `--control-h: 44px`, radius 6/10/pill, 2 shadows, 2 durations. Replace literals.
      `html { scrollbar-gutter: stable; }`. Red test first: distinct font-size count ≤ 8; h1 `left` equal on all tabs.
- [ ] L2 (must) One control system: `.btn`, `input`, `select`, custom dropdown share height per row (36 or 44),
      same border/arrow. Remove `.btn-goi-y` 2px black border + lightbulb; `btnCt1Mo` becomes `.btn-secondary`.
      Max one `.btn-primary` per toolbar. Test: all visible controls in `#view-results` toolbar have equal height.
- [ ] L3 (must) One tab component for Kết quả segmented tabs and Quản lý `#qlTabs`; `min-width` + bold-width
      reservation (`::after{content:attr(data-label);font-weight:700;visibility:hidden;height:0}`). Top alert strip:
      fixed height, quiet style, button text "Xem <n> em chưa có CLB" via i18n key (vi + en).
      Test: tab widths unchanged after click and after vi↔en toggle.
- [ ] L4 (optional) KPI cards drop left accent bar; "?" inline with its label; card padding from tokens;
      sidebar "Tài khoản" as secondary/quiet.
- [ ] Final: 3 screenshots (before/after) at 1366×768 in branch file notes; CHANGELOG + TIEN_DO (rule 6).

## Current state (overwrite each handoff)
- Done so far: L0 (registry + JSON), L1 (tokens on `:root`, literals replaced in non-`.dk-*` rules, `scrollbar-gutter`).
- Tests: `tests/test_tk1_on_dinh.py` (3 tests, green). L1 gate: + ux2_nut, ux5a_l2, 7 style.css-reading files green;
  `kiem_nhanh.py` 7/7 (needs `git fetch origin main` first). Local env: no `.venv`; `pip install playwright pillow
  python-docx pypdf reportlab ruff` into system python3 works.

## Decisions and gotchas (keep short)
- Control heights 36/44 chosen because both already exist (6× and 10× in style.css) and 44 = kiosk touch target.
- Scrollbar shift is inferred (body scrolls, WebView2 classic scrollbar); confirm on Windows in final review.
- Keep `.dk-*` portal rules untouched; scope new tokens so portal output is pixel-identical (screenshot check).
- L1 snap rules (script, non-`.dk-*` rules only): font px/rem→6 tokens (`html` is 14 px so 1 rem = 14 px; tokens in px,
  not rem); spacing px→4-pt scale (6→8, 10→8, 14→12, 18/20→16, 22/26/28→24, 40/64→48, 2/3/5→4; 1 px kept, `em`/`calc` kept);
  height 44/36 → `--control-h`/`--control-h-sm` (same value); radius 3/4/6/8→sm, 10/20→md, 999→pill; transition
  ≤160 ms→`--dur-1` (150), ≤260 ms→`--dur-2` (240); 6 drop shadows→`--shadow-1/2` (inset rings/accent bars untouched).
- Gutter is `html:has(body:not(.dk-body))`: plain `html{scrollbar-gutter}` shifted the portal by the gutter width
  (screenshot diff). With the `:has()` scope the portal login screenshot is pixel-identical (1366×768).
- Static font-size count (test) skips `.dk-*`, `em`, `%`, `var()` values; counts 6 tokens + any literals ≤ 8.
- Test updated: `test_giao_dien_ux2_chuyen_canh.py::test_o_nhap_trong_hang_55px_…` row height 55→51 (cell padding
  14→12 px on the 4-pt scale; the test is about the no-slide-in effect, not the height).

## Next steps (ordered)
1. L2 (controls), then L3, then write `MILESTONE 1 READY` after L2.

## Files touched
- docs/ke_hoach/TK1_DESLOP_GIAO_DIEN.md: audit + research
- docs/phien/claude__tk1-deslop-giao-dien.md, docs/phien/TK1_GIAO_THUC.md: plan
- L0: docs/ke_hoach/SO_DANG_KY_33_MUC.md, ke_hoach_thay_doi.json. L1: style.css, tests/test_tk1_on_dinh.py,
  tests/test_giao_dien_ux2_chuyen_canh.py (one assert)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus (planner) | Measured style.css, screenshots 6 tabs × 2 widths, wrote audit + plan | no product code |
| 2026-11-28 | Sonnet (coder) | L0 registry; L1 tokens + gutter, test first | portal login pixel-identical |
