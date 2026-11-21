# Branch handoff (CODER / impl session): claude/ux2-phan-hoi-nut

> Purpose: a fresh session reads CLAUDE.md, docs/phien/UX2_GIAO_THUC.md, docs/phien/claude__ux2-phan-hoi-nut.md (lead's
> plan + ticks), then THIS file, and can continue as CODER without the old chat. English, <=150 lines.
> Role: CODER (Sonnet). Lead = session_01VfPzNumBTQB5odHhUwJqun. Checker reports: docs/phien/claude__ux2-phan-hoi-nut__checker.md.
> Written because the Stop hook asked at ~400k tokens. NOTE: UX2_GIAO_THUC.md section 2 says exactly 3 sessions for the job and
> that auto-summary replaces the 400k handoff, so lead may simply keep using this session (context is summarised).

## Feature / goal
UX2 = positive interaction feedback (UI only: style.css, js/*.js, index.html, i18n.js). No algorithm / api*.py shapes / CSV /
schema change (invariants 1, 6, 7). I do lots L1..L9 on lead's "GO L<n>" / "FIX" messages, one commit per lot
`UX2-L<n>: ...`, report "CODER DONE L<n> | base <sha> head <sha>" with send_message to the lead.

## Plan (ticked in the lead's branch file; status here)
- [x] L1 #2+#13 busy state / double-click guard (datNutBan)  PASSED (+fix1, fix2)
- [x] L2 #3 check mark after save/export (nutDaXong)          PASSED
- [x] L3 #8 #9 #1 hit area / one focus ring / state layer     PASSED (+fix1 nav-item 44px, fix2 controls above ::after)
- [x] L4 #7 inline field errors (baoLoiTaiO...)               PASSED (+fix1 language switch)
- [x] L5 #11 four-phase progress (UX2_PHA)                    PASSED (+fix1 backup warning)
- [x] L6 #12 guided empty states (veTrangThaiRong)            PASSED (291deb8 + fix1 788709f)
- [x] L7 #6 skeleton loading (hienKhungCho)                   DONE head b00b9e3, reported, checker verdict pending
- [ ] L8 #10 smooth transitions   [ ] L9 docs/screenshots/verify (spec: lead's branch file)

## Current state (overwrite each handoff)
- Done: L1-L7 committed + pushed; last code commit b00b9e3 (L7). Working tree clean after the handoff push.
- In progress: nothing. Waiting for lead: checker verdict on L7 and "GO L8".
- Tests: related ones only (never the 22-min full suite); redirect pytest output to a scratchpad file.
  Last (L7): 217 passed (ux2_*, tien_trinh, a13_8, a13_12, quan_ly_tab_con, a14_lop, t3_l0, t3_l2_van_hanh, chay, ux1_ket_qua,
  fa_n2, cham_diem, tro_nang, i18n_sync, khoa_xuat, ux_xuat), ruff clean, kiem_nhanh.py --co-so origin/main --so-seed 20 7/7.
- Open problems: none known. 800 HS admin list loads in ~0.4 s locally (no skeleton shown; threshold 300 ms).

## Decisions and gotchas (keep short)
- Helpers live in js/00_nen.js: datNutBan (busy), nutDaXong/goDauXong (check mark), baoLoiTaiO/xoaLoiTaiO/focusODau/baoLoiForm
  (inline errors), veTrangThaiRong/ux2DiToi (empty states). Spinner/check are child <span>s, never ::before/::after.
- LANGUAGE SWITCH rule (bit me 3 times): any dynamic UI text must re-render on `langchange` (store a key or a () => text,
  not a string). applyStaticText overwrites [data-i18n] textContent, so boxes that hold buttons must NOT carry data-i18n.
  07_ngon_ngu.js rebuilds some tables on langchange (e.g. scoring club table) -> re-apply state afterwards.
- Hit-area CSS (L3): ::after >=44 px on button/.btn/[role=button]; td bare buttons 34 px, li bare buttons 20 px (neighbours
  would overlap); controls (input/select/textarea/summary/label) get position:relative;z-index:1 except inside closed
  <details>; .nav-item min-height 44, .nav-nhom-nut 24 (lead decision).
- Measure widths with offsetWidth (not getBoundingClientRect: :active scale(0.97) skews it).
- `page.evaluate("() => fn()")` returning a never-resolving promise hangs Playwright: wrap in braces `{ fn(); }`.
- Result panels default closed (MAC_DINH_DONG); admin student list is in the "Học sinh" sub-tab (#qlTabHs): tests must open them.
- Closed <details> content keeps phantom coordinates; elementFromPoint there hits whatever is underneath.
- giao_vien: Vận hành tab (4 phases, btnRun) is data-quyen quan_tri -> invisible to that role.
- ws_nhan FREEZES default UI strings (tests/du_lieu_ws/chuoi_truoc_khi_co_nhan.json): never edit an existing i18n value; add new ux2_ keys.
  test_van_phong_tu_nhien bans long dashes, address forms (en "you"), ALL CAPS, internal words in UI strings.
- Empty states (L6): cfg.gv = role text for giao_vien (no button, "ask an administrator"); tab names come from ux2TenThe() = nav
  labels ({the_xep}/{the_quan_ly}/{the_nhap}); redraw on `langchange` AND `ux2vai` (ganVai in 16_tai_khoan.js dispatches it).
- Skeleton (L7): hienKhungCho(tbody, soCot, soDong, hoi, caoHang): 300 ms delay, only when tbody empty, ONE colspan cell per row
  (per-column bars made columns jump 100-135 px), cleared by hoi.then(ket, ket) (success/error/reject), token compare for double
  loads; tests avoid wall-clock asserts (use the synthetic-table test); admin student row height 55 px.
- Push rejected -> `git fetch origin claude/ux2-phan-hoi-nut && git merge --no-edit FETCH_HEAD` (protocol: never rebase/force).
- Stop hook "uncommitted changes": commit a clearly labelled WIP and push; only report "CODER DONE" when tests are green.

## Next steps (ordered)
1. Wait for lead: checker verdict on L7 (FIX L7 -> test first, minimal fix, related tests, report "CODER DONE L6 fixN").
2. On "GO L8": `git pull origin claude/ux2-phan-hoi-nut` + `git fetch origin main && git merge --no-edit FETCH_HEAD`, read the L8 block.
3. L8 smooth transitions (@supports for ::details-content / interpolate-size), L9 docs + screenshots (HUONG_DAN_SU_DUNG.md section,
   re-shoot docs/ke_hoach/ux/anh/, CLAUDE_CHI_TIET.md code map, kiem_nhanh 7/7, CHANGELOG + TIEN_DO rows).
4. Each lot: failing test first -> minimal code -> related tests -> ruff -> kiem_nhanh 7/7 -> CHANGELOG + TIEN_DO row `UX2-L<n>` ->
   tick Plan in the lead's branch file only if lead asks (lead ticks) -> commit -> push -> message lead.

## Files touched (whole job so far)
- js/00_nen.js: all shared helpers above + langchange listeners
- js/02_van_hanh.js: btnRun busy via datNutBan; UX2_PHA / ux2TinhPha / ux2VePha; seed inline error
- js/03_ket_qua.js, 05_quan_ly.js, 06_cham_diem.js, 04_nhap_tai_cho.js, 09_the_xem.js, 10_theo_doi.js, 14_giai_trinh.js: check-mark wiring,
  inline errors, empty-state configs (UX2_RONG_*), chayXuat 4th param
- js/07_ngon_ngu.js: redraw phases + keep score-input errors across table rebuild
- i18n.js (+ applyStaticText busy/check handling), index.html (#ux2Pha, empty boxes), style.css (blocks "UX2 - L1..L6")
- tests: test_giao_dien_ux2_{ban,xong,nut,loi_o,tien_trinh,rong}.py, test_ux2_tien_trinh.py
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md (rows UX2-L1..L6), docs/phien/claude__ux2-phan-hoi-nut.md (Plan ticks L1-L6)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-21 | Sonnet (coder) | L1-L6 built, fixed per checker (L1 x2, L3 x2, L4 x1, L5 x1), all pushed; handoff written at ~400k context | head 291deb8 |
| 2026-11-21 | Sonnet (coder) | L6 fix1 (role-aware empty boxes, nav tab names, ux2vai), handoff refreshed (hook fired again) | head 788709f |
| 2026-11-21 | Sonnet (coder) | L7 skeleton loading built + reported; handoff refreshed (hook fired again) | head b00b9e3 |
