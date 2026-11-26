# DK6 protocol — size M (coder Sonnet + checker Sonnet, no lead)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 token rules apply; do not copy). Plan, boxes, gotchas:
> `docs/phien/claude__dk6-hoan-thien-phat-hanh.md`.

## 0. Rules (do not ask Truong)
- Lots L1, L2, L4 must ship; L3 optional (drop it without asking if it needs a schema/naming change).
- Allowed files: those named per lot + new tests + CHANGELOG/TIEN_DO/registry/CLAUDE_CHI_TIET count. No schema/CSV
  change, no new library, no change to the algorithm or `compute_club_priority`. Anything else → "Needs Truong", continue.
- Backend contract `{ok,data,errors}`; error text only via `i18n_errors.py` → `python tao_i18n_js.py`.
- Branch `claude/dk6-hoan-thien-phat-hanh`; before each lot fetch + merge `claude/loving-babbage-8yqo7d` and `main`
  (`--no-edit`). Never rebase, force-push, tag, release or open a PR. Max 2 FIX rounds per milestone, then
  "Needs Truong" + `git revert` of that lot.

## 1. Coder loop per lot (L1 → L2 → [L3] → L4)
Failing test from the lot's boxes → minimal code → lot test + ≤ 3 related (`-q --tb=line 2>&1 | tail -15`) →
`ruff check .` → `.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10` (7/7; invariant 1) → CHANGELOG (`head -20`
only) + TIEN_DO row `DK6-L<k>` → commit `DK6-L<k>: …` → push (only if no CI run you need is in flight; else batch).
Update "Current state" in the branch file after every commit.
MILESTONE 1 after L2, MILESTONE 2 after L4: wait for CI green on that head (Linux + Windows), then write
`MILESTONE <k> READY | head <sha>` in the branch file and tell Truong in one line (Vietnamese).
After the last lot: `soat-ma` four tiers (report only), registry row DK6, test-file count. CI gate: `tests.yml` +
*Build Windows executable* for the head (`failed_only` logs ≤ 60 lines); wait with `send_later` 25 min, never poll.
Red → fix; never skip/disable/weaken a test. Green → `Status: DONE <sha> CI green <date>`.

## 2. Checker (Truong starts it by pasting its prompt at `MILESTONE <k> READY`)
Reviews `<base>..<head>` (base = previous milestone head, or `c4486d3`); writes `PASS` or `FIX <≤10 lines>` in
`docs/phien/claude__dk6-hoan-thien-phat-hanh__checker.md`; pushes only that file; never edits product code/tests;
never PASS with CI pending. Checks: the lot's boxes; invariants 1, 4, 5, 6; password: salted, old token behaviour,
no password in logs/nhat_ky text, non-admin refused; refresh guards (focused input, PIN list, confirm box) and that
Cài đặt/Thêm/chuan_bi/xuat never poll; fold state survives redraw; L3 never deletes run_history or the pre-allocation
file; docs truthful (restore is MANUAL, decision A). 2–3 own edge cases. Milestone 2 also re-runs
`tests/test_giao_dien_dkl_*.py tests/test_dkl_*.py tests/test_dk4_chot_va_xep.py` and reports the tail.

## 3. Prompts
**Coder** (new Sonnet session on branch `claude/dk6-hoan-thien-phat-hanh`):
```
You are CODER for DK6 (size M) on branch claude/dk6-hoan-thien-phat-hanh. Read CLAUDE.md, then
docs/phien/DK6_GIAO_THUC.md and docs/phien/claude__dk6-hoan-thien-phat-hanh.md and follow them exactly. Set up the
venv (python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt). Do L1, L2, (L3 optional), L4 in
order, test first, update the branch file after every commit, write "MILESTONE <k> READY | head <sha>" after L2 and
after L4 (CI green first), then run the CI gate. Never ask Truong; blocked parts go under "Needs Truong".
Reply to Truong in Vietnamese.
```
**Checker** (new Sonnet session, same branch, at a milestone):
```
You are CHECKER for DK6 milestone <k> on branch claude/dk6-hoan-thien-phat-hanh. Read CLAUDE.md, then section 2 of
docs/phien/DK6_GIAO_THUC.md and the branch file. Review <base>..<head> as written there, run the lot tests, write
PASS or FIX in docs/phien/claude__dk6-hoan-thien-phat-hanh__checker.md, push only that file. Never edit product code
or tests. Reply to Truong in Vietnamese.
```
