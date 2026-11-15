# SP04 — Bảng câu lạc bộ

[← SP03](SP03_thao_tac_list_co_ban.md) · Tiếp theo: [SP05](SP05_list_HocSinh.md)

Làm lần lượt từng bước. Mỗi bước sao chép đúng chữ trong ô xám.

**Bước 1 — Làm T1.** Tên bảng:
```
CLB
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã câu lạc bộ):
```
club_id
```

**Bước 3 — Làm T3.** Loại «Single line of text», **Bắt buộc**. Tên cột (tên câu lạc bộ):
```
name
```

**Bước 4 — Làm T3.** Loại «Number», 0 số lẻ, **Bắt buộc**. Tên cột (số chỗ):
```
capacity
```

**Bước 5 — Làm T3.** Loại «Number», 0 số lẻ. Tên cột (số chỗ ưu tiên):
```
reserve_capacity
```

**Bước 6 — Làm T3.** Loại «Single line of text». Tên cột (nhóm được ưu tiên):
```
reserve_group
```

**Bước 7 — Làm T3.** Loại «Multiple lines of text». Tên cột (giới thiệu):
```
mo_ta
```

**Bước 8 — Làm T3.** Loại «Yes/No». Tên cột (có thi tuyển không):
```
co_thi
```

**Bước 9 — Làm T4** với cột `club_id`.

**Bước 10 — Làm T5** với cột `club_id`.

## Kiểm tra

- [ ] Các cột theo đúng thứ tự: `club_id`, `name`, `capacity`, `reserve_capacity`, `reserve_group`, `mo_ta`, `co_thi`. Sai thứ tự: xem "đổi thứ tự cột" ở SP03.

## Lưu ý

- Mã câu lạc bộ viết liền, không dấu, ví dụ `clb_bongro`. **Đã mở cho học sinh đăng ký thì không đổi mã nữa.**
- Số chỗ ưu tiên **nằm trong** số chỗ, không cộng thêm.
