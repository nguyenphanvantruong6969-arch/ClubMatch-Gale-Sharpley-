# DG1 protocol (size M: coder + checker, NO lead) — follows `docs/phien/_GIAO_THUC_GON.md`

> Work source: `docs/phien/claude__dg1-danh-gia-dinh-luong.md` (metrics A–E, decisions D1–D5, lots L1–L4).
> Branch: `claude/dg1-danh-gia-dinh-luong`. Where this file and `_GIAO_THUC_GON.md` differ, THIS file wins.

## 0. Setup (coder, first session)
- Branch already exists (created from `origin/main` on 2026-11-28 with both plan files): `git fetch origin claude/dg1-danh-gia-dinh-luong && git checkout claude/dg1-danh-gia-dinh-luong`.
- Every question has a safe default: pick it, one line in "Decisions", continue. "Needs Truong" is a note, never a stop.

## 1. Roles
- Coder: Sonnet. Does L1→L4 in order, test first, commits per lot, writes `MILESTONE <k> READY` in the branch file.
- Checker: Sonnet, started by Truong at each milestone; writes only `docs/phien/claude__dg1-danh-gia-dinh-luong__checker.md`
  ending with `CHECKER REPORT <k> NO BUGS` or a numbered finding list. Max 2 FIX rounds per finding, then note + revert that lot.
- Milestone 1 = after L2 (metrics + generator + runner). Milestone 2 = after L4 (variants, mechanisms, report, UI). Milestone 3 = after L5 (scientific report + screenshots).

## 2. Checker focus
- Each metric matches its definition table row: recompute 3 metrics by hand on the 6×3 test case and 1 on `bo_sach`.
- Denominators are stated and consistent (all students vs assigned; per session vs per student).
- Cross-check with `SO_LIEU_DA_KIEM_CHUNG.md` §2 is exact; RB-DA blocking pairs are 0 on every run.
- Upper bound: RB-DA assigned ≤ max matching on every run; hand-check the bound on the 6×3 case.
- Data seed and lottery seed are separate; CI computed over data seeds; generator is deterministic per seed.
- Control mechanisms still call the real `club_choice_function` (no copied priority logic).
- Variants change ONE thing each and reuse the same data + seed; churn counts sum correctly (better + worse + same-rank-moved).
- No product file changed in L1–L3 (L4 is the only product lot) (`git diff --stat origin/main -- ':!du_lieu_test' ':!tests' ':!docs' ':!CHANGELOG.md'` empty).
- L5: every number in `DG1_BAO_CAO_KHOA_HOC.md` traceable to `ket_qua/*.json` (spot-check 5); HS sections (0, 2, 6, 7, 8) contain
  only headings / guiding questions; captions factual (grep «cho thấy|chứng tỏ|tốt hơn|vượt trội» = 0 outside quotes);
  references exist in repo docs; screenshots show no real names; AI log line added.
- Integrity: report says SIMULATED at the top; no interpretation sentences; «Giả thuyết» and «Nhận xét» sections empty; no real data committed.
- L4: invariants 1, 2, 6, 7 (export sheet is additive; CSV contract unchanged) (read-only, no rank fed into priority, `{ok,data,errors}`, i18n via `i18n_errors.py` → `tao_i18n_js.py`).

## 3. Budget
- `_GIAO_THUC_GON.md` §3. Full harness run only once, at the end (report generation); during lots use `--nhanh`.
- Tests: `tests/test_dg1_*.py` + ≤ 3 related, `-q --tb=line | tail -15`.

## 4. Final gate
- `tests/test_dg1_*.py` green, `kiem_nhanh.py` 7/7, `soat-ma` four tiers, CHANGELOG + `TIEN_DO.md` rows, push,
  GitHub Actions `tests.yml` (coverage ≥ 85 %) green. Then rewrite "Current state" and stop.

## 5. Checker prompt (Truong pastes at a milestone)
"You are the DG1 checker (Sonnet). Read CLAUDE.md, `docs/phien/claude__dg1-danh-gia-dinh-luong.md`, `docs/phien/DG1_GIAO_THUC.md`
§2. Branch `claude/dg1-danh-gia-dinh-luong`. Review milestone <k> only (`git log` since the last checker report). Do not edit product
or harness code. Write findings to `docs/phien/claude__dg1-danh-gia-dinh-luong__checker.md`, end with `CHECKER REPORT <k> NO BUGS`
or a numbered list, commit and push that file only. Reply to Truong in Vietnamese."
