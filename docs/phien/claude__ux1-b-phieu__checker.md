# Checker (UX1B) — verdicts

CHECKER REPORT L4-B | reviewed 0100cd7..0f73c43
verdict: NO BUGS (2 notes, not blocking)

Checked against "Done when" (UX1_KE_HOACH L4 as changed by §10):
- Related tests: test_ux1b_l4_bao_cao, test_gt3_phan_quyen, test_giao_dien_ux1b_vai_gv -> 34 passed.
- Invariant 1: `kiem_nhanh.py --co-so origin/main --so-seed 20` -> 7/7, 60 cases identical (diff touches only
  bao_cao_tong_hop.py, api_xuat.py, phan_quyen.py, UI/i18n; no solver/schema/CSV file).
- Invariants 2/4/7: builder is read-only (no compute_club_priority, no write to run_history, no schema/CSV change). 6: `{ok,data,errors}` kept,
  error code `xuat_chua_co_ket_qua` reused. QUYEN: in `_GIAO_VIEN` (completeness test green). One audit row: test green.
- Privacy: no student id/name/score/lottery number in HTML (test + my run on 120HS book + late-added student "Nguyễn Văn Đặng"/ZZ999: no leak).
- Own edge cases (fake data, scratchpad scripts, nothing committed):
  1. No data / no run yet -> `xuat_chua_co_ket_qua`, no file. OK.
  2. `dung_html` with club name `<b>X</b>`, class `<img src=x>`, diacritics, empty lists, capacity None -> escaped, renders. OK.
  3. Export twice to same path -> second file `f (2).html`, no overwrite. OK.
  4. Student with empty class added after run -> shown as "Chưa có {cohort_l}" row logic OK; no crash.
  5. FA on: not exercised (fa_daa config refused here: `ws_tat_che_do`); builder has no FA branch, only aggregates -> low risk.
- UI: i18n vi+en present (kiem_nhanh i18n_khoa ok), `giao_vien` reaches both buttons in ≤ 2 clicks (Chromium test green). No "In phiếu cả lớp" button. OK.

Notes (optional, not bugs):
1. After the run, if data changes (new student added), `ket_qua_cu` is returned but the HTML has no "out of date" line; cards use
   `n_students` (121) while the class table sums to 120 (students without match rows). Suggest a one-line stale warning in the HTML.
2. HTML text is built in Python with the `nhan_ws` placeholders (Vietnamese only, not `i18n`); consistent with other exports.
