# Branch handoff: claude/gt3-quyen-tai-lieu (writer / impl)

> Purpose: a fresh WRITER session reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, the branch file
> `claude__gt3-quyen-tai-lieu.md`, then THIS file, and continues. Language: English. Cap: 150 lines.
> Lead session: session_01YVAyu1qFUsCrfJzADRDejq. Lot specs: `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md`.

## Feature / goal
GT3 writer: implement lots L1-L4 (accounts+login, permission gate, audit log, evidence docs) one at a time on
`GO L<n>` / `FIX` from the lead; report only in the protocol section 7 formats.

## Plan (written by Opus; ticked by Sonnet)
- [x] L1 Accounts and login: WRITER DONE L1 sent (head 53e453a). Awaiting checker verdict.
- [ ] L2 Permission gate (wait for `GO L2`)
- [ ] L3 Audit log
- [ ] L4 Evidence docs

## Current state (overwrite each handoff)
- Done so far: L1 committed and pushed (53e453a). `.claude/phien_vai.json` = impl (gitignored); `.venv` exists.
- In progress: nothing. No half-finished files.
- Tests: `tests/test_gt3_tai_khoan.py` (42) + `tests/test_giao_dien_gt3_dang_nhap.py` (6) = 48 passed; related set 139 passed;
  `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7, 60/60 identical.
- Open problems: none known. Full soat-ma 4-tier eye review was only partly done (XSS via textContent, dead code, mutations).

## Decisions and gotchas (keep short)
- Session state in memory on PipelineAPI (`api._dang_nhap`, `TrangThaiDangNhap`), keyed to `db_path`; clock injectable via `api._dong_ho`.
- `get_phien_dang_nhap` does NOT refresh idle time. L2 gate must call `api._hoat_dong()` on every call (True if no accounts or live session).
  `_phien_can_co(can_quan_tri)` returns `(phien, err)` and refreshes idle time.
- Dialog opens from a sidebar button (`#tkNutMoHop`), not a Quan ly sub-tab: `test_giao_dien_quan_ly_tab_con` asserts visible tabs.
- Display text must avoid "ban/you/your/em" (`chu_cam` check in kiem_nhanh). Error `detail` is appended automatically; do not put `{detail}` in templates.
- Mutation-checked: lock threshold, idle limit, last-admin guard, db-key check.
- `git pull --no-rebase` (never rebase pushed branch).

## Next steps (ordered)
1. Wait for lead messages: `GO L2` (spec "Lot L2" in the task file, `phan_quyen.py` map `QUYEN`, central gate in PipelineAPI), then L3, L4, `FIX`.
2. Per lot: failing test, code, related tests, kiem_nhanh, soat-ma, CHANGELOG + TIEN_DO row `GT3-L<n>`, tests row in CLAUDE_CHI_TIET (300 files / 6365 cases after L1), commit, push, `WRITER DONE`.

## Files touched
- tai_khoan.py, api_tai_khoan.py: accounts logic and mixin
- api.py (mixin + `_khoi_tao_tai_khoan`), rbda_priority_pipeline.py (table `tai_khoan`), recovery.py (clear option + CLI)
- i18n_errors.py (14 `gt3_*`), i18n.js (`tk_*`), i18n_loi.js (generated), js/16_tai_khoan.js, js/_danh_sach.txt, js/08_khoi_dong.js, index.html, style.css
- tests/test_gt3_tai_khoan.py, tests/test_giao_dien_gt3_dang_nhap.py; CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Sonnet (writer) | L1 implemented, pushed 53e453a, reported to lead | handoff at context limit |
