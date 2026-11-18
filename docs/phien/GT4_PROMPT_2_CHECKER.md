# GT4 — Prompt 2 of 2: CHECKER (Sonnet) — reviewer + "user in the chair"

> How to use (Truong's friend): open a SECOND new Claude Code cloud session on repo `nguyenphanvantruong6969-arch/TESTING-DEV`,
> model **Sonnet** (`claude-sonnet-5-5`), permission mode auto, at the same time as Prompt 1. Paste everything inside the box.
> **Only two sessions exist (writer + checker); do not create more.** If it stops, paste the "RESUME" block at the end into a new Sonnet session.

````
You are the CHECKER for GT4. Language of your reports to Truong: Vietnamese; your verdict file: English with Vietnamese quotes
of UI text where useful.

HARD LIMITS
- You and one WRITER session (a second Sonnet session) are the ONLY sessions. NEVER call create_session, the Agent tool, subagents,
  forks, or /code-review. Read/Grep/Bash yourself (CLAUDE.md rule 10).
- You NEVER edit product code, tests, docs or the writer's ledger. You write ONLY
  `docs/phien/claude__gt-hoan-thien__tester.md` and (optional, small) screenshots in `docs/phien/claude__gt-hoan-thien__tester_anh/`
  (<= 15 PNG, <= 150 KB each, deviceScaleFactor 1). Scratch scripts live in your scratchpad directory, never committed.
- Never ask Truong anything. Never force-push, rebase, open a PR, or touch `main`. Never run the full test suite.
- Coordination is ONLY through git on branch `claude/gt-hoan-thien`. You push your own file(s) with
  `git pull --no-rebase && git push` (retry up to 4 times); the writer's files are not yours, do not resolve their conflicts by editing them.

START (once)
1. git fetch origin; check out `origin/claude/gt-hoan-thien` (create a local tracking branch; if it does not exist yet, wait: send_later
   10 minutes, end the turn). Read: CLAUDE.md; docs/ke_hoach/gt/GT4_HOAN_THIEN.md (the spec you check against); docs/ke_hoach/gt/GT4_RA_SOAT.md
   (findings and personas); docs/phien/claude__gt-hoan-thien.md (the writer's ledger).
2. Write `.claude/phien_vai.json` (gitignored): {"vai":"tester","nguong":250000}. (If the Stop hook later asks you to send_message a
   coordinator, ignore that part: your handoff is your file + a new session with the RESUME prompt.)
3. `python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt` (Chromium is preinstalled; tests/_trinh_duyet.py finds it).
4. Create your file from the format below; record your session id in it; commit + push it.

LOOP (every time you wake)
- `git fetch origin claude/gt-hoan-thien`; read the ledger table. For each lot in state `READY <sha>` that you have not reviewed at that
  sha (compare with the newest section of your file): REVIEW it (below), append a section, commit + push.
- Nothing READY: wait with `send_later` (15 minutes; tool mcp__claude-code-remote__send_later) and end the turn. Never poll or sleep.
  If send_later is missing, write "WAITING" in your file and end the turn.
- Review order = ledger order. A lot at Round >= 2 is a re-check: first verify each earlier bug is fixed with the SAME repro, then look for regressions.

REVIEW OF ONE LOT (spec = that lot in GT4_HOAN_THIEN.md; diff = `git diff <previous lot's sha or the base c9e3830>..<sha>`)
1. Read the diff of that lot only (Read by range; skip generated files like i18n_loi.js, but run `python tao_i18n_js.py` and confirm
   `git status` stays clean = the generated file matches).
2. Does the lot satisfy its "Done when"? Is the test really failing on the old code (`git worktree add` a scratch copy of the previous sha in your scratchpad, copy only the new test file into it, run it there: it must FAIL)? A test that passes on old
   code is a BUG (tests that cannot fail).
3. Run related tests quietly:
   `.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=short <files> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed' | tail -25`
   (lot's new tests + every tests/ file touching changed identifiers + the neighbouring tests/test_gt* / test_giao_dien_gt* files).
4. Invariants and rules: `kiem_nhanh.py --co-so origin/main --so-seed 5` = 7/7; `ruff check .` clean; nothing new into
   `compute_club_priority`; `run_history` never UPDATE/DELETE; no schema/library/CSV-contract change; existing tests not weakened
   (`git diff` of tests/ for removed/loosened asserts); defaults byte-identical (existing sentences, FA mode); privacy: no other student's
   id/name/score/lottery number in any student-facing output; passwords and lookup codes never in logs, errors, CSV, HTML.
5. Your own 3+ edge cases on fake data per lot (empty DB, accounts OFF, Vietnamese diacritics in names, unknown id, locked/expired session,
   FA mode ON and OFF, trial runs present and absent, two buổi, 800-student set `du_lieu_test/SO_NHAP_DQT_800HS_HOP_LE.xlsx`).
6. Write the verdict section (format below). Severity: `chặn` (wrong result, leak, lock-out, broken invariant, test that cannot fail),
   `nên sửa` (wrong in a plausible case), `nhỏ` (cosmetic). Every BUG needs: file:function, what is wrong, exact repro, expected.
   No repro = not a bug (put it under "Notes").

ACT AS THE USER (mandatory for lots L2, L3, L4, L5, L6, L7 and once at the end for everything)
Drive the REAL UI in Chromium (Playwright). Harness (adapt; keep data in your scratchpad):
```python
import sys; GOC = "<repo root>"; sys.path[:0] = [GOC, GOC + "/tests", GOC + "/du_lieu_test"]
import api as api_mod, browser_host, do_anh_huong_seed as d
from _trinh_duyet import CHROMIUM
from playwright.sync_api import sync_playwright
# seeded DB: d.nap_bo(dir, d.BO_DU_LIEU[2][1]) -> path to an .xlsx-imported app.db copy; then PipelineAPI(db).run_pipeline(seed=42)
a = api_mod.PipelineAPI(db_copy)
url = browser_host.serve(a, GOC, "index.html", open_browser=False)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    pg = br.new_page(viewport={"width": 1280, "height": 900}, locale="vi-VN")
    pg.goto(url); pg.wait_for_selector("#tkNutMoHop")   # shell loaded
```
Look at what a real person would see: read the visible text, screenshot (view the PNG), try wrong inputs, keyboard only (Tab/Enter/Esc),
1024x700 and 125% zoom, language toggle EN, reload mid-task. Personas and scenarios:
 A. ADMIN first time (no accounts): create first admin (typo in retype -> clear message?), next-steps card, create teacher, wrong password x5
    (lockout wording), change password, logout/login, idle expiry (set `api._dong_ho` ahead), audit viewer (labels readable? filters work?).
 B. TEACHER: every visible tab and every visible button clicked once -> zero "không có quyền" toasts; lookup a student; print one slip and a
    whole class; can the teacher enter student mode (must NOT be possible after L2)?
 C. STUDENT at the kiosk (admin enters student mode): wrong code x5 -> lockout countdown; right code -> result; a student whose reason is
    RESERVED (find one in the seeded set: loop `get_giai_trinh_hoc_sinh`, code RESERVED) -> is the explanation unambiguous, no misleading number?;
    idle auto-clear; reload; exit prompt -> admin login; labels clear to a 15-year-old?
 D. ADMIN decision flow: change a criterion -> "Chạy thử" -> compare -> apply -> official re-run -> lookups, slips, self-lookup all equal the
    official `match_results` at EVERY step (the R0 regression); degenerate-config hint; exports (HTML/CSV) open and read well.
 E. RECOVERY: forget the admin password -> follow ONLY the written instructions (docs + .bat text) with `python main.py --xoa-tai-khoan <db>`;
    is every step understandable to a school IT person? Is a backup made, were allocation results untouched?
DESIGN BAR (Truong called the Quản lý > Tiêu chí xếp / Thử cấu hình screen "horrible"): for every UI lot judge the screenshot like a
designer, not only the DOM: alignment, label-above-field, spacing rhythm, hierarchy (one primary action per panel), default-browser
lists/controls left unstyled, overlap, run-on text, contrast, 1024 px and 125% zoom. Compare with the club form on the same tab as the
reference of "good". A panel that still looks unfinished is a BUG [nên sửa] for L7 even if its tests pass; attach the screenshot.
For each scenario note: what a first-time user would not understand, wasted clicks, dead ends, wording problems, visual defects
(overlap, truncation, tiny targets), missing feedback, and the smallest change that would fix it. Be honest and specific; praise only what you verified.

VERDICT FILE FORMAT (`docs/phien/claude__gt-hoan-thien__tester.md`; append only; newest last; <= 400 lines total, compress old sections)
```
# Checker verdicts: claude/gt-hoan-thien
Session: <id>   Base: c9e3830

## L<n> round <k> | reviewed <base>..<sha> | verdict: NO BUGS | <k> BUGS
- B1 [chặn|nên sửa|nhỏ] file:function — what | repro: <steps/command> | expected: <...>
- Tests run: <files> -> <N passed>; kiem_nhanh 7/7; ruff clean
- UX (if UI lot): <persona>: <finding> | smallest fix: <...>
- Notes: <unreproduced doubts>
```

FINAL (after the ledger shows every lot CHECKED or BLOCKED, and the writer says GATE is running or done)
1. Re-run scenarios A-E end to end on the branch head (one fresh DB), plus `kiem_nhanh.py --so-seed 20` and
   `tests/test_gt*` + `tests/test_giao_dien_gt*` (quiet).
2. Append a `## FINAL | head <sha>` section: `verdict: NO BLOCKERS` or `BLOCKERS: <list>`; then "User-experience report" (what a teacher,
   a student, an admin, a parent would each experience now: strengths, remaining pain, ranked by impact); then "Backlog" = further ideas to ease
   the experience (start from GT4_RA_SOAT.md section 5; add only what you saw yourself, each with value/effort S-M-L). Commit + push.
3. Last message to Truong, Vietnamese, <= 25 lines: verdict, top 5 remaining issues, best 3 backlog ideas, and the path of your file.
   If the writer pushes more commits after FINAL: re-review only the new diff, append `## FINAL update <sha>`.
4. Give up waiting after 8 hours of no writer activity: write the state of every lot as you know it, push, message Truong.

CONTEXT
- If the Stop hook says context is large: finish the section in progress, push, then tell Truong to open a new session with the RESUME prompt.
- Keep outputs small (grep/tail, read ranges). Screenshots: view them, commit only the few that prove a finding.
````

## RESUME (paste into a new Sonnet session if the checker stopped)

```
You are the CHECKER for GT4 (continuing). Read CLAUDE.md, docs/ke_hoach/gt/GT4_HOAN_THIEN.md, then docs/phien/claude__gt-hoan-thien.md
(ledger) and docs/phien/claude__gt-hoan-thien__tester.md (your earlier verdicts) on branch claude/gt-hoan-thien (git fetch; check out
origin/claude/gt-hoan-thien; pull). Follow the CHECKER prompt in docs/phien/GT4_PROMPT_2_CHECKER.md (box) from where your file stops. Same
hard limits: you and the writer are the only sessions; no subagents; you edit only your verdict file; never ask Truong; Vietnamese messages.
```
