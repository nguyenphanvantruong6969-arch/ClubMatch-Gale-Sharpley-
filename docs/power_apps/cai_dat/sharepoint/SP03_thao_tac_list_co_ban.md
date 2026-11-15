# SP03 — 5 thao tác List cơ bản

⏱ 10 phút · [← SP02](SP02_tao_site.md) · Tiếp: [SP04](SP04_list_CLB.md)

Các tệp SP04–SP07 chỉ ghi "**làm T1**", "**làm T3 với cột X**"… Đọc tệp này một lần, quay lại khi cần.

> **Quy tắc vàng:** gõ tên cột **chữ thường, có gạch dưới, không dấu cách, không dấu tiếng Việt**, đúng y bảng. Sai tên → xuất CSV kiosk không nhận. Gõ nhầm thì **xoá cột, tạo lại**, đừng chỉ đổi tên.

## T1 — Tạo một List trống
1. Mở "ĐỊA CHỈ SITE".
2. Bấm **⚙** (bánh răng, góc trên phải) → **Site contents**.
3. Bấm **+ New** → **List**.
4. Bấm **Blank list**.
5. Ô **Name**: gõ tên List (đúng chữ hoa/thường).
6. Bỏ tick **Show in site navigation** (cho gọn, tuỳ ý).
7. Bấm **Create**.
   👀 Bảng trống chỉ có cột **Title**.

## T2 — Đổi tên cột Title
1. Bấm vào chữ **Title** ở tiêu đề cột.
2. Bấm **Column settings** → **Rename**. (Không thấy: **⚙ → List settings** → dưới *Columns* bấm **Title**.)
3. Xoá chữ cũ, gõ tên mới.
4. Bấm **Save**.
   ⚠️ **Không xoá** cột Title. Trong Power Apps nó vẫn có thể hiện tên `Title`.

## T3 — Thêm một cột
1. Bấm **+ Add column** (cuối hàng tiêu đề).
2. Chọn kiểu theo bảng:
   - *Single line of text* = chữ ngắn
   - *Multiple lines of text* = đoạn văn
   - *Number* = số
   - *Yes/No* = có/không
   - *Date and time* = ngày giờ
3. Bấm **Next**.
4. Ô **Name**: gõ tên cột.
5. Cột *Number*: bấm **More options** → **Number of decimal places** chọn **0** (số đếm) hoặc **1** (điểm).
6. Cột *Date and time*: bật **Include time**.
7. Nếu bảng ghi **Bắt buộc**: **More options** → bật **Require that this column contains information**.
8. Bấm **Save**.
   👀 Cột mới xuất hiện cuối bảng.

## T4 — Đánh chỉ mục (Indexed) một cột
1. **⚙ → List settings**.
2. Kéo xuống dưới bảng *Columns*, bấm **Indexed columns**.
3. Bấm **Create a new index**.
4. **Primary column**: chọn cột.
5. Bấm **Create**.

## T5 — Không cho trùng (Unique)
1. **Làm T4 với cột đó trước.**
2. **⚙ → List settings** → bấm tên cột.
3. Mục **Enforce unique values**: chọn **Yes**.
4. Bấm **OK**.
   ⚠️ Báo lỗi index → quay lại T4. Báo lỗi dữ liệu trùng → xoá dòng trùng rồi làm lại.

## Thêm: sắp thứ tự cột
**⚙ → List settings → Column ordering** → chọn số thứ tự → **OK**.

- [ ] Đã đọc, hiểu T1–T5.
