# Checker — UX1A (branch claude/ux1-a-giao-dien)

## L1 — REVIEW 016ae66..ebf24cd — verdict: NO BUGS (2 minor notes)

Checked against "Done when" of L1 + invariants 1, 2, 4, 6, 7 + privacy.

- Tests: `tests/test_giao_dien_ux1_tiep_theo.py` 6 passed (Chromium, 120-student simulated book). `ruff check` on js/test: clean.
- Spec match: `#viecTiepTheo` at top of `<main>`, `data-quyen="quan_tri"` (hidden for `giao_vien` by CSS); five states in the
  specified order; labels/targets match (dropZone focus, health summary focus, `#btnRun`, unplaced panel expanded+scrolled,
  `#btnXuatTuyChon` focus). "n Cần xử lý" KPI card now runs the same `viecXuLyChuaCoCho`. Script 17 listed in
  `_danh_sach.txt` + `index.html`; i18n keys `ux1a_*` in vi + en.
- Invariants: read-only (3 existing GET-style APIs, all allowed for `giao_vien` in `phan_quyen.py`); no backend, algorithm,
  CSV, schema, `run_history` or error-catalogue change → 1, 2, 4, 6, 7 untouched. No personal data in the bar (counts only).
- Click count (admin, 120-student book): dropzone/file 1 → "Chạy sắp xếp" 2 → "Xuất kết quả" 3 → `#btnXuatTuyChon` 4 = **4**
  (was 5). The 4th click only starts the export once L3 lands (as the coder noted); L1's own part is correct.
- Edge cases tried: empty workspace → state `nap_so`, APIs return ok; stale-response guard (`viecTiepTheoLanGoi`) drops
  old results; `giao_vien` → bar hidden, no extra API errors.

Minor (not blocking, fix with L3 or later):
1. "Has run" is `n_matched > 0`; `get_dashboard_status` also returns `has_results`. A run that places nobody would show
   "Chạy sắp xếp" instead of "Xử lý n …". Cannot be reproduced with valid data (capacity > 0 CHECK), so low risk.
2. `viecChoRoiLam` gives up silently after ~3 s if the target panel never appears (no message). Acceptable.

## L2 — REVIEW ab1bd16..0ded385 — verdict: NO BUGS (2 notes)

- Tests: 141 passed (ux1_dieu_huong 5 + ux1_tiep_theo + a14_lop, gt2_thu, gt2_tieu_chi, gt4_tieu_chi, gt3_phan_quyen/hoc_sinh,
  gt4_man_hoc_sinh/vai/phien_rieng_tu, fg9, t3_l1, quan_ly_tab_con, doi_ngon_ngu, tro_nang, gt3_tai_lieu). Only these 4 tests were
  grep-affected by the moved GT2 panels (`#gt2Tc*`, `#gt2Thu*`); all four got the one-line selector edit (open `#ux1aNangCao`) — selector-only, no assertion changed.
  a14_lop edit = new tab order only. Product edits are UI only (index.html, js/01_khung.js, style.css, i18n.js): invariants 1,2,4,6,7 untouched.
- Spec: 4 groups (1. Nạp & xếp / 2. Nhập tay / 3. Kết quả & phiếu / Cài đặt); all `.nav-item[data-tab]` unchanged; group button opens first
  visible view; empty groups hide (giao_vien sees only Nhập tay + Kết quả & phiếu, lands on `results`); `chuan_bi` shows → Cài đặt stays;
  "Nâng cao" `<details>` closed by default holds both GT2 panels, club editing first.
- MutationObserver: watches only `hidden` (subtree of `.nav-group`) + `data-vai` on body; writes `nhom.hidden` only when the value changes,
  so no self-trigger loop; cost = 4 groups × ≤2 buttons per mutation. No freeze seen across 141 browser tests.
- Student lock (GT I2): overlay `#gtHs` covers all group buttons and nav items (test_man_hoc_sinh_phu_kin_ca_bon_nhom), existing GT3/GT4 student tests pass.
- Also noticed: coder applied my L1 minor note #1 (`has_results ||`) in 17_viec_tiep_theo.js — correct.
Notes (non-blocking): (1) visibility uses `getClientRects()`, so a mutation while the sidebar is `display:none` (only `@media print`) would hide
all groups until the next `hidden`/`data-vai` change; not reachable in normal use. (2) Spec suggested a segmented control inside the group; the
implementation lists the group's buttons under its heading — equivalent for selectors and clicks.
