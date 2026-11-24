# SFB automation protocol (size M: ONE autonomous coder session, optional checker)

> Template: `docs/phien/_GIAO_THUC_GON.md` (token budget rules in its section 3 apply). Planner wrote this; the planner never codes the item.
> Branch `claude/sfb-stress-ui-sau-ux5`. Branch file `docs/phien/claude__sfb-stress-ui-sau-ux5.md`. Input analysis: `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.md` + `.patch`.

## 0. Decisions already made (do not ask Truong again)
- Run unattended until DONE or a stop condition. Never merge. Never open a second PR. Push only to this branch.
- Fixing tests = adapt them to the new UI; never skip, xfail, delete a test, or auto-open every `<details>`; never widen a time threshold to get green.
- Product change is limited to ONE CSS rule for narrow screens (L2). No i18n text change, no id change, desktop (> 800 px) layout unchanged.
- L2 lives in its own commit so Truong can revert it alone if he dislikes the look.

## 1. Lots (at most 4)
| Lot | Must? | Work | Done when |
|---|---|---|---|
| L1 | must | Review then `git apply docs/phien/ST_B_SUA_GIAO_DIEN_MOI.patch`; run every `tests_stress/b/test_*.py` separately | 63+ of 65 pass; the 2 failing are `test_b4_do_rong_man_hinh[390]` and `[768]` (wait for L2); `ruff check .` clean |
| L2 | must | Append to `style.css`: `@media (max-width: 800px) { .menu-khac-hop.ux5a-hop-rong { position: fixed; left: 12px; right: 12px; top: auto; bottom: 12px; width: auto; max-height: 70vh; overflow: auto; } }` (verified in the memo). Add `tests/test_giao_dien_sfb_menu_hep.py` (red first): at widths 390, 768 (with and without class select) and 1280, open every `details.menu-khac` that has `.ux5a-hop-rong` on tabs `results` and `others` and assert its box is inside `[0, viewport width]`. Save 3 screenshots (390 px: open menu on Kết quả, open menu on Chi tiết, 1280 px unchanged) to `docs/ke_hoach/ux/anh/sfb/`, `deviceScaleFactor: 1` | new test green, `test_b4_do_rong_man_hinh[390,768]` green, 1280 px result identical |
| L3 | optional | Delete `docs/phien/claude__great-edison-6ry675__TU_CHAY.md` and `claude__ux1-tich-hop-vao-main__TU_CHAY.md`; set TIEN_DO rows still saying "xong, chờ CI" for SF/UX5/UX1F to the real state (main CI #1522 green); add TIEN_DO + CHANGELOG rows for SFB; recount `ls tests/test_*.py | wc -l` into CLAUDE_CHI_TIET; make `tests_stress/b/conftest.py` write screenshots to a temp dir unless env `RBDA_ANH_ST_B` is set | rows match reality; running stress tests leaves `git status` clean |
| L4 | optional | (a) PDF export progress: poll `get_tien_do_xuat()` every 500 ms in `chayXuatPdf` (`js/03_ket_qua.js`), show done/total on the button, new vi+en text in `i18n.js` (no ALL CAPS, no raw `{detail}`), test in `tests/`; (b) dedicated zip error code for ST-B-011 in `i18n_errors.py` then `python tao_i18n_js.py`, test | tests green; drop the lot (revert) if it needs more than 3 CI rounds |

## 2. Roles
- One coder session (Sonnet). Optional checker (Truong starts it with the prompt in section 5 when the coder prints `STATUS: DONE`).
- No subagents (CLAUDE.md rule 10). Context near 400k tokens: update the branch file, commit, push, stop.

## 3. Loop per lot
Red test first (for L2/L4), minimal change, related tests only (`-q --tb=line | tail -15`), `ruff check .`, `python kiem_nhanh.py | tail -10` once per lot, CHANGELOG line, one commit per lot, then continue. Tests touching Chromium: one file per run. Never run the full suite locally.

## 4. CI loop (repeat until DONE)
1. Push once per round (a new push cancels the running CI). After the first push open ONE PR into `main` titled "SFB: stress UI after UX5 (tests + narrow-screen menus)" with a body listing lots, verification and the known flake; mirror the repo's PR template if it exists.
2. Wait with `mcp__claude-code-remote__send_later` (delay_minutes 15) and end the turn. Also create ONE recurring scheduled task (`create_trigger`, every 30 minutes, prompt "continue SFB per docs/phien/SFB_GIAO_THUC.md section 4") as a backup and delete it when DONE.
3. On wake-up: `mcp__github__actions_list` for the branch, then `get_job_logs` (`run_id` + `failed_only`). Poll at most once per 10 minutes.
4. Red job: find the ROOT CAUSE, reproduce with a test, minimal fix, back to the lot loop. Windows timing test `test_a13_12_browser_host.py` red: rerun the job once (`mcp__github__actions_run_trigger` rerun_failed_jobs; if unavailable add a real line to the branch file, never an empty commit); real failure only if red in 2 separate runs.
5. Green: `mcp__github__pull_request_read` (get). `mergeable_state` "unknown": wait 60 s and ask again (max 5 times). "dirty": `git fetch`, `git merge origin/main`, resolve (CHANGELOG/TIEN_DO keep both sides, `style.css` keep both, recount the test-file line), fix semantic clashes in TESTS, back to step 1. "blocked" (review required): stop and report.
6. DONE when: (a) every job of the head's latest run is success (coverage gate included), (b) `mergeable_state` = "clean", (c) `git rev-list --left-right --count origin/main...HEAD` = "0 N", (d) per-file runs of `tests_stress/b` show all 65 passing (the keyboard test may be re-run alone once if it flakes), (e) `git status` clean (no `docs/phien/anh_st_b` changes committed), (f) branch file updated (Plan ticked, Current state, Session log).
7. Stop early (write the branch file, report): same root cause 3 rounds; more than 10 CI rounds; a product change beyond the L2 CSS rule seems needed; invariant conflict; new library needed.
8. Last message must contain exactly one line: `STATUS: DONE <head sha>` or `STATUS: STOPPED <reason>`; then a short Vietnamese report (what changed, CI rounds and root causes, remaining items, the 3 screenshots to look at). SIMULATED data.

## 5. Optional checker prompt (Truong pastes when the coder printed STATUS: DONE)
```
Read CLAUDE.md, docs/phien/claude__sfb-stress-ui-sau-ux5.md and docs/phien/SFB_GIAO_THUC.md. You are the CHECKER (read-only, no edits, no pushes). Check out claude/sfb-stress-ui-sau-ux5. Verify: (1) the diff only touches tests_stress/b/*.py, tests/test_giao_dien_sfb_menu_hep.py, style.css (one @media rule), docs, and L3/L4 files if done; (2) no test skipped/xfailed/deleted, no threshold widened, no auto-open-all-details; (3) the L2 test fails without the CSS rule (revert it locally in a scratch copy and run it) and passes with it; (4) desktop CSS unchanged; (5) CI of the head is green and the PR is mergeable. Report PASS or a numbered list of defects in Vietnamese, ≤ 30 lines.
```
