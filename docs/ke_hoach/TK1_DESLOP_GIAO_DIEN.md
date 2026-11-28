# TK1 — Gỡ "slop" giao diện kiosk: bản soát và hướng nghiên cứu (28/11/2026)

> Phạm vi: chỉ giao diện kiosk (`index.html`, `style.css`, `js/*.js`), KHÔNG đụng backend, thuật toán, CSV, schema.
> Bằng chứng: đo trực tiếp `style.css` + chụp 6 thẻ ở 1366×768 và 1024×700 với bộ 120 HS (seed 42).
> "Slop" ở đây = những dấu hiệu khiến giao diện trông như ghép vội: kích thước đoán mò, nhiều kiểu cho cùng một việc,
> bố cục nhảy khi đổi thẻ, trang trí không mang nghĩa.

## 1. Số đo (hiện trạng)
| Đại lượng | Hiện có | Nên có | Nguồn chuẩn |
|---|---|---|---|
| Cỡ chữ khác nhau | **43** (có 11.5 / 12.5 / 13.5 / 14.5 px) | 6 bậc | Thang chữ module (Bringhurst; Refactoring UI) |
| Chiều cao nút đo được | 24, 26, 28, 34, 36, 37, 38, 40, 44, 53 px | 2 bậc: 36 (gọn) / 44 (mặc định) | Apple HIG 44 pt; WCAG 2.5.8 ≥ 24 px |
| Giá trị padding/margin/gap | **188** | thang 4-pt: 4·8·12·16·24·32·48 | Lưới 8-pt (Material) |
| Bo góc | 6, 10, 999 + 3, 4, 8 px viết tay | 3 token: 6 / 10 / pill | — |
| `box-shadow` khác nhau | 21 | 2 (nổi nhẹ / lớp phủ) | — |
| `transition` khác nhau | 23 | 2 token thời lượng | — |
| Mã màu hex viết tay | 54 (32 token) | chỉ dùng token | — |
| `scrollbar-gutter` | 0 | 1 (`html`) | CLS — web.dev |

## 2. Phát hiện chính (theo mức ảnh hưởng)
1. **Bố cục nhảy ngang khi đổi thẻ (Windows).** Trang cuộn ở `body`; WebView2 trên Windows dùng thanh cuộn
   cổ điển (~17 px). Thẻ ngắn (Nhập điểm) không có thanh cuộn, thẻ dài (Kết quả, ~4 900 px) có → toàn bộ nội dung
   dịch ~17 px mỗi lần bấm. Sửa: `html { scrollbar-gutter: stable; }`. (Cần xác nhận trên máy Windows thật.)
2. **Một hàng công cụ, bốn kiểu nút** (thẻ Kết quả): tab phân đoạn + nút xám + nút viền đen dày 2 px có bóng đèn
   (`.btn-goi-y`) + nút vàng. Cao 36/38/44 px lẫn lộn. Quy tắc: tối đa 1 nút chính (vàng)/vùng, còn lại phụ (xám)
   hoặc liên kết chữ; bỏ biến thể viền đen và icon bóng đèn (dấu hiệu "AI gợi ý" điển hình).
3. **Hai kiểu tab cho cùng một việc**: Kết quả dùng tab phân đoạn (khung trắng), Quản lý dùng tab gạch chân có viền
   vàng trên. Chọn một; tab có `min-width` cố định và giữ chỗ cho chữ đậm để không xô khi chọn hoặc đổi vi↔en.
4. **Hai kiểu ô nhập**: ô tìm "Tra cứu một học sinh" nền xám cao 46 px; ô "Tìm mã hoặc tên" nền trắng viền cao 38 px;
   `select` nền trắng cạnh `input` nền xám ở form "Thêm hoặc sửa CLB". Gộp về một kiểu, cao bằng nút cùng hàng.
5. **Thanh cảnh báo trên cùng lặp ở mọi thẻ**, viền đậm màu mực — to hơn cả tiêu đề trang, nút "Xử lý" mơ hồ.
   Đổi thành dải trạng thái nhẹ, chiều cao cố định; chữ nút nói rõ việc ("Xem 32 em chưa có CLB").
6. **Thẻ KPI viền trái màu** (`.kpi-o.is-nguy` 4 px đỏ) — mẫu "accent bar" rất phổ biến ở giao diện sinh tự động.
   Ý nghĩa đã có ở chữ "⚠ Cần xử lý"; giữ một tín hiệu (chữ + icon), bỏ thanh.
7. **Phần tử mồ côi / khoảng trống thừa**: nút "?" nằm riêng một dòng dưới ô "Chia CLB theo loại"; thẻ "1. Nhập sổ"
   có đệm dưới gần gấp đôi nội dung. Đưa "?" vào cùng dòng nhãn; đệm thẻ theo token.
8. **Native `select` lẫn nút thả xuống tự vẽ** ("Thêm tuỳ chọn ▾", "Báo cáo và phiếu in ▾", "Theo buổi"): cùng
   hàng nhưng khác mũi tên, khác viền. Một kiểu mũi tên, một kiểu viền.
9. **Nút "Tài khoản" ở chân thanh bên**: khối trắng lớn, sáng nhất màn hình, cho việc ít dùng nhất. Hạ xuống kiểu phụ.

## 3. Điều đã tốt — giữ nguyên
Bảng màu ít, trung tính, có token và bản tối; font Be Vietnam Pro đóng gói offline; `tabular-nums` cho số;
`:focus-visible` (38 chỗ) và `prefers-reduced-motion` (24 chỗ); thanh bên đánh số theo luồng việc 1→2→3.

## 4. Nguyên tắc "tự nhiên, ổn định" áp dụng
- **Ổn định không gian**: cùng loại phần tử → cùng kích thước ở mọi thẻ; không gì đổi kích thước khi hover/chọn/đổi ngôn ngữ;
  chỗ cho nội dung động (thanh cảnh báo, thông báo lỗi) được giữ sẵn.
- **Ít biến thể, nhiều nhất quán** (Nielsen heuristic #4 "Consistency and standards").
- **Thứ bậc bằng khoảng cách và độ đậm, không bằng khung và màu** (Refactoring UI, Wathan & Schoger).
- **Trang trí phải mang nghĩa**: icon, viền màu, bóng chỉ dùng khi truyền thông tin không có ở chỗ khác.
- **Lời nói như người**: nhãn nút = động từ + đối tượng cụ thể.

## 5. Đề xuất triển khai (4 lô, chỉ giao diện)
| Lô | Nội dung | Bắt buộc? |
|---|---|---|
| L1 | Token: thang chữ 6 bậc, thang khoảng cách, chiều cao điều khiển 36/44, bo góc, bóng, thời lượng; `scrollbar-gutter` | Bắt buộc |
| L2 | Nút + ô nhập + select + dropdown: một hệ, cùng chiều cao theo hàng; bỏ `.btn-goi-y` viền đen/bóng đèn | Bắt buộc |
| L3 | Tab: một thành phần, `min-width`, giữ chỗ chữ đậm; thanh cảnh báo chiều cao cố định, chữ nút rõ | Bắt buộc |
| L4 | Dọn chi tiết: KPI bỏ viền trái, "?" mồ côi, đệm thẻ, nút Tài khoản | Tuỳ chọn |
Kiểm nhận: test Chromium đo (a) mọi nút trong một hàng cùng cao, (b) tọa độ trái của `h1` bằng nhau ở mọi thẻ,
(c) bề rộng tab không đổi khi chọn và khi đổi vi↔en, (d) số cỡ chữ khác nhau trong `style.css` ≤ 8.
