# Branch handoff: claude/dg1-danh-gia-dinh-luong

> Purpose: a fresh session reads CLAUDE.md, then THIS file, then `docs/phien/DG1_GIAO_THUC.md`, and can continue.
> Language: English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
**DG1 — quantitative evaluation evidence (size M).** Reviewer feedback (Truong, 2026-11-28): "no quantitative evidence of
wish satisfaction, quota allocation, or the effect of changing criteria; results are mostly exported files. Test on simulated
(or permitted) datasets of different scales; measure wish-satisfaction rate, number of unassigned students, quota usage."
New item code; add a stub to `SO_DANG_KY_33_MUC.md` § "Phụ lục" + `ke_hoach_thay_doi.json` (L1).
Output = ONE reproducible harness + raw tables/charts + an in-app read-only metrics block (L4, the only product change).
Academic integrity: every number is SIMULATED; the report holds tables, charts, definitions and "how to reproduce" only.
Two blank sections written by the student: «Giả thuyết (viết TRƯỚC khi chạy)» and «Nhận xét / kết luận». Never draft them.

## Research questions (the report is organised by these)
- Q1 How well are wishes met? (metrics A) — compared with control mechanisms, not as a bare number.
- Q2 Who stays unassigned, and is it the algorithm's fault or the data's? (metrics B, vs the max-matching upper bound)
- Q3 How well are quotas used? (metrics C)
- Q4 What changes when a criterion changes? (metrics D, one change at a time)
- Q5 How do Q1–Q3 move as competition rises? (sweep of α, see Datasets) and as the school grows? (metrics E)

## Reuse (do not re-implement)
- Run path: `PipelineAPI` + Sổ nhập / CSV import + `run_pipeline`, read `match_results` (as `bao_cao_phan_bo.chay_pipeline`).
- Per-run stats `tieu_chi._thong_ke`; run diff `tieu_chi.so_sanh_lan_chay` (pure).
- Control mechanisms `du_lieu_test/co_che_doi_chung.py`: `co_che_boston`, `co_che_thu_tu_boc_tham` (RSD), `co_che_ttc`,
  `da_clb_de_xuat`, `la_ghep_on_dinh` (blocking pairs). They call the real `club_choice_function` — keep it that way.
- Cross-check, not redo: `do_khong_du_tru.py`, `do_do_dai_nguyen_vong.py`, `do_anh_huong_seed.py`, `stress/s4_dung_dan.py`.
- HTML bar drawing: `bao_cao_phan_bo.do_thi_cot`.

## Metrics (M = must, O = optional). Per session (buổi) AND per student over all sessions; denominator always stated.
**A. Wish satisfaction** — M: % at wish 1 / top-2 / top-3 / top-k (cumulative rank curve; over ALL students and over
assigned); mean & median rank; # placed outside own list (must be 0); split by Tier 1/Tier 2, each reserve category vs
general, grade. M: # blocking pairs (RB-DA must be 0). O: Pareto-improving cycles left (`chu_trinh_pareto`).
**B. Unassigned** — M: count, %; causes: (i) all listed clubs full of higher-priority students, (ii) failed/no score,
(iii) empty/short list, (iv) total capacity < students. M: **upper bound** = maximum bipartite matching size (students ×
listed clubs, club capacity, priorities ignored; own ~30-line augmenting-path / Hopcroft–Karp, no new library).
Report: unavoidable = N − bound; cost of priority+stability = bound − RB-DA assigned. M: mismatch = # unassigned while some
club they did not list has empty seats.
**C. Quota usage** — M: fill = assigned / capacity; per-club fill (min, p25, median, max, # full, # < 50 %); reserve seats
used / offered; reserve-eligible admitted via reserve vs general; demand ratio (# wish-1 / capacity) beside fill.
**D. Criteria change** (same data, same seeds, ONE change each vs default) — M variants: reserves off; `tier_mode` /
`score_scope` alternatives from `tieu_chi.cac_lua_chon_hop_le`; `max_choices` 3/5/10; capacity −20 %/+20 %. O: Wharton
on/off, FA-DAA on/off. Per variant: Δ of A–C, churn (# students whose club changes; better / worse / same rank), by group.
**Mechanism comparison** — M: A, B, C + blocking pairs for RB-DA vs Boston vs RSD vs TTC vs club-proposing DA.
**E. Scale & cost** — M: run time (median of 3), rounds. 2 000×50 only here (not in the full sweep).
**F. Change over time (O)** — +5 % late arrivals, −5 % withdrawals: # existing students who move.

## Randomness (two separate sources — never merge them)
- Data seed = a different simulated school. Lottery seed (STB) = same school, different draw.
- Grid per config: 5 data seeds × 10 lottery seeds. Report mean, 95 % CI (t-interval over data seeds of the per-school mean)
  and the lottery-only spread (sd within a school); also # students whose "has a seat" flips across lottery seeds.

## Datasets (all simulated, seeds fixed and printed in the report)
- Preference model: utility(student, club) = α·popularity(club) + (1−α)·ε, ε ~ U(0,1) per student-club; popularity drawn
  once per school (sorted, linear 1→0). List = top L clubs by utility, L ~ uniform {3..6} (mirrors Forms Top 1–10, clipped).
  **α sweep: 0, 0.25, 0.5, 0.75, 0.9** (0 = everyone wants different things; 0.9 = everyone wants the same clubs).
- Exams: ~30 % of clubs are "Tuyển chọn"; each student ticks ≤ 5 tested clubs among their list; score = ρ·ability +
  (1−ρ)·noise, scaled 0–10, 1 decimal; **ρ ∈ {0, 0.7}** (score unrelated / related to ability). Reserve categories
  `chinh_sach` ≈ 15 %, `khoi_10` ≈ 6 %; reserve seats ≈ 10 % in the 4 most popular clubs (as `bo_sach`).
- Capacity: total = κ·N, split ∝ popularity with noise; **κ ∈ {0.9, 1.1, 1.3}**.
- Scales: 120×10, 300×10, 800×20 (target school) in the full sweep; 800×20×3 sessions once at default; 2 000×50 for E.
- Default config for D and mechanism comparison: 800×20, α = 0.5, ρ = 0.7, κ = 1.1.
- Also run as-is: `bo_sach`, `bo_can_bang`, `bo_kich_tran`, `SO_NHAP_DQT_800HS_HOP_LE.xlsx`.
- Permitted real data: `--so-nhap PATH`; output tagged «dữ liệu thật — không commit»; never committed. With permission, only
  AGGREGATE marginals (wish-1 share per club) may be used to pick a calibrated α; no rows copied.

## Decisions (safe defaults; do not re-ask)
- D1 Harness `du_lieu_test/danh_gia/`: `do_danh_gia.py` (runner), `_chi_so.py` (pure metrics + upper bound), `_sinh.py`
  (generator above, writes Sổ nhập via `so_nhap.ghi_so_nhap`), `README.md`. `--nhanh` = 120 & 300, α ∈ {0, 0.5, 0.9},
  κ = 1.1, 2 data × 3 lottery seeds (< 2 min). Output `ket_qua/*.json` (gitignored except committed `ket_qua/mac_dinh.json`)
  + generated `docs/ke_hoach/BAO_CAO_DANH_GIA_DINH_LUONG.md` (+ `.html` with 3 charts: cumulative rank curve, per-club fill,
  criteria tornado of Δ%NV1 / Δunassigned). No hand-typed numbers.
- D2 Temp DB per run (`tempfile`); never touch `app.db`. No product change in L1–L3; still run `kiem_nhanh.py`.
- D3 Pure metrics unit-tested on a hand-checkable 6 students × 3 clubs case, incl. a case where bound > RB-DA assigned.
- D4 Report starts with a metric definitions table (name, formula, denominator, source) and the generator parameters.
- D5 L4 (must): read-only «Chỉ số phân bổ» block on the default results screen (A1 %NV1/top-3, B count, C fill, reserve
  used) via a NEW pure function reusing `tieu_chi._thong_ke`, `{ok,data,errors}`, i18n `dg1_`; plus a «Chi_so» sheet in the
  Excel export. If an equivalent block already shows in default mode, add only the export sheet and note why.

## Plan (lots; ✱ = must-ship)
- [ ] ✱L1 `_chi_so.py` (A, B incl. upper bound, C; pure) + `tests/test_dg1_chi_so.py` (test first) + registry stub.
- [ ] ✱L2 `_sinh.py` (α, ρ, κ model) + runner (scales × α × κ × seed grid, E timing, JSON), `--nhanh`, `--so-nhap`;
      `tests/test_dg1_sinh.py`: same seed → byte-identical Sổ nhập; α = 0.9 gives higher wish-1 concentration than α = 0.
- [ ] ✱L3 Criteria variants + mechanism comparison + report generator (Q1–Q5 sections, definitions, charts, reproduce
      commands, two blank student sections). Exact cross-check vs `SO_LIEU_DA_KIEM_CHUNG.md` §2 (TEST set, seed 42: 108/120,
      wish-1 64). Blocking pairs 0 for RB-DA on every run.
- [ ] ✱L4 In-app block + export sheet (D5), one Chromium test, related export tests.
- [ ] O  F (late arrivals / withdrawals) if budget remains.
- [ ] Final: tests green, `kiem_nhanh.py` 7/7, `soat-ma`, CHANGELOG + TIEN_DO `DG1-L<n>`, CI green.

## Current state
- Plan v2 (Opus planner, 2026-11-28): added control mechanisms, upper bound, two-seed grid, α/ρ/κ generator, L4 must-ship,
  student hypotheses section. No code. Plan files live on `claude/vg2-ra-soat-theo-vai` (only branch the planning session
  could push); coder creates `claude/dg1-danh-gia-dinh-luong` from `origin/main` and checks these two files out (protocol §0).

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus | plan + metrics outline | planner role (rule 12) |
| 2026-11-28 | Opus | plan v2 (6 improvements) | Truong approved all six |
