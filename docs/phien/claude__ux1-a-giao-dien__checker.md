# Checker — UX1A (branch claude/ux1-a-giao-dien) — latest verdict first

## L2b — REVIEW 7bb6a9b..e3d0382 — NO BUGS (3 notes)
- Tests: 198 passed (new ux1_cai_dat + ux1_cai_dat_backend, all 12 rewritten old tests, fa_n3, a13_13, ws_*, gt3_phan_quyen, ux1 L1/L2); ruff clean.
- Backend: `get_san_sang_huy_chuong` = read-only, tier GIAO_VIEN; `dat_loai_clb` = tier QUAN_TRI, reuses `ghi_thuoc_tinh_clb` (UPDATE clubs only),
  `loai`/`diem_san` validated (bad loai, unknown club, diem_san 99, None → ok:False, nothing written); anonymous call blocked; every call (ok or
  rejected) gets an audit row (probe: 4 rows); `run_history` unchanged (test_dat_loai_khong_dong_toi_ket_qua_da_xep). No schema change.
- Invariants 1,2,4,6,7: no algorithm/CSV/schema change; default = Chia 100 điểm (wharton on, fa off) shown for a new workspace.
- Undo: `luatCu()` snapshots rules + post-run flags + complaint days; undo = same `update_workspace_config` call; error path leaves
  card unchanged and shows message under it (`datCach` only on success). Toast adds "kết quả giữ nguyên" when a run exists.
- Rewritten old tests (diffed all 12): only selectors/UI-structure changes; removed assertions all concerned controls that no longer exist
  (`#wzWharton`, `#gt2TcWharton`, 5 wizard ticks, ⋯ dialog). Behaviours kept or re-asserted via config read-back (fa_gap1/gap3 now assert
  the flag after the action button; fg1 keeps the "14" range error and unchanged config).
- Deviation (3): old UI test "FA on + wharton off rejected" replaced — backend rejection `fa_can_diem_quyet_tam` IS still covered, but by
  `tests/test_fa_n3_loi_diem_quyet_tam.py` (passes), NOT `test_a13_13_kiem_nhan.py` as the test comment says → fix the comment.
- Deviation (4): "Thay đổi…" → Quản lý › Nâng cao (opens `<details>`, scrolls to GT2 panel): reachable, obvious, acceptable.
- Notes: (1) wrong file named in the comment above; (2) Undo uses the snapshot from the click, so an Undo pressed after another change
  within 10 s would overwrite it (low risk); (3) fix-in-place panel only lists clubs with NULL loai — consistent with spec.

## Earlier lots
- L1 (016ae66..ebf24cd): NO BUGS; 4 clicks measured (was 5); minor notes (has_results, silent timeout) — first fixed later.
- L2 (ab1bd16..0ded385): NO BUGS; 141 tests passed; MutationObserver loop-safe; student lock OK; notes: print-only hidden sidebar edge.
