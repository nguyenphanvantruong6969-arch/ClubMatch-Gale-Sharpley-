# Branch handoff: claude/xp1-xuat-pdf

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).

Status: IN PROGRESS (L1-L3 passed; CI green a5b610e run 44533627421; L4 in review). Protocol: docs/phien/XP1_GIAO_THUC.md

## Feature / goal
New item **XP1 — bulk PDF export** (approved by Truong 2026-11-18; new item like UX1, tracked in `TIEN_DO.md`,
not in the 33-item registry). For Truong's workflow PDF is THE way data leaves the app, so the admin must be able to
export in bulk: (1) **member lists** as PDF, one file per club OR one file per class; (2) **explanation slips**
(`phieu giai trinh`) as PDF in bulk, one file per class (or one chosen class), and every slip row shows the
**club type** (Tự do / Giới hạn / Tuyển chọn, `clubs.loai`). Branched from `claude/ux1-a-giao-dien` @ `66f9ffb`
(needs its "Xuất…" menu and club-type UI); merge UX1A first, then this.

## Decisions (Truong, 2026-11-18)
- PDF engine: **reportlab** (new runtime dependency, approved) + a bundled **TTF** font with Vietnamese glyphs.
  `assets/fonts/` has only `.woff2` (reportlab cannot read it): add Be Vietnam Pro `.ttf` (SIL OFL, same family as
  the UI) regular + bold, plus its OFL licence file. Add `reportlab` to `requirements.txt`; add the TTFs to
  `kiosk.spec` `datas` (already ships `assets/fonts`) and `collect_all("reportlab")` if PyInstaller misses modules.
- Roles: Opus wrote this plan; **Sonnet codes** and ticks it; checker reviews per lot.
- Overlap (confirmed 2026-11-19, see `UX1_GIAO_THUC.md` §10 on `claude/ux1-b-phieu`): team B keeps the medal
  column; XP1 owns `loai` + "Loại CLB". Integration order A → B → XP1. XP1 replaces UX1 team B lot L6 (print-dialog PDF) and the club-type part of L7 (`claude/ux1-b-phieu`,
  not started). Update `docs/phien/claude__ux1-b-phieu.md` Plan with a one-line note in L2.
- Engine is separate from data: keep `phieu_giai_trinh.dung_phieu_html` (HTML export unchanged); build PDF from the
  SAME data (`giai_trinh.giai_trinh_mot_hoc_sinh` output), never by converting HTML.

## Plan (written by Opus; ticked by Sonnet)
Lot L1 — PDF core (no UI)
- [x] Failing test first: `tests/test_xp1_pdf_loi.py` — a 3-page PDF with Vietnamese text ("Nguyễn Văn Ánh, Lê Đức
      Cường") round-trips: page count correct, text extractable (use `pypdf` ONLY if already installed in dev; else
      assert font embedded + `/Count n` in bytes). Skip cleanly if reportlab missing (like playwright tests).
- [x] New module `xuat_pdf.py`: font registration (once, path via the same resource lookup the app uses for
      `assets/`), `dung_pdf(path, trang)` with simple building blocks (title, key/value line, table with header
      repeat on page break, footer "Trang x/y"). A4 portrait; tables wrap long text (Paragraph cells).
- [x] No file overwrite: reuse `_duong_xuat` / `duong_dan_khong_de` rules. Write to temp then rename.

Lot L2 — explanation slips as PDF, by class, with club type
- [x] Test: `tests/test_xp1_phieu_pdf.py` — n slips = n pages minimum (each student starts a new page; long slip may
      span 2); filter by `lop`; bulk = folder with one PDF per class + `_chua_co_lop.pdf`; every row shows club
      type label; a student's slip has ONLY their own data (no other student id/name in their page text).
- [x] `giai_trinh.giai_trinh_mot_hoc_sinh`: add `loai_clb` to each `cac_lua_chon` item (read `clubs.loai` via
      `dung_du_lieu_run` data; None in plain RB-DA mode when column is NULL → label "—"). Additive key only.
- [x] ONE student's slip as PDF (replaces dropped UX1B-L6): `student_ids=[sid]` → one PDF; button "Lưu PDF" on the
      lookup card (`js/14_giai_trinh.js`), target ≤ 4 clicks (search → pick → Lưu PDF → save). Test it.
- [x] Also show the type in the HTML slip (`phieu_giai_trinh._bang`: new column "Loại CLB"); update affected
      snapshot tests deliberately (`SUA_CO_Y` pattern if needed).
- [x] API (`api_xuat.py`): `export_phieu_giai_trinh_pdf(output_path="", lop=None, theo_lop=False, student_ids=None)` →
      `theo_lop=True`: folder `phieu_giai_trinh_theo_lop/` one PDF per class; else one PDF (all or one class).
      Reuse `_export_phieu_giai_trinh_da_khoa` selection logic (extract a helper, do not copy). Same errors
      (`gt1_chua_chay`, `gt1_khong_co_hoc_sinh`, `gt1_lan_chay_cu`). Wrap in `_khoa_xuat`. Returns
      {path|thu_muc, n_tep, n_trang}.

Lot L3 — member lists as PDF
- [x] Test: `tests/test_xp1_danh_sach_pdf.py` — `theo="clb"`: one PDF per club (+ per session if multi-session),
      rows = matched students (id, name, class), count = `match_results` count; `theo="lop"`: one PDF per class,
      rows = student, club, session; NO scores, NO lottery numbers (same rule as `export_theo_lop`); unassigned
      students listed in a separate section "Chưa có CLB".
- [x] API: `export_danh_sach_pdf(output_path="", theo="clb")` — data from `_du_lieu_xuat()` (same source as
      `export_theo_lop`); folder output; `xuat_chua_co_ket_qua` when no results. Club title line shows club type.
- [ ] (skipped, on Needs Truong) Optional (ask Truong): one combined PDF with a cover table of contents in addition to the folder.

Lot L4 — UI + permissions + i18n
- [ ] "Xuất…" menu (`#xuatMenu`, thẻ Kết quả): "Danh sách theo CLB (PDF)", "Danh sách theo lớp (PDF)",
      "Phiếu giải trình theo lớp (PDF)" + class picker reusing the existing class selector of the HTML slip export.
- [ ] `phan_quyen.QUYEN`: the 2 new functions = QUAN_TRI; `nhat_ky` labels `nkhd_export_*_pdf` (vi+en) —
      `test_gt4_nhat_ky_doc.py` enforces this (that is what broke CI #1013).
- [ ] New error codes (e.g. `xp1_thieu_thu_vien_pdf` when reportlab/font missing) in `i18n_errors.py` →
      `python tao_i18n_js.py`. No "—" joining sentences (`test_van_phong_tu_nhien.py`).
- [ ] UI test: `tests/test_giao_dien_xp1_xuat_pdf.py` (menu items visible for admin only, call right API).

Lot L5 — docs + packaging + verify
- [ ] `HUONG_DAN_SU_DUNG.md` section "Xuất PDF hàng loạt"; `CLAUDE_CHI_TIET.md` code map (`xuat_pdf.py`).
- [ ] Windows build workflow green; launch the built exe once and export (manual check by Truong).
- [ ] Invariant 1: `kiem_nhanh.py` 7/7 (`trung_khit`): exports must not change `match_results`.
- [ ] Performance: 800 students bulk slips < 30 s on CI Linux; record the number in CHANGELOG.
- [ ] `CHANGELOG.md`, `TIEN_DO.md` rows per lot.

## Acceptance (kiem_nhan)
- Admin exports, in one click each: member lists per club, per class, and slips per class, all as PDF.
- Vietnamese diacritics render correctly; every slip row shows club type; no data of other students on a slip;
  member lists carry no scores/lottery numbers; nothing in DB changes (match_results, run_history, stb_lock).
- Full CI green (coverage ≥ 85 %), Windows exe exports PDF offline.

## Gotchas
- Simulated data only for tests/samples (e.g. `du_lieu_test/SO_NHAP_MAU_120HS_3BUOI.xlsx`, seed 3).
- Slip text is Vietnamese-only today (`phieu_giai_trinh.py` hard-codes it); keep that unless Truong asks for en.
- Role check: teacher role must not reach these exports (backend `phan_quyen`, not just hidden buttons).
- Push only after CI of the previous lot finishes (two cancelled runs hid a bug on the UX1A branch).

## Sessions
| Role | Model | Session id | State |
|---|---|---|---|
| lead | claude-opus-5-5 | session_01VfPzNtmP5QGfFfaGiBWkze | running |
| coder | claude-sonnet-5-5 | session_01VfPzNrcErSweid4dXBTk72 | setup |
| checker | claude-sonnet-5-5 | session_01VfPzNunsu6WPaVRox9FJYc | setup |

## Needs Truong (1 line each + recommendation)
- L3 optional combined PDF with table of contents: not built unless Truong asks. Rec: folder output is enough for v1.
- pypdf as a dev-only test dependency (reads PDF text to prove diacritics in CI): removed per §0 (one new library). Rec: allow it in requirements-dev.txt; it never ships in the exe.
- L5 manual check: launch the built Windows exe once and export PDFs offline. Rec: do it after CI is green.

## Current state (overwrite each handoff)
- Done so far: plan only (this file) + `TIEN_DO.md` row. No code.
- In progress: —
- Tests: —
- Open problems: depends on `claude/ux1-a-giao-dien` CI being green (fix4 `66f9ffb` pending at handoff time).

## Next steps (ordered)
1. Sonnet session: Lot L1 (font + `xuat_pdf.py` + test), push, wait for CI.
2. Lots L2 → L5 in order, one push per lot.

## Files touched
- docs/phien/claude__xp1-xuat-pdf.md: this handoff (plan).
- docs/ke_hoach/TIEN_DO.md: XP1 row.
- docs/phien/XP1_GIAO_THUC.md: lead/coder/checker protocol + prompts.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-18 | Opus | Created branch from ux1 @66f9ffb; wrote Goal + Plan | Decisions: reportlab + TTF, Sonnet codes |
| 2026-11-18 | Opus | Wrote XP1_GIAO_THUC.md (3-session protocol, prompts) | Lead prompt in §7 |
