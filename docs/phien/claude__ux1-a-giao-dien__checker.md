# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L8-A — REVIEW c2c7a30..ad569c2 — 1 doc BUG (minor) → FIX L8-A
- Tests: 166 passed (i18n_sync, ws_nhan, fg7, tai_lieu*, bang_loi, vi_du_huong_dan, kich_ban_nhap_tay …); `tao_i18n_js.py` regenerates `i18n_loi.js` with no diff. `pytest --collect-only` = 6845 tests / 339 files → CLAUDE_CHI_TIET counts exact.
- Re-ran `chup_luong_chinh.py` (images restored afterwards, nothing left in the tree): admin load→run→export = 4 clicks (state xu_ly), unplaced = 1 click on the bar, homeroom = 0 clicks (app opens on Kết quả) + 1 to see own class, student = 2. All match "After" table.
- BUG (docs): UX1_RA_SOAT §2b row 2 says "sổ mẫu còn 12 em chưa có chỗ"; measured on SO_NHAP_DQT_120HS_HOP_LE seed 42 (and default seed) = **32 unplaced, 88 placed**. Fix the number (the script prints no count; the "Ghi chú" wording is fine).
- Labels spot-checked vs index.html/i18n.js: group names, card names, Huy chương/Chỉ xếp thứ tự/Chia 100, "Sau khi xếp", "Xuất…", "Xuất theo {cohort_l}", Theo lớp, Bật chế độ huy chương, Việc tiếp theo, Nâng cao — all exist; "Gán lớp:"/"Gửi giáo viên chủ nhiệm:" are guide run-in headings, not UI labels (OK).
- Team B untouched: no change to 04_phieu.png, phieu_mau.pdf, CA_MAU.md, slip docs (only 3 docs/giai_trinh demo/run scripts + HUONG_DAN, A scope).
- i18n_errors (health/wharton hint) + test_fg7 edit + tao_mau_forms.py step-4 text: wording only (old "⋯ → Tính năng sau khi xếp…" replaced by Cài đặt/Sau khi xếp); no logic.
- Academic integrity: data labelled MÔ PHỎNG; §2b is a measurement table, no report conclusions/interpretation. Poster PDF/PPTX not rebuilt → Needs Truong (accepted).

## Earlier lots (all NO BUGS after fixes): L1 4 clicks; L2 nav/MutationObserver; L2b settings+backend; L3 (+fix1) results/export/stale-error; L5 warnings/sample books; L5b medal words (94 tests).
