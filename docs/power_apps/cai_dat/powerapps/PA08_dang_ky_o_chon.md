# PA08 — Trang đăng ký: 10 ô chọn câu lạc bộ

[← PA07](PA07_dang_ky_phan_tren.md) · Tiếp theo: [PA09](PA09_dang_ky_nut_nop.md)

Làm **ô 1 thật kỹ**, chạy thử thấy đúng, rồi mới nhân ra 9 ô còn lại. **Luôn làm đủ 10 ô**, kể cả khi trường chỉ cho chọn 5: ứng dụng tự ẩn các ô thừa.

Các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC: xem đầu tệp [PA05](PA05_tao_man_hinh_va_khung.md).

**Trước khi bắt đầu:** cây bên trái → đưa chuột vào «App» → «⋯» → «Run OnStart» (để danh sách câu lạc bộ được nạp).

## Phần 1 — Khung chứa các ô

1. Cây bên trái: bấm `conKhung_DangKy`.
2. THÊM khung ngang (dán vào ô tìm):
```
Horizontal container
```
3. ĐỔI TÊN khung vừa thêm thành:
```
conLuoi
```
4. Bấm `conLuoi`, rồi ĐIỀN 4 MỤC sau:

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
If(LaPhone, 90 * SoNguyenVongToiDa, 90 * RoundUp(SoNguyenVongToiDa / 2, 0))
```

👀 Trên trang ở giữa, dưới lời dặn có một khung trống.

## Phần 2 — Ô số 1

5. Cây bên trái: bấm `conLuoi`.
6. THÊM khung dọc (`Vertical container`).
7. ĐỔI TÊN khung vừa thêm thành:
```
conNV1
```
8. Bấm `conNV1`, rồi ĐIỀN 3 MỤC sau:

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

9. Cây bên trái: bấm `conNV1`.
10. THÊM ô chữ (`Text label`).
11. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblNV1
```
12. Bấm `lblNV1`, rồi ĐIỀN 3 MỤC sau:

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

13. Cây bên trái: bấm `conNV1`.
14. Trên thanh lệnh bấm «Insert», bấm vào ô tìm kiếm, dán:
```
Drop down
```
15. Bấm dòng «Drop down» trong kết quả. Có hai dòng: bấm dòng nằm dưới chữ «Classic».

👀 Ở cây bên trái, dưới `conNV1` có thêm «Dropdown1» (số có thể khác), nằm sau `lblNV1`.

16. ĐỔI TÊN ô thả xuống vừa thêm thành:
```
ddNV1
```
17. Bấm `ddNV1`, rồi ĐIỀN 7 MỤC sau:

**«Items»** — dán:
```
colCLB
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

⚠️ Không điền được mục «Value» bằng cách dán: bấm `ddNV1`, ở khung bên phải bấm thẻ «Properties», bấm ô thả xuống «Value», chọn `name`.
⚠️ Ô thả xuống của bạn **không có** các mục «Value», «Default», «AllowEmptySelection»: bạn đã thêm nhầm bộ mới. Bấm chuột phải `ddNV1` → «Delete». Làm lại [PA02](PA02_tao_app.md) bước 23 đến 25 (tắt «Modern controls and themes»), rồi làm lại từ bước 13.

18. Bấm `Ctrl` + `S`.
19. Cây bên trái: bấm `scrDangKy`.
20. Bấm nút **▶** ở đầu bên phải thanh lệnh (hoặc phím `F5`).

👀 Ứng dụng chạy thử, hiện trang đăng ký có một ô "Nguyện vọng 1".

21. Bấm vào ô thả xuống dưới chữ "Nguyện vọng 1".

👀 Xổ ra danh sách **tên** các câu lạc bộ, xếp theo vần.

22. Bấm phím `Esc` (hoặc dấu X ở góc trên bên phải) để thoát chạy thử.

⚠️ Danh sách trống: thoát chạy thử, làm lại dòng "Trước khi bắt đầu", rồi thử lại. Vẫn trống: bảng `CLB` chưa có dữ liệu, xem [SP08](../sharepoint/SP08_nap_excel.md).
⚠️ Danh sách hiện mã (`clb_bongro`) thay cho tên: mục «Value» chưa đúng, điền lại.

## Phần 3 — Nhân ra ô 2 đến ô 10

Với **mỗi** ô từ 2 đến 10, làm đủ 9 bước sau. Các ô xám của từng ô nằm ở danh sách bên dưới.

23. Cây bên trái: bấm chuột phải `conNV1`, bấm «Copy».
24. Cây bên trái: bấm một lần vào `conLuoi`.
25. Bấm `Ctrl` + `V`.

👀 Dưới `conLuoi` xuất hiện một khung mới tên `conNV1_1` (đuôi số có thể khác), bên trong có một ô chữ và một ô thả xuống cũng mang đuôi số.

26. ĐỔI TÊN khung mới (ô xám thứ 1 của ô đó).
27. ĐỔI TÊN ô chữ bên trong khung mới (ô xám thứ 2).
28. ĐỔI TÊN ô thả xuống bên trong khung mới (ô xám thứ 3).
29. Bấm khung mới, ĐIỀN MỤC «Visible» (ô xám thứ 4).
30. Bấm ô chữ bên trong, ĐIỀN MỤC «Text» (ô xám thứ 5).
31. Bấm ô thả xuống bên trong, ĐIỀN MỤC «Default» (ô xám thứ 6).

Cứ xong 2 ô thì bấm `Ctrl` + `S`.

⚠️ Sau bước 25, khung mới **không** nằm thụt dưới `conLuoi`: bấm `Ctrl` + `Z`, làm lại bước 24 (phải thấy `conLuoi` được tô sáng) rồi bước 25.

### Ô 2

Thứ 1 — tên khung:
```
conNV2
```
Thứ 2 — tên ô chữ:
```
lblNV2
```
Thứ 3 — tên ô thả xuống:
```
ddNV2
```
Thứ 4 — `conNV2`, mục **«Visible»**:
```
2 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV2`, mục **«Text»**:
```
"Nguyện vọng 2"
```
Thứ 6 — `ddNV2`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_2).name
```

### Ô 3

Thứ 1 — tên khung:
```
conNV3
```
Thứ 2 — tên ô chữ:
```
lblNV3
```
Thứ 3 — tên ô thả xuống:
```
ddNV3
```
Thứ 4 — `conNV3`, mục **«Visible»**:
```
3 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV3`, mục **«Text»**:
```
"Nguyện vọng 3"
```
Thứ 6 — `ddNV3`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_3).name
```

### Ô 4

Thứ 1 — tên khung:
```
conNV4
```
Thứ 2 — tên ô chữ:
```
lblNV4
```
Thứ 3 — tên ô thả xuống:
```
ddNV4
```
Thứ 4 — `conNV4`, mục **«Visible»**:
```
4 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV4`, mục **«Text»**:
```
"Nguyện vọng 4"
```
Thứ 6 — `ddNV4`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_4).name
```

### Ô 5

Thứ 1 — tên khung:
```
conNV5
```
Thứ 2 — tên ô chữ:
```
lblNV5
```
Thứ 3 — tên ô thả xuống:
```
ddNV5
```
Thứ 4 — `conNV5`, mục **«Visible»**:
```
5 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV5`, mục **«Text»**:
```
"Nguyện vọng 5"
```
Thứ 6 — `ddNV5`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_5).name
```

### Ô 6

Thứ 1 — tên khung:
```
conNV6
```
Thứ 2 — tên ô chữ:
```
lblNV6
```
Thứ 3 — tên ô thả xuống:
```
ddNV6
```
Thứ 4 — `conNV6`, mục **«Visible»**:
```
6 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV6`, mục **«Text»**:
```
"Nguyện vọng 6"
```
Thứ 6 — `ddNV6`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_6).name
```

### Ô 7

Thứ 1 — tên khung:
```
conNV7
```
Thứ 2 — tên ô chữ:
```
lblNV7
```
Thứ 3 — tên ô thả xuống:
```
ddNV7
```
Thứ 4 — `conNV7`, mục **«Visible»**:
```
7 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV7`, mục **«Text»**:
```
"Nguyện vọng 7"
```
Thứ 6 — `ddNV7`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_7).name
```

### Ô 8

Thứ 1 — tên khung:
```
conNV8
```
Thứ 2 — tên ô chữ:
```
lblNV8
```
Thứ 3 — tên ô thả xuống:
```
ddNV8
```
Thứ 4 — `conNV8`, mục **«Visible»**:
```
8 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV8`, mục **«Text»**:
```
"Nguyện vọng 8"
```
Thứ 6 — `ddNV8`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_8).name
```

### Ô 9

Thứ 1 — tên khung:
```
conNV9
```
Thứ 2 — tên ô chữ:
```
lblNV9
```
Thứ 3 — tên ô thả xuống:
```
ddNV9
```
Thứ 4 — `conNV9`, mục **«Visible»**:
```
9 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV9`, mục **«Text»**:
```
"Nguyện vọng 9"
```
Thứ 6 — `ddNV9`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_9).name
```

### Ô 10

Thứ 1 — tên khung:
```
conNV10
```
Thứ 2 — tên ô chữ:
```
lblNV10
```
Thứ 3 — tên ô thả xuống:
```
ddNV10
```
Thứ 4 — `conNV10`, mục **«Visible»**:
```
10 <= SoNguyenVongToiDa
```
Thứ 5 — `lblNV10`, mục **«Text»**:
```
"Nguyện vọng 10"
```
Thứ 6 — `ddNV10`, mục **«Default»**:
```
LookUp(colCLB, club_id = varNV.pref_10).name
```

## Kiểm tra

1. Ở cây bên trái, mở `conLuoi`.

👀 Có đủ `conNV1` đến `conNV10`. Mở từng khung: bên trong là `lblNV…` và `ddNV…` **cùng số** với khung.

2. Bấm `scrDangKy`, bấm **▶**.

👀 Cửa sổ rộng: các ô xếp 2 cột. Kéo cửa sổ trình duyệt cho hẹp lại: các ô xếp 1 cột. Số ô hiện ra bằng `SoNguyenVongToiDa` đã điền ở PA04.

3. Bấm `Esc`, bấm `Ctrl` + `S`.

- [ ] Đủ 10 khung, tên cùng số.
- [ ] Chạy thử đúng số ô, co giãn đúng.
