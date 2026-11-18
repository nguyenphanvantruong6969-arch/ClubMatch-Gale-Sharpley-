# GT automation protocol (3 teams × lead + writer + checker)

> Written 2026-11-15 (Opus, branch `claude/determined-allen-kig6ud`) at Truong's request: "divide into 3 tasks; each
> collaborator has 1 Opus lead, 1 Sonnet coder, 1 Sonnet rechecker; repeat until all features done and CI green; no
> further input". English (cheap). Every GT session reads this once at start. Modelled on `FA_SC_GIAO_THUC.md`
> (proven); where they differ, THIS file wins.

## 0. Source, scope, decisions
- Source: jury feedback on the pre-repo version (2 points: technical evidence + role of AI; per-student explanation +
  bounded criteria config + school review). Gap analysis and plan: `docs/ke_hoach/GT_KE_HOACH.md`.
- Task files (the lot specs): `docs/ke_hoach/gt/GT1_GIAI_TRINH.md`, `GT2_TIEU_CHI.md`, `GT3_QUYEN_TAI_LIEU.md`.
- Item codes approved by Truong 2026-11-15: **GT1** (parent C3), **GT2** (parent A1, Z7-lite), **GT3** (parents E1-lite,
  E2, plus docs outside the registry). Rule 1 is satisfied for everything listed in the task files; nothing else.
- Decisions (Truong, 2026-11-15; do NOT ask again):
  - D-GT1 criteria = bounded lexicographic: only the existing `rules` keys and values (`LUAT_XEP_MAC_DINH`); no
    weighted sum; no new criterion that reads personal circumstances, preference rank or past outcomes.
  - D-GT2 trial runs append to `run_history` with `loai_chay = 'thu'`; never published; official results untouched.
  - D-GT3 explanation for 3 audiences: admin/teacher lookup, printed slip, student self-lookup.
  - D-GT4 student self-lookup = student_id + random printed lookup code.
  - D-GT5 two roles (`quan_tri`, `giao_vien`) + password + audit log; OFF until the first admin account exists.
  - D-GT6 missing data / conflicting criteria: block the run and name the rows (current behaviour); document cases.
  - D-GT7 evidence: video script, GitHub link, Word/PDF pack, live-demo script.
  - D-GT8 **schema changes approved (rule 7)**: table `ma_tra_cuu` (GT1); column `run_history.loai_chay` + table
    `ket_qua_thu` (GT2); tables `tai_khoan`, `nhat_ky_thao_tac` (GT3). Only via `di_tru_schema` / `CREATE TABLE IF
    NOT EXISTS`, idempotent, backup first. CSV contract (invariant 7) unchanged. No new library (stdlib only;
    `python-docx` is already a dev dependency, docs build only).
  - D-GT9 time is short (deadline ~1 week): do lots in the order written; a lot that cannot finish goes on "Needs
    Truong" and the team moves on. Polished > many.

## 1. Teams, branches, namespaces (keeps the 3 teams from colliding)
| Team | Task file | Work branch | Error codes | New JS file | Test files | Schema insertion point |
|---|---|---|---|---|---|---|
| GT1 | `gt/GT1_GIAI_TRINH.md` | `claude/gt1-giai-trinh` | `gt1_*` | `js/14_giai_trinh.js` | `tests/test_gt1_*.py`, `tests/test_giao_dien_gt1_*.py` | after `giu_cho` block |
| GT2 | `gt/GT2_TIEU_CHI.md` | `claude/gt2-tieu-chi` | `gt2_*` | `js/15_tieu_chi.js` | `tests/test_gt2_*.py`, `tests/test_giao_dien_gt2_*.py` | `di_tru_schema` (ALTER) + after `fa_phan_hoi` |
| GT3 | `gt/GT3_QUYEN_TAI_LIEU.md` | `claude/gt3-quyen-tai-lieu` | `gt3_*` | `js/16_tai_khoan.js` | `tests/test_gt3_*.py`, `tests/test_giao_dien_gt3_*.py` | after `wharton_lock` block |
| Integration | §9 | `claude/gt-tich-hop` (GT3 lead) | — | — | `tests/test_gt_tich_hop.py` | — |

- Each lead creates its work branch from `origin/claude/determined-allen-kig6ud` (= main + these plan docs). Push only
  there. Never touch `main` or another team's branch. Never force-push. **No PR** (not asked).
- Shared files: edit only your own contiguous block, marked with a comment `GT1`/`GT2`/`GT3`; never reformat or reorder
  others' lines. `i18n_errors.py`: append your block at the end of the dict, then `python tao_i18n_js.py`.
  `index.html`: one block per team. `js/_danh_sach.txt`: add your file on its own line just before `08_khoi_dong`.
  `CHANGELOG.md` / `docs/ke_hoach/TIEN_DO.md`: add your rows; conflicts there are resolved at integration.
- To stay current: `git fetch origin main && git merge origin/main` (never rebase a pushed branch).

## 2. Roles
| Role | Model | Owns | Never |
|---|---|---|---|
| lead | Opus (`claude-opus-5-5`) | branch setup, lot specs in the branch file, creating/steering children, CI gate, final summary | writes product code, reads big diffs |
| writer | Sonnet (`claude-sonnet-5-5`) | tests first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | marks own lot as passed |
| checker | Sonnet (`claude-sonnet-5-5`) | reviews ONE lot diff, runs related tests, own edge cases, writes verdict | edits product code or tests (only its verdict file) |

## 3. Rules for all (from CLAUDE.md; do not ask Truong about these)
- Invariants 1–8 and rules 1–11 of `CLAUDE.md`. Truong explicitly asked for these sessions (rule 10 satisfied); no
  other subagents or Agent tool. Rule 11: Opus plans, Sonnet codes/checks.
- Invariant 1 proof, once per lot: `.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main
  --so-seed 20` (expect every dataset × seed identical). Every new option/table defaults OFF.
- Invariant 2: nothing new feeds `compute_club_priority` except what already did. Explanations, codes, accounts, logs
  and trial labels are reports/controls only.
- Privacy: fake data only (all numbers SIMULATED). A student-facing output contains ONLY that student's data; never
  another student's id, name, score or lottery number. Passwords never logged or returned.
- User-facing text: plain Vietnamese (+ English in `i18n`), no internal codes (GT1, L2, C3) in text a teacher reads.
- Tests quiet: `.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no <files> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed' | tail -25`.
  Related tests = the lot's new tests + every `tests/` file that greps for an identifier you changed. Full suite = CI.
- New test file → update the `tests/` row in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (file count + collect count).
- Env: `python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt`. Chromium is preinstalled.
- Locate code by function name (`grep -n "def <name>"`), never line numbers.
- Blocked (invariant conflict, new library, change beyond D-GT8, unclear spec): skip that part, add a line under
  "Needs Truong" in the team's branch file, continue. **Never stop to ask.**

## 4. Session start
1. Write `.claude/phien_vai.json` (gitignored): lead `{"vai":"coord","nguong":400000}`; children
   `{"vai":"impl"|"tester","coord_id":"<lead id>","nguong":200000}` (writer = impl, checker = tester).
2. Read `CLAUDE.md`, this file, the team branch file `docs/phien/claude__<branch tail>.md`, own `__<vai>.md` if any,
   then ONLY the task-file section of the current lot (and the code it names).

## 5. Work loop per lot (L1 → Ln of the task file)
1. lead → writer: `GO L<n>` (spec = "Lot L<n>" in the task file + any notes the lead adds in the branch file).
2. writer: failing test from the lot's "Done when" → minimal code → related tests → invariant-1 check → `soat-ma`
   (`kiem_nhanh.py` + the 4 tiers of `SKILL.md`, report only) → `CHANGELOG.md`, `TIEN_DO.md` row `GT<k>-L<n>` →
   commit `GT<k>-L<n>: ...` → `git pull --no-rebase && git push -u origin <branch>`.
3. writer → lead: `WRITER DONE L<n>`.
4. lead → checker: `REVIEW L<n> <base>..<head>`.
5. checker: read the diff, run related tests, check invariants 1, 2, 4, 5, 6, 7 and privacy, try 2–3 edge cases of its
   own on fake data (empty data, Vietnamese diacritics, unknown id, run never done, stale results, FA on and off).
   Write the verdict in `docs/phien/claude__<branch tail>__tester.md`, commit+push that file only.
6. checker → lead: `CHECKER REPORT L<n>`.
7. Bugs → lead sends `FIX L<n>` with the list → writer fixes → `WRITER DONE L<n> fix<k>` → checker re-checks.
   Max 3 rounds; then the lead records the lot under "Needs Truong" and moves on.
8. NO BUGS → lead ticks the lot in the branch file, pushes, sends `GO L<n+1>`.

## 6. CI gate (after the last lot; repeat until green)
1. Lead: `git fetch`; find the GitHub Actions runs for the branch head (`mcp__github__actions_list`, workflow
   `tests.yml`; load with ToolSearch). Wait with `send_later` 30 min while running; never poll in a loop.
2. Red → `mcp__github__get_job_logs` for failed jobs → lead writes a short FIX list (test ids + 1-line cause) →
   writer fixes (§5 step 7, no round limit for CI but a test may never be skipped, disabled or weakened) → push → back
   to step 1. Coverage < 85 % counts as red (the combine job).
3. Green (lint + all shards + coverage) on the head commit → lead merges `origin/main` if it moved, waits for green
   again, then writes in the branch file: `Status: DONE <sha> CI green <date>` and pushes.

## 7. Message formats (≤ 15 lines; no pasted diffs/logs, give file:function or sha)
```
WRITER DONE L<n>[ fix<k>] | base <sha> head <sha>
done: <what>; skipped: <part> (needs Truong: reason)
tests: <files> -> <N passed>; soat-ma: <DAT/KHONG DAT + 1 line>
invariants: 1 <how proven>, 2, 7 <ok/n/a>
```
```
CHECKER REPORT L<n> | reviewed <base>..<head>
verdict: NO BUGS | <k> BUGS
1. <file:function> <what> | repro: <steps> | expected: <...>
```
```
HANDOFF <vai> <file> <sha>
```

## 8. Messaging, silence, context (rule 9)
- Children report with `send_message` to the lead id. Without that tool: write the report at the top of own
  `__<vai>.md`, push, end the turn; the lead detects it by `git fetch`.
- Lead: after each `GO`/`REVIEW`/`FIX`, `send_later` 60 min. On a wake without a report: `get_session` +
  `list_events(kinds=["assistant","result"], limit=20)` + `git fetch`; idle child → `send_message` "report status in
  protocol format". Ignore wakes whose report already arrived.
- Child at 200k tokens (Stop hook): write `__<vai>.md` (from `_TEMPLATE.md`), push, send `HANDOFF ...`, stop. Lead
  creates a fresh child (same model, §11 prompt + "continue from Next steps of <file>"), archives the old one.
- Lead at 400k: update the branch file (state, next steps, child ids), create a new lead with the §11 lead prompt +
  "previous lead: <id>; continue from the branch file", send `NEW LEAD <id>` to both children, stop.

## 9. Integration (GT3 lead, after its own `Status: DONE`)
1. Every 60 min (`send_later`): `git fetch`; read `Status:` in `docs/phien/claude__gt1-giai-trinh.md` and
   `claude__gt2-tieu-chi.md` on their branches. Both DONE → step 2. If 48 h pass after GT3 DONE and a team is not DONE,
   integrate its latest pushed commit that had green CI (or leave it out) and list the gap under "Needs Truong".
2. Create `claude/gt-tich-hop` from `origin/main`; `git merge --no-ff` gt1, then gt2, then gt3. The writer resolves
   conflicts (shared files only; keep every team's lines; regenerate `i18n_loi.js`; renumber nothing).
3. Integration lots (spec in `gt/GT3_QUYEN_TAI_LIEU.md` § "Integration lots"): I1 permission map covers GT1/GT2 APIs;
   I2 student-lookup mode exit needs admin login when accounts are ON; I3 audit log records trial runs and code
   (re)generation; I4 case pack + evidence pack built from real GT1/GT2 output. Same §5 loop, then §6 CI gate.
4. Done: `Status: DONE <sha> CI green` in `docs/phien/claude__gt-tich-hop.md`, final summary (§10), archive all
   children, stop. Truong merges to main himself.

## 10. Final summary (each lead; Vietnamese; in the branch file and as its last message)
Lots done / skipped, new tests, CI result (run link), "Needs Truong" list with a recommendation each, what Truong
should try by hand (3–5 steps), a 3–5 line AI-log note for `docs/nhat_ky_ai/`. No report conclusions (integrity).

## 11. Prompts (leads are started by Truong's collaborators; leads use the writer/checker prompts verbatim)
**Lead** (replace `<K>` with 1, 2 or 3 and `<BRANCH>` from §1):
```
You are LEAD for GT<K> on branch <BRANCH>. Read CLAUDE.md, then docs/phien/GT_GIAO_THUC.md and
docs/ke_hoach/gt/GT<K>_*.md (both on origin/claude/determined-allen-kig6ud) and follow them exactly. Create
<BRANCH> from origin/claude/determined-allen-kig6ud, write docs/phien/claude__<branch tail>.md from
docs/phien/_TEMPLATE.md (goal, the lot list as the Plan, a Sessions table, a "Needs Truong" list, a Status line),
push, then create the WRITER and CHECKER sessions with the protocol §11 prompts (repo
https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV, source_revision <BRANCH>, models from §2,
permission_mode auto) and run §5 to the last lot, then §6 until CI is green. GT3 lead only: then run §9.
Never wait for Truong; anything that needs him goes on the list.
```
**Writer:**
```
You are WRITER for GT<K> on branch <BRANCH>. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/GT_GIAO_THUC.md and docs/phien/claude__<branch tail>.md, write .claude/phien_vai.json (§4), set up the
venv, then wait for "GO L<n>" or "FIX" from the lead and follow §5 steps 2-3 using the lot spec in
docs/ke_hoach/gt/GT<K>_*.md. Do not ask Truong anything; blocked parts go on the "Needs Truong" list. Report only in
the §7 formats.
```
**Checker:**
```
You are CHECKER for GT<K> on branch <BRANCH>. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/GT_GIAO_THUC.md and docs/phien/claude__<branch tail>.md, write .claude/phien_vai.json (§4), set up the
venv, then wait for "REVIEW L<n> <base>..<head>" and follow §5 steps 5-6 against the lot's "Done when" in
docs/ke_hoach/gt/GT<K>_*.md. Never edit product code or tests; only your verdict file. Report only in §7 formats.
```
