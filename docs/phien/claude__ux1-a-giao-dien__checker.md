# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L3 fix1 — REVIEW e812cf3..3ba1efe — NO BUGS (L3 now clean)
- Tests: 32 passed (ux1_tiep_theo incl. real-book 4-click test, upload incl. fail→retry→success, ux1_ket_qua, ux1_dieu_huong, doi_ngon_ngu).
- (1) `feedbackImportAll` cleared at start of `nhapTatCa()`; new test checks the error text AND the `is-error` class are gone after a successful retry.
- (2) `#viecTiepTheoNut2` ("Xuất kết quả", secondary style) is `hidden` by default and set `hidden = state !== "xu_ly"` on every refresh → visible only
  in xu_ly; hidden in nap_so/canh_bao/chay/xuat (checked chay in test; xuat uses the main button); bar itself is `data-quyen=quan_tri`, so
  `giao_vien` never sees it. Click → `VIEC_HANH_DONG.xuat()` = same real export. Real 120-book (32 unplaced) now exports in 4 clicks, no monkeypatch.
- Note: in xu_ly the primary stays "Xử lý n…" (btn-primary) and export is secondary — consistent with spec order.

## L3 — REVIEW 275a459..e812cf3 — 1 minor bug (fixed in fix1)
- Item 1 OK (4 export buttons already FA-only on 275a459); item 2 OK (bar export = `btnXuatTuyChon.click()`); item 4: monkeypatch hid the
  unplaced path (32 unplaced on real book) → now covered by the real-book test. Bug: stale `feedbackImportAll` error after retry (fixed).

## Earlier lots
- L2b (7bb6a9b..e3d0382): NO BUGS; 198 tests; dat_loai_clb QUAN_TRI + audit, no schema change; backend FA-needs-wharton still covered by
  test_fa_n3_loi_diem_quyet_tam.py (comment fixed in L3); note: Undo snapshot could overwrite a change made within 10 s.
- L2 (ab1bd16..0ded385): NO BUGS; 141 tests; MutationObserver loop-safe; student lock OK; print-only hidden-sidebar edge noted.
- L1 (016ae66..ebf24cd): NO BUGS; 4 clicks measured (was 5); notes (has_results fixed in L2; silent 3 s timeout).
