# UX1 — Đánh giá bản tích hợp A + XP1 + B từ góc người dùng (lead, 2026-11-19)

> Tài liệu vận hành, không phải nội dung báo cáo KHKT. Dữ liệu **MÔ PHỎNG**: `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`
> và `SO_NHAP_FA_MAU_120HS.xlsx` (bật FA), chia 3 lớp 10A1–10A3, hạt giống 42. Chromium thật qua `browser_host`,
> khung 1366×900, nhánh `claude/ux1-tich-hop` sau I3 fix1 (`b2f7f8b`). Kịch bản: `docs/ke_hoach/ux/chup_tich_hop.py`
> (cần `pypdf`). Ảnh: `docs/ke_hoach/ux/anh/danh_gia_tich_hop/`. Không có lỗi JavaScript trong cả lượt thử.

## 1. Mục tiêu §1 của `UX1_KE_HOACH.md`

| Việc | Trước | Mục tiêu | Đo được | Kết quả |
|---|---|---|---|---|
| Quản trị: nạp sổ → chạy → tải kết quả | 5 | 4 | **4** (chọn tệp, Nhập sổ, Chạy sắp xếp, Xuất kết quả trên thanh "Việc tiếp theo") | Đạt |
| Quản trị: xử lý em chưa có CLB | 4–6 | 2 | **1** trên thanh (đo của A, I1 không đổi luồng này) | Đạt |
| Phiếu PDF một em | ~8 | 4 | **3** bấm + gõ mã: thẻ Kết quả, chọn em, "Lưu PDF" → tệp PDF lưu thẳng | Đạt (chỉ quản trị, xem §3.3) |
| GV chủ nhiệm: kết quả lớp mình | 3 | 2 | **1** (mở app là ở Kết quả; chọn lớp) | Đạt |
| GV/BGH: báo cáo tổng hợp | không có | 1 | **1** (HTML hoặc PDF, 1 trang) | Đạt |
| GV chủ nhiệm: phiếu cả lớp | — | ≤ 2 | **2** (chọn lớp, "In phiếu cả lớp") → một PDF | Đạt |
| Học sinh tự tra cứu | 2 | 2 | **2** (không đổi; test `test_giao_dien_gt4_man_hoc_sinh.py`) | Đạt |

## 2. Điều đã tốt
- Một menu "Xuất…" duy nhất cho quản trị: CSV, biên bản bốc thăm và ba mục PDF nằm cùng chỗ; giáo viên không thấy menu.
- Phiếu PDF đủ ý cho phụ huynh đọc: tóm tắt "Em có 2/2 buổi…", bảng từng buổi có **Loại CLB rồi Huy chương**, câu
  "Vì sao" cho mọi dòng, bảng "Điểm các CLB em đã thi", hộp "Em nên làm gì tiếp" và dòng khiếu nại (ảnh 5, 6).
- Báo cáo tổng hợp PDF đúng 1 trang, chỉ số gộp (lấp đầy, mức hài lòng, chưa có CLB theo lớp); cột "Buổi" hiện
  "Thứ 2/4/6", không còn mã nội bộ (ảnh 7).
- Danh sách thành viên theo CLB: không có điểm hay số bốc thăm; có thêm tệp `_chua_duoc_xep.pdf` cho em chưa có chỗ (ảnh 8).

## 3. Năm vấn đề lớn nhất khi dùng (theo mức ảnh hưởng)
1. **Phiếu một em tràn sang trang 2 gần trắng** (ảnh 6: trang 2 chỉ còn "Em nên làm gì tiếp" và "Khiếu nại"). Phiếu cả
   lớp 10A2 (40 em) ra **75 trang**, bản FA 78 trang: gần gấp đôi giấy in. Nên thu gọn để phần lớn phiếu vừa 1 trang
   (bảng "Điểm các CLB em đã thi" gộp vào bảng chính, lề và cỡ chữ nhỏ hơn một chút).
2. **Tiêu đề cột bị ngắt giữa chữ**: "Huy ch / ương", "Nguyện / vọng", "Chỗ đã nhận / tối đa" ba dòng (ảnh 5). Cột
   "Vì sao" hẹp nên câu giải thích thành 4–5 dòng. Nên nới cột "Vì sao", rút tiêu đề ("Huy chương" → không ngắt;
   "Chỗ" thay "Chỗ đã nhận / tối đa").
3. **Giáo viên không lưu được PDF của MỘT em** (`#btnGtPdfMot` chỉ quản trị), trong khi "In phiếu cả lớp" (PDF chứa
   chính em đó) lại được phép. Giáo viên muốn in lại phiếu cho một em phải in cả lớp hoặc dùng bản HTML rồi In → Lưu PDF.
   Nên cho `giao_vien` dùng "Lưu PDF" một em (cùng phạm vi quyền như phiếu cả lớp).
4. **Trang giáo viên vẫn có hai ô "Chọn lớp"** (khối "Theo lớp và báo cáo" và bảng "Theo lớp" ngay dưới, ảnh 4) — vấn đề
   số 2 của `UX1_DANH_GIA_B.md` chưa được xử lý. Hai ô đồng bộ một chiều; người dùng vẫn phải đoán dùng ô nào.
5. **Giáo viên không bị giới hạn theo lớp** (mô hình 2 vai): bất kỳ giáo viên nào cũng in được phiếu (kèm mã tra cứu)
   của mọi lớp. Không phải lỗi mới (bản HTML đã vậy) nhưng giờ in hàng loạt dễ hơn; ghi ở "Needs Truong" mục 4.

## 4. Ghi chú nhỏ
- Bình luận HTML cũ ở `index.html` (khối `#ux1bPanel`: "Không có nút in phiếu cả lớp: XP1 nối ở bước tích hợp") đã
  sai sau I3.
- Sổ FA nạp với cấu hình mặc định (FA tắt) thì "Chạy" báo lỗi `wharton_*` cho cả 120 em: đúng luật cũ, nhưng người dùng
  không biết phải bật FA ở Cài đặt; thông báo nên gợi ý chỗ bật.
- Từ checker I1: mức cảnh báo `health_oversubscribed*` đã từ "thông tin" lên "trung bình"; đổi loại CLB sau khi xếp
  không đánh dấu kết quả là cũ (có từ trước).

## 5. Khuyến nghị theo thứ tự
1. Thu gọn phiếu PDF về 1 trang/em trong đa số trường hợp và sửa tiêu đề cột bị ngắt (vấn đề 1, 2) — một mục nhỏ mới.
2. Cho giáo viên "Lưu PDF" một em (vấn đề 3); đổi quyền ở `phan_quyen.py` + `data-quyen` của nút, có test.
3. Gộp hai ô "Chọn lớp" thành một (vấn đề 4).
4. Truong quyết định có cần giới hạn giáo viên theo lớp không (vấn đề 5; nếu có thì là mục mới, đụng mô hình vai).
5. Thêm `pypdf` vào `requirements-dev.txt` để CI không bỏ qua các test đọc chữ trong PDF ("Needs Truong" mục 5).

## UX1F — đo lại sau sửa (lead, 2026-11-20, nhánh `claude/ux1-sua-pdf`, dữ liệu MÔ PHỎNG)
Chạy lại `chup_tich_hop.py` (120 HS, 3 lớp, seed 42) và các test UX1F; không lỗi JavaScript.
| Điểm | Trước | Sau |
|---|---|---|
| pypdf trong test | bỏ qua (skip) | chạy thật: 4 tệp, 70 test qua, 0 skip (cả Windows CI) |
| Phiếu 1 em | tràn trang 2 gần trống, "Huy ch/ương" | HS004: 1 trang; tiêu đề cột không ngắt giữa từ |
| Phiếu cả lớp | 40 HS (FA, seed 3): 74 trang; 800 HS: 1519 | 40 trang; 800 HS: 1278; không trang < 200 ký tự |
| Phiếu cả lớp (kịch bản 120 HS) | — | DQT 48 trang, FA 41 trang |
| Giáo viên "Lưu PDF" 1 em | không có nút | 3 bấm (tìm → chọn → Lưu PDF); PDF chỉ chứa em đó; vai học sinh bị từ chối |
| Ô "Chọn lớp" trên Kết quả | 2 ô (`#ux1bLop`, `#kqChonLop`) | 1 ô `#kqChonLop` cho quản trị và giáo viên |
Còn lại (nhỏ): "Xuất theo lớp" và "Báo cáo tổng hợp" vẫn cho toàn trường (backend không nhận lớp), nằm cạnh ô
chọn lớp nhưng không dùng nó; nút "Lưu PDF" chỉ hiện sau khi chọn em; phiếu có buổi cực dài (10 NV × ~600 ký tự)
có thể để trang 1 chỉ còn tiêu đề.
