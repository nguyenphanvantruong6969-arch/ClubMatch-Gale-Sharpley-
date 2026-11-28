# Branch handoff: claude/serene-goldberg-2cjcxe

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

## Plan (written by Opus; ticked by Sonnet)
- [ ] L1 `chi_tieu_ct1.py` (pure, new file): `chi_so_clb_ct1`, `khuyen_nghi_chi_tieu`, `ghep_buoc_chuyen`. Tests first.
- [ ] L2 API `get_xem_xet_chi_tieu` (read-only) incl. step-by-step re-solve via `_giai_trong_bo_nho(..., sao_luu=False, sua_clb=...)`.
- [ ] L3 UI: new view inside the results tab, 4 sections, hand-written SVG/divs, vi+en strings. One Chromium test.
- [ ] L4 docs: CHANGELOG, TIEN_DO, registry line CT1, HUONG_DAN_SU_DUNG short paragraph; `soat-ma`; push.

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
- Done: design (mockup), simulation, this plan, protocol. No product code yet.
- Next: coder starts L1.

## Files touched
- docs/phien/CT1_BAN_MAU.dc.html: target design.
- docs/phien/CT1_GIAO_THUC.md: protocol + prompts.
- du_lieu_test/ct1_mo_phong/*.py: simulation that chose the rule (SIMULATED data).

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-28 | Opus (planner) | Brainstorm, 4-round simulation, mockup v3, plan + protocol | no product code (rule 12) |
