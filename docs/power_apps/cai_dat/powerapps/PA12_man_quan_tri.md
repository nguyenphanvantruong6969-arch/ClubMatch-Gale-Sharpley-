# PA12 — Trang theo dõi cho giáo viên

[← PA11](PA11_man_chon_thi.md) · Tiếp theo: [PA13](PA13_man_dau_tien_va_chay_thu.md)

Mọi thứ thêm vào `conKhung_QuanTri`. Mỗi lần thêm: bấm `conKhung_QuanTri` ở cây bên trái trước.

## 1. Số học sinh đã nộp

Thêm «Text label». Tên:
```
lblQTSoLieu
```
**«Text»**:
```
CountRows(NguyenVong) & " / " & CountRows(HocSinh) & " học sinh đã nộp"
```
**«Size»**:
```
26
```
**«Width»**:
```
Parent.Width
```

## 2. Nút làm mới số liệu

Thêm «Button». Tên:
```
btnLamMoi
```
**«Text»**:
```
"Làm mới số liệu"
```
**«OnSelect»**:
```
Refresh(NguyenVong); Refresh(HocSinh)
```
**«Height»**:
```
48
```

## 3. Tiêu đề "Học sinh chưa nộp"

Thêm «Text label». Tên:
```
lblQTChuaNop
```
**«Text»**:
```
"Học sinh chưa nộp"
```
**«FontWeight»**:
```
FontWeight.Semibold
```

## 4. Danh sách học sinh chưa nộp

1. «+ Insert» → dán vào ô tìm:
```
Vertical gallery
```
2. Bấm «Vertical gallery» (danh sách cuộn dọc). Nếu hỏi chọn dữ liệu: chọn `HocSinh`.
3. Đổi tên thành:
```
galChuaNop
```
**«Items»**:
```
Filter(HocSinh, !(student_id in NguyenVong.student_id))
```
**«WrapCount»** (máy tính hiện 3 cột):
```
If(App.Width < 900, 1, 3)
```
**«TemplateSize»**:
```
50
```
**«Height»**:
```
400
```
**«Width»**:
```
Parent.Width
```
4. Bên trong danh sách, bấm vào dòng chữ đầu tiên. Mục **«Text»**:
```
ThisItem.student_id & " – " & ThisItem.name & " (" & ThisItem.class_id & ")"
```
5. Các thứ thừa trong dòng mẫu (dòng chữ thứ hai, ảnh, mũi tên): bấm vào → phím `Delete`.

## 5. Bảng đếm nguyện vọng 1 theo câu lạc bộ

1. Thêm «Vertical gallery» mới. Tên:
```
galThongKe
```
**«Items»**:
```
AddColumns(colCLB, NV1, CountRows(Filter(NguyenVong, pref_1 = club_id)))
```
**«Height»**:
```
400
```
**«Width»**:
```
Parent.Width
```
**«TemplateSize»**:
```
50
```
2. Bấm dòng chữ đầu tiên trong danh sách. Mục **«Text»**:
```
ThisItem.name & ":  " & ThisItem.NV1 & " NV1 / chỉ tiêu " & ThisItem.capacity
```
⚠️ Báo đỏ ở chữ `NV1` trong «Items»: dán bản này thay thế:
```
AddColumns(colCLB, "NV1", CountRows(Filter(NguyenVong, pref_1 = club_id)))
```

## 6. Nút mở bảng để tải dữ liệu về

Thêm «Button». Tên:
```
btnMoList
```
**«Text»**:
```
"Mở danh sách để xuất CSV"
```
**«OnSelect»** — dán, rồi **thay phần địa chỉ** bằng ĐỊA CHỈ TRANG của bạn (giữ nguyên đuôi `/Lists/NguyenVong`):
```
Launch("https://truong.sharepoint.com/sites/CLB-2026/Lists/NguyenVong")
```

Bấm `Ctrl` + `S`.

> Hình tam giác vàng hiện ở vài chỗ: đây chỉ là nhắc nhở với danh sách rất dài. Trường dưới 2000 học sinh thì không sao.

- [ ] Xong.
