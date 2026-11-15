# PA11 — Trang chọn câu lạc bộ thi

[← PA10](PA10_man_xac_nhan.md) · Tiếp theo: [PA12](PA12_man_quan_tri.md)

**Bỏ qua cả tệp này** nếu không có bảng `ChonThi` (đã bỏ SP07).

Thêm vào `conKhung_ChonThi`, đúng thứ tự: nút quay về, 5 ô chọn câu lạc bộ thi, nút lưu. Cuối cùng thêm một nút ở trang đăng ký để sang trang này.

Các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC: xem đầu tệp [PA05](PA05_tao_man_hinh_va_khung.md).

## Phần 1 — Nút quay về trang nguyện vọng

1. Cây bên trái: bấm mũi tên cạnh `scrChonThi` để mở ra, rồi bấm `conKhung_ChonThi`.
2. THÊM nút bấm (`Button`).
3. ĐỔI TÊN nút vừa thêm thành:
```
btnVeDangKy
```
4. Bấm `btnVeDangKy`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"← Nguyện vọng"
```
**«OnSelect»** — dán:
```
Navigate(scrDangKy)
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
48
```

## Phần 2 — Khung chứa 5 ô

5. Cây bên trái: bấm `conKhung_ChonThi`.
6. THÊM khung ngang (`Horizontal container`).
7. ĐỔI TÊN khung vừa thêm thành:
```
conLuoiThi
```
8. Bấm `conLuoiThi`, rồi ĐIỀN 4 MỤC sau:

**«Width»** — dán:
```
Parent.Width
```
**«LayoutWrap»** — dán:
```
true
```
**«LayoutGap»** — dán:
```
12
```
**«Height»** — dán:
```
If(LaPhone, 450, 270)
```

## Phần 3 — Ô thi số 1

9. Cây bên trái: bấm `conLuoiThi`.
10. THÊM khung dọc (`Vertical container`).
11. ĐỔI TÊN khung vừa thêm thành:
```
conThi1
```
12. Bấm `conThi1`, rồi ĐIỀN 2 MỤC sau:

**«Width»** — dán:
```
If(LaPhone, Parent.Width, (Parent.Width - 12) / 2)
```
**«Height»** — dán:
```
80
```

13. Cây bên trái: bấm `conThi1`.
14. THÊM ô chữ (`Text label`).
15. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblThi1
```
16. Bấm `lblThi1`, rồi ĐIỀN 3 MỤC sau:

**«Text»** — dán:
```
"CLB thi 1"
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
30
```

17. Cây bên trái: bấm `conThi1`.
18. Trên thanh lệnh bấm «Insert», dán `Drop down` vào ô tìm kiếm, bấm dòng «Drop down» (có hai dòng thì bấm dòng dưới chữ «Classic»).
19. ĐỔI TÊN ô thả xuống vừa thêm thành:
```
ddThi1
```
20. Bấm `ddThi1`, rồi ĐIỀN 7 MỤC sau:

**«Items»** — dán (chỉ hiện câu lạc bộ có thi):
```
Filter(colCLB, co_thi)
```
**«Value»** — dán (có cả hai dấu ngoặc kép):
```
"name"
```
**«AllowEmptySelection»** — dán:
```
true
```
**«Default»** — dán:
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_1).name
```
**«DisplayMode»** — dán:
```
If(HetHan, DisplayMode.View, DisplayMode.Edit)
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
44
```

⚠️ Không điền được mục «Value» bằng cách dán: ở khung bên phải bấm thẻ «Properties», bấm ô thả xuống «Value», chọn `name`.

## Phần 4 — Nhân ra ô 2 đến ô 5

Với **mỗi** ô từ 2 đến 5, làm đủ 8 bước sau. Các ô xám của từng ô nằm ở danh sách bên dưới.

21. Cây bên trái: bấm chuột phải `conThi1`, bấm «Copy».
22. Cây bên trái: bấm một lần vào `conLuoiThi`.
23. Bấm `Ctrl` + `V`.

👀 Dưới `conLuoiThi` xuất hiện khung mới tên `conThi1_1` (đuôi số có thể khác), bên trong có một ô chữ và một ô thả xuống.

24. ĐỔI TÊN khung mới (ô xám thứ 1).
25. ĐỔI TÊN ô chữ bên trong (ô xám thứ 2).
26. ĐỔI TÊN ô thả xuống bên trong (ô xám thứ 3).
27. Bấm ô chữ bên trong, ĐIỀN MỤC «Text» (ô xám thứ 4).
28. Bấm ô thả xuống bên trong, ĐIỀN MỤC «Default» (ô xám thứ 5).

### Ô 2

Thứ 1 — tên khung:
```
conThi2
```
Thứ 2 — tên ô chữ:
```
lblThi2
```
Thứ 3 — tên ô thả xuống:
```
ddThi2
```
Thứ 4 — `lblThi2`, mục **«Text»**:
```
"CLB thi 2"
```
Thứ 5 — `ddThi2`, mục **«Default»**:
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_2).name
```

### Ô 3

Thứ 1 — tên khung:
```
conThi3
```
Thứ 2 — tên ô chữ:
```
lblThi3
```
Thứ 3 — tên ô thả xuống:
```
ddThi3
```
Thứ 4 — `lblThi3`, mục **«Text»**:
```
"CLB thi 3"
```
Thứ 5 — `ddThi3`, mục **«Default»**:
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_3).name
```

### Ô 4

Thứ 1 — tên khung:
```
conThi4
```
Thứ 2 — tên ô chữ:
```
lblThi4
```
Thứ 3 — tên ô thả xuống:
```
ddThi4
```
Thứ 4 — `lblThi4`, mục **«Text»**:
```
"CLB thi 4"
```
Thứ 5 — `ddThi4`, mục **«Default»**:
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_4).name
```

### Ô 5

Thứ 1 — tên khung:
```
conThi5
```
Thứ 2 — tên ô chữ:
```
lblThi5
```
Thứ 3 — tên ô thả xuống:
```
ddThi5
```
Thứ 4 — `lblThi5`, mục **«Text»**:
```
"CLB thi 5"
```
Thứ 5 — `ddThi5`, mục **«Default»**:
```
LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_5).name
```

## Phần 5 — Nút lưu

29. Cây bên trái: bấm `conKhung_ChonThi` (khung ngoài cùng, không phải `conLuoiThi`).
30. THÊM nút bấm (`Button`).
31. ĐỔI TÊN nút vừa thêm thành:
```
btnLuuThi
```
32. Bấm `btnLuuThi`, rồi ĐIỀN 5 MỤC sau:

**«Text»** — dán:
```
"Lưu CLB thi"
```
**«DisplayMode»** — dán:
```
If(HetHan || IsBlank(varHS), DisplayMode.Disabled, DisplayMode.Edit)
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
48
```
**«OnSelect»** — dán:
```
With({ds: Filter([ddThi1.Selected.club_id, ddThi2.Selected.club_id, ddThi3.Selected.club_id, ddThi4.Selected.club_id, ddThi5.Selected.club_id], !IsBlank(Value))},
  If(Now() > HanChot, Notify("Đã hết hạn.", NotificationType.Error),
    CountRows(Distinct(ds, Value)) < CountRows(ds), Notify("Trùng CLB thi.", NotificationType.Error),
    With({cu: LookUp(ChonThi, student_id = varHS.student_id)},
      With({kq: Patch(ChonThi,
          If(IsBlank(cu), Defaults(ChonThi), cu),
          {student_id: varHS.student_id, name: varHS.name,
           test_club_1: If(CountRows(ds) >= 1, Index(ds, 1).Value, Blank()),
           test_club_2: If(CountRows(ds) >= 2, Index(ds, 2).Value, Blank()),
           test_club_3: If(CountRows(ds) >= 3, Index(ds, 3).Value, Blank()),
           test_club_4: If(CountRows(ds) >= 4, Index(ds, 4).Value, Blank()),
           test_club_5: If(CountRows(ds) >= 5, Index(ds, 5).Value, Blank())})},
        If(IsError(kq) || IsBlank(kq),
          Notify("Lưu thất bại, em thử lại hoặc báo giáo viên.", NotificationType.Error),
          Reset(ddThi1); Reset(ddThi2); Reset(ddThi3); Reset(ddThi4); Reset(ddThi5);
          Notify("Đã lưu CLB thi.", NotificationType.Success))))))
```

## Phần 6 — Nút ở trang đăng ký để sang trang này

33. Cây bên trái: mở `scrDangKy`, bấm `conKhung_DangKy`.
34. THÊM nút bấm (`Button`).
35. ĐỔI TÊN nút vừa thêm thành:
```
btnSangThi
```
36. Bấm `btnSangThi`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Chọn CLB thi tuyển →"
```
**«OnSelect»** — dán:
```
Navigate(scrChonThi)
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
48
```

👀 Ở trang đăng ký, nút "Chọn CLB thi tuyển →" nằm dưới cùng, ngay dưới nút Nộp.

37. Bấm `Ctrl` + `S`.

## Kiểm tra

1. Cây bên trái: bấm `scrChonThi`, bấm **▶**.

👀 Từ trên xuống: nút "← Nguyện vọng", 5 ô "CLB thi 1" đến "CLB thi 5", nút "Lưu CLB thi". Bấm một ô thả xuống: chỉ thấy tên các câu lạc bộ có `co_thi` là «Yes».

2. Bấm `Esc`.

- [ ] Đủ 5 ô, tên cùng số, không gạch đỏ.

⚠️ Ô thả xuống trống: chưa câu lạc bộ nào có `co_thi` là «Yes» trong bảng `CLB` (sửa trên SharePoint), hoặc chưa «Run OnStart».
⚠️ Học sinh đổi câu lạc bộ thi **sau khi đã có điểm** thì điểm nằm lệch ô. Vì vậy chỉ điền điểm sau hạn chót, khi bảng đã khoá ([SP09](../sharepoint/SP09_phan_quyen.md), Phần 4).
