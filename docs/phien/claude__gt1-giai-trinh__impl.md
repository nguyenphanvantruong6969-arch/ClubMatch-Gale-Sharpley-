# Branch handoff: claude/gt1-giai-trinh (writer / impl session)

> Purpose: a fresh WRITER session reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, the branch file
> `claude__gt1-giai-trinh.md`, then THIS file, and continues without the old chat.
> Language: English. Lead session: session_01TGThn8ujS9oohKhbgDiJgD. Role file: `.claude/phien_vai.json`
> = `{"vai":"impl","coord_id":"<lead id>","nguong":200000}` (gitignored; rewrite it, venv is `.venv`).

## Feature / goal
GT1 (parent C3): per-student explanation for any run (RB-DA default and FA-DAA). Lots L1-L4 in
`docs/ke_hoach/gt/GT1_GIAI_TRINH.md`. Reports/controls only: no run code path changes.

## Plan (ticked by writer; the lead ticks the branch file after checker NO BUGS)
- [x] L1 explanation engine: committed + pushed, head 6fda292, `WRITER DONE L1` sent. Awaiting checker.
- [ ] L2 lookup screen (admin/teacher)  - wait for `GO L2`
- [ ] L3 printable slip  - wait for `GO L3`
- [ ] L4 lookup codes + self-lookup mode  - wait for `GO L4`

## Current state (overwrite each handoff)
- Done so far: L1 complete. base a75a02b, head 6fda292 (pushed).
- In progress: nothing. No uncommitted work.
- Tests: `tests/test_gt1_giai_trinh.py` 24 passed; i18n sync + fa_ly_do + fa_n1 + i18n-related files 313 passed;
  `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7 (60 cases identical); ruff clean.
- Open problems: none known. Waiting for lead: `REVIEW L1` result, then `GO L2` or `FIX L1`.

## Decisions and gotchas (keep short)
- Default workspace has Wharton ON (A13.13). For plain RB-DA tests call `tests/_wharton.tat_wharton(api)` before
  loading CSV datasets (`tests/_ket_qua_bo_test.nap_bo`: nhieu_buoi, sach, can_bang). FA tests: `tests/_fa.py`.
- `get_giai_trinh_hoc_sinh` (api_xuat.py, GT1 block before `_export_ly_do_da_khoa`) replays the whole run read-only
  (`giai_trinh.dung_du_lieu_run`, locked `stb_buoi`) on every call. L3 class slips: build the replay once and loop
  `giai_trinh_mot_hoc_sinh` (pure) over students instead of calling the API per student.
- Replay uses the rules stored in `run_history.luat_xep`; FA on reuses `fa_ly_do` rows via `_doc_ly_do_moi_nhat`.
- `du_lieu_da_doi` True when: fingerprint differs, replay != stored match_results, or run_id != latest.
- Extra outcome codes beyond spec: FULL_GROUP, FULL_WHARTON. Visible text must not say "Wharton" (use "điểm
  quyết tâm"); `kiem_nhanh` chu_cam checks this.
- Each entry already has fields L2/L3 need: hang, ten_clb, diem_em, suc_chua, du_tru, da_nhan, diem_chuan(+_loai),
  stb_em (own only), duoc_xep, ma, cau, vi_tri_cho (FA). Student name is NOT in the explanation JSON; add own name
  at the API/UI layer for L2/L3.
- Use `git pull --no-rebase` (protocol), never rebase a pushed branch. Commit trailer session id: use the id from
  the attribution reminder, copied exactly.
- New test file => update the `tests/` row in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (now 299 files / 6341 cases).

## Next steps (ordered)
1. Wait for lead message (`FIX L1` or `GO L2`); read the lot section of the task file only.
2. Per lot: failing test first, minimal code, related tests, `kiem_nhanh`, soat-ma tiers, CHANGELOG + TIEN_DO row
   `GT1-L<n>`, commit `GT1-L<n>: ...`, `git pull --no-rebase && git push`, then `WRITER DONE L<n>` (protocol §7).
3. L2: new `js/14_giai_trinh.js` + `js/_danh_sach.txt` line before `08_khoi_dong` + one `<!-- GT1 -->` block in
   `index.html`; Chromium tests `tests/test_giao_dien_gt1_tra_cuu.py`.

## Files touched (L1)
- giai_trinh.py: new engine (pure explanation + in-memory replay)
- fa_ly_do.py: `cau_ly_do_rbda`
- api_xuat.py: `get_giai_trinh_hoc_sinh`, `_giai_trinh_hoc_sinh`
- i18n_errors.py, i18n_loi.js: `gt1_chua_chay`, `gt1_khong_co_hoc_sinh`
- tests/test_gt1_giai_trinh.py: 24 cases
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md: rows/counts

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Sonnet writer | L1 done, pushed, reported; handoff at ~200k context | head 6fda292 |
