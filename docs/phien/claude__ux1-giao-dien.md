# Branch handoff: claude/ux1-giao-dien

> Fresh session: read CLAUDE.md, docs/ke_hoach/ux/UX1_RA_SOAT.md, docs/ke_hoach/ux/UX1_KE_HOACH.md, then THIS file.
> English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

Status: PLANNED (Opus, 2026-11-18). Branch to be created from `origin/claude/gt-tich-hop`.

## Feature / goal
UX1 — direct UI, fewer steps (opened by Truong 2026-11-18, outside the 33-item registry). UI/presentation only.
Targets and lot details: `docs/ke_hoach/ux/UX1_KE_HOACH.md` §1–§2.

## Plan (written by Opus; ticked by Sonnet)
- [x] UX1a audit (`docs/ke_hoach/ux/UX1_RA_SOAT.md`, on claude/gt-tich-hop c21a334)
- [ ] L1 "Next step" bar (`js/17_viec_tiep_theo.js`) — test `tests/test_giao_dien_ux1_tiep_theo.py`
- [ ] L2 navigation 6 → 4 groups, keep every `data-tab` — test `tests/test_giao_dien_ux1_dieu_huong.py`
- [ ] L3 lookup first on results; one "Xuất…" menu; import message once
- [ ] L4 role pages (giao_vien) + "Báo cáo tổng hợp" (`bao_cao_tong_hop.py`, `export_bao_cao_tong_hop`, QUYEN)
- [ ] L5 oversubscription warnings info → medium, shorter text; medal book in non-FA mode → clear message + link to FA setting
- [ ] L5b medal cells accept Vàng/Bạc/Đồng (+ unaccented/English) → 60/30/10 at reading layer; one-click 'Bật chế độ huy chương'; two sample books
- [ ] L6 slip "In / Lưu PDF" via iframe print (`get_phieu_giai_trinh_html`, QUYEN, audit row); Truong checks on Windows
- [ ] L7 slip content: summary line, tested-club scores, SVG own-vs-cutoff, next steps, FA: club type + medal per row, plain words; regenerate CA_MAU + pack
- [ ] L8 docs (guide, demo/video scripts, poster, code map) + re-shoot screenshots + "After" table
- [ ] L9 gate: ruff, kiem_nhanh 7/7, soat-ma, full CI green

## Current state (overwrite each handoff)
- Done: plan only. In progress: none. Tests: n/a.

## Needs Truong
1. L6: confirm the print dialog opens in the packaged Windows app (WebView2) and in browser fallback.

## Decisions and gotchas
- Truong 2026-11-18: all four user groups; PDF via Print → Save as PDF (no new library); cutoff may be printed for
  tested clubs only (it is already on the slip); tab renames allowed with docs updated in the same item;
  keep default config (FA off); app suggests FA when book has medals; words Vàng/Bạc/Đồng accepted;
  slip shows medal placed + club type in FA mode (audit §6: algorithm uses them ONLY when FA is on).
- Keep element ids and `data-tab` values (≈97 Chromium tests select by them).
- Slip sentence changes break `tests/test_gt_tich_hop.py::test_i4_*` until CA_MAU.md is regenerated.

## Next steps (ordered)
1. Sonnet: create branch, L1 → L9 (one commit per lot). 2. Truong: Windows print check after L6. 3. Truong merges.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-18 | Opus | UX1 plan written (UX1_KE_HOACH.md) and this file created | — |
