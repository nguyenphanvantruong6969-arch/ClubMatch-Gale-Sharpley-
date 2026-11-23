# A5 coder notes

## L2 — `git grep -n reserve_group -- '*.py' ':!tests'`: club-vs-student label comparisons
Fixed (`|` aware):
- `api_bao_cao.py` get_suat_du_tru (`instr`, not `LIKE`)
- `api.py` data-health checks 4 (student label not in any club) and 6 (club label no student) — `instr`/`NOT EXISTS`
- `api_nhap.py` `_soat_nhom_du_tru_la` (split club labels), club write path (`chuan_hoa_o_nhom_clb`)
- `api_quan_ly.py` `create_or_update_club`, `list_reserve_groups_in_use`, `set_student_reserve_group`
Checked, no change needed:
- `muc_tieu.py` `de_xuat_cho_giu`, `nhan_dien_muc_tieu` (a club `a|b` != any single key -> `clb_ghi_de` / `tuy_chinh`; locked by tests)
- `api_muc_tieu.py` (writes a single label), `api_xuat.py` (display/export only, no equality), `giai_trinh.py` (calls pipeline), `fa_daa.py` (untouched)
- `rbda_priority_pipeline.py` SQL loaders (`COALESCE(reserve_group,'')`) pass the raw cell through.
Behaviour note: a student cell with `|` in a CSV import skips that student entirely (not created, no prefs), with warning `a5_nhom_hs_co_gach`.

## L2 — soat-ma walk (report only; no blocking findings)
- Tier 1: `compute_club_priority` / `club_choice_function` untouched (no diff lines mention them) → invariants 2, 8 unaffected; L1 random test covers multi-label choice function.
- Tier 2: pipeline order / transaction / run_history not touched (inv. 4, 5); errors keep `{code, params}` and `a5_nhom_hs_co_gach` is in `i18n_errors.py` + regenerated `i18n_loi.js` (inv. 6); no schema or column change (inv. 7); SQL parameterised, `instr` only, no `LIKE`; no new write path to locked data (same functions, same lock behaviour).
- Tier 4 mutation tests (6): `>0`→`>=0` in report SQL; `instr` prefix in api.py health SQL; student-`|` rejection off; tiers cross-rank check off; substring match instead of set in `default_reserve_eligible_fn` → all caught (the substring one only after adding `test_reserve_khop_nhan_nguyen_khong_khop_chuoi_con`, a WEAK TEST I found and fixed). Survivor: `chuan_hoa_o_nhom_clb` fast path `if False` = equivalent mutant (general path gives the same string) — fine.
- Known limitation: a student-cell `|` in a CSV import skips the whole student (lines 'nothing written'); a teacher sees a warning, not an error.
- Out of scope noted: none. UI tier skipped (no UI changes in L2).

## L2 FIX1 — student-label write paths re-grep (`UPDATE students SET reserve_group`, `INSERT INTO students`, `chuan_hoa_nhom_du_tru`)
- `api_nhap._ghi_nhom_du_tru` (both import loops): guarded (check before student creation).
- `api_quan_ly.set_student_reserve_group`: guarded. `bulk_set_reserve_group`: NOW guarded (new code `a5_nhom_hs_co_gach_hang_loat`, no student_id), rejects before any write.
- `api_nhap` ~L550 `SET reserve_group = NULL`, `api_nhap._tao_hoac_bo_sung_hoc_sinh`, `api_quan_ly.create_or_update_student`, `rbda_priority_pipeline` demo seeder: write NULL / fixed labels only, no user cell.
- `api_nhap` ~L335 `_soat_...` only reads the normalised cell.
- Sổ nhập student sheet and student CSV both go through `_ghi_nhom_du_tru` loops.
- Also found: `tests/test_gt3_phan_quyen.py` requires every public method in `phan_quyen.py`; added `chuan_hoa_o_nhom_clb`, `o_nhom_hs_co_gach` to `_GIAO_VIEN` (phan_quyen.py) and `_KHONG_GHI` (nhat_ky.py) next to `chuan_hoa_nhom_du_tru`.
