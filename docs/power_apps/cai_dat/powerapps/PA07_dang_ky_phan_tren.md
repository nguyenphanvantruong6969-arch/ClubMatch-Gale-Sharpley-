# PA07 — Trang đăng ký: lời chào, hạn chót, lời dặn

Mất khoảng 10 phút · [← PA06](PA06_man_khong_co_ten.md) · Tiếp theo: [PA08](PA08_dang_ky_o_chon.md)

Thêm 3 ô chữ vào `conKhung_DangKy`. Với **mỗi** ô chữ: bấm `conKhung_DangKy` ở cây bên trái → «+ Insert» → «Text label» → đổi tên → điền các mục.

Ba mục này giống nhau ở cả 3 ô chữ:

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

## Ô chữ 1 — Lời chào

Tên:
```
lblChao
```
**«Text»** — dán:
```
"Chào " & varHS.name & " (" & varHS.student_id & " – " & varHS.class_id & ")"
```
**«Size»** — dán (thay cho cỡ chữ chung, vì đây là tiêu đề):
```
If(LaPhone, 22, 26)
```
**«FontWeight»** — dán:
```
FontWeight.Semibold
```

## Ô chữ 2 — Hạn chót

Tên:
```
lblHan
```
**«Text»** — dán:
```
If(HetHan, "Đã hết hạn nộp nguyện vọng.",
  "Hạn chót: " & Text(HanChot, "dd/mm/yyyy hh:mm") &
  If(IsBlank(varNV), "  •  Em chưa nộp.", "  •  Đã nộp lúc " & Text(varNV.nop_luc, "dd/mm hh:mm")))
```
**«Color»** — dán:
```
If(HetHan, Color.Red, Color.DarkGreen)
```

## Ô chữ 3 — Lời dặn

Tên:
```
lblHuongDan
```
**«Text»** — dán:
```
"Chọn tối đa " & SoNguyenVongToiDa & " CLB, CLB em thích nhất ở ô 1. Không chọn trùng. Hãy xếp đúng thứ tự em thật sự muốn: cách xếp của trường (Gale–Shapley) bảo đảm khai thật luôn có lợi nhất cho em."
```

Bấm `Ctrl` + `S`.

## Kiểm tra

- 👀 Lúc đang thiết kế, lời chào có thể chỉ hiện "Chào ( – )" vì bạn không có trong bảng học sinh. Bình thường.
- [ ] Ở cây bên trái, thứ tự từ trên xuống là `lblChao`, `lblHan`, `lblHuongDan`. Sai thứ tự: chuột phải → «Reorder» → «Move up» hoặc «Move down».
