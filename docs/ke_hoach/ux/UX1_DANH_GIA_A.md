# UX1 — Đánh giá nhóm A từ góc người dùng (lead, 2026-11-19)

> Tài liệu vận hành, không phải nội dung báo cáo KHKT. Dữ liệu **MÔ PHỎNG**: `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`
> và `SO_NHAP_FA_MAU_120HS.xlsx`, hạt giống 42. Chạy bằng Chromium thật qua `browser_host`, khung 1366×800, nhánh
> `claude/ux1-a-giao-dien` (sau L1–L8-A và các lần sửa L2b fix2–fix4). Ảnh: `docs/ke_hoach/ux/anh/danh_gia_a/`.
> Không có lỗi JavaScript trong cả lượt thử.

## 1. Mục tiêu §1 của kế hoạch — đo lại

| Việc | Trước | Mục tiêu | Đo được | Kết quả |
|---|---|---|---|---|
| Quản trị: nạp sổ → chạy → tải kết quả | 5 | 4 | **4** (chọn tệp, Nhập sổ, Chạy trên thanh, Xuất kết quả trên thanh) — đúng cả khi còn 32 em chưa có chỗ | Đạt |
| Quản trị: xử lý em chưa có CLB | 4–6 | 2 | **1** lần bấm sau khi chạy (nút "Xử lý 32 học sinh…" mở danh sách) | Đạt |
| GV chủ nhiệm: kết quả lớp mình | 3 | 2 | **0** để tới trang Kết quả (mở app là ở đó) + 1–2 để chọn lớp | Đạt |
| Học sinh tự tra cứu | 2 | 2 | **2** (không đổi) | Đạt |
| Phiếu PDF một em | ~8 | 4 | — nhóm B (L6), đo sau tích hợp | Chưa đo |
| Ban giám hiệu: báo cáo tổng hợp | không có | 1 | — nhóm B (L4-B), đo sau tích hợp | Chưa đo |

## 2. Điều đã tốt khi dùng thử
- Thanh "Việc tiếp theo" luôn nói đúng trạng thái và một việc chính; sau khi chạy có thêm nút phụ "Xuất kết quả" (ảnh 1).
- Điều hướng 4 nhóm dễ đọc; giáo viên chỉ thấy "Nhập tay" và "Kết quả & phiếu", mở app là vào Kết quả.
- Sổ có huy chương nạp ở chế độ mặc định: lời nhắc rõ + nút "Bật chế độ huy chương"; bấm xong nhập, chạy được ngay.
- Trang Cài đặt một câu hỏi, ba thẻ, bấm là lưu, có Hoàn tác; giá trị 60·30·10 hiện ngay trên thẻ.
- Hai lỗi lead thấy ở lượt thử đầu đã sửa (L2b fix2): khung "sửa tại chỗ" từng báo "Sẵn sàng" khi lần chạy vẫn bị chặn;
  "Mở vòng 2 cho 0 học sinh…" từng hiện khi không còn em nào thiếu chỗ.

## 3. Năm vấn đề còn thấy khi dùng (xếp theo mức ảnh hưởng)
1. **Bật Huy chương trên sổ điểm quyết tâm → 678 dòng "Nghiêm trọng" từng em một, ghi mã CLB thô** (`clb_bcs`, `clb_lamvuon`)
   (ảnh 3). Thanh "Việc tiếp theo" nói "Xem cảnh báo" và đưa tới danh sách này, không đưa về khung Cài đặt nơi đã có câu
   giải thích một dòng "120 học sinh … hãy nạp lại sổ có cột Huy chương" (ảnh 2). Người dùng dễ hoảng và không thấy lối
   quay lại "Chia 100 điểm".
2. **Khung "sửa tại chỗ" liệt kê 9 CLB × 3 nút loại** ngay cả khi vấn đề chính là dữ liệu huy chương sai cả sổ (ảnh 2):
   người dùng có thể đặt loại cho 9 CLB rồi vẫn không chạy được. Câu "nạp lại sổ" đứng trên nhưng không có nút làm việc đó.
3. **"Nhận khiếu nại trong [3] ngày"**: nút, ô số và chữ "ngày" lệch hàng, nút đọc như câu cụt (ảnh 4). Các nút "Sau khi
   xếp" không nói bấm xong thì điều gì xảy ra với học sinh.
4. **Khung tra cứu ở đầu Kết quả vẫn nặng**: dải 4 bước + 3 nút (Tạo mã, Xuất mã, Chế độ học sinh) đứng trước ô tìm (ảnh 5);
   giáo viên chỉ muốn gõ tên. Ô tìm nhỏ, cùng chữ gợi ý với ô lọc bảng ngay dưới → dễ gõ nhầm ô.
5. **Nhãn nhóm và tiêu đề trang không khớp**: nhóm "Cài đặt" mở trang tên "Quản lý"; thẻ Huy chương nằm giữa trang CLB.
   Ngoài ra dòng đỏ "Tệp xuất có điểm chấm và số bốc thăm…" luôn hiện ở khung Xuất, kể cả khi người dùng chưa bấm gì.

## 4. Đề xuất, theo thứ tự ưu tiên
1. Khi chế độ Huy chương bị chặn vì dữ liệu: gộp các cảnh báo `fa_huy_chuong_*` thành một dòng có số em, dùng tên CLB thay
   mã; thanh "Việc tiếp theo" trỏ tới khung Cài đặt; thêm nút "Quay lại Chia 100 điểm" cạnh câu "nạp lại sổ".
2. Khung sửa tại chỗ: khi cả sổ sai huy chương, chỉ hiện câu "nạp lại sổ" + nút "Tải sổ mẫu có huy chương"; ẩn các nút loại
   CLB cho tới khi dữ liệu học sinh hợp lệ.
3. Viết lại các hành động "Sau khi xếp" thành câu đầy đủ + một dòng hệ quả (ví dụ "Nhận khiếu nại 3 ngày — học sinh gửi qua
   mã tra cứu"); canh hàng ô số.
4. Thu gọn khung tra cứu: ô tìm to ở đầu, các nút mã tra cứu gập vào "Mã tra cứu…".
5. Đồng bộ tên nhóm/trang ("Cài đặt" ↔ "Quản lý"); chỉ hiện dòng đỏ quyền riêng tư khi mở "Tuỳ chọn khác".

## 5. Việc còn lại (không thuộc nhóm A)
- Phiếu PDF và báo cáo tổng hợp: đo ở `UX1_DANH_GIA_TICH_HOP.md` sau khi gộp nhánh nhóm B.
- Poster PDF/PPTX chưa dựng lại (cần python-pptx, matplotlib) — mục "Needs Truong" trong tệp nhánh.
