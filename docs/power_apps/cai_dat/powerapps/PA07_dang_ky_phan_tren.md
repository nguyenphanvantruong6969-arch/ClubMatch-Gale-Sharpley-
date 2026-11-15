# PA07 — Trang đăng ký: lời chào, hạn chót, lời dặn

[← PA06](PA06_man_khong_co_ten.md) · Tiếp theo: [PA08](PA08_dang_ky_o_chon.md)

Thêm 3 ô chữ vào `conKhung_DangKy`, đúng thứ tự: lời chào, hạn chót, lời dặn. Thêm theo thứ tự nào thì chúng xếp từ trên xuống theo thứ tự đó.

Các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC: xem đầu tệp [PA05](PA05_tao_man_hinh_va_khung.md).

## Ô chữ 1 — Lời chào

1. Cây bên trái: bấm mũi tên cạnh `scrDangKy` để mở ra, rồi bấm `conKhung_DangKy`.
2. THÊM ô chữ (`Text label`).
3. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblChao
```
4. Bấm `lblChao`, rồi ĐIỀN 5 MỤC sau:

**«Text»** — dán:
```
"Chào " & varHS.name & " (" & varHS.student_id & " – " & varHS.class_id & ")"
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```
**«Size»** — dán:
```
If(LaPhone, 22, 26)
```
**«FontWeight»** — dán:
```
FontWeight.Semibold
```

👀 Trên trang ở giữa hiện chữ đậm "Chào ( – )". Tên trống là đúng, vì bạn không có trong bảng học sinh.

## Ô chữ 2 — Hạn chót

5. Cây bên trái: bấm `conKhung_DangKy`.
6. THÊM ô chữ (`Text label`).
7. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblHan
```
8. Bấm `lblHan`, rồi ĐIỀN 5 MỤC sau:

**«Text»** — dán:
```
If(HetHan, "Đã hết hạn nộp nguyện vọng.",
  "Hạn chót: " & Text(HanChot, "dd/mm/yyyy hh:mm") &
  If(IsBlank(varNV), "  •  Em chưa nộp.", "  •  Đã nộp lúc " & Text(varNV.nop_luc, "dd/mm hh:mm")))
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```
**«Size»** — dán:
```
If(LaPhone, 16, 14)
```
**«Color»** — dán:
```
If(HetHan, Color.Red, Color.DarkGreen)
```

👀 Dưới lời chào hiện dòng chữ xanh lá "Hạn chót: …  •  Em chưa nộp.", ngày giờ đúng với ngày giờ bạn đã điền ở PA04.

## Ô chữ 3 — Lời dặn

9. Cây bên trái: bấm `conKhung_DangKy`.
10. THÊM ô chữ (`Text label`).
11. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblHuongDan
```
12. Bấm `lblHuongDan`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Chọn tối đa " & SoNguyenVongToiDa & " CLB, CLB em thích nhất ở ô 1. Không chọn trùng. Hãy xếp đúng thứ tự em thật sự muốn: cách xếp của trường (Gale–Shapley) bảo đảm khai thật luôn có lợi nhất cho em."
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```
**«Size»** — dán:
```
If(LaPhone, 16, 14)
```

13. Bấm `Ctrl` + `S`.

## Kiểm tra

👀 Trên trang ở giữa, từ trên xuống: lời chào (chữ to đậm), dòng hạn chót (xanh lá), lời dặn.

- [ ] Đúng 3 dòng, đúng thứ tự.

⚠️ Sai thứ tự (ví dụ lời dặn nằm trên dòng hạn chót): ở cây bên trái, bấm chuột phải vào ô chữ nằm sai chỗ → «Reorder» → bấm một trong các lệnh hiện ra, rồi nhìn trang ở giữa. Chưa đúng chỗ thì bấm lệnh còn lại. (Tên các lệnh trong «Reorder» khác nhau giữa các bản, nên hãy nhìn kết quả trên trang ở giữa.)
