# UX2 automation protocol (1 team: lead + coder + checker)

> Source of work: `docs/phien/claude__ux2-phan-hoi-nut.md` (goal, decisions, Plan = lots L1–L9, acceptance,
> gotchas). Truong asked for these sessions explicitly (CLAUDE.md rule 10 satisfied). Base: `origin/claude/ux2-phan-hoi-nut`
> (branched from `origin/main` @ `30cd849`). Mechanics not repeated here (message formats, quiet test command,
> messaging/silence): use `docs/phien/GT_GIAO_THUC.md` §7, §8 with "writer" = coder, "GT<k>" = "UX2".
> Where they differ, THIS file wins. Modelled on `XP1_GIAO_THUC.md`.

## 0. Decisions already made (do not ask Truong again)
- UI only: `style.css`, `js/*.js`, `index.html`, `i18n.js`; `i18n_errors.py` only for a truly new error code (append
  at END, then `python tao_i18n_js.py`). NO new library, NO `alert()`/`confirm()`, NO change to `api*.py` return
  shapes, algorithm, CSV, schema (invariants 1, 6, 7). Anything else → "Needs Truong".
- #2 and #13 share ONE helper (`datNutBan`, used by existing `chayNut` / `khiBan`). Do not create a second lock.
- Every new motion respects BOTH `prefers-reduced-motion: reduce` and `html.tat-hieu-ung`; meaning never depends on
  motion (text + ARIA carry it).
- #11 progress is display-only (no backend streaming). Live progress = future item, list under "Needs Truong" only
  if the final review shows users think the app froze.
- i18n prefix `ux2_` (vi + en, `test_i18n_sync.py`); CSS block `/* UX2 */`; tests `tests/test_ux2_*.py`,
  `tests/test_giao_dien_ux2_*.py`.

## 1. Branch, lots
| Branch | Lots (dependency order) | Branch file |
|---|---|---|
| `claude/ux2-phan-hoi-nut` | L1 #2+#13 → L2 #3 → L3 #8 #9 #1 → L4 #7 → L5 #11 → L6 #12 → L7 #6 → L8 #10 → L9 docs/verify | `docs/phien/claude__ux2-phan-hoi-nut.md` |

- Why this order: L1 builds the busy helper that L2 (✓ on the same button) and L5 (btnRun) reuse; L3 decides who
  owns `::before/::after` on buttons before later lots add more CSS; L4–L8 are independent and ranked by user value
  (errors > progress > empty states > skeleton > decoration). L5–L8 may be dropped one by one (fallback §5).
- Each lot's spec/tests = its block in the branch file's Plan; "Done when" = ticked boxes + Acceptance.
- Stay current: before each lot and before the CI gate `git fetch origin main && git merge --no-edit FETCH_HEAD`.
  Never rebase or force-push.

## 2. Roles and session limit
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | updates the branch file (Status, Sessions, Needs Truong), creates EXACTLY two child sessions (coder, checker), runs the loop, CI gate, final user review | writes product code |
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | marks own lot passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews one lot diff, runs related tests + own edge cases, writes verdict | edits product code or tests |

- **Exactly 3 sessions for the whole job. No replacement or extra sessions, no Agent tool.** Context is summarised
  automatically; this overrides the "stop at 400k" part of CLAUDE.md rule 9. Keep the branch file's "Current
  state" and your own `__<vai>.md` up to date after every message you send.
- Never ask Truong. Blocked part → one line under "Needs Truong" in the branch file, continue.

## 3. Loop per lot (L1 → L9)
1. lead → coder `GO L<n>`.
2. coder: failing test from the lot's boxes → minimal code → related tests (quiet; UI tests need `pip install
   playwright` matching the preinstalled browser, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) → invariant 1:
   `git fetch origin main` then `.claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20`
   must be 7/7 (incl. `trung_khit`) → `soat-ma` four tiers → CHANGELOG + TIEN_DO row `UX2-L<n>` → commit
   `UX2-L<n>: …` → push → `CODER DONE L<n> | base <sha> head <sha>`.
3. lead → checker `REVIEW L<n> <base>..<head>`.
4. checker: verdict in `docs/phien/claude__ux2-phan-hoi-nut__checker.md` (push only that file) →
   `CHECKER REPORT L<n>`. Checks: the lot's boxes; invariants 1, 5, 6, 7 (diff touches no backend shape, CSV,
   schema); `git diff --stat` stays inside §0 files; both motion switches; keyboard-only path; vi AND en text fits
   the button (en labels longer); `giao_vien` role sees no admin action; 2–3 own edge cases (API rejects, language
   switch while busy, double Enter key, button with icon, 0 rows, 800 rows `SO_NHAP_DQT_800HS_HOP_LE.xlsx`).
5. Bugs → `FIX L<n>` → coder → checker again (max 3 rounds, then §5 fallback + "Needs Truong", move on).
   NO BUGS → lead ticks the lot in the branch file and pushes.
- Push a lot only after CI of the previous push has finished or been read.

## 4. Risks
| Risk | Lot | Mitigation |
|---|---|---|
| `chayNut` swaps `textContent` → icon children lost, width jumps | L1 | save/restore child nodes; lock `minWidth`; test ≤ 1 px |
| `tat-hieu-ung` `animation:none !important` freezes spinner | L1 | accepted; label "Đang xếp…" + `aria-busy` carry meaning; test |
| Old tests assert "Đang chạy…" / exact button text | L1, L2 | update deliberately, list each file in CHANGELOG; never weaken |
| 44 px makes dense tables taller | L3 | compact buttons grow hit area only (transparent pseudo / padding) |
| `::before/::after` already used (toast-close ×, 6 `::after`) | L3 | grep first; state layer via inset `box-shadow` where taken |
| Focus ring low contrast on gold buttons | L3 | 3:1 test on `--paper` and `--gold` |
| Error→input map drifts from backend codes | L4 | map lives next to the form; unknown code → toast (never silent) |
| Progress implies live tracking it does not have | L5 | indeterminate during run; static test ties map to `api.py` step names |
| Skeleton flicker on fast loads | L7 | 300 ms delay; MutationObserver test |
| `::details-content` / `interpolate-size` unsupported in an old WebView2 | L8 | `@supports`; fallback = instant open |
| CI time grows (Chromium) | all | ≤ 8 tests per file, one page fixture per file |
| Screenshot docs drift | L9 | re-shoot only once, in L9 |

## 5. Fallback
- A lot that fails 3 FIX rounds: coder `git revert` its commits (no force-push), lead writes one line under "Needs
  Truong" (what failed, recommendation), continue with the next lot. L1–L4 are the must-ship core; if L1 cannot
  pass, STOP the job (L2, L5 depend on it) and report.
- A lot that breaks a related old test in a way that needs a behaviour decision → keep old behaviour, list it.
- Kill switch for users: all decorative motion (L7 shimmer, L8) is already off via the "Hiệu ứng" button.

## 6. CI gate (after L9; repeat until green)
Lead reads GitHub Actions `tests.yml` and `Build Windows executable (rbda-kiosk)` for the head commit
(`mcp__github__actions_list`, `mcp__github__get_job_logs` with `failed_only`, load via ToolSearch); waits with
`send_later` 30 min, never a polling loop. Red → short FIX list → coder → checker → push → again. A test may never be
skipped, disabled or weakened. Green (lint + all shards + coverage ≥ 85 % + Windows build) →
`Status: DONE <sha> CI green <date>` in the branch file.

## 7. Final review by the lead (user's point of view)
On `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx` (and 800 HS for skeleton/rows), Chromium, as admin and `giao_vien`:
click every main action once with mouse and once with keyboard; measure click→`aria-busy` latency, ✓ duration,
smallest hit area, first-invalid focus; toggle "Hiệu ứng" off and `reducedMotion: reduce` and repeat. Write
`docs/ke_hoach/ux/UX2_DANH_GIA.md` (≤ 60 lines, Vietnamese): per item met/missed with numbers, top problems with
one screenshot each, recommendations. Push. No report conclusions for the student's science report.

## 8. Handoff files (short; Truong reads them)
Branch file ≤ 150 lines: Status line, Plan (lots ticked), Current state (3 lines), Sessions table, Needs Truong
(1 line each + recommendation), Final summary in Vietnamese (≤ 10 lines: done/skipped, CI link, review file, what
Truong should try by hand in 3 steps, incl. the Windows exe). `__coder.md` / `__checker.md` ≤ 30 lines each.

## 9. Prompts (lead uses the child prompts verbatim; replace <LEAD_ID>)
**Lead** (Truong pastes this into a new Opus session):
```
You are LEAD for UX2 on branch claude/ux2-phan-hoi-nut. Read CLAUDE.md, then docs/phien/UX2_GIAO_THUC.md and
docs/phien/claude__ux2-phan-hoi-nut.md (both on origin/claude/ux2-phan-hoi-nut) and follow them exactly. Add a
Sessions table and a "Needs Truong" list to the branch file, push, then create the CODER and CHECKER sessions with
the protocol §9 prompts (repo https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV, source_revision
claude/ux2-phan-hoi-nut, models from §2, permission_mode auto) and run §3 for L1 to L9, then §6 until CI is green,
then §7. Never wait for Truong; anything that needs him goes on the list.
```
**Coder:**
```
You are CODER for UX2 on branch claude/ux2-phan-hoi-nut. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX2_GIAO_THUC.md and docs/phien/claude__ux2-phan-hoi-nut.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO L<n>" or "FIX" and follow protocol §3 step 2. Locate code by FUNCTION
NAME (chayNut, khiBan, capNhatKhoaVanHanh, chayXuat, showToast). UI files only (§0). Never ask Truong; blocked
parts go under "Needs Truong". Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for UX2 on branch claude/ux2-phan-hoi-nut. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX2_GIAO_THUC.md and docs/phien/claude__ux2-phan-hoi-nut.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and follow
protocol §3 step 4. Never edit product code or tests; only docs/phien/claude__ux2-phan-hoi-nut__checker.md.
Report in GT_GIAO_THUC §7 format.
```

## 10. Lean mode for the rest of UX2 (Truong, 2026-11-21) — WINS over §6, §7
Reason: the job hit a usage limit (L1–L9 = 17 checker reports, ~38 fix commits). From now on:
- CI gate: read only failed jobs (`get_job_logs` `failed_only`, last ≤ 60 lines). Max **2** FIX rounds per red run,
  then "Needs Truong". Wait with `send_later` 30 min; between waits send NO status messages.
- Messages between sessions: one line (`CODER DONE CI-<k> | base <sha> head <sha>`); details live in the
  `__coder.md` / `__checker.md` files, never pasted into a message.
- Final review (replaces §7): ONE Playwright script, ONE pass, admin + one `giao_vien` check, measure only
  click→`aria-busy` latency, ✓ duration, smallest hit area, first-invalid focus, both motion switches. No 800 HS
  run (checker L8 already measured it). ≤ 3 screenshots. `UX2_DANH_GIA.md` ≤ 30 lines.
- When CI is green and the review is pushed: archive coder and checker at once, set `Status: DONE`, stop.
- If the usage limit is near at any point: finish the current commit, update "Current state", stop. A new lead
  continues next day from the branch file (rule 9 handoff applies again; ignore the "no replacement" line of §2).
