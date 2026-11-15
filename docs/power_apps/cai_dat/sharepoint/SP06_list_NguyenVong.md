# SP06 — Bảng nguyện vọng

[← SP05](SP05_list_HocSinh.md) · Tiếp theo: [SP07](SP07_list_ChonThi.md)

Ứng dụng sẽ tự ghi phiếu của học sinh vào bảng này. Bạn chỉ tạo cột, **không** điền gì. **Không bật Bắt buộc** cho cột nào ở bảng này.

**Bước 1 — Làm T1.** Tên bảng:
```
NguyenVong
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title»:
```
student_id
```

**Bước 3 — Làm T3**, loại «Single line of text»:
```
name
```

**Bước 4 đến 13 — Làm T3 mười lần**, loại «Single line of text». Mỗi lần dán một tên, theo đúng thứ tự (nguyện vọng 1 đến 10):
```
pref_1
```
```
pref_2
```
```
pref_3
```
```
pref_4
```
```
pref_5
```
```
pref_6
```
```
pref_7
```
```
pref_8
```
```
pref_9
```
```
pref_10
```

**Bước 14 — Làm T3**, loại «Single line of text»:
```
email
```

**Bước 15 — Làm T3**, loại «Date and time», bật «Include time» (giờ nộp):
```
nop_luc
```

**Bước 16 — Làm T3**, loại «Number», 0 số lẻ (số lần nộp):
```
so_lan_nop
```

**Bước 17 — Làm T4** với cột `student_id`.

**Bước 18 — Làm T5** với cột `student_id`.

## Kiểm tra

- [ ] Có đủ 16 cột theo đúng thứ tự trên, có đủ 10 cột nguyện vọng từ `pref_1` đến `pref_10`.

## Lưu ý

- Trường chỉ cho chọn 5 câu lạc bộ thì **vẫn tạo đủ 10 cột**. Ứng dụng chỉ hiện 5 ô.
- Trường có **nhiều buổi** sinh hoạt khác nhau: dừng lại, hỏi người phụ trách trước khi tạo cột.
