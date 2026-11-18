# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L3 — REVIEW 275a459..e812cf3 — 1 BUG (minor) + 1 observation → FIX L3
- Tests: 165 passed (new ux1_ket_qua, ux1_tiep_theo, fa_ket_qua, upload, xoa_du_lieu, sg11a, gt4, gt1/gt3, xuat*, chay, …).
- Item 1 OK: on 275a459 the 4 buttons were `hidden` in HTML and toggled `hidden = !fa` in `loadMatchResults` → FA-only before; `#xuatMenu`
  follows the same flag. Default mode shows exactly 2 export buttons. No regression.
- Item 2 OK: bar "Xuất" = `btnXuatTuyChon.click()` → the real handler (same options, toast/feedback/error path, audit); guarded by `!disabled`.
- Item 3 BUG: success path no longer writes `#feedbackImportAll`, so a stale error survives a successful retry. Repro (probe): first
  `import_so_nhap` fails with a non-`so_nhap_*` error (DB locked) → red message, file kept → press "Nhập sổ" again → done row appears but
  "Không lưu được câu lạc bộ…" is still shown (before L3 the success line overwrote it). Fix: clear `feedbackImportAll` at the start of
  `nhapTatCa()`; add a fail→retry→success test.
- Item 4 observation: the monkeypatch only zeroes `so_em`; the export step is real → no hidden path difference there. BUT on the real sample
  book (120 students, seed 42) 32 are unplaced (88 matched) → bar state = "Xử lý 32…", never "Xuất", so 4 clicks holds only when everyone is
  placed; real task on that book takes more (bar → unplaced panel, then Others → Xuất). Lead: report honestly in §6; not a code bug.
- Invariants 1,2,4,6,7: UI only, untouched. Privacy: nothing new shown.

## Earlier lots
- L2b (7bb6a9b..e3d0382): NO BUGS; 198 tests; dat_loai_clb QUAN_TRI + audit, no schema change; backend FA-needs-wharton still covered by
  test_fa_n3_loi_diem_quyet_tam.py (comment fixed in L3); note: Undo snapshot could overwrite a change made within 10 s.
- L2 (ab1bd16..0ded385): NO BUGS; 141 tests; MutationObserver loop-safe; student lock OK; print-only hidden-sidebar edge noted.
- L1 (016ae66..ebf24cd): NO BUGS; 4 clicks measured (was 5); notes (has_results fixed in L2; silent 3 s timeout).
