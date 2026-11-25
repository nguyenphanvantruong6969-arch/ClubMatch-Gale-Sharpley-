# KD1 protocol — size S (1 Sonnet coder, self-check + Truong tries it on Windows)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (budget rules §3 apply). Spec, lots, gotchas:
> `docs/phien/claude__optimistic-bell-osau5x.md`. Size S although it touches `main.py`: two small changes in the
> startup layer, no API, no algorithm, no schema, no invariant 1–8 in play.

## 0. Decisions already made (do not ask Truong)
- Item KD1. On Windows, if pywebview picked MSHTML, use the existing `browser_host` fallback instead.
- Detection = `webview.platforms.winforms.renderer == "mshtml"`. No `gui=` argument, no pywebview upgrade,
  no new library, no change to `requirements*.txt` or `kiosk.spec`.
- Log lines go through `chan_doan.ghi` into `loi_khoi_dong.txt` (unaccented ASCII like the existing lines).
- Anything outside this → "Needs Truong" in the branch file, then continue.

## 1. Branch and lots
| Branch | Lots |
|---|---|
| `claude/optimistic-bell-osau5x` | L1 MSHTML → browser fallback · L2 startup timing log · L3 install-guide note (optional) |
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push. No PR.

## 2. Acceptance (`kiem_nhan`)
- L1: with fake renderer `"mshtml"` on `win32`: `browser_host.serve` called once, `webview.start` NOT called,
  log has one line naming MSHTML/WebView2, no traceback. With `"edgechromium"`: `webview.start` called,
  `serve` not called. With `import webview.platforms.winforms` raising: falls back to `serve` as today.
  Non-Windows: behaviour byte-identical to before (winforms never imported).
- L2: log contains the renderer name and `+<n> ms` milestones for main start, workspace opened, and the
  window/browser start; `chan_doan.ghi` still never raises.
- L3: `HUONG_DAN_CAI_DAT.md` gains ≤ 4 lines; no other doc changed except CHANGELOG, TIEN_DO, registry.

## 3. Coder loop per lot
Failing test in `tests/test_kd1_khoi_dong.py` → minimal code → that file + `tests/test_a13_12_browser_host.py`
+ ≤ 2 related, quiet (`-q --tb=line 2>&1 | tail -15`) → `ruff check main.py chan_doan.py tests/test_kd1_khoi_dong.py`
→ `kiem_nhanh.py | tail -10` → `soat-ma` four tiers (report only) → CHANGELOG + TIEN_DO row `KD1-L<n>` →
commit `KD1-L<n>: …` → push `-u origin claude/optimistic-bell-osau5x`. Tick the Plan in the branch file.
After the last lot: add the KD1 registry entry, update "Current state", write `KD1 READY | head <sha>`.

## 4. Truong's check (replaces the checker)
On the Windows machine that froze: install the CI build, launch once. Expected: a separate Edge app window that
responds to clicks, and `loi_khoi_dong.txt` shows `renderer mshtml` plus the ms milestones. Send the log back.
