# SP08 — Đưa danh sách học sinh và câu lạc bộ từ Excel vào

Mất khoảng 20 phút · [← SP07](SP07_list_ChonThi.md) · Tiếp theo: [SP09](SP09_phan_quyen.md)

**Cần có:** đã xong SP04 và SP05.

## Phần 1 — Tệp Excel học sinh

1. Mở Excel, tạo tệp trống.
2. Bấm vào ô **A1**. Sao chép dòng dưới đây và dán. Excel tự chia thành 5 ô tiêu đề:
```
student_id	name	class_id	email	reserve_group
```
3. Từ dòng 2, dán danh sách học sinh theo đúng thứ tự cột: Mã, Họ tên, Lớp, Thư điện tử, Nhóm ưu tiên. Ví dụ giả:

| student_id | name | class_id | email | reserve_group |
|---|---|---|---|---|
| HS001 | Nguyễn Văn An | 10A1 | hs001@truong.edu.vn | |
| HS002 | Trần Thị Bình | 10A1 | hs002@truong.edu.vn | chinh_sach |

4. **Làm sạch thư điện tử** (đưa về chữ thường, bỏ khoảng trắng thừa). Bấm vào ô **F2**, dán:
```
=LOWER(TRIM(D2))
```
5. Kéo ô vuông nhỏ ở góc dưới phải ô F2 xuống đến dòng cuối.
6. Bôi đen cả cột F → `Ctrl` + `C` → bấm ô **D2** → chuột phải → «Paste Values» (dán giá trị, biểu tượng có số 123).
7. Xoá cột F.
8. **Làm sạch mã học sinh:** bấm ô **F2**, dán công thức dưới, rồi lặp lại bước 5 đến 7 nhưng dán vào ô **A2**:
```
=TRIM(A2)
```
9. Bôi đen cột A → thẻ «Data» → «Remove Duplicates» (xoá dòng trùng).
10. Lưu tệp với tên:
```
HocSinh.xlsx
```

## Phần 2 — Tệp Excel câu lạc bộ

11. Tạo tệp trống, bấm ô **A1**, dán:
```
club_id	name	capacity	reserve_capacity	reserve_group	mo_ta	co_thi
```
12. Từ dòng 2 dán danh sách câu lạc bộ. Cột `co_thi` ghi `Yes` hoặc `No`. Ví dụ giả:

| club_id | name | capacity | reserve_capacity | reserve_group | mo_ta | co_thi |
|---|---|---|---|---|---|---|
| clb_bongro | CLB Bóng rổ | 20 | 0 | | Tập thứ Hai | No |
| clb_tienganh | CLB Tiếng Anh | 25 | 5 | chinh_sach | Giao tiếp | Yes |

13. Lưu tệp với tên:
```
CLB.xlsx
```

## Phần 3 — Dán vào bảng trên SharePoint

14. Mở bảng `HocSinh` trên trang.
15. Bấm «Edit in grid view» (sửa dạng ô, ở thanh trên).
👀 Bảng chuyển thành dạng ô giống Excel.
16. Trong Excel: bôi đen dữ liệu **từ dòng 2** (không lấy dòng tiêu đề), **mỗi lần tối đa 200 dòng**, bấm `Ctrl` + `C`.
17. Trên SharePoint: bấm vào ô đầu tiên của dòng trống cuối cùng, bấm `Ctrl` + `V`.
18. Chờ đến khi hết biểu tượng đang lưu.
19. Lặp lại bước 16 đến 18 cho đến hết danh sách.
20. Bấm «Exit grid view».
21. Làm lại bước 14 đến 20 cho bảng `CLB` với tệp `CLB.xlsx`.

⚠️ Cột trong Excel phải **cùng thứ tự** với cột trên SharePoint, nếu không dữ liệu sẽ lệch cột.
⚠️ Có dòng báo lỗi: thường do trùng mã hoặc trùng thư điện tử. Sửa trong Excel rồi dán lại riêng dòng đó.

## Kiểm tra

- [ ] Bấm ⚙ → «Site contents». Số ở cột «Items» của `HocSinh` bằng số học sinh, của `CLB` bằng số câu lạc bộ.
- [ ] Mở thử 3 dòng bất kỳ: thư điện tử viết chữ thường, các cột không bị lệch.
