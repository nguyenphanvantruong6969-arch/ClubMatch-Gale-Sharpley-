# Branch handoff: claude/gt3-quyen-tai-lieu

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/GT_GIAO_THUC.md`. Lot specs: `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md`.

Status: DONE c66889d CI green 2026-11-16 (run https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/43895943354)

## Feature / goal
GT3 (parents E1-lite, E2; docs outside the registry): two roles (`quan_tri`, `giao_vien`) with passwords, OFF until the
first admin account exists; a central permission gate in `PipelineAPI`; an append-only audit log of every write action;
and the evidence pack the jury asked for (role of AI, flow diagram, how to run, input data, member-roles template, demo
and video scripts). Then the GT3 lead runs integration of GT1+GT2+GT3 on `claude/gt-tich-hop` (protocol §9, lots I1–I4).
Schema changes approved (D-GT8): tables `tai_khoan`, `nhat_ky_thao_tac` after the `wharton_lock` block. Error codes
`gt3_*`; JS file `js/16_tai_khoan.js`; tests `tests/test_gt3_*.py`, `tests/test_giao_dien_gt3_*.py`.

## Plan (written by Opus; ticked by the lead after checker NO BUGS)
- [x] L1 Accounts and login (e62e24a, checker NO BUGS after fix1) (`tai_khoan.py`, API, lock/idle, recovery clear option, `js/16_tai_khoan.js`)
- [x] L2 Permission gate (5208c6d, checker NO BUGS after fix1) (`phan_quyen.py` map `QUYEN`, central enforcement, UI hides buttons)
- [x] L3 Audit log (ff12579, checker NO BUGS after fix1) (`nhat_ky_thao_tac`, append-only triggers, viewer + CSV export)
- [x] L4 Evidence docs (0b52a14, checker NO BUGS after fix1) (`docs/giai_trinh/*.md`, `so_do_luong.svg`, `PHAN_CONG.md` template)
- [x] CI gate (§6) green on branch head (c66889d; 2 fix rounds: recovery.py UTF-8 console, gate busy-wait; test decode)
- [ ] Integration §9 on `claude/gt-tich-hop`: I1 permissions, I2 student mode, I3 audit, I4 evidence pack, CI green

### Lead notes per lot
- All lots: every new table/option defaults OFF; accounts table empty ⇒ behaviour byte-identical to today.
- L2: the `dir(PipelineAPI)` completeness test will fail on integration until GT1/GT2 methods are classified (I1); that is intended.
- L3 (lead decision 2026-11-16, from checker L2): on-site entry writes (submit_preferences, submit_huy_chuong, submit_test_selection, attendance/score writes) stay `giao_vien`, so L3 audits EVERY write method of either role, not only `quan_tri` calls.

## Sessions
| Role | Model | Session id | State |
|---|---|---|---|
| lead | Opus | session_01YVAyu1qFUsCrfJzADRDejq | active |
| writer | Sonnet | session_01YVAyu1P96ELQbaGCN11z8y | archived (handoff after L1, 95fad10) |
| writer 2 | Sonnet | session_01YVAytzxaEXv7mrFdiaw85i | archived (handoff mid-L3, 385afc1) |
| writer 3 | Sonnet | session_01YVAytz9otUM5z9GiQks7T1 | archived (handoff after L4, 86826b4) |
| writer 4 | Sonnet | session_01YVAyu3LeKwuT4UDYYbTYZt | archived after CI green |
| checker | Sonnet | session_01YVAytz3RuHwjzM5L3EVnKE | archived (handoff after L3, e3e3202) |
| checker 2 | Sonnet | session_01YVAytyzqdgFPNE63JLRF6h | archived after CI green |

## Needs Truong
- **FA import warnings (pre-existing, not GT3):** importing `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` into an FA workspace returns 434 informational `wharton_chua_dung_het` warnings (same count on origin/main). Medals appear to be reported as unused commitment points. Recommendation: suppress that warning when `fa_daa` is ON (small fix under the FA item), so teachers are not flooded. Docs describe it as non-blocking for now.
- **Student self-entry needs login when accounts are ON:** on-site entry methods (`submit_preferences`, `submit_huy_chuong`, `submit_test_selection`) are `giao_vien` (logged in audit). Recommendation: keep; switch to `cong_khai` only if students must enter alone at the kiosk without a teacher present.

## Current state (overwrite each handoff)
- Done so far: branch created from `origin/claude/determined-allen-kig6ud`; this file written.
- In progress: §9 integration — waiting for GT2 (branch claude/gt2-tieu-chi not created yet). GT1 DONE 499edf1. Deadline to integrate without GT2: 2026-11-18 16:25 UTC.

## Decisions and gotchas (keep short)
- Decisions D-GT1…D-GT9 in the protocol §0; do not ask again.

## Next steps (ordered)
1. Run §5 for L1 → L4, then §6, then §9.

## Files touched
- docs/phien/claude__gt3-quyen-tai-lieu.md: branch handoff (this file)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-16 | Opus (lead) | Branch + handoff file created | |
| 2026-11-16 | Opus (lead) | L1-L4 passed checker; CI green on c66889d | 4 writers, 2 checkers (context handoffs) |

## Final summary GT3 (§10, tiếng Việt)
- **Lô xong:** L1 tài khoản + đăng nhập (e62e24a), L2 cổng phân quyền (5208c6d), L3 nhật ký thao tác chỉ-thêm (ff12579), L4 bộ tài liệu minh chứng `docs/giai_trinh/` (0b52a14). Không lô nào bỏ dở. Mỗi lô 1 vòng sửa sau soát.
- **Test mới:** `tests/test_gt3_tai_khoan.py`, `test_gt3_phan_quyen.py`, `test_gt3_nhat_ky.py`, `test_gt3_tai_lieu.py`, `test_giao_dien_gt3_dang_nhap.py`, `test_giao_dien_gt3_phan_quyen.py`.
- **CI:** xanh đủ 8 job trên c66889d — https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/43895943354 . Kết quả xếp mặc định giống hệt main (kiem_nhanh 60/60).
- **Needs Truong:** xem mục "Needs Truong" ở trên (2 việc, mỗi việc có khuyến nghị).
- **Truong nên thử tay:** (1) mở ứng dụng, chưa có tài khoản → chạy như cũ; (2) tạo tài khoản quản trị đầu tiên, đăng xuất, đăng nhập sai 5 lần → bị khóa 60 giây; (3) tạo tài khoản giáo viên, đăng nhập → không thấy tab quản trị, thử chạy xếp → bị từ chối; (4) quản trị xem "Nhật ký thao tác", xuất CSV, mở bằng Excel thấy tiếng Việt đúng; (5) làm theo `docs/giai_trinh/HUONG_DAN_CHAY.md` từ đầu.
- **Ghi chú nhật ký AI (cho `docs/nhat_ky_ai/`, các em tự viết lại):** AI (Opus điều phối, Sonnet viết mã và soát) làm GT3 ngày 2026-11-16: tài khoản 2 vai trò, cổng phân quyền, nhật ký thao tác, bộ tài liệu minh chứng. Người soát (AI) tìm 6 lỗi trước khi xong (tên Unicode NFC, cổng mở khi đọc lỗi, nhật ký ghi nhầm cơ sở dữ liệu, chờ khóa, quy trình tệp mẫu chế độ huy chương, mã chữ console Windows). Học sinh cần tự thử 5 bước trên và quyết 2 mục "Needs Truong".
