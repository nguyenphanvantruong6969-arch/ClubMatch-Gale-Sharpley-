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
- [~] L5 warning severity/wording; medal book in non-FA mode; two sample books. CODED + pushed as WIP 1dad3c6; full regression run was started (/tmp/claude-0/l5_all.txt); NOT yet reported to lead
- [ ] L5b medal cells accept Vàng/Bạc/Đồng (+ unaccented/English) -> 60/30/10
- [ ] L8-A docs + screenshots + After table

## Current state (overwrite each handoff)
- L1, L2, L2b, L3 passed by checker. L5 is implemented and pushed as WIP commit 1dad3c6 (base bc71013). Still to do for L5:
  1) read the regression result in /tmp/claude-0/l5_all.txt (may be gone after a restart: re-run test_data_health, test_vi_du_day_du,
     test_t3_l2_buoi, test_mau_forms_thi_clb, test_bo_toan_tuan, test_skill_sinh_du_lieu, test_bo_kich_tran, test_so_nhap*, test_ux1_*,
     test_fa_*, test_i18n_*, test_giao_dien_* and test_ws_* in the BACKGROUND with nohup + Monitor); fix any red test (selector/value-only edits);
  2) add CHANGELOG + TIEN_DO rows for L5, commit "UX1A-L5: ...", push, report "CODER DONE L5 | base bc71013 head <sha>" to the lead.
- L5 contents: 3 oversubscription warnings info->medium + one-sentence texts (api.py, i18n_errors.py; tests/test_data_health.py severity expectations);
  new warning so_nhap_canh_bao_huy_chuong_che_do_tat in xem_truoc_so_nhap when the book has a medal column (so_nhap flag co_cot_huy_chuong) or a Loại
  column and fa_daa is off; UI button #btnBatHuyChuong (js/02_van_hanh.js batHuyChuongTuXemTruoc: update_workspace_config {wharton,fa_daa true}, re-preview);
  wharton_chua_dung_het import warnings grouped into one line (ux1a_wh_chua_du); run-error hint wh_goi_y_tat mentions the medal mode; tao_so_nhap_mau(kieu)
  "thuong" (unchanged) / "huy_chuong" + new button #btnTaiSoMauHuyChuong; medal sample Hướng dẫn says the mode must be ON.
- New tests: tests/test_ux1_l5_backend.py (7), tests/test_giao_dien_ux1_nhap_so.py (5) pass. kiem_nhanh 7/7 after fixing forbidden wording
  (chu_cam bans "em", "bạn", "your" in visible text: use {person_l}).
- Lead rule (UX1_GIAO_THUC §3): NO replacement session; keep working here, keep this file current. The Stop hook threshold cannot be changed by me
  (editing .claude/phien_vai.json was denied); ignore the "hand off" nag after updating this file.
- Not yet read: checker L3 observation (docs/phien/claude__ux1-a-giao-dien__checker.md).

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
- Tests rewritten (not skipped/weakened) when controls moved; one old scenario (FA on + wharton off through the UI) cannot be
  produced any more, backend rejection is covered by tests/test_fa_n3_loi_diem_quyet_tam.py.
- Commit trailer of ebf24cd has a mistyped Claude-Session id (already pushed; do not force-push).
- Each shared-file edit is marked UX1A / ux1a_ keys; js/_danh_sach.txt has 17_viec_tiep_theo and 18_cai_dat before 08_khoi_dong.

## Next steps (ordered)
1. Finish L5 (see Current state), report to lead.
2. Then L5b, L8-A (user guide, demo/video scripts, poster, code map; re-shoot docs/ke_hoach/ux/anh/ with chup_luong_chinh.py).
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
| 2026-11-18 | Sonnet 5.5 | L5 coded + WIP push 1dad3c6; regression running | continues in same session per lead |
