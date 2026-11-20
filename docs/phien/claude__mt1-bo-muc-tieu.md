# Branch handoff: claude/mt1-bo-muc-tieu

> Read CLAUDE.md, then this file, then `docs/phien/MT1_GIAO_THUC.md`. English. Cap 150 lines.
> Background (Vietnamese chat with Truong, 2026-11-20): `docs/fable/08_MT0_MEMO.md` (simulated evidence).

## Feature / goal
New item **MT** (outside the 33-item registry; Truong approved 2026-11-20; parents C3/A1). Lot **MT1 = default
goal presets** ("Bộ mục tiêu mặc định"). The school picks an *educational goal*; the software sets the allocation
rules that fit it, explains them in plain words, lets the admin try it on current data, and after a run reports
whether the goal was met and at what cost. Goal first, rules second. The core algorithm does not change:
every preset is a combination of rules and club data that already exist. Out of scope here (later lots):
MT2 pre-commitment/publication, MT3 "why not met" diagnosis, MT5 parent report.

## Status
Status: PLANNED 2026-11-20 (Opus). Base: `origin/claude/trusting-bohr-wg0l4n` (contains MT0 + this plan).

## The six presets (content decided by Opus; Truong may rename, not re-design)
| id | Name (vi) | Educational goal (one line) | Rules patch (`rules`) | Club data |
|---|---|---|---|---|
| `can_bang` | Cân bằng (mặc định) | Talent clubs pick by test, other clubs give everyone a fair chance | none = `MAC_DINH_TRUONG_HOC["rules"]` exactly | unchanged |
| `nang_khieu` | Bồi dưỡng năng khiếu | Strongest candidates get the selective clubs | `priority=score, score_scope=per_slot, wharton=False, fa_daa=False` | unchanged; warn if reserved seats exist |
| `trai_nghiem` | Trải nghiệm cho mọi học sinh | Every student has the same chance; tests do not decide | `priority=tier, tiers=[], wharton=False, fa_daa=False` | unchanged; warn that test scores and reserves are ignored |
| `hoa_nhap` | Hoà nhập | A support group is present in popular clubs at least in proportion | `priority=score, tier_mode=reserve` (rest default) | reserve suggestion (L3), group chosen by admin |
| `khoi_dau_cap` | Ưu tiên khối đầu cấp | New grade (10 or 6) gets to try clubs it wants | same as `hoa_nhap` | reserve suggestion (L3), group = grade label |
| `dam_me` | Nuôi đam mê, gắn bó | Students who commit most to a club get it | `wharton=True, fa_daa=True` (rest default) | FA prerequisites; "advanced" badge; trial disabled (`gt2_thu_chua_ho_tro_fa`) |

Rules: one preset at a time. `hoa_nhap` and `khoi_dau_cap` both need the single `reserve_group` per club, so
they cannot be combined (overlapping reserves = later, invariant 8). Any manual edit after applying →
`muc_tieu.id = "tuy_chinh"` with the preset it came from.

## Plan (written by Opus; ticked by the lead after checker NO BUGS)
- [ ] **L1 Catalogue (pure, no UI, no DB)** — new `muc_tieu.py`: `BO_MUC_TIEU` (6 entries: id, vi/en name, goal
  sentence, rules patch, club-data action, metrics list, warnings, `nang_cao` flag), `rules_cua_muc_tieu(id, rules)`,
  `nhan_dien_muc_tieu(rules)` (current rules → preset id or `tuy_chinh`), `mo_ta_muc_tieu(id, lang)` (reuses
  `tieu_chi.mo_ta_tieu_chi`). Tests `tests/test_mt1_bo_muc_tieu.py`: every patch passes `cau_hinh_ws._chuan_hoa`;
  patches use only keys of `LUAT_XEP_MAC_DINH`; default config ⇒ `can_bang`; `can_bang` patch == default rules;
  `trai_nghiem` on simulated data gives the same assignment as pure lottery order (verify the claim
  "priority=tier + tiers=[] ⇒ STB only, reserves skipped"; if false → STOP, "Needs Truong"); no preset reads
  preference rank or previous results (invariant 2, static check on the patch keys).
- [ ] **L2 API** — `api_muc_tieu.py` mixin on `PipelineAPI`: `get_muc_tieu()` (catalogue + current id),
  `xem_truoc_muc_tieu(id)` (plain-word before/after of rules, warnings; read-only), `ap_dung_muc_tieu(id, nhom=None)`
  (writes via `update_workspace_config`; stores top-level config key `muc_tieu = {id, nhom, tu}`; NOT inside
  `rules`, so `run_history.luat_xep` and fingerprints are unchanged). Admin only (`phan_quyen.QUYEN` +
  `nkhd_` audit labels). Error codes `mt_*` appended to `i18n_errors.py`, then `python tao_i18n_js.py`.
  `{ok, data, errors}` contract. Tests: `tests/test_mt1_api.py` (roles, unknown id, FA prerequisites missing,
  idempotent re-apply, manual edit ⇒ `tuy_chinh`, config without `muc_tieu` behaves exactly as today).
- [ ] **L3 Reserve suggestion (hoa_nhap, khoi_dau_cap)** — `de_xuat_du_tru(nhom, he_so=1.0)`: per club
  `ceil(share_of_group_in_school × capacity × he_so)` capped at capacity; share read from the student list only
  (never preferences, never past results). Shows: token-reserve warning when the number is below the level that
  can matter (MT0 F4: 1–2 seats), "no gap found" note when the last official run already meets the goal (MT0 F5),
  and the clubs whose current reserve group differs (overwrite needs explicit confirm). Writing goes through the
  existing club update path, one transaction, backup first. Tests `tests/test_mt1_du_tru.py` (hand-checked 10-student
  case, cap, rounding, group absent ⇒ `mt_nhom_rong`, no write without confirm).
- [ ] **L4 Goal report card (read-only)** — `bao_cao_muc_tieu(run_id)`: per preset its metrics + guardrails always
  shown (first-choice %, top-3 %, unmatched, blocking pairs). For reserve presets also "helped vs gave way":
  compare with an in-memory solve without reserves using the SAME locked lottery (writes nothing). Small-number
  suppression: any group count 1–4 shown as "< 5". Tests `tests/test_mt1_bao_cao.py` (hand-checked case,
  suppression, no writes to any table, works for trial runs from `run_thu`).
- [ ] **L5 UI** — Settings: "Mục tiêu năm nay" with 6 cards (name, one-sentence goal, when to use, cost/warning),
  "Xem trước" (L2), "Thử trên dữ liệu hiện tại" (existing `run_thu` + `so_sanh_lan_chay`; disabled with reason
  for `dam_me`), "Dùng mục tiêu này" (L2), L3 step for reserve presets; Results tab shows the L4 card. Keys
  `mt1_*` (vi + en). Plain words only, no internal codes on screen. Tests `tests/test_giao_dien_mt1.py`
  (Chromium, 1280 + 1024 px, role teacher sees no apply button, contrast/size like GT4-L7). Screenshots
  `docs/phien/anh_mt1/`.
- [ ] **L6 Docs + final review** — `HUONG_DAN_SU_DUNG.md` section "Chọn mục tiêu", `CLAUDE_CHI_TIET.md` code map,
  `CHANGELOG.md`, `TIEN_DO.md`; final review per protocol §5.

## Acceptance (whole lot)
- Invariant 1: with no `muc_tieu` key and with `can_bang` applied, `kiem_nhanh.py` 7/7 incl. `trung_khit`
  (3 datasets × 20 seeds, `--so-seed 20`). Each other preset = existing rule combination, already covered by tests.
- Invariants 2, 4, 5, 6, 7, 8 untouched (no new choice function, no CSV change, `run_history` append-only).
- Every screen sentence passes `chu_cam`; no "Wharton", no internal ids visible.

## Decisions and gotchas
- Presets live in code (`muc_tieu.py`), not in the DB: same for every school, versioned with the app.
- `muc_tieu` is a top-level config key (like `name`), not a rule, so it never enters allocation or fingerprints.
- The formula in L3 is the MT0 finding F1/F2 (formula beats a fixed number 20/20 vs 13–14/20, simulated).
- `trai_nghiem` claim must be proven by test in L1 before anything else uses it.
- All numbers in tests/docs are SIMULATED. No report commentary for the student's science report.

## Current state
- Done: plan + protocol written. Nothing coded.
- Next: lead runs protocol §3 from L1.

## Needs Truong
- (empty)

## Sessions
| Role | Session id | Started |
|---|---|---|

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-20 | Opus | MT0 research, presets designed, plan + protocol | on `claude/trusting-bohr-wg0l4n` |
