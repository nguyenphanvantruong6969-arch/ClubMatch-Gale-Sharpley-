# SP05 — Bảng học sinh

[← SP04](SP04_list_CLB.md) · Tiếp theo: [SP06](SP06_list_NguyenVong.md)

**Bước 1 — Làm T1.** Tên bảng:
```
HocSinh
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã học sinh):
```
student_id
```

**Bước 3 — Làm T3.** Loại «Single line of text», **Bắt buộc**. Tên cột (họ tên):
```
name
```

**Bước 4 — Làm T3.** Loại «Single line of text». Tên cột (lớp):
```
class_id
```

**Bước 5 — Làm T3.** Loại «Single line of text», **Bắt buộc**. Tên cột (thư điện tử):
```
email
```

**Bước 6 — Làm T3.** Loại «Single line of text». Tên cột (nhóm được ưu tiên):
```
reserve_group
```

**Bước 7 — Làm T4** với cột `student_id`.

**Bước 8 — Làm T5** với cột `student_id`.

**Bước 9 — Làm T4** với cột `email`.

**Bước 10 — Làm T5** với cột `email`.

## Kiểm tra

- [ ] Các cột theo đúng thứ tự: `student_id`, `name`, `class_id`, `email`, `reserve_group`.

## Lưu ý

- Ứng dụng nhận ra học sinh **qua thư điện tử lúc đăng nhập**. Thư điện tử trong bảng phải viết **chữ thường** và đúng từng chữ.
- Học sinh không có trong bảng này thì không nộp được.
