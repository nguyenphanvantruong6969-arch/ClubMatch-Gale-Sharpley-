# PA11 — Trang chọn câu lạc bộ thi (có thể bỏ qua)

[← PA10](PA10_man_xac_nhan.md) · Tiếp theo: [PA12](PA12_man_quan_tri.md)

**Bỏ qua** nếu không có bảng `ChonThi` (đã bỏ SP07).

## Phần 1 — Khung chứa 5 ô

1. Bấm `conKhung_ChonThi` → «+ Insert» → «Horizontal container». Tên:
```
conLuoiThi
```
**«Width»**:
```
Parent.Width
```
**«LayoutWrap»**:
```
true
```
**«LayoutGap»**:
```
12
```
**«Height»**:
```
If(LaPhone, 450, 270)
```

## Phần 2 — Ô thi số 1

2. Bấm `conLuoiThi` → «Vertical container». Tên:
```
conThi1
```
**«Width»**:
```
If(LaPhone, Parent.Width, (Parent.Width - 12) / 2)
```
**«Height»**:
```
80
```

3. Bấm `conThi1` → «Text label». Tên:
```
lblThi1
```
**«Text»**:
```
"CLB thi 1"
```
**«Width»**:
```
Parent.Width
```

4. Bấm `conThi1` → «Drop down». Tên:
```
ddThi1
```
**«Items»** (chỉ hiện câu lạc bộ có thi):
```
Filter(colCLB, co_thi)
```
**«Value»** (ở khung bên phải) chọn:
```
name
```
**«AllowEmptySelection»**:
```
true
```
**«Default»**:
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_1).name
```
**«DisplayMode»**:
```
If(HetHan, DisplayMode.View, DisplayMode.Edit)
```
**«Width»**:
```
Parent.Width
```

## Phần 3 — Nhân ra ô 2 đến ô 5

5. Chuột phải `conThi1` → «Copy» → bấm `conLuoiThi` → `Ctrl` + `V`.
6. Đổi tên 3 thứ mới và sửa 2 mục theo bảng từng ô. Thứ tự 5 ô xám: tên khung, tên ô chữ, tên ô thả xuống, «Text» của ô chữ, «Default» của ô thả xuống.

### Ô 2
```
conThi2
```
```
lblThi2
```
```
ddThi2
```
```
"CLB thi 2"
```
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_2).name
```

### Ô 3
```
conThi3
```
```
lblThi3
```
```
ddThi3
```
```
"CLB thi 3"
```
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_3).name
```

### Ô 4
```
conThi4
```
```
lblThi4
```
```
ddThi4
```
```
"CLB thi 4"
```
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_4).name
```

### Ô 5
```
conThi5
```
```
lblThi5
```
```
ddThi5
```
```
"CLB thi 5"
```
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_5).name
```

## Phần 4 — Nút lưu

7. Bấm `conKhung_ChonThi` → «Button». Tên:
```
btnLuuThi
```
**«Text»**:
```
"Lưu CLB thi"
```
**«Width»**:
```
Parent.Width
```
**«Height»**:
```
48
```
**«OnSelect»**:
```
With({ds: Filter([ddThi1.Selected.club_id, ddThi2.Selected.club_id, ddThi3.Selected.club_id, ddThi4.Selected.club_id, ddThi5.Selected.club_id], !IsBlank(Value))},
  If(Now() > HanChot, Notify("Đã hết hạn.", NotificationType.Error),
    CountRows(Distinct(ds, Value)) < CountRows(ds), Notify("Trùng CLB thi.", NotificationType.Error),
    Patch(ChonThi,
      Coalesce(LookUp(ChonThi, student_id = varHS.student_id), Defaults(ChonThi)),
      {student_id: varHS.student_id, name: varHS.name,
       test_club_1: If(CountRows(ds) >= 1, Index(ds, 1).Value, Blank()),
       test_club_2: If(CountRows(ds) >= 2, Index(ds, 2).Value, Blank()),
       test_club_3: If(CountRows(ds) >= 3, Index(ds, 3).Value, Blank()),
       test_club_4: If(CountRows(ds) >= 4, Index(ds, 4).Value, Blank()),
       test_club_5: If(CountRows(ds) >= 5, Index(ds, 5).Value, Blank())});
    Notify("Đã lưu CLB thi.", NotificationType.Success)))
```

## Phần 5 — Nút chuyển qua lại giữa hai trang

8. Bấm `conKhung_DangKy` → «Button». Tên:
```
btnSangThi
```
**«Text»**:
```
"Chọn CLB thi tuyển →"
```
**«OnSelect»**:
```
Navigate(scrChonThi)
```
Kéo nút này lên ngay dưới `lblHuongDan` (chuột phải → «Reorder»).

9. Bấm `conKhung_ChonThi` → «Button». Tên:
```
btnVeDangKy
```
**«Text»**:
```
"← Nguyện vọng"
```
**«OnSelect»**:
```
Navigate(scrDangKy)
```
Kéo nút này lên trên cùng của khung.

10. Bấm `Ctrl` + `S`.

⚠️ Học sinh đổi câu lạc bộ thi sau khi giáo viên đã nhập điểm thì điểm có thể bị lệch ô. Nên cho chọn thi xong **trước** ngày chấm.

- [ ] Xong.
