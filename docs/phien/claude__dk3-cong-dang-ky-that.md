# Branch handoff: claude/dk3-cong-dang-ky-that

> Read CLAUDE.md, then THIS file, then `docs/phien/DK3_DK4_VONG_TU_DONG.md` (spec). English. Cap 150 lines.

## Goal
DK3: real registration portal backend + UI (decisions D1–D45 in `claude__gracious-johnson-pnqvrg.md`), built from
the v8 prototype. New SQLite tables `dk_*`, `api_dang_ky.py`, `js/dang_ky_*.js`, "Xuất Sổ nhập" via `dk2_so_nhap`.

## Plan
- [x] L1 schema `dang_ky_schema.py` + hook in `di_tru_schema` (step "dk3")
- [ ] L2 `api_dang_ky.py` (DangKyMixin) + i18n codes + QUYEN entries (CONG_KHAI, own auth)
- [ ] L3 UI `js/dang_ky_*.js` + CSS section + `tests/test_giao_dien_dk3_*.py`
- [ ] L4 "Xuất Sổ nhập" (`dinhDang` 1 JSON -> `dk2_so_nhap.ghi_tu_ban_mau`), test imports 0 errors + allocates
- [ ] Registry row, test-file count, CI green, then `READY | head <sha>`

## Current state
- L1 done (tests/test_dk3_schema.py, 2 pass). `kiem_nhanh` trung_khit fails only because env has no `origin/main`
  (not caused by this branch).

## Needs Truong
- (none)

## Session log
| Date | Model | What | Notes |
|---|---|---|---|
| 2026-11-25 | Sonnet | L1 schema | |
