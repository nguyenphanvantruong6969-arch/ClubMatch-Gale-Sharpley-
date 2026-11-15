# PA09 — Trang đăng ký: dòng báo lỗi và nút Nộp

[← PA08](PA08_dang_ky_o_chon.md) · Tiếp theo: [PA10](PA10_man_xac_nhan.md)

Thêm hai thứ vào `conKhung_DangKy`: dòng báo lỗi, rồi nút Nộp. Cả hai sẽ nằm **dưới** `conLuoi`.

**Cần có:** đã làm đủ 10 ô ở PA08 (`ddNV1` đến `ddNV10`). Thiếu ô nào thì đoạn dán dưới đây gạch đỏ ở tên ô đó.

Các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC: xem đầu tệp [PA05](PA05_tao_man_hinh_va_khung.md).

## Phần 1 — Dòng báo lỗi

1. Cây bên trái: bấm `conKhung_DangKy` (bấm đúng tên khung ngoài cùng, không bấm `conLuoi`).
2. THÊM ô chữ (`Text label`).
3. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblLoi
```
4. Bấm `lblLoi`, rồi ĐIỀN 5 MỤC sau:

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

👀 Trên trang ở giữa, dưới các ô chọn hiện chữ đỏ "Em chưa chọn CLB nào."

## Phần 2 — Nút Nộp

5. Cây bên trái: bấm `conKhung_DangKy`.
6. THÊM nút bấm (`Button`).
7. ĐỔI TÊN nút vừa thêm thành:
```
btnNop
```
8. Bấm `btnNop`, rồi ĐIỀN 5 MỤC sau:

**«Text»** — dán:
```
If(IsBlank(varNV), "Nộp nguyện vọng", "Cập nhật nguyện vọng")
```
**«DisplayMode»** — dán:
```
If(HetHan || IsBlank(varHS) || !IsBlank(lblLoi.Text), DisplayMode.Disabled, DisplayMode.Edit)
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
    With({cu: LookUp(NguyenVong, student_id = varHS.student_id)},
      With({kq: Patch(NguyenVong,
          If(IsBlank(cu), Defaults(NguyenVong), cu),
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
            so_lan_nop: Coalesce(cu.so_lan_nop, 0) + 1
          })},
        If(IsError(kq) || IsBlank(kq),
          Notify("Lưu thất bại, em thử lại hoặc báo giáo viên.", NotificationType.Error),
          Set(varNV, kq);
          Reset(ddNV1); Reset(ddNV2); Reset(ddNV3); Reset(ddNV4); Reset(ddNV5);
          Reset(ddNV6); Reset(ddNV7); Reset(ddNV8); Reset(ddNV9); Reset(ddNV10);
          Navigate(scrXacNhan, ScreenTransition.Fade))))))
```

👀 Trên trang ở giữa, dưới dòng chữ đỏ có nút "Nộp nguyện vọng", màu mờ (vì chưa chọn câu lạc bộ nào, và bạn không có trong bảng học sinh).

9. Bấm `Ctrl` + `S`.

## Nút này làm gì

- Học sinh bỏ trống một ô ở giữa: các lựa chọn tự **dồn lên trên**.
- Nộp lại lần nữa: **ghi đè** đúng phiếu cũ, không sinh phiếu mới; `so_lan_nop` tăng thêm 1.
- Kiểm tra hạn chót **một lần nữa** lúc bấm, phòng khi học sinh mở ứng dụng từ trước giờ hết hạn.
- Lưu xong, 10 ô chọn được đặt lại cho khớp với phiếu vừa lưu (để lần "Sửa lại" sau hiện đúng thứ tự đã dồn).
- Lưu không được thì báo lỗi và **ở lại trang**, không sang trang xác nhận.

## Kiểm tra

1. Bấm `lblLoi`, chọn mục «Text» ở thanh công thức, nhìn ô dài.
2. Bấm `btnNop`, chọn mục «OnSelect», nhìn ô dài.

👀 Cả hai nơi **không còn gạch chân đỏ nào** (trang `scrXacNhan` đã có từ PA05).

- [ ] Không còn gạch đỏ ở `lblLoi` và `btnNop`.

⚠️ Gạch đỏ ở `ddNV…`: ô mang số đó chưa được tạo hoặc đặt sai tên. Quay lại [PA08](PA08_dang_ky_o_chon.md), phần "Kiểm tra".
⚠️ Gạch đỏ ở `student_id` hoặc `club_id`: sửa chữ bị gạch thành `Title` (xem ⚠️ ở đầu [PA04](PA04_cong_thuc_app.md)).
⚠️ Về sau, học sinh nộp lại với **ít** câu lạc bộ hơn mà trên bảng `NguyenVong` các ô cũ không được xoá trống: tuỳ chọn «Formula-level error management» chưa bật. Làm lại [PA02](PA02_tao_app.md) bước 18 đến 20.
