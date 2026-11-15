# Hướng dẫn dựng app đăng ký CLB trên Power Apps (phương án A)

> **Mục đích:** học sinh nộp nguyện vọng CLB qua một Canvas app (dùng được trên điện thoại và laptop), dữ liệu lưu ở SharePoint, giáo viên xuất CSV rồi nạp vào **rbda-kiosk** để xếp CLB bằng RB-DA như hiện nay.
> **Không** chạy thuật toán trong Power Apps. Không đổi mã nguồn kiosk, không đổi hợp đồng cột CSV (bất biến 7).
> Tài liệu vận hành, chưa gắn mã mục trong sổ đăng ký (chờ Truong chọn).

---

## 0. Tổng quan

```
Học sinh (phone/laptop) ──► Canvas app ──► SharePoint Lists ──► Xuất CSV ──► rbda-kiosk (RB-DA)
Giáo viên ──► màn hình Quản trị (theo dõi, nhập điểm thi) ─┘
```

| Thành phần | Dùng gì | Giấy phép |
|---|---|---|
| Giao diện | Canvas app, khổ Tablet, tắt Scale to fit (co giãn) | Chuẩn M365 Education |
| Dữ liệu | 4 SharePoint List | Chuẩn |
| Đăng nhập | Tài khoản Microsoft của trường (`User().Email`) | Chuẩn |
| Xếp CLB | rbda-kiosk trên Windows | — |

**Không dùng Dataverse** (thường cần premium). Mọi kết nối ở đây là connector chuẩn.

### Việc cần chuẩn bị
- [ ] Quyền tạo (hoặc được cấp) một SharePoint site, ví dụ `CLB-2026`.
- [ ] Danh sách học sinh: Mã HS, Họ tên, Lớp, **email trường**, Nhóm ưu tiên (nếu có).
- [ ] Danh sách CLB: Mã CLB, Tên, Chỉ tiêu, Suất ưu tiên, Nhóm ưu tiên.
- [ ] Hạn chót nộp nguyện vọng.
- [ ] Email các giáo viên quản trị.

---

## 1. Tạo SharePoint site và 4 List

Vào SharePoint → **Create site → Team site** (hoặc nhờ IT). Trong site: **New → List → Blank list**.

> Quy tắc đặt tên cột: đặt **đúng** tên dưới đây (chữ thường, có gạch dưới). Khi xuất CSV, SharePoint dùng tên hiển thị làm tiêu đề cột, nên đặt đúng ngay từ đầu thì CSV khớp kiosk không cần sửa.
> Cột `Title` có sẵn: **đổi tên hiển thị** (List settings → bấm `Title` → Column name), không xoá.

### 1.1. List `CLB`
| Cột | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `club_id` (đổi tên từ Title) | Single line | ✅ | Mã khớp kiosk, ví dụ `clb_bongro`. Không dấu, không cách |
| `name` | Single line | ✅ | Tên hiện cho học sinh |
| `capacity` | Number (0 chữ số thập phân) | ✅ | Chỉ tiêu |
| `reserve_capacity` | Number | | Suất ưu tiên, nằm **trong** capacity. Mặc định 0 |
| `reserve_group` | Single line | | Ví dụ `chinh_sach` |
| `mo_ta` | Multiple lines | | Giới thiệu CLB (chỉ dùng trong app) |
| `co_thi` | Yes/No | | CLB có thi tuyển (Tier 1) |

Thứ tự cột 5 cột đầu đúng như trên ⇒ xuất CSV là file `05_danh_sach_club.csv` mà kiosk nhận được (kiosk nhận ra nhờ có `club_id` + `capacity`). Ẩn `mo_ta`, `co_thi` khỏi view trước khi xuất, hoặc xoá hai cột đó trong file CSV.

### 1.2. List `HocSinh` (danh sách gốc, giáo viên nạp sẵn)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| `student_id` (đổi tên từ Title) | Single line | Mã HS, không trùng. Bật **Enforce unique values** |
| `name` | Single line | Họ tên |
| `class_id` | Single line | Lớp, ví dụ `10A2` |
| `email` | Single line | Email trường, **chữ thường**. Bật Enforce unique values + Indexed |
| `reserve_group` | Single line | Để trống nếu không thuộc nhóm ưu tiên |

Nạp nhanh: chuẩn bị Excel đúng các cột trên → trong SharePoint chọn **New → List → From Excel**, hoặc mở list ở **Edit in grid view** và dán.

### 1.3. List `NguyenVong` (app ghi vào)
| Cột | Kiểu | Ghi chú |
|---|---|---|
| `student_id` (đổi tên từ Title) | Single line | Indexed, unique |
| `name` | Single line | |
| `pref_1` … `pref_10` | Single line (10 cột) | Mã CLB, `pref_1` là thích nhất |
| `email` | Single line | Ai nộp |
| `nop_luc` | Date and time | Lần nộp cuối |
| `so_lan_nop` | Number | Đếm số lần sửa |

> Trường chỉ cho chọn tối đa N CLB (ví dụ 5): vẫn tạo đủ 10 cột, app chỉ hiện N ô.
> Trường **nhiều buổi**: thay `pref_k` bằng `<buoi>_pref_k` (ví dụ `thu_2_pref_1`), mỗi buổi một nhóm cột; xem phụ lục C.

### 1.4. List `ChonThi` (tuỳ chọn, chỉ khi có CLB thi tuyển)
| Cột | Kiểu |
|---|---|
| `student_id` (đổi tên từ Title) | Single line, unique |
| `name` | Single line |
| `test_club_1`, `score_1`, … `test_club_5`, `score_5` | `test_club_k`: Single line; `score_k`: Number (1 chữ số thập phân) |

Học sinh chỉ chọn CLB muốn thi (`test_club_k`); **điểm do giáo viên nhập** sau khi chấm (`score_k`). Học sinh không được sửa cột điểm (xem mục 7).

### 1.5. Phân quyền SharePoint
- Học sinh: quyền **Contribute** trên `NguyenVong`, `ChonThi`; **Read** trên `CLB`; **Read** trên `HocSinh`.
- Để học sinh không xem được nguyện vọng của bạn: `NguyenVong` → List settings → **Advanced settings → Item-level permissions**: *Read items that were created by the user*, *Create items and edit items that were created by the user*. Làm tương tự với `ChonThi`.
- Giáo viên quản trị: **Full control** (hoặc Edit) toàn site.

---

## 2. Tạo app

1. Power Apps → **Create → Create from blank** (Canvas). Đặt tên `DangKyCLB`, **Format: Tablet**.
2. **Settings → Display**: tắt **Scale to fit**, tắt **Lock aspect ratio**, tắt **Lock orientation**. App giờ theo kích thước cửa sổ: phone hay laptop đều dùng được.
3. **Data (biểu tượng trụ) → Add data → SharePoint** → chọn site → tick `CLB`, `HocSinh`, `NguyenVong` (và `ChonThi` nếu dùng).
4. **Settings → Upcoming features**: bật **Modern controls** nếu muốn giao diện mới (công thức dưới đây viết cho control cổ điển, chạy được cả hai; khác biệt ghi chú tại chỗ).

> Nếu thanh công thức không chấp nhận `club_id` / `student_id`, thay bằng `Title` (tên nội bộ của cột đã đổi tên).

---

## 3. Công thức dùng chung (App)

Chọn **App** ở cây bên trái.

### 3.1. `App.Formulas` (giá trị tự cập nhật)
```
HanChot = DateTimeValue("2026-12-01 17:00");
SoNguyenVongToiDa = 5;
DSQuanTri = ["gv.a@truong.edu.vn", "gv.b@truong.edu.vn"];
EmailToi = Lower(User().Email);
LaQuanTri = EmailToi in DSQuanTri;
HetHan = Now() > HanChot;
LaPhone = App.Width < 600;
```
Sửa hạn chót, số nguyện vọng tối đa, email quản trị tại đây.

### 3.2. `App.OnStart`
```
Set(varHS, LookUp(HocSinh, email = EmailToi));
Set(varNV, LookUp(NguyenVong, student_id = varHS.student_id));
ClearCollect(colCLB, SortByColumns(CLB, "name"))
```

### 3.3. `App.StartScreen`
```
If(LaQuanTri, scrQuanTri, IsBlank(varHS), scrKhongCoTen, scrDangKy)
```

---

## 4. Bố cục co giãn (áp dụng mọi màn hình)

Mỗi màn hình dựng cùng khung:

1. **Insert → Layout → Vertical container**, đặt tên `conKhung_<màn hình>`:
   - `X`: `(Parent.Width - Self.Width) / 2`
   - `Y`: `0`
   - `Width`: `Min(Parent.Width - 32, 760)`
   - `Height`: `Parent.Height`
   - `LayoutGap`: `12`, `PaddingTop`: `16`, `PaddingBottom`: `16`
   - `LayoutOverflowY`: `LayoutOverflow.Scroll` (cuộn khi dài)
2. Mọi control đặt **bên trong** container; `Width` = `Parent.Width` (hoặc `AlignInContainer = Stretch`).
3. Cỡ chữ: tiêu đề `If(LaPhone, 22, 26)`, chữ thường `If(LaPhone, 16, 14)`.
4. Nút bấm cao tối thiểu `48` (dễ chạm trên phone).

Kết quả: phone ⇒ khung trải gần hết ngang; laptop ⇒ khung rộng tối đa 760 px, nằm giữa.

---

## 5. Màn hình học sinh

### 5.1. `scrKhongCoTen`
Một Label:
```
"Email " & User().Email & " chưa có trong danh sách học sinh. Em liên hệ giáo viên chủ nhiệm."
```

### 5.2. `scrDangKy`

Trong `conKhung_DangKy`, thêm theo thứ tự:

**a) Label `lblChao`**
```
"Chào " & varHS.name & " (" & varHS.student_id & " – " & varHS.class_id & ")"
```

**b) Label `lblHan`**
```
If(HetHan, "Đã hết hạn nộp nguyện vọng.",
  "Hạn chót: " & Text(HanChot, "dd/mm/yyyy hh:mm") &
  If(IsBlank(varNV), "  •  Em chưa nộp.", "  •  Đã nộp lúc " & Text(varNV.nop_luc, "dd/mm hh:mm")))
```
`Color`: `If(HetHan, Color.Red, Color.DarkGreen)`

**c) Label hướng dẫn**
```
"Chọn tối đa " & SoNguyenVongToiDa & " CLB, CLB em thích nhất ở ô 1. Không chọn trùng. Thứ tự em xếp là thứ tự thật em muốn: hệ thống xếp theo thuật toán Gale–Shapley nên khai thật luôn có lợi nhất cho em."
```

**d) Horizontal container `conLuoi`** (chứa các ô chọn)
- `Wrap`: `true`, `LayoutGap`: `12`, `Width`: `Parent.Width`, `AutoHeight`: `true` (hoặc `Height` đủ lớn).

Bên trong `conLuoi`, tạo **ô nguyện vọng 1** gồm một Vertical container `conNV1` chứa Label + Dropdown, rồi **copy/paste** thành `conNV2` … `conNV10`, sửa số tương ứng:

`conNV1`:
- `Width`: `If(LaPhone, Parent.Width, (Parent.Width - 12) / 2)` → phone 1 cột, laptop 2 cột
- `Visible`: `1 <= SoNguyenVongToiDa` (ô k: `k <= SoNguyenVongToiDa`)
- `Height`: `80`

`lblNV1` (Label): `"Nguyện vọng 1"`

`ddNV1` (Dropdown cổ điển):
- `Items`: `colCLB`
- `Value` (thuộc tính hiển thị, cổ điển): `name` — modern: `ItemDisplayText = ThisItem.name`
- `AllowEmptySelection`: `true`
- `Default`: `LookUp(colCLB, club_id = varNV.pref_1).name` — modern: `DefaultSelectedItems = Filter(colCLB, club_id = varNV.pref_1)`
- `DisplayMode`: `If(HetHan, DisplayMode.View, DisplayMode.Edit)`
- `Width`: `Parent.Width`

Ô k: thay `pref_1` bằng `pref_k`, `ddNV1` bằng `ddNVk`.

> Gợi ý: làm xong ô 1, kiểm tra chạy đúng rồi mới copy.

**e) Label `lblLoi`** (báo lỗi trực tiếp)
```
With({ds: Filter([ddNV1.Selected.club_id, ddNV2.Selected.club_id, ddNV3.Selected.club_id, ddNV4.Selected.club_id, ddNV5.Selected.club_id, ddNV6.Selected.club_id, ddNV7.Selected.club_id, ddNV8.Selected.club_id, ddNV9.Selected.club_id, ddNV10.Selected.club_id], !IsBlank(Value))},
  If(CountRows(ds) = 0, "Em chưa chọn CLB nào.",
     CountRows(Distinct(ds, Value)) < CountRows(ds), "Có CLB bị chọn trùng.",
     ""))
```
`Color`: `Color.Red`, `Visible`: `!IsBlank(Self.Text)`

> Không bắt điền liên tục (bỏ trống ô 2 rồi chọn ô 3 vẫn được): khi lưu, app tự dồn các lựa chọn lên trước (mục f).

**f) Button `btnNop`** — `Text`: `If(IsBlank(varNV), "Nộp nguyện vọng", "Cập nhật nguyện vọng")`
- `DisplayMode`: `If(HetHan || !IsBlank(lblLoi.Text), DisplayMode.Disabled, DisplayMode.Edit)`
- `OnSelect`:
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
          email: EmailToi,
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
- Width: `Parent.Width`, Height: `48`.

> `Patch` với `Coalesce(LookUp…, Defaults…)` nghĩa là nộp lại sẽ **ghi đè** bản cũ, không sinh dòng trùng.
> Nếu Studio báo `Blank()` không hợp lệ cho cột Text: bật **Settings → Updates → Formula-level error management**.

**g) (Tuỳ chọn) Gallery giới thiệu CLB `galCLB`**
- `Items`: `colCLB`; hiện `ThisItem.name`, `ThisItem.mo_ta`, `"Chỉ tiêu: " & ThisItem.capacity`.
- Gallery dạng **Flexible height**; `WrapCount`: `If(LaPhone, 1, 2)`.

### 5.3. `scrXacNhan`
- Label tóm tắt:
```
"Đã lưu lúc " & Text(varNV.nop_luc, "dd/mm/yyyy hh:mm") & Char(10) &
Concat(
  Filter(Table(
    {k:1, c:varNV.pref_1},{k:2, c:varNV.pref_2},{k:3, c:varNV.pref_3},{k:4, c:varNV.pref_4},{k:5, c:varNV.pref_5},
    {k:6, c:varNV.pref_6},{k:7, c:varNV.pref_7},{k:8, c:varNV.pref_8},{k:9, c:varNV.pref_9},{k:10, c:varNV.pref_10}),
    !IsBlank(c)),
  k & ". " & LookUp(colCLB, club_id = c).name, Char(10))
```
- Button **Sửa lại**: `Navigate(scrDangKy)` (ẩn khi `HetHan`).
- Label: `"Em có thể sửa đến hạn chót. Lần nộp cuối cùng được tính."`

### 5.4. (Tuỳ chọn) `scrChonThi` — chọn CLB thi tuyển
- 5 dropdown `ddThi1`…`ddThi5`, `Items`: `Filter(colCLB, co_thi)`, bố cục giống mục 5.2(d).
- Nút lưu:
```
With({ds: Filter([ddThi1.Selected.club_id, ddThi2.Selected.club_id, ddThi3.Selected.club_id, ddThi4.Selected.club_id, ddThi5.Selected.club_id], !IsBlank(Value))},
  If(CountRows(Distinct(ds, Value)) < CountRows(ds), Notify("Trùng CLB thi.", NotificationType.Error),
    Patch(ChonThi,
      Coalesce(LookUp(ChonThi, student_id = varHS.student_id), Defaults(ChonThi)),
      {student_id: varHS.student_id, name: varHS.name,
       test_club_1: Index(ds,1).Value,
       test_club_2: If(CountRows(ds)>=2, Index(ds,2).Value, Blank()),
       test_club_3: If(CountRows(ds)>=3, Index(ds,3).Value, Blank()),
       test_club_4: If(CountRows(ds)>=4, Index(ds,4).Value, Blank()),
       test_club_5: If(CountRows(ds)>=5, Index(ds,5).Value, Blank())});
    Notify("Đã lưu CLB thi.", NotificationType.Success)))
```
> Lưu ý thứ tự: nếu sau này học sinh đổi CLB thi, cặp `test_club_k / score_k` có thể lệch. Khoá chọn thi **trước** khi giáo viên nhập điểm (dùng hạn riêng), hoặc giáo viên nhập điểm theo tên CLB chứ không theo vị trí.

Thêm nút điều hướng giữa `scrDangKy` và `scrChonThi` ở đầu mỗi màn hình nếu dùng.

---

## 6. Màn hình giáo viên `scrQuanTri`

Chỉ vào được khi `LaQuanTri` (App.StartScreen đã lo). Bên trong `conKhung_QuanTri` (đặt `Width` tối đa `1200` thay vì 760):

**a) Thẻ số liệu** (Label):
```
CountRows(NguyenVong) & " / " & CountRows(HocSinh) & " học sinh đã nộp"
```
> SharePoint chỉ đếm chính xác tới 2.000 dòng với `CountRows` (giới hạn delegation). 800 HS là an toàn; nếu > 2.000, **Settings → General → Data row limit = 2000** và tách theo khối.

**b) Gallery học sinh chưa nộp `galChuaNop`**
- `Items`: `Filter(HocSinh, !(student_id in NguyenVong.student_id))`
- `WrapCount`: `If(App.Width < 900, 1, 3)`
- Hiện `ThisItem.student_id & " – " & ThisItem.name & " (" & ThisItem.class_id & ")"`
> Công thức `in` không delegable: chỉ đúng khi số dòng ≤ Data row limit (2000). Với 800 HS là ổn.

**c) Thống kê theo CLB** (Gallery `galThongKe`, Items):
```
AddColumns(colCLB, NV1, CountRows(Filter(NguyenVong, pref_1 = club_id)))
```
hiện `name`, `capacity`, `NV1` → giáo viên thấy CLB nào quá tải nguyện vọng 1.

**d) Nhập điểm thi** (nếu dùng `ChonThi`): chèn **Edit form** gắn `ChonThi`, chọn bản ghi từ một Gallery; chỉ hiện các thẻ `score_k`. Hoặc đơn giản hơn: giáo viên nhập điểm trực tiếp trong SharePoint (**Edit in grid view**).

**e) Nút mở danh sách**: `Launch("https://<tenant>.sharepoint.com/sites/CLB-2026/Lists/NguyenVong")` để xuất CSV (mục 8).

---

## 7. Bảo mật và toàn vẹn dữ liệu

| Rủi ro | Biện pháp |
|---|---|
| Học sinh nộp hộ / mạo danh | Mã HS lấy từ `HocSinh` theo **email đăng nhập**, không cho tự gõ |
| Xem nguyện vọng của bạn | Item-level permissions (mục 1.5) |
| Học sinh tự sửa điểm thi | Điểm nhập ngoài app; nếu muốn chặt hơn: tách điểm sang list `DiemThi` chỉ giáo viên có quyền ghi |
| Nộp trùng dòng | `Patch` + `Coalesce(LookUp…)` và cột `student_id` **unique** |
| Sửa sau hạn | Kiểm `Now() > HanChot` trong `OnSelect`, và giáo viên đổi quyền list sang **Read** ngay khi hết hạn (lớp bảo vệ thật; app chỉ là lớp giao diện) |
| Mã CLB gõ sai | Học sinh chỉ chọn từ dropdown lấy từ list `CLB` |
| Mất dữ liệu | SharePoint có Version history + Recycle bin; xuất CSV sao lưu cuối mỗi ngày |

> Dữ liệu học sinh là dữ liệu cá nhân: không chia sẻ link list ra ngoài tenant trường.

---

## 8. Xuất dữ liệu sang rbda-kiosk

Sau hạn chót (đã khoá quyền list):

1. Mở list `NguyenVong` → tạo view **"Xuat_kiosk"**: chỉ hiện cột `student_id, name, pref_1 … pref_10` theo đúng thứ tự đó (ẩn `email, nop_luc, so_lan_nop`). → **Export → Export to CSV**.
2. List `CLB` → view chỉ `club_id, name, capacity, reserve_capacity, reserve_group` → Export to CSV.
3. (Nếu có thi) List `ChonThi` → view `student_id, name, test_club_1, score_1, …` → Export to CSV.
4. (Nếu có nhóm ưu tiên / lớp) cần cột `reserve_group, class_id` của học sinh: thêm hai cột này vào file nguyện vọng hoặc file chọn thi (xem mẫu `mau_csv/07_…`, `mau_csv/08_…`). Cách dễ nhất: trong Excel, dùng `XLOOKUP` lấy từ bản xuất `HocSinh`.
5. Mở từng CSV bằng Excel kiểm nhanh: tiêu đề đúng tên, không có dòng trống, mã CLB khớp list `CLB`.
6. Trong rbda-kiosk: nạp **CLB trước**, rồi chọn thi (nếu có), rồi nguyện vọng. Kiosk tự nhận loại tệp theo tiêu đề cột (`detect_csv_kind`): có `capacity` ⇒ CLB; có `pref_` ⇒ nguyện vọng; có `test_club_` ⇒ chọn thi.
7. Chạy xếp như bình thường. Kiosk lo sao lưu, khoá seed/STB, kiểm tra và lưu lịch sử chạy.

> Đối chiếu mẫu chuẩn trong repo: `mau_csv/03_nguyen_vong_dang_rong.csv`, `mau_csv/05_danh_sach_club.csv`, `mau_csv/01_chon_club_thi_dang_rong.csv`.
> SharePoint xuất CSV có thể kèm cột phụ (`Item Type`, `Path`): xoá các cột đó trong Excel trước khi nạp. File lưu dạng **CSV UTF-8** để giữ dấu tiếng Việt.

---

## 9. Kiểm thử trước khi phát hành

| # | Kịch bản | Kết quả mong đợi |
|---|---|---|
| 1 | Preview (F5), chọn thiết bị **Phone** | Ô chọn 1 cột, không tràn ngang |
| 2 | Kéo cửa sổ rộng (laptop) | 2 cột, khung giữa màn hình |
| 3 | Email không có trong `HocSinh` | Vào `scrKhongCoTen` |
| 4 | Chọn trùng CLB | Báo đỏ, nút Nộp mờ |
| 5 | Chọn ô 1 và ô 3, bỏ trống ô 2 | Lưu thành `pref_1`, `pref_2` (dồn lên) |
| 6 | Nộp hai lần | Chỉ một dòng, `so_lan_nop = 2` |
| 7 | Đặt `HanChot` về quá khứ | Dropdown khoá, nút mờ |
| 8 | Đăng nhập tài khoản học sinh khác | Không thấy dòng của bạn trong list |
| 9 | Email quản trị | Vào `scrQuanTri`, số liệu đúng |
| 10 | Xuất CSV, nạp vào kiosk với 5–10 HS thử | Kiosk nạp không lỗi, xếp ra kết quả |

Dùng 3–5 tài khoản thử (nhờ IT tạo hoặc mượn học sinh tình nguyện) trước khi mở cho toàn trường.

---

## 10. Phát hành

1. **File → Save → Publish** (mỗi lần sửa phải Publish lại).
2. **Share**: thêm nhóm học sinh (Microsoft 365 group / Security group của khối) với quyền **User**; thêm giáo viên quản trị là **Co-owner**. Lưu ý: chia sẻ app **không** tự chia quyền list SharePoint — phải làm mục 1.5.
3. Lấy link: **Details → Web link**. Gửi qua Teams / email lớp. Học sinh mở trên điện thoại: link mở trong trình duyệt, hoặc cài app **Power Apps** (iOS/Android) rồi đăng nhập tài khoản trường.
4. Tạo mã QR từ web link để dán ở lớp.

---

## 11. Lịch triển khai đề xuất

| Ngày | Việc |
|---|---|
| D-14 | Tạo site, 4 list, nạp `HocSinh`, `CLB` |
| D-12 | Dựng app (mục 2–6) |
| D-10 | Kiểm thử mục 9 với tài khoản thử |
| D-8 | Sửa lỗi, Publish, Share |
| D-7 → D0 | Học sinh nộp; giáo viên theo dõi `galChuaNop`, nhắc lớp |
| D0 | Hết hạn: khoá quyền list (Read) |
| D+1 | Xuất CSV (mục 8), nạp kiosk, chạy xếp |

**Phương án dự phòng:** nếu app lỗi giữa chừng, dùng Google Forms / Microsoft Forms đã có (`tao-google-form-clb`) hoặc nhập Sổ nhập Excel tay; dữ liệu đã nộp trong SharePoint vẫn xuất được.

---

## Phụ lục A. Lỗi hay gặp

| Triệu chứng | Nguyên nhân / Cách sửa |
|---|---|
| Biểu tượng tam giác vàng "delegation" | Bình thường với ≤ 2.000 dòng; tăng Data row limit lên 2000 |
| `club_id` không nhận trong công thức | Dùng `Title` |
| Dropdown trống | `colCLB` chưa nạp: chạy lại **App → Run OnStart** |
| Patch báo lỗi quyền | Học sinh chưa có Contribute trên list |
| CSV mất dấu tiếng Việt | Mở bằng Excel **Data → From Text/CSV**, chọn UTF-8, lưu lại dạng **CSV UTF-8** |
| Kiosk báo mã CLB không tồn tại | Mã trong `NguyenVong` khác `CLB.club_id` (đổi mã sau khi học sinh đã nộp) — không đổi mã CLB sau khi mở đăng ký |
| App méo trên phone | Chưa tắt Scale to fit / Lock aspect ratio |

## Phụ lục B. Tên đặt cho control (để tra cứu)

`scrKhongCoTen`, `scrDangKy`, `scrXacNhan`, `scrChonThi`, `scrQuanTri`; `conKhung_*`, `conLuoi`, `conNV1…10`, `lblNV1…10`, `ddNV1…10`, `lblLoi`, `btnNop`, `ddThi1…5`, `galCLB`, `galChuaNop`, `galThongKe`; biến `varHS`, `varNV`; collection `colCLB`.

## Phụ lục C. Trường nhiều buổi

1. List `CLB` thêm cột `buoi` (ví dụ `thu_2`) — đúng mẫu `mau_csv/06_danh_sach_club_nhieu_buoi.csv`.
2. List `NguyenVong`: thay `pref_k` bằng `thu_2_pref_1…`, `thu_4_pref_1…` (mỗi buổi tối đa N cột).
3. App: mỗi buổi một nhóm dropdown, `Items = Filter(colCLB, buoi = "thu_2")`; bỏ trống cả buổi = em không học buổi đó.
4. Xuất CSV đúng mẫu `mau_csv/08_nguyen_vong_nhieu_buoi.csv` (bỏ cột `wp_k` nếu không dùng Điểm quyết tâm).

## Phụ lục D. Những gì KHÔNG làm trong app
- Không xếp CLB, không tính điểm ưu tiên, không chạy xổ số: kiosk làm (giữ bất biến 1–5).
- Không có huy chương (FA-DAA) ở phiên bản này; nếu cần, làm thành mục riêng có mã trong sổ đăng ký.
