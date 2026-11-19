# Checker verdicts: claude/ux1-tich-hop (English, <= 30 lines)

## CHECKER REPORT I1 | reviewed 90a4da1..dac41dd
verdict: NO BUGS

Done when (UX1_TICH_HOP_GIAO_THUC §2 I1):
- I1 test set (tests/test_giao_dien_ux1_*, test_ux1_*, test_khoi_dong_backend, test_ws_nhan, test_ws_nhan_giao_dien,
  test_van_phong_tu_nhien, test_gt4_nhat_ky_doc, test_gt_tich_hop): 159 passed, 0 failed (120 s).
- `kiem_nhanh.py --co-so origin/main --so-seed 20`: 7/7 DAT (60 cases = 3 datasets x 20 seeds identical).

Invariants:
- 1 OK (kiem_nhanh above). 2 OK: diff does not touch compute_club_priority or any priority input.
- 4 OK: kiem_nhanh `khong_sua_nhat_ky` DAT; no UPDATE/DELETE on run_history in diff.
- 6 OK: new errors keep {ok,data,errors}; codes (so_nhap_canh_bao_huy_chuong_che_do_tat, fa_loai_sai, club_not_found,
  error_saving_club) are in i18n_errors.py; kiem_nhanh `ma_loi_js` + `i18n_loi_khop` DAT.
- 7 OK: no schema or CSV change; only xlsx sample/reader and one club column write via existing fa_daa.ghi_thuoc_tinh_clb.

Privacy / roles:
- phan_quyen.QUYEN: `dat_loai_clb` = QUAN_TRI (writes), `get_san_sang_huy_chuong` = GIAO_VIEN (read only).
  Its payload has club fields + counts + one sample student_id; no scores, no names.
- UI: Cai dat panel, "Viec tiep theo", after-run panel all carry data-quyen="quan_tri"; style.css hides them under
  body[data-vai="giao_vien"].

Own edge cases (scratchpad script, fake data, all passed):
1. Empty workspace: get_san_sang_huy_chuong ok, san_sang False, no clubs.
2. dat_loai_clb: "Tu do"/"tu do"/"TU_DO"/"Gioi han" accepted; unknown club -> club_not_found; "bay_ba", None, "" ->
   fa_loai_sai; diem_san -5 / 99999 / "abc" -> fa_diem_san_sai; nothing written on failure.
3. dat_loai_clb after a finished run: get_match_results and get_run_history byte-identical before/after.
4. chuan_hoa_chu_huy_chuong: Vang/BAC/dong/gold/Silver/BRONZE (any case, diacritics) -> 60/30/10; "Kim cuong",
   "Vang Bac", empty, None left unchanged (later reported as fa_huy_chuong_gia_tri_sai).

Observations (not bugs):
- health_oversubscribed* severity changed info -> medium and texts shortened; tests updated by A. Teachers will now see
  it as a stronger warning. Worth a look in I4 review.
- dat_loai_clb after a run does not mark results stale (same as other club edits before); affects next run only.

## CHECKER REPORT I2 | reviewed 8f37d9d..9a4faca
verdict: NO BUGS

Done when (§2 I2): XP1 + I1 sets, pypdf + reportlab installed, RBDA_TEST_CHROMIUM=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome:
246 passed, 0 skipped, 0 failed (tests/test_xp1_*, test_giao_dien_xp1_*, test_ux1i_*, I1 set, test_gt4_cau_giai_trinh).
`kiem_nhanh.py --co-so origin/main --so-seed 20` = 7/7 (60 cases identical).

Lead's points:
(a) Edited tests: test_giao_dien_xp1_xuat_pdf.py = pure retarget #xuatPdfMenu -> #xuatMenu, label "Xuất PDF…" -> "Xuất…";
    all assertions kept (3 items, select, close-after-click, giao_vien hidden). test_giao_dien_ux1_ket_qua.py: old
    `#xuatMenu is_hidden` (medals off) replaced by "menu visible" + the 4 medal-only items still hidden when opened -> same
    intent kept, nothing dropped; new test_ux1i_i2_xp1_trong_menu.py covers the medals-on side. Other test edits are
    benign: gt4 column index o[4]->o[5] (new Loại CLB column), "PDF" added to acronym allow-list, "xp1_" i18n prefix.
(b) "Lưu PDF": search -> choose -> Lưu PDF = 3 clicks from Results tab (test asserts <= 3; I2 test <= 4). My own run:
    single-student PDF has that student's id/name only (no other id as a token, no other name), 1 page, has "Loại CLB".
(c) phan_quyen: export_phieu_giai_trinh_pdf + export_danh_sach_pdf = QUAN_TRI; giao_vien gets gt3_khong_du_quyen (tested).
    #xuatMenu and #btnGtPdfMot carry data-quyen=quan_tri (hidden for giao_vien). Medal-only items stay hidden when off.
(d) Slip PDF and HTML both show "Loại CLB" (— when the club has no type).
Invariants: 1 ok; 2 ok (loai only displayed, algorithm does not read it); 4 ok; 6 ok (xp1_thieu_thu_vien_pdf,
xp1_kieu_xuat_la in i18n; ma_loi_js DAT); 7 ok (no schema/CSV change; fonts + reportlab only in requirements).
Privacy: member-list PDFs (clb and lop) contain no "điểm / bốc thăm / stb / score" text.
Own edge cases (all ok): unknown or empty student_ids -> gt1_khong_co_hoc_sinh; bad `theo` -> xp1_kieu_xuat_la; no run yet ->
xuat_chua_co_ket_qua / gt1_chua_chay; data edited after the run -> stale warning in the PDF ("Lưu ý") and ket_qua_cu=True.
Observation (not a bug): per-class slip PDFs print each student's lookup code (same as the existing HTML slip, GT1-L4).
