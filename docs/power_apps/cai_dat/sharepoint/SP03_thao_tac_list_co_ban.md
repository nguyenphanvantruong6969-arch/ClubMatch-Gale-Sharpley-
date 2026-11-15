# SP03 — 5 thao tác cơ bản với bảng dữ liệu

Mất khoảng 10 phút · [← SP02](SP02_tao_site.md) · Tiếp theo: [SP04](SP04_list_CLB.md)

Trên SharePoint, **bảng dữ liệu** được gọi là «List». Mỗi bảng giống một trang tính Excel: mỗi dòng là một người hoặc một câu lạc bộ, mỗi cột là một thông tin.

Các tệp SP04 đến SP07 chỉ ghi ngắn như "**làm T1**", "**làm T3**". Đọc tệp này một lần, khi cần thì quay lại.

> **Quy tắc vàng:** tên cột luôn **sao chép từ ô xám**, không gõ tay. Sai một chữ thì phần mềm xếp câu lạc bộ sẽ không đọc được. Lỡ đặt sai tên: **xoá cột đó và tạo lại**, đừng sửa tên.

## T1 — Tạo bảng mới

1. Mở ĐỊA CHỈ TRANG.
2. Bấm hình bánh răng ⚙ (góc trên phải) → «Site contents».
3. Bấm «+ New» → «List».
4. Bấm «Blank list».
5. Bấm vào ô «Name», dán tên bảng (lấy từ ô xám trong tệp đang làm).
6. Bỏ đánh dấu «Show in site navigation» (tuỳ ý, cho gọn).
7. Bấm «Create».

👀 Một bảng trống, chỉ có một cột tên «Title».

## T2 — Đổi tên cột «Title» có sẵn

1. Bấm vào chữ «Title» ở đầu cột.
2. Bấm «Column settings» → «Rename».
   Không thấy: bấm ⚙ → «List settings» → trong phần «Columns», bấm «Title».
3. Bấm vào ô tên, `Ctrl` + `A`, rồi dán tên mới (lấy từ ô xám).
4. Bấm «Save».

⚠️ **Không xoá** cột này. Về sau, Power Apps có thể vẫn gọi nó là `Title`; các tệp PA đã có cách xử lý.

## T3 — Thêm một cột

1. Bấm «+ Add column» (ở cuối hàng tên cột).
2. Chọn loại cột theo bảng trong tệp đang làm:
   - «Single line of text»: chữ ngắn
   - «Multiple lines of text»: đoạn văn dài
   - «Number»: con số
   - «Yes/No»: có hoặc không
   - «Date and time»: ngày giờ
3. Bấm «Next».
4. Bấm vào ô «Name», dán tên cột (lấy từ ô xám).
5. Nếu là «Number»: bấm «More options» → mục «Number of decimal places» chọn **0** (số đếm) hoặc **1** (điểm thi), theo bảng.
6. Nếu là «Date and time»: bật «Include time».
7. Nếu bảng ghi **Bắt buộc**: bấm «More options» → bật «Require that this column contains information».
8. Bấm «Save».

👀 Cột mới hiện ở cuối hàng.

## T4 — Giúp tìm nhanh một cột

1. Bấm ⚙ → «List settings».
2. Kéo xuống dưới danh sách cột, bấm «Indexed columns».
3. Bấm «Create a new index».
4. Ô «Primary column»: chọn tên cột.
5. Bấm «Create».

## T5 — Không cho trùng trong một cột

1. **Làm T4 cho cột đó trước.**
2. Bấm ⚙ → «List settings» → bấm tên cột.
3. Mục «Enforce unique values»: chọn «Yes».
4. Bấm «OK».

⚠️ Báo lỗi nhắc đến «index»: quay lại T4. Báo có dữ liệu trùng: xoá dòng trùng rồi làm lại.

## Thêm: đổi thứ tự cột

Bấm ⚙ → «List settings» → «Column ordering» → chọn số thứ tự cho từng cột → «OK».

- [ ] Đã đọc và hiểu T1 đến T5.
