# PA08 — Trang đăng ký: 10 ô chọn câu lạc bộ

[← PA07](PA07_dang_ky_phan_tren.md) · Tiếp theo: [PA09](PA09_dang_ky_nut_nop.md)

Làm **ô 1 thật kỹ**, chạy thử thấy đúng, rồi mới nhân ra 9 ô còn lại.

## Phần 1 — Khung chứa các ô

1. Cây bên trái: bấm `conKhung_DangKy`.
2. «+ Insert» → dán vào ô tìm:
```
Horizontal container
```
3. Bấm «Horizontal container» (khung xếp ngang). Đổi tên thành:
```
conLuoi
```
4. Điền các mục:

**«Width»** — dán:
```
Parent.Width
```
**«LayoutWrap»** — dán (ở khung bên phải có thể tên «Wrap»):
```
true
```
**«LayoutGap»** — dán:
```
12
```
**«Height»** — dán:
```
If(LaPhone, 90 * SoNguyenVongToiDa, 90 * RoundUp(SoNguyenVongToiDa / 2, 0))
```

## Phần 2 — Ô số 1

5. Cây bên trái: bấm `conLuoi` → «+ Insert» → dán `Vertical container` → bấm «Vertical container». Đổi tên thành:
```
conNV1
```
**«Width»** — dán (điện thoại 1 cột, máy tính 2 cột):
```
If(LaPhone, Parent.Width, (Parent.Width - 12) / 2)
```
**«Height»** — dán:
```
80
```
**«Visible»** — dán:
```
1 <= SoNguyenVongToiDa
```

6. Cây bên trái: bấm `conNV1` → thêm «Text label». Đổi tên thành:
```
lblNV1
```
**«Text»** — dán:
```
"Nguyện vọng 1"
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
30
```

7. Cây bên trái: bấm `conNV1` → «+ Insert» → dán vào ô tìm:
```
Drop down
```
Bấm «Drop down» (ô thả xuống). Đổi tên thành:
```
ddNV1
```
**«Items»** — dán:
```
colCLB
```
**«Value»** — trong khung cài đặt bên phải, ô «Value», chọn:
```
name
```
**«AllowEmptySelection»** — dán:
```
true
```
**«Default»** — dán:
```
LookUp(colCLB, club_id = varNV.pref_1).name
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

> **Nếu ô thả xuống của bạn không có mục «Value» và «Default»**, mà có «ItemDisplayText» và «DefaultSelectedItems» (bản kiểu mới), thì điền thay:
>
> **«ItemDisplayText»** — dán:
> ```
> ThisItem.name
> ```
> **«DefaultSelectedItems»** — dán:
> ```
> Filter(colCLB, club_id = varNV.pref_1)
> ```

8. Bấm `Ctrl` + `S`. Bấm nút **▶** (góc trên phải) để chạy thử → mở ô 1.

👀 Thấy danh sách tên câu lạc bộ. Bấm `Esc` để thoát chạy thử.

## Phần 3 — Nhân ra ô 2 đến ô 10

9. Cây bên trái: chuột phải `conNV1` → «Copy».
10. Bấm `conLuoi` → `Ctrl` + `V`.

👀 Xuất hiện `conNV1_1`, bên trong có `lblNV1_1` và `ddNV1_1`.

11. Đổi tên 3 thứ vừa có, rồi sửa 3 mục, theo bảng của ô đó bên dưới.
12. Làm lại bước 9 đến 11 cho từng ô. Cứ 2–3 ô thì bấm `Ctrl` + `S`.

### Ô 2
Tên khung: `conNV2` · Tên ô chữ: `lblNV2` · Tên ô thả xuống: `ddNV2`
```
conNV2
```
```
lblNV2
```
```
ddNV2
```
`conNV2` mục **«Visible»**:
```
2 <= SoNguyenVongToiDa
```
`lblNV2` mục **«Text»**:
```
"Nguyện vọng 2"
```
`ddNV2` mục **«Default»** (bản kiểu mới: mục «DefaultSelectedItems», đổi `pref_1` thành `pref_2` trong đoạn ở trên):
```
LookUp(colCLB, club_id = varNV.pref_2).name
```

### Ô 3
```
conNV3
```
```
lblNV3
```
```
ddNV3
```
```
3 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 3"
```
```
LookUp(colCLB, club_id = varNV.pref_3).name
```

### Ô 4
```
conNV4
```
```
lblNV4
```
```
ddNV4
```
```
4 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 4"
```
```
LookUp(colCLB, club_id = varNV.pref_4).name
```

### Ô 5
```
conNV5
```
```
lblNV5
```
```
ddNV5
```
```
5 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 5"
```
```
LookUp(colCLB, club_id = varNV.pref_5).name
```

### Ô 6
```
conNV6
```
```
lblNV6
```
```
ddNV6
```
```
6 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 6"
```
```
LookUp(colCLB, club_id = varNV.pref_6).name
```

### Ô 7
```
conNV7
```
```
lblNV7
```
```
ddNV7
```
```
7 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 7"
```
```
LookUp(colCLB, club_id = varNV.pref_7).name
```

### Ô 8
```
conNV8
```
```
lblNV8
```
```
ddNV8
```
```
8 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 8"
```
```
LookUp(colCLB, club_id = varNV.pref_8).name
```

### Ô 9
```
conNV9
```
```
lblNV9
```
```
ddNV9
```
```
9 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 9"
```
```
LookUp(colCLB, club_id = varNV.pref_9).name
```

### Ô 10
```
conNV10
```
```
lblNV10
```
```
ddNV10
```
```
10 <= SoNguyenVongToiDa
```
```
"Nguyện vọng 10"
```
```
LookUp(colCLB, club_id = varNV.pref_10).name
```

(Từ ô 3 trở đi, 6 ô xám theo đúng thứ tự: tên khung, tên ô chữ, tên ô thả xuống, «Visible» của khung, «Text» của ô chữ, «Default» của ô thả xuống.)

## Kiểm tra

- [ ] Cây bên trái có `conNV1` đến `conNV10`, mỗi khung chứa `lblNV…` và `ddNV…` **cùng số**.
- [ ] Chạy thử với cửa sổ rộng: 2 cột. Thu hẹp cửa sổ: 1 cột.
- [ ] Đổi tạm `SoNguyenVongToiDa = 3` (ở PA04): chỉ còn 3 ô. **Nhớ đổi lại số thật.**
