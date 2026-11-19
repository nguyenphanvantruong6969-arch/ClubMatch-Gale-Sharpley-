# Branch handoff: claude/ux1-b-phieu (coder, UX1B)

> Purpose: a fresh coder session reads CLAUDE.md, docs/phien/UX1_GIAO_THUC.md (§10 wins), the branch file, THIS file.
> Lead session: session_01YVAytyWhTzeYjV1fcHGdde. Report in GT_GIAO_THUC §7 format via send_message.

## Feature / goal
UX1 team B: slip content, summary report, L5c UX fixes. Lot order: L4-B -> L7 -> L5c -> L8-B -> CI gate -> review.
No product-logic change; invariant 1 (byte-identical match_results) must stay 7/7.

## Plan
- [x] L4-B summary report + homeroom block (CODER DONE head 0f73c43)
- [x] L7 slip content (done; fix1 79c8e45, fix2 fc5e9fc)
- [x] L5c five recommendations of UX1_DANH_GIA_A §4 (CODER DONE 276616b; fix1 f3ff065 sent; checker re-review pending)
- [x] L8-B slip docs, images (04_phieu.png, phieu_mau.pdf, 03_tra_cuu_HS004.png), "After" rows, code map (CODER DONE head b960b60)
- [ ] CI gate, user review (lead)

## Current state
- UX1B is DONE: CI green on eac69df, lead's branch file at b510dbf. All coder lots (L4-B, L7, L5c, L8-B) and fixes
  (L7 fix1-2, L5c fix1, CI-1, R1 + fix2) are pushed and accepted by the checker.
- In progress: nothing. Coder is idle; Team A lead drives integration (I1-I3, branch claude/ux1-tich-hop).

## Decisions and gotchas
- Never rebase/force-push (protocol §2); merge origin/claude/ux1-b-phieu and origin/claude/ux1-a-giao-dien before each lot.
- Sentences for slip + on-screen card live in giai_trinh.py (single source); on-screen i18n headings must avoid "Em"/"you"
  (kiem_nhanh chu_cam). Slip (Python) may say "Em".
- Student-facing tra_cuu_hoc_sinh strips run.seed and per-row stb_em; staff paths keep them.
- Slip column order: Nguyện vọng | CLB | [Huy chương, FA only] | Điểm thi | Chỗ đã nhận / tối đa | Mức vào được | Vì sao.
  XP1 inserts "Loại CLB" right after CLB. Tests select the last/second-last td, not fixed indexes.
- Health report keeps `warnings`/`n_high`; grouping of fa_huy_chuong_* is display-only (`gop_huy_chuong` field).
- Lookup code buttons are inside <details id="gtMaFold">; UI tests open it with tests/_trinh_duyet.mo_gap_ma(page).
- New error codes ux1b_huy_chuong_gop(+_khong_clb) are in tests/test_ws_nhan.py MA_MOI_SAU_ANH_CHUP.
- "Whole book wrong" threshold lives only in api_quan_ly._huy_chuong_ca_so_sai (n_sai*2 >= n_hoc_sinh).
- Default export has sheets Điểm chuẩn + Dấu vết (seed, lottery numbers): privacy red line must stay visible by default.

## Next steps
1. Stay idle. Only act if the Team A lead / integration coder messages with a question about team B code.
2. Reminders for integration: XP1 inserts "Loại CLB" right after the CLB column of the slip (medal column follows it);
   "In phiếu cả lớp" and the slip PDF button are wired at I3; slip click target (4) only becomes true then.

## Files touched (whole branch so far)
- bao_cao_tong_hop.py, api_xuat.py, phan_quyen.py: summary report + slip data (huy_chuong, tinh_nang)
- giai_trinh.py, phieu_giai_trinh.py, fa_ly_do.py: slip content
- api.py, api_quan_ly.py, i18n_errors.py (+ i18n_loi.js): L5c health grouping, san_sang n_hoc_sinh
- index.html, style.css, i18n.js, js/02_van_hanh.js, js/14_giai_trinh.js, js/17_viec_tiep_theo.js, js/18_cai_dat.js,
  js/19_ux1b_gv.js, js/_danh_sach.txt: UI
- docs: HUONG_DAN_SU_DUNG.md, docs/giai_trinh/{HUONG_DAN_CHAY,KICH_BAN_DEMO}.md, docs/ke_hoach/ux/UX1_RA_SOAT.md, CLAUDE_CHI_TIET.md, anh/*
- tests: test_ux1b_l4_bao_cao, test_ux1b_l7_phieu, test_giao_dien_ux1b_{vai_gv,phieu,l5c}; edits in ux1_cai_dat, gt1/gt3/gt4 UI,
  gt1_tra_cuu, gt4_cau_giai_trinh, ws_nhan, _trinh_duyet

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-19 | Sonnet | L4-B, L7 (+2 fixes), L5c; handoff at ~400k context | lead id above |
| 2026-11-19 | Sonnet | Hook re-fired; no new work since 903bffa; lead said stay available (no replacement session) | waiting FIX L5c / GO L8-B |
- L5c fix1 coded; pushing, then CODER DONE L5c fix1.
| 2026-11-19 | Sonnet | L5c fix1 (f3ff065); hook re-fired at >400k; lead says no replacement session | stay available |
- L8-B done and pushed; waiting for review.
| 2026-11-19 | Sonnet | L8-B (b960b60); hook re-fired at >400k; staying available per lead | handoff refreshed |
| 2026-11-19 | Sonnet | CI-1: index.html fallback text of group label synced with i18n.js (test_t3_l1_chu_du_phong green) | note: fallback texts in index.html must equal i18n.js vi |
| 2026-11-19 | Sonnet | R1 (lead review): FA cutoff column, single MEDAL sentence, report label/case/unit fixes | pushed once |
| 2026-11-19 | Sonnet | R1 fix2: FA cutoff from stored REJECTED rows (reserve-safe), 3 tests | pushed once |
| 2026-11-19 | Sonnet | Final: UX1B DONE (CI green eac69df); impl file finalised | idle |
