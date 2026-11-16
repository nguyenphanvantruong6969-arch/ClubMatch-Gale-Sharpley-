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
- [x] L1 explanation engine (+ fix1) - passed
- [x] L2 lookup screen (+ fix1) - passed
- [x] L3 printable slip - passed (ticked 807499d)
- [x] L4 lookup codes + self-lookup mode (+ fix1 late-reply guard) - checker NO BUGS, lead ticked 5c166ce
- [ ] CI gate (§6): FIX CI round 1 pushed at a3a9cf9 (`WRITER DONE CI fix1` sent); wait for lead's next CI result / FIX

## Current state (overwrite each handoff)
- Done: L1-L4 all passed review. CI fix1 (3 groups) pushed, head a3a9cf9 on claude/gt1-giai-trinh.
- In progress: nothing; no uncommitted work.
- Last CI run seen: run 43805857085 on 5c166ce (lint green, Linux 1/2/3 red; fixed in a3a9cf9: van_phong_tu_nhien strings,
  role=dialog permanently in DOM, gt1_* codes in test_ws_nhan allowlist). Windows result unknown; new run triggered by push.
- Tests: GT1 files (giai_trinh 26, phieu 9, ma_tra_cuu 13, giao_dien tra_cuu 7, giao_dien hoc_sinh 9) pass; related sets 552 + 127 + 797 passed;
  kiem_nhanh 7/7 (60 cases identical); ruff clean.
- tests/ row in CLAUDE_CHI_TIET.md: 303 files / 6381 cases.

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
- Use `git pull --no-rebase` (protocol), never rebase a pushed branch. New test file => update tests/ row in CLAUDE_CHI_TIET.md.

- L4: codes via `ma_tra_cuu.py` (secrets); lockout state in `PipelineAPI.__dict__["_gt1_luot_sai_d"]`, clock `_gt1_dong_ho` (tests replace it).
  Overlay `#gtHs`: other body children get `inert`; `role=dialog` only while open; `luotHs` token drops late replies (send, clear, open, exit).
- UI text rules (tests/test_van_phong_tu_nhien.py): no " – " / "—" joiners, no "seed"/STB, no "em/bạn/you". Any new `gt1_*` error code must also go
  into `MA_MOI_SAU_ANH_CHUP` in tests/test_ws_nhan.py (GT1 block). Chromium tests may use `page.clock.install()` for 60 s timers.
- Commit trailer session id: use `session_01TGThn8kaGCdSNUJwzjvqVX` (this writer) or the id in the NEW session's attribution reminder (check with get_session).

## Next steps (ordered)
1. Wait for lead message (`FIX CI` with failing test ids, or confirmation CI is green). Never skip/disable/weaken a test.
2. On `FIX`: failing test first/reproduce, minimal fix, run the 4 failing files + GT1 tests + `kiem_nhanh.py --co-so origin/main --so-seed 20`,
   commit, `git pull --no-rebase && git push`, report `WRITER DONE CI fix<k>` (§7 format) to the lead.
3. Anything needing Truong goes on the "Needs Truong" list in the branch file (none from the writer so far).

## Files touched (L1-L4 + CI fix)
- giai_trinh.py, phieu_giai_trinh.py, ma_tra_cuu.py (new); fa_ly_do.py; api_xuat.py (GT1 blocks: explanation, slip, L4 code APIs)
- api_quan_ly.py (search_students; delete_student/reset_data also delete ma_tra_cuu); rbda_priority_pipeline.py (table ma_tra_cuu after giu_cho)
- js/14_giai_trinh.js, js/_danh_sach.txt, index.html (GT1 panel + #gtHs overlay), i18n.js (gt_*), style.css, i18n_errors.py + i18n_loi.js (gt1_*)
- tests: test_gt1_giai_trinh/phieu/ma_tra_cuu.py, test_giao_dien_gt1_tra_cuu/hoc_sinh.py, test_ws_nhan.py (allowlist block); CHANGELOG, TIEN_DO, CLAUDE_CHI_TIET

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Sonnet writer | L1 done, pushed, reported; handoff at ~200k context | head 6fda292 |
| 2026-11-16 | Sonnet writer 2 | L1 fix1, L2 (+fix1), L3 done and pushed; handoff at ~200k | head 35a16d2 |
| 2026-11-16 | Sonnet writer 3 | L4 (+fix1) done, CI fix1 pushed (a3a9cf9); handoff on hook | head a3a9cf9 |
