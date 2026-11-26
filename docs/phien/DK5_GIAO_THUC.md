# DK5 protocol — size M (coder Sonnet + checker Sonnet, no lead)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 token rules apply; do not copy). Plan, acceptance, gotchas:
> `docs/phien/claude__dk5-dien-tap.md`. Loop context: `docs/phien/DK3_DK4_VONG_TU_DONG.md`.

## 0. Rules (do not ask Truong)
- Rehearsal only: NEW files (`du_lieu_test/dien_tap_dk5.py`, `tests/test_dk5_*.py`, `tests/test_giao_dien_dk5_toan_trinh.py`,
  docs). No product file edited; no schema/CSV change; no new library. Anything else → "Needs Truong" line, continue.
- Drive everything through the DK3/DK4 API (`{ok,data,errors}`); never write SQLite directly except to READ for asserts.
- Data is SIMULATED (`MÔ PHỎNG`); never present as a real survey. Never draft report commentary.
- Branch `claude/dk5-dien-tap`; before each lot `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase,
  force-push or open a PR. Max 2 FIX rounds per milestone, then "Needs Truong" + `git revert` of that lot.

## 1. Coder loop per lot (L1 → L3; L4 optional)
Preconditions in the branch file first. Then: failing test from the lot's boxes → minimal code → lot test + ≤ 3 related
(`-q --tb=line 2>&1 | tail -15`) → `ruff check .` → `.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10` (7/7;
invariant 1) → CHANGELOG (`head -20` only) + TIEN_DO row `DK5-L<k>` → commit `DK5-L<k>: …` → push.
At each MILESTONE write `MILESTONE <k> READY | head <sha>` in the branch file, message the checker's requester (one line).
After the last lot: `soat-ma` four tiers (report only), registry row DK5, test-file count in `CLAUDE_CHI_TIET.md`, then CI gate:
read `tests.yml` + *Build Windows executable* for the head commit (`failed_only` logs ≤ 60 lines); wait with `send_later`
30 min, never poll. Red → fix; never skip/disable/weaken a test. Green → `Status: DONE <sha> CI green <date>`.

## 2. Checker (Truong starts it by pasting its prompt when the coder writes `MILESTONE <k> READY`)
Reviews `<base>..<head>`; writes `PASS` or `FIX <≤10 lines>` in `docs/phien/claude__dk5-dien-tap__checker.md`; pushes only
that file; never edits product code or tests. Checks: the lot's boxes; invariants 1, 4, 5, 6; diff touches only new files;
rollback test really injects inside the transaction (not before it); restore test compares EVERY row; idle/deadline tests
use an injected clock; no `hash()`; data labelled MÔ PHỎNG; 2–3 own edge cases (0 teachers, student re-submits after
deadline, two students same kiosk). **Milestone 2 also re-runs the DK3 and DK4 test files** (`tests/test_dk3_*`,
`tests/test_dk4_*`, `tests/test_giao_dien_dk3_*`, `tests/test_giao_dien_dk4_*`) and reports the tail.

## 3. Prompts
**Coder** (paste into a new Sonnet session on branch `claude/dk5-dien-tap`):
```
You are CODER for DK5 (size M) on branch claude/dk5-dien-tap. Read CLAUDE.md, then docs/phien/DK5_GIAO_THUC.md and
docs/phien/claude__dk5-dien-tap.md and follow them exactly. Set up the venv (python3 -m venv .venv && .venv/bin/pip
install -q -r requirements-dev.txt). Check the Preconditions first (DK3/DK4 code present). Then do L1, L2, L3 in order
(test first, new files only), update the branch file after every commit, write "MILESTONE <k> READY | head <sha>" at
milestones 1 and 2, then run the CI gate. Never ask Truong; blocked parts go under "Needs Truong". Reply to Truong in Vietnamese.
```
**Checker** (new Sonnet session, same branch, started at a milestone):
```
You are CHECKER for DK5 on branch claude/dk5-dien-tap. Read CLAUDE.md, docs/phien/DK5_GIAO_THUC.md §2 and
docs/phien/claude__dk5-dien-tap.md. Review MILESTONE <k> (<base>..<head> from the branch file) as protocol §2 says; at
milestone 2 also re-run the DK3 and DK4 tests. Write PASS or FIX (≤ 10 lines) in
docs/phien/claude__dk5-dien-tap__checker.md and push only that file. Never edit product code or tests.
```
