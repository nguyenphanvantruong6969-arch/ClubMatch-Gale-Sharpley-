# Checker log — MT1 (branch claude/mt1-bo-muc-tieu)

## L1 | 016f613..6909f06 | NO BUGS
- Box met; 31 tests pass; ruff clean; diff additive only (invariant 1 trivial).
- Edge: co_hoi with club reserves present == pure lottery (2 sim datasets); capacity 1; empty/unknown group.
- Notes for L2: (a) danh_cho leaves tiers/score_scope -> may read as tuy_chinh; (b) co_hoi + wharton=true -> mt_* message;
  (c) persist muc_tieu {id,nhom}, test reload; (d) coder wrote code before test (process only).

## L2 | 0a89219..bd93958 | NO BUGS
- 83 tests pass (mt1 api+pure, gt3_phan_quyen); ruff clean.
- wharton: co_hoi turns it off (explicit True is rejected by _chuan_hoa and the engine) = acceptable deviation; L4 must show canh_bao; nang_luc after co_hoi does not restore Chia 100 (Undo does).
- muc_tieu/truoc not in luat_xep (checked with non-default co_hoi run); Undo exact (config + every club), twice-safe.
- gt3 exception list: only get_muc_tieu added. Weak test: luat_xep leak test uses default rules (None) — add co_hoi variant.

## L3 | 2734cf7..f45708a | 1 BUG
- BUG: bao_cao_muc_tieu with muc_tieu.truoc missing/{} => counterfactual keeps card seats => silent "0 helped / 0 gave way". Expect co_so_sanh False or mt_* error + test.
- OK: run_thu refactor is a verbatim move (268 tests, ruff, kiem_nhanh 7/7 after fetching origin/main); zero writes (table sha, .bak count, mtime); suppression 1-4 in backend; trial run newest ignored; medal -> mt_uoc_tinh_fa.

## L3 fix1 | 6159eb2..7da70ad | 1 BUG (test only)
- Product fix OK: truoc missing/{} => co_so_sanh False, no fake 0s; uoc_tinh has no analogous issue.
- BUG: test_muc_tieu_khong_ro_ri_* flaky — dau_van_tay_chay.luc (timestamp) not excluded from the comparison. Exclude "luc".

## L3 fix2 | e02b83c..859d9c3 | NO BUGS
- Only "luc" added to the excluded columns; dau_van_tay still compared; 5x270 passed; ruff clean.

## L4 | a563622..3715bd8 | 2 BUGS (small)
- BUG1: mt1_da_theo "Lần xếp gần nhất đã theo mục tiêu này." is false when last run used another goal (only 0 moves). Reword to outcome ("Không em nào đổi chỗ…").
- BUG2: wizard step 3, Chia 100 + co_hoi silently flips first question to "Chỉ xếp thứ tự" with no note (Settings shows it).
- OK: clicks 1/1/1/2 counted; Undo x2; teacher UI hidden + 5 backend refusals; words; contrast/size/focus/1024; ux1 test edit necessary.
