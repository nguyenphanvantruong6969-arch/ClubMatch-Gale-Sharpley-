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
- **Workflow = phases in tab "Quản lý" (Truong, 2026-11-25; replaces the two independent switches):**
  `Chuẩn bị` (admin rooms + lists) → `GV đăng ký` (open, deadline) → `Duyệt CLB` (admin approves, edits quota
  / room) → `HS đăng ký` (admin presses open; students see ONLY approved clubs from the teacher phase;
  deadline) → `Đã đóng` (ready for allocation). One phase active at a time; a phase bar shows all five.
- Deadline: admin sets date+time per open phase; auto-closes by the machine clock (checked on load and every
  30 s); "Đóng ngay" and "Gia hạn" buttons. Auto-close of `GV đăng ký` moves to `Duyệt CLB`, never straight
  to `HS đăng ký`.
- After `HS đăng ký` opens: teachers cannot edit; admin may raise quota (≤ room capacity) or change room.
  Deleting a club or changing its session when students already chose it → warning with the number of
  affected students + confirm, and a line in an admin log (prototype: list on screen).
- Later (DK2): collection mode exports Sổ nhập; the allocation machine imports it (backup → validate → …).
  Not written straight to app.db. One kiosk for now (throughput not a concern yet, Truong 2026-11-25).
- **Round 3 (Truong, 2026-11-25):** scope = INPUT only (no post-allocation outputs).
  - Phases become 6: `Chuẩn bị → GV đăng ký → Duyệt CLB → HS đăng ký → Nhập điểm → Xuất`.
  - Tests are taken on Google Forms (not on the kiosk); admin enters scores in phase `Nhập điểm`: paste a
    block copied from the Forms sheet (columns mã HS + score, one club at a time, matched by mã HS; unknown
    IDs listed, not imported) AND a table students × ticked clubs to type / fix single scores.
  - Scale = what the software uses today: any number ≥ 0, decimal comma or dot (`doc_diem` in `so_nhap.py`);
    no fixed max; scores only compare within one club.
  - Ticked but no score → counted as **0** at export, and listed in a warning panel ("đã tick thi nhưng chưa
    có điểm") before export. Export enabled only after admin presses "Chốt điểm".
  - Student identity = mã HS + 4-digit PIN (mock PINs in data; admin can view/print the PIN list).
  - Up to **10 clubs per session**; at most 1 club won per session (already how multi-session allocation
    works). Tests: tick ≤ 5 in total (Sổ nhập also caps 5 per session — compatible).
  - Students may log in again and edit until the HS deadline; last submit counts; auto-logout after submit
    and after 60 s idle.
  - Export = one Sổ nhập after scores are locked. Real `.xlsx` needs a library in the browser (rule 7) →
    prototype exports a preview + JSON only; real `.xlsx` is written in DK2 by Python (`so_nhap.py` already
    writes workbooks).

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
- [ ] L1 Shell + mock data + role picker + Admin: phase bar + deadlines, rooms CRUD, student/teacher lists
- [ ] L2 Teacher registration (room/session clash, quota ≤ capacity, grades) + Admin approval table
- [ ] L3 Student flow: mã HS + PIN → per-session ranking (≤ 10) → tick ≤ 5 tests → confirm + receipt
- [ ] L4 Nhập điểm (paste + table, missing-score warnings, Chốt điểm) + export preview shaped like Sổ nhập
      `1. CLB` / `2. Học sinh` + JSON download (must-ship; demand counts optional)

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
