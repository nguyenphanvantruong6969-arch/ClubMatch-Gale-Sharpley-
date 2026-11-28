# Branch handoff: claude/tk1-deslop-giao-dien

## Feature / goal
TK1 (NEW item, proposed 2026-11-28, pending Truong's approval — running the lead prompt = approval): make the kiosk UI
calm and steady ("deslop"). UI only: `style.css`, `index.html`, `js/*.js`, `i18n.js` labels. No backend, algorithm,
CSV or schema change (invariants 1–8 untouched by construction). Audit + numbers: `docs/ke_hoach/TK1_DESLOP_GIAO_DIEN.md`.
Out of scope: registration portal `dang_ky.html` (VG3 just redesigned it).

## Plan (written by Opus; ticked by Sonnet)
- [ ] L0 Register TK1 in `docs/ke_hoach/SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json` (one row, sectors "–").
- [ ] L1 (must) Tokens on `:root`: type scale (12/13/14/16/20/28 px as rem), space scale (4·8·12·16·24·32·48),
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
- Done so far: audit memo, this file, protocol `docs/phien/TK1_GIAO_THUC.md`. No product code.
- Tests: none yet. Existing Chromium tests asserting classes/sizes (`tests/test_ux*`, `_ux5a_chung.py`
  JS_VANG counts `.btn-primary`) may need APPROVED updates — list each in "Decisions".

## Decisions and gotchas (keep short)
- Control heights 36/44 chosen because both already exist (6× and 10× in style.css) and 44 = kiosk touch target.
- Scrollbar shift is inferred (body scrolls, WebView2 classic scrollbar); confirm on Windows in final review.
- Keep `.dk-*` portal rules untouched; scope new tokens so portal output is pixel-identical (screenshot check).

## Next steps (ordered)
1. Coder starts at L0, then L1.

## Files touched
- docs/ke_hoach/TK1_DESLOP_GIAO_DIEN.md: audit + research
- docs/phien/claude__tk1-deslop-giao-dien.md, docs/phien/TK1_GIAO_THUC.md: plan

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus (planner) | Measured style.css, screenshots 6 tabs × 2 widths, wrote audit + plan | no product code |
