# SP04 — Bảng câu lạc bộ

[← SP03](SP03_thao_tac_list_co_ban.md) · Tiếp theo: [SP05](SP05_list_HocSinh.md)

Làm lần lượt từng bước. T1 đến T5 là các thao tác đã học ở [SP03](SP03_thao_tac_list_co_ban.md). Mỗi bước sao chép đúng chữ trong ô xám. "Loại" là dòng cần bấm ở T3 bước 2.

**Bước 1 — Làm T1.** Tên bảng:
```
CLB
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã câu lạc bộ):
```
club_id
```

**Bước 3 — Làm T3.** Loại: **Chữ ngắn**, **Bắt buộc**. Tên cột (tên câu lạc bộ):
```
name
```

**Bước 4 — Làm T3.** Loại: **Số**, số lẻ **0**, **Bắt buộc**. Tên cột (số chỗ):
```
capacity
```

**Bước 5 — Làm T3.** Loại: **Số**, số lẻ **0**. Tên cột (số chỗ ưu tiên):
```
reserve_capacity
```

**Bước 6 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nhóm được ưu tiên):
```
reserve_group
```

**Bước 7 — Làm T3.** Loại: **Đoạn văn**. Tên cột (lời giới thiệu):
```
mo_ta
```

**Bước 8 — Làm T3.** Loại: **Có/Không**. Tên cột (có thi tuyển không):
```
co_thi
```

**Bước 9 — Làm T4** với cột `club_id`.

**Bước 10 — Làm T5** với cột `club_id`.

## Kiểm tra

👀 Hàng tên cột của bảng `CLB`, đọc từ trái sang phải: `club_id`, `name`, `capacity`, `reserve_capacity`, `reserve_group`, `mo_ta`, `co_thi`.

- [ ] Đủ 7 cột, đúng tên, đúng thứ tự. Sai thứ tự: làm "Thêm 1" ở SP03. Sai tên: làm "Thêm 2" ở SP03.

## Lưu ý

- Mã câu lạc bộ viết liền, không dấu, ví dụ `clb_bongro`. **Đã mở cho học sinh đăng ký thì không đổi mã nữa.**
- Số chỗ ưu tiên **nằm trong** số chỗ, không cộng thêm. Ví dụ số chỗ 25, số chỗ ưu tiên 5: tổng vẫn là 25 chỗ.
- Bảng này để trống, chưa điền gì. Dữ liệu sẽ đưa vào ở [SP08](SP08_nap_excel.md).
