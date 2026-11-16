# Branch handoff: claude/gt3-quyen-tai-lieu

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/GT_GIAO_THUC.md`. Lot specs: `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md`.

Status: IN PROGRESS

## Feature / goal
GT3 (parents E1-lite, E2; docs outside the registry): two roles (`quan_tri`, `giao_vien`) with passwords, OFF until the
first admin account exists; a central permission gate in `PipelineAPI`; an append-only audit log of every write action;
and the evidence pack the jury asked for (role of AI, flow diagram, how to run, input data, member-roles template, demo
and video scripts). Then the GT3 lead runs integration of GT1+GT2+GT3 on `claude/gt-tich-hop` (protocol §9, lots I1–I4).
Schema changes approved (D-GT8): tables `tai_khoan`, `nhat_ky_thao_tac` after the `wharton_lock` block. Error codes
`gt3_*`; JS file `js/16_tai_khoan.js`; tests `tests/test_gt3_*.py`, `tests/test_giao_dien_gt3_*.py`.

## Plan (written by Opus; ticked by the lead after checker NO BUGS)
- [x] L1 Accounts and login (e62e24a, checker NO BUGS after fix1) (`tai_khoan.py`, API, lock/idle, recovery clear option, `js/16_tai_khoan.js`)
- [x] L2 Permission gate (5208c6d, checker NO BUGS after fix1) (`phan_quyen.py` map `QUYEN`, central enforcement, UI hides buttons)
- [ ] L3 Audit log (`nhat_ky_thao_tac`, append-only triggers, viewer + CSV export)
- [ ] L4 Evidence docs (`docs/giai_trinh/*.md`, `so_do_luong.svg`, `PHAN_CONG.md` template)
- [ ] CI gate (§6) green on branch head
- [ ] Integration §9 on `claude/gt-tich-hop`: I1 permissions, I2 student mode, I3 audit, I4 evidence pack, CI green

### Lead notes per lot
- All lots: every new table/option defaults OFF; accounts table empty ⇒ behaviour byte-identical to today.
- L2: the `dir(PipelineAPI)` completeness test will fail on integration until GT1/GT2 methods are classified (I1); that is intended.
- L3 (lead decision 2026-11-16, from checker L2): on-site entry writes (submit_preferences, submit_huy_chuong, submit_test_selection, attendance/score writes) stay `giao_vien`, so L3 audits EVERY write method of either role, not only `quan_tri` calls.

## Sessions
| Role | Model | Session id | State |
|---|---|---|---|
| lead | Opus | session_01YVAyu1qFUsCrfJzADRDejq | active |
| writer | Sonnet | session_01YVAyu1P96ELQbaGCN11z8y | archived (handoff after L1, 95fad10) |
| writer 2 | Sonnet | session_01YVAytzxaEXv7mrFdiaw85i | active |
| checker | Sonnet | session_01YVAytz3RuHwjzM5L3EVnKE | active |

## Needs Truong
- (none yet)

## Current state (overwrite each handoff)
- Done so far: branch created from `origin/claude/determined-allen-kig6ud`; this file written.
- In progress: L3 sent to writer (GO L3). L1 e62e24a, L2 5208c6d done.

## Decisions and gotchas (keep short)
- Decisions D-GT1…D-GT9 in the protocol §0; do not ask again.

## Next steps (ordered)
1. Run §5 for L1 → L4, then §6, then §9.

## Files touched
- docs/phien/claude__gt3-quyen-tai-lieu.md: branch handoff (this file)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Opus (lead) | Branch + handoff file created | |
