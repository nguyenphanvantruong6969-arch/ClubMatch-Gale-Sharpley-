# SP07 — Bảng chọn câu lạc bộ thi (có thể bỏ qua)

Mất khoảng 10 phút · [← SP06](SP06_list_NguyenVong.md) · Tiếp theo: [SP08](SP08_nap_excel.md)

**Bỏ qua tệp này** nếu không câu lạc bộ nào thi tuyển. Khi bỏ qua thì cũng bỏ PA11.

**Bước 1 — Làm T1.** Tên bảng:
```
ChonThi
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title»:
```
student_id
```

**Bước 3 — Làm T3**, loại «Single line of text»:
```
name
```

**Bước 4 đến 13 — Làm T3 mười lần, xen kẽ** tên câu lạc bộ thi và điểm. Đúng thứ tự dưới đây:

| Lần | Loại cột | Số lẻ |
|---|---|---|
| 1, 3, 5, 7, 9 | «Single line of text» | |
| 2, 4, 6, 8, 10 | «Number» | 1 |

```
test_club_1
```
```
score_1
```
```
test_club_2
```
```
score_2
```
```
test_club_3
```
```
score_3
```
```
test_club_4
```
```
score_4
```
```
test_club_5
```
```
score_5
```

**Bước 14 — Làm T4** với cột `student_id`.

**Bước 15 — Làm T5** với cột `student_id`.

## Lưu ý

- Học sinh chỉ chọn câu lạc bộ muốn thi. **Giáo viên nhập điểm** sau khi chấm.
- Nhớ đánh dấu «Yes» ở cột `co_thi` cho các câu lạc bộ có thi trong bảng `CLB`.
