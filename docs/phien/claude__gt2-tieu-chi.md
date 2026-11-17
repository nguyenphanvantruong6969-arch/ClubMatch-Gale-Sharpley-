# Branch handoff: claude/gt2-tieu-chi

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/GT_GIAO_THUC.md`. Lot specs: `docs/ke_hoach/gt/GT2_TIEU_CHI.md`.

Status: IN PROGRESS (L1)

## Feature / goal
GT2 (parents A1, Z7-lite): an authorised admin sees the allocation criteria as a plain ordered list, changes them only
within the approved bounded set (D-GT1: lexicographic, existing `rules` keys/values only, no weights, no sensitive
data), runs labelled TRIAL allocations (`run_history.loai_chay='thu'`, rows in `ket_qua_thu`) that never touch official
results, compares any two runs side by side (totals, per club, per priority group/class, changed students), and can
adopt a trial's criteria for the next official run. Schema (D-GT8): column `run_history.loai_chay` (in `di_tru_schema`)
+ table `ket_qua_thu` after the `fa_phan_hoi` block. Error codes `gt2_*`; JS `js/15_tieu_chi.js`; tests
`tests/test_gt2_*.py`, `tests/test_giao_dien_gt2_*.py`.

## Plan (written by Opus; ticked by the lead after checker NO BUGS)
- [ ] L1 Criteria in plain words + closed allow-list (`tieu_chi.py` `mo_ta_tieu_chi`, `cac_lua_chon_hop_le`; API `get_tieu_chi`; panel "Tiêu chí xếp")
- [ ] L2 Trial runs, labelled, append-only (`loai_chay`, `ket_qua_thu`, API `run_thu`, all official readers ignore trials)
- [ ] L3 Compare two runs (`so_sanh_lan_chay`, HTML + CSV export, UI "Thử cấu hình")
- [ ] L4 Adopt a trial's criteria (confirm dialog, save via `update_workspace_config`, no result copy)
- [ ] CI gate (§6) green on branch head

### Lead notes per lot
- All lots: every new table/option defaults OFF; no trial ever ⇒ behaviour byte-identical to today (invariant 1 via `kiem_nhanh.py --co-so origin/main --so-seed 20`).
- All lots: Windows CI console is cp1252 — any CLI print must reconfigure stdout to UTF-8; tests spawning CLIs decode with `encoding="utf-8"`.
- L1: user-facing text plain Vietnamese, no internal codes; the fixed "không dùng thứ hạng nguyện vọng…" note is mandatory.
- L2: re-grep `run_history` / `MAX(run_id)` / `ORDER BY run_id` in ALL .py files (not only those listed) before coding; prefer one helper `run_chinh_thuc_moi_nhat(cur)`. Trial must never redraw or relock STB.
- L2 FA: if the FA solver cannot take a rules override without touching `fa_*`, refuse with `gt2_thu_chua_ho_tro_fa` and add a Needs Truong line.

## Sessions
| Role | Model | Session id | State |
|---|---|---|---|
| lead | Opus | session_01YVAyu3PPHv9SNntepRSLwh | active |

## Needs Truong
- (none yet)

## Current state (overwrite each handoff)
- Done: branch created from origin/claude/determined-allen-kig6ud; this file.
- In progress: L1 (writer).
- Tests: —
- Open problems: —

## Decisions and gotchas (keep short)
- Decisions D-GT1..D-GT9 in protocol §0; do not ask again.
- Any push to the branch cancels the running CI (concurrency); no pushes during the CI gate except fixes.

## Next steps (ordered)
1. §5 loop L1 → L4, then §6.

## Files touched
- docs/phien/claude__gt2-tieu-chi.md: this file

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Opus (lead) | Branch + handoff file created | GT3 integration without GT2 starts 2026-11-18T16:25Z |
