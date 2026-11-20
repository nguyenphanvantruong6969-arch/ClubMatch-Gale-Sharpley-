# Checker log — MT1 (branch claude/mt1-bo-muc-tieu)

## L1 | 016f613..6909f06 | NO BUGS
- Box met; 31 tests pass; ruff clean; diff additive only (invariant 1 trivial).
- Edge: co_hoi with club reserves present == pure lottery (2 sim datasets); capacity 1; empty/unknown group.
- Notes for L2: (a) danh_cho leaves tiers/score_scope -> may read as tuy_chinh; (b) co_hoi + wharton=true -> mt_* message;
  (c) persist muc_tieu {id,nhom}, test reload; (d) coder wrote code before test (process only).
