# MT0 memo — goal-adjustable allocation: price, commitment, metrics

> New item **MT** (outside the 33-item registry; parent C3/A1), research lot MT0. Written 2026-11-20 by the
> Opus session (Truong: "no more Fable, you do it"). **SỐ LIỆU MÔ PHỎNG** — synthetic data only, never a survey.
> Commentary and conclusions for the project report are Truong's to write; this memo gives evidence and options.
> Script: `du_lieu_test/do_muc_tieu_mt0.py` (real `run_rbda` / `verify_stability`, ~20 s). No production code changed.

## Setup

800 students, 20 clubs, 10 preferences, 5 tested clubs, 20 seeds per scenario. Group G gets a uniform soft
reserve `r` in every club. "Hot clubs" = top 5 by first-choice count. Goal M1 = G's share in a hot club is at
least 90 % of G's school-wide share.

| Scenario | Popularity skew | Seats / student | G share | G score gap |
|---|---|---|---|---|
| S1 balanced | 0.5 | 1.05 | 15 % | 0 |
| S2 hot clubs | 1.2 | 1.00 | 15 % | −0.5 SD |
| S3 short of seats, small group | 1.0 | 0.90 | 8 % | −0.8 SD |

## Findings (severity = harm to real students if ignored)

### F1 (high) — Commit to a formula, not a number
Next-year test: policy fixed from last year's data, applied to a year whose G share differs (×0.5–1.6).

| Scenario | Fixed number: seeds meeting M1 5/5 | Formula `ceil(share × capacity)`: seeds meeting M1 5/5 |
|---|---|---|
| S1 | 14/20 | **20/20** |
| S2 | 13/20 | **20/20** |
| S3 | 14/20 | **20/20** |

The formula reads only the student list (group membership), never preferences or past outcomes, so it is
compatible with invariant 2 and can be locked before registration opens.

### F2 (high) — The formula is (almost) the smallest reserve that works
Smallest uniform `r` meeting M1 in all 5 hot clubs, median over seeds: S1 6 (formula 7), S2 6 (6), S3 3 (3).
Going beyond it buys little and costs a lot: S3, `r` 8 → 11 helps +2 G students and displaces +12 others.

### F3 (high) — Goals are not free; the cost is ≥ 1 : 1 and lands on specific students
At the formula level, displaced non-G students per helped G student: S1 26.3/23.2 ≈ 1.1, S2 ≈ 1.2,
S3 34.9/26.3 ≈ 1.3. Overall first-choice rate and unmatched count barely move — reserves redistribute,
they do not destroy. The UI must show "who gives way", not only "who gains".

### F4 (medium) — Token reserves do nothing
`r` = 1–2 changes M1 by 0 points (S1, S2) or even lowers it (S3). A school that sets "1 seat for fairness"
gets a label, not an effect. The UI should warn when the chosen reserve is below the level that can bind.

### F5 (medium) — A reserve can create a reverse gap when no gap existed
S1 (no score gap): without reserve, G's top-3 rate is already 48.8 % vs 44.8 %; the formula raises it to
54.7 % vs 43.7 %. Show the baseline gap *before* suggesting a reserve; if there is no gap, say so.

### F6 (medium) — One lever does not move every goal
The G reserve leaves unmatched count (S2 ≈ 115, S3 ≈ 135), under-filled clubs, class spread and grade-10
top-3 unchanged. Each goal card must name its own lever (capacity, list length, minimums) or be "measure only".
Large unmatched counts in S2/S3 come from skewed demand + 10-item lists, not from the mechanism.

### F7 (medium) — Small-number suppression is needed often
Clubs with 1–4 G members: S1 4–6, S2 3–8, S3 3–18 (of 20). Public and trial views must show "< 5".

### F8 (check) — Stability holds
0 blocking pairs at the formula level, all scenarios, all seeds (`verify_stability`).

## Recommendations for MT1–MT5 (planning input)

1. Goal library entries carry: definition, lever (or "measure only"), baseline-gap check, suppression rule.
2. Commitment stores the **formula** and its inputs' fingerprint; the number is recomputed at solve time.
3. Trade-off view shows helped vs displaced, marks the formula level and the token-reserve zone.
4. Guardrails always visible: first-choice rate, top-3 rate, unmatched, displaced count, blocking pairs.
5. `run_thu` does not support FA mode (`gt2_thu_chua_ho_tro_fa`): the trade-off view must state this limit
   until FA trial runs exist; `fa_daa` is off by default, so MT4 need not wait for it.

## Limits
Synthetic generator; uniform reserve in every club; one group; single session (buổi). Real data may differ.
