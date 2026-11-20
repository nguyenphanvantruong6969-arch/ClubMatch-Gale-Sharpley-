# UX1 integration protocol (A + XP1 now, B when ready) — lead + coder + checker

> Item: UX1 integration (lot names I1–I4). Opened by Truong 2026-11-19. Rule 12 / rule 10 satisfied (Truong asked).
> **Replaces `UX1_GIAO_THUC.md` §7 and §10 "Integration"**: the Team A lead does NOT integrate any more.
> Mechanics (message formats, quiet tests, silence): `docs/phien/GT_GIAO_THUC.md` §7, §8 ("writer" = coder).
> Branch: `claude/ux1-tich-hop` (created from `origin/claude/gt-tich-hop` @ `396509b`, which has CLAUDE.md rule 12).

## 0. Sources and their state at planning time (2026-11-19)
| Branch | State | Role here |
|---|---|---|
| `claude/ux1-a-giao-dien` | DONE, CI green `9fbdfdf` | merge in I1 |
| `claude/xp1-xuat-pdf` | IN PROGRESS (L1–L3 passed, L4 in review, L5 left) | merge in I2 once its branch file says `Status: DONE` |
| `claude/ux1-b-phieu` | NOT STARTED (based on A @ `dd43bdc`) | merge in I3 once `Status: DONE`; may be left out (see §3) |

## 1. Roles (exactly 3 sessions, no extras, no Agent tool)
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | branch file, merges (`git merge --no-ff`), waits, loop, CI gate, review | resolves conflicts in product code itself |
| coder | Sonnet `claude-sonnet-5-5` | resolves conflicts, wiring, tests, `soat-ma`, CHANGELOG/TIEN_DO | marks own lot passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews each lot diff + edge cases, verdict file | edits product code or tests |
- First action of the lead: `send_message` to the Team A lead `session_01TGThn4GicB4XGX5L6zfZ57`:
  "UX1 integration moved to claude/ux1-tich-hop (docs/phien/UX1_TICH_HOP_GIAO_THUC.md). Do not run §7; you may stop."
  If that session is gone, ignore.
- Never ask Truong; blocked part → one line under "Needs Truong" in the branch file, continue.

## 2. Lots (loop per lot = UX1_GIAO_THUC §4 steps 1–5; commit prefix `UX1I-I<n>:`)
- **I1 — merge A.** Lead: `git merge --no-ff origin/claude/ux1-a-giao-dien`. Coder resolves conflicts (keep both
  sides' lines; `python tao_i18n_js.py`; CHANGELOG/TIEN_DO keep all rows, newest first). Done when: related tests of A
  (`tests/test_giao_dien_ux1_*`, `test_ux1_*`, `test_khoi_dong_backend.py`, `test_ws_nhan.py`,
  `test_van_phong_tu_nhien.py`, `test_gt4_nhat_ky_doc.py`, `test_gt_tich_hop.py`) green; `kiem_nhanh.py` 7/7 vs `origin/main`.
- **I2 — merge XP1.** Wait with `send_later` 60 min until `origin/claude/xp1-xuat-pdf` branch file says
  `Status: DONE` (read it with `git show`; never edit that branch). Then merge it. Coder: XP1's three PDF items sit in
  A's "Xuất…" menu; single-student "Lưu PDF" on the lookup card ≤ 4 clicks; slip rows show club type
  (`loai`). Done when: XP1 tests (`tests/test_xp1_*`, `test_giao_dien_xp1_*`) + I1 set green; 7/7.
- **I3 — merge B (only if B is DONE, see §3).** Merge `origin/claude/ux1-b-phieu`. Coder: slip table has BOTH
  XP1's "Loại CLB" column and B's medal column (type first, then medal); "In phiếu cả {cohort_l}" on the homeroom page
  calls XP1 `export_phieu_giai_trinh_pdf(theo_lop=...)` for the chosen class; "Báo cáo tổng hợp" also offered as PDF via
  `xuat_pdf.py`; both reachable by a `giao_vien` in ≤ 2 clicks; regenerate `docs/giai_trinh/CA_MAU.md`
  (`du_lieu_test/tao_ca_mau_giai_trinh.py`) and the evidence pack. Done when: B tests + I1/I2 sets green; 7/7.
- **I4 — CI gate + review.** CI per UX1_GIAO_THUC §5 (Tests + Windows build) until green, then §6 review written to
  `docs/ke_hoach/ux/UX1_DANH_GIA_TICH_HOP.md` (clicks per task, PDF pages read as a homeroom teacher).

## 3. Waiting rules
- XP1 not DONE after 24 h of waiting: list it under "Needs Truong", go on to I3 if possible, come back after.
- B not DONE when I2 is green: do I4 with A + XP1 only, set `Status: DONE (A+XP1; B pending)`, list "merge B (I3)" under
  "Needs Truong", archive children, stop. A later session reopens this branch and runs I3 + I4 again.
- Stay current before each lot: `git fetch origin claude/gt-tich-hop main && git merge --no-edit origin/claude/gt-tich-hop`.
  Never rebase or force-push. Truong merges to `main` himself (pull request), not the lead.

## 4. Handoff
Branch file `docs/phien/claude__ux1-tich-hop.md` ≤ 60 lines: Status, Plan (I1–I4 ticked), Current state (3 lines),
Sessions table, Needs Truong, Final summary in Vietnamese (≤ 10 lines: what is merged, CI link, review file, 3 things
Truong should try by hand incl. the Windows exe PDF export). `__coder.md` / `__checker.md` ≤ 30 lines.

## 5. Child prompts (lead uses verbatim; replace <LEAD_ID>)
**Coder:**
```
You are CODER for UX1 integration on branch claude/ux1-tich-hop. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX1_TICH_HOP_GIAO_THUC.md and docs/phien/claude__ux1-tich-hop.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO I<n>" or "FIX" and follow UX1_GIAO_THUC.md §4 step 2 for that lot. Never
ask Truong; blocked parts go under "Needs Truong". Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for UX1 integration on branch claude/ux1-tich-hop. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX1_TICH_HOP_GIAO_THUC.md and docs/phien/claude__ux1-tich-hop.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW I<n> <base>..<head>" and check the
lot's "Done when", invariants 1, 2, 4, 6, 7, privacy (slips show only their own student; member lists no scores),
teacher role limits, and 2-3 edge cases of your own. Never edit product code or tests; only
docs/phien/claude__ux1-tich-hop__checker.md. Report in GT_GIAO_THUC §7 format.
```
