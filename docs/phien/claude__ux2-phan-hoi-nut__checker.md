# Checker notes: UX2 (claude/ux2-phan-hoi-nut)

## CHECKER REPORT L1 | reviewed d4f7427..9e9bbdc
verdict: 1 BUG (minor)
1. js/00_nen.js:datNutBan + data-i18n rewrite | repro: slow run_pipeline (1.5 s), click #btnRun, call
   `I18N.setLang('en')` while busy | expected: button still shows spinner + "Allocating…" until done.
   Actual: `applyStaticText` rewrites btnRun text to "Run allocation", spinner span gone, but `aria-busy="true"` and
   `disabled` remain → looks idle yet locked. Cosmetic/a11y mismatch; no crash, restored OK at end.
   Suggest: on `langchange`, if `nut.__ux2Ban` and its spans are detached, re-render busy DOM (re-call datNutBan after
   clearing state), or listen in datNutBan.

Checked OK: lot tests + sg9/chay/hieu_ung/i18n_sync green (61 passed); diff stays in §0 files (no api*/CSV/schema:
invariants 5,6,7 untouched); dblclick and double Enter -> API once; rejected promise restores icon child, minWidth,
aria-busy=false; width ≤1 px; no old "Đang chạy…" assertions in tests. Not verified: `kiem_nhanh.py` 7/7 (coder's),
`giao_vien` role, 800-row file (no table change in L1); vi/en width of other khiBan buttons only spot-checked.

## CHECKER REPORT L1 fix1 | reviewed abe72c8..f1eef14
verdict: 1 BUGS (minor)
1. js/00_nen.js:datNutBan restore | repro: button `<span id=ic>★</span> <span data-i18n="btn_run_pipeline">`, chayNut
   pending, `I18N.setLang('en')`, resolve | expected: label "Run allocation". Actual: icon kept but child span stays
   "Chạy sắp xếp" (detached nodes are skipped by applyStaticText). Fix: after restoring saved nodes, re-translate
   `[data-i18n]` descendants (and the button itself) with t().
Original bug (btnRun label/spinner on language switch) FIXED. 59 related tests passed.

## CHECKER REPORT L1 fix2 | reviewed 02bb4c6..9169da5
verdict: NO BUGS. icon + data-i18n child span now "Run allocation" after en switch while busy; button's own
data-i18n-aria-label still updated; 60 related tests passed. Note (non-blocking): a restored CHILD with
data-i18n-aria-label is not re-translated; no such button exists in index.html/js today.

## CHECKER REPORT L2 | reviewed 0eec401..8348237
verdict: NO BUGS (2 notes)
(a) width: all 13 wired buttons, vi+en, ✓ on: +0..+1 px (ceil of minWidth), back to original after; ≤1 px OK.
(b) NOTE: 18_cai_dat has NO save button wired (its saves are radio/toggle `dat_loai_clb`, `update_workspace_config`; no
    khiBan/chayNut there). CHANGELOG admits "other save buttons not wired". Plan line says coder lists them: listed OK.
(c) ✓ + setLang('en') + 2nd click inside 1.2 s: no stale ✓, no stale minWidth (ends ''), text correct. Cosmetic: after
    lang switch `is-xong` padding/minWidth(vi px) stay up to 1.2 s.
(d) chayXuat callers without nutXuat (04, 09, 03 others) unchanged path. Related tests: ux2 xong/ban, sg9, chay,
    i18n_sync, hieu_ung = 69 passed; xuat tests also run.

## CHECKER REPORT L3 | reviewed 44e7677..7f8b2f4
verdict: 1 BUG
1. style.css `:where(button,.btn,[role=button])::after` (44 px hit area) | repro: tab "others" (Xuất), real mouse click at
   centre of checkbox `#xuatKemCsv` (and `#xuatKetQua` reported covered by elementFromPoint) | expected: toggles
   the checkbox only. Actual: click lands on `btnXuatTuyChon` ::after -> export button handler fires (n=2 vs 1 on
   base CSS). Positioned ::after paints above non-positioned inputs. Fix: keep hit area but not over form controls
   (e.g. `position:relative` neighbours get `z-index:1`, or shrink ::after for buttons next to inputs, or give
   `input,select,textarea,label{position:relative;z-index:1}`), then add a test: elementFromPoint at the centre of every
   visible input/select/textarea/summary/label on all 5 tabs (vai quan_tri + giao_vien) is the control itself.
OK: other tabs/vai quan_tri + giao_vien: no stolen inputs; toast-close x clickable and closes; dark ring #9CC2FF 2px on
.nav-item and menu buttons; focus ring token 2px; state layer tests; 66 related tests passed. Note: `summary.lang-toggle`
ring is 1px (not a button; pre-existing). Not measured: 800-HS table height (diff has no table-height rule).
