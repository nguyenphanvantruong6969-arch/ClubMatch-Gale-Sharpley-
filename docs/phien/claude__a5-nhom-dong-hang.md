# Branch handoff: claude/a5-nhom-dong-hang

> Fresh session: read CLAUDE.md, then THIS file, then `docs/phien/A5_GIAO_THUC.md`. Cap 100 lines.
> Spec source: `docs/phien/claude__vibrant-goodall-sqcnbb.md` (design talk 2026-11-22). Planner: Opus, no product code.

Status: IN PROGRESS 2026-11-23 — lead started, creating coder + checker

## Feature / goal
Registry item **A5 (small part)**: equal-rank priority groups. Each student keeps exactly ONE label
(`students.reserve_group`). Notation `a|b` groups labels:
- **A, strict tiers**: an entry of `rules.tiers` may be `"a|b"` = labels a and b share ONE rank; both rank above
  every later entry and above unlabelled students. Inside the rank: tested first, −score, STB (= `compute_club_priority`).
- **B, reserve mode**: a cell `clubs.reserve_group` may be `"a|b"` = a student is reserve-eligible if their label is
  in the set. **D1 = POOLED**: a and b compete together for the reserve seats by base rank; `club_choice_function`
  unchanged. "Equal share" is OUT of scope (no lot). Guide must say: the higher-scoring group may take all seats.
- A and B never run in one run (strict tiers set `bo_qua_du_tru = True`); they only share the notation.

## Decisions (Truong, 2026-11-22 — do not ask again)
- Invariant 7 exception: `clubs.reserve_group` and `rules.tiers` entries may hold `a|b`. No new column, no schema
  change, CSV / Sổ nhập column names unchanged, no `di_tru_schema` change.
- A student cell containing `|` is an ERROR (clear message), never silently `a_b`.
- FA-DAA (`fa_daa.py`, own `reserve_fn`, does not read labels): untouched.
- Invariant 2 holds: a label is a person attribute, not preference rank.
- Lead model: Sonnet (`_GIAO_THUC_GON.md` §1: design is settled). Truong may swap in Opus.

## Plan (lots; ticked by the lead after checker NO BUGS)
- [ ] **L1 core (must)** — `rbda_priority_pipeline.py`
  - [ ] One helper `tach_nhom_clb(o) -> tuple[str, ...]` (split `|`, strip, drop empties; `""`/None → `()`).
        Pure, no normalising (callers normalise their own way). Used by every lot.
  - [ ] `default_reserve_eligible_fn`: cell without `|` keeps the exact old `==` path (byte-identical); with `|`
        → student label `in` set.
  - [ ] `xay_tier_rank`: each part of an entry gets the entry's index (key = existing `khoa`, i.e.
        `chuan_hoa_tim_kiem`); `uu_tien_theo_nhom` unchanged (already groups by rank).
  - [ ] Tests `tests/test_a5_nhom_dong_hang.py`: two labels in one tier ordered by score then STB, both before
        other groups and unlabelled; reserve `a|b` admits a and b, not c; randomised (≥ 200 cases, fixed seed)
        substitutability + law of aggregate demand of the club choice with multi-label eligibility (invariant 8).
  - [ ] Invariant 1: `kiem_nhanh.py --so-seed 20` → `trung_khit` OK (3 datasets × 20 seeds vs `origin/main`).
- [ ] **L2 backend (must)**
  - [ ] `NhapDuLieuMixin.chuan_hoa_o_nhom_clb(raw)` (api_nhap.py, next to `chuan_hoa_nhom_du_tru`): split `|`,
        `chuan_hoa_nhom_du_tru` each part, dedupe, sort, join `|`; no `|` → exactly `chuan_hoa_nhom_du_tru(raw)`.
  - [ ] Use it for CLUB cells in `create_or_update_club` (api_quan_ly.py), Sổ nhập club sheet (`so_nhap.py`
        path into api_nhap), clubs CSV. Student paths keep `chuan_hoa_nhom_du_tru` but REJECT raw `|`
        (`_ghi_nhom_du_tru`, `create_or_update_student`/bulk paths in api_quan_ly.py ~L443/457, Sổ student sheet,
        student CSV) with new error code `a5_nhom_hs_co_gach` (append at END of `i18n_errors.py`, vi+en,
        then `python tao_i18n_js.py`).
  - [ ] `csv_reserve_group_unknown` check (api_nhap.py ~L1059): build `nhom_clb` from split parts.
        `list_reserve_groups_in_use` (api_quan_ly.py): suggest single labels (split), not `a|b` strings.
        Also `_soat_nhom_du_tru_la` (api_nhap.py ~L334) if it compares to club cells.
  - [ ] `cau_hinh_ws.py` tiers check (~L354): each part non-empty; a label (same key as `xay_tier_rank`) in two
        entries → `ValueError` (follow the existing message style there).
  - [ ] `api_bao_cao.py` (~L566-572): `instr('|'||c.reserve_group||'|', '|'||s.reserve_group||'|') > 0`.
        NEVER `LIKE` (`_` is a wildcard and labels contain `_`).
  - [ ] `git grep -n "reserve_group" -- '*.py' ':!tests'`: list every other equality on club vs student label
        (e.g. `giai_trinh.py`, `phieu_giai_trinh.py`, `bao_cao_tong_hop.py`, `lop_hoc_sinh.py`); fix each with
        `tach_nhom_clb`; write the list in `__coder.md`.
  - [ ] `muc_tieu.de_xuat_cho_giu` / `nhan_dien_muc_tieu`: a club `a|b` counts as "held for another group"
        (`clb_ghi_de`) and makes `danh_cho` → `tuy_chinh`. No code change expected; lock with tests.
  - [ ] Tests: `tests/test_a5_nhom_dong_hang_backend.py` (normaliser cases `"B|a| a |"` → `"a|b"`, student `|`
        error + nothing written, CSV warning silent for `a` when a club has `a|b`, report count, tiers
        cross-rank error, goal-card lock, round-trip Sổ nhập export→import keeps `a|b`).
- [ ] **L3 UI (must)** — `js/075_workspace.js`, `js/15_tieu_chi.js`, i18n
  - [ ] `ws_v_tiers`: split each line by `|`, trim, key like the backend (lower-case, no diacritics, single
        spaces); duplicate inside or across lines, or empty part → error.
  - [ ] `rvTiers` shows `a = b › c`; `js/15_tieu_chi.js` read-only summary of tiers shows `a = b`
        (textarea input keeps `|`).
  - [ ] Hints: tiers textarea placeholder/hint and club "nhóm ưu tiên" field hint explain `a|b`; keys prefix `a5_`.
  - [ ] One Chromium test file `tests/test_a5_giao_dien.py`, one shared page fixture: JS error on a label in
        two lines; review shows `a = b`.
- [ ] **L4 docs (must; Truong asked)** — guide section on `a|b` (both modes) with the warning "nhóm điểm cao hơn
      có thể lấy hết suất dự trữ"; registry A5 note (small part done); CHANGELOG + TIEN_DO. Simulated data only.

## Acceptance (kiem_nhan)
1. Single-label cells and `tiers` without `|`: every `match_results` row byte-identical, 3 datasets × 20 seeds.
2. Two labels in one tier: ordered by score then STB, both ahead of other groups and unlabelled students.
3. A label in two ranks: error in Python (`cau_hinh_ws`) and JS (`ws_v_tiers`).
4. Randomised substitutability + aggregate demand pass for multi-label clubs.
5. Student cell with `|`: clear i18n error, no `a_b` stored. Report SQL uses `instr`, not `LIKE`.
6. CI green: lint, all shards, coverage ≥ 85 %, Windows build.

## Verified gotchas
- `chuan_hoa_nhom_du_tru` maps every non-alphanumeric run to `_`: `a|b` → `a_b` silently. Stored data today can
  never contain `|`, so `|` is a safe separator and old DBs need no migration.
- Club and student labels are both stored via `chuan_hoa_nhom_du_tru`, so set membership in
  `default_reserve_eligible_fn` needs no extra normalising. `xay_tier_rank` uses `chuan_hoa_tim_kiem` (keep it).
- `kiem_nhanh.py` default is 5 seeds: pass `--so-seed 20` for acceptance 1.
- Do not touch `compute_club_priority` signature (anti-endogeneity test guards it).
## Current state (overwrite)
- Done: planning. Lead started 2026-11-23; next: create coder/checker, GO L1.

## Sessions
| Role | Session id | Model | State |
|---|---|---|---|
| lead | session_01TGThn62kmcVTb1wTcWV1BG | claude-sonnet-5-5 | running |
| coder | session_01TGThn8yyRbdQHVrNVMixYj | claude-sonnet-5-5 | created, GO L1 sent |
| checker | session_01TGThn4sEFZK42aWUvKbj4R | claude-sonnet-5-5 | created, waiting |

## Needs Truong
- (none yet)

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Opus | Plan L1–L4, protocol A5_GIAO_THUC.md | No product code |
