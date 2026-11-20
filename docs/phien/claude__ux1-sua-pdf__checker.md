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
