# TK1 protocol (size M: coder + checker, NO lead) — follows `docs/phien/_GIAO_THUC_GON.md`

> Work source: `docs/phien/claude__tk1-deslop-giao-dien.md` (lots L0–L4). Branch: `claude/tk1-deslop-giao-dien`.
> Audit: `docs/ke_hoach/TK1_DESLOP_GIAO_DIEN.md` (read §1–§2 only).

## 1. Roles
- Coder: Sonnet. Ticks the Plan, one commit per lot, runs the CI gate.
- Checker: Sonnet, started by Truong when coder writes `MILESTONE <k> READY`. Writes verdict to
  `docs/phien/claude__tk1-deslop-giao-dien__checker.md` (only file it pushes).

## 2. Milestones
- MILESTONE 1 after L2 (checker reviews L0–L2). MILESTONE 2 after L3/L4.
- Max 2 FIX rounds per finding, then "Needs Truong" + `git revert` of that lot.

## 3. Rules specific to TK1
- UI only. Any diff in `*.py` other than tests = stop and ask.
- Test first per lot (Chromium, one file `tests/test_tk1_on_dinh.py`, one shared page fixture from `_ux5a_chung.py`).
- Existing test changed only if it asserts the old look (class/size/count); write the reason per test in "Decisions".
- Both languages: every new/changed label in `i18n.js` vi + en; `tests/test_i18n_sync.py` passes.
- Portal (`dang_ky.html`, `.dk-*`) must look identical: one before/after screenshot of the portal login.
- Budget: `_GIAO_THUC_GON.md` §3 (never print whole `style.css` / `index.html` / `i18n.js`).

## 4. Checker focus
- Steadiness: tab widths, toolbar control heights, h1 x-position across tabs, no layout shift on hover/select/vi↔en.
- Keyboard focus ring still visible on every changed control; contrast ≥ 4.5:1 for text, ≥ 3:1 for borders.
- Light AND dark theme, `prefers-reduced-motion`, 1024 px and 1366 px widths.
- 3 own edge cases per milestone (e.g. long CLB name, English labels, 125 % zoom).

## 5. Final gate
Lot tests + ≤ 3 related, `kiem_nhanh.py` 7/7, `soat-ma` four tiers, GitHub Actions green (coverage ≥ 85 %,
Windows build). Then CHANGELOG + TIEN_DO, update "Current state", stop.
