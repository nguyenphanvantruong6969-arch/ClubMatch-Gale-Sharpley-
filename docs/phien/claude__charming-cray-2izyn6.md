# Branch handoff: claude/charming-cray-2izyn6

> Purpose: a fresh session reads CLAUDE.md, then THIS file, then `docs/phien/VG1_GIAO_THUC.md`, and can continue.
> Language: English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
**VG1 — urgent patch of the registration portal (dk_*), size M.** New item code (Truong, 2026-11-27); coder adds a stub
row to `SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json` ("Phụ lục vá gấp"). After this branch the 6 defects below are gone,
proven by `tests/test_va_gap_tai_hien.py` (8 red repro tests; they are the acceptance).
Defect 7 (teacher tab shows "Đặng Văn Nam 4") is NOT understood yet: backend Excel import is correct (probed 2026-11-27);
needs Truong's screenshot. **Out of scope until then; do not guess.**

## Decisions already made (do not re-ask)
- D1 Gate (bugs 1–2): names compared as NFC + inner-space-collapsed + casefold; student ID casefold; PIN trimmed. A PIN that is not
  exactly 4 digits is rejected with `dk_pin_sai_dang` WITHOUT counting a failed attempt. Lock key built from the NORMALISED name.
  Stored/exported names and IDs keep original spelling (CSV contract, invariant 7). Names/IDs colliding after normalisation = duplicate.
- D2 PIN export (bug 3): PINs are hash-only, so "export" = RESET + export. New `dk_pin_xuat_excel(token, pham_vi, lop=None, xac_nhan=False)`,
  `pham_vi` in `hs|gv|tat_ca`; admin only; refuses without `xac_nhan`; new PIN per person, clears their lock counter, writes audit
  row WITHOUT any PIN; returns `{ten_tep, file_base64}` (xlsx, sheets «Học sinh» Mã|Họ tên|Lớp|PIN and «Giáo viên» Họ tên|PIN).
- D3 Stage back (bug 6): `dk_chuyen_giai_doan` may go back ANY number of steps in one call. Going back across `hs_dang_ky` with submitted
  wishes needs `xac_nhan=True` (else `dk_lui_co_nguyen_vong`, n). Going back clears `han_chot` of the target AND later stages (else the
  expired deadline auto-closes the stage on the next call). Forward jumps must pass the gate of EVERY boundary crossed. Never deletes data.
  Rejecting a club that students already picked needs `xac_nhan=True`; then only that club's wishes are removed, `hang` renumbered per
  (student, session), `nop_luc` kept, audit row with the count.
- D4 Free club (bugs 4–5): new setting `bat_buoc_tu_do` in `dk_cai_dat`, default ON = old behaviour (invariant 1). Set via
  `dk_cai_dat_doi(..., bat_buoc_tu_do=)` while stage ≤ `duyet`; shown in `dk_cai_dat_doc`; checkbox in Cài đặt. When ON, block EARLY:
  (a) entering `duyet` if a session has submitted clubs but no submitted Tự do club (`dk_thieu_clb_tu_do`, buoi); (b) `dk_clb_duyet`
  `tu_choi`, `dk_clb_xoa`, `dk_clb_sua_sau_mo` (xoa / đổi buổi) of the LAST Tự do club of a session that still has other live clubs.
  The old check in `_dk_kiem_dieu_kien_mo_hs` stays as safety net. When OFF all four checks and the `dk_khong_co_tu_do` warning are skipped.
- D5 Label (bug 7): untouched.

## Plan (lots; ✱ = must-ship)
- [ ] ✱L1 Gate + PIN format (bugs 1–2) — tests: 3 gate tests in repro file + lock key + duplicates-after-normalise + old `test_dk4_l0b*`, `test_dk3_api` stay green.
- [ ] ✱L2 PIN Excel export (bug 3) — backend + Cài đặt UI block «Phiếu PIN» (scope select, confirm dialog) + Chromium test. Rewrite the repro test
  `test_nap_lai_danh_sach...` into: xlsx has both sheets, every PIN logs in, old PIN fails, lock cleared, audit has no PIN, teacher/student denied, no `xac_nhan` → error.
- [ ] ✱L3 Multi-step back (bug 6) — backend D3 + UI select «Lùi về…» with confirm text (replace the single button; update `tests/test_giao_dien_dk8_l2.py:134`) + tests: back 3 steps, deadline cleared, orphan wishes, forward gate per boundary.
- [ ] ✱L4 Free-club option + early block (bugs 4–5) — backend D4 + checkbox UI + i18n (codes appended at END of `i18n_errors.py`, then `python tao_i18n_js.py`).
  **Check first:** does `dk_xuat_so_nhap` / the pipeline (FA mode, `buoi_thieu_tu_do` in `so_nhap.py`) accept a session with no Tự do club? If it needs an algorithm change → STOP, "Needs Truong", ship L4 without the export part.
- [ ] Final: all 8 repro tests green (renamed into the items' own test files is fine), related tests green, invariant 1 `kiem_nhanh.py` 7/7, `soat-ma`, CHANGELOG + TIEN_DO `VG1-L<n>`, one Chromium file `tests/test_giao_dien_vg1.py`.

## Current state
- Done so far: 8 red repro tests (`tests/test_va_gap_tai_hien.py`), this plan. No product code changed.
- Tests: `python -m pytest -q tests/test_va_gap_tai_hien.py` → 8 failed (expected before L1–L4).
- Open: defect 7 (needs Truong's screenshot). Repo has no `.venv`; system `python` has pytest + openpyxl, NOT playwright.

## Next steps
1. Coder session: follow `docs/phien/VG1_GIAO_THUC.md`.

## Files touched
- tests/test_va_gap_tai_hien.py: repro tests (acceptance)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-27 | Sonnet | repro tests + plan | planner role (Opus normally); Truong asked directly |
