# Branch handoff: claude/ux1-tich-hop (coder session)

> Role: coder (Sonnet). Protocol: docs/phien/UX1_TICH_HOP_GIAO_THUC.md. Lead owns the branch file. Simulated data only.

## Feature / goal
Integrate UX1 A (new UI), XP1 (PDF export) and UX1 B (slips, teacher role) into one branch. Done; CI green f8ee571.

## Plan (all done)
- [x] I1 A merged: i18n unchanged, 150 tests, kiem_nhanh 7/7
- [x] I2 XP1 merged: ONE admin "Xuất…" menu (#xuatMenu), 3 PDF items inside, #xuatPdfMenu removed
- [x] I3 B merged (conflicts by me): slip = Loại CLB then Huy chương (HTML+PDF); teacher gets "In phiếu cả lớp" + "Báo cáo tổng hợp (PDF)"; fix1: no `__mac_dinh__` in report
- [x] I4 CI fix1: CLAUDE_CHI_TIET test count 344 -> 353

## Current state
- Done: all lots; full Linux suite once locally: 6977 passed, 4 skipped (old reasons), 0 failed.
- Last coder head: b0b357c. No half-finished work.

## Decisions and gotchas
- "In phiếu cả lớp" = ONE PDF of the chosen class (theo_lop=False + lop), not a folder; XP1 admin menu still has the per-class folder.
- phan_quyen: giao_vien gets export_phieu_giai_trinh_pdf + export_bao_cao_tong_hop_pdf only; export_danh_sach_pdf stays quan_tri.
- test_ux1_ket_qua / xp1_xuat_pdf / ux1b_l7 / xp1_phieu_pdf were edited to the merged behaviour (menu, both columns, rights).
- Local test env: set RBDA_TEST_CHROMIUM; pip install pypdf (not in requirements-dev.txt, so CI skips 5 pypdf tests).
- tests/ count in CLAUDE_CHI_TIET must equal `ls tests/test_*.py | wc -l` (test_a13_12_tai_lieu).

## Open points
1. Add pypdf to requirements-dev.txt? (Truong/XP1 open question)
2. PDF slip has no SVG bars (table instead); HTML keeps SVG.
3. CI coverage >= 85 % never measured locally.

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-19 | Sonnet | I1, I2, I3 (+fix1), I4 fix1 | pushed b0b357c |
