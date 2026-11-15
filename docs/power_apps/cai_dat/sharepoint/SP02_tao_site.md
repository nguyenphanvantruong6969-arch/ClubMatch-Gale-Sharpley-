# SP02 — Tạo trang chứa dữ liệu

[← SP01](SP01_kiem_quyen.md) · Tiếp theo: [SP03](SP03_thao_tac_list_co_ban.md)

**Cần có:** SP01 đạt A và B.

- SP01 **đạt C**: làm "Cách 1".
- SP01 **chưa đạt C** (trường chặn tạo trang): nhảy xuống "Khi bị chặn".

## Cách 1 — Tự tạo (khi SP01 đạt C)

1. Mở trang SharePoint (làm lại SP01 bước 14 đến 16).
2. Bấm «+ Create site» ở phía trên bên trái trang.
3. Bấm ô «Team site».
4. Chỉ khi hiện trang cho chọn mẫu: bấm mẫu «Standard team», rồi bấm nút «Use template» ở góc dưới bên phải.
5. Bấm vào ô «Site name», dán:
```
CLB-2026
```

👀 Bên dưới ô tên hiện dòng chữ màu xanh lá báo tên dùng được, và ô «Site address» tự điền `CLB-2026`.

⚠️ Hiện chữ đỏ báo tên đã có người dùng: xoá chữ trong ô «Site name», dán `CLB-2026-A` thay vào. Từ đây về sau, chỗ nào hướng dẫn ghi `CLB-2026` thì bạn hiểu là `CLB-2026-A`.

6. Nhìn dưới ô tên:
   - Thấy mục «Privacy settings» ngay trên trang này: làm tiếp bước 7.
   - Chỉ thấy nút «Next»: bấm «Next», mục «Privacy settings» sẽ hiện ở trang sau.
7. Bấm ô thả xuống «Privacy settings», chọn «Private - only members can access this site» (chỉ thành viên mới vào được).
8. Mục «Select a language»: không đụng tới.
9. Bấm nút ở góc dưới bên phải: «Create site» (bản khác ghi «Next»).
10. Trang hỏi thêm thành viên («Add site owners and members»): không điền gì, bấm «Finish». (Thành viên sẽ thêm ở SP09.)

👀 Trang mới mở ra, có chữ `CLB-2026` ở phía trên bên trái. Cột trái có «Home», «Documents», «Site contents».

11. Bấm một lần vào thanh địa chỉ của trình duyệt. Địa chỉ có dạng `https://truong.sharepoint.com/sites/CLB-2026/...`
12. Kéo chuột bôi đen **từ chữ `https` đến hết chữ `CLB-2026`** (không lấy phần phía sau), bấm `Ctrl` + `C`. Ví dụ phần đã bôi đen: `https://truong.sharepoint.com/sites/CLB-2026`
13. Dán vào sổ tay, đặt tên là **ĐỊA CHỈ TRANG**. Các tệp sau đều cần.

- [ ] **Đã có ĐỊA CHỈ TRANG** → nhảy xuống mục "Kiểm tra".

## Khi bị chặn («Site is unavailable due to admin setting»)

Thử lần lượt cách a, b, c. Cách nào được thì dừng ở đó và nhảy xuống mục "Kiểm tra". Cách d chỉ để tập.

### Cách a — Nhờ bộ phận tin học tạo giúp (chắc chắn được, nhưng phải chờ)

1. Gửi tin nhắn mẫu ở cuối [SP01](SP01_kiem_quyen.md), giữ dòng việc số 2.
2. Khi bộ phận tin học báo đã tạo xong: xin họ gửi địa chỉ trang. Dán địa chỉ đó vào sổ tay làm **ĐỊA CHỈ TRANG**.
3. Trong lúc chờ, bạn có thể dùng cách d để tập trước các tệp SP03 đến SP07.

### Cách b — Nhờ một giáo viên đã có sẵn trang SharePoint

Giáo viên đó làm 6 bước sau trên máy của họ:

1. Mở trang SharePoint của họ.
2. Bấm hình bánh răng ⚙ ở góc trên bên phải.
3. Bấm «Site permissions».
4. Bấm «Add members», rồi bấm «Share site only». (Không có «Add members» mà có nút «Share site»: bấm «Share site».)
5. Dán thư điện tử của bạn vào ô nhập tên, bấm vào tên bạn hiện ra bên dưới.
6. Bấm ô thả xuống cạnh tên bạn, chọn «Full control», rồi bấm «Add».

Sau đó bạn làm:

7. Xin giáo viên đó gửi địa chỉ trang (dạng `https://truong.sharepoint.com/sites/ten-trang`). Dán vào sổ tay làm **ĐỊA CHỈ TRANG**.

⚠️ Mọi người đang là thành viên của trang đó cũng sẽ vào được trang. Việc ai xem được bảng nào sẽ chỉnh ở SP09.

### Cách c — Tạo qua Microsoft Teams (nhiều trường chặn cả cách này)

1. Mở Microsoft Teams, đăng nhập bằng tài khoản trường.
2. Ở dải biểu tượng dọc bên trái, bấm «Teams».
3. Bấm dấu «+» ở đầu danh sách nhóm (bản khác: nút «Join or create a team» ở cuối danh sách).
4. Bấm «Create team».
5. Chỉ khi hiện bảng cho chọn kiểu nhóm: bấm «From scratch», rồi bấm «Private».
6. Bấm vào ô «Team name», dán:
```
CLB-2026
```
7. Bấm «Create». Trang hỏi thêm thành viên: bấm «Skip».
8. Trong nhóm vừa tạo, bấm kênh «General».
9. Bấm thẻ «Files» ở hàng thẻ phía trên (bản khác ghi «Shared»).
10. Bấm «⋯» trên thanh lệnh của thẻ đó, rồi bấm «Open in SharePoint».

👀 Trình duyệt mở một trang SharePoint, địa chỉ có `/sites/CLB-2026/`.

11. Làm bước 11 đến 13 của "Cách 1" để ghi **ĐỊA CHỈ TRANG**.

⚠️ Không có nút «Create team», hoặc báo không được phép: trường chặn cách này. Dùng cách a.

### Cách d — Chỉ để tập làm (không dùng cho cả trường)

Bảng tạo theo cách này thuộc riêng tài khoản bạn và khó chia quyền cho học sinh. Chỉ dùng để luyện tay trong lúc chờ cách a.

1. Ở thẻ office.com, bấm hình 9 chấm vuông ở góc trên bên trái, bấm «Lists». (Không thấy: bấm «More apps», rồi bấm «Lists».)
2. Bấm «+ New list», bấm «Blank list».
3. Bấm ô «Name», dán `Thu`. Mục «Save to» để nguyên «My lists». Bấm «Create».
4. Bấm một lần vào thanh địa chỉ. Địa chỉ có dạng `https://truong-my.sharepoint.com/personal/ten_ban/Lists/Thu/...`
5. Bôi đen **từ `https` đến ngay trước `/Lists`**, bấm `Ctrl` + `C`, dán vào sổ tay làm **ĐỊA CHỈ TRANG (tập)**.

## Kiểm tra

1. Bấm `Ctrl` + `T` mở thẻ mới.
2. Dán ĐỊA CHỈ TRANG vào thanh địa chỉ, bấm `Enter`.

👀 Trang mở ra, không báo lỗi, không hỏi xin quyền.

- [ ] Mở được trang bằng ĐỊA CHỈ TRANG.
