# MT2 coder handoff (English, <=30 lines; the branch file stays lead-owned per MT2_GIAO_THUC.md)

Branch `claude/mt2-chia-clb-theo-loai`. Coder session `session_01YVAytzKYmkQsmVJ6CvbkXT`; lead `session_01YVAyu3BTRoD9jYgVDEJ86g`.

## Current state
- Done and pushed, each reported to the lead as "CODER DONE ...": L1 (config key `chia_loai`, `dung_chia_loai`, `get_chia_loai`),
  L2 (pipeline via `fa_daa.chay_fa_daa(diem_wharton=...)`, `kiem_loai_tu_csdl`, trial/estimate refuse `mt_thu_chua_ho_tro_loai`),
  L3 (+FIX F5: switch `#mt2CongTac` in Quan ly > Cau lac bo, `get_san_sang_loai`, health-report type checks),
  L4 (docs: HUONG_DAN muc 17, SO_DANG_KY MT2), R1 (+R1-FIX: import/export of Loai columns follow `dung_chia_loai`),
  CI-1 (UX3 footer button min-height 44px; head `cf290ec`).
- Working tree clean after the last push. Nothing in flight.

## Next steps (only if the lead asks)
- Wait for CI rerun of PR #28 (coverage job was skipped last run because Linux 1/6 failed).
- Optional leftovers: F6 (assert error toast text on ok=false), Settings-cards "types on/off" sentence (needs state-dependent text), pipeline-level rank-permutation test (invariant 2).

## Decisions / gotchas
- R1 deviation: all four club FA columns (Loai, Diem san, Toi thieu, Suc chua phong) follow `dung_chia_loai`; medal-only logic stays on `fa_daa`.
- chia_100 + GIOI_HAN mixes two point funds in one club (accepted by checker; documented in HUONG_DAN muc 17).
- New error code is `mt_thu_chua_ho_tro_loai` (prefix `mt_` required by MT1 tests on the last keys of `i18n_errors.py`).
- Run UI tests with real Chromium: `RBDA_TEST_CHROMIUM=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`; check there are no skips.
- Test-file count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` must equal `ls tests/test_*.py | wc -l` (now 379).

## Files touched (high level)
rbda_priority_pipeline.py, cau_hinh_ws.py, fa_daa.py, api.py, api_quan_ly.py, api_nhap.py, api_xuat.py, api_tieu_chi.py, tieu_chi.py,
phan_quyen.py, i18n_errors.py, i18n_loi.js, i18n.js, js/18_cai_dat.js, js/05_quan_ly.js, index.html, style.css, docs, CHANGELOG, TIEN_DO;
tests: test_mt2_l1_cau_hinh, test_mt2_l2_chay, test_mt2_l3_backend, test_giao_dien_mt2, test_mt2_r1_nap_loai.

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Sonnet | Coder for MT2 L1-L4, L3-FIX, R1, R1-FIX, CI-1 | context ~400k, handed off |
