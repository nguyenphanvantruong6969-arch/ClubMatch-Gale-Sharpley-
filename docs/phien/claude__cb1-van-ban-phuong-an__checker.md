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
