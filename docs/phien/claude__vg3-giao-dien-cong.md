# Branch handoff: claude/vg3-giao-dien-cong

## Feature / goal
VG3 — visual clean-up of the registration portal (`dang_ky.html`), size M, presentation only. Planned by Opus on Truong's request
("inspect the portal, fix AI-slop / layout problems, fully automatic"). Touches only `.dk-*` CSS, `js/dang_ky_*.js`, `dang_ky.html`.
No backend, no payloads, main app look unchanged. VG2 (branch `claude/vg2-ra-soat-theo-vai`) later edits the same JS: do NOT do VG2 items
(confirm dialogs, list sections, student wizard step skipping, "hạt giống"/NV legend, tap targets).

## Plan (Opus; ticked by Sonnet)
- [x] L1 CSS/layout: findings 1,2,3,4,5,6,7,12,14 (stage name once, compact 6-step bar, role cards, real logo, tabs/header on mobile, tables, rooms form, Xuất screen)
- [ ] L2 small JS/markup: 8 (Duyệt chỉ tiêu/status chip), 9 (↑↓ + counter + NV font), 10 (medal info box), 11 (review table), 13 (teacher "Chọn phòng…")
- [ ] L3 test `tests/test_giao_dien_vg3.py` + related tests + ruff + kiem_nhanh + CHANGELOG + TIEN_DO + registry stub + soat-ma + push + CI

## Current state (overwrite each handoff)
- Done so far: L1.
- In progress: L2.
- Tests: `test_giao_dien_dk8_l1/l2` green after L1 (dk8_l1 chip assertion for admin changed to 0 on purpose).
- Open problems: none yet.

## Decisions and gotchas
- Admin header: topbar stage chip hidden for `quan_tri` only (JS `DK.dauTren`); teacher/student/landing keep it.
- `DK.bang` empty header cell gets sr-only "Thao tác" (needs `.dk-bang {position:relative}` or the absolute sr-only span widens the page).
- Tables ≤720 px: `display:block; overflow-x:auto` so the table scrolls inside its card (no page scroll).
- "Tiến độ theo lớp" table: last header "" renamed "Tiến độ" (it is a progress bar, not an action column).

## Needs Truong
- (none yet)

## Next steps
1. L2, then L3 (see Plan).

## Files touched
- style.css (VG3 block at end), js/dang_ky_nen.js, js/dang_ky_quan_tri.js, tests/test_giao_dien_dk8_l1.py, tests/test_giao_dien_vg3.py

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-27 | Sonnet | L1 done | |
