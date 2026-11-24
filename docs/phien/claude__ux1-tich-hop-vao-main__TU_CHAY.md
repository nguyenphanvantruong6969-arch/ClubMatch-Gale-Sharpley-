# Lệnh tự chạy: đưa PR #32 (UX1F) về CI xanh và merge được

> Phiên TỰ CHẠY, không hỏi Truong giữa chừng. Đọc CLAUDE.md trước, rồi tệp này. Không dùng subagent. Báo cáo cuối bằng tiếng Việt, giữ nguyên tên hàm. Số liệu là dữ liệu MÔ PHỎNG.
> Nhánh: `claude/ux1-tich-hop-vao-main`, PR #32 "UX1F: sửa sau tích hợp UX1" (đích main). Tệp này có thể xoá khi xong.

MỤC TIÊU (chỉ dừng khi đạt hoặc gặp điều kiện DỪNG bên dưới): PR #32 có CI xanh TOÀN BỘ (mọi job, gồm ngưỡng độ phủ) VÀ mergeable_state = "clean" với main mới nhất. Không merge PR nào. Chỉ push lên `claude/ux1-tich-hop-vao-main`. Không mở PR mới. Chỉ sửa TEST (và tài liệu ghi chép), không đổi mã sản phẩm; bất biến 1-8 của CLAUDE.md không được đụng.

## BƯỚC A. Sửa lỗi CI hiện có (run 45303334169, Linux 5/6), đã kiểm thử cục bộ
`tests/test_giao_dien_ux1f_l4_mot_o_chon_lop.py::test_o_chon_lop_loc_bang_va_quyet_dinh_lop_in_phieu`, dòng 84: `page.locator("#btnUx1bPhieuLop").click()` hết thời gian vì nút không hiện. Nguyên nhân: UX5A-L2 (đã ở main) gập nút này vào nếp `<details id="ux1bThemMenu">` (summary `#ux1bThemTom`), đóng sẵn. Sửa: ngay trước dòng 84 thêm `page.locator("#ux1bThemTom").click()`. Các dòng 103 và 105 dùng is_disabled/is_enabled nên không đổi. Rà `tests/` và `tests_stress/` xem còn test nào bấm hoặc is_visible `#btnUx1bBaoCao`, `#btnUx1bPhieuLop`, `#btnUx1bBaoCaoPdf` mà chưa mở nếp; sửa cùng kiểu.

## VÒNG LẶP CI (lặp đến khi đạt MỤC TIÊU)
1. Trước mỗi push: `ruff check .`; chạy các test liên quan (tests/test_giao_dien_ux1f_l4_mot_o_chon_lop.py, test_giao_dien_ux1b_vai_gv.py, test_ux1i_i3_phieu_bao_cao.py, test_giao_dien_ux5a_l2.py, test_giao_dien_ux5a_l4.py, test_giao_dien_xp1_luu_pdf_mot_em.py, test_ux1f_*.py). KHÔNG chạy cả bộ (CI chạy). Test đỏ trước khi sửa.
2. Commit có thông điệp rõ (mã mục + nguyên nhân) và dòng CHANGELOG.md. Gom commit, push MỘT lần mỗi vòng (push mới huỷ run đang chạy).
3. Chờ CI: dùng `mcp__claude-code-remote__send_later` (delay_minutes 15) rồi kết thúc lượt; khi được đánh thức, xem run bằng `mcp__github__actions_list` rồi `mcp__github__get_job_logs` (run_id + failed_only, tail_lines lớn đủ thấy phần pytest FAILURES). KHÔNG thăm dò dày hơn 1 lần mỗi 10 phút.
4. Có job đỏ: tìm NGUYÊN NHÂN GỐC, viết hoặc xác nhận test tái hiện, sửa tối thiểu, quay lại bước 1. Nếu là test thời gian trên Windows (ví dụ tests/test_a13_12_browser_host.py) nghi flake: chạy lại job đỏ (`mcp__github__actions_run_trigger`, rerun_failed_jobs; nếu không có thì thêm một dòng thật vào hồ sơ nhánh để push kích CI, KHÔNG push commit rỗng); chỉ coi là lỗi thật khi đỏ lại ở 2 lần chạy khác nhau. Không bỏ qua, không xfail, không vô hiệu hoá test, không nới ngưỡng thời gian để lách. Không viết lại lịch sử, không đóng mở lại PR.
5. CI xanh: đọc `mcp__github__pull_request_read` (get) của PR #32; nếu mergeable_state không phải "clean" (xung đột hoặc main đã đổi, ví dụ PR #31 hoặc PR khác đã merge): `git fetch`; `git merge origin/main`; giải xung đột: CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, style.css giữ cả hai bên; dòng đếm tệp test trong docs/ke_hoach/CLAUDE_CHI_TIET.md đếm lại bằng `ls tests/test_*.py | wc -l`; .github/workflows/tests.yml giữ cả pytest-xdist lẫn pypdf; xuat_pdf.py (nếu main đã có SF-A5 tăng tốc PDF) giữ ĐỒNG THỜI bố cục UX1F và tăng tốc SF-A5 (bộ nhớ đệm theo CLB, `rl_config.useA85 = 0` có khôi phục trong finally, `khi_xong_em` / `get_tien_do_xuat`) rồi chạy tests/test_sf_a_4.py, tests/test_sf_a_5.py, tests/test_ux1f_*.py, tests/test_xp1_*.py. Xung đột ngữ nghĩa (git không báo) thì sửa TEST cho khớp giao diện mới. Rồi quay lại bước 1.
6. Điều kiện đạt: (a) run mới nhất của đầu nhánh có mọi job success, (b) mergeable_state = "clean", (c) `git rev-list --left-right --count origin/main...HEAD` cho "0 N".

## ĐIỀU KIỆN DỪNG SỚM
Ghi trạng thái vào `docs/phien/claude__ux1-tich-hop-vao-main.md` theo `docs/phien/_TEMPLATE.md` rồi báo cáo, khi: cùng một nguyên nhân gốc lặp 3 vòng; lỗi nằm ở mã sản phẩm cần quyết định của Truong; mâu thuẫn với bất biến CLAUDE.md; cần thư viện mới; quá 8 vòng CI; ngữ cảnh gần 400k token.

## BÁO CÁO CUỐI (tiếng Việt, ngắn)
Đạt hay dừng sớm; số vòng CI và nguyên nhân từng lần đỏ; việc còn tồn đọng (ví dụ: giáo viên chưa bị giới hạn theo lớp khi in phiếu, quyết định của Truong).
