# Branch handoff: claude/ux1-tich-hop (UX1 integration: A + XP1, then B)

> Protocol: docs/phien/UX1_TICH_HOP_GIAO_THUC.md. English. ≤ 60 lines.

Status: DONE f8ee571 CI green 2026-11-19 (Tests run 44610375319: lint, 4 Linux + 2 Windows shards, coverage gate; Windows exe build run 44610301427 on b0b357c green). A + XP1 + B merged.

## Plan (lead ticks)
- [x] I1 merge claude/ux1-a-giao-dien @0bc2026 — passed (head dac41dd, checker NO BUGS 6d16bb6; I4 review: health_oversubscribed* severity info->medium; dat_loai_clb after run does not mark results stale)
- [x] I2 merge claude/xp1-xuat-pdf @f7f1db6 — passed (head 9a4faca, checker NO BUGS c9b9c89; single "Xuất…" menu; Lưu PDF 3 clicks)
- [x] I3 merge claude/ux1-b-phieu @c618629 — passed (merge 944b111, wiring 5f27391, fix1 b2f7f8b; checker NO BUGS)
- [x] I4 CI gate + user review — passed (review 147fdbb; CI fix1 b0b357c doc test count 344->353, checker NO BUGS f8ee571; CI + Windows build green)

## Current state (overwrite)
- Done: I1–I4. Nothing in progress. Next: Truong opens a PR claude/ux1-tich-hop -> main and decides Needs Truong 4–8.

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01YVAyu2FhPzwKmmTgfwCCGj | done |
| coder | session_01YVAytyZ759wgqn178zVkKz | archived (Sonnet) |
| checker | session_01YVAytyhGhZ8LRTwtD3Z9GW | archived (Sonnet) |

## Needs Truong
1. (resolved) Team B finished; merged in I3.
2. XP1 open questions (combined PDF with contents; pypdf dev-only) are on XP1's own list.
3. (resolved) Windows exe build green on the integrated branch (run 44610301427). Still try the exe by hand (below).
4. Roles: giao_vien is NOT class-scoped (2-role model); any teacher can print every class's slips (with lookup codes) as PDF, same reach as the existing HTML slips. Decide if class scoping is wanted (new item).
5. pypdf not in requirements-dev.txt → pypdf-based PDF tests skip on CI (XP1 open question). Decide: add as dev-only dependency?
6. Review UX1_DANH_GIA_TICH_HOP.md §3: slip PDF spills to a near-empty 2nd page (40 students = 75 pages) and column headers break mid-word ("Huy ch/ương"). Small new item?
7. Review §3.3: giao_vien cannot "Lưu PDF" for ONE student (#btnGtPdfMot quan_tri) but can print the whole class PDF. Allow?
8. Review §3.4: two "Chọn lớp" selects on the Results page (#ux1bLop, #kqChonLop) still; stale comment index.html above #ux1bPanel.

## Final summary (Vietnamese)
- Đã gộp vào `claude/ux1-tich-hop`: A (giao diện, Cài đặt, Việc tiếp theo), XP1 (xuất PDF), B (phiếu, huy chương, báo cáo tổng hợp).
- CI xanh: https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/44610375319 ; bản Windows: run 44610301427.
- Đánh giá người dùng: `docs/ke_hoach/ux/UX1_DANH_GIA_TICH_HOP.md` (cả 7 mục tiêu số lần bấm đạt; 5 vấn đề cần làm tiếp).
- Truong thử tay: (1) tải exe từ run 44610301427, nạp sổ 120 HS, chạy, "Xuất…" → "Phiếu giải trình theo lớp (PDF)" và mở PDF;
  (2) đăng nhập giáo viên → "In phiếu cả lớp" + "Báo cáo tổng hợp (PDF)", xem phiếu có cả Loại CLB và Huy chương;
  (3) tra một em → "Lưu PDF", đếm số lần bấm và xem phiếu có tràn sang trang 2 không.
- Gộp vào `main`: Truong tự mở pull request.
