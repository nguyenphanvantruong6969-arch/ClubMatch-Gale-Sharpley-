# KD1 CHECK (Sonnet checker) — head 24ae55b

Tests (5 files) 54 passed; `ruff check .` clean; `kiem_nhanh.py --co-so origin/main` 7/7.
requirements*.txt, kiosk.spec: unchanged. Invariants 1–8: untouched (main.py startup layer + docs only).
Verified against pywebview 6.2.1 source (wheel): module-level `renderer` is set at import of
`webview.platforms.winforms` ('cef' | 'edgechromium' | 'mshtml'), so the detection is valid.

## Acceptance
- L1: covered (mshtml->serve 1x/start 0x, edgechromium->start, import failure->old path, linux never imports winforms,
  3 "webview is not a package" cases). OK.
- L2: covered (renderer name, 3 ms milestones, ghi never raises). OK.
- L3: 3 lines added. OK.
- `_show_ui`: only exact "mshtml" diverts; `_DungMshtml` is raised and caught inside the same try (cannot leak);
  KeyboardInterrupt/SystemExit still re-raised; src-order test in test_chan_doan.py passes.

## Findings
1. PLAUSIBLE (low) main.py:_renderer_winforms — importing winforms has side effects in the mshtml branch:
   pywebview runs `IE._set_ie_mode()` (writes HKCU FEATURE_BROWSER_EMULATION for the exe) and logs a deprecation
   warning at import, even though we then bypass pywebview. Harmless, but a registry write on a machine we
   claim not to use MSHTML on. No fix needed; mention in the log/changelog if wanted.
2. PLAUSIBLE (low) pywebview 6.2.1 winforms._is_chromium: `finally: winreg.CloseKey(net_key)` raises
   UnboundLocalError when the .NET NDP key is missing -> import fails -> `_renderer_winforms` returns "" ->
   log "renderer unknown" and old path (start() fails the same way -> BaseException fallback -> browser_host).
   Result is still correct; only the log wording ("unknown") is less precise. Docs mention only `renderer mshtml`.
3. PLAUSIBLE (low) main.py:_ghi_moc / _show_ui — "non-Windows byte-identical" holds for behaviour (winforms never
   imported), but `loi_khoi_dong.txt` on Linux/macOS now gets extra `moc ...` lines. Acceptable; say "behaviour",
   not "output", if the acceptance is re-quoted.
4. CONFIRMED (doc, trivial) SO_DANG_KY_33_MUC.md KD1 entry says "8 tests"; tests/test_kd1_khoi_dong.py has 11
   (4 + 4 + 3 parametrised). Also `ke_hoach_thay_doi.json` has no KD1 (CLAUDE.md: "same data, machine-readable";
   the handoff says MT2 is missing too, so likely accepted drift) and CLAUDE_CHI_TIET.md test-count line was edited
   (outside the "L3: only CHANGELOG/TIEN_DO/registry" wording).
5. PLAUSIBLE (doc) HUONG_DAN_CAI_DAT.md: "app tự mở bằng cửa sổ Edge riêng" is only true if Edge/Chrome exists;
   browser_host otherwise opens a normal tab (as the existing paragraph above already says). Fine on Win10/11.
6. Not a gap: kiosk.spec already lists `webview.platforms.winforms` + `clr` hiddenimports, so the early import
   works frozen; `renderer` attribute exists in 6.2.1 and absence/rename is handled by getattr -> "" -> old path.
   If pywebview is ever upgraded, re-check the attribute name (a rename silently disables KD1; log shows "unknown").
