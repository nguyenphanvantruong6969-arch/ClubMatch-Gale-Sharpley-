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
- [ ] DKL lot (coder+checker, after DK4-UI and CI green) then DK5
- [ ] DK4-UI: portal look/guidance like v8 (prompt below) → registry row, test-file count, `READY | head <sha>`

## Current state (2026-11-25)
- UPDATE: DK4-CI-2 (658dec9) targets the 3 red tests below; CI run 45645130466 on 6323281 was IN PROGRESS at
  handoff. First action of the next session: read its result (failed_only logs ≤60 lines).
- Earlier state at head 3eb51b7:
- CI run 45639876967 RED in 3 tests (Linux + Windows), 13 jobs green:
  1. `tests/test_gt3_nhat_ky.py::test_moi_ham_ghi_cua_bang_quyen_deu_duoc_ghi` — `dk_chuyen_giai_doan` (a WRITE
     function) is treated as not logged; DK4-CI seems to have excluded dk_* wholesale in `nhat_ky.py`. Only
     read-only dk_ functions may skip logging; writes need `nkhd_<fn>` labels vi+en. Audit log must never store
     PIN/password/token (dk_dang_nhap, dk_khoi_tao, dk_gv_tu_dang_ky, *_dat_lai_pin).
  2. `tests/test_giao_dien_fg9_ux_nho.py::test_thanh_ben_khong_con_so_thu_tu` and
  3. `tests/test_giao_dien_a14_lop.py::test_thanh_ben_sau_khi_gop_va_bao_chua_co_ket_qua` — expected sidebar lists
     lack the intended admin-only "Đăng ký CLB" link (L5, Opus). Update expected lists only.
- `dang_ky_sang_xep.py` `_dk_tom_tat_xep` has `ORDER BY buoi`: check COLLATE THU_TU_BUOI is present (DK3 fixed its own).
- L5 NOT tried in pywebview on Windows (browser only). Truong must try the CI-built exe.
- UI review (Opus screenshots): app sidebar OK; portal works but is bare vs v8 (no step bar, no 6-phase bar,
  no deadline, cards without description/teacher/room, no gold "next" button for students, cramped admin layout).
- Other branches: DK2 (`claude/gracious-johnson-pnqvrg`) CI green. DK3 (`claude/dk3-cong-dang-ky-that`) CI GREEN at
  bdb2be8 (confirmed by Opus). Its checker PASS (8715ba9) was written while CI was pending → re-run the DK3 checker
  (prompt given to Truong) before merging DK3 → main. DK5/DK6 branches exist at 6234344 (plan only).
- No orchestrator loop running: Truong wants PROMPTS for his collaborator, never auto-run sessions.

## Next steps (ordered; each = a collaborator prompt, Truong runs them)
1. DK4-CI-2 (prompt given to Truong 2026-11-25): fix the 3 tests above + PIN/token masking test; CI green.
2. Checker DK4 (prompt A2) — PASS only if CI green on Linux AND Windows for the head.
3. DK4-UI (prompt given to Truong): v8 look via style.css tokens; tests in test_giao_dien_dk3_cong.py.
0. DK3: fresh checker PASS on bdb2be8+ → Truong merges DK3 → main → DK4 merges origin/main.
4. DK4 → main after its checker PASS.
4b. After DK4-UI: feature audit D1–D45 (read-only, writes docs/phien/DK_DANH_GIA_TINH_NANG.md; prompt given
   to Truong). Likely gaps: PIN slips print (D8), live admin views (D31), receipt links (D24), auto-logout (D25),
   medal swap UI (D34), export versions/step back (D3). Build important gaps as one lot before DK5.
5. DK5 (prompt given: gate on DK4 PASS + green CI), DK6, then Truong tests the exe on Windows.

## Decisions (Truong, 2026-11-25; do not re-ask)
- Opus only writes prompts and plans; it runs sessions or pushes only when Truong explicitly says so.
- New SQLite tables for the portal approved; students register on the program's computers only (no LAN/phone).
- Merge step by step (DK3 → main, then DK4 …). No PR/tag/release by Claude.
- Checker rule: never PASS with CI pending; coder READY only with CI green on Linux and Windows.
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
