# Branch handoff: claude/ux5b-nap-xep-nhap-tay

> Read CLAUDE.md, then THIS file, then `docs/phien/UX5_GIAO_THUC.md` (Track B) and the "Design rule" sections of
> `docs/phien/claude__ux4-quan-ly-de-hieu.md`. English. Cap 150 lines.

## Feature / goal
Truong (2026-11-22): apply Hick's law (few equal choices) and Von Restorff (one thing stands out) to two sidebar groups:
**Nạp & xếp** = tab `Xếp CLB` (`#view-pipeline`: load the workbook/CSV, validate, lock seed, run, the "Chạy" button) and
**Nhập thủ công** = tabs `Nhập nguyện vọng` (`#view-fallback`: student entry form, new-student row, Wharton/quyết tâm
block, `btnSubmitWharton`) and `Nhập điểm` (`#view-scoring`). Item code **UX5B** (tentative).
Teacher role: `pipeline` is admin-only (hidden from teachers); `fallback` and `scoring` ARE visible to teachers, so
those two must be tidy under `body[data-vai="giao_vien"]` too (admin-only controls carry `data-quyen="quan_tri"`).

## Known starting points (planner, not yet audited with screenshots; coder audits first)
1. `#view-pipeline`: many steps and buttons on one screen; the Run button must be THE single gold, with the steps
   before it (load, check) as clear, ordered, low-weight actions; warnings must not compete with it.
2. `#view-fallback`: the entry form mixes required fields and rare ones (reset, delete, Wharton block with its own
   `.btn-primary`): required fields first, rare actions under the existing `menu-khac` pattern, Wharton behind a fold
   when the feature is on; hide row actions until a row/student is selected.
3. `#view-scoring`: check count of controls, gold buttons, and the teacher hint text (`js/06_cham_diem.js`, UX2-L6).
4. Keep sector vocabulary placeholders; keep ids; keep `data-quyen` semantics.

## Plan (ticked by Sonnet)
- [x] **L1 Audit + words + choice map (MUST, stop point).** `docs/ke_hoach/ux/UX5B_TU_NGU.md`: (1) per tab, count of
      visible enabled controls NOW (admin and teacher) + number of `.btn-primary` visible; (2) table of changed strings:
      key | old VI | new VI | new EN | why; (3) choice map: which ONE control is gold per panel, which go under
      "Thêm ▾" / `<details>`. **MILESTONE 1: Truong approves before code.**
- [ ] **L2 `Xếp CLB` tab (MUST).** One ordered path (load → check → run), one gold ("Chạy"), ≤ 7 visible controls before
      any fold, status line saying what is done / what is next; advanced options under one fold.
- [ ] **L3 `Nhập nguyện vọng` + `Nhập điểm` (MUST).** Required fields first; rare actions folded; Wharton block folded
      with its own gold removed from the first view; selection-dependent buttons hidden until a selection exists.
- [ ] **L4 Teacher view + tests (MUST).** Playwright "Hick budget" + "Von Restorff" tests per owned tab, admin and
      teacher (teacher: `fallback`, `scoring` only); jargon test; payload-equality test where a control moved (same API
      arguments as before). **MILESTONE 2: checker + Truong.**

## Acceptance
- ≤ 1 visible `.btn-primary` per panel; `.btn-danger` only where data is destroyed; banner/alert buttons not gold.
- Visible enabled controls ≤ budget per panel (UX4 branch file), as admin AND as teacher.
- Nothing removed: every hidden capability reachable in ≤ 2 clicks, ids unchanged, run pipeline order untouched
  (invariant 5); default results byte-identical; `kiem_nhanh.py` 7/7; `test_i18n_sync.py`, `test_ws_nhan.py` green.

## Current state
- L1 done (2026-11-22): `docs/ke_hoach/ux/UX5B_TU_NGU.md`. **MILESTONE 1 APPROVED by Truong 2026-11-23**: words §2, defaults D1–D6, open questions 1–3 by default. L2–L4 may start.
- Work continues on `claude/affectionate-lamport-595imn` (it holds UX5A fixes and CI is green there, run #1403); `claude/ux5b-nap-xep-nhap-tay` is stale and red, do not push to it.
- Full autonomous run: prompt in `docs/phien/UX5B_L2_L4_AUTO_PROMPT.md` (P0 merge `main`, then L2-L4, auto checker, CI loop). P0 comes first so the
  `index.html`/`style.css` conflicts with MT2 are solved once, on a small diff. After P0 re-count controls on the three tabs (MT2 touched the quyet-tam block).
- Test env: venv at scratchpad (`pip install -r requirements-dev.txt`), no `.venv` in the checkout.

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Sonnet | Plan + protocol for Track B | split from UX5A by Truong |
| 2026-11-22 | Sonnet | L1 audit (Chromium measurements), words table, choice map | stop at MILESTONE 1 |
