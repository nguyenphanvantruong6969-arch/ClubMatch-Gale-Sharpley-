# DG1 — tự soát bằng `soat-ma` (thay checker; không có người trực) — 2026-11-28

> Người soát: chính phiên coder (Sonnet), theo lệnh «không chờ checker» của Truong. Đây là SOÁT TỰ THÂN, không độc lập:
> nên đọc kỹ các mục «Chưa kiểm được». Cột «Chắc chắn?» theo `SKILL.md` §4.

## Máy
- `python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so FETCH_HEAD` (FETCH_HEAD = `origin/main` vừa `git fetch`): **7/7 ĐẠT**
  (ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, trung_khit 3 bộ × 5 seed, khong_sua_nhat_ky). Chạy sau L4 (bất biến 1).
- `git diff origin/main HEAD --stat -- . ':!du_lieu_test' ':!tests' ':!docs' ':!CHANGELOG.md'`: 10 tệp, **+162 dòng, 1 dòng sửa (mở rộng một selector CSS)**;
  `rbda_priority_pipeline.py`, `fa_daa.py`, `cau_hinh_ws.py`, schema: KHÔNG đổi. Lô sản phẩm duy nhất là L4.
- `tests/test_dg1_*.py`: 49 qua (cuối phiên). Test liên quan: `test_so_excel_de_dung`, `test_du_lieu_ket_qua`, `test_giao_dien_bieu_do`,
  `test_i18n_sync`, `test_i18n_khoa_dc_khong_chet` (73 qua).

## Tầng 1 — lõi
- Bất biến 1 (mặc định giữ nguyên) và 2 (không đưa hạng vào ưu tiên): L4 không chạm hàm lõi; `chi_so_phan_bo` chỉ ĐỌC cột
  `rank_in_student_pref` đã ghi để hiển thị. Điểm quyết tâm mô phỏng (nhóm G) dùng thứ tự danh sách ở phía HỌC SINH giả lập
  chia điểm; phía phần mềm (`diem_wharton_hieu_luc` → `run_rbda`) không nhận hạng.
- Cơ chế đối chứng vẫn gọi `club_choice_function` thật qua `cc._ham_chon`; `dem_cap_chan` chỉ gọi `chon(...)`, không chép luật ưu tiên.
  Test `test_dem_cap_chan_cua_co_che_on_dinh_bang_0_con_boston_khac_0`.
- RB-DA 0 cặp phá vỡ: có trong `doi_chieu_so_lieu.json` (cổng chạy) và kiểm ở MỌI lần chạy lưới (`a.cap_chan` = 0 trong mọi JSON; xem README_LAN_CHAY).
- Cổng đối chiếu: bộ TEST, seed 42, qua `run_pipeline` thật = 108/120, NV1 = 64, 7 vòng; lõi trong bộ nhớ khớp TỪNG dòng `match_results`.

## Tầng 2 — backend
- `get_chi_so_phan_bo`: chỉ SELECT; trả `{ok,data,errors}`; mã lỗi `dg1_error_reading_chi_so` ở `i18n_errors.py`, `i18n_loi.js` sinh lại
  (`kiem_nhanh` ĐẠT). Test canh «chỉ đọc»: `test_api_chi_doc_khong_doi_ket_qua`.
- Nhiều buổi: chạy thử 300 HS × 3 buổi qua `PipelineAPI` → `n = 900` (em × buổi), đã xếp 330 = khớp `match_results` (chạy tay, không commit).
- CLB Tự do (`loai = TU_DO`) không tính vào chỉ tiêu/lấp đầy (test ca tay `test_ham_thuan_ca_tay`).
- Không có rollback/ghi mới nào để chứng minh (đường chỉ đọc).

## Tầng 3 — giao diện (Chromium thật, một test)
- Khối hiện đúng số sau khi chạy; chữ vi/en đổi giữa chừng (`I18N.setLang`) vẽ lại, không còn `{...}` hay chữ Việt trong bản Anh.
- Lỗi đọc (route giả `ok:false`) **hiện câu lỗi** thay vì lặng lẽ ẩn khối (theo mục 3.1 của SKILL). Sửa trong phiên này sau khi tự soát.
- Chữ trong ô đi qua `esc()`; số liệu là số, không có dữ liệu người dùng tự do trong khối (không có tên CLB/em) → rủi ro XSS thấp.
- Chưa thử: ba vai (học sinh/giáo viên/quản trị) — khối thuộc thẻ Kết quả của quản trị; kiosk học sinh không có thẻ này.

## Tầng 4 — vệ sinh, tài liệu, test
- ruff sạch. CHANGELOG + TIEN_DO có dòng DG1-L1..L4, G. Sổ đăng ký (md + json) có mục DG1.
- **Gây hỏng tạm 5 chỗ** (rồi hoàn tác, `git status` sạch): bỏ đường tăng (cận trên) → test đỏ; `<50 %` → `<= 50 %` → đỏ;
  `cận + 1` → đỏ; đảo tốt/xấu trong churn → đỏ; **đổi `h == 1` → `h <= 2` ở `pct_nv1_tat_ca` → test KHÔNG đỏ** (phát hiện #1).
- Cạm bẫy khi thử: hoán `h == 1` ↔ `h <= 2` cùng độ dài + cùng giây → `.pyc` cũ còn giữ bản hỏng sau khi hoàn tác nguồn (pytest ra đỏ giả sau khi
  đã sửa). Đã xoá `__pycache__`; mọi lần chạy đầy đủ dùng mã đã commit (xem README_LAN_CHAY).

## Phát hiện
| # | Mức | Tệp | Hàm | Vấn đề | Đường xảy ra | Đề xuất | Chắc chắn? | Trạng thái |
|---|---|---|---|---|---|---|---|---|
| 1 | nên sửa | tests/test_dg1_chi_so.py | `TestNhomA` | Ca tay đầu mọi em được xếp ở NV1 nên đổi `h == 1` → `h <= 2` không làm test đỏ | mutation M3 | thêm ca có em hạng 2, 3 | đã tái hiện | **ĐÃ SỬA** (`test_phan_biet_nv1_nv2_nv3`; mutation lại → đỏ) |
| 2 | nên sửa | js/03_ket_qua.js | `loadChiSoPhanBo` | `!res.ok` ẩn khối lặng lẽ (lỗi đọc giống «chưa có kết quả») | API lỗi → khối biến mất, không thông báo | hiện câu lỗi | suy luận + test route giả | **ĐÃ SỬA** |
| 3 | nhỏ | du_lieu_test/danh_gia/_sinh.py | `sinh_truong` | κ nhiều buổi lấy `κ·N` cho CẢ BA buổi (mỗi em cần 1 chỗ MỖI buổi) → mô hình quá chật | 300 HS × 3 buổi: 330 chỗ cho 900 suất | κ·N·số buổi | đã tái hiện (36,7 % được xếp) | **ĐÃ SỬA**; `nhieu_buoi.json` chạy lại sau sửa |
| 5 | chặn (đo sai) | do_danh_gia.py | `chay_du_lieu_co_san` | 3/5 bộ có sẵn là NHIỀU BUỔI (bo_can_bang 6, bo_kich_tran 3, DQT_800 4) nhưng bị chạy gộp thành MỘT buổi qua `run_rbda` → số «chưa xếp», «lấp đầy» sai | bo_can_bang: 15 chưa xếp / 32 % lấp đầy (gộp) so với từng buổi 94–114 chưa xếp / 100 % | chạy qua `run_rbda_nhieu_buoi`, số liệu theo buổi + theo học sinh | đã tái hiện (in_bang bản đầu) | **ĐÃ SỬA** + test `test_bo_co_san_nhieu_buoi_khop_run_pipeline_that` so TỪNG dòng với `run_pipeline` thật (seed 42); `bo_co_san.json` chạy lại |
| 6 | nên sửa | do_danh_gia.py | `phan_thoi_gian` | gọi `run_pipeline(seed=1+lan)` ba lần: bốc thăm đã khoá sau lần đầu → `hat_giong_da_khoa` (bất biến 3 hoạt động đúng; lỗi ở bộ đo) | lần chạy đầy đủ đầu tiên sập ở phần thời gian | dùng cùng seed | đã tái hiện | **ĐÃ SỬA**; `thoi_gian.json` chạy lại riêng một mình |
| 7 | nên sửa | do_danh_gia.py, do_tinh_nang.py | `do_cau_hinh`, `do_luoi_2x2` | gộp theo khoá của lần chạy ĐẦU → nhóm vắng mặt ở một lần chạy (không em nào ở Tầng 2 khi α = 0,9) gây `KeyError` (tính chung: trung bình chia cho cả số lần có và không có) | `do_tinh_nang.py` sập ở 800 × 20, α = 0,9 | hợp khoá, trung bình CHỈ trên giá trị có mặt (`hop_khoa`, `tb_co`) | đã tái hiện (log chạy đầu) | **ĐÃ SỬA** + 2 test |
| 8 | nên sửa | style.css, js/03_ket_qua.js | `loadChiSoPhanBo` | ô chỉ số dùng lớp `.kpi-o` — test `test_o_tom_tat_khop_ham_doc` đếm MỌI `.kpi-o` trên trang → đỏ (3 ô thành 7 ô) | chạy `test_giao_dien_tom_tat_ket_qua.py` | lớp riêng `.dg1-o` | đã tái hiện | **ĐÃ SỬA** |
| 9 | nhỏ | i18n.js | `dg1_du_tru` | chữ «dự trữ» ở giao diện trái quy ước T3-L3 (`test_nguon_chu_khong_con_du_tru_o_i18n_va_index`) | chạy 32 tệp test giao diện thẻ Kết quả | «Suất ưu tiên đã dùng» / «Priority seats used» | đã tái hiện | **ĐÃ SỬA** (mục Excel giữ «dự trữ» như trang Thống kê sẵn có) |
| 4 | nhỏ | do_danh_gia.py | `tong_hop` | KTC t có thể vượt [0, 100] (hoặc âm) với phần trăm khi n nhỏ | n = 2 (`--nhanh`) | chỉ là cách đọc; ghi trong README | đã thấy | ghi chú, không sửa |

## Chưa kiểm được
- Chưa có người độc lập xem lại (soát tự thân). Chưa chạy bộ test đầy đủ (~22 phút; CI chạy). Chưa chụp ảnh giao diện (thuộc L5).
- Chưa thử Excel mở bằng Excel thật; chỉ đọc lại bằng `openpyxl` (mục «CHỈ SỐ PHÂN BỔ» nằm cuối trang «Thống kê»).

## Chạy rộng
- 32 tệp test giao diện có mở thẻ Kết quả (`-n 2`): 331 qua, 2 đỏ — #9 (đã sửa) và `test_giai_phong_thi_hien_loi_moi_va_bam_nhan` (FA «gap1»,
  timeout 8 giây khi máy đang chạy hai lần đo nặng; chạy lại riêng: ĐẠT, và ĐẠT trên `origin/main` — nhiễu tải, không liên quan thay đổi).
- `kiem_ket_qua.py` trên JSON cuối: 356 ô cap_chan/ngoai_danh_sach = 0 cho RB-DA, đối chiếu số liệu ĐẠT.

CHECKER REPORT 1+2 NO BUGS (sau khi sửa #1–#3 và #5–#9; #4 là ghi chú; soát tự thân, chưa có người độc lập)
