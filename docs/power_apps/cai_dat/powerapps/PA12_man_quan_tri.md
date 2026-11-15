# PA12 — Màn quản trị cho giáo viên

⏱ 20 phút · [← PA11](PA11_man_chon_thi.md) · Tiếp: [PA13](PA13_man_dau_tien_va_chay_thu.md)

Mọi control chèn trong `conKhung_QuanTri`.

## 1. Label `lblQTSoLieu`
`Size` = `26` · `Width` = `Parent.Width` · `Text` =
```
CountRows(NguyenVong) & " / " & CountRows(HocSinh) & " học sinh đã nộp"
```

## 2. Nút `btnLamMoi`
`Text` = `"Làm mới số liệu"` · `OnSelect` = `Refresh(NguyenVong); Refresh(HocSinh)` · `Height` = `48`

## 3. Label `lblQTChuaNop`
`Text` = `"Học sinh chưa nộp"` · `FontWeight` = `FontWeight.Semibold`

## 4. Gallery `galChuaNop`
1. Chọn `conKhung_QuanTri` → **+ Insert → Vertical gallery** → nếu hỏi nguồn dữ liệu: chọn `HocSinh`.
2. Đổi tên `galChuaNop`.
3. Thuộc tính:

| Thuộc tính | Dán |
|---|---|
| `Items` | `Filter(HocSinh, !(student_id in NguyenVong.student_id))` |
| `WrapCount` | `If(App.Width < 900, 1, 3)` |
| `TemplateSize` | `50` |
| `Height` | `400` |
| `Width` | `Parent.Width` |

4. Trong gallery, bấm label đầu tiên (Title) → `Text` = `ThisItem.student_id & " – " & ThisItem.name & " (" & ThisItem.class_id & ")"`.
5. Xoá các control thừa trong ô mẫu (subtitle, ảnh, mũi tên): chọn → **Delete**.

## 5. Gallery thống kê `galThongKe`
1. Chèn **Vertical gallery** mới → đổi tên `galThongKe`.
2. `Items` =
```
AddColumns(colCLB, NV1, CountRows(Filter(NguyenVong, pref_1 = club_id)))
```
3. `Height` = `400`, `Width` = `Parent.Width`, `TemplateSize` = `50`.
4. Label trong ô mẫu: `Text` = `ThisItem.name & ":  " & ThisItem.NV1 & " NV1 / chỉ tiêu " & ThisItem.capacity`.
   ⚠️ Bản mới có thể đòi `AddColumns(colCLB, "NV1", …)` (tên cột trong ngoặc kép) hoặc ngược lại. Báo đỏ ở `NV1` → thử dạng còn lại.

## 6. Nút `btnMoList`
`Text` = `"Mở danh sách để xuất CSV"` · `OnSelect` (thay bằng "ĐỊA CHỈ SITE" thật):
```
Launch("https://truong.sharepoint.com/sites/CLB-2026/Lists/NguyenVong")
```

**Ctrl+S.**

> Biểu tượng tam giác vàng (*delegation*) ở `galChuaNop`, `lblQTSoLieu`: bình thường khi ≤ 2000 học sinh (PA02 phần 5).

- [ ] Xong.
