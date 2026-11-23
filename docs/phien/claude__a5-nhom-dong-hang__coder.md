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
Not walked in full: `soat-ma` four tiers (only `kiem_nhanh`).
