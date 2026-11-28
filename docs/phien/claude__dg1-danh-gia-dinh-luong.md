# Branch handoff: claude/dg1-danh-gia-dinh-luong

> Purpose: a fresh session reads CLAUDE.md, then THIS file, then `docs/phien/DG1_GIAO_THUC.md`, and can continue.
> Language: English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
**DG1 — quantitative evaluation evidence (size M).** Reviewer feedback (Truong, 2026-11-28): "no quantitative evidence of
wish satisfaction, quota allocation, or the effect of changing criteria; results are mostly exported files. Test on simulated
(or permitted) datasets of different scales; measure wish-satisfaction rate, number of unassigned students, quota usage."
New item code; add a stub to `SO_DANG_KY_33_MUC.md` § "Phụ lục" + `ke_hoach_thay_doi.json` (L1).
Output = ONE reproducible harness + raw tables. **No product code in L1–L3** (measurement only, like `du_lieu_test/stress/`).
Academic integrity: every number is SIMULATED; the report holds tables + "how to reproduce" only; the "Nhận xét / kết luận"
section is a blank heading «Học sinh tự viết». Never draft interpretation.

## Reuse (do not re-implement)
- Run path: `PipelineAPI` + `import_csv_auto` / Sổ nhập import + `run_pipeline`, read `match_results` (as `bao_cao_phan_bo.chay_pipeline`).
- Per-run stats: `tieu_chi._thong_ke`, run diff: `tieu_chi.so_sanh_lan_chay` (pure functions).
- Data generation: skill `sinh-du-lieu-clb` `sinh_ngau_nhien` + `stress/_chung.mo_rong_chu_de` (50+ clubs).
- Existing measurements to cross-check, not redo: `do_khong_du_tru.py`, `do_do_dai_nguyen_vong.py`, `do_anh_huong_seed.py`,
  `do_danh_doi_on_dinh.py`, `do_toi_uu_on_dinh.py`, `stress/s4_dung_dan.py` (stability).

## Metrics (M = must, O = optional). Each is reported per session (buổi) AND per student over all sessions.
**A. Wish satisfaction** — M: % assigned to wish 1 / top-2 / top-3 / top-k (cumulative rank profile, denominator = ALL
students, also shown over assigned only); mean & median assigned rank; # assigned to a club NOT in their list (must be 0).
M: same split by group: Tier 1 (tested) vs Tier 2, reserve-eligible (each reserve category) vs general, grade/class.
M: stability check = # justified-envy / blocking pairs (must be 0, reuse `s4_dung_dan` checker). O: # Pareto-improving
swaps left (`do_danh_doi_on_dinh`), gap to rank-optimal (`do_toi_uu_on_dinh`).
**B. Unassigned** — M: count and %; split by cause from `fa_ly_do`/reasons: (i) every listed club full of higher-priority
students, (ii) failed / no score for tested clubs, (iii) empty or very short list, (iv) total capacity < students.
M: "unassigned while seats remain" = # unassigned students × # clubs with empty seats they did not list (mismatch signal).
**C. Quota usage** — M: overall fill = assigned / total capacity; per-club fill (min, p25, median, max; # full, # < 50 %);
reserve seats used / offered; reserve-eligible admitted via reserve vs via general; demand ratio per club
(# wish-1 / capacity) next to its fill rate.
**D. Effect of changing criteria** (one change at a time vs the default; same data, same seed) — M: for each variant,
delta of A1–C and **churn** = # students whose club changes, # better / worse off (rank up/down), split by group.
Variants M: reserves off; `tier_mode`/`score_scope` alternatives allowed by `tieu_chi.cac_lua_chon_hop_le`; `max_choices`
3 / 5 / 10 (truncate lists); capacity −20 % / +20 %. O: Wharton/medals on vs off, FA-DAA on vs off.
M: seed sensitivity: 20 seeds → mean ± sd, min–max of A–C, and # students whose "has a seat" flips across seeds.
**E. Scale & cost** — M: run time (median of 3), rounds; scales below. Not memory (already in `stress/s1`).

## Datasets (all simulated; seeds fixed; written to the report)
- Scales: 120×10, 300×10, 800×20 (target school), 2 000×50; multi-session: 800×20 × 3 sessions (`bo_nhieu_buoi`-style).
- Demand shapes per scale: balanced (uniform popularity), skewed (Zipf s≈1, hot clubs), tight (capacity = 0.9 N),
  loose (capacity = 1.3 N). Existing sets also run as-is: `bo_sach`, `bo_can_bang`, `bo_kich_tran`, `SO_NHAP_DQT_800HS_HOP_LE.xlsx`.
- "Permitted real data": `--so-nhap PATH` flag runs the same metrics on a Sổ nhập the school allowed; never committed;
  output marked «dữ liệu thật — không commit». Default run uses simulated data only.

## Decisions (safe defaults; do not re-ask)
- D1 Harness at `du_lieu_test/danh_gia/do_danh_gia.py` (+ `_chi_so.py` pure metric functions, + `README.md`). Flags `--nhanh`
  (120/300/800, 3 seeds — CI-friendly < 2 min) and full (all scales, 20 seeds). Output `ket_qua/*.json` (gitignored except
  the committed baseline `ket_qua/mac_dinh.json`) + `docs/ke_hoach/BAO_CAO_DANH_GIA_DINH_LUONG.md` generated, no hand-typed numbers.
- D2 Temp DB per run (`tempfile`); never touch `app.db`. Invariant 1 untouched (no product change) — still run `kiem_nhanh.py`.
- D3 Metric functions are pure and unit-tested on a hand-checkable 6-student × 3-club case (`tests/test_dg1_chi_so.py`).
- D4 Metric definitions table (name, formula, denominator, source column) is part of the report, so a reader can recompute.
- D5 L4 (optional, the only product change): if the default (non-FA) results screen shows no rate summary, add a read-only
  «Chỉ số phân bổ» block (A1, B count, C fill) via a NEW pure function reusing `tieu_chi._thong_ke`; `{ok,data,errors}`;
  texts via i18n `dg1_`. If an equivalent already shows, drop L4 and write one line why.

## Plan (lots; ✱ = must-ship)
- [ ] ✱L1 `_chi_so.py` (A, B, C metrics, pure) + `tests/test_dg1_chi_so.py` (test first) + registry stub.
- [ ] ✱L2 Dataset generator + runner (scales × shapes × seeds, E timing), JSON out, `--nhanh`, `--so-nhap`; smoke test runs `--nhanh` on 120×10 only.
- [ ] ✱L3 Criteria variants + seed sweep (D) using `so_sanh_lan_chay`; report generator → `BAO_CAO_DANH_GIA_DINH_LUONG.md`
      (definitions, tables per section A–E, reproduce commands, blank «Nhận xét — học sinh tự viết»); cross-check 3 numbers
      against `SO_LIEU_DA_KIEM_CHUNG.md` §2 (bo TEST, seed 42: 108/120, NV1 64) — must match exactly.
- [ ] L4 In-app «Chỉ số phân bổ» (D5), one Chromium test.
- [ ] Final: tests green, `kiem_nhanh.py` 7/7, `soat-ma`, CHANGELOG + TIEN_DO `DG1-L<n>`, CI green.

## Current state
- Plan only (Opus planner, 2026-11-28). No code. Plan files were committed on `claude/vg2-ra-soat-theo-vai` (only branch the
  planning session could push); the coder creates `claude/dg1-danh-gia-dinh-luong` from `origin/main` and checks these two files out.

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus | plan + metrics outline | planner role (rule 12) |
