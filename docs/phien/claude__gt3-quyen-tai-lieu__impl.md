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
- [x] L3 Audit log: done; related run 1255 tests green (after allowlist fix in test_ws_nhan); WRITER DONE L3 sent.
- [x] L4 Evidence docs: done (7 docs + svg + ve_so_do.py + tests/test_gt3_tai_lieu.py); WRITER DONE L4 sent.

## Current state (overwrite each handoff)
- L1, L2, L3 passed the checker. L3 fix1 (db_path captured before the call, bounded 1 s lock wait with background catch-up write,
  case-insensitive actor filter) pushed and reported; lead replied GO L4 (so L3 passed).
- L4 done and reported (WRITER DONE L4, head 6d36d68): docs/giai_trinh/ (VAI_TRO_AI, SO_DO_LUONG + so_do_luong.svg via ve_so_do.py,
  HUONG_DAN_CHAY, DU_LIEU_DAU_VAO, PHAN_CONG template, KICH_BAN_DEMO, KICH_BAN_VIDEO), tests/test_gt3_tai_lieu.py (20 passed).
- Not verified: real pywebview window and Windows commands (no display/Windows here); stated in HUONG_DAN_CHAY.
- soat-ma 4-tier eye review remains partial for L1-L4 (kiem_nhanh 7/7 each time).

## Decisions and gotchas (keep short)
- Hook text names unknown__impl.md; the real handoff file is this one. Never rebase a pushed branch (use --no-rebase). `git push` once failed on a stale tracking ref; `git push origin HEAD:refs/heads/<branch>` worked.
- test_ws_nhan allowlist now accepts `gt3_` codes; test_gt3_tai_lieu allows the product name FA-DAA but forbids item codes.
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
1. `git pull --no-rebase`; wait for `CHECKER REPORT L4` / `FIX L4` from the lead (or `GO` for integration lots I1-I4).
2. On FIX: fix, rerun tests/test_gt3_tai_lieu.py + related, `WRITER DONE L4 fix1`.
3. Integration (only if the lead starts it): merge gt1/gt2/gt3 on claude/gt-tich-hop, lots I1-I4 per spec; fill "(sau tích hợp)" steps in the demo/video scripts.

## Files touched
- L1: tai_khoan.py, api_tai_khoan.py, recovery.py, js/16_tai_khoan.js, tests/test_gt3_tai_khoan.py
- L2: phan_quyen.py, api.py, api_tai_khoan.py, index.html, style.css, tests/test_gt3_phan_quyen.py, tests/test_giao_dien_gt3_phan_quyen.py
- L4: docs/giai_trinh/*, tests/test_gt3_tai_lieu.py, CHANGELOG.md, TIEN_DO.md, CLAUDE_CHI_TIET.md
- L3: nhat_ky.py, api_nhat_ky.py, phan_quyen.py, api.py, rbda_priority_pipeline.py, i18n_errors.py, i18n.js, i18n_loi.js,
  js/16_tai_khoan.js, tests/test_gt3_nhat_ky.py, tests/test_giao_dien_gt3_dang_nhap.py, CHANGELOG.md, TIEN_DO.md, CLAUDE_CHI_TIET.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Sonnet (writer) | L1 implemented, pushed 53e453a, reported to lead | handoff at context limit |
| 2026-11-16 | Sonnet (writer 2) | L1 fix1 (NFC), L2 + fix1 reported; L3 coded and tested, WRITER DONE L3 not sent | handoff at ~200k tokens |
| 2026-11-16 | Sonnet (writer 3) | L3 related run + test_ws_nhan fix, L3 fix1, L4 docs; all reported | handoff at ~200k tokens |
