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
- [x] L7 #6 skeleton loading (hienKhungCho)                   PASSED (b00b9e3)
- [x] L8 #10 smooth transitions (ux2QuanSatBang, ux2Abre)    PASSED (fef2862 + fix1 a71baec)
- [~] L9 docs / screenshots / verify: content WRITTEN + committed as WIP, verification NOT finished (see Current state)

## Current state (overwrite each handoff)
- L9 DONE and reported (full UI sweep 810 passed / 0 failed, ruff clean, kiem_nhanh 7/7, doc tests 94 passed). Awaiting checker verdict.
- (history) L9 (lead said GO L9, base 816e92c) was IN PROGRESS. Written and committed (WIP commit, not yet reported "CODER DONE L9"):
  HUONG_DAN_SU_DUNG.md new section (end of section 4), docs/ke_hoach/CLAUDE_CHI_TIET.md code-map row + tests/ count 360->369
  (test_a13_12_tai_lieu.py demands the exact count; backticked names must be top-level `function`/def names, so no const / nested names),
  14 screenshots re-shot with docs/ke_hoach/ux/chup_luong_chinh.py into docs/ke_hoach/ux/anh/ (all 14 that script writes changed),
  CHANGELOG.md UX2-L9 entry, TIEN_DO.md row UX2-L9, Plan L9 ticked in the lead's branch file.
- RUNNING when this handoff was written (background, started ~08:50 machine time): full UI sweep
  `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q tests/test_giao_dien_*.py tests/test_*ux2*.py`
  -> output in the scratchpad file full.txt (ends with a line "done"). It takes ~20+ min. A fresh session may have lost that file:
  then just rerun it. The L9 spec says: run it ONCE and report.
- Lead confirmed (09:02): continue L9 from this file; report "CODER DONE L9 | base 816e92c head <sha>" with sweep pass/fail counts and the list of the 14 re-shot PNGs
  (01_trang_dau, 02_co_dl_admin, 02_co_dl_chua_co_cho, 02_co_dl_fallback, 02_co_dl_others, 02_co_dl_results, 03_tra_cuu_HS004, 05_sau_chon_tep,
  06_sau_nhap, 07_sau_chay, 08_tieu_chi, 09_gvcn_ket_qua_lop, 10_ws_menu, 11_cai_dat).
- Still TO DO for L9: (1) read the sweep result and fix real failures (test first); (2) `.venv/bin/ruff check .`;
  (3) `.claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20` must be 7/7; (4) tests/test_a13_12_tai_lieu.py,
  test_vi_du_huong_dan.py, test_giao_dien_tieng_viet_sach.py (docs tests, were green); (5) amend CHANGELOG line "kết quả trong báo cáo L9"
  with the numbers; (6) push; (7) send "CODER DONE L9 | base 816e92c head <sha>" to the lead with: sweep result, list of 14 re-shot PNGs.
- Earlier lots: L1-L8 all PASSED by the checker. Open note for lead: admin-student rows are rebuilt on redraw so focus/caret in .lop-sua
  is lost (pre-existing; separate item if wanted).

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
- Slide-in/accordion (L8): ux2QuanSatBang observes 4 tbody ids (first 20 new data rows, never skeleton rows); details animation is CSS only
  inside @supports(interpolate-size + ::details-content) + no-preference, NOT on .menu-khac; html.tat-hieu-ung does not cover
  ::details-content (own rule). Layout tests must use offsetTop/offsetHeight (transform of the slide-in shifts getBoundingClientRect).
- Row animation keys (L8 fix1): cumulative per-tbody Set (UX2_KHOA_HANG in 00_nen.js); forgotten when the tbody is emptied for good.
  A computed animation-name stays after the animation ends: assert on class presence / MutationObserver records, not on name.
- Merge conflicts in CHANGELOG.md / TIEN_DO.md (other branches append at the same spot): keep BOTH sides, strip markers.
- Push rejected -> `git fetch origin claude/ux2-phan-hoi-nut && git merge --no-edit FETCH_HEAD` (protocol: never rebase/force).
- Stop hook "uncommitted changes": commit a clearly labelled WIP and push; only report "CODER DONE" when tests are green.

## Next steps (ordered)
1. Finish L9 verification exactly as listed under Current state (sweep result, ruff, kiem_nhanh, docs tests), then report to the lead.
2. After that wait for the checker verdict on L9 (FIX L9 -> test first, minimal fix, related tests, report "CODER DONE L9 fixN").
4. Each lot: failing test first -> minimal code -> related tests -> ruff -> kiem_nhanh 7/7 -> CHANGELOG + TIEN_DO row `UX2-L<n>` ->
   tick Plan in the lead's branch file only if lead asks (lead ticks) -> commit -> push -> message lead.

## Files touched (whole job so far; L9 adds HUONG_DAN_SU_DUNG.md, docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/ke_hoach/ux/anh/*.png x14)
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
| 2026-11-21 | Sonnet (coder) | L8 smooth transitions built + reported; merged origin/main (MT1); handoff refreshed | head fef2862 |
| 2026-11-21 | Sonnet (coder) | L8 fix1 (animate only genuinely new rows) reported; handoff refreshed | head a71baec |
| 2026-11-21 | Sonnet (coder) | L9 docs + 14 screenshots + code map written, WIP-committed; full UI sweep running; handoff (hook fired mid-L9) | WIP, see git log |
| 2026-11-21 | Sonnet (coder) | handoff refreshed again (hook); full UI sweep still running, nothing else changed | head 21c488c |
