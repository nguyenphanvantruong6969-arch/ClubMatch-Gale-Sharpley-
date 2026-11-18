# UX1a — Rà soát thao tác người dùng (2026-11-18)

> Mục **UX1 — Giao diện trực tiếp, ít bước** (Truong duyệt mở mục ngày 2026-11-18; ngoài sổ 33 mục).
> Dữ liệu dùng để rà: `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`, hạt giống 42 — **dữ liệu MÔ PHỎNG**.
> Ảnh chụp bằng Chromium thật (`browser_host`), khung 1366×800: `docs/ke_hoach/ux/anh/`.
> Chụp lại: `python docs/ke_hoach/ux/chup_luong_chinh.py`, `python docs/ke_hoach/ux/chup_phieu.py` (cần playwright).
> Chụp trên nhánh đã gộp GT4 (merge efce9d1): GT4 đã thêm liên kết "Tra cứu một học sinh ↓" đầu thẻ Kết quả, nút "Mở tệp" sau khi xuất phiếu, và chữ "Chỗ dành riêng" trên phiếu.
> Tài liệu vận hành, không phải nội dung báo cáo KHKT.

## 1. Hiện trạng đo được

| Thẻ | Điều khiển hiện ra (nút/ô/chọn) | Chiều cao trang (px) | Ghi chú |
|---|---|---|---|
| Xếp CLB | 9 | 1 450 | Luồng chính tốt: chọn tệp → **Nhập sổ** → **Chạy sắp xếp** = 3 lần bấm |
| Kết quả | 14 | **4 807** | Bảng 120 dòng; ô **Tra cứu một học sinh** vẫn ở cuối trang (GT4 thêm liên kết nhảy xuống ở đầu) |
| Chi tiết và xuất tệp | 24 | 1 166 | 7 mục gập; nút xuất chính ở đây, không ở thẻ Kết quả |
| Nhập nguyện vọng | 7 | 1 376 | Danh sách thẻ học sinh, 15 trang |
| Quản lý | 32 | 2 066 | Tiêu chí xếp + Thử cấu hình (nâng cao) đứng TRƯỚC phần sửa CLB |
| Nhập điểm | 4 | 414 | Tách khỏi Nhập nguyện vọng dù cùng là "nhập dữ liệu học sinh" |

Không có lỗi JavaScript trong toàn bộ lượt chụp.

## 2. Số lần bấm cho từng việc (hiện tại → đề xuất)

| Người dùng | Việc | Hiện tại | Đề xuất | Chỗ mất bước |
|---|---|---|---|---|
| GV phụ trách | Nạp sổ → chạy → tải kết quả Excel | 3 + tự tìm thẻ "Chi tiết và xuất tệp" + 1 = **5** | **4** | Sau khi chạy xong không có nút "Bước tiếp theo" |
| GV phụ trách | Xem và xử lý 32 em chưa có CLB | Tự tìm trong 3 thẻ (Kết quả hồng, Chi tiết › mục gập, Mời vào chỗ trống) ≈ **4–6** | **2** | Thẻ đỏ "32 Cần xử lý" không bấm được |
| GV phụ trách | Phiếu PDF cho **một** em | Thẻ Kết quả → "Tra cứu ↓" → gõ → chọn → In phiếu → Mở tệp → Ctrl+P → Lưu PDF ≈ **8** | **4** | Phiếu ghi ra tệp HTML trên đĩa rồi mới in |
| GV chủ nhiệm | Lấy kết quả lớp mình | Chi tiết và xuất tệp → Xuất theo lớp → mở thư mục = **3** | **2–3** | Ổn; chỉ cần đưa lên trang chính |
| Học sinh | Tự tra cứu bằng mã | Mã + Xem = **2** | 2 | Ổn |
| Ban giám hiệu | Một trang tổng hợp để đọc/in | Không có nút riêng; phải ghép thẻ Tóm tắt + Bảng điều khiển (thẻ Quản lý) | **1** | Thiếu "Báo cáo tổng hợp" |

## 3. Vấn đề phát hiện (xếp theo mức ảnh hưởng)

1. **Không có "việc tiếp theo".** Chạy xong, màn hình báo "88/120 có CLB" nhưng không có nút sang Kết quả, Xuất, hay xử lý 32 em (`anh/07_sau_chay.png`).
2. **Tra cứu và in phiếu vẫn ở cuối** thẻ Kết quả dài 4 807 px; liên kết nhảy của GT4 đỡ cuộn nhưng vẫn thêm một bước (`anh/02_co_dl_results.png`).
3. **In phiếu = ghi tệp HTML**, người dùng phải tự mở rồi in thành PDF (`anh/04_phieu.png`).
4. **Hai thẻ cùng nói về kết quả** ("Kết quả" và "Chi tiết và xuất tệp"); nút xuất chính nằm ở thẻ thứ hai.
5. **Cảnh báo ghi nhãn "THÔNG TIN"** nhưng nội dung là "ít nhất 60 em chắc chắn không có CLB" — mức độ bị đánh thấp, câu dài (`anh/07_sau_chay.png`).
6. **Một thông báo lặp 3 lần** sau khi nhập ("Xong: 9 CLB, 120 học sinh…": khung tệp, dòng dưới, toast).
7. **Từ nội bộ lọt ra màn hình/phiếu**: "số khoá bốc thăm: 42" (i18n `gt_lan_chay`), cột "Mức vào được = Bốc thăm", "Điểm thử thách". GT4 đã đổi một phần sang "Chỗ dành riêng" + chú thích.
8. **Phiếu thiếu dòng tóm tắt đầu trang** (em được mấy buổi, CLB nào) và **thiếu "việc em nên làm tiếp"** khi trượt hết (HS004 trượt cả 3 buổi, phiếu chỉ nói "liên hệ giáo viên").
9. **Thẻ Quản lý đặt phần nâng cao lên trước** (Tiêu chí xếp, Thử cấu hình) — người mới dễ đổi nhầm.
10. **Tên cột không thống nhất** giữa màn hình ("Điểm của học sinh") và phiếu ("Điểm của em").

## 4. Đề xuất (đã thống nhất với Truong: cả 4 nhóm người dùng; PDF qua In → Lưu PDF)

### UX1b — Gọn giao diện
- **Thanh "Việc tiếp theo"** trên đầu mọi thẻ quản trị: một nút chính đổi theo trạng thái (Nạp sổ → Chạy → Xem kết quả → Xử lý n em chưa có CLB → Xuất). Thẻ "Cần xử lý" bấm được.
- **Gộp điều hướng 6 → 4 thẻ**: *1. Dữ liệu* (nhập sổ, nhập nguyện vọng, nhập điểm), *2. Xếp*, *3. Kết quả & phiếu* (bảng + tra cứu ở ĐẦU trang + mọi nút xuất trong một menu "Xuất…"), *Cài đặt* (CLB, tiêu chí, thử cấu hình ở mục "Nâng cao" gập sẵn).
- **Lối vào theo vai**: GV chủ nhiệm và Ban giám hiệu có một trang chỉ đọc gồm 1–2 nút (Xuất lớp / Báo cáo tổng hợp).
- Sửa mức cảnh báo (vấn đề 5) và bỏ thông báo lặp (vấn đề 6).
- Ràng buộc: chỉ đổi giao diện; bất biến 1 không bị chạm; test Chromium `tests/test_giao_dien_*` phải sửa theo bố cục mới, không được bỏ test.

### UX1c — Phiếu học sinh in ra PDF
- Nút **"In / Lưu PDF"** mở thẳng hộp thoại in trên phiếu (không ghi tệp HTML trung gian); vẫn giữ nút xuất tệp cho in hàng loạt theo lớp.
- Thêm vào phiếu: **dòng tóm tắt đầu trang**; **điểm thi mọi CLB em đã thi**; **biểu đồ nhỏ** đặt điểm của em cạnh điểm chuẩn — chỉ với CLB em đã thi, không tên/điểm em khác; **việc nên làm tiếp** (vòng 2, mời vào chỗ trống, khiếu nại) khi em thiếu chỗ.
- Thay từ nội bộ bằng lời thường (vấn đề 7); thống nhất tên cột (vấn đề 10).
- Ràng buộc: không thêm thư viện; giữ quy tắc riêng tư của `phieu_giai_trinh.py` (mỗi trang chỉ dữ liệu của chính em đó).

## 5. Câu hỏi còn mở cho Truong
1. Điểm chuẩn in trên phiếu là con số tổng hợp (không lộ cá nhân). Đồng ý in cho CLB em đã thi?
2. Gộp 6 thẻ thành 4 sẽ đổi tên thẻ trong `HUONG_DAN_SU_DUNG.md`, kịch bản demo/video và poster — chấp nhận cập nhật tài liệu cùng lúc?
