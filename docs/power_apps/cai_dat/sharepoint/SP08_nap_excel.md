# SP08 — Đưa danh sách học sinh và câu lạc bộ từ Excel vào

[← SP07](SP07_list_ChonThi.md) · Tiếp theo: [SP09](SP09_phan_quyen.md)

**Cần có:** đã xong SP04 và SP05; có danh sách học sinh và danh sách câu lạc bộ (SP01 phần E).

## Phần 1 — Tệp Excel học sinh

1. Mở Excel, bấm «Blank workbook» để tạo tệp trống.
2. Bấm vào ô **A1**.
3. Sao chép dòng trong ô xám dưới đây, bấm `Ctrl` + `V`:
```
student_id	name	class_id	email	reserve_group
```

👀 Excel tự chia thành 5 ô tiêu đề từ A1 đến E1. (Nếu cả dòng dồn vào một ô A1: xoá ô đó, rồi gõ tay 5 tên này vào 5 ô A1, B1, C1, D1, E1.)

4. Bấm vào ô **A2**, dán danh sách học sinh của bạn, đúng thứ tự cột: A là mã, B là họ tên, C là lớp, D là thư điện tử, E là nhóm ưu tiên (không có thì để trống). Ví dụ giả:

| student_id | name | class_id | email | reserve_group |
|---|---|---|---|---|
| HS001 | Nguyễn Văn An | 10A1 | hs001@truong.edu.vn | |
| HS002 | Trần Thị Bình | 10A1 | hs002@truong.edu.vn | chinh_sach |

**Làm sạch thư điện tử** (đưa về chữ thường, bỏ khoảng trắng thừa):

5. Bấm vào ô **F2**, dán:
```
=LOWER(TRIM(D2))
```
6. Bấm phím `Enter`.
7. Bấm lại vào ô **F2**. Đưa chuột tới ô vuông nhỏ ở góc dưới bên phải của ô F2 (con trỏ đổi thành dấu cộng đen), bấm đúp chuột.

👀 Cột F tự điền đến dòng học sinh cuối cùng.

8. Bấm vào chữ **F** ở đầu cột để chọn cả cột, bấm `Ctrl` + `C`.
9. Bấm chuột phải vào ô **D1**, bấm biểu tượng có số **123** («Values») dưới chữ «Paste Options».
10. Bấm vào ô **D1**, dán lại tên cột:
```
email
```
11. Bấm chuột phải vào chữ **F** ở đầu cột, bấm «Delete».

**Làm sạch mã học sinh** (bỏ khoảng trắng thừa):

12. Bấm vào ô **F2**, dán:
```
=TRIM(A2)
```
13. Bấm phím `Enter`, rồi làm lại bước 7 và 8.
14. Bấm chuột phải vào ô **A1**, bấm biểu tượng có số **123** («Values»).
15. Bấm vào ô **A1**, dán lại tên cột:
```
student_id
```
16. Bấm chuột phải vào chữ **F** ở đầu cột, bấm «Delete».

**Xoá dòng trùng mã:**

17. Bấm vào ô **A1**.
18. Bấm thẻ «Data» ở hàng thẻ phía trên, bấm «Remove Duplicates».
19. Trong hộp vừa mở: bấm «Unselect All», đánh dấu riêng ô `student_id`, bấm «OK».

👀 Excel báo đã xoá bao nhiêu dòng trùng và còn lại bao nhiêu dòng. Ghi lại số dòng còn lại: đó là **số học sinh**.

20. Bấm `Ctrl` + `S`, đặt tên tệp:
```
HocSinh
```

## Phần 2 — Tệp Excel câu lạc bộ

21. Trong Excel bấm `Ctrl` + `N` để tạo tệp trống mới.
22. Bấm vào ô **A1**, dán:
```
club_id	name	capacity	reserve_capacity	reserve_group	mo_ta	co_thi
```
23. Bấm vào ô **A2**, điền danh sách câu lạc bộ, đúng thứ tự cột. Cột `co_thi` chỉ ghi `Yes` (có thi tuyển) hoặc `No` (không thi). Ví dụ giả:

| club_id | name | capacity | reserve_capacity | reserve_group | mo_ta | co_thi |
|---|---|---|---|---|---|---|
| clb_bongro | CLB Bóng rổ | 20 | 0 | | Tập thứ Hai | No |
| clb_tienganh | CLB Tiếng Anh | 25 | 5 | chinh_sach | Giao tiếp | Yes |

24. Bấm `Ctrl` + `S`, đặt tên tệp:
```
CLB
```

## Phần 3 — Dán danh sách học sinh vào bảng trên SharePoint

25. Mở ĐỊA CHỈ TRANG → bấm ⚙ → «Site contents» → bấm tên bảng `HocSinh`.
26. Trên thanh lệnh phía trên bảng, bấm «Edit in grid view».

👀 Bảng chuyển thành dạng ô kẻ giống Excel, có một dòng trống ở cuối.

27. Sang Excel, tệp `HocSinh`: bấm ô **A2**, giữ phím `Shift`, bấm ô cột **E** của dòng thứ 201. (Danh sách ít hơn 200 em: bấm ô cột E của dòng cuối cùng.) Bấm `Ctrl` + `C`.
28. Sang SharePoint: bấm vào ô đầu tiên bên trái (cột `student_id`) của **dòng trống cuối cùng** trong bảng. Bấm `Ctrl` + `V`.
29. Chờ. Không bấm gì cho đến khi các dòng vừa dán hết biểu tượng xoay tròn ở đầu dòng.

👀 Các dòng vừa dán hiện đủ 5 cột, không có ô nào viền đỏ.

30. Danh sách còn nữa: sang Excel chọn 200 dòng kế tiếp (dòng 202 đến 401, cột A đến E), bấm `Ctrl` + `C`, rồi làm lại bước 28 và 29. Lặp cho đến hết.
31. Bấm «Exit grid view» trên thanh lệnh.

⚠️ Có dòng viền đỏ hoặc báo lỗi: thường do trùng mã hoặc trùng thư điện tử. Bấm vào dòng đó để đọc lời báo, sửa ô sai ngay trên bảng, bấm `Enter`.
⚠️ Dữ liệu lệch cột (ví dụ họ tên nằm ở cột lớp): thứ tự cột trong Excel khác thứ tự cột trên SharePoint. Xoá các dòng vừa dán, làm "Thêm 1" ở SP03 để xếp lại cột trên SharePoint cho giống Excel, rồi dán lại.

## Phần 4 — Dán danh sách câu lạc bộ

32. Bấm ⚙ → «Site contents» → bấm tên bảng `CLB`.
33. Bấm «Edit in grid view».
34. Sang Excel, tệp `CLB`: bấm ô **A2**, giữ `Shift`, bấm ô cột **G** của dòng cuối cùng. Bấm `Ctrl` + `C`.
35. Sang SharePoint: bấm ô đầu tiên bên trái (cột `club_id`) của dòng trống cuối cùng. Bấm `Ctrl` + `V`.
36. Chờ hết biểu tượng xoay tròn.
37. Bấm «Exit grid view».

👀 Cột `co_thi` của câu lạc bộ có thi hiện dấu tích (hoặc chữ «Yes»).

⚠️ Cột `co_thi` không nhận, để trống hết: bấm lại «Edit in grid view», bấm vào ô `co_thi` của từng câu lạc bộ có thi để đánh dấu tích, rồi «Exit grid view».

## Kiểm tra

1. Bấm ⚙ → «Site contents».

👀 Ở dòng `HocSinh`, cột «Items» bằng **số học sinh** đã ghi ở bước 19. Ở dòng `CLB`, cột «Items» bằng số câu lạc bộ.

2. Mở bảng `HocSinh`, nhìn 3 dòng bất kỳ.

👀 Thư điện tử viết chữ thường, mỗi thông tin nằm đúng cột.

- [ ] Số dòng khớp.
- [ ] Không lệch cột.
