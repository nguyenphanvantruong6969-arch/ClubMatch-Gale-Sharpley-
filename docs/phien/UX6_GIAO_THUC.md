# UX6 protocol — make the UI look intentional, not generated (size M: coder + checker, no lead)

> Source: design review 2026-11-27 (screenshots of the real app, 120-student Sổ, seed 42). Budget and review rules:
> `docs/phien/_GIAO_THUC_GON.md` (do not copy it here). Branch `claude/ux6-giao-dien-gon`, created from
> `origin/claude/hopeful-cannon-urfiul` (holds this plan). Branch file: `docs/phien/claude__ux6-giao-dien-gon.md`.
> UX6 is a new UI code outside the 33-item registry, like UX1–UX5.

## 0. Decisions (do not ask Truong again)
- **UI only.** Allowed: `index.html`, `dang_ky.html`, `style.css`, `i18n.js`, `js/*.js`, `tests/`, `CHANGELOG.md`,
  `docs/`. Any `*.py` change at repo root, schema, CSV contract or `i18n_errors.py` = stop and ask (rule 7).
  If a screen needs data the API does not return yet, show what IS returned; do not add backend.
- **Copy rule (L1).** A helper sentence stays only if it (a) warns before an irreversible action, (b) explains an
  error or blocked state, or (c) states a required input format. Everything else is deleted, or moved behind a
  small "?" button (`<details>` or `title`) when it holds a fact the user cannot see elsewhere. Target: ≤ 25
  elements with class `hint-text` / `view-desc` / `hint` left in `index.html` (78 today). Delete the key from BOTH
  vi and en in `i18n.js` when its text goes; `tests/test_i18n_sync.py` must pass.
- **Tests.** A Chromium test that asserts deleted COPY may be updated (list each in CHANGELOG). A test that asserts
  BEHAVIOUR (role hiding, target size ≥ 44 px, focus ring, contrast, keyboard path) may not be weakened. Max 2 FIX
  rounds per review, then "Needs Truong" + `git revert` of that lot.
- All screenshots/numbers come from SIMULATED data. Do not write report commentary for the student.

## 1. Lots (L1–L3 must-ship; L4 dropped)
- **L1 Less text.** Apply the copy rule on every tab (Xếp CLB, Đăng ký, Nhập nguyện vọng/điểm, Kết quả, Chi tiết,
  Quản lý + sub-tabs, Cài đặt). Next-step banner (`js/17_viec_tiep_theo.js`, `#viecTiepTheoCau`): one short line
  + one button whose label does not repeat the number ("32 học sinh chưa có CLB" · [Xử lý]); button aligned the
  same on every tab. Test file: `tests/test_giao_dien_ux6_l1.py` (counts helper elements ≤ 25; banner layout).
- **L2 Screens follow state + less card soup.** Xếp CLB: after a Sổ is imported, `#dropZone` is replaced by a
  one-line summary (counts + import/run time from data already loaded, + [Đổi sổ] that brings the drop zone
  back); finished steps collapse to one line with ✓ and can be reopened; a blocking warning keeps its step open.
  `#statusStrip`: "88/120 đã có CLB" + thin progress bar; the unplaced count is a button calling the same handler
  as the banner. Kết quả: the results table is not wrapped in a card and spans the content width; "Xuất theo lớp" /
  "Báo cáo và phiếu in" / "Tải bảng này" move to one toolbar above the table; lookup box stays on top. Test file:
  `tests/test_giao_dien_ux6_l2.py` (empty DB shows drop zone; after import+run it is hidden and summary shows 120;
  [Đổi sổ] shows it; strip text; strip button = banner action; teacher role still sees only allowed controls).
- **L3 Consistent details.** `.brand-mark`: `logo.svg` instead of the "RB" text. Results segmented control uses the
  same accent, size and font as the other tab controls. Replace text glyphs used as icons ("▾", "⋯", "…" on
  buttons) with inline SVG + `aria-label`; the "⋯" button gets a visible tooltip/label. Monospace only for machine
  codes (workspace label and other UI labels → body font). Table headers: sentence case, no letter-spacing.
  Quản lý → Danh sách CLB: club id shown as small secondary text under the name (not its own column; still
  selectable for copying); per-row "Xoá" becomes an icon button with `aria-label`, visible on row hover AND
  keyboard focus, keeping the existing two-step confirm and ≥ 44 px target. `dang_ky.html` first-time setup:
  example placeholders, Khối thấp/cao side by side, button not full width. Test file:
  `tests/test_giao_dien_ux6_l3.py` (no "▾"/"⋯" text in buttons; brand shows an image; delete reachable by keyboard).
- **L4 dropped** (Truong, 2026-11-27): no document moves, no repo tidy in UX6.

## 2. Truong's answers (2026-11-27)
- No document moves anywhere. L4 skipped. Repo rename is not part of UX6.

## 3. Milestones (checker, `_GIAO_THUC_GON.md` §1 size M)
- **M1** after L1+L2: coder writes `MILESTONE 1 READY`. **M2** after L3: `MILESTONE 2 READY`.
- Checker verdict PASS / FIX (≤ 2 rounds) in `docs/phien/claude__ux6-giao-dien-gon__checker.md`; at M2 it takes
  ≤ 3 screenshots (Xếp CLB after run, Kết quả, Quản lý → CLB; `deviceScaleFactor: 1`) and compares with the
  pre-UX6 look described in the branch file.
- Gate before each milestone: lot tests + `tests/test_i18n_sync.py` + ≤ 3 related UX2/UX5 Chromium files,
  `ruff check .`, `kiem_nhanh.py | tail -10`, `git diff --stat origin/claude/hopeful-cannon-urfiul -- '*.py' ':!tests'`
  is EMPTY. Before push: skill `soat-ma` (rule 8). CI must be green.

## 4. Prompts
**Coder (Sonnet) — first session prompt:**
See the code block at the end of the branch file.

**Checker (Sonnet) — Truong pastes when `MILESTONE <k> READY`:**
"You are the UX6 checker. Read CLAUDE.md, `docs/phien/UX6_GIAO_THUC.md`, `docs/phien/claude__ux6-giao-dien-gon.md`.
`git fetch origin claude/ux6-giao-dien-gon`, check milestone <k> against §0–§1 and the Done-when list of the branch
file: run the gate in §3, check no backend file changed, check each deleted hint against the copy rule (sample ≥ 10),
check vi and en render without raw keys. Write PASS or FIX with numbered items in
`docs/phien/claude__ux6-giao-dien-gon__checker.md`, commit, push, reply one line. Do not edit product code."
