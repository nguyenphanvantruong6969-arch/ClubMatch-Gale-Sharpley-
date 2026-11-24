# Kiểm độc lập đầu vào ⇄ kết quả (DC1, phạm vi B)

> **Dữ liệu mô phỏng.** Mọi sổ mẫu dùng ở đây do máy sinh; không có học sinh thật.

Một tệp Python (`kiem_doc_lap.py`) dành cho giám khảo và nhà trường. Nó chỉ dùng thư viện chuẩn của Python và
`openpyxl`, **không import mô-đun nào của phần mềm**, đọc đúng hai thứ: Sổ nhập (.xlsx) và bộ tệp xuất CSV mặc định.

## Chạy

```bash
.venv/bin/python du_lieu_test/kiem_doc_lap/kiem_doc_lap.py \
    --so-nhap du_lieu_test/SO_NHAP_TEST.xlsx \
    --ket-qua <thư mục xuất>/ket_qua_phan_bo.csv \
    [--ra dau_vao_ket_qua.csv]
```

Tệp kết quả phải nằm cạnh `ket_qua_phan_bo_theo_club/` và `ket_qua_phan_bo_tong_hop.csv` (bộ do `export_csv` ghi).
Không có `--ra` thì `dau_vao_ket_qua.csv` được ghi cạnh tệp kết quả. Windows: `.venv\Scripts\python`.

Mã thoát: `0` mọi phép kiểm PASS · `1` có FAIL · `2` đầu vào không đọc được hoặc ngoài phạm vi (nhiều buổi).

## Các phép kiểm

| Mã | Nội dung |
|---|---|
| K0 | Đọc được cả hai tệp; một buổi; mọi CLB trong kết quả khớp một CLB của Sổ nhập (theo Mã CLB, nếu trống thì theo tên) |
| K1 | Mỗi học sinh của Sổ nhập có đúng một dòng; không dòng lạ, không dòng lặp |
| K2 | Số em xếp vào mỗi CLB ≤ Chỉ tiêu (CLB không có Chỉ tiêu bị bỏ qua, có ghi chú) |
| K3 | Số em diện "Dự trữ" ≤ Suất ưu tiên của CLB; nhóm của em dự trữ = Nhóm ưu tiên của CLB; cột "Nhóm dự trữ" khớp Sổ nhập |
| K4 | CLB nhận nằm trong danh sách nguyện vọng của em đó |
| K5 | "Nguyện vọng thứ" = vị trí CLB đó trong danh sách của em (đã bỏ ô trống); em chưa xếp thì để trống |
| K6 | Các tệp trong `*_theo_club/` khớp tệp chính (cùng tập học sinh, cùng thứ hạng/diện/nhóm; `_chua_duoc_xep.csv` = tập chưa xếp) |

Mỗi FAIL ghi số lượng và tối đa 5 mã học sinh/CLB. Tệp `dau_vao_ket_qua.csv` có mỗi học sinh một dòng:
`student_id, ho_ten, nhom, nv_1..nv_k, diem_1..diem_k, club_id_nhan, ten_clb_nhan, dien, hang_nhan`
(`nv_k` là ô thứ k của Sổ nhập; `hang_nhan` là cột "Nguyện vọng thứ" của tệp xuất; điểm chỉ được in lại, không so sánh).

## Giới hạn (phạm vi B)

- **Một buổi**, không gian làm việc mặc định, tệp xuất 8 cột. Tệp nhiều buổi (9 cột) hoặc Sổ nhập có nhiều buổi → mã thoát 2.
- Không hỗ trợ sổ huy chương (FA).
- **Không kiểm đúng luật ưu tiên, không kiểm ổn định, không tính lại bốc thăm.** CLB có hai quỹ chỗ (dự trữ rồi chung), nên phép thử
  "CLB đầy và người nhận cuối kém hơn tôi" sẽ báo sai cho em nhận bằng quỹ dự trữ.
- Sổ nhập có CLB lạ hoặc CLB lặp trong một dòng bị phần mềm từ chối cả sổ khi nạp, nên không đi tới tệp kết quả.

Kiểm thử: `tests/test_dc1_kiem_doc_lap.py` (đột biến từng phép kiểm, cô lập import, ba bộ hợp lệ).
