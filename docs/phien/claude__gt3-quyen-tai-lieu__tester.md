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

## L2 fix1 — reviewed 22fb361..5208c6d — verdict: NO BUGS
Bug 1 fixed (per-db cache `_co_tk_nho`, primed in `__init__`, unread DB + read error => accounts ON). Verified with accounts
present, never-read cache and errors: "database is locked", "unable to open database file", "disk I/O error", "malformed",
"no such column", a non-sqlite RuntimeError, and a real exclusive lock held by a second connection => all
`gt3_can_dang_nhap` (closed). Only "no such table" => OFF (legacy DB without the table => OFF; cannot be triggered by a lock
message). Error after an earlier success uses the cached True. DB switch (as `open_workspace` does): db2 without accounts =>
OFF, back to db1 => ON and gated, never-read db3 + read error => ON; login session is bound to its DB (gone after switch).
Related tests 124 passed (L2 + L1 + do_api + browser_host); `ruff` clean; `kiem_nhanh` 7/7.

## L3 — reviewed 656c12a..7fcba6a — verdict: 1 BUG
Ran: `test_gt3_nhat_ky`, `test_giao_dien_gt3_dang_nhap`, `test_gt3_phan_quyen`, `test_gt3_tai_khoan`, `test_ws_nhan`, `test_do_api` ->
151 passed; `ruff` clean; `kiem_nhanh` 7/7. Own scripts (fake data, scratchpad) confirmed:
- `test_ws_nhan` edit is a legitimate allowlist extension (`ws_` -> `ws_`/`gt3_` for NEW codes); the assertion that every existing
  message is unchanged (`lech`) is untouched. Not weakened.
- Accounts OFF: 0 rows (login attempts, reset_data, create_student). First `tao_tai_khoan` logs 1 row (author logged in): fine.
- No secret in any row: wrong passwords, `mat_khau=` kwarg, odd kwarg `pw_xx`, `doi_mat_khau` (params `{}`), a password typed into the
  name field (`chi_tiet` `{}` because not a real account), `tao_tai_khoan` rows keep only ten/vai.
- UPDATE and DELETE abort (trigger message). `reset_data` (hoc_sinh and tat_ca, accounts ON and OFF) works; log rows kept.
- Failing log write (`OperationalError` inside `ghi`): action result/login result unchanged, no exception to caller, only a log warning.
- Exactly one row for: config change, run_pipeline, failed login, logout (none when already logged out); anonymous denied write =
  1 row (`gt3_can_dang_nhap`, nguoi NULL); teacher denied/allowed writes = 1 row each; reads (get_*) = 0 rows.
- Pagination (newest first, last page, beyond range = empty, bad args clamp), filters (exact), SQL-injection string = 0 rows,
  CSV UTF-8 BOM with Vietnamese intact, formula guard on a user name starting with `=`. Teacher cannot view/export (`gt3_khong_du_quyen`).
### Bug
1. `phan_quyen.py:_boc` (+ `_ghi_nhat_ky`/`nk.ghi` use `api.db_path` AFTER the call) | repro: accounts ON in workspace A; admin calls
   `create_workspace("B")` then `open_workspace(slug)`; the row for `open_workspace` is written into workspace B's DB (which has NO
   accounts): B now holds 1 audit row although accounts are OFF there, and A has no record of the switch | expected: write the row
   to the DB that was current BEFORE the call (capture `db_path` before running; pass it to `ghi`), so A logs the switch and an
   accounts-OFF workspace stays at zero rows. Same for any method that changes/removes the open DB (e.g. `delete_workspace` of the open one).
### Notes (not bugs)
- A denied/anonymous/teacher call now writes a row and therefore waits on `_khoa_ghi` (measured 2.8 s while another thread held it):
  during a long `run_pipeline` denied clicks and failed logins hang until the run ends. Acceptable for a kiosk; consider a short timeout.
- Filter `nguoi` is exact and case-sensitive; anonymous rows (nguoi NULL) cannot be filtered by name.

## L3 fix1 — reviewed 7fcba6a..ff12579 — verdict: NO BUGS
Bug 1 fixed: after `create_workspace` + `open_workspace` the row lands in the PRE-call DB (+1 there, 0 in the new workspace).
Deferred write (`ghi` waits <= 1 s on `_khoa_ghi`, then a daemon thread writes): denied call returns in 1.00 s while another
thread holds the lock; the row appears after release; 6 concurrent denied calls during a held lock -> exactly 6 rows (no
duplicates); DB file deleted while a write is pending -> warning only, file NOT recreated, thread ends, no crash.
`nguoi` filter now matches NFC/NFD/any case of an account name (3/3/3) and 0 for unknown.
Related tests 155 passed; `ruff` clean; `kiem_nhanh` 7/7.
Note (not a bug): a deferred row is lost if the process exits within milliseconds of the lock release (daemon thread); only
affects calls that were made concurrently with a long run, never the run's own row (written synchronously).
