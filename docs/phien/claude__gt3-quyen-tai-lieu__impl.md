# Branch handoff: claude/gt3-quyen-tai-lieu (writer / impl)

> Purpose: a fresh WRITER session reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, the branch file
> `claude__gt3-quyen-tai-lieu.md`, then THIS file, and continues. Language: English. Cap: 150 lines.
> Lead session: session_01YVAyu1qFUsCrfJzADRDejq. Lot specs: `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md`.

## Feature / goal
GT3 writer: implement lots L1-L4 (accounts+login, permission gate, audit log, evidence docs) one at a time on
`GO L<n>` / `FIX` from the lead; report only in the protocol section 7 formats (send_message to the lead id).

## Plan (written by Opus; ticked by Sonnet)
- [x] L1 Accounts and login (passed checker; fix1 NFC done)
- [x] L2 Permission gate (passed checker after fix1: fail-closed account read)
- [~] L3 Audit log: code + tests + docs DONE and committed locally/pushed; related-test run (58 files) was still running at
      handoff; `WRITER DONE L3` NOT yet sent. See "Next steps".
- [ ] L4 Evidence docs (wait for `GO L4`)

## Current state (overwrite each handoff)
- L3 implemented: `nhat_ky.py` (redaction, nen_ghi, ghi, doc_trang), `api_nhat_ky.py` (NhatKyMixin: get_nhat_ky_thao_tac,
  export_nhat_ky_thao_tac_csv, both quan_tri), schema table `nhat_ky_thao_tac` + 2 triggers in rbda_priority_pipeline.py,
  hook in `phan_quyen._boc` (single place; denied calls logged; cong_khai login methods now wrapped too, get_phien_dang_nhap not),
  i18n (`gt3_loi_nhat_ky`, `tk_nk_*`), viewer section in the Tai khoan dialog (js/16_tai_khoan.js, admin only).
- Tests: tests/test_gt3_nhat_ky.py (24) + 1 UI case in test_giao_dien_gt3_dang_nhap.py; gt3 + phan_quyen + stress + browser_host
  = 172+ passed; ruff clean; kiem_nhanh 7/7, 60/60 identical. Count row in CLAUDE_CHI_TIET: 303 files / 6.419 cases.
- Pending: full related run output is in the old session's scratchpad (may be lost). Re-run it.
- Open: soat-ma 4-tier eye review still only partial for L1-L3.

## Decisions and gotchas (keep short)
- Gate wraps public methods at class level (`phan_quyen.ap_dung_cong`, called at end of api.py); outermost call only (thread-local depth).
  Write wrappers must NOT carry `__wrapped__` (test_a13_11_stress N4); `_gt3_goc` holds the original, `__signature__` is copied.
- Accounts cache `_co_tk_nho` per db_path; read failure with no earlier success => treated as accounts ON (fail closed).
- Audit rule `nhat_ky.nen_ghi`: everything except get_/list_/search_/xem_truoc/check_/detect_/preview_/liet_ke and a small explicit set.
  Failed login records the typed name only if it is a real account. `doi_mat_khau` records nothing. Log write failure never raises.
- Classification: on-site entry (submit_preferences, submit_huy_chuong, submit_test_selection) = giao_vien; export_workspace = quan_tri.
  Integration I1/I2 may change this. Audit viewer lives in the account dialog, not an admin sub-tab (test asserts visible sub-tabs).
- Use `git pull --no-rebase` (never rebase a pushed branch). Commit trailer session id must be copied from the system reminder.
- Display text must avoid "ban/you/your/em" (kiem_nhanh chu_cam).

## Next steps (ordered)
1. `git pull --no-rebase`; re-run related tests: `grep -lE "sqlite_master|wharton_lock|i18n_loi|tai_khoan|DEFAULT_SCHEMA|test_do_api|dir\(PipelineAPI|__wrapped__|_xep_hang" tests/*.py`
   plus tests/test_gt3_*.py tests/test_giao_dien_gt3_*.py (run in background, ~20 min); fix any failure.
2. Send `WRITER DONE L3` (section 7 format) to the lead; then wait for `REVIEW` fixes (`FIX L3`) or `GO L4`.
3. L4: docs/giai_trinh/*.md, so_do_luong.svg, PHAN_CONG.md template per spec "Lot L4"; all numbers labelled SIMULATED; never write conclusions.

## Files touched
- L1: tai_khoan.py, api_tai_khoan.py, recovery.py, js/16_tai_khoan.js, tests/test_gt3_tai_khoan.py
- L2: phan_quyen.py, api.py, api_tai_khoan.py, index.html, style.css, tests/test_gt3_phan_quyen.py, tests/test_giao_dien_gt3_phan_quyen.py
- L3: nhat_ky.py, api_nhat_ky.py, phan_quyen.py, api.py, rbda_priority_pipeline.py, i18n_errors.py, i18n.js, i18n_loi.js,
  js/16_tai_khoan.js, tests/test_gt3_nhat_ky.py, tests/test_giao_dien_gt3_dang_nhap.py, CHANGELOG.md, TIEN_DO.md, CLAUDE_CHI_TIET.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Sonnet (writer) | L1 implemented, pushed 53e453a, reported to lead | handoff at context limit |
| 2026-11-16 | Sonnet (writer 2) | L1 fix1 (NFC), L2 + fix1 reported; L3 coded and tested, WRITER DONE L3 not sent | handoff at ~200k tokens |
