# Branch handoff: claude/ux1-sua-pdf (UX1F: fixes after integration review)

> Protocol: docs/phien/UX1F_GIAO_THUC.md. English. ≤ 60 lines.

Status: DONE 3306876 CI green 2026-11-20 (Tests run 44649407159; Windows build run 44645133761 green)

## Plan (lead ticks)
- [x] L1 pypdf dev-only; pypdf tests run (not skip) on CI
- [x] L2 slip PDF: typical slip = 1 page, no near-empty 2nd page; headers never break mid-word (40 students ≤ 44 pages)
- [x] L3 giao_vien can "Lưu PDF" for one student (#btnGtPdfMot)
- [x] L4 one "Chọn lớp" select on Results (keep #kqChonLop; drop #ux1bLop; stale comment)
- [x] L5 CI + Windows build + short UX1F review section; PR (base main if #21 merged, else claude/ux1-tich-hop)

## Current state (overwrite)
- Done: L1–L5. PR open to claude/ux1-tich-hop (PR #21 still open).

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01YVAyu14eN1iunrtd4gEvz4 | done |
| coder | session_01YVAytzdPaKNfd55P1azpLB | done, archived |
| checker | session_01YVAytz5p2qHMPQ93QrvuXy | done, archived |

## Needs Truong
- (none yet) Answers already given: 1 keep teacher scope, 6 release overwrite resolved.

## Tóm tắt cuối (tiếng Việt)
- L1: pypdf chỉ ở requirements-dev.txt + máy Windows CI; 4 tệp test PDF chạy thật (70 passed, 0 skip).
- L2: phiếu PDF lề 12 mm, chữ 8,5 pt, tiêu đề cột không ngắt giữa từ, tiêu đề buổi đi cùng bảng; 40 HS 74→40 trang, 800 HS 1519→1278, không trang < 200 ký tự.
- L3: giáo viên "Lưu PDF" phiếu một em (3 bấm), PDF chỉ chứa em đó; vai học sinh bị từ chối.
- L4: một ô "Chọn lớp" (#kqChonLop) trên Kết quả; "In phiếu cả lớp" dùng nó; "Xuất theo lớp"/"Báo cáo tổng hợp" vẫn toàn trường (backend không nhận lớp).
- L5: CI xanh (lint, 4 Linux, 2 Windows, độ phủ ≥ 85 %), bản dựng Windows xanh; mục UX1F trong UX1_DANH_GIA_TICH_HOP.md.
- Thử tay: (1) giáo viên tìm 1 em → Lưu PDF; (2) chọn lớp → In phiếu cả lớp, xem số trang; (3) mở phiếu 1 em, xem tiêu đề cột.
