# PA16 — Phiếu đăng ký và bài thi tuyển ngay trong ứng dụng

[← PA15](PA15_thu_3_hoc_sinh.md) · [Mục lục](../00_MUC_LUC.md)

Tệp này thêm **bài thi trắc nghiệm** của các câu lạc bộ có thi tuyển vào ứng dụng `DangKyCLB`. Học sinh chọn câu lạc bộ muốn thi (tối đa 5), chỉ thấy đề của các câu lạc bộ đã chọn, làm bài và nộp. Sau hạn, giáo viên bấm nút chấm; điểm tự vào cột `score_1` … `score_5` của bảng `ChonThi`, rồi xuất sang phần mềm xếp câu lạc bộ như cũ.

**Cần có:** đã xong [SP07](../sharepoint/SP07_list_ChonThi.md), [PA11](PA11_man_chon_thi.md) và [PA15](PA15_thu_3_hoc_sinh.md) đã đạt. Các thao tác T1 đến T5 ở [SP03](../sharepoint/SP03_thao_tac_list_co_ban.md); các chữ THÊM, ĐỔI TÊN, ĐIỀN MỤC ở đầu [PA05](PA05_tao_man_hinh_va_khung.md).

⚠️ **Phần bài thi trong tệp này chưa được chạy thử trên Microsoft thật.** Bắt buộc làm hết "Bảng thử" ở Phần 11 bằng tài khoản thử trước khi cho học sinh thi. Dòng thử nào không đạt mà không sửa được: dùng "Đường khác" ở Phần 12.

## Phần 0 — Phiếu đăng ký: đã có sẵn

Phiếu đăng ký nguyện vọng đã được dựng ở các tệp trước, không phải làm lại:

| Phần của phiếu | Tệp |
|---|---|
| Lời chào, hạn chót, lời dặn | [PA07](PA07_dang_ky_phan_tren.md) |
| 10 ô chọn câu lạc bộ theo thứ tự thích | [PA08](PA08_dang_ky_o_chon.md) |
| Báo lỗi chọn trùng, nút Nộp | [PA09](PA09_dang_ky_nut_nop.md) |
| Trang xác nhận, nút "Sửa lại" | [PA10](PA10_man_xac_nhan.md) |
| Chọn tối đa 5 câu lạc bộ muốn thi | [PA11](PA11_man_chon_thi.md) |

Tệp này nối thêm vào sau PA11: từ trang chọn câu lạc bộ thi, học sinh bấm "Làm bài thi →".

## Cách làm đã chọn, và điều KHÔNG được bảo vệ

**Vấn đề:** bảng nào học sinh đọc được thì học sinh mở thẳng trên SharePoint được, kể cả khi ứng dụng không hiện ra. Nên **đáp án không được nằm trong bảng mà học sinh đọc được**.

**Cách làm:** tách thành 3 bảng, và việc chấm do **giáo viên** bấm nút, chạy bằng quyền của giáo viên.

| Bảng | Chứa gì | Học sinh | Giáo viên phụ trách |
|---|---|---|---|
| `CauHoi` | Câu hỏi và các lựa chọn. **Không có đáp án** | Chỉ xem | Xem, sửa |
| `DapAn` | Đáp án đúng của từng câu | **Không vào được** | Xem, sửa |
| `BaiLam` | Bài đã nộp: mỗi học sinh, mỗi câu lạc bộ một dòng | Tạo và xem **bài của chính mình** | Xem tất cả |
| `ChonThi` (đã có) | Câu lạc bộ chọn thi và điểm | Tạo, sửa dòng của mình (đến khi khoá) | Xem tất cả; nút chấm ghi điểm vào đây |

Chỉ dùng những thứ có sẵn trong gói Microsoft 365 của trường, không dùng phần phải trả thêm tiền.

**Nói thẳng những điều cách làm này KHÔNG bảo vệ được:**

1. **Đề thi không bí mật.** Học sinh nào biết mở thẳng bảng `CauHoi` trên SharePoint sẽ đọc được câu hỏi của **mọi** câu lạc bộ, kể cả câu lạc bộ mình không chọn thi, và đọc được từ trước khi làm bài. Ứng dụng chỉ "không hiện", không "chặn".
2. **Không có đồng hồ tính giờ, không chống tra cứu.** Học sinh làm bài ở nhà, mở tài liệu hay hỏi bạn đều được.
3. **Nộp một lần chỉ là khoá trên màn hình.** Cho đến khi giáo viên khoá bảng, học sinh biết mở thẳng bảng `BaiLam` có thể sửa hoặc xoá bài **của chính mình** để làm lại. Em đó không biết đáp án nên không tự cho điểm được, nhưng có thêm thời gian và thêm lượt làm.
4. **Học sinh sửa được ô điểm trong dòng `ChonThi` của mình** cho đến khi khoá bảng. Vì vậy quy trình chấm ở Phần 10 bắt buộc: khoá bảng → xoá hết điểm cũ → mới chấm.
5. **Sau khi chấm, học sinh đọc được điểm của chính mình** nếu mở thẳng bảng `ChonThi`. Không muốn vậy thì làm bước gỡ quyền ở Phần 10, bước 8.
6. Ai có quyền «Full control» trên trang đều đọc được bảng `DapAn`.

Trường cần đề thi bí mật hoặc có tính giờ: dùng "Đường khác" ở Phần 12.

## Phần 1 — Bảng câu hỏi `CauHoi`

Làm trên SharePoint. **Không bật Bắt buộc** cho cột nào.

**Bước 1 — Làm T1.** Tên bảng:
```
CauHoi
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã câu hỏi):
```
ma_cau
```

**Bước 3 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (mã câu lạc bộ ra đề):
```
club_id
```

**Bước 4 — Làm T3.** Loại: **Số**, số lẻ **0**. Tên cột (số thứ tự câu trong đề):
```
so_cau
```

**Bước 5 — Làm T3.** Loại: **Đoạn văn**. Tên cột (nội dung câu hỏi):
```
cau_hoi
```

**Bước 6 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (lựa chọn a):
```
lua_chon_a
```

**Bước 7 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (lựa chọn b):
```
lua_chon_b
```

**Bước 8 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (lựa chọn c):
```
lua_chon_c
```

**Bước 9 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (lựa chọn d):
```
lua_chon_d
```

**Bước 10 — Làm T4** với cột `ma_cau`.

**Bước 11 — Làm T5** với cột `ma_cau`.

**Bước 12 — Làm T4** với cột `club_id`.

👀 Hàng tên cột của bảng `CauHoi`: `ma_cau`, `club_id`, `so_cau`, `cau_hoi`, `lua_chon_a`, `lua_chon_b`, `lua_chon_c`, `lua_chon_d`. **Không có cột đáp án.**

⚠️ Ở bước 5, trong khung «Create a column» có công tắc «Use enhanced rich text»: để **Off**.

- [ ] Xong bảng `CauHoi`. Quyền của bảng này để nguyên (học sinh chỉ xem, theo SP09 Phần 2).

## Phần 2 — Bảng đáp án `DapAn` (học sinh không vào được)

**Bước 1 — Làm T1.** Tên bảng:
```
DapAn
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã câu hỏi, giống hệt mã ở bảng `CauHoi`):
```
ma_cau
```

**Bước 3 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (mã câu lạc bộ ra đề):
```
club_id
```

**Bước 4 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (chữ cái của lựa chọn đúng: a, b, c hoặc d):
```
dap_an
```

**Bước 5 — Làm T4** với cột `ma_cau`.

**Bước 6 — Làm T5** với cột `ma_cau`.

**Bước 7 — Làm T4** với cột `club_id`.

**Chặn học sinh (làm ngay, trước khi điền đáp án):**

8. Ở bảng `DapAn`: bấm ⚙ → «List settings».
9. Bấm «Permissions for this list».
10. Trên dải lệnh, bấm «Stop Inheriting Permissions», rồi bấm «OK» ở hộp hỏi lại.
11. Trong danh sách trên trang, bấm đánh dấu ô ở đầu **mọi dòng không ghi «Full Control»** ở cột «Permission Levels» (dòng của nhóm học sinh, dòng có chữ «Visitors», dòng có chữ «Members»).
12. Trên dải lệnh, bấm «Remove User Permissions», rồi bấm «OK» ở hộp hỏi lại.

👀 Danh sách chỉ còn các dòng ghi «Full Control» (giáo viên phụ trách, nhóm có chữ «Owners»).

⚠️ Lỡ xoá hết, không còn dòng nào: bấm «Grant Permissions», dán thư điện tử của bạn, «Show options», chọn «Full Control», «Share».

- [ ] Xong bảng `DapAn`, chỉ còn «Full Control».

## Phần 3 — Bảng bài làm `BaiLam`

Ứng dụng tự ghi vào bảng này. **Không bật Bắt buộc** cho cột nào.

**Bước 1 — Làm T1.** Tên bảng:
```
BaiLam
```

**Bước 2 — Làm T2.** Tên mới cho cột «Title» (mã học sinh):
```
student_id
```

**Bước 3 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (họ tên):
```
name
```

**Bước 4 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (mã câu lạc bộ của bài thi):
```
club_id
```

**Bước 5 — Làm T3.** Loại: **Chữ ngắn**. Tên cột (mã bài: mã học sinh, dấu gạch đứng, mã câu lạc bộ):
```
ma_bai
```

**Bước 6 — Làm T3.** Loại: **Đoạn văn**, công tắc «Use enhanced rich text» để **Off**. Tên cột (các câu trả lời):
```
tra_loi
```

**Bước 7 — Làm T3.** Loại: **Ngày giờ**, bật «Include Time». Tên cột (giờ nộp):
```
nop_luc
```

**Bước 8 — Làm T4** với cột `ma_bai`.

**Bước 9 — Làm T5** với cột `ma_bai`. (Nhờ bước này mỗi học sinh chỉ có một bài cho mỗi câu lạc bộ.)

**Bước 10 — Làm T4** với cột `club_id`.

**Bước 11 — Làm T4** với cột `student_id`.

**Bước 12 — Cấp quyền cho học sinh:** làm [SP09](../sharepoint/SP09_phan_quyen.md) Phần 3, bước 14 đến 29, nhưng ở bước 14 bấm tên bảng `BaiLam`.

👀 Hàng tên cột của bảng `BaiLam`: `student_id`, `name`, `club_id`, `ma_bai`, `tra_loi`, `nop_luc`.

- [ ] Xong bảng `BaiLam`: nhóm học sinh có «Contribute», và đã chọn hai mục "chỉ của mình" ở «Item-level Permissions».

## Phần 4 — Đưa câu hỏi và đáp án vào

Soạn đề trong **một** tệp Excel có đủ cả đáp án (tệp này chỉ giáo viên giữ), rồi dán sang hai bảng.

1. Mở Excel, tạo tệp trống. Bấm ô **A1**, dán:
```
ma_cau	club_id	so_cau	cau_hoi	lua_chon_a	lua_chon_b	lua_chon_c	lua_chon_d	dap_an
```
2. Từ dòng 2, điền đề thi vào các cột **B đến I**, mỗi câu hỏi một dòng (cột A để trống, bước 3 sẽ tự điền). Ví dụ giả:

| ma_cau | club_id | so_cau | cau_hoi | lua_chon_a | lua_chon_b | lua_chon_c | lua_chon_d | dap_an |
|---|---|---|---|---|---|---|---|---|
| | clb_tienganh | 1 | Từ nào là danh từ? | run | table | quickly | blue | b |
| | clb_tienganh | 2 | "Xin chào" tiếng Anh là gì? | Hello | Bye | | | a |

   Quy tắc điền:
   - `club_id`: đúng mã trong bảng `CLB`, và câu lạc bộ đó có `co_thi` là «Yes».
   - `so_cau`: 1, 2, 3… trong từng câu lạc bộ.
   - Mỗi câu có ít nhất hai lựa chọn (a và b). Câu chỉ có 2 hoặc 3 lựa chọn thì để trống các ô còn lại.
   - Trong một câu, **không có hai lựa chọn giống hệt nhau**.
   - Mỗi lựa chọn nên ngắn (dưới chừng 60 chữ cái) để vừa một dòng trên điện thoại.
   - `dap_an`: đúng **một chữ thường** `a`, `b`, `c` hoặc `d`, và ô lựa chọn tương ứng không được trống.
   - Mọi câu lạc bộ nên có cùng số câu hỏi. Điểm mỗi bài = số câu đúng chia tổng số câu của câu lạc bộ đó, nhân 10.

3. Bấm ô **A2**, dán công thức tạo mã câu, bấm `Enter`:
```
=B2&"-"&C2
```
4. Bấm lại ô **A2**, bấm đúp vào ô vuông nhỏ ở góc dưới bên phải ô để điền xuống hết các dòng.

👀 Cột A hiện mã dạng `clb_tienganh-1`, `clb_tienganh-2`…, không mã nào trùng nhau.

5. Bấm `Ctrl` + `S`, đặt tên tệp:
```
DeThi
```

**Dán câu hỏi vào bảng `CauHoi` (không lấy cột đáp án):**

6. Trong Excel: bấm ô **A2**, giữ `Shift`, bấm ô cột **H** của dòng cuối cùng. Bấm `Ctrl` + `C`. (Cột H là `lua_chon_d`. **Không** kéo sang cột I.)
7. Mở bảng `CauHoi` trên SharePoint, bấm «Edit in grid view».
8. Bấm ô đầu tiên bên trái (cột `ma_cau`) của dòng trống cuối cùng, bấm `Ctrl` + `V`.
9. Chờ hết biểu tượng xoay tròn ở đầu các dòng, rồi bấm «Exit grid view».

👀 Số dòng của bảng `CauHoi` bằng số câu hỏi trong Excel. Cột `ma_cau` hiện **mã** (không phải công thức).

**Dán đáp án vào bảng `DapAn`:**

10. Trong Excel, bấm dấu «+» ở hàng tên trang tính phía dưới cùng cửa sổ để thêm một trang tính mới.
11. Ở trang tính mới, bấm ô **A1**, dán:
```
ma_cau	club_id	dap_an
```
12. Bấm ô **A2**, dán công thức, bấm `Enter`:
```
=Sheet1!A2
```
13. Bấm ô **B2**, dán công thức, bấm `Enter`:
```
=Sheet1!B2
```
14. Bấm ô **C2**, dán công thức, bấm `Enter`:
```
=Sheet1!I2
```
15. Bôi đen ba ô **A2 đến C2**, bấm đúp vào ô vuông nhỏ ở góc dưới bên phải vùng chọn; nếu không tự điền, kéo ô vuông nhỏ đó xuống cho đủ số dòng câu hỏi.

👀 Trang tính mới có 3 cột: mã câu, mã câu lạc bộ, chữ cái đáp án; số dòng bằng số câu hỏi.

16. Bôi đen từ ô **A2** đến ô cột **C** của dòng cuối cùng, bấm `Ctrl` + `C`.
17. Mở bảng `DapAn` trên SharePoint, bấm «Edit in grid view», bấm ô đầu tiên (cột `ma_cau`) của dòng trống cuối cùng, bấm `Ctrl` + `V`.
18. Chờ hết biểu tượng xoay tròn, bấm «Exit grid view».

👀 Số dòng của bảng `DapAn` bằng số dòng của bảng `CauHoi`.

⚠️ Ở bước 12, trang tính đầu của bạn không tên `Sheet1` (ví dụ Excel tiếng Việt ghi `Trang_tính1`): trong ba công thức, thay chữ `Sheet1` bằng đúng tên trang tính đầu (nhìn ở hàng tên trang tính phía dưới cùng).

- [ ] `CauHoi` và `DapAn` cùng số dòng. Tệp `DeThi` cất nơi chỉ giáo viên mở được.

## Phần 5 — Nối 3 bảng mới và thêm hạn làm bài

Làm trong màn hình thiết kế của `DangKyCLB`.

1. Làm [PA03](PA03_noi_du_lieu.md) bước 1 đến 7.
2. Ở khung «Choose a list»: bấm đánh dấu `CauHoi`, `DapAn`, `BaiLam`.
3. Bấm «Connect».

👀 Bấm hình cái trụ tròn («Data») ở dải biểu tượng dọc: danh sách có thêm `CauHoi`, `DapAn`, `BaiLam`. Bấm biểu tượng trên cùng («Tree view») để quay lại cây bên trái.

4. Cây bên trái: bấm «App». Ô thả xuống nhỏ: chọn «Formulas».
5. Bấm vào ô dài, bấm `Ctrl` + `End` để đưa con trỏ về **cuối** đoạn đang có, bấm `Enter` để xuống dòng mới, rồi dán:
```
HanThi = HanChot;
HetHanThi = Now() > HanThi;
```

👀 Không có gạch chân đỏ. Bảy dòng cũ ở trên vẫn còn nguyên.

6. Bấm `Ctrl` + `S`.

Như trên là hạn làm bài **trùng** với hạn nộp nguyện vọng. Muốn hạn làm bài riêng: trong dòng `HanThi = HanChot;`, bôi đen chữ `HanChot`, dán đoạn dưới rồi sửa ngày giờ (kiểu `năm-tháng-ngày giờ:phút`):
```
DateTimeValue("2026-12-03 17:00")
```

⚠️ Ở PA04 bạn đã dùng **đoạn thay thế** (không có mục «Formulas»): chọn mục «OnStart» của «App», đưa con trỏ về cuối, gõ dấu `;` rồi `Enter`, dán đoạn dưới; sau đó «Run OnStart»:
```
Set(HanThi, HanChot);
Set(HetHanThi, Now() > HanThi)
```

## Phần 6 — Trang làm bài `scrBaiThi` và khung

1. Trên thanh lệnh bấm «New screen», bấm «Blank».
2. ĐỔI TÊN trang vừa tạo thành:
```
scrBaiThi
```
3. Bấm `scrBaiThi`, ĐIỀN MỤC **«OnVisible»** (việc làm mỗi lần trang này hiện ra) — dán:
```
Set(varThi, LookUp(ChonThi, student_id = varHS.student_id));
ClearCollect(colBaiCuaToi, Filter(BaiLam, student_id = varHS.student_id));
Set(varCLBThi, Blank());
Set(varBai, Blank());
Clear(colCau);
Clear(colTraLoi)
```

(Lúc này có gạch đỏ ở `varCLBThi`, `varBai`, `colCau`, `colTraLoi`: bình thường, sẽ hết sau Phần 7.)

4. Cây bên trái: bấm `scrBaiThi`.
5. THÊM khung dọc (`Vertical container`).
6. ĐỔI TÊN khung vừa thêm thành:
```
conKhung_BaiThi
```
7. Bấm `conKhung_BaiThi`, rồi ĐIỀN 8 MỤC sau:

**«X»** — dán:
```
(Parent.Width - Self.Width) / 2
```
**«Y»** — dán:
```
0
```
**«Width»** — dán:
```
Min(Parent.Width - 32, 760)
```
**«Height»** — dán:
```
Parent.Height
```
**«LayoutGap»** — dán:
```
12
```
**«PaddingTop»** — dán:
```
16
```
**«PaddingBottom»** — dán:
```
16
```
**«LayoutOverflowY»** — dán:
```
LayoutOverflow.Scroll
```

## Phần 7 — Các thứ trên trang làm bài

Thêm vào `conKhung_BaiThi`, đúng thứ tự: nút quay về, tiêu đề, danh sách câu lạc bộ thi, dòng trạng thái, danh sách câu hỏi, nút nộp bài.

### 7.1. Nút quay về

1. Cây bên trái: bấm `conKhung_BaiThi`.
2. THÊM nút bấm (`Button`).
3. ĐỔI TÊN nút vừa thêm thành:
```
btnVeChonThi
```
4. Bấm `btnVeChonThi`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"← Chọn CLB thi"
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

### 7.2. Tiêu đề

5. Cây bên trái: bấm `conKhung_BaiThi`.
6. THÊM ô chữ (`Text label`).
7. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblBTTieuDe
```
8. Bấm `lblBTTieuDe`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Bài thi tuyển  •  Hạn làm bài: " & Text(HanThi, "dd/mm/yyyy hh:mm")
```
**«Size»** — dán:
```
If(LaPhone, 20, 22)
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```

### 7.3. Danh sách câu lạc bộ em đã chọn thi

9. Cây bên trái: bấm `conKhung_BaiThi`.
10. Trên thanh lệnh bấm «Insert», bấm vào ô tìm kiếm, dán:
```
Blank vertical gallery
```
11. Bấm dòng «Blank vertical gallery» trong kết quả. Hiện bảng nhỏ «Select a data source» thì bấm `Esc`.
12. ĐỔI TÊN danh sách vừa thêm thành:
```
galCLBThi
```
13. Bấm `galCLBThi`, rồi ĐIỀN 4 MỤC sau:

**«Items»** — dán:
```
Filter(colCLB, club_id in [varThi.test_club_1, varThi.test_club_2, varThi.test_club_3, varThi.test_club_4, varThi.test_club_5])
```
**«TemplateSize»** — dán:
```
58
```
**«Height»** — dán:
```
290
```
**«Width»** — dán:
```
Parent.Width
```

14. Cây bên trái: bấm `galCLBThi` (để nút sắp thêm nằm **bên trong** danh sách).
15. THÊM nút bấm (`Button`).

👀 Ở cây bên trái, nút mới nằm thụt dưới `galCLBThi`.

16. ĐỔI TÊN nút vừa thêm thành:
```
btnChonBai
```
17. Bấm `btnChonBai`, rồi ĐIỀN 6 MỤC sau:

**«Text»** — dán:
```
ThisItem.name & If(IsBlank(LookUp(colBaiCuaToi, club_id = ThisItem.club_id)), "  –  bấm để làm bài", "  –  đã nộp bài")
```
**«X»** — dán:
```
0
```
**«Y»** — dán:
```
0
```
**«Width»** — dán:
```
Parent.TemplateWidth
```
**«Height»** — dán:
```
50
```
**«OnSelect»** — dán:
```
Set(varCLBThi, ThisItem);
Set(varBai, LookUp(colBaiCuaToi, club_id = ThisItem.club_id));
ClearCollect(colCau, SortByColumns(Filter(CauHoi, club_id = ThisItem.club_id), "so_cau"));
Clear(colTraLoi)
```

⚠️ Không tìm thấy «Blank vertical gallery», hoặc nút nằm ngoài danh sách: xem hai dòng ⚠️ ở [PA12](PA12_man_quan_tri.md), mục 4.

### 7.4. Dòng trạng thái

18. Cây bên trái: bấm `conKhung_BaiThi` (khung ngoài cùng, không phải `galCLBThi`).
19. THÊM ô chữ (`Text label`).
20. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblBTTrangThai
```
21. Bấm `lblBTTrangThai`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
If(IsBlank(varThi), "Em chưa lưu CLB thi nào. Bấm nút trên cùng để quay lại chọn và bấm Lưu.",
   HetHanThi, "Đã hết hạn làm bài thi.",
   IsBlank(varCLBThi), "Bấm vào tên một CLB ở trên để làm bài. Mỗi CLB chỉ nộp bài được một lần. Thoát trang khi chưa nộp thì phải chọn lại từ đầu.",
   !IsBlank(varBai), varCLBThi.name & ": em đã nộp bài lúc " & Text(varBai.nop_luc, "dd/mm/yyyy hh:mm") & ".",
   CountRows(colCau) = 0, varCLBThi.name & ": chưa có câu hỏi. Em báo giáo viên.",
   "Đang làm bài: " & varCLBThi.name & ". Đã chọn " & CountRows(colTraLoi) & " / " & CountRows(colCau) & " câu.")
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```
**«FontWeight»** — dán:
```
FontWeight.Semibold
```

### 7.5. Danh sách câu hỏi

22. Cây bên trái: bấm `conKhung_BaiThi`.
23. Trên thanh lệnh bấm «Insert», bấm vào ô tìm kiếm, dán:
```
Blank flexible height gallery
```
24. Bấm dòng «Blank flexible height gallery» (danh sách mà mỗi dòng tự cao theo nội dung) trong kết quả. Hiện bảng nhỏ «Select a data source» thì bấm `Esc`.
25. ĐỔI TÊN danh sách vừa thêm thành:
```
galCau
```
26. Bấm `galCau`, rồi ĐIỀN 4 MỤC sau:

**«Items»** — dán:
```
colCau
```
**«Visible»** — dán:
```
!IsBlank(varCLBThi) && IsBlank(varBai) && !HetHanThi
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
Max(360, App.Height - 360)
```

27. Cây bên trái: bấm `galCau`.
28. THÊM ô chữ (`Text label`).
29. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblCau
```
30. Bấm `lblCau`, rồi ĐIỀN 6 MỤC sau:

**«Text»** — dán:
```
ThisItem.so_cau & ". " & ThisItem.cau_hoi
```
**«X»** — dán:
```
8
```
**«Y»** — dán:
```
8
```
**«Width»** — dán:
```
Parent.TemplateWidth - 16
```
**«AutoHeight»** — dán:
```
true
```
**«FontWeight»** — dán:
```
FontWeight.Semibold
```

31. Cây bên trái: bấm `galCau`.
32. Trên thanh lệnh bấm «Insert», bấm vào ô tìm kiếm, dán:
```
Radio
```
33. Bấm dòng «Radio» (nhóm nút tròn, chỉ chọn được một) trong kết quả. Có hai dòng: bấm dòng dưới chữ «Classic».

👀 Ở cây bên trái, dưới `galCau` có `lblCau` và một thứ mới «Radio1» (số có thể khác).

34. ĐỔI TÊN nhóm nút tròn vừa thêm thành:
```
rdoChon
```
35. Bấm `rdoChon`, rồi ĐIỀN 7 MỤC sau:

**«Items»** — dán:
```
Filter([ThisItem.lua_chon_a, ThisItem.lua_chon_b, ThisItem.lua_chon_c, ThisItem.lua_chon_d], !IsBlank(Value))
```
**«Default»** — dán:
```
Switch(LookUp(colTraLoi, ma_cau = ThisItem.ma_cau).chon, "a", ThisItem.lua_chon_a, "b", ThisItem.lua_chon_b, "c", ThisItem.lua_chon_c, "d", ThisItem.lua_chon_d)
```
**«OnSelect»** — dán:
```
RemoveIf(colTraLoi, ma_cau = ThisItem.ma_cau);
Collect(colTraLoi, {ma_cau: ThisItem.ma_cau, chon: Switch(Self.Selected.Value, ThisItem.lua_chon_a, "a", ThisItem.lua_chon_b, "b", ThisItem.lua_chon_c, "c", ThisItem.lua_chon_d, "d")})
```
**«X»** — dán:
```
8
```
**«Y»** — dán:
```
lblCau.Y + lblCau.Height + 4
```
**«Width»** — dán:
```
Parent.TemplateWidth - 16
```
**«Height»** — dán:
```
44 * CountRows(Filter([ThisItem.lua_chon_a, ThisItem.lua_chon_b, ThisItem.lua_chon_c, ThisItem.lua_chon_d], !IsBlank(Value)))
```

⚠️ Không tìm thấy «Blank flexible height gallery»: dán `Flexible height gallery` thay vào; ở cây bên trái mở `galCau`, bấm chuột phải từng thứ có sẵn bên trong → «Delete» cho đến khi trống, rồi làm tiếp từ bước 25.
⚠️ Gạch đỏ ở chữ `ma_cau` sau `ThisItem.`: sửa riêng chữ đó thành `Title` (thành `ThisItem.Title`). Chữ `ma_cau` đứng một mình hoặc đứng trước dấu `:` thì giữ nguyên.

### 7.6. Nút nộp bài

36. Cây bên trái: bấm `conKhung_BaiThi` (khung ngoài cùng).
37. THÊM nút bấm (`Button`).
38. ĐỔI TÊN nút vừa thêm thành:
```
btnNopBai
```
39. Bấm `btnNopBai`, rồi ĐIỀN 6 MỤC sau:

**«Text»** — dán:
```
"Nộp bài " & varCLBThi.name
```
**«Visible»** — dán:
```
!IsBlank(varCLBThi) && IsBlank(varBai) && !HetHanThi
```
**«DisplayMode»** — dán:
```
If(CountRows(colCau) > 0 && CountRows(colTraLoi) >= CountRows(colCau) && !IsBlank(varHS), DisplayMode.Edit, DisplayMode.Disabled)
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
If(Now() > HanThi,
  Notify("Đã hết hạn làm bài thi.", NotificationType.Error),
  With({kq: Patch(BaiLam, Defaults(BaiLam),
      {
        student_id: varHS.student_id,
        name: varHS.name,
        club_id: varCLBThi.club_id,
        ma_bai: varHS.student_id & "|" & varCLBThi.club_id,
        tra_loi: Concat(colTraLoi, ma_cau & ":" & chon, ";"),
        nop_luc: Now()
      })},
    If(IsError(kq) || IsBlank(kq),
      Notify("Nộp bài thất bại. Em đã nộp bài CLB này rồi thì không nộp lại được. Nếu chưa, em báo giáo viên.", NotificationType.Error),
      Collect(colBaiCuaToi, kq);
      Set(varBai, kq);
      Clear(colTraLoi);
      Notify("Đã nộp bài.", NotificationType.Success))))
```

40. Bấm `Ctrl` + `S`.

👀 Bấm `scrBaiThi`, chọn mục «OnVisible»: các gạch đỏ ở Phần 6 bước 3 đã hết.

Nút này làm gì:
- Chỉ sáng lên khi **mọi câu** đã được chọn.
- Ghi một dòng vào `BaiLam`. Cột `tra_loi` có dạng `clb_tienganh-1:b;clb_tienganh-2:a` (mã câu, dấu hai chấm, chữ cái đã chọn).
- Nộp xong thì đề của câu lạc bộ đó ẩn đi, dòng trạng thái ghi giờ nộp.
- Học sinh **không thấy điểm**.

## Phần 8 — Nút "Làm bài thi" ở trang chọn câu lạc bộ thi

1. Cây bên trái: mở `scrChonThi`, bấm `conKhung_ChonThi`.
2. THÊM nút bấm (`Button`).
3. ĐỔI TÊN nút vừa thêm thành:
```
btnSangBaiThi
```
4. Bấm `btnSangBaiThi`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Làm bài thi →  (bấm Lưu CLB thi trước)"
```
**«OnSelect»** — dán:
```
Navigate(scrBaiThi)
```
**«Width»** — dán:
```
Parent.Width
```
**«Height»** — dán:
```
48
```

👀 Ở trang chọn câu lạc bộ thi, nút này nằm dưới cùng, ngay dưới nút "Lưu CLB thi".

5. Bấm `Ctrl` + `S`.

## Phần 9 — Nút chấm điểm ở trang giáo viên

Thêm vào `conKhung_QuanTri` (trang `scrQuanTri`), nối tiếp sau các thứ đã có ở PA12, đúng thứ tự: tiêu đề, nút xoá điểm cũ, danh sách câu lạc bộ có thi kèm nút chấm, dòng kết quả.

### 9.1. Tiêu đề

1. Cây bên trái: mở `scrQuanTri`, bấm `conKhung_QuanTri`.
2. THÊM ô chữ (`Text label`).
3. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblQTCham
```
4. Bấm `lblQTCham`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Chấm bài thi — chỉ bấm SAU KHI đã khoá bảng ChonThi và BaiLam"
```
**«FontWeight»** — dán:
```
FontWeight.Semibold
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```

### 9.2. Nút xoá điểm cũ

5. Cây bên trái: bấm `conKhung_QuanTri`.
6. THÊM nút bấm (`Button`).
7. ĐỔI TÊN nút vừa thêm thành:
```
btnXoaDiem
```
8. Bấm `btnXoaDiem`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"1. Xoá hết điểm cũ"
```
**«Width»** — dán:
```
Min(Parent.Width, 280)
```
**«Height»** — dán:
```
48
```
**«OnSelect»** — dán:
```
ClearCollect(colThiCoDiem, Filter(ChonThi, !IsBlank(score_1) || !IsBlank(score_2) || !IsBlank(score_3) || !IsBlank(score_4) || !IsBlank(score_5)));
ForAll(colThiCoDiem As hs,
  Patch(ChonThi, hs, {score_1: Blank(), score_2: Blank(), score_3: Blank(), score_4: Blank(), score_5: Blank()}));
Set(varKetQuaCham, "Đã xoá điểm cũ ở " & CountRows(colThiCoDiem) & " dòng của bảng ChonThi.");
Notify(varKetQuaCham, NotificationType.Success)
```

### 9.3. Danh sách câu lạc bộ có thi, mỗi dòng một nút chấm

9. Cây bên trái: bấm `conKhung_QuanTri`.
10. Trên thanh lệnh bấm «Insert», dán `Blank vertical gallery` vào ô tìm kiếm, bấm dòng «Blank vertical gallery». Hiện bảng nhỏ «Select a data source» thì bấm `Esc`.
11. ĐỔI TÊN danh sách vừa thêm thành:
```
galCham
```
12. Bấm `galCham`, rồi ĐIỀN 4 MỤC sau:

**«Items»** — dán:
```
Filter(colCLB, co_thi)
```
**«TemplateSize»** — dán:
```
58
```
**«Height»** — dán:
```
360
```
**«Width»** — dán:
```
Parent.Width
```

13. Cây bên trái: bấm `galCham`.
14. THÊM nút bấm (`Button`).

👀 Ở cây bên trái, nút mới nằm thụt dưới `galCham`.

15. ĐỔI TÊN nút vừa thêm thành:
```
btnChamCLB
```
16. Bấm `btnChamCLB`, rồi ĐIỀN 6 MỤC sau:

**«Text»** — dán:
```
"2. Chấm: " & ThisItem.name
```
**«X»** — dán:
```
0
```
**«Y»** — dán:
```
0
```
**«Width»** — dán:
```
Min(Parent.TemplateWidth, 480)
```
**«Height»** — dán:
```
50
```
**«OnSelect»** — dán:
```
Set(varMaCham, ThisItem.club_id);
ClearCollect(colDapAnCLB, Filter(DapAn, club_id = varMaCham));
ClearCollect(colBaiCLB, Filter(BaiLam, club_id = varMaCham));
ClearCollect(colThiCLB, Filter(ChonThi, test_club_1 = varMaCham || test_club_2 = varMaCham || test_club_3 = varMaCham || test_club_4 = varMaCham || test_club_5 = varMaCham));
If(CountRows(colDapAnCLB) = 0,
  Set(varKetQuaCham, ThisItem.name & ": CHƯA CHẤM, vì bảng DapAn chưa có đáp án của CLB này."),
  ForAll(colThiCLB As hs,
    With({bai: LookUp(colBaiCLB, student_id = hs.student_id)},
      With({tl: Split(Coalesce(bai.tra_loi, ""), ";")},
        With({diem: If(IsBlank(bai), Blank(),
              Round(10 * CountRows(Filter(colDapAnCLB,
                  (ma_cau & ":" & dap_an) in tl &&
                  CountRows(Filter(tl, StartsWith(Value, ma_cau & ":"))) = 1)) / CountRows(colDapAnCLB), 1))},
          If(hs.test_club_1 = varMaCham, Patch(ChonThi, hs, {score_1: diem}));
          If(hs.test_club_2 = varMaCham, Patch(ChonThi, hs, {score_2: diem}));
          If(hs.test_club_3 = varMaCham, Patch(ChonThi, hs, {score_3: diem}));
          If(hs.test_club_4 = varMaCham, Patch(ChonThi, hs, {score_4: diem}));
          If(hs.test_club_5 = varMaCham, Patch(ChonThi, hs, {score_5: diem}))))));
  Set(varKetQuaCham, ThisItem.name & ": " & CountRows(colThiCLB) & " học sinh chọn thi; " & CountRows(colBaiCLB) & " bài đã nộp; " & CountRows(Filter(colBaiCLB, !(student_id in colThiCLB.student_id))) & " bài bị bỏ vì học sinh không còn chọn thi CLB này; " & CountRows(Filter(colThiCLB, !(student_id in colBaiCLB.student_id))) & " học sinh chọn thi nhưng không nộp bài (để trống điểm)."));
Notify(varKetQuaCham, NotificationType.Information)
```

### 9.4. Dòng kết quả chấm

17. Cây bên trái: bấm `conKhung_QuanTri` (khung ngoài cùng, không phải `galCham`).
18. THÊM ô chữ (`Text label`).
19. ĐỔI TÊN ô chữ vừa thêm thành:
```
lblKetQuaCham
```
20. Bấm `lblKetQuaCham`, rồi ĐIỀN 3 MỤC sau:

**«Text»** — dán:
```
varKetQuaCham
```
**«Width»** — dán:
```
Parent.Width
```
**«AutoHeight»** — dán:
```
true
```

21. Bấm `Ctrl` + `S`.
22. Mở «App checker» (hình ống nghe, như [PA13](PA13_man_dau_tien_va_chay_thu.md) Phần 2): số cạnh «Formulas» phải là **0**.
23. Phát hành lại: [PA14](PA14_phat_hanh_chia_se.md) bước 1 đến 4.

Nút chấm làm gì, với **một** câu lạc bộ mỗi lần bấm:
- Đọc đáp án của câu lạc bộ đó từ `DapAn` (chỉ giáo viên đọc được), các bài đã nộp từ `BaiLam`, các học sinh đang chọn thi câu lạc bộ đó từ `ChonThi`.
- Điểm = số câu đúng ÷ tổng số câu của câu lạc bộ × 10, làm tròn 1 số lẻ (thang 10).
- Một câu chỉ được tính đúng khi bài làm có **đúng một** câu trả lời cho câu đó và câu trả lời ấy trùng đáp án. (Chặn trường hợp học sinh sửa thẳng bảng `BaiLam` để ghi cả bốn chữ cái cho một câu.)
- Ghi điểm vào đúng ô `score_…` **cùng số** với ô `test_club_…` chứa câu lạc bộ đó.
- Học sinh chọn thi nhưng không nộp bài: ô điểm **để trống** (phần mềm xếp câu lạc bộ sẽ báo "chưa chấm điểm" để giáo viên quyết định).
- Bài của học sinh đã bỏ chọn thi câu lạc bộ đó: **không tính**.
- Bấm lại lần nữa thì chấm lại từ đầu, kết quả như cũ.

⚠️ Hình tam giác vàng ở các nút này: là lời nhắc giới hạn 2000 dòng mỗi lần đọc. Mỗi câu lạc bộ có dưới 2000 bài nộp và trường dưới 2000 học sinh thì bỏ qua.

## Phần 10 — Quy trình ngày chấm (làm sau hạn làm bài)

Làm đúng thứ tự. Không đảo.

1. **Khoá bảng `ChonThi`:** làm [SP09](../sharepoint/SP09_phan_quyen.md) Phần 4, bước 1 đến 6, với bảng `ChonThi`.
2. **Khoá bảng `BaiLam`:** làm SP09 Phần 4, bước 1 đến 6, với bảng `BaiLam`.

👀 Ở trang «Permissions» của cả hai bảng, dòng của nhóm học sinh ghi «Read».

3. Mở ĐƯỜNG DẪN ỨNG DỤNG bằng tài khoản giáo viên phụ trách.

👀 Trang theo dõi, kéo xuống cuối thấy phần "Chấm bài thi".

4. Bấm nút "1. Xoá hết điểm cũ". Chờ đến khi hiện thông báo màu xanh "Đã xoá điểm cũ ở … dòng".
5. Bấm nút "2. Chấm: …" của **câu lạc bộ thứ nhất**. **Không bấm gì khác, không đóng trang** cho đến khi hiện thông báo và dòng kết quả dưới danh sách đổi thành tên câu lạc bộ đó kèm các con số.
6. Làm lại bước 5 cho **từng** câu lạc bộ còn lại trong danh sách, lần lượt từng cái một.
7. Mở bảng `ChonThi` trên SharePoint.

👀 Các ô `score_…` nằm cạnh ô `test_club_…` có mã câu lạc bộ đã có điểm từ 0 đến 10. Chọn 3 học sinh bất kỳ, mở bài của các em trong bảng `BaiLam`, so cột `tra_loi` với bảng `DapAn`, tự đếm số câu đúng: khớp với điểm.

8. Chỉ khi trường **không** muốn học sinh tự xem điểm: ở bảng `ChonThi` → ⚙ → «List settings» → «Permissions for this list» → đánh dấu dòng của nhóm học sinh → «Remove User Permissions» → «OK». Làm thêm với dòng có chữ «Visitors».
9. Tải bảng `ChonThi` về và đưa vào phần mềm xếp câu lạc bộ: [PA15](PA15_thu_3_hoc_sinh.md), mục "Tải dữ liệu về" bước 12 và mục "Sau hạn chót" bước 3.

⚠️ Dòng kết quả ghi "CHƯA CHẤM, vì bảng DapAn chưa có đáp án": cột `club_id` trong bảng `DapAn` của câu lạc bộ đó trống hoặc sai mã. Sửa trên SharePoint, bấm chấm lại.
⚠️ Sau bước 4, mở bảng `ChonThi` vẫn thấy điểm cũ: tuỳ chọn «Formula-level error management» chưa bật. Làm [PA02](PA02_tao_app.md) bước 18 đến 20, phát hành lại, rồi làm lại từ bước 3. Vẫn không được: bấm «Edit in grid view» ở bảng `ChonThi`, bôi đen các ô điểm, bấm phím `Delete`.
⚠️ Bấm chấm báo lỗi đỏ về quyền: tài khoản đang mở ứng dụng không có «Full Control» trên bảng `DapAn` hoặc `ChonThi`.

## Phần 11 — Bảng thử và dọn dẹp

**Chuẩn bị:** 3 tài khoản thử `HS901`, `HS902`, `HS903` có trong bảng `HocSinh` (như [PA15](PA15_thu_3_hoc_sinh.md), mục "Chuẩn bị"). Hai câu lạc bộ có thi (gọi là X và Y), mỗi câu lạc bộ có ít nhất 2 câu hỏi trong `CauHoi` và đáp án trong `DapAn`. Đã phát hành lại.

| # | Ai làm | Làm gì | 👀 Kết quả đúng | Không đạt thì xem | Đạt |
|---|---|---|---|---|---|
| 1 | HS901 | Mở ĐƯỜNG DẪN ỨNG DỤNG | Vào trang đăng ký như trước. **Không** hiện dải đỏ báo lỗi nào nhắc đến `DapAn` | ⚠️ dưới bảng | [ ] |
| 2 | HS901 | Mở thẳng địa chỉ: ĐỊA CHỈ TRANG + `/Lists/DapAn` | Báo không có quyền («Access Denied» hoặc «You need permission») | Phần 2 bước 8 đến 12 | [ ] |
| 3 | HS901 | Bấm "Chọn CLB thi tuyển →", chọn X ở ô 1 và Y ở ô 2, bấm "Lưu CLB thi", bấm "Làm bài thi →" | Danh sách có đúng 2 dòng X và Y, đều ghi "bấm để làm bài" | Phần 7.3 | [ ] |
| 4 | HS901 | Bấm dòng X | Hiện các câu hỏi của X theo thứ tự 1, 2…; không có câu nào của Y. Nút "Nộp bài" mờ | Phần 7.5 | [ ] |
| 5 | HS901 | Chọn đáp án cho từng câu của X (cố ý chọn **đúng hết**) | Dòng trạng thái đếm "Đã chọn 1 / …", "2 / …"; chọn đủ thì nút "Nộp bài" sáng | ⚠️ dưới bảng | [ ] |
| 6 | HS901 | Bấm "Nộp bài" | Thông báo "Đã nộp bài."; đề ẩn đi; dòng X ghi "đã nộp bài". Giáo viên mở bảng `BaiLam`: có một dòng `HS901`, `ma_bai` dạng `HS901\|mã của X`, `tra_loi` dạng `mã câu:chữ cái;…` | Phần 7.6 | [ ] |
| 7 | HS901 | Bấm lại dòng X | Chỉ hiện "em đã nộp bài lúc …", không hiện đề, không có nút nộp | Phần 7.5 mục «Visible» | [ ] |
| 8 | HS902 | Chọn thi X, lưu, làm bài X, cố ý chọn **sai hết**, nộp. Rồi mở thẳng ĐỊA CHỈ TRANG + `/Lists/BaiLam` | Chỉ thấy **một dòng** của `HS902`, không thấy bài của `HS901` | Phần 3 bước 12 | [ ] |
| 9 | HS903 | Chọn thi X, lưu, **không làm bài** | Bảng `ChonThi` có dòng `HS903` với `test_club_1` là mã của X | PA11 | [ ] |
| 10 | Bạn | Ở Phần 5, tạm đổi dòng `HanThi` thành ngày hôm qua (dùng đoạn `DateTimeValue` ở Phần 5) → phát hành lại. Rồi HS903 mở ứng dụng → "Chọn CLB thi tuyển →" → "Làm bài thi →" | HS903 thấy "Đã hết hạn làm bài thi.", bấm vào tên câu lạc bộ không hiện đề | Phần 5; Phần 7.5 mục «Visible» | [ ] |
| 11 | Bạn | Làm Phần 10 bước 1 đến 7 (chấm X, rồi chấm Y) | Kết quả X: "3 học sinh chọn thi; 2 bài đã nộp; 0 bài bị bỏ…; 1 học sinh chọn thi nhưng không nộp bài". Bảng `ChonThi`: `HS901` có `score_1` là 10 và `score_2` trống (chọn Y nhưng không làm); `HS902` có `score_1` là 0; `HS903` có `score_1` trống | Phần 9.3 | [ ] |
| 12 | Bạn | Tải bảng `ChonThi` về (PA15, "Tải dữ liệu về" bước 12), đưa vào phần mềm xếp câu lạc bộ sau tệp câu lạc bộ | Phần mềm nhận tệp chọn thi; điểm của `HS901` và `HS902` hiện đúng; `HS903` được báo "chưa chấm điểm" | Mục 8 của [hướng dẫn chi tiết](../../HUONG_DAN_POWER_APPS_DANG_KY.md) | [ ] |

⚠️ **Dòng 1 không đạt** (học sinh thấy lỗi đỏ nhắc đến `DapAn` ngay khi mở ứng dụng): gỡ bảng `DapAn` khỏi ứng dụng (màn hình thiết kế → hình cái trụ tròn «Data» → đưa chuột vào `DapAn` → «⋯» → «Remove»), ở cây bên trái bấm chuột phải `galCham` → «Delete», phát hành lại, và chấm theo "Chấm bằng Excel" ở Phần 12.
⚠️ **Dòng 5 không đạt** (bấm chọn mà số đếm không tăng): bấm `rdoChon`, sao chép toàn bộ đoạn ở mục «OnSelect», dán đoạn đó vào mục «OnChange» của `rdoChon`, rồi xoá trống mục «OnSelect». Phát hành lại.
⚠️ **Lựa chọn dài bị cắt chữ:** bấm `rdoChon`, mục «Height», đổi số `44` thành `60`.

**Dọn dẹp (bắt buộc trước khi cho học sinh thi thật):**

- [ ] Bảng `BaiLam`: xoá mọi dòng thử.
- [ ] Bảng `ChonThi`: xoá các dòng `HS901`, `HS902`, `HS903`.
- [ ] Bảng `NguyenVong`, `HocSinh`: xoá các dòng thử như ở PA15.
- [ ] **Mở khoá lại** hai bảng `ChonThi` và `BaiLam` (đã khoá ở dòng 10): ở trang «Permissions for this list» của từng bảng, đánh dấu dòng nhóm học sinh → «Edit User Permissions» → bỏ «Read», đánh dấu «Contribute» → «OK».
- [ ] `CauHoi` và `DapAn` chứa đề thật, cùng số dòng.
- [ ] Dòng `HanThi` (Phần 5) đã đổi về đúng ngày giờ thật; đã phát hành lại.

## Phần 12 — Đường khác

### So sánh ba đường

| | Bài thi trong ứng dụng (tệp này) | Microsoft Forms dạng bài kiểm tra | Google Forms (đang có sẵn) |
|---|---|---|---|
| Học sinh đăng nhập | Tài khoản trường, cùng ứng dụng | Tài khoản trường, mở thêm một trang | Tài khoản Google |
| Đáp án có lộ cho học sinh không | Không (bảng `DapAn` khoá) | Không (Forms giữ đáp án) | Không (Forms giữ đáp án) |
| Đề có lộ trước không | **Có**, nếu học sinh mở thẳng bảng `CauHoi` | Không, chỉ thấy khi mở biểu mẫu | Không |
| Chỉ hiện đề của câu lạc bộ đã chọn | Có, tự động theo bảng `ChonThi` | Phải dựng rẽ nhánh bằng tay, hoặc mỗi câu lạc bộ một biểu mẫu | Có (đã dựng sẵn bằng tệp `.gs`) |
| Tính giờ, trộn câu | Không | Có (tuỳ gói của trường) | Trộn câu có, tính giờ không |
| Điểm vào `ChonThi.score_…` | Tự động khi bấm chấm | **Không tự động**: giáo viên tải Excel từ Forms rồi nhập điểm | Không dùng `ChonThi`: có công cụ riêng tạo sổ nhập cho phần mềm |
| Công dựng | Nhiều (tệp này) | Vừa | Ít (có sẵn công cụ) |
| Đã chạy thử thật | Chưa | Chưa | Đã có quy trình dùng |

### Đường Microsoft Forms: một nút mở biểu mẫu thi

Dùng khi cần đề bí mật hoặc tính giờ. Ứng dụng vẫn lo phần đăng ký và chọn câu lạc bộ thi; bài thi làm trên Microsoft Forms.

1. Giáo viên tạo bài kiểm tra trên Microsoft Forms (trang `https://forms.office.com` → «New Quiz»), đặt chỉ người trong trường mới làm được và mỗi người một lần nộp.
2. Trong Forms bấm «Collect responses», bấm «Copy link» để lấy đường dẫn biểu mẫu.
3. Trong màn hình thiết kế: cây bên trái mở `scrChonThi`, bấm `conKhung_ChonThi`.
4. THÊM nút bấm (`Button`). ĐỔI TÊN thành:
```
btnMoForms
```
5. Bấm `btnMoForms`, rồi ĐIỀN 4 MỤC sau:

**«Text»** — dán:
```
"Làm bài thi trên Microsoft Forms →"
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
Launch("https://forms.office.com/r/XXXXXXXX")
```
6. Trong ô dài của mục «OnSelect»: bôi đen đoạn `https://forms.office.com/r/XXXXXXXX`, dán đường dẫn biểu mẫu thật đè lên (giữ hai dấu ngoặc kép).
7. Bấm `Ctrl` + `S`, phát hành lại.
8. Sau hạn: trong Forms, thẻ «Responses» → «Open results in Excel». Khoá bảng `ChonThi` (SP09 Phần 4), bấm «Edit in grid view» ở bảng `ChonThi`, gõ điểm thang 10 của từng học sinh vào ô `score_…` cùng số với ô `test_club_…` của câu lạc bộ đó.

Khi đi đường này thì **không làm** Phần 1 đến Phần 10 của tệp này.

Bản thiết kế đầy đủ hơn (mỗi câu lạc bộ một biểu mẫu, ứng dụng hiện trạng thái "đã làm", có công cụ chấm lại và ghép điểm) nằm ở [T4M_CONG_THI.md](../../../he_sinh_thai/T4M_CONG_THI.md) và mục 0 của [mau_forms_thi_clb/README.md](../../../../mau_forms_thi_clb/README.md). Hai tài liệu đó viết cho người phụ trách kỹ thuật và dùng **bộ bảng khác** với bộ bảng trong hướng dẫn này; đừng tự ghép, hãy báo người phụ trách.

### Đường Google Forms (đang có sẵn)

Một biểu mẫu Google Forms làm cả đăng ký lẫn thi: chọn Top 1 đến Top 10, tick tối đa 5 câu lạc bộ thi, chỉ hiện đề của câu lạc bộ đã chọn, tự chấm, xuất điểm theo từng câu lạc bộ. Đi đường này thì **không cần** ứng dụng Power Apps. Hướng dẫn: [HUONG_DAN_TUNG_BUOC.md](../../../../mau_forms_thi_clb/HUONG_DAN_TUNG_BUOC.md).

### Chấm bằng Excel (dự phòng khi nút chấm không dùng được)

Vẫn dùng Phần 1 đến Phần 8 (học sinh làm bài trong ứng dụng), chỉ thay việc chấm.

1. Khoá hai bảng `ChonThi` và `BaiLam` (Phần 10, bước 1 và 2).
2. Mở bảng `BaiLam` → «Export» → «Export to CSV». Làm tương tự với bảng `ChonThi` và bảng `DapAn`.
3. Mở Excel, tạo tệp trống. Đổi tên trang tính đầu thành `ChonThi`: bấm đúp vào tên trang tính ở hàng dưới cùng, dán:
```
ChonThi
```
4. Bấm dấu «+» để thêm trang tính, đổi tên thành:
```
BaiLam
```
5. Bấm dấu «+» để thêm trang tính nữa, đổi tên thành:
```
DapAn
```
6. Mở từng tệp `.csv` vừa tải, bấm `Ctrl` + `A`, `Ctrl` + `C`, sang trang tính cùng tên trong tệp mới, bấm ô **A1**, `Ctrl` + `V`.

👀 Trang `ChonThi`: cột A đến L là `student_id`, `name`, `test_club_1`, `score_1`, … `score_5`. Trang `BaiLam`: cột A đến F là `student_id`, `name`, `club_id`, `ma_bai`, `tra_loi`, `nop_luc`. Trang `DapAn`: cột A đến C là `ma_cau`, `club_id`, `dap_an`. Khác thứ tự này thì kéo cột cho đúng trước khi làm tiếp.

7. Trang `BaiLam`: bấm ô **G1**, gõ `diem`. Bấm ô **G2**, dán công thức, bấm `Enter`, rồi bấm đúp ô vuông nhỏ ở góc dưới phải ô G2 để điền xuống:
```
=IFERROR(ROUND(10*SUMPRODUCT((DapAn!$B$2:$B$3000=C2)*ISNUMBER(SEARCH(";"&DapAn!$A$2:$A$3000&":"&DapAn!$C$2:$C$3000&";",";"&E2&";"))*((LEN(";"&E2)-LEN(SUBSTITUTE(";"&E2,";"&DapAn!$A$2:$A$3000&":","")))/LEN(";"&DapAn!$A$2:$A$3000&":")=1))/COUNTIF(DapAn!$B$2:$B$3000,C2),1),"")
```
8. Trang `ChonThi`: xoá hết số đang có trong các cột D, F, H, J, L (từ dòng 2 trở xuống).
9. Bấm ô **D2**, dán công thức, bấm `Enter`:
```
=IF(C2="","",IFERROR(INDEX(BaiLam!$G$2:$G$6000,MATCH($A2&"|"&C2,BaiLam!$D$2:$D$6000,0)),""))
```
10. Bấm ô **D2**, bấm `Ctrl` + `C`. Bấm ô **F2**, `Ctrl` + `V`. Làm tương tự với **H2**, **J2**, **L2**.
11. Điền xuống cho **từng cột điểm một**: bấm ô **D2**, bấm đúp ô vuông nhỏ ở góc dưới phải ô. Làm y như vậy với ô **F2**, rồi **H2**, **J2**, **L2**. (Không bôi đen cả dải D2 đến L2 để điền xuống: làm vậy sẽ ghi đè các cột `test_club_…`.)

👀 Cột điểm cạnh mỗi câu lạc bộ thi có số từ 0 đến 10; học sinh không nộp bài thì trống. Các cột `test_club_…` không bị thay đổi.

12. Bấm vào trang tính `ChonThi`. Bấm «File» → «Save As», chọn kiểu «CSV UTF-8 (Comma delimited)», đặt tên `ChonThi_co_diem`, bấm «Save». Tệp này đưa vào phần mềm xếp câu lạc bộ thay cho tệp `ChonThi` tải thẳng từ SharePoint.

⚠️ Ở bước 6, chữ tiếng Việt trong cột `name` bị vỡ: xem Phụ lục A của [hướng dẫn chi tiết](../../HUONG_DAN_POWER_APPS_DANG_KY.md) (mở tệp `.csv` bằng «Data» → «From Text/CSV», chọn UTF-8).

- [ ] Xong.
