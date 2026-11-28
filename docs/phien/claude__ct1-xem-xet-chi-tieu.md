# Branch handoff: claude/ct1-xem-xet-chi-tieu

> Fresh session: read CLAUDE.md, then THIS file, then `docs/phien/CT1_GIAO_THUC.md`. English, ≤150 lines.

## Feature / goal
**CT1 — "Xem xét chỉ tiêu" (quota review) tab.** Hackathon item. The school only gets CSV exports today; it needs
ONE simple screen that says which clubs to raise/lower, by how much, and what happens after each change.
Target design = `docs/phien/CT1_BAN_MAU.dc.html` (also live: claude.ai artifact "Xem xét chỉ tiêu CLB"). It is a
Design-canvas file: read its markup and inline styles as the spec; do NOT copy the `<x-dc>`/`support.js` runtime.
New registry item code CT1 (Truong asked for it 2026-11-28; add one line to the registry + JSON in L4).

Four sections, top to bottom (see mockup):
1. **Khuyến nghị** sentence ("Chuyển N chỗ từ A CLB đang thừa chỗ sang B CLB đang thiếu chỗ.") + 4 before→after
   tiles: em vào CLB thích nhất (x → y / N em), em không có CLB (x → y), em xếp tốt hơn (k), em xếp kém hơn (k).
2. **Kết quả sau từng bước**: stacked progress bar (baseline + one segment per step), unit squares for unassigned
   students, then an ordered list of steps (donor chip → recipient chip, "Vì sao" sentence, after-step numbers,
   "k em lên, j em xuống"; a warning line when j > 0).
3. **CLB nào thiếu chỗ, CLB nào thừa chỗ?**: per club two bars (capacity grey, NV1 count coloured tăng/giảm/giữ).
4. **Chỉ tiêu đề xuất** table + `<details>` "Phần mềm tính đề xuất như thế nào?".
Dropped on purpose: quadrant chart, trade-off curve, score histogram (Truong found the quadrant hard to read).

## Design rules (MUST; Truong 2026-11-28: "follow the 2 design rules we agreed")
Source: "Design rule" sections of `docs/phien/claude__ux4-quan-ly-de-hieu.md` (Hick's law, Von Restorff), as
applied to the Kết quả tab by UX5A (`tests/test_giao_dien_ux5a_l2.py`… must stay green). Overrides the mockup.
- **Entry point does not grow the Kết quả budget:** CT1 opens from ONE secondary control placed where UX5A puts rare
  actions (the existing `details.menu-khac` / "Thêm ▾" of the Kết quả tab), admin only (`data-quyen="quan_tri"`).
  The CT1 view is its own panel; UX5A Hick/Von Restorff tests unchanged and green.
- **Hick budgets inside CT1** (count VISIBLE enabled buttons/selects/inputs/links per panel, ≤ 7):
  1. "Khuyến nghị" panel: 1 control = gold "Xuất bảng đề xuất (CSV)". **No "Áp dụng làm chỉ tiêu kỳ sau" button**
     (the mockup's gold button writes capacities: out of scope, read-only item) and no "Xuất PDF".
  2. "Kết quả sau từng bước": per step "Xem em nào đổi chỗ (k em)" secondary + one "Xuất bảng đối chiếu (CSV)"
     secondary. Lists closed by default. If steps > 6, show 6 and a "Xem thêm bước" link.
  3. "Tự thử một thay đổi": collapsed `<details>` by default (progressive disclosure); inside: 3 selects + 1 gold
     "Xếp lại với chỉ tiêu này" + copy/CSV secondary (≤ 5). "Số chỗ" select ≤ 3 options shown (1, 2, 3).
  4. "CLB nào thiếu chỗ…": no buttons; the method text stays in one `<details>`.
  5. One plain link to Tiêu chí (GT2) for priority changes.
- **Von Restorff:** at most ONE `.btn-primary` visible per panel (panel 2 and 4 have none). Green/gold only carry
  meaning (tăng / giảm), always with text (+4, −3, "Mất chỗ", "Lên NV1"), never colour alone (WCAG 1.4.1). No accent
  on headings, eyebrows ("KHUYẾN NGHỊ" in muted ink), icons or counts. A step where someone loses a seat or drops shows
  an ALERT-style text line, not a button. After "Xếp lại", the result block is highlighted briefly (respect
  `prefers-reduced-motion` and `html.tat-hieu-ung`), meaning also stated in text. No `.btn-danger` anywhere.
- Test: `tests/test_giao_dien_ct1.py` adds a "Hick budget" + "Von Restorff" check for each CT1 panel (reuse helpers in
  `tests/_ux5a_chung.py`), as admin; as teacher the entry point is not visible.
- Working prototype (shows behaviour, not budgets): claude.ai artifact "Thử chỉ tiêu CLB"; its data generator is
  reproducible from `du_lieu_test/ct1_mo_phong/`.

## Plan (written by Opus; ticked by Sonnet)
- [x] L1 `chi_tieu_ct1.py` (pure, new file): `chi_so_clb_ct1`, `khuyen_nghi_chi_tieu`, `ghep_buoc_chuyen`. Tests first.
- [x] L2 API `get_xem_xet_chi_tieu` (read-only) incl. step-by-step re-solve via `_giai_trong_bo_nho(..., sao_luu=False, sua_clb=...)`.
- [x] L3 UI: new view inside the results tab, 4 sections, hand-written SVG/divs, vi+en strings. One Chromium test.
- [x] L4 docs: CHANGELOG, TIEN_DO, registry line CT1, HUONG_DAN_SU_DUNG short paragraph; `soat-ma`; push.

## Decisions and gotchas (keep short)
- Rule (tested in simulation, `du_lieu_test/ct1_mo_phong/`, SIMULATED data): target_c = round(T·nv1_c/N); raise only
  if `chua_dap_c ≥ 1`; clamp to cap·(1±tran) (default tran 0.20) and `toi_thieu` (default 8, never above current
  cap); rebalance by ±1 so Σ cap_moi == T (raise priority chua_dap/cap desc, lower priority the reverse; ties by club_id).
  Beat "keep as is" in 18/18 next-year scenarios. Existing `fa_daa.goi_y_chi_tieu` drops total seats (566–653 for
  800 students) → do NOT use it; log as known issue in CHANGELOG only (separate item).
- `chua_dap_c` = students who rank c above the club they got (unassigned = below every listed club), per session.
- NV1 is per session: reuse the ROW_NUMBER-per-buoi logic of `get_club_fill_stats` (rank column runs across sessions).
- Free clubs (`loai == TU_DO`) and clubs with no capacity are excluded from recommendations.
- Steps: pair donors and recipients greedily (largest |delta| first, ties club_id) → list of (from, to, k), each
  total-neutral. Re-solve cumulatively; baseline = re-solve with unchanged caps (must equal official match_results;
  if not, return a warning code and still show numbers). Locked STB only (never re-draw). No DB writes, no
  `run_history` row, no backup (`sao_luu=False`), invariants 1–5 untouched.
- If `_giai_trong_bo_nho` refuses (e.g. `mt_thu_chua_ho_tro_loai`), return recommendations without step results
  plus that error code; UI shows section 1/3/4 and a plain message in place of section 2.
- No new library. Colours: tăng `--chart-general`, giảm `--gold` (text `--gold-text`), giữ `--chart-khong-nhan`.
- Labels: "CLB thích nhất" not "NV1"; "muốn vào mà chưa được" not "cầu chưa đáp ứng". Banner "dữ liệu mô phỏng"
  only in demo data, not in product UI.
- Expected numbers on `du_lieu_test/SO_NHAP_TEST.xlsx` with locked seed 42 (use as a regression test):
  steps Bóng rổ→Bóng đá 4, Âm nhạc→Tiếng Anh 3, Tình nguyện→Tin học 2, Văn học→Mỹ thuật 2;
  NV1 64→67→69→73→74; unassigned 12→11→11→10→8; final 15 better / 0 worse. If the app's seed path gives other
  numbers, trust the app and update the test, but the rule outputs (cap_moi) must match.

- Verifiability (added 2026-11-28 after a planning loop): in-product = per-step "who changed" list + CSV (admin only,
  names inside); outside = 3 hand-checkable quota cases on the 8-student scenario (verified by Opus with
  `run_rbda`, identical on 5 seeds) + regression test on SO_NHAP_TEST. Recommendation rule yields NO step on the
  8-student set (±20 % and min size), so hand cases go through `buoc_tu_chon` (custom what-if).
- Reuse, do not rewrite: `tieu_chi.so_sanh_lan_chay` (pure diff, GT2 definition), `_giai_trong_bo_nho`,
  `cac_dong_match_results`, `_khoa_xuat`/`_ghi_csv`. Priority-change demo = existing GT2 screen (link only).

## Current state (overwrite each handoff)
- L1–L4 and CT1-FIX … FIX5 are DONE and pushed; never redo them. Entry point is now a dedicated button "Gợi ý thay đổi chỉ tiêu"
  (`#btnCt1Mo`, `.btn-secondary.btn-goi-y`, admin only) at the right of the Kết quả toolbar, next to the gold Excel button (FIX4, Truong's request).
- FIX5 fixed the 6 red tests of CI run 46102624745. The CI run on head `a724f9e` (run 46105606804) was still running at handoff: NOT yet seen.
  Do not write `Status: DONE` until "Tests (rbda-kiosk)" is green on the latest head. No PR is open yet.
- A scheduled self-check (trigger `trig_013Q7CdabaVbAs7eyzf11RkT`, ~04:18 UTC) may fire into the old session; ignore it in a new one.
- Two sessions (Sonnet + Opus) pushed to this branch in parallel; every push cancels the running CI. Push only after fetch + merge, and not while CI runs.

## Next steps (in order)
0. FIRST `git fetch origin && git checkout claude/ct1-xem-xet-chi-tieu && git pull origin claude/ct1-xem-xet-chi-tieu` (this file is not on `main`).
1. Check CI for the latest head (`mcp__github__actions_list`, branch filter, perPage 1). Red → extract FAILED lines (large logs are saved to a file; use python),
   minimal fix, re-run those tests locally, fetch + merge, push. Green → `Status: DONE <sha>` here, push, then open the PR (Truong said "after ci green open PR");
   mirror the repo PR template if any, end the description with the attribution lines. Tell Truong in Vietnamese (≤10 lines; 3 steps: load SO_NHAP_TEST.xlsx → run →
   Kết quả › nút Gợi ý thay đổi chỉ tiêu).
2. Merge, never rebase. In a fresh container: `pip install playwright` for the Python Chromium tests (browser is in /opt/pw-browsers). `pip install pytest-xdist` was blocked by the classifier: do not retry.
3. Before each push run the WHOLE related UI set, not only the lot's tests (CI found 3 rounds of repo-wide guards: nhật ký labels, i18n prefix tests, UX6 25-hint budget, UX6-L2 table selector).

## Needs Truong
1. ~~Multi-session units~~ FIXED (CT1-FIX). 2. ~~o_chua_co~~ FIXED. 3. Chose (b) warning line (`#ct1KemNhieuHon`); confirm or veto. 5. Truong may want the new button to be THE gold button (then Excel becomes secondary) or the CT2 ideas: nav item, text in the Việc tiếp theo bar, verdict sentence at top (not started; needs an item code). 4. ~~contrast / ±1 test~~ FIXED.
- Deviations: >6 steps shows 5 + "Xem thêm bước" (keeps panel ≤7 controls); Tiêu chí link uses `ux1aMoNangCao()` (GT2 now lives in Quản lý › Cách xếp, not "Chi tiết").
- Gotchas learnt: repo lint (`kiem_nhanh` chu_cam) forbids the words "em"/"you" in visible strings → use `{person_l}`/`{slot_l}`; wharton default is ON so tests set `{"wharton": False}`; `o_chua_co` = step from which a student stably has a club (app gives [1,2,3,4], mockup's [1,3,4,4] was illustrative).

## Files touched
- New: `chi_tieu_ct1.py`, `api_chi_tieu.py`, `js/20_xem_xet_chi_tieu.js`, `tests/test_ct1_khuyen_nghi.py`, `test_ct1_api.py`, `test_ct1_ca_kiem_tay.py`, `test_giao_dien_ct1.py`, `docs/ke_hoach/BAO_CAO_SOAT_MA_CT1.md`, `docs/phien/CT1_KICH_BAN_DEMO.md`.
- Edited: `api.py`, `phan_quyen.py`, `i18n_errors.py`, `i18n_loi.js`, `index.html`, `i18n.js`, `style.css`, `js/_danh_sach.txt`, `tests/_ux5a_chung.py`, `tests/test_gt3_phan_quyen.py`, `tests/test_mt1_uoc_tinh.py`, CHANGELOG, TIEN_DO, registry (md + json), HUONG_DAN_SU_DUNG, NHAP_TAY, SO_LIEU_DA_KIEM_CHUNG.
- Planning files: `docs/phien/CT1_BAN_MAU.dc.html`, `CT1_GIAO_THUC.md`, `du_lieu_test/ct1_mo_phong/*.py` (SIMULATED data).

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus (planner) | Brainstorm, 4-round simulation, mockup v3, plan + protocol | no product code (rule 12) |
| 2026-11-28 | Opus (planner) | Moved to item branch; added Design rules (Hick, Von Restorff) | planning was on claude/serene-goldberg-2cjcxe |
| 2026-11-28 | Sonnet (coder) | L1 `chi_tieu_ct1.py` + 27 tests | tie-break pairing: recipients by chua_dap/cap desc then id (needed to match expected step order, since clb_mythuat < clb_tinhoc) |
| 2026-11-28 | Sonnet (coder) | L2 API + 22 tests, i18n codes `ct1_*`, phan_quyen admin-only, ChiTieuMixin in api.py | also adjusted 2 brittle tests (gt3 phan_quyen allow-list, mt1 'last 12 keys') to include CT1 |
| 2026-11-28 | Sonnet (coder) | L3 UI + 13 Chromium tests; `_ux5a_chung.mo_ux5a` got optional `so_nhap`/`rules`/`rong` | UI text avoids "em"/"you" (lint): uses {person_l}/{slot_s} |
| 2026-11-28 | Sonnet (coder) | L4 docs + 3 hand cases + soat-ma report | findings 1–5 in BAO_CAO_SOAT_MA_CT1.md; none fixed (report-only) |
| 2026-11-28 | Sonnet (coder) | Handoff at ~400k context: state rewritten, awaiting CI | next session checks CI and finishes per protocol §4 |
| 2026-11-28 | Sonnet (coder) | Second handoff: added step 0 (check out the branch first) after a new chat restarted at L1 | state was correct on origin; that chat was on the wrong branch |
| 2026-11-28 | Opus | CT1-FIX5: full suite locally, fixed the 6 CI reds (see CHANGELOG) | no product .py changed |
| 2026-11-28 | Sonnet | CT1-FIX…FIX5: soat-ma findings 1,2,3b,4,5; advisor UI review; dedicated entry button; CI-red fixes | handoff at ~400k context; CI on a724f9e pending, no PR yet |
