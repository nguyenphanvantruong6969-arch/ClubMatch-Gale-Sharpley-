# Branch handoff: claude/dk4-noi-thang-bo-xep

> Read CLAUDE.md, then THIS file, then `docs/phien/DK3_DK4_VONG_TU_DONG.md` (spec). English. Cap 150 lines.

## Feature / goal
DK4: connect DK3 registration tables (`dk_*`) straight to the allocator: "Chốt và xếp" button
(`dk_chot_va_xep`), equal to the dk2 export + `import_so_nhap` path. Based on `claude/dk3-cong-dang-ky-that`.

## Plan
- [x] L1 `dang_ky_sang_xep.py`: dk tables -> Sổ nhập (via `dk2_so_nhap`) -> `import_so_nhap`
- [x] L2 `dk_chot_va_xep`: backup, validate, import (1 txn), run_pipeline (1 txn), rollback via in-memory snapshot
- [x] L3 `tests/test_dk4_hai_duong_trung_khit.py` both paths, 3 datasets x 20 seeds, match_results equal
- [x] L4 button + result summary in `dang_ky_quan_tri.js` + Playwright test
- [ ] CI green, registry row, test-file count, then `READY | head <sha>`

## Current state
- L1+L2 done (tests/test_dk4_chot_va_xep.py, 5 pass; ruff + kiem_nhanh 7/7). Locked seed: a second press with another seed fails with `dk_chot_that_bai` (hat_giong_da_khoa), DB restored.
- L3: 60 cases (3 sets x 20 seeds) path A == path B on every match_results row. L4: button + summary, Playwright test passes (needs `pip install playwright`).
- Merged DK3 branch into this one (ff not possible).

- L5 (Opus, 2026-11-25, Truong asked): entry from the app — sidebar "Đăng ký CLB" (admin only) opens dang_ky.html;
  admin in the portal gets "← Mở phần mềm xếp CLB"; after "Chốt và xếp", "Xem kết quả trong phần mềm" opens
  index.html#ket-qua. Keeps `?t=` token for browser_host. Test tests/test_giao_dien_dk4_cong_vao.py. NOT yet tried in
  pywebview on Windows. Coder session was interrupted after L4; L0 items (error-detail leak, PIN attempt limit,
  hard-coded 10/5) NOT done; DK4 not reviewed by a checker yet.

## Needs Truong
- (none)

## Session log
| Date | Model | What | Notes |
|---|---|---|---|
| 2026-11-25 | Sonnet | L1+L2 | |
