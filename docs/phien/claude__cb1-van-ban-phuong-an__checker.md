# CB1 checker verdict — Milestone 1 (L1–L2), range 3ea539e..0e72c16

**Verdict: NO BUGS.**

## Run
- `tests/test_cb1_noi_dung.py`, `test_cb1_api_pdf.py`, `test_mt1_api.py`, `test_mt1_uoc_tinh.py`, `test_ws_nhan.py`, `test_gt3_phan_quyen.py`: 183 passed.
- `kiem_nhanh.py`: 7/7 (trung_khit passes once `origin/main` is fetched; no algorithm file in the diff).
- The 4 older tests the coder adjusted only exclude the new `cb1_` codes / add the 3 new names; no weakening.

## Checked
- Inv. 1/2/4/5/6/7: no algorithm, priority, CSV or schema file touched; `chot_phuong_an` is a plain `workspace_settings` row, `doc_cau_hinh` reads only `config`; `run_history` count unchanged by chốt/export (own script); chốt written in one `_ket_noi_ghi` transaction; codes in `i18n_errors.py` + regenerated `i18n_loi.js`.
- Privacy: content dict is whitelisted (`KHOA_NOI_DUNG`); PDF text of both versions has no student id/name; no score/stb field can enter the dict.
- Seed: absent by default; `in_hat_giong=True` on dự kiến → `cb1_hat_giong_chua_khoa`; present only when ticked on bản chốt after lock (seed 31415926 grep).
- Roles: all 3 names in `_QUAN_TRI`; audit row path via `nen_ghi` tested.
- Edge cases run by hand: no run yet (dự kiến OK, chốt refused); chốt twice (one row); chốt → change goal card → re-export (warning `doi_sau_chot` in PDF); re-chốt clears it but `xep_khac_chot` correctly appears (official run used older rules); FA off (“Không áp dụng bước nhận khiếu nại”); reportlab missing (test exists).

## Notes (not bugs)
- The protocol path `kiem_nhanh.py` is actually `.claude/skills/soat-ma/scripts/kiem_nhanh.py`.
- Leak test asserts ids and names only (stb is queried but not asserted); safe because of the whitelist, optional to tighten in L3/L4.

---

# Milestone 2 (L3 UI + L4 docs), range 0e72c16..2a72a38 (+ 842a6f4 leak-test tightening)

**Verdict: NO BUGS.**

- `tests/test_cb1_ui.py` (Chromium, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`): 7 passed. API/PDF/permission/ws_nhan tests: 114 passed. `kiem_nhanh.py` 7/7.
- Leak test: at 2a72a38 it was NOT yet tightened (stb/score unused); commit 842a6f4 now sets unique per-student `stb_number` (700000+rowid) and `score` (8123.25+rowid) and asserts none appear in either PDF version. Passes.
- UI: panel is admin-only (`data-quyen`), teacher skips the call (no refused-audit noise); confirm box lists goal + rules, re-chốt asks again, Esc/cancel works; bản chốt and seed checkbox disabled with a reason until chốt + official run + lock; no hard-coded text (i18n keys). Product code in L3 touches only UI + `.run-confirm-bar[hidden]` CSS fix.
- Docs: HUONG_DAN section, 5-step demo script and code-map row present and consistent with behaviour; no commentary written for the student's report.
- Minor (not a bug): panel refreshes on every `pointerenter` (extra read-only API call per hover); harmless.
