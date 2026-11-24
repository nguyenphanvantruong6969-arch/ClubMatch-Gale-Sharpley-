# Branch handoff: claude/ux4-quan-ly-de-hieu

> Read CLAUDE.md, then THIS file, then `docs/phien/UX4_GIAO_THUC.md`. English. Cap 150 lines.

## Feature / goal
Truong (2026-11-22): the "Quản lý" tab (sidebar group "Cài đặt và quản lý") is the real bottleneck: "I don't
understand anything when I open it; wording is unclear." Redesign it user-first so a school admin understands each
part within seconds of opening it. UI + wording only: no backend, schema, algorithm or API change. Item code
**UX4** (tentative, same family as UX1/UX2; confirm with Truong at milestone 1).

## Problems found (planner, screenshot of sample data, 2026-11-22)
1. Page subtitle only describes the CLB sub-tab and uses jargon ("suất ưu tiên", "cùng nhãn").
2. Sub-tab names are nouns with no hint of the task ("Điểm chuẩn", "Xoá dữ liệu"); no one-line purpose per sub-tab.
3. "Nâng cao: tiêu chí xếp, thử cấu hình" sits under EVERY sub-tab, even "Xoá dữ liệu"; the rules for who gets in
   first (the most important setting) are hidden in a fold.
4. CLB form: "Chỉ tiêu", "Suất ưu tiên", "Nhóm ưu tiên", "Buổi (ví dụ: thu_3)" = internal words / raw codes;
   the table has an unlabeled column (session) and "Chưa chia buổi".
5. Rules panel: "Xếp theo / Cách dùng nhóm ưu tiên / Phạm vi điểm / Một điểm cho cả người" read as system terms.
   Nothing says in one sentence what the current choice DOES.
6. "Thử cấu hình": both dropdowns default to the same official run; "Chính thức số 1"; the steps are unclear.
7. Học sinh: action buttons are visible and active before anyone is selected.
8. Điểm quyết tâm: "Quỹ 1, đã thi", "Phóng cho đủ 100 theo tỉ lệ", raw ISO lock time "2026-11-22 03:36:59", bare "i".
9. Điểm chuẩn: "XÉT ĐIỂM THI —" / "XÉT ĐIỂM QUYẾT TÂM 0" with no meaning for "—" or 0.

## Design rule: Hick's law (Truong, 2026-11-22)
"Don't give the user too many options or they get confused." Decision time grows with the number of equal-weight
choices shown at once, so every screen shows FEW choices; the rest is one click away (progressive disclosure).
Budgets (checked by a test that counts VISIBLE, enabled controls: buttons, selects, inputs, tabs, links):
- Sub-tab strip: **≤ 4** visible items. Rarely used / dangerous items go under one "Thêm ▾" item.
- One choice group (radio cards / one select): **≤ 3 options**, one pre-selected default, short labels.
- Per panel: **1 primary button**; ≤ 7 visible controls before the user opens "Thêm tuỳ chọn".
- A control that does not apply to the current choice is HIDDEN, not just disabled (e.g. group settings when no
  priority group is used). Actions on selected rows appear only after a row is selected.
- Never remove a capability: everything hidden stays reachable in ≤ 2 clicks and keeps its element id.

## Design rule: Von Restorff / isolation effect (Truong, 2026-11-22)
The one thing that looks different is the thing users notice and remember, so difference is RESERVED for what
matters. Works with Hick: Hick cuts the number of choices, Von Restorff marks the one to take.
- **One gold (`.btn-primary`) per visible panel** = the next step (e.g. "Lưu CLB", "Thử cách xếp này"). All other
  buttons `.btn-secondary`/link style. Today one screen shows 4 gold buttons ("Xem cảnh báo", "Lưu CLB",
  "Lưu tiêu chí", "Chạy thử"): none stands out.
- The global banner action is an ALERT style (outlined, warning colour), not gold, so it never competes.
- **Red (`.btn-danger`) only inside "Làm lại từ đầu"**, isolated, with the two-step confirm kept.
- The default/recommended card carries one small badge "Đề xuất"; the selected card has a clearly different border
  + check mark (not colour alone, WCAG 1.4.1).
- After a save/run, the changed row/status line is highlighted briefly (respect `prefers-reduced-motion` and
  `html.tat-hieu-ung`); meaning also in text.
- Never use accent colour for decoration (headings, icons, counts).

## Plan (written by Opus; ticked by Sonnet)
- [x] **L1 Wording + choice map (MUST, stop point).** `docs/ke_hoach/ux/UX4_TU_NGU.md`: (1) table of every visible
      string of the Quản lý tab: key | old VI | new VI | new EN | why; (2) a "choice map" per panel (incl. which ONE control is gold): controls visible
      now (count) → visible after redesign (count) → where each hidden one goes. Keep sector placeholders
      (`{person_l}` etc.). **MILESTONE 1: Truong approves words + choice map before any code.**
- [x] **L2 Structure (MUST).** One plain subtitle for the tab. Sub-tab strip = **3 items + "Thêm ▾"**:
      "Danh sách CLB", "Học sinh", "Cách xếp"; "Thêm ▾" holds Điểm quyết tâm*, Điểm chuẩn*, Làm lại từ đầu
      (* only when the feature is on, as now). "Tiêu chí xếp" + "Thử cấu hình" leave the "Nâng cao" fold and live in
      "Cách xếp". Each sub-tab: one-line purpose + live status line (e.g. "3 CLB · 30 chỗ · 1 buổi"). Keep ids and
      remember-tab (`localStorage`, try/catch; old saved values still open the right panel).
- [x] **L3 CLB + Học sinh (MUST).** CLB form shows 3 fields: Tên, Số chỗ, Buổi (dropdown of existing sessions +
      "Thêm buổi mới…", via `get_danh_sach_buoi`) + one "Lưu CLB" button. Mã CLB auto-filled from the name (editable,
      UI only; backend validation unchanged) and Chỗ dành riêng / Nhóm ưu tiên live under "Thêm tuỳ chọn".
      Label the session column. Học sinh: assign/export buttons hidden until ≥ 1 row ticked ("Đã chọn n học sinh").
- [x] **L4 Cách xếp (MUST) + score panels (OPTIONAL).** Replace the three selects with ONE question
      "Khi CLB hết chỗ, ai được xét trước?" and ≤ 3 cards (pattern of `js/18_cai_dat.js`): "Điểm bài thi cao hơn"
      (default), "Học sinh thuộc nhóm ưu tiên", "Cả hai". Each card maps to existing `priority` values; tier_mode,
      score_scope and the group list appear only when they apply, under "Tuỳ chỉnh thêm". Live sentence
      "Với lựa chọn này: …" (display only). Trial: one button "Thử cách xếp này" that compares with the latest
      official result by default; the two run dropdowns move under "So sánh lần khác". Dates dd/mm/yyyy HH:mm.
      Optional: Điểm quyết tâm / Điểm chuẩn wording + same budgets. **MILESTONE 2: checker + Truong 5-second test.**

## Starting wording proposal (L1 refines; Truong decides)
| Old | Proposed |
|---|---|
| Quản lý (subtitle about CLB) | "Sửa danh sách CLB và học sinh, chọn cách xếp, hoặc làm lại từ đầu. Chọn một mục bên dưới." |
| Câu lạc bộ / Học sinh | Danh sách CLB / Học sinh và nhóm ưu tiên |
| Nâng cao: tiêu chí xếp, thử cấu hình | sub-tab **Cách xếp** |
| Xoá dữ liệu / Vùng nguy hiểm | Làm lại từ đầu |
| Chỉ tiêu | Số chỗ |
| Suất ưu tiên | Chỗ dành riêng (cho nhóm ưu tiên) |
| Chưa chia buổi | Một buổi chung |
| Xếp theo | Khi CLB hết chỗ, ai được xét trước? |
| Chỉ theo điểm bài thi / nhóm ưu tiên / cả hai | Điểm bài thi cao hơn / Học sinh thuộc nhóm ưu tiên / Cả hai |
| Giữ suất riêng cho nhóm / Nhóm đứng trước điểm | Giữ một số chỗ riêng cho nhóm / Nhóm luôn được xét trước |
| Phạm vi điểm: Điểm theo từng CLB / Một điểm cho cả người | Mỗi CLB một bài thi riêng / Một điểm chung cho mọi CLB |
| Thử cấu hình | Thử cách xếp khác (không đổi kết quả chính thức) |
| Quỹ 1, đã thi / Quỹ 2, không thi | Điểm cho CLB có thi / Điểm cho CLB không thi |
| Phóng cho đủ 100 theo tỉ lệ | Tự cộng cho đủ 100 (giữ tỉ lệ) |

## Acceptance (both milestones)
- Truong opens the tab cold and can say what each sub-tab is for (5-second test) — his verdict decides.
- Playwright "Von Restorff" test per sub-tab: ≤ 1 visible `.btn-primary` inside `#view-admin` panels; `.btn-danger`
  only inside the "Làm lại từ đầu" panel; banner button is not `.btn-primary`.
- Playwright "Hick budget" test per sub-tab: visible enabled controls within the budgets above; sub-tab strip ≤ 4.
- Saving a card in "Cách xếp" sends exactly the same `priority/tier_mode/score_scope` values the old selects sent
  for the same choice (test compares payloads), so stored config and results are unchanged.
- Playwright test: visible text of `#view-admin` (each sub-tab) contains none of: "cấu hình", "suất", "nhãn",
  "Quỹ 1", "Phóng", an ISO timestamp `\d{4}-\d\d-\d\d \d\d:`; the fold "Nâng cao" text appears nowhere.
- Default config: results byte-identical (no backend change; `kiem_nhanh.py` `trung_khit` 7/7).
- EN strings updated in step (plain English, same structure); `test_i18n_sync.py` green.

## Decisions and gotchas
- UI only. Saving rules still calls the existing API with the same values; only labels change.
- Invariant 2 text stays true: the panel must still say rank order / past results are never used.
- `tests/test_ws_nhan.py` snapshots UI strings: every intentionally changed key → add to `SUA_CO_Y` with a comment
  `UX4`. Never weaken the snapshot test.
- Existing tests select by id/data-tab; keep ids. Tests asserting old wording → update on purpose, list in CHANGELOG.
- Teacher role never sees this tab (unchanged).

## Current state
- L1–L4 all done and pushed (head d2a8190, base 7e9d673). Truong was sent 3 "after" screenshots (`docs/phien/anh_ux4/sau_*.png`) and must approve them.
- Tests: ux4_l2/l3/l4 green; with test_ws_nhan + test_i18n_sync 79 pass; ~34 old UI test files migrated on purpose (list in CHANGELOG). kiem_nhanh 7/7 (compared to 7e9d673; no origin/main locally). Soat report: `docs/phien/claude__ux4-quan-ly-de-hieu__soat.md` (short form).
- Full suite NOT run locally (CI does).

## Decisions and gotchas
- D1: reuse MT1 three-card question (retitled "Khi CLB hết chỗ, ai được xét trước?"); no second card set. D2: delete-all wharton buttons are `.btn-secondary` (red only in "Làm lại từ đầu"). D3: Cài đặt panel lives in Cách xếp tab. D4: dashboard under "Thêm ▾". D5: backend labels overridden in UI by code (`ux4_tc_*`), `tieu_chi.py` untouched.
- Deviations from L1 sheet: no "Với lựa chọn này:" prefix; HS status line only "{n} học sinh"; extra status line for "Làm lại từ đầu"; Điểm quyết tâm/Điểm chuẩn got wording only (no Hick restructure, optional part).
- Closed `<details>` content still has client rects in Chromium: tests count visibility with `checkVisibility()`.
- `tab_ql(page, ma)` in tests/_trinh_duyet.py opens "Thêm ▾" for wh/dc/db/du_lieu.
- Pre-existing red (also on base 7e9d673): tests/test_giao_dien_ux2_nut.py (tkNutMoHop 216x36). Flaky once: test_giao_dien_a13_10_nhan EN test (re-render race), green on rerun.
- Backend business name for new Mã CLB is auto slug; collisions get `_2`, `_3`.

## Next steps (ordered)
1. Truong approves/rejects screenshots (5-second test).
2. Truong pastes the checker prompt from `docs/phien/UX4_GIAO_THUC.md` §4 in a new session (base 7e9d673, head d2a8190); max 2 FIX rounds, then "Needs Truong".
3. After PASS: watch CI (coverage ≥ 85 %, full suite); optional leftover: Hick budgets for Điểm quyết tâm/Điểm chuẩn panels; remove unused key `ux1a_nang_cao` from i18n.js.

## Files touched
index.html, style.css, i18n.js, js/00_nen.js, js/03_ket_qua.js, js/05_quan_ly.js, js/09_the_xem.js, js/15_tieu_chi.js, js/18_cai_dat.js, js/19_muc_tieu.js, js/19_ux1b_gv.js; tests: new test_giao_dien_ux4_l2/l3/l4.py, helper in _trinh_duyet.py, ~34 migrated; docs: ke_hoach/ux/UX4_TU_NGU.md, CHANGELOG.md, TIEN_DO.md, phien/anh_ux4/*.

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Opus | Audit of Quản lý tab, plan + protocol | UX3-L3 rename "Nhập thủ công" shipped separately |
| 2026-11-22 | Opus | Plan revised for Hick's law (budgets, 3 tabs + Thêm, one-question rules panel) | replaces "6 sub-tabs" idea |
| 2026-11-22 | Opus | Added Von Restorff rule (one gold per panel, red isolated, badge on default) | |
| 2026-11-22 | Sonnet | L1 wording sheet + choice map (measured counts with Chromium) | Found MT1 three-card question overlaps L4 (D1) |
| 2026-11-22 | Sonnet | L1 approved; L2 + L3 implemented, ~30 old tests migrated | `tab_ql` helper in tests/_trinh_duyet.py |
| 2026-11-22 | Sonnet | L4 implemented, soat-ma (report only), 3 after-screenshots | |
| 2026-11-22 | Sonnet | Handoff at ~400k tokens; no new work | Next: Truong approves screenshots, then checker |
