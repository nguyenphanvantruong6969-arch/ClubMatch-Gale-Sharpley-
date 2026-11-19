# UX1 — Đánh giá nhóm B từ góc người dùng (lead, 2026-11-19)

> Tài liệu vận hành, không phải nội dung báo cáo KHKT. Dữ liệu **MÔ PHỎNG**: `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`
> (chia 3 lớp 10A1–10A3) và `SO_NHAP_FA_MAU_120HS.xlsx` (chế độ huy chương), hạt giống 42. Chromium thật qua
> `browser_host`, khung 1366×900, nhánh `claude/ux1-b-phieu` sau L4-B, L7, L5c, L8-B và lượt sửa R1.
> Ảnh: `docs/ke_hoach/ux/anh/danh_gia_b/`. Không có lỗi JavaScript trong cả lượt thử (quản trị, giáo viên, học sinh, FA).

## 1. Mục tiêu §1 của kế hoạch — phần nhóm B

| Việc | Trước | Mục tiêu | Đo được | Kết quả |
|---|---|---|---|---|
| Phiếu PDF cho một em | ~8 | 4 | **5**: gõ mã + chọn (2), "In phiếu cho học sinh này" (1) ra tệp HTML, "Mở tệp" (1), In → Lưu PDF (1) | Chưa đạt — cần nút PDF của XP1 (lô I3) |
| Ban giám hiệu / GV: báo cáo tổng hợp | không có | 1 | **1** (tài khoản `giao_vien` mở app là ở trang Kết quả; bấm "Báo cáo tổng hợp") | Đạt (HTML; PDF ở I3) |
| GV chủ nhiệm: "Xuất theo lớp" | — | ≤ 2 | **1** (ra 3 tệp, một tệp mỗi lớp) | Đạt |
| Học sinh tự tra cứu | 2 | 2 | **2**; thẻ học sinh không còn số khoá bốc thăm, không có chữ "undefined" | Đạt |

## 2. Điều đã tốt khi dùng thử
- Phiếu có dòng tóm tắt ngay dưới tên ("Em có 2/2 buổi: …" hoặc "Em chưa có CLB ở buổi nào."), bảng "Điểm các CLB em đã
  thi" với thanh điểm em so với vạch đỏ, và hộp "Em nên làm gì tiếp" chỉ khi còn buổi chưa có chỗ (ảnh 5).
- Chế độ huy chương: cột "Huy chương" của chính em; dòng bị loại vì huy chương nói một câu rõ ("Em đặt huy chương Bạc; các
  bạn đặt Vàng ở … được xét trước"); cột "Mức vào được" khớp với vạch đỏ và câu "Vì sao" trên mọi dòng (ảnh 4).
- Báo cáo tổng hợp chỉ có số gộp — không có mã, tên, điểm hay số bốc thăm (đã soát bằng máy trên toàn văn bản).
- Màn học sinh tra cứu phủ kín khung hình cả khi cuộn: học sinh không nhìn thấy danh sách lớp phía sau.

## 3. Năm vấn đề lớn nhất khi dùng (theo thứ tự ảnh hưởng)
1. **In phiếu một em vẫn 5 lần bấm và phải rời ứng dụng** (ảnh 1). Nút tạo ra tệp HTML; giáo viên phải tự mở rồi In → Lưu
   PDF. Đây là phần đã chuyển sang XP1, nhưng người dùng sẽ thấy ngay — cần làm I3 trước khi phát hành.
2. **Trang giáo viên có hai ô "Chọn lớp" giống hệt nhau** (khối "Theo lớp và báo cáo" và bảng "Theo lớp" ngay dưới, ảnh 2).
   Người dùng không biết nên dùng ô nào, và hai ô có thể chỉ hai lớp khác nhau cùng lúc.
3. **Báo cáo tổng hợp thiếu tên trường, thời điểm xếp và ý nghĩa các ô** (ảnh 3). In ra giấy không biết của trường nào,
   lần chạy nào. "Đã có câu lạc bộ 88 / Chưa có 32" thực chất là "có ít nhất một buổi / không buổi nào" — với 3 buổi, hiệu
   trưởng dễ hiểu sai. Bảng hài lòng đếm theo lượt (138 lượt cho 120 em) — đúng nhãn nhưng khó so với các ô ở trên.
4. **Phiếu chế độ huy chương còn chỗ khó hiểu** (ảnh 4): CLB Giới hạn mà em lỡ có điểm thi vẫn hiện trong "Điểm các CLB em
   đã thi" kèm thanh không có vạch, dù cách xếp bỏ qua điểm ở CLB đó; các dòng Tự do và "không cần xét" chỉ có "—".
   Chưa có loại CLB và câu chú giải từng loại (thuộc XP1), nên học sinh chưa hiểu vì sao CLB này xét điểm, CLB kia không.
5. **Em không có chỗ ở mọi buổi chỉ nhận một lời khuyên "hỏi giáo viên phụ trách"** (ảnh 5) khi trường chưa bật vòng 2 /
   mời chỗ trống / khiếu nại. Phiếu cũng in "Mã tra cứu" ở cuối — đúng ý GT1, nhưng nên ghi một dòng "dùng mã này để tự
   xem kết quả trên máy của trường" để học sinh biết dùng vào việc gì.

Ngoài phạm vi nhóm B, ghi để nhóm tích hợp biết: ở thẻ "Xếp CLB" khi đã có 120 học sinh, khung "Nhập dữ liệu" vẫn ghi
"Chưa có sổ nhập? Bấm 'Tải sổ nhập mẫu'…".

## 4. Đề xuất, theo thứ tự ưu tiên
1. Lô I3 (tích hợp): nút "In / Lưu PDF" gọi PDF của XP1 ngay trên thẻ tra cứu và "In phiếu cả lớp" ở khối giáo viên;
   đo lại cho đạt 4 lần bấm (một em) và ≤ 2 (cả lớp).
2. Gộp hai ô chọn lớp trên trang giáo viên thành một (giữ `#ux1bLop` hoặc ô của bảng, ô còn lại ẩn với `giao_vien`).
3. Đầu báo cáo tổng hợp: tên trường (từ không gian làm việc), "Lần xếp lúc …", và đổi nhãn ô thành "Có CLB ít nhất một
   buổi" / "Chưa có CLB buổi nào"; thêm một dòng giải thích đơn vị "lượt" ở bảng hài lòng.
4. Phiếu FA: ẩn điểm thi của CLB Giới hạn/Tự do khỏi "Điểm các CLB em đã thi" (hoặc ghi "không dùng điểm"); khi XP1 vào,
   đặt câu chú giải loại CLB cạnh câu chú giải huy chương.
5. Hộp "Em nên làm gì tiếp" thêm một dòng cố định cho em không có chỗ nào (ví dụ "đăng ký lại vào CLB còn chỗ với giáo viên
   phụ trách"), và một dòng hướng dẫn dùng "Mã tra cứu".

## 5. Việc còn lại (không thuộc nhóm B)
- PDF phiếu và báo cáo, cột "Loại CLB": XP1, gộp ở lô I3 (`docs/phien/UX1_GIAO_THUC.md` §10).
- Kiểm tay trên Windows (pywebview/WebView2) cho nút xuất HTML + "Mở tệp": mục "Needs Truong" trong tệp nhánh.
