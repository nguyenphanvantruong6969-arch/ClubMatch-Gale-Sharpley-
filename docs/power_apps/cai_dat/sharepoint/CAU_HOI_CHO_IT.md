# Phiếu hỏi bộ phận tin học

Kính gửi thầy/cô phụ trách tin học,

Em là Trường, đang làm đề tài nghiên cứu khoa học: **xếp học sinh vào câu lạc bộ** bằng một phần mềm riêng. Học sinh sẽ đăng ký nguyện vọng qua một ứng dụng nhỏ làm bằng **Power Apps**. Dữ liệu lưu trên **SharePoint** của trường.

Phần SharePoint đã có sẵn một **tệp lệnh tự động** (chạy bằng PowerShell). Tệp lệnh tự tạo trang, các bảng dữ liệu, phân quyền và nạp danh sách học sinh. Nó **chỉ tạo mới, không xoá gì**, và có chế độ chạy thử để xem trước. Hướng dẫn chạy từng bước nằm ở tệp `SP00_tu_dong.md`.

Để chuẩn bị đúng, em cần thầy/cô trả lời các câu dưới đây. Mỗi câu có ghi:
- **Vì sao em hỏi**: câu trả lời dùng vào việc gì.
- **Cách tìm**: tìm câu trả lời ở đâu (nếu cần tra).
- **Nếu "không" hoặc "chưa biết"**: chuyện gì xảy ra, và cách xử lý.

Thầy/cô điền vào dòng **Trả lời** dưới mỗi câu. Câu nào chưa rõ cứ ghi "chưa biết", em sẽ tìm cách khác.

---

## Phần A — Địa chỉ và tài khoản quản trị

### A1. Địa chỉ SharePoint của trường là gì?

Khi mở SharePoint của trường, thanh địa chỉ trình duyệt hiện dạng `https://_____.sharepoint.com`. Em cần phần trong chỗ trống.

- **Vì sao em hỏi:** tệp lệnh cần biết trang mới sẽ được tạo trong "ngôi nhà" nào.
- **Cách tìm:** mở `https://www.office.com` → bấm hình 9 chấm vuông góc trên bên trái → «SharePoint» → nhìn thanh địa chỉ.
- **Ví dụ trả lời:** `truongabc`

**Trả lời:** ……………………………………

### A2. Tên miền gốc của trường (kết thúc bằng `.onmicrosoft.com`) là gì?

Mỗi trường dùng Microsoft 365 đều có một tên miền gốc do Microsoft cấp, khác với tên miền thư điện tử thường dùng (ví dụ `@truongabc.edu.vn`).

- **Vì sao em hỏi:** cần cho bước làm "thẻ tên" cho tệp lệnh (gọi là **đăng ký ứng dụng trong Entra**). Thẻ này cho phép tệp lệnh đăng nhập. Mỗi lần chạy, tệp lệnh vẫn phải đi kèm tài khoản của thầy/cô, **không tự chạy một mình được**.
- **Cách tìm:** trang quản trị `https://admin.microsoft.com` → «Settings» → «Domains» → dòng kết thúc bằng `.onmicrosoft.com`.
- **Ví dụ trả lời:** `truongabc.onmicrosoft.com`

**Trả lời:** ……………………………………

### A3. Tài khoản của thầy/cô có những quyền nào dưới đây?

| Quyền | Dùng để | Có / Không / Chưa biết |
|---|---|---|
| Quản trị SharePoint («SharePoint Administrator») hoặc Quản trị toàn bộ («Global Administrator») | Tạo trang mới, phân quyền | |
| Được bấm "đồng ý thay cả tổ chức" khi một ứng dụng xin quyền («Grant admin consent»). Thường cần «Global Administrator», «Application Administrator» hoặc «Cloud Application Administrator» | Làm thẻ tên cho tệp lệnh (chỉ một lần) | |
| Tạo nhóm tài khoản («Groups Administrator» hoặc «User Administrator») | Tạo nhóm học sinh nếu trường chưa có | |

- **Vì sao em hỏi:** thiếu quyền thứ nhất hoặc thứ hai thì tệp lệnh không chạy được.
- **Cách tìm:** `https://admin.microsoft.com` → «Users» → «Active users» → bấm tên mình → mục «Roles».
- **Nếu "không":** nhờ người có quyền làm riêng bước làm thẻ tên (SP00 Bước 3, chỉ một lệnh và vài lần bấm). Phần còn lại thầy/cô làm được nếu có quyền quản trị SharePoint.

### A4. Thầy/cô sẽ chạy trên máy nào?

- Máy Windows 10 hay Windows 11?
- Máy có cho cài thêm phần mềm không (cần cài **PowerShell 7** và công cụ **PnP**, đều miễn phí của Microsoft)?
- Máy có bị chặn tải công cụ từ kho «PowerShell Gallery» không?

- **Vì sao em hỏi:** tệp lệnh chỉ chạy trên PowerShell 7 có cài công cụ PnP.
- **Nếu máy bị khoá cài đặt:** dùng một máy khác của phòng tin học, hoặc cài PnP vào riêng tài khoản của mình (lệnh trong SP00 đã dùng cách này, không cần quyền quản trị máy).

**Trả lời:** ……………………………………

### A5. Ai sẽ đứng tên chủ trang SharePoint?

Trang cần một người chịu trách nhiệm chính (ghi bằng thư điện tử). Người này có toàn quyền trên trang, kể cả xoá.

- **Vì sao em hỏi:** tệp lệnh cần thư điện tử này khi tạo trang.
- **Gợi ý:** thầy/cô tin học, hoặc giáo viên hướng dẫn đề tài. Không nên là tài khoản học sinh.

**Trả lời:** ……………………………………

---

## Phần B — Tài khoản học sinh

### B1. Tất cả học sinh tham gia đã có thư điện tử của trường chưa?

- Học sinh đã có tài khoản Microsoft của trường chưa? Có đủ **tất cả** các em tham gia không?
- Thư điện tử có dạng thế nào? (ví dụ `hs001@truongabc.edu.vn` hay `nguyenvana.10a1@…`)
- Học sinh có biết mật khẩu và đã đăng nhập được chưa?

- **Vì sao em hỏi:** ứng dụng nhận ra từng em **qua thư điện tử lúc đăng nhập**, rồi đối chiếu với danh sách học sinh. Em nào không có tài khoản thì không đăng ký được.
- **Nếu một số em chưa có:** cần cấp tài khoản trước ngày mở đăng ký, hoặc giáo viên nhập nguyện vọng giúp các em đó.

**Trả lời:** ……………………………………

### B2. Có thể xuất danh sách học sinh kèm thư điện tử ra Excel không?

Em cần một bảng gồm: **mã học sinh, họ tên, lớp, thư điện tử**.

- **Vì sao em hỏi:** bảng này được nạp vào SharePoint để ứng dụng biết ai là học sinh nào.
- **Cách tìm:** `https://admin.microsoft.com` → «Users» → «Active users» → «Export users». Hoặc lấy từ phần mềm quản lý học sinh của trường.
- **Lưu ý:** đây là dữ liệu cá nhân. Gửi qua kênh nội bộ của trường, không gửi qua mạng xã hội.

**Trả lời:** ……………………………………

### B3. Trường đã có nhóm gom tài khoản các học sinh tham gia chưa?

"Nhóm" là một danh sách tài khoản có tên riêng, ví dụ "HS-Khoi10" hay "Toàn bộ học sinh".

- Nếu **có**: tên nhóm là gì? Nhóm có thư điện tử không? Nếu không có thư điện tử, cho em **mã nhóm** («Object ID», dạng `1a2b3c4d-…`).
- Nếu **chưa**: thầy/cô tạo giúp một **nhóm bảo mật** («Security group») tên `HS-CLB-2026` gồm các học sinh tham gia được không?
- Nhóm có tự cập nhật khi có học sinh mới không, hay phải thêm tay?

- **Vì sao em hỏi:** cấp quyền cho cả nhóm một lần, thay vì cấp cho 800 em từng em một.
- **Cách tìm mã nhóm:** `https://admin.microsoft.com` → «Teams & groups» → «Active teams & groups» → bấm tên nhóm → thẻ «General».

**Trả lời:** ……………………………………

### B4. Tài khoản học sinh có được dùng Power Apps không?

Thường gói Microsoft 365 Education cho học sinh (A1, A3 hoặc A5) đã có sẵn quyền dùng Power Apps với SharePoint, không tốn thêm tiền.

- **Vì sao em hỏi:** thiếu quyền này thì học sinh mở ứng dụng sẽ báo "cần giấy phép".
- **Cách tìm:** `https://admin.microsoft.com` → «Users» → bấm tên một học sinh → «Licenses and apps» → xem có mục «Power Apps for Office 365» (hoặc tên tương tự) đang bật không.
- **Nếu tắt:** bật cho nhóm học sinh tham gia.

**Trả lời:** ……………………………………

### B5. Học sinh có được mở ứng dụng trên điện thoại cá nhân không?

- Trường có chính sách chặn đăng nhập tài khoản trường từ điện thoại cá nhân không (ví dụ bắt buộc thiết bị do trường quản lý)?
- Học sinh có cài được ứng dụng «Power Apps» từ App Store / Google Play không, hay chỉ mở bằng trình duyệt?

- **Vì sao em hỏi:** đa số học sinh sẽ đăng ký bằng điện thoại.
- **Nếu bị chặn:** học sinh đăng ký bằng máy tính ở phòng tin học, theo lịch từng lớp.

**Trả lời:** ……………………………………

---

## Phần C — Giáo viên

### C1. Những giáo viên nào cần xem toàn bộ dữ liệu?

Ghi thư điện tử từng người. Các thầy cô này sẽ:
- xem được phiếu của **tất cả** học sinh;
- vào được trang theo dõi trong ứng dụng (ai đã nộp, ai chưa);
- tải dữ liệu về để đưa vào phần mềm xếp câu lạc bộ.

- **Vì sao em hỏi:** tệp lệnh cho các thầy cô này toàn quyền trên trang. Danh sách càng ngắn càng an toàn.
- **Gợi ý:** giáo viên hướng dẫn đề tài, thầy/cô tin học, một người trong ban giám hiệu.

**Trả lời:** ……………………………………

### C2. Có cần giáo viên chủ nhiệm xem danh sách lớp mình không?

- **Vì sao em hỏi:** nếu cần, phải làm thêm phần quyền riêng. Bản hiện tại chưa có.

**Trả lời:** Có / Không

---

## Phần D — Quy định và cài đặt của trường

### D1. Trường có quy định về lưu thông tin cá nhân học sinh không?

- Được phép lưu họ tên, lớp, thư điện tử, nguyện vọng của học sinh trên SharePoint của trường không?
- Có cần xin phép ban giám hiệu hoặc phụ huynh trước không?
- Lưu bao lâu thì phải xoá?

- **Vì sao em hỏi:** để làm đúng quy định ngay từ đầu.
- **Em cam kết:** chỉ lưu trong hệ thống của trường; học sinh chỉ xem được phiếu của chính mình; không đưa dữ liệu thật vào báo cáo đề tài.

**Trả lời:** ……………………………………

### D2. Trong Power Apps, nên dùng khu làm việc (Environment) nào?

Power Apps chia thành nhiều "khu làm việc", giống các ngăn tủ riêng. Ứng dụng phải nằm đúng ngăn.

- Trường có quy định khu nào cho ứng dụng của giáo viên/học sinh không, hay dùng khu mặc định?
- Khu đó có **chính sách chặn nối dữ liệu** («Data policies», còn gọi là DLP) ngăn Power Apps đọc SharePoint không?

- **Vì sao em hỏi:** chọn sai khu là lỗi hay gặp nhất. Nếu bị chặn nối SharePoint thì ứng dụng không chạy.
- **Cách tìm:** `https://admin.powerplatform.microsoft.com` → «Environments» (danh sách khu) và «Policies» → «Data policies».

**Trả lời:** ……………………………………

### D3. Trường có chặn tạo trang SharePoint mới hoặc chặn một số loại trang không?

Hiện tài khoản của em báo **"Site is unavailable due to admin setting"** khi tạo trang.

- **Vì sao em hỏi:** tệp lệnh tạo **trang nhóm không kèm nhóm Microsoft 365** («Team site without a Microsoft 365 group»). Nếu trường chặn loại trang này, em sẽ sửa tệp lệnh sang loại khác.

**Trả lời:** ……………………………………

### D4. Đặt tên trang là `CLB-2026` và để giao diện tiếng Anh có được không?

- **Vì sao em hỏi:** hướng dẫn cho người dựng ứng dụng viết theo tên nút tiếng Anh. Để giao diện tiếng Anh thì người làm dễ đối chiếu.
- **Nếu muốn tên khác:** tên viết liền, không dấu, không khoảng trắng.

**Trả lời:** ……………………………………

---

## Phần E — Lịch làm và sau này

### E1. Hôm nào thầy/cô có khoảng 1 giờ để chạy?

Thứ tự trong buổi đó:
1. Cài phần mềm (nếu máy chưa có).
2. Làm thẻ tên cho tệp lệnh (một lần).
3. **Chạy thử**: chỉ in ra việc sẽ làm, không ghi gì.
4. Tạo **trang thử** `CLB-THU` với 3 học sinh giả, kiểm tra.
5. Xoá trang thử.
6. Tạo **trang thật** với dữ liệu thật.

- **Vì sao em hỏi:** gom hết việc của thầy/cô vào một buổi, không phải làm nhiều lần.
- **Em có thể ngồi cùng không?** (để ghi lại lỗi nếu có và sửa ngay)

**Trả lời:** ……………………………………

### E2. Nếu tệp lệnh báo lỗi, thầy/cô gửi lại cho em được không?

Mỗi lần chạy, tệp lệnh tạo một tệp nhật ký `nhat_ky_sharepoint_….txt`. Tệp này ghi lại từng việc đã làm và lỗi nếu có, **không chứa mật khẩu**.

**Trả lời:** Có / Không

### E3. Hết năm học thì xử lý thế nào?

- Ai giữ quyền trang sau khi đề tài kết thúc?
- Có xoá trang (cùng dữ liệu học sinh) không? Xoá vào khi nào?
- Có xoá thẻ tên của tệp lệnh trong Entra không?
- Năm sau dùng tiếp thì tạo trang mới (`CLB-2027`) hay dùng lại trang cũ?

- **Vì sao em hỏi:** để dữ liệu học sinh được dọn dẹp đúng hạn, không bị bỏ quên.

**Trả lời:** ……………………………………

---

## Tóm tắt những gì em cần nhận lại

| # | Thông tin | Đã có |
|---|---|---|
| 1 | Địa chỉ SharePoint (A1) | [ ] |
| 2 | Tên miền gốc `.onmicrosoft.com` (A2) | [ ] |
| 3 | Xác nhận quyền quản trị (A3) | [ ] |
| 4 | Thư điện tử chủ trang (A5) | [ ] |
| 5 | Bảng học sinh kèm thư điện tử (B2) | [ ] |
| 6 | Tên/thư điện tử hoặc mã của nhóm học sinh (B3) | [ ] |
| 7 | Xác nhận học sinh dùng được Power Apps (B4) | [ ] |
| 8 | Thư điện tử giáo viên phụ trách (C1) | [ ] |
| 9 | Tên khu làm việc Power Apps (D2) | [ ] |
| 10 | Ngày giờ chạy (E1) | [ ] |

Em cảm ơn thầy/cô rất nhiều ạ.
