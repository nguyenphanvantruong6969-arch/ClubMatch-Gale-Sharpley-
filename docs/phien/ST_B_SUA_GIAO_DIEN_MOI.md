# tests_stress/b on main (60142c8): why 54 of 65 tests fail, and the verified fix

> English. Written 2026-11-24. All data SIMULATED. Verified locally (scratch venv, Playwright Chromium). Companion file: `ST_B_SUA_GIAO_DIEN_MOI.patch` (test-only diff, applies cleanly on main; `git apply docs/phien/ST_B_SUA_GIAO_DIEN_MOI.patch`).

## Result of running the whole folder (7 files, 65 tests; folder is NOT in CI)
Earlier notes said "19 failing": that was only `test_b2_quan_ly.py`. Real count: **54 failed** (b1 13/13, b2_nhap_tep 8/8, b2_quan_ly 19/19, b3_phuc_hoi 2/7, b4 10/10, b5 2/2; b3_vai_tro 9/9 pass).

## Root causes (all 54 failures hit one of these first)
1. **53 failures: ONE helper.** `ho_tro.chon_cach` waits for `#ux1aHuyChuong` / `#ux1aChia100` right after `ui.tab("admin")`. UX4-L4 moved the three mode cards to tab `#qlTabCachXep`, inside the closed fold `<details id="ux1aNangCao">`. Fix: helper `mo_the_che_do(page)` (click `#qlTabCachXep`, open `#ux1aNangCao` only if `open` attr is None). After this: b1, b2_nhap_tep, b3_phuc_hoi, b5 pass.
2. **Quản lý sub-tabs in the "Thêm ▾" menu (UX4-L2).** `#qlTabWh/#qlTabDc/#qlTabDb/#qlTabDuLieu` sit in `#qlThemMenu` (opened by `#qlNutThem`, `aria-expanded`). Fix: helpers `mo_menu_them`, `tab_ql_hien`, `clic_tab_ql` (b1 `test_b1_moi_tab_va_tab_con`, 4 clicks in b2_quan_ly, 2 loops in b4).
3. **UX4-L3 form changes in b2_quan_ly.** `#clubFormBuoi` is now a `<select>` (use `select_option`, skip when empty); `#clubFormId` / reserve capacity are behind `#clubFormThemTuyChon` and a save can re-fold them (reopen if hidden inside `_luu_clb`); `#btnBulkAssign` is hidden until students are ticked, so the old step "click Assign with nothing ticked, expect an error toast" no longer exists: assert `is_hidden()` instead.
4. **REAL PRODUCT BUG (not a test problem): `test_b4_do_rong_man_hinh[390]` and `[768]`.** UX5A-L2 dropdowns `.menu-khac-hop.ux5a-hop-rong` ("Báo cáo và phiếu in ▾" on Kết quả, `#xuatMenu` on Chi tiết) use `position:absolute; right:0; width:min(360px,90vw)`, anchored to the right edge of a button that sits at the LEFT of its row. At 390 px the open menu spans x=-132..219 (kết quả) and -37..314 (xuất tệp): cut off at the left edge (screenshot confirmed). At 768 px with no class selector it is -12..348. 1280 px is fine.

## Verified candidate CSS (not in repo yet; needs Truong's wording/visual review)
```css
@media (max-width: 800px) {
  .menu-khac-hop.ux5a-hop-rong { position: fixed; left: 12px; right: 12px; top: auto; bottom: 12px; width: auto; max-height: 70vh; overflow: auto; }
}
```
Measured at 390/768/1280 on both menus: no element off-screen after the rule; unchanged at 768/1280 for the old layout. A naive `left:0` fix is WRONG (moves `xuatMenu` to 179..521). With the rule, all 10 tests of `test_b4_hien_thi.py` passed except one flaky run (see below). Not reviewed visually yet.

## Verification after the test-side fixes (folder files run separately; conftest clashes with tests_stress/a)
b1 13 pass, b2_nhap_tep 8, b3_phuc_hoi 7, b3_vai_tro 9, b5 2; b2_quan_ly: 14 pass in the full run + the other 5 pass after item 3 (run with `-k "form_clb or xoa_clb_khong_co or gan_nhom"`); b4: 9 pass with the CSS rule.
- `test_b4_chi_ban_phim_nhap_chay_xuat` failed once in a 4-way parallel run ("Chưa chọn mục nào để xuất", run not finished) and passed 3/3 alone (6.8 s): timing flake under load (same family as SF-B8). Run files in parallel at most 2-way, or alone.
- Tests write screenshots into `docs/phien/anh_st_b/*.png` (tracked files get modified): do not commit those.

## Suggested next item (own branch, Opus plans, Sonnet codes; CLAUDE.md rule 12)
A. Test-side items 1-3 (apply the patch, review, run each file, add CHANGELOG + TIEN_DO row). B. Product fix item 4 as a separate small UI item (CSS only, needs Truong's visual OK; add a test that opens each `.ux5a-hop-rong` menu at 390 px and asserts it fits). Do both in one branch only if Truong agrees; B changes what users see.
