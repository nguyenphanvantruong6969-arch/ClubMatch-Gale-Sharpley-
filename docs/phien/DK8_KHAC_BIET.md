# DK8 — khác biệt giữa bản mẫu v8 và cổng thật (dữ liệu MÔ PHỎNG)

> Chụp bằng `du_lieu_test/chup_dk8.py <thư_mục_ra>` (cặp `v8_<màn>.png` / `that_<màn>.png`, không commit PNG).
> Cột «trạng thái»: **còn khác** · **đã giống** · **khác chấp nhận** (kèm lý do). Cập nhật mỗi lô.

| Màn | Khác biệt (v8 → cổng thật trước DK8) | Lô | Trạng thái |
|---|---|---|---|
| landing | v8: tiêu đề «Đăng ký câu lạc bộ» + dòng phụ; cổng thật: một khung trắng chứa 3 nút nhỏ | L1 | đã giống |
| landing | v8: 3 thẻ vai trò lớn (tên, một dòng mục đích, chip trạng thái, dòng đếm); cổng thật: 3 nút | L1 | đã giống |
| landing | chip «Chưa mở» / «Đang mở · còn N ngày» / «Đã đóng» / «Cần mật khẩu»; dòng «N em đã gửi», «N giáo viên đã đăng ký tài khoản» (cần số đếm công khai) | L1 | đã giống |
| landing | v8: nhãn thẻ thứ ba là «Quản lý»; cổng thật giữ «Quản trị» (mọi test và hướng dẫn dùng chữ này) | L1 | khác chấp nhận: giữ nhãn nút để không đổi test/hướng dẫn |
| landing | v8: dải vàng «Bản mẫu», khung «Thông tin để thử», «Đặt lại: Demo/Cả trường» | — | khác chấp nhận: chỉ có trong bản mẫu (ngoài phạm vi DK8) |
| thanh trên | v8: thanh dính `.top` (thương hiệu «Cổng đăng ký CLB» + chip «Giai đoạn k/6 · tên» + vai trò bên phải + «Thoát»); cổng thật: không có | L1 | đã giống |
| thanh trên | v8 «Thoát»; cổng thật giữ «Đăng xuất» (test `test_giao_dien_dkl_hoc_sinh`, `gt4`) | L1 | khác chấp nhận: giữ nhãn nút |
| thanh trên | v8 tên giai đoạn rút gọn («GV đăng ký», «HS đăng ký»); cổng thật dùng tên đầy đủ (đã có ở thanh sáu bước, test dùng) | L1 | khác chấp nhận: tên đầy đủ rõ hơn, test dựa vào |
| thanh trên | «← Mở phần mềm xếp CLB» (chỉ quản trị): v8 không có | L1 | khác chấp nhận: lối về phần mềm xếp là chức năng thật (DK4-L5), chuyển lên thanh trên |
| đăng nhập (ba vai) | v8: thẻ hẹp giữa trang (≤ 480 px), «← Về trang chọn vai trò» phía trên, nút vàng rộng hết thẻ, dòng gợi ý dưới nút | L1 | đã giống |
| đăng nhập | v8 nút «Vào» (quản lý) / «Đăng nhập»; cổng thật giữ «Đăng nhập» cho cả ba (test dùng) | L1 | khác chấp nhận: giữ nhãn nút |
| đăng nhập quản trị | v8 ghi sẵn mật khẩu thử trong dòng gợi ý | — | khác chấp nhận: chỉ có trong bản mẫu |
| viec_0..viec_5 | v8: thẻ trên hết, MỘT thẻ nổi chứa thanh sáu bước + tiêu đề giai đoạn + một dòng giải thích + dòng đếm (mono) + dòng hạn chót; cổng thật: thanh sáu bước nằm NGOÀI trên các thẻ, nội dung xếp lỏng | L2 | đã giống |
| viec_0..viec_5 | v8: thanh thẻ (Việc bây giờ · Danh sách · Cài đặt · Thêm ▾) nằm TRÊN thanh sáu bước; cổng thật: dưới | L2 | đã giống |
| viec_1 | v8: «Gia hạn» (menu +1 giờ / +1 ngày) và «Đóng ngay» ở bên phải dòng hạn chót; cổng thật: «+1 giờ», «+1 ngày», «Đóng ngay» là chữ trần rời rạc | L2 | khác chấp nhận: «+1 giờ», «+1 ngày», «Đóng ngay» hiện sẵn bên phải dòng hạn chót (nhãn «Gia hạn»), không giấu trong menu: quản trị bấm một lần, test và hướng dẫn dùng đúng hai nút này |
| viec_1 | v8: thẻ thứ hai «CLB đã gửi» (bảng CLB · Giáo viên · Buổi · Phòng · Nhận); cổng thật: không có | L2 | đã giống |
| viec_1 | v8: ô dán tên giáo viên không nằm ở «Việc bây giờ» (nằm ở Danh sách → Giáo viên); cổng thật: ô dán + «Tạo tài khoản giáo viên» ở «Việc bây giờ» | L2 | khác chấp nhận: giữ ô dán tên ở «Việc bây giờ», trong thẻ «Tạo hộ tài khoản giáo viên» (giai đoạn này quản trị cần thấy ngay; test dk3_cong / dkl_m_lam_moi dựa vào vị trí) |
| viec_1 | v8: nút vàng «Đóng đăng ký giáo viên» không có (đóng sớm bằng «Đóng ngay»); cổng thật: có nút vàng | L2 | khác chấp nhận: giữ nút vàng «Đóng đăng ký giáo viên» (test dk3_cong, chuyển giai đoạn); đặt trong thẻ giai đoạn |
| viec_1 | v8: ô «Hạn chót» + «Đặt hạn» không có ở giai đoạn này (hạn đặt lúc mở); cổng thật: có | L2 | khác chấp nhận: ô hạn chót khác gấp trong «Chọn hạn chót khác» (cổng thật đặt hạn sau khi mở, không có ô khi mở) |
| viec_0 | v8: danh sách kiểm (✓ tròn) «N phòng · tổng sức chứa», «N học sinh · N lớp · đã có PIN», «Mã trường» + «Sửa»; hạn chót + «Mở đăng ký giáo viên» | L2 | đã giống (danh sách kiểm 3 mục có «Sửa»); khác chấp nhận: không có ô «Hạn chót» khi mở (hạn đặt sau khi mở); phòng và danh sách học sinh nằm ở hai thẻ bên dưới (giai đoạn Chuẩn bị cần nhập ngay), «Sửa» cuộn tới thẻ đó |
| viec_2 | v8: bảng duyệt trong thẻ, ghi chú; nút «Mở cho học sinh» cuối | L2 | đã giống (bảng duyệt trong thẻ giai đoạn, đếm «chờ duyệt · đã duyệt · từ chối», nút «Mở cho học sinh» cuối thẻ) |
| viec_3 | v8: tiến độ theo lớp (thanh) + nhu cầu theo CLB (hai thẻ cạnh nhau), «Sửa CLB đã duyệt» gấp | L2 | đã giống (hai thẻ cạnh nhau; «Sửa CLB đã duyệt» gấp trong thẻ riêng) |
| viec_4 | v8: chọn CLB, dán cột, bảng điểm trong thẻ, «Chốt điểm» | L2 | đã giống (thẻ giai đoạn có «Chốt và xếp»; thẻ dưới: dán cột + bảng điểm theo CLB) |
| viec_5 | v8: tiêu đề «Xuất Sổ nhập», đếm, xem trước hai sheet trong thẻ | L2 | đã giống (đếm «N CLB · M học sinh», kết quả xếp và xem trước trong thẻ) |
| ds | v8: Danh sách = thanh chọn (Phòng · Học sinh · Giáo viên) trong một thẻ; cổng thật: ba mục gấp | L2 | khác chấp nhận: giữ ba `<details>` gấp theo khối (DK6-L2, test dùng) nhưng đặt trong thẻ có tiêu đề + dòng đếm |
| cai_dat | v8: các thẻ nhỏ (Buổi · Khối · Mã trường) lưới hai cột; cổng thật: một cột liền | L2 | đã giống (lưới thẻ: Mã trường · Buổi và khối · Giới hạn · Đổi mật khẩu) |
| them | v8: «Thêm ▾» có Nhật ký · Sao lưu · Lùi giai đoạn · Công cụ thử | L2 | đã giống («Thêm ▾»; ba thẻ liền nhau Sao lưu · Lùi giai đoạn · Nhật ký thay cho thanh chọn; không có «Công cụ thử» vì ngoài phạm vi) |
| gv_dang_nhap | v8: thẻ hẹp, chip giai đoạn giáo viên trong tiêu đề, «Chưa có tài khoản? Tạo bằng mã trường» | L1 | đã giống (khung); luồng đăng ký GV giữ nút «Đăng ký tài khoản giáo viên» |
| gv_ds | v8: «CLB của tôi» + chip giai đoạn bên phải; thẻ CLB (tên, dòng buổi · phòng · chỗ · khối · loại, chip trạng thái, Sửa/Xoá); «+ Đăng ký CLB mới» | L3 | đã giống (tiêu đề + chip giai đoạn, thẻ CLB bo góc 10 px với chip trạng thái và dòng «buổi · phòng · nhận · khối · loại»; Sửa/Xoá giữ chữ cũ) |
| gv_form | v8: màn riêng (thẻ hẹp), tiêu đề «Đăng ký CLB mới», ba bước «1. Lịch và phòng …», thứ tự trường như v8, dòng chú thích | L3 | khác chấp nhận: form nằm NGAY dưới danh sách trong thẻ hẹp (không phải màn riêng sau nút «+ Đăng ký CLB mới») và tên CLB vẫn ở bước 3 — test và luồng DKL dựa vào; nhãn, tuỳ chọn «Tự do – nhận mọi em…», «Số học sinh nhận (tối đa N)», dòng tóm tắt đã như v8 |
| hs_dang_nhap | v8: thẻ hẹp, chip giai đoạn học sinh, dòng gợi ý «Máy tự thoát sau 60 giây…» | L1 | đã giống |
| hs_xacnhan | v8: «Đúng là em chứ?», tên lớn, dòng «Lớp · Khối · Mã», hai nút «Đúng là em» / «Không phải em» | L3 | đã giống (thẻ hẹp, tên lớn 1,4rem, «Lớp · Khối · Mã», nút «Đúng là em» vàng + «Không phải em» viền) |
| hs_buoi | v8: hai cột (CLB cho khối · Nguyện vọng) với thẻ CLB đủ chip và chú thích; thanh bước «Buổi k/N · …» | L3 | đã giống (thẻ CLB và hàng nguyện vọng bo góc 10 px); khác chấp nhận: nút +Thêm / ↑ ↓ ✕ cao 44 px (v8 36 px) vì kiosk cảm ứng, test kiểm ≥ 44 px |
| hs_xemlai | v8: «Xem lại và gửi», bảng tóm tắt + «Bài kiểm tra (n)» | L3 | đã giống từ DK4-UI/DKL (bảng tóm tắt + «Bài kiểm tra (n)») |
| hs_dagui | v8: «Đã gửi», «Đã gửi lúc …», tóm tắt, «Xong, thoát», dòng «Máy sẽ tự thoát sau 30 giây» | L3 | đã giống từ DK4-UI/DKL («Đã gửi lúc …», tóm tắt, «Xong, thoát», «Máy sẽ tự thoát sau 30 giây») |
| mọi màn | v8: phông chữ tải từ Google Fonts; cổng thật dùng phông cài sẵn (`assets/fonts`) — cùng họ Be Vietnam Pro / IBM Plex Mono | — | khác chấp nhận: kiosk chạy offline |
| mọi màn | v8: lớp phủ `body::before` an toàn vùng tai thỏ (iOS) | — | khác chấp nhận: kiosk Windows, không cần |

## Ghi chú theo lô
- **L1** (khung): thanh trên dính, thẻ vai trò, thẻ đăng nhập hẹp, số đếm công khai (`dk_trang_thai`: `so_da_gui`, `so_gv`).
- **L2** (quản trị): thanh thẻ trên thẻ giai đoạn, thẻ giai đoạn (stepper, tiêu đề, đếm, hạn), thẻ nội dung từng giai đoạn.
- **L3** (giáo viên + học sinh): phần lớn đã giống từ DK4-UI/DKL; còn lại là khung hẹp, chip giai đoạn, thứ tự trường.
