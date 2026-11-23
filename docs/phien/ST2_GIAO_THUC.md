# ST2 protocol — round 2 stress test: try to CRASH the program (after SF is merged and green)

> Truong (2026-11-23): after all SF fixes land and CI is green, stress further; crashing the program is encouraged.
> Same rules as `ST_GIAO_THUC.md` §0, §1, §3 (report only, never edit production code, `xfail(strict)`, no new
> library, simulated data) unless this file says otherwise. Ids `ST2-A-NNN` / `ST2-B-NNN`; reports
> `docs/phien/ST2_BAO_CAO_<A|B>.md`; tests in `tests_stress2/<a|b>/`. Two Sonnet sessions, no lead, no Agent tool.

## 0. Gate (check first; if it fails, write one line in your handoff file and STOP)
- `origin/claude/happy-cerf-xvn495` contains the merged PR "SF: fix stress-test bugs" and its CI run is green.
- Create your branch from it: `git checkout -b claude/happy-cerf-xvn495-st2-<a|b> origin/claude/happy-cerf-xvn495`,
  push, handoff file `docs/phien/claude__happy-cerf-xvn495-st2-<a|b>.md` from `_TEMPLATE.md`.
- Every ST/SF stress test still passes on that head (`pytest -q tests_stress`); a regression = first bug of ST2.

## 1. What counts as a crash (oracle after EVERY step, not only at the end)
Uncaught exception or traceback reaching the user; process exit / hang > 30 s; reply not `{ok,data,errors}`;
error code missing in vi or en; `PRAGMA integrity_check` ≠ ok; `run_history` lost a row; latest `match_results`
not stable (`verify_stability`) or over capacity; invariant 1–8 broken; data silently lost; UI console error,
unhandled rejection, blank screen, stuck spinner, or a button that never re-enables. S1 = data loss / wrong
allocation / security; S2 = crash / hang / unrecoverable without a developer.

## 2. Lots (4 each; commit + push after each)
**ST2-A — process, disk, DB, scale chaos** (drive the real API in a SUBPROCESS so you can kill it)
- A1 Kill -9 at random points (≥ 200 seeded kills) during `run_pipeline`, `import_so_nhap`, backup, export,
  `di_tru_schema`, workspace import; reopen → integrity ok, either the old or the new state (never half), backups
  usable, `recovery.py` restores. Also truncate / delete the `-journal` / `-wal` file between kill and reopen.
- A2 Resource starvation via `resource.setrlimit` in the child: RLIMIT_FSIZE (disk full at 1 KB…50 MB),
  RLIMIT_NOFILE (16 fds), RLIMIT_AS (memory 200 MB), read-only workspace dir, permission-denied export folder,
  paths with Unicode / spaces / 300 chars / symlinks, `TZ` and clock jumps (time moves backwards between runs).
- A3 Seeded state-machine fuzz: ≥ 20 sequences × 300 random public API calls (import, edit, delete, late arrival,
  withdraw, mode switch, medals, accounts, kiosk enter/exit, run, export, restore), oracle §1 after each call;
  shrink every failure to the shortest sequence that still fails and save it as the repro test.
- A4 Extreme sizes and pathologies: 20 000 students × 500 clubs × 7 sessions; everyone ranks the same club;
  all scores tied; capacity 1 everywhere; 1 000 consecutive runs (DB size, memory, time per run, `run_history`
  paging); two processes on the same workspace at once (multi-instance kiosk). Report numbers (simulated).
**ST2-B — UI and local HTTP host chaos** (`browser_host.py` + Chromium)
- B1 HTTP fuzz on `browser_host.py`: malformed / truncated JSON, wrong or missing token, bad Host header, huge or
  lying Content-Length, 100 MB body, slow-loris, 200 parallel requests, path traversal on static files,
  unknown method names; the server must stay up and answer the next good request.
- B2 Monkey test: seeded random clicks / typing / file drops / key presses on every screen, ≥ 20 seeds × 2 000
  actions, oracle §1 in the browser after each action; save each failing seed + shortest action list.
- B3 Backend dies under the UI: kill the host mid-run, mid-import, mid-export; restart it; reload; double-start;
  network delay 3 s on every call; `localStorage` throwing; two tabs on the same workspace editing at once.
- B4 Long session: 2 h soak (or the longest your budget allows) of realistic admin use with memory and DOM-node
  counts sampled every 5 min; vi ↔ en and 390/768/1366 px mixed in; final check that every result shown equals DB.

## 3. End
Summary table at the top of each report; then the next Opus session triages ST2 into a new fix round (same SF
loop: `SF_GIAO_THUC.md` §2–§5 with "ST" → "ST2").
