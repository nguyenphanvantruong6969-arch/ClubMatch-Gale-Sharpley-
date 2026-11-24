# Lệnh tự chạy: đưa PR #31 (SF) về CI xanh và merge được

> Phiên TỰ CHẠY, không hỏi Truong giữa chừng. Đọc CLAUDE.md trước, rồi tệp này. Không dùng subagent. Báo cáo cuối bằng tiếng Việt, giữ nguyên tên hàm. Số liệu là dữ liệu MÔ PHỎNG.
> Nhánh: `claude/great-edison-6ry675`, PR #31 "SF: fix stress-test bugs" (đích main). Tệp này có thể xoá khi xong.

MỤC TIÊU (chỉ dừng khi đạt hoặc gặp điều kiện DỪNG bên dưới): PR #31 có CI xanh TOÀN BỘ (mọi job, gồm ngưỡng độ phủ) VÀ mergeable_state = "clean" (không xung đột) với main mới nhất, VÀ nhánh đã gộp xong `claude/ux1-tich-hop-vao-main` (PR #32, UX1F) để merge #31 và #32 theo thứ tự nào cũng được. Không merge PR nào. Chỉ push lên `claude/great-edison-6ry675`. Không mở PR mới.

PHẠM VI SỬA: chủ yếu TEST. Mã sản phẩm chỉ được đổi ở bước giải xung đột xuat_pdf.py (bước B) và chỉ để giữ cả hai bên. Bất biến 1-8 của CLAUDE.md không được đụng.

## BƯỚC A. Sửa lỗi CI hiện có (run 45302117321), đã kiểm thử cục bộ
- A1. `tests/test_giao_dien_sf_b_lo2.py::test_st_b_006_chi_tieu_thap_phan_bao_loi_o_chi_tieu`: trước `page.fill("#clubFormId", "T4")` thêm: `if not page.locator("#clubFormId").is_visible(): page.locator("#clubFormThemTuyChon").click()` (UX4-L3 gập Mã CLB sau nút "Thêm tuỳ chọn"; chỉ bấm khi ô chưa hiện).
- A2. `tests/test_giao_dien_sf_b_lo2.py::test_st_b_004_nhap_tai_cho_ma_khac_hoa_thuong_hoi_lai`: sau khi bấm tab fallback, trước `wait_for_selector("#newStudentId", state="visible")` thêm: `if page.locator("#ux5bTaoMoi").get_attribute("open") is None: page.locator("#ux5bTaoMoi > summary").click()` (UX5B-L3 gập ô tạo học sinh mới).
- A3. Windows 8/9: `tests/test_a13_12_browser_host.py::test_tai_lai_trang_khong_tat_may_chu` ("F5 làm máy chủ tắt"): nghi flake thời gian (PR không đổi browser_host.py; cùng test đạt ở PR #32). Chạy lại job đỏ (mcp__github__actions_run_trigger, rerun_failed_jobs; nếu công cụ không có thì thêm một dòng thật vào hồ sơ nhánh `docs/phien/claude__great-edison-6ry675.md` để push kích CI, KHÔNG push commit rỗng). Chỉ khi nó đỏ lại ở 2 lần chạy khác nhau mới coi là lỗi thật: đọc browser_host.py, viết test tái hiện, sửa tối thiểu; KHÔNG nới ngưỡng thời gian để lách.
- A4. Rà `tests/` và `tests_stress/b/` cho cùng kiểu lỗi (ô nằm sau mục gập UX4-L3, UX4-L4 "Tuỳ chỉnh thêm" ở tab #qlTabCachXep, UX5B-L3). Dùng hàm hỗ trợ nhỏ.

## BƯỚC B. Gộp UX1F để hết xung đột với PR #32
- B1. `git fetch origin; git merge origin/claude/ux1-tich-hop-vao-main`. Xung đột đã biết: xuat_pdf.py (SF-A5 viết lại để tăng tốc PDF 3000 em; UX1F-L2 sửa bố cục phiếu một trang, tiêu đề cột không gãy chữ, khối giu_cung tiêu đề buổi), cộng CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, dòng đếm tệp test trong docs/ke_hoach/CLAUDE_CHI_TIET.md (đếm lại bằng `ls tests/test_*.py | wc -l`), .github/workflows/tests.yml (giữ cả pytest-xdist lẫn pypdf), style.css (giữ cả hai khối).
- B2. xuat_pdf.py: giữ ĐỒNG THỜI hành vi UX1F (bố cục) và tăng tốc SF-A5 (bộ nhớ đệm theo CLB, tắt ASCII85 `rl_config.useA85 = 0` có khôi phục trong finally, callback `khi_xong_em` / `get_tien_do_xuat`). Chạy: tests/test_sf_a_4.py, tests/test_sf_a_5.py (phần ≤ 30 s ở 3000 em nếu chạy được cục bộ, nếu quá chậm thì để CI kiểm), tests/test_ux1f_*.py, tests/test_xp1_*.py, tests/test_ux1i_*.py. Số trang và chữ trong PDF của một bộ dữ liệu cố định phải trùng bản nền; ghi số đo vào CHANGELOG.
- B3. Xung đột ngữ nghĩa (git không báo) giữa SF, UX5 và UX1F: sửa TEST cho khớp giao diện mới, không đổi mã giao diện. Ví dụ UX1F-L4 thay `#ux1bLop` bằng `#kqChonLop`; UX5A-L2 gập "In phiếu cả lớp" và "Báo cáo tổng hợp (PDF)" vào nếp `#ux1bThemTom` (phải bấm mở trước). Mẫu sửa ở nhánh `claude/ux1-tich-hop-vao-main`.

## VÒNG LẶP CI (lặp đến khi đạt MỤC TIÊU)
1. Trước mỗi push: `ruff check .`; chạy các test liên quan đã nêu (KHÔNG chạy cả bộ, CI chạy); `python kiem_nhanh.py`. Test đỏ trước khi sửa.
2. Commit có thông điệp rõ (mã mục + nguyên nhân) và dòng CHANGELOG.md. Gom commit, push MỘT lần mỗi vòng (push mới huỷ run đang chạy).
3. Chờ CI: dùng `mcp__claude-code-remote__send_later` (delay_minutes 15) rồi kết thúc lượt; khi được đánh thức, xem run bằng `mcp__github__actions_list` rồi `mcp__github__get_job_logs` (run_id + failed_only, tail_lines lớn đủ thấy phần pytest FAILURES). KHÔNG thăm dò dày hơn 1 lần mỗi 10 phút.
4. Có job đỏ: tìm NGUYÊN NHÂN GỐC (đọc cả test và phần giao diện/mã liên quan), viết hoặc xác nhận test tái hiện, sửa tối thiểu, quay lại bước 1. Không bỏ qua, không xfail, không vô hiệu hoá test để ra xanh. Không push commit rỗng, không viết lại lịch sử, không đóng mở lại PR.
5. CI xanh: đọc `mcp__github__pull_request_read` (get) của PR #31; nếu mergeable_state không phải "clean" (xung đột hoặc nhánh đích đã đổi): `git fetch`; `git merge origin/main` và (nếu có commit mới) `git merge origin/claude/ux1-tich-hop-vao-main`; giải xung đột theo quy tắc ở bước B; quay lại bước 1.
6. Điều kiện đạt: (a) run mới nhất của đầu nhánh có mọi job success, (b) mergeable_state = "clean", (c) `git rev-list --left-right --count origin/main...HEAD` cho "0 N", (d) `origin/claude/ux1-tich-hop-vao-main` là tổ tiên của HEAD (`git merge-base --is-ancestor`). Nếu (d) sai vì #32 có commit mới thì gộp tiếp và lặp.

## ĐIỀU KIỆN DỪNG SỚM
Ghi trạng thái vào `docs/phien/claude__great-edison-6ry675.md` theo `docs/phien/_TEMPLATE.md` rồi báo cáo, khi: cùng một nguyên nhân gốc lặp 3 vòng; lỗi nằm ở mã sản phẩm cần quyết định của Truong; mâu thuẫn với bất biến CLAUDE.md; cần thư viện mới; quá 8 vòng CI; ngữ cảnh gần 400k token.

## BÁO CÁO CUỐI (tiếng Việt, ngắn)
Đạt hay dừng sớm; số vòng CI và nguyên nhân từng lần đỏ; số đo PDF; việc còn tồn đọng (ví dụ 19 test UI trong tests_stress/b/ viết theo giao diện cũ, nằm ngoài CI; đánh giá flake Windows).
