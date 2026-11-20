> **Bản tham khảo do AI viết (Claude Sonnet, 20/11/2026), theo yêu cầu của Truong.** Mọi số liệu là **dữ liệu mô phỏng** do máy sinh, không phải khảo sát học sinh thật. Chỗ đánh dấu **[Truong kiểm lại]** là điều AI không biết chắc (cảm nhận, sự việc ở trường, tên trường) — Truong phải sửa cho đúng sự thật trước khi dùng.

# Vai trò của AI trong đề tài (bản tham khảo)

Phần mềm khi chạy **không** chứa mô hình AI hay học máy; việc xếp chỗ là một thuật toán xác định, cùng dữ liệu và cùng seed thì cùng kết quả (nguồn: docs/giai_trinh/VAI_TRO_AI.md, mục 1). Bài này nói về chuyện khác: AI đã giúp gì **trong lúc làm** phần mềm. Nguồn là nhật ký AI trong kho mã, không lấy từ lịch sử trò chuyện (nguồn: docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md).

## 1. Phần nào em làm, phần nào AI làm theo yêu cầu của em?

**Phần em tự viết** (bản gốc đưa lên ngày 26/08/2026): thuật toán xếp chỗ cốt lõi, phần nối giữa giao diện và thuật toán, giao diện ban đầu, và tệp đóng gói chương trình (nguồn: NHAT_KY_AI_DE_DOC.md, mục 2; VAI_TRO_AI.md, mục 2). Dòng trích dẫn Kominers & Sönmez (2016) trong mã là do em viết từ lần lưu đầu ngày 26/08 (nguồn: BAO_VE_RA_SOAT_BAO_CAO.md, mục A6).

**Phần AI làm, theo yêu cầu và dưới sự duyệt của em** (Claude Code: phiên Opus lập kế hoạch, điều phối và kiểm tra lại; phiên Sonnet viết mã theo kế hoạch):

- tìm và sửa lỗi (khoảng 25 lỗi được đánh số; theo thống kê dự án có 10 lỗi "im lặng", tức phần mềm báo thành công trong khi dữ liệu sai), viết bộ kiểm thử tự động;
- thêm tính năng: không gian làm việc nhiều ngành, điểm quyết tâm, lớp của học sinh, cơ chế FA-DAA, giải trình kết quả cho từng học sinh, tài khoản và nhật ký thao tác, xuất PDF, thẻ mục tiêu (kế hoạch và bản đánh giá);
- viết tài liệu hướng dẫn, kế hoạch và báo cáo kiểm tra; chạy mô phỏng và viết memo MT0 về mục tiêu giáo dục (số liệu mô phỏng).

**Phần em làm với vai trò người đặt hướng và quyết định** (theo ghi chép trong nhật ký): đặt yêu cầu và mục tiêu; viết bản tầm nhìn cho cơ chế FA-DAA (08/11/2026); duyệt từng kế hoạch; chọn phương án ở các điểm cần quyết định (ví dụ chọn phương án A cho quỹ điểm quyết tâm ngày 25/10); cho phép hoặc từ chối ngoại lệ với quy tắc (ví dụ 01/11 cho phép phá quy tắc "kết quả giống hệt bản cũ" để bật điểm quyết tâm mặc định; 08/11 cho phép huy chương mặc định lấy theo thứ tự nguyện vọng với điều kiện mọi học sinh đổi được); quyết định gộp mã vào bản chính (nguồn: NHAT_KY_AI_DE_DOC.md, mục 4).

Phần nhận xét, diễn giải và kết luận trong báo cáo đề tài do em viết; bản tham khảo này chỉ là mẫu để em đối chiếu (theo CLAUDE.md, mục Academic integrity, có ngoại lệ do em yêu cầu ngày 20/11/2026).

**[Truong kiểm lại: so sánh mức đóng góp của em với phần AI bằng nhận định của chính em, nêu rõ phần nào em thật sự tự nghĩ và tự quyết, và đối chiếu với bảng phân công thành viên.]**

## 2. Em kiểm tra việc AI làm bằng cách nào?

Theo tài liệu của dự án, việc kiểm tra gồm:

- **Kiểm thử tự động** chạy trên dữ liệu mô phỏng. Theo thống kê mới nhất trong kho, một lần chạy cả bộ trên Linux ngày 19/11/2026 cho 6.977 ca qua, 4 ca bỏ qua (nguồn: CHANGELOG.md, mục "UX1I-I4 fix1"). Mỗi thay đổi bắt đầu từ một test sai (làm test trước, sửa tối thiểu sau).
- **Kiểm "trùng khít" (byte-identical):** với cấu hình mặc định, so từng dòng bảng kết quả và số bốc thăm của 3 bộ dữ liệu × 20 seed với nhánh so sánh (lệnh `kiem_nhanh.py --co-so origin/main --so-seed 20`) (nguồn: VAI_TRO_AI.md, mục 1; CHANGELOG.md).
- **Phiên kiểm tra riêng (checker):** mỗi tính năng có một phiên viết mã và một phiên kiểm tra khác chạy độc lập; phiên điều phối chỉ liệt kê lỗi, không tự sửa (nguồn: NHAT_KY_AI_DE_DOC.md, giai đoạn 9, 13, và quy tắc 12 trong CLAUDE.md).
- **Soát mã trước khi đẩy lên:** kỹ năng `soat-ma` chạy bốn tầng (lõi thuật toán, phần xử lý, giao diện, tài liệu/test) (nguồn: CLAUDE.md, quy tắc 8).
- **CI:** quy trình tự động trên GitHub chạy cả bộ kiểm thử, yêu cầu độ phủ tối thiểu 85% (nguồn: CLAUDE.md, mục Commands).
- **Em quyết định gộp:** chỉ em được quyết định gộp mã vào bản chính (nguồn: NHAT_KY_AI_DE_DOC.md, mục 1).
- **Các giới hạn tự thừa nhận:** có những phần chưa thử trên hệ thống thật (Microsoft thật, máy kiosk thật) và được ghi rõ như vậy (nguồn: NHAT_KY_AI_DE_DOC.md, giai đoạn 8 và 9).

**[Truong kiểm lại: những cách em tự kiểm tay (ví dụ tự chạy thử, tự đọc kết quả, tự so với tính tay) và chưa ghi trong nhật ký. AI không biết.]**

## 3. Một lần AI sai hoặc hiểu sai, em xử lý ra sao?

**Trường hợp 1 — AI hiểu sai yêu cầu "mục tiêu giáo dục" (Giai đoạn 15, 20/11/2026).** Em yêu cầu phát triển phần mềm thành công cụ giúp nhà trường ra quyết định minh bạch, thay đổi theo mục tiêu giáo dục, không chỉ xuất danh sách. AI đã thu hẹp "mục tiêu giáo dục" thành "giữ chỗ cho một nhóm". Em chỉ ra chỗ hiểu sai, và AI sửa lại kế hoạch: từ 6 mẫu cài đặt rút xuống 3 thẻ mục tiêu (Theo năng lực, Cơ hội như nhau, Dành chỗ cho một nhóm), với yêu cầu "đồng bộ, không phức tạp, tối giản thao tác" (nguồn: NHAT_KY_AI_DE_DOC.md, giai đoạn 15; docs/phien/claude__mt1-bo-muc-tieu.md, mục Session log).

**Trường hợp 2 — lỗi "im lặng" được phát hiện ở giai đoạn đầu.** Một ví dụ có ghi: ô điểm biến 8,5 thành 85 (Excel và nhập liệu), và kết quả bốc thăm phụ thuộc thứ tự nhập học sinh; cả hai đều khiến phần mềm vẫn báo thành công trong khi dữ liệu sai. Dự án ghi nhận 25 lỗi đã sửa, trong đó 10 lỗi im lặng, và dùng bài học đó để thêm các bước kiểm dữ liệu khi nhập (nguồn: NHAT_KY_AI_DE_DOC.md, giai đoạn 1; du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md, mục 6). Một ví dụ khác cùng loại: dòng nhật ký "cửa sổ gốc mở THÀNH CÔNG" được ghi **trước** lệnh thật sự mở cửa sổ, nên nó báo thành công kể cả khi ứng dụng treo; tài liệu đã sửa lại khẳng định đó (nguồn: SO_LIEU_DA_KIEM_CHUNG.md, mục 7).

**Trường hợp 3 (cùng loại, ở giao diện) — ước tính lệch xa.** Khi đánh giá thẻ mục tiêu, một ước tính cho 273 em so với kết quả thật 28 em, vì thẻ "Cơ hội như nhau" tắt "Chia 100 điểm" mà người dùng không biết. Lỗi được phát hiện nhờ so ước tính với kết quả xếp thật, rồi sửa (nguồn: MT1_DANH_GIA.md trên nhánh origin/claude/mt1-bo-muc-tieu).

**[Truong kiểm lại: kể bằng lời của em em đã phát hiện sai sót thế nào, đã nói gì với AI, và đã quyết định ra sao. AI chỉ có bản ghi tóm tắt.]**

## 4. Em học được gì?

**[Truong kiểm lại — viết lại bằng trải nghiệm thật của em. Dưới đây chỉ là gợi ý AI đoán từ tài liệu; xoá hoặc thay bằng điều em thật sự rút ra.]**

Làm cùng AI cho em thấy rằng một câu trả lời nghe có vẻ hợp lý vẫn có thể sai. Điều giúp phát hiện sai không phải là tin vào AI hay không tin, mà là có cách kiểm: một bài kiểm thử, một phép so sánh "trùng khít" giữa bản cũ và bản mới, một phiên kiểm tra tách khỏi phiên viết mã. Em cũng thấy mình phải giữ quyền quyết định ở những chỗ có đánh đổi: AI đề xuất, nhưng em chọn có phá một quy tắc hay không (như hai lần cho phép ngoại lệ ghi trong nhật ký) và em chịu trách nhiệm với số liệu em trình bày, nhất là việc luôn ghi rõ đó là dữ liệu mô phỏng. Cuối cùng, em hiểu rõ hơn phần lõi do chính em viết, vì phải giải thích nó để kiểm tra điều AI viết thêm xung quanh nó.

---

*Chi tiết từng giai đoạn và lời nguyên văn của Truong: `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md`, `docs/nhat_ky_ai/NHAT_KY_AI.docx` (cập nhật đến 20/11/2026).*
