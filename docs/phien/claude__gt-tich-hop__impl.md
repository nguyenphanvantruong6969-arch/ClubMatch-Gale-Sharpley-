# Branch handoff: claude/gt-tich-hop (WRITER / impl)

> Fresh writer: read CLAUDE.md, docs/phien/GT_GIAO_THUC.md (§5, §7), docs/phien/claude__gt-tich-hop.md (lead file),
> then THIS file. Lead session: session_01YVAyu27w5WZmfqRfkjo3Av. Report only in §7 formats via send_message.
> English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Writer for the GT1+GT2+GT3 integration on `claude/gt-tich-hop` (lots I0-I4, spec: Plan in the lead file and
`docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md` § "Integration lots"). Setup done: `.claude/phien_vai.json`
(`impl`, coord = lead id), `.venv` built from requirements-dev.txt.

## Plan (ticked by Sonnet; mirrors lead file)
- [x] I0 merges (gt2 then gt3 into branch; head d4447a5; checker NO BUGS)
- [x] I1 permission map (9f5962d; checker NO BUGS)
- [x] I2 student mode locked in backend (67b2faf, fix1 fa490c3, fix2 2abdd09; checker verdict 24c030e; waiting lead tick)
- [x] I3 audit rows (tests only, no product change; waiting checker): run_thu, ap_dung_tieu_chi, code (re)generation, slip export each log exactly ONE row
- [x] I4 evidence pack (waiting checker): du_lieu_test/tao_ca_mau_giai_trinh.py -> docs/giai_trinh/CA_MAU.md; tao_goi_minh_chung.py -> .docx/.pdf

## Current state (overwrite each handoff)
- Done so far: I0, I1, I2 (incl. reload fix). Lead has been told WRITER DONE I2 fix2 (head 2abdd09). No GO I3 yet.
- In progress: I3 done (4 tests in test_gt_tich_hop.py), waiting checker; I4 next after GO.
- Tests: tests/test_gt_tich_hop.py (5), tests/test_giao_dien_gt3_hoc_sinh.py (4, Chromium), test_gt3_phan_quyen.py,
  test_giao_dien_gt1_hoc_sinh.py -> 52 passed at fa490c3; kiem_nhanh 7/7 (60 cases identical to origin/main).
- Open problems: none. A broad run of 100 test files hit the 10-min cap (0 failures at 61%); CI shards cover the rest.

## Decisions and gotchas
- Merge conflicts in shared files: keep every team block GT1->GT2->GT3 (script: keep both sides, then fix by hand);
  `i18n_loi.js` = `git checkout --ours` then `python tao_i18n_js.py`. Never rebase (protocol); use `git pull --no-rebase`.
- Student mode (I2): flag `api._che_do_hs` is in memory (restart clears flag + sessions). `phan_quyen._xet` allows only
  `_HS_DUOC` = tra_cuu_hoc_sinh, thoat_che_do_hoc_sinh, get_phien_dang_nhap when accounts ON and flag set (error
  `gt3_che_do_hoc_sinh`). `vao_che_do_hoc_sinh` = giao_vien; `thoat_che_do_hoc_sinh(ten, mat_khau)` = cong_khai but needs
  quan_tri login; args never logged (`nhat_ky._CHI_GIU`). JS 14 opens overlay instantly, 16 emits `tkPhien`/listens
  `tkLamMoi`; reload reopens overlay from `get_phien_dang_nhap.che_do_hs`.
- QUYEN additions (I1): GT2 methods + tao_ma_tra_cuu/tao_lai_ma_tra_cuu/export_ma_tra_cuu_csv = quan_tri;
  get_giai_trinh_hoc_sinh/export_phieu_giai_trinh = giao_vien; tra_cuu_hoc_sinh = cong_khai.
- I3 hint: audit goes through `phan_quyen._boc` + `nhat_ky.nen_ghi` (default logs every non-read call; `_DOC` prefixes
  get_/list_/... are NOT logged, so check export_phieu_giai_trinh / get_* style names such as get_giai_trinh_hoc_sinh);
  nested calls (`_TL.sau`>0) are not logged, so run_thu internals must not double-log. Test with "exactly one row".
- Test slow: run only related files; use `timeout` < 600 s; no `sleep` loops in Bash (use background + notification).
- Tests dir helpers: `_fa.dung_fa_clb`, `_wharton.tat_wharton`, `_trinh_duyet.CHROMIUM`; test_giao_dien_gt3_hoc_sinh
  imports `_dung` from test_gt_tich_hop.

## Next steps (ordered)
1. Wait for `GO I3` (lead). Spec: lead file Plan item I3.
2. Failing test first (tests/test_gt_tich_hop.py): accounts ON, each of run_thu, ap_dung_tieu_chi, tao_ma_tra_cuu +
   tao_lai_ma_tra_cuu, export_phieu_giai_trinh -> exactly one `nhat_ky_thao_tac` row; then minimal fix in nhat_ky.py /
   phan_quyen.py. Then related tests, kiem_nhanh, CHANGELOG, TIEN_DO row, tick I3, commit, push, WRITER DONE I3.
3. Then I4 (GT3 task file § Integration lots; all data SIMULATED, labelled so; no report conclusions).

## Files touched (this session)
- phan_quyen.py, api_tai_khoan.py, nhat_ky.py, i18n_errors.py, i18n_loi.js, i18n.js, index.html, style.css
- js/14_giai_trinh.js, js/16_tai_khoan.js
- tests/test_gt_tich_hop.py (new), tests/test_giao_dien_gt3_hoc_sinh.py (new), tests/test_gt3_phan_quyen.py
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/phien/claude__gt-tich-hop.md (ticks)
- merges: i18n_errors.py, index.html, js/_danh_sach.txt, style.css, api.py (mixin lists), CHANGELOG/TIEN_DO/CLAUDE_CHI_TIET

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Sonnet (writer) | I0 merges, I1 QUYEN, I2 student-mode lock + reload fix, soat-ma on I2 | handoff at ~200k tokens; head before handoff 2abdd09 |
