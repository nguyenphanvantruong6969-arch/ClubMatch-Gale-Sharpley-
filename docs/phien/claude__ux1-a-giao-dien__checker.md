# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L5 — REVIEW bc71013..764c85c — NO BUGS (3 notes)
- Tests: 129 + 136 passed (new l5_backend/ux1_nhap_so, data_health, ws_nhan, so_mau tests, i18n/bang_loi, fa_n3, L1/L3 suites); `tao_i18n_js.py` regenerates `i18n_loi.js` with no diff.
- (1) Severity: only `n_high` gates anything (run gate, L1 bar `canh_bao`, UI sort/label); no code reads "medium" as blocking → L1 bar unaffected.
- (2) Plain sample: `tao_so_nhap_mau(out)` cell-by-cell md5 identical to bc71013 (3 sheets); `kieu="huy_chuong"` gives the medal book whose Hướng dẫn has the "BẬT ở Cài đặt" line;
  preview of that book with FA off returns `so_nhap_canh_bao_huy_chuong_che_do_tat`. Unknown `kieu` falls back to plain (safe).
- (3) `#btnBatHuyChuong`: created only in the import queue (admin pipeline view); calls `update_workspace_config {wharton,fa_daa}` (QUAN_TRI → blocked for giao_vien, audited), disables while running,
  error → toast + button re-enabled, success → `ux1aApDungSong` + re-preview of the same pending book. Never silent.
- (4) Test edits (`test_ws_nhan` SUA_CO_Y, `test_data_health` severity, `chu_ui_doi_co_y_t3.json` import_hint): string/severity only; matching i18n.js strings; nothing weakened.
- (5) Deviations OK: summary line sits ABOVE the grouped list (list kept); two sample buttons instead of a menu — acceptable.
- (6) Invariant 1/2/4/6/7: only messages, one preview-only flag (`co_cot_huy_chuong`), optional `kieu` arg; stored data + run decisions untouched; error code added to catalogue + regenerated JS.
Notes: (a) without a workspace (`ws_tat_che_do`) the "Bật chế độ huy chương" button just shows an error toast — mode cannot be enabled there; consider hiding the button then. (b) "run error points to FA setting" is done as the
hint text `wh_goi_y_tat`, not a new run error; fine. (c) summary says "chưa đặt đủ điểm quyết tâm (huy chương)" (not exactly "huy chương" only).

## Earlier lots
- L3 + fix1 (275a459..3ba1efe): stale import error found, fixed; real-book 4 clicks via secondary export button; Nut2 visible only in xu_ly, admin only.
- L2b (7bb6a9b..e3d0382): NO BUGS; dat_loai_clb QUAN_TRI + audit, no schema change; note: Undo snapshot may overwrite a change made within 10 s.
- L2 (ab1bd16..0ded385): NO BUGS; MutationObserver loop-safe; student lock OK. L1 (016ae66..ebf24cd): NO BUGS; 4 clicks measured.
