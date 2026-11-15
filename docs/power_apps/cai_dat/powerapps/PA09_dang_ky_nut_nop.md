# PA09 — Màn đăng ký: báo lỗi và nút Nộp

⏱ 15 phút · [← PA08](PA08_dang_ky_o_chon.md) · Tiếp: [PA10](PA10_man_xac_nhan.md)

Cả hai đặt trong `conKhung_DangKy`, **dưới** `conLuoi`.

## Phần 1 — Label báo lỗi `lblLoi`
1. Cây: bấm `conKhung_DangKy` → **+ Insert → Text label** → đổi tên `lblLoi`.
2. Thuộc tính:

| Thuộc tính | Dán |
|---|---|
| `Text` | khối dưới |
| `Color` | `Color.Red` |
| `Visible` | `!IsBlank(Self.Text)` |
| `Width` | `Parent.Width` |
| `AutoHeight` | `true` |

```
With({ds: Filter([ddNV1.Selected.club_id, ddNV2.Selected.club_id, ddNV3.Selected.club_id, ddNV4.Selected.club_id, ddNV5.Selected.club_id, ddNV6.Selected.club_id, ddNV7.Selected.club_id, ddNV8.Selected.club_id, ddNV9.Selected.club_id, ddNV10.Selected.club_id], !IsBlank(Value))},
  If(CountRows(ds) = 0, "Em chưa chọn CLB nào.",
     CountRows(Distinct(ds, Value)) < CountRows(ds), "Có CLB bị chọn trùng.",
     ""))
```

## Phần 2 — Nút `btnNop`
3. Cây: bấm `conKhung_DangKy` → **+ Insert → Button** → đổi tên `btnNop`.
4. Thuộc tính:

| Thuộc tính | Dán |
|---|---|
| `Text` | `If(IsBlank(varNV), "Nộp nguyện vọng", "Cập nhật nguyện vọng")` |
| `DisplayMode` | `If(HetHan || !IsBlank(lblLoi.Text), DisplayMode.Disabled, DisplayMode.Edit)` |
| `Width` | `Parent.Width` |
| `Height` | `48` |
| `OnSelect` | khối dưới |

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

5. **Ctrl+S**.

## Giải thích ngắn (để tự sửa khi cần)
- Bỏ trống ô ở giữa → các lựa chọn tự **dồn lên** (`pref_1`, `pref_2`…).
- Nộp lại → **ghi đè** đúng dòng cũ (`Coalesce(LookUp…)`), không tạo dòng mới.
- Kiểm hạn chót **lần nữa** lúc bấm, phòng học sinh mở app từ trước hạn.

## Kiểm tra xong
- [ ] Không còn gạch đỏ ở `lblLoi`, `btnNop` (trừ `scrXacNhan` nếu chưa có — đã có từ PA05).
- ⚠️ Gạch đỏ ở `Blank()` → bật *Formula-level error management* (PA02 phần 4).
- ⚠️ Gạch đỏ ở `student_id` / `club_id` → thay bằng `Title`.
