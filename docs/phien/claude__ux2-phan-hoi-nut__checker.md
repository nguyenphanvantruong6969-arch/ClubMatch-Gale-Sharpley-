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
