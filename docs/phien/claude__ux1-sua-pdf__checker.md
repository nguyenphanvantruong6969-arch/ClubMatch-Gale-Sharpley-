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
