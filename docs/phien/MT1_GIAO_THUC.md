# MT1 automation protocol (1 team: lead + coder + checker)

> Source of work: `docs/phien/claude__mt1-bo-muc-tieu.md` (goal, goal cards, UI contract, Plan = lots L1–L5, acceptance,
> gotchas). Modelled on `docs/phien/XP1_GIAO_THUC.md`. Truong asked for this workflow (CLAUDE.md rule 12), which
> satisfies rule 10 for these three sessions only. Message formats, quiet test command, messaging/silence: use
> `docs/phien/GT_GIAO_THUC.md` §7, §8 with "writer" = coder, "GT<k>" = "MT1". Where they differ, THIS file wins.

## 0. Decisions already made (do not ask Truong again)
- Item code MT (outside the registry), lot MT1, approved by Truong 2026-11-20.
- The THREE goal cards, their rule patches and the UI contract (1–7) in the branch file are fixed (rev. 2,
  Truong 2026-11-20: "đồng bộ, tuyệt đối không phức tạp, tối giản thao tác"). Wording may be polished.
- When a UI choice is unclear: fewer clicks and fewer words win; reuse an existing component before adding one.
- No new library. No new choice function. No change to the CSV contract. Schema: none expected (config JSON key
  only); if a table/column turns out necessary → "Needs Truong", do not add it.
- Fable no longer exists (Truong 2026-11-20); research questions go to the lead.

## 1. Branch, lots
| Branch | Lots | Branch file |
|---|---|---|
| `claude/mt1-bo-muc-tieu` (already created by the planning session) | L1 catalogue → L2 API → L3 estimate + result → L4 UI → L5 docs/review | `docs/phien/claude__mt1-bo-muc-tieu.md` |

- Each lot's spec and tests = its box in the branch file's Plan; "Done when" = box + Acceptance.
- Before each lot and before the CI gate: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase
  or force-push.
- New i18n keys prefix `mt1_`; new error codes `mt_*` appended at the END of `i18n_errors.py`, then
  `python tao_i18n_js.py`. New audit labels `nkhd_<function>` (vi + en) for every new `phan_quyen.QUYEN` entry.

## 2. Roles and session limit
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | creates the branch, updates the branch file (Status, Sessions, Needs Truong), creates EXACTLY two child sessions, runs the loop, CI gate, final review | writes product code |
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | marks own lot passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews one lot diff, runs related tests + own edge cases, writes verdict | edits product code or tests |

- **Exactly 3 sessions for the whole job. No extra sessions, no Agent tool.** Context is summarised automatically;
  this overrides the "stop at 400k" part of CLAUDE.md rule 9. Keep "Current state" and your `__<vai>.md` current.
- Never ask Truong. Blocked part (invariant conflict, new library, schema change, change outside MT1, manual Windows
  check, L1 `trai_nghiem` claim false) → one line under "Needs Truong", continue with the next unblocked lot.

## 3. Loop per lot (L1 → L5)
1. lead → coder `GO L<n>`.
2. coder: failing test from the lot's box → minimal code → related tests only (UI tests: `pip install playwright`
   matching the preinstalled browser, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) → invariant 1:
   `git fetch origin main` then `.claude/skills/soat-ma/scripts/kiem_nhanh.py --so-seed 20` 7/7 incl. `trung_khit`
   → `soat-ma` four tiers → CHANGELOG + TIEN_DO row `MT1-L<n>` → commit `MT1-L<n>: …` → push →
   `CODER DONE L<n> | base <sha> head <sha>`.
3. lead → checker `REVIEW L<n> <base>..<head>`.
4. checker: verdict in `docs/phien/claude__mt1-bo-muc-tieu__checker.md` (push only that file) → `CHECKER REPORT L<n>`.
   Checks: the lot's box; invariants 1, 2, 4, 5, 6, 7, 8; card patches only use existing rule keys and never `wharton`/`fa_daa`; `muc_tieu`
   never reaches `run_history.luat_xep` or the fingerprint; seat formula reads only the student list; estimate and
   result write nothing and suppress counts 1–4; teacher role cannot call write functions (backend); for L4 every
   line of the UI contract, counting clicks yourself in Chromium; 2–3 own edge cases (no official run yet,
   multi-session, medal mode on, no group column, several groups, capacity 1, club with another reserve group,
   Undo after Undo, manual edit after a card).
5. Bugs → `FIX L<n>` → coder → checker again (max 3 rounds, then "Needs Truong" and move on). NO BUGS → lead ticks
   the lot in the branch file and pushes.
- Push a lot only after CI of the previous push has finished or been read.

## 4. CI gate (after L5; repeat until green)
Lead reads GitHub Actions `tests.yml` and `Build Windows executable (rbda-kiosk)` for the head commit
(`mcp__github__actions_list`, `mcp__github__get_job_logs` with `failed_only`, loaded via ToolSearch); waits with
`send_later` 30 min, never a polling loop. Red → short FIX list → coder → checker → push → again. A test may never be
skipped, disabled or weakened. Green (lint + all shards + coverage ≥ 85 % + Windows build) →
`Status: DONE <sha> CI green <date>` in the branch file.

## 5. Final review by the lead (school's point of view)
On simulated data (`du_lieu_test/SO_NHAP_MAU_120HS_3BUOI.xlsx`, `SO_NHAP_DQT_800HS_HOP_LE.xlsx`, seed 3), in Chromium
as admin, act as a principal in a 30-minute meeting: pick each card, read the estimate, Undo, apply, run, read the
result line. Measure clicks from "open Settings" to "goal applied" (target 1, max 2) and whether every sentence on
screen is understandable without training; compare the Settings panel before/after (no new page, same look). Write `docs/ke_hoach/mt/MT1_DANH_GIA.md` (≤ 60 lines,
Vietnamese, no technical words): targets met/missed with numbers, top problems with one screenshot each,
recommendations for MT2/MT3. Push. No report conclusions for the student's science report.

## 6. Handoff files (short; Truong reads them)
Branch file ≤ 150 lines: Status line, Plan (lots ticked), Current state (3 lines), Sessions, Needs Truong (1 line each
+ recommendation), Final summary in Vietnamese without technical words (≤ 10 lines: done/skipped, CI link, review
file, what Truong should try by hand in 3 steps, incl. the Windows exe). `__coder.md` / `__checker.md` ≤ 30 lines.

## 7. Prompts (lead uses the child prompts verbatim; replace <LEAD_ID>)
**Lead** (Truong pastes this into a new Opus session):
```
You are LEAD for MT1 on branch claude/mt1-bo-muc-tieu (it already exists on origin; check it out).
Read CLAUDE.md, then docs/phien/MT1_GIAO_THUC.md and
docs/phien/claude__mt1-bo-muc-tieu.md and follow them exactly. Fill the Status line, Sessions table and "Needs
Truong" list in the branch file, push, then create the CODER and CHECKER sessions with the protocol §7 prompts
(repo https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV, source_revision claude/mt1-bo-muc-tieu, models
from §2, permission_mode auto) and run §3 for L1 to L5, then §4 until CI is green, then §5. Never wait for Truong;
anything that needs him goes on the list.
```
**Coder:**
```
You are CODER for MT1 on branch claude/mt1-bo-muc-tieu. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/MT1_GIAO_THUC.md and docs/phien/claude__mt1-bo-muc-tieu.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO L<n>" or "FIX" and follow protocol §3 step 2. Never ask Truong; blocked
parts go under "Needs Truong". Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for MT1 on branch claude/mt1-bo-muc-tieu. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/MT1_GIAO_THUC.md and docs/phien/claude__mt1-bo-muc-tieu.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and follow
protocol §3 step 4. Never edit product code or tests; only docs/phien/claude__mt1-bo-muc-tieu__checker.md. Report in
GT_GIAO_THUC §7 format.
```
