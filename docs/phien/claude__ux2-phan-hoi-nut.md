# Branch handoff: claude/ux2-phan-hoi-nut

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).

Status: IN PROGRESS (lead running L3, 2026-11-21). Protocol: docs/phien/UX2_GIAO_THUC.md

## Feature / goal
New item **UX2 — positive interaction feedback** (asked by Truong 2026-11-21; new item like UX1/XP1, tracked in
`TIEN_DO.md`, NOT in the 33-item registry). 11 low-risk UI improvements so every click visibly answers: busy state +
double-click guard, ✓ after save/export, 44 px hit areas, one focus ring, Material-style state layer, inline field
errors, 4-phase run progress, guided empty states, skeleton loading, smooth list/accordion transitions.
Scope: `style.css`, `js/*.js`, `index.html`, `i18n.js` (+ `i18n_errors.py` → `python tao_i18n_js.py` only if a NEW
error code is truly needed). NOT touched: algorithm, `api*.py` behaviour, CSV, schema, `{ok,data,errors}`
(invariants 1, 6, 7). Branched from `origin/main` @ `30cd849` (UX1 + XP1 merged).

## Decisions (Opus plan, 2026-11-21)
- ONE busy helper for #2 and #13: extend the existing `chayNut` / `khiBan` (`js/00_nen.js`, SG-9) with a new
  `datNutBan(nut, bat, khoaNhan)`; never write a second locking mechanism. `capNhatKhoaVanHanh` (btnRun) uses it.
- Busy label for btnRun: new key `ux2_dang_xep` ("Đang xếp…" / "Allocating…"); other buttons keep `dang_xu_ly`.
- Spinner and ✓ are real child `<span aria-hidden="true">`, NOT pseudo-elements (`::before`/`::after` are kept free
  for #1 state layer / #8 hit area). Meaning never depends on motion: text + `aria-busy` carry it.
- `html.tat-hieu-ung *{animation:none!important}` already kills every animation: spinner becomes a static ring;
  that is accepted. Every NEW animation/transition also sits under `@media (prefers-reduced-motion: no-preference)`
  or has a `reduce` override.
- #11 is DISPLAY ONLY: `run_pipeline` returns steps only at the end, so during the run all phases show "running"
  (indeterminate); after the return they map from `steps`. Live progress would need a backend change: out of scope.
- Inline errors (#7) map backend `errors[].code` → input id in a UI-side table; texts still from `trErr`
  (one source, invariant 6). Non-field errors stay toasts.
- i18n keys prefix `ux2_`; CSS block marked `/* UX2 */`; new tests `tests/test_ux2_*.py` (+ Chromium ones
  `tests/test_giao_dien_ux2_*.py`). No `alert()`/`confirm()`, no new library, no Agent tool.

## Plan (written by Opus; ticked by Sonnet). Order = dependency order; each lot = one commit `UX2-L<n>: …`
Lot L1 ✅ PASSED (checker NO BUGS, head 9169da5, 2 fix rounds) — #2 busy state + #13 double-click guard (shared helper; everything else builds on it)
- [x] Test first `tests/test_giao_dien_ux2_ban.py` (pattern: `test_giao_dien_sg9_nut_ban.py`, slow API via
      `_cham` in `test_giao_dien_chay.py`): during a slow call the button has `disabled`, `aria-busy="true"`,
      class `is-ban`, one `.ux2-xoay` span, label = `t(nhan)`; width changes ≤ 1 px; double click → API called
      ONCE; after success AND after a rejected promise: `aria-busy="false"`, original children restored (button
      with an icon keeps it). btnRun: label "Đang xếp…", width stable, run called once on dblclick.
- [x] `datNutBan(nut, bat, khoaNhan)` in `js/00_nen.js`: lock `style.minWidth` to current width, save/restore
      child nodes (not only textContent), `aria-busy`, spinner span. `chayNut` and `khiBan` call it.
- [x] `capNhatKhoaVanHanh` (`js/02_van_hanh.js`) uses it for btnRun instead of setting `textContent`.
- [x] CSS `.ux2-xoay` 14 px ring, `@keyframes ux2Xoay`; static under both motion switches (test computed
      `animation-name` = none with `html.tat-hieu-ung` and with `reducedMotion:"reduce"`).
- [x] Update tests that assert the old "Đang chạy…" label deliberately; list them in CHANGELOG.
Lot L2 ✅ PASSED (checker NO BUGS, head 8348237) — #3 ✓ after save / export (needs L1)
- [x] Test `tests/test_giao_dien_ux2_xong.py`: success → `.ux2-xong` visible on the same button within 100 ms,
      gone at 1.6 s (shown ≈1.2 s), width stable; `ok:false` → no ✓; under `tat-hieu-ung` ✓ still shows (state,
      not motion) without animation.
- [x] `chayNut` option `xongKhi: (res) => res.ok` → `nutDaXong(nut)`; wire save + export buttons (`chayXuat`
      in `js/03_ket_qua.js`, save buttons in `05_quan_ly`, `06_cham_diem`, `18_cai_dat`; coder lists them).
Lot L3 — #8 hit area, #9 focus ring, #1 state layer (CSS button system)
- [x] Test `tests/test_giao_dien_ux2_nut.py`: every visible `button, .btn, [role=button]` on each main tab has a
      hit area ≥ 44×44 px (bounding box, or `elementFromPoint` at centre ±22 px returns the button);
      `touch-action: manipulation`; Tab focus shows the SAME `outline` (width, colour token) on 5 sample
      button kinds; mouse click shows no ring (`:focus-visible` only); ring contrast ≥ 3:1 on `--paper` and
      `--gold` (reuse contrast helper of `test_giao_dien_tro_nang.py`).
- [x] State layer: hover 8 %, focus 10 %, pressed 12 % overlay via `inset box-shadow` or `::after` with
      `currentColor` (no colour change of the base token); disabled = no layer. Test computed style per state.
- [x] Compact buttons (`.btn-nho`, `.btn-ghost`, icon/close buttons) keep visual size; hit area grows with a
      transparent pseudo-element or padding (grep `::after`/`::before` users first; 6 `::after` exist).
- [x] Remove duplicated per-component `:focus-visible` rules only when the shared one covers them.
Lot L4 — #7 inline field errors
- [ ] Test `tests/test_giao_dien_ux2_loi_o.py`: invalid seed, admin add-club form, admin add-student form, a
      score input (`06_cham_diem`): input gets `aria-invalid="true"`, class `is-loi`, `aria-describedby` → a
      `.loi-o` text = translated message; focus on the FIRST invalid input; shake 200 ms (`ux2Rung`) only when
      motion allowed; typing clears the error. Non-field errors still toast.
- [ ] Helpers `baoLoiTaiO(o, chu)`, `xoaLoiTaiO(o)`, `baoLoiForm(goc, errors, bangMaO)` in `js/00_nen.js`;
      reuse in `04_nhap_tai_cho` / `06_cham_diem` existing `aria-invalid` code (unify, keep behaviour).
Lot L5 — #11 4-phase progress (display only; needs L1)
- [ ] Static test `tests/test_ux2_tien_trinh.py`: the JS map `UX2_PHA` (Kiểm tra = backup, validate; Xếp =
      stb_lottery, rbda_cascade; Ghi = write_results, rollback; Xuất = export) lists phases in invariant-5
      order and covers EVERY `"step": "<name>"` in `api.py` (parse it; `unknown` explicitly ignored).
- [ ] Chromium test: running → all 4 `aria-current`/running; success → 4 done; validate error → phase 1 error,
      2–4 "not reached"; stepper details unchanged (T3-06 collapse still works).
Lot L6 — #12 guided empty states
- [ ] Helper `veTrangThaiRong(hop, {chu, huongDan, nut})`; apply to `resultsEmptyState`, `kqRong`,
      `adminClubEmptyState`, `adminStudentEmptyState`, `scoringPersonEmpty`, `clbEmpty` (+ others if cheap).
- [ ] Test: each shows guidance + ONE primary button; click goes to the right tab / focuses the right input;
      a `giao_vien` never sees an admin-only action (respect `data-quyen`).
Lot L7 — #6 skeleton loading
- [ ] `hienKhungCho(tbody, soCot, soDong)` shown only if load > 300 ms (no flicker); `aria-busy` on the table;
      results table, admin student table, run history, admin club table.
- [ ] Test: slow API → skeleton after 400 ms, gone after data; fast API → never inserted (MutationObserver);
      shimmer off under both motion switches.
Lot L8 — #10 smooth transitions
- [ ] New list rows slide in (≤ 20 rows, 180 ms, no stagger beyond 200 ms total); `<details>` accordions open by
      height via `::details-content` + `interpolate-size` inside `@supports` (fallback: instant).
- [ ] Test: animation/transition present with effects on; none with `tat-hieu-ung` / reduced motion; accordion
      content still visible and readable after open (no clipped text).
Lot L9 — docs, screenshots, verify
- [ ] `HUONG_DAN_SU_DUNG.md` short section; re-shoot changed `docs/ke_hoach/ux/anh/` screens; code map in
      `CLAUDE_CHI_TIET.md`; `kiem_nhanh.py` 7/7; CHANGELOG + TIEN_DO rows per lot.

## Acceptance (kiem_nhan)
- Every box above ticked with its test green; related old UI tests green (`test_giao_dien_sg9_nut_ban.py`,
  `test_giao_dien_chay.py`, `test_giao_dien_hieu_ung.py`, `test_giao_dien_tro_nang.py`, `test_i18n_sync.py`,
  `test_van_phong_tu_nhien.py`, `test_ws_nhan.py`).
- Invariant 1: `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7 after every lot (UI-only change must be 0 diff).
- `git diff origin/main --stat` touches no `rbda_priority_pipeline.py`, no CSV/schema, no API return shapes.
- Feedback latency: `aria-busy` set ≤ 100 ms after click (measured in L1 test).

## Current state (overwrite each handoff)
- Done so far: L1 passed (9169da5), L2 passed (8348237; 13 buttons wired, 18_cai_dat has no save button).
- In progress: L3 sent to coder (GO L3). Open problems: none.

## Sessions
| Role | Model | Session id | Started | State |
|---|---|---|---|---|
| lead | Opus | session_01VfPzNumBTQB5odHhUwJqun | 2026-11-21 | running |
| coder | Sonnet | session_01VfPzNrAmRdig3chvfTGSSu | 2026-11-21 | running |
| checker | Sonnet | session_01VfPzNv4Zy4WBo2xtuj4piV | 2026-11-21 | running |

## Needs Truong (1 line each + recommendation)
- L3 hit area: dense table/list buttons and sidebar group headers are 24 px (AA), not 44 px. Recommend: accept; revisit only if teachers mis-tap on the touch kiosk.

## Decisions and gotchas (keep short)
- Lead L3 (2026-11-21): 44 px everywhere except edge-to-edge rows: .nav-item gets min-height 44; .nav-nhom-nut + dense td/li buttons ≥ 24 px (WCAG 2.5.8 AA) instead of 44 (they would overlap neighbours); .ranking-list li 20 px if 24 overlaps. Focus ring token #173F8C (≥3:1 on --gold).
- `chayNut` swaps `textContent` today: a button with an icon loses it. L1 fixes by saving child nodes.
- `applyStaticText` rewrites `[data-i18n]` on language switch: a busy button must not be rewritten mid-call.
- Screenshot-based docs (`docs/ke_hoach/ux/anh/`) will drift: re-shoot only in L9.

## Next steps (ordered)
1. Lead follows `docs/phien/UX2_GIAO_THUC.md`.

## Files touched
- docs/phien/claude__ux2-phan-hoi-nut.md, docs/phien/UX2_GIAO_THUC.md: plan + protocol
- docs/ke_hoach/TIEN_DO.md, CHANGELOG.md: UX2 planning row

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-21 | Opus (planner) | Goal, decisions, Plan L1–L9, protocol | no product code |
