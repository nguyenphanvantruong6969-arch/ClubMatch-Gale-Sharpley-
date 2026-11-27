# VG2 protocol (size M: coder + auto-spawned checker, NO lead) — same mechanics as `VG1_GIAO_THUC.md`

> Source of work: `docs/phien/claude__vg2-ra-soat-theo-vai.md` (decisions D1–D5, lots L1–L3). Branch: `claude/vg2-ra-soat-theo-vai`.
> Read `docs/phien/VG1_GIAO_THUC.md` §0–§5 and apply it with VG1→VG2, branch/file names swapped, and the points below. Where they differ, THIS file wins.

## 0. FULL AUTO (Truong, 2026-11-27) and exceptions
- Never wait for human input; never end a turn with work/CI pending (use `send_later` / `ScheduleWakeup` / `Monitor`). Every question has a SAFE default: pick it, write one line in "Decisions", continue. "Needs Truong" is a note, never a stop.
- CLAUDE.md rule 10 is lifted for this item only: the coder spawns ONE checker session (`create_session`, model `claude-opus-5-5`, same repo, `source_revision` = this branch, prompt = VG1 protocol §5 with VG2 names). If `create_session` is unavailable in this account, do a second self-review pass with `soat-ma` four tiers and continue (note it in the branch file).
- Start condition (branch file "START CONDITION") is checked FIRST: base = tip of `origin/claude/charming-cray-2izyn6` once VG1 is CI-green; create `claude/vg2-ra-soat-theo-vai` from it.

## 1. Roles: coder Sonnet `claude-sonnet-5-5`; checker Opus `claude-opus-5-5` (verdict file `docs/phien/claude__vg2-ra-soat-theo-vai__checker.md`, only file it pushes).
## 2. Milestones: MILESTONE 1 after L2 (checker reviews L1+L2); MILESTONE 2 after L3. Coder marks a lot passed only on `CHECKER REPORT <k> NO BUGS`; max 2 FIX rounds per finding then note + `git revert` that lot.
## 3. Checker focus
- Invariants 1, 4, 5, 6, 7 (new parameters default to old behaviour; `{ok,data,errors}`; errors only via `i18n_errors.py`).
- Security: the admin lock still refuses a correct password during a lock, and the level resets only on success; no PIN in logs; `dk_gv_xoa` and all new admin calls denied to teacher/student; deleted teacher's sessions dead.
- Integrity: normalised duplicates blocked but existing duplicate rows still log in; `dk_phong_xoa` never leaves a dangling `phong_id`; nothing is deleted without confirm in the UI.
- UI: confirm dialogs keyboard-operable; lists visible at 375 px without horizontal overflow; 3 own edge cases per milestone.
## 4. Final gate = CI LOOP — exactly VG1 protocol §4 (all of: repro tests, related tests, `kiem_nhanh.py` 7/7, `soat-ma`, GitHub Actions `tests.yml` incl. coverage ≥ 85 % and `Build Windows executable (rbda-kiosk)` green; no cap on rounds; never skip/loosen a test; then write "Current state" and stop).
