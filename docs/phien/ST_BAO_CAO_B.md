# ST-B bug report (real-UI stress test, Chromium) — branch claude/happy-cerf-xvn495-st-b

All data SIMULATED. Production code untouched. Run: `.venv/bin/python -m pytest -q --tb=short tests_stress/b/<file> -p no:cacheprovider`.
Screenshots (deviceScaleFactor 1): `docs/phien/anh_st_b/`. Backend report: branch `claude/happy-cerf-xvn495-st-a`, `ST_BAO_CAO_A.md`.

## Summary (severity counts) — updated at end of each lot
| S1 | S2 | S3 | S4 | total |
|---|---|---|---|---|
| 0 | 0 | 2 | 0 | 2 |

## Lot status
| Lot | State | Tests |
|---|---|---|
| B1 | done | test_b1_dieu_huong_cai_dat.py (11 tests; 3 xfail strict = ST-B-001, ST-B-002 x2) |
| B2 | – | |
| B3 | – | |
| B4 | – | |

## Bugs
| id | sev | area | title | repro | invariant |
|---|---|---|---|---|---|
| ST-B-001 | S3 | Kết quả tab | Results table keeps showing the PREVIOUS run's assignments (no loading frame, no stale banner) until the reload finishes | tests_stress/b/test_b1_dieu_huong_cai_dat.py::test_b1_bang_ket_qua_cu_hien_khi_tai_cham | — |
| ST-B-002 | S3 | Cài đặt / Quản lý | After clicking a mode card, the "Chia CLB theo loại" switch just below keeps its OLD enabled/checked state and note until the tab is re-entered | tests_stress/b/test_b1_dieu_huong_cai_dat.py::test_b1_cong_tac_chia_loai_cu_sau_khi_doi_che_do | — |

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
- Is the import-warning-after-import (not before) in Chia 100 / Chỉ xếp acceptable, given points are discarded irreversibly (ST-A-001)?
