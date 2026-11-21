# SM2 protocol (lean, size M-lite: 1 coder session + 1 checker review)

> Template: `docs/phien/_GIAO_THUC_GON.md` (token rules §3 apply to every session). Work: `docs/phien/claude__sm2-mot-so-mau.md`.
> Truong approved SM2 on 2026-11-21 and asked for these sessions (CLAUDE.md rule 10 satisfied).

## 1. Sessions (exactly 2, no lead, no Agent tool)
| Role | Model | Does | Never |
|---|---|---|---|
| coder | Sonnet `claude-sonnet-5-5` | creates branch `claude/sm2-mot-so-mau` from `origin/claude/ux2-phan-hoi-nut` (plan + SO-MAU live there), L1 then L2 (test first), related tests, `kiem_nhanh.py` 7/7, `soat-ma`, CHANGELOG/TIEN_DO, commit `SM2-L<n>: …`, push, CI gate | marks own work passed |
| checker | Sonnet `claude-sonnet-5-5` | ONE review of `origin/claude/ux2-phan-hoi-nut..origin/claude/sm2-mot-so-mau` after L2; verdict in `docs/phien/claude__sm2-mot-so-mau__checker.md` | edits product code or tests |

- Truong starts the checker (pastes its prompt) when the branch file says `READY FOR REVIEW`.
- Bugs → checker lists them in its file; Truong pastes `FIX` into the coder; max 2 rounds, then "Needs Truong".

## 2. Coder loop
- Base (Truong, 2026-11-21, option A): plans stay off `main` until their code is reviewed. Stay current with
  `git fetch origin main claude/ux2-phan-hoi-nut && git merge --no-edit origin/main` before each lot; never rebase.
- PR to main only after `Status: DONE`, one PR for SM2 (it also carries SO-MAU + this plan if PR #26 is still open).
L1 → commit → push → L2 → commit → push → set `Status: READY FOR REVIEW <sha>` in the branch file → wait for
CI (`send_later` 30 min, read only failed jobs, ≤ 60 lines) → fix red (max 2 rounds; never skip or weaken a test)
→ `Status: DONE <sha> CI green` + Vietnamese summary (≤ 8 lines: what changed, what Truong should click to try).
Usage limit near → finish the commit, update "Current state", stop; a new coder continues from the branch file.

## 3. Checker checks
Plan boxes; invariants 1, 6, 7 (no api return shape, CSV or schema change); `ghi_so_nhap` default byte-identical;
non-FA workspace: empty FA columns give no warning; FA: no `wharton_chua_dung_het` noise but medal errors still
reported (`kiem_ho_so_huy_chuong`); old API caller `kieu="huy_chuong"` still works; vi + en text; 2 own edge cases
(workspace with custom vocabulary labels, a school with one buổi).

## 4. Fallback
L2 fails 2 rounds → `git revert` L2 only, keep L1 (it is independent), note under "Needs Truong".

## 5. Prompts
**Coder** (Truong pastes into a new Sonnet session):
```
You are CODER for SM2. Read CLAUDE.md, docs/phien/_GIAO_THUC_GON.md §3, docs/phien/SM2_GIAO_THUC.md and
docs/phien/claude__sm2-mot-so-mau.md (all on origin/claude/ux2-phan-hoi-nut). Create branch claude/sm2-mot-so-mau
from origin/claude/ux2-phan-hoi-nut (NOT main: the plan is not on main),
set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt), then follow protocol
§2 for L1 and L2. Locate code by function name (_soat_ho_so_wharton, tao_so_nhap_mau, ghi_so_nhap,
taiSoNhapMau). Never ask Truong; blocked parts go under "Needs Truong" in the branch file.
```
**Checker** (Truong pastes when the branch file says READY FOR REVIEW):
```
You are CHECKER for SM2 on branch claude/sm2-mot-so-mau. Read CLAUDE.md, docs/phien/_GIAO_THUC_GON.md §3,
docs/phien/SM2_GIAO_THUC.md and docs/phien/claude__sm2-mot-so-mau.md. Set up the venv, review
origin/claude/ux2-phan-hoi-nut..origin/claude/sm2-mot-so-mau per protocol §3, write the verdict (NO BUGS or a numbered bug list) in
docs/phien/claude__sm2-mot-so-mau__checker.md, push only that file. Never edit product code or tests.
```
