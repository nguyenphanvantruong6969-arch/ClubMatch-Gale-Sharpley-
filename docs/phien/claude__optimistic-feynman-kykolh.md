# Branch handoff: claude/optimistic-feynman-kykolh

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Coordinator branch for Truong's competition-feedback work (2 requirements: technical evidence + AI role; allocation
explanation and bounded priority-criteria control). This branch itself carries only **SEC-1** (CodeQL path-injection
fix in `browser_host.py`, PR #34 to main). Two feature items live on their own branches, built by Opus lead sessions:
- **CB1** "Van ban phuong an xep" (PDF + "Chot phuong an"), branch `claude/cb1-van-ban-phuong-an`.
- **DC1 (variant B)** independent input-vs-result checker script, branch `claude/dc1-kiem-doc-lap`.

## Plan (written by Opus; ticked by Sonnet)
- [x] SEC-1: fix two CodeQL alerts in `browser_host.py` (+ test), CI green, PR #34 opened.
- [x] CB1 and DC1 planned and built by Opus sessions (CI green on their branches at last check).
- [x] CB1-FIX3 (UI fixes, "De xuat" badge removed, hints trimmed, button budget 9 to 11) pushed to CB1 branch.
- [x] CB1-FIX4 (PDF rewrite, neutral grey palette only, optional school name) pushed to CB1 branch.
- [ ] Confirm CI green on CB1 head (`d163275`) and DC1 head (`ea11138`), then open PR CB1 to main (Truong said yes).
- [ ] Open PR DC1 to main (not yet asked; ask Truong).
- [ ] After PR #34 merges: check CodeQL re-scan closed alerts #1 and #2.

## Current state (overwrite each handoff)
- Done so far: SEC-1 fix on this branch (`795bca7`, merge `b8b85cd`); PR #34 open. CB1 FIX3 + FIX4 pushed to the
  CB1 branch (head `d163275`). DC1 branch head `ea11138`, CI green on `ea11138`.
- In progress: a scheduled one-shot check (trigger `trig_011fiCs3Aq7NiwdSCsWR3GU6`, fires 12:05 UTC 2026-11-24) will
  check CI on the CB1 branch and, if green, open the CB1 PR to main and report to Truong briefly. If this session is
  gone, do that check manually.
- Tests last run: `tests/test_browser_host.py` 41 pass; CB1 tests (`test_cb1_noi_dung`, `test_cb1_api_pdf`,
  `test_cb1_ui`, `test_cb1_pdf_trung_tinh`) 53 pass; `kiem_nhanh.py --so-seed 2` 7/7. Python Playwright was
  pip-installed in the container only for local UI tests; Node Playwright is at `/opt/node-tools`.
- Open problems: (a) CodeQL fix unverified (no CodeQL locally); if alerts persist after merge, replace path joining
  with a startup-built allowlist map of static files. (b) CB1 PDF is 2 pages (bản chốt page 2 holds "Dấu xác nhận" and
  draw steps); Truong has not asked for 1 page. (c) CB1 head CI not yet seen green after FIX3/FIX4.

## Decisions and gotchas (keep short)
- Truong chose DC1 variant B (conservation checks + join CSV only); full stability check (C) kept in reserve, spec in
  the old scratchpad brief, because soft reserves make a naive stability check give false FAILs.
- CB1: seed printing is opt-in, default OFF (D5 kept), never in the draft; "Chot phuong an" logged via existing log.
- Button budget in Cach xep tab raised 9 to 11 (Chot + Xuat ban du kien visible, panel moved out of the collapsed
  "Tuy chinh them"). Test: `tests/test_giao_dien_ux4_l4.py`.
- PDF colours: greys only (`phuong_an_xep._MAU`), enforced by `tests/test_cb1_pdf_trung_tinh.py`.
- Truong wants short replies and no feature over-explaining, in Vietnamese.
- I pushed directly to the CB1 branch (Truong approved fixing there). Before any push, `git fetch` and check the
  Opus session has not added commits.
- Sample PDFs/screenshots were made from a git worktree at `/tmp/claude-0/cb1wt` (container-local, may be gone).

## Next steps (ordered)
1. Check CI of `claude/cb1-van-ban-phuong-an` head; if green open PR to main (title "CB1: Van ban phuong an xep"),
   attribution footer from the session reminder; report link briefly.
2. Ask Truong whether to open the DC1 PR; check PR #34 merge status and CodeQL alerts.
3. Pending Truong answers: keep or shrink the CB1 PDF to one page; the earlier open questions on D5 wording
   ("thu tu tieu chi co gioi han" vs numeric weights) and `PHAN_CONG.md` (students fill it themselves).
4. Optional doc work (needs an item code first, rule 1): add `CA_MAU.md` sections 3-5 to `KICH_BAN_DEMO.md`.

## Files touched
- browser_host.py, tests/test_browser_host.py: SEC-1 path-injection guards and test.
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: SEC-1 entries (merged main CHANGELOG conflict, kept both).
- (CB1 branch) index.html, js/2x_phuong_an.js, js/18_cai_dat.js, style.css, i18n.js, api_phuong_an.py,
  phuong_an_xep.py, tests/test_cb1_*.py, tests/test_giao_dien_ux4_l4.py, tests/test_giao_dien_ux1_cai_dat.py,
  CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md: CB1-FIX3 and CB1-FIX4.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-24 | Sonnet 5.5 (Opus advisor) | Audited transparency/goals vs feedback; wrote DC1/CB1 briefs; launched two Opus sessions; fixed SEC-1; CB1 UI/PDF fixes; opened PR #34 | CI check for CB1 scheduled 12:05 UTC |
