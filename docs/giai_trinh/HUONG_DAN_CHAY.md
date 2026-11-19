# Hướng dẫn chạy từ bản sao mới

> **Dữ liệu mô phỏng.** Sổ mẫu dùng ở đây gồm 120 học sinh do máy sinh (hạt giống cố định); không có học sinh thật.
> Các bước 1–7 (bước 4–6 ở không gian bật chế độ huy chương) đã được chạy thật trên Linux (Python 3.11), kết quả ghi bên dưới. Lệnh Windows ghi cạnh lệnh Linux; riêng
> lệnh Windows và các thao tác bấm trên giao diện (ví dụ tích chế độ huy chương lúc tạo không gian) chưa chạy lại trong lần soạn này;
> phần đã chạy là lời gọi API tương đương.

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

**Bật chế độ huy chương trước khi nạp.** Sổ `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` dành cho không gian làm việc xếp theo loại CLB và
huy chương (các cột 60/30/10 là huy chương, không phải điểm quyết tâm). Không gian mặc định không có chế độ này và sẽ chặn lần chạy
(`wharton_ho_so_chua_hop_le`). Cách làm (chế độ "Xếp theo loại CLB và huy chương"): vào nhóm **Cài đặt** (thẻ **Quản lý**), ở đầu trang chọn thẻ **Huy chương** (câu hỏi "Học sinh cho biết mình muốn CLB nào nhiều hơn bằng cách nào?"); bấm là lưu ngay, có nút **Hoàn tác** trong 10 giây. Cũng chọn được ở bước 3 khi tạo không gian làm việc mới, hoặc ở menu **⋯ → Cài đặt…**. Nếu quên và kéo sổ vào trước, phần xem trước sẽ nói sổ có cột Huy chương mà chế độ đang tắt, kèm nút **Bật chế độ huy chương**. Dữ liệu CLB chưa đủ (loại CLB, mỗi buổi một CLB Tự do) thì thẻ Huy chương mở bảng "còn thiếu" để sửa tại chỗ cho tới khi hiện *Sẵn sàng*; các tính năng sau khi xếp (mở vòng 2, khiếu nại, điểm danh, danh sách chờ, phản hồi) là các nút ở khung **Sau khi xếp** của thẻ **Chi tiết và xuất tệp**, chỉ hiện ở chế độ này. Trong mã, cấu hình tương đương là `rules.fa_daa = true`. Ô huy chương của sổ nhận cả **Vàng / Bạc / Đồng** lẫn 60 / 30 / 10.
Không dùng nút "Phóng cho đủ 100": nút đó dành cho điểm quyết tâm và sẽ biến huy chương thành điểm tự đặt.

Rồi trong thẻ **Xếp**: kéo tệp `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` vào vùng thả tệp. Việc tương đương qua API:
`xem_truoc_so_nhap` rồi `import_so_nhap`.

Mong đợi ở bước xem trước: **8 CLB, 2 buổi, 120 học sinh, 829 nguyện vọng, 194 lượt thi**, không lỗi và không cảnh báo. Nạp xong,
phản hồi có `n_clb: 8, n_hoc_sinh: 120`. Khi nạp, phần mềm có thể liệt kê nhiều cảnh báo `wharton_chua_dung_het` ("Chưa dùng hết điểm
quyết tâm…"; lần chạy thử có 434 dòng); đó chỉ là lưu ý, không chặn việc chạy xếp.

Muốn thử sổ có lỗi: nạp `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx`. Mong đợi: năm lỗi (`so_nhap_chi_tieu_sai`, `so_nhap_clb_khong_co`,
`so_nhap_diem_sai`, `so_nhap_hs_trung`, `so_nhap_nv_trung`) và **không nạp gì**.

## 5. Chạy xếp

Bấm chạy xếp với hạt giống 42 (hoặc `run_pipeline(42)`).

Mong đợi: lần chạy **không bị chặn**; các bước `backup`, `validate`, `stb_lottery`, `rbda_cascade`, `write_results`, `export` đều
`done`; `n_matched: 120` trên `n_total: 120`, `rounds_run: 8`; thư mục xuất có `match_results.csv`; trạng thái kết quả
`co_ket_qua: true`.

## 6. Tra cứu một học sinh

Thẻ Kết quả, ô tìm kiếm: gõ `FA001` (tên "Học sinh mô phỏng 001"). Với hạt giống 42, `match_results.csv` ghi:

| Buổi | CLB | Hạng nguyện vọng |
|---|---|---|
| `thu_2` | `THU_2_4` | 2 |
| `thu_5` | `THU_5_4` | 1 |

Học sinh `FA002` cùng hạt giống: `thu_2` nhận `THU_2_1` (hạng 3), `thu_5` nhận `THU_5_1` (hạng 4).

Ở chế độ huy chương, phần giải thích bằng câu cho từng học sinh **đã có sẵn**: `get_ly_do_ket_qua` trả `fa_bat: true` cùng các câu
cho từng buổi, ví dụ FA001 buổi Thứ 2: "Em và các bạn bằng điểm; các bạn có huy chương cao hơn ở CLB Cờ vua (Giới hạn A) được xét
trước." rồi "Em được xếp vào CLB Robot (Tuyển chọn) – nguyện vọng 2 của em." Phiếu in và tra cứu bằng mã tại kiosk, tiêu chí thử và so sánh: xem `KICH_BAN_DEMO.md` bước 8–10; số liệu ca mẫu: `CA_MAU.md`.

## 7. Xuất

Thẻ Kết quả, nút xuất Excel (`export_ket_qua`): tệp có các trang *Hướng dẫn, Danh sách học sinh, Theo CLB, Theo lớp, Chưa có chỗ,
Điểm chuẩn, Thống kê, Dấu vết (kỹ thuật)*. CSV: `match_results.csv` (cột `student_id, buoi, club_id, matched_tier, rank_in_student_pref`).

## 8. Tài khoản, vai trò, nhật ký thao tác

- **Mặc định tắt.** Chưa có tài khoản nào thì phần mềm làm việc như trước, không đòi đăng nhập, không ghi nhật ký.
- **Bật:** tạo tài khoản **đầu tiên** (hộp *Tài khoản*, hoặc `tao_tai_khoan(ten, mat_khau, vai)`). Tài khoản đầu tiên phải có vai
  `quan_tri`; người tạo được đăng nhập luôn. Từ lúc đó mọi thao tác cần đăng nhập.
- **Hai vai:** `quan_tri` (làm mọi việc, kể cả chạy xếp, đổi cấu hình, quản lý tài khoản, xem nhật ký) và `giao_vien` (nhập dữ liệu,
  xem kết quả; không làm việc dành riêng cho quản trị). Thao tác bị từ chối trả `gt3_khong_du_quyen` và vẫn được ghi nhật ký.
- **Nhật ký thao tác:** hộp *Tài khoản*, thẻ *Nhật ký thao tác* (chỉ quản trị): mới nhất trước, hiện bằng chữ dễ đọc (tên thao tác, vai, kết quả, giờ địa phương), lọc theo người, thao tác, ngày, hoặc chỉ các dòng bị từ chối; xuất
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
- **Mã tra cứu và nhật ký:** lượt học sinh tự tra cứu chỉ ghi mã học sinh (không ghi mã tra cứu, không ghi tên người đang đăng
  nhập); xem lời giải trình của một em được ghi một dòng (người xem + mã học sinh). Cơ sở dữ liệu đã dùng **trước bản này** có thể còn mã
  tra cứu trong các dòng nhật ký cũ (bảng chỉ thêm, không xoá được): hãy **tạo lại toàn bộ mã** (`tao_ma_tra_cuu(chi_hs_chua_co=False)`)
  trước khi dùng thật.
- **Quên mật khẩu với bản `.exe` (không có Python):** đóng phần mềm, bấm đúp `QUEN_MAT_KHAU.bat` cạnh `PhanBoCauLacBo.exe`, gõ `XOA`
  (hoặc dòng lệnh `PhanBoCauLacBo.exe --xoa-tai-khoan [app.db] [--yes]`; chạy từ mã nguồn: `python main.py --xoa-tai-khoan <app.db> --yes`).
  Sao lưu trước, xoá toàn bộ tài khoản, dữ liệu phân bổ giữ nguyên.
- **Tạo quản trị đầu tiên trước khi đưa máy cho học sinh dùng:** khi chưa có tài khoản nào, ai mở hộp *Tài khoản* trước sẽ tạo được tài khoản
  quản trị đầu tiên. Hộp tạo tài khoản có ô nhập lại mật khẩu để tránh gõ nhầm.
- Đăng nhập sai nhiều lần thì tài khoản tạm khoá (`gt3_tam_khoa`); phiên đăng nhập hết hạn khi không hoạt động.

## 9. Kiểm "trùng khít" (tuỳ chọn)

```bash
.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20
```

Mong đợi: `7/7 mục ĐẠT`, trong đó `trung_khit`: 60 ca (3 bộ × 20 hạt giống) trùng khít với nhánh so sánh.
