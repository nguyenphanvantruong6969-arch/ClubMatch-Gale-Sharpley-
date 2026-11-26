# DK3 → DK6 automatic loop (Truong 2026-11-25: plan, then coder/checker sessions, NO human input)

> Orchestrator = session `session_01YVAyu2z93KyWsnJMXBdS4t` (Opus). Truong approved: coding without asking,
> NEW SQLite tables for DK3 (rule 7 satisfied), child sessions (rule 10 satisfied). Token rules:
> `docs/phien/_GIAO_THUC_GON.md` §3. Decisions D1–D45: `claude__gracious-johnson-pnqvrg.md`,
> `claude__dk2-cau-noi-so-nhap.md`. Reference design: `docs/phien/DK1_BAN_MAU_V8.html`.

## Defaults (do not ask)
- Students register on the program's computers only (no LAN/phone server).
- UI = v8 look built with `style.css` tokens (light only, local fonts), no new library.
- New error codes appended at END of `i18n_errors.py`, then `python tao_i18n_js.py`.
- Blocked → one "Needs Truong" line in the branch file; continue with the next lot. Never ask a human.

## DK3 — branch `claude/dk3-cong-dang-ky-that` (base: `claude/gracious-johnson-pnqvrg`)
- L1 schema: tables rooms, teachers, registration phases/deadlines, registrations (per-session ranked choices,
  tests, medals) via `di_tru_schema` (idempotent, backup first). Test: migrate twice = same; old data kept.
- L2 `api_dang_ky.py`: {ok,data,errors}; admin password + PINs hashed (pbkdf2, salt); teacher sign-up and
  admin-created teachers; rules D2, D14, D15, D18/D19, D21, D44; medals ≤ 1 per club, never Tự do; medals
  stored, `compute_club_priority` never reads rank (invariant 2, exception D2 path A).
- L3 UI: v8 screens as new `js/dang_ky_*.js` + CSS section; ≤ 1 gold button and ≤ 7 items per frame (D37);
  `tests/test_giao_dien_dk3_*.py` (one shared page fixture).
- L4 "Xuất Sổ nhập": JSON `dinhDang` 1 → `dk2_so_nhap.ghi_tu_ban_mau`; test imports 0 errors (FA) + allocates.

## DK4 — branch `claude/dk4-noi-thang-bo-xep` (base: DK3 branch after PASS)
- L1 `dang_ky_sang_xep.py`: DK3 tables → the rows `import_so_nhap` writes; equal to the dk2 + import path.
- L2 "Chốt và xếp": pipeline order invariant 5, one transaction, rollback; `run_history` append-only.
- L3 `tests/test_dk4_hai_duong_trung_khit.py`: both paths, 3 datasets × 20 seeds, every `match_results` row equal.
- L4 button + result summary (v8 style), Playwright test.

## DK5 — branch `claude/dk5-dien-tap` (base: DK4 branch after PASS) · size M
- L1 `du_lieu_test/dien_tap_dk5.py` + `tests/test_dk5_dien_tap.py`: seeded 798 students / 40 clubs through the
  DK3/DK4 API only: setup → teachers → approval → students submit (interleaved, as several kiosks) → scores →
  "Chốt và xếp" → export. Asserts: 0 errors, every student has a result row, run_history +1, time budget logged.
- L2 robustness: backup → restore round-trip equal; idle lock; deadline auto-close; re-submit keeps last; kill
  mid-run (exception injected) → rollback, DB unchanged (invariant 5). Data labelled MÔ PHỎNG.
- L3 Playwright smoke `tests/test_giao_dien_dk5_toan_trinh.py`: one admin, one teacher, one student path.

## DK6 — branch `claude/dk6-goi-phat-hanh` (base: DK5 branch after PASS) · size S
- L1 docs: `docs/huong_dan/DK6_BAT_DAU_NHANH.md` (1 page: install, first setup, 6 phases) and
  `docs/huong_dan/DK6_XU_LY_SU_CO.md` (forgot PIN, power loss, restore backup, WebView2 missing).
- L2 build: `kiosk.spec` includes new js/ files and assets; CI "Build Windows executable" green; CHANGELOG
  version note. No git tag, no GitHub release, no PR (Truong does that).

## Per lot (coder)
Failing test → code → lot tests + ≤ 3 related (`-q --tb=line 2>&1 | tail -15`) → `ruff check .` →
`.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10` → CHANGELOG + TIEN_DO row `DK<n>-L<k>` → commit
`DK<n>-L<k>: …` → push. After the last lot: registry row, test-file count in CLAUDE_CHI_TIET.md, CI green
(`mcp__github__actions_list`, failed_only logs ≤ 60 lines). Never rebase/force-push, no PR.

## Loop
coder writes `READY | head <sha>` in its branch file and messages the orchestrator (send_message, one line) →
orchestrator starts a checker → checker writes `PASS` or `FIX <≤10 lines>` in `<branch file>__checker.md`, pushes,
messages the orchestrator → FIX is forwarded to the coder (max 2 FIX rounds, then "Needs Truong" + continue).
DK3 PASS → DK4 → DK5 → DK6, each started the same way after the previous PASS. After DK6 PASS: orchestrator
reports to Truong (branches in order, what to merge). Checker for DK5 also re-runs DK3/DK4 lot tests.
