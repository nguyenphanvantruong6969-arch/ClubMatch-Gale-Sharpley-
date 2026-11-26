# DK5 checker — MILESTONE 1+2 (base 88ff2ba, head b510313)

PASS
- CI run 45723562339 (#1687) on head b510313: success — lint, Linux 6/6, Windows 9/9, coverage ≥ 85 %. (Build-exe workflow has no run on this branch; not triggered by push.)
- (a) b510313 touches only `du_lieu_test/dien_tap_dk5.py` (+CHANGELOG, branch file): admin re-login at start of `duyet`, `hoc_sinh_nop`, `nhap_diem`. `GIAY_NGHI_QUAN_TRI = 120` and `api_dang_ky.py` unchanged; no assertion/test edited (test l2b still asserts the 120 s lock with an injected clock).
- (b) diff vs DK4: only NEW files (generator, 3 test files, 2 docs) + doc/CHANGELOG edits; no product file.
- (c) data labelled MÔ PHỎNG; no `hash()`; rollback test injects `luat_xep_de_ghi` inside the write transaction (after match_results + STB lock, before run_history); restore compares every row; idle/deadline use injected clocks.
- Re-run locally: DK5 12 passed; DK3+DK4 backend 100 passed; UI DK3/DK4/DK5 17 passed. Edge: 0 teachers (tu_dang_ky_gv=0.0) runs OK.
- Note: dk_phong_luu `lastrowid` bug stays in "Needs Truong" (separate item).
