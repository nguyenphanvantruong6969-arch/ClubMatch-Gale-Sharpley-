# Cài đặt app đăng ký CLB — Mục lục các bước nhỏ

> Bộ tài liệu này tách hướng dẫn cài đặt thành **các tệp nhỏ, mỗi tệp một việc**. Mỗi tệp có: *Cần có trước*, *các bước (mỗi bước một thao tác)*, *Kiểm tra xong*, *Nếu lỗi*.
> Làm **theo đúng thứ tự** bên dưới. Xong tệp nào, tick ở đây.
> Bản gộp (đọc một mạch): [`../HUONG_DAN_CAI_DAT_MOI_TRUONG.md`](../HUONG_DAN_CAI_DAT_MOI_TRUONG.md). Bản kỹ thuật: [`../HUONG_DAN_POWER_APPS_DANG_KY.md`](../HUONG_DAN_POWER_APPS_DANG_KY.md).
> Giao diện Microsoft thay đổi theo thời gian: tên nút có thể hơi khác, mỗi bước đã ghi tên thay thế. Dữ liệu ví dụ là **giả**.

## Quy ước trong mọi tệp

| Ký hiệu | Nghĩa |
|---|---|
| **Bấm** `A → B` | Bấm A, rồi bấm B trong menu hiện ra |
| `chữ đơn cách` | Gõ hoặc dán **đúng y hệt**, kể cả chữ hoa/thường |
| 👀 | Bạn sẽ thấy gì nếu làm đúng |
| ⚠️ | Lỗi hay gặp ở bước này |
| ⏱ | Thời gian ước tính |

## Phần A — SharePoint (nơi chứa dữ liệu)

| ✓ | Tệp | Việc | ⏱ |
|---|---|---|---|
| [ ] | [SP01](sharepoint/SP01_kiem_quyen.md) | Kiểm tra tài khoản và quyền | 10 phút |
| [ ] | [SP02](sharepoint/SP02_tao_site.md) | Tạo SharePoint site (và cách làm khi bị chặn) | 10 phút |
| [ ] | [SP03](sharepoint/SP03_thao_tac_list_co_ban.md) | Học 5 thao tác List cơ bản (dùng lại ở SP04–SP07) | 10 phút |
| [ ] | [SP04](sharepoint/SP04_list_CLB.md) | Tạo List `CLB` | 10 phút |
| [ ] | [SP05](sharepoint/SP05_list_HocSinh.md) | Tạo List `HocSinh` | 10 phút |
| [ ] | [SP06](sharepoint/SP06_list_NguyenVong.md) | Tạo List `NguyenVong` | 15 phút |
| [ ] | [SP07](sharepoint/SP07_list_ChonThi.md) | Tạo List `ChonThi` (bỏ qua nếu không có thi) | 10 phút |
| [ ] | [SP08](sharepoint/SP08_nap_excel.md) | Nạp danh sách học sinh và CLB từ Excel | 20 phút |
| [ ] | [SP09](sharepoint/SP09_phan_quyen.md) | Phân quyền giáo viên và học sinh | 20 phút |

## Phần B — Power Apps (giao diện học sinh dùng)

| ✓ | Tệp | Việc | ⏱ |
|---|---|---|---|
| [ ] | [PA01](powerapps/PA01_dang_nhap_moi_truong.md) | Đăng nhập, chọn đúng Environment | 5 phút |
| [ ] | [PA02](powerapps/PA02_tao_app.md) | Tạo app trống, cài hiển thị phone + laptop | 10 phút |
| [ ] | [PA03](powerapps/PA03_noi_du_lieu.md) | Nối app với 4 List | 5 phút |
| [ ] | [PA04](powerapps/PA04_cong_thuc_app.md) | Dán công thức chung (hạn chót, quản trị…) | 10 phút |
| [ ] | [PA05](powerapps/PA05_tao_man_hinh_va_khung.md) | Tạo 5 màn hình và khung co giãn | 20 phút |
| [ ] | [PA06](powerapps/PA06_man_khong_co_ten.md) | Màn hình "không có tên" | 5 phút |
| [ ] | [PA07](powerapps/PA07_dang_ky_phan_tren.md) | Màn đăng ký: lời chào, hạn chót, hướng dẫn | 10 phút |
| [ ] | [PA08](powerapps/PA08_dang_ky_o_chon.md) | Màn đăng ký: 10 ô chọn CLB | 30 phút |
| [ ] | [PA09](powerapps/PA09_dang_ky_nut_nop.md) | Màn đăng ký: báo lỗi và nút Nộp | 15 phút |
| [ ] | [PA10](powerapps/PA10_man_xac_nhan.md) | Màn xác nhận | 10 phút |
| [ ] | [PA11](powerapps/PA11_man_chon_thi.md) | Màn chọn CLB thi (tuỳ chọn) | 20 phút |
| [ ] | [PA12](powerapps/PA12_man_quan_tri.md) | Màn quản trị cho giáo viên | 20 phút |
| [ ] | [PA13](powerapps/PA13_man_dau_tien_va_chay_thu.md) | Chọn màn đầu tiên, chạy thử trong Studio | 10 phút |
| [ ] | [PA14](powerapps/PA14_phat_hanh_chia_se.md) | Publish, chia sẻ, link, mã QR | 15 phút |
| [ ] | [PA15](powerapps/PA15_thu_3_hoc_sinh.md) | Thử với 3 học sinh giả, rồi dọn dẹp | 30 phút |

## Phần C — Sau hạn chót
Xuất CSV và nạp rbda-kiosk: mục 8 của [bản kỹ thuật](../HUONG_DAN_POWER_APPS_DANG_KY.md). Cài kiosk: [`HUONG_DAN_CAI_DAT.md`](../../../HUONG_DAN_CAI_DAT.md).

## Sơ đồ phụ thuộc
```
SP01 → SP02 → SP03 → SP04, SP05, SP06, SP07 → SP08 → SP09
                                                  ↓
PA01 → PA02 → PA03 → PA04 → PA05 → PA06…PA12 → PA13 → PA14 → PA15
```
PA03 cần các List đã có (SP04–SP07). PA15 cần SP09 xong.

## Khi kẹt
Chụp **nguyên màn hình** thông báo lỗi, ghi mã tệp và số bước (ví dụ "PA08 bước 7"), gửi người phụ trách.
