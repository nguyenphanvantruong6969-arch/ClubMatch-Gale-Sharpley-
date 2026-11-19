# XP1 automation protocol (1 team: lead + coder + checker)

> Source of work: `docs/phien/claude__xp1-xuat-pdf.md` (goal, decisions, Plan = lots L1–L5, acceptance, gotchas).
> Truong asked for these sessions explicitly (CLAUDE.md rule 10 satisfied). Base: `origin/claude/xp1-xuat-pdf`
> (branched from `claude/ux1-a-giao-dien` @ `66f9ffb`). Mechanics not repeated here (message formats, quiet test
> command, messaging/silence): use `docs/phien/GT_GIAO_THUC.md` §7, §8 with "writer" = coder, "GT<k>" = "XP1".
> Where they differ, THIS file wins.

## 0. Decisions already made (do not ask Truong again)
- PDF engine = `reportlab` (new runtime dependency, APPROVED 2026-11-18) + bundled Be Vietnam Pro `.ttf` (SIL OFL)
  with its licence file. This is the ONE allowed new library; anything else → "Needs Truong".
- Outputs: member lists per club / per class (PDF, folder of files), explanation slips per class (PDF, folder or one
  class), club type (Tự do / Giới hạn / Tuyển chọn, `clubs.loai`) on every slip row. HTML slip export stays.
- Overlap with UX1 team B (`claude/ux1-b-phieu`, NOT STARTED): XP1 replaces UX1B **L6** (slip "In / Lưu PDF" via
  print dialog) and the **club type** part of **L7**. Do not build those again; note it in the branch file.

## 1. Branch, lots
| Branch | Lots | Branch file |
|---|---|---|
| `claude/xp1-xuat-pdf` | L1 PDF core → L2 slips PDF by class + club type → L3 member lists PDF → L4 UI/permissions/i18n → L5 docs/packaging/verify | `docs/phien/claude__xp1-xuat-pdf.md` |

- Each lot's spec and tests = its block in the branch file's Plan; "Done when" = the ticked boxes + Acceptance.
- Stay current: before each lot and before the CI gate run
  `git fetch origin claude/ux1-a-giao-dien && git merge --no-edit FETCH_HEAD` (UX1A may still get fixes).
  If UX1A has been merged to main, merge `origin/main` instead. Never rebase or force-push.
- New i18n keys use prefix `xp1_`; new error codes appended at the END of `i18n_errors.py`, then
  `python tao_i18n_js.py`. New audit labels `nkhd_<function>` (vi + en) for every new `phan_quyen.QUYEN` entry.

## 2. Roles and session limit
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | updates the branch file (Status, Sessions, Needs Truong), creates EXACTLY two child sessions (coder, checker), runs the loop, CI gate, final user review | writes product code |
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | marks own lot passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews one lot diff, runs related tests + own edge cases, writes verdict | edits product code or tests |

- **Exactly 3 sessions for the whole job. No replacement or extra sessions, no Agent tool.** Context is summarised
  automatically; this overrides the "stop at 400k" part of CLAUDE.md rule 9. Keep the branch file's "Current
  state" and your own `__<vai>.md` up to date after every message you send.
- Never ask Truong. Blocked part (invariant conflict, second new library, change outside XP1, manual Windows check)
  → one line under "Needs Truong" in the branch file, continue.

## 3. Loop per lot (L1 → L5)
1. lead → coder `GO L<n>`.
2. coder: failing test from the lot's boxes → minimal code → related tests (quiet; UI tests need
   `pip install playwright` matching the preinstalled browser, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) →
   invariant 1: `git fetch origin main` then `.claude/skills/soat-ma/scripts/kiem_nhanh.py` must be 7/7 (incl.
   `trung_khit`) → `soat-ma` four tiers → CHANGELOG + TIEN_DO row `XP1-L<n>` → commit `XP1-L<n>: …` → push →
   `CODER DONE L<n> | base <sha> head <sha>`.
3. lead → checker `REVIEW L<n> <base>..<head>`.
4. checker: verdict in `docs/phien/claude__xp1-xuat-pdf__checker.md` (push only that file) → `CHECKER REPORT L<n>`.
   Checks: the lot's boxes; invariants 1, 2, 4, 5, 6; privacy (a slip shows only its own student; member lists no
   scores/lottery numbers); teacher role cannot call new exports (backend); Vietnamese diacritics readable in the
   PDF; 2–3 own edge cases (no run yet, student without class, multi-session, FA on/off, 0 students in a class,
   club name with `/` or diacritics as file name).
5. Bugs → `FIX L<n>` → coder → checker again (max 3 rounds, then "Needs Truong" and move on). NO BUGS → lead ticks
   the lot in the branch file and pushes.
- Push a lot only after CI of the previous push has finished or been read (two cancelled runs hid a bug on UX1A).

## 4. CI gate (after L5; repeat until green)
Lead reads GitHub Actions `tests.yml` and `Build Windows executable (rbda-kiosk)` for the head commit
(`mcp__github__actions_list`, `mcp__github__get_job_logs` with `failed_only`, load via ToolSearch); waits with
`send_later` 30 min, never a polling loop. Red → short FIX list → coder → checker → push → again. A test may never
be skipped, disabled or weakened. Green (lint + all shards + coverage ≥ 85 % + Windows build) →
`Status: DONE <sha> CI green <date>` in the branch file.

## 5. Final review by the lead (user's point of view)
On simulated data (`du_lieu_test/SO_NHAP_MAU_120HS_3BUOI.xlsx`, `SO_NHAP_FA_MAU_120HS.xlsx`, seed 3) run the app in
Chromium as admin: export member lists per club, per class, slips per class; open each PDF and read it as a homeroom
teacher (diacritics, page breaks, club type, no other students' data, file names). Measure: clicks per export, time
for 800 students (`SO_NHAP_DQT_800HS_HOP_LE.xlsx`). Write `docs/ke_hoach/xp/XP1_DANH_GIA.md` (≤ 60 lines,
Vietnamese): targets met/missed with numbers, top problems with one screenshot of a PDF page each, recommendations.
Push. No report conclusions for the student's science report (academic integrity).

## 6. Handoff files (short; Truong reads them)
Branch file ≤ 150 lines: Status line, Plan (lots ticked), Current state (3 lines), Sessions table, Needs Truong
(1 line each + recommendation), Final summary in Vietnamese (≤ 10 lines: done/skipped, CI link, review file, what
Truong should try by hand in 3 steps, incl. the Windows exe). `__coder.md` / `__checker.md` ≤ 30 lines each.

## 7. Prompts (lead uses the child prompts verbatim; replace <LEAD_ID>)
**Lead** (Truong pastes this into a new Opus session):
```
You are LEAD for XP1 on branch claude/xp1-xuat-pdf. Read CLAUDE.md, then docs/phien/XP1_GIAO_THUC.md and
docs/phien/claude__xp1-xuat-pdf.md (both on origin/claude/xp1-xuat-pdf) and follow them exactly. Add a Status
line, a Sessions table and a "Needs Truong" list to the branch file, push, then create the CODER and CHECKER
sessions with the protocol §7 prompts (repo https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV,
source_revision claude/xp1-xuat-pdf, models from §2, permission_mode auto) and run §3 for L1 to L5, then §4 until
CI is green, then §5. Never wait for Truong; anything that needs him goes on the list.
```
**Coder:**
```
You are CODER for XP1 on branch claude/xp1-xuat-pdf. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/XP1_GIAO_THUC.md and docs/phien/claude__xp1-xuat-pdf.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO L<n>" or "FIX" and follow protocol §3 step 2. Never ask Truong; blocked
parts go under "Needs Truong". Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for XP1 on branch claude/xp1-xuat-pdf. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/XP1_GIAO_THUC.md and docs/phien/claude__xp1-xuat-pdf.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and follow
protocol §3 step 4. Never edit product code or tests; only docs/phien/claude__xp1-xuat-pdf__checker.md. Report in
GT_GIAO_THUC §7 format.
```
