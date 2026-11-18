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
