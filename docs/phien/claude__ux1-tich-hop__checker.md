# Checker handoff: claude/ux1-tich-hop (English, <= 30 lines)

Role: tester. All lots checked; final state CI green f8ee571. Full per-lot detail is in git history of this file.

| Lot | Range | Verdict | Evidence |
|---|---|---|---|
| I1 merge A | 90a4da1..dac41dd | NO BUGS | 159 tests; kiem_nhanh 7/7; inv 1,2,4,6,7 ok; dat_loai_clb QUAN_TRI |
| I2 merge XP1 | 8f37d9d..9a4faca | NO BUGS | 246 tests, 0 skipped; edited tests only retargeted; Lưu PDF 3 clicks; PDF exports QUAN_TRI |
| I3 merge B | 91d5f1a..5f27391 | 1 BUG (low) | `__mac_dinh__` printed in Báo cáo tổng hợp "Buổi" (HTML + PDF); 353 tests |
| I3 fix1 | 5f27391..b2f7f8b | NO BUGS | bug gone; real labels and custom label kept; 269 tests; 7/7 |
| I4 fix1 | 147fdbb..b0b357c | NO BUGS | docs only; test file count 353; map rows and review doc match the code |

Notes (not bugs):
- giao_vien is not class-scoped (2 roles): the PDF slip calls reach every student and print lookup codes, same as HTML.
- health_oversubscribed* severity info -> medium; dat_loai_clb after a run does not mark results stale (pre-existing).
- Not re-measured in I4: 75/78-page slip counts and the admin 4-click flow.
Method: fake data only; own edge scripts lived in the scratchpad (not committed); Chromium via RBDA_TEST_CHROMIUM, pypdf installed.
