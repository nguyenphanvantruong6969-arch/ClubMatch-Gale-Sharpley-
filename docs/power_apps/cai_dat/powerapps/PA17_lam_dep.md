# PA17 — Làm đẹp ứng dụng: màu trường, logo, phông chữ, bo góc, biểu tượng, hiệu ứng

[← PA12](PA12_man_quan_tri.md) · Tiếp theo: [PA13](PA13_man_dau_tien_va_chay_thu.md) · [Mục lục](../00_MUC_LUC.md)

**Làm tệp này sau PA12 (và sau PA16 nếu có làm bài thi), trước PA13.**

**Cần có:**
- Đã xong PA04 đến PA12.
- Tệp logo của trường, dạng `.png` (nền trong suốt càng tốt), lưu trên máy.
- Biết cách ĐỔI TÊN, THÊM, ĐIỀN MỤC (định nghĩa ở đầu [PA05](PA05_tao_man_hinh_va_khung.md)).

**Cách làm của tệp này:** mọi màu, phông chữ, độ bo góc, khoảng cách được khai báo **một lần** trong một "bảng giao diện" tên `Giao`. Các thứ trên màn hình chỉ trỏ tới bảng đó. Muốn đổi màu cả ứng dụng thì chỉ sửa một chỗ.

---

## Phần 1 — Lấy mã màu của trường từ logo

Mã màu là một chuỗi dạng `#1F4E79`. Cần lấy 2 màu: **màu chính** (màu chủ đạo của logo) và **màu nhấn** (màu phụ, nổi bật).

1. Bấm phím `Windows`, gõ `Paint`, bấm `Enter`.
2. Trong Paint, bấm `Ctrl` + `O`, chọn tệp logo, bấm «Open».
3. Trên thanh công cụ, bấm biểu tượng **ống hút màu** («Color picker»).
4. Bấm vào vùng có màu chủ đạo của logo.

👀 Ô «Color 1» trên thanh công cụ đổi sang màu vừa hút.

5. Bấm «Edit colors» (biểu tượng bảng màu cầu vồng, bên phải thanh công cụ).

👀 Hiện bảng chọn màu, có ô «Hex» chứa chuỗi 6 ký tự, ví dụ `1F4E79`.

6. Chép chuỗi đó vào sổ tay, đặt tên **MÀU CHÍNH**. Bấm «Cancel».
7. Làm lại bước 3 đến 6 với màu phụ của logo, đặt tên **MÀU NHẤN**.

⚠️ Paint không có ô «Hex» (Windows 10 bản cũ): dùng luôn màu mặc định ở Phần 2, bỏ qua bước sửa màu.
⚠️ Màu chính quá nhạt (vàng, xanh nhạt, hồng nhạt): chữ trắng trên nền đó sẽ khó đọc. Dùng màu đậm nhất trong logo làm MÀU CHÍNH, màu nhạt làm MÀU NHẤN.

---

## Phần 2 — Khai báo bảng giao diện `Giao`

### Trường hợp A — Ở PA04 bạn dùng mục «Formulas»

1. Cây bên trái: bấm «App».
2. Ô thả xuống nhỏ của thanh công thức: chọn «Formulas».
3. Bấm vào ô «fx», bấm `Ctrl` + `End` để đưa con trỏ xuống cuối cùng.
4. Bấm `Enter` hai lần để xuống dòng trống.
5. Dán đoạn sau (**không** bấm `Ctrl` + `A` trước, để không xoá đoạn cũ):
```
Giao = {
    TenTruong: "Trường THPT Mẫu",
    MauChinh: ColorValue("#1F4E79"),
    MauChinhDam: ColorValue("#163A5C"),
    MauNhan: ColorValue("#F2A900"),
    MauNen: ColorValue("#F4F6F9"),
    MauThe: ColorValue("#FFFFFF"),
    MauChu: ColorValue("#1F2937"),
    MauChuPhu: ColorValue("#6B7280"),
    MauVien: ColorValue("#D7DCE3"),
    MauLoi: ColorValue("#B42318"),
    MauDat: ColorValue("#1E7B4F"),
    Phong: Font.'Segoe UI',
    BoGoc: 12,
    BoGocNho: 8,
    Cach: 16,
    CachNho: 8,
    CaoDau: 72
};
```

👀 Không có gạch chân đỏ trong ô «fx».

⚠️ Gạch đỏ ở dòng ngay **trên** chữ `Giao =`: dòng đó thiếu dấu chấm phẩy ở cuối. Bấm vào cuối dòng đó, gõ `;`.

### Trường hợp B — Ở PA04 bạn dùng đoạn thay thế trong «OnStart»

1. Cây bên trái: «App». Ô thả xuống nhỏ: «OnStart».
2. Bấm vào ô «fx», bấm `Ctrl` + `Home` để đưa con trỏ lên **đầu** ô.
3. Dán đoạn sau (**không** bấm `Ctrl` + `A` trước):
```
Set(Giao, {
    TenTruong: "Trường THPT Mẫu",
    MauChinh: ColorValue("#1F4E79"),
    MauChinhDam: ColorValue("#163A5C"),
    MauNhan: ColorValue("#F2A900"),
    MauNen: ColorValue("#F4F6F9"),
    MauThe: ColorValue("#FFFFFF"),
    MauChu: ColorValue("#1F2937"),
    MauChuPhu: ColorValue("#6B7280"),
    MauVien: ColorValue("#D7DCE3"),
    MauLoi: ColorValue("#B42318"),
    MauDat: ColorValue("#1E7B4F"),
    Phong: Font.'Segoe UI',
    BoGoc: 12,
    BoGocNho: 8,
    Cach: 16,
    CachNho: 8,
    CaoDau: 72
});
```
4. Cây bên trái: đưa chuột vào «App», bấm «⋯» → «Run OnStart».

### Sửa cho đúng trường (cả hai trường hợp)

5. Trong đoạn vừa dán, bôi đen chữ `Trường THPT Mẫu` (giữ nguyên hai dấu ngoặc kép), gõ tên trường của bạn.
6. Bôi đen `1F4E79` ở dòng `MauChinh`, dán MÀU CHÍNH (chỉ 6 ký tự, giữ nguyên dấu `#`).
7. Bôi đen `F2A900` ở dòng `MauNhan`, dán MÀU NHẤN.
8. Dòng `MauChinhDam` (màu khi đưa chuột vào nút): để nguyên, hoặc dùng một màu cùng tông nhưng đậm hơn MÀU CHÍNH.
9. Bấm `Ctrl` + `S`.

### Đổi phông chữ (không bắt buộc)

Power Apps chỉ có sẵn một số phông, **không tải thêm phông riêng được**. Các phông dưới đây hiển thị đúng dấu tiếng Việt. Muốn đổi: bôi đen `Font.'Segoe UI'` trong đoạn ở trên rồi dán một dòng sau:

Phông mặc định, gọn, dễ đọc trên điện thoại (khuyên dùng):
```
Font.'Segoe UI'
```
Phông tròn, thân thiện:
```
Font.'Open Sans'
```
Phông có chân, trang trọng:
```
Font.Georgia
```

⚠️ Dán xong báo đỏ ở tên phông: phông đó không có trong bản Power Apps của bạn. Dán lại `Font.'Segoe UI'`.

### Bảng tra: các tên trong bảng giao diện

| Tên | Dùng cho |
|---|---|
| `Giao.TenTruong` | Tên trường trên thanh đầu trang |
| `Giao.MauChinh` | Thanh đầu trang, nút chính, tiêu đề |
| `Giao.MauChinhDam` | Nút khi đưa chuột vào hoặc bấm |
| `Giao.MauNhan` | Viền khi đang chọn, điểm nhấn |
| `Giao.MauNen` | Nền cả trang |
| `Giao.MauThe` | Nền tấm thẻ trắng chứa nội dung |
| `Giao.MauChu` | Chữ thường |
| `Giao.MauChuPhu` | Chữ phụ, chữ mờ |
| `Giao.MauVien` | Viền ô chọn, nút bị mờ |
| `Giao.MauLoi` | Chữ báo lỗi |
| `Giao.MauDat` | Chữ, biểu tượng báo thành công |
| `Giao.Phong` | Phông chữ |
| `Giao.BoGoc`, `Giao.BoGocNho` | Độ bo góc tấm thẻ, nút |
| `Giao.Cach`, `Giao.CachNho` | Khoảng cách lớn, nhỏ |
| `Giao.CaoDau` | Chiều cao thanh đầu trang |

---

## Phần 3 — Đưa logo vào ứng dụng

1. Trên máy, đổi tên tệp logo thành đúng tên dưới đây (chuột phải tệp → «Rename» → dán):
```
logo_truong.png
```
2. Trong màn hình thiết kế, dải biểu tượng dọc bên trái: bấm biểu tượng **hình ảnh** («Media»).

⚠️ Không thấy biểu tượng «Media»: bấm «⋯» (More) ở cuối dải biểu tượng, chọn «Media».

3. Bấm «Upload».
4. Chọn tệp `logo_truong.png` → bấm «Open».

👀 Trong khung «Media» có ảnh tên `logo_truong`.

⚠️ Tên hiện ra khác (ví dụ `logo_truong_1`): ở mọi chỗ dán `logo_truong` bên dưới, thay bằng đúng tên đang hiện.

---

## Phần 4 — Thanh đầu trang có logo và tên trường

Làm cho trang `scrDangKy` trước, rồi chép sang các trang khác.

### Tạo thanh đầu trang

1. Cây bên trái: bấm **tên trang** `scrDangKy` (bấm tên trang, **không** bấm khung `conKhung_DangKy`).
2. THÊM khung ngang: «Insert» → dán vào ô tìm `Horizontal container` → bấm «Horizontal container».

👀 Khung mới nằm **ngang hàng** với `conKhung_DangKy` ở cây bên trái, không thụt vào trong.

⚠️ Khung mới bị thụt vào trong `conKhung_DangKy`: bấm `Ctrl` + `Z`, làm lại bước 1 cho đúng.

3. ĐỔI TÊN khung mới thành:
```
conDau_DangKy
```
4. ĐIỀN MỤC **«X»**:
```
0
```
5. **«Y»**:
```
0
```
6. **«Width»**:
```
Parent.Width
```
7. **«Height»**:
```
Giao.CaoDau
```
8. **«Fill»**:
```
Giao.MauChinh
```
9. **«PaddingLeft»**:
```
Giao.Cach
```
10. **«PaddingRight»**:
```
Giao.Cach
```
11. **«LayoutGap»**:
```
Giao.CachNho
```
12. **«LayoutAlignItems»** (căn giữa theo chiều dọc):
```
LayoutAlignItems.Center
```

### Logo

13. Bấm `conDau_DangKy` → «Insert» → dán `Image` → bấm «Image».
14. ĐỔI TÊN thành:
```
imgLogo_DangKy
```
15. **«Image»**:
```
logo_truong
```
16. **«Width»**:
```
48
```
17. **«Height»**:
```
48
```
18. **«ImagePosition»**:
```
ImagePosition.Fit
```

### Tên trường

19. Bấm `conDau_DangKy` → THÊM ô chữ («Text label»).
20. ĐỔI TÊN thành:
```
lblTenTruong_DangKy
```
21. **«Text»**:
```
Giao.TenTruong & " · Đăng ký câu lạc bộ"
```
22. **«Color»**:
```
Color.White
```
23. **«Font»**:
```
Giao.Phong
```
24. **«FontWeight»**:
```
FontWeight.Semibold
```
25. **«Size»**:
```
If(LaPhone, 15, 20)
```
26. **«FillPortions»** (chiếm hết phần còn lại của thanh):
```
1
```

### Dời tấm thẻ nội dung xuống dưới thanh đầu trang

27. Bấm `conKhung_DangKy`. ĐIỀN MỤC **«Y»**:
```
Giao.CaoDau + Giao.Cach
```
28. **«Height»**:
```
Parent.Height - Giao.CaoDau - Giao.Cach
```

👀 Trang `scrDangKy` có một thanh màu trường ở trên cùng, logo bên trái, tên trường bên cạnh; nội dung nằm bên dưới, không bị che.

29. Bấm `Ctrl` + `S`.

### Chép thanh đầu trang sang các trang khác

30. Cây bên trái: chuột phải `conDau_DangKy` → «Copy».
31. Bấm **tên trang** `scrXacNhan` → bấm `Ctrl` + `V`.

👀 Có khung `conDau_DangKy_1` nằm ngang hàng với `conKhung_XacNhan`. **Không cần đổi tên** các thứ vừa dán.

32. Bấm `conKhung_XacNhan`, ĐIỀN MỤC **«Y»** và **«Height»** bằng đúng hai đoạn ở bước 27 và 28.
33. Làm lại bước 31 và 32 cho từng trang còn lại, mỗi lần dùng khung nội dung của trang đó:

| Trang | Khung nội dung cần sửa «Y» và «Height» |
|---|---|
| `scrKhongCoTen` | `conKhung_KhongCoTen` |
| `scrQuanTri` | `conKhung_QuanTri` |
| `scrChonThi` (nếu có) | `conKhung_ChonThi` |
| `scrBaiThi` (nếu có, PA16) | `conKhung_BaiThi` |

34. Bấm `Ctrl` + `S`.

---

## Phần 5 — Nền trang và tấm thẻ bo góc

### Nền trang

1. Cây bên trái: giữ phím `Ctrl`, bấm lần lượt **tên tất cả các trang** (`scrKhongCoTen`, `scrDangKy`, `scrXacNhan`, `scrQuanTri`, và `scrChonThi`, `scrBaiThi` nếu có).

👀 Các tên trang cùng được tô sáng.

⚠️ Chỉ một trang được tô sáng: bản Power Apps của bạn không cho chọn nhiều trang. Làm bước 2 cho **từng trang một**.

2. ĐIỀN MỤC **«Fill»**:
```
Giao.MauNen
```

### Tấm thẻ trắng bo góc cho nội dung

Làm lần lượt cho từng khung nội dung: `conKhung_DangKy`, `conKhung_XacNhan`, `conKhung_KhongCoTen`, `conKhung_QuanTri`, `conKhung_ChonThi` (nếu có), `conKhung_BaiThi` (nếu có).

3. Bấm tên khung. ĐIỀN MỤC **«Fill»**:
```
Giao.MauThe
```
4. **«RadiusTopLeft»**:
```
Giao.BoGoc
```
5. **«RadiusTopRight»**:
```
Giao.BoGoc
```
6. **«RadiusBottomLeft»**:
```
Giao.BoGoc
```
7. **«RadiusBottomRight»**:
```
Giao.BoGoc
```
8. **«DropShadow»** (bóng mờ nhẹ dưới thẻ):
```
DropShadow.Light
```
9. **«PaddingLeft»**:
```
Giao.Cach
```
10. **«PaddingRight»**:
```
Giao.Cach
```
11. **«LayoutGap»**:
```
Giao.Cach
```

👀 Nội dung nằm trên một tấm thẻ trắng, góc bo tròn, có bóng mờ, nổi trên nền xám nhạt.

⚠️ Khung không có mục «DropShadow»: bỏ qua bước 8, thay bằng hai mục sau:

**«BorderColor»**:
```
Giao.MauVien
```
**«BorderThickness»**:
```
1
```

12. Bấm `Ctrl` + `S`.

---

## Phần 6 — Chữ

### Tiêu đề

Làm cho từng ô chữ tiêu đề: `lblChao`, `lblXNTieuDe`, `lblQTSoLieu` (và `lblBTTieuDe` nếu có PA16).

1. Bấm tên ô chữ. ĐIỀN MỤC **«Font»**:
```
Giao.Phong
```
2. **«Color»**:
```
Giao.MauChinh
```
3. **«FontWeight»**:
```
FontWeight.Bold
```

### Chữ thường

Làm cho từng ô chữ còn lại trên mỗi trang (mọi tên bắt đầu bằng `lbl`, **trừ** `lblLoi`, các ô chữ tiêu đề ở trên và `lblTenTruong_…`). Trên cùng một trang có thể giữ `Ctrl` và bấm nhiều tên để điền một lần.

4. ĐIỀN MỤC **«Font»**:
```
Giao.Phong
```
5. **«Color»**:
```
Giao.MauChu
```

### Chữ phụ (hạn chót, lời dặn)

6. Bấm `lblHuongDan`, ĐIỀN MỤC **«Color»**:
```
Giao.MauChuPhu
```

### Dòng báo lỗi

7. Bấm `lblLoi`. ĐIỀN MỤC **«Font»**:
```
Giao.Phong
```
8. **«Color»**:
```
Giao.MauLoi
```

9. Bấm `Ctrl` + `S`.

---

## Phần 7 — Nút bấm

Làm cho **từng trang**. Trên mỗi trang: giữ `Ctrl`, bấm lần lượt tên tất cả các nút (tên bắt đầu bằng `btn`) của trang đó ở cây bên trái, rồi điền một lần cho cả nhóm.

| Trang | Các nút |
|---|---|
| `scrDangKy` | `btnNop`, `btnSangThi` (nếu có), `btnSangBaiThi` (nếu có) |
| `scrXacNhan` | `btnSuaLai` |
| `scrQuanTri` | `btnLamMoi`, `btnMoList`, và các nút chấm điểm của PA16 nếu có |
| `scrChonThi` | `btnLuuThi`, `btnVeDangKy` |
| `scrBaiThi` | mọi nút `btn…` của trang |

⚠️ Bản Power Apps của bạn không cho chọn nhiều nút: điền cho từng nút một.

1. ĐIỀN MỤC **«Fill»**:
```
Giao.MauChinh
```
2. **«HoverFill»** (màu khi đưa chuột vào):
```
Giao.MauChinhDam
```
3. **«PressedFill»** (màu khi đang bấm):
```
Giao.MauChinhDam
```
4. **«DisabledFill»** (màu khi nút bị mờ):
```
Giao.MauVien
```
5. **«Color»**:
```
Color.White
```
6. **«DisabledColor»**:
```
Giao.MauChuPhu
```
7. **«Font»**:
```
Giao.Phong
```
8. **«FontWeight»**:
```
FontWeight.Semibold
```
9. **«RadiusTopLeft»**:
```
Giao.BoGocNho
```
10. **«RadiusTopRight»**:
```
Giao.BoGocNho
```
11. **«RadiusBottomLeft»**:
```
Giao.BoGocNho
```
12. **«RadiusBottomRight»**:
```
Giao.BoGocNho
```
13. **«BorderThickness»**:
```
0
```
14. **«FocusedBorderColor»** (viền khi chọn bằng bàn phím):
```
Giao.MauNhan
```
15. **«FocusedBorderThickness»**:
```
3
```

### Nút phụ (nút quay lại, nút sửa lại)

Nút phụ dùng nền trắng, viền màu trường, để không tranh chỗ với nút chính. Làm cho `btnSuaLai`, `btnVeDangKy` (nếu có), `btnMoList`.

16. Bấm tên nút. ĐIỀN MỤC **«Fill»**:
```
Giao.MauThe
```
17. **«HoverFill»**:
```
Giao.MauNen
```
18. **«Color»**:
```
Giao.MauChinh
```
19. **«BorderColor»**:
```
Giao.MauChinh
```
20. **«BorderThickness»**:
```
2
```

👀 Nút chính màu trường, chữ trắng, góc bo; đưa chuột vào thì đậm lên. Nút Nộp khi chưa chọn câu lạc bộ thì xám.

21. Bấm `Ctrl` + `S`.

---

## Phần 8 — Ô chọn câu lạc bộ

1. Cây bên trái, trang `scrDangKy`: giữ `Ctrl`, bấm lần lượt `ddNV1`, `ddNV2`, … `ddNV10`.

⚠️ Mỗi ô chọn nằm trong một khung con (`conNV1`…), có thể phải bấm mũi tên nhỏ cạnh tên khung để thấy tên ô chọn.

2. ĐIỀN MỤC **«Fill»**:
```
Giao.MauThe
```
3. **«Color»**:
```
Giao.MauChu
```
4. **«Font»**:
```
Giao.Phong
```
5. **«BorderColor»**:
```
Giao.MauVien
```
6. **«BorderThickness»**:
```
1
```
7. **«HoverBorderColor»**:
```
Giao.MauChinh
```
8. **«ChevronBackground»** (nền của mũi tên thả xuống):
```
Giao.MauThe
```
9. **«ChevronFill»** (màu mũi tên):
```
Giao.MauChinh
```
10. **«SelectionFill»** (nền dòng đang chọn trong danh sách):
```
Giao.MauChinh
```
11. **«SelectionColor»**:
```
Color.White
```
12. **«HoverFill»**:
```
Giao.MauNen
```
13. Nếu có trang `scrChonThi`: làm lại bước 1 đến 12, ở bước 1 chọn `ddThi1` … `ddThi5`.
14. Bấm `Ctrl` + `S`.

⚠️ Một mục bên trên không có trong ô thả xuống: bỏ qua mục đó, làm tiếp mục sau. Ô chọn kiểu cũ **không bo góc được**; đây là giới hạn của Power Apps.

### Nhãn "Nguyện vọng 1, 2, …"

15. Giữ `Ctrl`, bấm `lblNV1` … `lblNV10`. ĐIỀN MỤC **«Color»**:
```
Giao.MauChuPhu
```
16. **«FontWeight»**:
```
FontWeight.Semibold
```
17. **«Font»**:
```
Giao.Phong
```

---

## Phần 9 — Biểu tượng

### Dấu tích lớn ở trang xác nhận

1. Bấm `conKhung_XacNhan` → «Insert» → dán vào ô tìm:
```
Check badge
```
2. Bấm biểu tượng «Check badge» (huy hiệu có dấu tích).

⚠️ Không có kết quả: «Insert» → «Icons» → kéo xuống tìm hình dấu tích (tên «Check»).

3. ĐỔI TÊN thành:
```
icoXacNhan
```
4. ĐIỀN MỤC **«Color»**:
```
Giao.MauDat
```
5. **«Width»**:
```
72
```
6. **«Height»**:
```
72
```
7. **«AlignInContainer»** (đặt giữa):
```
AlignInContainer.Center
```
8. Cây bên trái: chuột phải `icoXacNhan` → «Reorder» → «Bring to front» (bản khác ghi «Move to top»).

👀 Dấu tích xanh nằm trên cùng tấm thẻ, phía trên chữ "Đã lưu nguyện vọng".

⚠️ Dấu tích vẫn nằm dưới cùng: kéo tên `icoXacNhan` ở cây bên trái lên trên `lblXNTieuDe`.

### Biểu tượng cảnh báo ở trang "không có tên"

9. Bấm `conKhung_KhongCoTen` → «Insert» → dán:
```
Warning
```
10. Bấm biểu tượng «Warning» (hình tam giác có dấu chấm than). ĐỔI TÊN thành:
```
icoCanhBao
```
11. **«Color»**:
```
Giao.MauLoi
```
12. **«Width»**:
```
64
```
13. **«Height»**:
```
64
```
14. **«AlignInContainer»**:
```
AlignInContainer.Center
```
15. Đưa `icoCanhBao` lên trên `lblKhongCoTen` như bước 8.

### Biểu tượng làm mới ở trang giáo viên

16. Bấm `btnLamMoi`. ĐIỀN MỤC **«Text»**:
```
"⟳  Làm mới số liệu"
```

17. Bấm `Ctrl` + `S`.

---

## Phần 10 — Danh sách cuộn ở trang giáo viên

Làm cho `galChuaNop` và `galThongKe`.

1. Bấm tên danh sách. ĐIỀN MỤC **«TemplateFill»** (nền từng dòng, xen kẽ trắng và xám nhạt):
```
If(Mod(ThisItem.ID, 2) = 0, Giao.MauNen, Giao.MauThe)
```
2. **«TemplatePadding»**:
```
4
```

⚠️ Báo đỏ ở `ThisItem.ID`: dán bản đơn giản này thay thế:
```
Giao.MauThe
```

3. Bấm `Ctrl` + `S`.

---

## Phần 11 — Hiệu ứng chuyển trang

Power Apps **không có** hoạt hình tự do. Hiệu ứng dùng được: đổi màu khi đưa chuột vào nút (đã làm ở Phần 7) và hiệu ứng khi chuyển trang dưới đây.

1. Bấm `btnSuaLai`. ĐIỀN MỤC **«OnSelect»** (trang trượt về từ bên trái):
```
Navigate(scrDangKy, ScreenTransition.UnCover)
```
2. Nếu có `btnSangThi`: **«OnSelect»**:
```
Navigate(scrChonThi, ScreenTransition.Cover)
```
3. Nếu có `btnVeDangKy`: **«OnSelect»**:
```
Navigate(scrDangKy, ScreenTransition.UnCover)
```

**Không sửa** «OnSelect» của `btnNop`: đoạn đó dài, đã có sẵn hiệu ứng mờ dần (`ScreenTransition.Fade`) khi sang trang xác nhận.

4. Bấm `Ctrl` + `S`.

---

## Phần 12 — Kiểm tra

1. Bấm trang `scrDangKy` ở cây bên trái, bấm nút **▶** (góc trên bên phải, «Preview»).

| Kiểm | Đúng là |
|---|---|
| Thanh đầu trang | Màu trường, logo rõ, tên trường không bị cắt |
| Tấm thẻ | Nền trắng, bo góc, nổi trên nền xám nhạt |
| Chữ | Cùng một phông; tiêu đề màu trường; lời dặn màu xám |
| Nút Nộp khi chưa chọn | Xám, không bấm được |
| Nút Nộp khi đã chọn | Màu trường, đưa chuột vào thì đậm lên |
| Ô chọn | Viền xám, mũi tên màu trường, dòng đang chọn màu trường |

2. Bấm `Esc`. Thu hẹp cửa sổ trình duyệt còn khoảng một nửa, chạy thử lại.

👀 Tên trường nhỏ lại cho vừa, logo không méo, các ô chọn xếp một cột.

⚠️ Tên trường bị cắt trên điện thoại: rút ngắn `TenTruong` trong bảng `Giao` (ví dụ "THPT Mẫu").
⚠️ Chữ trên nút khó đọc: MÀU CHÍNH quá nhạt, xem cảnh báo ở Phần 1.

3. Bấm `Ctrl` + `S`. Sang [PA13](PA13_man_dau_tien_va_chay_thu.md).

- [ ] Có màu trường, logo, phông chữ thống nhất.
- [ ] Có tấm thẻ bo góc, nút bo góc, khoảng cách đều.
- [ ] Có biểu tượng ở trang xác nhận và trang "không có tên".
- [ ] Có hiệu ứng đổi màu nút và chuyển trang.

---

**Muốn đổi giao diện sau này:** chỉ sửa bảng `Giao` (Phần 2), bấm `Ctrl` + `S`, rồi phát hành lại (PA14). Không phải sửa từng nút.
