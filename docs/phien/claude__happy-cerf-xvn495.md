# Branch handoff: claude/happy-cerf-xvn495

## Feature / goal
Start of field-trial phase (Truong, 2026-11-22). (1) One import file that is valid in every Cài đặt mode so the
admin can switch Chỉ xếp / Chia 100 / Huy chương and "Chia CLB theo loại" back and forth without re-importing.
(2) Plan a deep stress test run by two Sonnet implementers on sub-branches; protocol `docs/phien/ST_GIAO_THUC.md`.

## Plan (written by Opus)
- [x] `du_lieu_test/tao_so_nhap_doi_che_do.py` → `du_lieu_test/SO_NHAP_DOI_CHE_DO_150HS.xlsx` (simulated data).
- [x] Verified with the real API: imported in Huy chương mode → 0 import warnings; 8 mode switches + 3 chia_loai
      toggles, health report empty and `run_pipeline(seed=42)` ok after every switch.
- [x] ST-A on `claude/happy-cerf-xvn495-st-a` (backend): 8 bugs (0 S1, 4 S2, 3 S3, 1 S4), `ST_BAO_CAO_A.md`.
- [x] ST-B on `claude/happy-cerf-xvn495-st-b` (UI): 13 bugs (1 S1, 1 S2, 6 S3, 5 S4), `ST_BAO_CAO_B.md`.
- [x] Fix plan: `docs/phien/SF_GIAO_THUC.md` (item SF, two coders on the son branches, loop until green).
- [ ] SF-A lots 1–4 on `-st-a`; SF-B lots 1–4 on `-st-b`; cross-check; one PR `-st-b` → this branch.
- [ ] ST2 crash-hunting (`ST2_GIAO_THUC.md`) on new branches `-st2-a` / `-st2-b` from this branch after SF is merged + green.
- Prompts for all four sessions: `docs/phien/SF_ST2_PROMPTS.md`.

## Current state
- Done: data file + generator, protocol, this file. No production code touched.
- Open finding for ST-A: importing in Chia 100 / Chỉ xếp silently drops Loại (and points) columns; switching to
  Huy chương afterwards blocks the run (`fa_thieu_clb_tu_do`, `fa_clb_thieu_loai`) until re-import.

## Decisions and gotchas
- Why the file is valid for both point rules: medals 60/30/10 sum to 100 inside ONE fund (tested or untested);
  the other fund is empty or one blank club, which Chia 100 autofills to 100 in memory
  (`tu_dien_wharton_mot_clb`). Each session: 1 Tự do, 3 Giới hạn, 3 Tuyển chọn.

## Files touched
- du_lieu_test/tao_so_nhap_doi_che_do.py, du_lieu_test/SO_NHAP_DOI_CHE_DO_150HS.xlsx: test data.
- docs/phien/ST_GIAO_THUC.md, docs/phien/claude__happy-cerf-xvn495.md, CHANGELOG.md.

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Opus | data file, ST protocol, two implementer prompts | planning only |
| 2026-11-23 | Opus | ST results summarised; SF fix protocol + two coder prompts | planning only |
| 2026-11-23 | Opus | ST2 crash-hunting protocol + prompts file | planning only |
