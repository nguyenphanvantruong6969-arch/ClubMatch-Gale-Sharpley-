# MT1-X1 automation protocol (1 team: lead + coder + checker)

> Source of work: `docs/phien/claude__mt1-xuat-so-nhap-loai.md` (verified facts, decisions D1–D6, Plan = lots
> L1–L3, acceptance). Truong asked for this lead/coder/checker setup (CLAUDE.md rules 10, 12 satisfied).
> Base: `origin/claude/mt1-xuat-so-nhap-loai` (branched from `claude/mt1-bang-loai-clb` @ `05783a7`).
> Mechanics not repeated here (message formats, quiet test command, silence rules): `docs/phien/GT_GIAO_THUC.md`
> §7, §8 with "writer" = coder, "GT<k>" = "MT1-X1". Where they differ, THIS file wins.

## 0. Decisions already made (do not ask Truong again)
- D1–D6 in the branch file. In short: FA club keys only when FA on or some club has FA values; "Giữ chỗ" sheet
  only when FA on; no `che_do_fa=True` from the export; return tuple of `_du_lieu_so_nhap` unchanged; compare xlsx
  by sheet names + cell values (not zip bytes); re-import overwrite warning NOT built (Needs Truong N1).
- No new library, no schema change, no CSV-contract change, no i18n/UI change. Any need for one → "Needs Truong".
- All data is SIMULATED (`du_lieu_test/`); never describe numbers as a real survey.

## 1. Branch, lots
| Branch | Lots | Branch file |
|---|---|---|
| `claude/mt1-xuat-so-nhap-loai` | L1 FA club columns → L2 Giữ chỗ + full round trip → L3 verify + docs | `docs/phien/claude__mt1-xuat-so-nhap-loai.md` |

- Each lot's spec = its block in the branch file's Plan; "Done when" = all its boxes ticked + the checks below.
- Stay current before each lot: `git fetch origin claude/mt1-bang-loai-clb && git merge --no-edit FETCH_HEAD`.
  If MT1 has been merged to main, merge `origin/main` instead. Never rebase or force-push.

## 2. Roles and session limit
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | updates branch file (Status, Sessions, Needs Truong), creates EXACTLY two child sessions, runs the loop, CI gate, final check | writes product code or tests |
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | ticks a lot as passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews one lot diff, runs related tests + own edge cases, writes verdict | edits product code or tests |

- **Exactly 3 sessions. No extra sessions, no Agent tool.** Context is summarised automatically; this overrides the
  "stop at 400k" part of CLAUDE.md rule 9. Keep "Current state" and your `__<vai>.md` file current after each message.
- Never ask Truong. Blocked part → one line under "Needs Truong", continue.

## 3. Loop per lot (L1 → L3)
1. lead → coder `GO L<n>`.
2. coder: failing test from the lot's boxes (show it RED) → minimal code → related tests only:
   `.venv/bin/python -m pytest -q tests/test_xuat_du_lieu.py tests/test_fa_du_lieu.py tests/test_a13_12_so_nhap.py
   tests/test_mt1_dong_bo_loai_clb.py <new test file>` → `ruff check .` → `git fetch origin main` then
   `.claude/skills/soat-ma/scripts/kiem_nhanh.py` 7/7 (incl. `trung_khit`) → `soat-ma` four tiers (report only) →
   CHANGELOG + TIEN_DO row `MT1-X1-L<n>` → commit `MT1-X1-L<n>: …` → push → `CODER DONE L<n> | base <sha> head <sha>`.
3. lead → checker `REVIEW L<n> <base>..<head>`.
4. checker: verdict in `docs/phien/claude__mt1-xuat-so-nhap-loai__checker.md` (push only that file) →
   `CHECKER REPORT L<n>`. Lot-specific checks:
   - **L1**: xfail really removed (not `skip`, not weakened assert); gate is D1 exactly (key PRESENCE drives
     `ghi_so_nhap.co_fa`, so check no key is added in normal mode); normal-mode export cell values unchanged;
     `loai` written as display label (`NHAN_LOAI_HIEN_THI`) and read back to the code. Own edge cases: FA on with
     all NULL; FA off with one club `diem_san` only; club name with diacritics / duplicate names (`ten_khong_trung`).
   - **L2**: round trip equal for `loai, diem_san, so_toi_thieu, suc_chua_phong` and the `giu_cho` SET; FA off →
     no "Giữ chỗ" sheet; FA on + empty table → header-only sheet and re-import clears nothing wrongly; a `giu_cho`
     row whose student has no preference still round-trips (or the limit is documented); `_du_lieu_so_nhap`
     callers unaffected (`grep -n "_du_lieu_so_nhap"`).
   - **L3**: D5 comparison done on 3 datasets with results recorded; docstring updated; CHANGELOG/TIEN_DO rows;
     invariants 1, 2, 4, 5, 6, 7 untouched (no solver, priority, run_history, schema or CSV-header change).
5. Bugs → `FIX L<n>` → coder → checker again (max 3 rounds, then "Needs Truong", move on). NO BUGS → lead ticks the
   lot in the branch file and pushes. Push a lot only after CI of the previous push has finished or been read.

## 4. CI gate (after L3; repeat until green)
Lead reads GitHub Actions `tests.yml` and `Build Windows executable (rbda-kiosk)` for the head commit
(`mcp__github__actions_list`, `mcp__github__get_job_logs` with `failed_only`; load via ToolSearch); waits with
`send_later` 30 min, never a polling loop. Red → short FIX list → coder → checker → push → again. A test may never
be skipped, disabled or weakened. Green (lint + all shards + coverage ≥ 85 % + Windows build) →
`Status: DONE <sha> CI green <date>` in the branch file.

## 5. Final check by the lead (user's point of view, backend only, simulated data)
In a scratch folder: FA workspace from `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx`, set one type in the UI path
(`dat_loai_clb`), add 2 reserved seats, export, open the xlsx and read sheet "1. CLB" + "Giữ chỗ" as a teacher would
(labels Tự do / Giới hạn / Tuyển chọn readable, no stray columns), import into a new empty DB, run seed 3 on both DBs
and compare `match_results` rows: identical. Then the same with `SO_NHAP_DQT_120HS_HOP_LE.xlsx` (FA off): no new
column, no new sheet. Write 5–10 lines (Vietnamese) in the branch file "Final summary". No report conclusions for
the student's science report (academic integrity).

## 6. Handoff files (short; Truong reads them)
Branch file ≤ 150 lines: Status, Plan (ticked), Current state (3 lines), Sessions table, Needs Truong (1 line each +
recommendation), Final summary in Vietnamese (≤ 10 lines: done/skipped, CI link, what Truong tries by hand in 3
steps). `__coder.md` / `__checker.md` ≤ 30 lines each.

## 7. Prompts (lead uses the child prompts verbatim; replace <LEAD_ID>)
**Lead** (Truong pastes this into a new Opus session): see the end of the planning reply / below.
```
You are LEAD for MT1-X1 on branch claude/mt1-xuat-so-nhap-loai. Read CLAUDE.md, then docs/phien/MT1_X1_GIAO_THUC.md
and docs/phien/claude__mt1-xuat-so-nhap-loai.md (both on origin/claude/mt1-xuat-so-nhap-loai) and follow them
exactly. Add a Sessions table to the branch file and set Status to IN PROGRESS, push, then create the CODER and
CHECKER sessions with the protocol §7 prompts (repo https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV,
source_revision claude/mt1-xuat-so-nhap-loai, models from §2, permission_mode auto) and run §3 for L1 to L3, then
§4 until CI is green, then §5. Never wait for Truong; anything that needs him goes on the "Needs Truong" list.
```
**Coder:**
```
You are CODER for MT1-X1 on branch claude/mt1-xuat-so-nhap-loai. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/MT1_X1_GIAO_THUC.md and docs/phien/claude__mt1-xuat-so-nhap-loai.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO L<n>" or "FIX" and follow protocol §3 step 2. Test first: show the test
RED before any product change. Never ask Truong; blocked parts go under "Needs Truong". Report in GT_GIAO_THUC §7
format.
```
**Checker:**
```
You are CHECKER for MT1-X1 on branch claude/mt1-xuat-so-nhap-loai. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/MT1_X1_GIAO_THUC.md and docs/phien/claude__mt1-xuat-so-nhap-loai.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and follow
protocol §3 step 4. Never edit product code or tests; only docs/phien/claude__mt1-xuat-so-nhap-loai__checker.md.
Report in GT_GIAO_THUC §7 format.
```
