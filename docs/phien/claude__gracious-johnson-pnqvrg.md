# Branch handoff: claude/gracious-johnson-pnqvrg

> Read CLAUDE.md, then THIS file, then `docs/phien/DK1_GIAO_THUC.md`. English. Cap 150 lines.

## Feature / goal
Item **DK1 (new, not in the 33-item registry; Truong approves the code)**: a clickable **prototype shell**
("cái vỏ") for registration, so Truong's teacher can try the input flow before anything is built for real.
Three roles: **Admin** (rooms, lists, approval, open/close switches), **Giáo viên** (register a club with
room, session, quota, grades, entrance test yes/no, description), **Học sinh** (rank clubs per session,
tick up to 5 entrance tests, confirm). Mock data only, no backend, no app.db, no algorithm. Insight source:
https://magenta-crepe-416060.netlify.app/dang-ky-clb (evaluated 2026-11-25, see "Insight" below).
In-kiosk entrance exams and the real integration are LATER (DK2), not this branch.

## Truong's decisions (2026-11-25, do not re-ask)
- Runs inside the kiosk look (offline, same machine). Prototype = standalone page, NOT wired into `index.html`.
- Rooms: admin pre-creates a room list with capacity; teacher picks a room free in that session; app blocks
  two clubs in one room in one session and blocks quota > room capacity.
- Admin approves every club before students see it (approve / reject, edit quota, change room).
- Teacher fields: name of club, session, quota, allowed grades (Khối 6–12), entrance test yes/no,
  description + basic requirements.
- Login: admin pre-loads student list (mã HS, họ tên, lớp, khối) and teacher list; students type mã HS,
  teachers pick name + type mã GV. Unknown code → refused (fixes the "a / a / a" problem seen on the site).
- Student preferences: per session, click or drag clubs into a ranked list; no duplicates; empty session
  = not attending that session. Only approved clubs of the student's grade are shown.
- Entrance tests: student ticks at most 5 clubs that have a test, chosen among clubs in their preferences.
- Time budget: one night. Size S.

## Insight from the reference site (keep / avoid)
- KEEP: role picker home (3 doors); teacher self-registration; admin approval layer with "original quota"
  vs "admin quota"; per-session preference lists; open/close switches; admin-only live demand counts.
- AVOID (seen in its export 2026-11-25): grade collected but not used to filter or exported; no
  validation (student "a/a/a", same club NV1 and NV2); rank restarts per day with no session column; quota
  as text; club ids by row order; free-text room, no capacity/clash check; admin page public with student
  names and emails; changes applied via chatbot with 30-min sync drift.
- Do NOT show demand counts to students (they would dodge popular clubs; truthful ranking is the point of
  Gale–Shapley).

## Plan (written by Opus; ticked by Sonnet)
- [ ] L1 Shell + mock data + role picker + Admin: rooms CRUD, student/teacher lists (view), switches
- [ ] L2 Teacher registration (room/session clash, quota ≤ capacity, grades) + Admin approval table
- [ ] L3 Student flow: login by mã HS → per-session ranking → tick ≤ 5 tests → confirm + receipt
- [ ] L4 (optional) Admin export preview shaped like Sổ nhập sheets `1. CLB` / `2. Học sinh` + demand counts

## Current state (overwrite each handoff)
- Done so far: planning only (this file + `docs/phien/DK1_GIAO_THUC.md`).
- In progress: none. Tests: none yet. Open problems: item code DK1 awaiting Truong's OK.

## Decisions and gotchas (keep short)
- Prototype folder `nguyen_mau/dk1/` is not loaded by the app and not in `kiosk.spec`: invariants 1–8 untouched.
- No new library (rule 7): native HTML5 drag-and-drop + up/down buttons (touch kiosks may not fire drag).
- Prototype-local Vietnamese messages are allowed here; DK2 must move them to `i18n_errors.py` (invariant 6).
- Colour tokens copied from `style.css :root` (--ink, --paper, --gold, --moss, --rust, --focus-ring);
  fonts as in `style.css` (Be Vietnam Pro bundled, no network).
- localStorage wrapped in try/catch; "Đặt lại dữ liệu mẫu" button restores mock data.
- All data is SIMULATED; label the page "Bản mẫu — dữ liệu giả".

## Next steps (ordered)
1. Truong OKs item code DK1, then starts the coder with the prompt in `DK1_GIAO_THUC.md` §5.
2. After Truong's teacher tries it: write DK2 plan (schema: rooms, club grades/description/test flag; A5 grade
   filter; import to Sổ nhập; size L).

## Files touched
- docs/phien/claude__gracious-johnson-pnqvrg.md: this handoff
- docs/phien/DK1_GIAO_THUC.md: protocol + coder prompt

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-25 | Opus | Evaluated reference site, asked Truong 8 questions, wrote plan + protocol | no product code |
