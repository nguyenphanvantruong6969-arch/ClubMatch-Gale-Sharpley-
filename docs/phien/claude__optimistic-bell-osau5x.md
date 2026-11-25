# Branch handoff: claude/optimistic-bell-osau5x

> Read CLAUDE.md, then THIS file, then `docs/phien/KD1_GIAO_THUC.md`. English. Cap 150 lines.

## Feature / goal
New item **KD1 — safe startup when WebView2 is missing** (code proposed by Opus 2026-11-25, approved by Truong "ok").
Symptom (Truong): on first launch after install the window opens, is very laggy, and nothing can be clicked.
Root cause (hypothesis, strongest): pywebview 6.2.1 `webview/platforms/winforms.py` → `_is_chromium()` returns
False when the WebView2 Runtime is absent (or .NET < 4.6.2) and pywebview SILENTLY renders with MSHTML (IE11).
IE11 cannot parse our JS (`=>`, `const` in `chung.js`, `i18n.js`, `js/*.js`) → `init()` never runs → static,
non-interactive page. No exception is raised, so `main._show_ui` never falls back to `browser_host`, and
`loi_khoi_dong.txt` does not say which renderer was used.
Ruled out (measured on Linux, fresh workspace, headless Chromium via `browser_host`): Python import 0.30 s,
`khoi_dong_workspace` 0.05 s, pywebview API discovery (174 functions) ~1 ms, UI interactive at ~0.4 s,
20 startup API calls ≤ 14 ms each, one 79 ms long task. So our Python/JS is not the cause on empty data.
Secondary (if WebView2 exists): `private_mode=True` default = fresh WebView2 profile every launch + Defender
scanning `_internal` DLLs on first run. Not fixed in KD1 (measure first, via L2 log).

## Plan (written by Opus; ticked by Sonnet)
- [ ] L1 (must) `main._show_ui`: on win32, after `import webview`, import `webview.platforms.winforms` and read
      its `renderer`. If `"mshtml"`: log one clear line (no traceback) and go straight to `browser_host.serve`
      (Edge/Chrome `--app=` window). Otherwise unchanged. Import failure keeps today's path (except → fallback).
- [ ] L2 (must) Startup timing in `loi_khoi_dong.txt`: renderer name, and elapsed ms since process start at:
      main start, workspace opened, before `webview.start()` / before `browser_host.serve`.
- [ ] L3 (optional) `HUONG_DAN_CAI_DAT.md`: 3-line note — if the app opens in a separate Edge window, the
      machine lacks "Microsoft Edge WebView2 Runtime"; installing it restores the native window.
- [ ] Registry: add a short KD1 entry to `SO_DANG_KY_33_MUC.md` + `ke_hoach_thay_doi.json` (pattern of MT2),
      CHANGELOG + TIEN_DO rows `KD1-L<n>`.

## Current state (overwrite each handoff)
- Done so far: diagnosis + plan only (no product code).
- Tests: new `tests/test_kd1_khoi_dong.py` (to write). Related: `tests/test_a13_12_browser_host.py`,
  any `tests/test_*main*`/`*chan_doan*` that exist.
- Open: unverified on Truong's Windows machine. Truong to check (a) "Microsoft Edge WebView2 Runtime" in
  Installed apps, (b) `msedgewebview2.exe` in Task Manager while the app is open.

## Decisions and gotchas (keep short)
- No algorithm/pipeline/schema change → invariants 1–5, 7, 8 untouched; invariant 6 untouched (no new API).
- Detect via the module attribute `webview.platforms.winforms.renderer`; do NOT pass `gui=` (pywebview 6
  still falls to MSHTML when forced to edgechromium without a runtime).
- Importing winforms early is safe: `webview.start()` imports the same cached module; it imports `clr`, whose
  failure must still reach the existing `except BaseException` fallback.
- Tests run on Linux: fake `webview` + `webview.platforms.winforms` in `sys.modules`, monkeypatch
  `sys.platform`, `browser_host.serve`, `chan_doan.go_dau_tai_ve`. Never launch a real window.
- `chan_doan.ghi` must never raise (keep it so).

## Next steps (ordered)
1. Coder session (Sonnet) with the prompt in `KD1_GIAO_THUC.md` §3.

## Files touched
- docs/phien/claude__optimistic-bell-osau5x.md: this handoff
- docs/phien/KD1_GIAO_THUC.md: protocol

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-25 | Opus | Diagnosed first-launch freeze, wrote KD1 plan + protocol | no product code |
