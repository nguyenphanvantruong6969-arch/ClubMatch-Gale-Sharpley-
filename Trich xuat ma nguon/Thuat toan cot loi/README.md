# Thuật toán cốt lõi

Phần "bộ não" của phần mềm: các tệp quyết định **học sinh nào vào câu lạc bộ (CLB) nào**.
Đây là bản sao mã nguồn dạng chữ (đọc được bằng bất kỳ trình soạn thảo nào), không phải tệp chạy `.exe`.

Thuật toán **RB-DA**: chấp nhận trì hoãn Gale–Shapley (học sinh đề nghị) + chỗ dự trữ mềm hai lượt
(Kominers & Sönmez 2016) + một lần bốc thăm chung phá hoà (STB) + hai tầng ưu tiên
(tầng 1: CLB có thi xét điểm cao trước, rồi số bốc thăm; tầng 2: số bốc thăm).

## Các tệp thuật toán chính

| Tệp | Vai trò |
|---|---|
| `rbda_priority_pipeline.py` | Lõi thuật toán. Hàm then chốt: `compute_club_priority` (thứ tự ưu tiên của CLB), `club_choice_function` (CLB chọn ai, có chỗ dự trữ), `run_rbda` (chạy chấp nhận trì hoãn), `verify_stability` (kiểm kết quả ổn định, không ai "bị oan"), `run_rbda_nhieu_buoi` (xếp nhiều buổi trong tuần), `generate_stb_lottery` / `chen_stb_cho_hoc_sinh_moi` (bốc thăm, khoá số, chèn học sinh đến muộn). Kèm cấu trúc cơ sở dữ liệu SQLite. |
| `fa_daa.py` | Chế độ "huy chương" FA-DAA (mặc định TẮT): lớp bọc quanh lõi, không sửa lõi. Học sinh chia huy chương vàng/bạc/đồng để thể hiện mức muốn. |
| `fa_ly_do.py` | Mẫu câu giải thích kết quả cho học sinh (một nơi duy nhất giữ câu chữ). |
| `giai_trinh.py` | Giải trình cho MỘT học sinh: vì sao em vào CLB này, vì sao không vào CLB cao hơn. Chỉ đọc, không đổi kết quả. |
| `fa_vong_doi_cho.py` | Tìm "vòng đổi chỗ" mà mọi người trong vòng đều lợi (Erdil & Ergin 2008). Chỉ để ĐO, không ghi kết quả. |
| `fa_sau_xep.py` | Sau khi xếp: điểm danh, giải phóng chỗ, mời danh sách chờ. Mọi thay đổi chỉ GHI THÊM, kết quả gốc không bao giờ bị sửa. |
| `lop_hoc_sinh.py` | Chuẩn hoá tên lớp (ví dụ "10a1" → "10A1"). |

## Tệp phụ trợ (cần để các tệp trên chạy được)

| Tệp | Vai trò |
|---|---|
| `so_nhap.py` | Đọc "Sổ nhập CLB" (một tệp Excel chứa danh sách CLB, nguyện vọng, điểm thi). `fa_daa.py` và `giai_trinh.py` dùng vài hằng số ở đây. |
| `nhan_ws.py` | Điền nhãn từ vựng (Học sinh / CLB / Buổi…) vào câu chữ. |
| `i18n_errors.py` | Bảng thông báo lỗi song ngữ Việt–Anh. |

## Chạy thử
Cần Python 3.11. Đứng trong thư mục này:

```bash
python -c "import rbda_priority_pipeline, fa_daa, giai_trinh; print('OK')"
```

Đọc `.xlsx` cần thêm thư viện `openpyxl` (`pip install openpyxl==3.1.5`). Toàn bộ phần mềm (giao diện, nhập/xuất) nằm ở thư mục bên cạnh, `Ma nguon phan mem`.
