# Branch handoff: claude/dk8-giong-ban-mau

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/DK8_GIAO_THUC.md` (size M, AUTO: coder runs its own checker; no human input).

## Feature / goal
Item **DK8** (registry row to add: "Giao diện cổng đăng ký giống bản mẫu v8"). Truong, 2026-11-26: the real portal
(`dang_ky.html`) works (~90-95 % of v8 features) but LOOKS only ~60 % like the prototype `docs/phien/DK1_BAN_MAU_V8.html`.
Close the visual/layout gap. UI only: HTML/CSS/JS of the portal. Base = `claude/dk6-hoan-thien-phat-hanh` @ `7c5dae5`
(DK6 PASS, not yet in main). OUT: prototype-only parts (yellow "Bản mẫu" banner, "Thông tin để thử" box, "Đặt lại: Demo/
Cả trường", "Công cụ thử", fake data); portal backup restore (decision A); admin-password reset; DK7.

## Gaps already seen by the planner (2 screens, phase 2; screenshots were in chat, re-make them in L1)
- Landing: v8 = 3 large role cards (title, one-line purpose, status chip "Chưa mở" / "Đang mở · còn 2 ngày" /
  "Cần mật khẩu", count line "0 em đã gửi", "6 giáo viên đã đăng ký tài khoản"); real = 3 plain buttons in one box.
- Top bar: v8 sticky `.top` = brand "Cổng đăng ký CLB" + chip "Giai đoạn k/6 · <tên>" + right side role + "Thoát";
  real = none ("← Mở phần mềm xếp CLB" link + "Quản trị · <phase>" line instead).
- Admin "Việc bây giờ": v8 = tabs ABOVE one raised card holding the 6-step stepper, phase title ("Giáo viên đang đăng
  ký"), one-line explanation, mono count line ("6 giáo viên · 10 CLB đã gửi"), deadline line ("Hạn chót 28/11 03:53 ·
  còn 2 ngày. Đến hạn tự đóng.") with "Gia hạn" / "Đóng ngay" on the right; then a second card "CLB đã gửi" (table).
  Real = stepper above tabs, loose stack: textarea for teacher names, date input, "Đặt hạn", "+1 giờ/+1 ngày/Đóng ngay"
  as bare text buttons, gold "Đóng đăng ký giáo viên". Tabs: v8 "Thêm ▾" is a dropdown.
- Login screens: v8 = narrow centred card (max ~480 px), "← Về trang chọn vai trò" above, full-width gold "Vào",
  hint line under it ("Tự khoá sau 2 phút không thao tác.").
- Design tokens: v8 `:root` (`--ink --paper --raised --hairline --gold --gold-soft --moss --rust --focus`…) in its
  `<style>`; real uses `style.css` `.dk-*` rules (112 lines). Reuse v8 values; do not restyle the MAIN app.

## Plan (written by Opus; ticked by Sonnet)
- [x] **L1 (must) harness + shell.** NEW `du_lieu_test/chup_dk8.py`: builds the same SIMULATED state through the API
  (30 students, 6 teachers, 10 clubs, 3 rooms, like v8 "Demo nhỏ") and screenshots BOTH v8 (file://, password
  `admin123`, sample PINs on its landing page) and the real portal for this fixed list: landing; admin login; admin
  "Việc bây giờ" in phases 1,2,3,4,5,6; admin "Danh sách", "Cài đặt", "Thêm"; teacher login, teacher list, teacher
  club form; student login, student per-session screen, student review/sent screen. Output to a scratch folder
  (never commit PNGs). Write `docs/phien/DK8_KHAC_BIET.md`: one row per screen × difference, column "lô" (L1–L3) and
  "trạng thái" (còn khác / đã giống / khác chấp nhận + why). Then build the SHELL: design tokens scoped to the portal
  (`body.dk` or `dang_ky.css` — if a new css file, add it to `dang_ky.html` and to the build bundle test of DK6), top
  bar, landing role cards with status, login cards. Landing status needs counts: if `dk_trang_thai` lacks them, add
  read-only COUNTS only (no names/ids: it is public) + backend test.
- [x] **L2 (must) admin.** Tabs above content; "Việc bây giờ" = phase card (stepper inside, title, explanation,
  counts, deadline line + "Gia hạn" (menu +1 giờ/+1 ngày/date) and "Đóng ngay") + content cards per phase as v8
  (phase 1 checklist, 2 "CLB đã gửi", 3 approve table, 4 progress + demand, 5 score entry, 6 export). Move teacher bulk
  creation and other setup forms to where v8 has them (Danh sách / Cài đặt). "Thêm ▾" dropdown. Tables in cards.
  Keep every DKL/DK6 behaviour (auto-refresh guards, PIN slips, fold per grade, password change).
  **MILESTONE 1 after L2** (auto checker, see protocol).
- [ ] **L3 (must) teacher + student.** Teacher: club list cards + "+ Đăng ký CLB mới", form card with v8 field order
  and help lines. Student: v8 step flow per session "Tiếp: đặt huy chương" → "Tiếp: bài kiểm tra" → "Tiếp: xem lại và
  gửi" (DKL S7), confirm-identity step, sent screen "Đã gửi lúc …" + "Xong, thoát". Medal override UI MUST stay
  reachable for every student (invariant 2 exception); priority never reads rank.
- [ ] **L4 (optional) final pass.** Re-run the harness, fix remaining "còn khác" rows (≤ 10 small items), narrow
  width 390 px check (no horizontal scroll), focus ring + keyboard order. **MILESTONE 2 after L3 (or L4).**
- [ ] Close: CHANGELOG, TIEN_DO rows `DK8-L<k>`, registry row DK8, test-file count in `CLAUDE_CHI_TIET.md`, CI green.

## Acceptance (checker uses these)
- `DK8_KHAC_BIET.md`: zero rows "còn khác" for lots done; each "khác chấp nhận" has a reason.
- Same screens, same data: layout order, cards, chips, top bar match v8 by eye (screenshots ≤ 6 in the final review).
- No test weakened: UI tests may change SELECTORS only when an element moved; assertions/labels stay. Prefer keeping
  existing button texts and `name=` attributes so old tests pass untouched.
- `kiem_nhanh.py` 7/7 (invariant 1: no allocation change). No new library, no schema/CSV change.

## Current state (overwrite each handoff)
- Done: L1 (shell) and L2 (admin cards). Local: all portal UI tests green (50 + L2 7), ruff clean, kiem_nhanh 7/7.
  Next: push, wait CI green on the head, then MILESTONE 1 (create checker session), then L3.
- Harness: `.venv/bin/python du_lieu_test/chup_dk8.py <out> [--chi v8|that] [--ten landing,viec_1]` (~40 s for all 19 pairs).
- Kept button labels for old tests (Đăng nhập / Đăng xuất / Quản trị / Tạo tài khoản giáo viên / Đóng đăng ký giáo viên / +1 giờ / +1 ngày / Đóng ngay).
- Tests require: exactly ONE `ol.dk-gd`, one `#dkHan`, one textarea in the GV phase, every visible `.btn` in `#dkApp` >= 44 px high, one gold button per frame.

## Decisions and gotchas (keep short)
- Before each lot fetch and merge (`--no-edit`) `claude/dk6-hoan-thien-phat-hanh`, `claude/loving-babbage-8yqo7d`, `main`.
- Every push cancels running CI (~20 min). Batch; never push docs-only while CI you need is running.
- grep ALL tests for a UI string before changing it (DK6 broke a DK4 test that way).
- Playwright `clock.install()` makes `wait_for_function` hang: use `wait_for_timeout` + assert.
- Portal is school-vocabulary only; the MAIN app (`index.html`, `style.css` non-`.dk` rules) must not change look.
- Adding `tests/test_*.py` → update the count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (at close).
- v8 reloads its state from localStorage every 3 s: any harness change of `S` must call `save()`.
- Role cards: whole card clickable via `.dk-cua-nut::after`; the button keeps the exact role name (tests use `exact=True`).
- Top bar lives in `#dkTop` (outside `#dkApp`); `DK.hien` moves any `header.dk-dau` there.

## Next steps (ordered)
1. Coder: (L1 done) L2 → MILESTONE 1 (auto checker) → L3 → (L4) → MILESTONE 2 (auto checker) → CI gate → DONE.

## Files touched
- docs/phien/claude__dk8-giong-ban-mau.md, docs/phien/DK8_GIAO_THUC.md: plan
- L2: js/dang_ky_quan_tri.js, js/dang_ky_quan_tri_2.js, style.css (end block), tests/test_giao_dien_dk8_l2.py
- L1: api_dang_ky.py, dang_ky.html, js/dang_ky_{nen,quan_tri,gv_hs}.js, style.css (end block), du_lieu_test/chup_dk8.py, docs/phien/DK8_KHAC_BIET.md, tests/test_dk8_l1_dem_cong_khai.py, tests/test_giao_dien_dk8_l1.py

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-26 | Opus | Plan DK8 (visual parity with v8), auto protocol | no product code |
| 2026-11-26 | Sonnet | L1 done: harness, shell (top bar, role cards, narrow login), public counts | CI pending |
| 2026-11-26 | Sonnet | L2 done: admin tab bar on top, phase card + content cards, 2-col grids | CI pending |
