# Branch handoff: claude/ux1-b-phieu (UX1 team B)

> Protocol: docs/phien/UX1_GIAO_THUC.md (**§10 wins**). Lots: docs/ke_hoach/ux/UX1_KE_HOACH.md. English. ≤ 60 lines.

Status: IN PROGRESS (re-scoped by Opus 2026-11-19; branch created from origin/claude/ux1-a-giao-dien @ dd43bdc)

## Plan (lead ticks) — order from protocol §10
- [x] L4-B Báo cáo tổng hợp (bao_cao_tong_hop.py, export_bao_cao_tong_hop HTML, QUYEN giao_vien) + homeroom landing
      (class picker, "Xuất theo {cohort_l}"); NO "In phiếu cả lớp" button (XP1, wired at integration I3)
- [x] L7 slip content: summary, tested-club scores, SVG own-vs-cutoff, next steps, FA medal column + medal legend,
      plain words. NOT the club type (XP1 owns `loai`)
- [x] L5c the 5 recommendations of docs/ke_hoach/ux/UX1_DANH_GIA_A.md §4 (rec 5: privacy red line kept
      visible by default — default export has cutoff + lottery sheet; rename done)
- [x] L8-B slip docs, regenerate CA_MAU.md + evidence pack + phieu_mau.pdf, After row
- [ ] CI gate (§5)   - [ ] user review UX1_DANH_GIA_B.md (§6)
- ~~L6 slip In / Lưu PDF via iframe print~~ DROPPED (XP1)

## Current state (overwrite)
- Done: L4-B (0f73c43), L7 (fc5e9fc, 2 fix rounds), checker NO BUGS. L5c (f3ff065, 1 fix round). L8-B (b960b60), CI-1 fix (775f669), lead review fixes R1 (f58df43: FA cutoff, MEDAL sentence, report labels). In progress: CI gate on head.

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01YVAytyWhTzeYjV1fcHGdde (Opus) | running |
| coder | session_01YVAyu2zZMBG9biCXj6dH9h (Sonnet) | running |
| checker | session_01YVAyu1k1DkBJUtG9sVekSz (Sonnet) | running |

## Needs Truong
1. Merge order at integration: A → B → XP1 (protocol §10); XP1 must be DONE first or it waits.
