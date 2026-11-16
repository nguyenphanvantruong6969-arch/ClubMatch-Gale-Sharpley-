# Hướng dẫn chạy từ bản sao mới

> **Dữ liệu mô phỏng.** Sổ mẫu dùng ở đây gồm 120 học sinh do máy sinh (hạt giống cố định); không có học sinh thật.
> Các bước 1–7 đã được chạy thật trên Linux (Python 3.11), kết quả ghi bên dưới. Lệnh Windows ghi cạnh lệnh Linux; riêng
> lệnh Windows chưa chạy lại trong lần soạn này.

Mọi lệnh chạy từ thư mục gốc của kho mã. Linux dùng `.venv/bin/python`; Windows dùng `.venv\Scripts\python`.

## 1. Chuẩn bị môi trường

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Windows: `python -m venv .venv` rồi `.venv\Scripts\pip install -r requirements-dev.txt`.
Kết quả mong đợi: cài xong không lỗi; `.venv/bin/python -c "import pytest"` không báo gì.

## 2. Chạy thử bộ kiểm thử (một tệp nhỏ)

```bash
.venv/bin/python -m pytest -q tests/test_gt3_tai_lieu.py
```

Mong đợi: dòng cuối dạng `NN passed`. Bộ kiểm thử đầy đủ chạy khoảng 22 phút (có cả test giao diện bằng Chromium); trong dự án,
bộ đầy đủ do hệ thống kiểm tra tự động của kho mã chạy.

## 3. Mở phần mềm

```bash
.venv/bin/python main.py
```

Windows: `.venv\Scripts\python main.py`, hoặc chạy tệp đã đóng gói (`build_windows.bat` dựng ra `dist\PhanBoCauLacBo\PhanBoCauLacBo.exe`).
Phần mềm thử mở cửa sổ pywebview; nếu cửa sổ này không dựng được thì tự chuyển sang `browser_host.py`: máy chủ cục bộ ở `127.0.0.1`
cùng một cửa sổ trình duyệt riêng. Chỉ nghe trên máy này, mọi lời gọi phải kèm mã thông hành ngẫu nhiên sinh lúc khởi động.

**Phần đã kiểm trong lần soạn này:** máy chủ trình duyệt khởi động không mở cửa sổ (`browser_host.serve(..., open_browser=False)`),
rồi một lời gọi `POST /__api__/get_trang_thai_ket_qua` kèm mã thông hành trả `{"ok": true, "data": {"co_ket_qua": false, ...}}`;
không kèm mã thì bị từ chối `403`. **Chưa kiểm:** cửa sổ pywebview thật (môi trường soạn không có màn hình).

## 4. Nạp sổ nhập mẫu

Trong giao diện, thẻ **Xếp**: kéo tệp `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` vào vùng thả tệp. Việc tương đương qua API:
`xem_truoc_so_nhap` rồi `import_so_nhap`.

Mong đợi ở bước xem trước: **8 CLB, 2 buổi, 120 học sinh, 829 nguyện vọng, 194 lượt thi**. Nạp xong, phản hồi có
`n_clb: 8, n_hoc_sinh: 120`, cùng một cảnh báo `fa_cot_bo_qua` (tệp mẫu có các cột của chế độ FA-DAA, không gian làm việc mặc
định chưa bật chế độ đó nên các cột này bị bỏ qua, không lưu).

Muốn thử sổ có lỗi: nạp `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx`. Mong đợi: năm lỗi (`so_nhap_chi_tieu_sai`, `so_nhap_clb_khong_co`,
`so_nhap_diem_sai`, `so_nhap_hs_trung`, `so_nhap_nv_trung`) và **không nạp gì**.

## 5. Chạy xếp

Bấm chạy xếp với hạt giống 42 (hoặc `run_pipeline(42)`).

**Lần chạy đầu bị chặn là đúng:** sổ mẫu có điểm quyết tâm của 120 học sinh chưa chia đủ 100, nên `validate` dừng với
`wharton_ho_so_chua_hop_le` (n = 120). Cách xử lý theo đúng lời nhắn: thẻ Quản lý, mục Điểm quyết tâm, bấm **"Phóng cho đủ 100 theo
tỉ lệ"** (API `phong_wharton_hang_loat("PHONG")`, phản hồi `n_phong: 120`). Chạy lại.

Mong đợi: các bước `backup`, `validate`, `stb_lottery`, `rbda_cascade`, `write_results`, `export` đều `done`; thư mục xuất có
`match_results.csv`; trạng thái kết quả `co_ket_qua: true`.

## 6. Tra cứu một học sinh

Thẻ Kết quả, ô tìm kiếm: gõ `FA001` (tên "Học sinh mô phỏng 001"). Với hạt giống 42, `match_results.csv` ghi:

| Buổi | CLB | Hạng nguyện vọng |
|---|---|---|
| `thu_2` | `THU_2_2` | 1 |
| `thu_5` | `THU_5_4` | 1 |

Chế độ giải thích từng học sinh (`get_ly_do_ket_qua`) chỉ có nội dung khi bật chế độ FA-DAA; ở không gian làm việc mặc định nó trả
`fa_bat: False`. Phần giải thích bằng câu cho từng học sinh, phiếu in và tra cứu bằng mã tại kiosk: (sau tích hợp).

## 7. Xuất

Thẻ Kết quả, nút xuất Excel (`export_ket_qua`): tệp có các trang *Hướng dẫn, Danh sách học sinh, Theo CLB, Theo lớp, Chưa có chỗ,
Điểm chuẩn, Thống kê, Dấu vết (kỹ thuật)*. CSV: `match_results.csv` (cột `student_id, buoi, club_id, matched_tier, rank_in_student_pref`).

## 8. Tài khoản, vai trò, nhật ký thao tác

- **Mặc định tắt.** Chưa có tài khoản nào thì phần mềm làm việc như trước, không đòi đăng nhập, không ghi nhật ký.
- **Bật:** tạo tài khoản **đầu tiên** (hộp *Tài khoản*, hoặc `tao_tai_khoan(ten, mat_khau, vai)`). Tài khoản đầu tiên phải có vai
  `quan_tri`; người tạo được đăng nhập luôn. Từ lúc đó mọi thao tác cần đăng nhập.
- **Hai vai:** `quan_tri` (làm mọi việc, kể cả chạy xếp, đổi cấu hình, quản lý tài khoản, xem nhật ký) và `giao_vien` (nhập dữ liệu,
  xem kết quả; không làm việc dành riêng cho quản trị). Thao tác bị từ chối trả `gt3_khong_du_quyen` và vẫn được ghi nhật ký.
- **Nhật ký thao tác:** hộp *Tài khoản*, mục *Nhật ký thao tác* (chỉ quản trị): mới nhất trước, lọc theo người và hành động, xuất
  CSV `nhat_ky_thao_tac.csv` (`export_nhat_ky_thao_tac_csv`). Bảng chỉ thêm; không sửa, không xoá được. Mật khẩu và nội dung tệp không
  bao giờ vào nhật ký. Ví dụ hai dòng đầu của một lần thử (dữ liệu mô phỏng):

  ```
  id,luc,nguoi,vai,hanh_dong,ket_qua,chi_tiet
  1,2026-11-16T12:56:22,quantri,quan_tri,tao_tai_khoan,ok,"{""ten"": ""quantri"", ""vai"": ""quan_tri""}"
  2,2026-11-16T12:56:22,quantri,quan_tri,create_or_update_club,ok,"{""club_id"": ""B"", ""name"": ""CLB B"", ...}"
  ```
- **Quên mật khẩu quản trị** (phần mềm đang đóng):

  ```bash
  .venv/bin/python recovery.py --xoa-tai-khoan <đường dẫn app.db>
  ```

  Windows: `.venv\Scripts\python recovery.py --xoa-tai-khoan <đường dẫn app.db>`. Lệnh sao lưu `app.db` rồi xoá **toàn bộ** tài khoản
  (dữ liệu phân bổ giữ nguyên); đã chạy thật, in `Da sao luu va xoa 1 tai khoan.`. Sau đó phần mềm trở về trạng thái chưa có tài khoản.
- Đăng nhập sai nhiều lần thì tài khoản tạm khoá (`gt3_tam_khoa`); phiên đăng nhập hết hạn khi không hoạt động.

## 9. Kiểm "trùng khít" (tuỳ chọn)

```bash
.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20
```

Mong đợi: `7/7 mục ĐẠT`, trong đó `trung_khit`: 60 ca (3 bộ × 20 hạt giống) trùng khít với nhánh so sánh.
