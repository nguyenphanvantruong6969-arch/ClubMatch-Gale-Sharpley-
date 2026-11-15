# SP06 — Bảng nguyện vọng

[← SP05](SP05_list_HocSinh.md) · Tiếp theo: [SP07](SP07_list_ChonThi.md)

Ứng dụng sẽ tự ghi phiếu của học sinh vào bảng này. Bạn chỉ tạo cột, **không** điền dòng nào. **Không bật Bắt buộc** cho bất kỳ cột nào ở bảng này (bỏ qua T3 bước 7).

**Bước 1 — Làm T1.** Tên bảng:
```
NguyenVong
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã học sinh):
```
student_id
```

**Bước 3 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (họ tên):
```
name
```

**Bước 4 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 1):
```
pref_1
```

**Bước 5 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 2):
```
pref_2
```

**Bước 6 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 3):
```
pref_3
```

**Bước 7 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 4):
```
pref_4
```

**Bước 8 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 5):
```
pref_5
```

**Bước 9 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 6):
```
pref_6
```

**Bước 10 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 7):
```
pref_7
```

**Bước 11 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 8):
```
pref_8
```

**Bước 12 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 9):
```
pref_9
```

**Bước 13 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (nguyện vọng 10):
```
pref_10
```

**Bước 14 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (thư điện tử):
```
email
```

**Bước 15 — Làm T3.** Loại: **Ngày giờ**, bật «Include Time». Tên cột (giờ nộp):
```
nop_luc
```

**Bước 16 — Làm T3.** Loại: **Số**, số lẻ **0**. Tên cột (số lần nộp):
```
so_lan_nop
```

**Bước 17 — Làm T4** với cột `student_id`.

**Bước 18 — Làm T5** với cột `student_id`.

## Kiểm tra

👀 Hàng tên cột của bảng `NguyenVong`, đọc từ trái sang phải (kéo thanh trượt ngang để xem hết): `student_id`, `name`, `pref_1`, `pref_2`, `pref_3`, `pref_4`, `pref_5`, `pref_6`, `pref_7`, `pref_8`, `pref_9`, `pref_10`, `email`, `nop_luc`, `so_lan_nop`.

- [ ] Đủ 15 cột, đúng tên, đúng thứ tự.

## Lưu ý

- Trường chỉ cho chọn 5 câu lạc bộ thì **vẫn tạo đủ 10 cột** nguyện vọng. Ứng dụng chỉ hiện 5 ô.
- Trường có **nhiều buổi** sinh hoạt khác nhau (mỗi học sinh xếp nguyện vọng riêng cho từng buổi): bộ hướng dẫn này chưa làm trường hợp đó. Dừng ở đây và báo người phụ trách trước khi tạo cột.
