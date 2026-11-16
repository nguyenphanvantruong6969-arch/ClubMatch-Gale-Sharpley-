# Branch handoff: claude/gt1-giai-trinh

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/GT_GIAO_THUC.md`. Lot specs: `docs/ke_hoach/gt/GT1_GIAI_TRINH.md`.

Status: IN PROGRESS (base 5926107)

## Feature / goal
GT1 (parent item C3): per-student explanation for ANY run (default RB-DA and FA-DAA). The school can show each
student, in plain words, their preferences, the scores/criteria that mattered, each club's capacity and cut-off,
constraints, and why they got (or did not get) each club — on screen (admin/teacher), on a printed slip, and by
self-lookup with a code. Reports/controls only: no run code path changes (invariants 1, 2, 3 untouched).

## Plan (written by Opus lead; ticked by lead after CHECKER NO BUGS)
- [ ] L1 Explanation engine: `giai_trinh.py` (`giai_trinh_mot_hoc_sinh`), `fa_ly_do.cau_ly_do_rbda`, stale guard
      via `dau_van_tay_chay`, API `get_giai_trinh_hoc_sinh`, errors `gt1_khong_co_hoc_sinh`, `gt1_chua_chay`.
      Tests `tests/test_gt1_giai_trinh.py` (a)–(e).
- [ ] L2 Lookup screen (admin/teacher): panel "Tra cứu một học sinh" in results tab, `js/14_giai_trinh.js`,
      `<!-- GT1 -->` block in `index.html`. Tests `tests/test_giao_dien_gt1_tra_cuu.py` (Chromium).
- [ ] L3 Printable slip: `export_phieu_giai_trinh`, buttons in L2 panel. Tests `tests/test_gt1_phieu.py`.
- [ ] L4 Lookup codes + student self-lookup mode: table `ma_tra_cuu`, `tao_ma_tra_cuu`, `tao_lai_ma_tra_cuu`,
      `export_ma_tra_cuu_csv`, `tra_cuu_hoc_sinh`, lockout, overlay UI. Tests `tests/test_gt1_ma_tra_cuu.py`,
      `tests/test_giao_dien_gt1_hoc_sinh.py`.
- [ ] CI gate (§6): lint + all shards + coverage ≥ 85 % green on head.

### Lead notes per lot (added to the spec; writer must follow)
- All lots: error codes only `gt1_*`; i18n block appended at end of dict marked `# GT1`; run `python tao_i18n_js.py`.
  Fake data only. Student-facing JSON/HTML contains only that student. No internal codes in teacher-visible text.
- L1: FA off path must reconstruct inputs read-only (no writes to any table); prove with `kiem_nhanh.py --co-so
  origin/main --so-seed 20`. Outcome codes are constants in `giai_trinh.py`; sentences only in `fa_ly_do.py`.

## Sessions
| Role | Session id | Model | State |
|---|---|---|---|
| lead | session_01TGThn8ujS9oohKhbgDiJgD | claude-opus-5-5 | active |
| writer | session_01TGThn4UaExaTx1hj5kH5FF | claude-sonnet-5-5 | active (L1) |
| checker | session_01TGThn8ZPKEmNQz6wmpDseA | claude-sonnet-5-5 | active (idle) |

## Current state (overwrite each handoff)
- Done so far: branch created, this file written.
- In progress: L1 (GO L1 sent 2026-11-16).
- Tests: none yet.
- Open problems: none.

## Needs Truong
- (none yet)

## Decisions and gotchas (keep short)
- Decisions D-GT1…D-GT9 in the protocol §0 are final; do not ask again.

## Next steps (ordered)
1. Create writer + checker (§11 prompts), send `GO L1`.
2. Run §5 loop L1 → L4, then §6 CI gate.

## Files touched
- docs/phien/claude__gt1-giai-trinh.md: this file.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Opus lead | Branch + handoff file created | base 5926107 |
