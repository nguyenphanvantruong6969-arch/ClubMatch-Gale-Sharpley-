# GT4 — Hoàn thiện sau tích hợp GT1+GT2+GT3 (lot specs)

> Opus-style plan written 2026-11-17 by a Sonnet session at Truong's request. Source: `docs/ke_hoach/gt/GT4_RA_SOAT.md`
> (findings R0–R10, evidence, personas). English (cheap); user-facing text is plain Vietnamese (+ English in `i18n`).
> Item code **GT4** (new; Truong approves by starting the run). Work branch `claude/gt-hoan-thien`, created from
> `origin/claude/admiring-fermat-yf077m` (= `claude/gt-tich-hop` c9e3830 + these plan files). No PR. Truong merges to `main`.

## Rules (inherit CLAUDE.md invariants 1–8 and rules 1–11; GT-protocol `docs/phien/GT_GIAO_THUC.md` §3 applies)
- **No new schema, no new library, CSV contract unchanged** (rule 7). Only code/UI/text/docs/tests.
- Invariant 1: `kiem_nhanh.py --co-so origin/main --so-seed 5` must stay 7/7 after every lot. Invariant 2: nothing new
  reaches `compute_club_priority`. Invariant 4: never UPDATE/DELETE `run_history`. Explanations are **reports only**.
- Text rules: no "bạn / các em / em" in `i18n.js`, `i18n_errors.py`, `index.html` display text (kiem_nhanh `chu_cam`);
  every new `i18n.js` key in both vi and en; after `i18n_errors.py` edits run `python tao_i18n_js.py`.
  (Sentences in `fa_ly_do.py` are the one place that speaks to the student; see L4.)
- Test first (failing test from "Done when"), minimal fix, related tests only (`tests/test_gt*`, plus any file that greps
  an identifier you changed). **Never skip, weaken or delete an existing test.** Where a decision below changes behaviour
  that an existing test asserts, change that assertion in the same commit and name the decision (D4-n) in the message.
- Before every push: `soat-ma` (`kiem_nhanh.py` + four tiers, report only). Then `CHANGELOG.md` row + `docs/ke_hoach/TIEN_DO.md`
  row `GT4-L<n>`; new test file → update the `tests/` row of `docs/ke_hoach/CLAUDE_CHI_TIET.md` (file count + collect count).
- All data SIMULATED; fake accounts/passwords only.

## Decisions taken by this plan (Truong can veto by editing this file before starting)
| Id | Decision | Why |
|---|---|---|
| D4-1 | `vao_che_do_hoc_sinh` becomes `quan_tri` (enter) like exit; teachers no longer see its button | teacher could lock the kiosk and not leave |
| D4-2 | Viewing one student's explanation (`get_giai_trinh_hoc_sinh`) is audited (one row, id only) | private data; today only exports are logged |
| D4-3 | Student self-lookups are logged with `nguoi = NULL, vai = NULL` (never the active admin), student id only, never the code | log must not claim an admin looked, nor hold secrets |
| D4-4 | Recovery for the packaged `.exe` = command-line flag `--xoa-tai-khoan` handled by `main.py` before any window opens, + a `.bat` helper; no button inside the app that wipes accounts | locked-out school needs a path without Python; in-app wipe would defeat the login |
| D4-5 | First-admin hijack window: mitigated by wording + retype-password + docs ("create the first admin before the kiosk faces students"); no extra secret | no safe place to keep a setup secret on a single offline kiosk |

## Lots (do in this order; one commit per lot; `GT4-L<n>: ...`)
### L0 — official-only reader (R0, blocking)
`api_xuat._giai_trinh_dung_lai` must read `run_history` through `loc_chinh_thuc(cur)` (as `api.py` and `fa_sau_xep.py` do),
for BOTH the `lan` query and any later run lookup. Then grep every other `FROM run_history` / `ket_qua_thu` reader and
list in the commit message which are official-only and which are intentionally not (trial list in `api_tieu_chi`).
Done when: new `tests/test_gt4_chay_thu_giai_trinh.py` — official run → `run_thu` with a rule that changes ≥1 student
(e.g. `{"priority": "tier"}`) → for EVERY student `get_giai_trinh_hoc_sinh` result equals the official `match_results`
(club per buổi), `du_lieu_da_doi` is False, `run.run_id` is the official run; same for `export_phieu_giai_trinh`
(n pages, no trial text) and `tra_cuu_hoc_sinh`; repeated after a second trial and after `ap_dung_tieu_chi` (config saved,
no official re-run yet: explanation still matches stored official results, `du_lieu_da_doi` may be True because rules
differ from the saved ones — assert the shown club still equals `match_results`). Repro script of the review gave 49/120 mismatches.

### L1 — audit log hygiene (R1, D4-2, D4-3)
`nhat_ky.py`: (a) `tra_cuu_hoc_sinh` keeps only `student_id` (add to `_CHI_GIU`; also treat the parameter name `ma` as
secret in `_AN` for any function); (b) `phan_quyen._ghi_nhat_ky`: for `tra_cuu_hoc_sinh` write `nguoi=None, vai=None`
even when an admin session exists; (c) `get_giai_trinh_hoc_sinh` is logged (extend `nen_ghi` with an explicit allow list;
rows carry `student_id` only; `run_id` optional); (d) a note in `docs/giai_trinh/HUONG_DAN_CHAY.md` §8: DBs used before
GT4 may hold codes in old log rows (append-only) → regenerate all codes (`tao_ma_tra_cuu(chi_hs_chua_co=False)`) before real use.
Done when: end-to-end test (api level, accounts ON, student mode ON) does wrong code ×2, right code ×1, then scans EVERY
`chi_tiet` of EVERY row and the exported CSV: none contains any issued code or any typed code; the 3 lookup rows have
`nguoi IS NULL`; a teacher viewing an explanation adds exactly 1 row with the teacher as `nguoi`.

### L2 — controls match the role (R3, D4-1)
(a) `vao_che_do_hoc_sinh` becomes `quan_tri`: MOVE the name from `_GIAO_VIEN` to `_QUAN_TRI` in `phan_quyen.py` (the `QUYEN` dict is built with `setdefault`, first list wins, so leaving it in `_GIAO_VIEN` changes nothing); update the I1/I2 test expectations and cite D4-1;
(b) in `index.html` add `data-quyen="quan_tri"` to every control that calls a `quan_tri` method (at least `btnGtTaoMa`,
`btnGtXuatMa`, `btnGtCheDoHs`, and the GT2 criteria/trial controls if a teacher can reach them); the CSS rule that hides
`[data-quyen="quan_tri"]` for `body[data-vai="giao_vien"]` already exists (`js/16_tai_khoan.js` `ganVai`, `style.css`).
(c) a **role sweep**: Chromium test logs in as a teacher, visits every visible tab, clicks every visible non-destructive
button/link once, then asserts the audit table has **zero** rows with `ket_qua = 'gt3_khong_du_quyen'` (refused calls are
already logged). Destructive/hidden controls are skipped by their `data-quyen`; list any control you skip and why in the commit.
Done when that sweep passes and fails on the pre-fix code.

### L3 — account setup and recovery (R2, R4, D4-4, D4-5)
(a) first-admin form and "add account" and "change password": add a retype-password field and a show/hide toggle; mismatch →
one plain Vietnamese error; (b) after the FIRST admin is created, replace the "change password" focus with a short next-steps
card: "Tạo tài khoản giáo viên", "Ghi nhớ mật khẩu", "Cách lấy lại quyền nếu quên" (one line pointing to the `.bat`/docs); focus
the "Thêm tài khoản" name field; (c) `main.py`: if `argv` contains `--xoa-tai-khoan` (optional path, default = the app's
`app.db`), call `recovery.xoa_tai_khoan_sau_sao_luu`, print the Vietnamese result, ask `Go XOA de xac nhan` on stdin unless
`--yes`, exit **before** importing/launching pywebview; add `QUEN_MAT_KHAU.bat` (Windows, next to the exe; also copied by
`build_windows.bat` and listed in `kiosk.spec` datas or the release folder) that calls the exe with the flag in a visible
console; (d) docs: `HUONG_DAN_CAI_DAT.md` + `docs/giai_trinh/HUONG_DAN_CHAY.md` §8 — recovery with the exe, and the "create the
first admin before students touch the kiosk" warning, also shown in the Tài khoản box when no account exists (i18n vi+en).
Done when: tests for the retype mismatch (UI), for `python main.py --xoa-tai-khoan <tmp db> --yes` (subprocess: backup file
exists, 0 accounts left, allocation rows untouched, exit code 0; wrong confirmation → nothing deleted), and the next-steps card.
Mark "Windows exe + .bat not testable on Linux" under Needs Truong.

### L4 — explanations that cannot be misread (R5, R6)
Presentation only. (a) For `RESERVED` rows (`giai_trinh._lua_chon_rbda`): do not show the numeric "Mức vào được" (column shows
"—" or "Chỗ dành riêng"), and add ONE fixed explanatory sentence under the table (and on the slip): "Một số chỗ của CLB được giữ
riêng cho nhóm theo quy định của trường; mức vào được chỉ áp dụng cho các chỗ còn lại." (wording via `fa_ly_do.py`, one source);
(b) neutral voice for the teacher/admin view: the lookup panel shows the sentences in third person ("Học sinh chưa có chỗ…"),
while the slip and the student screen keep "Em…". Implement as a `giong` argument ("hoc_sinh" default = byte-identical current
strings, "giao_vien" = neutral) on `fa_ly_do.cau_ly_do_rbda` and the callers; FA-mode sentences (`cau_ly_do`) unchanged;
(c) fix the subtitle contradiction on the Kết quả tab (`kq_desc` says no scores/lottery numbers; the lookup panel shows both) —
reword to say the table has none and the lookup panel (admin/teacher) shows a student's own details.
Done when: tests (default `giong` output byte-identical to today for every code; RESERVED rows never carry a numeric cut in
panel, slip or student view; teacher view has no "Em"); FA tests untouched and green.

### L5 — student screen and lookup placement (R9)
(a) student screen: visible `<label>`s "Mã học sinh" / "Mã tra cứu" (vocabulary-aware via `{person_l}`), school logo/name if
the workspace has one, lockout shows remaining seconds counting down (the backend error already says "một phút"), Enter submits,
focus returns to the first field after an error, language toggle reachable; (b) Kết quả tab: clicking a row of the results table
opens that student's explanation (scroll to panel), the lookup panel moves **above** the 120-row table or gets a "Tra cứu" jump
link at the top; (c) a one-glance 4-step helper inside the panel ("1 Tạo mã → 2 Xuất mã/in phiếu → 3 Chế độ học sinh tra cứu →
4 Thoát bằng tài khoản quản trị") shown only to admins; (d) after exporting slips/codes show the existing "Mở thư mục" plus
an "Mở tệp" button for the file just written (see how `Mở thư mục` is wired; `mo_thu_muc` is `giao_vien`-level).
Done when: Chromium tests for labels, countdown (inject the clock like `_gt1_dong_ho`), row-click, helper visible for admin only.

### L6 — readable audit log (R7)
Viewer only (CSV export stays raw). Map action names, role names and result codes to Vietnamese labels (+ English) through
one dictionary in `i18n.js` with a safe fallback to the raw name; the action filter becomes a `<select>` filled from the
distinct actions present; add "chỉ bị từ chối" checkbox and a date field (`YYYY-MM-DD`, server side filter in `nhat_ky._loc`);
time shown as local `dd/mm/yyyy hh:mm`; `chi_tiet` rendered as `key: value` text, not JSON; rows with `nguoi IS NULL` and
`hanh_dong = tra_cuu_hoc_sinh` show "Học sinh tự tra cứu". Move the log out of the account modal into its own section/tab of
that modal (account list and password change stay short).
Done when: tests for every label key present in vi+en, the filter by date/refused, null-actor label, raw CSV unchanged.

### L7 — criteria and comparison polish (R8)
(a) fix the layout of "Tiêu chí xếp"/"Thử cấu hình" (use the existing form-grid classes of the Quản lý tab or add small rules in
`style.css`; labels above fields, checkbox with its own row, ordered lists styled like the rest of the app); (b) in the compare
view render the two criteria descriptions as two short lists (tier 1 / tier 2 separated), never one run-on paragraph; (c) hide
the "Buổi" column when there is only one buổi and never print `__mac_dinh__` (friendly "Mặc định" if shown); (d) a yellow hint
(not a block) before "Chạy thử" when the selected options are degenerate: `priority = tier` with no groups declared ("không có
nhóm nào nên thực chất chỉ bốc thăm"), or `tier_mode = strict` with an empty list; (e) one-sentence summary on top of the compare
view built only from the numbers already computed ("49 học sinh đổi CLB; tỉ lệ được nguyện vọng 1: 53,3% → 60%") — no judgement words.
Done when: UI tests for each point + `tieu_chi` unit tests for the summary string; the exported HTML shows the same.

### L8 — stretch (only if all above are green; otherwise list under Needs Truong)
Vocabulary-aware explanation sentences: pass the workspace vocabulary (the same source `{person_l}`/`{slot_sl}` use in the UI)
into `fa_ly_do.cau_ly_do_rbda(..., tu_vung=None)`; default `None` = byte-identical current Vietnamese; add an English set
(`lang`) used when the UI language is EN. Done when: default byte-identical test, a non-student vocabulary example (e.g.
"nhân viên"/"dự án") produces sentences without "em"/"CLB", EN set covers every code.

## Gate (after L7 or L8)
`ruff check .` clean; `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7; all `tests/test_gt*` + `tests/test_giao_dien_gt*`
green (Chromium); push; check GitHub Actions for the branch head (`mcp__github__actions_list`, workflow `tests.yml`; lint + all
shards + coverage ≥ 85 %); red → fix (never skip a test) → push → check again. Done: `Status: DONE <sha> CI green <date>` in
`docs/phien/claude__gt-hoan-thien.md` + final summary in Vietnamese (lots done/skipped, tests, CI run link, Needs Truong with a
recommendation each, 3–5 steps Truong tries by hand incl. the Windows `.exe` recovery, a 3–5 line AI-log draft). No report conclusions.

## Backlog (not lots; the checker may add UX findings here, the writer does not build them unless asked)
See `GT4_RA_SOAT.md` §5.
