# Branch handoff: claude/happy-cerf-xvn495

## Feature / goal
Start of field-trial phase (Truong, 2026-11-22). (1) One import file that is valid in every Cài đặt mode so the
admin can switch Chỉ xếp / Chia 100 / Huy chương and "Chia CLB theo loại" back and forth without re-importing.
(2) Plan a deep stress test run by two Sonnet implementers on sub-branches; protocol `docs/phien/ST_GIAO_THUC.md`.

## Plan (written by Opus)
- [x] `du_lieu_test/tao_so_nhap_doi_che_do.py` → `du_lieu_test/SO_NHAP_DOI_CHE_DO_150HS.xlsx` (simulated data).
- [x] Verified with the real API: imported in Huy chương mode → 0 import warnings; 8 mode switches + 3 chia_loai
      toggles, health report empty and `run_pipeline(seed=42)` ok after every switch.
- [ ] ST-A on `claude/happy-cerf-xvn495-st-a` (backend) — prompt in ST_GIAO_THUC context / Truong's chat.
- [ ] ST-B on `claude/happy-cerf-xvn495-st-b` (UI).
- [ ] Merge both bug reports, triage into registry items (next Opus session).

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
