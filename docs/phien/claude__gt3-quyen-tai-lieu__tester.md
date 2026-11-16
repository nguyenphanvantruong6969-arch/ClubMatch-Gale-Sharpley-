# GT3 checker verdicts (tester)

All data fake/simulated. Checker never edits product code or tests.

## L1 — reviewed 1e39ae5..53e453a — verdict: 1 BUG (minor)

Ran: `test_gt3_tai_khoan.py`, `test_giao_dien_gt3_dang_nhap.py`, `test_giao_dien_quan_ly_tab_con.py`, `test_do_api.py` -> 62 passed.
Invariant 1: `kiem_nhanh.py --co-so origin/main --so-seed 20` -> 7/7 DAT (60 cases identical).
Own edge script (scratchpad, fake data) confirmed OK: first account must be quan_tri; no accounts -> `dang_nhap` returns
`gt3_chua_co_tai_khoan`, app unchanged; no hash/salt/password in any response (scanned); no print/logging in new files;
lock after 5 wrong = 60 s, correct password refused while locked, works at t+61; last admin undeletable; giao_vien denied
list/create/delete; anonymous denied; idle 15 min logs out; change-password wrong old/short/ok; non-string name/password
rejected; case-insensitive duplicate rejected; recovery clear backs up first (backup keeps 3 rows), missing db not created.
Sidebar button instead of a Quan ly sub-tab: acceptable (keeps the existing UI test unchanged).

### Bug
1. `tai_khoan.py:tim_ten` / `_khoa_ten` (casefold only, no Unicode normalisation) | repro: create admin `"Thầy Tâm"`
   (NFC); then, logged in as admin, `tao_tai_khoan("Thầy Tâm" in NFD form, ..., "giao_vien")` -> ok, giving two accounts
   that look identical; `dang_nhap(<NFD form>, <admin password>)` -> `gt3_sai_thong_tin`. | expected: names compared after
   `unicodedata.normalize("NFC", ...)` (in `chuan_hoa_ten` and the lookup), so the NFD duplicate is `gt3_ten_da_co` and
   an NFD-typed name logs in. Matters for Vietnamese names (macOS / some IMEs / pasted text produce NFD).
   Suggested test: create NFC name, login with NFD name succeeds; create NFD duplicate fails.

### Notes (not bugs)
- Idle refresh per API call comes with the L2 gate (as the lead said); `get_phien_dang_nhap` deliberately does not refresh.
- Lock counters are kept in memory per name (also for unknown names); reset on restart — acceptable for a kiosk.

## L1 fix1 — reviewed 53e453a..e62e24a — verdict: NO BUGS
Bug 1 fixed: names and passwords NFC-normalised (`chuan_hoa_ten`, `_khoa_ten`, `bam_mat_khau`). Re-ran own edge script:
NFD login of NFC admin name OK; NFD duplicate -> `gt3_ten_da_co`; NFD-typed password and name log in; delete via NFD name
still blocked for the last admin. Related tests 65 passed; `ruff` clean; `kiem_nhanh` 7/7 (60 cases identical); lock,
roles, idle, no-leak scan unchanged. Note: normalising passwords is safe now (L1 unreleased, no stored accounts).
