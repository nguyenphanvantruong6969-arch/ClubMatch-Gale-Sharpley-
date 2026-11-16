# Branch handoff: claude/gt1-giai-trinh (writer / impl session)

> Purpose: a fresh WRITER session reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, the branch file
> `claude__gt1-giai-trinh.md`, then THIS file, and continues without the old chat.
> Language: English. Lead session: session_01TGThn8ujS9oohKhbgDiJgD. Role file: `.claude/phien_vai.json`
> = `{"vai":"impl","coord_id":"session_01TGThn8ujS9oohKhbgDiJgD","nguong":200000}` (gitignored; rewrite it; venv is `.venv`,
> create with `python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt` if missing).

## Feature / goal
GT1 (parent C3): per-student explanation for any run (RB-DA default and FA-DAA). Lots L1-L4 in
`docs/ke_hoach/gt/GT1_GIAI_TRINH.md`. Reports/controls only: no run code path changes.

## Plan (ticked by writer; the lead ticks the branch file after checker NO BUGS)
- [x] L1 explanation engine (+ fix1) - lead ticked, passed
- [x] L2 lookup screen (+ fix1 stale search) - lead ticked 47b5751, passed
- [x] L3 printable slip: committed + pushed, head 35a16d2, `WRITER DONE L3` sent. Awaiting checker.
- [ ] L4 lookup codes + self-lookup mode  - wait for `GO L4` (or `FIX L3`)

## Current state (overwrite each handoff)
- Done so far: L1, L2 passed review. L3 done: base 47b5751, head 35a16d2 (pushed).
- In progress: nothing. No uncommitted work.
- Tests: tests/test_gt1_phieu.py 9, test_giao_dien_gt1_tra_cuu.py 7, test_gt1_giai_trinh.py 26 passed; related set 120
  passed; `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7 (60 cases identical); ruff clean.
- tests/ row in CLAUDE_CHI_TIET.md: 301 files / 6359 cases.
- Open: lead should confirm decision below (appeal days only when fa_khieu_nai ON).

## Decisions and gotchas (keep short)
- Default workspace has Wharton ON; for plain RB-DA tests call `tests/_wharton.tat_wharton(api)` before loading data. FA tests: `tests/_fa.py`
  (`bat_fa` REPLACES rules, so write extra rules via `cau_hinh_ws.ghi_cau_hinh` AFTER it; FA needs one GIOI_HAN + one TU_DO club per buoi).
- `api_xuat._giai_trinh_dung_lai(run_id)` builds the replay once -> `(du_lieu, {sid: (name, class)})` or a `_fail` dict. Only the latest run
  is explainable (`gt1_lan_chay_cu`); unknown run -> `gt1_khong_tim_thay_lan_chay`. `_giai_trinh_them_ten` adds own name/class.
- `phieu_giai_trinh.dung_phieu_html(cac_em, so_ngay)`: `cac_em` = `[(giai_trinh_one, (sid, name, lop), ma_tra_cuu_or_None)]`. L4 should pass the
  code as 3rd item (and `export_phieu_giai_trinh` must look codes up from `ma_tra_cuu`); empty `<div class="ma-tra-cuu">` is the placeholder.
- Appeal days printed only when `_co_khieu_nai()` is ON (stored run rules lack it; default 3 exists even when off). Slip is Vietnamese-only.
- UI: `js/14_giai_trinh.js` IIFE; `luotTim` token cancels stale searches (card DOM must hold ONE student). `.search-row` is display:flex so
  `[hidden]` needs a CSS rule. UI strings must avoid "em/bạn/you/Wharton" (kiem_nhanh `chu_cam`). `i18n.js` keys `gt_*` (vi + en).
- Chromium tests: `tests/test_giao_dien_gt1_tra_cuu.py` pattern (`mo` fixture, `_dung`, `_tra`); wait for specific text, not just a selector.
- Commit trailer session id: `session_01TGThn4KfT4gVBLHBdZiZXv`... use the id from the attribution reminder of the NEW session, copied exactly.
- Use `git pull --no-rebase` (protocol), never rebase a pushed branch. New test file => update tests/ row in CLAUDE_CHI_TIET.md.

## Next steps (ordered)
1. Wait for lead message (`FIX L3` or `GO L4`); read the lot section of the task file only.
2. L4: table `ma_tra_cuu` after the `giu_cho` block (CREATE TABLE IF NOT EXISTS, idempotent); APIs `tao_ma_tra_cuu`, `tao_lai_ma_tra_cuu`,
   `export_ma_tra_cuu_csv`, `tra_cuu_hoc_sinh` (secrets, hmac.compare_digest, 5 tries -> 60 s lock, `gt1_ma_sai`, `gt1_tam_khoa`);
   slip prints the code; overlay UI "Chế độ học sinh tra cứu" (60 s idle clear, exit confirm). Tests `tests/test_gt1_ma_tra_cuu.py`,
   `tests/test_giao_dien_gt1_hoc_sinh.py`.
3. Per lot: failing test first, minimal code, related tests, `kiem_nhanh`, soat-ma tiers, CHANGELOG + TIEN_DO row, commit, push, `WRITER DONE`.

## Files touched (L1-L3)
- giai_trinh.py, phieu_giai_trinh.py (new); fa_ly_do.py (`cau_ly_do_rbda`); api_xuat.py (GT1 block: get/export APIs, replay helpers)
- api_quan_ly.py: `search_students(query, lop=None)`
- js/14_giai_trinh.js, js/_danh_sach.txt, index.html (GT1 block), i18n.js (`gt_*`), style.css (GT1 rules)
- i18n_errors.py + i18n_loi.js: gt1_khong_co_hoc_sinh, gt1_chua_chay, gt1_lan_chay_cu, gt1_khong_tim_thay_lan_chay
- tests: test_gt1_giai_trinh.py, test_gt1_phieu.py, test_giao_dien_gt1_tra_cuu.py; CHANGELOG.md, TIEN_DO.md, CLAUDE_CHI_TIET.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Sonnet writer | L1 done, pushed, reported; handoff at ~200k context | head 6fda292 |
| 2026-11-16 | Sonnet writer 2 | L1 fix1, L2 (+fix1), L3 done and pushed; handoff at ~200k | head 35a16d2 |
