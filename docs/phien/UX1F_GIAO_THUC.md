# UX1F protocol — fixes after integration review (lead + coder + checker)

> Item **UX1F** (Truong, 2026-11-20): answers to "Needs Truong" of `docs/phien/claude__ux1-tich-hop.md` and
> `docs/ke_hoach/ux/UX1_DANH_GIA_TICH_HOP.md` §3. Rule 10/12 satisfied (Truong asked).
> Mechanics (message formats, quiet tests, silence): `docs/phien/GT_GIAO_THUC.md` §7, §8 ("writer" = coder).
> Branch `claude/ux1-sua-pdf`, created from `origin/claude/ux1-tich-hop` @ `2d1a547` (PR #21, open at planning time).

## 0. Truong's answers (final; do not ask again)
| # | Question | Answer | Lot |
|---|---|---|---|
| 1 | `giao_vien` not class-scoped | **Keep as is** (no change) | — |
| 2 | `pypdf` as dev-only test dependency | **Approved** | L1 |
| 3 | Slip PDF spills to near-empty 2nd page; headers break mid-word ("Huy ch/ương") | **Fix** | L2 |
| 4 | `giao_vien` cannot "Lưu PDF" for one student | **Fix: allow** | L3 |
| 5 | Two "Chọn lớp" selects on Results (`#ux1bLop`, `#kqChonLop`) | **Reduce to one** | L4 |
| 6 | Windows build overwrites release `ban-moi-nhat` | **Resolved** (no change) | — |

## 1. Lots (each: failing test first; done when its boxes hold + related tests green + `kiem_nhanh.py` 7/7)
- **L1 — pypdf.** Add `pypdf>=4,<6` to `requirements-dev.txt` ONLY (never `requirements.txt`, never `kiosk.spec`).
  The pypdf tests that skipped (`tests/test_xp1_*`, `tests/test_ux1i_i3_phieu_bao_cao.py`, any `importorskip("pypdf")`)
  must now RUN and pass on CI. Done when: CI log shows them passed, not skipped.
- **L2 — slip PDF layout** (`xuat_pdf.py` `bang`/`dung_pdf`, slip builder that calls it).
  (a) A slip of ≤ 3 sessions × ≤ 5 choices fits ONE A4 page: tighter paragraph spacing, smaller table font
  (≥ 8.5 pt), margins ≥ 12 mm; a slip that truly needs 2 pages may use 2, but the 2nd page must not be near-empty
  (no orphan footer/legend alone: keep legend + footer with the last table, `KeepTogether`).
  (b) Column headers never break inside a word: set explicit column widths that fit the longest header word at the
  header font ("Nguyện vọng", "Huy chương", "Loại CLB", "Mức vào được", "Chỗ đã nhận / tối đa"), wrap headers only
  at spaces. Tests (pypdf): `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` seed 3, 40 students of one class →
  pages ≤ 44 (was 75); no page has fewer than 200 extracted characters; extracted header text contains
  "Huy chương" and "Mức vào được" unbroken. Record pages for 800 students (`SO_NHAP_DQT_800HS_HOP_LE.xlsx`) in CHANGELOG
  (was 1519). Same data on the slip as before: content is not cut, only layout changes.
- **L3 — `giao_vien` saves ONE student's slip PDF.** `#btnGtPdfMot` (index.html) visible for `giao_vien`
  (`data-quyen`), backend `phan_quyen` already lets `giao_vien` call `export_phieu_giai_trinh_pdf`: verify, add a
  backend test (giao_vien + `student_ids=[sid]` → ok; student role → refused) and a Chromium test (teacher: search →
  pick → Lưu PDF ≤ 4 clicks). Privacy: the PDF holds only that student.
- **L4 — one class picker on Results.** Keep ONE select (keep id `kqChonLop`; `#ux1bLop` removed or made an alias that
  drives the same value) serving both the class filter of the results table and the homeroom actions ("Xuất theo
  {cohort_l}", "In phiếu cả {cohort_l}", "Báo cáo tổng hợp"). Remove the stale comment above `#ux1bPanel`. Update
  every test/selector that used `#ux1bLop` (grep tests/). Done when: exactly one "Chọn lớp" select on the Results
  page for admin and teacher (Chromium test), all homeroom actions use its value.
- **L5 — gate.** CI (Tests) green; Windows build: trigger `build-windows-exe.yml` once on the head (Truong: release
  overwrite is resolved). User review: re-measure the 4 points above as admin and teacher, append a short "UX1F" section
  (≤ 20 lines, Vietnamese, simulated data) to `docs/ke_hoach/ux/UX1_DANH_GIA_TICH_HOP.md`.

## 2. Roles (exactly 3 sessions, no extras, no Agent tool)
| Role | Model | Does | Never |
|---|---|---|---|
| lead | Opus `claude-opus-5-5` | branch file, loop, CI gate, review, PR | writes product code |
| coder | Sonnet `claude-sonnet-5-5` | test first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO (`UX1F-L<n>`) | marks own lot passed |
| checker | Sonnet `claude-sonnet-5-5` | reviews each lot diff + 2-3 edge cases (no class, FA off, long names, 1 session) | edits product code or tests |
- Loop per lot = `UX1_GIAO_THUC.md` §4 steps 1–5 (commit prefix `UX1F-L<n>:`; verdicts in
  `docs/phien/claude__ux1-sua-pdf__checker.md`). Push a lot only after the previous CI run finished or was read.
- Stay current: before each lot `git fetch origin claude/ux1-tich-hop main`; merge `origin/claude/ux1-tich-hop`
  (or `origin/main` once PR #21 is merged). Never rebase or force-push.
- Never ask Truong; blocked part → "Needs Truong" line in the branch file, continue.

## 3. Finish
- `Status: DONE <sha> CI green <date>` + Vietnamese final summary (≤ 8 lines) in `docs/phien/claude__ux1-sua-pdf.md`.
- Open a PR: base `main` if PR #21 is merged, else base `claude/ux1-tich-hop` (title "UX1F: …"; check for a PR
  template; body ends with the attribution lines). Do not merge it.

## 4. Child prompts (lead uses verbatim; replace <LEAD_ID>)
**Coder:**
```
You are CODER for UX1F on branch claude/ux1-sua-pdf. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX1F_GIAO_THUC.md and docs/phien/claude__ux1-sua-pdf.md. Write .claude/phien_vai.json
{"vai":"impl","coord_id":"<LEAD_ID>"}, set up the venv (python3 -m venv .venv && .venv/bin/pip install -q -r
requirements-dev.txt), then wait for "GO L<n>" or "FIX" and follow UX1_GIAO_THUC.md §4 step 2 for that lot. Never
ask Truong; blocked parts go under "Needs Truong". Report in GT_GIAO_THUC §7 format.
```
**Checker:**
```
You are CHECKER for UX1F on branch claude/ux1-sua-pdf. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/UX1F_GIAO_THUC.md and docs/phien/claude__ux1-sua-pdf.md. Write .claude/phien_vai.json
{"vai":"tester","coord_id":"<LEAD_ID>"}, set up the venv, then wait for "REVIEW L<n> <base>..<head>" and check the
lot's boxes, invariants 1, 4, 6, privacy (a slip holds only its own student), teacher limits, and 2-3 edge cases of
your own. Never edit product code or tests; only docs/phien/claude__ux1-sua-pdf__checker.md. Report in
GT_GIAO_THUC §7 format.
```
