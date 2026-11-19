# Branch handoff: claude/ux1-tich-hop (UX1 integration: A + XP1, then B)

> Protocol: docs/phien/UX1_TICH_HOP_GIAO_THUC.md. English. ≤ 60 lines.

Status: IN PROGRESS (lead started 2026-11-19; branch from origin/claude/gt-tich-hop @ 396509b)

## Plan (lead ticks)
- [x] I1 merge claude/ux1-a-giao-dien @0bc2026 — passed (head dac41dd, checker NO BUGS 6d16bb6; I4 review: health_oversubscribed* severity info->medium; dat_loai_clb after run does not mark results stale)
- [x] I2 merge claude/xp1-xuat-pdf @f7f1db6 — passed (head 9a4faca, checker NO BUGS c9b9c89; single "Xuất…" menu; Lưu PDF 3 clicks)
- [ ] I3 merge claude/ux1-b-phieu after its Status: DONE (or leave for later, protocol §3)
- [ ] I4 CI gate + user review UX1_DANH_GIA_TICH_HOP.md

## Current state (overwrite)
- Done: I1, I2. B is DONE (eac69df CI green, branch c618629) → I3 merge running.

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01YVAyu2FhPzwKmmTgfwCCGj | active |
| coder | session_01YVAytyZ759wgqn178zVkKz | active (Sonnet) |
| checker | session_01YVAytyhGhZ8LRTwtD3Z9GW | active (Sonnet) |

## Needs Truong
1. Team B (claude/ux1-b-phieu) has no lead yet; I3 cannot run until it is DONE.
2. XP1 open questions (combined PDF with contents; pypdf dev-only) are on XP1's own list.
3. XP1: Windows exe build was NOT run on its branch (XP1 Needs Truong); I4 runs it on the integrated branch.
