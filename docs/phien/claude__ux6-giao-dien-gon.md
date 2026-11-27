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
- [x] 0. Create branch `claude/ux6-giao-dien-gon` from `origin/claude/hopeful-cannon-urfiul`; venv:
      `python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt -q` (Chromium is preinstalled).
- [x] L1-a. Inventory: list every `hint-text` / `view-desc` / `hint` element in `index.html` with its i18n key
      and a verdict (keep a/b/c · move to "?" · delete) as a table in this file (Decisions section, ≤ 40 lines).
- [x] L1-b. Red test `tests/test_giao_dien_ux6_l1.py`; apply the verdicts; remove dead keys from vi + en in
      `i18n.js`; shorten the next-step banner (`js/17_viec_tiep_theo.js`). Commit `UX6-L1: …`.
- [x] L2-a. Red test `tests/test_giao_dien_ux6_l2.py`; Xếp CLB summary line replacing `#dropZone` after import,
      [Đổi sổ], collapsible finished steps (blocking warning keeps its step open).
- [x] L2-b. `#statusStrip` "x/y đã có CLB" + bar + unplaced-count button (same handler as the banner).
- [x] L2-c. Kết quả: table out of its card, one toolbar above it. Commit `UX6-L2: …`. → `MILESTONE 1 READY`.
- [x] L3. Red test `tests/test_giao_dien_ux6_l3.py`; logo, icons (inline SVG + aria-label), one accent for
      segmented controls, monospace only for codes, sentence-case headers, CLB id under name, icon "Xoá" on
      hover+focus, `dang_ky.html` setup form. Commit `UX6-L3: …`. → `MILESTONE 2 READY`.
- L4 dropped by Truong (2026-11-27): no document moves.
- [~] End (CHANGELOG, TIEN_DO done; soat-ma + CI pending): CHANGELOG (UX6, files, new tests, tests whose copy asserts changed), `docs/ke_hoach/TIEN_DO.md`
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
- L1, L2, L3 implemented. MILESTONE 1 READY (bf12e43), MILESTONE 2 READY (f392ae1); checker NOT run yet.
- Pushed to origin: head 1d7ffe3 (includes a01a8fc: keeps "Kiểm tra lại" visible when step 2 collapses; tests count 450).
- CI run 1806 on e28fe96 was red: btnValidate hidden (fixed), test count 447 vs 450 (fixed), 3 more Linux failures of unknown
  names (jobs 1/6, 2/6, 6/6). A new CI run on 1d7ffe3 is in progress; a check was scheduled for 23:24 UTC 2026-11-27.
- Truong (latest): fix ONLY what is red in CI, then recheck, then done.
- Local: related UI tests green; ruff clean; kiem_nhanh 7/7; backend diff empty.

## Next steps
1. Read the CI result for 1d7ffe3; if red, fetch CI failures with failed_only and tail_lines ~130 (summary
   lines "FAILED ..." sit right before "N failed"); fix inside UX6 only; loop until Tests (rbda-kiosk) is green on head.
2. soat-ma pass on the diff (report, fix only UX6 findings); list anything outside UX6 for Truong.
3. Checker runs M1 and M2 (protocol section 4); then final CHANGELOG/TIEN_DO touch-ups.

## Decisions and gotchas (keep short)
- UI only; data not returned by the API today is not added (show what exists).
- `.hint-text` has several scoped overrides in `style.css` (`#paPanel`, `#dcQlTongQuan`, `.ws-tn-wharton`,
  `.gt-ui`, `.ux5a-hop-rong`): remove dead rules when their element goes.
- Kết quả table and Quản lý are shared with the teacher role: re-run the role-hiding tests after L2/L3.

## L1-a inventory (78 helper elements; verdict by i18n key or id)
- KEEP 25 (a/b/c): import_hint(c) · health_panel_hint(b) · chonBuoiNhac(a) · ux5bBuoiTom, ux2PhaGhiChu, paLyDo (b, status)
  · xuatFaAnGoiY(b) · ux5a_xuat_canh_bao, xuat_canh_bao_diem(a) · phGoiYNut(c) · fallbackStep1Hint(a)
  · fallback_step3_hint(c) · hcNhacTuyenChon, hcNhacDaChinh(b) · whPhongHoi, whPhongTieuDe, whMoKhoaHoi,
  whXoaTatCaHoi(a, confirm) · dcQlRong, dcKhongXet, gt2ThuChuaCo, gt2TcGhiChu, cbGhiChuTat (b, empty/blocked)
  · danger_zone_desc(a) · ghiChuDangKy(b).
- MOVE to "?" (`<details class="ux6-hoi">`): ux1b_bao_cao_hint, xuat_theo_lop_hint, clb_desc, du_tru_desc,
  chua_co_cho_desc, tham_desc, dd_goi_y, v2_goi_y, mt2_ghi_chu, buoi_hint_form, ti_le_choi_giai_thich,
  fallback_step3_hc_hint, gt2_tc_mo_ta, gt2_thu_mo_ta, gt2_ad_ghi_chu; wh_ql_desc and dc_mo_ta already sit
  behind a toggle button, so only their class changes.
- DELETE: pipeline_desc, kq_desc, ux5a_gt_mo_ta, ux5a_kq_mo_bang, others_desc, xuat_hint_hoc_sinh, do_phu_desc,
  nv_desc, tham_tai_lap, fallback_desc, ux5b_fallback_desc_qt, fallback_buoi_hint, fallback_step2_hint,
  admin_desc, ux4_mo_clb, admin_tai_buoi_desc, ux4_mo_hs, wh_sua_rong, wh_dang_mo_khong_can, wh_nk_chon_em,
  wh_nhat_ky_rong, ux4_mo_lam_lai, danger_zone_safety, ux4_mo_cach_xep, gt2_tc_nhom_goi_y, scoring_desc,
  cb_desc, cb_duong_hint, cb_duong_a_ghi, cb_duong_b_ghi, cb_buoc_trong x5, knGoiY (+ their JS lines).

## Files touched
- CI fix: style.css (data-gon keeps btnValidate; #gtTim min-height), docs/ke_hoach/CLAUDE_CHI_TIET.md (tests count 450).
- L2: index.html, i18n.js, style.css, js/02_van_hanh.js, js/00_nen.js (ux2DiToi focuses btnRun when dropZone hidden), tests (ux6_l2 new; 67 files wait on dropZone "attached").
- L1: index.html, i18n.js, style.css, js/05_quan_ly.js, js/06_cham_diem.js, tests (ux6_l1 new; copy asserts updated in
  ws_nhan, gt4, ws_luat_giao_dien, xoa_du_lieu, ux5a_l2, ux4_l2, ux5b_l3).

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-27 | Opus | Design review + UX6 plan (this file, `UX6_GIAO_THUC.md`) | no product code |
| 2026-11-27 | Sonnet | L1 done (inventory, helpers 78->25, banner) | one commit |
| 2026-11-27 | Sonnet | Context handoff 2: pushed 1d7ffe3, CI rerun pending, Truong said fix only CI-red then recheck | next session continues |
| 2026-11-27 | Sonnet | Context handoff: CI red on e28fe96, fix a01a8fc committed locally | superseded |
| 2026-11-27 | Sonnet | L3 done, MILESTONE 2 READY | CSS mask icons keep UX2 ::after hit areas intact |
| 2026-11-27 | Sonnet | L2 done, MILESTONE 1 READY | xuat_theo_lop_hint "?" removed (Hick budget of #xuatPanel) |

## Coder first-session prompt
```
You are the UX6 coder (Sonnet). Read CLAUDE.md, then docs/phien/claude__ux6-giao-dien-gon.md, then
docs/phien/UX6_GIAO_THUC.md and docs/phien/_GIAO_THUC_GON.md §3. Create branch claude/ux6-giao-dien-gon from
origin/claude/hopeful-cannon-urfiul and work only there. Do the Plan in order (L1 → L2 → L3; L4 is dropped, never
move any document), test first per lot, one commit per lot step, tick the Plan and update "Current state"
after each commit, push after each lot. UI files only (protocol §0). At L2 end write "MILESTONE 1 READY", at L3 end
"MILESTONE 2 READY" in the branch file and in your reply, then wait for the checker. No subagents. Reply to Truong
in Vietnamese.
```
