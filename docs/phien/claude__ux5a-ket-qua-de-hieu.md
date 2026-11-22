# Branch handoff: claude/ux5a-ket-qua-de-hieu

> Read CLAUDE.md, then THIS file, then `docs/phien/UX5_GIAO_THUC.md` (Track A) and the "Design rule" sections of
> `docs/phien/claude__ux4-quan-ly-de-hieu.md`. English. Cap 150 lines.

## Feature / goal
Truong (2026-11-22): apply Hick's law (few equal choices) and Von Restorff (one thing stands out) to the sidebar group
**Kết quả & phiếu** = tab `Kết quả` (`#view-results`, with the `#ux1bPanel` "Theo {cohort_l} và báo cáo" block, the
results table, the "Lưu PDF"/lookup-code/"Chế độ {person_l} tra cứu" row) and tab `Chi tiết và xuất tệp`
(`#view-others`, ~420 lines of HTML: exports, detail tables, round-2 button). Item code **UX5A** (tentative).
Both tabs must also be tidy for the TEACHER role (`body[data-vai="giao_vien"]`).

## Known starting points (planner, not yet audited with screenshots; coder audits first)
1. `#view-results`: several export/print/PDF buttons at the same visual weight; `btnGtCheDoHs` is `.btn-primary` next to
   other actions (check how many gold buttons are visible at once).
2. `#view-others`: very long page; `btnChayVong2` ("Chạy vòng 2") is `.btn-primary` inside a big detail page.
3. Export menu `#xuatMenu` and PDF menu already use `<details class="menu-khac">`: reuse that pattern for rare actions.
4. Teacher view: admin-only controls are hidden by `data-quyen="quan_tri"`; confirm nothing the teacher sees is gold
   when it is not their next step, and that the teacher still reaches "Theo {cohort_l}", lookups and per-class exports.

## Plan (ticked by Sonnet)
- [x] **L1 Audit + words + choice map (MUST, stop point).** `docs/ke_hoach/ux/UX5A_TU_NGU.md`: (1) per tab, count of
      visible enabled controls NOW (admin and teacher) + number of `.btn-primary` visible; (2) table of changed strings:
      key | old VI | new VI | new EN | why; (3) choice map: which ONE control is gold per panel, which go under
      "Thêm ▾" / `<details>`. **MILESTONE 1: Truong approves before code.**
- [x] **L2 `Kết quả` tab (MUST).** ≤ 7 visible controls before opening a fold; one gold = the next step; the rest
      secondary or inside the existing menus; one-line purpose under the title.
- [ ] **L3 `Chi tiết và xuất tệp` tab (MUST).** Same budgets; exports grouped behind one "Xuất tệp ▾"; the single gold
      action is chosen in L1; long detail tables stay reachable (collapsed by default if > 1 screen, never removed).
- [ ] **L4 Teacher view + tests (MUST).** Playwright "Hick budget" + "Von Restorff" tests for both tabs, admin and
      teacher; jargon test (no "cấu hình", "suất", raw ISO timestamps in visible text). **MILESTONE 2: checker + Truong.**

## Acceptance
- ≤ 1 visible `.btn-primary` per panel; `.btn-danger` only where data is destroyed; banner/alert buttons not gold.
- Visible enabled controls ≤ budget per panel (UX4 branch file), as admin AND as teacher.
- Nothing removed: every hidden capability reachable in ≤ 2 clicks, element ids unchanged, `{cohort_l}`-style placeholders kept.
- Default results byte-identical (no backend change); `kiem_nhanh.py` 7/7; `test_i18n_sync.py`, `test_ws_nhan.py` green.

## Current state
- L1 done (2026-11-22): `docs/ke_hoach/ux/UX5A_TU_NGU.md` written (measured with real Chromium, 6 decisions D1–D6 with defaults).
- Truong approved M1 (D1–D6 defaults) and ordered: all lots L2–L4 non-stop, then phase 2 (whole-UX5A debug). L2 done.
- Env: `.venv` created locally from `requirements-dev.txt` (gitignored). Measure script is in the session scratchpad only.

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Sonnet | Plan + protocol for Track A | split from UX5B by Truong |
| 2026-11-22 | Sonnet | L1 audit + words + choice map | measured admin+teacher, both tabs; stop point |
| 2026-11-22 | Sonnet | L2 Kết quả tab | tests ux5a_l2 green; t3_l3 failure pre-exists (UX4) |
