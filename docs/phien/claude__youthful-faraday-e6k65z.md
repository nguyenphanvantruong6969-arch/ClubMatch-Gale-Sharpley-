# Branch handoff: claude/youthful-faraday-e6k65z

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Check that manual (kiosk/UI) entry and the Excel "Sổ nhập" are in sync, and that data entered by hand but absent from the
Excel is still considered. Working item code: SN-COT-LA (TEMPORARY; Truong has not given an official registry code).

## Plan (written by Opus; ticked by Sonnet)
No Opus plan: small request handled directly by Sonnet at Truong's request.
- [x] Round-trip audit (enter by hand -> export -> import into empty DB -> diff every table)
- [x] Warn when a headed-but-unrecognised column holds data (both sheets), test first
- [x] CHANGELOG, TIEN_DO, handoff
- [ ] Truong to confirm or replace the item code SN-COT-LA

## Current state (overwrite each handoff)
- Done: `so_nhap_canh_bao_cot_la` warning (preview and real import). Pushed; no PR opened.
- Tests: `tests/test_so_nhap_cot_la.py` (5). Related group (so_nhap, so_mau, xuat_du_lieu, i18n, skill_, ws_so_nhap, sm2, a14): 546 passed, 4 skipped. `kiem_nhanh.py` 7/7.
- soat-ma tiers: only tiers 2 and 4 apply (no algorithm or UI change). Tier 4 mutation: dropping the "has data" condition is caught; dropping `i not in da_nhan` is an equivalent mutant (check is duplicated in the callers), not a weak test.
- Open: none blocking.

## Decisions and gotchas (keep short)
- Option A (Truong, 2026-11-24): test entries for clubs the student did not rank stay OUT of the Excel (no schema change). Already announced at export (`n_thi_ngoai_nv`, `xuat_kq_dau_vao_thieu`); no effect on results. Option B (extra optional sheet) needs its own registry item and Opus plan (rule 12).
- Re-importing an Excel merges: hand-entered students/clubs not in the file are kept.
- Hand-entered students without Wharton points block `run_pipeline` (`wharton_chua_dung_het`): correct.
- English i18n text must not contain "you" (`chu_cam`).

## Next steps (ordered)
1. Truong gives the official item code; rename in CHANGELOG.md and TIEN_DO.md.
2. Open a PR only if Truong asks.

## Files touched
- so_nhap.py: `_ten_cot_la`, `cot_la` meta for both sheets
- api_nhap.py: `_canh_bao_so_nhap` emits the warning
- i18n_errors.py, i18n_loi.js: message `so_nhap_canh_bao_cot_la`
- tests/test_so_nhap_cot_la.py: new
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, this file

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-24 | Sonnet | Sync audit, SN-COT-LA warning, docs | Option A chosen for out-of-preference test entries |
