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
