# CB1 protocol — size M (coder + checker, no lead)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (budget rules §3 apply; not repeated). Work spec, decisions,
> lots, acceptance: `docs/phien/claude__cb1-van-ban-phuong-an.md`. Truong asked for these sessions (rule 10 ok).

## 0. Decisions already made (do not ask Truong)
- Item CB1, independent of DC1. One plain-language Vietnamese PDF, two versions (dự kiến / chốt). No comparison
  table, no appendix. Seed checkbox default OFF, only in bản chốt after `stb_lock` is locked.
- Chốt stored as key `chot_phuong_an` in existing `workspace_settings` (no new table/column/migration). Audit row
  via existing `nhat_ky` wrapper. FA-9 biên bản unchanged and stays the signing page.
- No new library (reportlab already approved in XP1). Anything else → "Needs Truong" + continue.

## 1. Branch and lots
| Branch | Lots | Milestones |
|---|---|---|
| `claude/cb1-van-ban-phuong-an` | L1 builder → L2 API+PDF → L3 UI → L4 docs | M1 after L2, M2 after L4 |
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push. No PR.
- L1–L3 must ship; L4 docs line in HUONG_DAN must ship, demo script optional.

## 2. Roles
| Role | Model | Does | Never |
|---|---|---|---|
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push, CI gate | marks a milestone passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews at M1 and M2, runs tests + own edge cases, writes verdict | edits product code or tests |
- Truong starts the checker by pasting its prompt when the coder writes `MILESTONE <k> READY | base <sha> head <sha>`.

## 3. Coder loop per lot
Failing test from the lot's box → minimal code → lot test file + ≤ 3 related (`tests/test_mt1*`,
`tests/test_gt2*`, `tests/test_bao_cao_tong_hop*`, `tests/test_fa_bien_ban*` — whichever exist), quiet
(`-q --tb=line 2>&1 | tail -15`) → `kiem_nhanh.py | tail -10` must be 7/7 → `soat-ma` four tiers (report only)
→ CHANGELOG + TIEN_DO row `CB1-L<n>` → commit `CB1-L<n>: …` → push. After L2 and L4 write MILESTONE line.
UI tests: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, one Chromium file, `--trace off`.

## 4. Checker (per milestone; verdict in `docs/phien/claude__cb1-van-ban-phuong-an__checker.md`, push only it)
- Boxes of the lots in range; invariants 1, 2, 4, 5, 6, 7; `cau_hinh_ws.doc_cau_hinh` unaffected by the new key.
- Privacy: PDF text (both versions, sample 120 students) has no student id, name, score or lottery number.
- Seed: absent by default, absent in dự kiến even with `in_hat_giong=True` (refused), present only when ticked.
- Teacher role refused on the 3 new functions (backend); audit row written on chốt; `run_history` not touched.
- Edge cases (pick 3): no run yet; chốt then change one rule then re-export; chốt twice; FA off (no complaint
  line); workspace with custom labels (non-school sector); reportlab missing.
- Verdict: NO BUGS or numbered FIX list. Max 2 FIX rounds, then "Needs Truong" + `git revert` of that lot.

## 5. CI gate (coder, after M2 passes)
Read `tests.yml` + `Build Windows executable (rbda-kiosk)` for head (`mcp__github__actions_list`,
`get_job_logs failed_only`, ≤ 60 lines); wait with `send_later` 30 min, never poll. Never skip/weaken a test.
Green → `Status: DONE <sha> CI green <date>` + Vietnamese summary (≤ 10 lines, 3 steps for Truong to try).

## 6. Prompts
**Coder (first session; Truong pastes it):**
```
You are CODER for CB1 on branch claude/cb1-van-ban-phuong-an. Read CLAUDE.md, docs/phien/CB1_GIAO_THUC.md and
docs/phien/claude__cb1-van-ban-phuong-an.md (on origin/claude/cb1-van-ban-phuong-an); follow them exactly.
Set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt), then do L1 to L4
per protocol §3, writing "MILESTONE 1 READY | base <sha> head <sha>" after L2 and "MILESTONE 2 READY ..." after
L4, then §5 once the checker says NO BUGS. Never ask Truong mid-lot; blocked parts go under "Needs Truong".
```
**Checker (Truong pastes it at each milestone):**
```
You are CHECKER for CB1 on branch claude/cb1-van-ban-phuong-an, milestone <k>, range <base>..<head>. Read
CLAUDE.md, docs/phien/CB1_GIAO_THUC.md and docs/phien/claude__cb1-van-ban-phuong-an.md. Set up the venv, then
follow protocol §4. Never edit product code or tests; write only
docs/phien/claude__cb1-van-ban-phuong-an__checker.md, push it, and end with one line: NO BUGS or FIX <n items>.
```
