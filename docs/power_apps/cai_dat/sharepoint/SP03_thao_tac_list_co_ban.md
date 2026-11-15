# SP03 — 5 thao tác cơ bản với bảng dữ liệu

[← SP02](SP02_tao_site.md) · Tiếp theo: [SP04](SP04_list_CLB.md)

Trên SharePoint, **bảng dữ liệu** được gọi là «List». Mỗi bảng giống một trang tính Excel: mỗi dòng là một người hoặc một câu lạc bộ, mỗi cột là một thông tin.

Các tệp SP04 đến SP07 chỉ ghi ngắn như "**làm T1**", "**làm T3**". Đọc tệp này một lần, khi cần thì quay lại.

> **Quy tắc vàng:** tên bảng và tên cột luôn **sao chép từ ô xám**, không gõ tay. Sai một chữ thì phần mềm xếp câu lạc bộ sẽ không đọc được. Lỡ đặt sai tên cột: **xoá cột đó và tạo lại** (cách xoá ở cuối tệp này), đừng sửa tên.

## T1 — Tạo bảng mới

1. Mở ĐỊA CHỈ TRANG.
2. Bấm hình bánh răng ⚙ ở góc trên bên phải trang.
3. Bấm «Site contents» trong bảng vừa mở.

👀 Trang liệt kê mọi thứ có trong trang, phía trên có nút «+ New».

4. Bấm «+ New».
5. Bấm «List».
6. Bấm ô «Blank list» (bản khác ghi «List» nằm dưới chữ «Create from blank»).
7. Bấm vào ô «Name», dán tên bảng (lấy từ ô xám trong tệp đang làm).
8. Bấm vào ô đánh dấu «Show in site navigation» để **bỏ** dấu tích.
9. Bấm «Create».

👀 Một bảng trống mở ra. Phía trên bên trái là tên bảng vừa dán. Hàng tên cột chỉ có một cột «Title» và nút «+ Add column».

⚠️ Báo tên đã tồn tại: bạn đã tạo bảng này rồi. Bấm ⚙ → «Site contents», bấm vào tên bảng đó để mở, không tạo lại.

## T2 — Đổi tên cột «Title» có sẵn

1. Bấm vào chữ «Title» ở hàng tên cột.
2. Bấm «Column settings» trong bảng vừa mở.
3. Bấm «Rename».
4. Bấm vào ô tên, bấm `Ctrl` + `A`, rồi dán tên mới (lấy từ ô xám).
5. Bấm «Save».

👀 Chữ «Title» ở hàng tên cột đổi thành tên mới.

⚠️ Bấm vào «Title» mà không có «Column settings»: làm đường khác.
1. Bấm ⚙ → «List settings».
2. Kéo xuống phần «Columns», bấm chữ «Title».
3. Bấm vào ô «Column name», bấm `Ctrl` + `A`, dán tên mới.
4. Kéo xuống cuối trang, bấm «OK».
5. Bấm tên bảng ở dòng chữ nhỏ phía trên cùng trang để quay lại bảng.

⚠️ **Không xoá** cột này. Về sau, Power Apps có thể vẫn gọi nó là `Title`; các tệp PA đã có cách xử lý.

## T3 — Thêm một cột

1. Bấm «+ Add column» ở cuối hàng tên cột (bên phải cột cuối cùng).
2. Trong bảng chọn loại cột, bấm đúng loại mà tệp đang làm yêu cầu:

   | Tệp ghi | Bấm vào | Dùng cho |
   |---|---|---|
   | Chữ ngắn | «Text» (bản khác ghi «Single line of text») | tên, mã, lớp |
   | Đoạn văn | «Multiple lines of text» | lời giới thiệu, câu hỏi dài |
   | Số | «Number» | số chỗ, điểm |
   | Có/Không | «Yes/No» | có thi tuyển không |
   | Ngày giờ | «Date and time» | giờ nộp |

3. Bấm «Next» ở cuối bảng chọn.

👀 Bên phải mở ra khung «Create a column».

4. Bấm vào ô «Name», dán tên cột (lấy từ ô xám).
5. Chỉ với loại **Số**: tìm mục «Number of decimal places» trong khung (chưa thấy thì bấm «More options» để mở thêm), bấm ô thả xuống, chọn số mà tệp đang làm ghi (**0** hoặc **1**).
6. Chỉ với loại **Ngày giờ**: gạt công tắc «Include Time» sang bật.
7. Chỉ khi tệp đang làm ghi **Bắt buộc**: bấm «More options», gạt công tắc «Require that this column contains information» sang bật.
8. Bấm «Save» ở cuối khung.

👀 Cột mới hiện ở cuối hàng tên cột, đúng tên vừa dán.

⚠️ Báo «The column name that you entered is already in use or reserved»: nhìn lại hàng tên cột. Cột đó đã có thì bấm «Cancel», bạn đã tạo rồi. Chưa có mà vẫn báo: chụp màn hình gửi người phụ trách, đừng tự đặt tên khác.

## T4 — Giúp tìm nhanh theo một cột

1. Bấm ⚙ ở góc trên bên phải.
2. Bấm «List settings».
3. Kéo xuống hết danh sách cột trong phần «Columns», bấm dòng chữ «Indexed columns».
4. Bấm «Create a new index».
5. Bấm ô thả xuống «Primary column for this index», chọn tên cột mà tệp đang làm ghi.
6. Bấm «Create».

👀 Tên cột vừa chọn hiện trong danh sách «Indexed columns».

7. Bấm tên bảng ở dòng chữ nhỏ phía trên cùng trang (dạng `CLB-2026 > tên bảng > Settings`) để quay lại bảng.

## T5 — Không cho trùng trong một cột

1. **Làm T4 cho cột đó trước.**
2. Bấm ⚙ → «List settings».
3. Trong phần «Columns», bấm tên cột.
4. Tìm mục «Enforce unique values», bấm chọn «Yes».
5. Kéo xuống cuối trang, bấm «OK».

👀 Quay về trang «Settings», không báo lỗi.

6. Bấm tên bảng ở dòng chữ nhỏ phía trên cùng trang để quay lại bảng.

⚠️ Hiện hộp hỏi có muốn tạo «index» cho cột không: bấm «OK».
⚠️ Báo có dữ liệu trùng: quay lại bảng, xoá dòng trùng, rồi làm lại T5.

## Thêm 1 — Đổi thứ tự cột

1. Bấm ⚙ → «List settings».
2. Kéo xuống dưới danh sách cột, bấm «Column ordering».
3. Mỗi cột có một ô số bên phải. Bấm ô số, chọn vị trí mong muốn (1 là cột đầu tiên).
4. Bấm «OK».

## Thêm 2 — Xoá một cột đặt sai tên

1. Ở bảng, bấm vào tên cột sai ở hàng tên cột.
2. Bấm «Column settings».
3. Bấm «Edit».
4. Kéo xuống cuối khung bên phải, bấm «Delete».
5. Bấm «Delete» lần nữa để xác nhận.
6. Tạo lại cột bằng T3.

- [ ] Đã đọc T1 đến T5.
