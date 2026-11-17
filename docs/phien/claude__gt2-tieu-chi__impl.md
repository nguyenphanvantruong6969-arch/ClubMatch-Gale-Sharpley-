# Branch handoff: claude/gt2-tieu-chi (writer / impl)

> Purpose: a fresh writer session reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, docs/phien/claude__gt2-tieu-chi.md, then THIS file.
> Language: English. Lead session: session_01YVAyu3PPHv9SNntepRSLwh. Lot specs: docs/ke_hoach/gt/GT2_TIEU_CHI.md.

## Feature / goal
GT2 writer role: implement lots L1-L4 (criteria in plain words, trial runs, compare, adopt), one lot per `GO L<n>` from the lead.

## Plan (lead ticks after checker NO BUGS)
- [x] L1 Criteria in plain words (passed; fixes 9b67a95, 48ad9d8)
- [~] L2 Trial runs: code + tests + docs written, committed as WIP; related-test run NOT yet confirmed; `WRITER DONE L2` NOT yet sent
- [ ] L3 Compare two runs
- [ ] L4 Adopt a trial's criteria

## Current state (overwrite each handoff)
- Done (L2, uncommitted before this handoff, committed now): `run_thu(rules_thu, chi_buoi=None)` in api_tieu_chi.py; schema `run_history.loai_chay` (CREATE + di_tru_schema ALTER) and table `ket_qua_thu` (SCHEMA + di_tru) in rbda_priority_pipeline.py; helpers `loc_chinh_thuc(cur)` / `run_chinh_thuc_moi_nhat(cur)` there; official readers filtered: api.get_run_history, api_xuat._doc_ly_do_moi_nhat, fa_sau_xep.run_goc_theo_buoi; error codes gt2_* in i18n_errors.py (+ i18n_loi.js regenerated); CHANGELOG, TIEN_DO row, CLAUDE_CHI_TIET count (301 files / 6.461 cases), Needs Truong line (FA trial unsupported).
- Verified: tests/test_gt2_chay_thu.py 25 passed; ruff clean; kiem_nhanh 7/7, 60 cases identical.
- NOT verified: the broad related-test run (48 files that grep run_history / di_tru_schema / sqlite_master / PRAGMA table_info) was started in background and unfinished. Re-run it: `F=$(grep -l "run_history\|di_tru_schema\|run_goc_theo_buoi\|_doc_ly_do_moi_nhat\|get_run_history\|sqlite_master\|PRAGMA table_info" tests/*.py)`; run quiet per protocol (can take >10 min; run in background). Fix any failure (likely: tests asserting exact table lists / run_history column order / di_tru_schema()==[] on new DB).
- soat-ma four tiers (SKILL.md) not yet read through; only kiem_nhanh run.

## Decisions and gotchas
- FA trial refused with gt2_thu_chua_ho_tro_fa (saved or trial fa_daa true); STB never drawn: missing numbers -> gt2_thu_stb_chua_day; needs official run + locked STB else gt2_chua_co_lan_chinh_thuc.
- ket_qua_thu.rank_in_list = rank_in_student_pref of the assigned club.
- Trial rules validated by cau_hinh_ws._chuan_hoa(tron_len(saved, {"rules": rules_thu}), kiem_trung=False); ValueError -> gt2_tieu_chi_khong_hop_le.
- Official `MAX(run_id)` uses in api.py left as is (inside the official transaction, serialized by _khoa_ghi).
- Env: .venv ready; .claude/phien_vai.json written (impl).

## Next steps (ordered)
1. Run the related tests (above) and fix failures; run soat-ma tiers (report only).
2. If green: amend nothing, commit fixes, `git pull --no-rebase && git push`, send `WRITER DONE L2` (format §7) to the lead.
3. Wait for REVIEW/FIX L2 or GO L3.

## Files touched
- api_tieu_chi.py, rbda_priority_pipeline.py, api.py, api_xuat.py, fa_sau_xep.py, i18n_errors.py, i18n_loi.js
- tests/test_gt2_chay_thu.py
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/phien/claude__gt2-tieu-chi.md (Needs Truong line)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Sonnet (writer) | L1 implemented, tested, pushed, reported | context >200k, handed off |
| 2026-11-17 | Sonnet (writer 2) | L1 fix1+fix2 passed; L2 coded and tested (25 new), WIP committed | related-test run unfinished; context >200k, handed off |
