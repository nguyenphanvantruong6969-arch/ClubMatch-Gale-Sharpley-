# GT1 — Per-student explanation (parent item C3)

> Task file for team GT1. Protocol: `docs/phien/GT_GIAO_THUC.md`. Branch `claude/gt1-giai-trinh`. English.
> Goal: for ANY run (default RB-DA and FA-DAA), the school can show each student, in plain words, their preferences,
> the scores/criteria that mattered, each club's capacity and cut-off, constraints, and why they got (or did not get)
> each club — on screen (admin/teacher), on a printed slip, and by self-lookup with a code.

## Facts the lead should know (verified 2026-11-15)
- Reasons exist only in FA mode: `fa_daa.ly_do_ket_qua` → table `fa_ly_do` → sentence `fa_ly_do.cau_ly_do`
  ("one place for sentences"); API `api_xuat.get_ly_do_ket_qua` returns `fa_bat False` and nothing when FA is off.
- Priority key: `rbda_priority_pipeline.compute_club_priority` (tier 1 −score then STB; tier 2 STB); soft reserves in
  `club_choice_function`; rules in `luat_xep_hieu_luc` / `tham_so_luat`; multi-session in `run_rbda_nhieu_buoi`;
  stability check `verify_stability` / `verify_stability_tuan`.
- Run record: `run_history` (seed, `luat_xep`, `buoi_da_chay`); results `match_results`; result fingerprint table
  `dau_van_tay_chay` (use it to detect "data changed after the run").
- Search: `api_quan_ly.search_students`; class column exists (item A14, `lop_hoc_sinh.py`).

## Lot L1 — Explanation engine (backend, pure + API)
- New module `giai_trinh.py` (pure functions, no DB): `giai_trinh_mot_hoc_sinh(du_lieu_run, student_id) -> dict`.
  Per session (`buoi`): ordered preference list; for each club: name, selective or not, the student's own score (if
  any), capacity, reserve seats, seats filled, cut-off (lowest admitted: its score if tier 1 decided it, otherwise the
  text "bốc thăm"), the student's own STB number only, and an outcome code:
  `ACCEPTED`, `HIGHER_CHOICE_ACCEPTED` (not considered: got a higher choice), `FULL_SCORE` (full; below cut score),
  `FULL_LOTTERY` (full; tie-break by lottery), `RESERVED` (seats reserved for a priority group), `NOT_TESTED`
  (selective club, student has no score), `UNASSIGNED` summary when nothing fits.
- FA on → reuse the `fa_ly_do` rows of that run (do not recompute). FA off → rebuild the run's inputs from the DB as
  the pipeline reads them (same `rules` stored in `run_history.luat_xep`, same locked STB) and derive codes from
  `compute_club_priority` / `club_choice_function` outputs. Never change any run code path.
- Sentences: add `cau_ly_do_rbda(dong, ten_clb)` to `fa_ly_do.py` (keep it the only sentence source; vi + en via
  `i18n` keys if the module already supports lang, else Vietnamese like `cau_ly_do`).
- Stale guard: if the current data fingerprint ≠ the run's, return the explanation plus a flag `du_lieu_da_doi True`
  (UI shows a warning); never silently explain with new data.
- API (in `api_bao_cao.py` or `api_xuat.py` mixin): `get_giai_trinh_hoc_sinh(student_id, run_id=None)` →
  `{ok, data, errors}`; errors `gt1_khong_co_hoc_sinh`, `gt1_chua_chay` (add to `i18n_errors.py`, run `tao_i18n_js.py`).
- **Done when** (`tests/test_gt1_giai_trinh.py`): (a) on 3 simulated datasets × 5 seeds, FA off: for every student,
  every club ranked above the assigned one has code FULL_* or RESERVED or NOT_TESTED, and the student's priority is
  below that club's last admitted (consistent with `verify_stability` = no justified envy); (b) FA on: codes equal the
  stored `fa_ly_do` reasons; (c) privacy: the JSON of one student contains no other student_id or name; (d) data edited
  after the run → `du_lieu_da_doi True`; (e) `kiem_nhanh.py` identical (no run path touched).

## Lot L2 — Lookup screen for admin / teacher
- In the "results" tab, a panel "Tra cứu một học sinh": search box (reuse `search_students`, filter by class), then a
  card per session: table of preferences (rank, club, own score, capacity / filled, cut-off, outcome sentence), the
  assigned club highlighted, waitlist position if any, the run date + seed + criteria in words, stale warning.
- New file `js/14_giai_trinh.js` (add to `js/_danh_sach.txt`), one `<!-- GT1 -->` block in `index.html`, i18n vi/en.
- **Done when** (`tests/test_giao_dien_gt1_tra_cuu.py`, Chromium): search by name with/without diacritics, card shows
  correct club and sentence for an accepted and a rejected student; no other student's name in the card DOM; FA on/off.

## Lot L3 — Printable slip
- API `export_phieu_giai_trinh(output_path="", student_ids=None, lop=None)`: one self-contained HTML (print CSS,
  `page-break-after` per student; no external assets), one page per student: school/kiosk title, student id, name,
  class, per-session table as in L2, sentence, how to ask for review (text: "liên hệ giáo viên phụ trách trong N ngày" —
  use the appeal window from rules `fa_khieu_nai_so_ngay` if present, else omit the number), space for the lookup code
  (filled by L4). Button in the L2 panel: "In phiếu cho học sinh này" and "In phiếu cả lớp".
- **Done when** (`tests/test_gt1_phieu.py`): one page per selected student; each page has only its student's id/name
  (parse the HTML per page); empty class → error `gt1_khong_co_hoc_sinh`; Vietnamese diacritics intact.

## Lot L4 — Lookup codes + student self-lookup mode
- Table `ma_tra_cuu(student_id TEXT PRIMARY KEY, ma TEXT NOT NULL, tao_luc TEXT NOT NULL)` (insert in the schema
  after the `giu_cho` block; `CREATE TABLE IF NOT EXISTS`). Codes: 8 chars from `ABCDEFGHJKMNPQRSTUVWXYZ23456789`
  via `secrets` (never `random`/`hash()`/the STB seed — unrelated to the lottery, invariant 3 untouched).
- API: `tao_ma_tra_cuu(chi_hs_chua_co=True)` (returns counts), `tao_lai_ma_tra_cuu(student_id)`,
  `export_ma_tra_cuu_csv(output_path="", lop=None)` (student_id, name, class, code — for mail merge),
  `tra_cuu_hoc_sinh(student_id, ma)` → the L1 explanation of that student only. Compare with `hmac.compare_digest`;
  5 wrong tries for one student_id → locked 60 s (in memory); error codes `gt1_ma_sai`, `gt1_tam_khoa`.
- Slip (L3) prints the code when one exists.
- UI "Chế độ học sinh tra cứu": full-screen overlay started from the L2 panel; two inputs + button; shows the same card
  as L2 without admin controls; auto-clears after 60 s idle; exit button with confirm (integration I2 puts it behind
  admin login when accounts are ON).
- **Done when** (`tests/test_gt1_ma_tra_cuu.py`, `tests/test_giao_dien_gt1_hoc_sinh.py`): codes unique, right alphabet,
  stable unless regenerated; wrong code → no data; 6th try within 60 s → `gt1_tam_khoa`; right code → only that
  student's data; generating codes leaves `match_results`, `stb_lock`, `run_history` unchanged; `kiem_nhanh.py` identical.

## Out of scope (→ "Needs Truong" if it comes up)
Online/remote lookup, email sending, showing other students' scores or lottery numbers, any change to how results
are computed, appeals workflow changes (already exists).
