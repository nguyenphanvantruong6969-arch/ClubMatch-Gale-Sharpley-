# PA09 — Trang đăng ký: dòng báo lỗi và nút Nộp

[← PA08](PA08_dang_ky_o_chon.md) · Tiếp theo: [PA10](PA10_man_xac_nhan.md)

Cả hai thêm vào `conKhung_DangKy`, nằm **dưới** `conLuoi`.

## Phần 1 — Dòng báo lỗi

1. Cây bên trái: bấm `conKhung_DangKy` → thêm «Text label». Đổi tên thành:
```
lblLoi
```
2. Điền các mục:

**«Text»** — dán:
```
With({ds: Filter([ddNV1.Selected.club_id, ddNV2.Selected.club_id, ddNV3.Selected.club_id, ddNV4.Selected.club_id, ddNV5.Selected.club_id, ddNV6.Selected.club_id, ddNV7.Selected.club_id, ddNV8.Selected.club_id, ddNV9.Selected.club_id, ddNV10.Selected.club_id], !IsBlank(Value))},
  If(CountRows(ds) = 0, "Em chưa chọn CLB nào.",
     CountRows(Distinct(ds, Value)) < CountRows(ds), "Có CLB bị chọn trùng.",
     ""))
```
**«Color»** — dán:
```
Color.Red
```
**«Visible»** — dán:
```
!IsBlank(Self.Text)
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```

## Phần 2 — Nút Nộp

3. Cây bên trái: bấm `conKhung_DangKy` → thêm «Button». Đổi tên thành:
```
btnNop
```
4. Điền các mục:

**«Text»** — dán:
```
If(IsBlank(varNV), "Nộp nguyện vọng", "Cập nhật nguyện vọng")
```
**«DisplayMode»** — dán:
```
If(HetHan || !IsBlank(lblLoi.Text), DisplayMode.Disabled, DisplayMode.Edit)
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
48
```
**«OnSelect»** (việc làm khi bấm nút) — dán:
```
With({ds: Filter([ddNV1.Selected.club_id, ddNV2.Selected.club_id, ddNV3.Selected.club_id, ddNV4.Selected.club_id, ddNV5.Selected.club_id, ddNV6.Selected.club_id, ddNV7.Selected.club_id, ddNV8.Selected.club_id, ddNV9.Selected.club_id, ddNV10.Selected.club_id], !IsBlank(Value))},
  If(Now() > HanChot,
    Notify("Đã hết hạn.", NotificationType.Error),
    Set(varNV,
      Patch(NguyenVong,
        Coalesce(LookUp(NguyenVong, student_id = varHS.student_id), Defaults(NguyenVong)),
        {
          student_id: varHS.student_id,
          name: varHS.name,
          email: Lower(User().Email),
          pref_1: Index(ds, 1).Value,
          pref_2: If(CountRows(ds) >= 2, Index(ds, 2).Value, Blank()),
          pref_3: If(CountRows(ds) >= 3, Index(ds, 3).Value, Blank()),
          pref_4: If(CountRows(ds) >= 4, Index(ds, 4).Value, Blank()),
          pref_5: If(CountRows(ds) >= 5, Index(ds, 5).Value, Blank()),
          pref_6: If(CountRows(ds) >= 6, Index(ds, 6).Value, Blank()),
          pref_7: If(CountRows(ds) >= 7, Index(ds, 7).Value, Blank()),
          pref_8: If(CountRows(ds) >= 8, Index(ds, 8).Value, Blank()),
          pref_9: If(CountRows(ds) >= 9, Index(ds, 9).Value, Blank()),
          pref_10: If(CountRows(ds) >= 10, Index(ds, 10).Value, Blank()),
          nop_luc: Now(),
          so_lan_nop: Coalesce(varNV.so_lan_nop, 0) + 1
        }));
    If(IsError(varNV),
      Notify("Lưu thất bại, em thử lại hoặc báo giáo viên.", NotificationType.Error),
      Navigate(scrXacNhan, ScreenTransition.Fade))))
```

5. Bấm `Ctrl` + `S`.

## Nút này làm gì

- Học sinh bỏ trống một ô ở giữa: các lựa chọn tự **dồn lên trên**.
- Nộp lại lần nữa: **ghi đè** đúng phiếu cũ, không sinh phiếu mới.
- Kiểm tra hạn chót **một lần nữa** lúc bấm, phòng trường hợp học sinh mở ứng dụng từ trước giờ hết hạn.

## Kiểm tra

- [ ] Không còn gạch đỏ ở `lblLoi` và `btnNop`.
- ⚠️ Gạch đỏ ở chữ `Blank()`: bật «Formula-level error management» (PA02, Phần 4).
- ⚠️ Gạch đỏ ở `student_id` hoặc `club_id`: thay bằng `Title`.
