# DK1 protocol — size S (1 Sonnet coder, self-check + Truong tries it)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 budget rules apply). Spec, decisions, insight:
> `docs/phien/claude__gracious-johnson-pnqvrg.md`. Size S: standalone prototype, no backend, no schema,
> no algorithm, no invariant 1–8 in play.

## 0. Decisions already made (do not ask Truong)
- Files ONLY under `nguyen_mau/dk1/`: `index.html`, `dk1.css`, `dk1_du_lieu.js` (mock data), `dk1.js`.
  Opens by double-click (file://), offline, no CDN, no new library, no change to `index.html`, `js/`,
  `style.css`, `kiosk.spec`, Python code. Test: `tests/test_dk1_nguyen_mau.py` (Playwright, one page fixture).
- Mock data: 5 sessions Thứ 2–6; 8 rooms (name, capacity 10–40); 6 teachers (mã GV, name); 30 students
  (mã HS, họ tên, lớp, khối 6–12); 4 pre-registered clubs (2 approved, 1 pending, 1 rejected).
- State in one object saved to localStorage (try/catch; page works without it). Header button
  "Đặt lại dữ liệu mẫu". Banner "Bản mẫu — dữ liệu giả".
- Touch-sized targets (≥ 44 px), visible focus ring `--focus-ring`, Vietnamese UI, works at 1280×800 and 390 px.
- Anything outside this → "Needs Truong" line in the branch file, then continue.

## 1. Branch and lots
| Branch | Lots |
|---|---|
| `claude/gracious-johnson-pnqvrg` | L1 shell+admin · L2 teacher+approval · L3 student · L4 export preview (optional) |
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push. No PR.

## 2. Acceptance (`kiem_nhan`)
- L1: home shows 3 role doors; Admin can add / edit / delete a room (name unique, capacity integer > 0; a room
  used by a club cannot be deleted); sees student and teacher lists; two switches (GV form, HS form) — when
  off, that role's door shows "Đang đóng" and its form cannot be submitted.
- L2: teacher logs in with name + mã GV (wrong code refused). Form: club name (unique, required), session,
  room (dropdown lists only rooms free in that session; taken ones shown disabled with the club using them),
  quota (integer 1…room capacity; above capacity → blocked with message), grades (≥ 1 ticked), test yes/no,
  description, requirements. "CLB của tôi" lists own clubs with status; editable while "Chờ duyệt".
  Admin approval table: approve / reject, admin quota (blank = teacher quota, still ≤ room capacity), change
  room (same clash rule), shows teacher quota and admin quota side by side.
- L3: student types mã HS → card "Họ tên · Lớp · Khối" + "Đúng là em" button; unknown code refused. Per-session
  tabs: left = approved clubs allowing the student's grade (card: name, room, teacher, description,
  requirements, "Có thi" badge); right = ranked list. Add by click or drag; reorder by drag or ↑/↓; remove ✕;
  a club cannot appear twice; empty session allowed. Step 2: clubs with a test that are in the ranked lists,
  tick ≤ 5 (6th checkbox disabled, counter "x/5"); note that an untested club is still considered but ranks
  behind students with a score. Step 3: summary per session + tests → "Gửi" → receipt with a code;
  re-entering the same mã HS reopens the saved choices while the HS form is open. No demand counts anywhere
  in the student view.
- L4 (optional): Admin tab "Xem trước xuất" renders two tables shaped like Sổ nhập `1. CLB`
  (Tên CLB, Buổi, Chỉ tiêu, Mã CLB, + Phòng, Khối, Có thi) and `2. Học sinh` (Mã, Họ tên, Lớp, NV per session,
  tests), approved clubs only, plus admin-only demand count per club. No file write needed.

## 3. Coder loop per lot
Failing Playwright case in `tests/test_dk1_nguyen_mau.py` (load `nguyen_mau/dk1/index.html` via file URL,
`--trace off`) → minimal code → `python -m pytest -q tests/test_dk1_nguyen_mau.py --tb=line 2>&1 | tail -15`
→ `ruff check tests/test_dk1_nguyen_mau.py` → `kiem_nhanh.py | tail -10` → `soat-ma` tiers (report only) →
CHANGELOG + TIEN_DO row `DK1-L<n>` → commit `DK1-L<n>: …` → push `-u origin claude/gracious-johnson-pnqvrg`.
Tick the Plan in the branch file. After the last lot: update "Current state", write `DK1 READY | head <sha>`.

## 4. Truong's check (replaces the checker)
Open `nguyen_mau/dk1/index.html` in Edge. Walk: Admin adds a room → teacher registers a club in it → admin
approves → a grade-6 student ranks clubs and ticks tests → submit. Then show the teacher; note feedback for DK2.

## 5. Coder prompt (Truong pastes this into a new Sonnet session)
See the code block at the end of Truong's planning reply (2026-11-25); same text:
"Item DK1, branch claude/gracious-johnson-pnqvrg. Read CLAUDE.md, docs/phien/claude__gracious-johnson-pnqvrg.md,
docs/phien/DK1_GIAO_THUC.md. Build lots L1→L3 (L4 if budget allows) per §2, loop §3, budget
_GIAO_THUC_GON.md §3. Only files under nguyen_mau/dk1/ and tests/test_dk1_nguyen_mau.py plus CHANGELOG/TIEN_DO.
Stop and write 'Needs Truong' for anything outside §0."
