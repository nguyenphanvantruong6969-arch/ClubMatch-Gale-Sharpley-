# CT1 protocol — size M-hackathon (1 coder, checker optional)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 budget rules apply). Spec, rule, expected numbers:
> `docs/phien/claude__serene-goldberg-2cjcxe.md`. Design: `docs/phien/CT1_BAN_MAU.dc.html`.

## 0. Decisions already made (do not ask Truong)
- Item CT1 on branch `claude/serene-goldberg-2cjcxe`. Read-only feature: no schema change, no CSV-contract change,
  no write to `match_results`/`run_history`, no new library. Recommendation rule and step pairing as in the branch file.
- Hackathon: speed over polish, but tests-first and invariants hold. Checker runs once at the end only if Truong asks.

## 1. Lots (must-ship: L1, L2, L3; L4 docs short)
| Lot | Files | Box (acceptance) |
|---|---|---|
| L1 | `chi_tieu_ct1.py`, `tests/test_ct1_khuyen_nghi.py` | Σcap_moi == T; clamp ±tran and toi_thieu; no raise when chua_dap==0; TU_DO excluded; deterministic ties; pairing gives total-neutral steps covering every delta |
| L2 | `api_bao_cao.py` (method `get_xem_xet_chi_tieu` on `BaoCaoMixin`, or a small mixin), `phan_quyen.py`, `i18n_errors.py` (+`tao_i18n_js.py`), `tests/test_ct1_api.py` | `{ok,data,errors}`; data = `{tong_cho, so_hoc_sinh, clb:[…], buoc:[…], truoc:{…}, sau:{…}}`; steps cumulative via `_giai_trong_bo_nho(luat, seed, chi_buoi, [], sao_luu=False, sua_clb=…)` (pattern: `api_muc_tieu.py`); no result yet → error code; DB file bytes and `run_history` row count unchanged after the call; regression numbers on SO_NHAP_TEST |
| L3 | `index.html` (one view in results tab), new `js/<nn>_xem_xet_chi_tieu.js`, `style.css`, `i18n.js` (vi+en), `tests/test_giao_dien_ct1.py` | 4 sections as in the mockup; works at 390 px width (no horizontal page scroll); empty/error states; SVG `role="img"` + `aria-label`; one Chromium test asserting headline text, N step items, table rows |
| L4 | `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, registry line CT1 (`SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json`), `HUONG_DAN_SU_DUNG.md` | short entries; known issue: `fa_daa.goi_y_chi_tieu` does not preserve total seats |

## 2. Coder loop per lot
Failing test → minimal code → the lot's test file + ≤3 related (`tests/test_du_lieu_ket_qua.py`,
`tests/test_mt1*`, `tests/test_gt2*`) `-q --tb=line 2>&1 | tail -15` → `ruff check .` →
`.claude/skills/soat-ma/kiem_nhanh.py | tail -10` → commit `CT1-L<n>: …` → push
`git push -u origin claude/serene-goldberg-2cjcxe`. Never rebase/force-push; before each lot
`git fetch origin main && git merge --no-edit FETCH_HEAD`. After L4: run `soat-ma` four tiers (report only).
UI tests: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, `--trace off`.

## 3. Stop points
- Usage limit near or context > ~400k: update "Current state" in the branch file, push, stop.
- An invariant conflict, a needed new library, or a schema/CSV change: write "Needs Truong" in the branch file, skip
  that part, continue with the rest.

## 4. Done
CI green (`tests.yml` + Windows build) → `Status: DONE <sha>` in the branch file + Vietnamese summary to Truong
(≤10 lines, 3 steps to try: load SO_NHAP_TEST.xlsx → run → open Kết quả › Xem xét chỉ tiêu).
