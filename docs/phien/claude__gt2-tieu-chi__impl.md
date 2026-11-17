# Branch handoff: claude/gt2-tieu-chi (writer / impl)

> Purpose: a fresh writer session reads CLAUDE.md, docs/phien/GT_GIAO_THUC.md, docs/phien/claude__gt2-tieu-chi.md, then THIS file.
> Language: English. Lead session: session_01YVAyu3PPHv9SNntepRSLwh. Lot specs: docs/ke_hoach/gt/GT2_TIEU_CHI.md.

## Feature / goal
GT2 writer role: implement lots L1-L4 (criteria in plain words, trial runs, compare, adopt) on this branch, one lot per `GO L<n>` from the lead.

## Plan (lead ticks after checker NO BUGS)
- [x] L1 Criteria in plain words + allow-list (writer done, awaiting checker)
- [ ] L2 Trial runs (loai_chay, ket_qua_thu, run_thu)
- [ ] L3 Compare two runs
- [ ] L4 Adopt a trial's criteria

## Current state (overwrite each handoff)
- Done: L1, commits ecf2130 (+ merge 4738551), pushed. `WRITER DONE L1` sent to lead.
- In progress: nothing. Waiting for REVIEW result / `FIX L1` / `GO L2`.
- Tests: tests/test_gt2_tieu_chi.py (107) + tests/test_giao_dien_gt2_tieu_chi.py (6 Chromium) all pass; kiem_nhanh 7/7, 60 cases identical; ruff clean.
- Open problems: none known. tests/ row of CLAUDE_CHI_TIET.md (300 files / 6.430 cases) will conflict at integration; recount.

## Decisions and gotchas (keep short)
- Error code gt2_tieu_chi_khong_hop_le NOT added in L1: cau_hinh_ws._chuan_hoa already rejects unknown keys/values (ws_du_lieu_sai). Add in L2 if run_thu needs it.
- get_tieu_chi lives in api_tieu_chi.py (TieuChiMixin), uses self._cfg_ws(nghiem=True); works without workspace mode; saving needs workspace mode (update_workspace_config).
- Default workspace config has wharton=True (A13.13) while LUAT_XEP_MAC_DINH has False; descriptions follow the saved rules.
- tests: soat-ma chu_cam bans "you" in English UI strings; test_a13_12_tai_lieu checks test file count in CLAUDE_CHI_TIET.
- Env: .venv set up; .claude/phien_vai.json written (impl).

## Next steps (ordered)
1. Wait for lead: FIX L1 or GO L2.
2. L2: re-grep run_history / MAX(run_id) / ORDER BY run_id in ALL .py first; schema via di_tru_schema (loai_chay) + ket_qua_thu after fa_phan_hoi block; never redraw STB; refuse FA with gt2_thu_chua_ho_tro_fa if solver needs fa_* writes.

## Files touched
- tieu_chi.py, api_tieu_chi.py, js/15_tieu_chi.js, api.py (mixin), index.html (GT2 block), i18n.js (gt2_tc_*), js/05_quan_ly.js, js/08_khoi_dong.js, js/_danh_sach.txt
- tests/test_gt2_tieu_chi.py, tests/test_giao_dien_gt2_tieu_chi.py
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Sonnet (writer) | L1 implemented, tested, pushed, reported | context >200k, handed off |
