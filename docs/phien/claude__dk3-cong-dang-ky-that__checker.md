PASS | head 60c84fc
1. CI pending: "Tests (rbda-kiosk)" run 1644 for head 60c84fc was status `pending` at review time (earlier runs were cancelled by newer pushes; this checker commit will start a new run). Orchestrator must confirm green before DK4. Check: actions_list, branch claude/dk3-cong-dang-ky-that.
2. Local: test_dk3_schema + test_dk3_api + test_gt3_phan_quyen = 39 passed; test_giao_dien_dk3_cong (Chromium) = 5 passed (after `pip install playwright`; skipped without it). kiem_nhanh --co-so origin/claude/gracious-johnson-pnqvrg = 7/7 (15 cases byte-identical, invariant 1). Default run fails only trung_khit (no origin/main in env). `ruff` is not installed in this env; kiem_nhanh's ruff item was DAT in the earlier run, re-run `ruff check .` in CI/venv.
3. L1/L2/L4 acceptance OK: `dk3` step in di_tru_schema (backup first, CREATE IF NOT EXISTS, idempotent); error codes appended in one hunk (0 removed lines in i18n_errors.py), i18n_loi.js matches; dk_xuat_so_nhap -> dk2_so_nhap.ghi_tu_ban_mau, test imports 0 errors and allocates.
4. Invariants 2-5 OK: compute_club_priority and the pipeline/run_history untouched (rbda_priority_pipeline.py diff = only the dk3 hook); medals stored, PK(student_id, clb_id), Tự do refused.
5. Security OK: PIN/admin pbkdf2-sha256 (SO_VONG_PIN 10_000) + random salt, no PIN in logs; students see only status='duyet' clubs within their grade; >10 choices, >5 tests rejected server-side.
6. Nit api_dang_ky.py `_dk_chay`: `except Exception` returns `detail=str(e)` to UI (may expose SQL text). Check: force an sqlite error.
7. Nit api_dang_ky.py `dk_dang_nhap`: no attempt limit; 4-digit PIN brute-forceable from UI. Not in DK3 spec; candidate for DK4.
8. Nit js/dang_ky_gv_hs.js: limits 5 and 10 hard-coded, UI text literal Vietnamese (not i18n keys). Check: grep "dem >= 5".
9. UI OK: local fonts/style.css tokens, no dark mode, no external URL; one gold button (DK.nutVang) per phase view in dang_ky_quan_tri.js (chuyen), per step in dang_ky_gv_hs.js; no disabled gold button.
10. Packaging OK: dang_ky.html in kiosk.spec and build-windows-exe.yml; DangKyMixin in api.py; dk_* in CONG_KHAI.
