# Branch handoff: claude/gt-tich-hop

> Fresh session: read CLAUDE.md, docs/phien/GT_GIAO_THUC.md (§5, §6, §9), then THIS file.
> English. Cap 150 lines. Rewrite "Current state"; only APPEND to "Session log".

Status: DONE 572685d CI green 2026-11-17 (run https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/44052031595)

## Feature / goal
Integrate GT1 (giải trình, `claude/gt1-giai-trinh` DONE 499edf1), GT2 (tiêu chí, `claude/gt2-tieu-chi` DONE 8965d2b)
and GT3 (quyền + tài liệu, `claude/gt3-quyen-tai-lieu` DONE c66889d) on one branch from `origin/main` (35609f7), then
run integration lots I1-I4 (spec: `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md` § "Integration lots") and the §6 CI gate.
Truong merges to main himself. No PR.

## Plan (written by Opus; ticked by Sonnet)
- [x] I0 merges: GT1 already merged by lead (a38fef8, clean). Writer: `git merge --no-ff origin/claude/gt2-tieu-chi`,
      then `git merge --no-ff origin/claude/gt3-quyen-tai-lieu`. Conflicts are shared files only (CHANGELOG.md,
      docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/ke_hoach/TIEN_DO.md, i18n_errors.py, i18n_loi.js, index.html,
      js/_danh_sach.txt, style.css): keep every team's block, GT1→GT2→GT3 order, renumber/reformat nothing;
      `i18n_loi.js` = rerun `python tao_i18n_js.py`; CLAUDE_CHI_TIET tests row = recount files/collect.
      Done when: no conflict markers (`git grep -nE '^(<<<<<<<|>>>>>>>)'` empty), `ruff check .` clean, all
      `tests/test_gt1_*`, `test_gt2_*`, `test_gt3_*` (non-UI) pass except the intended `dir(PipelineAPI)` completeness
      failure in `test_gt3_phan_quyen.py` (fixed in I1), kiem_nhanh invariant-1 identical.
- [x] I1 permission map: classify every GT1/GT2 PipelineAPI method in `QUYEN`.
      GT1: `tra_cuu_hoc_sinh` → `cong_khai`; lookup / slip view+export → `giao_vien`; code (re)generation → `quan_tri`.
      GT2: get_tieu_chi, run_thu, list_lan_chay, so_sanh_lan_chay, export_so_sanh_html, export_so_sanh_csv,
      ap_dung_tieu_chi → `quan_tri` (GT2 lead: compare student list is admin-only; stricter than the task file's
      "compare view → giao_vien", see Needs Truong #1). Done when `test_gt3_phan_quyen.py` passes.
- [x] I2 student mode: accounts ON → leaving the self-lookup overlay needs an admin login; while in it only
      `cong_khai` methods work. Done when a Chromium test shows a student cannot reach any tab.
- [x] I3 audit: run_thu, ap_dung_tieu_chi, code (re)generation, slip export each log exactly one audit row.
      Done when tested (`tests/test_gt_tich_hop.py` or a `test_gt3_*` file).
- [x] I4 evidence pack (4661b7b; checker bug 1 tab name fixed in the I4-fix commit): `du_lieu_test/tao_ca_mau_giai_trinh.py` (simulated 120 students, fixed seed) writes
      `docs/giai_trinh/CA_MAU.md` (3 got 1st choice, 3 did not — GT1 sentences + data; 1 run blocked by missing data,
      real message; 1 conflicting criteria rejected at save, real message; GT2 table default vs one alternative:
      changed students, per-group effects). Then `docs/giai_trinh/tao_goi_minh_chung.py` builds
      `GOI_MINH_CHUNG.docx` + `.pdf`; fill the "(sau tích hợp)" steps. Done when `tests/test_gt_tich_hop.py`
      regenerates CA_MAU.md byte-identically and every case matches app output. All data SIMULATED, labelled so.
- [x] §6 CI gate on `claude/gt-tich-hop` (572685d; fixes: CA_MAU.md LF via .gitattributes, code-map wording) (lint + all shards + coverage ≥ 85 %).

## Current state (overwrite each handoff)
- Done: I0-I4. I4 checker bug 1 ("thẻ Quản trị" -> "thẻ Quản lý" in KICH_BAN_DEMO/VIDEO) fixed + test
  `test_gt3_tai_lieu.py::test_ten_the_trong_kich_ban_khop_nhan_giao_dien`; GOI_MINH_CHUNG.docx/.pdf rebuilt.
- In progress: none. Integration DONE; Truong merges to main himself.
- Tests: test_gt3_tai_lieu.py + test_gt_tich_hop.py 35 passed; ruff clean (docs/test-only change, no product code).

## Sessions
| Role | Model | Session | State |
|---|---|---|---|
| lead | Opus | session_01YVAyu27w5WZmfqRfkjo3Av | running |
| writer | Sonnet | session_01YVAytzUoskbGS1rGPtH4ZW | GO I0 sent 05:30 UTC |
| checker | Sonnet | session_01YVAytyqoQv2u5JTmCyKLkE | waiting for REVIEW I0 |

## Needs Truong
1. Compare view permission: task file says `giao_vien`; GT2 lead classified all GT2 APIs `quan_tri` because the
   compare student list shows other students' outcomes. Recommend: keep `quan_tri` (privacy); loosen later if
   teachers need it.
2. Audit rows keep student ids passed as arguments (e.g. which student's slip was exported); no names, scores,
   codes or passwords. Recommend: keep (admin-only log, needed to answer "who printed whose slip").
3. (pre-existing GT3) Calls while logged out each add one refused row with no user; nothing limits how many.
   Recommend: accept for a single offline kiosk; add a rate limit only if the log grows in practice.
4. Student mode lock is held in memory: restarting the app clears it and every login session (by design).
(GT1/GT2/GT3 branch files hold their own Needs Truong lists; they are carried into the final summary.)

## Decisions and gotchas
- Merge order GT1 → GT2 → GT3 (§9 step 2). Never rebase or force-push.
- GT3 L2 `dir(PipelineAPI)` completeness test fails after merges until I1: intended.

## Next steps (ordered)
1. Writer: I0, then I1-I4 by §5 loop. 2. Lead: §6 CI gate. 3. Status DONE + §10 summary, archive children, stop.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-17 | Opus (lead) | GT2 DONE verified (run 44018417803 success); branch created, GT1 merged, file written | — |

| 2026-11-17 | Opus (orig. GT3 lead) | I4 fix + 2 CI fixes, CI green 572685d, Status DONE | integration sessions had stopped on spend limit |

## Final summary (§10, tiếng Việt)
- **Xong:** I0 gộp GT1+GT2+GT3; I1 bảng quyền cho hàm GT1/GT2; I2 chế độ học sinh tự tra cứu khoá ở backend; I3 nhật ký cho chạy thử / áp dụng tiêu chí / mã tra cứu / phiếu; I4 ca mẫu + gói minh chứng (`docs/giai_trinh/CA_MAU.md`, `GOI_MINH_CHUNG.docx/.pdf`). Không lô nào bỏ.
- **CI:** xanh đủ 8 job trên 572685d — https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/actions/runs/44052031595 . Nhánh đã chứa main mới nhất.
- **Needs Truong (gộp 4 nhánh, kèm khuyến nghị):**
  1. Xem so sánh chạy thử chỉ cho quản trị (đặc tả ghi giáo viên). KN: giữ quản trị (riêng tư).
  2. Nhật ký giữ mã học sinh trong tham số (vd in phiếu của ai). KN: giữ.
  3. Gọi khi chưa đăng nhập mỗi lần thêm một dòng bị từ chối, không giới hạn. KN: chấp nhận cho kiosk đơn.
  4. Cờ chế độ học sinh nằm trong bộ nhớ; khởi động lại là mất. KN: giữ (đúng thiết kế).
  5. (GT1) Câu giải trình chỉ tiếng Việt. KN: giữ; thêm tiếng Anh nếu hội đồng cần.
  6. (GT1) Chỉ giải trình được lần chạy mới nhất. KN: giữ.
  7. (GT2) Chạy thử chưa hỗ trợ chế độ huy chương. KN: để sau.
  8. (GT2) Chạy thử lưu tiêu chí dạng chuẩn hoá. KN: giữ.
  9. (GT3) 434 cảnh báo khi nạp sổ mẫu chế độ huy chương (có sẵn trên main). KN: ẩn cảnh báo khi bật huy chương.
  10. (GT3) Học sinh tự nhập nguyện vọng cần đăng nhập khi đã bật tài khoản. KN: giữ.
- **Truong thử tay:** (1) chạy kiosk, chưa tạo tài khoản → như cũ; (2) tạo quản trị, tra cứu một học sinh, in phiếu; (3) "Thử cấu hình": đổi một tiêu chí, Chạy thử, So sánh, xem kết quả chính thức không đổi; (4) bật "Chế độ học sinh tra cứu", thử thoát → phải đăng nhập quản trị; (5) mở `docs/giai_trinh/GOI_MINH_CHUNG.pdf`.
- **Nháp nhật ký AI (các em tự viết lại):** 16–17/11/2026 AI (Opus điều phối, Sonnet viết/soát) làm GT1, GT2, GT3 trên 3 nhánh rồi gộp; người soát AI bắt lỗi trước mỗi lô; CI xanh. Học sinh cần tự thử 5 bước và quyết 10 mục trên. Mọi số liệu là MÔ PHỎNG.
