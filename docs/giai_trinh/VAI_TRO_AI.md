# Vai trò của AI trong đề tài

> **Dữ liệu mô phỏng.** Mọi con số kiểm thử nhắc tới ở đây chạy trên dữ liệu do máy sinh (hạt giống cố định), không phải
> khảo sát học sinh thật. Tài liệu chỉ nêu sự việc; phần nhận xét và kết luận của đề tài do học sinh tự viết.

Tài liệu trả lời hai câu hỏi: **phần mềm có dùng AI để quyết định kết quả không**, và **AI đã giúp ở khâu nào của việc
làm ra phần mềm**.

## 1. Phần mềm khi chạy: không có mô hình AI hay học máy

- Phần mềm không chứa, không tải và không gọi mô hình học máy hay dịch vụ AI nào. Danh sách thư viện chạy nằm ở
  `requirements.txt`: `pywebview` (cửa sổ), `openpyxl` (đọc tệp Excel). Hai thư viện kèm theo chỉ dùng trên Windows. Không có
  thư viện học máy nào.
- Việc xếp học sinh vào câu lạc bộ là một **thuật toán xác định**: xét theo học sinh đề xuất (Deferred Acceptance), có
  suất dự trữ mềm, và một lần bốc thăm duy nhất để phá hoà. Mô tả từng lớp, kèm tên hàm trong mã: `docs/CO_CHE_THUAT_TOAN.md`.
- **Cùng dữ liệu vào và cùng hạt giống thì cùng kết quả ra.** Số bốc thăm được khoá sau lần chạy đầu và sinh bằng `crc32`
  (không dùng `hash()`), nên chạy lại cho đúng các số cũ.
- Kiểm tra bằng lệnh có sẵn: `python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20`.
  Lệnh so từng dòng bảng `match_results` và số bốc thăm của 3 bộ dữ liệu × 20 hạt giống với nhánh so sánh, rồi báo "trùng
  khít" hoặc không. Bộ ba dữ liệu và cách dựng: `du_lieu_test/README.md`.
- Thứ hạng nguyện vọng và kết cục của buổi trước **không** đi vào khoá ưu tiên của câu lạc bộ. Chi tiết ở
  `DU_LIEU_DAU_VAO.md`, mục 5.
- Các chức năng của tài khoản, nhật ký thao tác, tra cứu và xuất tệp chỉ đọc và ghi dữ liệu; chúng không đổi thứ tự ưu
  tiên.

## 2. Trong lúc làm phần mềm: AI giúp ở đâu

Nguồn duy nhất là nhật ký có sẵn trong kho mã; không lấy từ lịch sử trò chuyện.

| Tệp | Nội dung |
|---|---|
| `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md` | Bản đọc nhanh: bảng tác giả, tóm tắt, dòng thời gian, 10 giai đoạn |
| `docs/nhat_ky_ai/NHAT_KY_AI.md` | Bản chi tiết: từng phiên, từng lần lưu mã, lời của Truong lưu nguyên văn (mục 1) |
| `docs/nhat_ky_ai/NHAT_KY_AI_DAY_DU.md` | Bản đầy đủ nhất, dành cho người cần tra cứu |
| `CHANGELOG.md` | Từng thay đổi: mã mục, tệp đã sửa, test mới |

Theo `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md`, mục 2:

- **Phần do học sinh tự viết** (bản gốc đưa lên ngày 26/08/2026): thuật toán xếp chỗ cốt lõi, phần nối giữa giao diện và
  thuật toán, giao diện ban đầu và tệp đóng gói chương trình.
- **Phần do công cụ AI làm** (Claude Code, theo yêu cầu và dưới sự duyệt của Truong): tìm và sửa lỗi, viết bộ kiểm thử
  tự động, thêm tính năng (không gian làm việc nhiều ngành, điểm quyết tâm, lớp của học sinh, cơ chế FA-DAA, tài khoản và
  nhật ký thao tác), viết tài liệu hướng dẫn và báo cáo kiểm tra.
- **Việc Truong đã làm** theo ghi chép trong nhật ký: đặt yêu cầu và mục tiêu, viết bản tầm nhìn cho cơ chế mới
  (`docs/ke_hoach/FA_DAA_VISION.md`), duyệt từng kế hoạch, chọn phương án ở các điểm cần quyết định, cho phép hoặc từ chối
  ngoại lệ với quy tắc, quyết định gộp mã vào bản chính. Những quyết định cụ thể kèm ngày nằm ở mục 4 của
  `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md` và mục 1 của `docs/nhat_ky_ai/NHAT_KY_AI.md`.
- **Việc kiểm tra:** bộ test tự động chạy trên dữ liệu mô phỏng (số ca ghi ở `docs/ke_hoach/CLAUDE_CHI_TIET.md`, dòng
  `tests/`), kiểm "trùng khít" nói ở mục 1, và các biên bản soát mã trong `docs/ke_hoach/`.

## 3. Quy ước đang áp dụng với AI trong kho mã

Ghi trong `CLAUDE.md`, mục *Academic integrity*:

- Mọi số liệu kiểm chứng là số mô phỏng; không trình bày như khảo sát thật.
- Phần nhận xét, diễn giải và kết luận trong báo cáo đề tài do học sinh tự viết; AI không soạn.
- Mỗi lần AI giúp đáng kể đều ghi vào nhật ký AI của đề tài.

## 4. Chưa có trong tài liệu này

Nhận xét về mức độ đóng góp, so sánh phần của học sinh với phần của công cụ, và mọi kết luận: do học sinh tự viết.
