# Branch handoff: claude/vg2-ra-soat-theo-vai

> Purpose: a fresh session reads CLAUDE.md, then THIS file, then `docs/phien/VG2_GIAO_THUC.md`, and can continue.
> Language: English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
**VG2 — fixes from the role-play test of the registration portal (dk_*), size M.** Source: `docs/phien/VG1_KIEM_TRA_TOAN_DIEN.md` (findings 1,3,4,5,6,7,8,10,11,12,13).
New item code (Truong, 2026-11-27); add a stub row to `SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json` ("Phụ lục vá gấp", next to VG1).
Acceptance = `tests/test_vg2_tai_hien.py` (16 red repro tests) + one Chromium file `tests/test_giao_dien_vg2.py` (L3). Findings 2 and 9 were already fixed by VG1-L2.
**START CONDITION:** VG2 touches the same functions as VG1 (L1 gate, L2 PIN, L3 stage back, L4 free club). Branch from the TIP of
`origin/claude/charming-cray-2izyn6` ONLY after its branch file "Current state" says VG1 CI is green. If not green yet: schedule a wake-up
(`send_later` 20 min) and re-check; do not start earlier (merge conflicts).
`test_hs_da_bi_xoa_khoi_danh_sach_khong_con_luu_duoc` uses VG1-L3's `xac_nhan=True` back-step; if VG1 changed that signature, adapt the test, not the intent.

## Decisions already made (do not re-ask; Truong did not answer finding 1, so the SAFE default is chosen)
- D1 Admin lock-out (finding 1): only the `quan_tri` account changes. First lock after 5 wrong passwords = **1 minute**, each consecutive lock
  doubles (1, 2, 4, capped at 5 min); a successful login clears the level (new `dk_cai_dat` key `dn_bac:quan_tri`; counter format of the old
  key untouched). A correct password is STILL refused during a lock (keeps brute-force protection). Teacher/student locks stay 5 min (admin unlocks).
  Residual risk (stranger can still delay the admin ≤ 5 min) → one "Needs Truong" note; no further mechanism.
- D2 Trivial PIN (finding 7): `dk_pin_de_doan` for self-registered PINs and `_pin_moi()` never returns: 4 equal digits, ascending/descending runs
  (0123…6789, 3210…9876), `2580`. Existing PINs untouched.
- D3 Teachers (finding 6): `dk_gv_xoa(token, gv_id)` admin only; refuses `dk_gv_con_clb` if the teacher has any club not rejected; else deletes
  the teacher + its rejected clubs, revokes its sessions, audit row. Self-register cap `TOI_DA_GV = 300` (module constant) → `dk_gv_qua_nhieu`.
- D4 Integrity (findings 4,5,3,13,12,11): names of rooms and clubs compared with the same normaliser VG1-L1 added (NFC + collapse spaces + casefold) →
  existing `dk_phong_trung` / `dk_clb_ten_trung`; existing rows are never renamed. `dk_phong_xoa` refuses if ANY club (even rejected) references the room.
  `dk_hs_luu` / `dk_hs_nguyen_vong`: student row must exist (else `dk_khong_thay`), `nguyen_vong` must be a list of dicts (else `dk_nv_sai_dang`).
  Un-ticking an exam club that already has a score → warning `dk_mat_diem` in `canh_bao` (data still saved; nothing blocked).
  `dk_khoi_tao` requires school code ≥ 4 chars like `dk_cai_dat_doi` (`dk_ma_truong_sai`); admin password minimum stays 4 (changing it = out of scope).
- D5 UI (findings 8,10): «Danh sách» sections Giáo viên / Học sinh open by default when ≤ 60 rows (collapsed with "Bấm để xem" hint above); «Đóng ngay»
  (and any stage-closing button) asks a confirm dialog; «Xoá» button + confirm per teacher in the list. Texts via i18n keys prefix `vg2_`.

## Plan (lots; ✱ = must-ship)
- [ ] ✱L1 Accounts (D1–D3): `dk_dang_nhap` escalating lock, `dk_gv_xoa`, `TOI_DA_GV`, `_pin_moi` + `dk_pin_de_doan`, `dk_khoi_tao` code length. Tests: repro tests 1,3,4 + `test_dk4_l0b_khoa_dang_nhap.py` stays green.
- [ ] ✱L2 Integrity (D4): repro tests 2,5 + room/student/list/score warning; related: `test_dk3_api.py`, `test_dk4_chot_va_xep.py`.
- [ ] ✱L3 UI + i18n (D5): codes appended at END of `i18n_errors.py` then `python tao_i18n_js.py`; Chromium `tests/test_giao_dien_vg2.py` (one shared page fixture: lists visible after Excel import; confirm dialog on «Đóng ngay» both accept/cancel; «Xoá» teacher).
- [ ] Final: 16 repro tests green, related green, invariant 1 `kiem_nhanh.py` 7/7, `soat-ma`, CHANGELOG + TIEN_DO `VG2-L<n>`, CI loop to green.

## Current state
- Done so far: 16 red repro tests (`tests/test_vg2_tai_hien.py`), findings report, this plan. No product code changed.
- Open: defect 7 of VG1 (Truong's "Đặng Văn Nam 4") is probably finding 8 here (collapsed lists) — Truong to confirm; if it is not, it stays open.

## Next steps
1. Follow `docs/phien/VG2_GIAO_THUC.md`.

## Files touched
- tests/test_vg2_tai_hien.py: repro tests (acceptance)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-27 | Sonnet | role-play test, repro tests, plan | planner role; Truong asked directly |
