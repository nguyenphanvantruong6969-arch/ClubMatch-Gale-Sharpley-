# Prompt: sửa CI đến khi xanh và merge được (nhánh claude/affectionate-lamport-595imn)

Dán nguyên khối dưới đây vào một phiên Claude Code mới (repo `nguyenphanvantruong6969-arch/ClubMatch-Gale-Sharpley-`).

```
Bạn là Sonnet, làm việc trên nhánh claude/affectionate-lamport-595imn của repo ClubMatch-Gale-Sharpley-.
Trả lời Truong bằng tiếng Việt. Đọc CLAUDE.md trước, rồi docs/phien/claude__affectionate-lamport-595imn.md
(nếu chưa có trên nhánh thì dùng phần "Bối cảnh" dưới đây).

MỤC TIÊU
Làm CI (workflow "Tests (rbda-kiosk)": Lint, Linux 1-6, Windows 1-9, job do-phu >= 85 %) XANH hoàn toàn trên commit
mới nhất của nhánh này, VÀ làm nhánh merge được vào main (không xung đột, CI xanh sau khi đã merge main vào).
Đây chỉ là việc sửa CI. KHÔNG làm UX5B L2-L4 (đang chờ Truong duyệt MILESTONE 1). KHÔNG tạo PR, KHÔNG merge vào main
khi Truong chưa nói rõ trong chat.

BỐI CẢNH
- Đỉnh nhánh: ba1e4ac = UX5B-L1 (chỉ tài liệu, 0d02f6a) + merge nhánh claude/ux5a-ket-qua-de-hieu (16 commit sửa) + sửa
  một test chạy đua (tests/test_giao_dien_a13_10_nhan.py, chờ bảng Tổng quan vẽ lại sang tiếng Anh).
- Run #1401 (0d02f6a) đỏ vì nhánh rẽ ra trước các bản sửa UX5A; run #1402 (ba1e4ac) đang chạy lúc 16:20 UTC,
  chưa biết kết quả. Đọc nó đầu tiên.
- So với main (2b5a87e, đã có MT2 "Chia CLB theo loại" từ PR #28): nhánh hơn 28 commit, thiếu 43 commit.
  Thử merge main (đã huỷ) xung đột ở: CHANGELOG.md, docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/ke_hoach/TIEN_DO.md
  (tài liệu: giữ cả hai bên) và index.html, style.css (MÃ THẬT: MT2 va UX4/UX5A, giữ cả hai tính năng, soát tay).
- Từ ngữ: Truong đã chọn giữ "Chỉ tiêu" / "Suất ưu tiên" (phương án B2). Nếu xung đột về chữ không rõ, hỏi Truong.

CÁCH LÀM — VÒNG LẶP (tối đa 6 vòng, tự nhịp bằng ScheduleWakeup 600-900 giây, không hỏi dồn dập)
Vòng 0: đọc kết quả run #1402. Xanh thì sang bước MERGE MAIN. Đỏ thì chạy vòng sửa.
Mỗi vòng sửa:
 1. mcp__github__actions_list (list_workflow_runs, lọc theo nhánh) lấy run mới nhất. Đang chạy thì chờ, không poll dày.
    Mỗi lần push sẽ HUỶ lượt CI đang chạy của nhánh, nên gom các sửa rồi mới push.
 2. Run đỏ: list_workflow_jobs, rồi get_job_logs từng job đỏ (return_content=true, tail_lines 80-100), tìm dòng
    "FAILED" / "short test summary". Nhóm lỗi theo NGUYÊN NHÂN GỐC trước khi sửa.
 3. Tái hiện cục bộ chỉ với các file test liên quan (cấm chạy cả bộ 22 phút). Sửa nguyên nhân, không sửa triệu chứng.
    Test chập chờn: chạy 3 lần cục bộ, sửa bằng wait_for_function, không dùng sleep.
    Lỗi chỉ ở Windows: soi đường dẫn gạch ngược, tệp mở chưa đóng, tên tệp dành riêng; không chạy được Windows nên đọc log.
 4. Trước khi push: test liên quan, `ruff check .`, `python .claude/skills/soat-ma/scripts/kiem_nhanh.py` (phải 7/7),
    thêm mục CHANGELOG.md, commit có dòng ghi công, `git push -u origin claude/affectionate-lamport-595imn`
    (lỗi mạng thử lại tối đa 4 lần, giãn dần).
 5. Hết 6 vòng, hoặc lỗi cần quyết định sản phẩm: dừng và báo Truong.

BƯỚC MERGE MAIN (sau khi nhánh xanh)
 a. `git fetch origin main && git merge origin/main` (không rebase, không force-push). Giải 5 xung đột ở trên.
 b. Chạy các test giao diện liên quan tới index.html/style.css (ux2_nut, ux1_*, ux4_*, ux5a_*, mt1_*, sg2_*, t3_*),
    ruff, kiem_nhanh.py, rồi push và quay lại vòng lặp cho đến khi CI xanh trên commit merge.
 c. Xong khi: CI xanh toàn bộ trên đỉnh nhánh, và `git rev-list --left-right --count HEAD...origin/main` ra "N 0".
    Báo Truong: đường dẫn run xanh, số đo trên, tóm tắt các xung đột đã giải và lý do. DỪNG. Truong quyết định PR/merge.

QUY TẮC CỨNG
- Không bỏ qua, xoá hay nới lỏng test để qua CI. Không push commit rỗng, không đóng/mở lại PR để kích CI, không viết lại lịch sử.
- Không push lên nhánh khác (ux5a, ux5b, main). Không dùng subagent (CLAUDE.md quy tắc 10).
- 8 bất biến trong CLAUDE.md vẫn giữ; kết quả mặc định phải giống từng byte (kiem_nhanh.py kiểm 15 ca).
- KHÔNG chạy `git stash` khi đang merge: nó làm mất MERGE_HEAD.
- Số liệu thẩm định là dữ liệu MÔ PHỎNG; không viết phần nhận xét/kết luận của báo cáo dự án.
- Cuối cùng cập nhật docs/phien/claude__affectionate-lamport-595imn.md (nhật ký phiên, tick kế hoạch) và CHANGELOG.md.

MÔI TRƯỜNG TEST (container đám mây)
- python3.11 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt  (.venv không được đưa vào commit)
- Playwright Python cần Chromium bản 1255, container có 1243 trong /opt/pw-browsers: tạo thư mục có symlink
  chromium-1255 và chromium_headless_shell-1255 trỏ tới hai thư mục 1243, thêm ffmpeg-1011, đặt PLAYWRIGHT_BROWSERS_PATH
  tới đó. Không chạy `playwright install`.
- Chạy: python -m pytest -q -p no:cacheprovider -n 4 --no-cov <các file>
```
