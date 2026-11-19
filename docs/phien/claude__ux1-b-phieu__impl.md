# Branch handoff: claude/ux1-b-phieu (coder, UX1B)

> Purpose: a fresh coder session reads CLAUDE.md, docs/phien/UX1_GIAO_THUC.md (§10 wins), the branch file, THIS file.
> Lead session: session_01YVAytyWhTzeYjV1fcHGdde. Report in GT_GIAO_THUC §7 format via send_message.

## Feature / goal
UX1 team B: slip content, summary report, L5c UX fixes. Lot order: L4-B -> L7 -> L5c -> L8-B -> CI gate -> review.
No product-logic change; invariant 1 (byte-identical match_results) must stay 7/7.

## Plan
- [x] L4-B summary report + homeroom block (CODER DONE head 0f73c43)
- [x] L7 slip content (done; fix1 79c8e45, fix2 fc5e9fc)
- [x] L5c five recommendations of UX1_DANH_GIA_A §4 (CODER DONE head 276616b; checker not yet run)
- [ ] L8-B slip docs, regenerate CA_MAU.md + evidence pack + anh/04_phieu.png + anh/phieu_mau.pdf, "After" row
- [ ] CI gate, user review (lead)

## Current state
- Done: L4-B, L7 (+fix1, fix2), L5c. All pushed on origin/claude/ux1-b-phieu. Waiting for lead: REVIEW L5c or GO L8-B.
- In progress: nothing half-finished.
- Tests last run green: test_giao_dien_ux1b_l5c (5), ux1_*/ux1b_*, gt1/gt3/gt4 UI, ws_nhan, van_phong_tu_nhien,
  gt4_nhat_ky_doc, fa_huy_chuong (241 + 75 passed); kiem_nhanh 7/7 (60 cases byte-identical vs origin/main).
- Open problems: none known. Commit trailers from L4-B had a wrong Claude-Session id (cosmetic).

## Decisions and gotchas
- Never rebase/force-push (protocol §2); merge origin/claude/ux1-b-phieu and origin/claude/ux1-a-giao-dien before each lot.
- Sentences for slip + on-screen card live in giai_trinh.py (single source); on-screen i18n headings must avoid "Em"/"you"
  (kiem_nhanh chu_cam). Slip (Python) may say "Em".
- Student-facing tra_cuu_hoc_sinh strips run.seed and per-row stb_em; staff paths keep them.
- Slip column order: Nguyện vọng | CLB | [Huy chương, FA only] | Điểm thi | Chỗ đã nhận / tối đa | Mức vào được | Vì sao.
  XP1 inserts "Loại CLB" right after CLB. Tests select the last/second-last td, not fixed indexes.
- Health report keeps `warnings`/`n_high`; grouping of fa_huy_chuong_* is display-only (`gop_huy_chuong` field).
- Lookup code buttons are inside <details id="gtMaFold">; UI tests open it with tests/_trinh_duyet.mo_gap_ma(page).
- New error code ux1b_huy_chuong_gop is in tests/test_ws_nhan.py MA_MOI_SAU_ANH_CHUP.

## Next steps
1. Wait for lead: FIX L5c (if checker finds bugs) or GO L8-B.
2. L8-B: update slip docs (CHANGELOG/TIEN_DO rows), regenerate docs/giai_trinh/CA_MAU.md
   (du_lieu_test/tao_ca_mau_giai_trinh.py), docs/giai_trinh/tao_goi_minh_chung.py, anh/04_phieu.png + anh/phieu_mau.pdf
   (docs/ke_hoach/ux/chup_phieu.py), "After" row of the slip task in UX1 docs.
3. After each lot: invariant-1 check (`kiem_nhanh.py --co-so origin/main --so-seed 20` after `git fetch origin main`),
   soat-ma, CHANGELOG + TIEN_DO, commit "UX1B-L<n>: ...", push, send CODER DONE.

## Files touched (whole branch so far)
- bao_cao_tong_hop.py, api_xuat.py, phan_quyen.py: summary report + slip data (huy_chuong, tinh_nang)
- giai_trinh.py, phieu_giai_trinh.py, fa_ly_do.py: slip content
- api.py, api_quan_ly.py, i18n_errors.py (+ i18n_loi.js): L5c health grouping, san_sang n_hoc_sinh
- index.html, style.css, i18n.js, js/02_van_hanh.js, js/14_giai_trinh.js, js/17_viec_tiep_theo.js, js/18_cai_dat.js,
  js/19_ux1b_gv.js, js/_danh_sach.txt: UI
- tests: test_ux1b_l4_bao_cao, test_ux1b_l7_phieu, test_giao_dien_ux1b_{vai_gv,phieu,l5c}; edits in ux1_cai_dat, gt1/gt3/gt4 UI,
  gt1_tra_cuu, gt4_cau_giai_trinh, ws_nhan, _trinh_duyet

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-19 | Sonnet | L4-B, L7 (+2 fixes), L5c; handoff at ~400k context | lead id above |
