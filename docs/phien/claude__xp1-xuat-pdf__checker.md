# XP1 checker log (CHECKER session; only this file is edited)

## L1 — reviewed 1444d12..446c362: 1 BUG, 1 note
- reportlab==5.1.0 exists on PyPI and installs (wheel downloaded here). L1 tests 10/10 pass WITH pypdf; ruff clean.
- OFL file is the Be Vietnam Pro licence (Copyright 2021 The Be Vietnam Pro Project Authors); both .ttf carry that copyright + SIL OFL text. OK.
- Font embedding, page count, "Trang x/y", no-overwrite, temp-file cleanup and missing-font error all behave as specified.
1. BUG `tests/test_xp1_pdf_loi.py:7` module-level `pytest.importorskip("pypdf")` skips the WHOLE file when pypdf is absent
   (verified: without pypdf, `1 skipped`). Plan says use pypdf only if already installed, else assert font embedded + `/Count n` in bytes.
   Tests that need no pypdf (font embedded, no-overwrite, temp file, error mid-build, missing font) are lost too.
   Fix: import pypdf with try/except; keep a bytes-level fallback (`/Count 3`, `/FontFile2`, `BeVietnamPro`, no leftover tmp) running always.
2. Note (needs lead/Truong decision): `pypdf` in requirements-dev.txt is a 2nd new library (dev-only). §0 allows only reportlab.
   If kept, label it dev-only; preferred: drop it and rely on the bytes-level asserts.

## L1 fix1 — reviewed 446c362..d56c913: NO BUGS
- Without pypdf: 8 passed, 5 skipped (only the text-extraction tests); bytes-level page count (`/Count`), `/FontFile2`, no-overwrite, tmp cleanup, mid-build error, missing font all run. With pypdf: 13 passed. ruff clean.
- `pypdf` removed from requirements-dev.txt; requirements.txt unchanged (reportlab only). Bug 1 and note 2 resolved.

## L2 — reviewed 2524332..b5987b6: NO BUGS
- Tests: xp1_pdf_loi, xp1_phieu_pdf, giao_dien_xp1_luu_pdf_mot_em, gt4_cau_giai_trinh, van_phong_tu_nhien, ws_nhan, gt4_nhat_ky_doc = 108 passed. `kiem_nhanh.py` 7/7 (trung_khit 15 cases identical vs origin/main).
- 3 edited old tests are NOT weakened: gt4 index 4→5 = new "Loại CLB" column shifts the cell; "PDF" added to abbreviation set; `xp1_` added to new-i18n-prefix allowance. Assertions otherwise intact.
- QUYEN `export_phieu_giai_trinh_pdf` = QUAN_TRI; nkhd label vi+en present; button has data-quyen="quan_tri".
- Own temp tests (deleted, not committed): teacher login → all 3 call shapes `gt3_khong_du_quyen`, nothing created; FA on shows "Giới hạn"/"Tự do"; student without class → `_chua_co_lop.pdf` holds only that student; empty class → `gt1_khong_co_hoc_sinh`; not run → `gt1_chua_chay`; match_results/run_history/stb_lock unchanged after exports; class "10/A é" → file `10_A é.pdf`.
- Privacy: slip page has only own id/name (test + temp). Team B medal column untouched (no diff in medal code).
- Not covered by me: multi-session slip layout beyond code reading; Windows font rendering visually.
- Verdict file committed locally only (lead: push when CI says so).

## L3 — reviewed b5987b6..a5b610e (code 7217c8c): NO BUGS, 1 note
- Tests: xp1_danh_sach_pdf + gt4_nhat_ky_doc + gt3_phan_quyen + xp1_phieu_pdf + van_phong_tu_nhien + ws_nhan = 130 passed.
- Own temp tests (deleted): teacher → `gt3_khong_du_quyen` for theo=clb/lop, no folder; 3-session sample (120HS 3BUOI): rows counted FROM the PDFs by student id = 360 = match_results; by class 120 students; no "điểm/bốc thăm/stb/hạng/tier/score/ưu tiên" in any PDF text; error injected on 2nd file → folder removed, retry works, 2nd export → "x (2)"; data changed after run → stale warning (`ket_qua_cu` True).
- Code: only student_id, ho_ten, lop, buoi, gio, dia_diem, club type reach the PDF; QUYEN=QUAN_TRI; nkhd vi/en; new error code at end of i18n_errors.
- Note: a club with 0 matched students gets no file (groups come from result rows). Acceptable for v1 (nothing to list); a homeroom/club teacher of an empty club finds no file — mention in HUONG_DAN.

## L4 — reviewed a5b610e..56e55ff (code 25582fd): NO BUGS
- Chromium + related tests: xp1_xuat_pdf, xp1_luu_pdf_mot_em, ux1_ket_qua, van_phong_tu_nhien, ws_nhan, gt4_nhat_ky_doc, gt3_phan_quyen (+giao_dien) = 104 passed. `kiem_nhanh.py` 7/7; `tao_i18n_js.py` leaves no diff (i18n_loi.js in sync); vi+en keys for every `xp1_*`.
- `test_giao_dien_ux1_ket_qua.py` edit: filter now skips buttons inside a CLOSED `<details>` only; assertion (`== ["btnXuatTuyChon","btnXuatTheoLop"]`) and the `#xuatMenu` hidden check are unchanged, so it still proves "default shows only two buttons". Not weakened.
- Separate "Xuất PDF…" menu (not inside `#xuatMenu`): justified (`#xuatMenu` is medal-only/hidden when FA off). Deviation from Plan text; works. Buttons call the right API: DS-CLB `export_danh_sach_pdf(["","clb"])`, DS-lớp `["","lop"]`, phiếu "Tất cả lớp" → `theo_lop=True` folder (4 files incl. `_chua_co_lop.pdf`), one class → ONE file `phieu_giai_trinh.pdf`, no folder; menu closes after click; buttons locked while running/no results.
- Admin-only: `data-quyen="quan_tri"` + UI test; backend rejection for teacher verified in L2/L3 (`gt3_khong_du_quyen`, new functions in QUYEN).
- Visual (own screenshot): labels "Xuất PDF… / Danh sách theo câu lạc bộ (PDF) / Danh sách theo lớp (PDF) / Tất cả lớp… / Phiếu giải trình theo lớp (PDF)"; popup overlaps the helper text below (normal for a dropdown). No "—" joining sentences (van_phong test passes).
