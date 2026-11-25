# Branch handoff: claude/dk2-cau-noi-so-nhap

> Read CLAUDE.md, then THIS file, then `docs/phien/DK2_GIAO_THUC.md`. English. Cap 150 lines.
> Previous item: DK1 (`docs/phien/claude__gracious-johnson-pnqvrg.md`, decisions D1–D42 stay valid).

## Goal
Item **DK2** (Truong 2026-11-25): make the DK1 prototype's output a REAL Sổ nhập. Prototype JSON →
`dk2_so_nhap.py` → `SO_NHAP_CLB.xlsx` via `so_nhap.ghi_so_nhap` → kiosk imports with 0 errors (FA mode).
Full integration (SQLite tables, LAN student registration) is NOT DK2; later item after a school pilot.

## Decisions (Truong, 2026-11-25; do not re-ask)
- D43 Scope = bridge, size M, no CSV-contract / schema / algorithm change (Truong chose option "Cầu nối").
  Mapping (planner verified in `so_nhap.py`): Phòng → `dia_diem` ("Địa điểm", `KHOA_GIO`), room capacity →
  `suc_chua_phong`, type → `loai` (`chuan_hoa_loai` labels), floor → `diem_san`, Lớp → `class_id` with
  `co_lop=True`; khối not written (derived from Lớp, D7); Forms link, teacher, description: not in the sổ.
- D44 Keep the test cap at 5 **per session** (= `so_nhap.TRAN_THI_MOI_BUOI`); once 5 are ticked in a session,
  show a warning that unticked Tuyển chọn clubs there cannot admit the student. Replaces D23 "≤ 5 total".
- D45 D39–D41 are built in DK2 L2 on a v8 copy of the prototype; D41 (drop receipt code) is approved.

## Plan
### L1 converter + importer test (must) → MILESTONE 1
- [ ] Freeze the JSON shape (`dinhDang: 1`): `buoi[]`, `clb[]` {ma, ten, buoi, loai, chiTieu|null, diemSan|null,
      phong, sucChuaPhong}, `hocSinh[]` {ma, hoTen, lop, nv[] in session-then-rank order: {clb, thi, diem|null,
      huyChuong: "Vàng"|"Bạc"|"Đồng"|null}}. Write fixtures small + large (generate from v7 "Demo nhỏ" /
      "Cả trường" with Playwright once, or by a seeded script; mark MÔ PHỎNG).
- [ ] `tu_ban_mau(du_lieu) -> (clubs, students)`; `ghi_tu_ban_mau(du_lieu, duong_dan)`; call `ghi_so_nhap(...,
      co_lop=True, che_do_fa=True, co_nhom=False)`. Find the nv medal key by reading `ghi_so_nhap` (`co_w`
      branch) and `_doc_sheet_hs`; medal names → 60/30/10. Session label → `so_nhap.ma_buoi`.
- [ ] Tự do capacity: read how `fa_daa` treats `TU_DO` capacity (`grep -n "TU_DO\|capacity" fa_daa.py`). Default
      choice: capacity = room capacity; if total Tự do capacity in a session < students of that session, the
      converter returns a warning (not an error). Record the finding here.
- [ ] Club id: keep prototype `ma` if `so_nhap` accepts it, else `tao_ma_clb(ten)`; test both fixtures.
- [ ] Validation before writing (h in protocol §2): messages in Vietnamese, plain strings (not UI codes; the
      CLI is not the UI contract). No file written on error.
- [ ] Tests `tests/test_dk2_so_nhap.py` for §2 L1 (a)–(i); import through `api_nhap` the same way
      `tests/test_sm2_canh_bao_fa.py` builds its `api` fixture with FA on.
### L2 prototype v8 (must, D39 cuttable)
- [ ] Copy v7 → `docs/phien/DK1_BAN_MAU_V8.html`; `buildExport` emits the L1 shape (one NV run).
- [ ] D40 chip, D41 "Đã gửi lúc hh:mm, thứ …", D44 per-session cap + warning, then D39 per-day flow.
- [ ] `tests/test_dk2_ban_mau.py`: export JSON passes `tu_ban_mau` with 0 errors; D40 no overlap (bounding
      boxes) at 1366/390 px; D44 6th tick blocked; Hick counter ≤ 7 and 1 gold on student screens.
### L3 CLI + docs (must) → MILESTONE 2
- [ ] `main()` argparse `vao.json ra.xlsx`, exit 1 with messages on error; test via `main([...])`.
- [ ] `docs/huong_dan/DK2_CAU_NOI.md` (≤ 40 lines, plain Vietnamese, says data is mock); CHANGELOG; TIEN_DO;
      registry rows DK1 + DK2 in `SO_DANG_KY_33_MUC.md` and `ke_hoach_thay_doi.json` (follow existing format).
- [ ] Tell Truong (branch file "Current state"): to see v8 as an artifact, ask an Opus session to republish
      `https://claude.ai/artifact/BuEtHrR61XXuju8kGXvmAX` from the v8 file.

## Current state (overwrite each handoff)
- Planned only (Opus, 2026-11-25). Branch not created yet: the coder creates it from
  `origin/claude/gracious-johnson-pnqvrg` and pushes it.

## Files touched
- docs/phien/DK2_GIAO_THUC.md, docs/phien/claude__dk2-cau-noi-so-nhap.md (planning)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-25 | Opus | Planned DK2 (3 questions answered: bridge/M, D39–D41 in L2, cap 5 per session) | no code |
