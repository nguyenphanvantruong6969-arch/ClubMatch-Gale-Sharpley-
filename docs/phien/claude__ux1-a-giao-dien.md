# Branch handoff: claude/ux1-a-giao-dien (UX1 team A)

> Protocol: docs/phien/UX1_GIAO_THUC.md. Lots: docs/ke_hoach/ux/UX1_KE_HOACH.md. English. ≤ 60 lines.

Status: IN PROGRESS (branch created 2026-11-18 from origin/claude/gt-tich-hop 407e62c)

## Plan (lead ticks)
- [x] L1 Next-step bar (ebf24cd; checker NO BUGS 02f0a62; admin export = 4 clicks once L3 menu lands)
- [x] L2 navigation 6 → 4 groups (0ded385; checker NO BUGS 89efe2a)
- [x] L2b settings 3 cards + Undo + fix-in-place + post-run actions (e3d0382; checker NO BUGS c2aff36; new dat_loai_clb/get_san_sang_huy_chuong; 'Thay đổi…' → Quản lý › Nâng cao)
- [x] L3 lookup first, Xuất… menu, import msg once (e812cf3+fix1 3ba1efe; checker NO BUGS 2a226e0; admin export 4 clicks on real 120 book incl. 32 unplaced)
- [x] L5 warnings medium + short; medal-book message + Bật chế độ huy chương; two sample books (764c85c; checker NO BUGS 576ad3f)
- [ ] L5b medal cells accept Vàng/Bạc/Đồng (+ unaccented/English) → 60/30/10
- [ ] L8-A docs + screenshots + After table
- [ ] CI gate (§5)   - [ ] user review UX1_DANH_GIA_A.md (§6)   - [ ] integration (§7)

## Current state (overwrite)
- Done: L1, L2, L2b, L3, L5. In progress: L5b (GO sent).

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01TGThn4GicB4XGX5L6zfZ57 (Opus) | running |
| coder | session_01TGThn7nTbkpGayZsVaCCRd (Sonnet) | running |
| checker | session_01TGThn4gcnMUxsQjDeXhcVc (Sonnet) | running |

## Needs Truong
1. (L6, team B) Print dialog in the packaged Windows app (WebView2) and browser fallback — manual check.

## Decisions (Truong 2026-11-18)
- Default config unchanged (determination points ON, medals OFF). Medal values 60/30/10, order only.
- Settings = 3 cards saved on click; medals change live; post-run features are actions on results.
- Slip PDF via Print → Save as PDF, no new library; cutoff shown for tested clubs; medal + club type on slip in FA mode.
- Exactly 3 sessions per team; never ask Truong; integration by team A lead.

## Final summary (Vietnamese, ≤ 10 lines)
