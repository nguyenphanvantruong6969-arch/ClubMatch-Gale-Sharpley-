# Branch handoff: claude/vg2-ra-soat-theo-vai

> Purpose: a fresh session reads CLAUDE.md, then THIS file, then `docs/phien/VG2_GIAO_THUC.md`, and can continue.
> Language: English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
**VG2 — fixes from the role-play test of the registration portal (dk_*), size M.** Source: `docs/phien/VG1_KIEM_TRA_TOAN_DIEN.md` (findings 1,3,4,5,6,7,8,10,11,12,13, round-2 UI findings 15–19, round-3 stress/simplicity findings 21–27).
New item code (Truong, 2026-11-27); add a stub row to `SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json` ("Phụ lục vá gấp", next to VG1).
Acceptance = `tests/test_vg2_repro.py` (16 red repro tests) + one Chromium file `tests/test_giao_dien_vg2.py` (L3). Findings 2 and 9 were already fixed by VG1-L2.
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
  Round-2 UI items (findings 15–19 in `VG1_KIEM_TRA_TOAN_DIEN.md`): wrap every `.dk-bang` in `overflow-x:auto` (no page-level horizontal scroll at 375 px on any admin stage); clear the score error on the next successful save; confirm dialog for the teacher's own club «Xoá»; `aria-label` «Đặt lại PIN — <tên>» (same for the other per-row buttons), one `<h1>` per admin screen, ≥ 36 px tap targets for «← Mở phần mềm xếp CLB» and the switch; `maxlength=80` on the club name + separate messages for blank / too long.

- D6 Simplicity (findings 23–27, 21–22): student wizard shows ONLY the steps that apply per session: no wishes → one line «Em không học buổi này» and jump to the next session (no medal/exam screens); medal screen only if ≥ 1 non-Tự do club is chosen; exam screen only if ≥ 1 Tuyển chọn club is chosen; the review screen still lists every session. Server rules unchanged (`dk_hs_luu` payload identical → invariant 1). `dk_sai_giai_doan` message uses the stage's Vietnamese name (map `phan` → «Chuẩn bị / Giáo viên đăng ký / Duyệt CLB / Học sinh đăng ký / Nhập điểm / Xuất» in the i18n layer, vi + en). «hạt giống» wording replaced (technical number kept under a collapsed «Chi tiết kỹ thuật»); «NV1» gets a one-line legend «NV = nguyện vọng». First-run screen: helper text under each field. Status text: hide «đã có PIN» when 0 students; disable (not hide) the student login form when the stage is «Chưa mở». Lock table (21): purge rows older than the lock window on each login; unknown ids share one counter. Sessions (22): purge expired tokens on each login.

## Plan (lots; ✱ = must-ship)
- [x] ✱L1 Accounts (D1–D3): `dk_dang_nhap` escalating lock, `dk_gv_xoa`, `TOI_DA_GV`, `_pin_moi` + `dk_pin_de_doan`, `dk_khoi_tao` code length. Tests: repro tests 1,3,4 + `test_dk4_l0b_khoa_dang_nhap.py` stays green.
- [x] ✱L2 Integrity (D4): repro tests 2,5 + room/student/list/score warning; related: `test_dk3_api.py`, `test_dk4_chot_va_xep.py`.
- [x] ✱L3 UI + i18n (D5): codes appended at END of `i18n_errors.py` then `python tao_i18n_js.py`; Chromium `tests/test_giao_dien_vg2.py` (one shared page fixture: lists visible after Excel import; confirm dialog on «Đóng ngay» both accept/cancel; «Xoá» teacher).
- [x] L4 Simplicity (student wizard + texts done; #21 lock table for unknown ids and #27 disabled student login form NOT done) (D6): student wizard skips empty/irrelevant steps (Chromium test: 5 sessions, 1 club → ≤ 6 screens, payload to `dk_hs_luu` byte-identical to the long path), plain-language texts, first-run help, i18n `vg2_`; purge of lock rows/tokens in L1 files. Optional if budget is short: first-run help and status-text polish.
- [ ] Final: 16 repro tests green, related green, invariant 1 `kiem_nhanh.py` 7/7, `soat-ma`, CHANGELOG + TIEN_DO `VG2-L<n>`, CI loop to green.

## Current state
- Done: L1–L4 code, accent-free login, CI-debug fixes (see Session log). VG1 tip `892f55d` merged (commit `2d5a6e0`; kept VG2's side for 3 UI tests + code map 454).
- Truong (2026-11-27): NO checker / review needed; done = CI green + bugs solved. Checker step skipped on purpose.
- After merge: `kiem_nhanh.py` 7/7; repro + accent-free + vg1 + i18n/doc tests 86 green; UI tests vg2 6, dk3_cong 16, dk4_mo_khoa 1, dkl_giao_vien 3 green.
- CI: Tests (rbda-kiosk) run 46079820841 on `118182d` = SUCCESS (all jobs incl. coverage >= 85 %). Build Windows is manual-only and overwrites the public release: NOT run, waiting for Truong.
- Next: when VG1 (`claude/charming-cray-2izyn6`, head `c6766f8`, CI run 46079810673) is green, merge it again (adds defect-7 fix); then PR/merge to main only if Truong asks. Open (low, for Truong): #21, #27, 2–3 ms login timing gap.

## Decisions added in this session (safe defaults)
- Old tests were edited where the contract changed on purpose: school code ≥ 4 chars (`TR1`→`TRU1`, `T`→`TRUONG`), trivial PINs refused for teacher self-register (`1234`→`7391`, `5678`→`5903`), lists open by default (tests set `parentElement.open = true` instead of toggling), confirm dialogs (tests `pg.once("dialog", accept)`), student wizard skips empty steps (dk8_l5 tests add a Tuyển chọn club so the exam step exists).
- `dk_sai_giai_doan` shows Vietnamese stage names via `TEN_GD_VI` in `_Loi.__init__` (English text also gets the Vietnamese name; acceptable).
- Admin lock uses `dn_bac:quan_tri` (level doubles 1,2,4, capped at 5 = `PHUT_KHOA`); a correct password is still refused during a lock.
- `i18n_errors.py` rule `chu_cam` forbids «Em»/«You»: `dk_mat_diem` is worded without a pronoun.

## Next steps (ordered)
1. `git fetch origin && git merge origin/claude/charming-cray-2izyn6` (VG1 tip); fix any conflicts (take VG1's side for `docs/phien/claude__charming-cray-2izyn6*.md`); re-run `tests/test_vg2_repro.py tests/test_giao_dien_vg2.py` and `kiem_nhanh.py`.
2. Spawn ONE checker (Opus, `claude-opus-5-5`, prompt = `VG1_GIAO_THUC.md` §5 renamed to VG2) with `REVIEW 1 18c63d2..HEAD`; fix findings (max 2 rounds each).
3. CI loop per `VG1_GIAO_THUC.md` §4: read GitHub Actions `tests.yml` (coverage ≥ 85 %) and `Build Windows executable (rbda-kiosk)` for the head commit, fix, push, repeat until both green. Never skip/loosen a test.
4. Optional: #21 and #27; Truong's open question: how will students reach the portal (server listens on `127.0.0.1` only)?

## Files touched
- tests/test_vg2_repro.py: repro tests (acceptance); tests/test_giao_dien_vg2.py: Chromium tests (new); tests/test_vg2_dang_nhap_khong_dau.py (accent-free login)
- api_dang_ky.py, i18n_errors.py, i18n_loi.js: L1–L2 backend, new codes `dk_pin_de_doan`, `dk_gv_con_clb`, `dk_gv_qua_nhieu`, `dk_nv_sai_dang`, `dk_mat_diem`
- js/dang_ky_nen.js, js/dang_ky_quan_tri.js, js/dang_ky_quan_tri_2.js, js/dang_ky_gv_hs.js, style.css: L3–L4 UI
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: VG2 entries
- ~20 older tests: adapted to the new contract (see Decisions)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-27 | Sonnet | role-play test, repro tests, plan | planner role; Truong asked directly |
| 2026-11-27 | Sonnet | implemented VG2 L1–L4, tests, CHANGELOG/TIEN_DO, pushed `638b556`; handoff at context limit | checker + CI still pending |
| 2026-11-27 | Opus | CI debug: 5 red CI tests fixed, 3 review bugs fixed (+ regression test), CHANGELOG/TIEN_DO | Build Windows workflow is manual-only (publishes a release): not triggered |
| 2026-11-27 | Opus | accent-free / font-insensitive login, 18 tests, merged with remote L1–L4 | Truong asked directly |
