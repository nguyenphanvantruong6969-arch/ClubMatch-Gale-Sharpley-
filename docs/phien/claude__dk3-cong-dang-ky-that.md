# Branch handoff: claude/dk3-cong-dang-ky-that

> Read CLAUDE.md, then THIS file, then `docs/phien/DK3_DK4_VONG_TU_DONG.md` (spec). English. Cap 150 lines.

## Goal
DK3: real registration portal backend + UI (decisions D1–D45 in `claude__gracious-johnson-pnqvrg.md`), built from
the v8 prototype. New SQLite tables `dk_*`, `api_dang_ky.py`, `js/dang_ky_*.js`, "Xuất Sổ nhập" via `dk2_so_nhap`.

## Plan
- [x] L1 schema `dang_ky_schema.py` + hook in `di_tru_schema` (step "dk3")
- [x] L2 `api_dang_ky.py` (DangKyMixin) + i18n codes + QUYEN entries (CONG_KHAI, own auth)
- [x] L3 UI `js/dang_ky_*.js` + CSS section + `tests/test_giao_dien_dk3_*.py`
- [x] L4 "Xuất Sổ nhập" (`dinhDang` 1 JSON -> `dk2_so_nhap.ghi_tu_ban_mau`), test imports 0 errors + allocates
- [x] Registry row, test-file count; [x] CI green

## Current state
- L1–L4 done: tests/test_dk3_schema.py, test_dk3_api.py, test_giao_dien_dk3_cong.py (needs `pip install playwright`). UI is a separate page `dang_ky.html` (not linked from index.html on purpose: no change to existing frames). Open it at `<base url>/dang_ky.html?t=<token>` in browser mode, or `window.location` from a launcher; Truong may want a link later. `kiem_nhanh` trung_khit fails only because env has no `origin/main`
  (not caused by this branch).

## Status
CI green | head bdb2be8 (run 45642162707, Linux + Windows + lint all green)

## Needs Truong
- (none)

## Session log
| Date | Model | What | Notes |
|---|---|---|---|
| 2026-11-25 | Sonnet | L1 schema | |
| 2026-11-25 | Sonnet | L2 API | |
| 2026-11-25 | Sonnet | L3 UI, L4 export, docs | CI pending |
