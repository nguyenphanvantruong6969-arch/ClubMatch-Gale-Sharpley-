# Dữ liệu đầu vào và cách phần mềm xử lý

> **Dữ liệu mô phỏng.** Các ví dụ lấy từ sổ mẫu `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` và `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx`, toàn
> bộ tên và mã do máy sinh. Không có học sinh thật.

Phần mềm nhận **một tệp Excel duy nhất**, gọi là Sổ nhập CLB. Bấm "Tải sổ nhập mẫu" trong giao diện để lấy bản trắng đúng định dạng
(`tao_so_nhap_mau`).

## 1. Sổ nhập gồm gì

**Sheet "1. CLB": mỗi câu lạc bộ một dòng.**

| Cột | Ý nghĩa |
|---|---|
| Tên CLB, Mã CLB | Tên hiển thị và mã; mỗi CLB một tên, một mã riêng |
| Buổi | Buổi sinh hoạt của CLB (ví dụ Thứ 2, Thứ 5). Có thể để trống khi trường chỉ có một buổi |
| Chỉ tiêu | Số chỗ; số nguyên lớn hơn 0 |
| Suất ưu tiên | Số chỗ trong Chỉ tiêu dành riêng (dự trữ) cho một nhóm; không lớn hơn Chỉ tiêu |
| Nhóm ưu tiên | Tên nhóm được dùng suất dự trữ của CLB này |
| Loại, Điểm sàn, Tối thiểu, Sức chứa phòng | Cột của chế độ FA-DAA (CLB tự do, giới hạn, tuyển chọn). Chế độ tắt thì các cột này bị bỏ qua, có cảnh báo |

**Sheet "2. Học sinh": mỗi học sinh một dòng.**

| Cột | Ý nghĩa |
|---|---|
| Mã HS, Họ tên | Mã duy nhất; mỗi học sinh một dòng |
| Nhóm ưu tiên | Nhóm của học sinh (nếu thuộc nhóm có suất dự trữ) do trường khai |
| NV1 … NV5 (hoặc "Nguyện vọng 1…") | CLB học sinh muốn, theo thứ tự; chọn tên trong danh sách thả xuống |
| Điểm 1 … Điểm 5 / "Điểm thi" | Điểm thi vào CLB đó; để trống hoặc ghi chữ "thi" nếu chưa có điểm |
| Huy chương (60/30/10) | Có ở sổ mẫu của chế độ FA-DAA: huy chương học sinh đặt cho từng nguyện vọng |

Điểm quyết tâm (mỗi học sinh chia 100 điểm cho các lựa chọn) và lớp của học sinh được nhập ở thẻ Quản lý hoặc qua biểu mẫu, không nằm trong
sổ này.

## 2. Phần mềm làm gì khi dữ liệu thiếu hoặc mâu thuẫn

Nguyên tắc: **dừng và nói rõ, không đoán, không sửa thay**. Có lỗi ở bước nạp thì không nạp gì (không nạp một nửa). Có lỗi ở bước chạy
thì lần chạy dừng ngay, dữ liệu không đổi. Mỗi thông báo nêu sheet, số dòng và mã học sinh để người nhập sửa đúng chỗ.

## 3. Các thông báo thật, trích nguyên văn

Chữ trong ngoặc nhọn như `{sheet}`, `{dong}` là chỗ phần mềm điền giá trị thật (sheet nào, dòng mấy, học sinh nào) khi hiện lên màn hình.
Nguồn duy nhất của các thông báo: `i18n_errors.py`.

**Khi nạp Sổ nhập (không nạp gì nếu có lỗi)**

- `so_nhap_chi_nhan_xlsx`:
  > Phần mềm chỉ nhận Sổ nhập CLB (tệp .xlsx). Hãy bấm "Tải sổ nhập mẫu", điền vào sổ đó rồi nạp lại.
- `so_nhap_thieu_sheet`:
  > Sổ nhập thiếu sheet "{sheet}".
- `so_nhap_thieu_cot`:
  > Sheet "{sheet}" thiếu cột "{cot}". Đừng xoá hay đổi tên dòng tiêu đề của sổ.
- `so_nhap_khong_co_clb`:
  > Sheet "{sheet}" chưa có {slot_l} nào.
- `so_nhap_clb_trung_ten`:
  > Sheet "{sheet}", dòng {dong}: tên {slot_sl} "{ten}" đã có ở dòng {dong_truoc}. Mỗi {slot_sl} một tên riêng.
- `so_nhap_clb_trung_ma`:
  > Sheet "{sheet}", dòng {dong}: Mã CLB "{ma}" đã có ở dòng {dong_truoc}.
- `so_nhap_chi_tieu_sai`:
  > Sheet "{sheet}", dòng {dong} ({ten}): Chỉ tiêu phải là số nguyên lớn hơn 0, Suất ưu tiên không được lớn hơn Chỉ tiêu (đang ghi: {chi_tieu} / {uu_tien}).
- `so_nhap_thieu_ma_hs`:
  > Sheet "{sheet}", dòng {dong}: thiếu Mã HS.
- `so_nhap_hs_trung`:
  > Sheet "{sheet}", dòng {dong}: Mã HS {student_id} đã có ở dòng {dong_truoc}. Mỗi {person_l} một dòng.
- `so_nhap_clb_khong_co`:
  > Sheet "{sheet}", dòng {dong} ({student_id}), NV{k}: không có {slot_sl} nào tên "{gia_tri}" ở sheet "1. {slot_s}". Hãy chọn tên trong danh sách thả xuống.
- `so_nhap_nv_trung`:
  > Sheet "{sheet}", dòng {dong} ({student_id}): "{gia_tri}" được chọn hai lần (NV{k_truoc} và NV{k}).
- `so_nhap_diem_sai`:
  > Sheet "{sheet}", dòng {dong} ({student_id}), {score} {k}: "{gia_tri}" không phải {score_l}. Ghi một số (vd 8,5), hoặc chữ thi nếu chưa có {score_l}.
- `so_nhap_diem_khong_nv`:
  > Sheet "{sheet}", dòng {dong} ({student_id}): có {score} {k} nhưng NV{k} trống. {score} phải nằm ngay cạnh {slot_sl} của nó.
- `so_nhap_qua_tran_nv`:
  > Sheet "{sheet}", dòng {dong} ({student_id}): {n} nguyện vọng ở {session_l} {buoi}, tối đa {tran} mỗi {session_l}. Bớt nguyện vọng của {session_l} này.

**Khi bấm chạy xếp (chạy dừng, dữ liệu không đổi)**

- `chua_co_du_lieu_de_chay`:
  > Chưa có {person_l} hoặc chưa có {slot_l} nào, nên chưa chạy xếp. Hãy nhập dữ liệu ở thẻ Xếp {slot_sl} trước: Sổ nhập CLB hoặc các tệp CSV.
- `wharton_ho_so_chua_hop_le`:
  > {n} {person_l} có hồ sơ điểm quyết tâm chưa hợp lệ, nên chưa chạy xếp. Hãy điền đủ điểm quyết tâm cho những {person_l} này rồi chạy lại: mở thẻ 05 (Quản lý), mục Điểm quyết tâm, sửa điểm của từng {person_l} hoặc bấm "Phóng cho đủ 100 theo tỉ lệ".
- `wharton_chua_dung_het`:
  > Chưa dùng hết điểm quyết tâm: {person_l} {student_id} còn thiếu {thieu} điểm ở quỹ {quy}.

**Sau khi có kết quả**

- `khieu_nai_khong_hop_le`:
  > Không nhận được khiếu nại: không tìm thấy {person_l} {student_id} hoặc buổi {buoi} chưa có kết quả.
- `khieu_nai_qua_han`:
  > Đã quá hạn khiếu nại ({so_ngay} ngày từ lúc công bố kết quả).
- `khieu_nai_trung`:
  > {person} {student_id} đã có một khiếu nại đang chờ xử lý cho buổi này.
- `khieu_nai_da_xu_ly`:
  > Khiếu nại này đã được xử lý rồi.

**Tài khoản và quyền**

- `gt3_can_dang_nhap`:
  > Cần đăng nhập để làm việc này.
- `gt3_khong_du_quyen`:
  > Tài khoản này không có quyền làm việc này. Hãy nhờ người quản trị.
- `gt3_sai_thong_tin`:
  > Tên tài khoản hoặc mật khẩu không đúng.
- `gt3_tam_khoa`:
  > Nhập sai quá nhiều lần. Tài khoản tạm khoá, thử lại sau {giay} giây.

Ví dụ thật: nạp `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx` (10 học sinh, cố ý sai 5 chỗ) cho đúng năm lỗi `so_nhap_chi_tieu_sai`,
`so_nhap_clb_khong_co`, `so_nhap_diem_sai`, `so_nhap_hs_trung`, `so_nhap_nv_trung` và không nạp gì. Chạy xếp khi chưa có dữ liệu trả
`chua_co_du_lieu_de_chay`.

## 4. Khi một câu lạc bộ đã đủ chỗ

- Mỗi học sinh có danh sách nguyện vọng theo thứ tự. Thuật toán cho học sinh "đề xuất" lần lượt từng nguyện vọng; CLB giữ tạm những
  học sinh ưu tiên nhất trong giới hạn chỉ tiêu (có tính suất dự trữ) và từ chối phần còn lại; học sinh bị từ chối đề xuất nguyện vọng kế tiếp.
- Học sinh hết nguyện vọng mà vẫn không có chỗ được liệt kê ở trang **Chưa có chỗ** của tệp Excel kết quả.
- **Khiếu nại:** học sinh gửi khiếu nại theo mã học sinh và buổi; quản trị chấp nhận hoặc từ chối. Có hạn khiếu nại tính bằng
  ngày kể từ lúc công bố kết quả, quá hạn bị từ chối, và mỗi học sinh một khiếu nại đang chờ cho mỗi buổi (xem các thông báo ở mục 3).
- **Nhập thêm sau khi có kết quả** (học sinh đến muộn): số bốc thăm đã khoá được giữ nguyên, học sinh mới được chèn ngẫu nhiên, thứ tự
  của những người đã có không đổi.
- Mỗi lần chạy thêm một dòng vào lịch sử chạy; dòng cũ không bao giờ bị sửa hay xoá.

## 5. Phần mềm không bao giờ dùng

- **Thứ hạng nguyện vọng** (học sinh xếp CLB nào thứ mấy) không đi vào khoá ưu tiên của câu lạc bộ. Thứ hạng chỉ cho biết học sinh muốn CLB nào hơn.
- **Kết quả của buổi hoặc kỳ trước** không đi vào khoá ưu tiên.
- **Hoàn cảnh cá nhân** (gia cảnh, nhận xét của giáo viên…) không có chỗ nhập và không có tiêu chí nào đọc.
- Điều đó nghĩa là ưu tiên chỉ đến từ: điểm thi (nếu CLB có thi), nhóm dự trữ trường khai, huy chương (chế độ FA-DAA) và một số bốc thăm cố định.
  Kiểm tra trong mã: `compute_club_priority` ở `rbda_priority_pipeline.py` không nhận thứ hạng nguyện vọng hay kết cục kỳ trước làm tham số.

## 6. Tài khoản và quyền

Có hai vai (`quan_tri`, `giao_vien`); tính năng tắt cho tới khi có tài khoản đầu tiên. Các thông báo ở mục 3 nhóm "Tài khoản và quyền". Cách bật,
cách xem nhật ký thao tác và cách xoá tài khoản khi quên mật khẩu: `HUONG_DAN_CHAY.md`, mục 8.

## 7. Giới hạn đã biết (chưa làm)

Không có máy chủ nhiều người dùng hay đăng nhập qua mạng, không mã hoá dữ liệu lưu trên đĩa, không yêu cầu hai người cùng duyệt. Đây là máy dùng
một chỗ, ngoại tuyến.
