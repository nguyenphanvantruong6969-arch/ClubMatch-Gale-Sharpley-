# UX5 protocol — two independent tracks, size M each (coder + checker, no lead), per `_GIAO_THUC_GON.md`

> Truong (2026-11-22): apply Hick's law + Von Restorff (rules in `docs/phien/claude__ux4-quan-ly-de-hieu.md`,
> sections "Design rule") to the other sidebar groups. UI + wording only, no backend. Tracks run in parallel, never talk.
> Token rules: `_GIAO_THUC_GON.md` §3. Where they differ, THIS file wins.

## 0. Decisions already made (do not ask again)
- Both laws apply exactly as written in the UX4 branch file (budgets, one gold `.btn-primary` per visible panel, red only
  for danger, "Đề xuất" badge on the default, hidden-not-disabled, nothing removed, every element id kept).
- UI + wording only. No backend/API/schema/algorithm change; no new library; keep sector placeholders (`{person_l}` ...).
- **Teacher side is in scope.** For every tab the track owns, also check `body[data-vai="giao_vien"]` (admin-only parts
  carry `data-quyen="quan_tri"`; the teacher sees the replacement hint, never a dead button). Budgets apply to what the
  TEACHER sees too, counted separately.
- i18n: change existing keys' text in place (vi + en); new keys prefix `ux5a_` / `ux5b_`; CSS block `/* UX5A */` or
  `/* UX5B */`; tests `tests/test_giao_dien_ux5a_*.py` / `ux5b_*`; `tests/test_ws_nhan.py` snapshot: add changed keys to
  `SUA_CO_Y` with comment `UX5A`/`UX5B`, never weaken it.
- Words are Truong's call: each track's L1 sheet is approved BEFORE L2+ code.
- Shared files (`index.html`, `style.css`, `i18n.js`, `CHANGELOG.md`, `TIEN_DO.md`): touch ONLY your own region/keys and
  append your own rows; the two branches are merged by Truong later (expect trivial conflicts only in these files).

## 1. Tracks
| Track | Branch (create from `claude/ux4-quan-ly-de-hieu`) | Owns (sidebar) | Branch file |
|---|---|---|---|
| A | `claude/ux5a-ket-qua-de-hieu` | group **Kết quả & phiếu**: tabs `results`, `others` | `docs/phien/claude__ux5a-ket-qua-de-hieu.md` |
| B | `claude/ux5b-nap-xep-nhap-tay` | groups **Nạp & xếp** (`pipeline`) and **Nhập thủ công** (`fallback`, `scoring`) | `docs/phien/claude__ux5b-nap-xep-nhap-tay.md` |
- Max 4 lots each; L1 words+choice map (stop point) → L2 structure → L3 detail → L4 teacher view + tests. Optional parts
  may be dropped without asking. Max 2 FIX rounds per review, then "Needs Truong" + `git revert` of that lot.

## 2. Roles (per track)
| Role | Model | Does | Never |
|---|---|---|---|
| Coder | Sonnet | L1–L4, tests first, CI gate (`kiem_nhanh.py` 7/7, related tests, `ruff check .`), CHANGELOG + TIEN_DO row `UX5A-L<n>`/`UX5B-L<n>`, commit `UX5A-L<n>: ...`, push | edit backend; run full suite |
| Checker | Sonnet | At milestone 2: diff review, lot tests, 3 screenshots admin + 2 teacher (deviceScaleFactor 1), write `__checker.md` | edit product code |

## 3. Messages (one line)
- Coder → Truong: `MILESTONE 1 READY: docs/ke_hoach/ux/UX5A_TU_NGU.md` (or `UX5B_...`), then WAIT for approval.
- Coder → Truong: `MILESTONE 2 READY | base <sha> head <sha>` → Truong pastes the checker prompt below.
- Checker → Truong: `PASS` or `FIX: <n> items (see __checker.md)`.

## 4. Checker prompt (Truong pastes at milestone 2; replace X by `a` or `b`)
You are the UX5X checker (Sonnet). Read CLAUDE.md, `docs/phien/UX5_GIAO_THUC.md`, `docs/phien/claude__ux4-quan-ly-de-hieu.md`
("Design rule" sections), your branch file. Review `git diff <base>..<head>` only. Run `tests/test_giao_dien_ux5X_*.py` +
`tests/test_ws_nhan.py` + `tests/test_i18n_sync.py`. Screenshots (≤ 5): each owned tab as admin, plus the teacher view of
each owned tab that a teacher can open. Count visible enabled controls per panel yourself; check acceptance list, approved
words used exactly, no id removed, EN mirrors VI, `git diff --stat` shows no backend file. Write findings to
`docs/phien/claude__ux5X-...__checker.md`, reply one line `PASS` / `FIX: <n>`. Reply in Vietnamese to Truong.
