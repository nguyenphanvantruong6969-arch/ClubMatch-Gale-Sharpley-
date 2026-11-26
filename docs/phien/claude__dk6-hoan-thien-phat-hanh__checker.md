# Checker: DK6 milestones 1+2 (c4486d3..cb698f1)

**PASS** (code head cb698f1 = d312516: Tests run 1701 + Build run 24 green; run 1702/1703 on docs-only 8bf21b2 were still pending when checked)

- Tests re-run here: dk6 (doi_mat_khau, goi_phat_hanh, gd_dk6_l1, gd_dk6_l2) + gd_dk4_chot_xep = 23 passed; `test_giao_dien_dkl_*` + `test_dkl_*` + `test_dk4_chot_va_xep` = 49 passed.
- L1/L2/L4 boxes met. Password: salted via `_bam`, old pw checked first, other admin tokens dropped only after commit, journal holds only "doi_mat_khau". Invariants 1/4/5/6 untouched (no solver, history, backup or pipeline code in the diff).
- L3 drop reason is TRUE: `_backup_db` (api.py) names every backup `app.db.bak-<ts>`, no pre-allocation marker; docs say so and tell users to copy the file away.
- Docs truthful: restore is manual (decision A); no admin-password reset is stated plainly.
- Plan assumption wrong, confirmed: `dk_diem_dat` and `dk_diem_dan` are QUAN_TRI-only, and students cannot submit in `nhap_diem`. Auto-refresh there only helps a second admin screen; it stays harmless because refresh is skipped for focused input, unsaved text (`data-v0`), PIN list and open confirm box.
- Own edge cases (scratch, not committed): no plaintext old/new password in `dk_nhat_ky`, `dk_cai_dat` or log records (both error and success paths); old caller token survives while a second admin token is revoked; non-string old password (None/int) gives `dk_mat_khau_cu_sai`. All pass.
- Nit (no fix needed): no attempt limit on `dk_mat_khau_cu_sai`; acceptable since an admin session is required.
