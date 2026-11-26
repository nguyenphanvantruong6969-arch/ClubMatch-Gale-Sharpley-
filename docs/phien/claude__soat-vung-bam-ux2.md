# Branch handoff: claude/soat-vung-bam-ux2

> Review, then fix on Truong's request (2026-11-26, "sửa ngay"; code UX2-VB, outside the registry). Base: `claude/stoic-ride-e92joa` @ 21cfdd4.
> Data: none of the algorithm is touched; the browser checks used a throw-away `app.db` (simulated).

## Feature / goal
Independent check of the fix in 21cfdd4 (role card "Quản trị" on `dang_ky.html` only clickable on its
title text), and a sweep of `style.css` for other buttons whose own `::after`/`position` is overridden by
the UX2-L3 hit-area block (`:where(button, .btn, [role="button"]) { position: relative }` and its `::after`
centred at 50%/50%, `max(100%, 44px)`, `translate(-50%, -50%)`). No registry item; UI bug follow-up.

## Plan
- [x] Verify the fix with real mouse clicks at 1000 / 600 / 375 px.
- [x] Sweep for the same pattern (CSSOM diff with/without the UX2 rules + static grep of every `::after`).
- [x] Propose a coordinate-click test for `tests/test_giao_dien_dk3_cong.py` (not added).
- [x] Fix F1/F2 (Truong: fix now). Tests written first (RED: 3 failed without the CSS change), then CSS.

## Current state
### Root cause (confirmed)
`.dk-cua-nut::after { position:absolute; inset:0 }` set only top/right/bottom/left. Specificity of
`:where()` is 0, so the class rule won on those, but UX2's `width`, `height`, `transform` and the button's
`position: relative` still applied (the class rule never set them). Result: the button itself became the
containing block and `::after` was a ~100x44 box around the title → clicks on the rest of the card fell on
`div.dk-cua` / `p.dk-cua-md`, which have no handler.

### Evidence — fix verified (Playwright/Chromium, `browser_host.serve` + `PipelineAPI` on temp db)
Clicks at x = 80 % of card width, y = 6 % / 50 % / 94 % of card height; then `input[name=ma]` must exist.
| Width | Cards | Fixed (HEAD) | Pre-fix simulated (`!important` re-applying UX2 values) |
|---|---|---|---|
| 1000 | GV, HS, QT (3 cols, 312x260) | 9/9 OK, `elementFromPoint` = `button.dk-cua-nut` | 9/9 MISS (`div.dk-cua`, `p.dk-cua-md`) |
| 600 | 2+1 grid, 276x260 | 9/9 OK | 9/9 MISS |
| 375 | 1 col, 343x157..179 | 9/9 OK | 9/9 MISS |
Computed `::after` at HEAD: button `position: static`, `::after` top 0 / left 0 / width = card width-2 /
height = card height-2 / transform none. Pre-fix: button `relative`, `::after` 106x44, `translate(-53px,-22px)`.
Why the suite missed it: `get_by_role(...).click()` clicks the button's centre, which was always inside the
small box.

### Other places with the same pattern (sweep result)
Method: on `dang_ky.html` (role screen, admin login, admin dashboard) and `index.html`, snapshot every
element's rect and computed `::after`, delete the 4 UX2 rules via CSSOM, snapshot again, diff. `.is-xong` /
`.is-loi` forced on all `.btn` to expose DK8-L5 states. Static grep of all 20+ `::after` selectors confirms
the list is complete.

- **F1 — DK8-L5 badge `.dk-app .btn.is-xong::after` / `.is-loi::after` (and `.dk-dau` variants)** — REAL BUG.
  The rule sets `top:-7px; right:-7px; width/height:18px` but not `left`/`transform`. UX2's `left:50%` wins;
  with left+right+width all set, `right` is ignored (LTR over-constraint). Measured on "Đăng nhập"
  (442x44): badge left = 220 px inside the button, expected 431 (top-right corner). With
  `prefers-reduced-motion: reduce` (no `dkTich` animation to mask transform) UX2's
  `translate(-50%,-50%)` also applies → badge at (211, -16). Visible as a ✓/! disc on the top edge
  centre, over the label, instead of at the corner. Same offset for every `.btn` in the portal
  (ghost, secondary, primary, `#dkThay`, `#dkThayCo`). Cosmetic, but it is the feedback signal of DK8-L5.
  Side effect: `pointer-events:none` on the badge also removes UX2's 44 px hit area while the state lasts
  (buttons are 44 px tall already, so low impact).
- **F2 — `.club-them > summary::after` and `#ux1aNangCao > summary::after` (content " ▾")** on
  `summary.btn.btn-secondary` (`#clubFormThemTuyChon`, `#adminHsThemTuyChon`, `#gt2ThuSoSanhKhac`'s
  summary, `#ux1aNangCao` summary) — REAL (cosmetic). `.btn` matches the UX2 rule, so the arrow becomes
  an absolute 127x44 box translated to the summary's top-left; screenshot shows "▾" in the top-left corner
  instead of after "Thêm tuỳ chọn". Click target is unaffected (the pseudo belongs to the summary).
- **Checked, no conflict:** `.step-dot::after`, `.option-hop::after`, `.dk-truong:has(...)::after`,
  `.dk-xong-dau::after`, `.gt2-buoc li::after` (subjects are span/li/div, not button/.btn/[role=button]);
  `html.tat-hieu-ung *::after` and the reduced-motion `*::after` reset touch animation only. No
  absolutely-positioned descendant changed position when UX2 `position: relative` was removed (no
  other "stretched link" inside a button). One 375 px header shift seen in the first run was a web-font
  timing artifact (gone after `document.fonts.ready`).
- **Limit:** only DOM present on the screens visited was diffed; the static grep covers the rest.

### Fix (DONE 2026-11-26; first idea below kept for record)
Any rule that styles a button's `::after` must reset UX2 explicitly, as 21cfdd4 did:
F1: add `left:auto; transform:none` to the badge rule (and keep the `dkTich` keyframes ending at
`transform:none`). F2: add `position:static; width:auto; height:auto; transform:none` for the two
summary `::after` rules (or exclude `summary` from the UX2 selector). Longer term: scope the UX2 block as
`:where(button, .btn, [role="button"]):not(.co-after)` or document the reset rule in `style.css` header.

### Test (ADDED as test_11, plus test_12 badge and test_13 summary arrow)
```python
@pytest.mark.parametrize("rong", [1000, 600, 375])
def test_11_ca_the_vai_tro_bam_duoc_bang_toa_do(cong, rong):
    """Bấm vào THÂN thẻ (không phải chữ tiêu đề) phải mở màn đăng nhập — bắt lỗi UX2 ::after."""
    pg = cong
    pg.set_viewport_size({"width": rong, "height": 900})
    for vai in ("Giáo viên", "Học sinh", "Quản trị"):
        for fy in (0.06, 0.5, 0.94):
            pg.goto(pg.dia_chi)
            pg.wait_for_selector(".dk-cua")
            the = pg.locator(".dk-cua", has=pg.get_by_role("button", name=vai, exact=True))
            bb = the.bounding_box()
            x, y = bb["x"] + bb["width"] * 0.8, bb["y"] + bb["height"] * fy
            tren = pg.evaluate("([x,y]) => document.elementFromPoint(x,y).className", [x, y])
            assert "dk-cua-nut" in tren, (rong, vai, fy, tren)
            pg.mouse.click(x, y)
            pg.wait_for_selector("input[name=ma]", timeout=3000)
    pg.set_viewport_size({"width": 1100, "height": 900})
```
Place it after test_1 (portal must be initialised; the module fixture is shared). It fails on edf1eed (pre-fix)
(all 27 points MISS in the simulation) and passes on 21cfdd4. An F1 guard could assert the badge's
`getBoundingClientRect` via `getComputedStyle(b,'::after').left` ≈ `width + 7 - 18`.

### What was applied
- F1: badge rule gets `left: auto; transform: none` → measured 429 px = padding-box width 440 + 7 − 18 (both motion modes).
- F2: making the summary `::after` static removed its 44 px hit area (`test_giao_dien_ux2_nut` admin failed on
  `clubFormThemTuyChon 139x36`). Final: `::after` static for the arrow; `summary.btn::before` carries UX2's hit area.
- Tests: `tests/test_giao_dien_dk3_cong.py` 16 passed; with dk8_l5, ux2_nut, ux4_l2/l3/l4, dk8_l1, dk4_cong_vao: all pass.
  Screenshots checked: "Thêm tuỳ chọn ▾" arrow after text; ✓ badge at top-right.

## Decisions and gotchas
- Python Playwright is not installed in this container (the project venv is missing); used the
  pre-installed Node Playwright as client and `python3` + `browser_host.serve` as server.
- `:where()` has zero specificity: overriding SOME properties is not enough; every property UX2 sets
  (`position` on the button; `top,left,width,height,transform` on `::after`) must be reset.

## Invariant risk (CLAUDE.md)
None. CSS only; no change to `compute_club_priority`, STB, `run_history`, pipeline, CSV or schema
(invariants 1–8 untouched). Fixing F1/F2 is likewise CSS-only; existing UI tests
(`tests/test_giao_dien_dk3_cong.py`, UX2/DK8 UI tests) should be re-run.

## Next steps
1. CI green on the branch; then PR into the target branch if Truong asks.
2. Truong: confirm the temporary code UX2-VB (or assign a registry code).

## Files touched
- docs/phien/claude__soat-vung-bam-ux2.md: this report.
- style.css: F1 badge reset, F2 summary arrow + ::before hit area.
- tests/test_giao_dien_dk3_cong.py: test_11/12/13.
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: UX2-VB entry.

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-26 | Opus | Verified 21cfdd4 fix at 3 widths; swept UX2 overrides; found F1, F2 | Report only |
| 2026-11-26 | Opus | Fixed F1/F2 on Truong's request, tests first | Rule 11/12 (Opus plans only) waived by Truong's direct order |
