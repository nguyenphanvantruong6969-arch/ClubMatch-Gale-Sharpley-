# Prompt tự động UX5B-L3/L4 đến khi CI xanh (Truong, 2026-11-23)

Dán nguyên khối dưới đây vào MỘT phiên Claude Code mới (Sonnet). Phiên này là CODER/IMPLEMENTER (cộng tác viên của Truong);
nó tự kiểm, tự gọi checker, tự lặp CI đến khi xanh. Thay thế phần L2 của `UX5B_L2_L4_AUTO_PROMPT.md` (L2 đã xong, commit 8441218).

```
Bạn là IMPLEMENTER của UX5B (Sonnet), cộng tác viên của Truong. Repo: nguyenphanvantruong6969-arch/ClubMatch-Gale-Sharpley-.
Trả lời Truong bằng tiếng Việt. Không dùng Agent tool; dùng create_session cho checker.

NHÁNH: tạo `claude/ux5b-l3-l4-tu-dong` từ origin/claude/affectionate-lamport-595imn (đã có UX4, UX5A, UX5B-L1, UX5B-L2).
Chỉ đẩy lên nhánh này. KHÔNG đẩy lên main, ux5b-nap-xep-nhap-tay (cũ, đỏ), affectionate-lamport hay nhánh khác.
Tạo hồ sơ docs/phien/claude__ux5b-l3-l4-tu-dong.md (từ _TEMPLATE.md, tiếng Anh, <=150 dòng) ở commit đầu.

ĐỌC (theo token rules _GIAO_THUC_GON.md §3; đọc theo hàm, không in cả index.html/style.css/i18n.js):
CLAUDE.md; docs/phien/claude__ux5b-nap-xep-nhap-tay.md; docs/phien/UX5_GIAO_THUC.md (§3 vòng tự kiểm, §4 prompt checker);
docs/phien/CI_XANH_VONG_LAP_PROMPT.md; docs/ke_hoach/ux/UX5B_TU_NGU.md (ĐÃ DUYỆT 2026-11-23: từ ngữ §2, D1-D6, bản đồ lựa chọn);
tests/_ux5b_chung.py và tests/test_giao_dien_ux5b_l2.py (mẫu test L2); phần "Design rule" của docs/phien/claude__ux4-quan-ly-de-hieu.md.

ĐÃ CHỐT (không hỏi lại): từ ngữ §2; D1-D6 mặc định; câu hỏi mở: 1) chỉ gập chip buổi vào "Tuỳ chọn khi chạy", 2) CÓ nút vàng
"Chấm tiếp", 3) test Hick đo ở trạng thái "đã chọn một em". Chỉ giao diện + chữ: không sửa backend/API/schema/thứ tự pipeline,
không thêm thư viện, giữ mọi id và chỗ giữ của ngành ({person_l}...). Khoá i18n mới tiền tố ux5b_; CSS trong khối /* UX5B */;
test tests/test_giao_dien_ux5b_*.py; chuỗi đổi thêm vào SUA_CO_Y của tests/test_ws_nhan.py kèm ghi chú UX5B (không nới lỏng).

CHẠY TỰ ĐỘNG, KHÔNG DỪNG HỎI GIỮA CHỪNG (trừ mục DỪNG ở cuối).

B0 Chuẩn bị: tạo nhánh; xác nhận CI nền xanh (actions_list). Chưa xanh thì áp VÒNG LẶP CI trước khi làm gì khác.
B1 Nhập main: git fetch origin main && git merge origin/main (không rebase, không force-push, không git stash lúc merge).
   Xung đột đã biết: CHANGELOG.md, CLAUDE_CHI_TIET.md, TIEN_DO.md (giữ cả hai bên); index.html, style.css (mã thật: giữ cả hai
   tính năng MT2 và UX4/UX5A, soát tay). Test liên quan + ruff + kiem_nhanh.py 7/7, push. Đo lại số ô/nút vàng 3 thẻ.
B2 L3 Nhập nguyện vọng + Nhập điểm: ba bước thành ba mục gập, chỉ mục đang mở có nút vàng (D2); D3 giáo viên không thấy mục điểm
   quyết tâm; D4 btnScoringQuayLai; D5 lưới thẻ tính một nhóm; D6; "Chấm tiếp" vàng. Test viết trước.
B3 L4 Giao diện giáo viên + test: Hick budget + Von Restorff mỗi thẻ (quản trị và giáo viên đếm riêng, trạng thái "đã chọn một em"),
   test từ cấm, test "cùng payload" (ba lần Lưu gọi đúng API đúng tham số như trước). MILESTONE 2.
   Mỗi lô: test trước, sửa tối thiểu, test liên quan, ruff, kiem_nhanh.py MỘT lần, CHANGELOG + TIEN_DO "UX5B-L<n>", commit, push.
   Mỗi lô tối đa 2 vòng sửa; không qua thì git revert lô đó, ghi "Needs Truong", làm tiếp lô độc lập.
B4 Tự kiểm: sau B3 push; get_session lấy session_id; create_session (source_url repo, source_revision và outcome_branch = nhánh của
   bạn, model sonnet, title "UX5B checker") với prompt §4 UX5_GIAO_THUC.md (X=b; điền <base> <head> <coder_session_id>); ghi
   session_id vào hồ sơ; kết thúc lượt. PASS thì sang B5. FIX thì sửa đúng mục đó, commit "UX5B-FIX<n>: ...", push, send_message
   cho CHÍNH checker đó "ROUND <n>: re-check <base>..<head>". Tối đa 4 vòng FIX, sau đó revert lô sai, "Needs Truong", DỪNG.
B5 Soát mã: chạy skill soat-ma MỘT lần (kiem_nhanh.py + bốn tầng, chỉ báo cáo), sửa lỗi nó nêu nếu thuộc phạm vi UX5B, push.
B6 CI đến xanh (VÒNG LẶP CI bên dưới). Kết thúc chỉ khi CI xanh trên commit cuối VÀ checker PASS.
B7 KẾT: `git rev-list --left-right --count HEAD...origin/main` phải ra "N 0" (main đi tiếp thì merge lại, giải xung đột, quay B6).
   Cập nhật hồ sơ nhánh, TIEN_DO, CHANGELOG. Báo Truong: đường dẫn run xanh, 3 ảnh admin + 2 ảnh giáo viên của checker, số ô
   trước/sau mỗi thẻ, mục "Needs Truong". Gõ DONE. KHÔNG tạo PR, KHÔNG merge vào main khi Truong chưa nói rõ.

VÒNG LẶP CI (lặp đến khi XANH; không giới hạn số vòng, chỉ giới hạn theo nguyên nhân ở dưới)
  1. actions_list lấy run mới nhất của nhánh. Đang chạy: ScheduleWakeup 600-900 giây, đừng poll dày. Một push mới huỷ lượt đang chạy,
     nên gom sửa rồi mới push.
  2. Đỏ: list_workflow_jobs, get_job_logs từng job đỏ (return_content=true, tail_lines 80-100). Nhóm lỗi theo NGUYÊN NHÂN GỐC; tái hiện
     cục bộ chỉ với file test liên quan; sửa; ruff + kiem_nhanh.py 7/7; CHANGELOG; push; quay bước 1.
  3. Xanh: kiểm job coverage >= 85 %, rồi sang bước kế tiếp của quy trình.
  4. Chốt an toàn (thay cho giới hạn số vòng): cùng MỘT nguyên nhân gốc đỏ 3 vòng liên tiếp, hoặc đỏ vì hạ tầng (runner, mạng) 3 lần
     liên tiếp, thì ghi "Needs Truong" kèm log, DỪNG. Sắp hết giới hạn dùng: cập nhật "Current state" trong hồ sơ nhánh rồi dừng.
     Phiên sau nối lại từ hồ sơ và tiếp tục vòng lặp.

DỪNG VÀ HỎI TRUONG (chỉ các trường hợp này): đổi backend/API/schema; mâu thuẫn bất biến CLAUDE.md; phải đổi CHỮ đã duyệt; cần thư viện
mới; chạm chốt an toàn mục 4; hết 4 vòng FIX.

QUY TẮC CỨNG: không bỏ qua/xoá/nới test để qua CI; không push commit rỗng, không viết lại lịch sử, không force-push; không chạy cả
bộ test cục bộ (22 phút, CI chạy); không git stash khi đang merge; số liệu đo là dữ liệu MÔ PHỎNG; không viết nhận xét/kết luận của báo
cáo dự án; hàng cuối commit message ghi dòng Co-Authored-By theo quy định phiên.

MÔI TRƯỜNG TEST: python3.11 -m venv ngoài thư mục dự án, pip install -r requirements-dev.txt; Playwright cần Chromium 1255, container
có 1243 trong /opt/pw-browsers: tạo thư mục có symlink chromium-1255 và chromium_headless_shell-1255 trỏ tới hai thư mục 1243, thêm
ffmpeg-1011, đặt PLAYWRIGHT_BROWSERS_PATH tới đó; không chạy `playwright install`.
Chạy: python -m pytest -q -p no:cacheprovider -n 4 --no-cov --tb=line <file> 2>&1 | tail -15
```
