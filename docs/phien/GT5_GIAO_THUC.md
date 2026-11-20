# GT5 automation protocol (1 team: lead + coder + checker)

> Source of work: `docs/phien/claude__inspiring-cori-2za7na.md` (goal, decisions D1–D6, Plan = lots L1–L5,
> acceptance, gotchas). Truong asked for these sessions explicitly on 2026-11-20 (CLAUDE.md rule 10 satisfied).
> Base: `origin/claude/inspiring-cori-2za7na`. Mechanics not repeated here (message formats, quiet test command,
> messaging/silence): use `docs/phien/GT_GIAO_THUC.md` §7, §8 with "writer" = coder, "GT<k>" = "GT5".
> Where they differ, THIS file wins. Modelled on `XP1_GIAO_THUC.md`.

## 0. Decisions already made (do not ask Truong again)
- Docs and doc generators only (`docs/giai_trinh/`, `du_lieu_test/tao_*.py`, tests). No production module, schema,
  CSV contract or UI change. No new library (Chromium/Playwright + python-docx already present).
- Every generated file is deterministic and has a freshness test.
- Academic integrity: facts and software output only, marked "DỮ LIỆU MÔ PHỎNG"; student sections left empty;
  `PHAN_CONG.md` never filled by any session.

## 1. Branch, lots
| Branch | Lots | Branch file |
|---|---|---|
| `claude/inspiring-cori-2za7na` | L1 diagram in PDF/DOCX → L2 `TIEU_CHI.md` (no weights, seed, default medals) → L3 `CA_MAU.md` §6–7 → L4 `DOI_CHIEU_YEU_CAU.md` + regenerate pack → L5 docs/verify/CI | `docs/phien/claude__inspiring-cori-2za7na.md` |

- Each lot's spec and tests = its block in the branch file's Plan.
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push.
- Push only to `claude/inspiring-cori-2za7na`.

## 2. Roles and session limit
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | updates the branch file (Status, Sessions, Needs Truong), creates EXACTLY two child sessions, runs the loop, CI gate, final review | writes docs/code of the lots |
| coder | Sonnet `claude-sonnet-5-5` | test first, generator code, regenerate docs, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | marks own lot passed; writes commentary/conclusions |
| checker | Sonnet `claude-sonnet-5-5` | reviews one lot diff, runs related tests + own edge cases, writes verdict | edits docs, code or tests |

- **Exactly 3 sessions for the whole job. No extra sessions, no Agent tool.** Context is summarised automatically;
  this overrides the "stop at 400k" part of CLAUDE.md rule 9. Keep "Current state" and your `__<vai>.md` current.
- Never ask Truong. Blocked part → one line under "Needs Truong" in the branch file, continue.

## 3. Loop per lot (L1 → L5)
1. lead → coder `GO L<n>`.
2. coder: failing test from the lot's boxes → minimal change → regenerate the affected docs → related tests
   (quiet; Chromium tests need `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) → `.claude/skills/soat-ma/scripts/
   kiem_nhanh.py` 7/7 (incl. `trung_khit`) → `soat-ma` four tiers → CHANGELOG + TIEN_DO row `GT5-L<n>` → commit
   `GT5-L<n>: …` → push → `CODER DONE L<n> | base <sha> head <sha>`.
3. lead → checker `REVIEW L<n> <base>..<head>`.
4. checker: verdict in `docs/phien/claude__inspiring-cori-2za7na__checker.md` (push only that file) →
   `CHECKER REPORT L<n>`. Checks: the lot's boxes; no production file in the diff (`git diff --stat`); generators
   deterministic (run twice, `cmp`); every number in a generated doc recomputed independently; every file/test path
   named in a doc exists; Vietnamese reads plainly for a teacher (D5); "DỮ LIỆU MÔ PHỎNG" present; no evaluative or
   concluding sentence written for the student; open the regenerated PDF and DOCX (render PDF page with the
   diagram to PNG and look at it).
5. Bugs → `FIX L<n>` → coder → checker again (max 3 rounds, then "Needs Truong" and move on). NO BUGS → lead ticks
   the lot and pushes.
- Push a lot only after CI of the previous push has finished or been read.

## 4. CI gate (after L5; repeat until green)
Lead reads GitHub Actions `tests.yml` and `Build Windows executable (rbda-kiosk)` for the head commit
(`mcp__github__actions_list`, `mcp__github__get_job_logs` with `failed_only`, load via ToolSearch); waits with
`send_later` 30 min, never a polling loop. Red → FIX list → coder → checker → push → again. Never skip, disable or
weaken a test. Green → `Status: DONE <sha> CI green <date>` in the branch file.

## 5. Final review by the lead (a judge's point of view)
Open `GOI_MINH_CHUNG.pdf` and `.docx` and read them as the reviewer who wrote the feedback: for each bullet of
requirements 1 and 2, can it be found within 1 minute from `DOI_CHIEU_YEU_CAU.md`? Is the diagram visible? Does
`TIEU_CHI.md` answer "where are the weights / what is the seed" in plain words? Write `docs/ke_hoach/gt/
GT5_DANH_GIA.md` (≤ 40 lines, Vietnamese): bullet → found yes/no, problems with one screenshot each, what Truong must
still do by hand (fill `PHAN_CONG.md`, repository access for judges, write the letter's own sections). No
conclusions for the student's report.

## 6. Handoff files
Branch file ≤ 150 lines: Status, Plan (ticked), Current state (3 lines), Sessions table, Needs Truong (1 line each +
recommendation), Final summary in Vietnamese (≤ 10 lines). `__coder.md` / `__checker.md` ≤ 30 lines each.

## 7. Prompts (lead uses the child prompts verbatim; replace <LEAD_ID>)
**Lead** (Truong pastes this into a new Opus session):
```
You are LEAD for GT5 on branch claude/inspiring-cori-2za7na. Read CLAUDE.md, then docs/phien/GT5_GIAO_THUC.md and
docs/phien/claude__inspiring-cori-2za7na.md (both on origin/claude/inspiring-cori-2za7na) and follow them exactly.
Add a Status line, a Sessions table and a "Needs Truong" list to the branch file, push, then create the CODER and
CHECKER sessions with the protocol §7 prompts (repo https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV,
source_revision claude/inspiring-cori-2za7na, models from §2, permission_mode auto) and run §3 for L1 to L5, then
§4 until CI is green, then §5. Never wait for Truong; anything that needs him goes on the list.
```
**Coder:**
```
You are CODER for GT5 on branch claude/inspiring-cori-2za7na. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/GT5_GIAO_THUC.md and docs/phien/claude__inspiring-cori-2za7na.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO L<n>" or "FIX" and follow protocol §3 step 2. Never ask Truong; blocked
parts go under "Needs Truong". Never write commentary or conclusions for the student; never fill PHAN_CONG.md.
Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for GT5 on branch claude/inspiring-cori-2za7na. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/GT5_GIAO_THUC.md and docs/phien/claude__inspiring-cori-2za7na.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and follow
protocol §3 step 4. Never edit docs, code or tests; only docs/phien/claude__inspiring-cori-2za7na__checker.md.
Report in GT_GIAO_THUC §7 format.
```
