# Branch handoff: claude/ux1-b-phieu (UX1 team B)

> Protocol: docs/phien/UX1_GIAO_THUC.md. Lots: docs/ke_hoach/ux/UX1_KE_HOACH.md. English. ≤ 60 lines.

Status: NOT STARTED (planned by Opus 2026-11-18; branch to be created from origin/claude/gt-tich-hop)

## Plan (lead ticks)
- [ ] L4-B Báo cáo tổng hợp (bao_cao_tong_hop.py, export_bao_cao_tong_hop, QUYEN giao_vien) + In phiếu cả lớp
- [ ] L6 (REPLACED by XP1: real PDF via reportlab, `export_phieu_giai_trinh_pdf`; do not build the print-dialog version) slip In / Lưu PDF via iframe print (get_phieu_giai_trinh_html, QUYEN, audit row)
- [ ] L7 (club type DONE in XP1-L2: `loai_clb` in `giai_trinh`, "Loại CLB" column in slip HTML/PDF) slip content: summary, tested-club scores, SVG own-vs-cutoff, next steps, FA: club type + medal, plain words
- [ ] L8-B slip docs, regenerate CA_MAU.md + evidence pack + phieu_mau.pdf, After row
- [ ] CI gate (§5)   - [ ] user review UX1_DANH_GIA_B.md (§6)

## Current state (overwrite)
- Done: none. In progress: none.

## Sessions
| Role | Session | State |
|---|---|---|
| lead | — | — |
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
