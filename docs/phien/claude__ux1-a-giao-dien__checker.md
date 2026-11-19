# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L2b fix3+fix4 — REVIEW d2aeaee..66f9ffb — NO BUGS (1 note) [verdict file written locally; not pushed during CI]
- Tests: 181 passed (ws_nhan, i18n_sync, ux1_* GUI suites, fg8, t3_l2, gt3_phan_quyen, all nhat_ky tests).
- Tests not weakened: only 2 `SUA_CO_Y` lines in test_ws_nhan changed (old text → new text for `health_oversubscribed_buoi`, wording "— ít nhất" → ", nên ít nhất"); i18n_errors/i18n_loi.js/i18n.js edits = dash→full-stop/comma wording, no logic.
- Health-once change: `capNhatViecTiepTheo(res)` reuses the result `loadHealthReport` has just fetched, else the in-flight request (`window.healthDangHoi`), else asks anew; `langchange` passes an Event → ignored (`"ok" in obj` guard). Triggers unchanged: after import and club edit (loadHealthReport), after run (refreshDashboardStats + loadEmChuaCoCho call it with no arg → fresh call or the just-started in-flight). Startup draw now comes from `loadPipelineTab` → `loadHealthReport` (called unconditionally in init()). No refresh dropped.
- Audit label: `nkhd_dat_loai_clb` added in vi + en; the log view maps `"nkhd_"+hanh_dong`, so "Đặt loại câu lạc bộ" / "Set a club type" show instead of the raw name.
- Note: reuse of an in-flight health request could return data older than a change made after it started (e.g. edit during the startup call); negligible, next refresh corrects it.

## L2b fix2 — REVIEW 64bc133..d2aeaee — NO BUGS (2 notes)
- Tests: 44 passed (ux1_cai_dat, ux1_cai_dat_backend, fg1, sg2, fa_gap1/gap3, ux1_tiep_theo).
- (1) `huy_chuong_sai` is READ-ONLY: `_ket_noi_doc` + `fa_daa.kiem_ho_so_huy_chuong`; probe: DB file md5 and every table's row count identical before/after the call. 800-student book: 0.02 s per call → fine.
  "Sẵn sàng" no longer shown while invalid medal rows exist; test asserts the real run (`run_pipeline`) is blocked when the panel says not ready, and a new positive test (FA sample book, FA on) says ready AND the run passes.
- (2) `fa_vong_2` hidden when no unplaced, `fa_vong_doi_cho` hidden when no empty seats (Tự do clubs excluded, same formula as the "Chỗ trống" card); flag already ON stays visible so it can be turned off. Redraw key includes `trong`.
- Privacy: `huy_chuong_sai_vd` = one student id (no name/score). Tier GIAO_VIEN already lists student ids via search/results; student mode blocks the call (`gt3_che_do_hoc_sinh`), giao_vien cannot call `dat_loai_clb`. Acceptable.
- Adapted old tests not weakened: the old "san_sang is True" on the plain-mode 120 book was replaced by the opposite (False) + run blocked — a deliberate behaviour change; the after-run test now simulates 3 unplaced (monkeypatch) AND a new real-data test covers the 0-unplaced case.
- Notes: (a) `.toast .toast-hanh-dong {color:#fff}` is right for success/error toasts, but `.toast.is-warn` has a light gold background (dark text): a future warn toast with an action would be white-on-gold; today only success toasts carry actions (Hoàn tác, Mở thư mục). (b) `huy_chuong_sai` counts all students in FA-off mode with plain books (e.g. 800) — only shown when the Huy chương card is selected, text tells to reload a Medal book: fine.

## Earlier lots (all NO BUGS after fixes): L1; L2; L2b; L3 (+fix1); L5; L5b; L8-A (+fix1; 32 unplaced/88 placed).
