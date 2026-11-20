# Checker verdicts — UX1F (branch claude/ux1-sua-pdf)

## L1 | reviewed 97ec70a..ec962ee
verdict: NO BUGS (1 note, outside the lot's stated scope)
- Diff = requirements-dev.txt (+pypdf>=4,<6), CHANGELOG.md, TIEN_DO.md only. No .py/html touched.
- Dev-only holds: pypdf absent from requirements.txt, requirements-build.txt (it is `-r requirements.txt`) and kiosk.spec.
- Verified: venv from requirements-dev.txt -> pypdf 5.9.0; test_xp1_phieu_pdf, test_xp1_danh_sach_pdf, test_xp1_pdf_loi,
  test_ux1i_i3_phieu_bao_cao -> 70 passed, 0 skipped (-rs). No other test file imports pypdf.
- tests.yml Linux job installs requirements-dev.txt (line 49) -> pypdf tests run there.
- Invariants 1, 4, 6, privacy, teacher limits: n/a (no product code changed).
- NOTE: .github/workflows/tests.yml `test-windows` (line ~121) installs requirements.txt + explicit pytest/pillow/python-docx,
  no pypdf -> on Windows the 3 xp1 files skip per-test and test_ux1i_i3 skips whole module (module-level importorskip).
  The L1 box says "CI log shows passed, not skipped": true for Linux shards only. Lead decides: accept (Linux covers it) or
  add pypdf to that pip line (workflow edit, not requirements.txt).

## L2 | reviewed f32dbab..235a3d7
verdict: NO BUGS (3 notes; none breaks a box)
Boxes: 40 students FA seed 3 -> 40 pages (old 74), min page 1577 chars; header text unbroken ("Huy chương", "Mức vào được");
 margins 12 mm, table font 8.5 pt; pypdf also on test-windows pip line (L1 note addressed).
Tests: test_ux1f_l2 + xp1_phieu/danh_sach/pdf_loi/hieu_nang + ux1i_i3 + ux1b_l7 -> 94 passed, 0 skipped.
Content identical: word-multiset diff old vs new (40 students) = only repeated column headers on continuation pages (21 x) and
 the old broken "ch"+"ương" (101) vs "chương" (80). No row/cell/legend text lost. Same check FA off (120HS_HOP_LE) and 1 student: ok
 (FA off 75 -> 42 pages, min 252; 1 student 2 -> 1 page, 1725 chars). List/report PDFs: their tests green; bang() first-call
 registers fonts (no KeyError).
800 students (DQT_800HS_HOP_LE, FA off): 1278 pages (was 1519). Every slip has 4 sessions: 322 take 1 page, 478 take 2.
 No slip with <=3 sessions spills. Judging the coder's flag: 106 second pages <400 chars, 2 <200 (min 159). Each such page holds
 one table row + "Em nên làm gì tiếp" + "Khiếu nại" + footer, never footer/legend alone -> acceptable under the letter of
 "no orphan footer/legend" and outside the <=3-session guarantee; but it is below the 200-char spirit on the 800 set.
Notes:
1. phieu_giai_trinh.py:_khoi_pdf `i_cuoi=len(k)` is set AFTER the session heading/"Kết quả"/"Giải thích" were appended, so those
   can stay at the bottom of page N while their table moves to N+1 (repro: 800HS slip HS006, "Thứ 6" heading on p.10, its table on
   p.11). Fix idea: start the KeepTogether at the heading of the last session. Cosmetic, lead's call.
2. xuat_pdf.py:_chia_cot: if the sum of minimum header widths > page width (about >11 columns of this header size) the table
   overflows the right margin silently. No current caller affected (max found 10 cols fits: 509 of 527 pt). Low.
3. test_ux1f_l2 guards only the FA 40-student set; the 800-set min-chars figure is not asserted (by design of spec).
Invariants 1, 4, 6: n/a (layout only; no pipeline/DB/contract change). Privacy: slips built from selected student_ids, unchanged.

## L3 | reviewed f30f05d..f4be762 (d159ba9 L2 follow-up + f4be762 L3)
verdict: NO BUGS (1 low note on d159ba9)
L3 boxes: index.html drops data-quyen="quan_tri" from #btnGtPdfMot; backend untouched (export_phieu_giai_trinh_pdf already in
 phan_quyen's GT1 "phiếu" group for giao_vien, same group as export_phieu_giai_trinh HTML -> no scope widening). Tests: giao_vien +
 student_ids=["s2"] -> ok, PDF contains only "Mã: s2" (s1/s3/s4 absent); student-lookup mode -> gt3_che_do_hoc_sinh, no file written;
 not logged in -> gt3_can_dang_nhap; Chromium: search(1) + pick(2) + Lưu PDF(3) = 3 clicks <= 4, button hidden until a student is
 picked, file name has the sid, no other student in the PDF. In student self-lookup mode the app is `inert` and the backend refuses,
 so showing the button to non-admin does not expose it.
Tests run: ux1f_l3 + ux1f_l2 + xp1_phieu_pdf + giao_dien_xp1_luu_pdf_mot_em + ux1b_l7 + giao_dien_ux1b_phieu + ux1i_i3 +
 fa_sc_l4_phieu_lop -> 71 passed; ux1i_i2_xp1_trong_menu + gt1_tra_cuu + ux1b_vai_gv -> 14 passed. 0 skipped.
d159ba9 (per-session KeepTogether): 40 students FA = 40 pages (unchanged); 800HS = 1278 pages (unchanged), min page chars 159 -> 267,
 pages <200: 2 -> 0, pages <400: 106 -> 52. Word-multiset diff vs 235a3d7: only dates/times differ + fewer repeated column headers
 (tables split less). No content cut. 0 session headings left at a page bottom with the table on the next page (note 1 of L2 closed).
Edge (own): a SINGLE session taller than a page inside KeepTogether -> reportlab splits it (no overflow, nothing cut: 600/600 cells
 present at 10 choices x ~600-char reasons) BUT it first breaks to a new page, so the title+summary stay alone on page 1 (27 chars)
 and the 2nd session also starts a fresh page. Realistic rows (<=~200-char reasons, 10 choices) stay on 1-2 full pages. Low; only
 pathological text length. Optional: no action.
Invariants 1, 4, 6: n/a (HTML attribute + layout only). Privacy ok. Teacher limits: unchanged scope (teacher could already call this
 API for any student_ids/class; Truong answered "keep" on class scoping).

## L4 | reviewed 55255f2..252466e
verdict: NO BUGS (2 low notes)
Boxes: exactly one visible "Chọn lớp" label/select (-> #kqChonLop) on Results for admin and teacher (own Chromium run + ux1f_l4 tests);
 #ux1bLop gone from html/js/tests/css (grep: only a negative assertion + docs remain); stale comment above #ux1bPanel replaced.
Tests: ux1f_l4 + t2_ket_qua + ux1b_vai_gv + ux1i_i3 + ux1b_phieu + t3_l1_ws -> 40 passed, 0 skipped.
Judging the coder's call: CORRECT. export_theo_lop(output_path) and export_bao_cao_tong_hop[_pdf](output_path) have no `lop`
 parameter and are school-wide by definition (one file per class / aggregate numbers, no ids). Only export_phieu_giai_trinh_pdf
 takes `lop`, and "In phiếu cả lớp" now reads #kqChonLop (test: PDF holds exactly the 10A2 students, no other class). Scoping the
 other two would need backend/contract changes (outside L4, would alter existing outputs). Read the box as "all homeroom actions that
 take a class use its value".
t2_ket_qua change: LEGITIMATE, not weakened. The test still asserts the exact visibility triple per tier; only the class-picker
 element's expectation changes ([True,False,False] -> always True when classes exist), a direct consequence of "one select serves
 both" (it now lives in #ux1bPanel, outside the tier switch). No assertion removed or loosened.
Own edge runs (Chromium, 120HS, scratch script): (a) no class data at all -> select hidden, 0 "Chọn lớp" labels, "In phiếu cả lớp"
 disabled, other two actions still work, no JS errors; (b) 115/120 with classes + 5 without (admin and teacher gv1) -> options
 10A1..10A3 + "Chưa có lớp (5)", picking the empty option disables "In phiếu cả lớp" and stays on "Theo lớp"; (c) switching tiers
 clb/ma/lop keeps the select visible with the same value; 0 pageerrors.
Notes: 1. Selecting a class while on the code-lookup tier ("ma") jumps to "Theo lớp" (same behaviour #ux1bLop had; fine).
 2. Unused i18n key ux1b_chon_lop (vi+en) left in i18n.js: harmless; remove when convenient. UX: "Xuất theo lớp" / "Báo cáo tổng hợp"
 sit beside the selector but ignore it (by design) - a short hint could avoid confusion; optional.
Invariants 1, 4, 6: n/a (UI only; no pipeline/DB/contract change). Privacy/teacher limits unchanged.
