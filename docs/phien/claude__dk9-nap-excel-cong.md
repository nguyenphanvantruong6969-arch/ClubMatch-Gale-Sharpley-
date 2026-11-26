# Branch handoff: claude/dk9-nap-excel-cong

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/DK9_GIAO_THUC.md` (size M, AUTO: coder runs its own checker; no human input).

## Feature / goal
Item **DK9** (registry row to add: "Nạp Excel cho cổng đăng ký"). Truong, 2026-11-26: today the registration portal
(`dang_ky.html`) is set up by pasting text (students, teachers) and typing rooms one by one. Add ONE `.xlsx` upload that
sets up all three, "great design, don't overcomplicate". Base = `claude/dk8-giong-ban-mau` @ `1bb488d` (DK8 not in main yet).
Portal setup only; the MAIN app (`index.html`, Sổ nhập) is untouched. All sample data is SIMULATED.

## Decisions by Truong (2026-11-26; do not ask again)
- One file, three sheets: «Học sinh» (`Mã HS | Họ tên | Lớp`), «Giáo viên» (`Họ tên`), «Phòng» (`Tên phòng | Sức chứa`).
  Grade (khối) is derived from the class as the paste box does (10A1 → 10); no Khối column.
- Place: portal → Quản trị → tab «Cài đặt», one block «Nạp từ Excel». Not the main app's «Quản lý» tab.
- Needs: «Tải file mẫu» button; «Xem trước» (valid-row counts, error rows with reason) before «Nạp».
- Re-upload = add or update, existing PINs kept. Error rows: load the valid rows, skip the bad ones, list them.
- Phase locks = the existing rule of each list; NO new rule.

## Design (planner's choices, keep unless a test shows a problem)
- Reuse, do not rewrite: `dk_hs_nap_danh_sach(token, text, "them")`, `dk_gv_tao_hang_loat`, `dk_phong_luu`. New module
  `api_dang_ky_excel.py` (mixin on the portal API, same pattern as other `api_*.py`) only READS the workbook, validates,
  and calls those. Excel text cells are normalised like `so_nhap.o_thanh_chu` (numbers such as `10001.0` → `10001`).
- Existing behaviours to keep: room with an existing name → skip and list «đã có» (`dk_phong_luu` raises
  `dk_phong_trung`); teacher with an existing name → skip (no new PIN); student already present → updated, PIN kept.
- File limits: `.xlsx` only, ≤ 5 MB, ≤ 5 000 rows per sheet. Sheet names matched trimmed, NFC, case-insensitive.
  Missing sheet = that list is simply not loaded (preview says so); NO sheet at all = error. Header row 1 required.
- The template's data sheets hold only the header row; a 4th sheet «Hướng dẫn» (ignored on load) has an example, so a
  forgotten example row is never loaded as data.
- Contract `{ok, data, errors}`; new error codes at the END of `i18n_errors.py`, then `python tao_i18n_js.py`;
  register new admin-only functions exactly as `dk_hs_nap_danh_sach` is registered (grep `phan_quyen.py`).
- No schema change, no CSV change, no new library (`openpyxl==3.1.5` is in `requirements.txt`), no allocation change.

## Plan (written by Opus-role planner; ticked by Sonnet)
- [ ] **L1 (must) backend, test first.** `tests/test_dk9_nap_excel.py`: (a) template round-trips: `dk_excel_mau` file →
  `dk_excel_xem_truoc` shows 0 rows, no error; (b) valid 3-sheet file loads exactly the rows, PINs returned once;
  (c) bad rows (empty code, no class, grade out of range, duplicate code, capacity ≤ 0, name > 60) skipped and listed
  with row number + reason, valid rows still load; (d) re-upload keeps student PINs, adds new, skips existing
  teachers/rooms; (e) not `.xlsx` / > 5 MB / no known sheet → error codes; (f) preview writes nothing (DB row counts
  unchanged); (g) non-admin token refused. Then `api_dang_ky_excel.py`: `dk_excel_mau(token)`,
  `dk_excel_xem_truoc(token, b64)` (read-only; counts new / already-present / error rows per sheet), `dk_excel_nap(token, b64)`.
- [ ] **L2 (must) UI.** In `QT2.caiDat` (`js/dang_ky_quan_tri_2.js`) add the block «Nạp từ Excel» (card, `.dk-*` CSS only):
  drop zone + file button, «Tải file mẫu», preview table per sheet (valid / already there / errors with row + reason),
  one gold button «Nạp» enabled only after a preview with ≥ 1 valid row, then show PIN slips via `hienPin`/`phieuPin`
  (PINs appear once). Disabled students sheet in locked phases follows `khoa` as the paste box does. One Chromium
  test file `tests/test_giao_dien_dk9_l2.py`, one shared page fixture; every visible `.btn` ≥ 44 px; one gold button.
  grep ALL tests for any UI string you change. **MILESTONE after L2** (auto checker, see protocol).
- [ ] Close: CHANGELOG, TIEN_DO rows `DK9-L<k>`, registry row DK9, test-file count in `CLAUDE_CHI_TIET.md`, CI green.

## Acceptance (checker uses these)
- Admin can: download template → fill → drop file → read preview → «Nạp» → see PIN slips → students/teachers/rooms
  appear in «Danh sách». Re-upload keeps PINs. Error rows are listed with row numbers, valid rows still load.
- Preview never writes. Teacher/student tokens cannot call the new functions.
- No test weakened; `kiem_nhanh.py` 7/7 (invariant 1: no allocation change); ruff clean; CI green.

## Current state (overwrite each handoff)
- Nothing built yet. Branch created from `claude/dk8-giong-ban-mau` @ `1bb488d`; this file and the protocol are the only additions.

## Decisions and gotchas (keep short)
- Before each lot fetch and merge (`--no-edit`) `claude/dk8-giong-ban-mau` and `main`. Every push cancels running CI (~20 min).
- Portal is school-vocabulary only; the MAIN app must not change look. Playwright `clock.install()` makes `wait_for_function` hang.
- Another session already used the name "DK8-L5" (input feedback) and Truong's visual pass is "DK8-L6"; DK9 lots are DK9-L1/L2.

## Files touched
- (none yet)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-26 | Sonnet (planner role at Truong's request) | Wrote this file and `DK9_GIAO_THUC.md` after two rounds of questions | No product code |
