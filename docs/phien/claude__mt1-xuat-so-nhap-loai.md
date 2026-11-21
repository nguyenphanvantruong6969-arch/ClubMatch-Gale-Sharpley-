# Branch handoff: claude/mt1-xuat-so-nhap-loai

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol (lead/coder/checker, lots, prompts): `docs/phien/MT1_X1_GIAO_THUC.md`.

Status: IN PROGRESS (lead, 2026-11-21). Planned by Opus 2026-11-21. Base `origin/claude/mt1-bang-loai-clb` @ `05783a7` (MT1 not yet in main).

## Feature / goal
Item **MT1-X1** (code set by Truong, group MT1, 2026-11-21). `PipelineAPI.export_du_lieu_dau_vao` (api_xuat.py)
promises that the exported Sổ nhập rebuilds the data "y nguyên" in an empty DB. It does not for FA-DAA data: club
type, cut score, minimum, room size and reserved seats are lost. Fix the export so the round trip
(export → import into empty DB) keeps them, while the export in normal mode (FA off, no club has FA values) stays
cell-for-cell identical to today (invariants 1, 7). Measured failing test, currently `xfail(strict=True)`:
`tests/test_mt1_dong_bo_loai_clb.py::test_xuat_so_nhap_mang_loai_va_diem_san_hien_tai`.

## Verified on the real code (Opus, 2026-11-21, by Read/Grep)
| Data | DB location | Export today | Import path | Verdict |
|---|---|---|---|---|
| `loai`, `diem_san`, `so_toi_thieu`, `suc_chua_phong` | `clubs` columns (schema + `di_tru_schema` ALTER list) | `_du_lieu_so_nhap` SELECT lacks them → no keys → `ghi_so_nhap` `co_fa` false → no FA columns | `so_nhap._doc_cot_fa` (columns Loại / Điểm sàn / Tối thiểu / Sức chứa phòng) | **MISSING** |
| `giu_cho` (club_id, student_id) | table `giu_cho` | `export_du_lieu_dau_vao` never passes `giu_cho=` → no sheet "Giữ chỗ" | `doc_so_nhap` → `_doc_sheet_giu_cho`; `import_so_nhap` applies via `fa_daa.thay_giu_cho` ONLY if `dung_fa_daa` (else warning `fa_giu_cho_bo_qua`); sheet present = full replacement | **MISSING** |
| medals (huy chương) | `wharton_bids` | exported as `diem_w` when `dung_wharton` (FA requires wharton, `dung_fa_daa`) | column "Điểm quyết tâm"/"Huy chương" (both read) | OK |
| `gio`, `dia_diem` | `clubs` | SG-6 gated block in `_du_lieu_so_nhap` | `KHOA_GIO` | OK (pattern to copy) |
| `class_id` | `students` | `co_lop=` | A14 | OK |
- `ghi_so_nhap` decides FA columns by KEY PRESENCE (`co_fa = che_do_fa or any(k in c ... KHOA_FA)`), not by value;
  `loai` codes are mapped to display labels by `NHAN_LOAI_HIEN_THI`. So adding keys only under a gate is enough.
- No schema change, no CSV column change: FA columns and the "Giữ chỗ" sheet are already part of the Sổ nhập format.
  No conflict with invariants found → no stop needed (rule 7).

## Decisions (Opus; lead/coder do not re-ask)
- D1 FA keys gate: add the four `KHOA_FA` keys to every club dict in `_du_lieu_so_nhap` iff
  `dung_fa_daa(rules)` OR any club has a non-NULL value in one of the four columns. Otherwise no key at all
  (normal-mode sổ unchanged). Same style as the SG-6 `gio/dia_diem` block.
- D2 `giu_cho` gate: pass `giu_cho=[(club_id, student_id), …]` (ORDER BY club_id, student_id) to `ghi_so_nhap`
  iff `dung_fa_daa(rules)`; else `None` (no sheet). Reason: import ignores the sheet when FA is off, so writing it
  in FA-off mode adds nothing but a warning. FA on + empty table → empty sheet (= "no reserved seats", correct on
  re-import).
- D3 Do NOT pass `che_do_fa=True` to `ghi_so_nhap` from the export: it would rename the medal column and rewrite
  the Hướng dẫn sheet — out of scope. Note it in the CHANGELOG as a possible later item.
- D4 Keep `_du_lieu_so_nhap`'s return tuple shape (4 values) unchanged; read `giu_cho` in
  `export_du_lieu_dau_vao` inside the same `_ket_noi_doc()` block (or a small helper), not by widening the tuple
  that other callers may use (coder: `grep -n "_du_lieu_so_nhap" *.py` first).
- D5 "Byte-identical" for an .xlsx: openpyxl writes timestamps into docProps, so compare SHEET NAMES + ALL CELL
  VALUES of every sheet (not zip bytes) before vs after the change, on 3 normal datasets. Invariant 1 for
  `match_results` (3 datasets × 20 seeds) is covered by `kiem_nhanh.py` `trung_khit`; the solver is not touched.
- D6 The re-import overwrite warning (sổ with column Loại overwrites UI-set types; empty cell → NULL) is NOT built
  here. It goes under "Needs Truong" as a proposed separate lot/item.

## Plan (written by Opus; ticked by coder, lead ticks after checker NO BUGS)
### L1 — FA club columns in export (`api_xuat.py` `_du_lieu_so_nhap`)
- [x] Remove the `xfail` mark; run the test, confirm RED (rule 2); record the failure line in the commit message.
- [x] Add a new test (same file or `tests/test_mt1_x1_xuat_so_nhap.py`): normal workspace (FA off, no FA values),
      export `SO_NHAP_DQT_120HS_HOP_LE.xlsx` data → sheet "1. CLB" has NO column Loại/Điểm sàn/Tối thiểu/Sức chứa
      phòng, and every sheet's cell values equal a reference produced from the unchanged path (build reference by
      calling `so_nhap.ghi_so_nhap` with the old club dicts, or a stored expected list — no timestamps).
- [x] Add test: FA on, clubs with NULL type → FA columns present, cells empty; import into empty FA DB → NULLs.
- [x] Add test: FA OFF but one club has `loai` set → columns present, round trip keeps it.
- [x] Implement D1. Red test now green.
### L2 — reserved seats + full round trip
- [x] Failing test: FA DB from `SO_NHAP_FA_MAU_120HS.xlsx`; set `so_toi_thieu`, `suc_chua_phong` on two clubs
      (via `dat_loai_clb` if it takes them, else direct UPDATE in the test), add 2–3 `giu_cho` pairs with
      `fa_daa.thay_giu_cho` on valid (club, student) pairs; export; import into an EMPTY FA DB; assert equal
      `loai, diem_san, so_toi_thieu, suc_chua_phong` per club AND equal `giu_cho` set.
- [x] Test: FA on, empty `giu_cho` → sheet "Giữ chỗ" exists, header only; FA off → no sheet.
- [x] Implement D2 (+ D4). All new tests green.
### L3 — verify + docs
- [x] Related tests green: `tests/test_xuat_du_lieu.py`, `tests/test_fa_du_lieu.py`, `tests/test_a13_12_so_nhap.py`,
      `tests/test_mt1_dong_bo_loai_clb.py`, the new test file; `ruff check .`.
- [x] D5 cell-value comparison on 3 normal datasets (e.g. `SO_NHAP_DQT_120HS_HOP_LE.xlsx`,
      `SO_NHAP_MAU_120HS_3BUOI.xlsx`, one 800-student sổ) old vs new: identical. Record in branch file.
- [x] `kiem_nhanh.py` 7/7 (incl. `trung_khit`) after `git fetch origin main`; `soat-ma` four tiers — REPORT only.
- [x] Fix the `export_du_lieu_dau_vao` docstring (mention FA columns + Giữ chỗ gate).
- [x] `CHANGELOG.md` entry `MT1-X1` (files, new tests, D3 note); `docs/ke_hoach/TIEN_DO.md` row `MT1-X1`;
      `docs/ke_hoach/CLAUDE_CHI_TIET.md` code map only if a new helper function was added.

- D5 result (coder + checker independently, f809b3f vs 902dcbb): sheet names + all cells IDENTICAL on DQT_120HS_HOP_LE, MAU_120HS_3BUOI, DQT_800HS_HOP_LE (+ SO_NHAP_TEST by checker).

## Acceptance (lead checks before DONE)
- The former xfail test passes without xfail; new round-trip test covers all 5 data kinds.
- Normal-mode export: sheet names + cell values identical to before on 3 datasets; `test_xuat_du_lieu.py` green.
- No schema, CSV contract, i18n or UI change. No new library. CI green (lint, shards, coverage ≥ 85 %).

## Sessions
| Role | Model | Session id |
|---|---|---|
| lead | Opus | session_01YVAyu39d3wUuWKN81tKqwC |
| coder | Sonnet | session_01YVAytzncT6kRaDK668vPPe |
| checker | Sonnet | session_01YVAyu1PMW4F6Ch9P1bfJHS |

## Needs Truong
- N1 (proposal, not built): before importing a sổ that HAS column Loại, warn that it overwrites types set in the UI
  and that empty cells clear them to NULL (behaviour already pinned by tests in `test_mt1_dong_bo_loai_clb.py`).
  Recommendation: separate lot/item (UI + i18n), after MT1-X1.

## Final summary (lead, §5 — dữ liệu MÔ PHỎNG)
- Đã làm L1–L3, checker NO BUGS cả 3 lô; không bỏ phần nào. CI: (chờ đọc).
- FA (`SO_NHAP_FA_MAU_120HS.xlsx`): đặt THU_2_2 = Giới hạn, điểm sàn 5 qua `dat_loai_clb`; 2 chỗ giữ. Sổ xuất có cột
  Loại/Điểm sàn/Tối thiểu/Sức chứa phòng, nhãn đọc được (Tự do / Giới hạn), sheet "Giữ chỗ" đúng 2 dòng.
- Nhập vào DB trống, chạy seed 3 cả hai DB: 240 dòng `match_results` trùng khít.
- Thường (`SO_NHAP_DQT_120HS_HOP_LE.xlsx`): không cột mới, không sheet mới; 360 dòng trùng khít.
- Lưu ý: đặt CLB Tự do duy nhất của buổi sang Giới hạn → chạy báo `fa_thieu_clb_tu_do` (kiểm hợp lệ có sẵn, đúng).
- Truong thử tay: (1) mở workspace FA, đặt loại 1 CLB + thêm giữ chỗ; (2) Xuất dữ liệu đầu vào, mở xlsx xem
  sheet "1. CLB" và "Giữ chỗ"; (3) nhập sổ đó vào workspace trống, chạy cùng seed, so kết quả.

## Current state (overwrite each handoff)
- Done so far: branch created, plan + protocol written (Opus). No product code yet.
- In progress: §4 CI gate (L1–L3 passed checker NO BUGS; L3 head 902dcbb)
- Tests: none run (planning only; container had no `.venv`).
- Open problems: —

## Files touched
- docs/phien/claude__mt1-xuat-so-nhap-loai.md: this file.
- docs/phien/MT1_X1_GIAO_THUC.md: lead/coder/checker protocol.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-21 | Opus (plan) | Verified export/import paths; wrote Plan L1–L3 + protocol | giu_cho also missing, medals OK |
