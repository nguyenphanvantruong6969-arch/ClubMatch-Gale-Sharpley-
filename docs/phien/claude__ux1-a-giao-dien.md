# Branch handoff: claude/ux1-a-giao-dien (UX1 team A)

> Protocol: docs/phien/UX1_GIAO_THUC.md. Lots: docs/ke_hoach/ux/UX1_KE_HOACH.md. English. ≤ 60 lines.

Status: IN PROGRESS (branch created 2026-11-18 from origin/claude/gt-tich-hop 407e62c)

## Plan (lead ticks)
- [ ] L1 Next-step bar
- [ ] L2 navigation 6 → 4 groups (+ giao_vien lands on Kết quả & phiếu)
- [ ] L2b settings: one question, 3 cards, saved on click + Undo, fix-in-place, post-run features as actions
- [ ] L3 lookup first on results, one Xuất… menu, import message once
- [ ] L5 warning severity/wording; medal book in non-FA mode → clear message + one-click enable; two sample books
- [ ] L5b medal cells accept Vàng/Bạc/Đồng (+ unaccented/English) → 60/30/10
- [ ] L8-A docs + screenshots + After table
- [ ] CI gate (§5)   - [ ] user review UX1_DANH_GIA_A.md (§6)   - [ ] integration (§7)

## Current state (overwrite)
- Done: branch created. In progress: creating coder + checker sessions.

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01TGThn4GicB4XGX5L6zfZ57 (Opus) | running |
| coder | — | — |
| checker | — | — |

## Needs Truong
1. (L6, team B) Print dialog in the packaged Windows app (WebView2) and browser fallback — manual check.

## Decisions (Truong 2026-11-18)
- Default config unchanged (determination points ON, medals OFF). Medal values 60/30/10, order only.
- Settings = 3 cards saved on click; medals change live; post-run features are actions on results.
- Slip PDF via Print → Save as PDF, no new library; cutoff shown for tested clubs; medal + club type on slip in FA mode.
- Exactly 3 sessions per team; never ask Truong; integration by team A lead.

## Final summary (Vietnamese, ≤ 10 lines)
