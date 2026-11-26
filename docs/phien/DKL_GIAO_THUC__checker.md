# DKL checker report — ROUND 3 (Sonnet) — head 80ef1be (integration: DK3+DK4+DKL+H..O+DK5), branch claude/loving-babbage-8yqo7d, 2026-11-26

**VERDICT: FIX (một mục THẤP, M3; mọi thứ khác PASS).** Không có rủi ro mất dữ liệu; M3 chỉ là cửa sổ lệch ~100–300 ms làm màn cũ thêm một vòng. Nếu Truong chấp nhận rủi ro thấp này thì có thể gộp; nếu muốn đóng hẳn mục vòng 2 thì sửa như dưới.

Head checked: 80ef1be (= origin/claude/loving-babbage-8yqo7d, no move). Env: Python 3.11 venv, Chromium, tests run for real.

## CI (verified, not trusted) — PASS
Run 45729479268 on head 80ef1be: all 17 jobs `success`: Lint (ruff), Linux 1/6…6/6 (full + real UI), Windows 1/9…9/9, coverage ≥ 85 %. (Linux 1/6 ran the «no UI test skipped» step; others skipped it by design.)

## 1. Round-2 items closed by DKL-N (ea30610)
- **M1 PIN list not wiped — PASS.** `test_4` PASS; own check: create PIN, switch tab «Danh sách» and back, data change + 12 s → screen redraws (not stuck forever; PIN box gone only because the tab was re-entered).
- **M2 typed text survives blur — PASS.** `test_5` PASS; own checks: type «abc» then delete back to «» → redraw resumes (PASS); a `<select>` changed but not saved in the duyệt phase, blurred, data change + 12 s → `.dk-noidung` NOT replaced (PASS). «Thay cả danh sách» box: guard `#dkThayHop` read in `coThuSeMat()`, not run in browser.
- **M3 re-arm uses fingerprint already seen — FIX (Low).** The code in `QT2.tuLamMoi` is right but dead: `DK.quanTri` (js/dang_ky_quan_tri.js, first lines) calls `DK.QT2.tuLamMoi(false)` on EVERY redraw, including the automatic one; that sets `dauCho = null` before the final `tuLamMoi(true)`, so re-arm always takes the `else layDau()` branch. Measured with a spy on `RBDA.callApi`: one data change + auto-redraw → `dk_dau_van_tay` called **2** times (poll + re-arm read), expected 1. No test covers it (test_4/5 do not count calls).
  **Change:** js/dang_ky_quan_tri.js line `if (DK.QT2) DK.QT2.tuLamMoi(false);` → `if (DK.QT2 && !tuDong) DK.QT2.tuLamMoi(false);` (the auto-redraw path then keeps `dauCho`; a failed/aborted auto-redraw is harmless: next interval sets `dauCho` again). Add test: spy counts `dk_dau_van_tay` == 1 after one change + 6 s (my scratch `test_m3_khong_doc_lai_dau` fails 2≠1 today, passes after fix).
- **Docs:** `git grep '^<<<<<<<\|^>>>>>>>'` → none in any tracked file; TIEN_DO table has no blank line inside it (rows DKL-H…O, DK5-L1…L3 contiguous); CHANGELOG DKL-M says «chế độ nhật ký là DELETE nên không có tệp WAL» — PASS.

## 2. DKL-O (0ddc2b3) — PASS
`test_giao_dien_dkl_loi_dan_cong.py` (3) + `test_ws_nhan_giao_dien.py::test_cong_ty_thay_tu_cua_minh_tren_man_hinh` PASS (hint visible only with default school vocabulary, hidden for company vocabulary). CLAUDE_CHI_TIET says 435; `ls tests/test_*.py | wc -l` = 435.

## 3. DK5 merge (80ef1be) — PASS
`git diff 0ddc2b3..80ef1be --stat`: only du_lieu_test/dien_tap_dk5.py, tests/test_dk5_dien_tap.py, tests/test_dk5_vung_chiu_loi.py, tests/test_giao_dien_dk5_toan_trinh.py + CHANGELOG, TIEN_DO, SO_DANG_KY_33_MUC, CLAUDE_CHI_TIET, docs/phien/*. No api*.py, js, i18n*, index.html, pipeline, so_nhap file changed.
Run: `tests/test_dk5_*.py tests/test_giao_dien_dk5_toan_trinh.py tests/test_giao_dien_dkl_*.py tests/test_dkl_*.py tests/test_a13_12_tai_lieu.py` + the ws test → **62 passed in 73.64s**.

## 4. Standing checks — PASS
`ruff check .` clean. `kiem_nhanh.py` **7/7** (trung_khit runnable this time: 15 cases byte-identical). Invariants 1–8: `git diff --stat 42b93af..HEAD` on rbda_priority_pipeline.py, dang_ky_schema.py, so_nhap.py, dk2_so_nhap.py, fa_daa.py, api.py → empty (no algorithm/schema/CSV change). `git merge-tree --write-tree --name-only origin/main HEAD` → clean tree (37cda1b), no conflict; origin/main still d106262.

**Kết luận:** merge-ready về an toàn dữ liệu và CI; còn đúng một sửa nhỏ M3 (1 dòng + 1 test) để đóng mục vòng 2.

---

# DKL checker report — ROUND 2 (Sonnet) — head f2db78f, branch claude/loving-babbage-8yqo7d, 2026-11-26

**VERDICT: FIX.** Three reasons, in order of weight:
1. **DKL-M defect (High):** the 5-second auto-refresh wipes the just-created teacher PIN list (shown once) and any typed-but-unsaved text. Reproduced (below).
2. **`docs/ke_hoach/TIEN_DO.md` has unresolved merge-conflict markers committed** (`<<<<<<< HEAD` line 321, `=======` 324, `>>>>>>> e1fb45c` 328).
3. **CI not finished:** run **45722740833** (head f2db78f) was `in_progress` when checked → "FIX: chờ CI". Note: my own push of this report cancels that run (workflow `cancel-in-progress`); the coder's fix push would cancel it anyway, so one clean full run is needed on the fix head, Linux AND Windows.

Environment: Python 3.11 venv in scratchpad, Chromium. DKL test files (7 files, 25 tests) + `test_dkl_k_id_tra_ve.py`, `test_dkl_m_dau_van_tay.py`, `test_dk4_chot_va_xep.py`, `test_dkl_cai_dat.py` all PASS. `ruff check .` clean. `kiem_nhanh.py` 6/7 (only `trung_khit` fails: no `origin/main` in this clone — environment, CI must cover; same as round 1).

## 1. Round-1 FIX items
| Item | Result | Evidence |
|---|---|---|
| (a1) «NVNone» → «Ngoài nguyện vọng» | PASS | `test_dk4_chot_va_xep.py::test_tom_tat_xep_hang_null_la_ngoai_nguyen_vong_va_co_ten_buoi` (`{"1":2,"ngoai":1}`) + UI assertion in `test_giao_dien_dk4_chot_xep.py` |
| (a2) «thu_2» → portal name «T2» | PASS | same tests (`ten_buoi == "T2"`, `match_results` still `thu_2`; display layer only) |
| (a3) «Xem trước Sổ nhập» open by default | PASS | `test_giao_dien_dkl_quan_tri.py` test_6 waits for table visible with no click (`details open: true`) |
| (b) TIEN_DO rows DKL-H, DKL-I | **FAIL (partial)** | rows present, no duplicates (DKL-H, I, J, K, M once each) BUT file contains conflict markers (see reason 2); also rows H/I/J have no test column |
| (c) dot decimal "8.5" in UI test | PASS | `quan_tri test_4` fills "8.5" → chip «Đạt» (asserts chip, not stored value; acceptable) |
| extra: unticked Tuyển chọn → no Forms link | PASS | `hoc_sinh test_2b_khong_tick_bai_thi_thi_khong_co_link_lam_bai` |

## 2. DKL-K (id trả về) — PASS
- `tests/test_dkl_k_id_tra_ve.py` FAILS on the old order (I swapped in `api_dang_ky.py` from 348f6d4: 2 failed, `[5, 6, 7] == [1, 2, 3]`, i.e. journal row ids) and PASSES on f2db78f.
- `grep lastrowid`: only 3 left in `api_dang_ky.py` — `dk_phong_luu` (373) and `dk_gv_tu_dang_ky` (420) read it BEFORE `_dk_ghi_nk`; `dk_clb_luu` (617) reads it before `_dk_ghi_nk` as well. None returns lastrowid after the journal INSERT. None in `dang_ky_sang_xep.py`, `dk2_so_nhap.py`, `dang_ky_schema.py`.

## 3. DKL-M (`dk_dau_van_tay` + 5 s refresh) — FIX (one High, one Medium)
Confirmed by reading + scratch Chromium tests (fake clock, scripts outside repo in scratchpad `test_scratch_dklm.py`, `test_scratch_pin.py`):

| # | Risk | Rating | How tested | Result |
|---|---|---|---|---|
| M1 | Redraw wipes **PIN list shown once** | **HIGH** | gv_dang_ky phase: create 2 teachers (PIN box shows "Cô Cúc 3139…"), then ANY other data change (e.g. a teacher self-registers), advance 6 s | PIN box becomes empty. Admin loses the PINs (recoverable only by «Đặt lại PIN» per teacher). Cause: `viecBayGio` renders `#dkPin` inside the redrawn tab; guard only checks a focused INPUT/TEXTAREA/SELECT and `#dkThayHop`, but focus is on a button/body after clicking «Tạo». The old 30 s loop ran only in hs_dang_ky, which has no PIN box; DKL-M widened it to gv_dang_ky and duyet |
| M2 | Redraw wipes typed-but-unsaved input | **MEDIUM** | gv_dang_ky: type "Cô Mới" in textarea, click elsewhere (blur), other change, +6 s | textarea reset to "". Same for the «Hạn chót» datetime field and the duyệt/«Sửa sau mở» quota/room fields when not focused |
| M3 | Fingerprint race on re-arm | LOW | by reading `QT2.tuLamMoi`: every redraw ends with `tuLamMoi(true)`, which re-reads `dauCu = layDau()` AFTER the redraw; a change that lands between the interval's fingerprint read and that re-read is recorded as "seen" though the redraw may predate it → screen stale until the NEXT change. Window ≈ one redraw (100–300 ms) | not reproduced (timing); fix = do not overwrite `dauCu` on re-arm if already set |
| M4 | Fingerprint validity / WAL | LOW | measured: `PRAGMA journal_mode` = **delete** (`rbda_priority_pipeline.py:2240` keeps DELETE by design), so the `-wal` part is always "-"; fingerprint = `st_mtime_ns:st_size` of `app.db`. 4 read cycles of every admin read API + a login left it unchanged (no redraw loop); a write changes it. Windows: `os.stat` works on NTFS; mtime_ns is 100 ns granularity. Cannot test Windows here; CI Windows runs `test_giao_dien_dkl_m_lam_moi.py`. CHANGELOG says "tệp WAL" — inaccurate wording, harmless | tested (Linux) |
| M5 | 2-minute idle lock still works | OK | `test_8` PASS; extra: with polling ON and data changing every 5 s, lock message appears after 23 steps (≈ 115–120 s fake) — client timer is not reset by `DK.quanTri(true)`. Note: redraw calls authenticated APIs, so the SERVER-side idle clock is refreshed on each change-driven redraw; harmless because the client calls `dk_dang_xuat` at 120 s, but the "server also locks" safety net is weakened while data keeps changing | tested |
| M6 | Interval left running after logout / tab change | OK | counted `RBDA.callApi('dk_dau_van_tay')`: after lock 0 → 0 over 60 s fake; after «Đăng xuất» 0 → 0; on tab «Danh sách» 0 → 0 over 30 s with data changed; back to «Việc bây giờ» polling resumes. `tuLamMoi` always `clearInterval` before arming → no stacking | tested |
| M7 | Student screen untouched | OK | `git diff 348f6d4..f2db78f` has no change in `js/dang_ky_gv_hs.js`, `dang_ky_nen.js`, `style.css`, `i18n.js` | read |
| M8 | Public + no session refresh + no DB open | OK | `test_dkl_m_dau_van_tay.py` (3 PASS): no token, stable on reads, changes on writes incl. student submit, session `luc` unchanged after 3 calls. Leaks no personal data (opaque mtime:size string) | tested |
| M9 | Timer/memory leak | LOW-OK | one interval at a time; callbacks hold no growing state; in-flight callback after logout re-checks `DK.quanTri` guard (`DK.S.vai`) before painting | read |

**What to fix (coder, one lot `DKL-N`, test first):**
1. M1+M2: skip the auto-redraw (keep the old fingerprint so it retries) when `#dkPin` has content, or when any `.dk-noidung` field differs from its initial value (e.g. `textarea.value !== ""`, `input.value !== defaultValue`); OR do not poll in `gv_dang_ky` (PIN screen) at all. Failing tests to add: (a) PIN box still has «Cô Cúc 3139…» after another change + 6 s; (b) typed textarea text survives blur + another change + 6 s; (c) after the PIN box is cleared (leave tab) polling resumes.
2. M3: `if (dauCu === null) dauCu = await layDau()` on re-arm.
3. Remove the conflict markers from TIEN_DO (keep all five rows: M, K, H, I, J), add the test column to H/I/J.
4. CHANGELOG: say "mtime + kích thước tệp CSDL (chế độ nhật ký DELETE, không phải WAL)".
5. Push once; wait for full CI green on Linux AND Windows on that head.

## 4. DKL-H, DKL-I, G1–G4 — PASS (re-run)
`test_giao_dien_dkl_hoc_sinh.py` (H `test_3d_…`, G1 `test_3b`, G4 `test_3c`), `test_giao_dien_dkl_loi_dan_cong.py` (I, 2 cases), `test_giao_dien_dkl_quan_tri.py::test_8` (G2/G3) — all in the 25 passed.

## 5. Standing checks
- Invariants 1–8: `rbda_priority_pipeline.py`, `dang_ky_schema.py`, `so_nhap.py`, `dk2_so_nhap.py`, `fa_daa.py`, `api.py`, `i18n_errors.py`, `i18n_loi.js`, `mau_csv` unchanged since 42b93af → no algorithm/schema/CSV change; `compute_club_priority` untouched (inv. 2 intact). `trung_khit` byte-identical check not runnable here (no `origin/main`) → CI.
- i18n: `i18n_errors.py` unchanged; `kiem_nhanh` i18n checks PASS. `dk_dau_van_tay` is a read → no `nkhd_` label needed; `nkhd_` list unchanged and complete for earlier write functions.
- CHANGELOG rows DKL-J, DKL-M, DKL-K: present. TIEN_DO: rows present but file corrupted by conflict markers (FIX 3).
- soat-ma tiers 2–4: not run by me beyond the checks above (report-only run).
- Not verifiable here: pywebview/WebView2, Windows `os.stat` timing, full suite.


---

# DKL checker report (Sonnet) — head 348f6d4, branch claude/loving-babbage-8yqo7d, 2026-11-26

**VERDICT: FIX (not PASS).** Reasons: (a) CI of head 348f6d4 = run 45719263842 still `queued`, so no Linux+Windows result; (b) 3 confirmed defects on the
admin "Xuất" screen; (c) TIEN_DO has no DKL-H / DKL-I rows. Everything below was run locally (Python 3.11, Chromium): the 5 DKL test files = **25 passed**;
`ruff check .` clean; `kiem_nhanh.py` 6/7 (`trung_khit` cannot run here: no `origin/main` in this clone, environment not code — CI must cover it).
No source change outside the DKL files: `rbda_priority_pipeline.py`, `dang_ky_schema.py`, `so_nhap.py`, `dk2_so_nhap.py`, `fa_daa.py`, `api.py` untouched since 42b93af
→ no schema / CSV / algorithm change; `compute_club_priority` unchanged (invariant 2 intact; the DKL code never reads rank for priority).

## Row by row (test = file `tests/test_giao_dien_dkl_*.py` unless noted; all PASS locally)
| Row | Result | Test |
|---|---|---|
| S1 Forms link after submit | PASS (link only for ticked Tuyển chọn; the test has one club so "unticked → no link" is not asserted: weak) | hoc_sinh `test_2_gui_roi_bien_nhan_co_link_bai_thi…` |
| S2 "Dưới sàn" chip + rule line | PASS | hoc_sinh `test_2` ("thì không xét", "Không làm bài, hoặc dưới mốc điểm") |
| S3 card info, no demand (D26) | PASS | hoc_sinh `test_1_the_clb_co_mo_ta…khong_lo_so_dong` |
| S4 deadline + expired message | PASS | hoc_sinh `test_3`, `test_4_het_han…` |
| S5 empty submit warning | PASS | hoc_sinh `test_3_nop_rong…` |
| S6 "Đã gửi lúc" + "Xong, thoát" | PASS | hoc_sinh `test_2` |
| S7 separate steps | PASS (DK4-UI; exercised by `test_2` steps, no dedicated test) | — |
| S8 teacher edit/delete own pending club | PASS | giao_vien `test_2`, `test_3` |
| S9 per-step errors, https, rooms free per buổi | PASS | giao_vien `test_1`, `test_2`; `test_dkl_cai_dat.py::test_clb_xoa_va_phong_trong_theo_buoi` |
| A1 Đóng ngay / Gia hạn / deadline | PASS | quan_tri `test_2` |
| A2 score entry (comma+dot, Dưới sàn, paste, Chốt điểm) | PASS: "8,5" → Đạt, "4" → Dưới sàn, paste "9,5" saved = 9.5. **Dot not asserted in UI test** (FIX-minor: add "8.5") | quan_tri `test_4`; `test_dkl_cai_dat.py::test_bang_diem_xem_truoc_…` |
| A3 PIN slips | PASS: only from the just-created/reset list (`hienPin`); DOM has no `pin_bam`/`pin_muoi` (real column names, verified in `api_dang_ky.py`); `dk_hs_danh_sach` returns no hash | quan_tri `test_1` |
| A4 replace whole list + lock | PASS | quan_tri `test_1` |
| A5 delete room | PASS | quan_tri `test_1` |
| A6 approve with quota/room, edit after open | PASS | quan_tri `test_2`, `test_7` |
| A7 demand per club (admin only) + not-registered | PASS; students never see demand (S3 test) | quan_tri `test_3` |
| A8 phase-1 checklist with reasons | PASS | quan_tri `test_1` |
| A9 Cài đặt tab | PASS | quan_tri `test_5`; `test_cai_dat_doi_*` |
| A10 export preview + version counter | PASS for data; **FIX defect 3** (collapsed) | quan_tri `test_6`; `test_bang_diem_xem_truoc_va_phien_ban_xuat` |
| A11 backup now | PASS (restore not built = Truong decision A, 2026-11-26) | `test_sao_luu_tao_tep_va_ghi_gio` |
| A12 2-min lock text + timeout message | PASS | quan_tri `test_8` |
| G1 identity "Đúng là em chứ?" | PASS | hoc_sinh `test_3b` |
| G2 admin lock 120 s = server 120 s | PASS | quan_tri `test_8` |
| G3 timeout message test | PASS | quan_tri `test_8` |
| G4 ≤7 cards + "Xem thêm (N)" | PASS | hoc_sinh `test_3c` |
| H limit text per buổi | PASS vs Truong's request. Note: v8 has no such sentence, so it is a new text, not a v8 copy | hoc_sinh `test_3d_gioi_han_nguyen_vong…` |
| I hint to open Đăng ký CLB when no data | PASS (shows only in `nap_so`; click → "Thiết lập lần đầu"; hidden when data exists) | `test_giao_dien_dkl_loi_dan_cong.py` (2 cases) |

## Cross-checks
- i18n: `i18n_errors.py` not changed in 42b93af..HEAD; `kiem_nhanh` `i18n_loi_khop`, `i18n_khoa` PASS.
- `nkhd_` labels: all 7 new `dk_*` functions (`dk_phong_danh_sach`, `dk_clb_xoa`, `dk_diem_danh_sach`, `dk_cai_dat_doc`, `dk_cai_dat_doi`, `dk_xuat_xem_truoc`, `dk_sao_luu`) have vi + en labels in `i18n.js`.
- CHANGELOG: rows for DKL, DKL-G, DKL-H, DKL-I present. **TIEN_DO: rows for DKL and DKL-G only; DKL-H and DKL-I MISSING → FIX.**
- soat-ma: coder ran tier 1 only (`kiem_nhanh`); tiers 2–4 were not run by the coder. Not run by me beyond the checks above.
- Not verified (cannot here): pywebview/WebView2, `window.print()`, `confirm()`; full suite; `trung_khit` vs main.

## Three known defects — all CONFIRMED
Repro: script `/tmp/claude-0/-home-user-ClubMatch-Gale-Sharpley-/53f1bac6-aa5e-5a5d-aad1-6f86fd6d1447/scratchpad/test_repro.py`
(copy into `tests/`, uses `test_dk4_chot_va_xep._dang_ky_va_cham`; 3 SIMULATED students H1 H2 H3, H3 sends no preference), run `dk_chot_va_xep(qt, 7)`.

**1. "NVNone: N"** — CONFIRMED. Output: `theo_nguyen_vong: {"None": 1, "1": 2}`; `match_results` row `('H3','thu_2','CLB001','general', rank NULL)`.
- WHY: H3 submitted no preferences (`preferences` has no row for H3), so the allocator placed H3 in the Tự do club by fallback (mode `fa_daa` is auto-enabled by `dk_chot_va_xep`). A fallback placement has `rank_in_student_pref = NULL` by design — NOT an algorithm bug. `api_bao_cao.py` (SG-3 block) already treats exactly this case as "xếp bằng phương án dự phòng, đếm riêng, không tính là nguyện vọng nào".
- CAUSE: `_dk_tom_tat_xep` (`dang_ky_sang_xep.py`) does `hang[str(h)]` → "None"; `bangKetQua` (`js/dang_ky_quan_tri.js`) prints `"NV"+key`.
- FIX: in `_dk_tom_tat_xep` key NULL as `"ngoai"` (or add field `ngoai_nguyen_vong`); in `bangKetQua` print `"Ngoài nguyện vọng: N"` for that key, sorted last. Label must read «Ngoài nguyện vọng» (placed outside the list), nothing more.
- Failing test: `tests/test_giao_dien_dk4_chot_xep.py::test_tom_tat_khong_in_NVNone` (HS with no preference placed → summary text has no "NVNone", has "Ngoài nguyện vọng: 1"; backend variant in `test_dk4_chot_va_xep.py::test_tom_tat_xep_hang_null_la_ngoai_nguyen_vong`).

**2. Buổi shows `thu_2`, `thu_3`** — CONFIRMED. `match_results.buoi = 'thu_2'` because the import runs `so_nhap.ma_buoi("T2") → "thu_2"`; the portal names are the strings stored in `dk_cai_dat['buoi']` ("T2","T3"). The portal does not load `js/05_quan_ly.js` (`nhanBuoi`), so no display mapping exists there.
- FIX (display layer only): in `_dk_tom_tat_xep` add `ten_buoi` per row: map `so_nhap.ma_buoi(b) → b` over `self._dk_buoi_khoi(cur)[0]`, fall back to the raw code; `bangKetQua` prints `x.ten_buoi || x.buoi`. Do NOT touch `match_results`.
- Failing test: `tests/test_giao_dien_dk4_chot_xep.py::test_tom_tat_hien_ten_buoi_cua_cong_khong_hien_thu_2` (settings buổi ["T2","T3"] → column shows "T2", never "thu_2"); backend `test_dk4_chot_va_xep.py::test_tom_tat_xep_co_ten_buoi`.

**3. "Xem trước Sổ nhập (N CLB, M học sinh)" with no table** — CONFIRMED, NOT timing. `DK.QT2.xemTruoc` (`js/dang_ky_quan_tri_2.js`) builds `h("details#dkXemTruoc", {}, h("summary"…), tables…)` without `open`, so the `<details>` is collapsed: only the `<summary>` is visible until clicked. Backend `dk_xuat_xem_truoc` returns full data (3 CLB, 3 students in the repro). The existing test `test_6` hides this by clicking `#dkXemTruoc summary` first (line ~216).
- FIX: `h("details#dkXemTruoc", { open: true }, …)` (same as the "Phòng" block in `danhSach`), or keep collapsed but show a one-line hint "Bấm để xem". Recommend open.
- Failing test: `tests/test_giao_dien_dkl_quan_tri.py::test_6b_xem_truoc_so_nhap_hien_san_bang_khong_can_bam` (after «Chốt và xếp» the "1. CLB" table is visible without clicking; wait for the selector so timing is excluded).

## FIX list for the coder (round 1 of 2 for this milestone)
1. Defects 1, 2, 3 above (3 failing tests named; commit as one lot `DKL-J`).
2. TIEN_DO rows for DKL-H and DKL-I (+ DKL-J).
3. Add dot decimal ("8.5") to `quan_tri test_4`; add "unticked Tuyển chọn → no Forms link" to `hoc_sinh test_2` (one extra Tuyển chọn club left unticked).
4. Run soat-ma tiers 2–4 on the diff; push, wait for CI green on Linux AND Windows (run for the new head); only then READY.
5. Head 348f6d4 CI (run 45719263842) must not be judged yet: it will be cancelled by the next push anyway.
