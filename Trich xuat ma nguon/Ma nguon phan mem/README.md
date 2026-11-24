# Mã nguồn phần mềm

Toàn bộ mã nguồn CẦN để phần mềm phân bổ CLB (rbda-kiosk) chạy được, dưới dạng chữ đọc được
(không phải tệp `.exe`). Chỉ gồm mã chạy thật; không gồm bộ kiểm thử, dữ liệu mô phỏng và tài liệu.

## Cách chạy từ mã nguồn
Cần Python 3.11. Đứng trong thư mục này:

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

Nếu cửa sổ ứng dụng không mở được, chạy giao diện bằng trình duyệt: `python browser_host.py`.
Bản `.exe` cho Windows được đóng gói riêng bằng PyInstaller (không nằm trong thư mục này).

## 1. Khởi động
| Tệp | Vai trò |
|---|---|
| `main.py` | Điểm khởi động: mở cửa sổ ứng dụng, nối giao diện với phần xử lý. |
| `browser_host.py` | Chế độ dự phòng: chạy giao diện trong trình duyệt (chỉ trên máy, địa chỉ 127.0.0.1). |
| `recovery.py`, `recovery.html`, `recovery.js` | Màn hình phục hồi khi tệp dữ liệu `app.db` hỏng hoặc mất. |
| `chan_doan.py` | Ghi lại lý do khi cửa sổ không mở được (để sửa lỗi). |

## 2. Thuật toán (giống thư mục `Thuat toan cot loi`)
| Tệp | Vai trò |
|---|---|
| `rbda_priority_pipeline.py` | Lõi RB-DA (Gale–Shapley + dự trữ mềm + bốc thăm), cấu trúc cơ sở dữ liệu. |
| `fa_daa.py`, `fa_ly_do.py`, `fa_bien_ban.py` | Chế độ huy chương, câu lý do, biên bản bốc thăm để in. |
| `fa_sau_xep.py`, `fa_vong_doi_cho.py` | Việc sau khi xếp; đo vòng đổi chỗ. |
| `giai_trinh.py`, `phieu_giai_trinh.py`, `ma_tra_cuu.py` | Giải trình kết quả từng em, phiếu in, mã để em tự tra cứu. |
| `lop_hoc_sinh.py` | Chuẩn hoá tên lớp. |

## 3. Cầu nối giao diện ↔ xử lý (các tệp `api_*.py`)
Mỗi nút bấm trên giao diện gọi một hàm ở đây; hàm luôn trả về dạng `{ok, data, errors}`.

| Tệp | Vai trò |
|---|---|
| `api.py` | Lớp chính `PipelineAPI`; quy trình chạy: sao lưu → soát → khoá bốc thăm → xếp → kiểm → ghi → xuất. |
| `api_chung.py` | Hàm tiện ích dùng chung. |
| `api_nhap.py` | Nhập dữ liệu (CSV, Excel, Sổ nhập CLB). |
| `api_xuat.py` | Xuất kết quả (Excel, CSV, PDF). |
| `api_bao_cao.py` | Các bảng thống kê ở thẻ Kết quả. |
| `api_quan_ly.py` | Quản lý CLB, học sinh, nhập tại chỗ, xoá dữ liệu. |
| `api_cham_diem.py` | Chấm điểm mù bài thi. |
| `api_sau_xep.py` | Điểm danh, mời danh sách chờ, khiếu nại. |
| `api_tai_khoan.py`, `api_nhat_ky.py` | Đăng nhập, xem nhật ký thao tác. |
| `api_workspace.py` | Quản lý nhiều không gian làm việc. |
| `api_tieu_chi.py`, `api_muc_tieu.py`, `api_phuong_an.py` | Tiêu chí xếp, thẻ mục tiêu, văn bản phương án xếp. |
| `api_forms.py`, `api_forms_bo.py`, `api_forms_nap.py` | Thẻ "Chuẩn bị đợt": dùng biểu mẫu Forms. |

## 4. Chức năng hỗ trợ
| Tệp | Vai trò |
|---|---|
| `so_nhap.py`, `so_excel.py` | Đọc Sổ nhập CLB; viết sổ kết quả Excel. |
| `xuat_pdf.py`, `danh_sach_pdf.py`, `bao_cao_tong_hop.py` | Xuất PDF, danh sách theo CLB/lớp, báo cáo cho ban giám hiệu. |
| `workspace.py`, `cau_hinh_ws.py`, `nhan_ws.py` | Không gian làm việc, cấu hình luật xếp, từ vựng (Học sinh/CLB…). |
| `tieu_chi.py`, `muc_tieu.py`, `muc_tieu_do.py`, `phuong_an_xep.py` | Mô tả luật xếp bằng lời thường, ba thẻ mục tiêu. |
| `tai_khoan.py`, `phan_quyen.py`, `nhat_ky.py` | Tài khoản, phân quyền quản trị/giáo viên, nhật ký chỉ ghi thêm. |
| `forms_dot.py` | Đường dẫn tệp của một đợt Forms. |
| `i18n_errors.py`, `tao_i18n_js.py` | Thông báo lỗi Việt–Anh (một nguồn) và lệnh sinh `i18n_loi.js` từ nó. |

## 5. Giao diện
| Tệp | Vai trò |
|---|---|
| `index.html`, `style.css` | Trang giao diện và kiểu dáng. |
| `js/` | Mã giao diện theo từng thẻ (`00_nen.js` nền chung … `19_muc_tieu.js`). |
| `i18n.js`, `i18n_loi.js`, `chung.js` | Chữ hiển thị Việt–Anh, thông báo lỗi, hàm dùng chung. |
| `assets/fonts/` | Phông chữ Be Vietnam Pro, IBM Plex Mono (giấy phép OFL). |
| `logo.png`, `logo.ico` | Biểu tượng. |

## 6. Công cụ biểu mẫu Forms (`mau_forms_thi_clb/`)
Phần mềm nạp các tệp này khi dùng thẻ "Chuẩn bị đợt": sinh biểu mẫu đăng ký + đề thi từ `de_thi.json`
(`bieu_mau.py`, `tao_mau_forms.py`, `so_de_thi.py`), chuyển tệp Forms xuất ra thành Sổ nhập
(`chuyen_forms_sang_phan_mem.py`, `chuyen_phieu_clb.py`), phân tích câu hỏi, danh sách chưa đăng ký,
đối chiếu, và `bo_dung_t4m/` (bộ dựng sẵn cho SharePoint / Power Apps).

## Thư viện cần cài (`requirements.txt`)
`pywebview` (cửa sổ ứng dụng), `openpyxl` (đọc/ghi Excel), `reportlab` (xuất PDF); trên Windows thêm `pythonnet`, `clr_loader`.
