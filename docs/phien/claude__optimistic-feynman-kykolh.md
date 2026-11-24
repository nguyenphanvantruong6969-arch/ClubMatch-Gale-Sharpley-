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
- [x] SEC-1: fix two CodeQL alerts in `browser_host.py` (+ test); PR #34 MERGED into main.
- [x] CB1 and DC1 planned and built by Opus sessions; CI green on both branches.
- [x] CB1-FIX3/FIX4/FIX5: UI fixes, badge removed, hints trimmed, neutral-grey one-page PDF with school name.
- [x] DC1 PR #35 opened (main merged into its branch first, head `38d1c06`).
- [x] Main merged into CB1 branch, doc conflicts resolved (head `99938da`).
- [ ] CB1 PR: scheduled one-shot (trigger `trig_01NHqDYC9ouTDR2UXZCTtv4L`, 12:46 UTC 2026-11-24; CI of CB1 merge commit `99938da` was still queued at 12:30) checks CI then opens
  it. If the session is gone, open it manually (see Next steps).
- [ ] Merge order, Truong to do: #35 DC1, then CB1 PR (CB1 will then conflict on docs; resolve).
- [ ] Check CodeQL re-scan closed alerts #1 and #2 after PR #34 merge.

## Current state (overwrite each handoff)
- Done so far: SEC-1 merged. PR #35 (DC1) open, CI running at last look. CB1 branch `claude/cb1-van-ban-phuong-an`
  head `99938da` (main merged, related tests pass); its PR not opened yet (scheduled).
- This branch (`claude/optimistic-feynman-kykolh`) was restarted from main after PR #34 merged (plain fast-forward
  push, no force); it carries only this handoff file.
- Tests last run: CB1 tests 54 pass, `test_browser_host.py` 41 pass, `test_a13_12_tai_lieu.py` pass (file count 406
  on the merged CB1 tree), DC1 `test_dc1_kiem_doc_lap.py` 27 pass; `kiem_nhanh.py --so-seed 2` 7/7 earlier.
- Open problems: (a) CodeQL fix unverified: if alerts persist, replace path joining with a startup-built allowlist map
  of static files in `browser_host.py`. (b) CB1 PDF is one page but dense; widen spacing if Truong finds it cramped.
  (c) After DC1 merges, CB1 conflicts in CHANGELOG.md, docs/ke_hoach/TIEN_DO.md and the test-file count line in
  docs/ke_hoach/CLAUDE_CHI_TIET.md (recount with `ls tests/test_*.py | wc -l`; keep both CHANGELOG/TIEN_DO sides).

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
1. If the CB1 PR is not open: check CI of CB1 head, then open PR `claude/cb1-van-ban-phuong-an` to main, title
   "CB1: Van ban phuong an xep", short body, attribution footer from the session reminder.
2. When Truong says DC1 (#35) merged: merge main into the CB1 branch, resolve the three doc conflicts above, run
   `tests/test_a13_12_tai_lieu.py` and CB1 tests, push (fetch first; the Opus session may have pushed).
3. Check PR #34's CodeQL result; report briefly.
4. Pending Truong decisions from earlier: D5 wording ("thu tu tieu chi co gioi han" vs numeric weights); students fill
   `docs/giai_trinh/PHAN_CONG.md` themselves; optional: link `CA_MAU.md` sections 3-5 into `KICH_BAN_DEMO.md` (needs an
   item code, rule 1).

## Files touched
- browser_host.py, tests/test_browser_host.py: SEC-1 path-injection guards and test.
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: SEC-1 entries (merged main CHANGELOG conflict, kept both).
- (CB1 branch) index.html, js/2x_phuong_an.js, js/18_cai_dat.js, style.css, i18n.js, api_phuong_an.py,
  phuong_an_xep.py, tests/test_cb1_*.py, tests/test_giao_dien_ux4_l4.py, tests/test_giao_dien_ux1_cai_dat.py,
  CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md: CB1-FIX3 and CB1-FIX4.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-24 | Sonnet 5.5 (Opus advisor) | Audited transparency/goals vs feedback; wrote DC1/CB1 briefs; launched two Opus sessions; fixed SEC-1; CB1 UI/PDF fixes; opened PR #34 | CI check for CB1 scheduled 12:35 UTC |
| 2026-11-24 | Sonnet 5.5 (Opus advisor) | CB1 PDF: neutral greys, school name, squeezed to one page (FIX4, FIX5); handoff refreshed | Truong: "everything looks fine" |
| 2026-11-24 | Sonnet 5.5 (Opus advisor) | Opened PR #35 (DC1); merged main into CB1 and DC1 branches; scheduled CB1 PR; restarted this branch from main after PR #34 merged | Merge order: #35 then CB1 PR |
| 2026-11-24 | Sonnet 5.5 (Opus advisor) | Scheduled CB1 PR check ran: CB1 CI queued, DC1 push CI green, PR run queued; rescheduled to 12:46 UTC | Merge order unchanged: #35 then CB1 |
