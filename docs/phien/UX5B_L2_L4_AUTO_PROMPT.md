# Prompt: UX5B tự động từ merge main đến L2-L4 và checker (Truong duyệt M1 ngày 2026-11-23)

Dán nguyên khối dưới đây vào MỘT phiên Claude Code mới (Sonnet). Phiên này là CODER của Track B; nó tự gọi checker.

```
Bạn là CODER Track B của UX5 (Sonnet). Repo: nguyenphanvantruong6969-arch/ClubMatch-Gale-Sharpley-.
Nhánh làm việc: claude/affectionate-lamport-595imn (nền xanh CI, run #1403; đã có sửa UX5A và UX5B-L1).
KHÔNG đẩy lên claude/ux5b-nap-xep-nhap-tay (cũ, đỏ), ux5a hay main. Trả lời Truong bằng tiếng Việt.

ĐỌC (theo token rules của _GIAO_THUC_GON.md §3, đọc theo hàm, không in cả index.html/style.css/i18n.js):
CLAUDE.md; docs/phien/claude__affectionate-lamport-595imn.md; docs/phien/claude__ux5b-nap-xep-nhap-tay.md;
docs/phien/UX5_GIAO_THUC.md (luật Track B, vòng tự kiểm §3, prompt checker §4);
docs/ke_hoach/ux/UX5B_TU_NGU.md (bảng từ ngữ, D1-D6, bản đồ lựa chọn: ĐÃ ĐƯỢC TRUONG DUYỆT ngày 2026-11-23, làm đúng như viết);
phần "Design rule" của docs/phien/claude__ux4-quan-ly-de-hieu.md.

CÁC QUYẾT ĐỊNH ĐÃ CHỐT (không hỏi lại): từ ngữ §2; D1-D6 theo mặc định; câu hỏi mở: 1) chỉ gập chip buổi vào
"Tuỳ chọn khi chạy", 2) CÓ nút vàng "Chấm tiếp", 3) test Hick đo ở trạng thái "đã chọn một em". Chỉ giao diện + chữ:
không sửa backend/API/schema/thứ tự pipeline, không thêm thư viện, giữ mọi id, giữ chỗ giữ của ngành ({person_l}...).
Khoá i18n mới tiền tố ux5b_; CSS trong khối /* UX5B */; test tests/test_giao_dien_ux5b_*.py; chuỗi đổi thêm vào
SUA_CO_Y của tests/test_ws_nhan.py kèm ghi chú UX5B (không nới lỏng). Chạm shared files chỉ ở vùng/khoá của mình.

QUY TRÌNH TỰ ĐỘNG (không dừng hỏi giữa chừng, trừ các điều kiện DỪNG ở cuối)

P0 — Nhập main trước (làm MỘT lần, trước khi viết mã giao diện)
  a. Xác nhận CI nhánh xanh (actions_list, run mới nhất). Chưa xanh thì sửa trước theo
     docs/phien/CI_XANH_VONG_LAP_PROMPT.md (cùng quy tắc, tối đa 6 vòng).
  b. git fetch origin main && git merge origin/main (không rebase, không force-push, KHÔNG git stash giữa lúc merge).
     Xung đột đã biết: CHANGELOG.md, docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/ke_hoach/TIEN_DO.md (tài liệu: giữ cả hai bên)
     và index.html, style.css (MÃ THẬT: MT2 "Chia CLB theo loại" va UX4/UX5A: giữ cả hai tính năng, soát tay).
  c. Test liên quan + ruff + kiem_nhanh.py (7/7), push, chờ CI xanh (vòng lặp CI bên dưới). Hết P0 khi
     `git rev-list --left-right --count HEAD...origin/main` ra "N 0".
  d. Đo lại nhanh số ô và số nút vàng của 3 thẻ (Xếp CLB, Nhập nguyện vọng, Nhập điểm; quản trị + giáo viên). MT2 chạm khối
     điểm quyết tâm của Nhập nguyện vọng. Ghi số mới vào hồ sơ nhánh. Nếu thiết kế đã duyệt không còn đúng
     (một ô/nút biến mất hoặc xuất hiện ngoài bảng) thì áp dụng cùng luật cho phần mới; chỉ DỪNG khi phải đổi CHỮ đã duyệt.

L2 -> L3 -> L4 (đúng kế hoạch trong hồ sơ nhánh; mỗi lô: test viết trước từ tiêu chí, sửa tối thiểu, test liên quan,
  ruff, kiem_nhanh.py MỘT lần mỗi lô; CHANGELOG + dòng TIEN_DO UX5B-L<n>; commit "UX5B-L<n>: ..."; push)
  L2 Xếp CLB: một đường đi nạp -> kiểm -> chạy, MỘT nút vàng (D1), <= 7 ô trước khi gập, dòng trạng thái, tuỳ chọn
     gập dưới "Tuỳ chọn khi chạy".
  L3 Nhập nguyện vọng + Nhập điểm: ba bước thành ba mục gập, chỉ mục đang mở có nút vàng (D2); D3 (giáo viên không thấy
     mục điểm quyết tâm); D4 (btnScoringQuayLai); D5 (test coi lưới thẻ là một nhóm); D6; "Chấm tiếp" vàng.
  L4 Giao diện giáo viên + test: Hick budget và Von Restorff cho từng thẻ, quản trị và giáo viên (đếm riêng); test từ cấm;
     test "cùng payload" (ba lần Lưu vẫn gọi đúng API với đúng tham số như trước). MILESTONE 2.
  Mỗi lô tối đa 2 vòng sửa của chính bạn; lô nào không qua thì git revert lô đó, ghi "Needs Truong", làm tiếp lô sau nếu độc lập.

TỰ KIỂM (UX5_GIAO_THUC.md §3, Truong đã cho phép gọi phiên con cho UX5; dùng create_session, KHÔNG dùng Agent tool)
  Sau L4: get_session lấy session_id của bạn; push; create_session (source_url = repo này, source_revision =
  claude/affectionate-lamport-595imn, outcome_branch = cùng nhánh, model = sonnet, title "UX5B checker") với prompt §4 của
  UX5_GIAO_THUC.md (X = b), điền <base> <head> <coder_session_id>; ghi session_id checker vào hồ sơ nhánh; KẾT THÚC lượt.
  Nhận PASS thì sang bước KẾT. Nhận FIX thì sửa đúng các mục đó, commit "UX5B-FIX<round>: ...", push, send_message cho
  CHÍNH checker đó ("ROUND <n>: re-check <base>..<head>"). Tối đa 4 vòng FIX; sau vòng 4 vẫn FIX thì revert lô sai,
  ghi "Needs Truong" và DỪNG.

VÒNG LẶP CI (sau mỗi lần push mà bạn cần kết quả; một push mới HUỶ lượt CI đang chạy, nên gom sửa rồi mới push)
  actions_list lấy run mới nhất của nhánh; đang chạy thì ScheduleWakeup 600-900 giây (đừng poll dày). Đỏ: list_workflow_jobs,
  get_job_logs từng job đỏ (return_content=true, tail_lines 80-100), nhóm lỗi theo NGUYÊN NHÂN GỐC, tái hiện cục bộ chỉ với
  file test liên quan, sửa, ruff + kiem_nhanh.py 7/7, CHANGELOG, push. Tối đa 6 vòng CI cho cả phiên; hết thì DỪNG và báo.

KẾT (khi checker PASS và CI xanh trên commit cuối)
  Chạy skill soat-ma MỘT lần trước push cuối (kiem_nhanh.py + bốn tầng, chỉ báo cáo). Cập nhật hồ sơ nhánh (Current state,
  nhật ký phiên), TIEN_DO, CHANGELOG. Chạy lại P0(c): `git rev-list --left-right --count HEAD...origin/main` phải ra "N 0"
  (main có thể đã đi tiếp; nếu có xung đột mới thì giải rồi CI xanh lại). Báo Truong: đường dẫn run xanh, 3 ảnh admin + 2 ảnh
  giáo viên của checker, số ô trước/sau mỗi thẻ, các mục "Needs Truong" (nếu có). Gõ DONE. KHÔNG tạo PR, KHÔNG merge vào main
  khi Truong chưa nói rõ.

DỪNG VÀ HỎI TRUONG (chỉ các trường hợp này): thiết kế đòi đổi backend/API/schema; mâu thuẫn với một bất biến trong CLAUDE.md;
cần đổi CHỮ đã duyệt; cần thư viện mới; hết 6 vòng CI hoặc 4 vòng FIX; sắp chạm giới hạn dùng (cập nhật "Current state" trong hồ sơ nhánh rồi dừng, sẽ nối lại từ hồ sơ).

QUY TẮC CỨNG: không bỏ qua/xoá/nới test để qua CI; không push commit rỗng, không viết lại lịch sử, không force-push; không chạy
cả bộ test cục bộ (22 phút, CI chạy); không git stash khi đang merge; số liệu đo là dữ liệu MÔ PHỎNG; không viết phần nhận xét
hay kết luận của báo cáo dự án (chỉ tài liệu vận hành, mã, test).

MÔI TRƯỜNG TEST (container đám mây): python3.11 -m venv ngoài thư mục dự án hoặc .venv (không commit), pip install -r
requirements-dev.txt; Playwright Python cần Chromium 1255 còn container có 1243 trong /opt/pw-browsers: tạo thư mục có symlink
chromium-1255 và chromium_headless_shell-1255 trỏ tới hai thư mục 1243, thêm ffmpeg-1011, đặt PLAYWRIGHT_BROWSERS_PATH tới đó;
không chạy `playwright install`. Chạy: python -m pytest -q -p no:cacheprovider -n 4 --no-cov --tb=line <file> 2>&1 | tail -15
```
