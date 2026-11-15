# SP00 — Tự động làm SP02 đến SP09 bằng một tệp lệnh (dành cho bộ phận tin học)

[← Mục lục](../00_MUC_LUC.md) · Tiếp theo: [PA01](../powerapps/PA01_dang_nhap_moi_truong.md)

**Dành cho ai:** người có **quyền quản trị** Microsoft 365 của trường (thường là bộ phận tin học), dùng máy tính Windows.

**Tệp lệnh làm thay những việc sau:**

| Việc | Thay cho tệp |
|---|---|
| Tạo trang `CLB-2026` (riêng tư) | SP02 |
| Tạo các bảng `CLB`, `HocSinh`, `NguyenVong` (và `ChonThi`, `CauHoi`, `DapAn`, `BaiLam` nếu chọn), đúng từng tên cột | SP03 đến SP07, PA16 Phần 1 đến 3 |
| Đánh chỉ mục, chặn trùng | SP04 đến SP07 |
| Cách xem `Xuat_kiosk` để tải dữ liệu cho phần mềm xếp câu lạc bộ | PA15 |
| Nạp danh sách học sinh và câu lạc bộ từ tệp CSV | SP08 |
| Giáo viên toàn quyền; học sinh chỉ xem; học sinh chỉ thấy và sửa phiếu của chính mình; bảng đáp án chỉ giáo viên mở được | SP09, PA16 Phần 2 |

**Tệp lệnh KHÔNG làm:**
- Không tạo nhóm tài khoản học sinh (làm ở Bước 5 nếu trường chưa có).
- Không dựng ứng dụng Power Apps (vẫn làm PA01 trở đi).
- Không nạp đề thi (PA16 Phần 4 vẫn làm tay).

**An toàn:**
- Tệp lệnh **chỉ tạo mới và thêm**, không có lệnh xoá nào.
- Chạy lại nhiều lần được: thứ gì đã có thì bỏ qua; học sinh có mã đã tồn tại thì không thêm lần nữa.
- Có **chế độ chạy thử** (Bước 8): chỉ in ra việc sẽ làm, không ghi gì.
- Mỗi lần chạy để lại một tệp nhật ký `nhat_ky_sharepoint_….txt` trong thư mục đang đứng.

⚠️ Tệp lệnh này **chưa được chạy trên một trường thật**. Lần đầu nên chạy với tên trang thử (Bước 9), kiểm tra xong mới chạy với tên thật.

---

## Bước 1 — Cài PowerShell 7

1. Bấm phím `Windows`, gõ `PowerShell`, bấm «Windows PowerShell» (cửa sổ nền xanh hoặc đen).
2. Dán lệnh dưới, bấm `Enter`:
```
winget install --id Microsoft.PowerShell --source winget
```
3. Nếu hỏi đồng ý điều khoản: gõ `Y`, bấm `Enter`.

👀 Dòng cuối báo «Successfully installed».

4. Đóng cửa sổ.
5. Bấm phím `Windows`, gõ `PowerShell 7`, bấm «PowerShell 7 (x64)».

👀 Cửa sổ có dòng `PowerShell 7.…` ở trên cùng. **Từ đây trở đi, mọi lệnh đều dán vào cửa sổ PowerShell 7 này.**

⚠️ Báo không có `winget`: tải bộ cài «PowerShell-7…-win-x64.msi» tại trang `https://aka.ms/powershell-release?tag=stable`, chạy, bấm «Next» đến hết.

## Bước 2 — Cài công cụ PnP

6. Dán, bấm `Enter`:
```
Install-Module PnP.PowerShell -Scope CurrentUser -Force
```
7. Nếu hỏi «Untrusted repository»: gõ `A`, bấm `Enter`.
8. Kiểm tra, dán:
```
Get-Module PnP.PowerShell -ListAvailable | Select-Object Name, Version
```

👀 Một dòng `PnP.PowerShell` kèm số phiên bản (3.0 trở lên).

## Bước 3 — Đăng ký ứng dụng cho công cụ PnP (làm một lần cho cả trường)

Microsoft bắt công cụ PnP phải có một "ứng dụng" đăng ký riêng của trường thì mới đăng nhập được.

9. Lấy **tên miền gốc** của trường: vào trang quản trị `https://admin.microsoft.com` → «Settings» → «Domains». Tìm dòng kết thúc bằng `.onmicrosoft.com`, ví dụ `truongabc.onmicrosoft.com`. Ghi vào sổ tay: **TÊN MIỀN GỐC**.
10. Dán lệnh dưới vào PowerShell 7, **sửa** `truongabc.onmicrosoft.com` thành TÊN MIỀN GỐC, rồi bấm `Enter`:
```
Register-PnPEntraIDAppForInteractiveLogin -ApplicationName "PnP CLB" -Tenant truongabc.onmicrosoft.com -Interactive
```
11. Trình duyệt mở ra: đăng nhập bằng tài khoản quản trị.
12. Trang hỏi cấp quyền («Permissions requested»): đánh dấu «Consent on behalf of your organization», bấm «Accept».

👀 PowerShell in ra một dòng có chữ `AzureAppId/ClientId` và một chuỗi dạng `1a2b3c4d-....`.

13. Chép chuỗi đó vào sổ tay: **MÃ ỨNG DỤNG**.

⚠️ Báo lỗi không nhận lệnh `Register-PnPEntraIDAppForInteractiveLogin`: bản PnP quá cũ. Làm lại bước 6.

## Bước 4 — Lấy tệp lệnh về máy

14. Tạo thư mục mới, đúng đường dẫn:
```
C:\CLB
```
15. Chép 3 tệp trong thư mục `docs/power_apps/cai_dat/sharepoint/tu_dong/` của dự án vào `C:\CLB`:
    - `tao_moi_truong_sharepoint.ps1`
    - `mau_HocSinh.csv`
    - `mau_CLB.csv`
16. Trong PowerShell 7, dán:
```
Set-Location C:\CLB
```
17. Bỏ dấu "tải từ mạng" của các tệp, dán:
```
Get-ChildItem C:\CLB | Unblock-File
```
18. Cho phép chạy tệp lệnh trong cửa sổ này (chỉ cửa sổ này, đóng là hết), dán:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

## Bước 5 — Nhóm tài khoản học sinh

Trường đã có nhóm gom tài khoản học sinh tham gia: chép **thư điện tử của nhóm** vào sổ tay, đặt tên **NHÓM HỌC SINH**, rồi sang Bước 6.

Chưa có thì tạo:

19. Vào `https://admin.microsoft.com` → «Teams & groups» → «Active teams & groups» → thẻ «Security groups» → «Add a security group».
20. Ô «Name», dán:
```
HS-CLB-2026
```
21. Bấm «Next» → «Next» → «Create group» → «Close».
22. Bấm vào tên nhóm `HS-CLB-2026` → thẻ «Members» → «View all and manage members» → «Add members» → thêm tài khoản học sinh → «Save».
23. Thẻ «General»: chép chuỗi ở dòng «Object ID» (dạng `1a2b3c4d-....`) vào sổ tay, đặt tên **NHÓM HỌC SINH**.

⚠️ Nhóm bảo mật không có thư điện tử, nên dùng «Object ID». Tệp lệnh nhận cả hai kiểu.

## Bước 6 — Chuẩn bị hai tệp CSV

Làm hai tệp Excel đúng như [SP08](SP08_nap_excel.md) Phần 1 và Phần 2 (dòng tiêu đề, làm sạch thư điện tử, xoá dòng trùng). Sau đó lưu dạng CSV:

24. Trong Excel: «File» → «Save As» → «Browse».
25. Ô «Save as type»: chọn «CSV UTF-8 (Comma delimited) (*.csv)». **Không** chọn loại «CSV (Comma delimited)» không có chữ UTF-8 (sẽ mất dấu tiếng Việt).
26. Lưu vào `C:\CLB`, tên tệp học sinh:
```
HocSinh.csv
```
27. Tệp câu lạc bộ:
```
CLB.csv
```

Dòng đầu của hai tệp phải đúng như sau (đã có sẵn trong `mau_HocSinh.csv`, `mau_CLB.csv` để đối chiếu):
```
student_id,name,class_id,email,reserve_group
```
```
club_id,name,capacity,reserve_capacity,reserve_group,mo_ta,co_thi
```

Quy tắc mà tệp lệnh kiểm tra (dòng sai bị bỏ qua và báo đỏ, các dòng khác vẫn nạp):
- `club_id`: chỉ chữ thường không dấu, số, dấu gạch dưới. Ví dụ `clb_bongro`.
- `capacity`: số nguyên lớn hơn 0. `reserve_capacity`: từ 0 đến `capacity`.
- `co_thi`: `Yes` hoặc `No`.
- `email`: đúng dạng thư điện tử; tệp lệnh tự đổi về chữ thường.
- Mã trùng trong tệp: giữ dòng đầu, bỏ dòng sau.

## Bước 7 — Điền thông tin cho lệnh chạy

28. Mở Notepad, dán khối dưới:
```
$thamSo = @{
    TenTenant     = "truongabc"
    ClientId      = "MÃ ỨNG DỤNG"
    EmailChuTrang = "admin@truongabc.edu.vn"
    TenTrang      = "CLB-2026"
    EmailGiaoVien = @("gv.a@truongabc.edu.vn", "gv.b@truongabc.edu.vn")
    NhomHocSinh   = "NHÓM HỌC SINH"
    TepHocSinh    = "C:\CLB\HocSinh.csv"
    TepCLB        = "C:\CLB\CLB.csv"
}
```
29. Sửa từng dòng (giữ nguyên dấu ngoặc kép):

| Dòng | Thay bằng |
|---|---|
| `TenTenant` | Phần đầu địa chỉ SharePoint. Trường có `https://truongabc.sharepoint.com` thì ghi `truongabc` |
| `ClientId` | MÃ ỨNG DỤNG (Bước 3) |
| `EmailChuTrang` | Thư điện tử người đứng tên chủ trang |
| `TenTrang` | Để nguyên `CLB-2026`, hoặc tên khác **không dấu, không cách** |
| `EmailGiaoVien` | Thư điện tử giáo viên phụ trách, mỗi địa chỉ trong ngoặc kép, cách nhau dấu phẩy |
| `NhomHocSinh` | NHÓM HỌC SINH (Bước 5) |

30. Bôi đen cả khối đã sửa, `Ctrl` + `C`, dán vào PowerShell 7, bấm `Enter`.

👀 Không báo lỗi đỏ, con trỏ xuống dòng mới.

## Bước 8 — Chạy thử (không ghi gì)

31. Chọn **một** trong ba lệnh, dán, bấm `Enter`:

Không có câu lạc bộ nào thi tuyển:
```
.\tao_moi_truong_sharepoint.ps1 @thamSo -ChayThu
```
Có thi tuyển, điểm do giáo viên nhập (SP07):
```
.\tao_moi_truong_sharepoint.ps1 @thamSo -CoThiTuyen -ChayThu
```
Có bài thi làm ngay trong ứng dụng (PA16):
```
.\tao_moi_truong_sharepoint.ps1 @thamSo -CoBaiThi -ChayThu
```
32. Trình duyệt mở ra hỏi đăng nhập: đăng nhập bằng tài khoản quản trị.

👀 Các dòng màu vàng bắt đầu bằng `[THỬ] Sẽ làm:`. Dòng cuối: `Đây là chạy thử. Bỏ -ChayThu để làm thật.`

33. Đọc kỹ danh sách việc sẽ làm: tên trang, tên bảng, tên cột đúng như mong muốn.

## Bước 9 — Chạy thật trên trang thử trước

34. Đổi tên trang sang tên thử, dán:
```
$thamSo.TenTrang = "CLB-THU"
```
35. Đổi tệp CSV sang tệp mẫu (3 học sinh giả, 3 câu lạc bộ giả), dán:
```
$thamSo.TepHocSinh = "C:\CLB\mau_HocSinh.csv"; $thamSo.TepCLB = "C:\CLB\mau_CLB.csv"
```
36. Chạy lệnh ở bước 31, **bỏ chữ** ` -ChayThu` ở cuối. Ví dụ:
```
.\tao_moi_truong_sharepoint.ps1 @thamSo -CoThiTuyen
```

👀 Lần lượt 6 phần `[1/6]` đến `[6/6]`, các dòng xanh bắt đầu bằng `+`. Cuối cùng: `=== Xong ===` và `ĐỊA CHỈ TRANG: https://…/sites/CLB-THU`.

37. Mở ĐỊA CHỈ TRANG vừa in ra trong trình duyệt, kiểm tra theo bảng:

| Kiểm | Đúng là |
|---|---|
| ⚙ → «Site contents» | Có các bảng `CLB`, `HocSinh`, `NguyenVong` (và `ChonThi`…), `HocSinh` có 3 dòng, `CLB` có 3 dòng |
| Mở bảng `NguyenVong` | Tên cột: `student_id`, `name`, `pref_1` … `pref_10`, `email`, `nop_luc`, `so_lan_nop` |
| Bảng `NguyenVong` → ô chọn cách xem (góc trên bên phải, cạnh nút lọc) | Có cách xem `Xuat_kiosk` |
| `NguyenVong` → ⚙ → «List settings» → «Advanced settings» | «Item-level Permissions» đang chọn hai mục "created by the user" |

38. Chạy lại lệnh ở bước 36 thêm một lần.

👀 Hầu hết các dòng là `= Đã có, bỏ qua`. Dòng nạp dữ liệu báo `thêm 0, đã có (bỏ qua) 3`.

⚠️ Trang thử `CLB-THU` không tự xoá. Kiểm tra xong, xoá tay ở `https://admin.microsoft.com` → «Show all» → «SharePoint» → «Active sites» → chọn `CLB-THU` → «Delete».

## Bước 10 — Chạy thật

39. Đặt lại tên trang thật và tệp thật, dán (sửa nếu bạn dùng tên khác):
```
$thamSo.TenTrang = "CLB-2026"; $thamSo.TepHocSinh = "C:\CLB\HocSinh.csv"; $thamSo.TepCLB = "C:\CLB\CLB.csv"
```
40. Chạy lại lệnh ở bước 36.
41. Chép dòng `ĐỊA CHỈ TRANG: …` cuối cùng vào sổ tay, gửi cho người dựng ứng dụng. Đây chính là ĐỊA CHỈ TRANG mà các tệp PA dùng.
42. Gửi kèm tệp nhật ký `nhat_ky_sharepoint_….txt` trong `C:\CLB`.

**Xong.** Người dựng ứng dụng bỏ qua SP01 đến SP09, sang thẳng [PA01](../powerapps/PA01_dang_nhap_moi_truong.md).

**Thêm học sinh đến muộn:** thêm dòng vào `HocSinh.csv`, chạy lại bước 40. Học sinh đã có không bị đụng tới.

---

## Bảng xử lý sự cố

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `File … cannot be loaded because running scripts is disabled` | Chưa cho phép chạy tệp lệnh | Làm bước 18 trong đúng cửa sổ đang dùng |
| `#Requires … 7.2` hoặc lệnh lạ không chạy | Đang ở Windows PowerShell cũ | Mở «PowerShell 7 (x64)» (bước 5), làm lại từ bước 16 |
| `Chưa cài PnP.PowerShell` | Thiếu bước 6, hoặc cài ở cửa sổ khác | Làm lại bước 6 trong PowerShell 7 |
| Đăng nhập báo `AADSTS700016` hoặc `application … not found` | MÃ ỨNG DỤNG sai | Chép lại MÃ ỨNG DỤNG ở Bước 3, sửa dòng `ClientId`, dán lại khối Bước 7 |
| Đăng nhập báo cần quản trị viên đồng ý («Need admin approval») | Bước 12 chưa bấm «Consent on behalf of your organization» | Làm lại Bước 3 bằng tài khoản quản trị |
| `Access denied` ở phần `[1/6]` | Tài khoản không phải quản trị SharePoint | Đăng nhập bằng tài khoản có vai trò «SharePoint Administrator» |
| `Không thấy tệp: …csv` | Sai đường dẫn hoặc tên tệp | Kiểm tra tệp nằm trong `C:\CLB`, đúng tên ở Bước 6 |
| `Tệp … thiếu cột: …` | Dòng đầu CSV khác mẫu | Sửa dòng đầu đúng như Bước 6 |
| Tên học sinh trên SharePoint mất dấu (`Nguy?n`) | Lưu CSV không phải UTF-8 | Lưu lại đúng «CSV UTF-8» (bước 25), chạy lại. Dòng đã nạp sai thì xoá tay trên SharePoint rồi chạy lại |
| `Không tìm thấy nhóm học sinh` | Thư điện tử nhóm sai, hoặc là nhóm bảo mật | Dùng «Object ID» của nhóm (bước 23) |
| Dòng đỏ `Dòng N bỏ qua: …` | Dòng đó sai quy tắc ở Bước 6 | Sửa dòng trong CSV, chạy lại; các dòng đúng đã nạp không bị nạp lại |
| `Không đổi được tên hiển thị của LinkTitle` (vàng) | Một số trang không cho đổi | Không ảnh hưởng, bỏ qua |
| Phần `[3/6]` báo lỗi khi chặn trùng | Bảng đã có dữ liệu trùng (do nhập tay trước đó) | Mở bảng, xoá dòng trùng, chạy lại |
| Chạy xong nhưng học sinh vẫn thấy phiếu của bạn | Học sinh có quyền cao hơn (ví dụ được thêm làm chủ trang) | Kiểm tra học sinh **không** nằm trong nhóm chủ trang |

Gặp lỗi khác: gửi tệp nhật ký `nhat_ky_sharepoint_….txt` cho người phụ trách.
