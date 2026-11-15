# SP04 — List `CLB`

⏱ 10 phút · [← SP03](SP03_thao_tac_list_co_ban.md) · Tiếp: [SP05](SP05_list_HocSinh.md)

**Cần có trước:** SP02, SP03.

| # | Thao tác | Tên | Kiểu | Bắt buộc | Số lẻ |
|---|---|---|---|---|---|
| 1 | T1 | List `CLB` | | | |
| 2 | T2 | `club_id` | (Title) | Có | |
| 3 | T3 | `name` | Single line of text | Có | |
| 4 | T3 | `capacity` | Number | Có | 0 |
| 5 | T3 | `reserve_capacity` | Number | | 0 |
| 6 | T3 | `reserve_group` | Single line of text | | |
| 7 | T3 | `mo_ta` | Multiple lines of text | | |
| 8 | T3 | `co_thi` | Yes/No | | |
| 9 | T4 | cột `club_id` | | | |
| 10 | T5 | cột `club_id` | | | |

- [ ] Làm xong 10 dòng trên, theo thứ tự.

## Kiểm tra xong
- 👀 Tiêu đề cột đúng thứ tự: `club_id, name, capacity, reserve_capacity, reserve_group, mo_ta, co_thi`. Sai thứ tự → *Column ordering* (SP03).
- 5 cột đầu **phải** đúng thứ tự này (khớp tệp mẫu kiosk `mau_csv/05_danh_sach_club.csv`).

## Lưu ý
- `club_id`: không dấu, không cách, ví dụ `clb_bongro`. **Không đổi mã sau khi mở đăng ký.**
- `reserve_capacity` nằm **trong** `capacity`, không cộng thêm.
