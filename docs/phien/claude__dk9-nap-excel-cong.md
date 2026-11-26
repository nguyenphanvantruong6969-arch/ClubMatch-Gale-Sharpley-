# Branch handoff: claude/dk9-nap-excel-cong

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/DK9_GIAO_THUC.md` (size M, AUTO: coder runs its own checker; no human input).

Status: DONE 593c0b7 CI green 2026-11-26 (run 1736 lượt 2: job Windows 8/9 chạy lại 1 lần vì `test_a13_12_browser_host::test_tai_lai_trang_khong_tat_may_chu` chập chờn thời gian, không liên quan DK9)

## Tóm tắt cho Truong (5 dòng)
1. Cổng đăng ký có khối «Nạp từ Excel» ở Quản trị → Cài đặt: tải file mẫu, chọn/thả một tệp .xlsx (ba trang Học sinh, Giáo viên, Phòng), xem trước, rồi «Nạp».
2. Xem trước chỉ đọc, không ghi gì; dòng lỗi được liệt kê kèm số dòng Excel và lý do, dòng hợp lệ vẫn nạp; nạp lại giữ nguyên PIN học sinh cũ, giáo viên và phòng đã có thì bỏ qua.
3. PIN chỉ hiện một lần sau «Nạp» trên phiếu gộp (tên · mã · lớp); chỉ quản trị gọi được; không đổi schema, CSV, thuật toán hay giao diện chính.
4. Test: 16 backend + 10 giao diện Chromium (gồm XSS); checker vòng 1 FIX ba mục nhỏ đã sửa, vòng 2 PASS; ruff sạch, kiem_nhanh 7/7; mutation 5 chỗ đều làm test đỏ.
5. Nhánh mang theo cả DK8 (chưa vào main) và merge sạch vào main; PR #44 đã mở. Còn lại: nút «In phiếu»/«Chép PIN» là nút nhẹ có sẵn của cổng; trang tính >20 000 hàng thô bị từ chối; tải file mẫu bằng Blob chưa thử trong WebView2 máy bàn.

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
- [x] **L1 (must) backend, test first.** `tests/test_dk9_nap_excel.py`: (a) template round-trips: `dk_excel_mau` file →
  `dk_excel_xem_truoc` shows 0 rows, no error; (b) valid 3-sheet file loads exactly the rows, PINs returned once;
  (c) bad rows (empty code, no class, grade out of range, duplicate code, capacity ≤ 0, name > 60) skipped and listed
  with row number + reason, valid rows still load; (d) re-upload keeps student PINs, adds new, skips existing
  teachers/rooms; (e) not `.xlsx` / > 5 MB / no known sheet → error codes; (f) preview writes nothing (DB row counts
  unchanged); (g) non-admin token refused. Then `api_dang_ky_excel.py`: `dk_excel_mau(token)`,
  `dk_excel_xem_truoc(token, b64)` (read-only; counts new / already-present / error rows per sheet), `dk_excel_nap(token, b64)`.
- [x] **L2 (must) UI.** In `QT2.caiDat` (`js/dang_ky_quan_tri_2.js`) add the block «Nạp từ Excel» (card, `.dk-*` CSS only):
  drop zone + file button, «Tải file mẫu», preview table per sheet (valid / already there / errors with row + reason),
  one gold button «Nạp» enabled only after a preview with ≥ 1 valid row, then show PIN slips via `hienPin`/`phieuPin`
  (PINs appear once). Disabled students sheet in locked phases follows `khoa` as the paste box does. One Chromium
  test file `tests/test_giao_dien_dk9_l2.py`, one shared page fixture; every visible `.btn` ≥ 44 px; one gold button.
  grep ALL tests for any UI string you change. **MILESTONE after L2** (auto checker, see protocol).
- [x] Close: CHANGELOG, TIEN_DO rows `DK9-L<k>`, registry row DK9, test-file count in `CLAUDE_CHI_TIET.md`, CI green.

## Acceptance (checker uses these)
- Admin can: download template → fill → drop file → read preview → «Nạp» → see PIN slips → students/teachers/rooms
  appear in «Danh sách». Re-upload keeps PINs. Error rows are listed with row numbers, valid rows still load.
- Preview never writes. Teacher/student tokens cannot call the new functions.
- No test weakened; `kiem_nhanh.py` 7/7 (invariant 1: no allocation change); ruff clean; CI green.

## Current state (overwrite each handoff)
MILESTONE 1 READY | head 4cfcc7e | base 1bb488d
Checker round 1 = FIX (3 small items) -> fixed in the next commit (result block kept after Nạp, PIN table label + spacing, max_col). Round 2 checker started after CI is green.
- L1 + L2 + design polish done (tests: `test_dk9_nap_excel.py` 15, `test_giao_dien_dk9_l2.py` 9; related UI files green; kiem_nhanh 7/7; ruff clean). Truong (2026-11-26, later): "spawn a checker and run CI until green and mergeable into main; do not wait" — checker started without waiting for CI; coder owns CI.
- UI note: students sheet skipped in locked phases via optional `bo_hoc_sinh`. Template download = Blob anchor (browser host); not testable in desktop WebView2 here.

## Decisions and gotchas (keep short)
- Before each lot fetch and merge (`--no-edit`) `claude/dk8-giong-ban-mau` and `main`. Every push cancels running CI (~20 min).
- Portal is school-vocabulary only; the MAIN app must not change look. Playwright `clock.install()` makes `wait_for_function` hang.
- Another session already used the name "DK8-L5" (input feedback) and Truong's visual pass is "DK8-L6"; DK9 lots are DK9-L1/L2.

## Files touched
- L2: `js/dang_ky_quan_tri_2.js`, `style.css`, `tests/test_giao_dien_dk9_l2.py`, `api_dang_ky_excel.py` (`bo_hoc_sinh`).
- L1: `api_dang_ky_excel.py` (new), `api.py`, `phan_quyen.py`, `i18n_errors.py`, `i18n_loi.js`, `tests/test_dk9_nap_excel.py`, CHANGELOG, TIEN_DO.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-26 | Sonnet (planner role at Truong's request) | Wrote this file and `DK9_GIAO_THUC.md` after two rounds of questions | No product code |
| 2026-11-26 | Sonnet (coder) | L1 backend + 14 tests | merged dk8 + main first; L1 CI not awaited separately (L2 push covers the same head) |
| 2026-11-26 | Sonnet (coder) | L2 UI + 9 Chromium tests, `bo_hoc_sinh` option | merged main + dk8 again; screenshots checked by eye |
| 2026-11-26 | Sonnet (checker) | Round 1: FIX x3 (see `__checker.md`) | backend/acceptance PASS |
| 2026-11-26 | Sonnet (coder) | Fixed the 3 items; 16 + 9 tests green | |

## soat-ma report (DK9, report only)
- T2 backend: preview writes nothing (row counts before = after, tested); only admin token; SQL parametrised (reads via fixed queries, writes via existing functions); dirty cells (10001.0, blank rows, merged, formulas) tolerated; no `run_history` touch. Not atomic across the three lists (each = one existing transaction) — re-uploading the same file is idempotent.
- T3 UI: names with `<img onerror>` render as text (`test_j`); `ok=false` shown via `DK.chay`; one gold button; all `.btn` ≥ 44 px; 390 px no horizontal scroll.
- T4: 5 deliberate mutations (`<= 0`, duplicate check, grade range `<=`→`<`, 5000 limit, mode "them"→"thay") each turned a DK9 test red; ruff clean; kiem_nhanh 7/7; tests only added.
- Known, left: >20 000 raw rows in a sheet are rejected with the «too many rows» message; «In phiếu»/«Chép PIN» use the portal's existing ghost buttons.
