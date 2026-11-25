# Branch handoff: claude/gracious-johnson-pnqvrg

> Read CLAUDE.md, then THIS file, then `docs/phien/DK1_GIAO_THUC.md`. English. Cap 150 lines.

## Feature / goal
Item **DK1** (approved by Truong 2026-11-25; DK2 = real integration later): a clickable **prototype shell**
for the INPUT side of club allocation (Admin / Giáo viên / Học sinh), mock data, no backend. Ends with a
Sổ nhập-shaped export. Post-allocation outputs: out of scope. Insight source evaluated 2026-11-25:
https://magenta-crepe-416060.netlify.app/dang-ky-clb (keep: role doors, teacher self-registration, admin
approval, per-session lists; avoid: unused grade field, no validation, free-text room, public admin page).

## Current state (overwrite each handoff)
- **A working prototype v7 exists**, built by Opus at Truong's explicit request as a claude.ai artifact
  (https://claude.ai/artifact/BuEtHrR61XXuju8kGXvmAX, link shared "Anyone with the link").
  Source saved in repo: `docs/phien/DK1_BAN_MAU_V7.html` (single file, ~109 KB, vanilla JS, localStorage key
  `dk1_state_v1`, state `v:2`). It is the **reference design**; it is NOT under `nguyen_mau/` yet.
- `docs/phien/DK1_GIAO_THUC.md` (protocol) is **OUT OF DATE**: written before rounds 7–12 below (medal mode,
  "Việc bây giờ", 3-step teacher form, add-vs-replace students, admin-created teachers). Plan unticked.
- No product code, no tests in `tests/`, no CHANGELOG/TIEN_DO rows yet. Registry entry for DK1 not added.
- Open question to Truong (unanswered): keep the 5-test cap? (in medal mode an untested Tuyển chọn club is
  never admitted, so capping at 5 makes extra ranked Tuyển chọn clubs pointless; UI lists them).

## Decisions (Truong, 2026-11-25; later rows override earlier; do not re-ask)
Workflow: 6 phases, one active: `Chuẩn bị → GV đăng ký → Duyệt CLB → HS đăng ký → Nhập điểm → Xuất`.
- D1 Deadline per open phase, auto-close by clock (30 s check), Đóng ngay, Gia hạn; GV close → Duyệt (never HS).
- D2 "Mở cho học sinh" only with no pending club, ≥ 1 approved, and **≥ 1 approved Tự do club in every session
  that has approved clubs** (medal mode).  D3 Step back allowed (logged); each export gets a version.
- D4 Sessions and grade list editable (default Thứ 2–6, 6–12), locked after GV phase. D5 Rooms: unique name,
  capacity > 0, room in use not deletable. D7 Grade read from class name ("10A1" → 10).
- D6 Student list: **"Thêm vào danh sách" (default)** or "Thay cả danh sách" (explicit, confirm, no error rows).
  Parser accepts Tab, comma/semicolon, or spaces (id first, class last, name between; optional 4th = khối).
  Preview row status: Mới / Đã có (cập nhật, giữ PIN) / Lỗi + reason. Add mode saves valid rows, skips errors.
- D8 Student PIN auto 4 digits, printable slips, reset. D9 Unlisted student refused at kiosk.
- D10 Admin password (demo `admin123`), lock after 2 min idle. D11 Backup/restore JSON (copy, no download).
- D12 Mock switch "Demo nhỏ" (30 HS, 10 CLB) / "Cả trường" (798 HS, 40 CLB).
- D13 Teachers: self sign-up (school code + name + own PIN) **and** admin-created accounts (paste names, auto
  PIN, PIN slips, "Đặt lại PIN"; column "Cách tạo"). D14 One teacher, never two clubs in one session.
- D15 Club fields: name (unique), session, **type Tự do / Giới hạn / Tuyển chọn**, room (free in that session),
  quota (not for Tự do; ≤ room capacity), grades (from–to range + optional per-grade fold), Tuyển chọn only:
  Forms link + **điểm sàn 0–10**; description, requirements. Teacher form = **3 steps** (Lịch và phòng / Ai
  được tham gia / Giới thiệu), per-step validation, `novalidate` (own Vietnamese messages).
- D16 Twice-weekly club = two clubs. D17 Teacher edits only while GV phase open and club "Chờ duyệt".
- D18/D19 Admin approves/rejects, admin quota vs teacher quota, room change; after HS opens: raise quota,
  change room/session or delete with "N học sinh bị ảnh hưởng" + log.
- D20 Student login ID + PIN + "Đúng là em". D21 Only approved clubs of own grade; ≤ 10 per session; no
  minimum; ≤ 1 club won per session. Club order shuffled per student (stable hash). Warn if no Tự do ranked.
- D22 Tap "+ Thêm", ↑/↓, ✕ (drag-and-drop cut). D24 Receipt with Forms links + code. D25 Edit until deadline;
  auto-logout after submit (30 s) and 60 s idle. D26 Students never see demand counts.
- **D34 Medal mode (FA-DAA, `docs/ke_hoach/FA_DAA_VISION.md` §5–6)**: per session Vàng 60 / Bạc 30 / Đồng 10;
  default = top 3 non-Tự-do ranked clubs; student can swap (choosing a club holding another medal swaps
  them; ≤ 1 medal per club); auto-follow ranking until edited by hand, then kept + "Đặt lại theo nguyện vọng".
  Tuyển chọn note shown. Invariant 2 exception D2 respected (defaults at registration layer, override path A).
- D23/D35 Tests: only Tuyển chọn clubs; tick ≤ 5 among ranked; **no test or score < điểm sàn = not admitted
  to that club** (overrides D29 "no score = tier 2"). Scores 0–10, comma or dot; "Dưới sàn" chip.
- D27 Scores: paste "mã ⇥ điểm" per club + typing table; missing-score list; "Chốt điểm" → Xuất.
- D30 Export preview: sheet `1. CLB` (Tên, Buổi, Loại, Chỉ tiêu [blank for Tự do], Điểm sàn, Mã, Phòng, Sức
  chứa phòng, Khối, Link) and `2. Học sinh` (per NV: CLB, Điểm, Huy chương) + JSON copy. Real .xlsx in DK2.
- D31 Live admin views (HS phase): progress by class (slowest first), demand per club, not-registered fold.
- **D36 Admin IA = "Việc bây giờ"**: 4 tabs `Việc bây giờ · Danh sách (Phòng/Học sinh/Giáo viên) · Cài đặt ·
  Thêm ▾ (Nhật ký/Sao lưu/Lùi giai đoạn/Công cụ thử)`; first tab shows only the current phase's work with
  exactly one gold button (Mở đăng ký GV / Mở cho học sinh / Chốt điểm / Chép dữ liệu xuất).
- **D37 Design laws** (`docs/ke_hoach/ux/UX4_TU_NGU.md`): Hick (tabs ≤ 4, ≤ 3 per choice group, ≤ 7 per frame
  before a fold, ≤ 9 per tab; count with folds closed, exclude table rows/data lists) + Von Restorff (≤ 1 gold
  per frame; red only for deleting data; hide unavailable actions instead of disabling). Measured on v7:
  admin 54/54 frames pass (max 6), teacher/student screens ≤ 7, no disabled gold button.
- D38 Every login screen has "← Về trang chọn vai trò"; closed phase shows message + one "Về trang đầu".

## Gotchas found while building v7 (carry into DK1/DK2 code)
- Re-render on `change` swallowed the next click and crashed with nested `innerHTML`; fixed with deferred
  render while pointer is down, a `rendering` guard, ignoring `change` during render, and focus restore.
- Score inputs must re-render after the value is saved (`setTimeout(render,0)`) or counters stay stale.
- Two browser tabs on one localStorage overwrote each other; fixed with `storage`/focus/3 s pull. DK2 uses
  one database, so this is prototype-only.
- Closed `<details>` children still have `offsetParent` in Chromium: Hick counters must exclude them.
- Artifact viewer blocks downloads, print, `confirm()`: prototype uses copy buttons and in-page modals.

## Truong feedback on v7, NOT yet built (2026-11-25, after handoff)
- D39 Student flow **per session**: for each day in turn: rank clubs → place medals → tick tests, then next
  day; final review covers all days. (Replaces the 4 global steps rank-all → medals-all → tests-all.)
  Keep the ≤ 5 tests total cap logic visible per day (open question on the cap still stands).
- D40 Bug: long type chip on student club cards ("Giới hạn 15 chỗ – …", "Tuyển chọn – … mốc …") overflows
  the card and overlaps "+ Thêm". Shorten chip (e.g. "Giới hạn · 15 chỗ") and move the full sentence to a
  second line of small text; let it wrap; button must not overlap at 1366 px and 390 px.
- D41 Proposal to Truong (awaiting OK): drop "Mã biên nhận" (receipt code) — kiosk re-login with ID + PIN
  already shows submission; replace with "Đã gửi lúc hh:mm, thứ …".

- D42 (Truong, 2026-11-25): "sample is OK" → start the next phase (DK2) once the Sổ nhập output is correct.
  Planner's finding (NOT verified by running): v7 export is NOT a valid Sổ nhập yet — NV groups restart per
  session (real sổ: one NV1…NVk run, session inferred from club); columns/headers not exactly
  `so_nhap.py` (Tên CLB, Buổi, Chỉ tiêu, Suất/Nhóm ưu tiên, Mã CLB + FA: Loại, Điểm sàn, Tối thiểu, Sức chứa
  phòng; NV group: CLB · Điểm thi · "Huy chương (60/30/10)"); Phòng/Khối/Link have no sổ column (CSV contract
  → rule 7, ask Truong); never passed the real importer.

## Next steps (ordered)
00. **DONE 2026-11-25** → `docs/phien/DK2_GIAO_THUC.md` + `docs/phien/claude__dk2-cau-noi-so-nhap.md` (D43–D45: bridge size M, D39–D41 in DK2 L2, test cap 5 per session). Steps 0–3 below are superseded by that plan. Original text: **DK2 planning (Opus, rule 12):** new branch + `docs/phien/DK2_GIAO_THUC.md`. Lot 1 must make the export
   a real Sổ nhập: converter v7 JSON → `SO_NHAP_CLB.xlsx` using `so_nhap.py` writers, test that the kiosk
   importer accepts it (FA/medal mode on) with 0 errors; decide with Truong whether Phòng/Khối/Link enter the
   CSV contract. Check whether D39–D41 are still wanted in the prototype or go straight into DK2 UI.
0. Apply D39–D41 to `docs/phien/DK1_BAN_MAU_V7.html` (republish the artifact if Truong wants it), re-run the
   Hick/Von Restorff count (≤ 7 per frame, 1 gold) and the full flow.
1. Ask Truong: update `DK1_GIAO_THUC.md` to match v7 (recommended), and keep or drop the 5-test cap.
2. Rewrite the protocol from v7: either move `DK1_BAN_MAU_V7.html` into `nguyen_mau/dk1/` (split into
   index/css/js) and add Playwright tests per lot, or skip straight to DK2 planning (Truong decides).
3. DK2 plan (size L): schema for rooms, club type/floor/grades/description, medals; Sổ nhập columns
   (CSV contract change → rule 7, ask Truong); .xlsx export via `so_nhap.py`; i18n via `i18n_errors.py`.

## Files touched
- docs/phien/claude__gracious-johnson-pnqvrg.md: this handoff
- docs/phien/DK1_GIAO_THUC.md: protocol (outdated, see above)
- docs/phien/DK1_BAN_MAU_V7.html: prototype v7 source (reference design, mock data only)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-25 | Opus | Evaluated reference site, 6 question rounds with Truong, wrote plan + protocol | no product code |
| 2026-11-25 | Opus | Built artifact prototype v1–v7 at Truong's request: Hick/Von Restorff redesign, student add/replace, admin-created teachers, tab sync, medal mode | handoff at ~400k context; protocol not yet updated |
| 2026-11-25 | Opus | Recorded Truong's v7 feedback as D39–D41 (per-day flow, chip overflow, drop receipt code) | not built; next session starts at Next steps 0 |
| 2026-11-25 | Opus | Recorded D42: v7 export not yet a valid Sổ nhập; next = DK2 planning (Next steps 00) | no code; handoff final |
| 2026-11-25 | Opus | Planned DK2 (Next step 00): protocol + branch file for `claude/dk2-cau-noi-so-nhap` | no code |
| 2026-11-25 | Opus | DK2 built on THIS branch at Truong's request; see `claude__dk2-cau-noi-so-nhap.md` Current state | awaiting CI |
