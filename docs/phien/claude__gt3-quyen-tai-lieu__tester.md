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

## L2 — reviewed 9f70aff..22fb361 — verdict: 1 BUG
Ran: `test_gt3_phan_quyen`, `test_giao_dien_gt3_phan_quyen`, `test_gt3_tai_khoan`, `test_giao_dien_gt3_dang_nhap`, `test_do_api`,
`test_browser_host` -> 116 passed; `ruff` clean; `kiem_nhanh` 7/7 (60 cases identical). Own script (fake data, scratchpad):
- Accounts OFF: wrapper vs original (`_gt3_goc`) on 7 writes (create_student_if_missing, delete_student, reset_data,
  create_or_update_club, run_pipeline, delete_club, set_student_class): identical returns/exceptions.
- No session: every non-`cong_khai` method -> `gt3_can_dang_nhap` (only staticmethods `chuan_hoa_buoi`,
  `chuan_hoa_nhom_du_tru` escape the wrapper; they are pure helpers, harmless).
- Teacher: all 40+ `quan_tri` methods -> `gt3_khong_du_quyen`, DB dump hash unchanged (denied => nothing written); reads OK.
- Admin passes the gate. Unclassified name while logged in -> denied (fail closed). `dir(PipelineAPI)` has no stale/missing names.
- Idle: calls refresh the 15 min clock (3 x 14 min stays alive), `get_phien_dang_nhap` does not; 16 min idle -> logged out.
- Nested depth: `_TL.sau` is thread-local (other thread sees 0); reset to 0 after an exception (TypeError); denied call after
  an exception still denied. No giao_vien method calls a quan_tri public method (static scan). browser_host: test passes
  (class-level wrap).
### Bug
1. `api_tai_khoan.py:_co_tai_khoan_nho` + `_khoa_tao_tai_khoan` default `_co_tk_cuoi = False` | repro: accounts exist, new
   `PipelineAPI` on that DB (app restart), first account-table read raises (e.g. "database is locked"); with no login call
   `reset_data()` -> the gate lets it through (reached its own validation `reset_confirmation_mismatch`) | expected: fail
   CLOSED — read the count once in the constructor after `init_db` (and per DB on `open_workspace`), and when a read fails with
   no earlier successful read for that DB treat accounts as ON (deny), not OFF. Also `_co_tk_cuoi` is not per DB.
### Judgement calls (not bugs)
- On-site entry methods as `giao_vien`: agree for `luu_diem_danh`, `submit_club_scores`, `submit_person_scores`, `gui_*`
  (teacher work). Mild disagreement for `submit_preferences`, `submit_huy_chuong`, `submit_test_selection`: they rewrite
  allocation inputs of ANY student with no lock; acceptable only because L3 logs them — make sure L3 logs these three
  (and the score/attendance writes), else move them to `quan_tri`.
