# Branch handoff: claude/gt2-tieu-chi

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/GT_GIAO_THUC.md`. Lot specs: `docs/ke_hoach/gt/GT2_TIEU_CHI.md`.

Status: DONE 8965d2b CI green 2026-11-17 (run https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/44018417803; later commits are doc-only)

## Feature / goal
GT2 (parents A1, Z7-lite): an authorised admin sees the allocation criteria as a plain ordered list, changes them only
within the approved bounded set (D-GT1: lexicographic, existing `rules` keys/values only, no weights, no sensitive
data), runs labelled TRIAL allocations (`run_history.loai_chay='thu'`, rows in `ket_qua_thu`) that never touch official
results, compares any two runs side by side (totals, per club, per priority group/class, changed students), and can
adopt a trial's criteria for the next official run. Schema (D-GT8): column `run_history.loai_chay` (in `di_tru_schema`)
+ table `ket_qua_thu` after the `fa_phan_hoi` block. Error codes `gt2_*`; JS `js/15_tieu_chi.js`; tests
`tests/test_gt2_*.py`, `tests/test_giao_dien_gt2_*.py`.

## Plan (written by Opus; ticked by the lead after checker NO BUGS)
- [x] L1 (48ad9d8, checker NO BUGS after fix2) Criteria in plain words + closed allow-list (`tieu_chi.py` `mo_ta_tieu_chi`, `cac_lua_chon_hop_le`; API `get_tieu_chi`; panel "Tiêu chí xếp")
- [x] L2 (e36fc60, checker NO BUGS after fix1) Trial runs, labelled, append-only (`loai_chay`, `ket_qua_thu`, API `run_thu`, all official readers ignore trials)
- [x] L3 (1cca309, checker NO BUGS) Compare two runs (`so_sanh_lan_chay`, HTML + CSV export, UI "Thử cấu hình")
- [x] L4 (a41f7bc, checker NO BUGS after fix1) Adopt a trial's criteria (confirm dialog, save via `update_workspace_config`, no result copy)
- [x] CI gate (§6) green on 8965d2b (1 fix round: old-DB fixture used DROP COLUMN, rejected by CI SQLite)

### Lead notes per lot
- All lots: every new table/option defaults OFF; no trial ever ⇒ behaviour byte-identical to today (invariant 1 via `kiem_nhanh.py --co-so origin/main --so-seed 20`).
- All lots: Windows CI console is cp1252 — any CLI print must reconfigure stdout to UTF-8; tests spawning CLIs decode with `encoding="utf-8"`.
- L1: user-facing text plain Vietnamese, no internal codes; the fixed "không dùng thứ hạng nguyện vọng…" note is mandatory.
- L2: re-grep `run_history` / `MAX(run_id)` / `ORDER BY run_id` in ALL .py files (not only those listed) before coding; prefer one helper `run_chinh_thuc_moi_nhat(cur)`. Trial must never redraw or relock STB.
- L2 (lead decision 2026-11-17): rules_thu keys must be ⊆ LUAT_XEP_MAC_DINH; FA refusal decided on merged effective rules.
- L2 FA: if the FA solver cannot take a rules override without touching `fa_*`, refuse with `gt2_thu_chua_ho_tro_fa` and add a Needs Truong line.

## Sessions
| Role | Model | Session id | State |
|---|---|---|---|
| lead | Opus | session_01YVAyu3PPHv9SNntepRSLwh | done |
| writer | Sonnet | session_01YVAyu1MNvsxmVCMTkDDtfN | archived (handoff after L1, e4991a3) |
| writer 2 | Sonnet | session_01YVAyu2JngdLXo2QUfsDamp | archived (handoff mid-L2, 3f5957c) |
| writer 3 | Sonnet | session_01YVAyu2U827tpBVb8oi1vsW | archived (handoff after L3, 9947e41) |
| writer 4 | Sonnet | session_01YVAyu29HSdnV77Lo8qJeao | archived after CI green |
| checker | Sonnet | session_01YVAyu2C5sE334n7iiw4hsP | archived (handoff after L2 review, b34457c) |
| checker 2 | Sonnet | session_01YVAyu11AFfpoJo5WWiwUja | archived (handoff after L4 review, 5dfcdcf) |
| checker 3 | Sonnet | session_01YVAyu1oGvGojvGmWkNvEa3 | archived after CI green |

## Needs Truong
- GT2-L2: chạy thử chế độ huy chương (FA) chưa hỗ trợ — `run_thu` từ chối bằng `gt2_thu_chua_ho_tro_fa` vì đường FA (`fa_daa.chay_fa_daa`) đọc/ghi hồ sơ `fa_*` trong cùng đường chạy. Đề xuất: để sau, ngoài phạm vi 1 tuần.
- GT2-L4 (thấp): lần chạy thử chỉ lưu tiêu chí dạng hiệu lực (`luat_xep`), không lưu nguyên văn tiêu chí đã chọn; khi "Dùng tiêu chí này", vài khóa không có tác dụng có thể bị lưu ở dạng chuẩn hoá (kết quả xếp vẫn y hệt). Muốn giữ nguyên văn cần thêm cột ngoài D-GT8. Đề xuất: giữ như hiện tại.

## Current state (overwrite each handoff)
- Done: L1-L4 passed checker; §6 CI green on 8965d2b (all jobs: lint, 4 Linux shards, 2 Windows shards, coverage). origin/main unchanged (already contained).
- In progress: nothing. GT3 lead integrates (protocol §9).
- For integration (GT3 I1): GT2 APIs (get_tieu_chi, run_thu, list_lan_chay, so_sanh_lan_chay, export_so_sanh_html, export_so_sanh_csv, ap_dung_tieu_chi) must be classified quan_tri; the compare student list is admin-only. I3: run_thu and ap_dung_tieu_chi are write actions to audit.
- Tests: tests/test_gt2_{tieu_chi,chay_thu,so_sanh,ap_dung}.py, tests/test_giao_dien_gt2_{tieu_chi,thu}.py.

## Final summary (§10, tiếng Việt)
- Lô đã xong: L1 tiêu chí bằng lời + danh sách cho phép đóng; L2 chạy thử gắn nhãn (`loai_chay='thu'`, bảng `ket_qua_thu`), không đụng kết quả chính thức; L3 so sánh hai lần chạy (tổng, theo CLB, theo nhóm ưu tiên/lớp, danh sách HS đổi CLB) + xuất HTML/CSV; L4 "Dùng tiêu chí này cho lần chạy chính thức". Không lô nào bị bỏ.
- Test mới: 6 tệp (4 backend, 2 Chromium). CI xanh: run 44018417803 trên 8965d2b.
- Needs Truong: xem mục trên (FA chạy thử — đề xuất để sau; L4 lưu dạng chuẩn hoá — đề xuất giữ nguyên).
- Truong thử tay: (1) tab quản trị → "Tiêu chí xếp": đọc danh sách, đổi "Chỉ theo nhóm ưu tiên" rồi về lại, thấy ô Wharton tự khoá/mở; (2) chạy chính thức một lần; (3) "Thử cấu hình" → đổi tiêu chí → "Chạy thử" → xem bảng so sánh, tab Kết quả không đổi; (4) xuất HTML so sánh, mở khi tắt mạng; (5) "Dùng tiêu chí này…" → xác nhận → chạy chính thức → so sánh lần chính thức mới với lần thử: 0 thay đổi.
- Ghi chú nhật ký AI (cho `docs/nhat_ky_ai/`): GT2 do 1 phiên Opus điều phối + 4 phiên Sonnet viết mã + 3 phiên Sonnet soát (bàn giao khi đầy ngữ cảnh), 2026-11-17. AI viết mã, test và tài liệu vận hành cho tiêu chí xếp, chạy thử, so sánh, áp dụng tiêu chí; checker AI tìm 5 lỗi (ô Wharton ×2, từ chối FA, khoá lạ, áp dụng tiêu chí làm mất nhóm), đều đã sửa. Mọi số liệu kiểm là dữ liệu MÔ PHỎNG. Phần nhận xét/kết luận báo cáo do học sinh tự viết.

## Decisions and gotchas (keep short)
- Decisions D-GT1..D-GT9 in protocol §0; do not ask again.
- Any push to the branch cancels the running CI (concurrency); no pushes during the CI gate except fixes.

## Next steps (ordered)
1. §5 loop L1 → L4, then §6.

## Files touched
- docs/phien/claude__gt2-tieu-chi.md: this file

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Opus (lead) | Branch + handoff file created | GT3 integration without GT2 starts 2026-11-18T16:25Z |
| 2026-11-17 | Opus (lead) | L1-L4 passed checker; CI green on 8965d2b; Status DONE | 4 writers, 3 checkers (context handoffs) |
