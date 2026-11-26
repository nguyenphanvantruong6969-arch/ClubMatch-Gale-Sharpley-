# DK1 protocol — size S (1 Sonnet coder, self-check + Truong tries it)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 budget rules apply). ALL decisions D1–D33:
> `docs/phien/claude__gracious-johnson-pnqvrg.md`. Size S: standalone prototype, no backend, no schema,
> no algorithm, no invariant 1–8 in play. Volume is large for one night → follow the cut order (D33).

## 0. Rules (do not ask Truong)
- Files ONLY under `nguyen_mau/dk1/`: `index.html`, `dk1.css`, `dk1_du_lieu.js` (mock data), `dk1.js`
  (split into more `dk1_*.js` if > 800 lines). Opens by double-click (file://), offline, no CDN, no new library,
  no change to `index.html`, `js/`, `style.css`, `kiosk.spec`, Python. Test: `tests/test_dk1_nguyen_mau.py`
  (Playwright, file URL, one shared page fixture, fake clock via `page.clock`).
- Banner "Bản mẫu — dữ liệu giả". Colours from `style.css :root`; laptop first (D32), usable at 390 px;
  targets ≥ 44 px; focus ring `--focus-ring`. Vietnamese UI. State = one object in localStorage (try/catch).
- Anything outside this → "Needs Truong" line in the branch file, then continue.

## 1. Branch and lots
| Branch | Lots |
|---|---|
| `claude/gracious-johnson-pnqvrg` | L1 shell + setup · L2 teacher + approval · L3 student · L4 scores + export |
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push. No PR.
- Cut order D33 (drop from the top only); record anything cut in the branch file "Current state".

## 2. Acceptance (`kiem_nhan`) — one or more Playwright cases per bullet group
- L1 = D3–D12 + D1 timing: doors; admin password + 2-min lock; phase bar; deadline auto-close with fake
  clock; step back logged; sessions/grades editable; rooms CRUD rules; paste AND CSV student load with error
  preview; "10A1" → 10; PIN generate/reset/print view; school code; backup → restore round-trip equal; mock switch.
- L2 = D13–D19 + D2: sign-up with wrong school code refused; re-login name + PIN; same teacher same session
  blocked; taken room disabled; quota > capacity blocked; approval with admin quota; "Mở cho học sinh"
  disabled while a club is pending; post-open delete shows affected count + log line.
- L3 = D20–D26: unknown ID / wrong PIN refused; grade filter; 11th club blocked; no duplicates; empty submit
  accepted; 6th test tick disabled; test ticks only on ranked clubs; receipt shows links; re-login reopens
  choices; after deadline login shows "Đã đóng"; auto-logout after 60 s idle (fake clock); no demand numbers.
- L4 = D27–D31: paste block fills matched scores and lists skipped rows; "8,5" and "8.5" equal; negative
  refused; missing score listed and exported blank; Chốt điểm → Xuất; preview columns per D30; JSON
  download; export version increments after a step back; live views D31 (cuttable).

## 3. Coder loop per lot
Failing Playwright case → minimal code → `python -m pytest -q tests/test_dk1_nguyen_mau.py --tb=line 2>&1 |
tail -15` → `ruff check tests/test_dk1_nguyen_mau.py` → `kiem_nhanh.py | tail -10` → `soat-ma` tiers (report
only) → CHANGELOG + TIEN_DO row `DK1-L<n>` → commit `DK1-L<n>: …` → push `-u origin claude/gracious-johnson-pnqvrg`.
Tick the Plan. After the last lot: add DK1 to the registry, update "Current state", write `DK1 READY | head <sha>`.

## 4. Truong's check (replaces the checker)
Open `nguyen_mau/dk1/index.html` in Edge on a laptop. Walk all 6 phases with "Demo nhỏ", then "Cả trường" and
check lists stay fast. Show the teacher; note feedback for DK2.
