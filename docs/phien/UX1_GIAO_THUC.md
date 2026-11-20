# UX1 automation protocol (2 teams × lead + coder + checker)

> Source of work: `docs/ke_hoach/ux/UX1_KE_HOACH.md` (lots) and `docs/ke_hoach/ux/UX1_RA_SOAT.md` (audit).
> Truong asked for these sessions explicitly (CLAUDE.md rule 10 satisfied). Base: `origin/claude/gt-tich-hop`.
> Mechanics not repeated here (message formats, quiet test command, invariant-1 command, messaging/silence): use
> `docs/phien/GT_GIAO_THUC.md` §3, §7, §8 with "writer" = coder, "GT<k>" = "UX1<A|B>". Where they differ, THIS file wins.

## 1. Teams, branches, lots
| Team | Branch | Lots (from UX1_KE_HOACH.md) | Branch file |
|---|---|---|---|
| A — screens & settings | `claude/ux1-a-giao-dien` | L1, L2 (+ `giao_vien` lands on "Kết quả & phiếu"), L2b, L3, L5, L5b, L8-A | `docs/phien/claude__ux1-a-giao-dien.md` |
| B — slip, PDF, report | `claude/ux1-b-phieu` | L4-B (builder `bao_cao_tong_hop.py` + `export_bao_cao_tong_hop` + "In phiếu cả lớp"), L6, L7, L8-B | `docs/phien/claude__ux1-b-phieu.md` |

- L8-A: user guide, demo/video scripts, poster, code map for navigation/settings; re-shoot `docs/ke_hoach/ux/anh/` screens;
  "After" click table for admin/homeroom/principal tasks. L8-B: slip docs, regenerate `docs/giai_trinh/CA_MAU.md` and
  the evidence pack, regenerate `anh/04_phieu.png` + `anh/phieu_mau.pdf`, "After" row for the slip task.
- Team B places its new buttons in its own block right after `#gtPanel` in `index.html` (`<!-- UX1B -->`); Team A
  moves blocks but never deletes another team's block. Integration (§6) fixes placement.

## 2. Shared files (keep teams from colliding)
- Each team edits only its own contiguous block in shared files, marked `UX1A` / `UX1B`: `index.html`, `style.css`,
  `i18n.js` (key prefixes `ux1a_` / `ux1b_` for new keys), `i18n_errors.py` (append at the end, then
  `python tao_i18n_js.py`), `js/_danh_sach.txt` (own line before `08_khoi_dong`). Never reformat others' lines.
- `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md` (rows `UX1A-L<n>` / `UX1B-L<n>`), `docs/ke_hoach/CLAUDE_CHI_TIET.md`:
  add rows; conflicts resolved at integration.
- Stay current: `git fetch origin claude/gt-tich-hop && git merge --no-edit FETCH_HEAD` before each lot and before the
  CI gate (other work lands there). Never rebase or force-push.

## 3. Roles and session limit
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | creates the branch + branch file, creates EXACTLY two child sessions (coder, checker), runs the loop, CI gate, final user review | writes product code |
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | marks own lot passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews one lot diff, runs related tests + own edge cases, writes verdict | edits product code or tests |

- **Exactly 3 sessions per team for the whole job. No replacement or extra sessions, no Agent tool.** Context is
  summarised automatically when it grows; this overrides the "stop at 400k" part of CLAUDE.md rule 9. To survive a
  summary, keep the branch file's "Current state" and your own `__<vai>.md` up to date after every message you send.
- Never ask Truong. Blocked part (invariant conflict, new library, change outside the lot, manual Windows check) →
  one line under "Needs Truong" in the branch file, continue.

## 4. Loop per lot (in the order of §1)
1. lead → coder `GO L<n>`. 2. coder: failing test from the lot's "Done when" → minimal code → related tests →
invariant-1 check (`kiem_nhanh.py --co-so origin/main --so-seed 20` after `git fetch origin main`) → `soat-ma` →
CHANGELOG/TIEN_DO → commit `UX1<A|B>-L<n>: …` → push → `CODER DONE L<n>`. 3. lead → checker
`REVIEW L<n> <base>..<head>`. 4. checker verdict in `docs/phien/claude__<branch tail>__checker.md` (push only that
file) → `CHECKER REPORT L<n>`. 5. Bugs → `FIX L<n>` → coder → checker again (max 3 rounds, then "Needs Truong" and
move on). NO BUGS → lead ticks the lot in the branch file and pushes.

## 5. CI gate (after the last lot; repeat until green)
Lead pushes; reads GitHub Actions `tests.yml` for the head commit (`mcp__github__actions_list`, load via ToolSearch);
waits with `send_later` 30 min, never a polling loop. Red → job logs → short FIX list → coder fixes → checker reviews
the fix → push → again. A test may never be skipped, disabled or weakened. Green (lint + all shards + coverage ≥ 85 %)
→ `Status: DONE <sha> CI green <date>` in the branch file.

## 6. Final review by the lead (Opus) — user's point of view
After green: set up the venv, build the app on simulated data (`du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`,
`SO_NHAP_FA_MAU_120HS.xlsx`), drive it in Chromium as each user (admin teacher, homeroom teacher, student,
principal), count clicks against `UX1_KE_HOACH.md` §1, read every new screen and the slip PDF as a teacher would.
Write `docs/ke_hoach/ux/UX1_DANH_GIA_<A|B|TICH_HOP>.md` (≤ 80 lines, Vietnamese): targets met / missed with numbers,
top 5 problems seen as a user with a screenshot each, recommendations in priority order. Push. No report conclusions
for the student's science report (academic integrity).

## 7. Integration (Team A lead, after its own §6)
1. Every 60 min (`send_later`): `git fetch`; read `Status:` in `docs/phien/claude__ux1-b-phieu.md` on
   `origin/claude/ux1-b-phieu`. DONE → step 2. If 48 h pass and B is not DONE, integrate B's last commit with green
   CI (or none) and list the gap under "Needs Truong".
2. Create `claude/ux1-tich-hop` from `origin/claude/gt-tich-hop`; `git merge --no-ff` A, then B. Team A's coder
   resolves conflicts (keep both teams' lines; regenerate `i18n_loi.js`; put B's buttons in the new results layout);
   lot `I1` = conflicts + placement, `I2` = slip print reachable in ≤ 4 clicks from the new results screen and
   "Báo cáo tổng hợp" reachable by a `giao_vien` in ≤ 2. Same §4 loop with Team A's checker, then §5, then §6 with
   file `UX1_DANH_GIA_TICH_HOP.md`. Branch file: `docs/phien/claude__ux1-tich-hop.md`.
3. Done: `Status: DONE`, archive both children, stop. Truong merges to main himself.

## 8. Handoff files (short; Truong extracts them)
Branch file ≤ 60 lines: Status line, Plan (lots ticked), Current state (3 lines), Needs Truong (1 line each +
recommendation), Final summary in Vietnamese (≤ 10 lines: done/skipped, CI link, review file, what Truong should try
by hand in 3 steps). `__coder.md` / `__checker.md` ≤ 30 lines each.

## 9. Child prompts (lead uses these verbatim; replace <T> = A or B, <BRANCH>, <LEAD_ID>)
**Coder:**
```
You are CODER for UX1<T> on branch <BRANCH>. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX1_GIAO_THUC.md, docs/phien/claude__<branch tail>.md, then only the current lot in
docs/ke_hoach/ux/UX1_KE_HOACH.md. Write .claude/phien_vai.json {"vai":"impl","coord_id":"<LEAD_ID>"}, set up the
venv (python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt), then wait for "GO L<n>" or "FIX"
and follow protocol §4 step 2. Never ask Truong; blocked parts go under "Needs Truong". Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for UX1<T> on branch <BRANCH>. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX1_GIAO_THUC.md, docs/phien/claude__<branch tail>.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and check the
diff against the lot's "Done when" in docs/ke_hoach/ux/UX1_KE_HOACH.md, invariants 1, 2, 4, 6, 7, privacy, and 2-3
edge cases of your own (empty data, diacritics, FA on/off, no run yet). Never edit product code or tests; only
docs/phien/claude__<branch tail>__checker.md. Report in GT_GIAO_THUC §7 format.
```

## 10. Team B re-scope (Truong, 2026-11-19) — WINS over §1, §2, §7 for team B
- **Base changed:** `claude/ux1-b-phieu` already exists, created from `origin/claude/ux1-a-giao-dien` @ `dd43bdc`
  (team A DONE, CI green). Do NOT recreate it from `gt-tich-hop`. Stay current with
  `git fetch origin claude/ux1-a-giao-dien && git merge --no-edit FETCH_HEAD` before each lot (A may get fixes).
  Team A's blocks are now in the tree: edit them only in lot L5c below.
- **Dropped: L6** (print-dialog PDF) and the **club type** part of **L7** item 5. Both move to item **XP1**
  (`claude/xp1-xuat-pdf`, protocol `docs/phien/XP1_GIAO_THUC.md`, PDF engine `reportlab`). XP1 owns the `loai` key
  on each slip row and the "Loại CLB" column; team B adds only `huy_chuong` (and the legend sentence for medals).
  Put the medal column right AFTER where XP1's type column will go; whoever merges second resolves the conflict.
- **L4-B changes:** "Báo cáo tổng hợp" = builder + HTML export only (no print flow: L6 is gone). "In phiếu cả lớp" is
  NOT built by B: the class picker and "Xuất theo {cohort_l}" stay; the bulk slip button is wired to XP1's
  `export_phieu_giai_trinh_pdf(theo_lop=...)` at integration (lot I3 below). Keep the ≤ 2 clicks test for
  "Báo cáo tổng hợp" and "Xuất theo {cohort_l}".
- **New lot L5c (after L7, before L8-B): the 5 recommendations of `docs/ke_hoach/ux/UX1_DANH_GIA_A.md` §4**, in
  that order. Done when: one Chromium test per recommendation + `test_van_phong_tu_nhien.py`, `test_ws_nhan.py`,
  `test_gt4_nhat_ky_doc.py` green; invariant 1 7/7.
- **Lot order for B:** L4-B → L7 (minus type) → L5c → L8-B → CI gate (§5) → review (§6, `UX1_DANH_GIA_B.md`).
- **Integration (§7) adds XP1:** after B is DONE, merge into `claude/ux1-tich-hop` in this order: A (already in B),
  B, then `claude/xp1-xuat-pdf` if its branch file says `Status: DONE` (else list it under "Needs Truong" and stop
  after B). Extra lot **I3**: "In phiếu cả {cohort_l}" (homeroom page) calls XP1's slip PDF for the chosen class;
  "Báo cáo tổng hợp" also offered as PDF through `xuat_pdf.py`; reachable in ≤ 2 clicks by a `giao_vien`.
- **Lead prompt for team B (Truong's collaborator pastes it into a new Opus session):**
```
You are LEAD for UX1B on branch claude/ux1-b-phieu (it already exists; do not recreate it). Read CLAUDE.md, then
docs/phien/UX1_GIAO_THUC.md (§10 wins over earlier sections), docs/phien/claude__ux1-b-phieu.md and team B's lots in
docs/ke_hoach/ux/UX1_KE_HOACH.md, all on origin/claude/ux1-b-phieu, and follow them exactly. Fill the Sessions
table and push, then create the CODER and CHECKER sessions with the §9 prompts (<T> = B, <BRANCH> =
claude/ux1-b-phieu; repo https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV, source_revision
claude/ux1-b-phieu, models from §3, permission_mode auto) and run §4 for the §10 lot order, then §5 until CI is
green, then §6. Never wait for Truong; anything that needs him goes on the list.
```
