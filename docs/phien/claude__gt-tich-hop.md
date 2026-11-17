# Branch handoff: claude/gt-tich-hop

> Fresh session: read CLAUDE.md, docs/phien/GT_GIAO_THUC.md (§5, §6, §9), then THIS file.
> English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

Status: IN PROGRESS (I0 merges)

## Feature / goal
Integrate GT1 (giải trình, `claude/gt1-giai-trinh` DONE 499edf1), GT2 (tiêu chí, `claude/gt2-tieu-chi` DONE 8965d2b)
and GT3 (quyền + tài liệu, `claude/gt3-quyen-tai-lieu` DONE c66889d) on one branch from `origin/main` (35609f7), then
run integration lots I1-I4 (spec: `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md` § "Integration lots") and the §6 CI gate.
Truong merges to main himself. No PR.

## Plan (written by Opus; ticked by Sonnet)
- [ ] I0 merges: GT1 already merged by lead (a38fef8, clean). Writer: `git merge --no-ff origin/claude/gt2-tieu-chi`,
      then `git merge --no-ff origin/claude/gt3-quyen-tai-lieu`. Conflicts are shared files only (CHANGELOG.md,
      docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/ke_hoach/TIEN_DO.md, i18n_errors.py, i18n_loi.js, index.html,
      js/_danh_sach.txt, style.css): keep every team's block, GT1→GT2→GT3 order, renumber/reformat nothing;
      `i18n_loi.js` = rerun `python tao_i18n_js.py`; CLAUDE_CHI_TIET tests row = recount files/collect.
      Done when: no conflict markers (`git grep -nE '^(<<<<<<<|>>>>>>>)'` empty), `ruff check .` clean, all
      `tests/test_gt1_*`, `test_gt2_*`, `test_gt3_*` (non-UI) pass except the intended `dir(PipelineAPI)` completeness
      failure in `test_gt3_phan_quyen.py` (fixed in I1), kiem_nhanh invariant-1 identical.
- [ ] I1 permission map: classify every GT1/GT2 PipelineAPI method in `QUYEN`.
      GT1: `tra_cuu_hoc_sinh` → `cong_khai`; lookup / slip view+export → `giao_vien`; code (re)generation → `quan_tri`.
      GT2: get_tieu_chi, run_thu, list_lan_chay, so_sanh_lan_chay, export_so_sanh_html, export_so_sanh_csv,
      ap_dung_tieu_chi → `quan_tri` (GT2 lead: compare student list is admin-only; stricter than the task file's
      "compare view → giao_vien", see Needs Truong #1). Done when `test_gt3_phan_quyen.py` passes.
- [ ] I2 student mode: accounts ON → leaving the self-lookup overlay needs an admin login; while in it only
      `cong_khai` methods work. Done when a Chromium test shows a student cannot reach any tab.
- [ ] I3 audit: run_thu, ap_dung_tieu_chi, code (re)generation, slip export each log exactly one audit row.
      Done when tested (`tests/test_gt_tich_hop.py` or a `test_gt3_*` file).
- [ ] I4 evidence pack: `du_lieu_test/tao_ca_mau_giai_trinh.py` (simulated 120 students, fixed seed) writes
      `docs/giai_trinh/CA_MAU.md` (3 got 1st choice, 3 did not — GT1 sentences + data; 1 run blocked by missing data,
      real message; 1 conflicting criteria rejected at save, real message; GT2 table default vs one alternative:
      changed students, per-group effects). Then `docs/giai_trinh/tao_goi_minh_chung.py` builds
      `GOI_MINH_CHUNG.docx` + `.pdf`; fill the "(sau tích hợp)" steps. Done when `tests/test_gt_tich_hop.py`
      regenerates CA_MAU.md byte-identically and every case matches app output. All data SIMULATED, labelled so.
- [ ] §6 CI gate on `claude/gt-tich-hop` (lint + all shards + coverage ≥ 85 %).

## Current state (overwrite each handoff)
- Done so far: branch created from origin/main 35609f7; GT1 merged (a38fef8). GT2 merge aborted (shared-file
  conflicts) for the writer.
- In progress: I0.
- Tests: none run on this branch yet.
- Open problems: none.

## Sessions
| Role | Model | Session | State |
|---|---|---|---|
| lead | Opus | session_01YVAyu27w5WZmfqRfkjo3Av | running |
| writer | Sonnet | session_01YVAytzUoskbGS1rGPtH4ZW | GO I0 sent 05:30 UTC |
| checker | Sonnet | session_01YVAytyqoQv2u5JTmCyKLkE | waiting for REVIEW I0 |

## Needs Truong
1. Compare view permission: task file says `giao_vien`; GT2 lead classified all GT2 APIs `quan_tri` because the
   compare student list shows other students' outcomes. Recommend: keep `quan_tri` (privacy); loosen later if
   teachers need it.
(GT1/GT2/GT3 branch files hold their own Needs Truong lists; they are carried into the final summary.)

## Decisions and gotchas
- Merge order GT1 → GT2 → GT3 (§9 step 2). Never rebase or force-push.
- GT3 L2 `dir(PipelineAPI)` completeness test fails after merges until I1: intended.

## Next steps (ordered)
1. Writer: I0, then I1-I4 by §5 loop. 2. Lead: §6 CI gate. 3. Status DONE + §10 summary, archive children, stop.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Opus (lead) | GT2 DONE verified (run 44018417803 success); branch created, GT1 merged, file written | — |
