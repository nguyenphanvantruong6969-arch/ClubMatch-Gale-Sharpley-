# Checker (UX1B) — verdicts (newest first)

CHECKER REPORT L7 | reviewed 11b6ce4..823e560
verdict: 1 BUG (minor wording) + 3 notes
1. fa_ly_do.py:cau_ly_do (MEDAL) + giai_trinh.py:_cau_huy_chuong | repro: FA on; clubs T (TUYEN_CHON, tested), U (GIOI_HAN, no test), F (TU_DO);
   s3/s4 prefs [T,U,F], s1 Vàng on U -> s3's U row reads "Em và các bạn bằng điểm; các bạn có huy chương cao hơn ở CLB U được xét trước.
   Em chưa đặt huy chương ở CLB này; các bạn đặt Vàng được xét trước." | expected: no "bằng điểm" where the club has no test / the student
   is tier 2 (khoa_uu_tien_wharton: tier2 key = (1, -medal, stb), no score step). Fix: when the row has no score (diem_em None / club not chon_loc),
   use "Các bạn đặt huy chương cao hơn được xét trước." (+ the new sentence). Legend itself is TRUE for tested and untested clubs
   ("khi bằng nhau ở các bước trước … chưa đặt thì xét sau … vẫn bằng thì bốc thăm") because it does not name the score step.
   The coder's chain "giữ chỗ > điểm > huy chương > bốc thăm" holds only for tested clubs (tier 1); at an untested club it is giữ chỗ > huy chương > bốc thăm.
Checked OK: tests 84 passed (test_ux1b_l7_phieu, l4_bao_cao, giao_dien_ux1b_phieu, gt_tich_hop incl. CA_MAU byte test, gt1_giai_trinh, gt3_phan_quyen).
 - Medal col only when fa_bat; own medals only (huy_chuong read per student; my 4-student FA run: no other id/medal in the card data).
 - SVG only for clubs the student tested (s3/s4 no test -> none, s1/s2 one each); slip has no seed text; "Chọn ngẫu nhiên khi bằng điểm" used.
 - Non-FA slip: no medal column/legend (tests). MEDAL sentence uses club's last-accepted medal (cut_medal), no names. L4-B stale line present (test_ux1b_l4_bao_cao).
Notes: (a) API JSON of get_giai_trinh_hoc_sinh still carries run.seed; only display hidden for students — fine if student path (tra_cuu_hoc_sinh) also
 omits it (not re-verified). (b) `tinh_nang` reads CURRENT rules, not rules at run time; harmless. (c) unplaced-everywhere + features on: only via unit tests
 (my scenario placed the student in a TU_DO club).

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
