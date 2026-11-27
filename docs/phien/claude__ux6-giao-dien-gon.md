# Branch handoff: claude/ux6-giao-dien-gon

> Read CLAUDE.md, then this file, then `docs/phien/UX6_GIAO_THUC.md`. English, ≤ 150 lines.
> Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
UX6: make the kiosk UI look designed by a person rather than generated. The design review (2026-11-27,
real app in Chromium, simulated 120-student Sổ, seed 42) found: (1) too much explanatory text — 78 helper
elements in `index.html`; (2) every screen is the same stack of identical white cards; (3) screens do not
change with state (the drop zone still dominates Xếp CLB after import and run); (4) small inconsistencies
(placeholder "RB" logo, text glyphs as icons, mixed accents, monospace on UI labels, raw ids and red
"Xoá" links in tables, template-like setup form in `dang_ky.html`); (5) repo hygiene (documents at the
root, misspelt repo name). UI only: no backend, algorithm, schema or CSV change, so invariants 1–5 and 7–8
are untouched by design. New code UX6, outside the 33-item registry (like UX1–UX5).

## Before (for the checker's comparison)
- Xếp CLB after run: banner, H1 + description, strip "120 học sinh | 9 CLB | 88 đã xếp CLB", step cards
  1–3 fully open, big dashed drop zone "Kéo Sổ nhập CLB vào đây".
- Kết quả: lookup card, "Theo lớp và báo cáo" card with 2 buttons, table card with a moss-green segmented
  control (bigger font than the rest) and a gold "Tải bảng này (Excel)".
- Quản lý → Danh sách CLB: columns MÃ CLB (mono, e.g. `clb_coking`) … with a red underlined "Xoá" per row.
- Sidebar brand: gold square with the text "RB"; "Không gian làm việc" label in monospace; "⋯" button with no label.

## Plan (written by Opus; ticked by Sonnet)
- [ ] 0. Create branch `claude/ux6-giao-dien-gon` from `origin/claude/hopeful-cannon-urfiul`; venv:
      `python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt -q` (Chromium is preinstalled).
- [ ] L1-a. Inventory: list every `hint-text` / `view-desc` / `hint` element in `index.html` with its i18n key
      and a verdict (keep a/b/c · move to "?" · delete) as a table in this file (Decisions section, ≤ 40 lines).
- [ ] L1-b. Red test `tests/test_giao_dien_ux6_l1.py`; apply the verdicts; remove dead keys from vi + en in
      `i18n.js`; shorten the next-step banner (`js/17_viec_tiep_theo.js`). Commit `UX6-L1: …`.
- [ ] L2-a. Red test `tests/test_giao_dien_ux6_l2.py`; Xếp CLB summary line replacing `#dropZone` after import,
      [Đổi sổ], collapsible finished steps (blocking warning keeps its step open).
- [ ] L2-b. `#statusStrip` "x/y đã có CLB" + bar + unplaced-count button (same handler as the banner).
- [ ] L2-c. Kết quả: table out of its card, one toolbar above it. Commit `UX6-L2: …`. → `MILESTONE 1 READY`.
- [ ] L3. Red test `tests/test_giao_dien_ux6_l3.py`; logo, icons (inline SVG + aria-label), one accent for
      segmented controls, monospace only for codes, sentence-case headers, CLB id under name, icon "Xoá" on
      hover+focus, `dang_ky.html` setup form. Commit `UX6-L3: …`. → `MILESTONE 2 READY`.
- [ ] L4 (optional; only after Truong answers protocol §2). Repo tidy with `git mv` + link check.
- [ ] End: CHANGELOG (UX6, files, new tests, tests whose copy asserts changed), `docs/ke_hoach/TIEN_DO.md`
      rows, `soat-ma`, push, CI green.

## Done when
- [ ] ≤ 25 helper elements in `index.html`; every kept one fits copy rule a/b/c.
- [ ] After import + run, the drop zone is hidden on Xếp CLB and a summary with the student count is shown.
- [ ] No "▾" / "⋯" text glyph inside buttons in `index.html` or `js/`; brand shows `logo.svg`.
- [ ] vi and en: no raw i18n key on any tab; `tests/test_i18n_sync.py` passes.
- [ ] UX2/UX5 behaviour tests unchanged and green (target ≥ 44 px, focus ring, role hiding).
- [ ] `git diff --stat origin/claude/hopeful-cannon-urfiul -- '*.py' ':!tests'` is empty.
- [ ] Checker PASS at M1 and M2; CI green.

## Current state (overwrite each handoff)
- Done so far: plan only (Opus, 2026-11-27).
- In progress: —
- Tests: —
- Open problems: protocol §2 questions for Truong (L4 only).

## Decisions and gotchas (keep short)
- UI only; data not returned by the API today is not added (show what exists).
- `.hint-text` has several scoped overrides in `style.css` (`#paPanel`, `#dcQlTongQuan`, `.ws-tn-wharton`,
  `.gt-ui`, `.ux5a-hop-rong`): remove dead rules when their element goes.
- Kết quả table and Quản lý are shared with the teacher role: re-run the role-hiding tests after L2/L3.

## Files touched
- (fill in while working)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-27 | Opus | Design review + UX6 plan (this file, `UX6_GIAO_THUC.md`) | no product code |

## Coder first-session prompt
```
You are the UX6 coder (Sonnet). Read CLAUDE.md, then docs/phien/claude__ux6-giao-dien-gon.md, then
docs/phien/UX6_GIAO_THUC.md and docs/phien/_GIAO_THUC_GON.md §3. Create branch claude/ux6-giao-dien-gon from
origin/claude/hopeful-cannon-urfiul and work only there. Do the Plan in order (L1 → L2 → L3; L4 only if Truong
has answered protocol §2), test first per lot, one commit per lot step, tick the Plan and update "Current state"
after each commit, push after each lot. UI files only (protocol §0). At L2 end write "MILESTONE 1 READY", at L3 end
"MILESTONE 2 READY" in the branch file and in your reply, then wait for the checker. No subagents. Reply to Truong
in Vietnamese.
```
