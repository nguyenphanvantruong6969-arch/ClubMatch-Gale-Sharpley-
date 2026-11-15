# PA11 — Màn chọn CLB thi (tuỳ chọn)

⏱ 20 phút · [← PA10](PA10_man_xac_nhan.md) · Tiếp: [PA12](PA12_man_quan_tri.md)

**Bỏ qua** nếu không có List `ChonThi` (đã bỏ SP07).

## Phần 1 — 5 ô chọn
Làm giống PA08 nhưng trong `conKhung_ChonThi`, với tên:
- Lưới: `conLuoiThi`
- Ô: `conThi1…5`, `lblThi1…5` (`Text` = `"CLB thi 1"`…), `ddThi1…5`
- `ddThik`:
  - `Items` = `Filter(colCLB, co_thi)`
  - `Value` = `name`
  - `AllowEmptySelection` = `true`
  - `Default` = `LookUp(colCLB, club_id = LookUp(ChonThi, student_id = varHS.student_id).test_club_k).name` *(thay `k` bằng 1…5)*
  - `DisplayMode` = `If(HetHan, DisplayMode.View, DisplayMode.Edit)`
- `conThik.Visible` = `true` (luôn hiện 5 ô), `conLuoiThi.Height` = `If(LaPhone, 450, 270)`.

## Phần 2 — Nút `btnLuuThi`
`Text` = `"Lưu CLB thi"` · `Width` = `Parent.Width` · `Height` = `48` · `OnSelect` =
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

## Phần 3 — Nút chuyển màn
- Trong `conKhung_DangKy`, chèn Button `btnSangThi` ngay dưới `lblHuongDan`: `Text` = `"Chọn CLB thi tuyển →"`, `OnSelect` = `Navigate(scrChonThi)`.
- Trong `conKhung_ChonThi`, chèn Button `btnVeDangKy` ở trên cùng: `Text` = `"← Nguyện vọng"`, `OnSelect` = `Navigate(scrDangKy)`.

**Ctrl+S.**

⚠️ Học sinh đổi CLB thi sau khi giáo viên đã nhập điểm → cặp CLB/điểm có thể lệch. Đặt hạn chọn thi **sớm hơn** ngày chấm, hoặc giáo viên nhập điểm theo tên CLB.

- [ ] Xong.
