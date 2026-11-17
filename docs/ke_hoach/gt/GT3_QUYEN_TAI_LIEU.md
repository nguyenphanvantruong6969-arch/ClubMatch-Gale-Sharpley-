# GT3 — Roles, audit log, evidence docs, integration (parents E1-lite, E2; docs outside the registry)

> Task file for team GT3. Protocol: `docs/phien/GT_GIAO_THUC.md`. Branch `claude/gt3-quyen-tai-lieu`. English.
> Goal: two roles with passwords (OFF until the first admin exists), every write action logged append-only, and the
> evidence pack the jury asked for (role of AI, flow diagram, how to run, input data, member roles template, demo and
> video scripts, worked cases). The GT3 lead also runs the integration branch (protocol §9).

## Facts the lead should know (verified 2026-11-15)
- pywebview exposes EVERY public method of `api.PipelineAPI` (mixins: `api_nhap`, `api_cham_diem`, `api_bao_cao`,
  `api_quan_ly`, `api_xuat`, `api_sau_xep`, `api_forms*`, `api_workspace`, …) to JS; `browser_host.py` serves the same
  object. So one gate inside `PipelineAPI` covers both hosts.
- Existing append-only precedent: `wharton_nhat_ky` written in the same transaction (`api_quan_ly._ghi_nhat_ky_wharton`).
- Recovery tool: `recovery.py` / `recovery.html`. Docs builders: `tao_bao_cao_docx.py` (python-docx, dev dep).
- Integrity: docs are operational; never write report conclusions; label all numbers SIMULATED.

## Lot L1 — Accounts and login
- New module `tai_khoan.py`: hash with `hashlib.pbkdf2_hmac("sha256", pw, salt, 200_000)`, salt `secrets.token_bytes(16)`,
  compare with `hmac.compare_digest`. Table `tai_khoan(ten TEXT PRIMARY KEY, vai TEXT NOT NULL CHECK(vai IN
  ('quan_tri','giao_vien')), bam BLOB NOT NULL, muoi BLOB NOT NULL, tao_luc TEXT NOT NULL)` after `wharton_lock`.
- API: `get_phien_dang_nhap()`, `tao_tai_khoan(ten, mat_khau, vai)` (first account must be `quan_tri` and needs no
  login; later ones need a `quan_tri` session), `dang_nhap(ten, mat_khau)`, `dang_xuat()`, `doi_mat_khau(cu, moi)`,
  `xoa_tai_khoan(ten)` (never the last `quan_tri`). Min password length 8. 5 failed logins → 60 s lock. Idle 15 min →
  logout. Errors `gt3_*` in `i18n_errors.py`.
- Accounts table empty → behaviour exactly as today (no login screen).
- Recovery: `recovery.py` gets an option to clear `tai_khoan` after a backup (physical access = authority); document it.
- UI `js/16_tai_khoan.js`: login screen when accounts exist; role badge + logout in the header; admin-tab section to
  create/delete accounts and change password.
- **Done when** (`tests/test_gt3_tai_khoan.py`, `tests/test_giao_dien_gt3_dang_nhap.py`): hash never equals password,
  salts differ; wrong password fails; lock after 5; cannot delete last admin; no accounts → app starts without login
  (an existing UI test still passes unchanged); passwords absent from every API response and log; `kiem_nhanh.py` identical.

## Lot L2 — Permission gate
- One map `QUYEN` (new module `phan_quyen.py`): every public method of `PipelineAPI` → `cong_khai` | `giao_vien` |
  `quan_tri`. Read-only methods (`get_*`, `search_*`, view/export of results) → `giao_vien`; everything that writes
  (imports, run, config, adjustments, appeals decisions, STB unlock, delete/reset, accounts) → `quan_tri`; login
  methods → `cong_khai`. Enforce centrally in `PipelineAPI` (e.g. wrapping in `__getattribute__` for names in the
  map) only when accounts exist; denied → `{ok: False, data: None, errors: [{code: "gt3_khong_du_quyen", params:
  {hanh_dong}}]}`. UI hides buttons the role cannot use (the backend stays the real gate).
- **Done when** (`tests/test_gt3_phan_quyen.py`): a test enumerates `dir(PipelineAPI)` public callables and fails if any
  is missing from `QUYEN` (this forces integration I1); teacher calling a write → denied, nothing written; admin →
  works; accounts OFF → every method behaves as before (spot-check 5 write methods); browser host goes through the gate.

## Lot L3 — Audit log (E2)
- Table `nhat_ky_thao_tac(id INTEGER PRIMARY KEY AUTOINCREMENT, luc TEXT NOT NULL, nguoi TEXT, vai TEXT, hanh_dong TEXT
  NOT NULL, ket_qua TEXT NOT NULL, chi_tiet TEXT)`; SQLite triggers abort UPDATE and DELETE (append-only).
- When accounts are ON: one row per `quan_tri` method call (method name, ok/error code, short params summary with
  secrets removed), per login success/failure, per account change. Accounts OFF → nothing written (old behaviour).
- API `get_nhat_ky_thao_tac(page=1, page_size=50, nguoi=None, hanh_dong=None)`, `export_nhat_ky_thao_tac_csv(path="")`;
  viewer table in the admin tab with filters.
- **Done when** (`tests/test_gt3_nhat_ky.py`): run / config change / failed login each add exactly one row; UPDATE and
  DELETE raise; no password in any row; pagination right; CSV opens with Vietnamese intact.

## Lot L4 — Evidence docs (`docs/giai_trinh/`, Vietnamese, plain words, every page says "dữ liệu mô phỏng")
- `VAI_TRO_AI.md`: the software contains no AI/ML model; the allocation is a deterministic algorithm (DA with soft
  reserves + single lottery), same input + same seed → same output (cite the byte-identity checks); where AI tools
  helped DEVELOPMENT (from `docs/nhat_ky_ai/`), and what the students decided and verified themselves. Factual list,
  no evaluation.
- `SO_DO_LUONG.md` + `so_do_luong.svg` (hand-written SVG or a small stdlib script `ve_so_do.py`; no new library):
  Forms → Sổ nhập → import checks → backup → validate → lock lottery → match → verify → save (one transaction) →
  export → explanation / slips / appeals → re-run history.
- `HUONG_DAN_CHAY.md`: from a fresh clone: venv, tests, start kiosk (`main.py`, `browser_host.py`), load
  `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx`, run, look up a student, export. Each step verified by actually running it.
- `DU_LIEU_DAU_VAO.md`: inputs (clubs, capacity, reserves, sessions, preferences, tests/scores, medals, groups), every
  constraint and what the software does when data is missing or conflicting (block + message; quote the real error
  texts from `i18n_errors.py`), what happens when a club is full (waitlist, appeals), what is never used (rank,
  previous outcome, personal circumstances).
- `PHAN_CONG.md`: TEMPLATE only — table for 2 members (Mã nguồn / Nghiên cứu) with empty cells and a note that the
  students fill it. Never invent who did what.
- `KICH_BAN_DEMO.md` and `KICH_BAN_VIDEO.md`: numbered steps (click → expected screen) covering: import, run, explain
  one accepted and one rejected student, print a slip, change one criterion as a trial, compare, adopt, show audit log.
  Mark steps that need integration (I4) as "(sau tích hợp)".
- **Done when** (`tests/test_gt3_tai_lieu.py`): files exist; every doc contains "mô phỏng"; no internal codes (GT1,
  L2…) in student/teacher-facing text; every error code quoted exists in `i18n_errors.py`; every file path mentioned
  exists; `PHAN_CONG.md` has no filled names.

## Integration lots (branch `claude/gt-tich-hop`, after protocol §9 steps 1–2)
- **I1** permissions: classify every GT1/GT2 method in `QUYEN` (`tra_cuu_hoc_sinh` → `cong_khai`; lookup/slip/compare
  view → `giao_vien`; code generation, trial run, adopt → `quan_tri`). Done when `test_gt3_phan_quyen.py` passes.
- **I2** student mode: when accounts are ON, leaving the self-lookup overlay requires an admin login; while in it, only
  `cong_khai` methods work. Done when a Chromium test shows a student cannot reach any tab.
- **I3** audit: trial runs, adopt, code (re)generation, slip export each log one row. Done when tested.
- **I4** evidence pack: `du_lieu_test/tao_ca_mau_giai_trinh.py` (simulated 120-student set, fixed seed) writes
  `docs/giai_trinh/CA_MAU.md`: 3 students who got their 1st choice, 3 who did not (with the GT1 sentences and data),
  1 run blocked by missing data (real message), 1 conflicting criteria rejected at save (real message), and a GT2
  comparison table (default vs one alternative: changed students, per-group effects). Then
  `docs/giai_trinh/tao_goi_minh_chung.py` builds `GOI_MINH_CHUNG.docx` (python-docx) and `.pdf` (Chromium print)
  from the `docs/giai_trinh/*.md`. Fill the "(sau tích hợp)" steps in the scripts. Done when
  `tests/test_gt_tich_hop.py` regenerates CA_MAU.md byte-identically and every case in it matches the app output.
- Then protocol §6 CI gate on `claude/gt-tich-hop`, final summary, stop.

## Out of scope (→ "Needs Truong")
Multi-user server, network login, encryption at rest, two-person approval, filling the member-roles table,
any report commentary or conclusion.
