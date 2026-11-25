# DK2 protocol — size M (coder Sonnet + checker Sonnet, no lead)

> Lean template: `docs/phien/_GIAO_THUC_GON.md` (§3 budget rules apply; do not copy it). Decisions D1–D44 and
> Plan: `docs/phien/claude__dk2-cau-noi-so-nhap.md`. Reference design: `docs/phien/DK1_BAN_MAU_V7.html`.

## 0. Rules (do not ask Truong)
- DK2 = **bridge**, not integration (Truong 2026-11-25): prototype JSON → real `SO_NHAP_CLB.xlsx` written ONLY
  through `so_nhap.ghi_so_nhap` → kiosk importer accepts it with 0 errors in FA/medal mode.
- **No CSV contract change, no schema change, no change to `fa_daa.py`, `rbda_priority_pipeline.py`,
  `so_nhap.py`, `api_*.py`** (invariants 1, 5, 7 stay untouched by construction). Mapping uses existing columns:
  Phòng → `dia_diem`, sức chứa → `suc_chua_phong`, Lớp → `class_id` (`co_lop=True`; khối derived, D7),
  Forms link and teacher stay out of the sổ. If the mapping cannot be done without touching those files →
  stop that lot, "Needs Truong" line in the branch file.
- New files only: `dk2_so_nhap.py` (root; pure functions + `main()` CLI), `tests/test_dk2_so_nhap.py`,
  `tests/du_lieu/dk2_ban_mau_*.json` (fixtures), prototype `docs/phien/DK1_BAN_MAU_V8.html` (copy of v7, edited),
  `tests/test_dk2_ban_mau.py` (one Playwright file, file URL, one shared page fixture). No new library.
- All data is MOCK; label it so in docs and fixtures (`duLieu: "MÔ PHỎNG"`).

## 1. Branch, lots, milestones
| Branch | Lots | Must ship |
|---|---|---|
| `claude/dk2-cau-noi-so-nhap` (from `claude/gracious-johnson-pnqvrg`) | L1 converter + importer test → **MILESTONE 1** · L2 prototype v8 (export format + D39–D41, D44) · L3 CLI + docs + registry → **MILESTONE 2** | L1, L3 must; L2 must except D39 (cuttable if > 1 session) |
- Before each lot: `git fetch origin main && git merge --no-edit FETCH_HEAD`. Never rebase or force-push. No PR.
- Coder runs the CI gate itself (size M). Max 2 FIX rounds per milestone, then "Needs Truong" + revert the lot.

## 2. Acceptance (`kiem_nhan`)
- L1: (a) fixture small (30 HS / 10 CLB) and large (798 / 40) convert; (b) `api_nhap` preview of the .xlsx in a
  workspace with FA on → `errors == []`, counts equal JSON; (c) NV order per student = session order then rank,
  one run NV1…NVk (never restarts per session); (d) medal cells exactly 60/30/10, ≤ 1 per club, never on Tự do;
  (e) Tuyển chọn: `loai`, `diem_san` written; untested → no score; score "8,5" → 8.5; (f) Tự do quota blank in
  JSON → capacity rule chosen in L1 (see Plan) with a test; (g) run one FA allocation on the imported data →
  ok, every admitted Tuyển chọn student has score ≥ điểm sàn; (h) invalid JSON (missing key, unknown club id,
  2 medals same club) → clear Vietnamese message, no file written; (i) `dk2_so_nhap.py` coverage ≥ 90 %.
- L2: export JSON has `dinhDang: 1` and the L1 shape; D39 per-day flow (rank → medals → tests per session, final
  review all days); D40 chip short + wrap, no overlap at 1366 and 390 px; D41 no receipt code, "Đã gửi lúc …";
  D44 ≤ 5 tests per session + warning; Hick ≤ 7 per frame, ≤ 1 gold, no disabled gold (count as in D37).
- L3: `python dk2_so_nhap.py vao.json ra.xlsx` works; short how-to in `docs/huong_dan/DK2_CAU_NOI.md`;
  CHANGELOG, TIEN_DO, registry row DK2 (and DK1 if missing).

## 3. Coder loop per lot
Failing test → minimal code → `python -m pytest -q <lot test file> --tb=line 2>&1 | tail -15` (+ ≤ 3 related:
`tests/test_so_nhap.py -k fa`, `tests/test_sm2_canh_bao_fa.py`) → `ruff check .` → `kiem_nhanh.py | tail -10` →
`soat-ma` tiers (report only) → CHANGELOG + TIEN_DO row `DK2-L<n>` → commit `DK2-L<n>: …` → push
`-u origin claude/dk2-cau-noi-so-nhap`. Tick the Plan. At a milestone write `MILESTONE <k> READY | head <sha>`
in the branch file and stop for the checker.

## 4. Checker prompt (Truong pastes at each milestone)
```
Checker DK2, branch claude/dk2-cau-noi-so-nhap. Read CLAUDE.md, docs/phien/DK2_GIAO_THUC.md, the branch file.
Verify milestone <k> against §2 only: run the lot test files, open one generated .xlsx with openpyxl and check
headers + 3 random students by hand against the JSON; confirm git diff touches no forbidden file (§0).
Write PASS or FIX <list> (≤ 10 lines) in docs/phien/claude__dk2-cau-noi-so-nhap__checker.md, commit, push.
```
