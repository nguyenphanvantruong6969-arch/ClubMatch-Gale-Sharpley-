# Branch handoff: claude/dk5-dien-tap

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/DK5_GIAO_THUC.md` (size M: coder + checker, no lead). Loop context: `docs/phien/DK3_DK4_VONG_TU_DONG.md`.

Status: NOT STARTED

## Feature / goal
DK5 = full rehearsal ("diễn tập") of the registration-to-allocation flow on SIMULATED data (798 students, 40 clubs),
driven ONLY through the DK3 (`api_dang_ky`) and DK4 (`dang_ky_sang_xep`) APIs, plus one Playwright smoke test for the
three paths (admin, teacher, student). It proves invariants 4 and 5 under realistic load; it adds NO product feature.
Base: DK4 branch `claude/dk4-noi-thang-bo-xep` after PASS. All data labelled `MÔ PHỎNG`.

## Preconditions (coder checks first; stop and write "Needs Truong" if false)
- `api_dang_ky.py` and `dang_ky_sang_xep.py` exist on this branch (`ls`). If missing: `git fetch origin
  claude/dk4-noi-thang-bo-xep && git merge --no-edit FETCH_HEAD`. If that branch does not exist yet, STOP.
- Function names in DK3/DK4 are unknown to this plan: find them by `grep -n "^def " api_dang_ky.py dang_ky_sang_xep.py`.
  Never edit those two files; a bug found there goes under "Needs Truong" (+ a failing test marked `xfail(strict)` is NOT
  allowed: report instead).

## Plan (written by Opus; ticked by Sonnet)
- [ ] L1 (must) `du_lieu_test/dien_tap_dk5.py` + `tests/test_dk5_dien_tap.py`: seeded generator (seed fixed, crc32 not
  `hash()`), 798 students / 40 clubs; scenario through the API only: setup → teachers sign up/are created → admin
  approves → students submit INTERLEAVED (round-robin over ≥ 4 simulated kiosks) → scores entered → "Chốt và xếp" →
  export. Asserts: every call `{ok:true, errors:[]}`; one `match_results` row per student; `run_history` +1;
  time per phase logged (budget: whole scenario < 120 s on CI; log, do not fail on a slower laptop).
  **→ MILESTONE 1**
- [ ] L2 (must) robustness, same test file or `tests/test_dk5_vung_chiu_loi.py`:
  (a) backup → restore → `match_results` identical to before (every row);
  (b) idle lock: lock engages after the idle limit (inject the clock, never `sleep`);
  (c) deadline auto-close: submission after the deadline is refused with a clear error code;
  (d) re-submit by the same student keeps ONLY the last submission (no duplicate rows, last ranking wins);
  (e) injected exception mid-"Chốt và xếp" (monkeypatch inside the write transaction) → rollback: DB byte-identical
      to before (hash of all tables), `run_history` unchanged, STB seed not consumed/locked by the failed run;
  (f) invariant 4: a second successful run appends a row; nothing in `run_history` is updated or deleted.
- [ ] L3 (must) `tests/test_giao_dien_dk5_toan_trinh.py`: ONE Playwright file, one shared page fixture, three paths on a
  SMALL dataset (≤ 30 students; 798 is for L1): admin (setup → approve → "Chốt và xếp" → result), teacher (sign up →
  sees own club), student (kiosk → ranks → submit → "Đã gửi lúc …"). `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
  **→ MILESTONE 2** (L2 + L3)
- [ ] L4 (optional, may drop) `docs/phien/DK5_BAO_CAO.md` ≤ 40 lines: numbers (time per phase, rows, runs), what failed.
  No report conclusions for the student's science report (academic integrity).

## Acceptance (`kiem_nhan`, taken from the task)
- Each student has exactly one result row; `run_history` grows by exactly 1 per successful run.
- Backup then restore returns the same results; lock when idle; auto-close at deadline; last submission kept;
  mid-run error → full rollback (invariants 4 and 5).
- Playwright covers admin, teacher, student paths. Checker re-runs the DK3 AND DK4 test files as well.
- Default behaviour unchanged (invariant 1): DK5 adds only new files; `git diff --stat origin/<base>` shows no product file.

## Decisions and gotchas
- New files only (no product code). If a product change looks necessary → "Needs Truong", do not edit.
- Invariant 3: locked seed ⇒ same numbers; the generator must be reproducible (same seed ⇒ same JSON bytes).
- Full suite is NOT run locally (CI does, ~22 min). Token rules: `_GIAO_THUC_GON.md` §3.

## Current state (overwrite)
- Done so far: nothing.

## Needs Truong (one line each + recommendation)
- (none)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
