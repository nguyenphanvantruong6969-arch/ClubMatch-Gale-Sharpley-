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

## Plan (written by Opus; ticked by Sonnet)
- [ ] **L1 Wording sheet (MUST, stop point).** `docs/ke_hoach/ux/UX4_TU_NGU.md`: one table, every visible string of
      the Quản lý tab (incl. sub-tabs, buttons, placeholders, column heads, hints, toasts): key | old | proposed new
      | why. Use the starting proposal below. Use `{club_s}/{person_l}`-style placeholders where the key already has
      them (sector vocabulary, Z1). **MILESTONE 1: Truong approves/edits the words before any code.**
- [ ] **L2 Structure (MUST).** (a) one plain subtitle for the whole tab; (b) sub-tabs renamed to tasks + one-line
      purpose and a live status line under each heading (e.g. "3 CLB · 30 chỗ · 1 buổi"); (c) move "Tiêu chí xếp"
      + "Thử cấu hình" out of the fold into a NEW sub-tab "Cách xếp" (order: CLB, Học sinh, Cách xếp, Điểm quyết tâm*,
      Điểm chuẩn*, Làm lại từ đầu; * = only when the feature is on, as now). Keep every element id and the
      `localStorage` remember-tab behaviour; old saved value "du_lieu"/"clb"/... still works.
- [ ] **L3 CLB + Học sinh panels (MUST).** Apply approved words; label the session column; session field = dropdown
      of existing sessions + "Thêm buổi mới…" (UI only, via `get_danh_sach_buoi`); ⓘ help for "Số chỗ dành riêng" and
      "Nhóm ưu tiên" with one example; Học sinh: buttons disabled + "Đã chọn 0 học sinh" until a row is ticked.
- [ ] **L4 Cách xếp + score panels (MUST: Cách xếp; OPTIONAL: Điểm quyết tâm, Điểm chuẩn).** Questions instead of
      system labels; a live plain sentence "Với lựa chọn này: …" built from the current selects (display only, no
      new rule); trial runs: default the 2nd dropdown to the newest trial, disable "So sánh" when both are the same,
      run labels "Kết quả chính thức lần 1 — 22/11 03:36"; dates as dd/mm/yyyy HH:mm; "—"/0 explained in the
      header ⓘ. **MILESTONE 2: checker + Truong 5-second test.**

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
- Planned only (2026-11-22, Opus). No code yet.

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-22 | Opus | Audit of Quản lý tab, plan + protocol | UX3-L3 rename "Nhập thủ công" shipped separately |
