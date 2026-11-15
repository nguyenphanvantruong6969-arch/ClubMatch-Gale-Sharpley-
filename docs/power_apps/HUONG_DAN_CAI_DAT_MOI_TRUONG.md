# Hướng dẫn cài đặt toàn bộ môi trường đăng ký CLB (từ con số 0)

> **Dành cho ai?** Giáo viên hoặc cán bộ IT chưa từng dùng Power Apps. Đọc từ trên xuống, làm theo từng bước, tick vào ô vuông khi xong. Không cần hỏi ai thêm.
> **Kết quả cuối cùng:** học sinh quét mã QR, đăng ký nguyện vọng CLB trên điện thoại; giáo viên xuất dữ liệu và nạp vào phần mềm **rbda-kiosk** trên máy Windows để xếp CLB.
> **Tài liệu kỹ thuật đi kèm:** [`HUONG_DAN_POWER_APPS_DANG_KY.md`](HUONG_DAN_POWER_APPS_DANG_KY.md) (công thức chi tiết, gọi tắt là **Tài liệu kỹ thuật**). Tài liệu này chỉ hướng dẫn thao tác; công thức nằm ở tài liệu kia.
> **Lưu ý về giao diện Microsoft:** Microsoft đổi tên nút và vị trí menu khá thường xuyên, và mỗi trường có thể thấy bản khác nhau. Khi tên nút bạn thấy khác tài liệu, mình luôn ghi đường dẫn thay thế. Nếu vẫn không thấy, tìm nút có ý nghĩa tương tự hoặc dùng ô tìm kiếm của trang. Các ví dụ dưới đây là **dữ liệu giả để thử**, không phải số liệu khảo sát thật.

### Giải thích 6 từ sẽ gặp nhiều lần (đọc một lần là đủ)

| Từ | Nghĩa đơn giản |
|---|---|
| **Tenant** (tài khoản tổ chức) | "Toà nhà Microsoft" riêng của trường bạn. Mọi tài khoản dạng `ten@truong.edu.vn` nằm trong đó |
| **SharePoint site** | Một "phòng" trên mạng của trường để chứa danh sách và tệp |
| **List** (danh sách) | Một bảng giống Excel nằm trong site. Mỗi dòng là một bản ghi, mỗi cột là một thông tin |
| **Power Apps / Canvas app** | Công cụ vẽ ra ứng dụng bằng cách kéo thả, như làm slide. Ứng dụng đọc/ghi vào các List |
| **Environment** (môi trường) | "Ngăn tủ" riêng trong Power Apps. App và dữ liệu kết nối chỉ nằm trong một ngăn. Chọn nhầm ngăn là lỗi hay gặp nhất |
| **Connector** (kết nối) | Sợi dây nối app với nguồn dữ liệu, ở đây là SharePoint |

### Sơ đồ toàn bộ

```
Học sinh (điện thoại) -> Power Apps -> 4 List trong SharePoint -> xuất CSV -> rbda-kiosk (Windows)
```

### Cần bao lâu?
Khoảng 3 đến 5 giờ nếu mọi quyền đã có sẵn; có thể thêm vài ngày nếu phải chờ IT cấp quyền (mục 0).

---

## 0. Kiểm tra điều kiện cần có

Làm mục này **đầu tiên**. Nếu thiếu quyền, bạn sẽ bị kẹt giữa chừng.

### 0.1. Bảng quyền cần có

| # | Cần có | Ai cấp | Tự kiểm tra thế nào |
|---|---|---|---|
| A | Tài khoản Microsoft 365 Education của trường (dạng `ten@truong.edu.vn`) | IT trường | Mục 0.2 |
| B | Giấy phép **Power Apps** (thường đã nằm trong gói Microsoft 365 Education; tên gọi: "Power Apps for Microsoft 365") | Quản trị viên M365 (Global admin / License admin) | Mục 0.3 |
| C | Quyền **tạo SharePoint site** | Quản trị viên SharePoint | Mục 0.4 |
| D | Quyền **tạo / dùng nhóm Microsoft 365 hoặc nhóm bảo mật** (để cấp quyền cho từng khối học sinh) | Quản trị viên M365 | Mục 0.5 |
| E | Quyền **tạo app** trong Environment của trường | Quản trị viên Power Platform | Mục 0.3 và 4.2 |
| F | Máy Windows 10/11 để cài rbda-kiosk (không cần quyền quản trị cho cách cơ bản) | IT trường | Mục 6 |

> Dữ liệu học sinh là dữ liệu cá nhân. Chỉ dùng tài khoản của trường; không dùng tài khoản Microsoft cá nhân (`@outlook.com`, `@gmail.com`).

### 0.2. Kiểm tra tài khoản (A)
- [ ] Mở trình duyệt, vào `https://www.office.com`, bấm **Sign in** (Đăng nhập), nhập email trường.
- Bạn sẽ thấy: trang chủ Microsoft 365 có tên bạn ở góc trên bên phải và một cột biểu tượng ứng dụng (Word, Excel, SharePoint...).
- Nếu báo "tài khoản không tồn tại" hoặc "không thể đăng nhập": gửi IT (mẫu ở 0.7).

### 0.3. Kiểm tra giấy phép Power Apps (B, E)
- [ ] Vào `https://make.powerapps.com`, đăng nhập bằng tài khoản trường.
- Bạn sẽ thấy: trang chủ **Power Apps** có menu bên trái (Home, Create, Learn, Apps...). Có thể có một cửa sổ chào mừng hỏi quốc gia/vùng: chọn **Vietnam**, bấm **Get started**.
- Nếu thay vì vậy hiện thông báo như "Bạn cần giấy phép" / "You need a license" / "Your organization has not enabled Power Apps": thiếu giấy phép, gửi IT.
- Trang này còn một cách kiểm khác: vào `https://admin.microsoft.com` (nếu bạn không phải quản trị viên sẽ bị chặn, bình thường), hoặc `https://portal.office.com/account` -> **Subscriptions** (Đăng ký) -> xem danh sách gói. Có thể giao diện này khác theo trường.

### 0.4. Kiểm tra quyền tạo SharePoint site (C)
- [ ] Từ trang `office.com`, bấm biểu tượng **SharePoint** (nếu không thấy: bấm chấm 9 ô vuông ở góc trên trái, hoặc tìm "SharePoint").
- Bạn sẽ thấy: trang **SharePoint Start** với nút **+ Create site** (Tạo site) ở góc trên bên trái.
- Nếu **không có** nút **Create site**, hoặc bấm vào báo "bạn không có quyền": thiếu quyền C. Gửi IT.

### 0.5. Kiểm tra nhóm (D)
- [ ] Vào `https://outlook.office.com` -> thanh bên trái kéo xuống **Groups** (Nhóm) -> bấm **New group** / **Tạo nhóm**.
- Nếu tạo được: có quyền D. Nếu không có nút này: bạn vẫn làm được phần lớn hướng dẫn nhưng không tự tạo được nhóm; nhờ IT tạo sẵn nhóm học sinh (mẫu ở 0.7).
- Cách khác (có thể khác theo trường): hỏi IT trường có nhóm như "HS-Khoi10", "HS-Toan-truong" chưa. Có sẵn thì chỉ cần xin tên nhóm.

### 0.6. Chuẩn bị thông tin (chuẩn bị trước, đỡ dừng giữa chừng)
- [ ] Danh sách học sinh: Mã HS, Họ tên, Lớp, **email trường của em**, Nhóm ưu tiên (nếu có).
- [ ] Danh sách CLB: Mã CLB, Tên, Chỉ tiêu, Suất ưu tiên, Nhóm ưu tiên.
- [ ] Hạn chót nộp nguyện vọng (ngày giờ).
- [ ] Email các giáo viên quản trị (người được xem số liệu).
- [ ] Có học sinh có email trường chưa? Nếu chưa, hỏi IT: học sinh không có email thì **không** dùng được app này.

### 0.7. Tin nhắn gửi IT (copy nguyên, sửa phần trong `[ ]`)

```
Kính gửi anh/chị phụ trách CNTT trường [tên trường],

Em là [họ tên], giáo viên [bộ môn/chức vụ]. Em đang chuẩn bị cho học sinh
đăng ký câu lạc bộ qua một ứng dụng Power Apps lưu dữ liệu ở SharePoint
(chỉ dùng tính năng có sẵn trong Microsoft 365 Education, không dùng tính
năng trả phí thêm). Nhờ anh/chị kiểm tra và cấp giúp em tài khoản
[email của em] các quyền sau (đánh dấu mục còn thiếu):

[ ] 1. Giấy phép Power Apps (gói "Power Apps for Microsoft 365" hoặc tương đương)
[ ] 2. Quyền tạo SharePoint site (Team site)
[ ] 3. Quyền tạo ứng dụng Canvas trong Environment [tên Environment, ví dụ
       "XCL Education Group"] và quyền kết nối SharePoint
[ ] 4. Một nhóm Microsoft 365 / nhóm bảo mật chứa tài khoản học sinh các lớp
       tham gia (tên gợi ý: HS-CLB-2026), em là chủ sở hữu (owner) hoặc
       anh/chị gửi em tên nhóm
[ ] 5. Chính sách của trường có chặn học sinh dùng Power Apps trên điện
       thoại không? Nếu có, nhờ mở cho nhóm HS-CLB-2026

Thời hạn em cần xong: [ngày]. Học sinh sẽ nộp nguyện vọng từ [ngày] đến [ngày].
Em xin cảm ơn anh/chị.
```

**Chỉ sang bước 1 khi mục A, B, C đã đạt.** D và E có thể bổ sung sau.

---

## 1. Tạo SharePoint site

**Bước 1.1 – Tạo site**
- [ ] Vào `office.com` -> **SharePoint** -> **+ Create site**.
- [ ] Chọn **Team site** (Site nhóm).
- [ ] Nếu hỏi mẫu (template): chọn **Standard team** hoặc **Blank** (trống). Bấm **Use template** / **Next**.
- [ ] **Site name:** `CLB-2026`. Xem địa chỉ ở dòng dưới (Site address), ghi lại, ví dụ `https://truong.sharepoint.com/sites/CLB-2026`.
- [ ] **Privacy settings** (Quyền riêng tư): chọn **Private - only members can access this site** (Riêng tư). Không chọn Public.
- [ ] Bấm **Next** / **Create site**. Có thể hỏi thêm thành viên: bỏ qua (**Finish**), mục 3 sẽ cấp quyền.
- Bạn sẽ thấy: trang chủ site với tên `CLB-2026` ở trên, menu bên trái (Home, Conversations, Documents, Pages, Site contents...).
- Nếu báo "tên đã tồn tại": thêm năm học, ví dụ `CLB-2026-A`.

**Bước 1.2 – Ghi lại địa chỉ site**
- [ ] Copy địa chỉ trên thanh địa chỉ trình duyệt vào sổ tay (sẽ dùng ở mục 4 và 7).

---

## 2. Tạo 4 List và nạp dữ liệu

Cách vào chỗ tạo List: ở site `CLB-2026` bấm **⚙ (Settings, hình bánh răng, góc trên bên phải) -> Site contents** (Nội dung site) -> **New -> List** (nếu không thấy menu **New** ở đầu trang: bấm **+ New** rồi chọn **List**; tên có thể hơi khác).

> **Quy tắc vàng đặt tên cột:** đặt **đúng chữ thường, có gạch dưới** như bảng dưới, ngay từ lúc tạo cột. Sau này xuất CSV, tiêu đề cột đúng tên là kiosk nhận được ngay. Đổi tên sau đó **không** đổi tên bên trong, và công thức sẽ rối (xem mục 8).
> **Nên bỏ dấu cách khi tạo cột:** ví dụ gõ `pref_1`, không gõ `pref 1`. SharePoint sẽ biến dấu cách thành `_x0020_` trong tên bên trong.

### 2.0. Cách tạo một List trống và thêm cột (làm lại cho từng List)

- [ ] **Site contents -> New -> List -> Blank list**. Đặt tên (đúng chữ hoa/thường: `CLB`, `HocSinh`, `NguyenVong`, `ChonThi`), bỏ tick "Show in site navigation" nếu muốn gọn, bấm **Create**.
- Bạn sẽ thấy: một bảng trống chỉ có một cột **Title** (hoặc "Tiêu đề").
- **Đổi tên cột Title:** bấm tiêu đề cột **Title** -> **Column settings -> Rename** (đổi tên) -> gõ tên mới -> **Save**. Nếu không thấy: bấm **⚙ -> List settings -> Title** (dưới *Columns*) -> sửa **Column name**. Đừng xoá cột này.
- **Thêm cột:** bấm **+ Add column** (cuối hàng tiêu đề) -> chọn kiểu (Single line of text, Number, Yes/No, Date and time, Multiple lines of text) -> **Next** -> gõ **Name** -> **Save**.
- **Bắt buộc / duy nhất:** khi tạo cột, bấm **More options** (Thêm tùy chọn): bật **Require that this column contains information** (bắt buộc), và **Enforce unique values** (không cho trùng). Cột Number: đặt **Number of decimal places** = 0 (đếm nguyên) hoặc 1 (điểm).
- **Đặt Indexed (đánh chỉ mục, làm tìm nhanh):** **⚙ -> List settings -> Indexed columns -> Create a new index** -> chọn cột -> **Create**. Bắt buộc phải index một cột **trước** khi bật Unique. Trong vài bản giao diện, ô "Enforce unique values" tự index cột giúp bạn; nếu báo lỗi về index, làm bước index trước.

### 2.1. List `CLB`

| Cột | Kiểu | Bắt buộc | Chi tiết |
|---|---|---|---|
| `club_id` (đổi tên từ Title) | Single line of text | Có | Mã CLB, không dấu, không cách, ví dụ `clb_bongro`. Bật **Enforce unique values** (nhớ index trước) |
| `name` | Single line of text | Có | Tên hiện cho học sinh |
| `capacity` | Number, 0 chữ số thập phân | Có | Chỉ tiêu (số chỗ) |
| `reserve_capacity` | Number, 0 chữ số thập phân | Không | Suất ưu tiên, nằm **trong** capacity. Mặc định 0 |
| `reserve_group` | Single line of text | Không | Ví dụ `chinh_sach` |
| `mo_ta` | Multiple lines of text | Không | Giới thiệu CLB (chỉ app dùng) |
| `co_thi` | Yes/No | Không | CLB có thi tuyển |

- [ ] Tạo List, đổi tên Title, thêm đủ 6 cột theo thứ tự đúng như bảng (5 cột đầu **phải** theo thứ tự này).
- Bạn sẽ thấy: một bảng trống, tiêu đề cột đúng thứ tự `club_id, name, capacity, reserve_capacity, reserve_group, mo_ta, co_thi`. Nếu cột không đúng thứ tự: **⚙ -> List settings -> Column ordering** (hoặc kéo thả tiêu đề cột).

### 2.2. List `HocSinh`

| Cột | Kiểu | Chi tiết |
|---|---|---|
| `student_id` (đổi từ Title) | Single line of text | Mã HS. **Enforce unique values** |
| `name` | Single line of text | Họ tên |
| `class_id` | Single line of text | Lớp, ví dụ `10A2` |
| `email` | Single line of text | Email trường, **chữ thường**. **Indexed + Enforce unique values** |
| `reserve_group` | Single line of text | Để trống nếu không thuộc nhóm ưu tiên |

- [ ] Tạo List `HocSinh` với 5 cột này.

### 2.3. List `NguyenVong` (app sẽ ghi vào đây)

| Cột | Kiểu | Chi tiết |
|---|---|---|
| `student_id` (đổi từ Title) | Single line of text | **Indexed + Enforce unique values** (chặn nộp trùng dòng) |
| `name` | Single line of text | |
| `pref_1` ... `pref_10` | Single line of text | 10 cột: mã CLB, `pref_1` là thích nhất |
| `email` | Single line of text | Ai nộp |
| `nop_luc` | Date and time | Lần nộp cuối (chọn Date and time, có giờ) |
| `so_lan_nop` | Number, 0 chữ số thập phân | Số lần sửa |

- [ ] Tạo List và đủ 14 cột sau Title (đã tính `pref_1`..`pref_10`). Trường chỉ cho chọn tối đa 5 CLB thì **vẫn** tạo đủ 10 cột.
- Mẹo: tạo `pref_1` xong, dùng **⚙ -> List settings -> pref_1** để xem tên bên trong (xem trên thanh địa chỉ, phần `Field=`), rồi tạo các cột còn lại tương tự, không gõ nhầm chữ.
- Trường **nhiều buổi** (ví dụ mỗi tuần hai buổi khác nhau): đọc Phụ lục C của Tài liệu kỹ thuật trước khi tạo cột, vì tên cột sẽ khác (`thu_2_pref_1`...).

### 2.4. List `ChonThi` (làm khi có CLB thi tuyển; bỏ qua nếu không)

| Cột | Kiểu |
|---|---|
| `student_id` (đổi từ Title) | Single line of text, unique + indexed |
| `name` | Single line of text |
| `test_club_1`, `test_club_2`, ... `test_club_5` | Single line of text |
| `score_1`, `score_2`, ... `score_5` | Number, 1 chữ số thập phân |

- [ ] Tạo List với 11 cột (Title đổi tên + 10 cột).
- Học sinh chỉ chọn CLB muốn thi; **điểm do giáo viên nhập**.

### 2.5. Nạp danh sách học sinh và CLB từ Excel

**Mẫu Excel cho `HocSinh`** (dòng 1 là tiêu đề, gõ **đúng** như dưới; các dòng dưới là dữ liệu giả để minh hoạ):

| student_id | name | class_id | email | reserve_group |
|---|---|---|---|---|
| HS001 | Nguyễn Văn An | 10A1 | hs001@truong.edu.vn | |
| HS002 | Trần Thị Bình | 10A1 | hs002@truong.edu.vn | chinh_sach |

**Mẫu Excel cho `CLB`:**

| club_id | name | capacity | reserve_capacity | reserve_group | mo_ta | co_thi |
|---|---|---|---|---|---|---|
| clb_bongro | CLB Bóng rổ | 20 | 0 | | Tập mỗi thứ 2 | |
| clb_tienganh | CLB Tiếng Anh | 25 | 5 | chinh_sach | Giao tiếp | |

Chuẩn bị tệp Excel:
- [ ] Mở Excel, gõ bảng như trên. Email viết chữ thường. Mã HS, mã CLB không có khoảng trắng thừa.
- [ ] Bôi toàn bộ bảng (gồm dòng tiêu đề) -> **Insert -> Table** (Chèn -> Bảng), tick **My table has headers** -> OK. (SharePoint chỉ nhận bảng đã định dạng "Table".) Lưu tệp.

**Cách 1 (nhanh nhất): dán vào lưới**
- [ ] Mở List đã tạo ở 2.1/2.2 -> **Edit in grid view** (Sửa dạng lưới; nút ở thanh trên) -> trong Excel chọn các ô dữ liệu (không gồm tiêu đề), **Ctrl+C**, bấm vào ô đầu tiên của cột đầu trong lưới, **Ctrl+V**.
- Bạn sẽ thấy: các dòng điền vào bảng. Dán 800 dòng một lúc có thể chậm hoặc báo lỗi: chia thành từng nhóm 200 dòng.
- Cột Title (đã đổi tên `student_id`) là cột đầu: dán đúng thứ tự cột như tệp Excel.

**Cách 2: tạo List mới từ Excel**
- [ ] **Site contents -> New -> List -> From Excel**, tải tệp lên (hoặc chọn từ OneDrive) -> chọn bảng -> đặt tên cột, chọn kiểu từng cột (Single line/Number...) -> **Next -> Create**. (Cách này tạo List đúng tên cột bạn đặt, nhưng không chỉnh được Unique/Indexed lúc tạo; sau đó vào mục 2.0 bật lại.)
- Nếu nút **From Excel** biến mất (có trường chưa mở): dùng Cách 1.

**Kiểm sau khi nạp**
- [ ] Đếm số dòng: dưới cùng List hoặc trong **Site contents** cột *Items* phải bằng số học sinh/CLB của bạn.
- [ ] Bạn sẽ thấy: bấm vào email bất kỳ không bị khoảng trắng/chữ hoa; không có dòng trống.

---

## 3. Phân quyền

> Mục tiêu: học sinh chỉ đọc danh sách CLB, chỉ **tạo và sửa phiếu của chính mình**, không xem phiếu của bạn. Giáo viên quản trị xem hết.

**Bước 3.1 – Chuẩn bị 2 nhóm**
- [ ] Nhóm học sinh: nhóm M365 hoặc nhóm bảo mật chứa tài khoản học sinh (nhờ IT tạo nếu bạn không có quyền; mẫu 0.7). Ghi tên, ví dụ `HS-CLB-2026`.
- [ ] Nhóm giáo viên quản trị: ghi email từng người.

**Bước 3.2 – Cấp quyền cho giáo viên**
- [ ] Ở site `CLB-2026`: **⚙ -> Site permissions** (Quyền của site) -> **Site members / Add members** -> thêm giáo viên quản trị với quyền **Owner** hoặc **Edit**. Nếu giao diện là "Share site", bấm **Share site** -> nhập email -> chọn **Edit** -> **Share**.
- Bạn sẽ thấy: tên giáo viên trong danh sách *Owners* hoặc *Members*.

**Bước 3.3 – Cấp quyền cho học sinh trên toàn site (mức đọc)**
- [ ] **⚙ -> Site permissions -> Share site** -> nhập tên nhóm `HS-CLB-2026` -> chọn quyền **Read** (Xem) cho cả site -> bỏ tick **Send email** nếu không muốn gửi thư -> **Share**.
- Bạn sẽ thấy: nhóm xuất hiện trong *Visitors* (Khách xem) hoặc *Site visitors*.

**Bước 3.4 – Cho học sinh ghi vào `NguyenVong` và `ChonThi` nhưng chỉ thấy phiếu của mình**
- [ ] Mở List `NguyenVong` -> **⚙ -> List settings -> Advanced settings** (Cài đặt nâng cao).
- [ ] Mục **Item-level Permissions** (Quyền theo từng mục):
  - **Read access:** chọn **Read items that were created by the user** (Chỉ đọc mục do chính người dùng tạo).
  - **Create and Edit access:** chọn **Create items and edit items that were created by the user** (Tạo và sửa mục do chính người dùng tạo).
- [ ] Bấm **OK**.
- [ ] Làm **y hệt** cho List `ChonThi`.
- Nếu **không thấy** mục Item-level Permissions: trong một số loại List bản mới mục này bị ẩn; hỏi IT (có trường khoá mục này), hoặc tìm trong **⚙ -> List settings** mục có chữ *permissions*.
- Học sinh cũng cần quyền **Contribute** (Tham gia) trên hai List này để tạo được mục: **⚙ -> List settings -> Permissions for this list -> Stop Inheriting Permissions** -> chọn **Grant Permissions** -> nhập nhóm `HS-CLB-2026` -> chọn **Contribute** -> **Share**. (Bước này tách quyền List khỏi site; làm cho `NguyenVong` và `ChonThi` thôi.)
- Hai List `CLB` và `HocSinh`: để nguyên quyền **Read** thừa hưởng từ site.

**Bước 3.5 – Kiểm tra lại bằng tài khoản học sinh thử** (đợi đến mục 7).

> Cảnh báo: chia sẻ app Power Apps **không** tự cấp quyền SharePoint. Hai việc riêng; thiếu bước này, học sinh mở app sẽ thấy lỗi quyền.

---

## 4. Power Apps: tạo ứng dụng

### 4.1. Đăng nhập
- [ ] Mở `https://make.powerapps.com` bằng trình duyệt Edge hoặc Chrome, đăng nhập tài khoản trường.
- Bạn sẽ thấy: trang chủ Power Apps, menu bên trái, thanh tìm kiếm phía trên.

### 4.2. Chọn đúng Environment (rất quan trọng)
- [ ] Nhìn **góc trên bên phải**, cạnh biểu tượng chuông và bánh răng có chữ tên Environment. Ví dụ trong màn hình mẫu: **XCL Education Group**.
- [ ] Bấm vào tên đó để mở danh sách. Sẽ thấy các Environment bạn có quyền (thường có 1 cái tên trường hoặc tên bạn kèm chữ *(default)*).
- **Chọn cái nào?**
  - Cái mà IT báo cho bạn dùng; nếu IT chưa nói gì, chọn Environment **(default)** hoặc tên có chữ **Education**/tên trường.
  - Tránh Environment kiểu **Developer**/**Sandbox** của người khác, và nơi bạn không thấy được các app của giáo viên khác nếu cả nhóm cần chung tay.
- Nếu **trong danh sách chỉ có một cái** hoặc **không bấm được:** bình thường, dùng cái đó.
- Nếu **danh sách trống** hoặc báo "no environments": thiếu giấy phép/quyền, gửi IT (0.7, mục 3).
- Ghi lại tên Environment đã chọn vào sổ tay. **Mọi thứ về sau** (tạo app, kết nối, xem app) phải ở cùng Environment này. Nếu mở app mà không thấy app của mình: gần như luôn do đang ở sai Environment.

### 4.3. Tạo app trống kiểu Tablet
- [ ] Menu trái **Create** (Tạo) -> chọn **Start with a page design / Blank canvas**. Thử các tên có thể gặp: **Blank app**, **Start from blank**, **Create from blank**. Chọn **Blank app -> Blank canvas app** (Ứng dụng canvas trống).
- [ ] Hộp thoại hỏi:
  - **App name:** `DangKyCLB`
  - **Format:** chọn **Tablet** (không chọn Phone).
- [ ] Bấm **Create**.
- Nếu hiện hộp "Welcome to Power Apps Studio": bấm **Skip** (Bỏ qua).
- Bạn sẽ thấy: màn hình soạn thảo (gọi là **Studio**) có khung app trống ở giữa, danh sách màn hình **Screen1** bên trái, thanh công thức phía trên.

### 4.4. Cài đặt hiển thị để dùng được cả điện thoại lẫn laptop
- [ ] Bấm **Settings** (Cài đặt; biểu tượng bánh răng ở trên cùng, hoặc **File -> Settings**) -> mục **Display**.
- [ ] Tắt **Scale to fit** (Co giãn vừa khít), tắt **Lock aspect ratio** (Khoá tỷ lệ), tắt **Lock orientation** (Khoá hướng).
- [ ] Bấm **Apply** (nếu có) / đóng hộp. Nếu thấy chữ như "Orientation" nằm ở **Display**, cũng đặt thành **Landscape** hoặc bỏ khoá.
- Bạn sẽ thấy: cả 3 công tắc ở trạng thái **Off**. Từ giờ app theo kích thước cửa sổ; trên phone sẽ co lại.
- Cài đặt nhìn khác (một số bản đưa phần này vào **Settings -> Display** hoặc ngay ở thanh **Properties** của App): tìm đúng chữ **Scale to fit** là được.

### 4.5. Nối dữ liệu SharePoint
- [ ] Menu bên trái trong Studio: biểu tượng **Data** (hình trụ). Nếu không thấy: **Insert** hoặc chữ **Add data** (có thể nằm ở thanh trên).
- [ ] **Add data** -> gõ `SharePoint` -> chọn **SharePoint** (connector, cái có biểu tượng chữ S).
- [ ] Nếu chưa có kết nối: bấm **Add a connection / Connect** -> đăng nhập tài khoản trường -> **Allow**.
- [ ] Danh sách **Recent sites** hiện: chọn `CLB-2026`. Nếu không thấy: dán địa chỉ site (đã ghi ở 1.2) vào ô **Enter or select a site** -> **Connect directly**.
- [ ] Tick 3 List: `CLB`, `HocSinh`, `NguyenVong` (thêm `ChonThi` nếu dùng) -> **Connect**.
- Bạn sẽ thấy: bốn tên List xuất hiện trong khung **Data** của app.
- Nếu List mới tạo không hiện: bấm biểu tượng làm mới (mũi tên tròn), hoặc đợi 1 phút; kiểm tra đang ở đúng site.

### 4.6. Dán công thức: bảng "dán gì, ở đâu"

Mọi công thức nằm trong Tài liệu kỹ thuật ([`HUONG_DAN_POWER_APPS_DANG_KY.md`](HUONG_DAN_POWER_APPS_DANG_KY.md)). Mở nó song song với Studio. Cách dán: chọn đối tượng ở **cây bên trái** (Tree view), chọn **thuộc tính** ở danh sách thả xuống ở góc trên trái của thanh công thức (ví dụ **OnStart**), dán công thức vào ô bên cạnh.

Nếu thấy dấu gạch chân đỏ hoặc cảnh báo ban đầu: cứ làm hết phần của mình rồi mới kiểm; chỉ lỗi đỏ **sau khi dán đủ** mới đáng lo.

| Thứ tự | Đối tượng trong Studio | Thuộc tính | Dán gì (mục trong Tài liệu kỹ thuật) | Sửa cái gì trước |
|---|---|---|---|---|
| 1 | **App** | **Formulas** (nếu không thấy, xem ghi chú dưới bảng) | Mục **3.1** (khối `HanChot`, `SoNguyenVongToiDa`, `DSQuanTri`...) | Hạn chót, số CLB tối đa, email giáo viên |
| 2 | **App** | **OnStart** | Mục **3.2** | Không cần sửa |
| 3 | **App** | **StartScreen** | Mục **3.3** | Chỉ dán **sau khi** có đủ màn hình ở bước 4 và 5 (nếu dán sớm sẽ lỗi đỏ vì chưa có màn hình `scrQuanTri`...) |
| 4 | Mỗi màn hình | Vertical container | Mục **4** (bố cục co giãn) | Làm một lần, copy cho màn hình khác |
| 5 | Screen `scrKhongCoTen` (đổi tên Screen1 và Add screen) | Label | Mục **5.1** | |
| 6 | Screen `scrDangKy` | Label chào, hạn, hướng dẫn, lưới ô chọn, báo lỗi, nút Nộp | Mục **5.2** a đến f (làm **ô 1 chạy đúng rồi mới copy** ra ô 2..10) | `SoNguyenVongToiDa` đã đặt ở bước 1 |
| 7 | Screen `scrXacNhan` | Label tóm tắt, nút Sửa lại | Mục **5.3** | |
| 8 | Screen `scrChonThi` (tuỳ chọn) | Dropdown + nút lưu | Mục **5.4** (chỉ khi có `ChonThi`) | |
| 9 | Screen `scrQuanTri` | Thẻ số liệu, gallery chưa nộp, thống kê | Mục **6** a đến e | Địa chỉ ở **6e** (`Launch("https://<tenant>...")`): thay bằng địa chỉ site thật |
| 10 | Làm lại bước 3 | **App.StartScreen** | Mục **3.3** | |

Chú thích:
- **Cách thêm màn hình:** thanh trên **+ New screen** (Màn hình mới) -> **Blank**; đổi tên: chuột phải tên màn hình ở cây -> **Rename**.
- **Nếu không thấy thuộc tính `Formulas`** ở App: bản Power Apps cũ chưa hỗ trợ. Cách thay thế: bật **Settings -> Updates -> New** / mục **Upcoming/Experimental**; hoặc đặt các giá trị đó bằng lệnh `Set(HanChot, DateTimeValue("..."))` ... trong **App.OnStart** (gỡ phần thuộc **3.1**, sao chép dòng thành lệnh `Set`). Nếu cần giúp, giữ nguyên lỗi và hỏi người phụ trách đề tài.
- **Nếu `club_id` / `student_id` bị báo "Name isn't valid":** thay bằng `Title` (Tài liệu kỹ thuật, ghi chú cuối mục 2).
- **Cột `Blank()` báo không hợp lệ:** bật **Settings -> Updates -> Formula-level error management** (Phụ lục A).
- **Dropdown cổ điển vs Modern:** nếu bạn chèn control bằng **Insert -> Input -> Dropdown** và thấy thuộc tính tên **Items / Value / Default**: là control cổ điển (làm theo công thức chính). Nếu thấy **ItemDisplayText / DefaultSelectedItems**: là control Modern (làm theo công thức Modern, đã ghi trong ngoặc ở mục 5.2d).

**Kiểm nhanh sau khi dán xong**
- [ ] Bấm **F5** hoặc nút **Play** (hình tam giác, góc trên bên phải) để chạy thử trong Studio.
- Bạn sẽ thấy: nếu email của bạn là quản trị (có trong `DSQuanTri`): màn hình `scrQuanTri`. Email bất kỳ khác chưa có trong `HocSinh`: câu "Email ... chưa có trong danh sách học sinh". Bấm **Esc** để thoát chạy thử.
- [ ] Bấm **File -> Save** (Ctrl+S) mỗi 10 phút. Nếu tắt trình duyệt đột ngột: app tự lưu bản nháp, mở lại từ **Apps** (menu trái) -> **...** -> **Edit**.

---

## 5. Phát hành, chia sẻ, mã QR

**Bước 5.1 – Publish (phát hành)**
- [ ] **File -> Save**; nếu có nhập **Version notes** (ghi chú phiên bản): gõ "Ban dau". Bấm **Publish** -> **Publish this version**.
- Bạn sẽ thấy: thông báo "Your app was published". **Mỗi lần sửa phải Publish lại**, nếu không học sinh vẫn thấy bản cũ.

**Bước 5.2 – Chia sẻ**
- [ ] **File -> Share** (hoặc từ trang **Apps**: chọn app -> **... -> Share**).
- [ ] Ô tìm: gõ tên nhóm `HS-CLB-2026` -> chọn -> tick **Use** / quyền **User** (Người dùng). **Đừng** cho học sinh quyền **Co-owner** (Đồng sở hữu).
- [ ] Thêm giáo viên quản trị -> quyền **Co-owner** (cho phép sửa app).
- [ ] Bỏ tick **Send an email invitation** nếu bạn không muốn gửi thư tự động. Bấm **Save** / **Share**.
- Nếu chia sẻ báo "cần cấp quyền dữ liệu / This app uses SharePoint, share the list": vẫn xong bước 3; có thể bấm **Share** tiếp.
- Nếu không tìm thấy nhóm: nhóm chưa được đồng bộ (có thể mất vài giờ), hoặc nhóm là danh sách phân phối, không phải nhóm M365/bảo mật: nhờ IT.

**Bước 5.3 – Lấy liên kết**
- [ ] Menu trái **Apps** -> bấm tên app `DangKyCLB` -> khung bên phải/ **Details** -> **Web link** -> **Copy**. Hoặc ở **Apps**, chọn app rồi nút **... (More)** -> **Details**.
- Bạn sẽ thấy: một địa chỉ dài kiểu `https://apps.powerapps.com/play/e/...`. Ghi lại.

**Bước 5.4 – Tạo mã QR**
- [ ] Dùng bất kỳ trang tạo mã QR miễn phí của bạn tin, nhưng **chỉ dán địa chỉ app**: không nhập thông tin học sinh. (Nếu trường không cho dùng trang bên ngoài: hỏi IT công cụ tạo QR được phép; nếu không có, chỉ gửi đường link.)
- [ ] In QR dán ở lớp, kèm chữ: "Quét mã, đăng nhập bằng email trường".
- Cách mở trên điện thoại: quét QR -> mở trong trình duyệt -> đăng nhập email trường. Hoặc cài ứng dụng **Power Apps** từ App Store/Google Play, đăng nhập, mở app `DangKyCLB`.

---

## 6. Cài rbda-kiosk trên máy Windows

Phần này tóm tắt; đọc kỹ ở [`HUONG_DAN_CAI_DAT.md`](../../HUONG_DAN_CAI_DAT.md).

- [ ] Máy Windows 10 hoặc 11, kết nối mạng.
- [ ] Lấy bản mới: mở kho mã trên GitHub -> **Releases** -> bản `ban-moi-nhat` -> tải `PhanBoCauLacBo-windows.zip` ở mục **Assets** (không cần đăng nhập).
- [ ] **Trước khi giải nén:** chuột phải tệp `.zip` -> **Properties** -> nếu có ô **Unblock** thì tick -> **OK**.
- [ ] Giải nén **cả thư mục** (không lấy riêng `.exe`) vào ví dụ `C:\PhanBoCauLacBo\`. Bên cạnh `.exe` phải có thư mục `_internal` và tệp `PhanBoCauLacBo.exe.config`.
- [ ] Chạy `PhanBoCauLacBo.exe`. Nếu hiện **Windows protected your PC**: **More info -> Run anyway** (đây là cảnh báo bình thường, không phải virus; xem giải thích trong tài liệu cài đặt). Windows nhớ lựa chọn này.
- Bạn sẽ thấy: một cửa sổ riêng của ứng dụng. Nếu chữ vàng **“Chế độ dự phòng (trình duyệt)”** ở góc dưới trái: vẫn dùng được, xem mục "Nếu app mở ra trong cửa sổ Edge" trong tài liệu cài đặt.
- [ ] Dữ liệu nằm trong tệp `app.db` cạnh phần mềm: sao chép cả thư mục này khi cần sao lưu.

**Cách nạp dữ liệu vào kiosk (sau khi học sinh đã nộp):** xem mục 8 của Tài liệu kỹ thuật (xuất CSV từ SharePoint). Kiosk nhận ra loại tệp theo tiêu đề cột: có `capacity` là danh sách CLB, có `pref_` là nguyện vọng, có `test_club_` là chọn thi. Mẫu chuẩn để đối chiếu: `mau_csv/05_danh_sach_club.csv` (CLB), `mau_csv/03_nguyen_vong_dang_rong.csv` (nguyện vọng), `mau_csv/01_chon_club_thi_dang_rong.csv` (chọn thi). Cũng có thể gộp tất cả vào một sổ Excel: xem `mau_csv/HUONG_DAN_SO_NHAP.md`. Nạp CLB **trước**, nguyện vọng sau.

---

## 7. Thử từ đầu đến cuối với 3 học sinh giả

Chuẩn bị: 3 tài khoản thử (nhờ IT tạo hoặc mượn 3 em tình nguyện; nếu mượn thì chỉ dùng email, không xem nội dung riêng tư). Đặt tên giả: HS901, HS902, HS903. Dữ liệu dưới đây hoàn toàn giả.

| # | Làm gì | Kết quả mong đợi |
|---|---|---|
| 1 | Thêm 3 dòng vào `HocSinh` (email của 3 tài khoản thử, `reserve_group` để trống) và 3 dòng vào `CLB` (ví dụ chỉ tiêu 2, 2, 2) | Mỗi list hiện đủ số dòng |
| 2 | Tài khoản thử 1 mở link app trên **điện thoại** | Thấy "Chào ... (HS901 - lớp ...)", mỗi ô chọn 1 cột, không tràn ngang |
| 3 | Mở trên **laptop** (cửa sổ rộng) | Ô chọn 2 cột, khung nằm giữa |
| 4 | Chọn CLB cho ô 1 và ô 3, bỏ ô 2, bấm **Nộp nguyện vọng** | Báo đã lưu; trong List `NguyenVong`: một dòng, `pref_1` và `pref_2` có mã (dồn lên), `so_lan_nop` = 1 |
| 5 | Nộp lại lần hai với lựa chọn khác | Vẫn **một dòng**, `so_lan_nop` = 2 |
| 6 | Chọn trùng một CLB hai ô | Chữ đỏ báo trùng, nút Nộp mờ |
| 7 | Dùng tài khoản thử 2 mở link | Chỉ thấy phiếu của chính mình, không thấy dòng của HS901 (thử mở List `NguyenVong` trực tiếp: chỉ có dòng của mình) |
| 8 | Dùng tài khoản **không có** trong `HocSinh` (hoặc email khác) | Câu "Email ... chưa có trong danh sách học sinh" |
| 9 | Đổi `HanChot` về quá khứ trong **App.Formulas**, Publish, mở lại | Ô chọn bị khoá, nút Nộp mờ. **Đổi lại hạn đúng và Publish lại** |
| 10 | Tài khoản giáo viên (có trong `DSQuanTri`) mở app | Vào màn hình quản trị: "x / 3 học sinh đã nộp", danh sách chưa nộp đúng |
| 11 | Xuất CSV: mở List `NguyenVong` -> **Export -> Export to CSV** (hoặc **Export to Excel**) | Tải được tệp; mở bằng Excel thấy tiêu đề `student_id, name, pref_1 ...` |
| 12 | Nạp CSV `CLB` rồi CSV nguyện vọng vào rbda-kiosk, chạy xếp | Kiosk nạp không lỗi, ra kết quả xếp 3 học sinh, không CLB nào vượt chỉ tiêu |
| 13 | **Dọn dẹp:** xoá dữ liệu thử (3 dòng mỗi list; trong kiosk: Quản lý -> Vùng nguy hiểm -> Xoá toàn bộ học sinh) | Các List trống, sẵn sàng nạp dữ liệu thật |

Quan trọng: **phải xoá dòng thử trong `NguyenVong`** trước khi mở cho toàn trường, vì cột `student_id` là duy nhất và dữ liệu thử còn sót sẽ lẫn vào kết quả.

---

## 8. Bảng xử lý sự cố

| # | Triệu chứng | Nguyên nhân thường gặp | Cách sửa |
|---|---|---|---|
| 1 | Không thấy nút **Create site** | Thiếu quyền tạo site | Gửi IT mẫu 0.7 mục 2 |
| 2 | Power Apps báo cần giấy phép | Tài khoản chưa có giấy phép Power Apps | Gửi IT mẫu 0.7 mục 1 |
| 3 | Vào make.powerapps.com thấy trống, không có app của mình | Đang ở **sai Environment** | Góc trên phải bấm tên Environment, chọn lại đúng cái đã ghi (mục 4.2) |
| 4 | Không thấy List `CLB-2026` khi **Add data** | Sai Environment/tài khoản, hoặc chưa đợi đồng bộ | Kiểm tra đăng nhập đúng tài khoản; dán thẳng địa chỉ site; làm mới |
| 5 | Bấm **Enforce unique values** báo lỗi | Cột chưa được **Indexed** hoặc đã có dữ liệu trùng | Tạo index trước (mục 2.0); xoá dòng trùng rồi bật lại |
| 6 | `club_id`/`student_id` báo "Name isn't valid" trong công thức | Tên nội bộ của cột vẫn là `Title` (đổi tên không đổi tên nội bộ) | Thay bằng `Title`, hoặc tạo cột mới đúng tên và dán dữ liệu (Tài liệu kỹ thuật, mục 2 và Phụ lục A) |
| 7 | Dropdown trống | `colCLB` chưa nạp | Cây trái -> **App** -> **...** -> **Run OnStart** |
| 8 | Tam giác vàng "delegation" | Cảnh báo bình thường, danh sách nhỏ hơn 2.000 dòng | **Settings -> General -> Data row limit** đặt 2000 |
| 9 | Học sinh bấm Nộp báo "Lưu thất bại" hoặc lỗi quyền | Chưa cấp **Contribute** trên `NguyenVong`, hoặc chưa tắt kế thừa quyền | Làm lại mục 3.4 |
| 10 | Học sinh mở app báo "bạn cần quyền" / không thấy app | Chưa chia sẻ app, hoặc chia sẻ sai nhóm | Mục 5.2: chia sẻ nhóm với quyền **User** |
| 11 | Học sinh thấy phiếu của bạn | Chưa bật Item-level permissions | Mục 3.4; kiểm bằng tài khoản thử 2 |
| 12 | App méo trên điện thoại | Chưa tắt **Scale to fit** / **Lock aspect ratio** | Mục 4.4, rồi Publish lại |
| 13 | Sửa app xong học sinh vẫn thấy cũ | Chưa **Publish** | **File -> Save -> Publish** |
| 14 | Nộp xong thấy 2 dòng cho một học sinh | `student_id` chưa bật Unique, hoặc `Patch` bị dán sai | Bật unique (mục 2.3), kiểm công thức mục 5.2f; xoá dòng thừa |
| 15 | CSV mất dấu tiếng Việt | Excel mở sai mã hoá | Excel **Data -> From Text/CSV** -> chọn **UTF-8** -> lưu lại **CSV UTF-8** |
| 16 | CSV có thêm cột lạ (`Item Type`, `Path`) hoặc đầu cột có dấu cách | Cách SharePoint xuất | Xoá các cột thừa trong Excel; đổi tiêu đề đúng tên cột; lưu CSV UTF-8 |
| 17 | Kiosk báo mã CLB không tồn tại | Mã trong nguyện vọng khác mã trong danh sách CLB (do đổi mã CLB sau khi mở đăng ký) | **Không đổi `club_id` sau khi mở đăng ký**; sửa mã trong CSV cho khớp |
| 18 | Windows chặn `.exe` | Chưa ký số, cảnh báo bình thường | **More info -> Run anyway** (mục 6) |
| 19 | Kiosk mở trong Edge hoặc chữ "Chế độ dự phòng" | Tệp bị dấu "tải từ Internet" | Mục 6: Unblock `.zip` trước khi giải nén, giải nén lại |
| 20 | Hết hạn nhưng học sinh vẫn sửa được | App chỉ khoá giao diện, quyền List vẫn cho sửa | Đổi quyền List sang **Read** khi hết hạn (Tài liệu kỹ thuật, mục 7) |

---

## 9. Danh sách kiểm cuối (một trang)

**Quyền**
- [ ] Đăng nhập được office.com và make.powerapps.com bằng email trường
- [ ] Có giấy phép Power Apps; có quyền tạo site; có nhóm học sinh

**SharePoint**
- [ ] Site `CLB-2026` đã tạo, riêng tư, địa chỉ đã ghi lại
- [ ] 3 hoặc 4 List đã tạo: `CLB`, `HocSinh`, `NguyenVong`, (`ChonThi`)
- [ ] Tên cột đúng chữ thường, có gạch dưới; Title đã đổi tên ở mọi List
- [ ] `student_id` (HocSinh, NguyenVong), `club_id` (CLB), `email` (HocSinh) đã Unique + Indexed
- [ ] Danh sách học sinh và CLB đã nạp, đếm số dòng khớp
- [ ] Item-level permissions bật ở `NguyenVong` và `ChonThi`; học sinh có Contribute

**Power Apps**
- [ ] Đã chọn đúng Environment, ghi lại tên
- [ ] App `DangKyCLB`, Tablet, đã tắt Scale to fit, Lock aspect ratio, Lock orientation
- [ ] Đã nối SharePoint và đủ List
- [ ] Đã sửa hạn chót, số nguyện vọng tối đa, email quản trị, địa chỉ ở nút xuất (mục 6e)
- [ ] Đã **Publish**, đã **Share** nhóm học sinh (User) và giáo viên (Co-owner)
- [ ] Có link app và mã QR

**Kiosk**
- [ ] rbda-kiosk giải nén cả thư mục, chạy được (đã bấm qua cảnh báo)

**Thử và mở cửa**
- [ ] Đã chạy bảng thử mục 7, đạt cả 13 dòng
- [ ] Đã xoá dữ liệu thử (List và kiosk)
- [ ] Đã đặt đúng hạn chót; gửi link và QR cho học sinh
- [ ] Lịch: sau hạn chót đổi quyền List sang Read, xuất CSV, nạp kiosk theo thứ tự CLB trước rồi nguyện vọng

**Nếu kẹt:** chụp nguyên màn hình thông báo lỗi (không gõ lại theo trí nhớ) và gửi cho người phụ trách đề tài kèm bước đang làm.
