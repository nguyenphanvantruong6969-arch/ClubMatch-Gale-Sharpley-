# Branch handoff: claude/gt1-giai-trinh

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/GT_GIAO_THUC.md`. Lot specs: `docs/ke_hoach/gt/GT1_GIAI_TRINH.md`.

Status: DONE 499edf1 CI green 2026-11-16 (run https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/43809965443)

## Feature / goal
GT1 (parent item C3): per-student explanation for ANY run (default RB-DA and FA-DAA). The school can show each
student, in plain words, their preferences, the scores/criteria that mattered, each club's capacity and cut-off,
constraints, and why they got (or did not get) each club — on screen (admin/teacher), on a printed slip, and by
self-lookup with a code. Reports/controls only: no run code path changes (invariants 1, 2, 3 untouched).

## Plan (written by Opus lead; ticked by lead after CHECKER NO BUGS)
- [x] L1 Explanation engine (2ccfd01, checker NO BUGS 76864f5): `giai_trinh.py` (`giai_trinh_mot_hoc_sinh`), `fa_ly_do.cau_ly_do_rbda`, stale guard
      via `dau_van_tay_chay`, API `get_giai_trinh_hoc_sinh`, errors `gt1_khong_co_hoc_sinh`, `gt1_chua_chay`.
      Tests `tests/test_gt1_giai_trinh.py` (a)–(e).
- [x] L2 Lookup screen (admin/teacher) (2d2c947, checker NO BUGS): panel "Tra cứu một học sinh" in results tab, `js/14_giai_trinh.js`,
      `<!-- GT1 -->` block in `index.html`. Tests `tests/test_giao_dien_gt1_tra_cuu.py` (Chromium).
- [x] L3 Printable slip (35a16d2, checker NO BUGS): `export_phieu_giai_trinh`, buttons in L2 panel. Tests `tests/test_gt1_phieu.py`.
- [x] L4 Lookup codes (5facef0, checker NO BUGS 22df9c2) + student self-lookup mode: table `ma_tra_cuu`, `tao_ma_tra_cuu`, `tao_lai_ma_tra_cuu`,
      `export_ma_tra_cuu_csv`, `tra_cuu_hoc_sinh`, lockout, overlay UI. Tests `tests/test_gt1_ma_tra_cuu.py`,
      `tests/test_giao_dien_gt1_hoc_sinh.py`.
- [x] CI gate (§6): lint + all shards + coverage ≥ 85 % green on 499edf1 (CI fix1 a3a9cf9: UI wording, role=dialog only while open, gt1_* in ws_nhan allowlist).

### Lead notes per lot (added to the spec; writer must follow)
- All lots: error codes only `gt1_*`; i18n block appended at end of dict marked `# GT1`; run `python tao_i18n_js.py`.
  Fake data only. Student-facing JSON/HTML contains only that student. No internal codes in teacher-visible text.
- L1: FA off path must reconstruct inputs read-only (no writes to any table); prove with `kiem_nhanh.py --co-so
  origin/main --so-seed 20`. Outcome codes are constants in `giai_trinh.py`; sentences only in `fa_ly_do.py`.

## Sessions
| Role | Session id | Model | State |
|---|---|---|---|
| lead | session_01TGThn8ujS9oohKhbgDiJgD | claude-opus-5-5 | done |
| writer | session_01TGThn4UaExaTx1hj5kH5FF | claude-sonnet-5-5 | archived (handoff 54e8c0d, ~217k) |
| writer 2 | session_01TGThn4KfT4gVBLHBdZiZXv | claude-sonnet-5-5 | archived (handoff 0eedd17, ~229k) |
| writer 3 | session_01TGThn8kaGCdSNUJwzjvqVX | claude-sonnet-5-5 | archived (handoff 499edf1, ~206k) |
| writer 4 | session_01TGThn4vSjqxxSgmqbs9E7H | claude-sonnet-5-5 | archived (unused) |
| checker | session_01TGThn8ZPKEmNQz6wmpDseA | claude-sonnet-5-5 | archived (handoff dadb8c4, ~223k) |
| checker 2 | session_01TGThn4g1pdbQL7MsAEKG9r | claude-sonnet-5-5 | archived |

## Current state (overwrite each handoff)
- Done: L1-L4 + CI gate. Head 499edf1 green (lint, Linux 1-4/4, Windows 1-2/2, coverage >= 85 %). origin/main included.
- New tests: test_gt1_giai_trinh, test_gt1_phieu, test_gt1_ma_tra_cuu, test_giao_dien_gt1_tra_cuu, test_giao_dien_gt1_hoc_sinh (+ GT1 block in test_ws_nhan allowlist).
- Open problems: none. Truong merges to main / integration (§9, GT3 lead) picks this branch up.

## Needs Truong (decisions, nothing blocked)
- Outcome sentences are Vietnamese only (EN mode switches labels only). Recommend: keep for the deadline; add EN sentences later if the jury demo is in English.
- Only the latest run's results are stored, so an older run cannot be explained (error gt1_lan_chay_cu). Recommend: keep; storing per-run results would be a schema change beyond D-GT8.
- Slip prints "trong N ngày" only when complaints (fa_khieu_nai) are ON. Recommend: keep.
- Each lookup replays the run (read-only); fine at ~800 students, measure on the real kiosk PC.

## Decisions and gotchas (keep short)
- L3: appeal "trong N ngày" printed only when fa_khieu_nai is ON (lead accepted).
- L1/L2: outcome sentences (fa_ly_do) are Vietnamese only; EN mode switches labels only (spec allows). L2 panel always uses latest run.
- Decisions D-GT1…D-GT9 in the protocol §0 are final; do not ask again.

## Next steps (ordered)
1. GT3 lead integrates this branch (§9). 2. Truong: try the manual steps in the final summary below.

## Files touched
- New: giai_trinh.py, phieu_giai_trinh.py, ma_tra_cuu.py, js/14_giai_trinh.js, 5 test files above.
- Changed (GT1 blocks): fa_ly_do.py, api_xuat.py, api_quan_ly.py, rbda_priority_pipeline.py (table ma_tra_cuu), index.html,
  i18n.js, style.css, js/_danh_sach.txt, i18n_errors.py + i18n_loi.js, tests/test_ws_nhan.py, CHANGELOG, TIEN_DO, CLAUDE_CHI_TIET.

## Final summary (§10, tiếng Việt)
- Lô xong: L1 bộ máy giải trình, L2 màn hình tra cứu (quản trị/giáo viên), L3 phiếu in, L4 mã tra cứu + chế độ học sinh tự tra cứu. Không lô nào bỏ.
- Vòng sửa: L1 (3 lỗi nhỏ), L2 (1 lỗi lộ tên khi tìm chậm), L4 (1 lỗi lộ thẻ khi tra chậm), CI 1 vòng (văn phong, role=dialog, danh sách mã).
- CI: xanh trên 499edf1 — https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/43809965443
- Bất biến 1: kiem_nhanh.py 60 trường hợp (3 bộ × 20 seed) giống hệt sau mỗi lô.
- Truong thử tay: (1) chạy xếp, mở tab Kết quả → "Tra cứu một học sinh", gõ tên không dấu, xem thẻ; (2) bấm "In phiếu cả lớp", mở HTML, in thử;
  (3) tạo mã tra cứu, xuất CSV; (4) mở "Chế độ học sinh tra cứu", nhập đúng/sai mã 6 lần, xem khoá 60 s; (5) sửa một điểm rồi tra lại, xem cảnh báo "dữ liệu đã đổi".
- Ghi chú nhật ký AI (docs/nhat_ky_ai/): "2026-11-16 GT1: Claude (Opus điều phối, Sonnet viết và soát) làm bộ giải trình từng học sinh, phiếu in,
  mã tra cứu. Truong duyệt đặc tả GT1 và các quyết định D-GT1…D-GT9. Số liệu kiểm chứng là dữ liệu MÔ PHỎNG. Phần nhận xét và kết luận
  trong báo cáo do học sinh tự viết."

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Opus lead | Branch + handoff file created | base 5926107 |
| 2026-11-16 | Opus lead | WRITER DONE L1 6fda292; REVIEW L1 sent; writer handoff -> writer 2 | |
| 2026-11-16 | Opus lead | L1 fix1 2ccfd01 NO BUGS; ticked; GO L2 | |
| 2026-11-16 | Opus lead | L2 fix1 2d2c947 NO BUGS; ticked; GO L3 | |
| 2026-11-16 | Opus lead | WRITER DONE L3 35a16d2; REVIEW L3; writer 2 handoff -> writer 3 | |
| 2026-11-16 | Opus lead | L3 NO BUGS; ticked; GO L4 to writer 3 | |
| 2026-11-16 | Opus lead | L4 1 bug -> FIX L4 r1; checker handoff -> checker 2 | |
| 2026-11-16 | Opus lead | L4 fix1 NO BUGS; ticked; start CI gate | |
| 2026-11-16 | Opus lead | CI fix1 a3a9cf9; CI green 499edf1; Status DONE; children archived | |
