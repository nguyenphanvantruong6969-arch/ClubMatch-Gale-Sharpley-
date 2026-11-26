# Branch handoff: claude/dk6-hoan-thien-phat-hanh

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/DK6_GIAO_THUC.md` (size M: coder + checker, no lead).

## Feature / goal
Item **DK6** (registry row to add: "Hoàn thiện cổng đăng ký + gói phát hành"): close the leftovers of the portal
(`dang_ky.html`) after DK3/DK4/DKL/DK5, then ship docs + build. Asked by Truong in chat 2026-11-26 ("get plan and start
cooking"). Base = `claude/loving-babbage-8yqo7d` @ `c4486d3` (NOT yet in main). OUT of scope: portal backup RESTORE
(Truong decision A: manual restore, document it only); DK7 (single source of truth) = separate size-L item, planned later.

## Plan (written by Opus; ticked by Sonnet)
- [x] **L1 (must) auto-refresh + wording** — `js/dang_ky_quan_tri.js`, `js/dang_ky_quan_tri_2.js`
  - Extend `QT2.tuLamMoi` (5 s fingerprint poll, `dk_dau_van_tay`) to: tab "ds" (Danh sách) in phases gv_dang_ky,
    duyet, hs_dang_ky, nhap_diem; tab "viec" in phase `nhap_diem` (teachers enter scores concurrently).
  - Do NOT auto-refresh: tab "cai" (Cài đặt), tab "them", phases `chuan_bi` and `xuat` (only the admin changes them;
    refresh adds risk, no value). Write this as a decision in CHANGELOG.
  - Same guards as DKL-N/P: never redraw while PIN list shown, unsaved typing, focused input, open confirm box.
  - Label: in the run summary (`k === "ngoai"` in `js/dang_ky_quan_tri.js`) "Ngoài nguyện vọng" → "Xếp ngoài nguyện
    vọng" + `title` hint "Học sinh không vào được CLB nào trong danh sách của mình, được xếp vào CLB còn chỗ."
    Check first what "ngoai" really counts in `dang_ky_sang_xep.py`; if the hint is wrong, write the true meaning.
  - Boxes: (a) teacher saves a score in session 2 → admin "Nhập điểm" view shows it ≤ 6 s without click; (b) same for
    Danh sách when a student submits; (c) typing in a focused input is never wiped; (d) Cài đặt never polls
    (assert no `dk_dau_van_tay` call while on that tab for 12 s); (e) new label text + title present.
  - Test: NEW `tests/test_giao_dien_dk6_l1.py` (one shared page fixture; reuse helpers of
    `tests/test_giao_dien_dkl_m_lam_moi.py`, do not edit that file except to import).
- [x] **L2 (must) admin password change + per-grade fold** — `api_dang_ky.py`, `i18n_errors.py`, `js/dang_ky_quan_tri*.js`
  - New `dk_doi_mat_khau(self, token, mat_khau_cu, mat_khau_moi)`: admin only; old must verify; new ≥ 4 chars (reuse
    `dk_mat_khau_ngan`); new salt via `_bam`; journal entry via `_dk_ghi_nk(cur, QUAN_TRI, "doi_mat_khau")`; other
    admin tokens invalidated except the caller's (if tokens are stored; else note it). New error code
    `dk_mat_khau_cu_sai` in `i18n_errors.py` → run `python tao_i18n_js.py`. Contract `{ok,data,errors}`.
  - UI: in tab "Cài đặt", block "Đổi mật khẩu quản trị" (old, new, repeat; repeat mismatch checked client-side).
  - Per-grade fold: Danh sách học sinh grouped by `khoi` with `<details>` per grade (summary "Khối 10 · 268 HS · 240
    đã nộp"); open state kept across auto-refresh redraws (L1 interaction!).
  - Boxes: wrong old pw → `dk_mat_khau_cu_sai`, pw unchanged; short new → `dk_mat_khau_ngan`; success → old pw fails
    at `dk_mo_khoa`, new works; non-admin token refused; nhat_ky row exists; fold groups correct for 3 grades; a
    grade left open stays open after an auto-refresh.
  - Tests: NEW `tests/test_dk6_doi_mat_khau.py` (backend) + `tests/test_giao_dien_dk6_l2.py` (one Chromium file).
  - **MILESTONE 1 after L2.**
- [~] **L3 (optional) DROPPED (see Needs Truong) keep the pre-"Chốt và xếp" backup** — `api.py` (`_MAX_BACKUPS` rotation)
  - Problem: repeated "Sao lưu ngay" can rotate out the backup taken before "Chốt và xếp". Fix: rotation never
    deletes the newest backup whose name marks it as pre-allocation (find the naming in `dang_ky_sang_xep.py` /
    `dk_sao_luu`); limit counts only the others. Touches the backup step of invariant 5: no other change.
  - Box: 12× "Sao lưu ngay" after a "Chốt và xếp" → pre-allocation file still exists, total ≤ `_MAX_BACKUPS` + 1.
  - Test: NEW `tests/test_dk6_giu_sao_luu.py`. If it needs a schema/naming change → skip lot, "Needs Truong".
- [x] **L4 (must) docs + build**
  - `docs/huong_dan/DK6_BAT_DAU_NHANH.md` (≤ 1 page: install, first setup, the 6 phases `CAC_GIAI_DOAN`).
  - `docs/huong_dan/DK6_XU_LY_SU_CO.md`: forgot student/teacher PIN, forgot admin password (state truthfully what
    exists), power loss mid-phase, restore backup BY HAND (decision A: which file, where, steps), WebView2 missing.
  - `kiosk.spec` (or build spec used by *Build Windows executable*) includes every `js/dang_ky_*.js`, `dang_ky.html`
    and assets; add a test that lists `js/*.js` referenced by `dang_ky.html`/`index.html` and asserts each is
    bundled, NEW `tests/test_dk6_goi_phat_hanh.py`. CHANGELOG version note. No tag / release / PR.
  - Registry row DK6 in `docs/ke_hoach/SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json` if DK rows exist there;
    test-file count in `CLAUDE_CHI_TIET.md` (435 + new files); `tests/test_a13_12_tai_lieu.py` green.
  - **MILESTONE 2 after L4**, then CI gate (Linux + Windows + Build Windows executable green).

## Current state (overwrite each handoff)
- Done: L1 b3daa55, L2 6eddc2b (pushed, CI run on that head pending at time of writing), L4 committed locally (not pushed: no push while CI for M1 head is in flight).
- L3 dropped (see Needs Truong). Tests: dk6 l1 7, l2 5, doi_mat_khau 6, goi_phat_hanh 4; kiem_nhanh 7/7; ruff clean.
- Next: wait CI green on 6eddc2b -> MILESTONE 1; push L4; wait CI -> MILESTONE 2; soat-ma tiers; CI gate; Status DONE.
- Note: Playwright `clock.install()` makes `wait_for_function` hang (rAF faked) — use `wait_for_timeout` + assert.
- Note: `dk_diem_dat` is admin-only here (no teacher token); "teacher saves score" simulated with an admin token.
- Note: Danh sách folds persist in `moDs` (js/dang_ky_quan_tri.js); a single grade opens by default.

## Needs Truong
- L3 (keep pre-"Chốt và xếp" backup) dropped: `_backup_db` (api.py, ~10 callers) names every backup `app.db.bak-<ts>`; nothing marks the
  pre-allocation one. Protecting it needs a naming change or a stored marker inside `_backup_db` (invariant 5 backup step). Docs tell users
  to copy that file away right after "Chốt và xếp".
- Portal admin password has NO reset path if forgotten (`QUEN_MAT_KHAU.bat` only clears main-app accounts). Needs a design decision
  (e.g. a `--dat-lai-mat-khau-cong` command-line switch like `--xoa-tai-khoan`). Documented truthfully in DK6_XU_LY_SU_CO.md.
- `dk_diem_dat` is admin-only, so teachers cannot enter scores concurrently (plan L1 assumed they could); auto-refresh still covers it.

## Decisions and gotchas (keep short)
- Base is the integration branch, not main: before each lot `git fetch origin claude/loving-babbage-8yqo7d main` and
  merge whichever moved (`--no-edit`). Once Truong has merged loving-babbage into main, merge only main.
- Every push cancels the running CI (~20 min). Batch; never push docs-only while CI runs.
- Adding a `tests/test_*.py` file → update the "N tep `test_*.py`" figure in `docs/ke_hoach/CLAUDE_CHI_TIET.md`.
- Multi-vocabulary app: any hard-coded "học sinh/giáo viên/CLB" text in the MAIN app shows only for the school
  vocabulary (`I18N.getLabels()`); the portal `dang_ky.html` is school-only, fine there.
- After any merge: `git grep -n '^<<<<<<<\|^>>>>>>>'`.
- Invariant 1: none of L1–L4 may change `match_results`; `kiem_nhanh.py` 7/7 each lot.

## Next steps (ordered)
1. Coder: L1 → L2 → MILESTONE 1 → (L3) → L4 → MILESTONE 2 → CI gate. Truong starts the checker at each milestone.
2. After DK6 PASS: Truong merges loving-babbage, then this branch. Then plan DK7 (needs Truong's design answer).

## Files touched
- docs/phien/claude__dk6-hoan-thien-phat-hanh.md, docs/phien/DK6_GIAO_THUC.md: plan

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-26 | Opus | Plan DK6 (4 lots, size M), protocol, coder prompt | no product code |
| 2026-11-26 | Sonnet | L1 done: tuLamMoi on ds + nhap_diem viec; label+title | test file new |
| 2026-11-26 | Sonnet | L2 done: dk_doi_mat_khau + UI, per-grade fold | 2 new test files + backend file |
| 2026-11-26 | Sonnet | L3 dropped; L4 done: 2 guides + test_dk6_goi_phat_hanh + registry row | new test file, docs |
