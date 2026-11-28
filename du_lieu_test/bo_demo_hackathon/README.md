# Bộ demo hackathon — mọi tính năng + cổng đăng nhập

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
> Tên, lớp, nguyện vọng, điểm thi, điểm quyết tâm do máy bịa (seed `20261128`). Mật khẩu và PIN
> chỉ dùng cho buổi demo, **không dùng ở trường thật**. Không trình bày các con số dưới đây như khảo sát thật.

## Trong thư mục này

| Tệp | Là gì | Dùng ở bước |
|---|---|---|
| `demo-truong-thpt-mo-phong.zip` | Workspace **Trường học**: 240 em · 12 CLB · 3 buổi (T2/T4/T6) · 8 lớp · suất ưu tiên (`chinh_sach`, `khoi_10`) · 2 CLB thi tuyển · điểm quyết tâm hợp lệ · mã tra cứu · **3 tài khoản** | A–F |
| `demo-cong-dang-ky.zip` | Workspace **Cổng đăng ký**, đang ở giai đoạn *Học sinh đăng ký*: 4 GV, 4 phòng, 8 CLB đã duyệt (Tự do / Giới hạn / Tuyển chọn), 60 em — **50 đã nộp, 10 chưa nộp** | G |
| `SO_NHAP_DEMO_240HS.xlsx` | Đúng sổ đã nạp trong workspace trên (để mở cho giám khảo xem định dạng đầu vào) | A |
| `SO_NHAP_DEN_MUON_6HS.xlsx` | 6 em đến muộn (`MUON01`–`MUON06`), nạp **sau** lần chạy đầu | E |
| `TAI_KHOAN_DEMO.csv` | **Mọi** thông tin đăng nhập: 3 tài khoản phần mềm, mật khẩu quản trị cổng, 4 PIN giáo viên, 60 PIN học sinh | mọi bước |
| `MA_TRA_CUU_DEMO.csv` | Mã tra cứu 8 ký tự của từng em (chế độ học sinh tự tra cứu) | F |
| `DIEM_DAN_CONG_DANG_KY.txt` | Điểm thi để dán cho các em nộp trực tiếp lúc demo | G |
| `KIEM_CHUNG.json` | Số liệu phần mềm thật trả về khi script tự kiểm | đối chiếu |
| `tao_bo_demo.py` | Script sinh lại cả bộ | — |

## Đăng nhập (trích `TAI_KHOAN_DEMO.csv`)

| Cổng | Vai | Tên đăng nhập | Mật khẩu / PIN | Thấy được gì |
|---|---|---|---|---|
| Phần mềm chính | Quản trị | `quantri.demo` | `Demo@2026` | Mọi thứ: nạp, chạy, cấu hình, tài khoản |
| Phần mềm chính | Giáo viên | `gv.nguyen` / `gv.tran` | `GiaoVien@01` / `GiaoVien@02` | Xem, xuất, nhập điểm; **bị chặn** chạy phân bổ |
| Cổng đăng ký | Quản trị | (bỏ trống) | `DangKy@2026` | Giai đoạn, duyệt CLB, PIN, nhập điểm, chốt và xếp |
| Cổng đăng ký | Giáo viên | `Cô Lê Thu Hà` … (4 GV) | PIN trong CSV | CLB của mình |
| Cổng đăng ký | Học sinh | `DK051`–`DK060` (chưa nộp) | PIN trong CSV | Tự xếp nguyện vọng, huy chương |
| Tra cứu | Học sinh | `HS…` | mã trong `MA_TRA_CUU_DEMO.csv` | Chỉ lời giải thích của chính em |

Mã trường (giáo viên tự đăng ký): `THPTDEMO`. PIN và mã tra cứu sinh bằng `secrets` nên **mỗi lần sinh lại
là bộ mới**; CSV luôn khớp với `.zip` cùng lần sinh — đừng trộn tệp của hai lần sinh.

## Chuẩn bị (2 phút)

1. Mở phần mềm → **Workspace** → **Nhập workspace** → chọn `demo-truong-thpt-mo-phong.zip`, rồi
   `demo-cong-dang-ky.zip`.
2. Mở workspace *DEMO Trường THPT Mô Phỏng*: màn đăng nhập hiện ra.

## Kịch bản demo theo tính năng

| # | Tính năng | Làm gì | Kết quả đúng (đã kiểm, `seed = 42`) |
|---|---|---|---|
| A | **Đầu vào một tệp** | Mở `SO_NHAP_DEMO_240HS.xlsx` cho giám khảo xem: một dòng một em, NV kèm điểm thi, điểm quyết tâm | Sổ đã nạp **0 cảnh báo** |
| B | **Cổng đăng nhập + phân quyền** | 1) Gõ sai mật khẩu. 2) Vào `gv.nguyen`, bấm Chạy phân bổ. 3) Đăng xuất, vào `quantri.demo` | 1) *"Tên tài khoản hoặc mật khẩu không đúng."* (không lộ tên nào có thật). 2) *"Tài khoản này không có quyền làm việc này."* 3) Vào được mọi thẻ |
| C | **Cảnh báo dữ liệu** | Thẻ Vận hành → *Cảnh báo dữ liệu* | Chỉ đúng một loại: *buổi quá tải* (cố ý chật chỗ) |
| D | **Chạy RB-DA nhiều buổi** | **Chạy phân bổ**, rồi xem Kết quả, Thời khoá biểu, Số bốc thăm, Suất ưu tiên, Điểm chuẩn | **192/240** em có ít nhất một CLB · 321 chỗ: NV1 257, NV2 45, NV3 19 · **20** suất ưu tiên được dùng |
| E | **Em đến muộn + khoá bốc thăm** | Nạp `SO_NHAP_DEN_MUON_6HS.xlsx` → bấm chạy → Quản lý → *Mở khoá sửa điểm quyết tâm* (gõ `MO`) → nạp lại → chạy lại | Lần nạp đầu cảnh báo điểm quyết tâm **đang khoá**, lần chạy **bị chặn** (6 hồ sơ chưa hợp lệ). Sau mở khoá: **195/246**. Thứ tự bốc thăm giữa 240 em cũ **giữ nguyên tuyệt đối**; 8 lượt chỗ (em × buổi) của em cũ đổi vì em mới bốc vị trí ngẫu nhiên. Lịch sử chạy có **2 dòng**, không dòng nào bị ghi đè |
| F | **Giải trình + chế độ học sinh** | Mở chế độ học sinh, nhập `HS001` + mã trong CSV; rồi nhập sai mã 5 lần | Em chỉ thấy lời giải thích của mình. Lần thứ 6: **tạm khoá 60 giây** |
| — | **Xuất** | Xuất kết quả (Excel), danh sách PDF theo CLB, báo cáo tổng hợp PDF, xuất theo lớp | Đều chạy được |
| G | **Cổng đăng ký trực tuyến** | Mở workspace *DEMO Cổng đăng ký* → *Mở Đăng ký CLB*. 1) Đăng nhập học sinh `DK051` + PIN → xếp NV, đặt huy chương, nộp. 2) PIN sai 5 lần cho một em. 3) Quản trị: chuyển *Nhập điểm*, dán khối điểm của từng CLB từ `DIEM_DAN_CONG_DANG_KY.txt` → **Chốt và xếp** | 1) Nộp được (nên chọn ít nhất một CLB *Tự do* mỗi buổi, không thì có cảnh báo). 2) **Tạm khoá 5 phút**, quản trị mở khoá được. 3) Dòng điểm của em chưa nộp bị bỏ qua và liệt kê (đúng thiết kế); cả 60 em có chỗ mỗi buổi, em không nộp được xếp vào CLB còn chỗ (cột *ngoài nguyện vọng*); xuất ra Sổ nhập |

### Ba điều nên chỉ cho giám khảo (số liệu mô phỏng)

- **Không ai muốn gì được nấy:** 64 chỗ (20%) là NV2–NV3 — thuật toán thật sự phải đẩy em xuống.
- **48 em chưa có CLB nào** trong khi vẫn có người được NV1: phần mềm không nhét em vào CLB em không chọn.
- **Em đến muộn được bốc thăm công bằng** mà không xáo trộn thứ tự của 240 em cũ (bất biến STB).

*Phần nhận xét, diễn giải kết quả trong báo cáo dự án: học sinh tự viết.*

## Bộ bổ sung (đã có sẵn trong `du_lieu_test/`, không chép lại)

| Muốn demo | Dùng |
|---|---|
| Phần mềm bắt lỗi dữ liệu và **không nạp gì** | `../SO_NHAP_CO_LOI_CO_Y.xlsx` (5 lỗi cài sẵn) |
| Điểm quyết tâm sai → lần chạy **bị chặn** đúng em | `../SO_NHAP_DQT_120HS_CO_LOI.xlsx` + `../DQT_BANG_LOI.json` |
| Xếp theo loại CLB + huy chương (FA-DAA) | `../SO_NHAP_MAU_DAY_DU.xlsx` trong workspace bật *Xếp theo loại CLB và huy chương* |
| **Ngành khác** (công ty, xếp nhân viên vào dự án) | `../bo_thu_workspace/cong-ty-binh-minh.zip` |
| Cỡ trường thật (800 em, 20 CLB, 4 buổi) | `../SO_NHAP_DQT_800HS_HOP_LE.xlsx` |

## Sinh lại

```bash
python du_lieu_test/bo_demo_hackathon/tao_bo_demo.py
```

Nội dung ô của hai sổ tất định theo seed; PIN và mã tra cứu đổi mỗi lần. Script dựng mọi thứ **chỉ qua API
của phần mềm** và tự kiểm bằng phần mềm thật trên bản sao (nạp 0 cảnh báo, đăng nhập đúng/sai, giáo viên
bị chặn, chạy, đến muộn, thứ tự bốc thăm, xuất, tra cứu, khoá PIN); một phép kiểm hỏng thì **không ghi tệp nào**.
