# A5 protocol — equal-rank priority groups (size L: lead + coder + checker)

> Work source: `docs/phien/claude__a5-nhom-dong-hang.md` (goal, decisions, Plan L1–L4, acceptance, gotchas).
> Truong asked for these sessions (CLAUDE.md rule 10). Budget/mechanics: `_GIAO_THUC_GON.md` (do not copy);
> message formats: `GT_GIAO_THUC.md` §7, §8 with "writer" = coder, "GT<k>" = "A5". Where they differ, THIS wins.

## 0. Decisions already made (do not ask Truong again)
- Invariant 7 exception (2026-11-22): `clubs.reserve_group` and `rules.tiers` entries may hold `a|b`; no new
  column, no schema change, CSV / Sổ nhập column names unchanged. Student keeps ONE label; `|` there = error.
- D1 = POOLED reserve (no `club_choice_function` change). "Equal share" out of scope. FA-DAA untouched.
- No new library. Anything outside A5 / invariant conflict → one line under "Needs Truong", continue.

## 1. Branch, lots
| Branch | Lots (all must-ship) | Branch file |
|---|---|---|
| `claude/a5-nhom-dong-hang` | L1 core → L2 backend → L3 UI → L4 docs | `docs/phien/claude__a5-nhom-dong-hang.md` |
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push.
- New error codes appended at END of `i18n_errors.py` (prefix `a5_`), then `python tao_i18n_js.py`; UI keys `a5_`.

## 2. Roles (exactly 3 sessions, no Agent tool, no replacements)
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Sonnet `claude-sonnet-5-5` | branch file (Status, Sessions, Needs Truong), creates coder + checker, loop, CI gate, final check | product code |
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | marks own lot passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews one lot diff, runs related tests + own edge cases, verdict | edits product code/tests |
- Budget rules `_GIAO_THUC_GON.md` §3 apply to all. Near the usage limit: update "Current state", stop.

## 3. Loop per lot
1. lead → coder `GO L<n>`.
2. coder: failing tests from the lot's boxes → minimal code → lot test file + ≤ 3 related (`-q --tb=line | tail -15`)
   → `git fetch origin main` → `.claude/skills/soat-ma/scripts/kiem_nhanh.py --so-seed 20 | tail -10` (all OK,
   incl. `trung_khit`; L3/L4 may use default seeds) → `soat-ma` four tiers → CHANGELOG + TIEN_DO row `A5-L<n>`
   → commit `A5-L<n>: …` → push → `CODER DONE L<n> | base <sha> head <sha>`.
3. lead → checker `REVIEW L<n> <base>..<head>`.
4. checker: verdict in `docs/phien/claude__a5-nhom-dong-hang__checker.md` (push only that file) →
   `CHECKER REPORT L<n>`. Checks: lot boxes; invariants 1, 2, 5, 6, 7 (only the approved exception), 8;
   no `LIKE` on labels; single-label paths unchanged in code (old `==` branch kept); edge cases (≥ 3 of):
   `"a||b"`, `" A | a "`, label `chinh_sach` vs `chinh|sach`, club `a|b` with reserve 0, tiers `a|b` + `b`,
   Excel NBSP in a tier, empty DB, FA on.
5. Bugs → `FIX L<n>` → coder → checker (max 2 rounds; then "Needs Truong" + `git revert` of the lot, move on).
   NO BUGS → lead ticks the lot and pushes. Push next lot only after CI of the previous push was read.

## 4. CI gate (after L4; repeat until green)
Lead reads `tests.yml` and `Build Windows executable (rbda-kiosk)` for the head commit (`mcp__github__actions_list`,
`mcp__github__get_job_logs` `failed_only`, ≤ 60 lines; load via ToolSearch); wait with `send_later` 30 min, never
poll. Red → FIX → coder → checker → push. Never skip/weaken a test. Green → `Status: DONE <sha> CI green <date>`.

## 5. Final check by the lead (≤ 3 screenshots, scale 1)
Simulated data `du_lieu_test/SO_NHAP_MAU_120HS_3BUOI.xlsx`, seed 3, in Chromium as admin: (a) set two student
labels + one club `a|b` with reserve seats, run, confirm both labels fill the pool by score; (b) strict tiers
`a|b` then `c`, confirm order; (c) type a label in two lines → error. Write ≤ 10-line Vietnamese summary in the
branch file (done/skipped, CI link, 3 steps Truong tries by hand incl. Windows exe). No report conclusions.

## 6. Prompts (lead uses child prompts verbatim; replace <LEAD_ID>)
**Coder:**
```
You are CODER for A5 on branch claude/a5-nhom-dong-hang. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/A5_GIAO_THUC.md and docs/phien/claude__a5-nhom-dong-hang.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO L<n>" or "FIX" and follow protocol §3 step 2. Never ask Truong; blocked
parts go under "Needs Truong". Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for A5 on branch claude/a5-nhom-dong-hang. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/A5_GIAO_THUC.md and docs/phien/claude__a5-nhom-dong-hang.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and follow
protocol §3 step 4. Never edit product code or tests; only docs/phien/claude__a5-nhom-dong-hang__checker.md.
Report in GT_GIAO_THUC §7 format.
```
