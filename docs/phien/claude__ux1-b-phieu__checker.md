# Checker (UX1B) — verdicts (newest first)

CHECKER REPORT R1 fix2 | reviewed 0185d9d..f58df43
verdict: NO BUGS (1 note)
- My repro (T cap 2, r reserved 3 pts, t 8, x 7): all three rows now show 8 điểm; x's SVG has 7 below the red line; sentence says "điểm chuẩn 8, em 7" -> column, SVG and sentence agree.
  Rule is the stored REJECTED fa_ly_do rows of the club (one worst-key member): RESERVED -> "Chỗ dành riêng", else cut_score, nobody rejected -> "Còn chỗ" (not full) or no value (exactly full).
- Coder's tier-2 claim is TRUE for Tuyển chọn: fa_daa.py (step 2) removes every student with no score (NOT_ATTEMPTED) or score < diem_san (BELOW_PASS) from the list BEFORE the DA run, also when diem_san is set,
  so a Tuyển chọn club has no untested/below-san members. Verified on a 4-student run (diem_san 5): a(9) accepted, b(6) SCORE rejected with 9, c(2) BELOW_PASS, e(untested) NOT_ATTEMPTED; no member without a score.
- 91 tests passed (l7_phieu incl. 3 new fix2 tests: reserved lowers nothing, all-reserved -> giu_cho, nobody rejected -> con_cho; l4_bao_cao, ux1b_phieu, gt_tich_hop, gt1_giai_trinh, gt4_cau_giai_trinh, gt1_phieu, gt1_tra_cuu); ruff clean.
Note: a Giới hạn club that still holds leftover test scores (warning fa_diem_bo_qua) counts as `chon_loc`, so "Điểm các CLB em đã thi" lists that score with a bar and no cut-off although FA ignores it for that club
 (and the lottery row reads "Chọn ngẫu nhiên khi bằng điểm"). No wrong number is shown; consider hiding scores of Giới hạn clubs on the slip (pre-existing since L7).

CHECKER REPORT R1 | reviewed 775f669..0185d9d
verdict: 1 BUG
1. giai_trinh.py:_chuan_clb_fa (used by _lua_chon_fa and _diem_da_thi) | repro (fake data, FA on): club T "Tuyển chọn" cap 2, diem_san 0; students r (score 3,
   holds a reserved seat via giu_cho), t (8), x (7), all rank T first, medal 60; run seed 3 -> r, t accepted, x rejected (reason SCORE).
   x's row: "Mức vào được 3 điểm" + SVG with x's 7 ABOVE the red line, but the same row's sentence says "điểm chuẩn 8, em 7" (fa_ly_do cut_score) | expected: 8.
   Cause: `min(accepted scores)` includes the reserved student. The FA key is (-giữ chỗ, -điểm, -huy chương, stb) (fa_daa.py ~l.545), so reserved members rank
   first and the real cut is the score of the worst-KEY member (= fa_daa cut_score = 8). Also misleading when untested (tier-2, diem 0) members are accepted:
   min over tested members then shows a cut no tested student faced. Fix: for a REJECTED row with r["cut_score"] use it (same number as the sentence); for ACCEPTED/untested
   rows take min only over accepted members WITHOUT a reserved seat (b has the reserve info as `reserve_fn` in fa_daa; pass or precompute it), and if all accepted are
   reserved / any accepted is untested show "Còn chỗ"/"Chỗ dành riêng" instead of a number. Compare the non-FA slip: `_diem_da_thi` uses `_nguoi_nhan_cuoi` (last by rank), not min.
   The R1 test uses the sample book where no reserve exists, so it does not catch this; add the case above.
Checked OK:
 - Item 2: MEDAL "Vì sao" is ONE sentence naming the club and own medal; 3 edited tests are tightened, not weakened (exact equality of the sentence, club name added,
   new assert on diem_chuan_loai "huy_chuong" = "Bạc"; "bằng điểm" still absent at untested clubs, still present at tested). "Huy chương X" as mức vào được on untested clubs = last accepted's medal
   (club-level, no name/id) -> true under key (1, -medal, stb).
 - Item 3: report shows "Thứ 2" (no "thu_"), capitalised headings ("Học sinh chưa có câu lạc bộ theo lớp"), column "Số lượt xếp (học sinh × buổi)"; numbers = summary API
   (120HS book: 87+40+11+... = tong_da_xep 138 > 120 students because 3 sessions each; test asserts sum ≤ tong_da_xep).
 - Privacy: only club-level numbers; 84 tests passed (l7, l4_bao_cao, ux1b_phieu/vai_gv, gt_tich_hop, gt1_giai_trinh, gt4_cau_giai_trinh, gt1_phieu); ruff clean.

CHECKER REPORT L8-B | reviewed 90ee9aa..b960b60
verdict: NO BUGS (3 minor notes)
- Tests: test_gt3_tai_lieu + test_gt_tich_hop (incl. test_i4_* byte test) + test_a13_12_tai_lieu -> 44 passed. Docs diff is text/tables/PNG/PDF only (no product code).
- Docs match the real UI: block "Theo lớp và báo cáo", buttons "Xuất theo lớp" / "Báo cáo tổng hợp", fold "Mã tra cứu…" (quản trị), group "Cài đặt và quản lý" in
  HUONG_DAN_SU_DUNG.md, HUONG_DAN_CHAY.md, KICH_BAN_DEMO.md; no stale "nhóm Cài đặt" left in the md files I grepped. Code-map rows added (bao_cao_tong_hop.py, js/19_ux1b_gv.js, _huy_chuong_ca_so_sai).
- anh/phieu_mau.pdf (4 pages, 2 slips: HS001, HS004) + anh/04_phieu.png: each slip carries only its own student's data (id appears once per slip, no other id); no seed / "số khoá";
  no "Huy chương" column or legend (non-FA sample); summary line, "Điểm các CLB em đã thi" with SVG bar only for tested clubs, "Em nên làm gì tiếp" box present; reason sentences say "bốc thăm" in words only.
- After table honest: slip = 5 clicks, target 4 marked "chưa" (needs XP1 PDF button at I3); Báo cáo tổng hợp 1 click (HTML, PDF at I3), labelled "đo", data marked MÔ PHỎNG, hạt giống 42; no figure presented as a real survey.
Notes: (a) anh/03_tra_cuu_HS004.png is the STAFF card (shows "số khoá bốc thăm: 42" and "Học sinh" voice) — correct for staff but it is not referenced by any md, so keep it out of student-facing docs;
 (b) on screen the next-steps box title is "Việc tiếp theo" while the slip says "Em nên làm gì tiếp" (L7 item 4 / "same wording"); (c) a missing score shows "Không có" on screen but "—" on the slip. None blocks.

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
