# Branch handoff: claude/vibrant-goodall-sqcnbb

> Purpose: a fresh session reads CLAUDE.md, then THIS file. This file holds the AGREED SPEC for registry item A5 (small part).
> No product code has been written yet. Planning (Opus, rule 12) still has to create branch `claude/a5-nhom-dong-hang`,
> its branch file and `docs/phien/A5_GIAO_THUC.md`. This file is the input to that planning session.

## Feature / goal
Registry item **A5 (small part)**: equal-rank priority groups. Each student keeps exactly ONE group label.
Two or more labels can share a rank (strict tiers) or share one reserve pool (reserve mode); all of them
rank above every other group. Size L (touches algorithm, invariant 1): lead + coder + checker, at most 4 lots.

## Decisions (Truong, 2026-11-22)
- Student has ONE label only (multi-label students rejected).
- Invariant 7 exception approved: the cells `clubs.reserve_group` and an entry of `rules.tiers` may hold `a|b`.
  No new column, no schema change, CSV/Sổ nhập column names unchanged.
- D1 = POOLED: labels a and b compete together for the reserve seats by base rank. `club_choice_function` unchanged.
  "Equal share" per label is OUT of scope (not even an optional lot). Docs must say: the higher-scoring group may take all reserve seats.
- A and B never run in one run: strict tiers set `bo_qua_du_tru = True` (`tham_so_luat`). They are two features sharing the `|` notation.

## Plan (to be refined by Opus; at most 4 lots)
- [ ] Lot 1 (must) core: shared label-splitting helper; `default_reserve_eligible_fn`; `xay_tier_rank`; byte-identical + substitutability tests.
- [ ] Lot 2 (must) backend: club-cell normaliser (split `|`, normalise each, dedupe, sort, join) at `create_or_update_club`, `so_nhap`, CSV; reject `|` in student labels; `csv_reserve_group_unknown`; `list_reserve_groups_in_use`; `tiers` duplicate check in `cau_hinh_ws`; report SQL; goal-card test.
- [ ] Lot 3 (must) UI: club form hint, tiers textarea hint, display "a = b", i18n (`i18n_errors.py` then `python tao_i18n_js.py`), `ws_v_tiers` in `js/075_workspace.js`.
- [ ] Lot 4 (optional) docs: HUONG_DAN, CHANGELOG.md, TIEN_DO.md, A5 note.

## Verified gotchas (read from the code)
1. `NhapDuLieuMixin.chuan_hoa_nhom_du_tru` (api_nhap.py) replaces every non-alphanumeric run with `_`, so `a|b` would silently become `a_b`. Need a new club-cell normaliser. `|` is safe: every existing write path goes through the normaliser, so stored data cannot contain it.
2. `api_bao_cao.py` (~L566-572) compares `s.reserve_group = c.reserve_group` in SQL. Use `instr('|'||c.reserve_group||'|', '|'||s.reserve_group||'|') > 0`. Do NOT use LIKE: `_` in labels is a wildcard.
3. `csv_reserve_group_unknown` (api_nhap.py ~L1059) compares a student label with DISTINCT club labels: split `|` first, else false warnings. Same for `list_reserve_groups_in_use` (form suggestions).
4. `muc_tieu.de_xuat_cho_giu` / `nhan_dien_muc_tieu`: a club `a|b` counts as holding for another group, so the "one group" goal card overwrites it. Correct; lock it with a test.
5. `rules.tiers` entry `a|b` = same rank. `xay_tier_rank` normalises names with `chuan_hoa_tim_kiem` (not the club normaliser): keep that. Validate label uniqueness across ranks in `cau_hinh_ws.py` (~L354) and `ws_v_tiers` (JS).
6. FA-DAA has its own `reserve_fn` and does not read labels: untouched.
7. Anti-endogeneity (invariant 2) holds: a label is a person property, not a preference rank.

## Acceptance (kiem_nhan)
- Single-label cells and `tiers` without `|`: every `match_results` row byte-identical (3 datasets x 20 seeds).
- Two labels in one tier order by score then STB, both ahead of other groups and of unlabelled students.
- A label in two ranks: error in Python and JS.
- Randomised substitutability and aggregate-demand test for multi-label clubs (invariant 8).
- Student cell containing `|`: clear error, no group `a_b` created.

## Next steps (ordered)
1. Opus planning session: create `claude/a5-nhom-dong-hang`, its branch file, `docs/phien/A5_GIAO_THUC.md` (model: `XP1_GIAO_THUC.md`, budget: `_GIAO_THUC_GON.md`).
2. Lead runs coder + checker lot by lot.

## Files touched
- docs/phien/claude__vibrant-goodall-sqcnbb.md: this spec (documentation only).

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Sonnet | Design discussion and code survey for A5; wrote this spec | No product code changed |
