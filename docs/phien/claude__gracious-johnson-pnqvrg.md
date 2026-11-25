# Branch handoff: claude/gracious-johnson-pnqvrg

> Read CLAUDE.md, then THIS file, then `docs/phien/DK1_GIAO_THUC.md`. English. Cap 150 lines.

## Feature / goal
Item **DK1** (approved by Truong 2026-11-25; DK2 = real integration later): a clickable **prototype shell**
("cái vỏ") for the INPUT side of club allocation, so Truong's teacher can try it before anything real is
built. Roles: Admin (Quản lý), Giáo viên, Học sinh. Mock data, no backend, no app.db, no algorithm.
Ends by producing a Sổ nhập-shaped export for the allocation program. Post-allocation outputs: out of scope.
Insight source: https://magenta-crepe-416060.netlify.app/dang-ky-clb (evaluated 2026-11-25, see "Insight").

## Workflow (6 phases, one active at a time, phase bar in Quản lý)
`Chuẩn bị → GV đăng ký → Duyệt CLB → HS đăng ký → Nhập điểm → Xuất`

## Decisions (Truong, 2026-11-25, six question rounds — do not re-ask; later rounds override earlier)
Phases and timing
- D1 Phase change: admin opens a phase with a deadline (date+time); auto-close by machine clock (checked on
  load and every 30 s); "Đóng ngay", "Gia hạn". Auto-close of GV đăng ký → Duyệt CLB, never straight to HS.
- D2 "Mở cho học sinh" only from Duyệt CLB with no pending club and ≥ 1 approved.
- D3 Admin may step back a phase (e.g. Xuất → Nhập điểm); every step back is logged; each export gets a version.
Setup (Chuẩn bị)
- D4 Sessions defined by admin (default Thứ 2–Thứ 6; rename / add / remove). Grade list editable (default 6–12).
- D5 Rooms: admin list, name unique, capacity integer > 0; a room used by a club cannot be deleted.
- D6 Student list loaded by paste from Excel AND by CSV upload; preview with errors before saving
  (duplicate ID, missing name/class, grade unreadable).
- D7 Grade read from class name ("10A1" → 10, "6B" → 6); rows the app cannot read are flagged; admin fixes.
- D8 Student PIN: auto random 4 digits; printable PIN slips by class; admin can reset one PIN.
- D9 Student not on the list → refused at the kiosk (no on-the-spot add, no self-add).
- D10 Admin area: password (prototype shows the demo password), auto-lock after 2 min idle.
- D11 Backup/restore: "Sao lưu" downloads all state as JSON, "Khôi phục" loads it; banner if no backup in 60 min.
- D12 Mock data switch: "Demo nhỏ" (30 students, 8 rooms, ~8 clubs) and "Cả trường" (800 students, 40 clubs).
Teachers (GV đăng ký)
- D13 Self sign-up: school code (set by admin) + name + own 4-digit PIN; re-login = name + PIN. Admin sees all
  sign-ups and can delete fakes. (Overrides earlier "admin loads teacher list".)
- D14 A teacher may register several clubs, but never two in the same session (hard block).
- D15 Club fields: name (unique), session, room (only rooms free in that session; taken ones disabled with
  the club using them), quota (integer 1…room capacity), grades (≥ 1), test yes/no, Google Forms test link
  (when test = yes), description, basic requirements. No max-score field (scale below).
- D16 A club meeting twice a week = two separate clubs (one club = one session, as the algorithm expects).
- D17 Teacher edits own clubs only while GV đăng ký is open.
Approval (Duyệt CLB)
- D18 Admin approves / rejects, sets admin quota (blank = teacher quota; ≤ room capacity), changes room
  (same clash rule). Teacher quota and admin quota shown side by side.
- D19 After HS đăng ký opens: admin may raise quota or change room only; delete or session change of a club
  already chosen → "N học sinh bị ảnh hưởng" + confirm + log line.
Students (HS đăng ký)
- D20 Login: student ID + PIN; card "Họ tên · Lớp · Khối" + "Đúng là em".
- D21 Sees only approved clubs whose grades include theirs. Per-session tabs; up to 10 clubs per session
  (counter x/10); no duplicates; whole session may be empty; NO minimum (empty submit allowed).
  Allocation gives at most 1 club per session (existing multi-session behaviour).
- D22 Ranking: tap to add, ↑/↓ to reorder, ✕ to remove, plus drag-and-drop.
- D23 Tests: tick ≤ 5 in total, only among ranked clubs that have a test (Sổ nhập also caps 5 per session).
  Note: an untested club is still considered, behind students with a score.
- D24 Receipt after submit: per-session list + ticked tests with their Forms links + receipt code.
- D25 Edit until the HS deadline (last submit counts). Auto-logout after submit and after 60 s idle.
- D26 Students never see demand counts.
Scores (Nhập điểm) and export (Xuất)
- D27 Tests are taken on Google Forms (not on the kiosk for now). Admin enters scores here: paste a block
  per club ("mã HS ⇥ điểm", matched by ID; unknown IDs / not-ticked / bad numbers listed and skipped) AND a
  typing table students × ticked clubs.
- D28 Scale = current system: any number ≥ 0, comma or dot (`doc_diem` in `so_nhap.py`), no max; scores only
  compare within one club.
- D29 Ticked but no score = **no score** (absent → tier 2, lottery), shown in a warning list before export.
  (Overrides round-3 "count as 0".) "Chốt điểm" locks scores and opens Xuất.
- D30 Export: preview tables shaped like Sổ nhập `1. CLB` (Tên CLB, Buổi, Chỉ tiêu, Mã CLB + Phòng, Khối,
  Có thi, Link) and `2. Học sinh` (Mã, Họ tên, Lớp, NV1…NV10 per session, score beside tested clubs, blank =
  not tested/absent) + JSON download. Real .xlsx: DK2 via Python (no JS library, rule 7; Truong agreed).
- D31 Live admin views during HS đăng ký: progress by class, demand per club (NV1 and total vs quota),
  not-yet-registered list, change log (teacher edits, admin edits, re-submits, step backs).
- D32 Demo target: teacher on a laptop (1366×768 / 1280×800, mouse); touch still works.
- D33 Cut order if short of time (Truong: no preference, planner set): 1) 800-student mock, 2) live views
  D31, 3) paste score import, 4) drag-and-drop.

## Insight from the reference site (keep / avoid)
- KEEP: role doors; teacher self-registration; admin approval with "original quota" vs "admin quota";
  per-session preference lists; open/close control; admin-only demand counts.
- AVOID (seen in its export 2026-11-25): grade collected but unused; no validation ("a/a/a", same club as NV1
  and NV2); rank restarts per day with no session column; quota as text; ids by row order; free-text room;
  public admin page with student names and emails; chatbot-applied changes with 30-min sync drift.

## Plan (written by Opus; ticked by Sonnet)
- [ ] L1 Shell + setup: doors, admin password/lock, phase bar + deadlines + step back, sessions, grades,
      rooms, student list (paste + CSV) + grade parse, PINs + slips, school code, backup/restore, mock switch
- [ ] L2 Teacher sign-up/login + club form + approval table + post-open limits + log
- [ ] L3 Student login + per-session ranking + test ticks + receipt + edit/auto-logout
- [ ] L4 Nhập điểm (paste + table + warnings + Chốt điểm) + Xuất preview + JSON + live admin views

## Current state (overwrite each handoff)
- Done so far: planning only (this file + `docs/phien/DK1_GIAO_THUC.md`). No product code.
- Tests: none yet. Open problems: none; DK2 open questions below.

## Gotchas
- Prototype folder `nguyen_mau/dk1/` is not loaded by the app nor in `kiosk.spec`: invariants 1–8 untouched.
- Prototype-local Vietnamese messages allowed; DK2 must move them to `i18n_errors.py` (invariant 6).
- Deadlines trust the machine clock; DK2 should warn if the clock looks wrong.
- All data SIMULATED; never present prototype numbers as a survey.

## Open questions for DK2 (not this branch)
- Exact Sổ nhập columns for room / grades / link (CSV contract change → rule 7, ask Truong).
- Grade filter at collection vs registry item A5 in the algorithm; several kiosks later (merge by USB/LAN).

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-25 | Opus | Evaluated reference site, 6 question rounds with Truong, wrote plan + protocol | no product code |
