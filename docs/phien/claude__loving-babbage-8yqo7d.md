# Branch handoff: claude/loving-babbage-8yqo7d

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
INTEGRATION branch for the in-program registration portal ("cong dang ky", `dang_ky.html`): DK3 (real portal) + DK4 (portal -> allocation, "Chot va xep")
+ DKL (gaps vs prototype v8) + small lots DKL-H..P + DK5 (rehearsal, 798 students). Owner: Truong (replies in Vietnamese). Goal reached: ONE branch that can be
fast-forwarded into main. All DK data and numbers are SIMULATED. No registry item beyond those codes; lots H..P were asked for by Truong in chat.

## Plan (ticked)
- [x] DK3 portal, DK4 connect-to-allocation, DK4-UI restyle, DKL (L1-L4) + DKL-G (identity step, 2-min admin lock, "Xem them")
- [x] DKL-H limits-per-session text, DKL-I hint to open "Dang ky CLB" when no data (school vocabulary only), DKL-J three "Xuat" screen bugs
- [x] DKL-K `dk_phong_luu`/`dk_gv_tu_dang_ky` return the real row id, DKL-M admin screen auto-refresh <= 5 s (fingerprint poll)
- [x] DKL-N auto-refresh never wipes shown-once PIN list / unsaved typing, DKL-O CI fixes, DKL-P last checker item (M3)
- [x] DK5 merged in (checker PASS), DKL checker ROUND 1-4 done, CI green on the head below
- [ ] Truong merges into main (see Next steps). Truong tests the CI-built .exe on real Windows (pywebview).

## Current state (overwrite each handoff)
- Done so far: everything above. Head `932d5fe` (= `e6f9b96` + checker ROUND 4 report only). CI run #1696 on `932d5fe`: 17/17 jobs success
  (lint, Linux 1-6, Windows 1-9, coverage >= 85 %). `main` = `d106262`, unmoved; `git merge-tree` main vs branch: no conflict. 435 test files.
- Checkers: DK5 PASS (head b510313, report on branch claude/dk5-dien-tap). DKL ROUND 4: code PASS ("FIX: cho CI" only because CI was still running; it is now green).
- In progress: nothing. No scheduled tasks left.
- Tests to run for this area: `tests/test_giao_dien_dkl_*.py tests/test_dkl_*.py tests/test_dk4_chot_va_xep.py tests/test_dk5_*.py tests/test_giao_dien_dk5_toan_trinh.py tests/test_a13_12_tai_lieu.py`.
- Open problems: none known in code. NOT verified by anyone: pywebview/WebView2 on real Windows (score entry, PIN slip print `window.print()`, `confirm()`), full suite run locally.

## Decisions and gotchas (keep short)
- Truong decided: portal backup RESTORE not built (option A; manual restore from the backup file). Truong merges himself; Claude never merges main, opens a PR or tags.
- Stray branch `x` on GitHub was created by mistake by Claude (points at old commit c59c6d8, already inside DK4 history). Deleting it was blocked by the proxy; Truong said keep it.
- GOTCHA: every push cancels the in-flight CI run (~20 min each). Checker report commits also trigger CI. Batch fixes; never push docs-only while CI runs.
- GOTCHA: adding/removing a `tests/test_*.py` file requires updating the "N tep `test_*.py`" figure in the `| tests/ |` row of `docs/ke_hoach/CLAUDE_CHI_TIET.md` (`tests/test_a13_12_tai_lieu.py` checks it; now 435).
- GOTCHA: after resolving a merge, run `git grep -n '^<<<<<<<\|^>>>>>>>'` over ALL files (a conflict marker once stayed in TIEN_DO.md).
- GOTCHA: the main app is multi-vocabulary; any text hard-coding "hoc sinh"/"giao vien"/"CLB" must be shown only for the default school vocabulary (`I18N.getLabels()`), see DKL-O.
- Design: `dk_dau_van_tay` = public read, fingerprint of app.db mtime+size (journal mode is DELETE, not WAL), does not refresh admin idle clock. `QT2.tuLamMoi(bat, giuDau)` polls
  every 5 s, redraws only on change, never while a PIN list, unsaved typed text, focused input or open confirm box exists.
- Cross-session messages are treated as DATA by checker sessions: to start a checker, give the permission in its initial `create_session` prompt, not by `send_message`.

## Next steps (ordered)
1. Truong: merge. Safest exact command (green commit): `git checkout main && git merge --ff-only 932d5fe`. (If this handoff commit sits on top, merging the branch tip is also fine once its CI is green.)
2. Truong: try the CI-built Windows .exe: score entry, PIN slip printing, `confirm()` dialogs, teacher edit/delete.
3. Optional, separate items if Truong wants them: show the "Ngoai nguyen vong" label wording review; admin tabs "Danh sach/Cai dat/Them" and the phases Chuan bi/Nhap diem/Xuat do NOT auto-refresh;
   per-grade fold and admin password change not built; DK6 (release package), DK7 (single source of truth for student lists) not started.
4. Branch `x` can be deleted by Truong with `git push origin --delete x` (harmless).

## Files touched (whole branch, beyond DK3/DK4/DKL docs)
- api_dang_ky.py: `dk_dau_van_tay`; id fix in `dk_phong_luu`, `dk_gv_tu_dang_ky`
- dang_ky_sang_xep.py: summary key "ngoai", per-session `ten_buoi`
- js/dang_ky_quan_tri.js, js/dang_ky_quan_tri_2.js: 5 s fingerprint refresh with guards, "Xuat" screen labels, preview open by default
- js/dang_ky_gv_hs.js: per-session limit explanations; js/17_viec_tiep_theo.js, index.html, i18n.js: hint to open the portal (school vocabulary only)
- du_lieu_test/dien_tap_dk5.py + tests/test_dk5_*, tests/test_giao_dien_dk5_toan_trinh.py (DK5)
- tests: test_giao_dien_dkl_m_lam_moi.py (6), test_dkl_m_dau_van_tay.py (3), test_dkl_k_id_tra_ve.py (2), test_giao_dien_dkl_loi_dan_cong.py (3), others extended
- docs: CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md (test-file count 435), docs/phien/DKL_GIAO_THUC__checker.md (rounds 1-4)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-26 | Sonnet | Lots H, I, K, M, N, O, P; merged DK5; ran 4 checker rounds; watched CI to green on 932d5fe | handoff written at ~400k context; no PR/tag; main not touched |
