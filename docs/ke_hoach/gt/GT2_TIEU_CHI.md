# GT2 — Bounded criteria, trial runs, comparison (parent A1, Z7-lite)

> Task file for team GT2. Protocol: `docs/phien/GT_GIAO_THUC.md`. Branch `claude/gt2-tieu-chi`. English.
> Goal: an authorised admin sees the allocation criteria as a plain ordered list, changes them only within the
> approved set (D-GT1: lexicographic, no weights, no sensitive data), runs labelled TRIAL allocations that never touch
> official results, and compares any two runs side by side (who changes, per-club and per-group effects).

## Facts the lead should know (verified 2026-11-15)
- The bounded set already exists: `rbda_priority_pipeline.LUAT_XEP_MAC_DINH` = `priority` (`score` | `score+tier` |
  `tier`), `tier_mode` (`reserve` | `strict`), `score_scope` (`per_slot` | `per_person`), `tiers` (ordered groups),
  `wharton`, `fa_daa`. Normalised by `luat_xep_cua`, `luat_xep_hieu_luc`; to params by `tham_so_luat`; stored per run
  as `run_history.luat_xep` (`luat_xep_de_ghi`; NULL = school default). Validated/saved by `cau_hinh_ws._chuan_hoa`,
  `ghi_cau_hinh`; UI checkboxes in `js/075_workspace.js` (`update_workspace_config`).
- Run entry: `api.PipelineAPI.run_pipeline` → `_run_pipeline_da_khoa` (write lock `_khoa_ghi`; backup → validate →
  lock STB → solve → verify → one transaction → export).
- Readers of `run_history` that mean "latest/official run" (ALL must ignore trial rows): `api.py` (2 × `MAX(run_id)`,
  one `ORDER BY run_id DESC LIMIT ?`), `api_xuat.py` (`ORDER BY run_id DESC`), `fa_sau_xep.py`, `api_sau_xep.py`,
  `rbda_priority_pipeline.py` (`COUNT(*)`). Re-grep `run_history` and `MAX(run_id)` before coding.

## Lot L1 — Criteria in plain words + closed allow-list
- New module `tieu_chi.py` (pure): `mo_ta_tieu_chi(rules, lang="vi") -> list[dict]` — the effective order of criteria
  for tier 1 and tier 2, e.g. `1. Điểm bài thi của CLB (cao trước) 2. Nhóm ưu tiên – giữ suất riêng 3. Số bốc thăm`,
  plus which keys are inactive and why (mirror `luat_xep_hieu_luc`). `cac_lua_chon_hop_le()` returns the allowed values
  per key (single source for the UI).
- API `get_tieu_chi()` → description of the saved rules + allowed options. UI file `js/15_tieu_chi.js`, panel
  "Tiêu chí xếp" (in the admin tab, `<!-- GT2 -->` block): ordered list, options as radio/select limited to the allowed
  values, a fixed note "Phần mềm không dùng thứ hạng nguyện vọng, kết quả kỳ trước hay hoàn cảnh cá nhân để xếp".
  Saving still goes through `update_workspace_config` (no new save path).
- **Done when** (`tests/test_gt2_tieu_chi.py`, `tests/test_giao_dien_gt2_tieu_chi.py`): descriptions correct for every
  allowed combination (enumerate them); `cau_hinh_ws` rejects any unknown `rules` key or value (add the check only if
  missing, error `gt2_tieu_chi_khong_hop_le`); a test asserts the allowed key set equals `LUAT_XEP_MAC_DINH` keys
  plus the existing non-priority keys (so a new criterion cannot sneak in silently); `kiem_nhanh.py` identical.

## Lot L2 — Trial runs (labelled, append-only)
- Schema (D-GT8): in `di_tru_schema`, idempotent `ALTER TABLE run_history ADD COLUMN loai_chay TEXT` (NULL =
  official; backup first, like the existing migrations); table `ket_qua_thu(run_id INTEGER NOT NULL, buoi TEXT,
  student_id TEXT NOT NULL, club_id TEXT, rank_in_list INTEGER)` inserted after the `fa_phan_hoi` block.
- API `run_thu(rules_thu: dict, chi_buoi=None)`: validate `rules_thu` with the same normaliser as saving; require an
  official run with a locked STB (else `gt2_chua_co_lan_chinh_thuc`); never redraw STB; reuse the solver path of
  `_run_pipeline_da_khoa` with rules overridden (factor out a helper only if needed; the official path must stay
  byte-identical); same order backup → validate → solve → verify → ONE transaction; write `run_history` row with
  `loai_chay='thu'` and `luat_xep`, rows into `ket_qua_thu`. NEVER write `match_results`, `ket_qua_truoc`,
  `dau_van_tay_chay`, `stb_lock`, `fa_*`, exports. FA rules in a trial: support if the FA solver accepts a rules
  override without touching `fa_*` tables; otherwise refuse with `gt2_thu_chua_ho_tro_fa` and log under Needs Truong.
- Every reader in "Facts" filters `loai_chay IS NULL` (or uses a shared helper `run_chinh_thuc_moi_nhat(cur)`).
- **Done when** (`tests/test_gt2_chay_thu.py`): (a) trial with rules == saved rules gives `ket_qua_thu` equal to the
  official `match_results` (3 datasets × 5 seeds); (b) after a trial with different rules, every existing `get_*` /
  export output used by the results, admin and after-run tabs is identical to before (snapshot); (c) `run_history`
  gained exactly one row, older rows unchanged (invariant 4); (d) failure mid-trial rolls back; (e) old DB without the
  column migrates twice without error; (f) `kiem_nhanh.py` identical.

## Lot L3 — Compare two runs
- Pure `so_sanh_lan_chay(a, b) -> dict` in `tieu_chi.py`; API `so_sanh_lan_chay(run_a, run_b=None)` (default b =
  latest official) and `export_so_sanh_html(output_path, run_a, run_b)` + CSV of changed students.
  Content: criteria A vs B in words (from L1); totals (assigned, unassigned, % 1st choice, % top 3, mean rank);
  per club (capacity, filled, cut-off A/B); per priority group from `tiers` and per class (assigned %, 1st-choice %) —
  this is the "fairness trade-off" view the jury asked for; list of students whose club changed (id, name, class,
  A → B). Labels say "chạy thử" vs "chính thức" everywhere.
- UI section "Thử cấu hình" in `js/15_tieu_chi.js`: edit criteria (L1 controls) → "Chạy thử" → comparison table vs
  official; list of past trials (date, criteria summary) to re-open or compare two trials.
- **Done when** (`tests/test_gt2_so_sanh.py`, `tests/test_giao_dien_gt2_thu.py`): numbers hand-checked on a 10-student
  fixture; same run vs itself → zero changes; changed-student list equals a direct diff; Chromium test runs a trial
  and sees the table; HTML export opens offline.

## Lot L4 — Adopt a trial's criteria
- Button "Dùng tiêu chí này cho lần chạy chính thức": saves the trial's `luat_xep` through `update_workspace_config`
  after a confirm dialog that shows the L1 description; then tells the admin to run officially. It never copies trial
  results into `match_results`.
- **Done when** (`tests/test_gt2_ap_dung.py`): saved rules equal the trial's; no result table changed until an official
  run; next official run's `run_history.luat_xep` equals the trial's.

## Out of scope (→ "Needs Truong")
Weighted scores, new criteria fields, per-club different rules, deleting trial rows, publishing trial results.
