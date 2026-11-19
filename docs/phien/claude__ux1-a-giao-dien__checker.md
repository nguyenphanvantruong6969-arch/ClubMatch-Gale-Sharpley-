# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L2b fix2 — REVIEW 64bc133..d2aeaee — NO BUGS (2 notes)
- Tests: 44 passed (ux1_cai_dat, ux1_cai_dat_backend, fg1, sg2, fa_gap1/gap3, ux1_tiep_theo).
- (1) `huy_chuong_sai` is READ-ONLY: `_ket_noi_doc` + `fa_daa.kiem_ho_so_huy_chuong`; probe: DB file md5 and every table's row count identical before/after the call. 800-student book: 0.02 s per call → fine.
  "Sẵn sàng" no longer shown while invalid medal rows exist; test asserts the real run (`run_pipeline`) is blocked when the panel says not ready, and a new positive test (FA sample book, FA on) says ready AND the run passes.
- (2) `fa_vong_2` hidden when no unplaced, `fa_vong_doi_cho` hidden when no empty seats (Tự do clubs excluded, same formula as the "Chỗ trống" card); flag already ON stays visible so it can be turned off. Redraw key includes `trong`.
- Privacy: `huy_chuong_sai_vd` = one student id (no name/score). Tier GIAO_VIEN already lists student ids via search/results; student mode blocks the call (`gt3_che_do_hoc_sinh`), giao_vien cannot call `dat_loai_clb`. Acceptable.
- Adapted old tests not weakened: the old "san_sang is True" on the plain-mode 120 book was replaced by the opposite (False) + run blocked — a deliberate behaviour change; the after-run test now simulates 3 unplaced (monkeypatch) AND a new real-data test covers the 0-unplaced case.
- Notes: (a) `.toast .toast-hanh-dong {color:#fff}` is right for success/error toasts, but `.toast.is-warn` has a light gold background (dark text): a future warn toast with an action would be white-on-gold; today only success toasts carry actions (Hoàn tác, Mở thư mục). (b) `huy_chuong_sai` counts all students in FA-off mode with plain books (e.g. 800) — only shown when the Huy chương card is selected, text tells to reload a Medal book: fine.

## Earlier lots (all NO BUGS after fixes): L1; L2; L2b; L3 (+fix1); L5; L5b; L8-A (+fix1; 32 unplaced/88 placed).
