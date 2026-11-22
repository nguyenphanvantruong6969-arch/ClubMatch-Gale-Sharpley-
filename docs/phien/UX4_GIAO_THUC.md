# UX4 protocol — size M (coder + checker, no lead), per `docs/phien/_GIAO_THUC_GON.md`

> Work source: `docs/phien/claude__ux4-quan-ly-de-hieu.md` (problems, Plan L1–L4, wording proposal, acceptance).
> Truong asked for this redesign (2026-11-22). Token rules: `_GIAO_THUC_GON.md` §3. Where they differ, THIS file wins.

## 0. Decisions already made (do not ask again)
- UI + wording only. No backend/API/schema/algorithm change; no new library. Keep every element id.
- New sub-tab "Cách xếp" holds the rules panel + trial runs (moved out of the "Nâng cao" fold).
- i18n: change existing keys' text in place (vi + en); new keys prefix `ux4_`; CSS block `/* UX4 */`;
  tests `tests/test_giao_dien_ux4_*.py` (one Chromium file per lot, one shared page fixture).
- Words are Truong's call: L1 sheet is approved BEFORE L2–L4 code.

## 1. Branch, lots
| Branch | Lots | Review |
|---|---|---|
| `claude/ux4-quan-ly-de-hieu` (from `claude/bold-clarke-ur1g35`) | L1 words → L2 structure → L3 CLB + Học sinh → L4 Cách xếp (+ optional score panels) | Milestone 1 after L1 (Truong), Milestone 2 after L4 (checker + Truong) |
- Optional parts of L4 (Điểm quyết tâm, Điểm chuẩn wording) may be dropped without asking.
- Max 2 FIX rounds per review, then "Needs Truong" + `git revert` of that lot.

## 2. Roles
| Role | Model | Does | Never |
|---|---|---|---|
| Coder | Sonnet | L1–L4, tests first, CI gate (`kiem_nhanh.py` 7/7, related tests, ruff), CHANGELOG + TIEN_DO row `UX4-L<n>`, commit `UX4-L<n>: …`, push | edit backend/algorithm; full suite locally |
| Checker | Sonnet | At each milestone: read diff, run the lot's tests + 3 screenshots (deviceScaleFactor 1), check acceptance list, write `docs/phien/claude__ux4-quan-ly-de-hieu__checker.md` | edit product code |

## 3. Messages (one line; details in the files)
- Coder → Truong: `MILESTONE 1 READY: docs/ke_hoach/ux/UX4_TU_NGU.md` (then WAIT for Truong's edits/approval).
- Coder → Truong: `MILESTONE 2 READY | base <sha> head <sha>` → Truong pastes the checker prompt.
- Checker → Truong: `PASS` or `FIX: <n> items (see __checker.md)`.

## 4. Checker prompt (Truong pastes at milestone 2)
You are the UX4 checker (Sonnet) on `claude/ux4-quan-ly-de-hieu`. Read CLAUDE.md, `docs/phien/UX4_GIAO_THUC.md`,
the branch file. Review `git diff <base>..<head>` only. Run `tests/test_giao_dien_ux4_*.py` + `tests/test_ws_nhan.py`
+ `tests/test_i18n_sync.py`. Take 3 screenshots of the Quản lý tab (CLB, Cách xếp, Làm lại từ đầu) with sample data.
Check: acceptance list; approved words used exactly; no id removed; EN mirrors VI; no backend file changed
(`git diff --stat` shows only index.html, style.css, i18n.js, js/*.js, tests, docs). Write findings to
`docs/phien/claude__ux4-quan-ly-de-hieu__checker.md`, reply one line `PASS` / `FIX: <n>`. Reply in Vietnamese to Truong.
