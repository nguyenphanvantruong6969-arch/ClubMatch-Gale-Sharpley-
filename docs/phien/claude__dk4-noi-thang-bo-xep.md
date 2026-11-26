# Branch handoff: claude/dk4-noi-thang-bo-xep

> Read CLAUDE.md, then THIS file, then `docs/phien/DK3_DK4_VONG_TU_DONG.md` (spec). English. Cap 150 lines.
> Earlier context: `docs/phien/claude__gracious-johnson-pnqvrg.md` (D1–D42), `claude__dk2-cau-noi-so-nhap.md` (D43–D45).

## Feature / goal
DK4: connect DK3 registration tables (`dk_*`) straight to the allocator: "Chốt và xếp" (`dk_chot_va_xep`),
equal to the dk2 export + `import_so_nhap` path; plus entry from the app (L5). Based on `claude/dk3-cong-dang-ky-that`.

## Plan
- [x] L1 `dang_ky_sang_xep.py`: dk tables -> Sổ nhập (via `dk2_so_nhap`) -> `import_so_nhap`
- [x] L2 `dk_chot_va_xep`: backup, validate, import (1 txn), run_pipeline (1 txn), rollback via in-memory snapshot
- [x] L3 `tests/test_dk4_hai_duong_trung_khit.py` both paths, 3 datasets x 20 seeds, match_results equal
- [x] L4 button + result summary in `dang_ky_quan_tri.js` + Playwright test
- [x] L5 sidebar "Đăng ký CLB" (admin only) ↔ portal "← Mở phần mềm xếp CLB" / "Xem kết quả trong phần mềm"
- [x] L0 checker items: no str(e) to UI, PIN attempt limit, 10/5 limits as settings (DK4-FIX commits)
- [x] CI green (run 1660, head 42b93af, success incl. DK4-L0a–e + merge of DK4-FIX) → checker DK4 (PASS only with CI green Linux+Windows)
- [x] Audit D1–D45 → `DK_DANH_GIA_TINH_NANG.md`; lot plan + prompts → `DKL_GIAO_THUC.md` (v8 diff table, 4 lots, same branch); CI green at 42b93af
- [x] DKL lots L2→L3→L1→L4 built locally by Sonnet in one session (2026-11-25 night); CI NOT yet run, checker NOT yet run
- [ ] DKL: CI green on Linux+Windows (CI on 5ac6d4f not read yet) → checker (prompt in DKL_GIAO_THUC §5) → `READY | head <sha>` → then DK5
- [x] DK4-UI: portal look/guidance like v8 — READY | head 8bde1ff (CI run 1671 green; contains DK4-UI commit a03ec2a plus DKL lots)

## Current state (2026-11-25, end of night session)
- Head `5ac6d4f` pushed. CI green earlier at `42b93af` (DK4 code). DKL lots L1–L4 built locally and pushed; CI on `5ac6d4f` was started by the push but its result is NOT read yet; checker NOT run.
- DK4-UI (cc80e00) merged. DKL scope/row→test map: see "DKL status" below and `docs/phien/DKL_GIAO_THUC.md` §2.
- 428 test files. Local: 106 related tests + 13 UI tests pass, ruff clean, kiem_nhanh 7/7. Full suite not run.
- Pywebview/Windows untested: score entry, PIN slip print (`window.print()`), `confirm()` dialogs.

## Next steps (ordered)
1. Read CI for `5ac6d4f` (`mcp__github__actions_list`, failed_only logs ≤60 lines); fix reds only (no docs-only pushes while a run is in flight).
2. Checker DKL: Truong pastes the checker prompt (DKL_GIAO_THUC §5). PASS needs CI green on Linux AND Windows.
3. Write `READY | head <sha>` here; Truong merges DK3 → main, then DK4 (+DKL) → main. No PR/tag by Claude.
4. DK5 (`claude/dk5-dien-tap`), DK6 (`claude/dk6-goi-phat-hanh`), then Truong tries the CI-built exe on Windows.
5. Decide: portal backup RESTORE (not built), per-grade fold, admin password change.

## Decisions (Truong, 2026-11-25; do not re-ask)
- Opus only writes prompts and plans; it runs sessions or pushes only when Truong explicitly says so.
- New SQLite tables for the portal approved; students register on the program's computers only (no LAN/phone).
- Merge step by step (DK3 → main, then DK4 …). No PR/tag/release by Claude.
- Checker rule: never PASS with CI pending; coder READY only with CI green on Linux and Windows.
- Portal backup RESTORE (Truong, 2026-11-26): option A — NOT built in the portal; restore stays manual from the backup file. Closes the "Needs Truong" restore item. Still open: `_MAX_BACKUPS` can push out the pre-«Chốt và xếp» backup when «Sao lưu ngay» is pressed repeatedly.
- Later options (not scheduled): DK4B direct table write only if "Chốt và xếp" > 60 s for 798 students;
  DK7 single source of truth (dk_* tables feed the app's manual screens).

## Files touched (this branch, beyond DK3)
- dang_ky_sang_xep.py, api.py, phan_quyen.py, i18n_errors.py, i18n_loi.js, i18n.js, nhat_ky.py (DK4-CI)
- index.html, js/01_khung.js, js/dang_ky_nen.js, js/dang_ky_quan_tri.js, js/dang_ky_gv_hs.js, style.css
- tests/test_dk4_chot_va_xep.py, test_dk4_hai_duong_trung_khit.py, test_giao_dien_dk4_chot_xep.py,
  test_giao_dien_dk4_cong_vao.py; CHANGELOG.md, docs/ke_hoach/{TIEN_DO,CLAUDE_CHI_TIET}.md

- DK4-UI (Sonnet, 2026-11-25): portal restyled like v8 (student step bar + two columns, admin 6-phase bar + deadline + progress bars,
  teacher 3-step form). Backend: `dk_hs_clb_hop_le` adds `giao_vien`, `chi_tieu`. Tests: dk3_cong 10 pass (+5), dk3/dk4/giao_dien_dk4/van_phong
  118 pass, ruff clean, kiem_nhanh 7/7. Screenshots (1366 / 390 / admin, scale 1): `docs/phien/dk4_ui/*.png`. Not tried in pywebview/Windows.
  Note: "+ Thêm" is now disabled (not hidden) at the limit; ≤7 items per frame (D37) is not enforced on the club list.

## DK4-finish (L0a–e) status (Sonnet coder, 2026-11-25)
READY | head 42b93af
- L0a no str(e) to UI; L0b PIN lock 5 tries → 5 min (persisted in dk_cai_dat) + `dk_mo_khoa` + unlock button; L0c limits read via `dk_trang_thai`/`dk_dat_gioi_han`; L0d `_dk_hoan_nguyen` keeps append-only log rows (test proves a failed run's run_history row would otherwise be lost); L0e `bat_luat` logged + `#dkLuuY` in summary.
- Later pushes by other sessions (DKL/DK4-UI) are outside this READY; run 1666+ not judged here.

## Needs Truong
- Try the exe on Windows: sidebar "Đăng ký CLB" ↔ portal round trip (pywebview untested).

## Session log
| Date | Model | What | Notes |
|---|---|---|---|
| 2026-11-25 | Sonnet | L1–L4 | |
| 2026-11-25 | Sonnet | L0 / checker FIX items, DK4-CI (11 → 3 red tests) | |
| 2026-11-25 | Opus | L5 entry link; CI triage; UI screenshots review; handoff at ~400k context | prompts only from now |
| 2026-11-25 | Opus | Confirmed DK3 CI green (bdb2be8); handoff updated | no new work |
| 2026-11-25 | Opus | DK4 CI check: run 45645130466 in progress (includes DK4-CI-2) | no new work |
| 2026-11-25 | Opus | Answered feature-coverage question; added audit step 4b | no new work |

## DKL status (Sonnet, 2026-11-25 night; Truong asleep, "run CI later")
- Built all four lots in one session (no checker round between). Scope = `DKL_GIAO_THUC.md` §2. CI NOT run, checker NOT run → NOT READY.
- Row → test (all in `tests/`; Chromium tests need `pip install playwright`):
  - S1 link bài thi · S2 "Dưới N thì không xét" · S3 thẻ CLB đủ thông tin/không lộ số đông · S4 hạn chót + hết hạn · S5 nộp rỗng · S6 "Đã gửi lúc"/"Xong, thoát": `test_giao_dien_dkl_hoc_sinh.py` test_1–test_4. S7 (bước tách riêng) DK4-UI, not re-tested.
  - S8 sửa/xoá CLB, S9 báo lỗi từng bước + https + phòng trống: `test_giao_dien_dkl_giao_vien.py` test_1–test_3, `test_dkl_cai_dat.py::test_clb_xoa_va_phong_trong_theo_buoi`.
  - A1 gia hạn/đóng ngay · A3 phiếu PIN · A4 thay cả danh sách · A5 xoá phòng · A6 duyệt kèm chỉ tiêu/phòng + sửa sau mở (tăng chỉ tiêu, đổi phòng, xoá CLB có xác nhận "N học sinh bị ảnh hưởng") · A7 nhu cầu + chưa đăng ký · A8 danh sách lý do: `test_giao_dien_dkl_quan_tri.py` test_1, test_2, test_3, test_7.
  - A2 nhập điểm (gõ, dán, Dưới sàn, Chốt điểm): `test_giao_dien_dkl_quan_tri.py::test_4`; backend `test_dkl_cai_dat.py::test_bang_diem_xem_truoc_va_phien_ban_xuat`.
  - A9 Cài đặt (mã trường, buổi/khối khoá, giới hạn): `test_5` + `test_dkl_cai_dat.py::test_cai_dat_doi_*`. A10 xem trước + phiên bản xuất: `test_6` + backend test. A11 sao lưu: `test_6` + `test_sao_luu_*`. A12 khoá quản trị: backend `GIAY_NGHI_QUAN_TRI` + message on `DK.henGio` (only the Cài đặt text is asserted, the timeout message itself is NOT tested).
- Changed existing test expectations (recorded in CHANGELOG): `test_giao_dien_dk3_cong.py` test_2/test_3.
- Test-file count 428. `ruff` clean, `kiem_nhanh.py` 7/7 (soat-ma tier 1 only: the four manual tiers were NOT run).
- Not verified: full suite, CI (Linux+Windows), pywebview/Windows, `window.print()` in WebView2 (copy button is the fallback), `confirm()` behaviour in pywebview.
- Simplifications: "Chốt điểm" only checks missing scores (gold button stays «Chốt và xếp»); PIN slips print only from the just-created/reset list; per-grade fold and admin password change not built.
## DKL-G status (Sonnet, 2026-11-26) — fixes after the v8 comparison
- [x] G1 identity confirmation "Đúng là em chứ?" (+ "Không phải em" → logout) — `test_giao_dien_dkl_hoc_sinh.py::test_3b_xac_nhan_danh_tinh_dung_la_em_khong_phai_em`
- [x] G2 admin auto-lock: server `GIAY_NGHI_QUAN_TRI` = 120 s = v8's 2 min → no conflict; client `DK.GIAY_NGHI_QUAN_TRI = 120` (was 110), login text "Tự khoá sau 2 phút không thao tác." — `test_giao_dien_dkl_quan_tri.py::test_8_man_dang_nhap_noi_tu_khoa_2_phut_va_het_gio_hien_thong_bao`
- [x] G3 A12 timeout message tested (Playwright fake clock, no test hook). The test exposed 3 real bugs, fixed: message wiped by async `dauTrang`; 30 s auto-refresh reset the idle timer (admin on "Việc bây giờ" never locked); in-flight calls after lock overwrote the page/message.
- [x] G4 D37 fold: ≤7 cards per buổi then "Xem thêm (N)" — `test_giao_dien_dkl_hoc_sinh.py::test_3c_moi_buoi_toi_da_7_the_roi_xem_them`
- Changed expectations: `test_giao_dien_dk3_cong.py` (test_5, `_vao_hs`), `test_dk4_l0c_gioi_han_tu_backend.py` (extra click "Đúng là em").
- soat-ma: `kiem_nhanh.py` 7/7; tier-3 eye check of the JS diff only (no XSS: all text via `h()`, PIN never stored). Tiers 1, 2, 4 untouched by this diff (no algorithm/backend/schema change), not re-run.
- CI run 1673 (head b28afe9) green on Linux 1–6, Windows 1–9 and ruff. Not verified: pywebview/WebView2 by hand.
- **DKL-G READY | head b28afe9** (only DKL-G; the whole DKL still needs the checker, DKL_GIAO_THUC §5).

## Needs Truong (DKL)
- Backup RESTORE from the portal ("Khôi phục từ bản sao lưu", DKL-G item 5) NOT built, needs Truong's decision (restore overwrites app.db). Original note: backup RESTORE from the portal (v8 has it) not built: needs a decision (restore overwrites app.db). Also `_backup_db` keeps only `_MAX_BACKUPS` copies, so pressing «Sao lưu ngay» repeatedly can push out the backup taken before the last «Chốt và xếp».
- Try the CI-built exe: score entry, PIN slip printing, teacher edit/delete.
| 2026-11-25 | Sonnet | DKL v8 diff table, built L1–L4 + tests, pushed 5ac6d4f; handoff at ~400k context | CI/checker pending |
