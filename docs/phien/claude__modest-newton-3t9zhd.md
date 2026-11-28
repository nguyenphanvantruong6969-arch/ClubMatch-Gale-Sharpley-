# Branch handoff: claude/modest-newton-3t9zhd

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Hackathon support for Truong (2026-11-28), outside the 33-item registry (Truong asked explicitly):
(a) demo data kit `du_lieu_test/bo_demo_hackathon/` (SIMULATED data); (b) bug fix: registration portal PIN sheet /
template download blocked in the pywebview .exe; (c) bug fix: portal step 5 «Nhập điểm» → «Chốt và xếp» did not reach «Xuất».

## Plan
- [x] Demo kit: two workspace zips + login data (`tao_bo_demo.py`), mode-switch book with reserves + classes
      (`tao_so_doi_che_do_du_tru.py` → `SO_NHAP_DEMO_DOI_CHE_DO.xlsx`), portal Excel clean + 8 deliberate errors (`tao_excel_dang_ky.py`)
- [x] Fix (b): Python writes the file via `_duong_xuat`; PIN reset + file write in ONE transaction (commit 105683c + help text)
- [x] Fix (c): wait for in-flight score saves before chot; inline «missing scores» box; «Chốt điểm» redraws
- [ ] Confirm full DK test run shows ONLY the pre-existing failures (see Open problems), then commit fix (c)
- [ ] Truong verifies both fixes on the real Windows .exe (cannot be done on Linux)

## Current state (overwrite each handoff)
- Done: demo kit + fix (b) committed and pushed. Fix (c) written, its 3 new tests green, `kiem_nhanh` 7/7, CHANGELOG +
  CLAUDE_CHI_TIET test count (465) updated — committed in the handoff commit (see Session log).
- In progress: a full DK regression run (`tests/test_{dk,vg,giao_dien_dk,giao_dien_vg,va_gap,gt3,dkl,giao_dien_dkl}*.py`,
  `-n 8`) was still running at handoff; result not yet read. RE-RUN it first (command in Next steps).
- Tests for this branch: `tests/test_dk_xuat_tep_ghi_dia.py` (7), `tests/test_giao_dien_dk_buoc5.py` (3, Chromium),
  edited `tests/test_giao_dien_vg1.py::test_l2_*`, `tests/test_giao_dien_dk9_l2.py::test_b_*`.
- Open problems (PRE-EXISTING, red also on `105683c~1`, i.e. before today's fixes; not fixed):
  `test_giao_dien_dk5_toan_trinh::test_4` (fixture hits `dk_chua_co_clb_duyet`), `test_giao_dien_dk3_cong::test_11[375|600|1000]`,
  `::test_12[no-preference|reduce]`, `test_giao_dien_dkl_giao_vien::test_3`. First parallel run showed 9 red; these 7 reproduce serially.
- Truong never sent the exact error text for (c); the race was reproduced deterministically and is the most likely cause.

## Decisions and gotchas
- UI downloads via `blob:` + `<a download>` are silently blocked in pywebview (WebView2); Chromium tests allow them, so CI
  cannot catch it. Any file export must be written by Python (`_duong_xuat`, Downloads, no overwrite). No `blob:` left in js/.
- `dk_pin_xuat_excel`: write failure → `_Loi("dk_xuat_tep_hong")` → rollback (old PINs kept); commit failure → file deleted.
  `file_base64` still returned for old callers. New error code `dk_xuat_tep_hong` (ran `tao_i18n_js.py`).
- Race test slows `api.dk_diem_dat` on the PYTHON side: patching `window.pywebview.api` in the page does not take effect
  (browser bridge calls Python per request on its own thread — `ThreadingHTTPServer`).
- Keep exactly ONE gold button on step 5 (`test_giao_dien_dk4_chot_xep` asserts it).
- Local env: no `.venv`; use `python3`; installed `playwright` (pip, pinned range) and `pytest-xdist`;
  UI tests need `RBDA_TEST_CHROMIUM=/opt/pw-browsers/chromium`.
- Demo kit: PINs and lookup codes are random (`secrets`) per regeneration; CSV only matches zips of the same run.
  Mode-switch book must be imported while the workspace is in «Huy chương» mode. Reserves only act in RB-DA modes.

## Next steps (ordered)
1. `RBDA_TEST_CHROMIUM=/opt/pw-browsers/chromium python3 -m pytest -q -n 8 $(ls tests/test_{dk,vg,giao_dien_dk,giao_dien_vg,va_gap,gt3,dkl,giao_dien_dkl}*.py)`
   — expect only the pre-existing failures above. Any NEW red → investigate fix (c) / (b) before anything else.
2. Fix the CHANGELOG line for fix (c) if the failing list differs (it says "9 … and 2 other cases").
3. Run `soat-ma` (CLAUDE.md rule 8) and report.
4. Ask Truong whether to open an item for the 7 pre-existing red UI tests and for the «Làm lại cổng đăng ký» reset button
   (does not exist; options listed in chat: backup first, typed confirmation, keep admin password?, allow after chot?).

## Files touched
- du_lieu_test/bo_demo_hackathon/*: demo kit (scripts, xlsx, zips, CSV, README, KIEM_CHUNG.json); du_lieu_test/README.md link
- api_dang_ky_excel.py: `_dk_ghi_tep_xuat(_dia)`, `dk_excel_mau`, `dk_pin_xuat_excel` write to disk
- js/dang_ky_quan_tri_2.js: no blob downloads; `ghiNhanLuuDiem`, `choLuuDiem`, `khungThieuDiem`; «Chốt điểm» redraw
- js/dang_ky_quan_tri.js: `nutXep` waits for saves; step 5 shows `#dkThieuDiem`
- i18n_errors.py, i18n_loi.js: `dk_xuat_tep_hong`
- tests/test_dk_xuat_tep_ghi_dia.py, tests/test_giao_dien_dk_buoc5.py (new); tests/test_giao_dien_vg1.py, tests/test_giao_dien_dk9_l2.py (edited)
- CHANGELOG.md, docs/ke_hoach/CLAUDE_CHI_TIET.md (test count 465)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus | Demo kit; fix (b) PIN/template export; fix (c) step-5 race + inline missing box | Full DK regression run unread at handoff; Windows check pending |
