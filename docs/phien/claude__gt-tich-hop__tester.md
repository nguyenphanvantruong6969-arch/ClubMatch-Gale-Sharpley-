# Checker verdicts: claude/gt-tich-hop

## I0 | reviewed 64882ac..d4447a5 | verdict: NO BUGS
- Conflict markers: none (only a docstring `=======` in main.py, pre-existing). `ruff check .` clean.
- Nothing dropped: every line added by 499edf1 (GT1), 8965d2b (GT2), c66889d (GT3) vs base 35609f7 is present in
  d4447a5, except each team's own handoff file (separate files, kept) and one CLAUDE_CHI_TIET tests row (recounted: 315 files).
- Shared files: js/_danh_sach.txt has 14, 15, 16 before 08_khoi_dong; index.html has GT1/GT2/GT3 blocks and scripts;
  CHANGELOG/TIEN_DO rows for all 3 teams; api.py mixins include TieuChiMixin, TaiKhoanMixin, NhatKyMixin;
  schema names (ma_tra_cuu, ket_qua_thu, loai_chay, tai_khoan, nhat_ky_thao_tac) present.
- i18n_loi.js: regeneration produces no diff; kiem_nhanh 7/7 DAT (ruff, chu_cam, i18n, 60 cases identical vs origin/main, run_history untouched).
- Tests tests/test_gt1_*, gt2_*, gt3_* (incl. UI): 319 passed, 2 failed = the intended test_gt3_phan_quyen.py failures
  (13 GT1/GT2 methods missing from QUYEN; KeyError get_giai_trinh_hoc_sinh) -> fixed in I1.
- Not covered here: full suite (CI), invariants 2/4/5 unchanged by a merge-only lot.

## I1 | reviewed 4970006..9f5962d | verdict: NO BUGS
- (a) Test edits not weakened: the get_/list_ exemption lists exactly get_tieu_chi and list_lan_chay (plus the 2
  pre-existing names); CONG_KHAI set now = old 5 + tra_cuu_hoc_sinh; new asserts pin all 13 methods (2 giao_vien, 11 quan_tri).
- (b) Own check on real PipelineAPI, accounts ON: logged out -> only tra_cuu_hoc_sinh of the 13 passes the gate;
  giao_vien -> get_giai_trinh_hoc_sinh, export_phieu_giai_trinh, tra_cuu_hoc_sinh only (all 7 GT2 + code
  generate/regenerate/CSV refused); quan_tri -> all 13. tra_cuu_hoc_sinh itself still needs id + code (gt1_ma_sai, lockout).
- (c) Accounts OFF: no method refused by the gate; kiem_nhanh 7/7 DAT (60 cases identical).
- Tests: test_gt3_phan_quyen + all gt1/gt2 files 225 passed; test_gt3_nhat_ky + test_giao_dien_gt3_phan_quyen 31 passed.

## I2 | reviewed d31c346..67b2faf | verdict: 1 BUG
Tests: test_gt_tich_hop, test_giao_dien_gt3_hoc_sinh, gt3 phan_quyen/nhat_ky/tai_khoan + UI gt1/gt3: 132 passed. kiem_nhanh 7/7 DAT.
Own checks (real PipelineAPI, scratch script): (1) flag on -> every non-`_HS_DUOC` method refused with `gt3_che_do_hoc_sinh`
(incl. dang_nhap, dang_xuat). (3) giao_vien with correct password cannot exit, flag stays, no session left; wrong password,
wrong name, unknown name+right password return identical `gt3_sai_thong_tin`; no password in nhat_ky_thao_tac or return values
(thoat_che_do_hoc_sinh logs `{}`). (4) accounts OFF: flag never set (`khoa: False`), nothing refused. (5) admin name with
diacritics works (login is case-insensitive, pre-existing). (2) App restart: flag lost, but sessions are in memory too, so
the login screen is shown: no student exit.
BUG 1 (medium, availability not security): `api_tai_khoan.vao_che_do_hoc_sinh` flag survives a page reload (F5 in browser fallback)
but the overlay does not. After reload `dang_nhap` is refused (`gt3_che_do_hoc_sinh`, `dang_nhap` is not in `_HS_DUOC`) and no
JS re-opens the overlay, so even an admin cannot log in or exit the mode until the app process is restarted. Repro: accounts ON,
giao_vien login, vao_che_do_hoc_sinh(), reload page, try dang_nhap with admin -> refused. Expected: admin login/exit still
reachable after reload (e.g. on load, if flag on, re-open the overlay via get_phien_dang_nhap/ a status field; or allow
`dang_nhap` for quan_tri to clear the flag).

## I2 fix1 | reviewed 67b2faf..fa490c3 | verdict: 1 BUG (low)
Original bug FIXED: Chromium, accounts ON, student mode, reload -> overlay reopens by itself (flag True, no second
vao_che_do_hoc_sinh), app-shell inert, `get_run_history` refused; admin exits through the reopened overlay and tabs work.
Accounts OFF: `che_do_hs` is `bool(co and flag)` = False, unchanged. Tests 89 passed (hoc_sinh UI, tich_hop, gt3 tai_khoan/phan_quyen/UI); kiem_nhanh 7/7.
BUG 2 (low; narrow timing): stale `get_phien_dang_nhap` response reopens the overlay after a legitimate admin exit.
Repro (scratch Chromium script, response of get_phien held 1.5 s after backend answered): student mode, trigger a poll
(`tkLamMoi`/30 s interval) -> backend answers `che_do_hs: true`; before it arrives admin exits (flag False, overlay closes);
the stale reply fires `tkPhien` with `che_do_hs: true` while `hsDangMo` is false -> `js/14_giai_trinh.js` listener calls
`moLopHs()`. Result: backend flag False but overlay open and app-shell inert; the later reply (`che_do_hs: false`) does
not close it. Admin can recover by exiting again. Expected: ignore replies older than the exit (sequence counter in
capNhat, or re-ask `get_phien_dang_nhap` before reopening, or close the overlay when `che_do_hs` is false and it was reopened by the poll).
Real-world window is only a few ms per 30 s poll.

## I2 fix3 | reviewed 2abdd09..cbcc10b | verdict: NO BUGS
Stale-reply race re-run with the same scratch Chromium script (reply held 1.5 s): after admin exit and after polls settle,
flag False, overlay hidden, app-shell not inert (was: overlay open + inert). js/16 request counter drops older replies;
js/14 closes a poll-reopened overlay when che_do_hs is false. No regression: reload reopens overlay, no tab reachable,
admin exit then tab active, accounts OFF unchanged. Tests 106 passed (hoc_sinh/tich_hop/gt3 tai_khoan+phan_quyen/UI gt1+gt3);
kiem_nhanh 7/7 DAT. => I2 clean.
