# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L5b (+L5 follow-up) — REVIEW 1ec7b23..4cae05b — NO BUGS (3 notes)
- Tests: 94 passed (new l5b 10+, ux1_nhap_so incl. no-workspace button test, l5_backend, so_mau tests, fa_m3_huy_chuong_b, upload). Plain sample (FA off) cell md5 still fab19c2c… = identical to bc71013.
- Mapping only when `dung_fa_daa(cfg.rules)` and only in `api_nhap._doc_so_nhap` via `so_nhap.chuan_hoa_chu_huy_chuong` (preview + import both go through it). FA off: strings untouched, same path as before (test).
- Probe of 25 inputs: "Vàng " / NFC / NFD "Vàng", "ĐỒNG", "Đồng", "dong", "DONG", "Gold", "SILVER", "bạc", "bronze" → 60/30/10; ambiguous/odd "vang 60", "", "  ", "0", "60", "6O", "vàng/bạc", "đồng đỏ" unchanged
  (unknown words keep `fa_huy_chuong_gia_tri_sai`; test uses "Kim cương"). Numeric cells (ints) never touched. Stored `wharton_bids` = 60/30/10; `fa_daa.kiem_ho_so_huy_chuong` untouched.
- Numbers-vs-words test compares `wharton_bids` AND `match_results` (>100 rows each, seed 42, two FA workspaces) → real equality, not a monkeypatch. 4 spelling variants parametrised.
- Forms path: offline converters call `so_nhap.doc_so_nhap` directly but only emit numeric 60/30/10 books; any book imported into the app goes through `_doc_so_nhap` → claim holds.
- Sample book: Hướng dẫn says "Vàng / Bạc / Đồng hoặc 60 / 30 / 10"; FA book dropdown accepts both; plain book has no such line/validation.
- L5 follow-up OK: `#btnBatHuyChuong` only when `wsTrangThai.enabled`; no workspace → sentence only (test).
- Notes: (a) `bo_dau` also strips punctuation/accent typos, so "Vàng." and "dóng" map (harmless, lenient). (b) FA-off test's 2nd assertion is a tautology (`{60,30,10} - {60,30,10}`); first assertion carries it. (c) invariant 1/2/4/6/7 untouched (reading layer only).

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
