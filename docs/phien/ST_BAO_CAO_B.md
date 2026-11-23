# ST-B bug report (real-UI stress test, Chromium) — branch claude/happy-cerf-xvn495-st-b

All data SIMULATED. Production code untouched. Run: `.venv/bin/python -m pytest -q --tb=short tests_stress/b/<file> -p no:cacheprovider`.
Screenshots (deviceScaleFactor 1): `docs/phien/anh_st_b/`. Backend report: branch `claude/happy-cerf-xvn495-st-a`, `ST_BAO_CAO_A.md`.

## Summary (severity counts) — updated at end of each lot
| S1 | S2 | S3 | S4 | total |
|---|---|---|---|---|
| 1 | 0 | 5 | 2 | 8 |

## Lot status
| Lot | State | Tests |
|---|---|---|
| B1 | done | test_b1_dieu_huong_cai_dat.py (11 tests; 3 xfail strict = ST-B-001, ST-B-002 x2) |
| B2 | done | test_b2_nhap_tep.py (7 tests), test_b2_quan_ly.py (13 tests); xfail strict: ST-B-003..008 |
| B3 | – | |
| B4 | – | |

## Bugs
| id | sev | area | title | repro | invariant |
|---|---|---|---|---|---|
| ST-B-001 | S3 | Kết quả tab | Results table keeps showing the PREVIOUS run's assignments (no loading frame, no stale banner) until the reload finishes | tests_stress/b/test_b1_dieu_huong_cai_dat.py::test_b1_bang_ket_qua_cu_hien_khi_tai_cham | — |
| ST-B-002 | S3 | Cài đặt / Quản lý | After clicking a mode card, the "Chia CLB theo loại" switch just below keeps its OLD enabled/checked state and note until the tab is re-entered | tests_stress/b/test_b1_dieu_huong_cai_dat.py::test_b1_cong_tac_chia_loai_cu_sau_khi_doi_che_do | — |
| ST-B-003 | S1 | import | Re-importing a Sổ that has no test marks silently deletes every stored tick + score (337 → 0); preview does not warn (extends ST-A-004) | tests_stress/b/test_b2_nhap_tep.py::test_b2_nap_lai_so_khong_co_diem_xoa_diem_cu_khong_canh_bao | — |
| ST-B-004 | S3 | import + kiosk | A student id differing only in case (`dc001` vs `DC001`) becomes a SECOND student, via Sổ import and via "Nhập tại chỗ" | tests_stress/b/test_b2_nhap_tep.py::test_b2_ma_hoc_sinh_khac_hoa_thuong_thanh_hoc_sinh_moi, test_b2_quan_ly.py::test_b2_nhap_tai_cho_ma_khac_hoa_thuong_tao_hoc_sinh_trung | — |
| ST-B-005 | S4 | import | Dropping several files uses the first .xlsx and ignores the rest without a word | tests_stress/b/test_b2_nhap_tep.py::test_b2_hai_tep_mot_lan_tot_va_xau | — |
| ST-B-006 | S3 | Quản lý › CLB | Capacity `1.5` → generic "Không lưu được… Hãy thử lại" + raw Python text `invalid literal for int() with base 10: '1.5'` in the details; no field error | tests_stress/b/test_b2_quan_ly.py::test_b2_form_clb_chi_tieu_thap_phan_bao_loi_ky_thuat | — |
| ST-B-007 | S3 | Quản lý › CLB | A club that has preferences/results can never be deleted from the UI; the message ("Hãy xử lý các dữ liệu đó trước") names no way to do it (same family as ST-A-005) | tests_stress/b/test_b2_quan_ly.py::test_b2_xoa_clb_dang_co_nguyen_vong_khong_chi_duong | — |
| ST-B-008 | S4 | Việc tiếp theo | After a late arrival the bar says "Dữ liệu có cảnh báo nghiêm trọng, cần sửa trước khi chạy" while the Run button is enabled and the run succeeds | tests_stress/b/test_b2_quan_ly.py::test_b2_viec_tiep_theo_noi_can_sua_truoc_khi_chay_nhung_nut_chay_van_bat | — |

### ST-B-001
Steps: new workspace → Cài đặt: Huy chương → import the shared Sổ (UI) → run → open Kết quả (150 rows) → Cài đặt: Chỉ xếp →
run → click tab Kết quả while `get_club_fill_stats` takes 1.5 s (a stand-in for a large school's slow load).
Expected: the table is cleared / shows a loading frame (UX2 `hienKhungCho`) or the stale banner (`kqCuBanner`) until fresh data arrives.
Actual: for the whole load the table shows the previous run's club for many students (at 300 ms: `DC091` shows Hội hoạ, DB says Khoa học);
`#kqCuBanner` hidden. Also seen once without any slowing (the 50-switch test failed once at switch 15, passed on the next 3 runs,
which now poll): a read right after the tab opens can return the old run. It heals by itself.
Risk: an admin reads / prints / exports-by-screen the wrong assignment right after re-running. Screenshot: `docs/phien/anh_st_b/ST-B-001_bang_ket_qua_cu.png`.
Suspected: `loadKetQuaTab` → `veKetQua` → `veKqTheoMa` (js/09_the_xem.js); `kqVeBang` replaces rows only after the fetch.

### ST-B-002
Steps: Cài đặt: Chia 100 → Quản lý › Câu lạc bộ (switch visible, enabled) → Cài đặt: click Huy chương, wait 2.5 s (and the reverse).
Expected: `#mt2CongTac` disabled + checked + note "Đang bật vì đang dùng chế độ Huy chương…" (and enabled again after the reverse switch),
as `mt2VeChiaLoai` computes from `get_chia_loai`.
Actual: the switch keeps the old state (still enabled / unchecked after Huy chương; still disabled after leaving it) until the main tab is clicked again.
Config is right (`fa_daa` true); only the control and the note lag. Clicking it in the stale state sends `chia_loai` while Huy chương is on.
Screenshots: `docs/phien/anh_st_b/ST-B-002_cong_tac_chia_loai_cu_*.png`.
Suspected: `ux1aApDungSong` (js/18_cai_dat.js) does not call `mt2VeChiaLoai`; the card click re-renders only the Cài đặt block.

### ST-B-003
Steps: Cài đặt: Huy chương → import the shared Sổ (337 ticks, 337 scores, 900 medal rows) → import the same Sổ with the sub-header row of
"2. Học sinh" deleted (preview: "…0 lượt thi", no "Lưu ý") → click import → `club_test_selection` 337 → 0, `club_scores` 337 → 0 (medals stay 900).
Expected: preview warns "N scores already stored will be deleted" (the existing `so_nhap_canh_bao_xoa_diem` fires only when the sheet marks "thi" on a cell that already has a
score; here the sheet marks nothing, so `n_xoa` = 0) — or the import keeps scores of students whose cells are empty. No backup is taken by `import_so_nhap`, no undo.
Actual: silent loss of all scores of every student in the sheet. Realistic trigger: re-import a prefs-only Sổ to add late students, or a Sổ saved without the sub-header.
Related: ST-A-004 (same file shape, empty DB: scores ignored with no warning). Screenshot: `ST-B-003_xem_truoc_khong_canh_bao_xoa_diem.png`.
Suspected: `xem_truoc_so_nhap` warning block (`n_xoa = sum(1 for cap in cap_thi if cap in diem)`), `DELETE FROM club_test_selection WHERE student_id = ?` in the import loop (`api_nhap.py`).
Severity note: data loss ⇒ S1; downgrade to S3 if Truong confirms "the Sổ is the single source of truth" and wants only a warning.

### ST-B-004
Steps: shared Sổ imported (150 students). (a) import the Sổ with `DC001` changed to `dc001` → preview "150 học sinh" no warning → students 150 → 151, 8 extra preference rows;
(b) kiosk "Nhập tại chỗ": id `dc001`, name x → "Tạo" → 151 students. Expected: same student (ids are case-insensitive elsewhere: club names, medals) or a clear "similar id exists" warning.
Actual: two students, the copy has its own preferences, both get placed, seats counted twice. Screenshots `ST-B-004_ma_hoa_thuong.png`, `ST-B-004_nhap_tai_cho_dc001.png`.
Suspected: `_tao_hoac_bo_sung_hoc_sinh` / `create_student_if_missing` (exact-match lookup).

### ST-B-005
Steps: drop two files (good + corrupt) on #dropZone. Actual: queue shows only the first .xlsx (`themFileVaoHangDoi`: `files.find(laFileExcel) || files[0]`), no note. Screenshot `ST-B-005_tha_hai_tep.png`.

### ST-B-006
Steps: Quản lý › Câu lạc bộ: id T4, name x, capacity `1.5` (the field is `type=number`, no `step`), Lưu. Expected: inline error on the capacity field like `0` / `-3` get.
Actual: toast/feedback "Không lưu được câu lạc bộ. Hãy thử lại." + details "invalid literal for int() with base 10: '1.5'"; retrying never works. The same stale text stays when the NEXT attempt
fails for another reason (reserve > capacity shows the inline error but the old feedback line remains). Screenshot `ST-B-006_chi_tieu_1.5.png`. Suspected: `create_or_update_club` (int() on raw string).

### ST-B-007
Steps: run once; Quản lý › CLB › Xoá THU_6_6 (2 clicks). Actual: refused, "…đang có trong 64 nguyện vọng và 15 kết quả. Hãy xử lý các dữ liệu đó trước." — no screen removes a club from 64 students'
preferences, so the only exit is wiping all data. Screenshot `ST-B-007_xoa_clb_co_nguyen_vong.png`. Suspected: `delete_club` refusal text / missing "retire club" action.

### ST-B-008
Steps: shared Sổ, Huy chương, run; Nhập tại chỗ: new student NEW01 with one test club + one preference; open Xếp CLB. Actual: bar "Dữ liệu có cảnh báo nghiêm trọng, cần sửa trước khi chạy." with button "Xem cảnh báo",
yet `#btnRun` is enabled and the run succeeds (the "nghiêm trọng" items are "1 student has no score yet"). Wording promises a block that does not exist. Screenshot `ST-B-008_viec_tiep_theo.png`.

## Checked, no bug (B2)
- 22 bad files through the UI (0-byte, text renamed .xlsx, truncated, .xls/.pdf/.csv/.zip, missing / empty sheets, capacity 0 / -5 / "abc", duplicate student id, duplicate club name, negative / date scores,
  unknown club, bad Loại, CSV UTF-16 / cp1258 / BOM): each refused with a Vietnamese message, no traceback / raw key, DB unchanged. Same file imported twice: no duplicates.
- Accepted and sane: "9,5" score, NFD + padded names, 3 150 students (3 000 extra rows) in 5.1 s through the UI (ST-A-002 does not reproduce here: that Sổ has ~1 pref per extra row, so it never spills SQLite's page cache), formulas shown literally, 40 000-char name truncated to 32 767.
- XSS: markup in club and student names never executes (checked on every tab + Quản lý lists, hover); formula-looking names (`=cmd|…`, `@SUM`) are shown as text.
- Club form: capacity 0 / -3 / "abc", reserve > capacity, reserve < 0, empty id / name rejected inline and nothing stored; 300-char name, `<b>`, id with a space accepted.
- Delete with two-step confirm: one click arms ("Bấm lần nữa để xoá"), second deletes; run after deleting an unused club works.
- Học sinh: 63 pages of 50 (3 150), 70 fast "next" clicks end on page 63/63, back 3 pages fine; 9 hostile search strings (`%`, `'`, `" OR 1=1 --`, `<script>`, 200 accents) no error; bulk assign 50 → group stored lower-case (`nhom_a`, by design), bulk clear works, nothing ticked → toast.
- Điểm quyết tâm edit: -5, 101, 1.5, 0, blank: clear messages, DB untouched; after a run the scores are locked (Lưu disabled).
- Chấm điểm: saving an empty table keeps the 57 scores; "abc", "-1" refused with a message; "9,5" accepted. Scores above 10 (11, 1000) are accepted (no upper bound in the code).
- Xoá dữ liệu: first click only changes the label; second deletes; students / clubs counts 0, sidebar no longer shows the old run.
- Nhập tại chỗ late arrival (NEW01): tests + 5 ranked clubs saved in order, run places the student, Results tab = DB; 11 hostile ids/names (empty, spaces, 120-char id, `a/b\c`, SQL text, `=cmd`, XSS name) no error.
- Huy chương step after a run: medals are locked (message "Nhờ người quản lý mở khoá…"), so a late arrival cannot enter medals until an admin unlocks Quản lý › Điểm quyết tâm; the run then places the student in Tự do clubs only. Acceptable but see Needs Truong.
- #ux1aSauXep: shows after a run in Huy chương, controls respond, hides in Chia 100.

## Checked, no bug (B1)
- Every nav tab and every Quản lý sub-tab ×2, sidebar group buttons: no console error / unhandled rejection; no raw i18n key, `undefined`, `NaN`, `[object` on any tab (empty and loaded).
- 50 random switches Chỉ xếp / Chia 100 / Huy chương (+ "Chia CLB theo loại" toggled) on the shared Sổ imported in Huy chương mode, a UI run after each: all 50 runs ok,
  config in DB matches the card, `run_history` +1 per run, Results table equals `match_results` for all 150 students, `#statMatched` equals backend, no raw keys on Cài đặt / Xếp CLB.
- Double-click on #btnRun (first run → 1 run; with confirm bar → 1 more run), double-click on mode cards, #btnValidate, #btnToggleHistory, #btnTaiSoMau, #viecTiepTheoNut: no duplicate run, no error.
- Reload 400 ms into a 2.5 s run: exactly one `run_history` row, full results, UI usable afterwards. Back / forward / about:blank round trip: app recovers.
- "Hoàn tác" on the mode-change toast returns the exact old rules (4 consecutive switches) and the card shown matches the config.
- Rapid clicks on 2–3 different mode cards (12 sequences): card on screen always equals the saved config; 9 rapid clicks on the chia_loai switch end consistent.
- Protocol question (ST-A-001, UI side): importing the shared Sổ in Chia 100 and then clicking Huy chương DOES show the readiness panel
  ("Để dùng Huy chương, hãy chọn loại cho từng CLB: 0/14") and the import itself shows "…14 CLB có cột loại… đã được bỏ qua…" after the import
  (not before). So the user is not left blind; the panel asks to pick Loại by hand and does not say "re-import the Sổ" — design note, not logged as a bug. Screenshot `ST-B-002_doi_sang_huy_chuong_sau_nhap_chia_100.png` is that panel, not a bug.
- Note: undo toasts stack and stay 10 s; clicking an OLD "Hoàn tác" after a newer switch restores the older state (expected, S4 at most; not logged).

## Needs Truong
- ST-B-003: is "the Sổ replaces every tick and score of the students it lists" intended? If yes, only a warning is needed (S3); if no, it is a data-loss bug (S1).
- Scores have no upper bound (11 or 1000 accepted by the scoring screen and the import); capacity 1e9 accepted. Is a cap wanted (10 / 100)?
- A late arrival after the first run cannot enter medals without a global unlock; confirm this is the intended flow for the field trial.
- Is the import-warning-after-import (not before) in Chia 100 / Chỉ xếp acceptable, given points are discarded irreversibly (ST-A-001)?
