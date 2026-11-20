# Handoff (coder, MT1): claude/mt1-bo-muc-tieu

> English. Lead: session_01TGThn5w7hS2AUUvuf2JfSJ. Protocol: docs/phien/MT1_GIAO_THUC.md. Branch file: docs/phien/claude__mt1-bo-muc-tieu.md.

## Plan (coder view)
- [x] L1 catalogue (checker NO BUGS)
- [x] L2 API (checker NO BUGS)
- [x] L3 estimate + result (NO BUGS after fix1, fix2)
- [x] L4 UI — done, verified, reported (CODER DONE L4)
- [ ] L5 docs + review (lead)

## Current state
- L4 implemented: js/19_muc_tieu.js (new), hooks in js/18_cai_dat.js (ux1aTaoThe got params `bo`, `khoaCauHoi`, `moiTheTab`; old "Cách xét khi đông" line removed), js/075_workspace.js (wizard step 3), js/03_ket_qua.js (calls mt1VeKetQua), js/08_khoi_dong.js, index.html (#mt1KetQua + script tag), js/_danh_sach.txt, i18n.js (mt1_* keys), style.css (.mt1-*).
- tests/test_giao_dien_mt1.py: 22 cases, ALL PASSED alone (Chromium). Old tests/test_giao_dien_ux1_cai_dat.py edited (no more #ux1aCachXet).
- A wider UI regression run (ux1_cai_dat, ws_giao_dien, a13_12_ws, a13_13, fa_cai_dat, fg1, gt2/gt4_tieu_chi, ux1b_l5c, ux1_tiep_theo, ux1_dieu_huong, tom_tat, fg8_cau_chu, sg11a, t3_l1_ws, mt1) was running with -x: ≥35 dots, no failure seen when handing off; final result NOT read. Re-run it.
- Verified 2026-11-20: 153 UI tests pass (wide list), 204 related backend/doc tests pass, ruff clean, kiem_nhanh 7/7, screenshots in docs/phien/anh_mt1/.

## Next steps
1. L4 was reported (CODER DONE L4, head 3715bd8). Wait for `REVIEW`/`FIX L4` from the lead; fix test-first, run related tests only, `kiem_nhanh.py --so-seed 20`, commit "MT1-L4 fix<k>: ...", push, report in GT_GIAO_THUC §7 format.
2. L5 is the lead's (docs + final review); coder only helps if asked (HUONG_DAN_SU_DUNG "Chọn mục tiêu").
3. Wide UI regression list (for fixes): ux1_cai_dat, ws_giao_dien, a13_12_ws, a13_13, fa_cai_dat, fg1, gt2/gt4_tieu_chi, ux1b_l5c, ux1_tiep_theo, ux1_dieu_huong, tom_tat, fg8_cau_chu, sg11a, t3_l1_ws, mt1 (153 passed, ~4 min).

## Decisions
- Contract strings use label tokens ({person_l} -> "học sinh", {slot_s} -> "CLB") because chu_cam bans "em" in i18n.js; so UI says "N học sinh được chỗ tốt hơn".
- danh_cho with several groups: card click only shows group pills (card shows selected, nothing saved); pill click saves (2 clicks). One group: auto (1 click).
- Wizard step 3: goal cards drive the existing "Thứ tự ưu tiên" select; danh_cho disabled (no student list yet).
- All 3 MT cards are tabbable (moiTheTab) so keyboard Tab+Enter works; first question keeps roving tabindex.
- Words-only effect line: tang_1 else tang_2 of get_tieu_chi-style mo_ta (co_hoi has only tang_2).
- Effect line text after run is "Lần xếp gần nhất đã theo mục tiêu này." when estimate is 0/0.

## Files touched (L4)
js/19_muc_tieu.js, js/18_cai_dat.js, js/075_workspace.js, js/03_ket_qua.js, js/08_khoi_dong.js, js/_danh_sach.txt, index.html, i18n.js, style.css, tests/test_giao_dien_mt1.py, tests/test_giao_dien_ux1_cai_dat.py, CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md.

## Needs Truong
- Manual check of the Windows exe (protocol §6).

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-20 | Sonnet (coder) | L1–L3 delivered; L4 code + 22 UI tests written | handed off at ~400k context by Stop hook |
| 2026-11-20 | Sonnet (coder) | L4 verified (153 UI + 204 backend tests, kiem_nhanh 7/7, screenshots) and reported | lead: MT1 §2 overrides the 400k stop; same session continues |
