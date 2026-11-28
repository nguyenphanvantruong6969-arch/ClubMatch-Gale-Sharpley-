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
**G. Feature evidence (M, Truong 2026-11-28)** — reserves, determination points (`wharton`) and medals (`fa_daa`) each
on vs off on the same data/seeds, plus a 2×2 reserves × Wharton grid; 120/300/800, α ∈ {0, 0.5, 0.9}, κ = 1.1. Generator
adds Wharton two-pool points (reuse `sinh_du_lieu_diem_quyet_tam.py` split kinds) and FA-DAA club types + medals (default
from rank, some students override; behaviours lazy / truthful / strategic as `mo_phong_fa_daa.py`). Metrics: per reserve
category vs general (%NV1, unassigned, mean rank), reserve seats used/offered, general students displaced; share placed at
top-points / gold-medal club; share of rejections decided by LOTTERY; A–C and churn per behaviour type.
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

- D6 (coder, 2026-11-28) Grid runs `run_rbda` in memory on simulated schools (the function `run_pipeline` calls); real `run_pipeline` only for the TEST seed-42 gate and `thoi_gian`.
- D7 Excel metrics = a section at the end of the «Thống kê» sheet, not a separate `Chi_so` sheet (a new sheet changes the sheet list that 6 test files + «Hướng dẫn» pin).
- D8 «Chỉ số phân bổ» denominator = ALL slots (student × session), unlike the existing «Mức đáp ứng nguyện vọng» (placed only); both shown, denominators labelled.
- D9 Group G (planner msg 02:45 read late): in `do_tinh_nang.py`, NOT `_sinh.py`/`_chi_so.py`; Wharton points go straight into `run_rbda` (not via Sổ nhập/rule key); medals reuse `mo_phong_fa_daa` model. Open: per-feature metrics not in `_chi_so.py`.

## Plan (lots; ✱ = must-ship)
- [x] ✱L1 `_chi_so.py` (A, B + upper bound, C; pure) + `tests/test_dg1_chi_so.py` + registry stub.
- [x] ✱L2 `_sinh.py` (α, ρ, κ) + runner (grid, timing, JSON, `--nhanh`, `--so-nhap`); `tests/test_dg1_sinh.py`, `test_dg1_do_danh_gia.py`.
- [x] ✱L3 Variants + 5 mechanisms + `in_bang.py` + exact cross-check vs `SO_LIEU_DA_KIEM_CHUNG.md` §2 (108/120, NV1 64). (Report generator → L5.)
- [x] ✱G `do_tinh_nang.py`: reserves × Wharton 2×2, medals (FA-DAA) vs old mode; `tests/test_dg1_tinh_nang.py`.
- [x] ✱L4 In-app «Chỉ số phân bổ» block + Excel section (D7), one Chromium test. Self-audited with soat-ma (checker file).
- [x] ✱L5 Scientific report + screenshots (AI part done 2026-11-28, Opus): `viet_bao_cao.py`, `chup_quy_trinh.py`, `tests/test_dg1_bao_cao.py`. Student sections still empty.
- [ ] O  F (late arrivals / withdrawals) — dropped this session (budget).
- [x] Final (coder part): tests green, `kiem_nhanh.py` 7/7, CHANGELOG + TIEN_DO, push. CI (`tests.yml`) not checked by the coder.

## Scientific report (L5; Truong, 2026-11-28)
Truong asked: after testing on many datasets and scales, write a scientific report from the collected data, with screenshots
where useful, including screenshots taken DURING the process. Integrity rule (CLAUDE.md) decides who writes what:
- File `docs/nghien_cuu/DG1_BAO_CAO_KHOA_HOC.md` (+ `.html` built from it, same pattern as `docs/NGHIEN_CUU_TOI_UU.*`);
  images in `docs/nghien_cuu/anh_dg1/`. Every number is read from `ket_qua/*.json` by a script
  (`du_lieu_test/danh_gia/viet_bao_cao.py`); no hand-typed numbers; the commit hash + command that produced the JSON is printed.
- Banner at the top: «Toàn bộ số liệu đo trên DỮ LIỆU MÔ PHỎNG, không phải khảo sát học sinh thật».
- Sections and authorship (AI = may draft, HS = student writes, AI leaves the heading + an empty box):
  0 Tóm tắt — HS. 1 Đặt vấn đề / câu hỏi nghiên cứu — AI states Q1–Q5 as questions only; motivation paragraph HS.
  2 Giả thuyết — HS, written BEFORE the full run (coder stops and asks Truong only here if empty: note "Needs Truong", run anyway,
  and mark in the report that hypotheses were written after). 3 Cơ chế RB-DA (short, cite `docs/CO_CHE_THUAT_TOAN.md`) — AI.
  4 Phương pháp: generator (α, ρ, κ, scales), seed grid, control mechanisms, upper bound, metric definitions table — AI.
  5 Kết quả: one subsection per Q1–Q5; tables + figures + one FACTUAL caption each («Bảng 3: tỉ lệ NV1 theo α, 5 bộ × 10 lần
  bốc thăm, trung bình và KTC 95 %»); no "cho thấy / chứng tỏ / tốt hơn" wording — AI. 6 Thảo luận — HS; AI may add ≤ 6
  neutral guiding questions («Ở α nào khoảng cách giữa RB-DA và Boston lớn nhất?»), never answers. 7 Hạn chế — HS
  (AI may list FACTUAL limits of the setup only: simulated data, list length 3–6, one school model). 8 Kết luận — HS.
  9 Tái lập: exact commands, versions, seeds, run time — AI. 10 Tài liệu tham khảo: only works already cited in repo docs
  (Gale & Shapley 1962; Kominers & Sönmez 2016; Abdulkadiroğlu, Che & Yasuda 2015 …), checked against `docs/CO_CHE_THUAT_TOAN.md`.
- Figures (matplotlib not allowed unless already in requirements-dev; else SVG/HTML via `do_thi_cot`, then screenshot):
  F1 cumulative rank curve RB-DA vs 4 controls (default config); F2 %NV1 and unassigned vs α (κ = 0.9/1.1/1.3);
  F3 per-club fill vs demand ratio; F4 criteria tornado (Δ%NV1, Δunassigned, churn); F5 RB-DA vs upper bound by κ;
  F6 run time vs scale.
- Screenshots (Playwright, `deviceScaleFactor: 2` — report figures are for people; exception to `_GIAO_THUC_GON` §3 rule),
  ≤ 10, reuse `du_lieu_test/chup_dk8.py` pattern, script `du_lieu_test/danh_gia/chup_quy_trinh.py`, temp workspace with the
  800×20 default set: S1 import of the Sổ nhập (preview), S2 data warnings = 0, S3 rules/criteria screen (tiêu chí GT2),
  S4 run in progress / done, S5 results with «Chỉ số phân bổ» block (L4), S6 per-club fill view, S7 «So sánh lần chạy»
  after the reserves-off variant (GT2-L3 UI), S8 Excel export «Chi_so» sheet (render via openpyxl → HTML table → screenshot),
  S9 the generated HTML report itself (first page). Each with a factual caption. No real student names (generator names only).
- Log in `docs/nhat_ky_ai/NHAT_KY_AI.md` (one dated line: what AI drafted, what is left to the student), via
  `dung_nhat_ky_ai.py` if it is the generator.

## Current state
**L5 AI PART DONE** (Opus, 2026-11-28). Report `docs/nghien_cuu/DG1_BAO_CAO_KHOA_HOC.md` + `.html`, figures `anh_dg1/F1..F6.svg` (7 files),
screenshots `anh_dg1/S1..S6.png`. Regenerate: `python du_lieu_test/danh_gia/viet_bao_cao.py` (keeps student text inside `<!-- HS:x -->` boxes);
screenshots: `python du_lieu_test/danh_gia/chup_quy_trinh.py` (needs Python `playwright`, Chromium from `tests/_trinh_duyet.py`).
- D10 Screenshots: 6 instead of the planned 9. S2 «warnings = 0» and S7 «So sánh lần chạy» not taken: the generated Sổ nhập raises 5 serious
  «outlier score» warnings (scores < 2 in tested clubs, ρ = 0.7 noise), shown as-is in S1; run comparison UI not driven (budget). Caption says so factually.
- D11 AI log not regenerated here: `dung_nhat_ky_ai.py` rewrites ~1 000 lines from all branches; run it after merge (it reads the CHANGELOG L5 line).
- Found while screenshotting (L4 product bug, NOT fixed — planner role): «Chỉ số phân bổ» block sub-label prints `16,099999999999994% mọi suất`
  (unrounded float) under «Chưa được xếp». Small fix in `js/03_ket_qua.js` formatter + one assertion in `tests/test_dg1_chi_so_ung_dung.py`.
- Needs Truong: write sections 0, 1.1, 2 (mark «viết sau khi có số liệu» if so), 6, 7, 8; decide on the float bug fix; confirm CI green. `kiem_nhanh.py` 7/7; `test_dg1_bao_cao.py` 2/2; no product file changed in L5.

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus | plan + metrics outline | planner role (rule 12) |
| 2026-11-28 | Opus | plan v2 (6 improvements) | Truong approved all six |
| 2026-11-28 | Opus | added L5 scientific report + screenshots | authorship split per CLAUDE.md integrity |
| 2026-11-28 | Sonnet | coder: L1–L4 + group G + full harness run (DATA READY); self-audit instead of checker | no L5 (planner writes report) |
| 2026-11-28 | Opus | L5: report generator, 7 SVG figures, 6 app screenshots, tests; found L4 float-format bug | student sections left empty |
