# PA15 — Thử với 3 học sinh, rồi dọn dẹp

[← PA14](PA14_phat_hanh_chia_se.md) · Tiếp theo (chỉ khi có thi tuyển): [PA16](PA16_bieu_mau_va_bai_thi.md) · [Mục lục](../00_MUC_LUC.md)

Mọi dữ liệu trong tệp này là **dữ liệu thử**, phải xoá trước khi mở cho cả trường.

## Chuẩn bị

1. Xin 3 tài khoản trường để thử (nhờ bộ phận tin học tạo, hoặc mượn 3 em tình nguyện). Cả 3 phải nằm trong NHÓM HỌC SINH.
2. Mở bảng `HocSinh` trên SharePoint, bấm «+ New», thêm dòng thứ nhất: `student_id` là `HS901`, `name` là `Thu Mot`, `email` là thư điện tử (chữ thường) của tài khoản thử thứ nhất. Bấm «Save».
3. Thêm dòng thứ hai y như vậy: `HS902`, `Thu Hai`, thư điện tử của tài khoản thử thứ hai.
4. Thêm dòng thứ ba: `HS903`, `Thu Ba`, thư điện tử của tài khoản thử thứ ba.
5. Gửi ĐƯỜNG DẪN ỨNG DỤNG cho 3 tài khoản thử.

## Bảng thử

Làm lần lượt từ dòng 1. Dòng nào không đạt: dừng lại, sửa theo cột "Không đạt thì xem", rồi làm lại dòng đó.

| # | Ai làm | Làm gì | 👀 Kết quả đúng | Không đạt thì xem | Đạt |
|---|---|---|---|---|---|
| 1 | HS901 | Mở ĐƯỜNG DẪN ỨNG DỤNG trên **điện thoại** | Chào "Thu Mot (HS901 – )". Ô chọn xếp 1 cột, không phải kéo ngang | PA02 Phần 3; PA08 | [ ] |
| 2 | HS901 | Mở ĐƯỜNG DẪN ỨNG DỤNG trên **máy tính** | Ô chọn xếp 2 cột, nằm giữa màn hình | PA05 Phần 2 | [ ] |
| 3 | HS901 | Chọn câu lạc bộ ở ô 1 và ô 3, bỏ trống ô 2, bấm Nộp | Sang trang "Đã lưu nguyện vọng", liệt kê 2 câu lạc bộ số 1 và 2. Giáo viên mở bảng `NguyenVong`: dòng `HS901` có `pref_1`, `pref_2` là mã câu lạc bộ, `pref_3` trống, `so_lan_nop` là 1 | PA09 | [ ] |
| 4 | HS901 | Bấm "Sửa lại" (👀 ô 1 và ô 2 đang có câu lạc bộ, ô 3 trống). Bấm ô 2, chọn **dòng trống** ở đầu danh sách. Bấm "Cập nhật nguyện vọng" | Bảng `NguyenVong` vẫn **một dòng** `HS901`, `pref_2` trống, `so_lan_nop` là 2 | PA09, ⚠️ cuối tệp | [ ] |
| 5 | HS901 | Bấm "Sửa lại", chọn **cùng một** câu lạc bộ ở ô 1 và ô 2 | Chữ đỏ "Có CLB bị chọn trùng.", nút Nộp mờ, bấm không được | PA09 Phần 1 | [ ] |
| 6 | HS902 | Nộp một phiếu. Rồi mở thẳng địa chỉ: ĐỊA CHỈ TRANG + `/Lists/NguyenVong` | Chỉ thấy **một dòng** `HS902`, không thấy dòng `HS901` | SP09 bước 27, 28 | [ ] |
| 7 | Một tài khoản trường **không** có trong bảng `HocSinh` | Mở ĐƯỜNG DẪN ỨNG DỤNG | Trang chữ đỏ "… chưa có trong danh sách học sinh" | PA13 Phần 1 | [ ] |
| 8 | Bạn | Ở PA04 bước 4 đổi ngày trong `HanChot` thành ngày hôm qua → phát hành (PA14 bước 1 đến 4). Rồi HS903 mở ĐƯỜNG DẪN ỨNG DỤNG | HS903 thấy chữ đỏ "Đã hết hạn nộp nguyện vọng.", các ô chọn không bấm được, nút Nộp mờ | PA07, PA08 mục «DisplayMode» | [ ] |
| 9 | Bạn | **Đổi `HanChot` về đúng ngày giờ thật → phát hành lại** | Mở lại ứng dụng thấy dòng hạn chót đúng | | [ ] |
| 10 | Bạn (giáo viên phụ trách) | Mở ĐƯỜNG DẪN ỨNG DỤNG, bấm "Làm mới số liệu" | Trang theo dõi: "2 / …học sinh đã nộp"; `HS903` có trong danh sách chưa nộp | PA12 | [ ] |
| 11 | Bạn | Làm mục "Tải dữ liệu về" bên dưới | Tải được tệp; mở bằng Excel thấy dòng đầu là `student_id`, `name`, `pref_1` … `pref_10` | | [ ] |
| 12 | Bạn | Đưa tệp câu lạc bộ, rồi tệp nguyện vọng vào phần mềm xếp câu lạc bộ, chạy xếp | Không báo lỗi, ra kết quả cho `HS901`, `HS902` | Mục 8 của [hướng dẫn chi tiết](../../HUONG_DAN_POWER_APPS_DANG_KY.md) | [ ] |

⚠️ HS901 mở ứng dụng mà vẫn thấy bản cũ sau khi bạn phát hành lại: bảo em đó đóng hẳn thẻ trình duyệt rồi mở lại ĐƯỜNG DẪN ỨNG DỤNG.

## Tải dữ liệu về

Làm một lần để tạo **cách xem chỉ gồm các cột phần mềm cần**, sau đó mỗi lần tải chỉ cần bước 8 đến 10.

1. Mở bảng `NguyenVong` trên SharePoint.
2. Ở đầu bên phải thanh lệnh của bảng, bấm vào tên cách xem đang dùng («All Items»).
3. Bấm «Create new view».
4. Bấm ô «View name», dán:
```
Xuat_kiosk
```
5. Mục «Show as» để nguyên «List». Bấm «Create».
6. Ẩn 3 cột không cần. Với **từng** cột `email`, `nop_luc`, `so_lan_nop`: bấm vào tên cột ở hàng tên cột → «Column settings» → «Hide this column».
7. Bấm lại vào tên cách xem («Xuat_kiosk*») ở đầu bên phải thanh lệnh → «Save view as» → bấm «Save».

👀 Bảng chỉ còn các cột `student_id`, `name`, `pref_1` đến `pref_10`, đúng thứ tự đó.

8. Kiểm tra tên cách xem ở đầu bên phải thanh lệnh đang là «Xuat_kiosk».
9. Trên thanh lệnh, bấm «Export».
10. Bấm «Export to CSV».

👀 Trình duyệt tải về một tệp đuôi `.csv`.

11. Bảng `CLB`: làm bước 1 đến 10 tương tự, tên cách xem `Xuat_kiosk`, ẩn 2 cột `mo_ta`, `co_thi`.
12. Có bảng `ChonThi`: mở bảng, làm bước 9 và 10 (không cần ẩn cột nào).

⚠️ Tệp tải về có thêm cột lạ ở cuối (ví dụ «Item Type», «Path»): mở tệp bằng Excel, xoá các cột đó, lưu lại với kiểu «CSV UTF-8 (Comma delimited)».
⚠️ Mở tệp thấy chữ tiếng Việt bị vỡ: xem Phụ lục A của [hướng dẫn chi tiết](../../HUONG_DAN_POWER_APPS_DANG_KY.md).

## Dọn dẹp (bắt buộc trước khi mở cho cả trường)

- [ ] Bảng `NguyenVong`: xoá các dòng `HS901`, `HS902`, `HS903`.
- [ ] Bảng `ChonThi` (nếu đã làm): xoá các dòng `HS901`, `HS902`, `HS903`.
- [ ] Bảng `HocSinh`: xoá 3 dòng `HS901`, `HS902`, `HS903`.
- [ ] Trong phần mềm xếp câu lạc bộ: xoá dữ liệu thử.
- [ ] Mở [PA04](PA04_cong_thuc_app.md) bước 4 đến 6, đọc lại `HanChot`, `SoNguyenVongToiDa`, `DSQuanTri` cho đúng. Có sửa thì phát hành lại.
- [ ] Gửi ĐƯỜNG DẪN ỨNG DỤNG và mã QR cho học sinh.

## Sau hạn chót

1. Khoá bảng lại: làm [SP09](../sharepoint/SP09_phan_quyen.md), Phần 4.
2. Tải dữ liệu về: làm mục "Tải dữ liệu về" ở trên, bước 8 đến 12.
3. Đưa vào phần mềm xếp câu lạc bộ: tệp câu lạc bộ trước, rồi tệp chọn thi (nếu có), rồi tệp nguyện vọng. Chi tiết: mục 8 của [hướng dẫn chi tiết](../../HUONG_DAN_POWER_APPS_DANG_KY.md).
