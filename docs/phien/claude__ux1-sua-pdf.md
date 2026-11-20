# Branch handoff: claude/ux1-sua-pdf (UX1F: fixes after integration review)

> Protocol: docs/phien/UX1F_GIAO_THUC.md. English. ≤ 60 lines.

Status: IN PROGRESS (lead started 2026-11-19). Was: NOT STARTED (planned by Opus 2026-11-20; branch from origin/claude/ux1-tich-hop @ 2d1a547, PR #21 open)

## Plan (lead ticks)
- [x] L1 pypdf dev-only; pypdf tests run (not skip) on CI
- [x] L2 slip PDF: typical slip = 1 page, no near-empty 2nd page; headers never break mid-word (40 students ≤ 44 pages)
- [ ] L3 giao_vien can "Lưu PDF" for one student (#btnGtPdfMot)
- [ ] L4 one "Chọn lớp" select on Results (keep #kqChonLop; drop #ux1bLop; stale comment)
- [ ] L5 CI + Windows build + short UX1F review section; PR (base main if #21 merged, else claude/ux1-tich-hop)

## Current state (overwrite)
- Done: L1 (ec962ee), L2 (235a3d7; 40HS 74→40 pages, 800HS 1519→1278). In progress: L3 (+ L2 note 1 heading-orphan fix).

## Sessions
| Role | Session | State |
|---|---|---|
| lead | session_01YVAyu14eN1iunrtd4gEvz4 | running |
| coder | session_01YVAytzdPaKNfd55P1azpLB | created, venv setup |
| checker | session_01YVAytz5p2qHMPQ93QrvuXy | created, venv setup |

## Needs Truong
- (none yet) Answers already given: 1 keep teacher scope, 6 release overwrite resolved.
