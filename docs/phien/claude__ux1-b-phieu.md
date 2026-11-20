# Branch handoff: claude/ux1-b-phieu (UX1 team B)

> Protocol: docs/phien/UX1_GIAO_THUC.md (**§10 wins**). Lots: docs/ke_hoach/ux/UX1_KE_HOACH.md. English. ≤ 60 lines.

Status: DONE eac69df CI green 2026-11-19 (run 44580819534: lint, 4 Linux + 2 Windows shards, coverage ≥ 85 %)

## Plan (lead ticks) — order from protocol §10
- [x] L4-B Báo cáo tổng hợp (bao_cao_tong_hop.py, export_bao_cao_tong_hop HTML, QUYEN giao_vien) + homeroom landing
      (class picker, "Xuất theo {cohort_l}"); NO "In phiếu cả lớp" button (XP1, wired at integration I3)
- [x] L7 slip content: summary, tested-club scores, SVG own-vs-cutoff, next steps, FA medal column + medal legend,
      plain words. NOT the club type (XP1 owns `loai`)
- [x] L5c the 5 recommendations of docs/ke_hoach/ux/UX1_DANH_GIA_A.md §4 (rec 5: privacy red line kept
      visible by default — default export has cutoff + lottery sheet; rename done)
- [x] L8-B slip docs, regenerate CA_MAU.md + evidence pack + phieu_mau.pdf, After row
- [x] CI gate (§5)   - [x] user review UX1_DANH_GIA_B.md (§6)
- ~~L6 slip In / Lưu PDF via iframe print~~ DROPPED (XP1)

## Current state (overwrite)
- Done: all lots. L4-B 0f73c43, L7 fc5e9fc, L5c f3ff065, L8-B b960b60, CI-1 775f669, review fixes R1 f58df43, review eac69df.
- Waiting for Team A lead to integrate (protocol §7/§10: A → B → XP1, lot I3). Coder/checker idle, not archived.
- origin/main has unrelated history (git refuses merge) — not merged; invariant 1 still checked against origin/main by content.

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01YVAytyWhTzeYjV1fcHGdde (Opus) | done |
| coder | session_01YVAyu2zZMBG9biCXj6dH9h (Sonnet) | idle |
| checker | session_01YVAyu1k1DkBJUtG9sVekSz (Sonnet) | idle |

## Needs Truong
1. Merge order at integration: A → B → XP1 (protocol §10); XP1 must be DONE first or it waits.
2. Manual Windows check (pywebview/WebView2): "Báo cáo tổng hợp" and "In phiếu cho học sinh này" write HTML; "Mở tệp"
   opens it. Recommendation: try once on the school PC before release.
3. origin/main and the UX branches have unrelated git histories; merging to main needs Truong's chosen method.

## Final summary (Vietnamese)
- Xong: L4-B (báo cáo tổng hợp HTML + trang giáo viên), L7 (nội dung phiếu, cột huy chương), L5c (5 đề xuất của nhóm A;
  dòng đỏ quyền riêng tư giữ hiện vì tệp xuất mặc định có điểm chuẩn và số bốc thăm), L8-B (tài liệu, ảnh phiếu).
- Bỏ theo §10: L6 và cột loại CLB (chuyển XP1). Phiếu PDF một em hiện 5 lần bấm, đạt 4 khi gộp XP1 (lô I3).
- CI xanh: https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/44580819534
- Đánh giá người dùng: docs/ke_hoach/ux/UX1_DANH_GIA_B.md (dữ liệu mô phỏng).
- Truong thử tay 3 bước: (1) đăng nhập tài khoản giáo viên → bấm "Báo cáo tổng hợp", mở tệp; (2) tra một em → "In phiếu
  cho học sinh này" → mở tệp, xem dòng tóm tắt và thanh điểm; (3) bật chế độ Huy chương, nạp SO_NHAP_FA_MAU_120HS.xlsx,
  chạy, in phiếu một em: cột Huy chương và "Mức vào được" khớp câu "Vì sao".
