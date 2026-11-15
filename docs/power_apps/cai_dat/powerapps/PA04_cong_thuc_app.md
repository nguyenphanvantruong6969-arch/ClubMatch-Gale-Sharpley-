# PA04 — Công thức chung của App

⏱ 10 phút · [← PA03](PA03_noi_du_lieu.md) · Tiếp: [PA05](PA05_tao_man_hinh_va_khung.md)

## Cách dán công thức (dùng cho mọi tệp PA)
1. Cây bên trái (**Tree view**, biểu tượng ☰ nhiều lớp): bấm tên đối tượng.
2. Thanh công thức: ô **thả xuống bên trái** → chọn **tên thuộc tính**.
3. Ô **fx** bên phải: xoá hết nội dung cũ, dán công thức.
4. Bấm ra ngoài. Gạch đỏ do **chưa có** màn hình/đối tượng được nhắc tới → bình thường, sẽ hết khi làm xong các tệp sau.

> ⚠️ Nếu công thức báo `club_id` hoặc `student_id` "*Name isn't valid*": thay chữ đó bằng `Title` ở **mọi** công thức.
> ⚠️ Máy cài ngôn ngữ dùng dấu phẩy thập phân có thể yêu cầu `;` thay `,` và `;;` thay `;`. Nếu công thức dán vào báo lỗi hàng loạt: vào **Settings → General → Formula separators** hoặc đổi ngôn ngữ trình duyệt sang English.

## Bước 1 — App.Formulas
5. Cây: bấm **App**.
6. Thuộc tính: **Formulas**.
7. Dán, rồi **sửa 3 dòng đầu** cho trường bạn:
```
HanChot = DateTimeValue("2026-12-01 17:00");
SoNguyenVongToiDa = 5;
DSQuanTri = ["gv.a@truong.edu.vn", "gv.b@truong.edu.vn"];
EmailToi = Lower(User().Email);
LaQuanTri = EmailToi in DSQuanTri;
HetHan = Now() > HanChot;
LaPhone = App.Width < 600;
```
   - `HanChot`: ngày giờ hết hạn, dạng `năm-tháng-ngày giờ:phút`.
   - `SoNguyenVongToiDa`: 1 đến 10.
   - `DSQuanTri`: email giáo viên quản trị, **chữ thường**, cách nhau dấu phẩy.

⚠️ Không có thuộc tính **Formulas**: bỏ bước 1, ở bước 2 dán **bản thay thế** bên dưới.

## Bước 2 — App.OnStart
8. Cây: **App** → thuộc tính **OnStart** → dán:
```
Set(varHS, LookUp(HocSinh, email = Lower(User().Email)));
Set(varNV, LookUp(NguyenVong, student_id = varHS.student_id));
ClearCollect(colCLB, SortByColumns(CLB, "name"))
```

**Bản thay thế (chỉ khi không có Formulas)** — dán vào OnStart thay cho khối trên:
```
Set(HanChot, DateTimeValue("2026-12-01 17:00"));
Set(SoNguyenVongToiDa, 5);
Set(DSQuanTri, ["gv.a@truong.edu.vn", "gv.b@truong.edu.vn"]);
Set(EmailToi, Lower(User().Email));
Set(LaQuanTri, EmailToi in DSQuanTri);
Set(HetHan, Now() > HanChot);
Set(varHS, LookUp(HocSinh, email = EmailToi));
Set(varNV, LookUp(NguyenVong, student_id = varHS.student_id));
ClearCollect(colCLB, SortByColumns(CLB, "name"))
```
   và ở mọi công thức sau, thay `LaPhone` bằng `(App.Width < 600)`.

9. Cây: **App** → bấm **⋯** → **Run OnStart**.
   👀 Không báo lỗi đỏ ở OnStart.
10. **Ctrl+S**.

## Bước 3 — App.StartScreen
**Để sau**, làm ở [PA13](PA13_man_dau_tien_va_chay_thu.md) (cần có đủ màn hình trước).

- [ ] Xong bước 1 (hoặc bản thay thế) và bước 2.
