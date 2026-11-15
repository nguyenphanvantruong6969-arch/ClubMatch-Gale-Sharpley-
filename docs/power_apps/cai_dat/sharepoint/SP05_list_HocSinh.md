# SP05 — Bảng học sinh

[← SP04](SP04_list_CLB.md) · Tiếp theo: [SP06](SP06_list_NguyenVong.md)

Làm lần lượt từng bước. T1 đến T5 là các thao tác ở [SP03](SP03_thao_tac_list_co_ban.md).

**Bước 1 — Làm T1.** Tên bảng:
```
HocSinh
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã học sinh):
```
student_id
```

**Bước 3 — Làm T3.** Loại: **Chữ ngắn**, **Bắt buộc**. Tên cột (họ tên):
```
name
```

**Bước 4 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (lớp):
```
class_id
```

**Bước 5 — Làm T3.** Loại: **Chữ ngắn**, **Bắt buộc**. Tên cột (thư điện tử):
```
email
```

**Bước 6 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nhóm được ưu tiên):
```
reserve_group
```

**Bước 7 — Làm T4** với cột `student_id`.

**Bước 8 — Làm T5** với cột `student_id`.

**Bước 9 — Làm T4** với cột `email`.

**Bước 10 — Làm T5** với cột `email`.

## Kiểm tra

👀 Hàng tên cột của bảng `HocSinh`, đọc từ trái sang phải: `student_id`, `name`, `class_id`, `email`, `reserve_group`.

- [ ] Đủ 5 cột, đúng tên, đúng thứ tự.

## Lưu ý

- Ứng dụng nhận ra học sinh **qua thư điện tử lúc đăng nhập**. Thư điện tử trong bảng phải viết **chữ thường** và đúng từng chữ. SP08 có bước làm sạch.
- Học sinh không có trong bảng này thì không nộp được.
- Bảng này để trống, chưa điền gì. Dữ liệu sẽ đưa vào ở [SP08](SP08_nap_excel.md).
