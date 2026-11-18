# UX1 — Implementation plan (for the coding collaborator)

> Item **UX1 — direct UI, fewer steps** (opened by Truong 2026-11-18, outside the 33-item registry).
> Audit and screenshots: `docs/ke_hoach/ux/UX1_RA_SOAT.md`, `docs/ke_hoach/ux/anh/`. Read the audit first.
> Truong's decisions (2026-11-18): all four user groups; PDF via **Print → Save as PDF** (no new library);
> cutoff ("mức vào được") may be printed on the slip for clubs the student tested; tab names may change and the
> user guide, demo/video scripts and poster are updated in the same item.
> Truong 2026-11-18 (2): the slip must also show the **medal each student placed** and the **type of each club**
> (FA mode). Findings on how the algorithm uses medals/types: audit §6.
> Truong 2026-11-18 (3): **keep the default config** (determination points ON, FA/medals OFF — invariant 1 safe);
> the app suggests turning medals on when a book has medal/type columns (L5); medal cells accept the words
> Vàng/Bạc/Đồng as well as 60/30/10 (L5b). Medals and determination points stay ONE column: FA medals REPLACE
> determination points (no parallel use — that would need a new choice function, invariant 8).
> Execution: two teams in parallel — protocol `docs/phien/UX1_GIAO_THUC.md` (team A: L1, L2, L2b, L3, L5, L5b, L8-A;
> team B: L4-B, L6, L7, L8-B). The §4 prompt below is superseded by the protocol.

## 0. Hard rules (from CLAUDE.md — read it)
- **UI and presentation only.** No change to `rbda_priority_pipeline.py`, `compute_club_priority`, STB, seeds,
  `run_history`, schema or the CSV contract. Invariant 1 (byte-identical `match_results`) must stay green:
  `python .claude/skills/soat-ma/scripts/kiem_nhanh.py` (needs `git fetch origin main`).
- **Keep every element `id` and every `data-tab` value.** About 97 Chromium tests (`tests/test_giao_dien_*`) select by
  them. Move DOM blocks; do not rename them. If a test really must change, change the selector, never skip the test.
- New backend method → add it to `QUYEN` in `phan_quyen.py` (the completeness test in `tests/test_gt3_phan_quyen.py`
  fails otherwise) and log one audit row if it exports/prints student data (GT I3 rule).
- New user text → `i18n.js` (vi + en; `kiem_nhanh` checks both). Error text → `i18n_errors.py`, then
  `python tao_i18n_js.py`. Use vocabulary placeholders (`{person_l}`, `{slot_l}`, `{cohort_l}`…), never hard-code "học sinh/CLB".
- Test first per lot; run only related tests (`python -m pytest -q <file>`); full suite only at the gate.
- After each lot: tick the plan in the handoff file, one line in `CHANGELOG.md` and `docs/ke_hoach/TIEN_DO.md`.
- No subagents. Before push: skill `soat-ma`.

## 1. Targets (measured with `docs/ke_hoach/ux/chup_luong_chinh.py` / `chup_phieu.py`)
| Task | Now | Target |
|---|---|---|
| Admin: load book → run → download results | 5 clicks | 4 |
| Admin: deal with unplaced students | 4–6 | 2 |
| Slip PDF for one student | ~8 | 4 (search → pick → "In / Lưu PDF" → Save) |
| Homeroom teacher: own class results | 3 | 2 |
| Principal: summary report | none | 1 |
| Student self-lookup | 2 | 2 (unchanged) |

## 2. Lots (do in order; each ends with its "Done when")

### L1 — "Next step" bar
- New block `#viecTiepTheo` at the top of `<main>` in `index.html` (admin only: `data-quyen="quan_tri"`), one primary
  button + one sentence. State is computed in JS from data already fetched by `refreshSidebarStatus()`
  (`js/01_khung.js`) and the run result in `executeRun()` (`js/02_van_hanh.js`); no new backend call unless needed.
- States, in order: no data → "Nạp sổ" (focus `#dropZone`); data + blocking warning → "Xem cảnh báo"; data, never run
  → "Chạy sắp xếp" (`#btnRun`); just run, n unplaced > 0 → "Xử lý n {person_l} chưa có {slot_l}" (opens the unplaced
  panel `#chuaCoChoPanelBody`, expanded, scrolled into view); otherwise → "Xuất kết quả" (`#btnXuatTuyChon`).
- Make the "n Cần xử lý" summary card (`tomTat…` in the results/others view) a button with the same action.
- Put the code in a new script `js/17_viec_tiep_theo.js`; add it to `js/_danh_sach.txt` and the script list in `index.html`.
- Done when: new `tests/test_giao_dien_ux1_tiep_theo.py` drives the 120-student book (`du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`)
  through every state and asserts the button label and target; the admin task above takes 4 clicks.

### L2 — Navigation 6 → 4 groups
- Sidebar shows 4 groups: **1. Nạp & xếp** (view `pipeline`: import, warnings, run — already one page),
  **2. Nhập tay** (`fallback`, `scoring`), **3. Kết quả & phiếu** (`results`, `others`), **Cài đặt** (`admin`, `chuan_bi`).
  No view is split, so no DOM block has to move between views.
- Recommended mechanism (keeps tests green): each group button opens its first view; inside the group a small
  segmented control holds the existing buttons with their **existing** `data-tab` values, so `switchTab(name)` and
  test selectors such as `[data-tab="fallback"]` keep working. Edit `initTabs/switchTab/doiThe` in `js/01_khung.js`.
- Respect `data-quyen` and `hidden` rules already on the nav items (workspace rules can hide "Nhập điểm"; `chuan_bi`
  is hidden until enabled). A group whose views are all hidden disappears.
- Inside **Cài đặt**, fold "Tiêu chí xếp" and "Thử cấu hình" (GT2 panels, `js/15_tieu_chi.js`) under one closed
  `<details>` "Nâng cao"; club editing comes first.
- Done when: `tests/test_giao_dien_ux1_dieu_huong.py` checks 4 groups for admin, correct groups for `giao_vien` and
  the student lock (GT I2) still blocks every tab; all existing `test_giao_dien_*` pass unchanged or with selector-only edits.

### L2b — Settings: one question, saved instantly (Truong 2026-11-18 (5), replaces the earlier "save bar" design)
Design rule: a setting exists only if a teacher can answer it in one sentence. Everything else is either a fact the
app shows, or an action offered where it is needed. Audit §7 lists today's problems.

**The whole settings page = one question + one sentence.**
```
Cài đặt · Trường THPT …

Học sinh cho biết mình muốn CLB nào nhiều hơn bằng cách nào?

 ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
 │ Chỉ xếp thứ tự   │  │ ✓ Chia 100 điểm  │  │ Huy chương        │
 │ NV1, NV2, NV3…   │  │ cho các nguyện   │  │ Vàng · Bạc · Đồng │
 │                  │  │ vọng (mặc định)  │  │ (60 · 30 · 10)    │
 └──────────────────┘  └──────────────────┘  └──────────────────┘

Cách xét khi đông: điểm thi → điểm quyết tâm → bốc thăm.   Thay đổi…
```
- Three cards map 1:1 to rules: "Chỉ xếp thứ tự" → `wharton=false, fa_daa=false`; "Chia 100 điểm" (default,
  selected) → `wharton=true, fa_daa=false`; "Huy chương" → `wharton=true, fa_daa=true`. The 60·30·10 line is
  read-only (`fa_daa.GIA_TRI_HUY_CHUONG`; only the order matters). Card text uses vocabulary placeholders.
- **No Save button.** Clicking a card saves at once with one `update_workspace_config({rules})` call, applies
  live (`wsApDungCauHinh`, reload dependent tabs) and shows a toast "Đã chuyển sang Huy chương · **Hoàn tác**"
  (10 s; Undo = the same call with the previous values). Errors: the card does not change and the message sits
  under it. One audit row per change (verify `update_workspace_config` logs; add if not).
- The sentence "Cách xét khi đông…" is generated from the effective rules (reuse GT2's "Thứ tự xếp hiện tại").
  "Thay đổi…" opens today's "Tiêu chí xếp" controls in a sheet with its own "Xong" (advanced, rarely used; GT2
  "Thử cấu hình" lives there too). Its "Xét điểm quyết tâm" checkbox is removed — the cards own `wharton`.
- **Choosing "Huy chương" with data that is not ready → fix in place, not a red checklist.** The card opens a small
  panel listing only what is missing, with the control to fix it right there: each club without a type gets three
  pills "Tự do · Giới hạn · Tuyển chọn" (saves per click through the existing club update path); a session without
  any "Tự do" club is shown as "Thứ 4 cần một CLB Tự do — chọn: [CLB…]". When nothing is missing the panel says
  "Sẵn sàng" and closes. The run stays blocked by the backend checks until ready (unchanged), and the L1 "Next step"
  bar points here.
- **Post-run features are not settings.** Remove the 5 checkboxes + complaint-days field from settings. Offer each
  as an action on the results screen at the moment it makes sense, e.g. "Mở vòng 2 cho 32 em chưa có CLB",
  "Nhận khiếu nại trong [3] ngày", "Điểm danh 3 buổi đầu", "Mời danh sách chờ vào chỗ trống", "Thu phản hồi".
  Pressing one sets its flag (`fa_vong_2`, `fa_khieu_nai` + `fa_khieu_nai_so_ngay`, `fa_diem_danh`,
  `fa_vong_doi_cho`, `fa_phan_hoi`) and opens the existing panel. They require Huy chương (backend
  `fa_tinh_nang_can_fa`): in other modes they are simply not shown.
- **One place only.** The ⋯ menu item "Tính năng sau khi xếp…" becomes "Cài đặt…" and opens this page; the ⋯ dialog
  `wsMoTinhNang` is deleted; the creation wizard step (`wsBuoc3`) shows the same three cards (same component).
- If an official run exists, the toast adds one line: "Kết quả đã xếp giữ nguyên; lần chạy sau dùng cách mới."
  (`run_history` untouched — invariant 4). Default config is unchanged (invariant 1).
- Done when: `tests/test_giao_dien_ux1_cai_dat.py`: a new workspace shows "Chia 100 điểm" selected; one click on
  "Huy chương" saves (config read back: `wharton=true, fa_daa=true`) with no other click; Undo restores; the fix-in-
  place panel on `SO_NHAP_DQT_120HS_HOP_LE.xlsx` lists 9 clubs without type and 3 sessions without Tự do, and
  setting them through the pills makes it say "Sẵn sàng"; "Chỉ xếp thứ tự" forces `fa_daa=false`; no settings view
  contains a post-run checkbox; the results screen offers "Mở vòng 2" only in medal mode; changing mode needs no
  restart. Selector-only updates to tests that used `#wsTnWharton` / `#gt2TcWharton`.

### L3 — Results page: lookup first, one export menu
- Move the lookup panel `#gtPanel` to the TOP of view `results` (above the table). Remove the GT4 jump link
  "Tra cứu một học sinh ↓" (no longer needed) — keep its i18n key only if something else uses it.
- Collect the export buttons of view `others` (`#btnXuatTuyChon`, `#btnXuatTheoLop`, `#btnXuatLyDo`, `#btnXuatNhuCau`,
  `#btnXuatGoiY`, `#btnXuatBienBan`, …) into one "Xuất…" menu button (reuse the existing `menu-khac-muc` pattern);
  "Xuất kết quả (Excel)" and "Xuất theo {cohort_l}" stay visible as the two main buttons. Keep ids and handlers.
- Show the import success message once (today: file box + line + toast). Keep the toast, drop the duplicate line.
- Done when: a test asserts `#gtPanel` is above `#kqBang`, only two export buttons are visible by default, and the
  import message appears once.

### L4 — Role pages (homeroom teacher, principal)
- `giao_vien` login lands on **3. Kết quả & phiếu** with: class picker, "Xuất theo {cohort_l}", "In phiếu cả {cohort_l}".
- New one-click **"Báo cáo tổng hợp"** (principal): a printable HTML built from existing aggregates only (summary cards,
  per-club fill, preference satisfaction, unplaced count per class) — **no names, scores or lottery numbers**.
  Backend: new pure builder `bao_cao_tong_hop.py` + method `export_bao_cao_tong_hop` in `api_xuat.py`;
  `QUYEN` = `giao_vien`; one audit row. Opens with the same print flow as L6.
- Done when: unit test for the builder (no student id/name in output; numbers equal the summary API) and a Chromium
  test that a `giao_vien` account reaches both actions in ≤ 2 clicks.

### L5 — Warning severity and wording
- In `api.py` validation, the three oversubscription warnings (`health_oversubscribed`, `…_buoi`,
  `…_chua_khai_buoi`) move from `"info"` to `"medium"` (non-blocking; only `"high"` blocks — verify in the run gate).
- Shorten their texts in `i18n_errors.py` to one sentence + one action, e.g. "{session} {buoi}: {n_seats} chỗ cho
  {n_students} {person_l} — ít nhất {n_short} em sẽ không có chỗ. Tăng chỉ tiêu hoặc thêm {slot_l}." Then `tao_i18n_js.py`.
- **Medal book in the wrong mode** (audit §6): when the imported book has medal/type columns and FA is off, the import
  preview must say plainly "Sổ này có cột Huy chương / Loại nhưng chế độ 'Xếp theo loại CLB và huy chương' đang tắt —
  bật chế độ này ở Cài đặt, hoặc huy chương sẽ không được dùng", with a button to that setting. With
  `wharton` on, do NOT let medal values be saved as determination points silently: keep the current blocking, but the
  run error must point to the FA setting, not to "điền đủ điểm quyết tâm". Group the per-student
  `wharton_chua_dung_het` warnings into one line ("n em chưa đặt đủ huy chương"). Detection: the medal column header
  `so_nhap.TEN_COT_HUY_CHUONG` or a `Loại` column on the club sheet (`fa_cot_bo_qua` already fires).
  This changes messages only — no change to what is stored or how the run decides (invariant 1).
- **One-click enable:** the import preview message above carries a button "Bật chế độ huy chương" that sets
  `rules.fa_daa = true` for the current workspace through the existing config path (`update_workspace_config`,
  admin only, audit row), then re-runs the preview. Never switch it on silently.
- **Sample books:** "Tải sổ nhập mẫu" offers two choices: "Sổ mẫu thường" (today's file, byte-identical) and
  "Sổ mẫu có huy chương" (`so_nhap` builder with `che_do_fa=True`). Its Hướng dẫn says the mode must be on.

### L5b — Medal words in the book
- When FA is on, a medal cell may hold `60/30/10` **or** `Vàng/Bạc/Đồng` (case/diacritics-insensitive, also
  `vang/bac/dong`, `gold/silver/bronze`); map to 60/30/10 at the reading layer only (where `diem_w` is parsed in
  `api_nhap.py`, and the same in the Forms import path if it carries medals). Stored values stay 60/30/10, so
  `fa_daa.kiem_ho_so_huy_chuong` and the run are unchanged. Unknown words keep today's `fa_huy_chuong_gia_tri_sai`.
  FA off: words are not mapped (the column is ignored/handled as today). Update the sample book's Hướng dẫn line
  ("60 (vàng), 30 (bạc), 10 (đồng)" → "Vàng / Bạc / Đồng hoặc 60 / 30 / 10").
- Done when: tests: same book with numbers vs words gives identical `wharton_bids` rows and identical
  `match_results`; mixed-case and unaccented words map; a wrong word still errors; FA off unchanged; invariant 1 green.

- Done when: tests that assert these codes/severities are updated (grep `health_oversubscribed` in `tests/`);
  invariant 1 green (severity is display-only).

### L6 — Slip: "In / Lưu PDF" directly
- New method `get_phieu_giai_trinh_html(student_ids=None, lop=None)` in `api_xuat.py` returning the HTML string from
  `phieu_giai_trinh.dung_phieu_html` (same data path as `export_phieu_giai_trinh`); `QUYEN` = `giao_vien`; one audit row.
- In `js/14_giai_trinh.js`: button "In / Lưu PDF" loads the HTML into a hidden `<iframe srcdoc>` and calls
  `iframe.contentWindow.print()`. Keep the old "export file" path as fallback in the menu (needed for whole-class batches
  and if printing is blocked).
- Add `@page { size: A4; margin: 14mm }` to the slip CSS; one student per page already holds.
- **Manual check on Windows (Truong):** print dialog opens in the packaged pywebview/WebView2 window and in browser
  fallback (`browser_host.py`). Record the result in the handoff file.
- Done when: Chromium test intercepts `print()` (stub `window.print` in the iframe) and asserts it was called with the
  student's page; audit has exactly one row; slip PDF task = 4 clicks.

### L7 — Slip content
In `phieu_giai_trinh.py` (and the on-screen card in `js/14_giai_trinh.js`, same wording):
1. **Summary line** under the name: "Em có {k}/{n} buổi: CLB Làm vườn (Thứ 4), CLB Mỹ thuật (Thứ 6)." or
   "Em chưa có {slot_l} ở buổi nào."
2. **Scores of every club the student tested** (from `tested_scores`), including tested clubs not in the ranking.
3. **Small inline SVG bar per tested club**: own score vs cutoff ("mức vào được"). Only clubs the student tested; no
   other student's data. Pure SVG string, escaped, no external files (slip must stay self-contained).
4. **"Em nên làm gì tiếp"** block when a session has no place: list only features that are on for this workspace
   (round 2, invitation to empty places, data-error complaint) + "hỏi giáo viên phụ trách".
5. **FA mode only — medals and club types:** each table row shows the club type ("Tuyển chọn / Giới hạn / Tự do",
   `so_nhap.NHAN_LOAI_HIEN_THI`, from `clubs.loai`) and the medal the student placed on it ("Vàng / Bạc / Đồng / —",
   from `wharton_bids` points 60/30/10, `fa_daa.GIA_TRI_HUY_CHUONG`). Add a short legend once per slip: "Tuyển chọn: xét
   điểm thi trước, rồi huy chương. Giới hạn: xét huy chương. Tự do: nhận mọi em còn chỗ." (verify each sentence
   against `rbda_priority_pipeline.uu_tien_wharton` before writing it). When the stored reason is `MEDAL`, the
   sentence names the medal ("Em đặt huy chương Bạc; các bạn đặt Vàng được xét trước"). Read data in
   `giai_trinh.dung_du_lieu_run` / `_lua_chon_fa` (add keys `loai`, `huy_chuong` to each row); render in
   `phieu_giai_trinh._bang` and the on-screen card. Non-FA workspaces: no new columns (slip unchanged except items 1–4, 6).
   Privacy: only this student's own medals.
6. Plain words: drop "số khoá bốc thăm: {seed}" from the student-facing card and slip (i18n `gt_lan_chay`; keep the seed
   in admin detail and exports); column "Mức vào được" shows a score or "Chọn ngẫu nhiên khi bằng điểm" instead of
   "Bốc thăm"; same column names on screen and slip ("Điểm thi", "Chỗ đã nhận / tối đa").
- Gotcha: `tests/test_gt_tich_hop.py::test_i4_*` regenerates `docs/giai_trinh/CA_MAU.md` **byte-identically** from app
  sentences. After changing sentences, rerun `python du_lieu_test/tao_ca_mau_giai_trinh.py` and
  `python docs/giai_trinh/tao_goi_minh_chung.py`, commit the new files in the same lot. Also check `tests/test_gt1_*`.
- Done when: unit tests on `dung_phieu_html` for a student placed everywhere, partly, and nowhere, plus an FA
  workspace test (book `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx`): every row shows the right type and medal, a MEDAL-reason
  row names the medal, a non-FA slip has no type/medal columns (summary line, tested-club scores, SVG present only for tested clubs, next-steps block only when unplaced, no other student id in
  the page); `chup_phieu.py` regenerated `anh/phieu_mau.pdf` looks right.

### L8 — Docs
- Update tab names and steps: `HUONG_DAN_SU_DUNG.md`, `docs/giai_trinh/KICH_BAN_DEMO.md`, `KICH_BAN_VIDEO.md`,
  `HUONG_DAN_CHAY.md`, `SO_DO_LUONG.md`, poster files under `poster/`, code map in `docs/ke_hoach/CLAUDE_CHI_TIET.md`.
  `tests/test_gt3_tai_lieu.py` checks that every "thẻ X" in the scripts is a real tab label.
- Re-run both capture scripts; replace screenshots in `docs/ke_hoach/ux/anh/`; add an "After" table to the audit with
  measured clicks.
- Done when: `test_gt3_tai_lieu.py` passes; audit "After" table meets §1 targets.

### L9 — Gate
- `ruff check .`, `kiem_nhanh.py` 7/7, skill `soat-ma` four tiers, full CI green (coverage ≥ 85 %). Status DONE in
  the handoff file; Truong merges.

## 3. Risks
| Risk | Mitigation |
|---|---|
| 97 UI tests break on layout change | keep ids/`data-tab`; move blocks only; fix selectors, never skip |
| `print()` blocked in WebView2 | keep file export + "Mở tệp" fallback; Truong checks on Windows (L6) |
| Slip wording change breaks CA_MAU byte test | regenerate CA_MAU + evidence pack in L7 |
| Role pages leak data | builder/unit tests assert no names/scores/lottery numbers; QUYEN classification |
| Scope creep into the algorithm | any change outside UI → stop and ask Truong (rule 7) |

## 4. Prompt to paste into the coding session (Sonnet)
```
Branch: create claude/ux1-giao-dien from origin/claude/gt-tich-hop. Read CLAUDE.md, then
docs/ke_hoach/ux/UX1_RA_SOAT.md and docs/ke_hoach/ux/UX1_KE_HOACH.md, then docs/phien/claude__ux1-giao-dien.md.
Implement lots L1 → L9 in order, test first, one commit per lot, tick the Plan in the handoff file after each lot.
UI/presentation only; keep every element id and data-tab; invariant 1 must stay green (kiem_nhanh.py).
Stop and ask Truong if a lot needs an algorithm, schema or CSV change, or a new library.
```
