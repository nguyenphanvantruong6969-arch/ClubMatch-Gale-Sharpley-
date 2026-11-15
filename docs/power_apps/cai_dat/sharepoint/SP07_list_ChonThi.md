# SP07 — Bảng chọn câu lạc bộ thi

[← SP06](SP06_list_NguyenVong.md) · Tiếp theo: [SP08](SP08_nap_excel.md)

**Bỏ qua cả tệp này** nếu không câu lạc bộ nào thi tuyển. Khi bỏ qua thì cũng bỏ [PA11](../powerapps/PA11_man_chon_thi.md) và [PA16](../powerapps/PA16_bieu_mau_va_bai_thi.md).

Mỗi học sinh có một dòng: tối đa 5 câu lạc bộ muốn thi, và điểm thi của từng câu lạc bộ đó. **Không bật Bắt buộc** cho bất kỳ cột nào ở bảng này.

**Bước 1 — Làm T1.** Tên bảng:
```
ChonThi
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã học sinh):
```
student_id
```

**Bước 3 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (họ tên):
```
name
```

**Bước 4 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (câu lạc bộ thi thứ 1):
```
test_club_1
```

**Bước 5 — Làm T3.** Loại: **Số**, số lẻ **1**. Tên cột (điểm của câu lạc bộ thi thứ 1):
```
score_1
```

**Bước 6 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (câu lạc bộ thi thứ 2):
```
test_club_2
```

**Bước 7 — Làm T3.** Loại: **Số**, số lẻ **1**. Tên cột (điểm của câu lạc bộ thi thứ 2):
```
score_2
```

**Bước 8 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (câu lạc bộ thi thứ 3):
```
test_club_3
```

**Bước 9 — Làm T3.** Loại: **Số**, số lẻ **1**. Tên cột (điểm của câu lạc bộ thi thứ 3):
```
score_3
```

**Bước 10 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (câu lạc bộ thi thứ 4):
```
test_club_4
```

**Bước 11 — Làm T3.** Loại: **Số**, số lẻ **1**. Tên cột (điểm của câu lạc bộ thi thứ 4):
```
score_4
```

**Bước 12 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (câu lạc bộ thi thứ 5):
```
test_club_5
```

**Bước 13 — Làm T3.** Loại: **Số**, số lẻ **1**. Tên cột (điểm của câu lạc bộ thi thứ 5):
```
score_5
```

**Bước 14 — Làm T4** với cột `student_id`.

**Bước 15 — Làm T5** với cột `student_id`.

## Kiểm tra

👀 Hàng tên cột của bảng `ChonThi`, đọc từ trái sang phải: `student_id`, `name`, `test_club_1`, `score_1`, `test_club_2`, `score_2`, `test_club_3`, `score_3`, `test_club_4`, `score_4`, `test_club_5`, `score_5`.

- [ ] Đủ 12 cột, đúng tên, đúng thứ tự (xen kẽ câu lạc bộ rồi điểm).

## Lưu ý

- Học sinh chỉ chọn câu lạc bộ muốn thi. Các cột điểm `score_…` do **giáo viên** điền sau khi chấm (gõ tay vào bảng), hoặc do nút chấm điểm ở [PA16](../powerapps/PA16_bieu_mau_va_bai_thi.md) tự điền.
- ⚠️ Trong thời gian mở đăng ký, mỗi học sinh sửa được **dòng của chính mình** trong bảng này, kể cả ô điểm, nếu em đó biết mở thẳng bảng trên SharePoint. Vì vậy: **chỉ điền điểm sau khi đã khoá bảng** (SP09, Phần 4), và trước khi điền hãy xoá hết điểm đang có trong các cột `score_…`.
- Ở bảng `CLB`, câu lạc bộ nào có thi thì cột `co_thi` phải là «Yes». Việc này làm ở [SP08](SP08_nap_excel.md).
