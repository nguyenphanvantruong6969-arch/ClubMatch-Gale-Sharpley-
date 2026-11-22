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
| Checker | Sonnet | Spawned by the coder after L4 (§3): diff review, lot tests, 3 screenshots admin + 2 teacher (deviceScaleFactor 1), write `__checker.md` | edit product code |

## 3. Auto-check loop (Truong, 2026-11-22: explicit OK to spawn sessions; overrides CLAUDE.md rule 10 for UX5 only)
After L4 (milestone 2) the CODER starts the checker itself, then waits:
1. Coder: `get_session` (no id) -> own `session_id`; push all commits; note `base`/`head` shas.
2. Coder: `create_session` (NOT the Agent tool): `source_url` = this repo, `source_revision` = own branch,
   `outcome_branch` = own branch, `model` = sonnet, `title` = `UX5X checker round <n>`, `prompt` = checker prompt (§4)
   with `<base> <head> <coder_session_id> <round>` filled in. Then END the turn (do not poll or sleep).
3. Checker: reviews, writes `docs/phien/claude__ux5X-...__checker.md`, commits + pushes it to the branch, then
   `send_message` to the coder session id: `PASS` or `FIX: <n> items (see __checker.md)`. The checker never edits product code.
4. Coder wakes on that message: on `FIX`, fix only the listed items, run the related tests, commit `UX5X-FIX<round>: ...`,
   push, spawn a NEW checker (round + 1) as in step 2. On `PASS`: update "Current state", append a TIEN_DO row, push,
   report `DONE` to Truong. Stop.
- **Max 2 FIX rounds.** After round 2 still `FIX`: `git revert` the offending lot, write "Needs Truong" in the branch
  file, stop and report to Truong.
- Milestone 1 (words approval) is NOT looped: the coder still stops and waits for Truong.
- Messages stay one line; details live in the `__checker.md` file.

## 4. Checker prompt (filled in by the coder; X = `a` or `b`)
You are the UX5X checker (Sonnet), round <round>, on branch `claude/ux5X-...` (checked out for you). Read CLAUDE.md,
`docs/phien/UX5_GIAO_THUC.md`, `docs/phien/claude__ux4-quan-ly-de-hieu.md` ("Design rule" sections), your branch file.
Review `git diff <base>..<head>` only. Run `tests/test_giao_dien_ux5X_*.py` + `tests/test_ws_nhan.py` +
`tests/test_i18n_sync.py`. Screenshots (<= 5, deviceScaleFactor 1): each owned tab as admin, plus the teacher view of each
owned tab a teacher can open. Count visible enabled controls per panel yourself; check the acceptance list, approved words
used exactly, no id removed, EN mirrors VI, `git diff --stat` shows no backend file. Write findings to
`docs/phien/claude__ux5X-...__checker.md`, commit and push it, then `send_message` to session `<coder_session_id>` with one
line `PASS` or `FIX: <n> items (see __checker.md)`. Never edit product code. Reply in Vietnamese.
