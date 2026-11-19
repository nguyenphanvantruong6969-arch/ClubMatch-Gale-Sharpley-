# Checker (UX1B) — verdicts (newest first)

CHECKER REPORT L5c fix1 | reviewed 276616b..f3ff065
verdict: NO BUGS
- Bug 1 fixed: (a) a book where no club name is available (fa_huy_chuong_trung_gia_tri) now uses `ux1b_huy_chuong_gop_khong_clb` (vi+en, no "ví dụ ở: "); test r1c green.
  (b) merge only when whole book wrong, via the single `QuanLyMixin._huy_chuong_ca_so_sai(n_sai, n_hs)` = n_sai > 0 and n_hs > 0 and n_sai*2 >= n_hs,
  used by get_data_health_report AND get_san_sang_huy_chuong (`huy_chuong_ca_so`) -> JS no longer recomputes. Boundary checked by hand:
  (0,10) F, (1,10) F, (4,10) F, (5,10) T (exactly half), (6,10) T, (1,2) T, (1,3) F, (0,0) F, (3,0) F. 4 students: 1 wrong -> per-line, no merge (both APIs agree);
  2 wrong (half) -> merge (both agree); 3 wrong -> merge. Health and Cài đặt always agree. Few-wrong path: per-student line with id kept, Việc tiếp theo does not jump
  to Cài đặt, type buttons still usable (test r1b).
- n_high / n_warnings unchanged in the API (4-student runs: n_high = n_warnings = number of wrong students whether merged or not; only the on-screen count merges).
- Rec 5 decision accepted: default Excel export carries "Điểm chuẩn" and "Dấu vết (kỹ thuật)" (seed + lottery numbers, api_xuat.py), so the red privacy line
  must stay visible; moved back below the export block; group rename kept (test r5 updated to assert visible, not weakened in the opposite direction).
- Tests: 165 passed (l5c, cai_dat, dieu_huong, tiep_theo, ws_nhan incl. new code, van_phong_tu_nhien, gt4_nhat_ky_doc, gt3_tai_lieu, ux_xuat, xuat_du_lieu, gt3_phan_quyen);
  ruff clean; kiem_nhanh --co-so origin/main --so-seed 20 -> 7/7.
- Note (not a bug): at exactly half the text says "Gần như cả sổ"; acceptable.

CHECKER REPORT L5c | reviewed 78e3bff..276616b
verdict: 1 BUG (+3 notes)
1. api.py:get_data_health_report (gop_huy_chuong) + i18n_errors.py:ux1b_huy_chuong_gop + js/02_van_hanh.js:loadHealthReport |
   repro: FA on, 2 students, clubs G,H (Giới hạn); insert wharton_bids s1 G=60,H=60 (same value twice; only reachable through a book
   import, submit_huy_chuong refuses it) -> report shows ONE merged line "1 học sinh chưa có huy chương hợp lệ (ví dụ ở: ). Sổ đang nạp
   mang điểm quyết tâm hoặc huy chương đặt sai chỗ, không phải lỗi của từng học sinh ... quay lại Chia 100 điểm" + button "Mở Cài đặt",
   and the "Việc tiếp theo" bar jumps to Settings | expected: (a) no empty "ví dụ ở: " — `fa_huy_chuong_trung_gia_tri` has no club_id, so
   `gop.clb` is [] and `n_clb` 0; (b) the merge must not claim "not each student's fault" when only a few students are affected; the
   original per-student lines (with student_id) are the only way to find them. Fix: merge only when the problem is book-wide (same rule the
   code already uses in ux1aVeSanSang: n_em*2 >= n_students) and keep the individual lines otherwise; skip the "ví dụ ở" part when clb is empty.
   (Verified on 120HS book with FA on: 120 students, 9 clubs, API n_high stays 686, merge correct there.)
Checked OK:
 - Tests: 195 passed (ux1b_l5c, ux1_cai_dat, ux1_dieu_huong, van_phong_tu_nhien, ws_nhan, gt4_nhat_ky_doc, gt3_tai_lieu, the 4 hoc_sinh/tieu_chi UI files,
   ux1b_phieu/vai_gv/tiep_theo, gt1_tra_cuu, gt3_phan_quyen). kiem_nhanh --co-so origin/main --so-seed 20 -> 7/7 (60 ca trùng khít).
 - Test edits legit: the cai_dat test was SPLIT, not weakened — old end assertions (wrong medals: "không phải huy chương" text, no "Sẵn sàng",
   run blocked) moved to the new whole-book test (text "Gần như cả sổ", no type buttons, run still blocked); the old test now deletes wharton_bids
   to simulate a clean book and ends on "Sẵn sàng". mo_gap_ma() only opens #gtMaFold before clicking (same buttons, same assertions).
   ws_nhan: only adds the new error code to the list.
 - No element id/data-tab renamed (all old ids kept; #gtBuocHuongDan moved inside the fold). #gtMaFold is data-quyen="quan_tri", but every
   button inside already was quan_tri-only, so giao_vien loses nothing (vai_gv tests green).
 - New texts use {person_l}/{person_pl}/{slot_l}; vi + en present (kiem_nhanh i18n 7/7). Health API n_high / n_warnings unchanged; only the display count is merged.
 - Group rename "Cài đặt và quản lý": gt3_tai_lieu green.
Notes: (a) the minority-wrong path (message "không phải huy chương" for < half the book) lost its Chromium assertion in the split; consider keeping one test.
 (b) the red privacy line "Tệp xuất có điểm chấm..." now only shows inside "Tuỳ chọn khác"; fine if the default Excel export carries no scores/lottery — please confirm.
 (c) "Điểm danh 3 buổi đầu" matches fa_sau_xep (3 buổi đầu).

CHECKER REPORT L7 fix2 | reviewed 79c8e45..fc5e9fc
verdict: NO BUGS
- Selector-only, not weakened: gt1_tra_cuu `td.nth(5)` -> `td.last` = the "Vì sao" cell in both modes (non-FA 6 cols, FA 7 cols), same >10-char assertion;
  gt4_cau_giai_trinh `o[4]` -> `o[-2]` = "Mức vào được" in both modes (non-FA index 4, FA index 5), same equality "Chỗ dành riêng". No assertion removed or loosened.
- Ran 88 tests (gt1_tra_cuu FA on+off, gt4_cau_giai_trinh, ux1b_l7_phieu, giao_dien_ux1b_phieu, gt1_hoc_sinh, gt4_giai_trinh, gt1_phieu, gt1_giai_trinh, gt_tich_hop) -> 88 passed.
- Other `td.nth(` users in tests/ (diem_chuan, a14_lop) do not touch the giải trình table; both files 34 passed.

CHECKER REPORT L7 fix1 | reviewed 823e560..79c8e45
verdict: 1 BUG (stale test selector, regression of L7 itself)
1. tests/test_giao_dien_gt1_tra_cuu.py::test_the_hien_dung_cho_em_duoc_xep_va_em_bi_tu_choi[True] (FA on), line ~91
   `hang.locator("td").nth(5)` | repro: run that test -> AssertionError: 'Không có' (8 chars) > 10 | cause: L7 adds the "Huy chương" column
   after "CLB" in FA mode, so "Vì sao" moved from td 5 to td 6; td 5 is now "Mức vào được" | expected: green; fix = change the selector
   (e.g. last `td`, or `nth(6 if fa else 5)`), never skip. Not caught earlier: file is not in the L7 related list; grep tests/ for
   `locator("td").nth(` / `gt-duoc-xep td` over FA-mode student-card tests for other index users (the 8 other files I ran pass).
Bug 1 of the previous round: FIXED (U row now "Các bạn đặt huy chương cao hơn ở CLB U được xét trước. Em chưa đặt ..."; tested-club row still says "bằng điểm").
seed/stb: student response (tra_cuu_hoc_sinh) has no "seed"/"stb" anywhere; js/14_giai_trinh.js never reads r.seed for a student (uses
 ux1b_gt_lan_chay_hs) and never reads stb_em -> no "undefined" text, no JS error (gt1_hoc_sinh / gt1_tra_cuu / gt4 Chromium tests green except the one above).
 Staff path keeps seed + stb_em (new test). Ran 92 tests: 91 passed, 1 failed (above).

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
