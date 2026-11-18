# Branch handoff: claude/ux1-a-giao-dien (coder / impl)

> Role: CODER for UX1 team A. Lead session: session_01TGThn4GicB4XGX5L6zfZ57. Protocol: docs/phien/UX1_GIAO_THUC.md.
> Lots: docs/ke_hoach/ux/UX1_KE_HOACH.md. Branch file (lead): docs/phien/claude__ux1-a-giao-dien.md. English.

## Feature / goal
UX1 (direct UI, fewer steps), team A: next-step bar, 4-group navigation, Settings = one question with three cards,
results page lookup first + one export menu, warnings/medal book (L5, L5b), docs (L8-A). UI/presentation only:
default config stays byte-identical (invariant 1), every element id and data-tab kept.

## Plan (lead ticks; coder status in brackets)
- [x] L1 Next-step bar (checker NO BUGS)
- [x] L2 navigation 6 -> 4 groups (checker NO BUGS)
- [x] L2b Settings: three cards, instant save + Undo, fix-in-place, post-run actions (checker NO BUGS)
- [x] L3 results page (checker NO BUGS after fix1, head 3ba1efe)
- [x] L5 warning severity/wording; medal book wrong-mode message + one-click enable; two sample books. Coder DONE at 764c85c, waiting for checker
- [x] L5b medal cells accept Vàng/Bạc/Đồng -> 60/30/10 (coder DONE, waiting for checker)
- [x] L8-A docs + screenshots + After table (coder DONE ad569c2, waiting for checker)

## Current state (overwrite each handoff)
- All 7 lots passed the checker; the lead's CI gate ran on 64bc133, then the lead sent FIX L2b round 2 (push allowed; CI is superseded).
- FIX L2b round 2 is CODED (WIP commit): (1) get_san_sang_huy_chuong also returns huy_chuong_sai (+_vd) via fa_daa.kiem_ho_so_huy_chuong (read-only);
  san_sang is false when > 0; panel line #ux1aSsHuyChuongSai (js/18_cai_dat.js ux1aVeSanSang, i18n ux1a_ss_huy_chuong_sai); (2) #ux1aSauXep shows
  "Mở vòng 2" only when unplaced > 0 and "Mời danh sách chờ" only when empty seats > 0 (shown anyway when the flag is already on); (3) .toast .toast-hanh-dong
  CSS (white, underlined). Tests updated/added in tests/test_ux1_cai_dat_backend.py and tests/test_giao_dien_ux1_cai_dat.py (14 + backend pass).
- (done: regression 252 passed, CHANGELOG added, reported) Old note: read the related regression result (/tmp/claude-0/fix2.txt, may be gone: re-run test_giao_dien_ux1_*, test_ux1_*, fg1_bat_tinh_nang,
  giao_dien_fa_*, sg2, sg11b, gt3_phan_quyen, i18n_*, ws_nhan in the BACKGROUND with nohup + Monitor), fix reds, add CHANGELOG line, commit, push,
  report "CODER DONE L2b fix2 | base <sha> head <sha>" to the lead.
- Open: checker L3 "observation" in docs/phien/claude__ux1-a-giao-dien__checker.md never read.
- Lead rule (UX1_GIAO_THUC §3): NO replacement session; keep working here. Do NOT push while the lead says a CI run is in flight unless a FIX/GO arrives.

## Decisions and gotchas (keep short)
- Group nav (L2): sub-items `.nav-item[data-tab]` stay visible under 4 `.nav-nhom` headings because 75 tests click
  `[data-tab=...]` from any tab. Group visibility is attribute based (hidden / giao_vien + data-quyen). An unguarded
  MutationObserver froze the page: only write `hidden` when it changes.
- Settings (L2b): three cards map wharton/fa_daa (chi_xep: false/false, chia_100: true/false, huy_chuong: true/true);
  switching away from Huy chương also turns off post-run flags in the same update_workspace_config call; Undo restores them.
  update_workspace_config already logs an audit row (default nen_ghi policy); test added. Backend added
  get_san_sang_huy_chuong (read) and dat_loai_clb (write, reuses fa_daa.ghi_thuoc_tinh_clb); both in phan_quyen.py.
  "Thay đổi…" opens Quản lý > Nâng cao (no separate sheet). Old wsMoTinhNang dialog and wizard FA checkboxes removed;
  wizard step 3 uses the same cards (ids wzChiXep/wzChia100/wzHuyChuong). Component ids: prefix + ChiXep/Chia100/HuyChuong,
  error id prefix+"LoiThe" (a plain "wzLoi" collided with the wizard error box).
- Post-run features are actions in #ux1aSauXep (Chi tiết tab), visible only when fa_daa; the grid skips re-render when
  nothing changed (keeps typed complaint days).
- L3: #gtPanel is first in view-results; #xuatMenu (details.menu-khac) holds the 4 secondary export buttons (menu closes
  after each pick; tests wait with state="attached"); import numbers shown only in the file row, toast says "Đã nạp sổ".
  The bar "Xuất" state exports directly with default options (4-click target); in state xu_ly a secondary export button exists.
- Snapshot tests (tests/test_ws_nhan.py): deliberately reworded default strings go into SUA_CO_Y (resolved strings, after THAY_CHU_T3) and tests/du_lieu_ws/chu_ui_doi_co_y_t3.json; new error codes go into MA_MOI_SAU_ANH_CHUP. The chu_cam check bans "em", "bạn", "your" in visible text.
- Tests rewritten (not skipped/weakened) when controls moved; one old scenario (FA on + wharton off through the UI) cannot be
  produced any more, backend rejection is covered by tests/test_fa_n3_loi_diem_quyet_tam.py.
- Commit trailer of ebf24cd has a mistyped Claude-Session id (already pushed; do not force-push).
- Each shared-file edit is marked UX1A / ux1a_ keys; js/_danh_sach.txt has 17_viec_tiep_theo and 18_cai_dat before 08_khoi_dong.

## Next steps (ordered)
1. Handle REVIEW/FIX for L8-A if the lead sends them, then CI-gate FIX lists; integration (I1/I2) on GO. (old: L8-A; L5b was, L8-A (user guide, demo/video scripts, poster, code map; re-shoot docs/ke_hoach/ux/anh/ with chup_luong_chinh.py).
4. Per lot: failing test -> minimal code -> related tests -> `kiem_nhanh.py --co-so origin/main --so-seed 20`
   (after git fetch origin main) -> soat-ma notes -> CHANGELOG + TIEN_DO row -> commit "UX1A-L<n>: …" -> push -> report
   "CODER DONE L<n> | base <sha> head <sha>" (GT_GIAO_THUC §7 format) with send_message to the lead.
5. Before each lot: git pull, then git fetch origin claude/gt-tich-hop && git merge --no-edit FETCH_HEAD. Never rebase/force-push.

## Files touched (whole job so far)
- js/17_viec_tiep_theo.js (new): next-step bar. js/18_cai_dat.js (new): Settings cards, fix-in-place, post-run actions.
- js/01_khung.js: nav groups. js/02_van_hanh.js: bar hooks, import message once. js/03_ket_qua.js: bar hook, export menu, KPI action.
- js/05_quan_ly.js, js/075_workspace.js (menu "Cài đặt…", wizard cards), js/14_giai_trinh.js (jump link removed), js/15_tieu_chi.js (wharton checkbox removed), js/08_khoi_dong.js.
- index.html, style.css, i18n.js (ux1a_* keys), js/_danh_sach.txt, api_quan_ly.py, phan_quyen.py, CHANGELOG.md, docs/ke_hoach/TIEN_DO.md.
- New tests: tests/test_giao_dien_ux1_tiep_theo.py, _dieu_huong.py, _cai_dat.py, _ket_qua.py, tests/test_ux1_cai_dat_backend.py.
- Rewritten tests (placement/controls): ws_wharton_giao_dien, a13_13_kiem_nhan, fa_cai_dat, fa_gap1, fa_gap3, fg8_cau_chu, fg1_bat_tinh_nang, sg2, sg11b, gt2_tieu_chi, gt4_tieu_chi, ws_giao_dien, fa_ket_qua, sg11a_ve_sinh, gt4_man_hoc_sinh, upload, xoa_du_lieu, a14_lop, gt2_thu.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-18 | Sonnet 5.5 | L1, L2, L2b, L3 (+fix1) coded, tested, pushed; reports sent to lead | handoff at ~400k tokens; head 3ba1efe |
| 2026-11-18 | Sonnet 5.5 | L5 coded, regression-fixed, pushed 764c85c, reported to lead | continues in same session per lead |
| 2026-11-18 | Sonnet 5.5 | L5b coded + tests; WIP pushed; regression pending | same session per lead |
| 2026-11-18 | Sonnet 5.5 | L5b done, pushed 4cae05b, reported | same session per lead |
| 2026-11-18 | Sonnet 5.5 | L8-A done (docs, screenshots, After table), pushed ad569c2, reported | same session per lead |
| 2026-11-18 | Sonnet 5.5 | L8-A fix1 (32 unplaced, poster line in lead file) pushed 326dbc6, reported | same session per lead |
| 2026-11-18 | Sonnet 5.5 | FIX L2b round 2 coded (readiness honesty, pointless actions hidden, Hoàn tác contrast), WIP pushed | regression pending |
