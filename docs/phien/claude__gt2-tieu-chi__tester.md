# Checker verdict — GT2 (branch claude/gt2-tieu-chi)

## L1 | reviewed 1ff5794..4738551 | verdict: 1 BUG (UI), rest OK

Tests: tests/test_gt2_tieu_chi.py + tests/test_giao_dien_gt2_tieu_chi.py -> 113 passed.
`kiem_nhanh.py --co-so 1ff5794 --so-seed 20` -> 7/7 DAT (60 cases identical, ruff, chu_cam, i18n, run_history untouched).

Verified:
- Writer's claim true: `cau_hinh_ws._chuan_hoa` (via `update_workspace_config`, workspace mode ON) rejects, with
  saved rules unchanged: unknown rules key, unknown top-level key, priority/tier_mode/score_scope bad values (string,
  list, dict), tiers non-list / non-string / empty / duplicate, wharton/fa_daa non-bool (incl. 1), rules list/None,
  priority=tier + wharton=true, fa_daa=true + wharton=false (`fa_can_diem_quyet_tam`). Code is `ws_du_lieu_sai`
  (existing), so no `gt2_tieu_chi_khong_hop_le` needed. Note: without workspace mode every call returns `ws_tat_che_do`.
- Allow-list key set pinned to LUAT_XEP_MAC_DINH + KHOA_NGOAI_LUAT_XEP; descriptions parametrised over all combos.
- Mandatory note present (`ghi_chu`, rendered in `#gt2TcGhiChu`); chu_cam/i18n checks pass; Vietnamese tier names with
  diacritics round-trip. get_tieu_chi is read-only; FA on/off descriptions covered by the enumerated combos.

BUG 1 (UI): js/15_tieu_chi.js `gt2TcLuatDangChon` always sends `wharton: el("gt2TcWharton").checked`.
- repro: fresh workspace (default wharton=true) -> panel -> choose "Chỉ theo nhóm ưu tiên" (priority=tier) or "Một điểm
  cho cả người" (score_scope=per_person) -> Save without touching the checkbox. Reproduced at API level with the exact
  payload: `ws_du_lieu_sai` "wharton chỉ dùng được khi priority là score hoặc score+tier và score_scope là per_slot
  (điểm Wharton cần biết em có thi CLB nào)" — jargon (`wharton`, `per_slot`) shown to the teacher. Explicit `wharton`
  also defeats the auto-off in `cau_hinh_ws.tron_len`/`_chuan_hoa`.
- expected: saving a combination that makes commitment points inactive works without an error (omit `wharton` from the
  payload or auto-uncheck + disable the box in the UI when priority==="tier" or scope==="per_person"; with FA on, say
  in plain words that FA turns off). 
- why tests missed it: `test_luu_khoa_diem_quyet_tam_khi_chi_xet_nhom_khong_loi` calls `.uncheck()` first. Add a
  case that does NOT uncheck.

## L1 fix1 | reviewed 4738551..9b67a95 | verdict: 1 BUG (minor)

Tests: 115 passed (L1 unit + Chromium). Original bug fixed: priority=tier / per_person -> box unchecked + disabled,
hint shown, save succeeds without .uncheck(); FA-on hint text present (vi + en).

BUG 2 (UI, minor): js/15_tieu_chi.js `gt2TcDongBoWharton` unchecks the box but never restores it.
- repro (Chromium, fresh workspace, saved wharton=true): choose priority "tier", then back to "score" -> box is
  ENABLED but UNCHECKED (same after per_person -> per_slot). Save now sends wharton=false: commitment points are
  silently turned off; with FA on the save is refused (fa_can_diem_quyet_tam) although the admin only toggled and
  reverted a select.
- expected: switching back to score + per_slot restores the box to the last state the admin chose (remember the
  pre-disable checked value, or reset to the saved value), hint hides.

Note (not blocking, pre-existing from L1): changing language re-runs gt2TcVeDieuKhien/gt2TcDatGiaTri, which resets
unsaved selects, textarea and box to the saved values.
