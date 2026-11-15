# Branch handoff: claude/fa-sc-sua (writer, lot L5)

> Purpose: fresh writer session reads CLAUDE.md, FA_SC_GIAO_THUC.md, claude__fa-sc-sua.md ("Lot L5"), then THIS file.
> Lead session: session_01YVAyu2GQZcAWLnBkzjQFwa. Checker: session_01YVAyu1NyBNoy8DMPNpoLfb.

## Feature / goal
FA-SC-L5 (P2-1): per-day lottery lock. Table `stb_buoi(buoi, student_id, so)`; first run = old `sinh_stb_theo_buoi`
(byte-identical), later runs keep old students' order every day and insert newcomers uniformly (`chen_stb_cho_hoc_sinh_moi`).

## Plan
- [x] Failing tests first: `tests/test_fa_sc_l5_khoa_so_theo_ngay.py` (62 cases, all pass)
- [x] Core: `stb_theo_buoi_da_khoa`, `doc_stb_buoi`, `KetQuaTuan.stb_tat_ca_buoi`, param `stb_buoi_da_khoa=None` on
      `run_rbda_nhieu_buoi` and `fa_daa.chay_fa_daa`; `di_tru_schema` step 8 (backup first; NOT in DEFAULT_SCHEMA on purpose)
- [x] api.py `_run_pipeline_da_khoa` (read stored when locked and not redraw; write in same transaction; step warnings
      `stb_buoi_luu_lan_dau` / `stb_buoi_ve_lai`), `api_bao_cao.get_so_boc_tham_theo_buoi`, `api_sau_xep._du_lieu_vong_2`,
      `api_quan_ly` delete_student + reset_data cleanup, i18n_errors + `tao_i18n_js.py` run
- [x] Drills: d12 20 -> 1, d16 18 -> 0 (flipped). `kiem_nhanh --co-so origin/main --so-seed 20` 7/7, 60/60 (before CHANGELOG edit)
- [x] CHANGELOG entry written; `tests/` row in CLAUDE_CHI_TIET.md updated (294 files, 6.286 cases)
- [ ] Related tests: full run of `grep -lE "stb|seed|boc_tham|lottery|di_tru_schema|dau_van_tay" tests/*.py` was ~66% done,
      no failures seen so far; I killed it for the handoff. Rerun the REST (or all) after rebase, quiet, no xdist (slow, ~25 min).
      Only failure seen earlier was test_a13_12_tai_lieu (file count) -> fixed by the CLAUDE_CHI_TIET row.
- [ ] TIEN_DO.md row `FA-SC-L5` (not written yet)
- [ ] Needs Truong line in claude__fa-sc-sua.md: invariant 3 wording extended to per-day order; fingerprint decision
- [ ] `soat-ma` (4 tiers, report only), `ruff check .`
- [ ] Final: git pull --rebase, push, send `WRITER DONE L5` (format §5) to lead

## Current state
- All code + tests done and committed in the handoff commit (local branch was behind origin by 18 commits at start; rebase needed).
- Rebase may conflict only in CLAUDE_CHI_TIET.md line 24 (tests row; recount: `pytest --collect-only -q | tail -1`,
  `ls tests/test_*.py | wc -l`), CHANGELOG.md top, i18n_loi.js (regenerate with `python tao_i18n_js.py`).

## Decisions and gotchas
- Fingerprint (FA-9): does NOT cover per-day orders (same reason as base lottery numbers); documented -> add one sentence to
  `dau_van_tay_du_lieu` docstring if missing (test asserts the text "KHÔNG gồm: số bốc thăm", which already exists).
- `stb_buoi` omitted from DEFAULT_SCHEMA so old DBs go through `di_tru_schema` backup path.
- Old workspace: first run after migration = legacy computation, then stored (step warning says so).
- Tests: stb_lottery step appears twice in `steps` (running, done): take the last one.
- `kiem_nhanh` is at `.claude/skills/soat-ma/scripts/kiem_nhanh.py`; needs `git fetch origin main` for `origin/main`.

## Next steps
1. `git pull --rebase`; rerun related tests (rest) + `tests/test_fa_sc_l5_khoa_so_theo_ngay.py` + `tests/test_a13_12_tai_lieu.py`.
2. TIEN_DO row, Needs-Truong line, soat-ma, ruff. 3. Push, report to lead.

## Files touched
rbda_priority_pipeline.py, api.py, api_bao_cao.py, api_sau_xep.py, api_quan_ly.py, fa_daa.py, i18n_errors.py, i18n_loi.js,
CHANGELOG.md, docs/ke_hoach/CLAUDE_CHI_TIET.md, tests/test_fa_sc_l5_khoa_so_theo_ngay.py, this file.

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-15 | Sonnet (writer L5) | L5 code+tests+drills+CHANGELOG | handoff at 200k tokens |
