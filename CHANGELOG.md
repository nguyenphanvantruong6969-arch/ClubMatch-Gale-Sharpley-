# CHANGELOG

## 2026-11-25 — DK2: cầu nối bản mẫu cổng đăng ký → Sổ nhập thật

- `dk2_so_nhap.py` (mới): JSON xuất của bản mẫu (`dinhDang` 1) → `SO_NHAP_CLB.xlsx` CHỈ qua `so_nhap.ghi_so_nhap` (chế độ huy chương, cột Lớp). Soát trước khi ghi (mã trùng, loại, chỉ tiêu, điểm sàn nguyên 0–10 theo `kiem_thuoc_tinh`, huy chương, trần 10 NV / 5 bài mỗi buổi); lỗi thì không ghi tệp. NV Tuyển chọn không thi / không điểm bị bỏ (cùng kết quả DA; tránh `fa_clb_tuyen_chon_chua_co_diem`, lỗi thấy ở CI). CLI `python dk2_so_nhap.py vao.json ra.xlsx`. Không đổi hợp đồng cột, schema, thuật toán.
- `docs/phien/DK1_BAN_MAU_V8.html` (mới, từ v7): xuất một dãy NV1…NVk theo buổi; học sinh đi từng buổi (xếp → huy chương → bài kiểm tra) rồi xem lại (D39); nhãn loại ngắn + câu giải thích xuống dòng (D40); bỏ mã biên nhận, ghi "Đã gửi lúc" (D41); tối đa 5 bài thi mỗi buổi + cảnh báo (D44); thiết kế khớp phần mềm: phông cục bộ `assets/fonts`, chỉ giao diện sáng, bo góc 6/10 px.
- Hướng dẫn `docs/huong_dan/DK2_CAU_NOI.md`. Test: `tests/test_dk2_so_nhap.py` (6), `tests/test_giao_dien_dk2_ban_mau.py` (5; dữ liệu xuất "Demo nhỏ" và "Cả trường" nhập 0 lỗi và chạy xếp được).

## 2026-11-25 — KD1-L1 fix: dò renderer an toàn (không đổi đường cũ khi không biết)

- CI Windows đỏ: test `test_do_phu_bo_sung.py` tiêm module `webview` giả (không phải package) nên `_renderer_winforms()` ném lỗi trước `create_window`. Nay `_renderer_winforms()` bắt `Exception` và trả `""` (không biết); chỉ `"mshtml"` mới chuyển sang `browser_host`. Log `renderer <tên|unknown>`.
- Test: sửa `test_nhap_winforms_loi_thi_duong_cu_khong_doi`, thêm 3 ca tái hiện test_do_phu_bo_sung với `sys.platform="win32"`. Cập nhật đếm tệp test (409) trong `CLAUDE_CHI_TIET.md`.

## 2026-11-25 — KD1-L3: hướng dẫn cài đặt + mục KD1 trong sổ đăng ký

- `HUONG_DAN_CAI_DAT.md`: ghi chú 2 dòng về `renderer mshtml` / WebView2 Runtime. `SO_DANG_KY_33_MUC.md`: dòng + mục KD1 (theo mẫu MT2, `ke_hoach_thay_doi.json` không có MT2 nên không thêm). Chỉ tài liệu.

## 2026-11-25 — KD1-L2: nhật ký khởi động có tên renderer và mốc thời gian

- `loi_khoi_dong.txt` ghi thêm `renderer <tên>` (win32) và `moc <bước> +<n> ms` tại: main bắt đầu, workspace đã mở, trước `webview.start`, trước `browser_host.serve`. Thêm `_T0`, `_ghi_moc` trong `main.py`. Không đổi hành vi nào khác.
- Test mới: 4 test trong `tests/test_kd1_khoi_dong.py` (tổng 8).

## 2026-11-25 — KD1-L1: Windows thiếu WebView2 thì dùng cửa sổ Edge/Chrome thay vì MSHTML

- Lỗi: pywebview lặng lẽ vẽ bằng MSHTML (IE11) khi máy thiếu WebView2 Runtime; IE11 không chạy nổi JS của app nên giao diện đứng hình, không bấm được.
- Sửa: `main._show_ui` (win32) đọc `webview.platforms.winforms.renderer`; nếu `mshtml` thì ghi một dòng vào `loi_khoi_dong.txt` và đi thẳng `browser_host.serve`. Thêm `_renderer_winforms`, `_DungMshtml`. Không đổi thuật toán, schema, API, CSV.
- Test mới: `tests/test_kd1_khoi_dong.py` (4, dùng module webview giả).

## 2026-11-24 — CI-WIN-PYPDF: sửa bộ test Windows trong workflow build exe (không có mã mục, Truong yêu cầu trực tiếp)

- Lỗi: run #21 của *Build Windows executable (rbda-kiosk)* đỏ ở `tests/test_cb1_pdf_trung_tinh.py::test_pdf_in_ten_truong_len_bang_dau_trang_khi_co` — `ModuleNotFoundError: No module named 'pypdf'`. Bước cài đặt của workflow này thiếu `pypdf`, trong khi `tests.yml` (job Windows) đã có.
- Sửa: thêm `"pypdf>=4,<6"` vào dòng `pip install` test của `.github/workflows/build-windows-exe.yml` (khớp `requirements-dev.txt`). Không đổi mã sản phẩm.

## 2026-11-24 — SN-COT-LA: cảnh báo cột lạ có dữ liệu khi nạp Sổ nhập (mã mục tạm, chờ Truong xác nhận)

- Trước đây cột có tiêu đề mà phần mềm không nhận ra (vd "Email", "Ghi chú", "Phòng") bị bỏ qua IM LẶNG; chỉ cột không tiêu đề mới có cảnh báo. Nay `so_nhap_canh_bao_cot_la` (sheet, số cột, tối đa 3 tên) báo ở xem trước lẫn nạp thật, cho cả sheet CLB và sheet học sinh; cột lạ trống thì không báo.
- Chỉ thêm cảnh báo: không đổi dữ liệu được đọc/ghi, không đổi CSV/schema (mặc định giữ nguyên hành vi cũ).
- Files: `so_nhap.py` (`_ten_cot_la`, khoá `cot_la`), `api_nhap.py` (`_canh_bao_so_nhap`), `i18n_errors.py` + `i18n_loi.js`. Test mới: `tests/test_so_nhap_cot_la.py`.
- Chưa làm: lượt thi ngoài nguyện vọng vẫn không vào Sổ (đã có thông báo `xuat_kq_dau_vao_thieu`); đổi cần mục riêng vì đụng hợp đồng Sổ nhập.

## 2026-11-24 — CB1-FIX3: sửa giao diện khung "Văn bản phương án xếp" sau khi xem ảnh; bỏ nhãn "Đề xuất" (Truong yêu cầu)

- Mục: CB1 (đợt sửa sau chụp ảnh). Tệp: `index.html`, `js/2x_phuong_an.js`, `js/18_cai_dat.js`, `style.css`, `i18n.js`, `api_phuong_an.py`, tests (xem dưới).
- Khung "Văn bản phương án xếp" ra khỏi mục gập "Tuỳ chỉnh thêm": nút Chốt và Xuất bản dự kiến hiện ngay. Ngân sách nút ở tab Cách xếp (`tests/test_giao_dien_ux4_l4.py`) nâng từ 9 lên 11 (thêm đúng hai nút đó); vẫn một nút vàng (`gt2ThuChay`).
- Hộp xác nhận chốt: tiêu chí hiện theo hai nhóm có tiêu đề ("Học sinh đã có điểm thi của CLB" / "chưa có") thay vì một danh sách lặp dòng (API thêm `tom_tat_luat_tang`; `tom_tat_luat` giữ nguyên); hộp trung tính thay vì đỏ; nút Chốt và Huỷ nằm dưới danh sách.
- Khoảng cách dòng gợi ý dưới ba nút và dưới ô "In hạt giống".
- PDF phương án xếp viết lại cho tự nhiên và có bố cục (Truong yêu cầu): băng đầu trang kèm nhãn bản, thẻ mục tiêu, thứ tự xét chia hai cột có số, ô lưu ý, các mốc quy trình có chấm trạng thái và giờ dạng 24/11/2026, 11:13, thẻ "Dấu xác nhận" (mã in chữ đều), các bước bốc thăm; tiêu đề hỏi-đáp ("Nhà trường ưu tiên điều gì?", "Khi một câu lạc bộ hết chỗ, ai được xét trước?"). Chỉ đổi `phuong_an_xep.dung_pdf` và câu trong `CAU`; `xuat_pdf` dùng chung không đụng; nội dung (`dung_noi_dung`) và mọi khoá giữ nguyên.
- PDF phương án xếp vừa MỘT trang (Truong, 24/11): giờ các mốc nằm cùng dòng với tên mốc, tên trường cạnh nhãn bản, "Dấu xác nhận" và "Bốc thăm có người chứng kiến" xếp hai cột, khoảng cách gọn hơn. Test: `n_trang == 1` cho cả hai bản (`tests/test_cb1_api_pdf.py`).
- PDF chỉ dùng màu trung tính (Truong, 24/11): bảng màu `_MAU` toàn mức xám, băng đầu trang đen với nhãn bản trắng. Thêm tên trường/không gian làm việc lên băng đầu trang (khoá tuỳ chọn `truong` trong `KHOA_NOI_DUNG`, tham số `truong=None` của `dung_noi_dung`; API truyền `cfg["name"]`). Test mới: `tests/test_cb1_pdf_trung_tinh.py` (bảng màu chỉ xám, mã nguồn không gọi màu lạ, tên trường).
- Gỡ bớt dòng gợi ý (Truong yêu cầu): đoạn mô tả dưới tiêu đề và dòng gợi ý dưới ô "In hạt giống" (khoá `cb1_mo_ta`, `cb1_ghi_chu_hat`, `cb1_ly_do_hat` bỏ vi và en); giữ dòng lý do khoá nút "Xuất bản chốt".
- Bỏ nhãn "Đề xuất" ở thẻ "Chia 100 điểm" (`js/18_cai_dat.js`, `style.css`, khoá `ux4_de_xuat` vi và en).
- Test: `tests/test_cb1_ui.py` (hai tiêu đề nhóm, hộp không đỏ, nút dưới danh sách), `tests/test_cb1_api_pdf.py` (`tom_tat_luat_tang`), `tests/test_giao_dien_ux1_cai_dat.py` (không còn "Đề xuất"). 66 ca liên quan đạt; `kiem_nhanh.py` 7/7. Thuật toán không đụng.

## 2026-11-24 — CB1: sửa 4 lỗi CI của vòng 1 (tests.yml run 1546)

- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: tên `workspace_settings` không để trong dấu huyền (test bản đồ mã chỉ chấp nhận tên có trong mã Python). `js/_danh_sach.txt`: thêm `2x_phuong_an` trước `08_khoi_dong` (khớp thứ tự `<script>` ở `index.html`). `index.html`: khung `#paPanel` chuyển vào mục "Tuỳ chỉnh thêm" (gập sẵn) và nút "Chốt phương án" đổi sang `btn-secondary`, để tab Cách xếp giữ đúng ngân sách điều khiển (≤ 9) và MỘT nút vàng duy nhất của `test_giao_dien_ux4_l4`. `tests/test_cb1_ui.py` mở mục đó trước. Không sửa test cũ.

## 2026-11-24 — CB1-L4: tài liệu văn bản phương án xếp

- `HUONG_DAN_SU_DUNG.md`: mục "Văn bản phương án xếp (bản dự kiến và bản chốt)". `docs/ke_hoach/CB1_KICH_BAN_DEMO.md`: kịch bản 5 bước (dữ liệu MÔ PHỎNG, hạt giống 3). `CLAUDE_CHI_TIET.md`: hàng bản đồ mã CB1 và số tệp test. Không đổi mã.

## 2026-11-24 — CB1-L3: giao diện "Văn bản phương án xếp" (tab Cách xếp của Quản lý)

- `index.html`: khung `#paPanel` (quản trị) trong mục "Tuỳ chỉnh thêm" (gập sẵn, để không vượt ngân sách điều khiển của tab Cách xếp): nút "Chốt phương án" (hộp xác nhận liệt kê mục tiêu và luật sẽ chốt; chốt lại cũng hỏi lại), "Xuất bản dự kiến", "Xuất bản chốt" (khoá kèm lý do cho tới khi đủ điều kiện), ô "In hạt giống" (tắt mặc định, chỉ bật cho bản chốt đã khoá số bốc thăm), dòng trạng thái và cảnh báo. Mới `js/2x_phuong_an.js` (nạp trước `08_khoi_dong.js`; `initPhuongAn` ở `08_khoi_dong.js`; `datTabConQl` làm mới khi mở tab Cách xếp; giáo viên không gọi API để khỏi để lại dòng "bị từ chối"). `style.css`: `.run-confirm-bar[hidden]`. `i18n.js`: khoá `cb1_*` vi + en.
- Test mới: `tests/test_cb1_ui.py` (7 ca, một Chromium, một trang dùng chung).
- Siết test rò rỉ (`test_cb1_api_pdf.py`): đặt số bốc thăm và điểm riêng từng học sinh thành giá trị lạ rồi khẳng định không có trong PDF hai bản.

## 2026-11-24 — CB1-L2: API + PDF "Văn bản phương án xếp"

- Mới `api_phuong_an.py` (`PhuongAnMixin`, nối vào `PipelineAPI`): `get_phuong_an_xep()` (chỉ đọc), `chot_phuong_an()` (MỘT hàng `workspace_settings` khoá `chot_phuong_an` = `{nguoi, vai, luc, bam_luat, muc_tieu, luat_xep}`; `luat_xep` là chuỗi `luat_xep_de_ghi(rules)` lúc chốt, thêm so với kế hoạch để so được với `run_history.luat_xep`; dòng nhật ký do cổng `phan_quyen`), `export_van_ban_phuong_an_pdf(output_path, ban, in_hat_giong)`. Bản chốt cần: đã chốt + có lần xếp chính thức + đã khoá số bốc thăm; hạt giống chỉ ở bản chốt đã khoá. Không đụng `run_history`, `match_results`, `stb_lock`, cấu hình; `doc_cau_hinh` chỉ đọc khoá `config`.
- `phuong_an_xep.dung_pdf` (PDF A4 qua `xuat_pdf`); `xuat_pdf.doan(chu)` (đoạn chữ 10,5 pt). `phan_quyen._QUAN_TRI` += 3 hàm; `i18n.js` `nkhd_*` vi+en; `i18n_errors.py` nối ở CUỐI: `cb1_ban_la`, `cb1_chua_du_dieu_kien_ban_chot`, `cb1_hat_giong_chua_khoa`, `cb1_khong_chot_duoc` (rồi `tao_i18n_js.py`).
- Test mới: `tests/test_cb1_api_pdf.py` (23 ca: rò rỉ mã/tên, hạt giống mặc định/dự kiến/chưa khoá, cảnh báo đổi sau chốt, chạy thử + chọn mục tiêu không ghi đè chốt, giáo viên bị từ chối, `run_history` không đổi, thiếu reportlab). Cập nhật 5 test đếm/liệt kê có sẵn cho khối `cb1_` và ba hàm mới (không nới lỏng): `test_mt1_api`, `test_mt1_uoc_tinh` (khối `mt_` nằm trước khối `cb1_`), `test_ws_nhan` (tiền tố `cb1_`), `test_gt3_phan_quyen` (ba hàm chỉ quản trị).

## 2026-11-24 — CB1-L1: bộ dựng nội dung "Văn bản phương án xếp" (hàm thuần)

- Mới `phuong_an_xep.py`: `bam_luat(cfg)` (SHA-256 của `{rules, muc_tieu:{id,nhom}}`, bỏ `truoc` và mọi khoá ngoài luật), `trang_thai_quy_trinh(moc)` (năm mốc Đã/Chưa kèm thời điểm), `dung_noi_dung(...)` (dict chỉ gồm khoá danh sách trắng `KHOA_NOI_DUNG`). Bản dự kiến không bao giờ có hạt giống hay dấu vân tay dữ liệu; bản chốt chỉ có hạt giống khi tick và đã khoá. Câu chữ ở `CAU = {"vi", "en"}`; luật xếp lấy từ `tieu_chi.mo_ta_tieu_chi`, bước lễ dùng `fa_bien_ban.THU_TU_LE` (import, không chép). Không đụng thuật toán, CSV, schema.
- Test mới: `tests/test_cb1_noi_dung.py` (20 ca, thuần).
## 2026-11-24 — DC1-FIX2: sửa theo báo cáo checker

- `kiem_doc_lap.py`: K0 đối chiếu cả `club_id` lẫn tên khi Sổ nhập đã điền Mã CLB (trước đây rơi sang tên, lọt `club_id` giả); lỗi đầu vào in một lần; không ghi được `--ra` → mã thoát 2.
- Test mới (+8, nay 27 trong `tests/test_dc1_kiem_doc_lap.py`): hai đột biến K0, ba test khoá riêng từng phép con của K3 (đã thử tắt từng phép: đúng một test đỏ), thiếu thư mục theo CLB → K6 FAIL mã 1, `--ra` không ghi được → 2, lỗi in một lần.
- README và `HUONG_DAN_CHAY.md` mục 10: nói rõ Mã CLB và hành vi khi thiếu tệp đi kèm (giữ FAIL, mã 1). Số tệp test 403.

## 2026-11-24 — DC1-FIX1: sửa hai test tài liệu đỏ trên CI

- `docs/giai_trinh/HUONG_DAN_CHAY.md`, `KICH_BAN_DEMO.md`: bỏ mã nội bộ K0/K7 và dấu nháy quanh tên tệp sinh ra (`test_gt3_tai_lieu.py`); `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 401 → 402 tệp test (`test_a13_12_tai_lieu.py`). Không đổi mã.

## 2026-11-24 — DC1-L4: phép kiểm K7 (tệp tổng hợp)

- `kiem_doc_lap.py`: K7 đối chiếu "Đã xếp" và "Trong đó diện dự trữ" của mục "TỪNG …" trong `_tong_hop.csv` với số đếm từ tệp chính; README và hai tài liệu giải trình đổi K0–K6 → K0–K7.
- Test mới: `test_k7_tong_hop_lech` (`tests/test_dc1_kiem_doc_lap.py`, nay 19 test; ba bộ hợp lệ đòi `8 PASS`).

## 2026-11-24 — DC1-L3: tài liệu cho script kiểm độc lập

- Mới `du_lieu_test/kiem_doc_lap/README.md`; thêm mục 10 vào `docs/giai_trinh/HUONG_DAN_CHAY.md` và bước tuỳ chọn 13b vào `docs/giai_trinh/KICH_BAN_DEMO.md`. Chỉ tài liệu; không test mới.

## 2026-11-24 — DC1-L1+L2: script kiểm độc lập đầu vào ⇄ kết quả (phạm vi B, chỉ bảo toàn)

- Mục DC1 (chưa có trong sổ đăng ký; xem "Needs Truong" ở tệp nhánh). Không đổi mã sản phẩm, không đổi hợp đồng CSV.
- Mới: `du_lieu_test/kiem_doc_lap/kiem_doc_lap.py` — chỉ dùng thư viện chuẩn + openpyxl; đọc Sổ nhập và bộ xuất CSV mặc định;
  in bảng K0–K6 (PASS/FAIL) và ghi `dau_vao_ket_qua.csv`. Mã thoát 0 / 1 (có FAIL) / 2 (nhiều buổi hoặc không đọc được).
- G2 đo trên 3 bộ: em không còn nguyện vọng nào vẫn có một dòng (chưa xếp); thứ hạng = vị trí trong danh sách nguyện vọng.
- Test mới: `tests/test_dc1_kiem_doc_lap.py` (18: 8 đột biến K0–K6, thoát 2 hai ca, cô lập import bằng ast, 3 bộ hợp lệ × 2).

## 2026-11-24 — SEC-1: sửa hai cảnh báo CodeQL "Uncontrolled data used in path expression" (browser_host.py)

- Mục: SEC-1 (Truong yêu cầu trực tiếp, không thuộc sổ 33 mục). Tệp: `browser_host.py` (`_tep_tinh`, nhánh phục vụ trang HTML trong `do_GET`), `tests/test_browser_host.py`.
- `_tep_tinh`: từ chối byte NUL; thêm rào `that.startswith(goc + os.sep)` trên đường dẫn đã `realpath` (mẫu CodeQL nhận là rào chắn) bên cạnh kiểm `commonpath` sẵn có. Trước khi `open(full)` chốt lại cùng rào. Hành vi cho đường dẫn hợp lệ không đổi; thuật toán không đụng.
- Test mới: `test_duong_dan_la_deu_tra_404_khong_loi` (NUL, gạch chéo ngược, thư mục anh em). `tests/test_browser_host.py` 41 ca đạt; `kiem_nhanh.py` 7/7.
- Còn mở: cảnh báo trên GitHub chỉ đóng sau khi bản sửa vào `main` và CodeQL quét lại.

## 2026-11-24 — SFB-L3: dọn sau các lần gộp SF/UX5/UX1F (chỉ tài liệu và hạ tầng test)

- Xoá `docs/phien/claude__great-edison-6ry675__TU_CHAY.md` và `claude__ux1-tich-hop-vao-main__TU_CHAY.md` (việc đã xong, nội dung đã ở main).
- `docs/ke_hoach/TIEN_DO.md`: các dòng SF-*, UX5B-FIX-CI, UX1F-L* còn ghi "chờ CI/chờ checker" sửa theo thực tế (đã gộp vào main, CI #1522 xanh); thêm dòng SFB. `CLAUDE_CHI_TIET.md`: đếm tệp test = 402.
- `tests_stress/b/conftest.py`: ảnh chụp mặc định ghi vào thư mục tạm (đặt `RBDA_ANH_ST_B` để lưu vào kho) nên chạy stress không còn sửa các PNG đã theo dõi.
- SFB-L4 (tiến trình PDF, mã lỗi zip riêng) là lô tuỳ chọn: BỎ, để mục riêng.

## 2026-11-24 — SFB-L2: menu UX5A không còn bị cắt ở màn hình hẹp (CSS, commit riêng để revert được)

- `style.css`: một khối `@media (max-width: 800px)` cuối tệp, gồm hai luật. (1) `.menu-khac-hop.ux5a-hop-rong` thành hộp `position: fixed` sát đáy (`left/right: 12px`, `max-height: 70vh`): sửa "Báo cáo và phiếu in ▾" (Kết quả) và "Xuất tệp khác ▾" (Chi tiết) bị cắt mép trái (x = -132 ở 390 px; -12 ở 768 px không chọn lớp). (2) `.panel:has(.menu-khac[open] > .ux5a-hop-rong):hover { transform: none; transition: none; }`: luật (1) một mình CHƯA ĐỦ — hiệu ứng nhấc 2 px khi rê chuột (`.panel:hover`) biến `.panel` thành khung chứa của `position: fixed`, nên hộp lệch (top = -127) ngay khi chuột còn ở trên panel; chỉ panel đang mở menu rộng mất hiệu ứng nhấc. Màn hình > 800 px không đổi (test khẳng định vẫn `position: absolute`, rộng ≤ 360 px). Không đổi chữ, id, i18n. CI vòng 1 (run #1549) đỏ ở `test_giao_dien_ux2_chuyen_canh.py::test_css_chuyen_canh_nam_trong_supports_...`: test đọc `style.css` từ mốc `/* UX2 — L8` đến hết tệp và cấm chữ `overflow`; khối SFB nằm cuối tệp nên lọt vào. Sửa: chuyển khối SFB lên TRƯỚC mốc UX2 — L8 (độ ưu tiên selector không phụ thuộc thứ tự), không đổi test.
- Test mới `tests/test_giao_dien_sfb_menu_hep.py` (6 ca: 390/768 × có/không ô chọn lớp, và 1280 giữ nguyên neo tuyệt đối; đỏ trước khi sửa). `test_b4_do_rong_man_hinh[390,768]` nay đạt.
- Ảnh cho Truong xem: `docs/ke_hoach/ux/anh/sfb/` (390 px Kết quả, 390 px Chi tiết, 1280 px). Dữ liệu MÔ PHỎNG.

## 2026-11-24 — SFB-L1: `tests_stress/b` chạy lại được sau UX4/UX5 (chỉ sửa test)

- Áp `docs/phien/ST_B_SUA_GIAO_DIEN_MOI.patch`: `ho_tro.py` thêm `mo_the_che_do`, `mo_menu_them`, `tab_ql_hien`, `clic_tab_ql`; `test_b1`, `test_b2_quan_ly`, `test_b4_hien_thi` theo giao diện UX4-L2/L3/L4 (menu "Thêm ▾", "Thêm tuỳ chọn", ô Buổi là ô thả xuống, nút Gán ẩn khi chưa tick). Không bỏ/skip/xfail test nào, không nới ngưỡng thời gian.
- Chạy từng tệp (DỮ LIỆU MÔ PHỎNG): 63/65 đạt; 2 test `test_b4_do_rong_man_hinh[390,768]` còn đỏ vì lỗi giao diện thật (menu UX5A tràn trái), sửa ở SFB-L2.

## 2026-11-24 — SF: gộp UX1F vào nhánh SF, CI xanh vòng 1 (tự chạy)

- Gộp `origin/claude/ux1-tich-hop-vao-main` (PR #32) để #31 và #32 merge theo thứ tự nào cũng được. Xung đột: `xuat_pdf.py`, CHANGELOG.md, đếm tệp test ở `CLAUDE_CHI_TIET.md` (nay 401).
- `xuat_pdf.py`: giữ ĐỒNG THỜI bố cục UX1F (`LE_MM`, `_chia_cot`, `_rong_toi_thieu`, `_DEM_NGANG_PT`) và tăng tốc SF-A4/A5 (ô chuỗi `_o_chuoi`, bộ nhớ đệm, `useA85 = 0` có khôi phục, `khi_xong_em`). Lỗi giữa hai bên (git không báo): ô chuỗi của SF ghi cứng chữ 9 pt / dòng cách 12 làm phiếu 40 em thành 51 trang; nay dùng `_CO_O` (8,5) và `_LEADING_O` (10,5). Đo (DỮ LIỆU MÔ PHỎNG, `SO_NHAP_FA_MAU_120HS.xlsx`, seed 3, 40 em): bản nền UX1F 40 trang, 73 590 ký tự; SF cũ 75 trang; sau gộp 40 trang, 73 590 ký tự (chữ y hệt), tệp 126 602 byte (nền 144 561, nhờ tắt ASCII85).
- Sửa test (không đổi mã giao diện): `tests/test_giao_dien_sf_b_lo2.py` (st_b_006 mở "Thêm tuỳ chọn" cho Mã CLB; st_b_004 mở `#ux5bTaoMoi`), `tests_stress/b/test_b2_quan_ly.py::_tao_hs` (cùng nếp UX5B-L3), `tests/test_sf_a_4.py` (cỡ chữ đọc từ `xuat_pdf._CO_O`).

## 2026-11-24 — SF+UX5: gộp nhánh SF vào main (sửa hai chỗ test của SF theo giao diện UX4/UX5)

- Gộp `origin/main` (đã có UX5) vào nhánh SF; xung đột chỉ ở CHANGELOG.md, TIEN_DO.md, đếm tệp test (nay 398) và style.css (giữ cả hai bên).
- `tests/test_giao_dien_sf_b_lo5.py`: mở "Thêm tuỳ chọn" (Mã CLB nằm sau nút này theo UX4-L3) và tab Cách xếp + "Tuỳ chỉnh thêm" (ba thẻ chế độ theo UX4-L4) trước khi thao tác. Chỉ đổi test, không đổi mã sản phẩm.
- `tests_stress/b/test_b2_quan_ly.py`: mở "Thêm tuỳ chọn" ở `_vao_clb`. Các test giao diện khác của `tests_stress/b/` (không nằm trong CI) còn lỗi vì viết theo giao diện cũ: xem hồ sơ nhánh.

## 2026-11-23 — SF-B9: CI Linux 6/6 (id trùng `ux1aMtCanhBao`), sửa lỗi của SF-B7

- Nguyên nhân gốc: vùng cảnh báo của SF-B7 đặt id `tienTo + "CanhBao"` trong `ux1aTaoThe`, mà thẻ mục tiêu MT1 cũng dùng `ux1aTaoThe` (tiền tố `ux1aMt`) và đã có `#ux1aMtCanhBao` (`js/19_muc_tieu.js`): hai phần tử cùng id làm `tests/test_giao_dien_mt1.py::test_che_do_huy_chuong_khoa_co_hoi_mot_dong_ly_do_va_uoc_tinh_khong_co` lỗi strict mode (chạy cục bộ tái hiện đỏ trước khi sửa). Bộ test liên quan em chạy trước khi push không có tệp này.
- Sửa: `js/18_cai_dat.js` đổi id thành `tienTo + "CanhBaoDuLieu"` (`#ux1aCanhBaoDuLieu`); test của SF-B7 đổi theo; thêm `test_st_a_001_vung_canh_bao_khong_trung_id_voi_the_muc_tieu` (không id `ux1a*` nào trùng trong trang Cài đặt) ở `tests/test_giao_dien_sf_b_lo5.py`.

## 2026-11-23 — SF-B8: test bàn phím `test_b4_chi_ban_phim_nhap_chay_xuat` (lỗi chập chờn của test) + bản hồi quy SF-B5..B7

- Nguyên nhân gốc: KHÔNG phải thứ tự focus sau ST-B-009 (Tab vẫn tới đúng `#dropZone`, `keydown` Enter chạy và `input.click()` được gọi). Chạy riêng 8 lần: 5 lần đỏ, kể cả với `index.html` nguyên bản. `expect_file_chooser` đăng ký chặn hộp chọn tệp bằng thông điệp không chờ phản hồi; nhấn Enter ngay thì đôi khi hộp chọn tệp mở trước khi chặn có hiệu lực nên sự kiện không bao giờ tới. Thêm một vòng khứ hồi `p.evaluate("0")` trước khi nhấn phím: 6/6 xanh. Thời gian chờ giữ nguyên 5000 ms.
- Phát hiện kèm (lỗi thật, nhỏ, không phải nguyên nhân của chập chờn): `<input id="fileAny">` nằm TRONG `#dropZone`, nên `input.click()` nổi bọt lên và `zone` gọi `input.click()` lần hai. `js/02_van_hanh.js` (`initCsvImportHandlers`): bỏ qua cú bấm xuất phát từ chính ô chọn tệp. Test khoá: cùng test bàn phím đếm `HTMLInputElement.prototype.click` bằng đúng 1 sau một lần Enter.
- Thêm `tests/test_giao_dien_sf_b_lo5.py` (5 ca): bản hồi quy nhỏ cho ST-B-006, ST-B-007 (CLB, học sinh), ST-A-001. Đếm lại tệp test: 388.

## 2026-11-23 — SF-B7: ST-A-001 (cảnh báo thiếu dữ liệu dưới các thẻ chế độ)

- `js/18_cai_dat.js` (`ux1aTaoThe`): thêm vùng `#ux1aCanhBao` (`role="status"`) dưới các thẻ chế độ (#ux1aChiXep, #ux1aChia100, #ux1aHuyChuong) và hàm `datCanhBao`; sau `update_workspace_config`, nếu `data.warnings` có `che_do_thieu_du_lieu` thì hiện câu của backend (`n_thieu_loai`, `n_buoi_thieu_tu_do`, `n_thieu_diem_san`, `n_huy_chuong_sai`, `che_do`), không có thì ẩn; đổi chế độ thì xoá cảnh báo cũ rồi vẽ lại theo lần lưu mới; "Hoàn tác" cũng cập nhật. `style.css`: `.ux1a-canh-bao`. Chữ từ `i18n_loi.js` của A, không có chữ mới.
- Test mới (đỏ trước): `tests_stress/b/test_b5_canh_bao_che_do.py` (thiếu dữ liệu thì có cảnh báo và hết khi đổi lại; đủ dữ liệu thì không có); bản hồi quy trong `tests/test_giao_dien_sf_b_lo5.py` (thêm ở SF-B8).

## 2026-11-23 — SF-B6: ST-B-007 (xoá CLB / học sinh đã có dữ liệu: xác nhận lần hai)

- `js/00_nen.js`: `hoiXacNhanXoaKem` / `boXoaKemBar` (thanh xác nhận `#xoaKemBar`, dùng kiểu `.run-confirm-bar`, không `confirm()` native; Esc hoặc "Huỷ" thì không gọi gì; con trỏ mặc định ở "Huỷ").
- `js/05_quan_ly.js`: khi `delete_club(id)` bị từ chối bằng `cannot_delete_club_referenced`, vẫn hiện thông báo lỗi như trước rồi hỏi lần hai; xác nhận thì gọi `delete_club(club_id, true)`. `xoaClbXong` dùng chung cho hai đường, báo số nguyện vọng bỏ, kết quả thành chưa có suất và tên tệp sao lưu (`backup_path`), làm mới dải "kết quả đã cũ" (`veXuatPanel`).
- `js/04_nhap_tai_cho.js`: tương tự cho `cannot_delete_student_matched` và `delete_student(student_id, true)` (`xoaHocSinhXong`); thanh hỏi bị gỡ khi mở học sinh khác.
- `i18n.js` (vi + en): `xoa_kem_clb_hoi`, `xoa_kem_hs_hoi`, `xoa_kem_nut`, `toast_xoa_kem_clb`, `toast_xoa_kem_hs` (không in hoa, không `{detail}`, tiếng Anh không dùng "you").
- Test mới (đỏ trước): 4 ca trong `tests_stress/b/test_b2_quan_ly.py` (CLB và học sinh: hỏi lần hai rồi xoá được; huỷ ở bước hai thì chỉ có đúng một lần gọi, dữ liệu và `run_history` nguyên; dải "kết quả cũ" bật); bản hồi quy trong `tests/test_giao_dien_sf_b_lo5.py` (thêm ở SF-B8).

## 2026-11-23 — SF-B5: ST-B-006 (chỉ tiêu CLB: báo đúng chữ ngay ở ô)

- `js/05_quan_ly.js`: bảng `UX2_LOI_CLB` thêm `club_capacity_not_integer` và `capacity_too_large` (mã backend của SF-A3) vào ô `clubFormCapacity`; bỏ kiểm phía trình duyệt `Number.isInteger(Number(capacity))` (báo sai chữ "phải lớn hơn 0" cho 1.5). Chữ lấy từ `i18n_loi.js` của A, nên không có chữ mới trong `i18n.js`.
- Test mới (đỏ trước khi sửa): `tests_stress/b/test_b2_quan_ly.py::test_b2_form_clb_chi_tieu_thap_phan_hien_dung_chu_o_o` (1.5 và số rất lớn); bản hồi quy trong `tests/test_giao_dien_sf_b_lo5.py` (thêm ở SF-B8).

## 2026-11-23 — SF-A5: PDF phiếu cả trường ≤ 30 s ở 3 000 em + báo tiến độ (ST-A-008)

- `giai_trinh.py`: bộ nhớ đệm theo CLB trong dữ liệu một buổi (`_nhan_cuoi_nho`, `_so_nhan`, `_chuan_clb_fa` nhớ kết quả; `_nguoi_nhan_cuoi`, đếm suất và quét `fa_rows` từng quét cả danh sách xếp cho MỖI nguyện vọng của MỖI em, nên chuẩn bị 3 000 phiếu tốn 4,7 s (Chia 100) / 6,8 s (Huy chương), nay 0,1 s). Kết quả không đổi: dữ liệu phiếu 3 000 em × 2 chế độ và 800 em × 2 chế độ so trước/sau bằng nhau từng trường (trừ `run_at`).
- `xuat_pdf.py` (`dung_pdf`): luồng trang chỉ nén Flate, tắt ASCII85 của reportlab trong lúc dựng (đặt `rl_config.useA85 = 0`, trả lại ngay cả khi lỗi); ~7 % nhanh hơn, tệp nhỏ hơn. `ngat_trang(khi_qua=None)` + `_tai_lieu_bao_tien_do`: gọi hàm báo sau mỗi ngắt trang.
- `phieu_giai_trinh.py` (`dung_phieu_pdf(..., khi_xong_em=None)`) + `api_xuat.py`: API mới `get_tien_do_xuat()` (chỉ đọc, KHÔNG lấy khoá ghi; mức giáo viên trong `phan_quyen.py`) trả `{dang_xuat, xong, tong, ten}`; `xong`/`tong` đếm học sinh, cộng dồn qua các lớp khi `theo_lop=True` (`ten` = lớp đang dựng). Xuất xong hoặc lỗi thì về trạng thái rảnh. Khung giao diện (B) hỏi định kỳ để hiện thanh tiến độ.
- Đo (mô phỏng, máy cloud 4 nhân, một PDF cả trường): 800 em 6,5 / 5,8 s; 3 000 em 26,3 s (Huy chương) / 24,3 s (Chia 100); trước SF-A: 68-76 s. Số trang không đổi (5 902 ở 3 000 em Chia 100; 1 578 ở 800). Chia theo lớp tuần tự không nhanh hơn một tệp (thời gian tuyến tính theo số phiếu), nên nhanh hơn nữa cần dựng song song nhiều tiến trình: chưa làm (xem tệp bàn giao).
- Test mới: `tests/test_sf_a_5.py` (9 ca). Bỏ nhánh `xfail` ST-A-008 ở `tests_stress/a/test_a4_exports_timing.py` (nay là `assert` ≤ 30 s).

## 2026-11-23 — SF-A (sửa CI 2): kiểm toàn vẹn không chờ khoá

- `api_chung.py` (`kiem_toan_ven_db`): chờ khoá 0,2 s (trước 5 s) rồi bỏ qua; CSDL đang bị khoá ngoài thì `run_pipeline` / `reset_data` vẫn báo `csdl_dang_ban` dưới 7 s (`tests/test_a13_11_stress.py` đỏ trên CI: 8-10 s).

## 2026-11-23 — SF-A (sửa CI): chữ cảnh báo mới theo luật văn phong, bản chụp chữ ws_nhan

- `i18n_errors.py`: bỏ `{detail}` thô và chữ IN HOA nhấn mạnh khỏi `csdl_hong_can_khoi_phuc`, `so_nhap_canh_bao_giu_diem`, `so_nhap_canh_bao_o_bo_qua` (`tests/test_van_phong_tu_nhien.py`). `tests/test_ws_nhan.py`: ba câu đổi chủ ý (`csv_student_id_case_conflict`, `cannot_delete_club_referenced`, `cannot_delete_student_matched`) vào `SUA_CO_Y`; bảy mã mới vào `MA_MOI_SAU_ANH_CHUP`.

## 2026-11-23 — SF-A4: PDF phiếu cả trường nhanh hơn ~1,8-2 lần (ST-A-008, một phần)

- `xuat_pdf.py`: ô bảng là chuỗi tự xuống dòng bằng `simpleSplit` (cache theo chữ + bề rộng cột; khoảng trắng gộp như `Paragraph`; ô có từ dài hơn cột vẫn dùng `Paragraph` để cắt từ) thay cho `Paragraph` mỗi ô; `Paragraph` của khối dùng chung nhớ kết quả `wrap` theo bề rộng (dựng lại `blPara` nếu `split` đã xoá).
- Đo (mô phỏng, máy cloud, phiếu cả trường một PDF): 800 em 18,8 s → 9,1 s; 3 000 em 68-76 s → 32,4 s (Chia 100) / 38,4 s (Huy chương) ở lần chạy stress cuối (lần đo đầu 40,6 s). Mục tiêu ≤ 30 s ở 3 000 em CHƯA đạt: phần còn lại là reportlab thuần Python (định dạng số, `drawString`, ghi PDF); xem "Needs Truong" trong tệp bàn giao. Số trang 800 em không đổi (1 589).
- Test mới: `tests/test_sf_a_4.py` (5 ca).

## 2026-11-23 — SF-A3: xoá có xác nhận, chỉ tiêu, đổi chế độ, biểu mẫu (ST-A-005, ST-B-007, ST-A-003, ST-B-006, ST-A-001, ST-A-007)

- `api_quan_ly.py`: `delete_student(student_id, xac_nhan_xoa_ket_qua=False)` chỉ chặn khi em có suất thật hoặc có nguyện vọng mà vẫn có dòng kết quả (em nhập nhầm không nguyện vọng xoá được); xác nhận thì sao lưu rồi xoá kèm dòng kết quả (lịch sử `run_history`/`fa_*` giữ nguyên, kết quả hiện tại thành cũ). `delete_club(club_id, xac_nhan_xoa_kem=False)`: xác nhận thì sao lưu, xoá nguyện vọng của CLB, dòng kết quả thành "chưa có suất". Mặc định chặn như cũ; thông báo `cannot_delete_*` nay nói rõ lối thoát. `create_or_update_club`: chỉ tiêu không nguyên (`club_capacity_not_integer`, thay cho "Hãy thử lại" + câu Python thô; số thực 1.5 không còn bị cắt thành 1) hoặc quá lớn (`capacity_too_large`).
- `so_nhap.py` (`TRAN_SUC_CHUA = 2**31-1`) + `api_nhap.py` (`import_clubs_csv`): chỉ tiêu vượt trần bị `so_nhap_chi_tieu_sai` ở cả xem trước lẫn nạp (trước: xem trước ổn, nạp vỡ `error_importing_clubs_csv`).
- `api_workspace.py` (`update_workspace_config`, `_canh_bao_doi_che_do`): data có thêm `warnings`; vừa bật Huy chương / Chia CLB theo loại mà dữ liệu CLB còn thiếu (Loại, CLB Tự do, điểm sàn, huy chương) thì báo `che_do_thieu_du_lieu`.
- `api_forms.py`, `api_forms_nap.py`: gọi `forms_dot.nap_mau_forms()` trước mọi `import` mô-đun của `mau_forms_thi_clb` (ST-A-007).
- `api_chung.py` (`kiem_toan_ven_db`): bỏ qua dòng vi phạm CHECK / NOT NULL của integrity_check (dữ liệu cũ, di trú cố ý không đụng) — chỉ hỏng cấu trúc mới là "hỏng" (sửa lỗi của SF-A2 làm vỡ `test_run_pipeline_reports_validation_errors`).
- `i18n_errors.py` + `i18n_loi.js`: `che_do_thieu_du_lieu`, `club_capacity_not_integer`, `capacity_too_large`; câu của hai mã `cannot_delete_*` sửa.
- Test mới: `tests/test_sf_a_3.py` (25 ca; chỉ tiêu, xoá em/CLB, đổi chế độ, biểu mẫu); các ca chỉ tiêu / xoá nằm trong `tests/test_sf_a_3.py`. Bỏ `xfail` ST-A-001, 003, 005, ST-B-006, ST-B-007.

## 2026-11-23 — SF-B2 (nốt): ST-B-009 (UI), ST-B-004 (hộp xác nhận kiosk)

- ST-B-009 (`js/14_giai_trinh.js` `moHs`, `js/16_tai_khoan.js` `window.tkMoHopTaoDau`, `i18n.js` `gt_hs_can_tai_khoan`): chưa có tài khoản thì "Chế độ học sinh" không dựng lớp phủ giả, báo và mở hộp tạo tài khoản quản trị (backend A trả `can_tao_tai_khoan`).
- ST-B-004 (`js/04_nhap_tai_cho.js`, `i18n.js` `kiosk_ma_khac_hoa_thuong`): "Nhập tại chỗ" hỏi lại khi mã chỉ khác hoa/thường với mã đã có (tìm bằng `search_students`; bấm Tạo lần hai thì tạo).
- Test cũ chỉnh theo luồng mới (cần tài khoản để vào chế độ học sinh): `test_giao_dien_gt1_hoc_sinh.py`, `_gt3_hoc_sinh.py`, `_gt4_man_hoc_sinh.py`, `_ux1_dieu_huong.py`, `_ux1b_phieu.py`; stress `test_b3_vai_tro.py` (nhánh chưa-có-tài-khoản chuyển thành khẳng định luồng mới). Test mới: 2 ca trong `test_giao_dien_sf_b_lo2.py`.

## 2026-11-23 — SF-B3 (một phần) + SF-B4: ST-B-005, 010, 012, 013

- ST-B-005 (`js/02_van_hanh.js`, `i18n.js` `so_nhap_bo_qua_tep`): thả nhiều tệp thì hàng đợi nói rõ tệp nào bị bỏ qua.
- ST-B-010 (`recovery.js`): bấm "Khôi phục" lần hai sau khi đã khôi phục xong không chạy lại (không thay câu thành công).
- ST-B-012 (`js/00_nen.js`): đổi ngôn ngữ thì đóng các thông báo đang hiện (chuỗi đã dịch sẵn, không dịch lại được).
- ST-B-013 (`style.css`, `index.html`): ≤900 px `.main` rộng bằng cột (hết co theo nội dung), `.scroll-x` thành khối chứa cho `.sr-only`, bảng CLB nằm trong `.scroll-x`.
- Chờ A: ST-A-001 (khung cảnh báo), ST-B-009, ST-B-004. Test mới: `tests/test_giao_dien_sf_b_lo4.py` (2 ca), thêm 2 ca vào `test_giao_dien_sf_b_lo2.py`; gỡ 4 xfail.

## 2026-11-23 — SF-B2 (một phần): ST-B-006, ST-B-011

- ST-B-006 (`js/05_quan_ly.js`, nút Lưu CLB): chỉ tiêu thập phân báo lỗi ngay ở ô chỉ tiêu (không gửi xuống backend); xoá dòng phản hồi cũ trước mỗi lần lưu.
- ST-B-011 (`js/075_workspace.js` `wsNhapZip`, `i18n.js` `ws_nhap_zip_loi`): nhập zip hỏng nói đúng nguyên nhân (backend vẫn trả `ws_du_lieu_sai`; chi tiết kỹ thuật giữ nguyên).
- Chờ backend của A: ST-B-009 (UI), ST-B-004 (hộp xác nhận kiosk). Test mới: `tests/test_giao_dien_sf_b_lo2.py` (2 ca); gỡ 2 xfail.

## 2026-11-23 — SF-B1: ST-B-001, ST-B-002, ST-B-008 (màn hình cũ)

- ST-B-001 (`js/09_the_xem.js`, `loadKetQuaTab`): tab Kết quả bỏ hàng của lần chạy trước ngay khi mở, hiện khung chờ nếu tải chậm.
- ST-B-002 (`js/18_cai_dat.js`, `ux1aApDungSong`): vẽ lại công tắc "Chia CLB theo loại" sau khi đổi chế độ.
- ST-B-008 (`i18n.js`, `ux1a_cau_canh_bao` vi/en): câu thanh "Việc tiếp theo" không còn hứa chặn chạy ("nên xem lại").
- Test mới: `tests/test_giao_dien_sf_b_lo1.py` (3 ca). `tests_stress/b/ho_tro.py`: `_doc_bang` bỏ qua hàng khung chờ (`.ux2-khung-hang`); gỡ 3 xfail.
## 2026-11-23 — SF-A2: an toàn (ST-A-006 CSDL hỏng, ST-B-009 khoá chế độ học sinh ở backend)

- `api_chung.py` (`kiem_toan_ven_db`): kiểm `PRAGMA integrity_check(1)` (không dùng `quick_check`: đo trên 8 ca lật byte thì 3 ca "row N missing from index" lọt quick_check). `api.py`: `PipelineAPI.__init__` từ chối mở CSDL hỏng (ném `sqlite3.DatabaseError` → `main.py` vào trang phục hồi); `run_pipeline` chặn ở Bước 00 bằng mã `csdl_hong_can_khoi_phuc` TRƯỚC sao lưu; `_backup_db` không chép trang hỏng (không đẩy bản tốt ra khỏi vòng 10 bản). `api_nhap.py` (`import_so_nhap`): cùng mã, trước mọi đọc/ghi. `recovery.py` (`_quick_check_ok`): dùng `integrity_check` để trang phục hồi không coi tệp hỏng chỉ mục là đọc được.
- `api_tai_khoan.py` (`vao_che_do_hoc_sinh`): chưa có tài khoản thì `{khoa: False, can_tao_tai_khoan: True}` (hợp đồng cũ giữ nguyên) để giao diện dẫn tới tạo tài khoản; có tài khoản thì khoá như cũ (đã khoá mọi hàm ngoài tra cứu, F5 không bỏ).
- `i18n_errors.py` + `i18n_loi.js`: mã mới `csdl_hong_can_khoi_phuc`.
- Test mới: `tests/test_sf_a_2.py` (6 ca); `tests/test_gt_tich_hop.py` thêm khẳng định `can_tao_tai_khoan`. Bỏ `xfail` ST-A-006.

## 2026-11-23 — SF-A1: nạp Sổ an toàn (ST-B-003, ST-A-004, ST-B-004 phần backend, ST-A-002)

- `so_nhap.py` (`_doc_sheet_hs`, `doc_so_nhap`): sheet học sinh báo thêm `co_cot_thi` (có cột điểm thi nào không) và `n_o_bo_qua` (ô có chữ nằm ở cột không có tiêu đề, tức không được đọc).
- `api_nhap.py` (`import_so_nhap`, `_canh_bao_so_nhap`, `xem_truoc_so_nhap`): sổ KHÔNG có cột điểm thi thì bỏ bước ghi đè ô thi/điểm — ô tick và điểm đã lưu được GIỮ, kèm cảnh báo `so_nhap_canh_bao_giu_diem`; sổ có cột mà bỏ ô thi đã lưu thì xem trước báo `so_nhap_canh_bao_mat_diem` (N); ô ở cột không tên báo `so_nhap_canh_bao_o_bo_qua`; xem trước báo mã học sinh chỉ khác mã đã có ở chữ hoa/thường (`csv_student_id_case_conflict`, câu chữ nói rõ "gần như trùng"); `import_so_nhap` sao lưu (`_backup_db`) trước khi ghi, hỏng sao lưu không chặn.
- `cau_hinh_ws.py` (`doc_cau_hinh(conn=)`), `api_workspace.py` (`_cfg_ws`): trong giao dịch chung, đọc cấu hình qua chính kết nối giao dịch, không mở kết nối thứ hai (gốc của `csdl_dang_ban` khi nạp sổ ~3 000 em, ST-A-002).
- `i18n_errors.py` + `i18n_loi.js`: ba mã cảnh báo mới, một câu sửa. `pyproject.toml`: per-file-ignores cho `tests_stress/**` (SIM115, B023, PLE2502/2515: ký tự độ rộng 0 là dữ liệu thử cố ý); bỏ import/biến thừa trong `tests_stress/a/`.
- Test mới: `tests/test_sf_a_1.py` (8 ca). Bỏ `xfail` ở ST-B-003, ST-B-004 (nhập sổ), ST-A-002, ST-A-004 trong `tests_stress/`.

## 2026-11-23 — ST2 (kế hoạch): stress test vòng 2, cố ý làm sập chương trình

- `docs/phien/ST2_GIAO_THUC.md` (kill -9, thiếu tài nguyên, fuzz chuỗi thao tác, cỡ cực lớn; fuzz HTTP, monkey test, backend chết dưới giao diện, chạy dài) và `docs/phien/SF_ST2_PROMPTS.md` (bốn prompt). Chỉ chạy sau khi SF đã gộp và CI xanh. Không đổi mã sản phẩm.

## 2026-11-23 — SF (kế hoạch): sửa toàn bộ lỗi stress test

- `docs/phien/SF_GIAO_THUC.md`: phân 21 lỗi ST-A/ST-B cho hai coder trên hai nhánh con (A: mã Python, B: giao diện), vòng lặp đỏ → xanh từng lỗi, điều kiện dừng (tests_stress 0 failed/0 xfail, CI xanh, trùng khít 3×20), kiểm chéo, một PR về nhánh mẹ. Không đổi mã sản phẩm.

## 2026-11-22 — ST (chuẩn bị thử nghiệm): sổ nhập đổi chế độ + giao thức stress test

- `du_lieu_test/tao_so_nhap_doi_che_do.py` → `du_lieu_test/SO_NHAP_DOI_CHE_DO_150HS.xlsx` (DỮ LIỆU MÔ PHỎNG, 150 em, 2 buổi × 7 CLB: 1 Tự do, 3 Giới hạn, 3 Tuyển chọn). Một sổ hợp lệ cho Chỉ xếp / Chia 100 / Huy chương và bật/tắt chia loại: huy chương 60/30/10 nằm trọn trong một quỹ (= 100). Nạp khi workspace đang ở chế độ Huy chương. Đã kiểm bằng API thật: 0 cảnh báo nhập, 8 lần đổi chế độ + 3 lần bật/tắt chia loại đều chạy được.
- `docs/phien/ST_GIAO_THUC.md`: giao thức stress test hai nhánh con (`-st-a` backend, `-st-b` giao diện), chỉ báo lỗi, không sửa mã sản phẩm. Không đổi mã sản phẩm, không thêm test vào `tests/`.

## 2026-11-24 — UX1F vào main: gộp nhánh `ux1-tich-hop` (sau UX5), sửa test theo giao diện mới

- Gộp `origin/claude/ux1-tich-hop` (UX1F-L1..L5: pypdf cho test PDF, phiếu PDF vừa một trang, giáo viên lưu PDF một em, MỘT ô Chọn lớp `#kqChonLop`) vào `main` đã có UX5. Xung đột chữ: `.github/workflows/tests.yml` (gộp cả `pytest-xdist` và `pypdf`), CHANGELOG.md, TIEN_DO.md, đếm tệp test (nay 392).
- Xung đột ngữ nghĩa với UX5A (git không báo): UX1F-L4 bỏ ô `#ux1bLop` để dùng `#kqChonLop`. Sửa test UX5A cho khớp: `tests/test_giao_dien_ux5a_l2.py` (danh sách điều khiển của khối Theo lớp), `tests/test_giao_dien_ux5a_l4.py` (bỏ `ux1bLop` khỏi danh sách id phải còn; chọn lớp bằng `#kqChonLop`).
- Hai test CÓ SẴN lỗi trên `main` (không do UX1F): `tests/test_ux1i_i3_phieu_bao_cao.py::test_giao_vien_in_phieu_lop_pdf_mot_lan_bam_sau_khi_vao` và `::test_giao_vien_bao_cao_tong_hop_pdf_mot_lan_bam`, vì UX5A-L2 gập các nút này vào nếp "Báo cáo và phiếu in". Sửa test: mở nếp (`#ux1bThemTom`) trước khi bấm. Chỉ đổi test, không đổi mã sản phẩm.

## 2026-11-23 — UX5B-FIX1 (checker vòng 1): không mất điểm im lặng khi bấm "‹ Danh sách"

- `js/06_cham_diem.js`, `index.html`, `i18n.js`: ô điểm nhớ giá trị đã lưu (`data-cu`); có điểm chưa lưu thì hiện "• Chưa lưu" (`#chuaLuuDiem`) cạnh nút Lưu điểm và nút "‹ Danh sách" bấm lần đầu chỉ cảnh báo (khoá mới `ux5b_diem_chua_luu_canh_bao`, vi + en), bấm lại trong 4 giây mới bỏ; lưu xong thì hết dấu và quay lại không hỏi. Chữ cảnh báo là chữ mới ngoài bảng duyệt (Truong cân nhắc).
- Test mới trong `tests/test_giao_dien_ux5b_l3.py` (+2).

## 2026-11-23 — UX5B-L4: test Hick + Von Restorff cả ba thẻ, vai quản trị và giáo viên; test cùng payload (MILESTONE 2)

- Chỉ test (không sửa mã sản phẩm): `tests/test_giao_dien_ux5b_l4.py` (11 ca): số ô ≤ 7 (Nhập nguyện vọng: quản trị ≤ 7, giáo viên ≤ 6, trạng thái "đã chọn một em"; Nhập điểm: danh sách ≤ 7, đang chấm ≤ 2), tối đa một nút vàng mỗi thẻ, không nút đỏ, không nút bị làm mờ thay vì ẩn, giáo viên không thấy thẻ Xếp CLB/Tạo mới/điểm quyết tâm; test từ cấm và chữ trần "i"; "cùng payload": ba lần Lưu gọi đúng `submit_test_selection`, `submit_preferences`, `submit_wharton` (giáo viên: hai lần đầu) với đúng tham số, Lưu Bước 1 không kéo theo lưu Bước 2. Cách đếm: ngoài hàng bảng, ngoài dữ liệu dạng danh sách (thẻ kết quả tìm và phân trang, hàng thứ tự nguyện vọng, lưới CLB) và nút "Sửa" của mục gập (điều hướng giữa các bước). Số đo là dữ liệu MÔ PHỎNG.

## 2026-11-23 — UX5B-L3: thẻ Nhập nguyện vọng (ba bước là ba mục gập) và Nhập điểm (Hick + Von Restorff)

- `index.html`, `js/04_nhap_tai_cho.js`, `js/06_cham_diem.js`, `js/00_nen.js`, `i18n.js`, `style.css` (khối `/* UX5B */`): D2 ba bước là ba mục gập, MỘT mục mở (nút Lưu của mục đó là nút vàng duy nhất); mục gập còn dòng "Đã lưu: …" hoặc "• Chưa lưu" + nút "Sửa"; Lưu Bước 1 thì Bước 2 tự mở, Lưu Bước 2 thì Bước 3 (nếu có) tự mở. Ba lời gọi lưu giữ riêng, tham số y như cũ.
- D3: giáo viên không thấy mục "Điểm quyết tâm" (`data-quyen="quan_tri"` trên `#fbWhartonStep`) và thấy câu mô tả cũ; quản trị thấy bản "Tìm …". D6: "Xoá hết" chỉ hiện khi đã có nguyện vọng. "Tạo {person_l} mới ▾" thành mục gập (`#ux5bTaoMoi`, giữ id ba ô và nút Tạo); `ux2DiToi` mở mọi `<details>` chứa ô cần đưa con trỏ tới. Nút "i" của khối quyết tâm đọc "Giải thích".
- Nhập điểm: dòng trạng thái `#ux5bTtDiem`, nút vàng "Chấm tiếp" ở CLB đầu tiên chưa chấm xong, D4 nút `#btnScoringQuayLai` (đang chấm một CLB thì danh sách lui đi).
- Khoá i18n mới `ux5b_*` (vi + en); đổi tại chỗ `fallback_step0_title`; ghi vào `SUA_CO_Y` của `tests/test_ws_nhan.py` (ghi chú UX5B, không nới lỏng).
- Test mới: `tests/test_giao_dien_ux5b_l3.py` (13); `tests/_mo_muc.py` (mở đúng bước trước khi thao tác). Test cũ chỉnh vì UI đổi: 15 tệp giao diện (mở đúng bước/mục gập, chờ lưới ở trạng thái `attached`), `test_giao_dien_t3_l1.py` (nút "Chấm tiếp"). Số ô (ngoài danh sách dữ liệu và nút "Sửa"): quản trị 7, giáo viên 6 (trước: 27 và 23). Số đo là dữ liệu MÔ PHỎNG.

## 2026-11-23 — UX5B-FIX-CI (sửa CI nền run #1443, commit L2 8441218)

- Nguyên nhân gốc 1: L2 đổi chữ catalog `i18n.js` (`import_panel_title`, `import_hint`, `health_panel_title`, `btn_validate`, `health_panel_hint`, `steps_panel_title`, `btn_toggle`) nhưng chữ dự phòng trong `index.html` còn bản cũ → `tests/test_t3_l1_chu_du_phong.py` đỏ (Linux 4/6, Windows 5/9). Sửa: `index.html` khớp catalog.
- Nguyên nhân gốc 2: `pipeline_desc` mới không còn chỗ giữ của ngành, nên `tests/test_ws_nhan_giao_dien.py` (2 ca) đòi câu mô tả cũ (Linux 6/6). Sửa test: kiểm tên bước `step_title_rbda` ("Xếp nhân viên vào dự án" / "Place employees in projects") để vẫn chứng minh từ của ngành lên màn hình. Không nới lỏng.

## 2026-11-23 — UX5B-L2: thẻ Xếp CLB (Hick + Von Restorff); đã nhập `origin/main` (MT2) trước

- P0: gộp `origin/main` (có MT2) vào nhánh; xung đột `CHANGELOG`, `CLAUDE_CHI_TIET`, `TIEN_DO` (giữ hai bên), `index.html`, `style.css` (giữ công tắc MT2 và thẻ UX4/UX5A). CI run #1435 xanh.
- `index.html`, `js/02_van_hanh.js`, `js/05_quan_ly.js`, `i18n.js`, `style.css` (khối `/* UX5B */`): dòng trạng thái `#ux5bTtPipeline` (nhập sổ / có tệp chờ / đã nạp N / đã xếp xong); mục gập "Tuỳ chọn khi chạy" (`#nangCao`) giờ chứa mã bốc thăm, dòng khoá bốc thăm và "Buổi sẽ xếp"; chọn một phần buổi thì dòng nhắc `#ux5bBuoiTom` hiện ngoài mục gập; danh sách cảnh báo trong `#healthChiTiet` (tự mở khi có mục nghiêm trọng). Số ô thấy được: 3 / 5 / 7 (trước 3 / 8 / 10). Chữ đổi theo bảng UX5B §2.1; nút "Chạy" và mọi `id` giữ nguyên, không đụng backend.
- Ghi chú: câu "{n} cảnh báo, {s} nghiêm trọng" đã có sẵn ở `#healthSummary`; mục gập chỉ mang nhãn "Xem chi tiết" (khoá `ux5b_xem_chi_tiet`) để không lặp hai lần.
- Test mới: `tests/test_giao_dien_ux5b_l2.py` (8), dùng `tests/_ux5b_chung.py`. Test cũ chỉnh vì UI đổi (mở `#nangCao` trước khi thao tác chip/khoá bốc thăm; nhãn "Kiểm tra lại"); `test_ws_nhan.py`: `SUA_CO_Y` ghi chú UX5B.

## 2026-11-23 — UX5B: Truong duyệt MILESTONE 1; prompt tự động L2-L4

- Chỉ tài liệu: ghi duyệt M1 (từ ngữ, D1-D6, câu hỏi mở theo mặc định) trong `docs/ke_hoach/ux/UX5B_TU_NGU.md`, hồ sơ nhánh, `TIEN_DO.md`; thêm `docs/phien/UX5B_L2_L4_AUTO_PROMPT.md` (P0 nhập main, L2-L4, checker tự động, vòng CI). Không đổi mã.

## 2026-11-22 — Sửa CI đỏ trên nhánh UX5B (run #1401): gộp bản sửa UX5A, bỏ chạy đua trong một test

- Nguyên nhân: nhánh UX5B rẽ ra từ `edf7526`, trước 16 commit sửa của UX5A (trả từ về "Chỉ tiêu" / "Suất ưu tiên", nút 44px, chữ dự phòng `index.html`, số tệp test trong tài liệu). Nền UX4 có chữ mới nhưng test đòi chữ cũ nên 7 lỗi ở Linux 1-6 và Windows 3, 5 (`test_giao_dien_ux2_nut`, `ux1_nhap_so`, `sg2_diem_quyet_tam`, `t3_l3`, `fa_quan_ly`, `ux1_tiep_theo`, `fg8_cau_chu`, `t3_l1_chu_du_phong`, `a13_12_tai_lieu`).
- Cách sửa: gộp `claude/ux5a-ket-qua-de-hieu` vào nhánh (chỉ xung đột `CHANGELOG.md`, `TIEN_DO.md`; giữ cả hai bên). Không sửa mã ngoài bản gộp.
- Lỗi riêng: `tests/test_giao_dien_a13_10_nhan.py::test_nhan_moi_en_co_mat_nhan_cu_het` chỉ chờ tiêu đề h2 đổi sang tiếng Anh, còn bảng Tổng quan vẽ lại sau khi gọi lại API nên test chụp chữ lúc bảng còn tiếng Việt (đỏ ổn định ở máy chậm/nhanh khác CI). Thêm bước chờ bảng có "By test score".

## 2026-11-22 — UX5B-L1: kiểm kê + bảng từ ngữ + bản đồ lựa chọn (Xếp CLB, Nhập nguyện vọng, Nhập điểm)

- Chỉ tài liệu: `docs/ke_hoach/ux/UX5B_TU_NGU.md` (số ô và số nút vàng đo bằng Chromium thật, vai quản trị và giáo viên; bảng từ ngữ; bản đồ lựa chọn; sáu quyết định D1–D6) và ba ảnh hiện trạng trong `docs/ke_hoach/ux/anh/ux5b/`. Chưa sửa mã. Chờ Truong duyệt (MILESTONE 1).
- Phát hiện chính: Nhập nguyện vọng có 3 nút vàng cùng một màn (27 ô; giáo viên 2 vàng, 23 ô); Xếp CLB có 2 vàng khi có tệp chờ; giáo viên thấy ô điểm quyết tâm nhưng không có nút Lưu.

## 2026-11-22 — Sửa test đỏ trên nhánh UX5A (Truong chọn B2: giữ từ cũ "Chỉ tiêu" / "Suất ưu tiên")

- Từ giao diện: trả `ux4_so_cho`, `ux4_cho_rieng`, `ux4_cho_rieng_cot`, `dc_thuong`, `dc_du_tru` và họ `du_tru_*`, `dem_suat`, `kpi_du_tru_thua`, `legend_*` về chữ cũ; bỏ 7 dòng đổi chữ tương ứng trong `tests/test_ws_nhan.py`; `index.html` đồng bộ chữ dự phòng với `i18n.js` (26 chỗ).
- Lỗi thật: nút "mở tính năng" ở khung lỗi chạy không mở tab "Cách xếp" (`wsMoTinhNangDangMo`, js/075_workspace.js); nút `tkNutMoHop` cao 36 px (nay ≥ 44 px, style.css); quy tắc `.panel:has(details.menu-khac[open])` đặt trước khối UX2-L8.
- Test cập nhật: `test_giao_dien_ux1_tiep_theo.py` (nút "Xử lý" là nút cảnh báo từ UX4), `test_giao_dien_ux4_l3.py`, `test_giao_dien_ux5a_l3.py`/`l4.py` (bỏ cấm chữ "suất"), số tệp test trong `CLAUDE_CHI_TIET.md`.
- Test cập nhật theo chữ mới của UX4/UX5A (chưa có lệnh trả chữ, Truong có thể đổi ý): `test_giao_dien_fg8_cau_chu.py` ("Một buổi chung"), `test_ux1i_i2_xp1_trong_menu.py` ("Xuất tệp khác ▾").

## 2026-11-22 — UX5A giai đoạn 2: soát tổng thể, đo lại, sửa lỗi

- Lỗi tìm khi kiểm tay bằng Chromium: menu "Báo cáo và phiếu in ▾" bị khung bên dưới đè; dòng "Chọn thêm tệp để xuất" dính sát hàng nút. Sửa trong `style.css` (`.panel:has(details.menu-khac[open])` nổi lên; margin cho `summary`).
- Hai test cũ do UX5A đổi: `test_giao_dien_xp1_xuat_pdf.py` (nhãn menu), `test_giao_dien_fa_gap5_phan_hoi.py` (câu "khó nhất" nay trong nếp "Thêm ý kiến").
- Test mới: `tests/test_giao_dien_ux5a_loi.py` (7 ca: menu không bị đè × 2 vai, menu xuất, khoảng cách, tiếng Anh × 4).
- Báo cáo: `docs/ke_hoach/BAO_CAO_SOAT_MA_UX5A.md` (số đo trước/sau, 12 test đỏ có sẵn từ UX4, điểm còn mở). `kiem_nhanh.py` 7/7.

## 2026-11-22 — UX5A-L4: thẻ Kết quả + Chi tiết cho giáo viên, bài test Hick / Von Restorff / từ cấm

- Không đổi mã sản phẩm: lô này khoá hành vi bằng test, cho cả quản trị lẫn giáo viên. Giáo viên: không thấy phần `data-quyen="quan_tri"`, không có nút chết, vẫn tới tra cứu, "Theo lớp", "Xuất theo lớp", báo cáo (≤ 2 lần bấm).
- Test mới: `tests/test_giao_dien_ux5a_l4.py` (13 ca: một nút vàng + không đỏ + ngân sách tổng mỗi thẻ × 2 vai, từ cấm × 2 thẻ × 2 vai, id còn nguyên, nút của quản trị ≤ 2 lần bấm). Banner cảnh báo không vàng.
- Không đổi backend.

## 2026-11-22 — UX5A-L3: thẻ Chi tiết và xuất tệp (đúng một nút vàng, bỏ "suất"/"Chọi", gợi ý gọn, nút theo hàng đã chọn)

- Chữ: "Tải kết quả về máy" (tiêu đề khung xuất), "Chọn thêm tệp để xuất", menu "Xuất tệp khác ▾"; "suất" → "chỗ dành riêng/chỗ thường" ở chú giải, khung "Chỗ dành riêng đã dùng", số đếm và dòng tóm tắt; "Chọi cao nhất" → "Nhiều học sinh muốn nhất"; dòng mục tiêu "Được vào CLB mình chọn đầu tiên: x%". Khoá mới `ux5a_nhom_chi_tiet`, `ux5a_xuat_canh_bao` (khoá cũ `xuat_canh_bao_diem` giữ cho thẻ Nhập tại chỗ). Bỏ đề xuất đổi "Học sinh trên mỗi chỗ" (cũ đã rõ).
- Bố cục: tiêu đề nhóm "Số liệu chi tiết" trên 7 khung gập; gợi ý huy chương chuyển vào trong menu "Xuất tệp khác"; chỉ còn một đoạn gợi ý + một dòng cảnh báo đỏ trong khung xuất; "Chạy vòng 2" và "Gửi khiếu nại" thành nút thường (D2) → đúng một nút vàng ("Xuất kết quả (Excel)").
- D4: "Xuất CSV học sinh đã chọn", "Bỏ chọn" và ô tick "Hồ sơ học sinh đã chọn" ẩn tới khi tick ít nhất một em (vẫn giữ id; `disabled` giữ nguyên).
- File: index.html, style.css, i18n.js, js/03_ket_qua.js. Không đổi backend; `kiem_nhanh.py` 7/7.
- Test mới: `tests/test_giao_dien_ux5a_l3.py` (12 ca). Test cũ sửa có chủ: `test_giao_dien_ux1_ket_qua.py` (nhãn menu), `test_ws_nhan.py` (`SUA_CO_Y`, nhãn UX5A, 11 khoá).

## 2026-11-22 — UX5A-L2: thẻ Kết quả (một nút vàng, nếp "Báo cáo và phiếu in", chữ dễ hiểu)

- "Tải bảng này (Excel)" là nút vàng duy nhất của thẻ; "Khoá máy cho học sinh tự tra cứu" (trước là vàng) thành nút thường (D1). "Gửi" ở khung phản hồi thành nút thường (D2).
- Khung "Theo lớp và báo cáo": 5 → 3 điều khiển; "Báo cáo tổng hợp", "In phiếu cả lớp", "Báo cáo tổng hợp (PDF)" vào nếp `ux1bThemMenu` (id nút giữ nguyên, 2 lần bấm).
- Chữ: `kq_desc`, `gt_tim_ph`, `ux1b_ma_tra_cuu`, `gt_che_do_hs`, `gt_buoc_3`, `ux1b_bao_cao_hint`, `ph_tieu_de`, `ph_cau_kho` đổi tại chỗ; khoá mới `ux5a_gt_mo_ta`, `ux5a_ux1b_them`, `ux5a_kq_mo_bang`, `ux5a_ph_them`. `kq_desc` giữ cụm "bảng này"/"tra cứu" (test GT4 đòi). O1: câu "khó nhất" của khung phản hồi vào nếp "Thêm ý kiến ▾".
- File: index.html, style.css, i18n.js. Không đổi backend; `kiem_nhanh.py` 7/7 (cần `git fetch origin main` để có nhánh so sánh).
- Test mới: `tests/test_giao_dien_ux5a_l2.py` (+ `tests/_ux5a_chung.py`, 9 ca: ngân sách Hick, một nút vàng, nếp báo cáo, chữ, EN). Test cũ sửa có chủ: `test_giao_dien_ux1b_vai_gv.py` (báo cáo nay 2 lần bấm), `test_giao_dien_ux1b_l5c.py` (nhãn "Mã tra cứu…").
- Đã có sẵn từ UX4, không phải của lô này: `test_giao_dien_t3_l3.py::test_chu_giao_dien_dung_chu_cua_so_nhap_khong_con_du_tru` đỏ (đòi "Chỉ tiêu" trong thẻ Quản lý); xử lý ở giai đoạn 2.

## 2026-11-22 — UX5A-L1: đo thẻ Kết quả + Chi tiết và xuất tệp, bảng từ ngữ, bản đồ lựa chọn (chưa có mã)

- Tài liệu `docs/ke_hoach/ux/UX5A_TU_NGU.md`: số điều khiển nhìn thấy hiện nay (quản trị và giáo viên, nếp đóng/mở), sáu quyết định D1–D6 kèm mặc định, bảng từ ngữ VI/EN, bản đồ lựa chọn (một nút vàng mỗi thẻ).
- Không đổi mã, không đổi backend. Chờ Truong duyệt (MILESTONE 1) trước khi làm L2.

## 2026-11-22 — UX4-L4: tab Cách xếp (một câu hỏi, "Tuỳ chỉnh thêm", "Thử cách xếp này")

- Câu hỏi MT1 thành "Khi CLB hết chỗ, ai được xét trước?" với ba thẻ "Điểm bài thi cao hơn · Bốc thăm · Dành chỗ cho một nhóm" (quyết định D1: không dựng bộ thẻ thứ hai; vẫn lưu qua `chon_muc_tieu` có Hoàn tác). Nút "Thay đổi…" ẩn (id giữ), thay bằng mục gập "Tuỳ chỉnh thêm" (`#ux1aNangCao` lại là `<details>`, chỉ chứa bảng Tiêu chí). Thẻ mặc định "Chia 100 điểm" mang nhãn "Đề xuất".
- Ba ô chọn cũ (`gt2TcPriority/TierMode/ScoreScope`) giữ nguyên giá trị gửi đi; nhãn và tiêu đề đọc dễ hiểu theo mã (`gt2TcChu` + khoá `ux4_tc_*`, không sửa `tieu_chi.py`); ô không áp dụng thì ẩn (`gt2TcAnHien`): chọn "điểm" thì ẩn cách dùng nhóm + danh sách nhóm, chọn "nhóm" thì ẩn phạm vi điểm. Lưu đi cùng ba giá trị như trước (test so payload).
- Thử cách xếp: nút vàng duy nhất "Thử cách xếp này" (tự so với lần chính thức gần nhất như trước); hai ô chọn lần chạy, So sánh/Xuất và danh sách "Dùng cách xếp này" vào mục gập "So sánh với lần khác"; ba bước hướng dẫn ẩn. Tên lần chạy "Xếp chính thức lần {id} (dd/mm/yyyy HH:mm)" / "Thử lần {id} (...)".
- Chữ tuỳ chọn: Điểm quyết tâm (giờ khoá dd/mm/yyyy, "Tự cộng cho đủ 100", "Có thi / Không thi", nút "Giải thích" thay chữ "i"), Điểm chuẩn ("Theo điểm thi / Theo điểm quyết tâm", "Chưa có ai", "Chưa cần điểm (còn n chỗ trống)"). Chưa làm ngân sách Hick cho hai khung này (tuỳ chọn).
- File: index.html, style.css, i18n.js, js/05_quan_ly.js, js/15_tieu_chi.js, js/18_cai_dat.js, js/19_muc_tieu.js. Không đổi backend; `kiem_nhanh.py` 7/7.
- Test mới: `tests/test_giao_dien_ux4_l4.py` (9 ca: ngân sách Hick, một nút vàng, ô ẩn theo lựa chọn, nhãn, payload lưu 4 tổ hợp, chữ cấm + bất biến 2, ngày giờ). Test cũ sửa có chủ đích: gt2_thu, gt2_tieu_chi, gt4_tieu_chi (mở hai mục gập; tên lần chạy; "Không dùng"), mt1 (tên thẻ, câu hỏi), ux1_cai_dat ("Đề xuất", `ux1aMoNangCao`), ux1_dieu_huong, a13_10_diem_chuan, a13_10_nhan, diem_chuan (nhãn mới, "Chưa có ai"), wharton_quan_ly ("Đã khoá từ", "Kind of points"), xoa_du_lieu; `test_ws_nhan.py` (`SUA_CO_Y`, UX4).
- Bỏ qua so với bảng L1: dòng "Với lựa chọn này:" trước dòng tác động của MT1 (nhiều test MT1 so đúng chữ); `test_a13_10_nhan::test_nhan_moi_en_...` có lúc chớp đỏ (vẽ lại bảng sau khi đổi ngôn ngữ), chạy lại thì xanh.

## 2026-11-22 — UX4-L2 + L3: thẻ Quản lý dễ hiểu (luật Hick + Von Restorff), chỉ giao diện và chữ

- L2 (cấu trúc): dải tab còn 4 mục "Danh sách CLB · Học sinh · Cách xếp · Thêm ▾"; Điểm quyết tâm*, Điểm chuẩn*, Bảng điều khiển* và "Làm lại từ đầu" nằm trong "Thêm ▾" (id và `data-ql-tab` giữ nguyên; `rbda_ql_tab_con` cũ vẫn mở đúng khung). Khung Cài đặt (thẻ MT1) và Tiêu chí/Thử chuyển vào tab Cách xếp, bỏ mục gập "Nâng cao" (`#ux1aNangCao` thành `div`). Mỗi tab con có một dòng mục đích và một dòng trạng thái (`#qlTtClb`, `#qlTtHs`, `#qlTtCachXep`, `#qlTtDuLieu`). Nút thanh "Việc tiếp theo" đổi từ vàng sang kiểu cảnh báo (`.btn-canh-bao`); "Lưu tiêu chí" và hai nút xoá điểm quyết tâm của tất cả thành nút thường (đỏ chỉ còn ở "Làm lại từ đầu").
- L3 (CLB + Học sinh): form CLB còn Tên, Số chỗ, Buổi (ô thả xuống: "Một buổi chung", các buổi đã có, "Thêm buổi mới…") và "Lưu CLB"; Mã (tự điền từ tên, không ghi đè mã đã có), Chỗ dành riêng, Nhóm gập trong "Thêm tuỳ chọn" (tự mở khi sửa CLB hoặc khi có lỗi ở các ô đó). Cột buổi có nhãn "Buổi sinh hoạt". Học sinh: nút Gán (vàng) và Xuất chỉ hiện khi đã chọn ≥ 1 em ("Đã chọn n học sinh"); "Sắp xếp" vào "Thêm tuỳ chọn". Nút ở trạng thái rỗng dẫn tới ô Tên.
- File: index.html, style.css, i18n.js, js/00_nen.js, js/03_ket_qua.js, js/05_quan_ly.js, js/09_the_xem.js, js/18_cai_dat.js, js/19_ux1b_gv.js. Không đổi backend/API/schema; `kiem_nhanh.py` 7/7 (so với nhánh gốc 7e9d673 vì máy không có `origin/main`).
- Test mới: `tests/test_giao_dien_ux4_l2.py` (7 ca), `tests/test_giao_dien_ux4_l3.py` (7 ca); trợ giúp `tab_ql` trong `tests/_trinh_duyet.py`.
- Test cũ sửa có chủ đích (cấu trúc/chữ mới, đi qua "Thêm ▾" hoặc "Thêm tuỳ chọn" hoặc tab Cách xếp): test_giao_dien_quan_ly_tab_con, ux1_dieu_huong, ux1_cai_dat, mt1, mt1_bang_loai, ux1b_l5c, gt2_thu, gt2_tieu_chi, gt4_tieu_chi, fa_gap8_dashboard, a13_8_quan_ly, a13_10_diem_chuan, a13_10_nhan, a13_12_ql_diem_chuan, a14_lop, diem_chuan, diem_quyet_tam_gon, doi_ngon_ngu, loi_chan_gon, sg9_nut_ban, t3_l0, t3_l1, t3_l2_van_hanh, ux2_chuyen_canh, ux2_loi_o, ux2_rong, ux_xuat, wharton_quan_ly, xoa_du_lieu, test_khoi_dong_backend; `test_ws_nhan.py` (`SUA_CO_Y`, chú thích UX4).
- Đã có từ trước (không do UX4): `tests/test_giao_dien_ux2_nut.py::test_moi_nut_nhin_thay_co_vung_bam_44px` đỏ ở nhánh gốc 7e9d673 (`tkNutMoHop` 216×36).
- Khác bảng từ ngữ L1: dòng trạng thái Học sinh chỉ ghi "{n} học sinh" (số "đã có nhóm" cần thêm API); thêm dòng trạng thái cho "Làm lại từ đầu".
## 2026-11-22 — MT2-CI1: vùng bấm 44 px của nút khối tài khoản ở thanh bên

- CI (PR #28, shard Linux 1/6) đỏ 5 ca `test_giao_dien_ux2_nut.py::test_moi_nut_nhin_thay_co_vung_bam_44px[*]` (`tkNutMoHop 216x36`). Nguyên nhân gốc: mã UX3 trên nhánh này (commit 91a5453, khối tài khoản thành lưới hai cột) để nút `#tkNutMoHop` cao 36 px; điểm thử cách tâm 21 px rơi vào `.sidebar-footer` (không phải nút). Không phải lỗi MT2.
- Sửa: `style.css` `.tk-thanh-ben .btn { min-height: 44px }`. Không đổi test, không đổi logic.
- Kiểm: 79 ca giao diện (ux2_nut, ux2_khung, gt3, gt4, ux1_dieu_huong, ux3_thanh_ben, mt2) đạt với Chromium thật, không bỏ qua.

## 2026-11-22 — MT2-FIX-R1-FIX: đếm lại số tệp test trong tài liệu

- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 378 → 379 tệp `test_*.py` (thêm `tests/test_mt2_r1_nap_loai.py`) để `test_ban_do_ma_so_tep_test_la_so_that` đạt. Không thêm/bớt tệp test.

## 2026-11-22 — MT2-FIX-R1: Sổ nhập / CSV nạp cột Loại khi "Chia CLB theo loại" bật

- Lỗi (checker, tái hiện): `chia_loai` bật, `fa_daa` tắt → cột Loại / Điểm sàn bị bỏ qua khi nạp (`fa_cot_bo_qua`), lần chạy sau bị chặn vì thiếu loại. Nguyên nhân: `api_nhap.py` cổng cột FA bằng `dung_fa_daa`.
- Sửa: `dung_chia_loai` thay `dung_fa_daa` ở (a) `import_clubs_csv` (đường duy nhất ghi cột CLB; Sổ nhập đi qua đó): cả bốn cột Loại, Điểm sàn, Tối thiểu, Sức chứa phòng, vì lớp loại dùng cả bốn khi chạy; (b) sheet "Giữ chỗ" khi nạp; (c) xem trước `_canh_bao_fa_xem_truoc`: chỉ kiểm loại, hồ sơ huy chương chỉ khi `fa_daa`; (d) câu nhắc "chế độ huy chương tắt" không còn bắn chỉ vì có cột Loại khi chia loại bật (cột Huy chương vẫn nhắc); (e) `api_xuat.py`: Sổ xuất mang cột loại và sheet Giữ chỗ khi chia loại bật, để nạp lại được. Việc của huy chương (chuẩn hoá Vàng/Bạc/Đồng, soát hồ sơ huy chương) vẫn chỉ theo `fa_daa`. Tắt và `fa_daa` cũ: đúng như trước. Không thêm cột (bất biến 7).
- Test mới: `tests/test_mt2_r1_nap_loai.py` (6 ca: Sổ FA mẫu 8/8 loại bằng workspace Huy chương, CSV, TẮT / fa_daa cũ giữ hành vi cũ, xem trước, xuất rồi nạp lại, chạy không còn thiếu loại).

## 2026-11-22 — MT2-L4: tài liệu "Chia CLB theo loại"

- Mục MT2 (L1 khoá `chia_loai`, L2 pipeline, L3 công tắc giao diện, L4 tài liệu). Tệp tài liệu: `HUONG_DAN_SU_DUNG.md` (mục 17 mới + mục lục), `docs/ke_hoach/SO_DANG_KY_33_MUC.md` (dòng và mục MT2), `docs/ke_hoach/CLAUDE_CHI_TIET.md` (đếm lại số tệp test: 378, để `test_ban_do_ma_so_tep_test_la_so_that` đạt). Không đổi cột Sổ nhập / CSV (bất biến 7).
- Câu nói "thẻ Cài đặt cho biết chia loại đang bật hay tắt" (mục 6 của thiết kế) KHÔNG làm: cần chữ theo trạng thái động, không phải đổi chữ nhỏ; công tắc đã có ghi chú riêng và chế độ Huy chương hiện "đang bật vì Huy chương".
- Test mới ở L4: không (chỉ sửa số đếm trong tài liệu). Mọi số đo trong tài liệu là dữ liệu MÔ PHỎNG.

## 2026-11-22 — MT2-L3 FIX 1: chữ chú thích loại "Giới hạn" ở bảng MT2 không nhắc huy chương

- Checker F5: chữ "i" của Giới hạn nói "xếp theo huy chương" dù chế độ chia loại không có huy chương. `ux1aVeSanSang` nhận `tuyChon.khoaGt` {loại: khoá chữ}; MT2 dùng `mt2_gt_GIOI_HAN` (vi + en: điểm quyết tâm nếu có, rồi bốc thăm). Khoá cũ `ux1a_ss_gt_GIOI_HAN` giữ cho chế độ Huy chương.
- Test mới: `test_chu_i_cua_gioi_han_khong_nhac_huy_chuong` (tests/test_giao_dien_mt2.py; 7 ca, chạy thật với Chromium, không bỏ qua).

## 2026-11-22 — MT2-L3: công tắc "Chia CLB theo loại" ở Quản lý › Câu lạc bộ

- Giao diện: khối `#mt2ChiaLoai` (index.html) đầu thẻ con "Câu lạc bộ": MỘT công tắc `#mt2CongTac` (mặc định TẮT), bật thì hiện bảng đặt loại `#mt2Bang` (dùng lại `ux1aVeSanSang`, thêm tuỳ chọn `giuBang` / `khoaConThieu`; lưu vẫn qua `dat_loai_clb`), tắt thì ẩn (loại vẫn nằm trong `clubs.loai`). Lưu `rules.chia_loai` qua `update_workspace_config` (chỉ quản trị); bấm đúp bị chặn; lỗi backend đưa công tắc về trạng thái thật. Chế độ Huy chương: công tắc khoá ở BẬT, bảng chỉ vẽ ở Cài đặt (không trùng id). Chữ mới `mt2_*` (vi + en, i18n.js); ghi chú nói rõ CLB Giới hạn bỏ qua điểm thi (phán quyết checker L2).
- Backend: `get_san_sang_loai` (đọc, không xét huy chương, dùng `fa_daa.kiem_loai_tu_csdl`); `get_data_health_report` chạy `kiem_loai_tu_csdl` khi chia loại bật mà không Huy chương (lỗi chặn "high" nên thanh "Việc tiếp theo" chỉ vào cảnh báo; cảnh báo "medium"); `list_clubs_admin` gửi cột loại khi `dung_chia_loai`.
- Test mới: `tests/test_mt2_l3_backend.py` (7 ca, gồm F4: cảnh báo không chặn hiện ở sức khoẻ và ở bước validate; bật→tắt→bật giữ `loai`; giáo viên bị chặn), `tests/test_giao_dien_mt2.py` (6 ca Chromium: mặc định tắt/ngân sách điều khiển, XSS tên CLB, lưu + cột Loại, bấm đúp, lỗi backend, Huy chương khoá). `kiem_nhanh` 7/7; trùng khít 60 ca.

## 2026-11-22 — MT2-L2: "Chia CLB theo loại" chạy trong pipeline, không cần huy chương

- `api.py` (`run_pipeline`): khi `dung_chia_loai` bật mà `fa_daa` tắt → kiểm loại CLB bằng `fa_daa.kiem_loai_tu_csdl` (mỗi buổi một CLB Tự do, mọi CLB có loại, Tuyển chọn có điểm sàn; lỗi chặn trước khi bốc/khoá/ghi), rồi chạy `fa_daa.chay_fa_daa` với `diem_wharton` hiệu lực: rỗng (chỉ xếp: điểm thi rồi bốc thăm) hoặc điểm quyết tâm hai quỹ (`chia_100`). Hai chốt `sanity_check_result` / `verify_stability` vẫn chạy trên đầu vào đã chuẩn bị; một giao dịch như cũ. `fa_daa` bật: đường cũ, không đổi.
- `fa_daa.chay_fa_daa(..., diem_wharton=None)` (mặc định = lấy từ huy chương, như cũ). Khoá ưu tiên không đọc hạng nguyện vọng (bất biến 2).
- Chạy thử / ước tính (`_giai_trong_bo_nho`) từ chối khi bật: mã mới `mt_thu_chua_ho_tro_loai` (cuối `i18n_errors.py`, đã sinh lại `i18n_loi.js`) — đường đó không qua lớp loại nên sẽ cho số sai.
- Đo bất biến 8 (dữ liệu MÔ PHỎNG, 30 em, 3 CLB, 12 seed × 2 chế độ): 0 cặp phá vỡ. Lý do lý thuyết: mỗi CLB dùng một thứ tự ưu tiên cố định theo từng em (điểm thi, điểm quyết tâm, bốc thăm) + chỉ tiêu, lọc điểm sàn chỉ loại cặp không hợp lệ → hàm chọn thay thế được; giữ chỗ dùng suất dự trữ mềm hai lượt.
- Test mới: `tests/test_mt2_l2_chay.py` (15 ca; gồm F1 dấu vân tay `fa_clb` khi bật, F2 `_luat_ap_dung` mang `chia_loai`). `kiem_nhanh` 7/7; trùng khít 3 bộ × 20 seed (60 ca).

## 2026-11-22 — MT2-L1: khoá luật `chia_loai` ("Chia CLB theo loại") — cấu hình + công tắc

- `rules.chia_loai` (bool, mặc định False) trong `LUAT_XEP_MAC_DINH` và `MAC_DINH_TRUONG_HOC`; kiểm bool trong `cau_hinh_ws._chuan_hoa`. Hiệu lực = `dung_chia_loai(rules)` = `chia_loai` HOẶC `fa_daa` (workspace Huy chương cũ chạy y nguyên). Không cần `wharton`.
- `_luat_de_ghi_hoac_bam` bỏ khoá khi False: chuỗi `run_history.luat_xep` và dấu vân tay của workspace cũ (kể cả `fa_daa`) giữ từng byte. Phần `fa_clb` của dấu vân tay nay theo `dung_chia_loai` (với `fa_daa` bật thì như cũ).
- `get_chia_loai` (api_quan_ly.py, quản trị) trả `{chia_loai, fa_daa, hieu_luc}` cho giao diện; `tieu_chi.py` / `api_tieu_chi.py` biết khoá mới. Thuật toán chưa đổi (L2).
- Test mới: `tests/test_mt2_l1_cau_hinh.py` (18 ca). `kiem_nhanh.py` 7/7.

## 2026-11-22 — UX3-L3: nhóm menu "Nhập tay" → "Nhập thủ công"

- `ux1a_nhom_nhap_tay` (vi) và chữ dự phòng trong index.html; bảng nhóm trong HUONG_DAN_SU_DUNG.md. Tiếng Anh giữ "Manual entry". Áp cho cả vai giáo viên và quản trị (cùng một nhãn).
- Test sửa có chủ đích: `tests/test_giao_dien_ux3_thanh_ben.py` (nhãn mới).

## 2026-11-22 — UX3-L2: sau khi xoá dữ liệu không còn hiện số liệu cũ

- Thẻ Nhập nguyện vọng vẫn hiện "Trang 1/15 · 120 học sinh" sau "Xoá toàn bộ học sinh": `.pagination-row { display:flex }` đè thuộc tính `hidden`. Thêm `.pagination-row[hidden] { display: none; }` (style.css) — áp cho cả phân trang thẻ Quản lý và điểm quyết tâm (vốn cũng không ẩn được).
- Khung "Tra cứu một học sinh" (thẻ Kết quả) vẫn giữ phiếu của em đã xoá. `noiNutXoa` (js/05_quan_ly.js) phát sự kiện `duLieuDaXoa`; js/14_giai_trinh.js nghe và bỏ phiếu đang xem, ô tìm, danh sách, danh sách lớp.
- Test mới: `tests/test_giao_dien_ux3_xoa_du_lieu.py` (2 ca, đỏ trước khi sửa).

## 2026-11-22 — UX3: thanh bên — đánh số nhóm theo nhóm đang hiện, khối tài khoản gọn

- Giáo viên không thấy nhóm "Nạp & xếp" nên menu từng bắt đầu ở "2. Nhập tay". Số nhóm nay do `capNhatNhomDieuHuong` (js/01_khung.js) điền vào `<span class="nav-nhom-so">` theo các nhóm đang hiện; chuỗi `ux1a_nhom_nap_xep/nhap_tay/ket_qua` (vi + en, i18n.js) bỏ tiền tố số. Quản trị vẫn thấy 1/2/3 như cũ.
- Khối tài khoản ở chân thanh bên (cả hai vai): dòng 1 tên + vai (cắt "…", có `title`), dòng 2 hai nút cùng cỡ (style.css `.tk-thanh-ben`, js/16_tai_khoan.js `veThanhBen`).
- Test mới: `tests/test_giao_dien_ux3_thanh_ben.py` (4 ca). Không đụng backend/thuật toán.

## 2026-11-21 — SM2-CI1: ảnh chụp chữ giao diện ghi nhận đổi chữ `import_hint` có chủ đích

- CI run 44911841737 (Linux 5/6, Windows 8/9): `tests/test_ws_nhan.py::test_moi_chuoi_giao_dien_mac_dinh_giong_het_anh_chup` đỏ vì `import_hint` (vi + en) đổi ở SM2-L2. Thêm mục `("ui", "import_hint")` vào `SUA_CO_Y` (cách các mục trước ghi chữ đổi có chủ đích); mọi chuỗi khác vẫn phải trùng ảnh chụp.

## 2026-11-21 — SM2-FIX1: từ điển cột chỉ ghi ở từ vựng trường học (checker lỗi 1)

- `so_nhap.ghi_so_nhap(day_du=True)`: bảng TỪ ĐIỂN CỘT viết bằng từ vựng trường ("1. CLB", "Mã HS", "học sinh") nên chỉ ghi khi tên sheet và tiêu đề cột là mặc định của trường; workspace nhãn riêng (vd. công ty "1. Dự án" / "2. Nhân viên") vẫn đủ cấu trúc nhưng không có từ điển, để không chỉ tới sheet / cột không có trong tệp. Sổ mẫu trường học không đổi (băm FG-2, T1a xanh).
- Test mới trong `tests/test_sm2_mot_so_mau.py`: `test_tu_dien_khong_chi_toi_sheet_khong_co_o_workspace_nhan_rieng` (đỏ khi bỏ điều kiện), `test_tu_dien_van_co_o_truong_hoc_mac_dinh`. kiem_nhanh 7/7.

## 2026-11-21 — SM2-L2: MỘT nút "Tải sổ nhập mẫu", sổ luôn đủ cấu trúc

- `so_nhap.py`: `TU_DIEN_COT` + `_ghi_tu_dien_cot(wb, tieu_de, ghi_chu, che_do_fa)` (nguồn duy nhất của từ điển cột; dòng cột thứ ba theo chế độ: FA nói Huy chương, không nói quỹ) và tham số `ghi_so_nhap(..., day_du=False)`: True thì luôn có 4 cột FA, Giờ, Địa điểm, sheet Giữ chỗ (chỉ tiêu đề) và bảng TỪ ĐIỂN CỘT. Mặc định không đổi.
- `api_xuat.tao_so_nhap_mau` truyền `day_du=True`; chữ ký giữ nguyên, `kieu="huy_chuong"` vẫn ép nhãn Huy chương. `mau_csv/tao_so_nhap.py` (`tao_mau_trong`) cũng `day_du=True` để `mau_csv/SO_NHAP_CLB.xlsx` vẫn trùng sổ phần mềm (T1a); sinh lại tệp đó. `du_lieu_test/tao_so_nhap_day_du.py` dùng lại `_ghi_tu_dien_cot` (bỏ `TU_DIEN` riêng); sinh lại `SO_NHAP_MAU_DAY_DU.xlsx` (từ điển: "em" → "học sinh", theo luật chữ của sheet Hướng dẫn).
- Giao diện: bỏ nút `btnTaiSoMauHuyChuong` (`index.html`, `js/02_van_hanh.js`); `taiSoNhapMau` luôn dùng `btnTaiSoMau` và hiện dấu ✓ UX2 (`nutDaXong`). Khoá i18n `ux1a_btn_so_mau_huy_chuong` GIỮ vì nút lời nhắc sai chế độ (`ux1bSsTaiSoMau`, js/18_cai_dat.js) còn dùng. Chữ `import_hint` (vi + en). `HUONG_DAN_SU_DUNG.md`, `mau_csv/HUONG_DAN_SO_NHAP.md`.
- Test mới: `tests/test_sm2_mot_so_mau.py` (6 ca). Test sửa có chủ đích (sổ mẫu nay có Giữ chỗ + cột FA/Giờ): `test_giao_dien_ux1_nhap_so.py` (ca "hai nút" → `test_mot_nut_so_mau_day_du_cau_truc`), `test_fg2_xem_truoc_fa.py` (băm `BAM_SO_MAU_MAC_DINH`, đọc sheet Hướng dẫn theo tên), `test_ws_so_nhap.py` (2 ca), `test_ws_so_nhap_giao_dien.py` (2 ca), `test_so_nhap.py::test_mau_trong_doc_duoc_va_dung_bo_cuc`. `CLAUDE_CHI_TIET.md` (372 tệp test). kiem_nhanh 7/7.

## 2026-11-21 — SM2-L1: chế độ FA không còn cảnh báo `wharton_chua_dung_het` giả

- `api_nhap.py` (`import_preferences_csv`, chỗ gọi `_soat_ho_so_wharton`): bỏ qua khi `dung_fa_daa(luat)`; huy chương FA soát bằng `fa_daa.kiem_ho_so_huy_chuong` / `kiem_fa_tu_csdl`. Trước: 657 cảnh báo khi nạp `SO_NHAP_MAU_DAY_DU.xlsx`, 434 với `SO_NHAP_FA_MAU_120HS.xlsx`; nay 0.
- `api_quan_ly.py` (`list_wharton_canh_bao`, thẻ Quản lý): ở FA bỏ mã `wharton_chua_dung_het`, các lỗi khác giữ nguyên. Báo cáo sức khoẻ (`api.py`) đã tách nhánh FA từ trước, không sửa.
- Test mới: `tests/test_sm2_canh_bao_fa.py` (3 ca, gồm ca hồi quy không FA vẫn cảnh báo). `CLAUDE_CHI_TIET.md` (371 tệp test). kiem_nhanh 7/7.

## 2026-11-21 — Sổ mẫu đầy đủ (dữ liệu mẫu, không đổi mã sản phẩm)

- `du_lieu_test/tao_so_nhap_day_du.py` sinh `du_lieu_test/SO_NHAP_MAU_DAY_DU.xlsx` bằng `so_nhap.ghi_so_nhap` (nguồn duy nhất của định dạng): 12 CLB, ba buổi, đủ bốn cột FA (Loại, Điểm sàn, Tối thiểu, Sức chứa phòng), Giờ, Địa điểm; 120 học sinh mô phỏng có Lớp, điểm thi (CLB Tuyển chọn), huy chương 60/30/10; sheet Giữ chỗ (3 dòng); sheet Hướng dẫn thêm bảng "Từ điển cột".
- Kiểm: nạp ở workspace bật FA rồi chạy xếp: 120/120 em có chỗ. Workspace thường: các cột FA và Giữ chỗ bị bỏ qua kèm cảnh báo; chạy bị chặn vì cột huy chương được đọc như điểm quyết tâm (giống sổ `SO_NHAP_FA_MAU_120HS.xlsx` sẵn có).
- Test mới: `tests/test_so_mau_day_du.py` (2 ca). `HUONG_DAN_SU_DUNG.md` (mục cột FA), `CLAUDE_CHI_TIET.md` (370 tệp test).

## 2026-11-21 — UX2-CI1: `<details>` mở nhẹ, KHÔNG cắt nội dung (sửa test đỏ trên CI)

- Lỗi (CI run 44887663728, shard 1/6): `test_giao_dien_ux2_nut.py::test_bam_chuot_vao_o_tick_xuat_khong_kich_nut_xuat[quan_tri|giao_vien]`: bấm chuột thật vào ô tick ngay sau khi mở mục "Nâng cao" không bật ô. Chẩn đoán: hoạt ảnh mở của L8 (`block-size` 0 → auto + `overflow: hidden` trên `::details-content`) cắt phần nội dung chưa mở tới khỏi hit-test; đo `elementFromPoint` tại tâm ô: ô chỉ trúng sau ~20 đến 36 ms. Máy CI chậm thì cú bấm đầu rơi vào khoảng đó. Đây là lỗi SẢN PHẨM (bấm ô trong ~30 ms đầu bị hụt), không chỉ lỗi test.
- Sửa ở CSS (`style.css`, khối L8): `ux2Abre` giờ chỉ mờ dần + trượt xuống 4 px, KHÔNG đổi chiều cao, KHÔNG `overflow`, bỏ `interpolate-size`; `@supports selector(::details-content)` + `no-preference`; `html.tat-hieu-ung ::details-content` vẫn tắt riêng. Ô nhập bấm được từ khung hình đầu tiên. (Chuyển cảnh `<details>` không còn "theo chiều cao" như L8 mô tả ở trên; dòng đó nay chỉ còn ý "mở nhẹ".)
- Test: `test_o_nhap_trong_details_bam_duoc_tu_khung_hinh_dau_tien_ca_khi_cpu_cham` (lấy mẫu `elementFromPoint` ngay khung hình đầu và mỗi 8 ms trong 400 ms với CPU thường và CPU bóp 6 lần qua CDP + bấm chuột thật vào ô tick NGAY sau khi mở): THẤT BẠI với CSS cũ (1/50 mẫu hụt), qua với CSS mới. Test tĩnh cập nhật: `@supports selector(::details-content)`, không có `overflow` trong khối. Test CI-1 gốc và cả hai tệp `ux2_chuyen_canh` + `ux2_nut` chạy 3 lần: 32 qua mỗi lần; 187 test liên quan qua.

## 2026-11-21 — UX2-L9: tài liệu, ảnh chụp, kiểm chứng cả mục UX2

- `HUONG_DAN_SU_DUNG.md`: mục mới "Phần mềm báo lại thế nào khi bấm, khi sai, khi chờ" (cuối §4): nút bận + chống bấm đúp, dấu ✓, lỗi ngay tại ô, bốn pha (gồm "Cảnh báo" khi sao lưu hỏng mà vẫn chạy xong), hộp rỗng có nút theo vai, khung chờ, hiệu ứng trượt, nút "Hiệu ứng" tắt mọi chuyển động. Tài liệu vận hành; không có kết luận cho báo cáo khoa học.
- `docs/ke_hoach/CLAUDE_CHI_TIET.md` (Bản đồ mã): dòng mới cho các hàm UX2 (`datNutBan`, `nutDaXong`, `goDauXong`, `baoLoiTaiO`, `xoaLoiTaiO`, `baoLoiForm`, `focusODau`, `ux2TinhPha`, `ux2VePha`, `ux2DatPha`, `veTrangThaiRong`, `ux2DiToi`, `hienKhungCho`, `ux2QuanSatBang`; bảng UX2_PHA, UX2_KHOA_HANG; sự kiện "langchange" / "ux2vai"); dòng `tests/`: 360 → 369 tệp (9 tệp UX2; `test_a13_12_tai_lieu.py` đòi số khớp thật).
- Ảnh chụp lại bằng `docs/ke_hoach/ux/chup_luong_chinh.py` (Chromium, dữ liệu MÔ PHỎNG, hạt giống 42): đủ 14 ảnh script này ghi vì cả thanh bên (hàng 44 px), nút (lớp trạng thái, vòng focus) và thẻ Xếp CLB (4 pha) đổi giao diện: `01_trang_dau`, `02_co_dl_admin`, `02_co_dl_chua_co_cho`, `02_co_dl_fallback`, `02_co_dl_others`, `02_co_dl_results`, `03_tra_cuu_HS004`, `05_sau_chon_tep`, `06_sau_nhap`, `07_sau_chay`, `08_tieu_chi`, `09_gvcn_ket_qua_lop`, `10_ws_menu`, `11_cai_dat` (`.png` trong `docs/ke_hoach/ux/anh/`). Không đụng `04_phieu.png`, `phieu_mau.pdf` và các thư mục `danh_gia_*` (ảnh của báo cáo UX1).
- Kiểm chứng: `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7; `ruff check .` sạch; toàn bộ `tests/test_giao_dien_*.py` + `tests/test_*ux2*.py` chạy một lượt: 810 qua, 0 hỏng (23 phút 13 giây); thêm các test tài liệu / i18n (`test_a13_12_tai_lieu`, `test_vi_du_huong_dan`, `test_giao_dien_tieng_viet_sach`, `test_i18n_sync`, `test_van_phong_tu_nhien`, `test_ws_nhan`): 94 qua.

## 2026-11-21 — UX2-L8: chuyển cảnh mượt (hàng mới trượt vào, `<details>` mở theo chiều cao)

- `js/00_nen.js`: `ux2QuanSatBang(dsId)` (MutationObserver trên 4 `tbody`: `resultsTableBody`, `adminStudentTableBody`, `adminClubTableBody`, `historyTableBody`; gọi ở `init()` của `08_khoi_dong.js`). Hàng dữ liệu mới → tối đa 20 hàng đầu gắn lớp `ux2-vao` (180 ms, trễ xếp chồng ≤ 19 ms nên tổng ≤ 200 ms), tự gỡ khi xong. Không gắn cho hàng khung chờ L7, không gắn từ hàng thứ 21 (bảng 800 dòng), không gắn khi tắt hiệu ứng / giảm chuyển động. Hàng bấm được ngay (không `pointer-events:none`, không chờ).
- `style.css` (`/* UX2 — L8 */`): `@keyframes ux2Vao` trong `prefers-reduced-motion: no-preference`; `<details>` mở theo chiều cao (`::details-content` + `interpolate-size`, keyframes `ux2Abre`) bọc trong `@supports (interpolate-size: allow-keywords) and selector(::details-content)` + `no-preference` → WebView2 cũ: bỏ qua hết, mở tức thì. Chỉ `.nang-cao`, `.ux1a-nang-cao`, `.wh-thao-tac`, `.mt1-chi-tiet`, `.chi-tiet-ky-thuat`; KHÔNG `.menu-khac` (hộp nút trôi tuyệt đối sẽ bị cắt). `overflow:hidden` chỉ nằm trong keyframes nên xong là trả về `visible` (vòng focus / chữ không bị cắt). `html.tat-hieu-ung ::details-content` tắt riêng vì `*::before/::after` không phủ `::details-content` (bắt được bằng test).
- fix1 (checker): chỉ hàng THẬT SỰ MỚI mới trượt vào. `ux2QuanSatBang` giữ, theo từng `tbody`, một tập khoá hàng TÍCH LUY (`UX2_KHOA_HANG`: kết quả = mã học sinh + tên CLB; học sinh quản lý = `data-student-id`; CLB quản lý = `data-club-id`; lịch sử = mã lần chạy) và chỉ gắn `ux2-vao` cho khoá chưa từng thấy. Vẽ lại cùng dữ liệu (tải lại, sắp xếp, đổi ngôn ngữ, tìm kiếm rồi bỏ lọc) → 0 hàng trượt, không nhấp nháy; thêm một CLB / học sinh → đúng hàng đó; bảng bị làm trống hẳn rồi có dữ liệu → tối đa 20 hàng đầu (tập khoá được quên khi bảng trống). Test thêm (+5, tổng 15): vẽ lại cùng dữ liệu (tải lại / sắp xếp / `setLang` / lọc / bỏ lọc) = 0; thêm 1 học sinh = đúng hàng HS9999; thêm CLB (trống → 1 → tải lại 0 → thêm = 1); `<details>` nội dung 40 dòng sau khi mở: `scrollHeight == clientHeight`, overflow `visible`; hàng 55 px có ô nhập khi vẽ lại không bị `transform`/`opacity` phủ lên. Ghi chú: hàng bảng quản lý vốn được DỰNG LẠI khi vẽ lại (focus/caret trong ô lớp mất như trước L8, không do L8) — L8 không làm tệ thêm.
- Test mới: `tests/test_giao_dien_ux2_chuyen_canh.py` (10): đúng 20 hàng / 180 ms / tổng ≤ 200 ms / không `pointer-events:none`; hàng bấm được ngay; không hàng nào trượt khi `tat-hieu-ung` và `reduce`; khung chờ L7 không bị gắn; `#xuatNangCao` mở theo chiều cao rồi trả overflow, chữ không bị cắt, focus vào nội dung được; `details` không chuyển động khi tắt hiệu ứng / giảm chuyển động; `.menu-khac` không bị hoạt ảnh; tĩnh: CSS nằm trong `@supports` + `no-preference`. Sửa test L7 (`test_khung_khong_lam_nhay_bo_cuc_120_hs`) đo `offsetTop/offsetHeight` thay `getBoundingClientRect` để không dính `transform` của hiệu ứng trượt (đổi có chủ ý, không nới lỏng). 259 test liên quan qua.
- Gộp `origin/main` (MT1) vào nhánh: xung đột chỉ ở `CHANGELOG.md` / `docs/ke_hoach/TIEN_DO.md`, giữ cả hai phía.

## 2026-11-21 — UX2-L7: khung chờ (skeleton) của bảng đang tải

- `js/00_nen.js`: `hienKhungCho(tbody, soCot, soDong, hoi, caoHang)`. Chỉ chèn khung khi tải lâu hơn 300 ms (`UX2_KHUNG_TRE_MS`) VÀ `tbody` đang trống (còn dữ liệu cũ thì để dữ liệu cũ); mỗi hàng khung là MỘT ô `colspan` toàn chiều ngang (không làm cột nào giãn ra, tiêu đề cột đứng yên như lúc bảng trống), `aria-hidden="true"`; bảng `aria-busy` true → false. `hoi.then(ket, ket)` gỡ khung cả khi thành công lẫn khi lỗi / bị từ chối (không kẹt). Gọi lần hai khi lần một chưa xong: huỷ khung cũ, chỉ còn một bộ; lần tải cũ về muộn không gỡ nhầm khung mới. Gỡ khung TRƯỚC khi người gọi vẽ dữ liệu hoặc trạng thái rỗng (L6).
- Nối vào: bảng kết quả `resultsTableBody` (`03_ket_qua.js`), học sinh quản lý `adminStudentTableBody` (hàng khung cao 55 px = hàng thật có ô nhập) và CLB quản lý `adminClubTableBody` (`05_quan_ly.js`), lịch sử chạy `historyTableBody` (`02_van_hanh.js`). `loadMatchResults` / `loadAdminStudents` giữ nguyên hành vi (chỉ tách `hoi`).
- `style.css`: `.ux2-khung` (xung sáng `ux2Khung` chỉ khi cho phép chuyển động; tĩnh khi `reduce` và `tat-hieu-ung`).
- Đo: 800 học sinh vào thẻ Quản lý → có dữ liệu ~0,4 s (không hiện khung). Cột co giãn theo dữ liệu khi dữ liệu về là hành vi cũ của bảng tự co giãn, khung không làm nó tệ hơn (đo: cột / đầu bảng khi có khung = khi giấu khung).
- Test mới: `tests/test_giao_dien_ux2_khung.py` (11): tải chậm → khung sau 300 ms rồi gỡ; tải nhanh không bao giờ chèn (MutationObserver); API bị từ chối vẫn gỡ khung; kết quả rỗng → trạng thái rỗng L6; tải lần hai chỉ một bộ khung; xung sáng tắt khi `tat-hieu-ung` / `reduce`; độ trễ 300 ms xác định; bố cục không nhảy (120 HS); 800 HS; tĩnh: bốn bảng đều nối. Không test cũ phải sửa; 217 test liên quan qua.

## 2026-11-21 — UX2-L6: trạng thái rỗng có hướng dẫn + một nút chính

- `js/00_nen.js`: `veTrangThaiRong(hop, {chu, thamSo, huongDan, nut:{nhan, quyen, tab, oId}})` (tham số là KHOÁ i18n; vẽ lại khi `langchange`), `ux2DiToi(tab, oId)` (bấm nút thẻ rồi đưa con trỏ vào ô đích). Mỗi trạng thái rỗng = câu nêu hiện trạng cũ (test cũ vẫn khớp) + hướng dẫn + tối đa MỘT nút `btn btn-primary` (hệ nút L3). Nút mang `data-quyen="quan_tri"`: `giao_vien` chỉ thấy hướng dẫn.
- Nối vào: `resultsEmptyState`, `clbEmpty` (`03_ket_qua.js`), `adminClubEmptyState` (nút → ô mã {CLB}), `adminStudentEmptyState` (nút → thẻ Nhập nguyện vọng, ô mã học sinh mới) (`05_quan_ly.js`), `scoringPersonEmpty` (`06_cham_diem.js`), `kqRong` (`09_the_xem.js`: chưa có kết quả → thẻ Xếp; chưa có CLB → thẻ Quản lý; không tìm thấy → chỉ hướng dẫn). `index.html`: bỏ `data-i18n` ở 5 hộp (nếu giữ, `applyStaticText` xoá mất nút). `scoringOverviewEmpty` chưa đổi (ngoài danh sách L6).
- `i18n.js`: `ux2_rong_*` (10 khoá, vi + en; câu không dùng gạch ngang dài, không xưng hô). `style.css`: `.ux2-rong-*`.
- Lưu ý khi dùng thử: các mục kết quả mặc định ĐÓNG (`MAC_DINH_DONG`) nên hộp rỗng trong đó chỉ thấy sau khi mở mục (hành vi cũ, không đổi).
- fix1 (lead): (1) hộp rỗng theo VAI: `cfg.gv = {chu?, huongDan}` — `giao_vien` không còn bị bảo đi tới thẻ Xếp / Quản lý (họ không thấy) mà được dặn nhờ quản trị viên, không có nút; vẽ lại cả khi đổi vai (`ganVai()` trong `16_tai_khoan.js` phát `ux2vai`) chứ không chỉ khi đổi ngôn ngữ. (2) Tên thẻ trong hướng dẫn / nhãn nút lấy từ nav (`ux2TenThe()`: `nav_pipeline`, `nav_admin`, `nav_fallback`, tham số `{the_xep}`, `{the_quan_ly}`, `{the_nhap}`) nên tiếng Anh luôn khớp thanh bên ("Run allocation"). Câu nêu hiện trạng của hộp kết quả đổi sang `ux2_rong_chu_ket_qua` ("Chưa có kết quả." / "No results yet."); câu cũ `results_empty_state` / `the_xem_chua_co_ket_qua` GIỮ NGUYÊN trong `i18n.js` vì `test_ws_nhan.py` đóng băng chuỗi mặc định (sửa chúng là đổi ảnh chụp). Test: bỏ hai `pytest.skip`, giao_vien kiểm khẳng định (hai nav-item ẩn, 0 nút, nhắc quản trị viên), đổi vai vẽ lại, tên thẻ tiếng Anh khớp nav.
- Test mới: `tests/test_giao_dien_ux2_rong.py` (11 + 2 bỏ qua theo vai): chữ + hướng dẫn + đúng một nút theo vai (quan_tri / giao_vien), nút bằng bàn phím → con trỏ vào đúng ô (`clubFormId`, `newStudentId`, `dropZone`), chấm điểm theo người, `kqRong`, đổi ngôn ngữ giữ nút, hộp không còn `data-i18n`, khoá i18n đủ hai tiếng. Không test cũ phải sửa; 224 test liên quan qua.

## 2026-11-21 — UX2-L5: 4 pha tiến trình (chỉ hiển thị)

- `index.html`: `<ol id="ux2Pha">` 4 pha (Kiểm tra / Xếp / Ghi / Xuất) + dòng ghi chú `#ux2PhaGhiChu` đặt trên `#stepper`. `js/02_van_hanh.js`: bảng `UX2_PHA` (backup, validate | stb_lottery, rbda_cascade | write_results, rollback | export; `unknown` bỏ qua có chủ ý), `ux2TinhPha(steps, ok)` (hàm thuần), `ux2VePha`, `ux2DatPha`; gọi từ `resetSteps` (chưa chạy), `danhDauDangChay` (cả 4 pha "Đang chạy…", `aria-current="step"`, `aria-busy`), `executeRun` sau khi có kết quả (suy từng pha từ `steps`), `loadPipelineTab`, và `reapplyDynamicTextForLangChange` (`07_ngon_ngu.js`).
- Luật: pha có bước `error` → "Lỗi"; khi `!ok` mọi pha sau → "Chưa tới"; lỗi không gắn bước (`unknown`, API ném lỗi, không có bước) → pha ĐANG CHẠY, không có thì pha đầu chưa xong — không im lặng; `rollback` KHÔNG BAO GIỜ làm pha Ghi thành "Xong", chỉ bật dòng "đã hoàn tác" (dùng lại câu `pipeline_rolled_back` của `i18n_errors.py`). Sao lưu hỏng nhưng vẫn chạy (`ok`) → Kiểm tra "Lỗi", các pha sau giữ "Xong"; xuất hỏng sau khi đã ghi → chỉ pha Xuất "Lỗi".
- Chỉ hiển thị: `run_pipeline` chỉ trả `steps` khi xong nên trong lúc chạy cả 4 pha cùng "đang chạy" (không phần trăm). Ô btnRun vẫn dùng chung `datNutBan` (L1), không khoá mới. Danh sách `#stepper` và T3-06 thu gọn giữ nguyên.
- `i18n.js`: `ux2_pha_nhan`, `ux2_pha_kiem_tra|xep|ghi|xuat|xong|loi|chua_den` (vi + en); chữ "Chưa chạy"/"Đang chạy…" dùng lại `step_not_run_yet`/`step_running`. `style.css`: `.ux2-pha*`, `@keyframes ux2PhaNhap` (chỉ khi cho phép chuyển động).
- fix1 (checker/lead): sao lưu hỏng nhưng lần chạy VẪN thành công (`ok`) → pha Kiểm tra hiện "Cảnh báo" (`ux2_pha_canh_bao` vi+en, lớp vàng riêng, không đỏ) và chi tiết bước sao lưu hiện ở `#ux2PhaGhiChu`; các pha sau giữ "Xong". Sao lưu hỏng mà chạy dừng ngay (`ok:false`, CSDL bị giữ) và lỗi xuất tệp khi `ok` vẫn là "Lỗi". Thêm test: ca thuần + ca Chromium, xung nhịp `animation-name: none` khi `tat-hieu-ung` và `reducedMotion: reduce`, giao_vien không thấy thẻ Vận hành (nên không có 4 pha lẫn nút Chạy — đúng `data-quyen` của nav-item).
- Test mới: `tests/test_ux2_tien_trinh.py` (3, tĩnh: bảng phủ mọi `"step"` trong `api.py`, đúng thứ tự bất biến 5) và `tests/test_giao_dien_ux2_tien_trinh.py` (5: 8 tình huống `ux2TinhPha`, đang chạy → xong + thu gọn, lỗi kiểm tra thật + hoàn tác, đổi ngôn ngữ, tắt hiệu ứng). Không test cũ phải sửa; 237 test liên quan qua.

## 2026-11-21 — UX2-L4: lỗi ngay tại ô nhập

- `js/00_nen.js`: `baoLoiTaiO(o, chu, tuyChon)`, `xoaLoiTaiO(o)`, `focusODau(dsO)`, `baoLoiForm(goc, errors, bangMaO, tuyChon)`. Ô lỗi có `aria-invalid="true"`, lớp `is-loi`, `<div.loi-o>` nối bằng `aria-describedby`; gõ chữ vào ô thì lỗi tự xoá; con trỏ về ô sai ĐẦU TIÊN (mở `<details>` đóng bọc nó); lắc `ux2Rung` 200 ms chỉ khi cho phép chuyển động (không `reduce`, không `tat-hieu-ung`). Chữ luôn qua `trErr`/`t` (không chuỗi mới); mã lỗi không có ô → `tuyChon.khac` hoặc toast, không im lặng.
- Nối vào: ô hạt giống (`02_van_hanh.js`, toast cũ giữ nguyên); form CLB (`05_quan_ly.js`: ô thiếu + bảng `UX2_LOI_CLB` mã backend → ô: `club_id_required`, `capacity_must_be_positive`, `reserve_capacity_negative`, `reserve_capacity_exceeds_capacity`, mã khác → khung phản hồi cũ); form thêm học sinh (`04_nhap_tai_cho.js`: mã/tên/lớp thiếu, `student_id_required`, mã khác → toast); ô điểm (`06_cham_diem.js`, 3 chỗ: giữ `is-invalid` + `title`, thêm `.loi-o` + focus ô đầu).
- Không gộp vào `04_nhap_tai_cho.js` phần `wh-diem` (kiểm tra sống khi gõ, đã có dòng `.wh-loi` tổng hợp): giữ nguyên hành vi.
- `style.css`: `.loi-o`, `.is-loi`, `@keyframes ux2Rung` (chỉ trong `prefers-reduced-motion: no-preference`).
- fix1 (checker): đổi ngôn ngữ lúc lỗi còn hiện → chữ theo ngôn ngữ mới, KHÔNG xoá lỗi: `baoLoiTaiO` nhận `() => chữ` (các nơi gọi truyền hàm `t(…)`/`trErr(e)`), nghe `langchange` ở `00_nen.js` vẽ lại `.loi-o` + `title`. Bảng điểm CLB bị dựng lại khi đổi ngôn ngữ (`07_ngon_ngu.js`): lỗi trên ô điểm được chụp và vẽ lại sau khi nạp (tuỳ chọn `khongRung`).
- Test mới: `tests/test_giao_dien_ux2_loi_o.py` (12 sau fix1: +form CLB/hạt giống đổi ngôn ngữ, lỗi theo mã backend, ô điểm cho cả quan_tri và giao_vien). Không test cũ phải sửa; 191 test liên quan qua; không đổi `api*.py`, `i18n_errors.py`.

## 2026-11-21 — UX2-L3: vùng bấm 44 px, một vòng focus, lớp trạng thái (CSS nút)

- `style.css` (khối `/* UX2 — L3 */`): `touch-action: manipulation` cho `button, .btn, [role=button]`; vùng bấm là `::after` trong suốt rộng tối thiểu 44 px quanh tâm nút (kích thước nhìn thấy không đổi; `::before` giữ nguyên cho × của toast, mũi tên panel). Nút chữ trần trong bảng (`td`) chỉ nới tới 34 px, trong danh sách dày (`li`, vd `.ranking-list`) tới 20 px, để hàng liền kề không đè vùng bấm nhau.
- MỘT vòng focus: `--focus-ring` đổi `#2F6FD0` → `#173F8C` (≥ 3:1 trên `--paper`, trắng VÀ `--gold`; cũ chỉ 1,7:1 trên nút vàng); gỡ bản lặp `.nut-i:focus-visible`, `.ql-tab:focus-visible`; nền tối (`.menu-khac-nen-toi`, `.nav-item`) dùng `#9CC2FF`.
- Lớp trạng thái hover 8 % / focus 10 % / nhấn 12 % (`--ux2-lop-*`) bằng `background-image` + `color-mix(currentColor)` — không đổi màu nền gốc; không có lớp khi `:disabled`. Gỡ `.btn-primary:hover{filter}` và `.btn-secondary:hover{background}` cũ (lớp mới thay).
- `i18n.js`: `applyStaticText` dọn dấu ✓ cũ (min-width/lớp `is-xong`) khi đổi ngôn ngữ. `js/00_nen.js`: `datNutBan`/`nutDaXong` đo `offsetWidth` (bỏ qua `scale` của `:active`).
- Ngoại lệ có chủ đích (báo lead): hàng thanh bên `.nav-item` (cao 40 px) và `.nav-nhom-nut` (cao 23 px) xếp sát toàn chiều rộng — không nới thành 44 px để khỏi chồng hàng / kéo dài thanh bên; test loại hai lớp này.
- fix1 (quyết định của lead): `.nav-item` `min-height: 44px` (hết ngoại lệ); `.nav-nhom-nut` `min-height: 24px`; test đòi ≥ 24 px (WCAG 2.5.8 AA) cho tiêu đề nhóm thanh bên và nút chữ trần trong `td`/`li`, riêng `.ranking-list` giữ 20 px (hàng cách ~22 px, 24 px sẽ đè hàng bên). Thanh bên cao thêm ~4 px mỗi mục.
- fix2 (checker): vùng bấm `::after` của nút hẹp có thể đè ô nhập / summary / nhãn kề bên → `:where(input, select, textarea, summary, label) { position: relative; z-index: 1 }` (các ô nằm TRÊN vùng bấm của nút); riêng nội dung `<details>` đang đóng giữ `position: static` (toạ độ ma của nó không được đè lên nút). Test: `elementFromPoint` tại tâm mọi ô nhập/summary/nhãn trên 6 thẻ × 2 vai (quan_tri, giao_vien) trả đúng ô; ô tick sát nút hẹp (dựng đúng lỗi, thất bại khi bỏ dòng CSS); bấm chuột thật vào ô tick Xuất sau khi mở "Nâng cao" không kích nút Xuất. Vùng nới của nút trùng ô kề bên thì ô thắng (test chấp nhận).
- Test mới: `tests/test_giao_dien_ux2_nut.py` (10: vùng bấm 5 thẻ, nút nhỏ, một vòng focus + tương phản, không vòng khi bấm chuột, lớp trạng thái, CSS tĩnh) + 1 test dọn ✓ khi đổi ngôn ngữ. Không test cũ phải sửa.

## 2026-11-21 — UX2-L2: dấu ✓ sau khi lưu / xuất xong

- `js/00_nen.js`: `nutDaXong(nut)` / `goDauXong(nut)` (✓ là `<span.ux2-xong aria-hidden>` ~1,2 s, min-width khoá, dọn lại cả khi đổi ngôn ngữ hay bấm bận lại); `chayNut` và `khiBan` nhận `tuyChon.xongKhi(ketQua)` (✓ chỉ khi true; API ném lỗi / `ok:false` thì không).
- Nối ✓ — nút lưu: `btnSaveClub`, `btnWhLuu` (`05_quan_ly.js`), `btnSavePersonScores`, `btnSaveScores` (`06_cham_diem.js`, khiBan). Nút xuất qua `chayXuat(…, nutXuat)` (tham số thứ 4, ✓ khi không có lỗi): `btnXuatTuyChon`, `btnXuatHsDaChon`, `btnXuatTheoLop` (`03_ket_qua.js`), `btnXuatPhanHoi`, `btnXuatDashboard`, `btnXuatKhieuNai`, `btnXuatDiemDanh` (`10_theo_doi.js`), `btnAdminXuatHs` (`05_quan_ly.js`), `btnGtXuatMa` (`14_giai_trinh.js`). Nút trong menu "Khác" và các nút lưu khác chưa nối (ngoài danh sách L2).
- `style.css`: `.ux2-xong`, `@keyframes ux2Xong` (chỉ hiện dần khi cho phép chuyển động; ✓ vẫn hiện khi tắt hiệu ứng).
- Test mới: `tests/test_giao_dien_ux2_xong.py` (6). Không test cũ phải sửa; 277 test liên quan qua.

## 2026-11-21 — UX2-L1: nút đang bận + chống bấm đúp (một hàm `datNutBan`)

- `js/00_nen.js`: hàm mới `datNutBan(nut, bat, khoaNhan)` (giữ nút con thật, khoá min-width, vòng xoay `<span.ux2-xoay>`, `aria-busy`, lớp `is-ban`); `chayNut` và `khiBan` gọi nó (nút có icon không còn mất icon).
- `js/02_van_hanh.js` (`capNhatKhoaVanHanh`): btnRun dùng `datNutBan` với nhãn mới `ux2_dang_xep` ("Đang xếp…" / "Allocating…"), bận từ lúc bấm (kể cả lúc hỏi cảnh báo chạy lại).
- `i18n.js`: khoá `ux2_dang_xep` (vi + en). `style.css`: khối `/* UX2 */` (`.ux2-xoay`, `@keyframes ux2Xoay`, tĩnh khi `reduce` và `html.tat-hieu-ung`).
- Test mới: `tests/test_giao_dien_ux2_ban.py` (5). Không test cũ phải sửa: không test nào khẳng định nhãn "Đang chạy…" của btnRun.
- Không đụng thuật toán/API/CSV/schema; `kiem_nhanh.py` 7/7 (60 ca trùng khít).
- fix1 (checker): đổi ngôn ngữ lúc nút đang bận không còn ghi đè nhãn/vòng xoay — `applyStaticText` (`i18n.js`) bỏ qua nút `__ux2Ban`, `datNutBan` nhớ khoá nhãn + nghe `langchange`, trả nhãn tĩnh theo ngôn ngữ hiện tại; thêm 1 test.
- fix2 (checker): nút có icon + con `[data-i18n]` — sau khi khôi phục nút con, `datNutBan` dịch lại các con `[data-i18n]` theo ngôn ngữ hiện tại; thêm 1 test.

## 2026-11-21 — UX2 (lập kế hoạch): phản hồi tích cực của giao diện khi tương tác

- Mục mới UX2 (Truong yêu cầu; theo dõi ở `TIEN_DO.md`, ngoài sổ 33 mục như UX1/XP1). Nhánh `claude/ux2-phan-hoi-nut`.
- `docs/phien/claude__ux2-phan-hoi-nut.md`: mục tiêu, quyết định, kế hoạch 9 lượt (L1 nút bận + chống bấm đúp → L2 dấu ✓ → L3 vùng bấm 44 px, vòng focus, lớp trạng thái → L4 lỗi tại ô → L5 thanh 4 pha → L6 trạng thái rỗng → L7 khung chờ → L8 chuyển cảnh → L9 tài liệu), tiêu chí kiểm nhận đo được.
- `docs/phien/UX2_GIAO_THUC.md`: giao thức lead / coder / checker, rủi ro, phương án lùi. Chưa đổi mã sản phẩm.

## 2026-11-21 — CI: tăng tốc bộ test Windows (ngoài sổ đăng ký, Truong yêu cầu)

- `.github/workflows/tests.yml`: Linux 4 → 6 và Windows 2 → 6 phần song song (`chia_test.py`), thêm `cache: pip` (Windows + Linux). Bước chạy lại test hỏng (`--lf`) trên Linux chỉ chạy khi phần đó thật sự có test hỏng cũ (`.github/test_hong_cu.py` mới) — trước đây pytest chạy lại CẢ PHẦN khi test hỏng cũ nằm ở phần khác (mất 8–16 phút mỗi phần).
- `.github/workflows/build-windows-exe.yml`: job test chia 6 phần song song (trước: 72 phút nối tiếp; mục tiêu cả lượt ~15–17 phút) thay vì chạy nối tiếp cả bộ; job build vẫn chờ cả 4 phần xanh. Không bỏ/giảm test nào.
- `pytest-xdist` (Truong đồng ý 2026-11-21, chỉ cho test — không vào `requirements-build.txt`): mọi phần CI chạy `-n auto` (4 nhân/máy). `chia_test.py` chia theo thời gian đo (`.github/thoi_gian_test.json`, tạo bằng `.github/do_thoi_gian_test.py`; thiếu thì ước theo kích thước); `--windows` coi 108 tệp giao diện (bị bỏ qua trên Windows) gần 0. Tệp NHẠY THỜI GIAN (117: giao diện Chromium + 4 tệp đo tốc độ có ngưỡng giây) chạy tuần tự ở bước riêng (`--tuan-tu`), vì chạy song song làm chúng hỏng giả (CI 44866898234: 5 hỏng, ngưỡng 30 s đo ra 42–67 s). Không hạ ngưỡng, không bỏ test. Số đo thời gian lấy THẬT từ CI (mỗi job in dòng `THOI_GIAN_TEP_JSON`): `.github/thoi_gian_test.json` (Linux, 359 tệp) và `.github/thoi_gian_test_windows.json` (Windows, 247 tệp). Windows 9 phần (GitHub chạy cùng lúc ~15 job; 6 Linux + 9 Windows + lint = 16). Kết quả: CI 42–75 phút → 14 phút (run 44869841085, 44871202387), mục tiêu ~10.

## 2026-11-21 — MT1-X1-L3 sửa (CI đỏ): số tệp test trong bản đồ mã

- `docs/ke_hoach/CLAUDE_CHI_TIET.md` ("Bản đồ mã", dòng `tests/`): 357 → 360 tệp `test_*.py`. Nhánh nền `claude/mt1-bang-loai-clb` đã có 359 tệp (con số cũ lỗi thời từ trước), MT1-X1 thêm `tests/test_mt1_x1_xuat_so_nhap.py` thành 360. Test `test_ban_do_ma_so_tep_test_la_so_that` không đổi.

## 2026-11-21 — MT1-X1-L3: kiểm chứng và tài liệu

- D5 (MÔ PHỎNG, so SHEET + MỌI Ô, không so byte zip): xuất Sổ nhập từ `SO_NHAP_DQT_120HS_HOP_LE.xlsx`, `SO_NHAP_MAU_120HS_3BUOI.xlsx`, `SO_NHAP_DQT_800HS_HOP_LE.xlsx` (nạp vào workspace thường) bằng mã cũ (`f809b3f`, trước L1) và mã mới: cả ba trùng khít (sheet `1. CLB`, `2. Học sinh`, `Hướng dẫn`; không cột FA, không sheet "Giữ chỗ"). `match_results` 3 bộ × 5 seed: `kiem_nhanh.py` `trung_khit` đạt (bộ giải không đụng).
- `api_xuat.py`: docstring `export_du_lieu_dau_vao` nêu cột FA, cổng sheet "Giữ chỗ", và việc không truyền `che_do_fa` (D3: có thể thành mục riêng sau). Không đổi hành vi.

## 2026-11-21 — MT1-X1-L2: Sổ nhập xuất ra mang sheet "Giữ chỗ"; khứ hồi đủ năm loại dữ liệu

- `api_xuat.py` (`export_du_lieu_dau_vao`): đọc bảng `giu_cho` (ORDER BY club_id, student_id) trong cùng khối `_ket_noi_doc()` và truyền `giu_cho=` cho `ghi_so_nhap` CHỈ KHI FA bật; FA tắt thì không có sheet (bước nạp bỏ qua sheet đó). Bảng rỗng + FA bật → sheet chỉ có tiêu đề (nạp lại = không giữ chỗ nào). `_du_lieu_so_nhap` giữ nguyên bộ trả về 4 giá trị (D4). Không đổi schema, CSV, i18n, giao diện.
- `tests/test_mt1_x1_xuat_so_nhap.py` (+3 ca, đỏ trước khi sửa): khứ hồi `loai, diem_san, so_toi_thieu, suc_chua_phong` và tập `giu_cho`; sheet "Giữ chỗ" chỉ khi FA bật và rỗng thì chỉ có tiêu đề; giữ chỗ của học sinh không có nguyện vọng vẫn khứ hồi.

## 2026-11-21 — MT1-X1-L1: Sổ nhập xuất ra mang cột FA của CLB (Loại, Điểm sàn, Tối thiểu, Sức chứa phòng)

- `api_xuat.py` (`_du_lieu_so_nhap`): thêm bốn khoá `so_nhap.KHOA_FA` vào từng CLB CHỈ KHI chế độ FA bật HOẶC có CLB đã khai một trong bốn cột; không thì không thêm khoá nào, nên Sổ nhập chế độ thường y như cũ (bất biến 1, 7). Không đổi schema, cột CSV, i18n, giao diện.
- `tests/test_mt1_dong_bo_loai_clb.py`: bỏ `xfail(strict=True)` của `test_xuat_so_nhap_mang_loai_va_diem_san_hien_tai` (đỏ trước khi sửa, xanh sau).
- `tests/test_mt1_x1_xuat_so_nhap.py` (mới): chế độ thường không thêm cột và mọi ô mọi sheet bằng đường cũ; FA bật + loại NULL → cột có, ô trống, nạp lại ra NULL; FA tắt nhưng một CLB có loại → cột có, khứ hồi vào CSDL FA bật giữ nguyên (nạp vào CSDL FA tắt thì bước nạp bỏ qua cột Loại, hành vi có sẵn).
- Ghi chú D3: xuất không truyền `che_do_fa=True` (sẽ đổi tên cột huy chương và Hướng dẫn); có thể là mục riêng sau. Còn lại: L2 (sheet "Giữ chỗ").

## 2026-11-21 — MT1 (gom): kiểm đồng bộ loại CLB / điểm sàn (giao diện ↔ CSDL ↔ lần chạy ↔ Excel)

- `tests/test_mt1_dong_bo_loai_clb.py` (mới, chỉ backend): (1) `dat_loai_clb` ghi vào CSDL, bảng Quản lý (`list_clubs_admin`), `get_san_sang_huy_chuong` và lần chạy đều đọc đúng giá trị vừa đặt (thiếu loại thì lần chạy bị chặn); (2) nạp lại sổ CÓ cột Loại / Điểm sàn ghi đè giá trị đặt tay; (3) ô Loại để trống xoá về NULL; (4) sổ KHÔNG có các cột đó giữ nguyên giá trị đã đặt.
- Lỗ hổng ĐÃ ĐO, chưa sửa (ghi bằng `xfail(strict=True)`): `export_du_lieu_dau_vao` (`_du_lieu_so_nhap` trong `api_xuat.py`) không chọn `loai` / `diem_san`, nên Sổ nhập xuất ra thiếu cột Loại, Điểm sàn; nạp vào CSDL trống thì mất loại, trái với lời hứa "dựng lại y nguyên" trong docstring. Cần mục riêng để sửa (đụng hợp đồng cột của Sổ nhập, bất biến 7).
- Đã chạy: 196 ca liên quan đạt, 1 xfail có chủ ý; `ruff` sạch.

## 2026-11-21 — MT1 (gom): chữ "i" nhỏ giải thích mục đích từng loại CLB

- `js/18_cai_dat.js`, `i18n.js` (vi + en), `style.css`: thay ba dòng giải thích luôn hiện bằng hàng "Các loại: Tự do (i) Giới hạn (i) Tuyển chọn (i)"; đưa chuột vào chữ "i" (hoặc focus bàn phím / chạm) thì hiện mục đích của loại đó. Chữ có trong DOM (`aria-label` + `role="tooltip"`) nên trình đọc màn hình đọc được. Nội dung bám đúng `fa_daa.py` / `uu_tien_wharton` (Tự do không từ chối ai và là chỗ xếp cho em chưa trúng; Giới hạn bỏ điểm thi, xếp theo huy chương rồi bốc thăm; Tuyển chọn lọc điểm sàn rồi xếp theo điểm thi).
- `tests/test_giao_dien_mt1_bang_loai.py`: ca `test_chu_i_nho_hien_muc_dich_tung_loai_khi_dua_chuot_hoac_focus` (đỏ trước khi dựng). 40 ca liên quan đạt, `ruff` sạch, `soat-ma` kiem_nhanh 7/7.

## 2026-11-21 — MT1 (gom): khối "Để dùng Huy chương" ở Cài đặt dựng lại thành BẢNG đặt loại CLB

- `js/18_cai_dat.js` (`ux1aVeSanSang`): mỗi CLB một dòng, ba nút Tự do / Giới hạn / Tuyển chọn có trạng thái chọn (`aria-pressed`), điểm sàn của Tuyển chọn nhập ngay tại dòng, nhóm theo buổi kèm dấu "Đã có / Cần ít nhất một CLB Tự do", bộ đếm "Đã chọn loại: x/y", ba câu giải thích loại; bỏ ô chọn xổ xuống (trùng với nút Tự do). Sau mỗi lần lưu vẽ lại từ dữ liệu đã lưu và trả tiêu điểm về ô vừa bấm. Vẫn lưu qua `dat_loai_clb`; không đổi backend, CSV hay schema.
- `i18n.js` (vi + en): `ux1a_ss_con_thieu` đổi chữ; thêm `ux1a_ss_dem`, `ux1a_ss_gt_*`, `ux1a_ss_buoi_*`; bỏ `ux1a_ss_chon_tu_do`, `ux1a_ss_thieu_tu_do`. `style.css`: `.ux1a-ss-*`.
- Tests: `tests/test_giao_dien_mt1_bang_loai.py` (mới, 6 ca; đỏ trước khi dựng); `tests/test_giao_dien_ux1_cai_dat.py` (ca cũ giả định dòng biến mất và có ô xổ xuống, cập nhật theo bảng). 66 ca liên quan đạt; `ruff` sạch. Chưa chạy cả bộ.
- Nhánh `claude/mt1-bang-loai-clb` (từ `claude/pensive-turing-s02bgi` @ 6c97791); handoff `docs/phien/claude__mt1-bang-loai-clb.md`.

## 2026-11-21 — MT1 sửa đồng bộ: đặt loại CLB tại chỗ làm tươi bảng CLB và thanh "Việc tiếp theo"

- `js/18_cai_dat.js` (`luu` trong `ux1aVeSanSang`, dùng cho nút Tự do / Giới hạn / Tuyển chọn, ô điểm sàn và ô chọn CLB Tự do của buổi): sau `dat_loai_clb` thành công gọi thêm `loadAdminClubs()` và `capNhatViecTiepTheo()`. Trước đây chỉ khối "còn thiếu" vẽ lại, cột "Loại" của bảng CLB cũ cho tới khi tải lại trang. Không đổi backend, không thêm đường lưu.
- `tests/test_giao_dien_mt1.py`: ca `test_dat_loai_clb_tai_cho_lam_tuoi_bang_clb_khong_can_tai_lai` (đỏ trước khi sửa vì ô "Loại" vẫn "—"; xanh sau sửa).
- Đã chạy: `test_giao_dien_mt1.py` + `test_giao_dien_ux1_cai_dat.py` 42 đạt; `ruff check .` sạch. Chưa chạy cả bộ test.

## 2026-11-21 — MT1 sửa chữ: mô tả thẻ "Theo năng lực" cho đúng thứ tự xếp thật

- `muc_tieu.py` (`BO_MUC_TIEU["nang_luc"]["cau"]`), `i18n.js` (`mt1_the_nang_luc_mt`, vi + en), `HUONG_DAN_SU_DUNG.md`: câu cũ "CLB không thi bốc thăm công bằng" sai khi đang dùng "Chia 100 điểm" / huy chương, vì `khoa_uu_tien_wharton` xét điểm quyết tâm TRƯỚC số bốc thăm (tầng 2: `(1, -w2, stb, sid)`). Câu mới: điểm thi, rồi điểm quyết tâm (nếu có), cuối cùng bốc thăm.
- Chỉ đổi chữ hiển thị; không đổi luật xếp, không đổi kết quả. Test: `tests/test_mt1_muc_tieu.py`, `tests/test_i18n_sync.py` (40 ca đạt).

## 2026-11-20 — MT1 CI-fix2: khối mục tiêu chỉ hiện khi đã có dữ liệu; bỏ phản hồi cũ về muộn

- `js/19_muc_tieu.js`: khối câu hỏi mục tiêu ẩn cho tới khi `get_muc_tieu` trả về (trước đó hiện ba thẻ còn bấm được mà chưa biết thẻ nào bị khoá — khoảng hở cho người dùng bấm nhầm, và cho kiểm tra "thẻ bị khoá" đọc quá sớm khi máy chậm); `lamMoi` bỏ phản hồi `get_muc_tieu` cũ về muộn (đếm lần hỏi, như `viecTiepTheoLanGoi`).
- `tests/test_giao_dien_mt1.py`: ca "Chia 100 điểm → Cơ hội như nhau" đợi đúng điều kiện cuối (dòng tác động có câu ghi chú) trước khi so; khẳng định giữ nguyên.
- Nguyên nhân gốc: khối hiện sớm hơn trạng thái khoá (cặp 1–2) và dòng tác động vẽ sau thông báo (cặp 3). Tái hiện cục bộ bằng chạy 12 bản song song: trước sửa 4/12 hỏng, sau sửa 0/12; cả tệp 6 bản song song 26/26.

## 2026-11-20 — MT1 CI-fix1: mã `mt_*` đăng ký ở bản chụp lỗi; thanh "Việc tiếp theo" không còn chạy đua với danh sách cảnh báo

- `tests/test_ws_nhan.py`: tiền tố `mt_` (MT1) vào danh sách tiền tố mã lỗi mới sau ảnh chụp, như `gt3_` / `xp1_`; phép so từng chữ giữ nguyên.
- `js/02_van_hanh.js` (`loadHealthReport`) + `js/17_viec_tiep_theo.js` (`capNhatViecTiepTheo` trả promise): danh sách cảnh báo chỉ hiện SAU khi thanh "Việc tiếp theo" đã có trạng thái. Nguyên nhân gốc (có sẵn từ trước, không do MT1: bản `main` cũng hỏng 3/14 lần khi máy bận): thanh còn chờ thêm hai lời gọi (`get_dashboard_status`, `get_em_chua_co_cho`) SAU khi danh sách đã hiện, nên nơi đọc (và `test_r1_canh_bao_huy_chuong…`) thấy danh sách mà `data-trang-thai` còn trống. Sau sửa: 0/14 lần hỏng ở cùng điều kiện (trước 4/14).

## 2026-11-20 — MT1 fix3 (L2 + L4): rời "Cơ hội như nhau" trả lại "Chia 100 điểm"; câu hỏi đầu chạy theo thẻ

- `cau_hinh_ws.py` (`_kiem_muc_tieu`): khoá tuỳ chọn `muc_tieu.wharton_truoc` (bool) = "Chia 100 điểm" đang bật TRƯỚC khi `co_hoi` tắt nó. `api_muc_tieu.py` (`_ke_hoach`): vào `co_hoi` thì nhớ; áp lại `co_hoi` giữ nguyên; rời `co_hoi` sang thẻ khác khi chưa sửa tay (không phải `tuy_chinh`) thì trả `rules.wharton` (không chạm `fa_daa`), không thêm ghi chú; `bao_cao_muc_tieu`: mốc "không dùng thẻ" của `co_hoi` gồm cả điểm chia đã nhớ. Hoàn tác giữ nguyên ngữ nghĩa (gói có cả `muc_tieu`).
- `js/18_cai_dat.js` + `js/19_muc_tieu.js`: câu hỏi đầu vẽ lại từ cấu hình đã lưu sau mỗi lần chọn / hoàn tác / "Về mục tiêu mẫu" (dấu ✓ chuyển sang "Chỉ xếp thứ tự" và trở lại).
- `HUONG_DAN_SU_DUNG.md`: câu về điểm chia nói cả Hoàn tác lẫn chuyển thẻ.
- Test: 6 ca mới ở `tests/test_mt1_api.py`, 1 ở `tests/test_mt1_uoc_tinh.py`, 1 ở `tests/test_giao_dien_mt1.py` (26 ca).

## 2026-11-20 — MT1-L4 fix2: "Dành chỗ" nhiều nhóm không giả vờ đã lưu

- `js/19_muc_tieu.js`: bấm thẻ "Dành chỗ" khi có nhiều nhóm chỉ mở các nút nhóm (tiêu điểm nhảy tới nút đầu; thẻ có `aria-expanded`, viền nét đứt, KHÔNG ✓, `aria-checked` giữ false). Thẻ đã lưu giữ dấu ✓, dòng tác động và thông báo của nó cho tới khi bấm một nhóm (bấm thứ hai mới lưu, rồi mới ✓ + thông báo + ước tính). Bấm thẻ khác hoặc chính thẻ đã lưu thì nút nhóm biến mất. `style.css`: `.ux1a-the.is-cho`.
- Test: `tests/test_giao_dien_mt1.py` 25 ca (sửa ca hai lần bấm, thêm ca bấm thẻ khác khi đang chờ).

## 2026-11-20 — MT1-L5 fix1: hướng dẫn nói đúng khi nào có nút "Về mục tiêu mẫu"

- `HUONG_DAN_SU_DUNG.md`: nút chỉ có nếu trước đó đã chọn một thẻ; ví dụ số ghi "(số minh hoạ)".

## 2026-11-20 — MT1-L5 (phần tài liệu): hướng dẫn "Chọn mục tiêu"

- `HUONG_DAN_SU_DUNG.md` (mục 4): đoạn "Chọn mục tiêu" (ba thẻ, một/hai lần bấm, Hoàn tác, ghi chú điểm chia, khoá khi huy chương, dòng tác động, dòng kết quả, "dưới 5", dòng xám "cài đặt riêng"); bảng nhóm "Cài đặt và quản lý" nói hai câu hỏi. Bản đồ mã (`CLAUDE_CHI_TIET.md`) đã có `muc_tieu.py`, `muc_tieu_do.py`, `api_muc_tieu.py`, `js/19_muc_tieu.js`. Chưa viết bản đánh giá của lead (§5).

## 2026-11-20 — MT1-L4 fix1: dòng "đã theo mục tiêu", ghi chú ở trình tạo workspace, thông báo cũ, câu cảnh báo

- `js/19_muc_tieu.js`: ước tính 0/0 nay nói kết quả ("Không học sinh nào đổi chỗ so với lần xếp gần nhất."; khoá `mt1_khong_doi` thay `mt1_da_theo`, vì lần xếp trước có thể dùng luật khác); lần chọn thẻ mới đóng thông báo "Đã chuyển sang…" cũ, Hoàn tác luôn là của lần mới nhất.
- `js/075_workspace.js` (bước 3): chọn "Cơ hội như nhau" khi đang "Chia 100 điểm" hiện cùng dòng "Điểm chia không được dùng với mục tiêu này." (`#wzMtGhiChu`).
- `i18n_errors.py` (`mt_khong_co_khoang_cach`): câu rõ hơn, "Lần xếp gần nhất chưa thấy nhóm này bị thiệt hơn các nhóm khác, nên có thể chưa cần giữ chỗ." (câu do lead chốt)
- "Xem từng CLB" vốn đã thu gọn sẵn (ảnh cũ do script chụp mở ra); đã có test canh. Test: `tests/test_giao_dien_mt1.py` 24 ca (+3, sửa 2); ảnh làm mới ở `docs/phien/anh_mt1/`.

## 2026-11-20 — MT1-L4: giao diện ba thẻ mục tiêu

- Mới: `js/19_muc_tieu.js` (`mt1TaoCauHoi`, `mt1VeKetQua`, `mt1NhanNhom`; nạp trong `index.html`, `js/_danh_sach.txt`, `initMucTieu` ở `js/08_khoi_dong.js`). Câu hỏi thứ hai ở Cài đặt, "Khi một CLB đông người, trường ưu tiên điều gì?", đặt ngay dưới câu hỏi đầu, vẽ bằng CÙNG thành phần `ux1aTaoThe` (thêm tham số `bo`, `khoaCauHoi`, `moiTheTab`; lưới thẻ có `id`); thay dòng "Cách xét khi đông" (`ux1aVeCachXet` bỏ), "Thay đổi…" nằm dưới câu hỏi mới. 1 lần bấm (`nang_luc`, `co_hoi`, `danh_cho` một nhóm), 2 lần (nhiều nhóm: bấm thẻ hiện nút nhóm đọc được "khối 10", bấm nhóm mới lưu). Lưu ngay, thông báo "Đã chuyển sang …" + Hoàn tác 10 giây (luật VÀ chỗ giữ từng CLB), ghi chú "Điểm chia không được dùng với mục tiêu này." khi `co_hoi` tắt điểm chia. Một dòng tác động (lời trước lần xếp đầu; "Ước tính so với lần xếp gần nhất…" sau đó; "dưới 5" từ `{n: null, duoi_5: true}`), `<details>` "Xem từng CLB", cảnh báo vàng mỗi loại một dòng, lý do khoá một dòng (huy chương / không có cột nhóm), dòng xám "Đang dùng cài đặt riêng · Về mục tiêu mẫu".
- Dòng kết quả `#mt1KetQua` ở thẻ "Chi tiết và xuất tệp" (`index.html`, gọi từ `loadTomTatKetQua` ở `js/03_ket_qua.js`): một dòng + `<details>`; không có số được giúp / nhường chỗ khi backend không so được; ẩn khi lần xếp không theo thẻ hiện tại. Giáo viên không thấy (`data-quyen`, và JS không gọi).
- `js/075_workspace.js` (bước 3 trình tạo workspace): cùng câu hỏi, cùng thành phần; hai thẻ đặt ô "Thứ tự ưu tiên", "Dành chỗ" khoá (chưa có danh sách học sinh).
- `i18n.js`: khoá `mt1_*` (vi + en, qua nhãn `{person_l}`, `{slot_s}`; không "dự trữ", "STB", "Wharton", "tier"); `style.css`: lớp `.mt1-*` (chữ ≥ 14px, nút ≥ 36px, vòng tiêu điểm 3px) chỉ thêm, không đổi lớp cũ.
- Test: `tests/test_giao_dien_mt1.py` (22 ca, Chromium); `tests/test_giao_dien_ux1_cai_dat.py` bỏ khẳng định dòng "Cách xét khi đông". Ảnh trước/sau: `docs/phien/anh_mt1/`.

## 2026-11-20 — MT1-L3 fix1: báo cáo không bịa "0 em được giúp" khi thiếu chỗ giữ ban đầu

- `api_muc_tieu.py` (`bao_cao_muc_tieu`): thẻ `danh_cho` mà `muc_tieu.truoc` thiếu hoặc rỗng thì `co_so_sanh` = False, bỏ `duoc_giup` / `nhuong_cho` / `nhom_duoc_giup` / `an_toan_truoc`; vẫn có `dat` và `an_toan`. Test: 2 ca trong `tests/test_mt1_uoc_tinh.py`.

## 2026-11-20 — MT1-L3: ước tính và dòng kết quả của thẻ mục tiêu (chỉ đọc)

- Mới: `muc_tieu_do.py` (phép đo thuần: `an_so` ẩn số 1–4 thành "dưới 5", `so_sanh_hang`, `dat_o_clb`, `co_khoang_cach`, `pct_nguyen_vong_1`…). `api_muc_tieu.py`: `uoc_tinh_muc_tieu(muc_tieu, nhom)` (thẻ GIẢ ĐỊNH chưa áp; giải trong bộ nhớ với bộ số đã khoá, so với lần chính thức mới nhất; chưa có lần xếp thì chỉ có lời; huy chương → `mt_uoc_tinh_fa`) và `bao_cao_muc_tieu(run_id)` (đạt ở mấy CLB được chọn nhiều nhất, em được giúp / nhường chỗ so với cùng dữ liệu không dùng thẻ, nguyện vọng 1, chưa có chỗ). Cả hai không ghi bảng nào, không sao lưu, không gọi `run_thu`; chỉ quản trị, không vào nhật ký (hàm đọc).
- `api_tieu_chi.py`: tách `_giai_trong_bo_nho` ra khỏi `_run_thu_da_khoa` (không đổi hành vi; thêm `sao_luu=False`, `sua_clb`).
- Mã mới `mt_cho_it`, `mt_khong_co_khoang_cach`, `mt_uoc_tinh_fa`, `mt_chua_co_ket_qua` (cuối `i18n_errors.py`, `i18n_loi.js` sinh lại); `phan_quyen.py`, `nhat_ky.py` (`_KHONG_GHI`).
- Test: `tests/test_mt1_uoc_tinh.py` (31 ca: tính tay 10/10 và 3/3, tổng kiểm mọi bảng trước/sau, nhiều buổi, lần chạy thử không làm mốc, dòng kết quả khớp hai lần chạy thật); `tests/test_mt1_api.py` thêm ca rò rỉ với `co_hoi` (luật ghi lịch sử và dấu vân tay y hệt khi không có `muc_tieu`).

## 2026-11-20 — MT1-L2: API ba thẻ mục tiêu (chỉ quản trị)

- Mới: `api_muc_tieu.py` (`MucTieuMixin`: `get_muc_tieu`, `chon_muc_tieu`, `hoan_tac_muc_tieu`); gắn vào `PipelineAPI`. Chọn thẻ = MỘT giao dịch (luật + khoá `muc_tieu` + chỗ giữ của CLB), sao lưu trước, không chạy xếp, không đụng `run_history` / `match_results` / `stb_lock`. Hoàn tác trả đúng luật, `muc_tieu` và từng CLB; rời thẻ "Dành chỗ" thì trả chỗ giữ nhập ban đầu.
- `cau_hinh_ws.py`: khoá cấp trên TUỲ CHỌN `muc_tieu` `{id, nhom, truoc?}` (`_kiem_muc_tieu`; không có thì cấu hình y như cũ, nằm ngoài `rules` nên không vào `luat_xep` / dấu vân tay); `ghi_cau_hinh(..., cung_giao_dich=f)` chạy `f(conn)` trong cùng giao dịch, lỗi thì rollback cả hai. `workspace.py` (`luu_mau`): mẫu không mang `muc_tieu`.
- `muc_tieu.py`: thẻ `danh_cho` đặt lại cả `tiers=[]` và `score_scope=per_slot` (thẻ sáng lại sau khi luật từng bị sửa tay).
- `co_hoi`: huy chương bật → lỗi `mt_the_can_diem`; "Chia 100 điểm" bật → chạy được, `wharton` tự tắt theo luật nhất quán sẵn có của `cau_hinh_ws`, kèm ghi chú `mt_diem_chia_khong_dung`, Hoàn tác trả lại.
- `phan_quyen.py` (ba hàm, cả hàm đọc, chỉ quản trị), `i18n.js` (`nkhd_chon_muc_tieu`, `nkhd_hoan_tac_muc_tieu`), `i18n_errors.py` (tám mã `mt_*` ở cuối) + `i18n_loi.js` sinh lại.
- Test: `tests/test_mt1_api.py` (28 ca, viết trước); `tests/test_gt3_phan_quyen.py` thêm `get_muc_tieu` vào danh sách hàm đọc chỉ quản trị.

## 2026-11-20 — MT1-L1: danh mục ba thẻ mục tiêu (phần thuần)

- Mới: `muc_tieu.py` (`BO_MUC_TIEU`, `rules_cua_muc_tieu`, `nhan_dien_muc_tieu`, `de_xuat_cho_giu`, `cac_nhom`). Chỉ đặt khoá của `LUAT_XEP_MAC_DINH`, không chạm `wharton`/`fa_daa`; số chỗ giữ = `ceil(tỉ lệ nhóm × sức chứa)` chỉ đọc danh sách học sinh. Chưa nối vào API/giao diện (L2, L4).
- Test: `tests/test_mt1_muc_tieu.py` (bản vá qua `_chuan_hoa`, mặc định ⇒ `nang_luc`, công thức ca 10 em tính tay, `co_hoi` = bốc thăm thuần so với Gale–Shapley viết riêng, 2 bộ × 3 seed). Số liệu MÔ PHỎNG.
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: bản đồ mã thêm `muc_tieu.py`, số tệp test 354.

## 2026-11-20 — MT0 (mục mới MT, ngoài sổ; mục cha C3/A1): nghiên cứu mục tiêu giáo dục (chỉ đo)

- Mới: `du_lieu_test/do_muc_tieu_mt0.py` (gọi `run_rbda`, `verify_stability` thật; 3 kịch bản × 20 seed), `docs/fable/08_MT0_MEMO.md`.
- Không đổi mã sản phẩm, không test mới. Số liệu MÔ PHỎNG.

## 2026-11-20 — UX1F-L4: một ô "Chọn lớp" ở thẻ Kết quả

- `index.html`, `js/09_the_xem.js`, `js/19_ux1b_gv.js`, `style.css`: bỏ `#ux1bLop`; ô `#kqChonLop` (bọc trong `#kqChonLopHang`) chuyển lên khối "Theo lớp và báo cáo" và hiện ở mọi tầng khi có lớp. Chọn lớp ở tầng khác tự mở "Theo lớp" (như `#ux1bLop` trước đây); "In phiếu cả lớp" dùng đúng giá trị này và tắt khi chọn "Chưa có lớp". "Xuất theo lớp" và "Báo cáo tổng hợp" vốn là việc cả trường nên không nhận lớp (không đổi hành vi). Bỏ chú thích cũ trên `#ux1bPanel`. Khoá i18n `ux1b_chon_lop` không còn dùng trong HTML (để lại, không hại).
- Test: `tests/test_giao_dien_ux1f_l4_mot_o_chon_lop.py` (4 ca; quản trị và giáo viên đúng MỘT ô, chọn lớp lọc bảng và quyết định phiếu cả lớp: PDF đúng các em của lớp đó; đỏ trước khi sửa); đổi selector `#ux1bLop` → `#kqChonLop` trong `test_giao_dien_ux1b_vai_gv.py`, `test_ux1i_i3_phieu_bao_cao.py`, `docs/ke_hoach/ux/chup_tich_hop.py`; `test_giao_dien_t2_ket_qua.py::test_tang1_ba_nut…` nay mong ô chọn lớp hiện ở mọi tầng. Bản đồ mã: 355 → 356 tệp test.

## 2026-11-20 — UX1F-L3: giáo viên lưu PDF phiếu của MỘT học sinh

- `index.html`: `#btnGtPdfMot` bỏ `data-quyen="quan_tri"`, giáo viên thấy nút "Lưu PDF" ở khung tra cứu. Backend không đổi: `phan_quyen.QUYEN["export_phieu_giai_trinh_pdf"]` vốn đã là giáo viên; chế độ học sinh vẫn bị chặn (`gt3_che_do_hoc_sinh`), chưa đăng nhập bị chặn (`gt3_can_dang_nhap`).
- Riêng tư: tệp chỉ chứa em đã chọn (`student_ids=[mã]`).
- Test mới: `tests/test_ux1f_l3_giao_vien_pdf_mot_em.py` (3 ca backend + 1 ca Chromium: giáo viên tìm → chọn → Lưu PDF = 3 lần bấm, tệp chỉ có em đó). Ca Chromium đỏ trước khi sửa (nút ẩn). Bản đồ mã: 354 → 355 tệp test.

## 2026-11-20 — UX1F-L2 fix1: tiêu đề buổi không nằm một mình ở đáy trang

- `phieu_giai_trinh.py` (`_khoi_pdf`): mỗi buổi là MỘT khối `giu_cung` (từ tiêu đề buổi); buổi cuối gộp luôn chú thích, khiếu nại, mã tra cứu. Trước đó khối giữ chung chỉ bắt đầu ở bảng nên "Thứ 6" có thể ở đáy trang 10 còn bảng ở trang 11.
- Test: thêm `test_tieu_de_buoi_cuoi_khong_mot_minh_o_day_trang` (quét 3–8 buổi × 4 độ dài lời giải thích; đỏ trước khi sửa). 800 em vẫn 1278 trang.

## 2026-11-20 — UX1F-L2: bố cục phiếu giải trình PDF (một trang, tiêu đề cột không gãy từ)

- `xuat_pdf.py`: lề 12 mm (trước 18/18/16/18), chữ bảng 8,5 pt (trước 9), đoạn và đệm ô chặt hơn; `bang` tính độ rộng tối thiểu từng cột từ TỪ DÀI NHẤT của tiêu đề (`_rong_toi_thieu`, `_chia_cot`) nên tiêu đề chỉ xuống dòng ở dấu cách ("Huy chương", "Mức vào được" không còn gãy "Huy ch/ương"); thêm `giu_cung` (KeepTogether).
- `phieu_giai_trinh.py` (`_khoi_pdf`): bảng cuối + ghi chú + khiếu nại + mã tra cứu đi liền nhau (`giu_cung`), không để chú thích/chân phiếu rơi một mình sang trang sau. Nội dung phiếu không đổi, chỉ bố cục.
- `.github/workflows/tests.yml`: job test-windows cài thêm `pypdf>=4,<6` (chỉ CI; không đụng `requirements.txt`, `kiosk.spec`).
- Số trang (dữ liệu MÔ PHỎNG, seed 3): 40 em của `SO_NHAP_FA_MAU_120HS.xlsx` 74 → 40 trang (đo lại trước khi sửa: 74, kế hoạch ghi 75; mỗi em một trang, trang ngắn nhất 1577 ký tự); toàn bộ 120 em 225 trang trước đó; 800 em `SO_NHAP_DQT_800HS_HOP_LE.xlsx`: 1519 → 1278 trang (phiếu quá 3 buổi vẫn cần 2 trang; trang 2 luôn có bảng cuối + chú thích, không chỉ chân trang).
- Test mới: `tests/test_ux1f_l2_phieu_pdf_bo_cuc.py` (3 ca: ≤ 44 trang, mỗi trang ≥ 200 ký tự, tiêu đề không gãy giữa từ). Bản đồ mã: 353 → 354 tệp test.

## 2026-11-20 — UX1F-L1: pypdf là phụ thuộc DEV

- `requirements-dev.txt`: thêm `pypdf>=4,<6` (CHỈ tệp dev; không đụng `requirements.txt`, `kiosk.spec`). CI (`tests.yml`) cài `requirements-dev.txt` nên các test đọc PDF nay chạy thật thay vì tự bỏ qua.
- Kiểm cục bộ: `tests/test_xp1_phieu_pdf.py`, `test_xp1_danh_sach_pdf.py`, `test_xp1_pdf_loi.py`, `test_ux1i_i3_phieu_bao_cao.py` → 70 qua, 0 bỏ qua. Không có test mới (chỉ bật test sẵn có).

## 2026-11-19 — UX1I-I4 fix1: CI #1 (shard 3) đỏ vì bản đồ mã

- `docs/ke_hoach/CLAUDE_CHI_TIET.md` ("Bản đồ mã"): số tệp test 344 → 353 (đếm `tests/test_*.py`), thêm các nhóm XP1 và UX1I; dòng `bao_cao_tong_hop.py` ghi `dung_pdf` và `export_bao_cao_tong_hop_pdf`.
- Chạy cả bộ Linux một lượt (Chromium + pypdf): 6977 qua, 4 bỏ qua (numpy ×2, người dùng POSIX, ưu tiên bù hoãn kỳ 2).

## 2026-11-19 — UX1I-I3 fix1: cột Buổi của Báo cáo tổng hợp không lộ mã nội bộ

- `bao_cao_tong_hop.py` (`dung_html`, `dung_pdf`): cột Buổi dùng thẳng `giai_trinh.nhan_buoi` (rỗng cho buổi mặc định), bỏ phần dự phòng in mã `__mac_dinh__`.
- Test: 2 ca mới trong `tests/test_ux1i_i3_phieu_bao_cao.py` (workspace một buổi, HTML và PDF).

## 2026-11-19 — UX1I-I3: gộp nhánh B (phiếu, vai giáo viên) với XP1 (PDF)

- Gộp `origin/claude/ux1-b-phieu` (xung đột ở `phieu_giai_trinh.py`, `api_xuat.py`, `i18n_errors.py`, tài liệu): bảng phiếu có cột "Loại CLB" (XP1) rồi "Huy chương" (B, chỉ khi bật huy chương); `i18n_loi.js` sinh lại bằng `tao_i18n_js.py`.
- `phieu_giai_trinh.py` (`_khoi_pdf`): bản PDF của phiếu có thêm dòng tóm tắt, cột Huy chương, bảng điểm các CLB đã thi, ghi chú huy chương và "Em nên làm gì tiếp", như bản HTML.
- `bao_cao_tong_hop.py` (`dung_pdf`), `api_xuat.py` (`export_bao_cao_tong_hop_pdf`): "Báo cáo tổng hợp" dạng PDF qua `xuat_pdf.py`, cùng số liệu gộp (không tên, mã, điểm).
- `phan_quyen.py`: giáo viên được gọi `export_phieu_giai_trinh_pdf` và `export_bao_cao_tong_hop_pdf`; `export_danh_sach_pdf` vẫn chỉ quản trị.
- `index.html`, `js/19_ux1b_gv.js`, `i18n.js`: khối "Theo lớp và báo cáo" thêm "In phiếu cả {cohort_l}" (MỘT tệp PDF của lớp đang chọn) và "Báo cáo tổng hợp (PDF)"; giáo viên cần 1 lần bấm sau khi vào thẻ Kết quả.
- Test: thêm `tests/test_ux1i_i3_phieu_bao_cao.py`; sửa `tests/test_ux1b_l7_phieu.py` (nay có cả hai cột) và `tests/test_xp1_phieu_pdf.py` (quyền). `docs/giai_trinh/CA_MAU.md` sinh lại: không đổi.

## 2026-11-19 — UX1I-I2: XP1 gộp vào menu "Xuất…" của A

- `index.html`, `js/03_ket_qua.js`: bỏ menu riêng `#xuatPdfMenu`; ba mục PDF (`btnPdfDsClb`, `btnPdfDsLop`, ô `pdfLop`, `btnPdfPhieuLop`) nằm trong `#xuatMenu`, menu này nay luôn hiện cho quản trị (`data-quyen="quan_tri"`), bốn nút chỉ-huy-chương vẫn ẩn khi tắt chế độ. Bỏ khoá `xp1_menu` ở `i18n.js` (không còn dùng).
- Test: thêm `tests/test_ux1i_i2_xp1_trong_menu.py` (một menu, giáo viên không thấy, "Lưu PDF" một em ≤ 4 lần bấm từ thẻ Kết quả, loại CLB đặt bằng `dat_loai_clb` vào phiếu); sửa `test_giao_dien_xp1_xuat_pdf.py` và `test_giao_dien_ux1_ket_qua.py` theo menu gộp.
## 2026-11-19 — UX1I-I1: gộp nhánh A vào nhánh tích hợp

- Lead gộp `origin/claude/ux1-a-giao-dien` (`--no-ff`, không xung đột). Không đổi mã sản phẩm; `python tao_i18n_js.py` sinh lại `i18n_loi.js` không đổi byte nào.
- Kiểm: 150 test của bộ I1 qua (`test_giao_dien_ux1_*`, `test_ux1_*`, `test_khoi_dong_backend`, `test_ws_nhan`, `test_van_phong_tu_nhien`, `test_gt4_nhat_ky_doc`, `test_gt_tich_hop`); `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7 (60 ca trùng khít).

## 2026-11-19 — XP1-L5 fix3: danh sách PDF (từ lượt xem của lead trên sổ mẫu 3 buổi)

- `xuat_pdf.py` (`bang`): tham số `cot_dau_mm` (cột đầu rộng cố định). `danh_sach_pdf.py`: cột STT rộng 13 mm (đủ "STT" in đậm và số 4 chữ số; trước đó 0,5/(0,5 + 2 x số cột) nên "STT" bị cắt dọc thành S/T/T và số 2 chữ số xuống dòng ở bảng nhiều buổi), `hoa_dau` viết hoa chữ cái đầu mọi tiêu đề và nhãn đứng đầu dòng (trước: "học sinh chưa có câu lạc bộ").
- `api_xuat.py`: `_chua_duoc_xep.pdf` nhiều buổi đếm EM khác nhau ("Số học sinh: 112", trước 222 là số lượt em x buổi) và thêm dòng "Số lượt chưa có chỗ: 222" khi hai số khác nhau.
- Test mới trong `tests/test_xp1_danh_sach_pdf.py` (+5 ca, 24 ca): độ rộng cột STT (luôn chạy), "STT" không bị cắt (pypdf), đếm em / lượt, tiêu đề viết hoa, `hoa_dau`. Xem ảnh trang trên sổ `SO_NHAP_MAU_120HS_3BUOI.xlsx` seed 3.

## 2026-11-19 — XP1-L5: tài liệu, đóng gói, hiệu năng

- `HUONG_DAN_SU_DUNG.md`: mục "Xuất PDF hàng loạt" (ba mục menu, ô chọn lớp, phiếu một em, ghi chú: CLB không có em nào được xếp thì không có tệp danh sách). `CLAUDE_CHI_TIET.md`: bản đồ mã (`xuat_pdf.py`, `danh_sach_pdf.py`, hai hàm API), số tệp test 346.
- `.github/workflows/build-windows-exe.yml`: bước soát bản đóng gói kiểm thêm hai phông `.ttf` và tệp giấy phép OFL (reportlab không đọc `.woff2`). `kiosk.spec` đã có `assets/fonts` và `collect_all("reportlab")` từ L1.
- `xuat_pdf.py`: kiểu đoạn tạo một lần (không tạo lại cho từng ô). Không đổi kết quả đầu ra.
- Hiệu năng, sổ mô phỏng `SO_NHAP_DQT_800HS_HOP_LE.xlsx` (800 em, 27 lớp, seed 3, Linux). Mục tiêu của kế hoạch: phiếu giải trình cả trường < 30 giây trên CI Linux.

  | Xuất | Không đo độ phủ | Có `--cov` |
  |---|---|---|
  | Phiếu theo lớp (28 tệp, 1.519 trang) | 12,6 giây | 21,6 giây |
  | Phiếu một tệp | 15,8 giây | 23,3 giây |
  | Danh sách theo CLB (21 tệp) | 2,7 giây | 4,1 giây |
  | Danh sách theo lớp (28 tệp) | 0,8 giây | 1,2 giây |

  Số đo thật trên CI (lần chạy 44551113280, ngưỡng cũ 30 giây): bước chạy KHÔNG đo độ phủ, các ca hiệu năng đạt; bước CÓ đo độ phủ, phiếu theo lớp 30,08 giây và phiếu một tệp 30,04 giây nên đỏ (đo độ phủ làm chậm thêm khoảng 50 %); Windows (không đo độ phủ) đạt. Vì vậy test tạm dừng đo độ phủ (`coverage.Coverage.current().stop()`, bật lại sau) CHỈ trong đoạn bấm giờ; sau sửa, máy phát triển có `--cov`: phiếu theo lớp 12,8 giây, một tệp 14,3 giây (không `--cov`: 13,2 và 14,5 giây). Mục tiêu 30 giây trên CI Linux giữ nguyên.

  Ngưỡng test: 30 giây trên Linux (mục tiêu của kế hoạch), 90 giây trên Windows (kế hoạch không đặt mục tiêu cho Windows), đổi được bằng biến môi trường `XP1_NGUONG_GIAY`; luôn in số giây đo được, không bỏ qua test.
- Test mới: `tests/test_xp1_hieu_nang.py` (4 ca, ngưỡng 30 giây), `tests/test_xp1_dong_goi.py` (5 ca: phông, giấy phép, spec, ghim phiên bản, workflow). `kiem_nhanh.py` 7/7.

## 2026-11-19 — XP1-L4: menu "Xuất PDF…" ở thẻ Xuất dữ liệu

- `index.html`, `js/03_ket_qua.js`: menu riêng `#xuatPdfMenu` (chỉ quản trị, `data-quyen="quan_tri"`) với "Danh sách theo CLB (PDF)", "Danh sách theo lớp (PDF)", ô chọn lớp `#pdfLop` (dùng lại `napOLocLop`, không có mục "chưa có lớp") và "Phiếu giải trình theo lớp (PDF)": "Tất cả lớp" ra thư mục mỗi lớp một tệp, chọn một lớp ra MỘT tệp. Ba nút khoá khi chưa có kết quả / đang chạy / đang xuất (như "Xuất theo lớp"); bấm xong menu tự đóng. Menu riêng vì "Xuất…" cũ chỉ hiện ở chế độ Huy chương và `test_giao_dien_ux1_ket_qua.py` khoá điều đó.
- `i18n.js`: khoá `xp1_menu`, `xp1_pdf_ds_clb`, `xp1_pdf_ds_lop`, `xp1_pdf_phieu_lop`, `xp1_pdf_lop_aria`, `xp1_kq_thu_muc`, `xp1_kq_mot_tep` (vi/en). Quyền backend và nhãn nhật ký đã có từ L2/L3.
- Sửa có chủ ý `tests/test_giao_dien_ux1_ket_qua.py`: "nút đang hiện" không đếm nút nằm trong menu `<details>` đang đóng (menu PDF mới có nút trong đó).
- Test mới: `tests/test_giao_dien_xp1_xuat_pdf.py` (7 ca Chromium: menu, khoá khi chưa có kết quả, gọi đúng hàm, một lớp / mọi lớp, giáo viên không thấy menu). Số tệp test trong `CLAUDE_CHI_TIET.md`: 344.

## 2026-11-19 — XP1-L3: danh sách thành viên PDF (theo CLB, theo lớp)

- `api_xuat.py`: `export_danh_sach_pdf(output_path, theo)` ("clb" hoặc "lop") ra một THƯ MỤC PDF; cùng nguồn `_du_lieu_xuat` với `export_theo_lop`, không điểm / số bốc thăm / diện trúng tuyển. Theo CLB: mỗi CLB (nhiều buổi: mỗi CLB mỗi buổi) một tệp có mã, loại CLB, giờ, địa điểm; CLB không ai được xếp không có tệp (như CSV); `_chua_duoc_xep.pdf` cho em chưa có chỗ. Theo lớp: mỗi lớp một tệp, em chưa có chỗ ở mục riêng, `_chua_co_lop.pdf`. Thêm `_loai_clb_theo_ma`.
- `danh_sach_pdf.py` (mới): bố cục hai kiểu tệp. `i18n_errors.py`: `xp1_kieu_xuat_la`. `phan_quyen.py`: hàm mới chỉ QUAN_TRI; `i18n.js`: nhãn `nkhd_export_danh_sach_pdf`.
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: số tệp test 343, bản đồ mã.
- Test mới: `tests/test_xp1_danh_sach_pdf.py` (19 ca, gồm sổ mẫu 3 buổi 120 HS).

## 2026-11-19 — XP1-L2: phiếu giải trình PDF theo lớp, có loại CLB

- `giai_trinh.py` (`dung_du_lieu_run`, `_lua_chon_rbda`, `_lua_chon_fa`): mỗi `cac_lua_chon` có thêm khoá `loai_clb` (mã `TU_DO`/`GIOI_HAN`/`TUYEN_CHON` hoặc None); chỉ thêm khoá, thuật toán xếp không đọc nó.
- `phieu_giai_trinh.py`: cột "Loại CLB" ở phiếu HTML; `dung_phieu_pdf` (cùng dữ liệu, mỗi học sinh một trang mới).
- `api_xuat.py`: `export_phieu_giai_trinh_pdf(output_path, lop, theo_lop)` (một tệp, hoặc thư mục `phieu_giai_trinh_theo_lop` mỗi lớp một PDF + `_chua_co_lop.pdf`); tách `_phieu_chuan_bi`, `_phieu_cac_em` dùng chung với phiếu HTML và `_thu_muc_xuat_moi` dùng chung với `export_theo_lop`. `_giai_trinh_dung_lai` đọc thêm `clubs.loai`.
- `xuat_pdf.py`: `dem_trang`, `san_sang`. `i18n_errors.py`: mã lỗi `xp1_thieu_thu_vien_pdf` (+ `i18n_loi.js` sinh lại). `phan_quyen.py`: hàm mới chỉ QUAN_TRI; `i18n.js`: nhãn nhật ký `nkhd_export_phieu_giai_trinh_pdf` (vi/en).
- Phiếu MỘT em: `export_phieu_giai_trinh_pdf(..., student_ids=[mã])` ra một tệp `phieu_giai_trinh_<mã>.pdf`; nút "Lưu PDF" (`#btnGtPdfMot`, chỉ quản trị) ở khung tra cứu thẻ Kết quả (`index.html`, `js/14_giai_trinh.js`, khoá i18n `xp1_luu_pdf`, `xp1_pdf_mot_xong`): tìm → chọn → Lưu PDF = 3 bước.
- Test: `tests/test_xp1_phieu_pdf.py` (22 ca), `tests/test_giao_dien_xp1_luu_pdf_mot_em.py` (Chromium). Sửa có chủ ý: `test_gt4_cau_giai_trinh.py` (cột "Mức vào được" dời từ 4 sang 5 vì thêm cột), `test_van_phong_tu_nhien.py` (thêm "PDF" vào viết tắt cho phép), `test_ws_nhan.py` (cho phép tiền tố mã lỗi `xp1_`).
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: số tệp test sửa thành 342 (đếm thật; CI #44514194103 đỏ vì còn 339), thêm hàng `xuat_pdf.py` vào bản đồ mã.
- `docs/phien/claude__ux1-b-phieu.md`: ghi chú L6/L7 đã được XP1 thay/làm. `kiem_nhanh.py` 7/7.

## 2026-11-19 — XP1-L1: lõi xuất PDF (chưa có giao diện)

- `xuat_pdf.py` (mới): `dung_pdf`, `tieu_de`, `dong_khoa_gia_tri`, `bang` (lặp tiêu đề cột, ô tự xuống dòng, thoát ký tự markup), `ngat_trang`; A4 dọc, chân trang "Trang x/y", ghi qua tệp tạm rồi đổi tên, không ghi đè (`duong_dan_khong_de`); thiếu reportlab/phông thì `ThieuThuVienPdf`.
- `assets/fonts/BeVietnamPro-Regular.ttf`, `BeVietnamPro-Bold.ttf`, `OFL-BeVietnamPro.txt` (SIL OFL; `assets/fonts` đã nằm trong `kiosk.spec` datas).
- `requirements.txt`: `reportlab==5.1.0` (thư viện mới, Truong duyệt 2026-11-18). `pypdf` KHÔNG thêm vào requirements: test đọc chữ tự bỏ qua khi thiếu nó.
- `kiosk.spec`: `collect_all("reportlab")`.
- Test mới: `tests/test_xp1_pdf_loi.py` (13 ca: 8 ca mức byte luôn chạy, 5 ca đọc chữ cần pypdf tuỳ chọn). Không đụng thuật toán/DB; `kiem_nhanh.py` 7/7.
## 2026-11-19 — UX1B R1 fix2 (từ checker)

- `giai_trinh._chuan_clb_fa`: mức vào được của CLB có thi (FA) lấy từ các dòng REJECTED đã lưu của CLB (cùng nguồn với câu "Vì sao"): có dòng RESERVED -> "Chỗ dành riêng" (không số), ngược lại `cut_score`; chưa ai bị từ chối -> "Còn chỗ". Không còn lấy điểm thấp nhất của người nhận (kể cả người giữ chỗ). Cột, thanh SVG và câu cùng một mức.
- `phieu_giai_trinh._o_chuan`: số điểm in như câu ("8" thay "8.0").
- Test: 3 ca mới trong `tests/test_ux1b_l7_phieu.py` (giữ chỗ 3 điểm + t 8 + x 7; người nhận cuối giữ chỗ; chưa ai bị từ chối).

## 2026-11-19 — UX1B R1 (từ lượt duyệt của lead)

- `giai_trinh._chuan_clb_fa`: chế độ FA, CLB có thi giờ có "Mức vào được" (điểm thấp nhất trong số người đã nhận khi CLB đầy, hay "Còn chỗ"), kể cả dòng ACCEPTED; thanh SVG có vạch đỏ. CLB không thi, dòng MEDAL: ghi huy chương của người nhận cuối ("Huy chương Vàng", `ux1b_gt_chuan_huy_chuong`). Chỉ con số của CLB.
- Lý do MEDAL chỉ còn MỘT câu: "Em đặt huy chương Bạc; các bạn đặt Vàng ở {CLB} được xét trước." (hoặc "Em chưa đặt huy chương ở {CLB}; …"); `CA_MAU.md` không đổi.
- `bao_cao_tong_hop.py`: buổi hiện "Thứ 2" (`giai_trinh.nhan_buoi`), mọi tiêu đề viết hoa chữ đầu sau khi điền nhãn, bảng nguyện vọng ghi "Số lượt xếp ({person_l} × {session_l})" (đếm lượt, không phải người).
- Test: `tests/test_ux1b_l7_phieu.py` (+1 trên sổ FA mẫu, sửa 2 câu cũ), `tests/test_ux1b_l4_bao_cao.py` (+1), `tests/test_giao_dien_ux1b_phieu.py` (sửa câu).

## 2026-11-19 — UX1B CI-1

- `index.html`: chữ dự phòng của nhóm `ux1a_nhom_cai_dat` đổi thành "Cài đặt và quản lý" cho khớp `i18n.js` (`tests/test_t3_l1_chu_du_phong.py`). Không đổi test.

## 2026-11-19 — UX1B-L8-B: tài liệu phiếu, ảnh, bảng "Sau"

- `HUONG_DAN_SU_DUNG.md`: mục "Phiếu giải trình và Báo cáo tổng hợp" (nội dung phiếu mới, khối "Theo lớp và báo cáo", thẻ học sinh không số khoá); hàng Kết quả; nhóm "Cài đặt và quản lý". `docs/giai_trinh/HUONG_DAN_CHAY.md`, `KICH_BAN_DEMO.md`: tên nhóm mới.
- `docs/ke_hoach/ux/anh/04_phieu.png`, `phieu_mau.pdf`, `03_tra_cuu_HS004.png` chụp lại bằng `chup_phieu.py` (Chromium, dữ liệu MÔ PHỎNG, hạt giống 42).
- `UX1_RA_SOAT.md` bảng "Sau": phiếu một em đo 5 lần bấm, CHƯA đạt mục tiêu 4 (cần nút PDF của XP1, tích hợp I3); báo cáo tổng hợp 1 lần bấm (HTML).
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: hai hàng bản đồ mã (`bao_cao_tong_hop.py`, `js/19_ux1b_gv.js`, `_huy_chuong_ca_so_sai`).
- `CA_MAU.md` và gói minh chứng: câu chữ không đổi từ L7, test sinh lại giống từng byte vẫn qua.

## 2026-11-19 — UX1B-L5c fix1 (từ checker)

- `api_quan_ly._huy_chuong_ca_so_sai`: MỘT nơi giữ ngưỡng "cả sổ sai" (từ một nửa số học sinh có nguyện vọng); `get_data_health_report` chỉ trả `gop_huy_chuong` khi qua ngưỡng, `get_san_sang_huy_chuong` thêm `huy_chuong_ca_so`. Ít em sai: giữ từng dòng có mã, thanh "Việc tiếp theo" không nhảy sang Cài đặt, khung Cài đặt vẫn cho đặt loại CLB (kèm nút Quay lại).
- Không in "ví dụ ở: " rỗng: mã lỗi mới `ux1b_huy_chuong_gop_khong_clb`.
- Dòng đỏ quyền riêng tư của khung Xuất trở lại hiện sẵn: tệp xuất mặc định có sheet "Điểm chuẩn" và "Dấu vết" (hạt giống, bộ số bốc thăm).
- Test: `tests/test_giao_dien_ux1b_l5c.py` thêm r1b (ít em sai), r1c (không có tên CLB), r5 đổi (dòng đỏ vẫn hiện).

## 2026-11-19 — UX1B-L5c: năm đề xuất của UX1_DANH_GIA_A §4 (chỉ thông điệp / bố cục)

- Đề xuất 1: `api.get_data_health_report` trả thêm `gop_huy_chuong` {n_em, n_clb, clb (tên, tối đa 3)} (danh sách `warnings` và `n_high` GIỮ NGUYÊN); `js/02_van_hanh.js` gộp các dòng `fa_huy_chuong_*` thành MỘT dòng `ux1b_huy_chuong_gop` (mã mới trong `i18n_errors.py`) có số em và tên CLB, kèm nút "Mở Cài đặt"; thanh "Việc tiếp theo" (`js/17_viec_tiep_theo.js`) có trạng thái `huy_chuong_sai` trỏ khung Cài đặt (`ux1bMoCaiDat`, `js/19_ux1b_gv.js`); nút "Quay lại Chia 100 điểm" cạnh câu "nạp lại sổ" (`js/18_cai_dat.js`).
- Đề xuất 2: `get_san_sang_huy_chuong` thêm `n_hoc_sinh`; khi có ô huy chương sai, khung sửa tại chỗ chỉ còn câu "nạp lại sổ" + "Tải sổ mẫu có huy chương" + "Quay lại Chia 100 điểm", ẩn nút loại CLB. `tests/test_giao_dien_ux1_cai_dat.py`: tách bài "chưa sẵn sàng" thành hai (cả sổ sai: không nút loại; sổ không có huy chương: sửa loại tại chỗ đến "Sẵn sàng").
- Đề xuất 3: "Sau khi xếp": mỗi hành động có một dòng hệ quả, nút/ô số/chữ "ngày" cùng một hàng; đang bật thì nút nói trọn câu ("Nhận khiếu nại trong 3 ngày"). Nhãn nút khi tắt giữ nguyên.
- Đề xuất 4: khung tra cứu: ô tìm to ở đầu, chữ gợi ý khác ô lọc bảng; dải 4 bước + ba nút mã tra cứu gập vào "Mã tra cứu…" (`#gtMaFold`, chỉ quản trị). Test cũ mở gập bằng `mo_gap_ma` (`tests/_trinh_duyet.py`); chỉ đổi cách chọn, không bỏ test.
- Đề xuất 5: nhóm "Cài đặt" đổi tên "Cài đặt và quản lý" (khớp trang Quản lý); dòng đỏ quyền riêng tư của khung Xuất chuyển vào "Tuỳ chọn khác".
- `tests/test_ws_nhan.py`: thêm mã `ux1b_huy_chuong_gop` vào `MA_MOI_SAU_ANH_CHUP`.
- Test mới: `tests/test_giao_dien_ux1b_l5c.py` (5, mỗi đề xuất một test).

## 2026-11-19 — UX1B-L7 fix2 (từ checker)

- `tests/test_giao_dien_gt1_tra_cuu.py`, `tests/test_gt4_cau_giai_trinh.py`: chọn ô "Vì sao" / "Mức vào được" theo vị trí cuối (không theo chỉ số cố định), để cột Huy chương (và cột Loại CLB của XP1 sau này) không làm lệch. Chỉ sửa bộ chọn, không bỏ test.

## 2026-11-19 — UX1B-L7 fix1 (từ checker)

- `fa_ly_do.cau_ly_do` (MEDAL): CLB không có điểm thi (`diem_em` rỗng) nói "Các bạn đặt huy chương cao hơn ở {CLB} được xét trước." thay vì "bằng điểm"; `docs/giai_trinh/HUONG_DAN_CHAY.md` sửa ví dụ cho khớp.
- `api_xuat.tra_cuu_hoc_sinh`: phản hồi cho học sinh bỏ `run.seed` và `stb_em` từng dòng (đường quản trị / giáo viên giữ nguyên).
- Test thêm trong `tests/test_ux1b_l7_phieu.py` (3).

## 2026-11-19 — UX1B-L7: nội dung phiếu giải trình (không gồm loại CLB — XP1)

- `giai_trinh.py`: `tom_tat_dong`, `cac_buoc_tiep`, `_diem_da_thi`, `NHAN_HUY_CHUONG`, `CHU_THICH_HUY_CHUONG`; `giai_trinh_mot_hoc_sinh` trả thêm `tom_tat_dong`, `buoc_tiep` (chỉ khi có buổi chưa có chỗ), `chu_thich_huy_chuong` (FA), `diem_da_thi` mỗi buổi; FA: mỗi dòng có `huy_chuong` (chỉ của chính em), dòng lý do MEDAL nối câu "Em đặt huy chương X; các bạn đặt Y được xét trước."
- `api_xuat._giai_trinh_dung_lai`: đọc `wharton_bids` (FA) và cờ `fa_vong_2` / `fa_diem_danh` / `fa_khieu_nai` thành `tinh_nang`.
- `phieu_giai_trinh.py`: dòng tóm tắt, bảng điểm CLB đã thi + thanh SVG (chỉ số, đã thoát, không tệp ngoài), khối "Em nên làm gì tiếp", cột "Huy chương" ngay sau cột CLB (chỉ FA) + chú giải; cột "Điểm thi", "Chỗ đã nhận / tối đa"; "Mức vào được" = "Chọn ngẫu nhiên khi bằng điểm" thay cho "Bốc thăm".
- `js/14_giai_trinh.js`, `i18n.js` (`ux1b_gt_*`, đổi `gt_th_diem`, `gt_th_cho`, `gt_chuan_boc_tham`), `style.css`: thẻ trên màn hình cùng nội dung; thẻ học sinh bỏ "số khoá bốc thăm" (quản trị / giáo viên vẫn thấy).
- `bao_cao_tong_hop.py`: thêm dòng "dữ liệu đã sửa sau lần xếp" khi kết quả cũ (gợi ý của checker L4-B).
- `docs/giai_trinh/CA_MAU.md` sinh lại (không đổi byte), `GOI_MINH_CHUNG.docx/.pdf` sinh lại.
- Test mới: `tests/test_ux1b_l7_phieu.py` (10), `tests/test_giao_dien_ux1b_phieu.py` (3, Chromium), thêm 1 test ở `tests/test_ux1b_l4_bao_cao.py`.

## 2026-11-19 — UX1B-L4-B: "Báo cáo tổng hợp" + khối chọn lớp ở thẻ Kết quả

- `bao_cao_tong_hop.py` (mới): `gom_du_lieu` (số liệu từ `get_dashboard_status`, `get_do_phu`, `get_club_fill_stats`, `get_phan_bo_nguyen_vong` + số em chưa có chỗ theo lớp; danh sách trắng khoá, không mã/tên/điểm/số bốc thăm) và `dung_html` (thuần, `html.escape`, một tệp tự đủ).
- `api_xuat.py`: `export_bao_cao_tong_hop` (HTML, không ghi đè, từ chối khi chưa có kết quả); `phan_quyen.py`: `giao_vien`; nhật ký thao tác: một dòng tự động, nhãn `nkhd_export_bao_cao_tong_hop` (vi/en).
- Giao diện: khối `<!-- UX1B -->` (`#ux1bPanel`) ngay sau `#gtPanel` ở thẻ Kết quả: chọn lớp (mở bảng Theo lớp), "Xuất theo {cohort_l}", "Báo cáo tổng hợp"; `js/19_ux1b_gv.js`, khoá i18n `ux1b_*`. KHÔNG có nút "In phiếu cả lớp" (XP1, nối ở bước tích hợp I3).
- Test mới: `tests/test_ux1b_l4_bao_cao.py` (7), `tests/test_giao_dien_ux1b_vai_gv.py` (3, Chromium).

## 2026-11-18 — UX1A-L2b fix4: CI #1014 còn 2 job đỏ

- `js/02_van_hanh.js` (`loadHealthReport`), `js/17_viec_tiep_theo.js` (`capNhatViecTiepTheo`, `initViecTiepTheo`): thanh "Việc tiếp theo" dùng lại kết quả `get_data_health_report` vừa có hoặc lần hỏi đang bay, và không tự vẽ lúc `init()`; lúc khởi động chỉ còn MỘT lần gọi (trước: 4).
- `tests/test_ws_nhan.py`: `SUA_CO_Y` của `health_oversubscribed_buoi` khớp câu mới (bỏ gạch ngang ở fix3).

## 2026-11-18 — UX1A-L2b fix3: sửa CI #1013 đỏ

- `js/18_cai_dat.js` (`ux1aVeSauXep`, `ux1aTaiCaiDat`): đọc `(data.config || {}).rules`, hết lỗi JS `Cannot read … 'rules'` khi backend trả `data: {}`.
- `i18n.js`: thêm nhãn nhật ký `nkhd_dat_loai_clb` (vi/en); bỏ gạch ngang nối câu ở `ux1a_ss_huy_chuong_sai`, `ux1a_ss_thieu_tu_do`.
- `i18n_errors.py` (+ `i18n_loi.js` sinh lại): bỏ gạch ngang nối câu ở `so_nhap_canh_bao_huy_chuong_che_do_tat`, `health_oversubscribed_buoi`; `so_nhap_canh_bao_wharton_trong` (vi) lại nói "tắt điểm quyết tâm".
- `index.html`: chữ dự phòng `import_hint` khớp catalog.
- Không thêm test mới; sửa để các test sẵn có qua lại.

## 2026-11-18 — UX1A-L2b fix2 (từ lượt duyệt của lead)

- `get_san_sang_huy_chuong` thêm `huy_chuong_sai` (+ `huy_chuong_sai_vd`): số học sinh có ô không phải huy chương hợp lệ hoặc có huy chương ở CLB Tự do, đọc bằng `fa_daa.kiem_ho_so_huy_chuong` (chỉ đọc, không đổi dữ liệu). Còn > 0 thì `san_sang = false` và bảng sửa tại chỗ nói MỘT dòng "n học sinh có giá trị không phải huy chương … nạp lại sổ có cột Huy chương (Vàng/Bạc/Đồng)" thay vì "Sẵn sàng" (trước đây báo sẵn sàng mà lần chạy vẫn bị chặn).
- Khung "Sau khi xếp": "Mở vòng 2" chỉ hiện khi còn em chưa có chỗ, "Mời danh sách chờ" chỉ khi còn chỗ trống (đang bật thì vẫn hiện để tắt).
- Nút "Hoàn tác" ở thông báo nổi: chữ trắng, gạch chân, rõ trên nền xanh.
- Test: `tests/test_ux1_cai_dat_backend.py` (sổ chế độ thường chưa sẵn sàng; sổ huy chương hợp lệ sẵn sàng VÀ chạy được), `tests/test_giao_dien_ux1_cai_dat.py` (+4).

## 2026-11-18 — UX1A-L8-A: tài liệu, ảnh chụp, bảng "Sau" đo được

- `HUONG_DAN_SU_DUNG.md`: bảng điều hướng thành 4 nhóm; mục mới về thanh "Việc tiếp theo", Cài đặt (ba thẻ), sổ mẫu có huy chương, Vàng/Bạc/Đồng; bỏ số thứ tự thẻ cũ (01–06). `docs/giai_trinh/HUONG_DAN_CHAY.md`, `KICH_BAN_DEMO.md`, `KICH_BAN_VIDEO.md`: cách bật chế độ huy chương theo giao diện mới. `docs/ke_hoach/CLAUDE_CHI_TIET.md`: bản đồ mã (`js/17`, `js/18`, `get_san_sang_huy_chuong`, `dat_loai_clb`, lớp đọc huy chương), số tệp/ca test (339 / 6.845).
- Chữ hiển thị trỏ tới hộp "Tính năng sau khi xếp…" đã bỏ nay trỏ tới Cài đặt / khung "Sau khi xếp": `i18n_errors.py` (`so_nhap_canh_bao_wharton_trong`), `mau_forms_thi_clb/tao_mau_forms.py` (+ `tests/test_fg7_bieu_mau_sau_ket_qua.py`).
- Poster: `poster/DU_LIEU_POSTER.md` (tên thẻ), ảnh giao diện chụp lại (`poster/hinh/giao_dien_*.png`). CHƯA dựng lại `poster_*.pdf/pptx` (cần python-pptx, matplotlib: thư viện chưa có trong môi trường) -> mục "Cần Truong".
- `docs/ke_hoach/ux/chup_luong_chinh.py` viết lại: chụp ảnh mới VÀ in số lần bấm; ảnh trong `docs/ke_hoach/ux/anh/` thay mới (`11_ws_tinh_nang.png` bỏ, `11_cai_dat.png` thêm; `04_phieu.png`, `phieu_mau.pdf` KHÔNG đụng: nhóm B). `UX1_RA_SOAT.md` mục 2b: bảng "Sau" với số đo (nạp→chạy→tải = 4; xử lý em chưa có CLB = 1; GV chủ nhiệm ≤ 2; học sinh 2); dòng phiếu PDF và báo cáo BGH ghi "nhóm B, sau tích hợp".

## 2026-11-18 — UX1A-L5b: ô huy chương nhận Vàng/Bạc/Đồng

- Chế độ huy chương BẬT: ô huy chương của Sổ nhập nhận `Vàng/Bạc/Đồng` (không phân biệt hoa/thường, dấu; cả `vang/bac/dong`, `gold/silver/bronze`), đổi về 60/30/10 ngay ở lớp đọc (`so_nhap.chuan_hoa_chu_huy_chuong`, gọi trong `api_nhap._doc_so_nhap`); giá trị lưu (`wharton_bids`), `fa_daa.kiem_ho_so_huy_chuong` và kết quả xếp không đổi. Chữ lạ vẫn báo `fa_huy_chuong_gia_tri_sai`. Chế độ tắt: không ánh xạ (như cũ). Đường Forms đi qua sổ nhập nên được phủ cùng chỗ.
- Sổ mẫu có huy chương: ô chọn sổ xổ xuống `Vàng,Bạc,Đồng,60,30,10`; Hướng dẫn: "Vàng / Bạc / Đồng hoặc 60 / 30 / 10". Sổ mẫu thường KHÔNG có dòng này nên giữ nguyên (đã so với bản cũ: giá trị ô và quy tắc nhập giống hệt).
- Sửa nhỏ của L5: nút "Bật chế độ huy chương" chỉ hiện khi đang mở một workspace.
- Test mới: `tests/test_ux1_l5b_huy_chuong_chu.py` (9: số vs chữ cho `wharton_bids` VÀ `match_results` giống hệt, hoa/thường/không dấu/tiếng Anh, chữ lạ, chế độ tắt, Hướng dẫn), thêm 1 test giao diện ở `tests/test_giao_dien_ux1_nhap_so.py`.

## 2026-11-18 — UX1A-L5: cảnh báo đúng mức và đúng lời; sổ huy chương sai chế độ; hai sổ mẫu

- Ba cảnh báo "vượt chỉ tiêu" (`health_oversubscribed`, `_buoi`, `_chua_khai_buoi`) từ "info" lên "medium" (vẫn không chặn: chỉ "high" chặn; không chỗ nào chặn theo mức này) và rút còn MỘT câu + MỘT hành động (`i18n_errors.py`).
- Xem trước sổ (`xem_truoc_so_nhap`): sổ có cột Huy chương (`so_nhap.TEN_COT_HUY_CHUONG`, cờ `co_cot_huy_chuong` của `doc_so_nhap`) hoặc cột Loại mà chế độ huy chương TẮT → cảnh báo mới `so_nhap_canh_bao_huy_chuong_che_do_tat` kèm nút "Bật chế độ huy chương" (`#btnBatHuyChuong`: `update_workspace_config {wharton, fa_daa}` rồi đọc thử lại sổ đang chờ; quản trị, có dòng nhật ký; không bật ngầm). Chỉ đổi thông điệp: cái được lưu và cách chạy không đổi (60 ca trùng khít).
- Nạp sổ huy chương khi chế độ tắt: thêm một dòng tóm tắt "n … chưa đặt đủ điểm quyết tâm (huy chương)" trên danh sách gom (5 ví dụ + "và N nữa" giữ nguyên); gợi ý ở khung lỗi chạy nói tới chế độ huy chương.
- "Tải sổ nhập mẫu": giữ nguyên (sổ mẫu thường) + nút mới "Tải sổ mẫu có huy chương" (`tao_so_nhap_mau(output_path, kieu)`, kiểu "huy_chuong" → `che_do_fa=True`; Hướng dẫn nói chế độ phải bật).
- Test mới: `tests/test_ux1_l5_backend.py` (7), `tests/test_giao_dien_ux1_nhap_so.py` (5). Cập nhật theo chủ ý đổi chữ: `tests/test_data_health.py` (mức "medium"), `tests/test_ws_nhan.py` (`SUA_CO_Y` + mã mới), `tests/du_lieu_ws/chu_ui_doi_co_y_t3.json` (`import_hint`).

## 2026-11-18 — UX1A-L3 fix1

- `nhapTatCa()` xoá dòng `#feedbackImportAll` cũ trước khi thử lại (lỗi lần trước không còn dính sau khi nạp thành công); test fail→thử lại→thành công trong `test_giao_dien_upload.py`.
- Thanh "Việc tiếp theo", trạng thái "Xử lý n …": thêm nút PHỤ `#viecTiepTheoNut2` "Xuất kết quả" (cùng hành động với trạng thái "xuất") để sổ mẫu thật (còn em chưa có CLB) vẫn tải kết quả trong 4 lần bấm; test không giả lập trong `test_giao_dien_ux1_tiep_theo.py`.

## 2026-11-18 — UX1A-L3: thẻ Kết quả tra cứu trước, một menu "Xuất…", thông báo nạp sổ một lần

- `#gtPanel` (tra cứu một học sinh) lên ĐẦU thẻ Kết quả, trên `#kqBang`; bỏ liên kết nhảy `#gtNhay` và khoá i18n `gt_nhay`.
- Thẻ "Chi tiết": chỉ hai nút xuất chính hiện sẵn ("Xuất kết quả (Excel)", "Xuất theo lớp"); bốn nút phụ (lý do, nhu cầu, gợi ý chỉ tiêu, biên bản bốc thăm) vào menu `#xuatMenu` "Xuất…" (chỉ có ở chế độ Huy chương). Giữ nguyên id và trình xử lý.
- Nạp sổ: câu kết quả (số CLB, học sinh) chỉ hiện ở hàng của tệp; bỏ dòng `#feedbackImportAll` khi thành công; thông báo nổi chỉ xác nhận "Đã nạp sổ".
- Thanh "Việc tiếp theo": trạng thái "Xuất" bấm là xuất luôn (tuỳ chọn mặc định) → luồng nạp → chạy → tải = 4 lần bấm (test `test_luong_chinh_nap_chay_tai_ket_qua_bon_lan_bam`).
- Test mới: `tests/test_giao_dien_ux1_ket_qua.py` (4). Sửa test cũ theo vị trí: fa_ket_qua, sg11a_ve_sinh (mở menu / chờ ở trạng thái attached), gt4_man_hoc_sinh (bỏ `#gtNhay`), upload, xoa_du_lieu (kết quả nạp ở hàng tệp).

## 2026-11-18 — UX1A-L2b: Cài đặt = một câu hỏi, ba thẻ, lưu ngay

- Mới: thẻ "Chỉ xếp thứ tự" / "Chia 100 điểm" (mặc định) / "Huy chương" (`js/18_cai_dat.js`, thành phần `ux1aTaoThe`) ánh xạ `wharton` + `fa_daa`; lưu ngay bằng MỘT lời gọi `update_workspace_config` (ghi một dòng nhật ký thao tác như mọi lần gọi khi có tài khoản), áp dụng tại chỗ, thông báo "Đã chuyển sang … · Hoàn tác" 10 giây; lỗi hiện dưới thẻ, thẻ không đổi. Một dòng "Cách xét khi đông" sinh từ Tiêu chí xếp; "Thay đổi…" mở mục Nâng cao.
- Một nơi duy nhất: panel `#ux1aCaiDat` (đầu thẻ Quản lý), mục ⋯ "Cài đặt…" (thay "Tính năng sau khi xếp…", hộp `wsMoTinhNang` đã xoá), bước 3 trình tạo workspace (cùng thành phần; ô điểm quyết tâm / huy chương / 4 ô theo dõi bỏ). Ô "Xét điểm quyết tâm" của Tiêu chí xếp bỏ (chỉ tự tắt cờ khi lựa chọn làm nó vô nghĩa).
- Huy chương mà dữ liệu chưa sẵn sàng: sửa tại chỗ (viên "Tự do · Giới hạn · Tuyển chọn" theo CLB, chọn CLB Tự do cho buổi thiếu, điểm sàn) cho tới "Sẵn sàng". Backend mới: `get_san_sang_huy_chuong` (đọc), `dat_loai_clb` (ghi, dùng lại `fa_daa.ghi_thuoc_tinh_clb`); thêm vào `phan_quyen.py`.
- Việc sau khi xếp thành hành động ở thẻ "Chi tiết và xuất tệp" (`#ux1aSauXep`, chỉ ở chế độ Huy chương): Mở vòng 2, Nhận khiếu nại trong [n] ngày, Điểm danh, Mời danh sách chờ, Thu phản hồi.
- Test mới: `tests/test_giao_dien_ux1_cai_dat.py` (10), `tests/test_ux1_cai_dat_backend.py` (7). Viết lại theo thẻ: ws_wharton_giao_dien, a13_13_kiem_nhan, fa_cai_dat, fa_gap1/gap3, fg8_cau_chu, fg1_bat_tinh_nang, sg2_diem_quyet_tam, sg11b, gt2_tieu_chi, gt4_tieu_chi, ws_giao_dien (một test cũ "FA bật, điểm quyết tâm tắt" nay không tạo được từ giao diện; backend vẫn từ chối, test ở test_a13_13_kiem_nhan.py).
- L2: nhóm điều hướng ẩn theo thuộc tính (hidden / vai giáo viên), không theo getClientRects.

## 2026-11-18 — UX1A-L2: thanh bên 4 nhóm

- Thanh bên: 4 nhóm "1. Nạp & xếp" (pipeline), "2. Nhập tay" (fallback, scoring), "3. Kết quả & phiếu" (results, others), "Cài đặt" (admin, chuan_bi). Nút nhóm mở thẻ đầu còn hiện; nhóm không còn thẻ hiện (vai giáo viên, thẻ ẩn) tự ẩn (`capNhatNhomDieuHuong`, `js/01_khung.js`). Mọi `.nav-item[data-tab]` và id giữ nguyên, vẫn bấm được từ nhóm khác. Giáo viên vào "Kết quả" như cũ.
- Cài đặt: "Tiêu chí xếp" + "Thử cấu hình" gấp vào `<details id="ux1aNangCao">` đóng mặc định, đặt SAU phần sửa CLB/học sinh.
- Việc tiếp theo (L1): trạng thái "đã chạy" dùng `has_results` (hoặc `n_matched > 0`).
- Test mới: `tests/test_giao_dien_ux1_dieu_huong.py` (5). Sửa test theo selector: GT2/GT4 mở `#ux1aNangCao` sau khi vào thẻ Quản lý; `test_giao_dien_a14_lop.py` đổi thứ tự thẻ kỳ vọng.

## 2026-11-18 — UX1A-L1: thanh "Việc tiếp theo"

- Mới: `#viecTiepTheo` ở đầu `<main>` (chỉ quản trị) — một nút chính theo trạng thái: nạp sổ → xem cảnh báo chặn → chạy → xử lý n {person_l} chưa có {slot_l} → xuất. Ô "Cần xử lý" ở thẻ "Chi tiết" dùng chung hành động. Mã: `js/17_viec_tiep_theo.js` (mới), móc ở `js/02_van_hanh.js`, `js/03_ket_qua.js`, `js/08_khoi_dong.js`; khoá i18n `ux1a_*`.
- Test mới: `tests/test_giao_dien_ux1_tiep_theo.py` (6). Không đổi backend/thuật toán; invariant 1 trùng khít (60 ca).

## 2026-11-18 — UX1a: rà soát thao tác người dùng (mục mới UX1, Truong duyệt)

- Mới: `docs/ke_hoach/ux/UX1_RA_SOAT.md` (số lần bấm theo 4 nhóm người dùng, 10 vấn đề, đề xuất UX1b/UX1c), ảnh `docs/ke_hoach/ux/anh/`, script chụp `docs/ke_hoach/ux/chup_luong_chinh.py`, `chup_phieu.py` (dữ liệu MÔ PHỎNG).
- Không đổi mã sản phẩm; không test mới.

## 2026-11-18 — GT4 fix 2: các ghi chú nhỏ của checker (L2, L3, L5, L6, L7) + Gate

- L2: thông báo nổi sau khi xuất chỉ nói đã xuất gì (đường dẫn đầy đủ vẫn ở dòng dưới nút) nên không che bảng kết quả.
- L2 (còn sót): nút do JS sinh (`xu_ly_khieu_nai`, `tra_loi_moi`) mang `data-quyen="quan_tri"` — giáo viên không còn thấy.
- L3: thẻ "Bước tiếp theo" ghi "tệp hướng dẫn cài đặt đi kèm" (không còn nhắc `.md`); thẻ đang chọn của hộp Tài khoản thấy rõ; "Đổi mật khẩu" xuống cuối hộp (danh sách + "Thêm tài khoản" lên trước); `HUONG_DAN_CAI_DAT.md` nói rõ trường hợp `.exe` ở thư mục chỉ-đọc.
- L5: nút xác nhận thoát đổi thành "Có, thoát" (không trùng tên nút "Thoát"); ô "Hiện mã" cho mã tra cứu; chỉ còn một dòng chờ khi bị khoá (dòng lỗi `gt1_tam_khoa` bỏ câu "đợi một phút", đồng hồ đếm nói số giây; đổi sang mã khác thì dòng lỗi mất); nhấn dòng kết quả cuộn tức thì tới khung; tên trường cập nhật cả khi nạp muộn sau khi tải lại trang; nút Xem thẳng hàng với ô nhập.
- L6: hộp rộng `min(960px, 92vw)` ở thẻ nhật ký; bộ lọc xếp ngang; nhãn "Ngày" (không còn "năm-tháng-ngày" sai với ngôn ngữ trình duyệt); chi tiết hiện "Vai trò: Quản trị" thay vì `quan_tri`.
- L7: chỉ một nút chính trong khung Thử cấu hình ("So sánh" thành nút phụ).
- Không sửa (quyết định nội dung của Truong): câu "dành một số chỗ cho nhóm được giữ chỗ" của L4 có đúng điều nhà trường muốn nói với phụ huynh không.
- Gate: `ruff` sạch; `kiem_nhanh` 7/7 với 20 seed (60 ca trùng khít); dựng lại `GOI_MINH_CHUNG.docx/.pdf`.
- Test mới: 3 ca vào `test_giao_dien_gt4_man_hoc_sinh.py`/`test_giao_dien_gt4_phien_rieng_tu.py`.

## 2026-11-18 — GT4 fix: sửa các lỗi checker báo (B1–B3, OL1, OL2) và các test hỏng trên CI

- B1 (L3): xoá tệp rỗng `--xoa-tai-khoan` bị commit nhầm ở thư mục gốc.
- B2 (L5, `js/14_giai_trinh.js`): khoá tạm chỉ chặn nút "Xem" khi ô mã học sinh đang là mã bị khoá (backend khoá theo từng mã); đổi mã thì mở lại, quay lại mã cũ thì khoá lại.
- B3 (L5, `style.css`): nút ngôn ngữ trên màn học sinh dùng chữ tối, 14 px, vùng bấm ≥ 40 px (trước: chữ trắng 75 % trên nền sáng, tương phản ~1,1:1).
- OL1 (GT3, `js/16_tai_khoan.js` + `style.css`): lớp phủ đăng nhập/đăng xuất đục (`.tk-kin`) — không còn đọc được tên, mã, CLB học sinh phía sau; hộp "Tài khoản" giữ nền mờ.
- OL2 (GT3, `js/00_nen.js`): mọi lỗi `gt3_can_dang_nhap` (hiện qua toast hoặc ô báo lỗi) hỏi lại phiên ngay → mở hộp đăng nhập, không đợi vòng hỏi 30 giây.
- CI: `test_ws_nhan` thêm 3 mã lỗi GT4 vào danh sách mã mới (`gt4_ngay_sai`, `tep_khong_hop_le`, `tep_khong_mo_duoc`); `i18n.js` đổi "Xuất so sánh (HTML)" → "(trang web)" / "(web page)" và "Seed" → "Draw number" (test văn phong); hai test Chromium dễ chập chờn trên CI chậm được sửa: đo nhãn–ô trong MỘT lần đánh giá và đợi danh sách tài khoản dàn xong; đợi `inert` về false sau khi thoát chế độ học sinh (không nới điều kiện, vẫn khẳng định trạng thái cuối).
- Test mới: `tests/test_giao_dien_gt4_phien_rieng_tu.py` (2), thêm 2 ca vào `tests/test_giao_dien_gt4_man_hoc_sinh.py`.
- Chưa sửa (ghi nhận): `test_a13_12_browser_host.py::test_tai_lai_trang_khong_tat_may_chu` hỏng một lần trên Windows CI, qua trên Linux — cần chạy lại trên CI để biết có chập chờn không.

## 2026-11-17 — GT4-L7: thiết kế lại khung Tiêu chí xếp / Thử cấu hình / so sánh (R8)

- Nguyên nhân gốc: nhãn và ô chọn là các phần tử flex rời nhau trong `.admin-form-grid`, `.check-row` không có CSS, `<ol>` mặc định. Làm lại bằng mẫu `.club-field` (nhãn trên ô) và các biến màu sẵn có (`style.css`, khối "GT4-L7"); `index.html` dựng lại hai khung; không dùng kỹ năng `formal-uidesign` (không có trong môi trường).
- Tiêu chí xếp: hai cột ≥ 1000 px (thẻ thứ tự bên trái với số thứ tự dạng huy hiệu, biểu mẫu bên phải), một cột dưới đó; nhãn trên ô, ô chọn ≤ 360 px, ô văn bản có nhãn + gợi ý một dòng, ô tích có hàng riêng và gợi ý thụt vào, nút Lưu căn phải; dòng "chưa dùng" là danh sách màu xám.
- Thử cấu hình: dải ba bước, hai ô chọn lần cạnh nhau, nút So sánh chính + hai nút xuất phụ, khối "Dùng tiêu chí…" tách bằng đường viền có câu nói rõ chỉ lưu tiêu chí; cảnh báo vàng (không chặn) khi chỉ theo nhóm mà chưa có nhóm, hoặc "nhóm đứng trước điểm" với danh sách rỗng.
- So sánh: `tieu_chi.tom_tat_so_sanh` (một câu chỉ có số, vi/en), `tieu_chi.chenh` (+3 / −2), `so_sanh_lan_chay` thêm `run_at`, `tang`, `tom_tat` (khoá thêm, không đổi khoá cũ); giao diện: câu tóm tắt, hai thẻ lần chạy với tiêu chí hai tầng tách riêng, bảng tiêu đề cố định + số căn phải + chênh lệch có chữ, danh sách đổi chỗ gập mặc định (nút "Hiện danh sách (n)"), cột Buổi chỉ khi nhiều buổi, không in `__mac_dinh__`. Tệp HTML xuất (`dung_html_so_sanh`) có cùng cấu trúc (thẻ, `<details>`, sticky, +/−).
- Cùng nhịp cho khung tra cứu, hộp tài khoản, màn học sinh (lớp `.gt-ui`: nhãn trên ô, chữ ≥ 14 px, ô ≥ 36 px, tương phản ≥ 4,5:1, vòng focus 3 px).
- Ảnh trước/sau ở 1280 px (MÔ PHỎNG): `docs/phien/anh_gt4/l7_{truoc,sau}_{tieu_chi,thu}_1280.png`.
- Test mới: `tests/test_gt4_so_sanh.py` (7), `tests/test_giao_dien_gt4_tieu_chi.py` (13 ca Chromium: 1280/1024 px, nhãn–ô, hai cột, ô tích, thẻ so sánh, cảnh báo, tương phản/cỡ chữ/ô bấm, focus).

## 2026-11-17 — GT4-L6: nhật ký thao tác đọc được (R7)

- `nhat_ky.py` + `api_nhat_ky.py`: lọc phía máy chủ thêm `chi_tu_choi` (kết quả khác `ok`) và `ngay` (`YYYY-MM-DD`, sai dạng → lỗi mới `gt4_ngay_sai` ở `i18n_errors.py`); `get_nhat_ky_thao_tac` trả thêm `hanh_dong_co` (các tên hành động có mặt, cho ô chọn). CSV xuất vẫn DẠNG THÔ (tên hành động, mã kết quả nguyên văn), chỉ thêm hai tham số lọc.
- `js/16_tai_khoan.js` + `i18n.js` (vi+en): nhật ký ra khỏi phần đầu hộp Tài khoản sang thẻ riêng "Nhật ký thao tác" (hai thẻ, thẻ đang mở được giữ khi đổi ngôn ngữ); một từ điển `nkhd_*` (87 hàm có ghi nhật ký), `nkvai_*`, `nkkq_*`, `nkkey_*` với nhãn Việt/Anh, tên lạ giữ nguyên chữ; ô lọc "Thao tác" là `<select>` điền từ `hanh_dong_co`; ô "chỉ bị từ chối hoặc lỗi"; ô ngày; giờ hiện `dd/mm/yyyy hh:mm`; `chi_tiet` hiện `khoá: giá trị`; dòng `tra_cuu_hoc_sinh` không có người → "Học sinh tự tra cứu".
- Sửa test cũ theo L6: `tests/test_giao_dien_gt3_dang_nhap.py::test_nhat_ky_thao_tac_hien_trong_hop_tai_khoan_cua_quan_tri` (mở thẻ nhật ký, nhãn tiếng Việt, chọn hành động bằng `<select>`).
- `docs/giai_trinh/HUONG_DAN_CHAY.md` §8 cập nhật mô tả nhật ký (gói `GOI_MINH_CHUNG` dựng lại ở lô cuối).
- Test mới: `tests/test_gt4_nhat_ky_doc.py` (8 test + từ điển đủ khoá vi/en cho mọi hàm có ghi nhật ký), `tests/test_giao_dien_gt4_nhat_ky.py` (4 test Chromium).

## 2026-11-17 — GT4-L5: màn học sinh và vị trí khung tra cứu (R9)

- Màn học sinh (`index.html`, `js/14_giai_trinh.js`, `style.css`, `i18n.js` vi+en): nhãn thấy được "Mã {person_l}" / "Mã tra cứu" (theo từ vựng workspace), tên workspace nếu có (workspace chưa có trường logo nên chỉ tên), nút đổi ngôn ngữ ngay trên màn, Enter gửi, lỗi thì con trỏ về ô đầu, khoá tạm thì đếm ngược số giây còn lại và khoá nút Xem.
- `api_xuat.tra_cuu_hoc_sinh`: lỗi `gt1_tam_khoa` kèm tham số `giay` (số giây còn lại; thông báo giữ nguyên).
- Thẻ Kết quả: liên kết "Tra cứu một {person_l} ↓" ở đầu thẻ; bấm một dòng của bảng (`js/09_the_xem.js`) mở lời giải thích của em đó ở khung tra cứu (`window.gtMoHocSinh`); khung tra cứu có dải bốn bước (tạo mã → xuất mã/in phiếu → chế độ học sinh → thoát bằng tài khoản quản trị), chỉ quản trị thấy (`data-quyen`).
- "Mở tệp": `api_xuat.mo_tep(path)` mới (mức giáo viên như `mo_thu_muc`, không ghi nhật ký): chỉ mở TỆP có thật trong chỗ xuất và đuôi .html/.csv/.xlsx/.pdf/.docx; lỗi mới `tep_khong_hop_le`, `tep_khong_mo_duoc` (`i18n_errors.py`, đã chạy `tao_i18n_js.py`). Nút "Mở tệp" cạnh "Mở thư mục" sau khi xuất phiếu / mã tra cứu (`chayXuat(..., kemMoTep)` ở `js/03_ket_qua.js`).
- Test mới: `tests/test_giao_dien_gt4_man_hoc_sinh.py` (6 test Chromium, đồng hồ giả `page.clock`), `tests/test_gt4_mo_tep.py` (16 ca).

## 2026-11-17 — GT4-L4: lời giải trình không bị hiểu sai (R5, R6)

- `fa_ly_do.py`: `cau_ly_do_rbda(dong, ten_clb, giong="hoc_sinh")` — giọng `giao_vien` trung tính (ngôi thứ ba), mặc định giữ nguyên từng byte; hằng `CAU_GIU_CHO` (một nguồn) cho câu chú thích chỗ dành riêng. Câu chế độ FA (`cau_ly_do`) không đổi.
- `giai_trinh.py`: hàng `RESERVED` không còn `diem_chuan` (loại `giu_cho`); mỗi buổi có thêm `chu_thich` (câu cố định khi có hàng chỗ dành riêng); `giai_trinh_mot_hoc_sinh(..., giong)`.
- `api_xuat.py`: khung tra cứu (`get_giai_trinh_hoc_sinh`) dùng giọng `giao_vien`; phiếu in và màn học sinh (`tra_cuu_hoc_sinh`) giữ giọng "Em". `phieu_giai_trinh.py`: ô "Chỗ dành riêng" + câu chú thích dưới bảng. `js/14_giai_trinh.js`, `i18n.js` (`gt_chuan_giu_cho`; `kq_desc` vi/en nói rõ bảng không có điểm còn khung tra cứu thì có), `index.html` (phụ đề `kq_desc`).
- Sinh lại `docs/giai_trinh/CA_MAU.md`, `GOI_MINH_CHUNG.docx/.pdf` (câu trong khung tra cứu nay ở giọng trung tính; gói cũng nhận các ghi chú L1/L3).
- Test mới: `tests/test_gt4_cau_giai_trinh.py` (7 test: mặc định giữ từng byte, giọng giáo viên không "Em", RESERVED không số + chú thích ở khung/màn học sinh/phiếu, phụ đề), `tests/test_giao_dien_gt4_giai_trinh.py` (Chromium: ô "Chỗ dành riêng" + chú thích + giọng trung tính).

## 2026-11-17 — GT4-L3: thiết lập tài khoản và lấy lại quyền (R2, R4, D4-4, D4-5)

- `js/16_tai_khoan.js` + `i18n.js` (vi, en): ô nhập lại mật khẩu và ô "Hiện mật khẩu" ở form tạo tài khoản đầu tiên, "Thêm tài khoản" và "Đổi mật khẩu" (lệch → một câu báo lỗi, không gọi backend); sau khi tạo quản trị ĐẦU TIÊN hộp mở lại với thẻ "Bước tiếp theo" (tạo giáo viên / ghi nhớ mật khẩu / cách lấy lại quyền) và con trỏ ở ô tên của "Thêm tài khoản"; khi chưa có tài khoản nào hộp có dòng cảnh báo "tạo quản trị đầu tiên trước khi đưa máy cho học sinh" (D4-5: chỉ bằng lời + nhập lại mật khẩu + tài liệu, không thêm bí mật).
- `recovery.chay_xoa_tai_khoan_dong_lenh` + `main.py` (`--xoa-tai-khoan [app.db] [--yes]`, chạy trước khi nạp pywebview): hỏi gõ `XOA`, sao lưu rồi xoá hết tài khoản; không đường dẫn thì quét mọi workspace cạnh chương trình; bản đóng gói (không console) còn ghi `QUEN_MAT_KHAU_ket_qua.txt`. Không có nút nào trong ứng dụng xoá tài khoản (D4-4).
- Mới: `QUEN_MAT_KHAU.bat` (cạnh `.exe`; hỏi `XOA`, gọi exe với `--yes`, in kết quả), được chép bởi `build_windows.bat` và `.github/workflows/build-windows-exe.yml`. Không kiểm được trên Linux.
- Tài liệu: `HUONG_DAN_CAI_DAT.md` (mục "Quên mật khẩu quản trị"), `docs/giai_trinh/HUONG_DAN_CHAY.md` §8.
- Sửa test cũ theo L3: `tests/test_giao_dien_gt3_dang_nhap.py` điền thêm ô nhập lại mật khẩu.
- Test mới: `tests/test_giao_dien_gt4_tai_khoan.py` (5 test: cảnh báo, nhập lại lệch, hiện/ẩn, thẻ bước tiếp + con trỏ, đổi mật khẩu), `tests/test_gt4_khoi_phuc.py` (5 test, subprocess `main.py --xoa-tai-khoan`: sao lưu, 0 tài khoản, kết quả xếp nguyên, xác nhận sai không xoá, quét workspace).

## 2026-11-17 — GT4-L2: nút hiện ra khớp với vai (R3, D4-1)

- `phan_quyen.py`: `vao_che_do_hoc_sinh` chuyển từ `_GIAO_VIEN` sang `_QUAN_TRI` (D4-1: vào = thoát = quản trị; giáo viên không còn tự khoá được kiosk).
- `index.html`: `data-quyen="quan_tri"` trên `btnGtTaoMa`, `btnGtXuatMa`, `btnGtCheDoHs`, `btnChayVong2`, `btnSubmitWharton`, `btnResetStudentEntry`, `btnDeleteStudent` và khối `.new-student-row` (đều gọi hàm mức quản trị). Các điều khiển GT2 (tiêu chí, chạy thử) nằm trong thẻ Quản lý, đã ẩn với giáo viên. Không bao phủ: nút do JS sinh động trong danh sách (xử lý khiếu nại `xu_ly_khieu_nai`, trả lời mời `tra_loi_moi`) — còn nếu giáo viên bấm thì vẫn bị từ chối và ghi nhật ký.
- Sửa test cũ theo D4-1: `tests/test_gt_tich_hop.py` (bảng quyền `vao_che_do_hoc_sinh` = quản trị; ba test chế độ học sinh đăng nhập bằng quản trị), `tests/test_giao_dien_gt3_hoc_sinh.py` (đăng nhập quản trị trước khi bấm "Chế độ học sinh").
- Test mới: `tests/test_giao_dien_gt4_vai.py` (quét vai giáo viên: bấm mọi nút nhìn thấy, nhật ký không có `gt3_khong_du_quyen`, kiosk không bị khoá; không đạt trên mã cũ) và `tests/test_gt_tich_hop.py::test_giao_vien_khong_vao_duoc_che_do_hoc_sinh`.

## 2026-11-17 — GT4-L1: nhật ký thao tác không giữ mã tra cứu (R1, D4-2, D4-3)

- `nhat_ky.py`: `tra_cuu_hoc_sinh` chỉ giữ `student_id` (`_CHI_GIU`); tham số tên `ma` bị ẩn ở mọi hàm (`_AN`); `get_giai_trinh_hoc_sinh` được ghi (`_GHI_DU_LA_DOC`, chỉ `student_id`, `run_id`).
- `phan_quyen._ghi_nhat_ky`: dòng `tra_cuu_hoc_sinh` ghi `nguoi = NULL, vai = NULL`; mã học sinh chỉ ghi khi là mã có thật (dán mã tra cứu vào ô mã em thì `chi_tiet = {}`).
- `docs/giai_trinh/HUONG_DAN_CHAY.md` §8: ghi chú CSDL cũ có thể còn mã trong nhật ký cũ → tạo lại toàn bộ mã trước khi dùng thật.
- Test mới: `tests/test_gt4_nhat_ky.py` (4 test: quét mọi cột + CSV xuất; ẩn tham số `ma`; một dòng cho lượt xem giải trình; ô mã em dán nhầm).

## 2026-11-17 — GT4-L0: lời giải trình chỉ đọc lần chạy chính thức (R0)

- `api_xuat._giai_trinh_dung_lai`: truy vấn `run_history` qua `loc_chinh_thuc(cur)` (bỏ lần chạy thử). Trước đó, sau một lần "Chạy thử", màn tra cứu, phiếu in và học sinh tự tra cứu hiện kết quả của lần thử thay cho `match_results` (49/120 em lệch).
- Rà các nơi đọc `run_history`: chỉ-chính-thức = `api.get_run_history`, `api_xuat` (lý do FA mới nhất), `fa_sau_xep`, `rbda_priority_pipeline` (lần chạy mới nhất), và nay `_giai_trinh_dung_lai`. Cố ý KHÔNG lọc: `api_tieu_chi` (danh sách/đọc theo run_id/áp dụng lần thử), `api.py` `MAX(run_id)` ngay sau khi ghi (cùng giao dịch), `api_sau_xep` (đọc theo run_id của kết quả đã lưu), `rbda_priority_pipeline` `COUNT(*)` kiểm tra đã chạy chưa (mọi lần chạy đều tính).
- Test mới: `tests/test_gt4_chay_thu_giai_trinh.py` (4 test: giải trình/tra cứu/phiếu in khớp `match_results` sau 1–2 lần thử và sau `ap_dung_tieu_chi`; không đạt trên mã cũ).

## 2026-11-17 — I4 sửa (tích hợp): tên thẻ trong kịch bản demo/video

- `docs/giai_trinh/KICH_BAN_DEMO.md` (bước 10), `KICH_BAN_VIDEO.md` (dòng 9): "thẻ Quản trị" → "thẻ Quản lý" (nhãn thật, i18n `nav_admin`); dựng lại `GOI_MINH_CHUNG.docx/.pdf`.
- Test mới: `tests/test_gt3_tai_lieu.py::test_ten_the_trong_kich_ban_khop_nhan_giao_dien` (mọi "thẻ X" trong hai kịch bản phải là nhãn thẻ có thật).

## 2026-11-17 — I4 (tích hợp GT1+GT2+GT3): ca mẫu và gói minh chứng

- Mới: `du_lieu_test/tao_ca_mau_giai_trinh.py` sinh `docs/giai_trinh/CA_MAU.md` (bộ TEST_0* 120 em MÔ PHỎNG, hạt giống 42): 3 em được nguyện vọng 1, 3 em không (câu giải trình + bảng), 1 lần chạy bị chặn vì thiếu dữ liệu, 1 tiêu chí mâu thuẫn bị từ chối khi lưu, bảng so sánh mặc định với một tiêu chí thử (số em đổi chỗ, theo nhóm, theo CLB). Chỉ dữ kiện và câu của phần mềm, không có nhận xét.
- Mới: `docs/giai_trinh/tao_goi_minh_chung.py` dựng `GOI_MINH_CHUNG.docx` (python-docx, đã có trong requirements-dev) và `.pdf` (Chromium in); hai tệp đã dựng kèm theo.
- Điền các bước "(sau tích hợp)" trong `KICH_BAN_DEMO.md`, `KICH_BAN_VIDEO.md`, `HUONG_DAN_CHAY.md`, `SO_DO_LUONG.md` bằng tên nút thật trên giao diện; `test_gt3_tai_lieu.py::test_kich_ban_khong_con_buoc_cho_tich_hop` thay cho test cũ đòi dấu "(sau tích hợp)".
- Test mới: `tests/test_gt_tich_hop.py::test_i4_*` (3 test: sinh lại CA_MAU.md giống từng byte, mỗi ca khớp đầu ra thật, gói dựng được).

## 2026-11-17 — I3 (tích hợp GT1+GT2+GT3): nhật ký thao tác cho chạy thử, áp dụng tiêu chí, mã tra cứu, phiếu

- Không đổi mã sản phẩm: cơ chế `phan_quyen._boc` + `nhat_ky` đã ghi đúng MỘT dòng cho `run_thu`, `ap_dung_tieu_chi` (lời gọi lồng `update_workspace_config` không ghi thêm), `tao_ma_tra_cuu`, `tao_lai_ma_tra_cuu`, `export_ma_tra_cuu_csv`, `export_phieu_giai_trinh`; giáo viên bị từ chối vẫn để lại một dòng kèm mã lỗi. Test mới (khoá hành vi này): `tests/test_gt_tich_hop.py::test_i3_*` (4 test).

## 2026-11-17 — I2 fix3: trả lời phiên cũ không mở lại lớp phủ học sinh

- `js/16_tai_khoan.js` `capNhat`: bộ đếm lượt hỏi, bỏ trả lời cũ hơn lần hỏi mới nhất (kể cả sau khi quản trị thoát). `js/14_giai_trinh.js`: lớp phủ do `tkPhien` mở lại sẽ đóng khi `che_do_hs` là false. Test mới: `test_giao_dien_gt3_hoc_sinh.py::test_tra_loi_phien_cu_...` (giữ một trả lời 1,5 giây).

## 2026-11-17 — I2 fix1: tải lại trang ở chế độ học sinh

- `api_tai_khoan.get_phien_dang_nhap` trả thêm `che_do_hs`; `js/16_tai_khoan.js` phát sự kiện `tkPhien`; `js/14_giai_trinh.js` mở lại lớp phủ học sinh khi cờ còn bật (trước đó tải lại trang để lại backend khoá mà không có nút thoát). `CLAUDE_CHI_TIET.md`: thêm dòng bản đồ mã GT3 (cờ nằm trong bộ nhớ). Test mới: `test_giao_dien_gt3_hoc_sinh.py::test_tai_lai_trang_...`.

## 2026-11-17 — I2 (tích hợp GT1+GT2+GT3): chế độ học sinh khoá ở backend khi có tài khoản

- `api_tai_khoan.py`: `vao_che_do_hoc_sinh` (giáo viên trở lên; đặt cờ khi CÓ tài khoản) và `thoat_che_do_hoc_sinh(ten, mat_khau)` (công khai; có tài khoản thì chỉ tài khoản quản trị mới thoát được, mọi lý do không vào được trả cùng `gt3_sai_thong_tin`; tên và mật khẩu không vào nhật ký). Không có tài khoản: không khoá gì, như cũ.
- `phan_quyen.py`: khi cờ bật, chỉ `tra_cuu_hoc_sinh`, `thoat_che_do_hoc_sinh`, `get_phien_dang_nhap` chạy được, bất kể phiên đăng nhập (lỗi mới `gt3_che_do_hoc_sinh` trong `i18n_errors.py`).
- `js/14_giai_trinh.js`, `index.html`, `i18n.js`, `style.css`, `js/16_tai_khoan.js`: nút Thoát hỏi tài khoản quản trị khi có tài khoản; sau khi thoát giao diện cập nhật phiên ngay.
- Tests mới: `tests/test_gt_tich_hop.py` (5), `tests/test_giao_dien_gt3_hoc_sinh.py` (3, Chromium). Không đổi hành vi xếp.

## 2026-11-17 — I1 (tích hợp GT1+GT2+GT3): bảng quyền cho hàm GT1/GT2

- `phan_quyen.py`: `tra_cuu_hoc_sinh` → công khai; `get_giai_trinh_hoc_sinh`, `export_phieu_giai_trinh` → giáo viên; `tao_ma_tra_cuu`, `tao_lai_ma_tra_cuu`, `export_ma_tra_cuu_csv` và 7 hàm GT2 (`get_tieu_chi`, `run_thu`, `list_lan_chay`, `so_sanh_lan_chay`, `export_so_sanh_html`, `export_so_sanh_csv`, `ap_dung_tieu_chi`) → quản trị (danh sách so sánh lộ kết quả học sinh khác).
- `tests/test_gt3_phan_quyen.py`: cập nhật danh sách công khai và kiểm các hàm mới. Không đổi hành vi xếp.

## 2026-11-16 — GT1 sửa lỗi CI (không đổi hành vi xếp)

- `i18n.js`: `gt_the_ten` bỏ gạch ngang nối ("{ten} ({ma}), {cohort_l} {lop}"), `gt_khong_co` thành "Không có" / "None", tiếng Anh `gt_lan_chay` bỏ từ "seed".
- `index.html` + `js/14_giai_trinh.js`: lớp phủ học sinh chỉ mang `role="dialog"` / `aria-modal` khi đang mở (trước đây luôn nằm trong DOM làm các test chờ hộp thoại treo).
- `tests/test_ws_nhan.py`: thêm khối `GT1` vào danh sách mã mới sau ảnh chụp (`gt1_*`).

## 2026-11-16 — GT1-L4 (mục cha C3): mã tra cứu và chế độ học sinh tự tra cứu

Không đổi cách xếp (`kiem_nhanh` trùng khít). Số liệu MÔ PHỎNG.
- Bảng MỚI `ma_tra_cuu(student_id PK, ma, tao_luc)` (`rbda_priority_pipeline.py`, sau khối `giu_cho`, `CREATE TABLE IF NOT EXISTS`;
  không có dòng nào cho tới khi quản trị bấm tạo mã). Xoá học sinh / `reset_data` cũng xoá mã (`api_quan_ly.py`).
- `ma_tra_cuu.py` (mới): mã 8 ký tự `secrets`, bảng chữ không ký tự dễ nhầm; không liên quan số khoá bốc thăm.
- API (`api_xuat.py`, khối GT1-L4): `tao_ma_tra_cuu(chi_hs_chua_co=True)`, `tao_lai_ma_tra_cuu(student_id)`,
  `export_ma_tra_cuu_csv(output_path, lop)`, `tra_cuu_hoc_sinh(student_id, ma)` (`hmac.compare_digest`; sai mã và mã học sinh lạ cùng
  lỗi `gt1_ma_sai`; 5 lần sai → `gt1_tam_khoa` 60 giây theo từng mã học sinh, đồng hồ thay được `_gt1_dong_ho`). Lỗi mới: `gt1_ma_sai`,
  `gt1_tam_khoa`, `gt1_chua_co_ma`. Phiếu in (L3) in mã của CHÍNH em khi đã có.
- Giao diện: ba nút ở khung tra cứu (tạo mã, xuất CSV, "Chế độ học sinh tra cứu"); lớp phủ toàn màn hình, phần còn lại của ứng dụng
  `inert`, 60 giây không thao tác thì xoá thẻ, thoát có hỏi lại (`js/14_giai_trinh.js`, `index.html`, `i18n.js` `gt_*`, `style.css`).
- Test mới: `tests/test_gt1_ma_tra_cuu.py` (13 ca), `tests/test_giao_dien_gt1_hoc_sinh.py` (9 ca; fix1: phản hồi về muộn không hiện thẻ em trước cho em sau, `luotHs` huỷ khi gửi lại, hết giờ, mở, thoát).

## 2026-11-16 — GT1-L3 (mục cha C3): phiếu giải trình in cho từng học sinh

Chỉ ĐỌC (`kiem_nhanh` 60 ca trùng khít). Số liệu MÔ PHỎNG.
- `phieu_giai_trinh.py` (mới, hàm thuần): MỘT tệp HTML tự đủ (CSS in, không địa chỉ ngoài, mọi giá trị qua `html.escape`), mỗi học sinh một trang:
  mã, tên, lớp, bảng nguyện vọng của chính em, câu giải thích, cảnh báo "dữ liệu đã đổi" ở mọi trang, cách xin xem lại (số ngày chỉ khi
  khiếu nại BẬT), chỗ trống cho mã tra cứu (L4).
- API `export_phieu_giai_trinh(output_path="", student_ids=None, lop=None)` (`api_xuat.py`): dựng lại lần chạy MỘT lần
  (`_giai_trinh_dung_lai`, tách từ `_giai_trinh_hoc_sinh`) rồi lặp; chỗ đặt theo `_duong_xuat` (không ghi đè); lỗi `gt1_chua_chay`,
  `gt1_khong_co_hoc_sinh`.
- Giao diện: hai nút "In phiếu cho học sinh này" / "In phiếu cả lớp" ở khung tra cứu (`js/14_giai_trinh.js`, `i18n.js` `gt_in_*`).
- Test mới: `tests/test_gt1_phieu.py` (9 ca), thêm 1 ca vào `tests/test_giao_dien_gt1_tra_cuu.py`.

## 2026-11-16 — GT1-L2 (mục cha C3): khung "Tra cứu một học sinh" ở thẻ Kết quả

Chỉ ĐỌC (`kiem_nhanh` 60 ca trùng khít). Số liệu MÔ PHỎNG.
- `js/14_giai_trinh.js` (mới, thêm vào `js/_danh_sach.txt` và `index.html`, khối `<!-- GT1 -->`): ô tìm (có / không dấu), lọc theo lớp,
  thẻ mỗi buổi: nguyện vọng, điểm của chính em, chỗ, mức vào được, câu giải thích, hàng được xếp tô nổi, cảnh báo "dữ liệu đã đổi".
  Chữ vi/en trong `i18n.js` (`gt_*`); CSS cuối `style.css`.
- `api_xuat.get_giai_trinh_hoc_sinh` thêm `ten`, `lop` của CHÍNH em; `search_students(query, lop=None)` thêm lọc lớp (mặc định như cũ).
- Sửa vòng 1 (checker): chọn một em huỷ mọi lần tìm đang bay, kết quả tìm về muộn không vẽ lại danh sách (không lộ tên em khác).
- Test mới: `tests/test_giao_dien_gt1_tra_cuu.py` (6 ca, Chromium).

## 2026-11-16 — GT1-L1 (mục cha C3): động cơ giải trình một học sinh

Chỉ ĐỌC, không đụng đường chạy (cấu hình mặc định giống từng byte: `kiem_nhanh` 60 ca trùng khít). Số liệu MÔ PHỎNG.
- `giai_trinh.py` (mới): `giai_trinh_mot_hoc_sinh` (hàm thuần), `dung_du_lieu_run` (dựng lại lần chạy RB-DA trong bộ nhớ bằng bộ số
  đã khoá; không ghi). Mã kết cục: ACCEPTED, HIGHER_CHOICE_ACCEPTED, FULL_SCORE, FULL_LOTTERY, FULL_GROUP, FULL_WHARTON, RESERVED, NOT_TESTED.
- `fa_ly_do.cau_ly_do_rbda`: câu cho lần chạy thường (FA bật dùng lại `fa_ly_do` đã lưu).
- API `get_giai_trinh_hoc_sinh(student_id, run_id=None)` (`api_xuat.py`): cờ `du_lieu_da_doi` (dấu vân tay khác, dựng lại khác kết quả
  đã lưu); lỗi `gt1_chua_chay`, `gt1_khong_co_hoc_sinh`, `gt1_lan_chay_cu`, `gt1_khong_tim_thay_lan_chay` (`i18n_errors.py`, `i18n_loi.js` sinh lại).
- Sửa vòng 1 (checker): mã NO_CHOICES cho em chưa đăng ký nguyện vọng; `run_id` cũ -> `gt1_lan_chay_cu`; `run_id` lạ -> `gt1_khong_tim_thay_lan_chay`.
- Test mới: `tests/test_gt1_giai_trinh.py` (26 ca).
## 2026-11-17 — GT2-L4 (mục GT2, mục cha A1/Z7-lite): Dùng tiêu chí của một lần chạy thử

Quản trị chọn một lần chạy thử, xem thứ tự tiêu chí bằng lời thường rồi lưu làm tiêu chí đang dùng; lần xếp chính thức
kế tiếp sẽ dùng nó. Chỉ LƯU cấu hình (qua `update_workspace_config`, giữ nguyên khoá ngoài tiêu chí); không chạy xếp,
không chép kết quả thử vào `match_results`. Bất biến 1: mặc định TẮT, `kiem_nhanh.py` 7/7. Số liệu MÔ PHỎNG.

- `api_tieu_chi.py`: `ap_dung_tieu_chi(run_id, slug="")` (chỉ nhận lần chạy thử; lần chính thức hoặc mã lạ → `gt2_lan_chay_khong_co`).
- `index.html`, `js/15_tieu_chi.js`, `style.css`, `i18n.js`: danh sách lần thử có nút "Dùng tiêu chí này cho lần chạy chính thức", thanh xác nhận nội tuyến hiện mô tả L1, nhắc chạy xếp chính thức sau khi lưu.
- Sửa sau soát (fix1): lưu từ luật ĐÃ LƯU, chỉ ghi đè khoá có tác dụng của lần thử (khoá vô tác dụng, nhóm đã nhập giữ nguyên); sau khi lưu luật hiệu lực phải bằng luật lần thử, nếu không thì từ chối `gt2_ap_dung_khong_khop`, không ghi gì.
- Test mới: `tests/test_gt2_ap_dung.py` (8 ca), `tests/test_giao_dien_gt2_thu.py` (+1 ca, fixture chuyển sang chế độ workspace).

## 2026-11-17 — GT2-L3 (mục GT2, mục cha A1/Z7-lite): So sánh hai lần chạy

So sánh một lần chạy thử với lần chính thức (hoặc hai lần thử) ngay trong thẻ Quản lý. Chỉ ĐỌC, không bốc thăm, không ghi
`match_results`. Bất biến 1: mặc định TẮT, `kiem_nhanh.py` trùng khít. Số liệu MÔ PHỎNG.

- `tieu_chi.py`: `so_sanh_lan_chay(a, b, ctx)` (hàm thuần: tổng quan, từng CLB gồm điểm chuẩn, nhóm ưu tiên, lớp, danh sách em
  đổi chỗ; chỉ so các buổi cả hai lần cùng có) và `dung_html_so_sanh` (HTML một tệp, không nạp gì từ ngoài, mọi chữ qua `escape`).
- `api_tieu_chi.py`: `list_lan_chay`, `so_sanh_lan_chay(run_a, run_b=None)`, `export_so_sanh_html`, `export_so_sanh_csv`
  (UTF-8 có BOM). Lần chính thức cũ không còn dòng kết quả → `gt2_so_sanh_lan_cu` (không bịa số); mã mới `gt2_lan_chay_khong_co`.
- Giao diện: khung "Thử cấu hình" (`index.html`, `js/15_tieu_chi.js`, `style.css`, khoá `gt2_thu_*` / `gt2_ss_*` trong `i18n.js`).
- Sửa kèm: `tests/test_ws_nhan.py` (khối GT2 cho mã lỗi mới của L1–L3), chữ gợi ý ô nhóm trong `index.html` khớp danh mục.
- Test mới: `tests/test_gt2_so_sanh.py` (9 ca, kiểm tay 10 em), `tests/test_giao_dien_gt2_thu.py` (4 ca, Chromium).

## 2026-11-17 — GT2-L2 (mục GT2, mục cha A1/Z7-lite): Chạy thử tiêu chí (ghi riêng, không công bố)

Chạy thử một bộ tiêu chí trong giới hạn đã duyệt (D-GT1) mà KHÔNG đụng kết quả chính thức. Mặc định TẮT: chưa ai chạy
thử thì mọi hành vi y như cũ. Bất biến 1: `kiem_nhanh.py --co-so origin/main --so-seed 20` trùng khít 60 ca. Số liệu MÔ PHỎNG.

Sửa vòng 1 (fix1): `run_thu` quyết định FA theo luật HIỆU LỰC (đã trộn luật đã lưu với luật thử), không theo luật đã lưu; luật thử chỉ nhận khoá của `LUAT_XEP_MAC_DINH` (khoá lạ → `gt2_tieu_chi_khong_hop_le`). +4 ca trong `tests/test_gt2_chay_thu.py`.
- Lược đồ (D-GT8, idempotent, sao lưu trước): cột `run_history.loai_chay` (NULL = chính thức, 'thu' = chạy thử; thêm vào
  `di_tru_schema` và `CREATE TABLE`), bảng `ket_qua_thu` (sau khối `fa_phan_hoi`).
- Mới: `PipelineAPI.run_thu(rules_thu, chi_buoi=None)` ở `api_tieu_chi.py`: kiểm luật bằng `cau_hinh_ws._chuan_hoa`,
  dùng đúng bộ số bốc thăm đã khoá (không vẽ lại, không khoá), giải + hai chốt như lần chính thức, ghi MỘT giao dịch
  (một dòng `run_history` + `ket_qua_thu`); không ghi `match_results`, `ket_qua_truoc`, `dau_van_tay_chay`, `stb_lock`, `fa_*`,
  tệp xuất. Trợ giúp dùng chung `loc_chinh_thuc`, `run_chinh_thuc_moi_nhat` (`rbda_priority_pipeline.py`).
- Mọi chỗ đọc `run_history` chính thức bỏ lần thử: `get_run_history`, `api_xuat._doc_ly_do_moi_nhat`, `fa_sau_xep.run_goc_theo_buoi`.
- Mã lỗi mới (`i18n_errors.py`, `i18n_loi.js` sinh lại): `gt2_tieu_chi_khong_hop_le`, `gt2_chua_co_lan_chinh_thuc`,
  `gt2_thu_chua_ho_tro_fa` (chế độ huy chương chưa hỗ trợ chạy thử), `gt2_thu_stb_chua_day`.
- Test mới: `tests/test_gt2_chay_thu.py` (25 ca).

## 2026-11-17 — GT2-L1 (mục GT2, mục cha A1/Z7-lite): Tiêu chí xếp bằng lời thường

Chỉ ĐỌC và hiển thị; thuật toán, CSDL và tệp xuất không đổi. Không có tiêu chí mới: chỉ mô tả luật xếp đã có
(`LUAT_XEP_MAC_DINH`) theo luật hiệu lực (`luat_xep_hieu_luc`), và cho chọn lại trong đúng tập giá trị đã duyệt (D-GT1).
Bất biến 1: `kiem_nhanh.py --co-so origin/main --so-seed 20` trùng khít 60 ca. Số liệu trong test là MÔ PHỎNG.
- Mới: `tieu_chi.py` (`mo_ta_tieu_chi`, `cac_lua_chon_hop_le`, `tieu_de_tang`, `KHOA_NGOAI_LUAT_XEP`, `GHI_CHU`),
  `api_tieu_chi.py` (`TieuChiMixin.get_tieu_chi`, nối vào `PipelineAPI`), `js/15_tieu_chi.js`, khung "Tiêu chí xếp" ở thẻ
  Quản lý (`index.html`, khối `GT2`), chuỗi `gt2_tc_*` trong `i18n.js`. Lưu vẫn qua `update_workspace_config`.
- Kiểm khoá lạ / giá trị lạ của `rules` đã có sẵn ở `cau_hinh_ws._chuan_hoa` (báo `ws_du_lieu_sai`), nên chưa thêm mã
  `gt2_tieu_chi_khong_hop_le`; lô L2 thêm khi `run_thu` cần.
- Test mới: `tests/test_gt2_tieu_chi.py` (107 ca: mọi tổ hợp luật, khoá chặt tập khoá, API), `tests/test_giao_dien_gt2_tieu_chi.py`
  (6 ca Chromium). `CLAUDE_CHI_TIET.md` hàng `tests/`: 300 tệp, 6.430 ca.
## 2026-11-16 — GT3 CI fix2
- `tests/test_gt3_tai_khoan.py::test_recovery_cho_lenh_dong_dong_goi`: đọc đầu ra của lệnh con bằng `encoding="utf-8"` (nghiêm ngặt) thay vì bảng mã mặc định của máy (Windows cp1252 làm luồng đọc ném lỗi). Không sửa mã sản phẩm.

## 2026-11-16 — GT3 CI fix1 (Windows)
- `recovery.py` (dòng lệnh): ép stdout/stderr sang UTF-8 (`reconfigure`, có kiểm `hasattr`) — `--help` không còn UnicodeEncodeError trên console cp1252.
- `api_tai_khoan._co_tai_khoan_nho`: đã có giá trị nhớ thì làm mới với thời gian chờ khoá 50 ms, thất bại do khoá thì 5 s sau mới thử lại; `tao_tai_khoan` cập nhật bộ nhớ ngay. Lần đầu (chưa từng đọc được) vẫn đóng khi lỗi. Đo trên Linux, CSDL bị khoá, tài khoản tắt: cổng cộng ≈ 0,05 s mỗi lời gọi (trước: ≈ 3 s).
- Test mới: `test_recovery_help_chay_duoc_tren_console_cp1252`, `test_cong_khong_cong_them_thoi_gian_cho_khi_csdl_bi_khoa`.

## 2026-11-16 — GT3-L4 fix1: luồng nạp sổ mẫu đúng chế độ huy chương
- `HUONG_DAN_CHAY.md` mục 4–6, `KICH_BAN_DEMO.md` bước 3–8, `KICH_BAN_VIDEO.md` bước 4–7: sổ `SO_NHAP_FA_MAU_120HS.xlsx` phải nạp vào không gian đã tích "Xếp theo loại CLB và huy chương" (chọn lúc tạo); bỏ bước "Phóng cho đủ 100" và lời nhắc `fa_cot_bo_qua`; số FA001/FA002 chạy lại thật (hạt giống 42); ghi chú câu giải thích từng học sinh đã có ở chế độ này.
- Test mới trong `tests/test_gt3_tai_lieu.py` (22 ca): tài liệu dặn bật chế độ trước khi nạp; số liệu FA001/FA002 trong tài liệu khớp một lần nạp + chạy thật (hạt giống 42).

## 2026-11-16 — GT3-L4 (mục cha E1-lite; ngoài sổ): bộ tài liệu minh chứng `docs/giai_trinh/`
- Tệp mới: `VAI_TRO_AI.md`, `SO_DO_LUONG.md` + `so_do_luong.svg` (dựng bằng `ve_so_do.py`, chỉ thư viện chuẩn), `HUONG_DAN_CHAY.md` (các bước 1–7 đã chạy thật), `DU_LIEU_DAU_VAO.md` (trích nguyên văn thông báo lỗi từ `i18n_errors.py`), `PHAN_CONG.md` (mẫu trống), `KICH_BAN_DEMO.md`, `KICH_BAN_VIDEO.md` (bước cần tích hợp đánh dấu "(sau tích hợp)").
- Toàn bộ nhãn "dữ liệu mô phỏng"; không có nhận xét hay kết luận (phần đó học sinh tự viết).
- Test mới: `tests/test_gt3_tai_lieu.py` (20 ca: tệp tồn tại, có chữ "mô phỏng", không lộ mã nội bộ, mã lỗi và đường dẫn nhắc tới có thật, trích đúng nguyên văn, `PHAN_CONG.md` trống).

## 2026-11-16 — GT3-L3 fix1: nhật ký ghi đúng CSDL, không chặn lời gọi
- `phan_quyen._boc` chụp `db_path` TRƯỚC lời gọi (open/delete_workspace không còn đẩy dòng nhật ký sang workspace khác; CSDL đã dời đi thì không tạo tệp rỗng).
- `nhat_ky.ghi` chờ khoá ghi tối đa 1 s; quá hạn thì luồng nền ghi bù khi khoá nhả. Lọc `nguoi` không phân biệt hoa/thường (NFC + casefold).
- Test mới: 4 ca trong `tests/test_gt3_nhat_ky.py` (28 ca).

## 2026-11-16 — GT3-L3 (mục cha E2; ngoài sổ): nhật ký thao tác (chỉ thêm)

Chỉ ghi khi bảng `tai_khoan` có dòng; chưa có tài khoản thì không ghi gì (chỉ thêm `CREATE TABLE/TRIGGER IF NOT EXISTS`). Chỉ là báo cáo, không dính `compute_club_priority`. `kiem_nhanh` 7/7, 60 ca trùng khít.
- Bảng `nhat_ky_thao_tac(id, luc, nguoi, vai, hanh_dong, ket_qua, chi_tiet)` (duyệt D-GT8) + hai trigger chặn UPDATE / DELETE; `reset_data` và các đường xoá khác không đụng tới.
- Ghi ở MỘT chỗ: lớp bọc của cổng phân quyền (`phan_quyen.py:_boc`) cho lời gọi ngoài cùng của mọi hàm GHI (cả hai vai: nhập nguyện vọng, điểm, điểm danh, khiếu nại, xuất tệp…), đăng nhập (đúng / sai / bị khoá), đăng xuất, tạo / đổi mật khẩu / xoá tài khoản. Hàm chỉ đọc (`get_*`, `list_*`, `search_*`…) không ghi (`nhat_ky.nen_ghi`). Lời gọi bị từ chối cũng ghi, `ket_qua` = mã lỗi (`gt3_khong_du_quyen`, `gt3_can_dang_nhap`).
- `chi_tiet` = tóm tắt tham số dạng JSON ≤ 300 ký tự: bỏ tham số giống mật khẩu / mã bí mật / nội dung tệp base64, chuỗi dài chỉ ghi độ dài, danh sách dài chỉ ghi số phần tử; `doi_mat_khau` không ghi gì. Đăng nhập sai chỉ ghi tên khi là tài khoản có thật (tránh lưu mật khẩu gõ nhầm vào ô tên).
- Ghi nhật ký lỗi chỉ đưa cảnh báo vào log (không kèm tham số), kết quả thao tác chính không đổi.
- API mới (`api_nhat_ky.py`, chỉ quản trị): `get_nhat_ky_thao_tac(page, page_size, nguoi, hanh_dong)` (mới nhất trước, 1..500 dòng/trang), `export_nhat_ky_thao_tac_csv(path, nguoi, hanh_dong)` (UTF-8 có BOM, cũ nhất trước). Mã lỗi mới `gt3_loi_nhat_ky`.
- Giao diện: mục "Nhật ký thao tác" (lọc, phân trang, xuất CSV) ngay trong hộp Tài khoản của quản trị (không thêm tab con vào Quản lý, vì test tab con khẳng định đúng danh sách tab).
- Test mới: `tests/test_gt3_nhat_ky.py` (24), thêm 1 ca vào `tests/test_giao_dien_gt3_dang_nhap.py`.
- `tests/test_ws_nhan.py`: danh sách mã lỗi mới sau ảnh chụp cho phép thêm tiền tố `gt3_` (các mã tài khoản / nhật ký).

## 2026-11-16 — GT3-L2 fix1: cổng phân quyền đóng khi đọc bảng tài khoản hỏng

`api_tai_khoan.py:_co_tai_khoan_nho`: bộ nhớ đệm theo từng CSDL (`_co_tk_nho`); đọc hỏng (vd. "database is locked") mà CSDL đó chưa từng đọc được thì coi như ĐÃ CÓ tài khoản (từ chối `gt3_can_dang_nhap`); thiếu bảng = chưa có tài khoản. `api.py` mồi bộ nhớ đệm sau `init_db` trong hàm khởi tạo. Test mới (6) trong `tests/test_gt3_phan_quyen.py`.

## 2026-11-16 — GT3-L2 (mục cha E1-lite; ngoài sổ): cổng phân quyền trung tâm

Chỉ có tác dụng khi bảng `tai_khoan` có dòng; chưa có tài khoản thì mọi hàm chạy y như trước (kết quả, ngoại lệ không đổi). Chỉ là điều khiển truy cập, không dính `compute_club_priority`.
- `phan_quyen.py`: bảng `QUYEN` phân mọi hàm công khai của `PipelineAPI` vào `cong_khai` (5 hàm đăng nhập/tài khoản, tự kiểm bên trong) / `giao_vien` (xem, xuất, nhập điểm, điểm danh, nhập hộ nguyện vọng tại chỗ, khiếu nại/phản hồi) / `quan_tri` (ghi dữ liệu, cấu hình, xoá, nạp tệp, workspace, tài khoản).
  `ap_dung_cong(PipelineAPI)` gọi ở cuối `api.py` bọc từng hàm ở cấp lớp, nên pywebview và `browser_host.py` đi qua cùng một cổng. Chỉ kiểm ở lời gọi ngoài cùng (hàm công khai gọi hàm công khai bên trong không bị kiểm lại).
  Chưa đăng nhập → `gt3_can_dang_nhap`; sai vai → `gt3_khong_du_quyen` với `params.hanh_dong`; hàm chưa có trong bảng bị từ chối cả với quản trị (đóng khi lỗi). Mỗi lời gọi bị kiểm đều làm mới giờ nghỉ 15 phút.
  `api_tai_khoan.py`: thêm `_co_tai_khoan_nho` (không ném lỗi; CSDL tạm không đọc được thì dùng kết quả đọc lần trước).
- Giao diện: `body[data-vai]` + `[data-quyen="quan_tri"]` ẩn các tab Xếp CLB / Quản lý / Chuẩn bị đợt và nút không gian làm việc khỏi giáo viên; giáo viên đang ở tab bị ẩn thì được đưa về Kết quả. Backend vẫn là cổng thật.
- Test mới: `tests/test_gt3_phan_quyen.py` (17), `tests/test_giao_dien_gt3_phan_quyen.py` (3). Test liệt kê hàm công khai sẽ ĐỎ ở nhánh tích hợp cho tới khi hàm của GT1/GT2 được phân loại (đúng thiết kế, mục I1).

## 2026-11-16 — GT3-L1 fix1: chuẩn hoá Unicode NFC cho tên và mật khẩu

`tai_khoan.py`: `chuan_hoa_ten`, `_khoa_ten`, `bam_mat_khau` chuẩn hoá NFC (stdlib `unicodedata`) → tên NFD trùng tên NFC bị chặn (`gt3_ten_da_co`), đăng nhập bằng NFD được; mật khẩu NFC/NFD băm như nhau (mật khẩu ASCII/NFC cũ không đổi). Tên lưu dạng NFC.
Test mới (3): `test_ten_unicode_nfd_trung_nfc_va_dang_nhap_duoc`, `test_ten_nfd_duoc_luu_dang_nfc`, `test_mat_khau_nfc_nfd_nhu_nhau` trong `tests/test_gt3_tai_khoan.py`. `kiem_nhanh` 7/7, 60 ca trùng khít.

## 2026-11-16 — GT3-L1 (mục cha E1-lite; ngoài sổ): tài khoản và đăng nhập (quản trị / giáo viên)

Tuỳ chọn MỚI, mặc định TẮT: bảng `tai_khoan` rỗng thì phần mềm chạy y như trước (không màn đăng nhập; chỉ thêm `CREATE TABLE IF NOT EXISTS`).
`kiem_nhanh` 7/7, 60 ca trùng khít. Số liệu MÔ PHỎNG. Chỉ là điều khiển, không dính `compute_club_priority` (bất biến 2).
- Bảng `tai_khoan(ten, vai, bam, muoi, tao_luc)` (duyệt D-GT8). Mật khẩu băm PBKDF2-SHA256 200.000 vòng + muối ngẫu nhiên; so sánh `hmac.compare_digest`;
  mật khẩu / băm / muối không bao giờ được trả ra, ghi nhật ký hay đưa vào tham số lỗi. Tối thiểu 8 ký tự.
- API mới (`api_tai_khoan.py`, mixin của `PipelineAPI`): `get_phien_dang_nhap`, `tao_tai_khoan`, `dang_nhap`, `dang_xuat`, `doi_mat_khau`,
  `xoa_tai_khoan`, `liet_ke_tai_khoan`. Tài khoản đầu tiên phải là quản trị, không cần đăng nhập, và người tạo được đăng nhập luôn; các tài khoản sau cần phiên
  quản trị. Không xoá quản trị cuối. 5 lần sai liên tiếp (theo từng tên) → khoá 60 giây. Nghỉ 15 phút → đăng xuất (đồng hồ tiêm được `api._dong_ho`;
  hàm nội bộ `_hoat_dong()` để cổng phân quyền L2 làm mới giờ nghỉ). Phiên nằm trong bộ nhớ, gắn với đường dẫn CSDL đang mở (đổi workspace là hết hiệu lực).
- Khôi phục: `recovery.xoa_tai_khoan_sau_sao_luu(db)`, `RecoveryAPI.xoa_tai_khoan_sau_sao_luu`, và `python recovery.py --xoa-tai-khoan <app.db>`: sao lưu bằng
  SQLite Backup API rồi xoá toàn bộ tài khoản (quên mật khẩu; quyền = có máy trong tay).
- Giao diện `js/16_tai_khoan.js`: màn đăng nhập chắn giao diện khi đã có tài khoản mà chưa đăng nhập; thanh bên có tên + vai + Đăng xuất + nút "Tài khoản"
  (hộp: tạo quản trị đầu tiên / đổi mật khẩu / quản trị tạo, xoá tài khoản). Khác kế hoạch: hộp mở từ thanh bên, không phải tab con của Quản lý (để không đổi tab con hiện có).
- Mã lỗi `gt3_*` (14) trong `i18n_errors.py`; khoá `tk_*` trong `i18n.js`.
- Test mới: `tests/test_gt3_tai_khoan.py` (42 ca), `tests/test_giao_dien_gt3_dang_nhap.py` (6 ca). `CLAUDE_CHI_TIET.md` hàng `tests/`: 300 tệp, 6.365 ca.

## 2026-11-15 — GT-KH (kế hoạch, ngoài sổ; mục cha C3, A1, E1, E2): trả lời góp ý của hội đồng

Chỉ tài liệu, mã không đổi. Đối chiếu góp ý vòng trước với kho mã và chia việc cho 3 nhóm tự động (mỗi nhóm: Opus dẫn,
Sonnet viết, Sonnet soát), chạy đến khi xong và CI xanh. Quyết định D-GT1…D-GT9 của Truong (15/11/2026), gồm duyệt đổi
cấu trúc CSDL (quy tắc 7) cho `ma_tra_cuu`, `run_history.loai_chay`, `ket_qua_thu`, `tai_khoan`, `nhat_ky_thao_tac`.
- Mới: `docs/ke_hoach/GT_KE_HOACH.md`, `docs/ke_hoach/gt/GT1_GIAI_TRINH.md`, `GT2_TIEU_CHI.md`, `GT3_QUYEN_TAI_LIEU.md`,
  `docs/phien/GT_GIAO_THUC.md`, `docs/phien/claude__determined-allen-kig6ud.md`.
- Test mới: không có (chỉ tài liệu).

## 2026-11-14 — FA-SC-L4 (FA-SC-2, kế hoạch P1-3): phiếu xác nhận theo lớp cho giáo viên chủ nhiệm

Chỉ bộ chuyển đổi, kiosk không đổi. Tuỳ chọn MỚI, mặc định TẮT: không có nó thì đầu ra giống từng byte (`chuyen_fa_daa` trên đợt giả
với danh sách trường + `can_xu_ly` + `bao_cao_clb` bật, HEAD trước lô và sau lô: 10 tệp, 0 khác; `kiem_nhanh` 7/7, 60 ca trùng khít). Số liệu MÔ PHỎNG.
- `chuyen_fa_daa(..., phieu_lop=False)` và cờ `--phieu-lop`: thư mục `PHIEU_XAC_NHAN_LOP/`, mỗi lớp một tệp `<lớp>.xlsx`, mỗi em MỘT khối:
  nguyện vọng đã lưu từng ngày (kèm huy chương), ba huy chương, bài thi nhận được và "Tính" / "Không tính — lý do" (không tick thi,
  không xếp CLB đó, bài lần hai bị bỏ, xếp CLB Tuyển chọn mà chưa nhận bài). Lớp lấy từ danh sách trường (L1) hoặc cột lớp của phiếu;
  em chưa có lớp vào tệp "Chưa có lớp". Không điểm (cả điểm của chính em), không số bốc thăm, không email, không dữ liệu lớp khác.
  Hàm mới `lap_phieu_lop`, `ghi_phieu_lop`. Kết quả có thêm khoá `phieu_lop`. Chỉ là báo cáo (bất biến 2).
- Test mới: `tests/test_fa_sc_l4_phieu_lop.py` (9 ca). `CLAUDE_CHI_TIET.md` hàng `tests/`: 297 tệp, 6.255 ca.

## 2026-11-14 — FA-SC-L3 (FA-SC-4b, kế hoạch P1-4): báo cáo theo CLB cho giáo viên CLB

Chỉ bộ chuyển đổi, kiosk không đổi. Tuỳ chọn MỚI, mặc định TẮT: không có nó thì đầu ra giống từng byte (so `demo_t4m.py` thường
và `--day-du`, và `chuyen_fa_daa` trên đợt giả, ở HEAD trước lô này: 0 khác; `kiem_nhanh` 7/7, 60 ca trùng khít). Số liệu MÔ PHỎNG.
- `chuyen_fa_daa(..., bao_cao_clb=False)` và cờ `--bao-cao-clb` (cần tệp bài thi): thư mục `BAO_CAO_CLB/`, mỗi CLB có đề thi một tệp
  `<club_id>.xlsx` (hai sheet: "Phiếu thi bị bỏ" = email không có trong danh sách đăng ký đã làm bài CLB này; "Chưa có bài thi" =
  mã em xếp CLB Tuyển chọn này mà chưa có bài). Không điểm, không số bốc thăm, không dữ liệu CLB khác. Hàm mới `lap_bao_cao_clb`,
  `ghi_bao_cao_clb`; `phan_tich_chi_thi(..., bo_phieu=None)` ghi lại CLB của phiếu bị bỏ (chỉ khi được yêu cầu). Kết quả có thêm
  khoá `bao_cao_clb`. Chỉ là báo cáo (bất biến 2).
- Test mới: `tests/test_fa_sc_l3_bao_cao_clb.py` (6 ca). `CLAUDE_CHI_TIET.md` hàng `tests/`: 296 tệp, 6.246 ca.

## 2026-11-14 — FA-SC-L2 (FA-SC-4, kế hoạch P1-2): sheet "Cần xử lý" trong BANG_DIEM.xlsx

Chỉ bộ chuyển đổi, kiosk không đổi. Tuỳ chọn MỚI, mặc định TẮT: không có nó thì đầu ra giống từng byte (so `demo_t4m.py` thường
và `--day-du` ở HEAD trước lô này: 42 tệp, 0 khác; `kiem_nhanh` 7/7, 60 ca trùng khít). Số liệu MÔ PHỎNG.
- `chuyen_fa_daa(..., can_xu_ly=False)` và cờ `--can-xu-ly` (cần tệp bài thi): hàm mới `lap_can_xu_ly` gom thành dòng việc
  [(mã, vấn đề, ai xử lý, việc cần làm)] — làm bài CLB này mà chưa thi CLB em xếp (hai cảnh báo rời gộp MỘT dòng, nêu cả hai CLB);
  chỉ làm bài không xếp / chỉ chưa thi; có bài mà không tick thi; bài thi gửi từ email ngoài danh sách (dòng nêu email, gửi quản
  trị viên); CLB Tự do đứng trước CLB Tuyển chọn em đã thi; giữ chỗ em không xếp CLB đó (gửi giáo viên CLB). `ghi_bang_diem(...,
  can_xu_ly=None)` thêm sheet "Cần xử lý" (Mã HS, Họ tên, Vấn đề, Ai xử lý, Việc cần làm); kết quả có thêm khoá `can_xu_ly`. Sheet
  "Cảnh báo" và danh sách cảnh báo giữ nguyên. Chỉ là báo cáo, không đi vào Sổ nhập hay khoá ưu tiên.
- Từ rà soát L1: `doi_chieu_danh_sach_truong` báo một dòng khi một email có ở hai mã trong danh sách trường (trước đây lặng lẽ lấy mã đầu).
- `du_lieu_test/su_co/chung.py`: `chay(..., can_xu_ly=False)`; d04, d06, d07 thêm dòng "FA-SC L2" (số cũ không đổi): d06 hai cảnh báo
  -> một dòng, d04 một dòng nêu email lạ + một dòng của em, d07 một dòng Tự do đứng trước Tuyển chọn.
- Test mới: `tests/test_fa_sc_l2_can_xu_ly.py` (9 ca).
- Chưa làm (cần Truong): "đổi nguyện vọng sau giờ thi" (phiếu đăng ký không có giờ nộp, cần đổi biểu mẫu); d05 (so tên gõ với tên danh
  sách cần câu hỏi lớp/họ tên trong biểu mẫu thi).

## 2026-11-14 — FA-SC-L1 (FA-SC-6, kế hoạch P1-1): danh sách học sinh của trường làm đầu vào bộ chuyển đổi

Chỉ bộ chuyển đổi (`mau_forms_thi_clb/`), kiosk không đổi. Tuỳ chọn MỚI, mặc định TẮT: không có nó thì đầu ra giống từng byte
(so `demo_t4m.py` thường và `--day-du`, và một đợt đường B 120 em giả; `kiem_nhanh` 7/7, 60 ca trùng khít). Số liệu MÔ PHỎNG.
- `chuyen_fa_daa(..., danh_sach_truong=CSV)` và cờ `--danh-sach-truong` (chỉ đường B): CSV `student_id, class_id[, email]` đọc bằng
  `danh_sach_chua_dang_ky.doc_danh_sach_truong` (hàm mới, `LoiDanhSach` nếu thiếu cột / rỗng). Hàm mới
  `doi_chieu_danh_sach_truong`: mã gõ không có trong danh sách → một dòng cảnh báo; danh sách có cột email → thay mã gõ nhầm
  bằng mã của danh sách và báo chỗ khác (nên mã trùng bạn không còn làm kiosk từ chối); hai email cùng một mã → một dòng nêu
  cả hai email; `class_id` điền vào cột Lớp có sẵn của Sổ nhập (cột Sổ nhập không đổi). Hàm `ghi_chua_dang_ky` ghi
  `CHUA_DANG_KY.xlsx` (sheet "Chưa đăng ký" theo lớp, sheet "Thiếu ngày"); kết quả có thêm khoá `bao_cao_danh_sach`. Chỉ là báo cáo
  và điền lớp, không đổi điểm hay thứ hạng.
- `du_lieu_test/su_co/chung.py`: `chay(..., danh_sach_truong=None)`, `danh_sach_that`, `ghi_danh_sach` (mặc định TẮT; số cũ của
  d01–d14 không đổi). d01, d02, d03, d14 thêm các dòng "[có danh sách trường]": d03(a) không còn bị kiosk chặn, d14 từ 120/120
  em không lớp xuống 0/120, d01 và d02 có em trong báo cáo.
- Test mới: `tests/test_fa_sc_l1_danh_sach.py` (7 ca).
- Chưa làm (cần Truong): đường A (CSV List) chưa dùng được với danh sách trường (báo lỗi rõ); chưa nối vào tab "Chuẩn bị đợt".
## 2026-11-15 — FA-SC-L5 (FA-SC-10 / P2-1, Truong duyệt 15/11 kể cả bảng mới `stb_buoi`): khoá thứ tự bốc thăm THEO NGÀY

Sửa mã sản phẩm (kiosk). Mọi số liệu là MÔ PHỎNG. Cấu hình mặc định giữ từng byte lần chạy ĐẦU: `kiem_nhanh --co-so origin/main
--so-seed 20` = 7/7, 60/60 trùng khít.
- **Việc**: lần chạy đầu gọi đúng `sinh_stb_theo_buoi` rồi LƯU thứ tự từng ngày vào bảng mới `stb_buoi(buoi, student_id, so)`
  (cùng giao dịch với kết quả; `run_history` không đụng). Lần chạy sau giữ thứ tự tương đối của em cũ ở MỌI ngày và chèn đều em
  mới từng ngày (`stb_theo_buoi_da_khoa` → `chen_stb_cho_hoc_sinh_moi`, seed `_seed_cua_buoi(seed, buoi)`). Ba nơi đọc cùng một
  nguồn: lần chạy (`run_rbda_nhieu_buoi`, tham số mới `stb_buoi_da_khoa=None` = cách cũ), `get_so_boc_tham_theo_buoi`, vòng 2
  (`_du_lieu_vong_2`). Một buổi hoặc chế độ khác `stb_ngay`: không lưu, không đổi.
- **Thay đổi hành vi có chủ ý — chạy lại với danh sách học sinh đã đổi giờ cho kết quả KHÁC lần chạy lại của bản cũ**: bản cũ
  hoán vị VỊ TRÍ cả dàn nên thêm một em là em cũ đổi chỗ ở mọi ngày (d12: 20 em cũ đổi CLB → 1; d16: 18 → 0). Chạy lại KHÔNG đổi
  danh sách thì vẫn giống hệt.
- **Workspace cũ** (đã khoá, chưa có `stb_buoi`): lần chạy đầu sau khi nâng cấp tính ĐÚNG như bản cũ (không ai bị xáo lặng lẽ), lưu
  thứ tự đó, và bước bốc thăm ghi `stb_buoi_luu_lan_dau`. Không bao giờ dựng lại âm thầm. "Vẽ lại" (`force_redraw_stb`) xoá thứ tự
  cũ, lập lại từ bộ số mới, ghi `stb_buoi_ve_lai` (+ `run_history.stb_redrawn = 1` như trước). Xoá học sinh: bỏ dòng của em đó,
  không đánh lại số ai. `reset_data`: xoá bảng.
- **Schema**: `stb_buoi` tạo bằng `di_tru_schema` (bước 8; sao lưu `.bak-` trước, chạy lại không làm gì); cố ý KHÔNG nằm trong
  `DEFAULT_SCHEMA` để mọi CSDL cũ đi qua đường di trú có sao lưu.
- **Dấu vân tay (FA-9)**: KHÔNG gồm thứ tự từng ngày (cùng lý do với số bốc thăm gốc: đó là kết quả của lần chạy, không phải dữ
  liệu đầu vào); ghi rõ trong docstring `dau_van_tay_du_lieu` và có test canh.
- Tệp: `rbda_priority_pipeline.py`, `api.py`, `api_bao_cao.py`, `api_sau_xep.py`, `api_quan_ly.py`, `fa_daa.py`,
  `i18n_errors.py` (+ `i18n_loi.js` sinh lại), `docs/ke_hoach/CLAUDE_CHI_TIET.md` (hàng `tests/`).
- Test mới: `tests/test_fa_sc_l5_khoa_so_theo_ngay.py` (62 ca: lần đầu giống cũ × 20 seed, thứ tự em cũ giữ nguyên, phân bố đều
  χ², xoá, vẽ lại, di trú, CSDL cũ, một buổi, dấu vân tay, báo cáo bốc thăm).
- Cần Truong xác nhận: lời hứa bất biến 3 nay mở rộng sang thứ tự TỪNG NGÀY (xem `docs/phien/claude__fa-sc-sua.md`).

## 2026-11-14 — FA-SC (mục mới ngoài sổ, Truong duyệt D-SC1): sự cố do con người, phần nghiên cứu

Chỉ tài liệu và kịch bản diễn tập; **không sửa mã sản phẩm**, không test mới. Mọi số liệu là MÔ PHỎNG (120 học sinh giả).
- `docs/fable/06_CRISIS_MEMO.md`: danh mục 48 sự cố phía học sinh + 13 phía giáo viên/IT (điểm S/O/D là giả định), kết quả 16
  diễn tập, bảng phương án, đề xuất FA-SC-1…9 (chưa mục nào được duyệt), quyết định chờ D-SC2…7.
- `docs/fable/06b_SO_TAY_SU_CO.md`: bản nháp sổ tay sự cố cho IT và giáo viên.
- `du_lieu_test/su_co/`: `chung.py`, `d01`…`d16`, `chay_tat_ca.py`, `README.md` (chỉ đọc mã sản phẩm, tất định theo `--seed`).
- `docs/phien/claude__fable-fa-sc.md`: bàn giao nhánh.
- `docs/fable/07_FA_SC_FIX_PLAN.md`: kế hoạch sửa đề xuất (3 pha, chưa duyệt) và `du_lieu_test/su_co/thu_p1_khoa_so_theo_ngay.py`
  (bản thử trong tiến trình: khoá thứ tự theo ngày thì d12 còn 1 em cũ đổi CLB thay vì 20, d16 còn 0 thay vì 18; số mô phỏng).
- Phát hiện cần Truong quyết (D-SC7, chưa sửa gì): chế độ `stb_ngay` tính lại thứ tự bốc thăm theo ngày của mọi em khi số học
  sinh đổi (`sinh_stb_theo_buoi`); một em đến muộn không tranh chỗ vẫn làm 18–38 em cũ đổi CLB trong dữ liệu giả 120 em.

## 2026-11-14 — SG-1 … SG-12: sửa sau đợt soát giao diện toàn kiosk (ba người song song, gộp ở claude/sg-sua)

Đặc tả: `docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md` (D1 = A, D2 = b, D3 = NULL đã duyệt). Cách chạy: `docs/ke_hoach/SG_SONG_SONG.md`
(người A `claude/sg-a`, B `claude/sg-b`, C `claude/sg-c`; mỗi mục một phiên viết mã + một phiên soát mã). Mảnh gốc từng người:
`docs/ke_hoach/sg_song_song/MANH_A.md`, `MANH_A_SG11a.md`, `MANH_B.md`, `MANH_C.md` (đủ chi tiết tệp và test). Mọi số liệu là MÔ PHỎNG.
Cấu hình mặc định giữ từng byte (`kiem_nhanh` 7/7, 60 ca = 3 bộ × 20 seed).

- **SG-1 (C3)**: CLB Tuyển chọn có người đăng ký mà chưa em nào có điểm → lỗi chặn `fa_clb_tuyen_chon_chua_co_diem` {club_id, so_dang_ky, so_nv1} ở lần chạy FA và trong báo cáo sức khoẻ (cùng một hàm `fa_daa.kiem_truoc_fa`). `so_nv1` đếm nguyện vọng 1 TRONG BUỔI, dùng chung `dem_nv1_trong_buoi` với bảng nhu cầu. Test: `tests/test_sg1_tuyen_chon_khong_diem.py`.
- **SG-2 (C1)**: không gian `Trường học` giữ `wharton: true`; hộp "Tính năng sau khi xếp…" có công tắc "Dùng điểm quyết tâm" (khoá khi bật FA), xem trước sổ cảnh báo em có ≥ 2 nguyện vọng cùng ngày mà không có điểm, câu "ô trống tính là 0" trong sheet Hướng dẫn được sửa, lần chạy bị chặn có nút mở hộp đó. Test: `tests/test_sg2_wharton_trong.py`, `tests/test_giao_dien_sg2_diem_quyet_tam.py`.
- **SG-3 (C2)**: chế độ FA lưu `rank_in_student_pref` = thứ hạng trong danh sách GỐC trong buổi (bằng `rank_in_list` của lý do); em xếp dự phòng vào CLB không khai → NULL (D3), hiện riêng "Xếp ngoài danh sách nguyện vọng". Lõi DA không đổi. Số FA cũ cần đo lại: xem "Chờ Truong" trong báo cáo. Test: `tests/test_sg3_hang_fa.py`.
- **SG-4 (M3)**: khiếu nại gõ tay khớp mã bằng `fa_sau_xep.khop_ma_hoc_sinh` như đường Forms; hai mã lỗi `khieu_nai_hs_khong_co`, `khieu_nai_chua_co_ket_qua`. Test: `tests/test_sg4_khop_ma.py`.
- **SG-5 (H3)**: câu huy chương có dòng giải thích; câu đổi bạc/đồng chỉ có khi ngày có ≥ 3 CLB nhận huy chương (chỉ đầu ra `--fa-daa*` đổi). Test: `tests/test_sg5_huy_chuong.py`.
- **SG-6 (H1, D1 = A)**: cột rỗng được `clubs.gio`, `clubs.dia_diem` qua `di_tru_schema` (sao lưu trước, chạy lại không đổi gì); hai cột TUỲ CHỌN "Giờ", "Địa điểm" ở sheet CLB của Sổ nhập; hiện ở bảng CLB, kết quả, danh sách, thời khoá biểu, Excel khi có. Hợp đồng CSV học sinh và `match_results` không đổi. Test: `tests/test_sg6_gio_dia_diem.py`, `tests/test_giao_dien_sg6_gio_dia_diem.py`.
- **SG-7 (H4, M1)**: bước 4 và khung cảnh báo thẻ Nhập dùng chung `veCanhBaoGom` (gom theo mã, đếm, tối đa 5 ví dụ). Test: `tests/test_giao_dien_sg7_canh_bao_gom.py`.
- **SG-8 (M5, bất biến 6)**: thông báo bước 1 "Chuẩn bị đợt" đi ra dạng mã `phieu_nd_*` qua `i18n_errors.py`, đổi ngôn ngữ vẽ lại bước 1–2; vòng lưu trước SG-8 vẫn hiện. Test: `tests/test_sg8_thong_bao_buoc1.py`, `tests/test_giao_dien_sg8_buoc1_tieng_anh.py`.
- **SG-9**: `chayNut` / `chayTai` / `noiTiep` (`js/00_nen.js`) cho mọi lời gọi API ở `js/05, 10, 11, 12, 13_*.js`: nút bận, lỗi có thông báo, luôn mở lại nút. Test: `tests/test_giao_dien_sg9_nut_ban.py`.
- **SG-10 (M2)**: CLB Tự do (FA) không còn % lấp đầy hay "x/y chỗ": màn kết quả, Theo CLB, độ chọi và tệp xuất hiện "N <người> · không giới hạn chỗ"; "Chỗ còn trống" bỏ CLB Tự do. Test: `tests/test_sg10_clb_tu_do.py`, `tests/test_giao_dien_sg10_clb_tu_do.py`.
- **SG-11a (M6, M7, L1, L4, L5)**: `color-scheme: light`; bảng kết quả vừa 1024 px; `.hs-buoi-nhan` dùng `--gold-text`; Nhập điểm dùng chung bề rộng nội dung; một dòng gợi ý khi nút xuất chỉ-FA bị ẩn. Test: `tests/test_giao_dien_sg11a_ve_sinh.py`.
- **SG-11b (M4)**: hộp chọn không gian làm việc giữ tiêu điểm trong hộp (Tab/Shift+Tab), Esc đóng đúng lớp, trả tiêu điểm về nút mở. Test: `tests/test_giao_dien_sg11b_focus_man_chon.py`.
- **SG-12 (H2, D2 = b)**: biểu mẫu học sinh dùng tiêu đề thuần (không `[mã]`, `(club_id)`); trình tạo ghi `MAP_*.json` cạnh từng biểu mẫu, bộ đọc khớp chính xác qua bản đồ; tệp xuất cũ có mã vẫn đọc được; `--giu-ma` cho đầu ra giống từng byte trước SG-12. Test: `tests/test_sg12_tieu_de_thuan.py`.
- **Gộp (người A)**: xung đột SG-6 × SG-10 ở `api_bao_cao.get_club_fill_stats`, `api_xuat` (đầu khối "Theo CLB") và `js/09_the_xem.js` (`veKqTheoClb`) giữ cả hai hành vi; `i18n_loi.js` sinh lại. Test: `tests/test_sg_tich_hop_tu_do_gio.py` (3). `CLAUDE_CHI_TIET.md`: số tệp test 293.
- **SG-6 (sửa CI)**: fixture `_csdl_cu` trong `tests/test_sg6_gio_dia_diem.py` dựng lại bảng `clubs` thay vì `ALTER TABLE … DROP COLUMN` (SQLite 3.45.1 của Python 3.11 trên CI báo "incomplete input" khi xoá cột cuối có chú thích `--`; SQLite 3.53 không lỗi). Chỉ đổi test; mã sản phẩm và schema không đổi.

## 2026-11-13 — FG FINISH: báo cáo, sổ sách, chạy thử người mới (chỉ tài liệu, TH)

- `docs/phien/bao_cao_dem/2026-11-13_fg_sua.md`: bảng 9 mục FG-1…FG-9, test đã thêm, quyết định, mục GONE-ON-HEAD, "Chờ Truong", chạy thử người mới theo spec §5 (chế độ trình duyệt, không gian làm việc mới ngoài kho mã): bật 5 tính năng từ menu → nạp sổ mẫu FA 120 em → chạy → nạp tệp Forms sau kết quả MÔ PHỎNG hai lần: cùng số đếm (33 phản hồi, 3 khiếu nại), lần hai báo trùng. Không có lỗi mới. Phần "Vòng xanh" để lead điền.
- `docs/ke_hoach/TIEN_DO.md`, `docs/phien/claude__forms-gop.md` (mục FG): ghi tiến độ. Không đổi mã sản xuất hay test.

## 2026-11-13 — FG-9: thanh bên bỏ số thứ tự, thông báo "Tải sổ nhập mẫu" có nút "Mở thư mục" (TH)

- `index.html` + `style.css`: bỏ 7 số 01–07 ở thanh bên (và luật `.nav-icon`); thứ tự thẻ không đổi.
- `js/00_nen.js` (`showToast`): tuỳ chọn `hanhDong {nhan, khiBam, tooltip}` thêm một nút trong thông báo, đường dài nằm ở tooltip. `js/02_van_hanh.js` (`taiSoNhapMau`): câu thông báo bỏ đường dẫn (khoá mới `so_mau_da_tao_ngan`, vi+en trong `i18n.js`), nút "Mở thư mục" gọi `mo_thu_muc`; vẫn tự mở thư mục như trước (giữ hành vi gần hôm nay nhất); dòng phản hồi dưới vùng thả tệp vẫn có đường đầy đủ.
- Chỉ số "chưa có chỗ nào · Cần xử lý" đã bấm được từ trước (test xanh, giữ).
- Test cũ mở rộng sang trạng thái mới (không bỏ khẳng định): `test_giao_dien_a14_lop.py::test_thanh_ben_sau_khi_gop_va_bao_chua_co_ket_qua` (nhãn không mở đầu bằng số, đúng 7 thẻ theo thứ tự), `test_ws_so_nhap_giao_dien.py::_tai_mau` (chờ tooltip chứa .xlsx + nút "Mở thư mục" thay vì tên tệp trong câu).
- Test: `tests/test_giao_dien_fg9_ux_nho.py` (3; 2 đỏ → xanh, thêm kiểm 7 nhãn không bắt đầu bằng số).

## 2026-11-13 — FG-8: chữ gợi ý cảnh báo, bước 3 trình hướng dẫn, nhóm "Sau khi công bố kết quả", ẩn "Chưa chia buổi" (TH)

- `i18n.js` + `index.html`: `health_panel_hint` (vi+en) nói mục "Nghiêm trọng" chặn việc chạy; `js/02_van_hanh.js`: dòng tóm tắt đỏ (`is-warn`) chỉ khi `n_high > 0`, còn lại trung tính (`style.css`).
- `js/075_workspace.js` (`wsBuoc3`): bốn ô "Theo dõi sau khi xếp…" bị khoá và bỏ tick khi `wzFaDaa` tắt; `style.css`: ô tick cùng dòng nhãn (chỉ `.ws-truong` có checkbox).
- `index.html` + `js/10_theo_doi.js` (`batKhung`): tiêu đề nhóm "Sau khi công bố kết quả" trước hai khung khiếu nại + phản hồi (hiện khi có khung hiện) và một dòng gợi ý nút nào cho biểu mẫu cũ/mới (`ph_goi_y_nut`); khi workspace chỉ có một buổi, ô chọn buổi ẩn và danh sách khiếu nại bỏ nhãn "Chưa chia buổi".
- `i18n_errors.py` (vi+en) + `tao_i18n_js.py`: câu `forms_tep_sau_ket_qua` gọi đúng tên nhóm mới (logic FA-M9 không đổi). `tests/test_ws_nhan.py`: `SUA_CO_Y` ghi nhận chủ ý đổi chữ `health_panel_hint`.
- Test: `tests/test_fg8_goi_y_suc_khoe.py` (2), `tests/test_giao_dien_fg8_cau_chu.py` (6) đỏ → xanh.

## 2026-11-13 — FG-7: biểu mẫu "Sau khi xem kết quả" chỉ liệt kê ngày có CLB, tiêu đề riêng, hướng dẫn đúng đường menu (TH)

- `mau_forms_thi_clb/tao_mau_forms.py`: `--sau-ket-qua` nhận `--so-nhap-clb` (chỉ liệt kê ngày có CLB trong sổ qua `buoi_co_clb_trong_so_nhap`; không có thì như cũ); tiêu đề docx riêng "Phản hồi và báo lỗi sau khi xem kết quả" (`ghi_docx_chi_thi(..., tieu_de=)`); bước 4 hướng dẫn chỉ "Kiosk → Không gian làm việc → ⋯ → Tính năng sau khi xếp…" (không còn khoá cấu hình); bước 5 giải thích vì sao giữ `[mã]`/`(mã)`; `--help` bỏ mã nội bộ; in thư mục ra tuyệt đối ở dòng cuối. Chỉ đầu ra `--sau-ket-qua` và chữ `--help` đổi; `--fa-daa`, `--fa-daa --mot-bieu-mau`, `--phan-hoi`, `--tuan-3` giữ từng byte (băm trong test).
- Test: `tests/test_fg7_bieu_mau_sau_ket_qua.py` (5 đỏ → xanh; sửa lỗi test `c["ten"]` → `c["name"]`).

## 2026-11-13 — FG-2: không gian FA cảnh báo ở bước xem trước, mẫu sổ FA và sổ mẫu 120 em (TH)

- `api_nhap.py`: `_canh_bao_fa_xem_truoc` + `xem_truoc_so_nhap`: workspace bật FA-DAA thì chạy `fa_daa.kiem_truoc_fa` và `kiem_ho_so_huy_chuong` trên dữ liệu đã đọc từ sổ (cột FA vắng thì lấy giá trị đang lưu), gom theo mã lỗi: mỗi mã MỘT cảnh báo mang chính mã đó, `params` = `nhom: true`, `n`, `vd`; thêm một dòng `so_nhap_canh_bao_fa_se_loi` khi có lỗi chặn. Vẫn nhập được; `import_so_nhap` không đổi. Workspace không FA: không thêm gì.
- `so_nhap.py`: `ghi_so_nhap(..., che_do_fa=False)`: True thì cột CLB có đủ 4 cột FA (Loại…), cột điểm quyết tâm có nhãn "Huy chương (60/30/10)" (danh sách thả xuống 60/30/10) và Hướng dẫn nói về huy chương (`_huong_dan_fa`). Bộ đọc nhận thêm tiêu đề "huy chuong" như "Điểm quyết tâm". Mặc định (không FA): sổ y như cũ (test băm). `api_xuat.tao_so_nhap_mau` truyền `che_do_fa=dung_fa_daa(...)`.
- `i18n_errors.py` (vi+en) + `python tao_i18n_js.py`: 11 câu `<mã>_nhom` (chọn khi `params.nhom`) và `so_nhap_canh_bao_fa_se_loi`; `format_message` và `translateError` (`i18n.js`) dùng câu `_nhom`; thêm vào `MA_MOI_SAU_ANH_CHUP` (`tests/test_ws_nhan.py`).
- `du_lieu_test/tao_so_nhap_fa_mau.py` (seed cố định) sinh `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx`: 120 em, 2 buổi, mỗi buổi 1 CLB Tự do + 2 Giới hạn + 1 Tuyển chọn; MÔ PHỎNG, ghi rõ ở sheet "Hướng dẫn".
- Test: `tests/test_fg2_xem_truoc_fa.py` (4 đỏ → xanh, thêm 4 test: câu chữ nhóm, không ghi CSDL, sổ mẫu tất định + ghi MÔ PHỎNG, hướng dẫn FA).

## 2026-11-13 — FG-6: mỗi số một đơn vị, danh sách thay cho tường chữ (TH)

- `api_sau_xep.py`: kết quả `nhap_phan_hoi_forms` và `nhap_sau_ket_qua_forms` thêm `hoc_sinh` (số học sinh có dòng/khiếu nại mới), `dong_bo_qua: [{dong, ly_do}]` (số dòng trong tệp + mã lý do); giữ khoá cũ `n_ket_qua`, `n_tuan_3`, `n_khieu_nai`, `bo_qua` vì test cũ còn đọc. Hàm `_tep_rong`: tệp không có dòng trả lời -> mã riêng `phan_hoi_tep_rong` (trước: "không phải tệp phản hồi"). `_chen_phan_hoi` trả thêm tập học sinh có dòng mới.
- `i18n_errors.py` (vi+en) + `python tao_i18n_js.py`: `phan_hoi_tep_rong`; thêm vào `MA_MOI_SAU_ANH_CHUP` (`tests/test_ws_nhan.py`).
- `js/10_theo_doi.js` (`ketQuaNapForms`): thông báo MỘT câu ("Đã nạp phản hồi của 3 học sinh, 1 khiếu nại mới."); khung `#phNhapKetQua` hiện `<ul>` theo lý do (dòng trùng, khiếu nại trùng, mã không khớp được liệt kê, dòng bỏ qua theo lý do, khiếu nại không nhận gom theo mã). `js/02_van_hanh.js` (`showLog`): lỗi cùng mã gom lại, tối đa 5 dòng mỗi mã rồi "và N lỗi nữa". `i18n.js` vi+en.
- `js/00_nen.js` + `style.css`: dấu × của nút đóng thông báo vẽ bằng CSS (`::before`) để chữ thông báo không kèm "×".
- Test: `tests/test_fg6_ket_qua_nap.py` (4 đỏ → xanh, 1 xanh sẵn), `tests/test_giao_dien_fg6_danh_sach_loi.py` (2 đỏ → xanh). Sửa 3 assert cũ theo spec (không nới): `test_fa_gap5_phan_hoi.py`, `test_fa_m6b_sau_ket_qua.py` (thêm khoá mới), `test_giao_dien_fa_m6b_sau_ket_qua.py` (thông báo giờ một câu; chi tiết s3 chuyển xuống danh sách).

## 2026-11-13 — FG-5: mã học sinh gõ khác hoa/thường hay thừa khoảng trắng vẫn khớp (TH)

- `fa_sau_xep.py`: `khop_ma_hoc_sinh(ma_go, tat_ca_ma)` (hàm thuần): khớp đúng thắng; không thì khớp `strip().casefold()` nếu đúng MỘT học sinh; mơ hồ/không có -> None. Mã đã lưu không đổi.
- `api_sau_xep.py`: `_chen_phan_hoi` (đường `nhap_phan_hoi_forms` và nhánh phản hồi của `nhap_sau_ket_qua_forms`) và nhánh khiếu nại của `nhap_sau_ket_qua_forms` dùng hàm trên; cả hai kết quả thêm `ma_khong_khop` (mã gõ không khớp, theo thứ tự gặp, tối đa 20); giữ các khoá cũ (đổi hình dạng là FG-6).
- Test: `tests/test_fg5_khop_ma.py` (6 đỏ → xanh); mở rộng 2 assert từ điển cũ (`test_fa_gap5_phan_hoi.py`, `test_fa_m6b_sau_ket_qua.py`) thêm khoá `ma_khong_khop`, không nới.

## 2026-11-13 — FG-4: hai nút nạp tệp Forms dùng một hàm, có trạng thái bận (TH)

- `js/10_theo_doi.js`: `napTepForms(nut, input, tenApi, khiXong)` thay hai bộ xử lý chép lại; nút khoá + nhãn "Đang nạp…" (`dang_nap`, vi+en trong `i18n.js`) khi gọi API, bấm lần hai không sinh yêu cầu mới, `.catch` hiện thông báo lỗi chung, `finally` luôn xoá ô tệp và mở lại nút.
- Test: `tests/test_giao_dien_fg4_nut_nap.py` (2 đỏ → xanh, 2 đường lỗi giữ nguyên).

## 2026-11-13 — FG-3: nạp lại cùng một tệp Forms không thêm gì (TH)

- `api_sau_xep.py`: `_chen_phan_hoi` bỏ qua dòng trùng hệt `(student_id, nguon, loai, hai_long, hieu_ly_do, kho_nhat, con_di, muon_doi)` và đếm (trả thêm số dòng trùng); `_them_khieu_nai(..., tu_forms)`: khi dòng Forms có giờ hoàn thành thật, cùng `(student_id, buoi, created_at)` ở MỌI trạng thái = "đã nạp" (không phải lỗi, không sinh khiếu nại CHO mới). Khiếu nại gõ tay trên kiosk giữ luật cũ.
- Kết quả `nhap_phan_hoi_forms` / `nhap_sau_ket_qua_forms` thêm `dong_moi`, `dong_trung` (và `khieu_nai_moi`, `khieu_nai_trung` ở đường sau kết quả); giữ khoá cũ (đổi hình dạng đầy đủ là FG-6).
- Test: `tests/test_fg3_nap_lai.py` (5 đỏ → xanh); mở rộng 2 assert từ điển cũ trong `test_fa_gap5_phan_hoi.py`, `test_fa_m6b_sau_ket_qua.py` (thêm khoá, không nới).

## 2026-11-13 — FG-1: bật/tắt tính năng sau khi xếp cho từng không gian làm việc (TH)

- `js/075_workspace.js`: mục "Tính năng sau khi xếp…" trong menu ⋯ của dòng không gian làm việc (`wsMoTinhNang`): hộp thoại 5 ô
  (`CO_SAU_XEP`) + số ngày khiếu nại (1–14), lưu qua `update_workspace_config` (chỉ các khoá này); lỗi hiện trong hộp thoại, hộp
  vẫn mở; không có FA thì ô khoá kèm một dòng giải thích; lưu xong áp lại cấu hình và nạp lại thẻ chi tiết (không cần khởi động lại).
  `wsHienOverlay`: màn chọn chỉ mang `role="dialog"` khi đang hiện (`index.html` bỏ role tĩnh).
- `i18n.js` (vi + en): `ws_btn_tinh_nang`, `ws_tn_*`. Không đổi mã backend (máy chủ đã chặn cờ khi thiếu FA).
- Test: `tests/test_giao_dien_fg1_bat_tinh_nang.py` (3 đỏ → xanh), `tests/test_fg1_bat_tinh_nang.py` (giữ); sửa
  `tests/test_ws_giao_dien.py` (thứ tự menu thêm `tinh_nang`).

## 2026-11-13 — GIAM-MAY-RUI-KH (Truong yêu cầu 13/11/2026): kế hoạch giảm may rủi cho Sonnet (chỉ tài liệu)

- `docs/ke_hoach/GIAM_MAY_RUI_KE_HOACH.md` (mới): FA-CT1 chia chỗ theo nhu cầu (gợi ý, không ghi chỉ tiêu), FA-CT2 "được thêm X chỗ thì thêm vào đâu" + nút xuất cho giáo viên, FA-D7L điểm lẻ 0,1 (tuỳ chọn, mặc định tắt; tập đạt điểm sàn giữ nguyên nhờ cắt bớt rồi làm tròn).
- `docs/phien/claude__giam-may-rui.md` (mới, bàn giao nhánh), `docs/ke_hoach/giam_may_rui/PROMPT_SONNET.md` (mới, câu lệnh khởi động).
- Không đổi mã, không test mới.

## 2026-11-12 — DOC-FABLE (ngoài sổ, Truong yêu cầu 12/11/2026): tệp bối cảnh dự án + tệp giao việc cho Fable

- `docs/fable/01_PROJECT_CONTEXT.md` (mới): tóm tắt toàn dự án cho AI đọc (bài toán, RB-DA, lớp FA-DAA, chương trình, bất biến, số liệu MÔ PHỎNG, điểm yếu, thứ tự đọc).
- `docs/fable/02_FABLE_BRIEF.md` (mới): luật nền, 6 mục tiêu nghiên cứu G-A…G-F theo ưu tiên, sản phẩm cần giao, cách chạy phiên Fable, ba câu lệnh dán sẵn.
- Chỉ tài liệu; không đổi mã, không test mới.
- `CLAUDE.md` quy tắc 11: thêm vai trò Fable (nghiên cứu, không sửa mã sản xuất), Truong duyệt 12/11/2026.

## 2026-11-12 — FA-M8, FA-M9, FA-M10: bước 3–5 của thẻ "Chuẩn bị đợt" (TH = chưa thử trên Microsoft thật)

- INTEGRATE-2: gộp `claude/it-ui-b` (FA-M9, FA-M10) và `claude/it-ui-c` (FA-M8) vào `claude/forms-gop` (gộp sạch, khối đánh dấu không xung đột); đếm lại số tệp test trong bản đồ mã (263) — lỗi duy nhất của nhánh B.

**FA-M9 — Nạp tệp Forms / List ngay trong phần mềm (thẻ "Chuẩn bị đợt", bước 4).**
- `api_forms_nap.py` (`FormsNapMixin`): `nhan_dien_tep_forms(files)` phân loại từng tệp (đăng ký / bài thi / List CSV / sau kết quả /
  không rõ), loại tệp sai đường (`forms_tep_sai_duong`), đoán đề A/B/C của tệp bài thi bằng `doan_bien_the` (không ghi gì);
  `chuyen_tep_forms(files, bien_the, lua_chon)` lưu tệp ở `forms/nap/tai_len/`, gọi `chuyen_fa_daa_du_lieu`, ghi
  `forms/nap/SO_NHAP_CLB.xlsx` + `EMAIL_MA_HS.csv` (+ `BANG_DIEM.xlsx`, `PHAN_TICH_CAU_HOI.xlsx`); chênh lệch giữa các đề ->
  `trang_thai: "cho_xac_nhan"` (hai nút "Dịch điểm về trung bình chung" / "Giữ điểm đã chấm", không phải chọn lại tệp); câu bị
  gắn cờ -> `cau_co_co` để tick "Bỏ câu này" rồi chấm lại; lỗi đề / tệp -> `forms_khong_chuyen_duoc`, không ghi Sổ.
  `get_forms_nap()` nhớ các tệp đã tải khi mở lại thẻ; `lay_so_nhap_nap()` trả Sổ nhập base64.
- Nhập vào app.db vẫn bằng `xem_truoc_so_nhap` / `import_so_nhap` CÓ SẴN (không có đường nhập thứ hai).
- Giao diện `js/12_chuan_bi_nap.js` (bước 4): khung thả nhiều tệp, bảng tệp (loại + ô chọn đề, đoán sẵn), nút "Chuyển thành Sổ
  nhập", hộp xác nhận, danh sách "Bỏ câu này" + "Chấm lại", cảnh báo, xem trước, nút "Nhập sổ". Chuỗi `cb_nap_*` (vi + en).
- Mã lỗi mới (khối B): `forms_thieu_tep_nap`, `forms_thieu_tep_dang_ky`, `forms_nhieu_tep_list`, `forms_chua_chuyen_tep`
  (đã thêm vào `MA_MOI_SAU_ANH_CHUP`, đã chạy `tao_i18n_js.py`).
- Tệp test mới: `tests/test_fa_m9_nap_tep_forms.py` (19 ca API), `tests/test_giao_dien_fa_m9_nap.py` (4 ca Chromium: đường B thả
  1 đăng ký + 2 bài thi -> xem trước -> nhập, số học sinh khớp; đường A lệch đề -> xác nhận; tệp lạ / sai đường khoá nút;
  chưa chọn đường). Trước đó: `tests/test_fa_m9_thuan.py`.
- Đột biến đã chạy: API bỏ qua `lua_chon` (`lua_chon=None`) -> 3 ca đỏ (`test_xac_nhan_roi_lua_chon_thi_ghi_so`,
  `test_bo_cau_cham_lai`, `test_duong_a_lech_giua_hai_de_hien_hop_xac_nhan`); khôi phục -> xanh. (`doan_bien_the` luôn "A" đã
  đỏ ở FA-M9-THUAN.)
- Mặc định không đổi: không đụng lõi DA, schema, cột CSV; đầu ra bộ chuyển đổi dòng lệnh y hệt (API == CLI, so từng ô).

**FA-M10 — Ba nút "Sau khi xếp" ngay trong phần mềm (thẻ "Chuẩn bị đợt", bước 5).** TH = chưa thử trên Microsoft thật.
- `api_forms_nap.py`: `xuat_ket_qua_list()` (các dòng `export_ly_do_csv` ghép email bằng `ghep_ket_qua_email.ghep` với
  `forms/nap/EMAIL_MA_HS.csv` -> `KETQUA_NHAP_LIST.csv`; thiếu tệp email -> `forms_thieu_email`; không để lại `ket_qua_ly_do.csv`),
  `ai_chua_dang_ky(file_base64)` (CSV danh sách lớp + mã học sinh đã đăng ký ở lần nạp cuối của bước 4 -> thư mục `chua_dang_ky/`:
  mỗi lớp còn em chưa đăng ký một tệp + `tong_hop.csv`), `doi_chieu_hai_lan(cu_base64, moi_base64)` (-> `DOI_CHIEU_LIST.xlsx`, đề lấy
  từ `forms/de_thi.json`). Mọi tệp ra rơi vào `thu_muc_tai_ve()` qua `_duong_xuat`: không ghi đè tệp cũ (`x (2)`), lỗi thì không ghi gì.
  Dùng lại hàm sẵn có (`ghep`, `chua_dang_ky`, `doi_chieu` + `ghi_bao_cao`); dòng lệnh y hệt (API == CLI, so từng byte / từng ô).
- Giao diện `js/12_chuan_bi_nap.js` (bước 5): ba khối — nút "Xuất KETQUA_NHAP_LIST.csv"; ô chọn CSV danh sách lớp + nút "Tạo danh sách
  chưa đăng ký" (khoá tới khi chọn tệp; cảnh báo vượt giới hạn Power Automate); hai ô chọn CSV cũ / mới + nút "Đối chiếu" (CHỈ đường A).
  Chuỗi `cb_nap_s5_*` (vi + en). Không mã lỗi mới (dùng `forms_thieu_email`, `forms_thieu_danh_sach_lop`, `forms_khong_chuyen_duoc`...).
- Tệp test mới: `tests/test_fa_m10_sau_xep_nut.py` (8 ca API), `tests/test_giao_dien_fa_m10_nut.py` (6 ca Chromium).
- Đột biến đã chạy: (1) API ghi thêm ký tự vào `KETQUA_NHAP_LIST.csv` -> `test_xuat_ket_qua_list_bang_cli_cung_tep` đỏ; (2) giao diện bỏ điều kiện
  "đã chọn tệp" của nút "Ai chưa đăng ký" -> `test_nut_ai_chua_dang_ky_khoa_den_khi_chon_tep_roi_ghi_thu_muc` đỏ; khôi phục -> xanh.
- Mặc định không đổi: không đụng lõi DA, schema, cột CSV; ba tập lệnh dòng lệnh không đổi.

**FA-M8 — Tạo bộ biểu mẫu một lần bấm (R3, R8, R9).**
- Hàm thuần (`mau_forms_thi_clb/tao_mau_forms.py`, `bieu_mau.py`): `sinh_phieu_clb` (R9, biểu mẫu thiết lập CLB, tiêu đề câu hỏi
  y nguyên `PHIEU_THIET_LAP_CLB.md` §1), tham số `dap_an_tren_forms` (mặc định True = như cũ; False = hướng dẫn KHÔNG dặn đặt đáp án
  trên Forms, R3), `ghi_xem_lai_dap_an` (`XEM_LAI_DAP_AN.xlsx`), `tao_bo_bieu_mau` và `ghi_zip_bo` (R8, một tệp zip cho đường đã chọn
  kèm `00_DOC_TRUOC.md`). Đường A gọi lại `tao_bo_dung_t4m.tao_bo_dung(fa=True)`, không sao chép.
- API `api_forms_bo.py` (`FormsBoMixin`): `get_bo_bieu_mau()` -> `{co_de, duong, co_bien_the}`; `tao_bo_bieu_mau_api(tuy_chon, output_path="")`
  (`tuy_chon = {mot_bieu_mau (mặc định True), bien_the (mặc định False)}`) lấy đề từ `forms/de_thi.json`, đường từ `rules.fa_duong`, Loại CLB
  từ `forms/SO_NHAP_CLB_CLB.xlsx` khi có (đường B); ghi `forms/bieu_mau/` và `BO_BIEU_MAU_<ngày>.zip` vào Tải xuống (không ghi đè, trùng
  tên thì "(2)"). Trả `{path, dir, ten_zip, thu_muc, n_tep, duong, mot_bieu_mau, bien_the}`. Lỗi: `forms_chua_co_de`, `forms_duong_chua_chon`,
  `forms_tao_bo_loi`. API KHÔNG có tuỳ chọn nào đổi R3; không ghi app.db.
- Giao diện `js/13_chuan_bi_bo.js`: bước 3 vẽ bằng `ChuanBi.dangKyBuoc(3, ...)`: ô "Một biểu mẫu cho mọi buổi" (tích sẵn; tắt ở đường A vì
  đường A dùng bộ dựng riêng), ô "Hai đề cho CLB Tuyển chọn" (chỉ bật khi đề có CLB có biến thể), nút "Tạo bộ biểu mẫu" (tắt khi chưa chọn đường
  hoặc chưa có đề), thông báo có tên tệp zip, nút "Mở thư mục" (`mo_thu_muc`). Chuỗi `cb_bo_*` (vi + en) trong khối C của `i18n.js`; kiểu `style.css`
  khối C.
- Mã lỗi mới: không (dùng ba mã đã có từ G0).
- Tệp test mới (3): `tests/test_fa_m8_bo_bieu_mau.py` (28 ca, hàm thuần), `tests/test_fa_m8_api.py` (12 ca), `tests/test_giao_dien_fa_m8_bo.py` (6 ca Chromium).
- Đột biến đã chạy: (1) `tao_bo_bieu_mau` truyền `dap_an_tren_forms=True` -> `test_r3_so_voi_dap_an_tren_forms_true` (API) đỏ, và ở lớp thuần
  `test_bo_khong_co_dap_an_tren_forms_o_moi_huong_dan` đỏ; (2) API bỏ qua `mot_bieu_mau` (luôn True) -> `test_mot_bieu_mau_theo_tuy_chon` đỏ;
  (3) giao diện luôn gửi `mot_bieu_mau: true` -> `test_bo_tich_mot_bieu_mau_doi_bo` đỏ. Khôi phục -> xanh.
- Mặc định không đổi: snapshot 8 chế độ của máy sinh (mặc định, `--fa-daa`, `--fa-daa --mot-bieu-mau`, `--chi-thi`, `--phan-hoi`,
  `--sau-ket-qua`, `--tuan-3`, `--bien-the` với đề hai CLB dựng trong thư mục tạm) dựng từ BASE 5196217 và từ nhánh: `diff -rq` KHÔNG khác biệt (23 tệp).
  Không đụng lõi DA, schema, cột CSV.

## 2026-11-11 — FA-M7 (+ G0): thẻ "Chuẩn bị đợt", CLB nhập một lần, đề thi trong một tệp Excel (TH = chưa thử trên Microsoft thật)

- Gộp từ `claude/it-ui-a` (nền G0 + FA-M7). FA-M8, FA-M9, FA-M10 CHƯA làm (hai cộng tác viên B và C không chạy).
- G0 (nền): `forms_dot.py` (đường dẫn thuần của đợt, mọi tệp nằm trong `forms/` cạnh app.db), `api_forms.py` (`FormsMixin`: `get_fa_duong`, `dat_fa_duong`, lưu `rules.fa_duong` A/B, không thuộc luật xếp), hai tệp rỗng `api_forms_nap.py` / `api_forms_bo.py` (dành cho FA-M9/FA-M10/FA-M8), `kiosk.spec` (hiddenimports cho `mau_forms_thi_clb`), thẻ "Chuẩn bị đợt" (chỉ hiện khi FA-DAA bật), `js/11_chuan_bi.js` + hai tệp JS rỗng, khối đánh dấu và mã lỗi dùng chung (vi + en).
- FA-M7: bước "1. CLB" (`nap_phieu_clb`: nạp tệp xuất Phiếu thiết lập CLB, ghi `forms/SO_NHAP_CLB_CLB.xlsx`, không ghi app.db) và bước "2. Đề thi" (`tai_mau_de_thi` ghi `MAU_DE_THI_KIOSK.xlsx`; `nap_de_thi` đọc, gom MỌI lỗi một lần, lỗi thì không ghi gì, thành công ghi `forms/de_thi.json`); `get_forms_buoc_12` trả trạng thái để vẽ lại thẻ. Mô-đun mới `mau_forms_thi_clb/so_de_thi.py`. `chuyen_phieu_clb.chuyen_phieu` trả thêm khoá `kq`; đầu ra dòng lệnh không đổi. FIX1: `loai` của CLB đi theo sang `de_thi.json` để CLB Tự do không vào câu huy chương vàng; sửa chữ lỗi `forms_thieu_email` (hết gạch ngang nối câu).
- Tệp chính: `forms_dot.py`, `api_forms.py`, `api_forms_nap.py`, `api_forms_bo.py`, `mau_forms_thi_clb/so_de_thi.py`, `mau_forms_thi_clb/chuyen_phieu_clb.py`, `js/11_chuan_bi.js`, `js/12_chuan_bi_nap.js`, `js/13_chuan_bi_bo.js`, `index.html`, `i18n.js`, `i18n_errors.py`, `i18n_loi.js`, `kiosk.spec`, `api.py`.
- Test mới (đỏ trước): `tests/test_fa_m7_dong_goi.py`, `tests/test_fa_m7_duong.py`, `tests/test_giao_dien_fa_m7_the.py` (G0); `tests/test_fa_m7_nguon_mot_lan.py` (18 ca), `tests/test_giao_dien_fa_m7_nguon.py` (3 ca Chromium).
- Đột biến đã chạy: bỏ phép đối chiếu CLB của đề thi với bước 1 (`if ma not in theo_ma` -> `if False and ...`) làm 3 ca đỏ; khôi phục thì 18/18 xanh.
- Mặc định không đổi: không đụng lõi DA, schema, cột CSV; kết quả xếp không đổi (bước này không ghi app.db); đầu ra các lệnh `tao_mau_forms.py` giống từng byte.

## 2026-11-11 — FA-M6b: MỘT biểu mẫu "Sau khi xem kết quả" = 3 câu phản hồi + nhánh khiếu nại lỗi dữ liệu (TH = chưa thử trên Microsoft thật)

- `mau_forms_thi_clb/bieu_mau.py`: `CAU_CO_SAI`, `LUA_CHON_CO_SAI`, `CAU_KN_BUOI`, `CAU_KN_GHI_CHU`, `cac_phan_sau_ket_qua(de)` (phần 1: mã học sinh + 3 câu phản hồi + `[co_sai]`; phần 2: `[kn_buoi]` hộp chọn nhiều + `[kn_ghi_chu]`). `cac_phan_phan_hoi()` giữ nguyên.
- `mau_forms_thi_clb/tao_mau_forms.py`: `--sau-ket-qua` (riêng một chế độ, báo lỗi nếu dùng chung chế độ khác) ghi `NHAP_FORMS_SAU_KET_QUA.docx` + `CAI_DAT_FORMS_SAU_KET_QUA.md` (rẽ nhánh `[co_sai]`, bật Multiple answers cho `[kn_buoi]`, Settings, hạn 3 ngày, nộp muộn -> giáo viên chủ nhiệm, xuất và nạp). Docx Quick Import không phân biệt kiểu câu: câu `[kn_buoi]` phải bật "Multiple answers" tay (ghi trong hướng dẫn).
- `fa_sau_xep.py`: `doc_tep_forms_khieu_nai(hang, ma_buoi_hop_le) -> (yeu_cau, bo_qua)` (hàm thuần; chỉ dòng `co_sai` = 1; mỗi (học sinh, buổi) một yêu cầu; giờ Forms từ "Completion time"/"Thời gian hoàn thành", dự phòng "Start time"; thiếu cột `[co_sai]` -> ValueError). `doc_tep_forms_phan_hoi` KHÔNG đổi (đọc tệp gộp, cột thừa bỏ qua).
- `api_sau_xep.py`: tách `_chen_phan_hoi` và `_them_khieu_nai` dùng chung (đầu ra `nhap_phan_hoi_forms`, `gui_khieu_nai` giữ nguyên); mới `nhap_sau_ket_qua_forms(file_base64)`: một giao dịch, hạn khiếu nại theo giờ Forms, lỗi từng khiếu nại (`khieu_nai_qua_han`, `khieu_nai_trung`, `khieu_nai_khong_hop_le`) được BÁO không làm hỏng lần nạp, hai cờ tắt -> `fa_sau_ket_qua_chua_bat`, một cờ tắt -> phần kia bị bỏ qua kèm cảnh báo.
- `i18n_errors.py` (+ `i18n_loi.js`, `tests/test_ws_nhan.py`): mã mới `fa_sau_ket_qua_chua_bat`, `khieu_nai_khong_co_gio_forms`. UI: nút "Nạp biểu mẫu Sau khi xem kết quả" ở khung Phản hồi (`index.html`, `js/10_theo_doi.js`, `i18n.js` vi + en).
- Test mới (đỏ trước): `tests/test_fa_m6b_sau_ket_qua.py` (22), `tests/test_giao_dien_fa_m6b_sau_ket_qua.py` (2, Chromium). Đột biến: dùng giờ nạp thay giờ Forms -> 2 ca đỏ; bỏ lọc `co_sai` -> 1 ca đỏ.
- Tài liệu: `docs/he_sinh_thai/FA_SAU_XEP.md` (mục 3.5 và mục 4). `--phan-hoi` và hướng dẫn của nó giữ nguyên từng byte.

## 2026-11-11 — FA-M2b: MỘT biểu mẫu đăng ký cho mọi ngày, đường B (TH = chưa thử trên Microsoft thật)

- `mau_forms_thi_clb/bieu_mau.py`: `cac_phan_fa_gop(de)` (phần thông tin một lần + mỗi ngày phần Nguyện vọng và phần Huy chương, đúng thứ tự `de["buoi"]`, chữ từng câu giống hệt `cac_phan_fa`) và `dem_cau_fa_gop(de)`.
- `mau_forms_thi_clb/tao_mau_forms.py`: `sinh_dang_ky(de, thu_muc, mot_bieu_mau=False)` ghi MỘT tệp `NHAP_FORMS_DANG_KY_TAT_CA.docx` (mỗi chế độ xoá tệp .docx cũ của chế độ kia; vượt `TRAN_CAU_MOI_BIEU_MAU` thì `LoiDeThi`, không ghi gì); `ghi_cai_dat_dang_ky(de, mot_bieu_mau=False)` thêm mục "Một biểu mẫu cho mọi buổi"; cờ `--mot-bieu-mau` (chỉ với `--fa-daa`, ngược lại `ap.error`).
- Bộ chuyển đổi `doc_dang_ky_fa_forms`: KHÔNG đổi (test chứng minh một tệp gộp cho cùng kết quả hai tệp từng ngày; nộp lại: phiếu cuối thắng mỗi ngày).
- Mặc định không đổi: `--fa-daa`, `--phan-hoi`, `--tuan-3` ra tệp giống từng byte so với trước (`diff -r`).
- Test mới (đỏ trước): `tests/test_fa_m2b_mot_bieu_mau.py` (13; đột biến bỏ một ngày khỏi `cac_phan_fa_gop` làm 5 ca đỏ).
- Tài liệu: `docs/ke_hoach/FA_DAA_KE_HOACH.md` §4 (cột đường B). Không chọn D8.

## 2026-11-10 — GAP-14: bản ghi nhớ D1 (ưu tiên bù), KHÔNG có mã

- Mới `docs/ke_hoach/FA_GAPS_D1_MEMO.md`: ba phương án A/B/C, rủi ro khuyến khích, bảng `hai_ky` đo bằng `du_lieu_test/mo_phong_fa_daa.py --n 100 --so-seed 5 --hai-ky 15` (SỐ LIỆU MÔ PHỎNG), ngoại lệ bất biến 2 mà B/C cần, câu hỏi cho Truong. Trạng thái: chờ Truong.
- Test: thêm 1 ca vào `tests/test_fa_gap12_mo_phong.py` (bản ghi nhớ có nhãn, có lệnh, số khớp lần chạy lại).

## 2026-11-10 — GAP-13: chu trình cải thiện ổn định, chế độ đo (không bảo đảm ổn định)

- Mới `fa_vong_doi_cho.py` (hàm thuần): `tim_chu_trinh`, `chay_chu_trinh` (Erdil & Ergin 2008: em có khoá tốt nhất — cho phép hoà — trong những em muốn CLB đó mới được nhận chỗ; chỉ thứ tự bốc thăm giữa các em hoà khoá bị bỏ qua), `khoa_tho_fa` (khoá FA không có bốc thăm: giữ chỗ, điểm, huy chương), `NHAN_KHONG_BAO_DAM`.
- Cờ mới `rules.fa_vong_doi_cho` (mặc định TẮT, cần `fa_daa`; không vào dấu vân tay). `api_sau_xep.py`: `get_vong_doi_cho` CHỈ ĐỌC (không ghi `match_results` hay `fa_dieu_chinh`), trả các chu trình và số em được lợi kèm nhãn.
- Mô phỏng: bảng `vong_doi_cho_theo_loai` (% em được lợi theo kiểu) chỉ trong `chay_mo_phong_day_du` (`--day-du`).
- Spec sửa khi làm: điều kiện thừa "khoá không kém người đang giữ chỗ" làm chu trình không thể có với bốc thăm đơn (STB); đã bỏ, ghi trong `FA_GAPS_KE_HOACH.md`.
- Test mới (đỏ trước): `tests/test_fa_gap13_vong_doi_cho.py` (5; có 200 ca ngẫu nhiên: không ai thiệt, sức chứa giữ nguyên, không cặp chặn với khoá tốt hơn hẳn).

## 2026-11-10 — GAP-12: mô phỏng đầy đủ — kiểu "tính toán", bảng cũ/mới theo kiểu (SỐ LIỆU MÔ PHỎNG)

- `du_lieu_test/mo_phong_fa_daa.py`: `HANH_VI_DAY_DU` (thêm `tinh_toan`); `dang_ky(..., cat_ky_truoc=None)`: em tính toán xếp thật nhưng bỏ CLB Tuyển chọn khi điểm dưới mốc nhận thấp nhất kỳ trước (`_duoi_cat`) và đặt vàng vào CLB Giới hạn xếp cao nhất không quá tải kỳ trước; `cat_ky_truoc` (mốc mỗi CLB từ kỳ 1); `theo_loai` (kỳ 2, cùng dữ liệu cho hai chế độ: % NV1, top 2, không CLB theo chế độ × kiểu, % thua bốc thăm theo kiểu); `chay_mo_phong_day_du` và cờ `--day-du`. `sinh_du_lieu(..., hanh_vi=HANH_VI)`: mặc định rút ngẫu nhiên y như cũ, nên bảng FA-10 (`chay_mo_phong`) không đổi.
- Test mới: `tests/test_fa_gap12_mo_phong.py` (5; đột biến `<` → `<=` ở luật mốc và bỏ luật dời vàng đều bị bắt).

## 2026-11-10 — GAP-11: công thức Power Fx màn đăng ký FA, đường A (TH)

- Mới `mau_forms_thi_clb/bo_dung_t4m/cong_thuc_fa.py`: `tao_dang_ky_fa` sinh `02_app/DangKyFA.txt` theo đặc tả §12 (R39–R54): xáo thứ tự CLB mỗi lần mở ngày (`Shuffle`), ▲▼ đổi chỗ, tối đa 7 không trùng, tối thiểu 3 (hoặc tất cả), cảnh báo thiếu CLB Tự do, tự lưu MỘT `Patch` đặt DRAFT sau mỗi thao tác (`TU_LUU`), nộp SUBMITTED có đọc lại khoá, widget huy chương (mặc định ba CLB không Tự do, tự cập nhật khi chưa chỉnh, giữ khi `HC_TuChinh = Có`, hoán đổi, không đặt vào Tự do, nhắc vàng ở Tuyển chọn). Lọc trên ECA/CLB qua `soat_loc_uy_quyen`.
- `bo_dung_t4m/sinh_bk1.py`: chỉ khi `fa` mới ghi thêm tệp này (README liệt kê); bộ dựng mặc định giống từng byte (đã so với bản cũ). Ghi chú FA và đặc tả §12.5 cập nhật. Không chọn D8.
- Test mới (đỏ trước): `tests/test_fa_gap11_cong_thuc_fa.py` (5).

## 2026-11-10 — GAP-8: bảng điều khiển quản trị (V§11), chỉ đọc

- `fa_sau_xep.py`: `chi_so_dashboard` (hàm thuần, 12 chỉ số theo thứ tự V§11: không có CLB, NV1, top 2, tỉ lệ bốc thăm, số em từng thua bốc thăm, đăng ký sau 3 ngày, thử thách nghiêm túc, độ lệch chấm, đi đủ 3 buổi, hài lòng, hiểu lý do, đổi huy chương; `gia_tri` None = chưa có dữ liệu, không bao giờ thay bằng 0; ba chỉ số nằm ngoài kiosk ghi nguồn `ngoai_kiosk`), `doc_du_lieu_dashboard` (chỉ SELECT; lý do và điểm danh chỉ của lần chạy gốc mới nhất mỗi buổi), `huy_chuong_mac_dinh` (D2, chỉ để đo tỉ lệ đổi; không vào khoá ưu tiên).
- `api_sau_xep.py`: `get_dashboard`, `export_dashboard` (`dashboard.xlsx` một trang: Chỉ số, Giá trị, Mục tiêu, Đạt, Nguồn; "chưa có dữ liệu"; không mã hay tên học sinh). Chỉ khi `rules.fa_daa` bật.
- Giao diện: khung `#dashboardPanel` ở thẻ Quản lý (bảng `#dbBang`, nút `#btnXuatDashboard`), khoá i18n `db_*` vi + en.
- Test mới (đỏ trước): `tests/test_fa_gap8_dashboard.py` (5), `tests/test_giao_dien_fa_gap8_dashboard.py` (2, Chromium).

## 2026-11-10 — GAP-7: gợi ý chỉ tiêu kỳ sau = NV1 kỳ này, chặn bởi giới hạn giáo viên

- `fa_daa.py`: `goi_y_chi_tieu` (hàm thuần: `goi_y_ky_sau = min(nv1, gioi_han)`, chưa khai giới hạn thì = nv1; `ghi_chu` khong_co_nv1 / khong_gioi_han / chan_boi_gioi_han), `kiem_tang_tu_goi_y` (dùng lại `kiem_chi_tang`: chỉ được tăng từ gợi ý).
- Bảng mới `fa_gioi_han_gv` (qua `DEFAULT_SCHEMA`; không đổi bảng `clubs`, hợp đồng CSV giữ nguyên).
- `api_xuat.py`: `_bang_nhu_cau_goi_y` (chỉ đọc, dùng chung), `export_goi_y_chi_tieu` (`goi_y_chi_tieu.csv`, không dữ liệu học sinh), `luu_gioi_han_gv`, `kiem_chi_tieu_ky_sau`; `export_bang_nhu_cau` thêm MỘT cột cuối `goi_y_ky_sau` (tệp xuất FA, không phải CSV đầu vào). Chỉ khi `rules.fa_daa` bật; mã lỗi mới `gioi_han_gv_sai`.
- Giao diện: nút `#btnXuatGoiY` ở khung xuất (chỉ hiện khi FA bật).
- Test mới (đỏ trước): `tests/test_fa_gap7_goi_y.py` (7); thêm 1 test Chromium vào `tests/test_giao_dien_fa_ket_qua.py`.

## 2026-11-10 — GAP-10: nhắc hạn đăng ký + danh sách chưa đăng ký cho GVCN (TH)

- Tài liệu mới `docs/he_sinh_thai/T4M_FLOW_NHAC_HAN.md`: ba lần nhắc (mở cổng, −2 ngày, −3 giờ) bằng email nhóm, nhắc riêng CLB Tuyển chọn chưa làm bài ×2, luật dưới 50 % sau 3 ngày → danh sách cho GVCN qua `T4M_FLOW_GUI_GVCN.md`, ước lượng theo giới hạn 6.000 yêu cầu/người/ngày. Nhãn TH/GĐ.
- Công cụ mới `mau_forms_thi_clb/danh_sach_chua_dang_ky.py`: `ty_le_dang_ky` (hàm thuần, cờ `DUOI_50` khi < 50 %), `doc_da_dang_ky` (cột "[student_id] …" của Forms hoặc `student_id`), ghi `chua_dang_ky_<lớp>.csv` (chỉ mã + lớp) và `tong_hop.csv`; in số email cần và cảnh báo khi vượt 6.000.
- Test mới (đỏ trước): `tests/test_fa_gap10_nhac_han.py` (4).

## 2026-11-10 — GAP-9: độ lệch giữa hai người chấm (TH)

- `mau_forms_thi_clb/phan_tich_cau_hoi.py`: `NGUONG_LECH_CHAM = 1.5`, `do_lech_cham(rows)` (hàm thuần: độ lệch tuyệt đối trung bình theo câu và theo CLB, cờ `LECH_CHAM` khi ≥ 1,5; dòng thiếu điểm người chấm 2 bị bỏ), `ghi_bao_cao(..., do_lech=None)` thêm trang "Độ lệch chấm" (các trang cũ giữ nguyên), lệnh `lech CHAM.csv --ra BAO_CAO.xlsx` (thiếu cột → báo, mã thoát 1).
- Test mới (đỏ trước): `tests/test_fa_gap9_lech_cham.py` (3).

## 2026-11-10 — GAP-6: khảo sát tuần 3 (2 câu) trên Forms

- `mau_forms_thi_clb/bieu_mau.py`: `cac_phan_tuan_3` (2 câu: còn đi sinh hoạt? muốn đổi CLB?); `mau_forms_thi_clb/tao_mau_forms.py`: `sinh_tuan_3`, cờ `--tuan-3` (dùng riêng, không ghép với cờ khác). Phần Microsoft ghi nhãn TH (chưa thử trên Microsoft thật).
- Nhập: dùng chung `nhap_phan_hoi_forms` / `doc_tep_forms_phan_hoi` (bảng `fa_phan_hoi`, `loai = tuan_3`); tổng hợp `tong_hop_phan_hoi(rows, "tuan_3")`; xuất trong `phan_hoi.xlsx`. Cùng cờ `rules.fa_phan_hoi`.
- Test mới (đỏ trước): `tests/test_fa_gap6_tuan_3.py` (4).

## 2026-11-10 — GAP-5: 3 câu phản hồi sau khi xem kết quả (kiosk + Forms)

- Cờ mới `rules.fa_phan_hoi` (mặc định TẮT, cần `fa_daa`). Bảng mới `fa_phan_hoi` (qua `DEFAULT_SCHEMA`).
- `fa_sau_xep.py`: `KHO_NHAT`, `tong_hop_phan_hoi`, `doc_tep_forms_phan_hoi` (đọc mã câu `[ma]` và mã lựa chọn `(ma)` từ tệp xuất Forms). `api_sau_xep.py`: `gui_phan_hoi`, `get_phan_hoi_tong_hop`, `nhap_phan_hoi_forms`, `export_phan_hoi` (`phan_hoi.xlsx`, không tên học sinh).
- Forms: `bieu_mau.py` thêm phần phản hồi, `tao_mau_forms.py` cờ `--phan-hoi` (`sinh_phan_hoi`), nhãn TH.
- Giao diện: khung `#phanHoiPanel` (bấm một lần mỗi câu), chữ hiển thị không xưng hô (đạt `chu_cam`). Mã lỗi mới `fa_phan_hoi_chua_bat`, `phan_hoi_gia_tri_sai`, `phan_hoi_tep_sai`.
- Nhập tệp Forms: mã ngoài miền (`MIEN_PHAN_HOI`) đọc thành rỗng, không ghi số sai.
- Test mới (đỏ trước): `tests/test_fa_gap5_phan_hoi.py` (8), `tests/test_giao_dien_fa_gap5_phan_hoi.py` (3, Chromium).

## 2026-11-10 — GAP-4: vòng 2 cho học sinh chưa có CLB mong muốn

- Cờ mới `rules.fa_vong_2` (mặc định TẮT, cần `fa_daa`).
- `fa_sau_xep.py`: `can_vong_2`, `cho_con_lai` (chỗ còn = chỉ tiêu − thành viên hiện tại − lời mời đang chờ), `chay_vong_2` (một lượt chọn theo thứ tự bốc thăm của buổi; mỗi lần chọn một dòng `round2` trong `fa_dieu_chinh`, không sửa kết quả xếp). `api_sau_xep.py`: `get_vong_2`, `chay_vong_2_api`.
- Giao diện: khung `#vong2Panel`. Mã lỗi mới `fa_vong_2_chua_bat`, `vong_2_da_chay`, `vong_2_lua_chon_sai`.
- Test mới (đỏ trước): `tests/test_fa_gap4_vong_2.py` (7), `tests/test_giao_dien_fa_gap4_vong_2.py` (2, Chromium).

## 2026-11-10 — GAP-3: khiếu nại lỗi dữ liệu trong hạn, chạy lại với seed đã khoá

- Cờ mới `rules.fa_khieu_nai` (mặc định TẮT, cần `fa_daa`) và `rules.fa_khieu_nai_so_ngay` (số nguyên 1..14, mặc định 3). Bảng mới `fa_khieu_nai`.
- `fa_sau_xep.py`: `SO_NGAY_KHIEU_NAI`, `bay_gio`, `trong_han_khieu_nai`, `anh_huong_sau_chay_lai` (liệt kê học sinh đổi chỗ và các điều chỉnh cũ cần soát lại, không bỏ âm thầm). `api_sau_xep.py`: `gui_khieu_nai`, `get_khieu_nai`, `xu_ly_khieu_nai` (chấp nhận ghi một dòng `appeal_rerun`; sửa dữ liệu rồi chạy lại toàn bộ pipeline với seed đã khoá, thêm dòng `run_history` mới), `export_khieu_nai` (`khieu_nai.csv`).
- Giao diện: khung `#khieuNaiPanel`; lỗi khi mở khung nay hiện thông báo thay vì ẩn khung (W1 N1); mã lỗi chung mới `loi_luu_sau_xep` (W1 N2) và `fa_khieu_nai_chua_bat`, `khieu_nai_da_xu_ly`, `khieu_nai_khong_hop_le`, `khieu_nai_qua_han`, `khieu_nai_trung`.
- Test mới (đỏ trước): `tests/test_fa_gap3_khieu_nai.py` (9), `tests/test_giao_dien_fa_gap3_khieu_nai.py` (4, Chromium).

## 2026-11-10 — GAP-2: mời học sinh đầu danh sách chờ vào chỗ được giải phóng

- `fa_sau_xep.py`: `moi_dang_cho`, `trang_thai_moi`, `hang_cho` (hàm thuần; dùng `fa_ly_do.waitlist_pos` — thứ tự D4 đã tính sẵn; chỉ em thua ở CLB đó và xếp nó cao hơn CLB hiện tại, không đang có lời mời, chưa từ chối), `moi_tiep` (mời khi thành viên + lời mời đang chờ < chỉ tiêu; chỉ CLB Giới hạn / Tuyển chọn).
- `api_sau_xep.py`: `get_moi_cho_trong`, `tra_loi_moi` (nhận / từ chối / hết hạn; mỗi bước một dòng `fa_dieu_chinh`; sau đó tự mời người kế tiếp). Giải phóng chỗ (GAP-1) tự gọi `moi_tiep`. Cùng cờ `rules.fa_diem_danh`.
- Giao diện: khung `#moiPanel` (nút Nhận / Từ chối / Hết hạn). Mã lỗi mới `moi_khong_con_cho`.
- Test mới (đỏ trước): `tests/test_fa_gap2_moi_cho.py` (9), thêm 1 test Chromium vào `tests/test_giao_dien_fa_gap1_theo_doi.py`.

## 2026-11-10 — GAP-1: điểm danh 3 buổi đầu, vắng 2/3 không phép thì giải phóng chỗ

- Cờ mới `rules.fa_diem_danh` (mặc định TẮT, chỉ bật được khi `fa_daa` bật: mã lỗi `fa_tinh_nang_can_fa`); không thuộc luật xếp nên không vào `run_history.luat_xep` hay dấu vân tay.
- `fa_sau_xep.py`: `can_giai_phong`, `NGUONG_VANG = 2`; `api_sau_xep.py` (mới, `SauXepMixin`): `get_diem_danh`, `luu_diem_danh` (đủ 2/3 buổi vắng không phép -> một dòng `release` trong `fa_dieu_chinh`, không sửa kết quả xếp), `export_diem_danh` (`diem_danh.xlsx`, mỗi CLB một trang, chữ an toàn cho Excel). Bảng mới `fa_diem_danh`.
- Giao diện: khung `#diemDanhPanel` ở thẻ Chi tiết (tệp mới `js/10_theo_doi.js`), ô `wzFaDiemDanh` ở bước luật của trình tạo không gian làm việc; 4 mã lỗi mới.
- Test mới (đỏ trước): `tests/test_fa_gap1_diem_danh.py` (10), `tests/test_giao_dien_fa_gap1_theo_doi.py` (3, Chromium).

## 2026-11-10 — GAP-0: nhật ký điều chỉnh sau khi xếp + hàm phát lại

- `fa_sau_xep.py` (mới): `vi_tri_hien_tai` (hàm thuần: kết quả lần chạy gốc + điều chỉnh phát lại theo `id`; dòng của lần chạy cũ hay không khớp chỗ hiện tại bị bỏ và báo `lech`), `run_goc_theo_buoi`, `doc_vi_tri`, `ghi_dieu_chinh` (cách duy nhất ghi, chỉ INSERT).
- `rbda_priority_pipeline.py` (`DEFAULT_SCHEMA`): bảng mới `fa_dieu_chinh` chỉ ghi thêm; CSDL cũ nhận bảng khi mở (`init_db`). `match_results`/`run_history` không bị sửa.
- `.claude/skills/soat-ma/scripts/kiem_nhanh.py`: `BANG_NHAT_KY` thêm `fa_dieu_chinh`.
- Test mới (đỏ trước): `tests/test_fa_gap0_dieu_chinh.py` (16 ca).

## 2026-11-10 — FA-P7/SM-3: kiem_nhanh --so-seed N > 5 chạy đủ N seed

- `.claude/skills/soat-ma/scripts/kiem_nhanh.py`: hàm mới `danh_sach_seed(n)` — n ≤ 5 lấy n seed đầu của `SEED_MAC_DINH` (không cờ: đúng 5 seed cũ); n > 5 thêm 2, 3, 4, … (bỏ số trùng) tới đủ n; tất định. `main` dùng hàm này; chữ trợ giúp ghi rõ luật. `--so-seed 20` nay in "60 ca (3 bộ × 20 seed) trùng khít" (trước đây cắt còn 15 ca).
- Test mới (đỏ trước): `tests/test_skill_soat_ma.py` — 3 test (`danh_sach_seed` mặc định / 20 seed khác nhau / `main --so-seed 20`).

## 2026-11-10 — SM-2: test giao diện chờ điều kiện thật thay cho 800 ms cố định

- `tests/test_giao_dien_fa_n2_luu_mac_dinh.py` (`test_sang_em_khac_giua_luc_luu_van_luu_huy_chuong_em_truoc`): bỏ `wait_for_timeout(800)`; chờ lời gọi bị giữ của HS1 về xong rồi dò CSDL tới khi huy chương HS1 đã lưu (tối đa 5 s). Chỉ đổi test, không đổi mã ứng dụng. Chạy 5 lần liền: 5/5 đạt (mỗi lần 2 biến thể).

## 2026-11-10 — FA-P5: cặp biên bản HTML + Excel luôn cùng tên gốc

- `api_xuat.py` (`_export_bien_ban_da_khoa`): chọn MỘT tên gốc cho cả cặp bằng `_duong_xuat(..., kem_duoi=(".xlsx",))`, đường Excel suy từ đường HTML. Thư mục đã có `bb.xlsx` -> `bb (2).html` + `bb (2).xlsx` (trước đây `bb.html` + `bb (2).xlsx`); không ghi đè tệp cũ.
- Test mới (đỏ trước): `tests/test_fa_bien_ban.py` — `test_api_html_va_xlsx_cung_ten_goc_khi_da_co_tep_xlsx`, `test_api_thu_muc_trong_thi_ten_goc_giu_nguyen`.

## 2026-11-10 — FA-P6: cảnh báo buổi thiếu lý do theo thứ tự ngày

- `api_xuat.py` (`_doc_ly_do_moi_nhat`): `tat_ca_buoi` sắp bằng `khoa_sap_buoi`, nên cảnh báo `fa_ly_do_thieu_buoi` của `export_ly_do_csv` và `thieu_buoi` (FA-P3) liệt kê `thu_2` trước `chu_nhat`.
- Test mới (đỏ trước): `tests/test_fa_n1_ly_do_mot_phan.py::test_buoi_thieu_ly_do_theo_thu_tu_ngay`.

## 2026-11-10 — FA-P4: biên bản bốc thăm liệt kê buổi theo thứ tự ngày

- `fa_bien_ban.py` (`tao_ban_ghi`): `dem_theo_buoi` sắp bằng `khoa_sap_buoi` (như FA-O1), nên `thu_2` đứng trước `chu_nhat` ở cả bản HTML lẫn Excel; mã băm và số liệu không đổi.
- Test mới (đỏ trước): `tests/test_fa_bien_ban.py::test_bien_ban_buoi_theo_thu_tu_ngay_ca_html_lan_xlsx`.

## 2026-11-10 — FA-P3: màn hình kết quả báo buổi thiếu lý do

- `api_xuat.py` (`get_ly_do_ket_qua`): khi FA bật trả thêm khoá `thieu_buoi` (buổi mà lần chạy mới nhất không dùng FA, nên không có lý do); FA tắt trả y như cũ.
- `index.html` + `js/03_ket_qua.js` (`loadMatchResults`): MỘT dòng thông báo `#lyDoThieuBuoi` trên bảng kết quả, chữ từ mã có sẵn `fa_ly_do_thieu_buoi` (không thêm câu mới); không thiếu buổi nào thì ẩn.
- Test mới (đỏ trước): `tests/test_fa_n1_ly_do_mot_phan.py` (3 test API, có test FA tắt không đổi), `tests/test_giao_dien_fa_ket_qua.py` (2 test Chromium).

## 2026-11-10 — SM-1: biên bản Excel không hỏng vì ký tự điều khiển

- `fa_bien_ban.py` (`ghi_xlsx`): mọi ô chữ đi qua `so_excel.lam_sach` (như `so_excel.Trang.o`). Tên workspace `"Kỳ\x01một"` trước đây làm `export_bien_ban_boc_tham` trả `error_exporting_csv` (IllegalCharacterError) và để lại tệp HTML; nay xuất đủ hai tệp. Chặn công thức FA-P1 giữ nguyên.
- Test mới (đỏ trước): `tests/test_fa_bien_ban.py` — `test_xlsx_bo_ky_tu_dieu_khien_ma_khong_hong`, `test_api_ten_workspace_co_ky_tu_dieu_khien_van_xuat_du_hai_tep`.

## 2026-11-10 — FA-KH: hướng dẫn mới nhất cho 7 lỗi nhỏ trước khi merge PR #14 (Truong yêu cầu)

- `LATEST_INSTRUCTION.md` (mới, gốc repo): phần 1 tiếng Việt cho người chạy (5 bước, xử lý sự cố); phần 2 tiếng Anh cho Claude (Sonnet): SM-1, FA-P3, FA-P4, FA-P6, FA-P5, SM-2, FA-P7/SM-3 theo thứ tự, mỗi mục test đỏ trước, quy tắc dừng, báo cáo `docs/phien/bao_cao_dem/<ngày>_sua_nho.md`.
- `docs/phien/claude__keen-ride-72sa7t.md`: thêm mục Plan "Pre-merge small fixes"; `docs/phien/CHAY_DEM_FA_DAA.md`: dòng trỏ sang tệp mới. Chỉ tài liệu, không đổi mã.

## 2026-11-10 — AI-LOG: nhật ký AI chỉ từ dữ liệu trong repo (Truong yêu cầu)

- `docs/nhat_ky_ai/NHAT_KY_AI.md` (mới, thay `NHAT_KY_AI_TAI_KHOAN_TRUONG.md` lấy từ lịch sử phiên): dựng CHỈ từ repo — 7 lời Truong lưu nguyên văn (kèm `FA_DAA_VISION.md`), 21 quyết định của Truong theo tiêu đề `CHANGELOG.md`, 12 luồng việc theo tệp bàn giao (phiên cha chép ô Session log, phiên con lồng bên dưới một dòng), bảng 70 phiên có dòng `Claude-Session` trong git, và phần trước lịch sử git. Không bình luận hay kết luận nghiên cứu.
- `docs/nhat_ky_ai/dung_nhat_ky_ai.py` (mới): script dựng lại tệp trên; chạy hai lần cho cùng kết quả; câu nguyên văn được kiểm có trong tệp nguồn. Nằm trong `docs/` nên không tính vào độ phủ.
- `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md` + `NHAT_KY_AI.docx` (Truong yêu cầu bản dễ đọc): tiếng Việt thường, bảng giải thích từ ngữ, 10 giai đoạn (mục tiêu / Truong quyết định / phiên chính / phiên phụ / kết quả), lời nguyên văn, giới hạn; Word A4 4 trang. `xuat_word.py` (mới) chuyển .md sang .docx có định dạng.
- `docs/nhat_ky_ai/NHAT_KY_AI_DAY_DU.md` (mới, Truong yêu cầu bản vừa dễ đọc vừa đủ chi tiết): mục 1–6 là bản dễ đọc, mục 7 dựng tự động xếp toàn bộ chi tiết vào 10 giai đoạn (24 quyết định, 146 mục `CHANGELOG.md`, 160 dòng phiên chính/phụ, 70 phiên có lưu mã; không sót mục nào). `NHAT_KY_AI.docx` nay dựng từ bản này: A4, 21 trang.

## 2026-11-10 — FA-CI3: CI Windows cài python-docx (PR #14, Truong chọn)

- `.github/workflows/tests.yml` job Windows và job test của `build-windows-exe.yml`: cài thêm `python-docx>=1.1,<2` (cùng ràng buộc với `requirements-dev.txt`). 9 test FA ghi tệp `.docx` (`test_fa_m2_forms_dang_ky.py`, `test_fa_m4_phan_tich.py`, `test_fa_m5_bo_dung.py`, `test_fa_n4_mot_de_khong_thi_lai.py`) chạy thật trên Windows thay vì đỏ `ModuleNotFoundError`; không test nào bị bỏ qua.

## 2026-11-10 — FA-CI2: test giao diện T3-19 hết chập chờn (CI Linux PR #14)

- `tests/test_giao_dien_t3_l3.py` `test_tai_bang_theo_clb_va_theo_ma_co_tim`: chờ bảng hiện đúng số thành viên CLB A (lấy từ `get_danh_sach_clb`) thay vì chỉ chờ `#kqBang` hiện; bảng "theo lớp" vẽ trước vẫn hiện tới khi danh sách CLB về, nên test có lúc đếm 2 dòng cũ. Tái hiện bằng độ trễ 1,5 giây cho `get_danh_sach_clb`: test cũ đỏ, test mới xanh; 5 lần liền xanh. Lỗi có sẵn từ trước PR, không do FA-DAA.

## 2026-11-10 — FA-CI1: sửa CI đỏ của PR #14 (Windows + văn phong)

- `du_lieu_test/mo_phong_fa_daa.py`, `mau_forms_thi_clb/so_sanh_suc_chua.py`: `main` chuyển stdout/stderr sang UTF-8 (`reconfigure`, như `du_lieu_test/sinh_du_lieu_diem_quyet_tam.py`); console Windows cp1252 làm hai script này ném `UnicodeEncodeError` khi in tiếng Việt. Tái hiện trên Linux bằng `PYTHONIOENCODING=cp1252` (4 đỏ trước, xanh sau).
- `tests/test_mo_phong_fa_daa.py` `test_chay_dong_lenh`: đọc đầu ra script bằng `encoding="utf-8"` (như `test_fa_nhu_cau.py`); trên Windows bảng mã mặc định cp1252 làm `stdout` thành `None`. Tái hiện bằng `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`: đỏ trước, xanh sau.
- `i18n_errors.py` (+ `i18n_loi.js` sinh lại): câu tiếng Anh của `bien_ban_chua_boc_tham` bỏ từ nội bộ "seed" (FA-9). `i18n.js`, `index.html`: nút biên bản ghi "bản in và Excel" / "printable page and Excel" thay chữ HOA "HTML" (FA-9, FA-9b). Cả hai do `tests/test_van_phong_tu_nhien.py` bắt.
- Không test nào bị bỏ qua hay tắt.

## 2026-11-10 — FA-P2: nhập tại chỗ, huy chương mặc định vẫn lưu khi người nhập sang em khác giữa lúc lưu (soát đêm 5)

- `js/04_nhap_tai_cho.js`: nút lưu nguyện vọng gọi `hcTheoNguyenVong` cả khi em vừa lưu không còn mở; `hcTheoNguyenVong` vẫn tính và gọi `submit_huy_chuong` cho đúng em đó, chỉ vẽ lại Bước 3 khi em đó còn mở; câu nhắc "đã chỉnh tay" của em đang mở không bị xoá. Trước đây em đó có nguyện vọng mà không có huy chương nào và lần chạy xếp sau không báo gì (FA-N2, đêm 4).
- Test mới: 2 ca Chromium trong `tests/test_giao_dien_fa_n2_luu_mac_dinh.py` (giữ `submit_preferences` hay `get_student_entry_state` của em trước; đỏ trước; 2 đột biến bắt được; 5 lần liền không chập chờn).

## 2026-11-10 — FA-P1: biên bản bốc thăm bản Excel không nhận công thức (soát đêm 5)

- `fa_bien_ban.py` `ghi_xlsx`: ô mà openpyxl hiểu là công thức (tên kỳ hay tên buổi mở đầu `=`, `+`, `-`, `@`) được ép về chữ, giữ nguyên văn (`data_type = "s"`, `quotePrefix`), như `so_excel.Trang.o`. Lỗi do FA-9b (đêm 5).
- Test mới: 2 test trong `tests/test_fa_bien_ban.py` (đỏ trước: có thẻ `<f>`; đột biến bỏ dòng ép kiểu bắt được).

## 2026-11-10 — FA-9b: biên bản bốc thăm bản Excel (đêm 5, Truong duyệt)

- `fa_bien_ban.py` `ghi_xlsx` (cùng bản ghi với HTML, không mã/tên học sinh); `api_xuat.py` `export_bien_ban_boc_tham` ghi thêm `.xlsx` cạnh `.html` (không ghi đè tệp cũ), trả `path_xlsx`; nút ở thẻ Kết quả báo cả hai tệp (`i18n.js`, `index.html`, `js/03_ket_qua.js`).
- Test mới: 5 test trong `tests/test_fa_bien_ban.py` (đỏ trước; 3 đột biến bắt được) + kiểm tệp .xlsx trong test Chromium của `tests/test_giao_dien_fa_ket_qua.py`.

## 2026-11-10 — FA-O1: lý do kết quả sắp theo thứ tự ngày (đêm 5)

- `api_xuat.py` `_doc_ly_do_moi_nhat`: sắp các dòng theo `khoa_sap_buoi` (cùng khoá với `COLLATE THU_TU_BUOI`), không theo chuỗi thường; `chu_nhat` đứng sau `thu_2` ở `ket_qua_ly_do.csv` và cột "Lý do". Lỗi do bản sửa FA-N1 gây ra (soát đêm 4).
- Test mới: 1 test trong `tests/test_fa_n1_ly_do_mot_phan.py` (đỏ trước khi sửa; đột biến bắt được). Vá luôn lỗ hổng FA-O2.

## 2026-11-09 — FA-10: mô phỏng so sánh chế độ cũ và FA-DAA, hành vi hai kỳ của D1 (đêm 4)

- `du_lieu_test/mo_phong_fa_daa.py` (mới, không đụng phần mềm): cùng dữ liệu sinh có hạt giống, chạy chế độ cũ (điểm thi + hai quỹ) và `chay_fa_daa`; in bốn bảng: %NV1 / %top 2 / %không CLB, % dòng theo lý do, % thua bốc thăm theo hành vi (lười / thật thà / chiến lược), và bảng hai kỳ D1 (em xếp CLB Giới hạn hot nhất lên NV1 cố ý; không bù và có bù — bù chỉ mô phỏng bằng cách xếp em lên đầu bốc thăm kỳ 2). Mỗi bảng ghi "SỐ LIỆU MÔ PHỎNG"; KHÔNG có câu nhận định. D1 chưa cài vào phần mềm.
- Test mới: `tests/test_mo_phong_fa_daa.py` (9).

## 2026-11-09 — FA-9: biên bản bốc thăm có người chứng kiến (đêm 4)

- `fa_bien_ban.py` (mới, hàm thuần): `sha256_stb`, `tao_ban_ghi`, `html_bien_ban`. `api_xuat.py` `export_bien_ban_boc_tham` → `bien_ban_boc_tham.html` (kỳ, thời điểm, dấu vân tay dữ liệu, hạt giống, SHA-256 danh sách (mã HS, số bốc thăm) đã sắp, số liệu từng buổi, thứ tự buổi lễ, dòng ký; không tên/mã học sinh; cảnh báo nếu dữ liệu đã sửa sau lần chạy). Chỉ đọc, không đổi schema/CSV. `i18n_errors.py` + `i18n_loi.js`: `bien_ban_chua_boc_tham`. Nút "Xuất biên bản bốc thăm" ở thẻ Kết quả (chỉ khi FA bật): `index.html`, `js/03_ket_qua.js`, `i18n.js`.
- Test mới: `tests/test_fa_bien_ban.py` (9) + 1 test Chromium trong `tests/test_giao_dien_fa_ket_qua.py`.

## 2026-11-09 — FA-N4: cảnh báo CLB chỉ có một đề thì không thi lại được (đêm 4)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: em bị gắn cờ làm quá nhanh ở CLB chỉ có một đề → cảnh báo "không có đề thi lại; giữ điểm bài đầu" (thay câu hứa thi lại). `mau_forms_thi_clb/tao_mau_forms.py`: `CAI_DAT_FORMS_BIEN_THE.md` có thêm dòng nói rõ. CLB có từ hai đề: không đổi.
- Test mới: `tests/test_fa_n4_mot_de_khong_thi_lai.py` (3).

## 2026-11-09 — FA-N3: câu báo rõ khi bật FA mà tắt điểm quyết tâm (đêm 4)

- `cau_hinh_ws.py` `FaCanDiemQuyetTam(ValueError)`, `api_workspace.py` bắt riêng, `i18n_errors.py` + `i18n_loi.js`: mã `fa_can_diem_quyet_tam` (song ngữ) thay lỗi chung `ws_du_lieu_sai` ở bước luật (tạo và sửa cấu hình). Lỗi luật khác vẫn là lỗi chung.
- Test mới: `tests/test_fa_n3_loi_diem_quyet_tam.py` (5); sửa kỳ vọng `tests/test_giao_dien_fa_cai_dat.py` (câu mới) và danh sách mã mới `tests/test_ws_nhan.py`.

## 2026-11-09 — FA-N2: màn nhập tại chỗ lưu huy chương mặc định và đi theo thứ tự mới (đêm 4)

- `js/04_nhap_tai_cho.js` (`hcTheoNguyenVong`), `index.html` (`hcNhacDaChinh`), `i18n.js` (`hc_nhac_da_chinh`): sau khi lưu nguyện vọng ở workspace FA, mỗi ngày: chưa có huy chương → lưu mặc định D2; huy chương = mặc định của thứ tự cũ và thứ tự đổi → lưu mặc định mới; đã chỉnh tay → giữ nguyên + câu nhắc. Chỉ gọi `submit_huy_chuong`; không suy diễn ở máy chủ, không đổi schema.
- Test mới: `tests/test_giao_dien_fa_n2_luu_mac_dinh.py` (3, Chromium chạy thật).

## 2026-11-09 — FA-N1: lý do theo từng buổi sau khi chạy lại một phần (đêm 4)

- `api_xuat.py` `_doc_ly_do_moi_nhat`: mỗi buổi lấy lý do của lần chạy mới nhất CÓ chạy buổi đó (`run_history.buoi_da_chay`); buổi mà lần đó không phải FA thì bỏ và báo `canh_bao` (`fa_ly_do_thieu_buoi`); chỉ lỗi `fa_chua_co_ly_do` khi không buổi nào có lý do. `i18n_errors.py` + `i18n_loi.js`: mã mới.
- Test mới: `tests/test_fa_n1_ly_do_mot_phan.py` (3). FA tắt: không đổi.

## 2026-11-09 — FA-SOAT3: soát đêm 3 và mở đêm 4 (chỉ tài liệu, chưa sửa lỗi)

- `docs/phien/bao_cao_dem/2026-11-09_soat_dem3.md`: kết luận GO; FA-N1 (chạy lại một ngày làm mất lý do của ngày khác, đã tái hiện), FA-N2 (màn nhập tại chỗ không lưu huy chương mặc định, đã tái hiện), FA-N3, FA-N4.
- `docs/ke_hoach/FA_DAA_KE_HOACH.md` §7: spec đêm 4 (FA-N1..N4, FA-9, FA-10). `docs/phien/CHAY_DEM_FA_DAA.md`: giao thức đêm 4. `docs/phien/claude__keen-ride-72sa7t.md`: Plan đêm 4.

## 2026-11-09 — FA-UI-5: mục hướng dẫn sử dụng "Xếp theo loại CLB và huy chương" (đêm 3, chỉ tài liệu)

- `HUONG_DAN_SU_DUNG.md` §15 (mới) + mục lục: bật ở bước luật (cần điểm quyết tâm), bốn cột mới của Sổ nhập và trang Giữ chỗ, bước huy chương, cột Lý do và `ket_qua_ly_do.csv`, `bang_nhu_cau.csv`.
- Test mới (trong tệp cũ): `tests/test_fa_m6_tai_lieu.py` `test_fa_ui_5_huong_dan_su_dung_co_muc_xep_theo_loai_clb`.

## 2026-11-09 — FA-UI-4: câu lý do ở thẻ kết quả và hai nút xuất (đêm 3)

- `api_xuat.py`: `get_ly_do_ket_qua` (mới: câu giải thích của lần chạy mới nhất theo học sinh và buổi; FA tắt thì `fa_bat` false); `_doc_ly_do_moi_nhat` và `_cau_cua_dong` dùng chung với `_export_ly_do_da_khoa` (cùng kết quả như trước).
- `index.html`, `js/03_ket_qua.js` (`veCotLyDo`): cột "Lý do" và nút `#btnXuatLyDo` (`export_ly_do_csv`), `#btnXuatNhuCau` (`export_bang_nhu_cau`) chỉ khi FA bật; tắt thì không cột, nút ẩn. `i18n.js`: chữ vi + en.
- Test mới: `tests/test_giao_dien_fa_ket_qua.py` (3 ca Chromium). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 221 tệp test.

## 2026-11-09 — FA-UI-3: bước "Huy chương" ở màn nhập tại chỗ (đêm 3)

- `api_quan_ly.py`: `get_student_entry_state` thêm khoá `huy_chuong` khi FA bật (`_trang_thai_huy_chuong`: huy chương đã lưu, loại và buổi của từng CLB trong nguyện vọng, khoá). Tắt: phản hồi như cũ.
- `index.html`, `js/04_nhap_tai_cho.js` (`renderHuyChuongStep`, `hcDoi`, `hcCapNhatNhac`, `hcThuThap`): FA bật thì bước 3 là ba ô vàng / bạc / đồng mỗi ngày thay cho điểm quyết tâm; điền sẵn theo thứ tự nguyện vọng, bỏ CLB Tự do (D2, chỉ ở lớp đăng ký); chọn CLB đang có huy chương khác thì đổi chỗ (đủ 6 cách đặt); câu nhắc V§6.1 khi vàng ở CLB Tuyển chọn; lưu qua `submit_huy_chuong`, lỗi server hiện ra. `i18n.js`: chữ vi + en.
- Test mới: `tests/test_giao_dien_fa_huy_chuong.py` (6 ca Chromium). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 220 tệp test.

## 2026-11-09 — FA-UI-2: cột FA trong bảng CLB ở thẻ Quản lý (đêm 3)

- `api_quan_ly.py` (`list_clubs_admin`): khi FA bật, mỗi CLB thêm `loai`, `diem_san`, `so_toi_thieu`, `suc_chua_phong`, `n_giu_cho`; tắt thì phản hồi như cũ.
- `js/05_quan_ly.js` (`veCotFaBangClb`, `oFaClb`): năm cột Loại, Điểm sàn, Tối thiểu, Sức chứa phòng, Giữ chỗ chỉ khi có dữ liệu FA; tắt thì không thêm phần tử nào. `i18n.js`: `th_fa_*`, `fa_loai_*` (vi + en).
- Test mới: `tests/test_giao_dien_fa_quan_ly.py` (3 ca Chromium). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 219 tệp test.

## 2026-11-09 — FA-UI-1: công tắc "Xếp theo loại CLB và huy chương" khi tạo không gian làm việc (đêm 3)

- `js/075_workspace.js`: bước luật có ô `#wzFaDaa` (tắt sẵn, lấy theo mẫu), hàng xem lại `#rvFaDaa`; chỉ gửi `rules.fa_daa: true` khi bật (tắt: cấu hình gửi đi như cũ); bật mà tắt điểm quyết tâm thì backend từ chối bằng lỗi sẵn có `ws_du_lieu_sai`, hiện trên màn hình. `wsApDungCauHinh` đặt `FA_BAT` (khai báo ở `js/05_quan_ly.js`) cho các màn FA sau.
- `i18n.js`: `ws_r_fa_daa`, `ws_r_fa_daa_ngan`, `ws_r_fa_daa_ghi_chu` (vi + en). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 218 tệp test.
- Test mới: `tests/test_giao_dien_fa_cai_dat.py` (5 ca Chromium, đều chạy thật).

## 2026-11-09 — FA-S10: sửa dòng đường B trong bảng D8 (đêm 3, chỉ tài liệu)

- `docs/ke_hoach/FA_DAA_KE_HOACH.md` §4: đường B ghi "huy chương theo thứ tự + câu vàng và câu đổi bạc/đồng (đủ 6 cách đặt)" thay cho "không đổi được". Không đổi mã.

## 2026-11-09 — FA-S11: ghép email với mã học sinh cho list KetQua (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py` (`chuyen_fa_daa`): ghi thêm `EMAIL_MA_HS.csv` (Email, student_id; dữ liệu cá nhân, chỉ trên máy IT).
- `mau_forms_thi_clb/ghep_ket_qua_email.py` (mới): `ket_qua_ly_do.csv` + `EMAIL_MA_HS.csv` -> `KETQUA_NHAP_LIST.csv` với các cột list `KetQua`; em thiếu email: cảnh báo, dòng vẫn ghi, Email rỗng.
- `docs/he_sinh_thai/FA_SAU_XEP.md` §2: cách ghép mới, cột `Email` "Lấy từ". `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 217 tệp test.
- Test mới: `tests/test_fa_s11_ghep_email.py` (4 ca).

## 2026-11-09 — FA-S6: bộ sinh biểu mẫu đăng ký đọc Loại CLB từ Sổ nhập CLB (đêm 3, TH)

- `mau_forms_thi_clb/tao_mau_forms.py`: `--fa-daa --so-nhap-clb <Sổ nhập CLB của FA-M1>` đọc Loại bằng `chuyen_forms_sang_phan_mem.doc_clb_fa` (`de_theo_so_nhap_clb`); CLB Tự do không có trong câu vàng; hướng dẫn ghi Loại lấy từ sổ. `--so-nhap-clb` chỉ dùng cùng `--fa-daa`. Không có cờ: tệp sinh ra giống hệt từng byte (đã so `diff -r` trước/sau).
- Test mới (trong tệp cũ): `tests/test_fa_m2_forms_dang_ky.py` `test_fa_s6_so_nhap_clb_bo_clb_tu_do_khoi_cau_vang`, `test_fa_s6_so_nhap_clb_chi_dung_cung_fa_daa`.

## 2026-11-09 — FA-S4: báo khi không đọc được giờ làm bài (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py` (`_thoi_gian_lam_bai`): nhận ô `datetime` và chữ ISO; trả thêm số phiếu không đọc được (không đoán thứ tự ngày/tháng). `chuyen_fa_daa` thêm MỘT cảnh báo mỗi tệp kèm số phiếu đó.
- Test mới (trong tệp cũ): `tests/test_fa_m4_phan_tich.py` `test_fa_s4_thoi_gian_iso_va_datetime_doc_duoc_dang_khac_dem_loi`, `test_fa_s4_mot_canh_bao_moi_tep_kem_so_phieu`.

## 2026-11-09 — FA-S2: bỏ câu theo từng đề (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `bo_cau` khoá `(CLB, đề, số câu)`; CLI `--bo-cau CLB-DE-SO` (ví dụ `C3-B-4`, hàm `_doc_bo_cau`); dạng cũ `CLB-SO` chỉ nhận khi CLB có một đề, nếu không là lỗi nêu các đề (`_chuan_bo_cau`). Bỏ câu 4 đề B không đổi điểm đề A.
- `mau_forms_thi_clb/tao_mau_forms.py`: dòng hướng dẫn `--bo-cau` trong `CAI_DAT_FORMS_BIEN_THE.md` (chỉ chế độ `--bien-the`).
- `tests/test_fa_m4_phan_tich.py`: 3 ca mới `test_fa_s2_*`; ca cũ `test_bo_cau_cham_lai_cho_moi_hoc_sinh` dùng dạng mới (CLB có hai đề).

## 2026-11-09 — FA-S5: cảnh báo khi em làm sai đề được giao (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py` (`chuyen_fa_daa`, khi có `--bien-the-tep`): bài làm đề khác đề giao (`chon_bien_the`, hoặc `chon_bien_the_thi_lai` với bài thi lại hợp lệ) -> một cảnh báo nêu email, CLB, đề đã làm và đề giao; vẫn giữ điểm.
- Test mới (trong tệp cũ): `tests/test_fa_m4_phan_tich.py` `test_fa_s5_lam_sai_de_duoc_giao_thi_canh_bao_giu_diem`; thêm một dòng kiểm vào ca thi lại FA-S1.

## 2026-11-09 — FA-S1: bài thi lại chỉ tính khi lần đầu bị gắn cờ và đúng đề thi lại (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `--fa-daa` giữ mọi bài của một CLB rồi `_tach_lan_dau` chọn "bài lần đầu" theo đề giao (`chon_bien_the`), không theo thứ tự tệp; trung vị D9 chỉ trên bài lần đầu; bài lần hai thay bài lần đầu CHỈ khi lần đầu bị cờ quá nhanh và bài lần hai là đề `chon_bien_the_thi_lai`; mọi bài lần hai khác: không tính + cảnh báo. Chế độ mặc định (không `--fa-daa`) giữ "giữ bài đầu", đường mã không đổi.
- Test mới (trong tệp cũ): `tests/test_fa_m4_phan_tich.py` 3 ca `test_fa_s1_*` (thi lại hợp lệ, lần hai không cờ bị bỏ, đảo thứ tự tệp cho cùng kết quả).

## 2026-11-09 — FA-S3: cân bằng đề không dịch điểm khi một phía có ít bài (đêm 3, TH)

- `mau_forms_thi_clb/phan_tich_cau_hoi.py` (`so_sanh_bien_the`): `N_NHO` (chỉ báo, không dịch) khi đề này HOẶC phần còn lại có ít hơn `N_TOI_THIEU` bài.
- `tests/test_fa_m4_phan_tich.py`: ca mới `test_fa_s3_mot_phia_nho_thi_khong_dich_ca_hai_de`; ca cũ `test_d11_de_it_hon_5_em_chi_bao_khong_bao_gio_chinh` đổi kỳ vọng của đề A sang `N_NHO` (đúng theo spec §6.2).

## 2026-11-09 — FA-S7, FA-S9: xuất lý do chỉ của lần chạy mới nhất; test rollback bảng FA (đêm 3)

- `api_xuat.py` (`_export_ly_do_da_khoa`): lấy lần chạy mới nhất trong `run_history`; lần đó không có lý do FA thì trả `fa_chua_co_ly_do` (không xuất lý do của lần FA cũ hơn).
- FA-S9 (chỉ test): lỗi ném sau lần ghi FA cuối -> `fa_nhom`, `fa_ly_do`, `match_results`, `run_history` giữ nguyên.
- Test mới (trong tệp cũ): `tests/test_fa_ly_do.py` `test_fa_s7_xuat_ly_do_chi_lay_lan_chay_moi_nhat`, `test_fa_s9_chay_hong_sau_khi_ghi_fa_rollback_ca_hai_bang`.

## 2026-11-09 — FA-S8: nhập CSV CLB khi FA tắt giữ nguyên dòng (đêm 3)

- `api_nhap.py` (`import_clubs_csv`): FA tắt thì không đọc cột FA nữa (ô loại sai không còn làm bỏ dòng); dòng vẫn được tạo, một cảnh báo `fa_cot_bo_qua`. FA bật: như cũ.
- Test mới (trong tệp cũ): `tests/test_fa_du_lieu.py` `test_fa_s8_csv_fa_tat_bo_cot_fa_giu_dong`, `test_fa_s8_csv_fa_bat_giu_hanh_vi_cu`.

## 2026-11-09 — FA-SOAT2: soát đêm 2 và mở đêm 3 (chỉ tài liệu, chưa sửa lỗi)

- `docs/phien/bao_cao_dem/2026-11-09_soat_dem2.md`: kết luận GO; danh sách sửa FA-S1..FA-S11 (6 lỗi mới của bộ chuyển đổi / bộ sinh, 4 phát hiện còn mở của soát đêm 1, 1 chỗ hở email ↔ mã học sinh). Theo yêu cầu của Truong: chưa sửa.
- `docs/ke_hoach/FA_DAA_KE_HOACH.md` §6: spec đêm 3 (sửa lỗi rồi FA-UI-1..5). `docs/phien/CHAY_DEM_FA_DAA.md`: giao thức đêm 3. `docs/phien/claude__keen-ride-72sa7t.md`: Plan đêm 3.

## 2026-11-09 — FA-M6: Tài liệu sau khi xếp (kết quả, phản hồi, khiếu nại, nhắc hạn, điểm danh) (đêm 2, TH = chưa thử trên Microsoft thật)

- `docs/he_sinh_thai/FA_SAU_XEP.md` (mới, chỉ tài liệu): `ket_qua_ly_do.csv` -> list `KetQua` (cách C; IT ghép email), màn kết quả và ba nút phản hồi -> list `PhanHoi`, Forms khiếu nại (3 ngày, chỉ lỗi dữ liệu, chạy lại cùng seed) và khảo sát tuần 3, flow nhắc (mở cổng, -2 ngày, -3 giờ, NOT_ATTEMPTED hai lần, dưới 50 % sau 3 ngày -> GVCN), phép tính hạn mức 6.000 (mỗi em một thư chạm hạn mức; gửi lô Bcc 50 người ≈ 225 yêu cầu), list `DiemDanh` với cột tính `GiaiPhong`, xuất danh sách chờ; bảng kiểm K1..K14 (TH). Không nói đường nào nên chọn (D8 mở).
- Test mới: `tests/test_fa_m6_tai_lieu.py` (6 ca: cột CSV khớp mã xuất `api_xuat.py`, đủ tên list/biểu mẫu/flow, phép tính, nhãn TH, không dữ liệu thật). Không đổi mã.

## 2026-11-09 — FA-M5: Đặc tả Power Apps v2 (đường A) và cột list FA-DAA (đêm 2, TH = chưa thử trên Microsoft thật)

- `T4M_DAC_TA_SUA_APP.md` §12 (mới): màn đăng ký v2 (xáo `Shuffle()`, ▲▼, tự lưu `Patch` DRAFT, tối thiểu 3, cảnh báo thiếu CLB Tự do, nhãn thẻ, Nộp SUBMITTED, ước tính số yêu cầu so với 6.000) và widget huy chương (mặc định theo thứ tự, tự cập nhật khi chưa chỉnh tay, hoán đổi, vàng vào Tuyển chọn có nhắc); yêu cầu R39 đến R54, tất cả TH; không nói đường nào nên chọn (D8 mở).
- `bo_dung_t4m`: `cot_lists.ECA_FA` / `TAT_CA_FA` (`WP1..WP7` = huy chương, `HC_TuChinh`, `TrangThai` DRAFT/SUBMITTED/Đã khóa, không `THIk`); `site_script`, `mau_csv`, `sinh_bk1`, `tao_bo_dung_t4m.py --fa-daa` (+ `00_FA_DAA_GHI_CHU.md`). Không cờ: bộ dựng cho ra đúng như trước (`diff -r` giống hệt).
- `tests/test_t4m_bo_dung_bk34.py`: test "nhắc mọi R1 đến R38" chỉ đếm R1..R38 (R39 trở đi thuộc bộ FA).
- Test mới: `tests/test_fa_m5_bo_dung.py` (10 ca). Công thức Power Fx `02_app/` chưa viết lại cho màn FA.

## 2026-11-09 — FA-M4: Đề biến thể, phân tích câu hỏi và cân bằng điểm giữa các đề (đêm 2, TH = chưa thử trên Microsoft thật)

- `mau_forms_thi_clb/phan_tich_cau_hoi.py`: `chon_bien_the` (crc32(email) % n), `kiem_bien_the`, `phan_tich_cau` (V§7.5: % đúng, độ phân biệt 1/3 trên - 1/3 dưới, cờ PHAN_BIET_AM / QUA_DE / QUA_KHO), `so_sanh_bien_the` (D11: ngưỡng z·√(s²/n+s²/n), z = 1,96 hoặc 2,39; n < 5 chỉ báo; vượt ngưỡng thì dịch về trung bình chung; làm tròn nửa lên, kẹp 0-10), lệnh `chia` (Email -> đề giao, đề thi lại).
- `tao_mau_forms.py --bien-the`: mỗi CLB có `de_thi_bien_the` (đề B, C trong de_thi.json) sinh một biểu mẫu cho từng đề + `CAI_DAT_FORMS_BIEN_THE.md` (time limit BẬT, xáo câu và lựa chọn BẬT). Lệch so với bảng việc: phần hướng dẫn nằm ở tệp riêng này, không chèn vào `CAI_DAT_FORMS_CHI_THI.md`, để chế độ `--chi-thi` vẫn giống hệt từng byte khi không có cờ.
- `chuyen_forms_sang_phan_mem.py --fa-daa`: `--bien-the-tep`, `--ap-dung-dieu-chinh`, `--giu-diem-goc`, `--bo-cau`; có chênh lệch ngoài ngưỡng thì ghi `DIEU_CHINH_BAN_DE.xlsx` rồi dừng (mã thoát 3) tới khi admin chọn một cờ; luôn ghi `PHAN_TICH_CAU_HOI.xlsx`.
- Không cờ: `--chi-thi`, `--moi-clb` (sinh tệp) và chế độ mặc định của bộ chuyển đổi cho ra đúng như trước (so bằng `diff -r` và so nội dung ô).
- Test mới: `tests/test_fa_m4_phan_tich.py` (24 ca).

## 2026-11-09 — FA-M3: Bộ chuyển đổi chế độ FA-DAA (đường A và đường B) (đêm 2, TH = chưa thử trên Microsoft thật)

- `chuyen_forms_sang_phan_mem.py --fa-daa --so-nhap-clb SO_NHAP_CLB.xlsx (--dang-ky FORMS... | --lists LIST.csv) [bài thi...]`: Loại CLB, chỉ tiêu, điểm sàn, giữ chỗ lấy từ Sổ nhập CLB của FA-M1; đường B đọc biểu mẫu FA-M2 và nối `dat_huy_chuong_duong_b` (không đổi hành vi, 19 test cũ xanh); đường A (`doc_lists(fa=True)`) bỏ dòng DRAFT (trừ `--nhan-ban-nhap`), lấy lần lưu cuối, điền huy chương mặc định khi ô trống và HC_TuChinh không đặt; bỏ nguyện vọng trùng và báo; điểm thi quy về nguyên 0-10 (D7, tính bằng phân số); em xếp CLB Tuyển chọn mà chưa thi -> cảnh báo NOT_ATTEMPTED; làm bài dưới 1/3 trung vị -> cờ (D9, chỉ báo); soát huy chương bằng `fa_daa.kiem_ho_so_huy_chuong`; không soát hai quỹ 100 điểm cũ.
- Không cờ: `doc_lists`, `phan_tich_chi_thi`, `ghi_tep_phan_mem` giữ hành vi cũ (nội dung ô SO_NHAP_CLB.xlsx và BANG_DIEM.xlsx của một lần chạy mặc định giống hệt trước thay đổi).
- Test mới: `tests/test_fa_m3_chuyen.py` (25 ca). Chưa thử trên Forms/Lists thật (TH).

## 2026-11-09 — FA-M2: Biểu mẫu đăng ký đường B (--fa-daa) (đêm 2, TH = chưa thử trên Microsoft thật)

- `bieu_mau.cac_phan_fa`, `tao_mau_forms.py --fa-daa`: mỗi ngày một biểu mẫu đăng ký (không câu Ranking; `[<buổi>-nv1..3]` bắt buộc, `[<buổi>-vang]` và `[<buổi>-doi]` tuỳ chọn, có đáp án \"giữ mặc định\" vì Forms không bỏ chọn được), `NHAP_FORMS_DANG_KY_<buổi>.docx` và `CAI_DAT_FORMS_DANG_KY.md` (một dòng mô tả V§5.1, cài đặt, giới hạn đường B). Không nói đường nào được khuyên dùng (D8 còn mở).
- Không cờ: `--chi-thi` và `--moi-clb` sinh ra tệp giống hệt từng byte so với trước thay đổi (so bằng `diff -r`). `ghi_docx_chi_thi` thêm hai tham số tuỳ chọn.
- Test mới: `tests/test_fa_m2_forms_dang_ky.py` (10 ca).

## 2026-11-09 — FA-M1: Phiếu thiết lập CLB trên Forms và bộ chuyển đổi (đêm 2, TH = chưa thử trên Microsoft thật)

- `mau_forms_thi_clb/chuyen_phieu_clb.py`: Excel xuất từ Phiếu thiết lập CLB -> `SO_NHAP_CLB.xlsx` (cột Loại, Điểm sàn, Tối thiểu, Sức chứa phòng, sheet Giữ chỗ) + `BAO_CAO_PHIEU_CLB.md`; phân loại V§4.1, nộp nhiều lần lấy phiếu cuối, CLB chưa nộp phiếu -> Giới hạn với chỉ tiêu kỳ trước (`--ky-truoc`), kiểm trước bằng `fa_daa.kiem_truoc_fa`.
- `PHIEU_THIET_LAP_CLB.md`: hướng dẫn dựng Forms bằng tay (Forms không có API tạo biểu mẫu).
- Test mới: `tests/test_fa_m1_phieu_clb.py` (17 ca). Không đổi mã kiosk, lược đồ hay CSV.

## 2026-11-09 — FA-SOAT: Opus soát đêm 1 (mục cha A13)

- `tests/test_van_phong_tu_nhien.py`: thêm `DAA` vào `VIET_TAT` (tên chế độ FA-DAA là chữ viết tắt, như `DA`, `RB`). Bốn thông báo lỗi mới của đêm 1 (`fa_cot_bo_qua`, `fa_giu_cho_bo_qua`, `fa_chua_bat`, `fa_chua_co_ly_do`) làm test này đỏ; đêm 1 không chạy lại nó sau khi thêm mã lỗi.
- Báo cáo soát: `docs/phien/bao_cao_dem/2026-11-09_soat_dem1.md`. Không có test mới.

## 2026-11-09 — FA-4 đến FA-8: chạy FA-DAA, đóng CLB thiếu người, lý do, bảng nhu cầu, tính chất V§13 (mục cha A13, A5, A6, C3, Z6)

(Bốn mục dùng chung `fa_daa.py`, `api.py`, `i18n_errors.py` nên đi cùng một commit.)

- **FA-4** `fa_daa.chay_fa_daa`: CLB Tự do không giới hạn trong bộ nhớ; lọc Tuyển chọn theo điểm sàn (`NOT_ATTEMPTED` / `BELOW_PASS`); bỏ điểm thi ở CLB Giới hạn; giữ chỗ bằng suất dự trữ mềm; phương án dự phòng (CLB Tự do ít người nhất, theo thứ tự STB của buổi); chia nhóm phòng (`fa_nhom`, chỉ thêm). Lõi `run_rbda_nhieu_buoi` không đổi; `api.py` gọi lớp bọc khi FA bật và chạy hai chốt (sanity, ổn định) trên đầu vào đã chuẩn bị, không ghi danh sách tăng cường vào `preferences`.
- **FA-5** đóng CLB thiếu người: mỗi vòng một CLB (thiếu nhiều nhất trước; hoà: ít người hơn, rồi mã), chạy lại cùng STB; `dong_cua`, `CLUB_CLOSED`, cảnh báo `fa_clb_dong_thieu_nguoi` (nói rõ là xấp xỉ).
- **FA-6** `ly_do_ket_qua` (RESERVED / SCORE / MEDAL / LOTTERY / BELOW_PASS / NOT_ATTEMPTED / CLUB_CLOSED, điểm chuẩn, danh sách chờ theo D4, lỗi ổn định thì ném ValueError); bảng `fa_ly_do` (chỉ thêm); `fa_ly_do.py` (mẫu câu V§9.1, không có mã học sinh khác, không hứa ưu tiên bù); `export_ly_do_csv` → `ket_qua_ly_do.csv`.
- **FA-7** `bang_nhu_cau`, `export_bang_nhu_cau` (không có mã hay tên học sinh), `kiem_chi_tang` và `mau_forms_thi_clb/so_sanh_suc_chua.py` (từ chối giảm chỉ tiêu và đổi loại).
- **FA-8** `tests/test_fa_tinh_chat.py`: 200 bộ nhỏ ngẫu nhiên cho V§13.1-13.9, 13.11 (13.12 bỏ qua có lý do: D1 hoãn).
- Tệp mới: `fa_ly_do.py`, `mau_forms_thi_clb/so_sanh_suc_chua.py`. Bảng mới `fa_nhom`, `fa_ly_do` (CREATE TABLE IF NOT EXISTS, không đổi bảng cũ). Test mới: `tests/test_fa_chay.py`, `test_fa_toi_thieu.py`, `test_fa_ly_do.py`, `test_fa_nhu_cau.py`, `test_fa_tinh_chat.py`. `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 210 tệp test, hàng mới cho `fa_daa.py` / `fa_ly_do.py`.

## 2026-11-09 — FA-3: huy chương một quỹ (mục cha A13)

- `fa_daa.py`: `kiem_ho_so_huy_chuong` (giá trị 60 / 30 / 10 đúng kiểu số nguyên, mỗi giá trị một lần mỗi buổi, mỗi CLB một huy chương, CLB trong nguyện vọng và không phải Tự do; ít hơn 3 huy chương hợp lệ), `diem_huy_chuong_hieu_luc` (một quỹ, bỏ qua `tier`, không đọc thứ hạng nguyện vọng).
- `api_quan_ly.py`: `submit_huy_chuong(student_id, huy_chuong)` (kiểm ở server, thay toàn bộ huy chương cũ của em, ghi `wharton_bids` + `wharton_nhat_ky`, tôn trọng khoá điểm). `api.py`: khi FA bật, hồ sơ huy chương được kiểm thay hồ sơ 100 điểm (chặn chạy, báo cáo sức khoẻ) và huy chương làm `diem_wharton` của lần chạy.
- `i18n_errors.py` (+ `i18n_loi.js`): 5 mã mới. `tests/test_fa_huy_chuong.py` (mới, 20 ca); `tests/test_ws_nhan.py`; `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 205 tệp test.

## 2026-11-09 — FA-2: kiểm trước khi chạy FA-DAA (mục cha A5)

- `fa_daa.py`: `kiem_truoc_fa` (mỗi buổi có CLB Tự do; mọi CLB có loại; Giới hạn / Tuyển chọn có chỉ tiêu; Tuyển chọn có điểm sàn; giữ chỗ không vượt chỉ tiêu; giữ chỗ cho học sinh lạ / em không xếp CLB đó chỉ là cảnh báo và không được tính), `giu_cho_hop_le`, `chi_loi_chan`, `doc_du_lieu_fa`, `kiem_fa_tu_csdl`.
- `api.py`: bước kiểm dữ liệu của `_run_pipeline_da_khoa` và `get_data_health_report` gọi kiểm FA khi `fa_daa` bật (lỗi chặn dừng trước khi bốc hay khoá số, không ghi gì); hồ sơ 100 điểm của Wharton không áp khi FA bật.
- `so_nhap.py`: kiểu CLB và `kiem_thuoc_tinh` chuyển vào đây (skill đóng gói của so_nhap chạy một mình); `fa_daa.py` nhập lại.
- `i18n_errors.py` (+ `i18n_loi.js`): 7 mã `fa_*` mới. `tests/test_fa_kiem_truoc.py` (mới, 15 ca); `tests/test_ws_nhan.py`: thêm mã vào danh sách mã mới; `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 204 tệp test.

## 2026-11-09 — FA-1: mô hình dữ liệu FA-DAA (mục cha A13)

- Luật `rules.fa_daa` (mặc định TẮT; bật cần `wharton`): `cau_hinh_ws.py`, `rbda_priority_pipeline.py` (`dung_fa_daa`, khoá bỏ khỏi `run_history.luat_xep` và dấu vân tay khi tắt; khi bật, dấu vân tay gồm kiểu CLB + giữ chỗ).
- `clubs` thêm bốn cột `loai`, `diem_san`, `so_toi_thieu`, `suc_chua_phong` (`di_tru_schema` idempotent, sao lưu trước); bảng mới `giu_cho(club_id, student_id)`; xoá CLB / học sinh / dữ liệu dọn cả `giu_cho`.
- Sổ nhập: cột CLB tuỳ chọn Loại / Điểm sàn / Tối thiểu / Sức chứa phòng và sheet tuỳ chọn "Giữ chỗ" (đọc, ghi, nạp); CSV CLB nhận bốn cột cùng tên khoá. Không có cột thì giống từng byte như cũ; FA tắt thì bỏ qua kèm cảnh báo `fa_cot_bo_qua` / `fa_giu_cho_bo_qua`. Mã lỗi mới trong `i18n_errors.py` (đã chạy `tao_i18n_js.py`).
- Module mới `fa_daa.py` (kiểu CLB, `kiem_thuoc_tinh`, ghi thuộc tính, `thay_giu_cho`).
- `tests/test_fa_du_lieu.py` (mới, viết trước); `tests/test_rang_buoc_csdl.py`: hàm trợ giúp `_ha_cap` chọn đúng cột của lược đồ cũ (bảng `clubs` nay có thêm cột). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 203 tệp test.

## 2026-11-08 — FA-KH: báo cáo đêm tự đẩy lên GitHub

- `docs/phien/CHAY_DEM_FA_DAA.md` mục E: phiên chạy đêm ghi `docs/phien/bao_cao_dem/<ngày>.md` (tiếng Việt, dễ hiểu), commit, push, kiểm push đã tới GitHub, in link. Không đổi mã.

## 2026-11-08 — FA-M3 (một phần, Truong duyệt): đặt huy chương trên đường B, đủ 6 cách đặt

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: hàm mới `dat_huy_chuong_duong_b` (mặc định theo thứ tự nguyện vọng, câu tuỳ chọn đặt vàng, câu tuỳ chọn đổi bạc/đồng; giá trị không dùng được thì giữ mặc định và báo). Chưa nối vào luồng chuyển (việc của FA-M3, đêm 2); đầu ra hiện có không đổi.
- `tests/test_fa_m3_huy_chuong_b.py` (19 ca, viết trước, đỏ rồi xanh; đột biến tắt bước đổi bạc/đồng làm 8 ca đỏ).
- `CLAUDE.md`: ghi chú ngoại lệ bất biến 2 nay đạt trọn điều kiện "mọi học sinh đổi được". `docs/ke_hoach/FA_DAA_KE_HOACH.md` D12, FA-M2, FA-M3; `docs/ke_hoach/CLAUDE_CHI_TIET.md` 202 tệp test.

## 2026-11-08 — FA-KH (quyết định của Truong): ngoại lệ bất biến 2 cho huy chương mặc định, D11 không chặn

- `CLAUDE.md`: ghi ngoại lệ bất biến 2 (huy chương mặc định theo thứ tự nguyện vọng, chỉ ở tầng đăng ký và chỉ khi học sinh đổi được; lý do: tín hiệu riêng kiểu CADA giữ khai thật thứ tự).
- `docs/ke_hoach/FA_DAA_KE_HOACH.md`: D2 (ngoại lệ), D11 (ngưỡng theo cỡ mẫu, tự điều chỉnh theo chênh lệch trung bình, admin xác nhận, không chặn), D12 (đường B thêm câu tuỳ chọn đặt huy chương vàng), FA-UI, FA-M2, FA-M3, FA-M4.
- `docs/phien/claude__keen-ride-72sa7t.md`: quyết định mới. Không đổi mã; D1 vẫn hoãn.

## 2026-11-08 — FA-KH (sửa sau soát hội đồng): D1, D3, D4, D5, D9, D11, D12, FA-9

- `docs/ke_hoach/FA_DAA_KE_HOACH.md`: D1 sửa lý do (không phá ổn định; vấn đề là động cơ giữa các kỳ, cần mô phỏng trước kỳ 2); D3 đóng CLB thiếu nhiều nhất trước; D4 danh sách chờ Tuyển chọn điểm → huy chương → bốc thăm, Giới hạn huy chương → bốc thăm, chỉ em xếp CLB đó cao hơn; D5 không làm hạt giống công khai, FA-9 thành biên bản bốc thăm có giáo viên chứng kiến; D9 bật giới hạn thời gian Forms, cờ < 1/3 trung vị; D11 so điểm trung bình giữa các bản đề; D12 đường B không dùng câu Ranking, 3 câu chọn NV1–3, huy chương gán theo thứ tự.
- `docs/phien/claude__keen-ride-72sa7t.md`, `docs/phien/CHAY_DEM_FA_DAA.md`: cập nhật theo các quyết định trên. Không đổi mã.

## 2026-11-08 — FA-KH: kế hoạch triển khai FA-DAA và tệp chạy đêm (chỉ tài liệu)

- `docs/ke_hoach/FA_DAA_VISION.md`: vision của Truong (chép nguyên văn).
- `docs/ke_hoach/FA_DAA_KE_HOACH.md`: kế hoạch theo mục FA-0..FA-10, FA-UI, FA-M1..M6; mục cha A13, A5, A6, C3, Z6, A2, T4M-NC; quyết định D1..D10 (D1 ưu tiên bù CHẶN vì bất biến 2).
- `docs/phien/CHAY_DEM_FA_DAA.md`: tệp duy nhất cho phiên chạy đêm; `docs/phien/claude__keen-ride-72sa7t.md`: bàn giao nhánh.
- Không đổi mã, schema, hợp đồng CSV; không test mới.

## 2026-11-06 — T4M-NC: sửa CI đỏ của PR #13 (3 nguyên nhân do nhánh)

- `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that`: `docs/ke_hoach/CLAUDE_CHI_TIET.md` bản đồ mã ghi 194 tệp test, thực tế 201; cập nhật 201 tệp, 3.645 ca.
- `tests/test_a13_13_kiem_nhan.py::test_F1_script_do_tat_wharton_ro_rang`: `du_lieu_test/demo_t4m.py` (từ T4M-Q5c) ghi `{"wharton": bool(day_du)}`; nay ghi tường minh `{"wharton": False}` / `{"wharton": True}`. Hành vi không đổi.
- `tests/test_t4m_bo_dung_bk34.py` (Windows CI không cài `python-docx`): `pytest.importorskip("docx")` như các test Forms khác; tái hiện bằng cách giả lập thiếu `docx` (25 đỏ/lỗi trước, bỏ qua sau).
- Không sửa: `tests/test_giao_dien_t3_l3.py::test_tai_bang_theo_clb_va_theo_ma_co_tim` đỏ một lần trên Linux CI (màn 2 dòng, tệp 3 dòng), xanh ở lần chạy CI kia và 6/6 lần ở máy: chập chờn, test của `main` (T3-L4), tách thành việc riêng.

## 2026-11-06 — T4M-BK3, BK4 (vòng 5, bước K2): bảng flow `DaLam_<ClubId>` và lệnh gộp `tao_bo_dung_t4m.py`

Không đổi lõi, schema, hợp đồng CSV, không thư viện mới (chỉ thư viện chuẩn); không sửa bộ sinh hay đặc tả cũ. Mọi đầu ra nhãn TH (chưa chạy trên Power Apps / SharePoint / Power Automate).
- Mới `mau_forms_thi_clb/bo_dung_t4m/bang_flow.py` (BK3): một hàng mỗi CLB CÓ đề (`bieu_mau.clb_co_thi`): `Flow` = `DaLam_<ClubId>`, `ClubId`, ô trống cho IT (`FormId`, `ChuBieuMau`, `DaThuNgay`), tệp Quick Import; `BANG_FLOW.md` (bảng + biểu thức dán `toLower(responder)`, hằng `ClubId`, OData `ResponseId eq '…'`, nhãn GĐ) và `BANG_FLOW.csv`. Không gói flow `.zip` (quyết định 3).
- Mới `mau_forms_thi_clb/bo_dung_t4m/huong_dan_it.py` (BK4): sinh `HUONG_DAN_IT.md`: bước 0 (HỎI-IT) đến bước 6 (vòng thử), mỗi bước có dòng `☐ Pass ☐ Fail` trỏ về R1..R38 và HDT §9; ba cách A/B/C với quyền và nhãn ĐXM/TT-CXM từ KQ §8.1; site script 46 hành động nên chỉ áp không đồng bộ (Settings > Apply a site template, hoặc `Add-SPOSiteDesignTask`), cấm `Invoke-SPOSiteDesign`; phụ lục R1..R38.
- Mới `mau_forms_thi_clb/tao_bo_dung_t4m.py` (BK4): `--de-thi`, `--ra`, `--zip`; ra `01_lists/` và `02_app/` (gọi `sinh_bk1.ghi_tat_ca` của K1), `03_flow/`, `04_forms/` (gọi `tao_mau_forms.sinh_moi_clb` như hàm), `HUONG_DAN_IT.md`; `<ra>.zip` nằm ngoài thư mục, tên sắp xếp, giờ cố định, sinh lại cho cùng từng byte. Kiểm đề trước khi ghi.
- Test mới `tests/test_t4m_bo_dung_bk34.py` (+25): số flow = số CLB có đề, mọi `ClubId` có trong `CLB.csv`, đủ R1..R38 (đọc từ đặc tả), dòng HDT có thật, `Invoke-SPOSiteDesign` chỉ để cấm, sinh lại giống từng byte kể cả zip (và sinh đè lên thư mục cũ), `04_forms` trùng khít đầu ra của `sinh_moi_clb`, không tên thật/tenantId/URL. Mutation check bắt 3 đột biến (flow cho mọi CLB, bỏ chữ cấm Invoke-SPOSiteDesign, đảo thứ tự zip); một đột biến sống sót lần đầu (kiểm "không" cùng dòng quá lỏng) nên đã siết test.
- `demo_t4m.py` mặc định, `--moi-clb`, `--day-du`: đầu ra trùng khít trước/sau (42, 52, 42 tệp; docx/xlsx so bỏ core.xml). README (mục 0c) và `T4M_VAN_HANH_MOT_DOT.md` (phụ lục) mỗi nơi một đoạn ngắn.

## 2026-11-06 — T4M-BK1, BK2 (vòng 5, bước K1): bộ dựng list và công thức Power Fx cho IT

Không đổi lõi, schema, hợp đồng CSV, không thư viện mới (chỉ `json`, `csv`, `uuid`, `re`); không sửa bộ sinh hay đặc tả cũ. Mọi đầu ra nhãn TH (chưa chạy trên SharePoint / Power Apps).
- Mới `mau_forms_thi_clb/bo_dung_t4m/`: `cot_lists.py` (MỘT định nghĩa cột cho ECA 30 cột, CLB 4, BaiThi 4, NHAT_KY_DA_LAM 4; GUID cố định uuid5), `site_script.py` (createSPList + addSPField / addSPFieldXml cho Choice; in số hành động, cảnh báo > 30, lỗi > 300; hiện 46), `mau_csv.py` (CSV mẫu một dòng ví dụ giả + `KIEM_COT_ECA.md`), `cong_thuc.py` (bốn tệp Power Fx khai triển k = 1..7 và bộ soát `soat_loc_uy_quyen`), `sinh_bk1.py` (một lệnh: `python -m bo_dung_t4m.sinh_bk1 --ra <thư mục>`; ra `01_lists/`, `02_app/`, `README_BK1.md`).
- Test mới (viết trước, đỏ khi thiếu mô-đun; sau đó sửa 3 lỗi sinh do test cú pháp tĩnh bắt: thiếu `;` trong `OnVisible`, `If` lệch dòng, `OnChange` k=7 thừa `;`): `tests/test_t4m_bo_dung_bk1.py` (37 ca). Gây hỏng tạm 3 chỗ (bỏ `WP7` khỏi ECA; khai triển chỉ tới k=6; `Email <>` trong `Filter(ECA…)`): test đỏ cả 3 (3, 3, 1 ca), khôi phục thì xanh.
- PHÁT HIỆN (không sửa, theo luật): `tao_mau_forms.ghi_clb_csv` ghi `Buoi` là "Thứ Hai" còn cột `Thu` của ECA là "Thứ 2"; quyết định 1 của §9 nói "cùng chữ". Bộ dựng dùng ánh xạ `buoi_theo_thu(de)` nên công thức lọc `Filter(CLB, Buoi = "Thứ Hai")` đúng; xfail ghi lại lệch.
- Sửa sau soát Opus (cùng bước K1): `addSPField`/`addSPFieldXml` nay là hành động CON (`subactions`) của `createSPList` (mức trên cùng chỉ có `createSPList`), thêm `$schema`; số hành động đếm cả hành động con (vẫn 46; cảnh báo > 30, lỗi > 300); mọi `addSPField` có `id` = GUID cố định (chạy lại không thêm cột hai lần). Test site script viết lại để ĐỎ trên đầu ra phẳng cũ (4 ca đỏ), đột biến 'làm phẳng' và 'bỏ id' đều bị bắt. Xfail Buoi/Thu đổi thành test thường (ánh xạ: khoá = 5 lựa chọn Thu, giá trị = Buoi của CLB.csv). Nhãn: công thức tên `Nhan` trong App.Formulas thay cho `ClearCollect(colNhan…)` ở App.OnStart (GĐ cú pháp).

## 2026-11-06 — T4M-Q5a/b/c (vòng 4, bước D1): bộ chuyển đổi đọc THIk/WPk, dữ liệu giả, `demo_t4m.py --day-du`

Không đổi lõi (`run_rbda`, `compute_club_priority`, `club_choice_function`), schema hay hợp đồng CSV của kiosk. Cột List cố định theo `T4M_KE_HOACH_TU_DONG.md` §8: `NV1..NV7`, `THI1..THI7`, `WP1..WP7`. List KHÔNG có `THIk`/`WPk` thì `SO_NHAP_CLB.xlsx`, `BANG_DIEM.xlsx` và tệp Lists giả giống hệt từng byte so với trước (băm toàn bộ khối zip trừ `docProps/core.xml`; 3 seed × {một biểu mẫu, `--moi-clb`} + tệp Lists giả mặc định; chạy tay trước và sau khi sửa).
- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `doc_lists` nhận `THIk`/`WPk` (khoá "tick", "wp", "dong_buoi" chỉ khi có cột); Q5a: "thi" đi theo tick (tick + bài -> điểm; tick + vắng -> ô `thi`; bài không tick -> bỏ điểm, báo, BANG_DIEM ghi "chưa tick thi"; tick CLB không đề -> bỏ tick, báo; quá 5 tick/ngày -> giữ 5 đầu theo thứ tự NV, báo); Q5b: `diem_w` vào Sổ nhập (`luon_co_cot_w=True`), `_soat_hai_quy` chỉ BÁO quỹ không cộng đúng 100 (quỹ 1 = CLB đã tick, quỹ 2 = còn lại; quỹ một CLB để trống không báo), ô không phải số nguyên >= 0 -> báo, để trống; ghi chú cuối lệnh nói "giữ BẬT" khi có điểm quyết tâm. Hàm mới: `tap_thi`, `_doc_tick`, `_doc_diem_quyet_tam`.
- `du_lieu_test/sinh_xuat_lists_gia.py`: `sinh`/`ghi_csv` thêm `so_nv`, `co_tick`, `co_wp`, `clb_co_de` (bộ ngẫu nhiên riêng cho tick/điểm, nên NV không đổi); `cot_csv`, `ghi_dong`, `gai_quy_khong_du`; cờ `--so-nv --tick --wp`.
- `mau_forms_thi_clb/tao_mau_forms.py`: `ghi_mau_xuat_chi_thi` khi List có tick thì chỉ nộp bài cho CLB đã tick và gài thêm `tick_vang`, `nop_khong_tick`.
- `du_lieu_test/demo_t4m.py`: `--day-du` (kết hợp `--moi-clb`): bật `rules.wharton` trong CSDL tạm, gài một quỹ thiếu 100 -> kiosk CHẶN lần chạy đầu -> demo sửa bằng `admin_save_wharton` rồi chạy lại; tóm tắt LUÔN in "Điểm quyết tâm: BẬT/TẮT"; khoá `diem_quyet_tam`, `bi_chan_lan_dau`, `so_nv`.
- Test mới (viết trước; chạy lần đầu 29 ca đỏ, nay đủ 34 xanh): `tests/test_t4m_day_du.py` (34 ca). Gây hỏng tạm 5 chỗ (`!=100` -> `>100`, bỏ việc bỏ điểm khi không tick, bỏ trần 5, bỏ miễn trừ quỹ một CLB, bỏ ô `thi` theo tick): cả 5 bị bắt.
- Tài liệu: `mau_forms_thi_clb/README.md` (mục 0 và 0b), `T4M_VAN_HANH_MOT_DOT.md` (bước 2, 4, 5, phụ lục; bỏ "Top 3", `NV1..NV3`).

## 2026-11-06 — T4M-M6 (vòng 4, bước D2): app Top 7, tick chọn thi, điểm quyết tâm; chỉ tài liệu

Không có mã, test, schema hay hợp đồng CSV; không đụng lõi. Cột List cố định theo `T4M_KE_HOACH_TU_DONG.md` §8: `NV1..NV7`, `THI1..THI7`, `WP1..WP7`.
- `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md`: tối đa 7 nguyện vọng mỗi ngày (số ô = min(7, số CLB ngày)), tick "Thi" chỉ ở CLB có đề (tối đa 5 mỗi ngày), bước điểm quyết tâm (hai khung 100, bộ đếm "Đã dùng X / 100", chặn Gửi khi khung không rỗng khác 100), một `Patch` ghi 21 cột; R2 đến R6 sửa; R15 sửa (thẻ Thi tuyển = CLB đã tick); mục 11 thêm R25 đến R38 (pass/fail, trỏ HDT §9 dòng 14.x).
- `T4M_HUONG_DAN_THU.md`: bảng cột §1, §2 (mô hình dài tới 52.500 dòng, vượt trần 30.000), §5 (7 ô), §10, §12; §9 thêm dòng 14.1 đến 14.5; mục 14 mới. Bộ sinh giả mặc định vẫn NV1..NV3 (ghi rõ; tuỳ chọn tới NV7 chờ T4M-Q5c).
- `T4M_CONG_THI.md` §1, §2, §4.5; `T4M_MICROSOFT.md` (tóm tắt, sơ đồ, ma trận, bảng cột kho, P3, §8 thêm hàng T4M-M6); `T4M_PHIEU_PHONG_VAN.md`: ECA-6 (tối đa 7, số CLB mỗi buổi), ECA-9 (tick tối đa 5), ECA-12 mới (điểm quyết tâm, màn điện thoại), IT-19 mới.
- Không còn chữ "Top 3" lỗi thời trong năm tệp được giao (kiểm bằng grep). Mọi thứ nhãn TH, không có số đo.

## 2026-11-06 — T4M-DEMO-B: `demo_t4m.py --moi-clb` (cách B) và câu hỏi cổng thi cho GĐ2

Không đổi lõi, schema, hợp đồng CSV, bộ chuyển đổi hay bộ sinh mẫu; chế độ mặc định của demo không đổi (test cũ không sửa).
- `du_lieu_test/demo_t4m.py`: `--moi-clb` / `chay_demo(moi_clb=True)`; `tach_moi_clb` tách tệp Forms giả chung thành một tệp xuất mỗi CLB có đề (không câu cổng, cột Points là số); `ghi_bai_thi_gia` sinh `BaiThi.csv` giả, cố ý thiếu một bài của em chỉ nộp một lần; bộ chuyển đổi chạy với `--bai-thi`; tóm tắt in mục đối chiếu.
- Test mới (viết trước, 4 đỏ -> xanh): 5 ca trong `tests/test_demo_t4m.py` (nay 16): kết quả xếp trùng với bản một biểu mẫu chung cùng seed, đúng một tệp mỗi CLB không câu cổng, đối chiếu bắt đúng chỗ gài, mặc định không có tệp mới, lệnh in đối chiếu. Gây hỏng tạm 2 chỗ: cả hai bị bắt.
- `docs/he_sinh_thai/T4M_PHIEU_PHONG_VAN.md`: sửa ECA-9 theo cách B; thêm mục B3 với IT-15 (sửa app hay trang SharePoint dự phòng), IT-16 (chủ biểu mẫu, trần 400), IT-17 (tài khoản dịch vụ, hạn mức flow, số ngày mở), IT-18 (quyền chỉ đọc `BaiThi`, DLP).
- README mục 0b, `T4M_VAN_HANH_MOT_DOT.md` phụ lục: lệnh `--moi-clb`.

## 2026-11-06 — T4M-NC vòng 3: soát C1 (T4M-Q4a/b/c) và C2 (T4M-M5)

Soát theo plan §7 "Nhận khi": 134 test liên quan đạt, ruff sạch, `kiem_nhanh` 7/7 (15 ca trùng khít với main); đầu ra mặc định và `--chi-thi` của `tao_mau_forms.py` trùng khít trước/sau C1 (bỏ qua `docProps/core.xml`). Không đổi mã sản phẩm.
- Gây hỏng tạm 4 chỗ trong `chuyen_forms_sang_phan_mem.py`: 3 bị bắt; `_da_thi` `any` -> `all` sống sót. Thêm `test_q4b_phieu_bo_trong_vai_cau_van_tinh_la_da_thi` (`tests/test_t4m_cong_thi.py`, nay 25): phiếu làm dở vẫn có điểm.
- M5: số dòng HDT §9 đề xuất "7.x" trùng với dòng 7.1/7.2 (flow xuất CSV) đã có. Thêm mục 13 vào `T4M_HUONG_DAN_THU.md` và dòng 13.1 đến 13.4 ở §9; cột "HDT §9" của R15 đến R24 trong `T4M_DAC_TA_SUA_APP.md` và hai chỗ trong `T4M_FLOW_DA_LAM.md` trỏ về 13.x.

## 2026-11-06 — T4M-M5 (vòng 3, bước C2): màn "Thi tuyển" và flow "Đã làm", chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md` thêm mục 10 "Màn Thi tuyển" (CLB có thi mà em đã chọn, `Launch(FormUrl)` chỉ khi chưa có dòng `BaiThi` và còn hạn, "Đã làm"/"Chưa làm", nút Làm mới, lọc `=` uỷ quyền được, không hiện điểm: mức 5a) và bảng yêu cầu R15 đến R24 mỗi dòng một kiểm pass/fail. `docs/he_sinh_thai/T4M_FLOW_DA_LAM.md` (mới, 85 dòng): flow mẫu mỗi biểu mẫu một flow (When a new response is submitted → Get response details → [kiểm trùng] → Create item `BaiThi`), chủ là tài khoản dịch vụ IT, cách nhân flow và Form Id biểu mẫu nhóm, ước tính 9.000 đến 12.000 hành động so với 6.000 mỗi ngày (nhãn ƯL), xử lý lỗi, đường thủ công với `--bai-thi`. Chỉ connector chuẩn; mọi bước TH/GĐ. Không đụng `T4M_VAN_HANH_MOT_DOT.md` và `mau_forms_thi_clb/README.md` (C1 sửa). Không test mới.

## 2026-11-06 — T4M-Q4a, Q4b, Q4c: cổng thi, mỗi CLB một biểu mẫu (vòng 3, bước C1)

Không đổi lõi, schema, hợp đồng CSV. Mặc định và `--chi-thi` giữ nguyên (bất biến 1): test cũ không sửa.
- **Q4a** `bieu_mau.cac_phan_moi_clb`; `tao_mau_forms.py --moi-clb [--ra]`: `sinh_moi_clb`, `ghi_docx_moi_clb`, `ghi_clb_csv`, `ghi_cai_dat_moi_clb`. Mỗi CLB có đề một `NHAP_FORMS_MOI_CLB_<club_id>.docx` (không câu cổng, thẻ `[clb_x-k]` giữ nguyên), `CLB.csv` (ClubId, Ten, Buoi, FormUrl trống; mọi CLB), `CAI_DAT_FORMS_MOI_CLB.md`. Sinh lại giống hệt từng byte; kiểm đề trước khi ghi; tệp cũ của CLB hết đề bị xoá; không chung chế độ với `--chi-thi`.
- **Q4b** `chuyen_forms_sang_phan_mem._cot_chi_thi/_cot_mot_clb/_da_thi`: tệp xuất không câu cổng phải chứa đủ câu của đúng MỘT CLB; trộn CLB, thẻ lạ, thiếu câu thì dừng không ghi gì; phiếu có ít nhất một câu trả lời = đã thi. Tệp có câu cổng chạy như cũ. N tệp một-CLB cho cùng `SO_NHAP_CLB.xlsx` như một biểu mẫu chung.
- **Q4c** `--bai-thi BaiThi.csv` (`doc_bai_thi`, `bai_trong_tep_xuat`, `doi_chieu_bai_thi`): báo bài lệch hai phía, sheet *Đối chiếu BaiThi* chỉ khi có cờ; không đổi điểm; không cờ thì `BANG_DIEM.xlsx` như cũ.
- Test mới (viết trước): `tests/test_t4m_cong_thi.py` (24). Liên quan: test_t4m_chi_thi, test_demo_t4m, test_mau_forms_thi_clb, test_doi_chieu_lists, test_do_t4m_thi: 126 pass; ruff sạch.
- Tài liệu: `mau_forms_thi_clb/README.md` mục 0a; `T4M_VAN_HANH_MOT_DOT.md` bước 1, 4, 5. `demo_t4m.py --moi-clb` chưa làm (không rẻ: demo dựng một tệp chung).

## 2026-11-06 — T4M-NC: thiết kế cổng thi (chọn CLB → mở bài thi → trạng thái → điểm)

Chỉ tài liệu. `docs/he_sinh_thai/T4M_CONG_THI.md` (mới): app Power Apps ECA làm cổng, mỗi CLB có thi một biểu mẫu Forms Quiz, list `CLB` (FormUrl) và `BaiThi` (trạng thái), mỗi biểu mẫu một flow "Đã làm" (connector chuẩn); connector Forms không trả điểm (TT-CXM) nên điểm chính thức vẫn do bộ chuyển đổi chấm lại; ba mức trả điểm 5a/5b/5c; mã đề xuất Q4a–c, M5; phương án lui trang SharePoint.

## 2026-11-06 — T4M-M4 (bước R3): hướng dẫn flow gửi Excel theo lớp cho GVCN, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_FLOW_GUI_GVCN.md` (mới, 77 dòng): flow Power Automate tuỳ chọn, chỉ connector chuẩn (SharePoint, Outlook/Teams), chủ là tài khoản dịch vụ IT; lấy tệp `export_theo_lop` từ thư viện SharePoint, ghép với tệp ánh xạ lớp → email GVCN (nguồn HỎI-IT, NC-08; khoá ghép theo tên tệp đã làm sạch), gửi từng GVCN. Bảng giới hạn ĐXM của NC-12, NC-13, đoạn DLP (NC-14), xử lý lỗi và đường thủ công; không ghi ngược về list (NC-13). Bước chưa thử nhãn TH, công thức/hành động nhãn GĐ. Không đổi hợp đồng CSV, schema, bất biến hay mã sản phẩm; không test mới.

## 2026-11-06 — T4M-M1 (vòng 2, R1): đặc tả sửa app ECA sang Top 3 mỗi ngày, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md` (mới, ~113 dòng) cho người sửa app (IT): cột dữ liệu mô hình rộng (`NV1..NV3`, `TrangThai`), hành vi màn hình (không trùng, không ô trống chen giữa, ngày trống hợp lệ, nhãn hai ngôn ngữ, điện thoại), `Patch` + `IfError` kèm báo đúng ngày lỗi, khoá theo `TrangThai`, chỉ dùng phép lọc uỷ quyền được (NC-04), sao lưu / khôi phục phiên bản (NC-21), bảng 14 yêu cầu R1..R14 mỗi yêu cầu một dòng kiểm pass/fail ánh xạ HDT §9, mục gói chỉ giữ chỗ "chờ A8-GOI". Mọi công thức gắn nhãn GĐ. Không đụng app thật, không đổi mã, schema, hợp đồng CSV.
## 2026-11-06 — T4M-M3 (vòng 2, bước R2): đối chiếu hai lần xuất List

Thêm công cụ dòng lệnh, chỉ đọc; không đụng kiosk, lõi, schema hay hợp đồng CSV.
- `mau_forms_thi_clb/doi_chieu_lists.py` (mới): `OLD.csv NEW.csv [--co-so CS1] [--ra bao_cao.xlsx] [--de de_thi.json]`. Dùng lại `doc_lists` của bộ chuyển đổi (không viết lại cách đọc). Liệt kê em mới, em rút, dòng đổi nguyện vọng (theo email chữ thường + Thu, kể cả đổi thứ tự), đổi Lớp, đổi CoSo. Hai tệp giống nhau => báo cáo rỗng; hoa/thường của email và thứ tự dòng không phải thay đổi. Lỗi thiếu cột => mã thoát 1, không ghi tệp.
- `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` bước 8: thêm đoạn dùng công cụ trước khi chạy lại.
- Sửa sau soát của điều phối: bản đầu so sánh qua `doc_lists` nên ô có mã CLB không có trong `de_thi.json` bị bỏ trước khi so (báo "không thay đổi" sai). Nay so giá trị THÔ NV1..NVn (bỏ khoảng trắng, phân biệt hoa/thường); ô mã lạ chỉ được đếm (`n_clb_la`) và dòng đầu in `CẢNH BÁO: N ô ...`, không bao giờ in "Không có thay đổi" phía trên cảnh báo chưa đọc.
- Test mới (viết trước, 17 ca + 7 ca sau soát = 24): `tests/test_doi_chieu_lists.py` (kiem_nhan ở T4M_MICROSOFT.md §8: rỗng / đúng một mục mỗi loại / email hoa-thường / lọc cơ sở / kiosk không bị nạp).

## 2026-11-06 — T4M-NC: Truong duyệt vòng 2

Chỉ tài liệu. Quyết định của Truong: duyệt nguyên tắc D1–D5 của thiết kế gói (mã A8-GOI chờ giáo viên ECA trả lời Q1–Q3); duyệt T4M-M1, M3, M4 (M2 chờ tệp xuất mẫu thật); T4-K2 giữ tạm dừng (K2-b). `T4M_KE_HOACH_TU_DONG.md` §6: vòng 2 R1–R3 kèm prompt.

## 2026-11-06 — T4M-GD4-V0 (bước S3): nháp v0 kiến trúc Microsoft, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_MICROSOFT.md` (mới), ghi rõ "Bản nháp v0 — chưa có kết quả phỏng vấn (GĐ2)", chạy prompt P2 theo dự phòng A: đủ 9 mục (tóm tắt; kiến trúc ô A–H; ma trận §7 điền đủ; mô hình kho rộng + ánh xạ Sổ nhập + điểm kiểm khi `student_id` là email; pha gói tóm tắt và dẫn `T4M_GOI_THIET_KE.md`, D1–D5 ghi là CHỜ DUYỆT; luồng muộn/đổi/rút; rủi ro + lộ trình (ước lượng); mã mục đề xuất T4M-Q1b, T4M-M1..M4, A8-GOI-1..3 kèm `kiem_nhan`; phương án T4-K2 để Truong quyết) và §10 danh sách soát lại sau GĐ2. Điểm phụ thuộc trường mang nhãn HỎI-IT; chỗ đổi thiết kế có hai nhánh (SharePoint List / Dataverse). Dẫn `T4M_VAN_HANH_MOT_DOT.md` (S1) và các bảng của `T4M_DO_MO_PHONG.md` (S4), cả hai có sau `git pull --rebase`; không diễn giải số đo. Không đổi hợp đồng CSV, schema hay bất biến nào; không test mới.

## 2026-11-06 — T4M-DO (bước S4): đo mô phỏng có / không bài thi tuyển, chỉ bảng số

Thêm công cụ đo; không đụng mã sản phẩm, schema hay hợp đồng CSV. Mọi số liệu là MÔ PHỎNG; không có nhận xét.
- `du_lieu_test/do_t4m_thi.py` (mới): 3 bộ giả (120 / 500 / 1.500 học sinh, hạt giống sinh cố định) x 20 hạt giống STB x 2 điều kiện (A không điểm thi, danh sách dự tuyển giữ nguyên; B có điểm thi như `de_thi.json`). Dữ liệu dựng bằng đúng chuỗi T4M (Lists giả → Forms giả → `--chi-thi` → `import_so_nhap`), đọc MỘT lần; mỗi lần chạy gọi `generate_stb_lottery`, `run_rbda_nhieu_buoi` (tham số như `api.run_pipeline`) và `verify_stability_tuan`. Chỉ số: tỉ lệ nguyện vọng 1 / top-3, số em chưa có CLB (tổng và theo buổi), tỉ lệ suất Tầng 1 về nhóm điểm cao nhất, số cặp phá vỡ, thời gian. `--nhanh` (lưới nhỏ cho test; bắt buộc kèm `--ra`, `--tai-lieu`). Cả lưới đủ chạy ~30 giây.
- `docs/he_sinh_thai/T4M_DO_MO_PHONG.md` (sinh ra): phương pháp, tham số, bảng trung bình / nhỏ nhất / lớn nhất, nhãn MÔ PHỎNG ở mọi tiêu đề bảng, lệnh tái lập. `du_lieu_test/ket_qua_t4m/`: CSV từng lần chạy và theo buổi.
- Sửa sau soát: bảng 2 ghi 15 CLB có đề thi, đúng là 10 (chỉ sai số đếm; điều kiện B vốn đã Tầng 1 đúng 10 CLB có `de_thi`); bảng 3 trở đi không đổi trừ số giây. Thêm test canh điều này (10 ca).
- Test mới (viết trước): `tests/test_do_t4m_thi.py` (8 ca): điều kiện A và B trùng khít từng byte với `PipelineAPI.run_pipeline`; tất định; không cặp phá vỡ; nhãn MÔ PHỎNG và không có mục nhận xét. Thử gây hỏng: bỏ danh sách dự tuyển ở điều kiện A làm kết quả không còn phụ thuộc hạt giống — đã bị bắt.

## 2026-11-06 — T4M-Q1b-b (bổ sung của điều phối vào T4M-Q1b): `--co-so` cho `--chi-thi`

`chuyen_forms_sang_phan_mem.py`: tham số tuỳ chọn `co_so` (CLI `--co-so CS1`) ở `doc_lists`, `phan_tich_chi_thi`, `chuyen_chi_thi`: chỉ giữ dòng List có `CoSo` bằng giá trị (bỏ khoảng trắng, không phân biệt hoa thường); phiếu thi của em ngoài danh sách đã lọc báo "ở cơ sở khác hoặc không có trong danh sách"; thiếu cột `CoSo` hoặc không em nào khớp thì lỗi, không ghi tệp. Không truyền `--co-so`: kết quả và cảnh báo y như cũ. `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` bước 4-5 dùng `--co-so` thay cho tách tay. Test mới: `test_q1bb_*` (4) trong `tests/test_t4m_chi_thi.py`. Không đổi hợp đồng CSV, schema, lõi.

## 2026-11-06 — T4M-Q1b (trong T4M-Q1 đã duyệt): `--chi-thi` chép Lớp từ Lists vào Sổ nhập

`chuyen_forms_sang_phan_mem.py`: `doc_lists` đọc cột `Lop` (hoặc `Lớp`) của tệp xuất Lists, giữ ô không trống đầu tiên của mỗi em; `phan_tich_chi_thi` mang `lop` theo; `ghi_tep_phan_mem` truyền `class_id` và `co_lop=True` CHỈ khi có ít nhất một em có lớp (Lists không có cột Lop hoặc mọi ô trống thì Sổ nhập y như cũ, không cột Lớp). Chế độ mặc định (Forms có Ranking) không đổi. `du_lieu_test/demo_t4m.py`: bỏ workaround `_lop_theo_email` + `set_student_class`. Test mới trong `tests/test_t4m_chi_thi.py`: `test_q1b_*` (3); sửa kỳ vọng của `test_q1_khong_co_bai_thi_so_nhap_trung_khit_ban_khong_diem` vì dữ liệu Lists của test có lớp 9A1. Không đổi hợp đồng CSV, schema, lõi.

## 2026-11-06 — T4M-VH (bước S1): vận hành một đợt xếp CLB, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` (mới, 99 dòng): 8 bước cho IT của trường (dựng bài thi, mở/đóng, khoá, xuất, chuyển đổi, nạp kiosk, xuất theo lớp, em đến muộn/rút); mỗi bước có lệnh hoặc đường bấm, chỗ kiểm, cách xử lý lỗi, tệp cần giữ. Phần chưa thử gắn nhãn TH, phụ thuộc trường gắn HỎI-IT. Không đổi mã, schema, hợp đồng CSV. Test mới: không (tài liệu).

## 2026-11-06 — T4M-GOI-TK (bước S2): thiết kế gói nhiều buổi (tiếng Nhật), chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_GOI_THIET_KE.md` (mới): bộ điều phối hai pha đặt trên `run_rbda_nhieu_buoi` (pha 1 DA trên các gói như buổi giả `goi`, cấp độ là bộ lọc điều kiện ở dữ liệu vào, cam kết cả năm chỉ trừ chỉ tiêu; pha 2 từng ngày với ngày của gói bị khoá), so với hai phương án bị loại và một phương án V0 dự phòng; phân tích bất biến 1, 2, 3, 4, 5, 8 kèm phản ví dụ cặp phá vỡ toàn tuần và nhãn "bảo đảm trong từng pha, không bảo đảm ổn định toàn tuần khi có gói"; đề xuất đổi hợp đồng CSV / schema tương thích ngược (chờ Truong, quy tắc 7); ba mục con đề xuất A8-GOI-1..3 kèm `kiem_nhan`; 8 câu hỏi cho giáo viên ECA; 5 quyết định chờ duyệt. Test mới: không có.

## 2026-11-06 — T4M-NC: kế hoạch tự chạy (S1 đến S4)

Chỉ tài liệu. `docs/he_sinh_thai/T4M_KE_HOACH_TU_DONG.md` (mới): Truong duyệt 06/11/2026 bốn quyết định (gói tiếng Nhật chỉ thiết kế, nháp v0 GĐ4, tự chạy chuỗi, đo mô phỏng chỉ bảng số); chuỗi bước S1 T4M-VH, S2 T4M-GOI-TK, S3 T4M-GD4-V0, S4 T4M-DO kèm phụ thuộc, tiêu chí nhận, luật dừng, vòng điều phối và prompt từng bước.

## 2026-11-06 — T4M-DEMO (Truong duyệt 06/11/2026): chạy thử trọn chuỗi bằng một lệnh

Thêm công cụ; không đụng mã sản phẩm, schema hay hợp đồng CSV. Dữ liệu hoàn toàn MÔ PHỎNG.
- `mau_forms_thi_clb/tao_mau_forms.py`: `ghi_mau_xuat_chi_thi(de, duong, danh_sach, hat_giong)` dựng tệp Forms chỉ-thi giả khớp tệp Lists giả và `de_thi.json` (Email, cột câu, cột Points); cố ý gài email viết hoa, một phiếu nộp lần hai, một email lạ, một bài thi CLB không xếp nguyện vọng.
- `du_lieu_test/sinh_xuat_lists_gia.py`: `sinh`/`ghi_csv` nhận thêm `clb_theo_ngay` (mã CLB thật); bỏ trống thì từng byte như cũ.
- `du_lieu_test/demo_t4m.py` (mới): `python du_lieu_test/demo_t4m.py --ra <thư mục>` chạy Lists giả → Forms giả → `--chi-thi` → nạp Sổ nhập vào CSDL tạm (`import_so_nhap`) → `run_pipeline` → `export_theo_lop` → tóm tắt tiếng Việt. Tắt điểm quyết tâm (mặc định BẬT) trong CSDL tạm; gán lớp bằng `set_student_class` vì bộ chuyển đổi chưa chép cột lớp; nhân chỉ tiêu mẫu cho vừa số em (`--he-so-cho`, bản sao trong bộ nhớ).
- `mau_forms_thi_clb/README.md`: mục 0b "Chạy thử trọn chuỗi".
- Test mới (viết trước): `tests/test_demo_t4m.py` (11 ca): hình dạng tệp, xác định, cảnh báo mong đợi, đủ tệp ra, không tạo `.db` ngoài thư mục tạm. Thử gây hỏng 5 chỗ: bỏ email viết hoa sống sót ở lần đầu, đã siết test; 4 chỗ còn lại bị bắt.

## 2026-11-05 — T4M-Q1, T4M-Q2, T4M-Q3 (Truong duyệt 05/11/2026): chế độ "chỉ thi" của mẫu Microsoft Forms

Thêm chế độ mới; chế độ mặc định giữ nguyên (`CAI_DAT_FORMS.md` sinh lại giống hệt tệp trong kho, test cũ 25/25 đạt). Không đụng lõi thuật toán, backend, giao diện, hợp đồng CSV hay bất biến nào; `kiem_nhanh.py` 7/7 ĐẠT (gồm `trung_khit` 15 ca). Dữ liệu thử đều MÔ PHỎNG.
- **Q1** `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `--chi-thi --lists DANH_SACH.csv` (nhận nhiều tệp `.xlsx` khi biểu mẫu tách theo buổi). Hàm mới `doc_lists`, `phan_tich_chi_thi`, `chuyen_chi_thi`. Khoá là cột Email Forms (`lower().strip()`) ghép với cột Email của tệp xuất List (mô hình rộng, `Thu`, `NV1..NVn`, `HoTen`). Phiếu trùng giữ phiếu ĐẦU; email lạ báo và bỏ; thi CLB mà List không có nguyện vọng CLB đó thì bỏ điểm (vẫn có trong `BANG_DIEM.xlsx`) và báo; không có bài thi thì Sổ nhập chỉ có nguyện vọng, không điểm. Tách nhẹ hàm dùng chung `_doc_cot`, `_ap_tran_thi` (hành vi chế độ cũ không đổi).
- **Q2** `bieu_mau.py`: `cac_phan/re_nhanh(..., chi_thi, buoi)`, `dem_cau`, `chia_theo_buoi`, `TRAN_CAU_MOI_BIEU_MAU = 200`, `cau_cong_thi(..., chi_thi)`. `tao_mau_forms.py --chi-thi [--ra]`: bỏ Ranking và ô gõ mã HS/họ tên (Forms tự ghi Name + Email), settings "Record name" + "One response per person"; tách theo buổi khi tổng câu vượt 200; `.docx` giống hệt từng byte khi `de_thi.json` không đổi (giờ zip và thuộc tính tài liệu cố định). Sinh `CAI_DAT_FORMS_CHI_THI.md`, `NHAP_FORMS_CHI_THI.docx` (60 câu, một biểu mẫu cho `de_thi.json` hiện tại).
- **Q3** `mau_forms_thi_clb/GHI_CHU_GIAO_VIEN.md` (một trang): Quick Import, tick đáp án + điểm, Settings bắt buộc, giới hạn 200 câu / 400 biểu mẫu, Post scores không cần cho kiosk; khớp mục 7.1 của `T4M_KET_QUA_TAI_LIEU.md`. `README.md` của mẫu thêm mục 0.
- Test mới (viết trước): `tests/test_t4m_chi_thi.py` (27 ca). Thử gây hỏng 4 chỗ (bỏ hạ chữ thường email, bỏ giữ phiếu đầu, đổi ranh giới 200, bỏ dedupe List): ban đầu ranh giới 200 sống sót, đã thêm ca biên đúng 200 câu rồi đỏ đúng.
- Lệch nhỏ so với đặc tả cần Truong biết: bỏ cả ô gõ họ tên (không chỉ mã HS) vì Forms ghi Name tự động; tên cột List cố định (`Email`, `Thu`, `NV1..`, `HoTen`) và mã CLB trong List phải là `club_id` của `de_thi.json`.

## 2026-11-05 — T4M-NC P5: đường thu điểm thi trên Microsoft (NC-23, 24, 27)

Chỉ tài liệu. `T4M_KET_QUA_TAI_LIEU.md` mục 7 (mới): Forms Quiz (điểm, cài đặt, giới hạn 200 câu / 400 biểu mẫu, cột xuất Excel), connector Forms chỉ đọc và không có trong Power Apps, không có API được hỗ trợ để tạo biểu mẫu, Quick Import không mang đáp án; bài thi trong Power Apps và rủi ro lộ đáp án; phát hiện `mau_forms_thi_clb/` đã có sẵn đường Forms Quiz; bảng so sánh, khuyến nghị tạm V1 Forms Quiz; đặc tả ghép điểm NC-25; mã mục đề xuất T4M-Q1 đến Q3. `T4M_KE_HOACH_NGHIEN_CUU.md`: thêm NC-27. `T4M_PHIEU_PHONG_VAN.md`: thêm ECA-9 đến 11, IT-14.

## 2026-11-05 — T4M-NC GĐ3 (tài liệu): hướng dẫn thử môi trường Microsoft + bộ sinh tệp xuất Lists giả

`docs/he_sinh_thai/T4M_HUONG_DAN_THU.md` (mới): hai người đọc (Truong nếu có môi trường thử; bản một trang cho IT = dự phòng B); kho SharePoint List, mô hình RỘNG (một dòng mỗi em mỗi ngày, `NV1..NV3`), mô hình dài ghi là phương án bị loại kèm lý do; màn Top 3, màn gói tiếng Nhật, flow xuất CSV và flow gửi Excel theo lớp (không ghi từng dòng, NC-13); bảng pass/fail/lý do; mục Premium kèm phương án chuẩn; thời gian đều là ước lượng mô phỏng. `du_lieu_test/sinh_xuat_lists_gia.py` (mới): chỉ thư viện chuẩn, `random.Random(seed)`, mặc định 1.500 em × 5 ngày = 7.500 dòng, UTF-8 có BOM, email giả (có chữ hoa), có ngày trống và dòng gói tiếng Nhật. `tests/test_sinh_xuat_lists_gia.py` (mới, 7 test, viết trước): tái lập theo seed, số dòng, BOM, không trùng NV, cột khớp tài liệu, email, dòng đặc biệt. Không đổi mã sản phẩm, hợp đồng CSV hay bất biến nào. Dữ liệu hoàn toàn mô phỏng.

## 2026-11-05 — T4M-NC: quyết định thi tuyển theo RB-DA (Truong), thêm NC-23 đến NC-26 và prompt P5

Chỉ tài liệu. `T4M_KE_HOACH_NGHIEN_CUU.md`: dòng "Ưu tiên" mục 1 ghi quyết định 05/11/2026 (trường đổi quy trình theo RB-DA; CLB có thi dùng Tầng 1, bài thi do giáo viên ra, công cụ của dự án dựng giúp); hệ quả với bất biến 2 và 7; bốn câu mới NC-23 (Forms Quiz), NC-24 (tạo form bằng công cụ), NC-25 (ghép điểm vào `score_k`), NC-26 (luật công bằng của bài thi); prompt P5. Tệp bàn giao cập nhật.

## 2026-11-05 — T4M-NC chuẩn bị GĐ2: phiếu phỏng vấn in mang theo

Chỉ tài liệu. `docs/he_sinh_thai/T4M_PHIEU_PHONG_VAN.md` (mới): gộp mục 6 của kế hoạch với mục 4 và cột "Còn hỏi IT" của kết quả GĐ1; 5 câu CHẶN cho IT (NC-01, 02, 03, 08, 16), 8 câu IT khác, 8 câu cho giáo viên ECA, mỗi câu có bối cảnh một dòng và chỗ ghi trả lời; nhắc riêng tư; checklist sau buổi gặp (mốc C2, dự phòng A/B). Kế hoạch bàn giao: P3 sửa sang mô hình kho rộng (một dòng mỗi em mỗi buổi) và hai người đọc (Truong hoặc IT).

## 2026-11-05 — T4M-NC GĐ1 + P4: kết quả đọc tài liệu Microsoft / PowerSchool, hợp đồng nhập của kiosk

Chỉ tài liệu. `docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md` (mới): 16 câu NC loại tài liệu, nhãn ĐXM / TT-CXM / GĐ / HỎI-IT, nguồn và ngày đọc; P4 tóm tắt hợp đồng nhập (`api_nhap.py`, `so_nhap.py`); câu mới cho IT; ma trận quyết định điền trước. Phát hiện chính: Dataverse for Teams và Developer Plan ngừng tạo mới từ 15/11/2026; PowerSchool không có trong danh sách OneRoster của SDS; hồ sơ Low của Power Automate (6.000 yêu cầu/người/ngày) nên V1 không ghi kết quả về app từng dòng; Sổ nhập không biểu diễn được CLB nhiều buổi. `TIEN_DO.md`: T4-K2 tạm dừng (Truong quyết 05/11/2026).

## 2026-11-05 — Z-CLAUDE-GON (ngoài sổ, Truong yêu cầu 05/11/2026; Truong duyệt bản tiếng Anh)

Chỉ tài liệu. `CLAUDE.md` gọn lại (9.112 B → 5.512 B): viết tiếng Anh (vẫn yêu cầu trả lời Truong bằng tiếng Việt); quy tắc 3 và 5 trỏ về bất biến 1 và 8 thay vì lặp; giữ nguyên số quy tắc 1–11 (tệp khác trỏ theo số) và câu "Trước khi push: chạy skill `soat-ma`" (test kiểm). Đoạn "Kiểm verify nhanh" và ghi chú thời gian bộ test chuyển nguyên văn sang `docs/ke_hoach/CLAUDE_CHI_TIET.md`. Test liên quan: `tests/test_skill_soat_ma.py`, `tests/test_a13_12_tai_lieu.py`, `tests/test_hook_ban_giao.py` (61 đạt).

## 2026-11-05 — T4M-NC (ngoài sổ, Truong yêu cầu 05/11/2026): kế hoạch nghiên cứu hệ sinh thái Microsoft của trường

Chỉ tài liệu; không đổi mã, test, hợp đồng CSV hay bất biến nào.

- `docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md` (mới): hồ sơ hệ thống đăng ký ECA của trường (Power Apps, M365 A3/A5, PowerSchool; Truong trả lời, chưa kiểm với IT), gói tiếng Nhật nhiều buổi và hướng xếp hai pha, 22 câu nghiên cứu NC-01 đến NC-22, quy tắc bằng chứng (ĐXM / TT-CXM / GĐ / HỎI-IT / TH), lộ trình 5 giai đoạn kèm hai kế hoạch dự phòng, bộ câu hỏi phỏng vấn IT và giáo viên ECA, mẫu ma trận quyết định, bốn prompt P1 đến P4.
- `docs/phien/claude__upbeat-shannon-g5nnms.md` (mới): tệp bàn giao của nhánh.
- T4-K2 (Google) chưa được đánh dấu tạm dừng: chờ Truong quyết.
- Gọn prompt (cùng ngày): luật chung gom một chỗ (mục 8.0, C1 đến C4) thay vì lặp ở từng prompt; prompt viết tiếng Anh; mỗi prompt chỉ đọc đúng mục cần; mục 4 bỏ phần trùng `CLAUDE.md`; báo cáo cuối có trần độ dài. Nội dung yêu cầu giữ nguyên.

## 2026-11-05 — T3-L5 (ngoài sổ, Truong yêu cầu): Điểm chuẩn cùng nền các thẻ khác, thẻ 05 chỉ ghi "Quản lý"

- `style.css`: bỏ hai khối nền tối riêng của `#adminDiemChuanBlock` (`prefers-color-scheme: dark` và `[data-theme=dark]`); khối giờ dùng nền trắng như các thẻ khác.
- `i18n.js`, `index.html`: `nav_admin` = "Quản lý" / "Manage" (thanh bên). `admin_title` (tiêu đề trang) cũng đổi thành "Quản lý" / "Manage".
- Test: `tests/test_giao_dien_a13_10_diem_chuan.py` (thay test chế độ tối bằng test cùng nền), `tests/test_giao_dien_t3_l3.py`, `tests/du_lieu_ws/chu_ui_doi_co_y_t3.json` (thêm `nav_admin`).

## 2026-11-04 — T3-L4 (ngoài sổ, Truong duyệt 04/11/2026): thứ tự tệp "Tải bảng này", bỏ dòng nhắc chết, Điểm chuẩn gọn

- Chỉ hiển thị / xuất theo màn hình; không đổi CSV, schema hay kết quả xếp.
- `api_xuat.py::export_bang_dang_xem`: thêm tham số tuỳ chọn `thu_tu` (mã theo thứ tự đang hiện); hàng tệp đi theo thứ tự đó, mã lạ xếp cuối. Không truyền thì như cũ. `js/09_the_xem.js`: `kqThuTuMan()` gửi thứ tự sắp hiện tại của tiêu đề cột.
- Bỏ nhánh "Chưa có lớp nào" của Theo lớp (`veKqTheoLop`) và khoá `theolop_khong_co_lop` (vi, en) trong `i18n.js`.
- `style.css`: nút "Xem chi tiết" không xuống dòng; chú giải Điểm chuẩn thành hàng ngang có ô mẫu.
- Test: `tests/test_t3_l3_backend.py::test_xuat_theo_thu_tu_man_hinh_thu_tu`, `tests/test_giao_dien_t3_l3.py` (`test_tai_bang_theo_thu_tu_dang_sap_tren_man_hinh`, `test_diem_chuan_nut_mot_dong_va_chu_giai_gon_trong_css`); `test_giao_dien_a14_lop.py` bỏ test dòng nhắc chết, đếm khoá 25→24.

## 2026-11-04 — T3-L3 fix (điều phối): test "chưa có lớp" theo hành vi thật

- `tests/test_giao_dien_a14_lop.py::test_theo_lop_chua_co_lop_nao_hien_dong_nhac`: bỏ đoạn ép `kq.tang1 = 'lop'` (người dùng không tới được từ T3-16, và lần vẽ lại bất đồng bộ làm test chập chờn trên CI); nay kiểm nút "Theo lớp" ẩn, bảng có dòng, không có ngõ cụt "Chưa có lớp nào". Dòng nhắc trong `js/03_ket_qua.js` thành đường mã chết, ghi ở mục "Cần Truong" của PR #10.

## 2026-11-04 — T3-L2 fix3 (điều phối): test node chạy được trên Windows

- `tests/test_t3_l2_buoi.py::test_loi_co_tham_so_buoi_hien_nhan_khong_hien_ma`: `subprocess.run(["node", ...])` đọc đầu ra bằng `encoding="utf-8"` (CI Windows đọc cp1252 nên gặp chữ Việt thì `stdout` là `None`).

## 2026-11-04 — T3-L3 (ngoài sổ, Truong duyệt 04/11/2026): tên thẻ, thẻ Kết quả gọn, tải bảng, Điểm chuẩn một nơi, chữ Sổ nhập (nghiên cứu T3, lô 3)

Chỉ đổi hiển thị (thêm một API xuất đọc `match_results`); thuật toán, `match_results`, `run_history`, STB, hợp đồng cột CSV không đụng tới.

- **Tên thẻ:** 03 "Dữ liệu khác" thành "Chi tiết và xuất tệp" / "Details and export" (`nav_others`, `others_title`); 05 thành "Quản lý {slot_sl}" / "Manage {slot_pl}" (`nav_admin`, `admin_title`). Chữ báo lỗi nhắc tên thẻ 05 (`i18n_errors.py`) theo tên mới.
- **T3-16/17/18 (`js/09_the_xem.js`, `index.html`, `style.css`):** nút "Theo lớp" chỉ hiện khi đã có lớp (chưa có lớp thì mở sẵn "Theo mã học sinh"); bỏ hàng sắp xếp `#kqTang2` (và khoá `kq_sap_nhan`, `kq_sx_*`, `kq_aria_tang2`), sắp bằng cách bấm tiêu đề cột (`.kq-sx-cot`, `aria-sort`; mã tự nhiên, lớp tự nhiên, còn lại theo vần tiếng Việt, ô trống luôn cuối); bỏ cột "Thứ tự" (`th_stt`), giữ dòng đếm. `localStorage` `rbda_ket_qua_xem_v1` không còn `tang2`.
- **T3-19:** nút "Tải bảng này (Excel)" (`#btnKqTaiBang`) ở thẻ 02, API mới `export_bang_dang_xem(kieu, gia_tri, output_path)` (`api_xuat.py`): một tệp, một trang, đúng lớp / CLB / danh sách theo mã đang xem; không điểm, không số bốc thăm; không ghi đè; chưa có kết quả thì `xuat_chua_co_ket_qua`.
- **T3-22:** Điểm chuẩn chỉ còn ở thẻ 05, tab "Điểm chuẩn" (`#qlTabDc`); bỏ thẻ và nút `#dcKqPanel` / `#btnDcKqMo` ở thẻ 03 (cùng `veDiemChuanKetQua`, `dongDiemChuanKq`, `initDiemChuanKetQua`, khoá `dc_xem`, `dc_an`).
- **T3-31 (`js/05_quan_ly.js`):** Điểm chuẩn mặc định MỘT bảng bằng số (CLB, điểm thi chuẩn, điểm quyết tâm chuẩn, "N đơn · M chỗ") + nút "Xem chi tiết" từng CLB; biểu đồ chấm và bảng hai cách xét x hai mức chuyển vào chi tiết (đóng bằng "Đóng chi tiết"); bỏ thanh điểm, thanh xếp chồng ba màu, ba mức "Đủ chỗ / Đông / Rất đông", hộp chọn CLB và các khoá `dc_muc_*`, `dc_bar_*`, `dc_chu_giai_thanh`, `dc_muc_giai_thich`, `dc_thanh_nhan`, `dc_ti_le_nhan`, `dc_chon_clb`.
- **T3-27:** chữ giao diện = chữ Sổ nhập ở mọi nơi trong `i18n.js`, `index.html`, `i18n_errors.py`: Chỉ tiêu (thay "Tổng chỗ"), Suất ưu tiên (thay "Suất dự trữ"), Nhóm ưu tiên (thay "Nhãn dự trữ"); tiếng Anh Quota / Priority seats / Priority group. Chỉ chữ hiển thị; không đổi mã, cột CSV hay tiêu đề cột trong tệp Excel xuất (`api_xuat.py`).
- **T3-11 (`js/075_workspace.js`):** tạo workspace từ mẫu: bước 1 có nút "Tạo" ngay (2 cú bấm) và nút "Tuỳ chỉnh từ vựng và luật" (`#wzTuyChinh`, kiểm tên trước) mở bước 2 đến 4; thanh bước và bước "Xem lại" chỉ có khi tuỳ chỉnh; dòng "Thứ tự các nhóm" trống ẩn đi.
- **Test mới:** `tests/test_t3_l3_backend.py` (7), `tests/test_giao_dien_t3_l3.py` (Chromium). **Test cũ sửa:** `test_giao_dien_t2_ket_qua.py` (viết lại ca tầng 2, sắp theo tiêu đề cột, không lớp), `test_giao_dien_diem_chuan.py`, `test_giao_dien_a13_10_diem_chuan.py` (một bảng, chi tiết mở theo yêu cầu, thẻ 03 không còn Điểm chuẩn), `test_i18n_khoa_dc_khong_chet.py`, `test_ws_nhan.py` (+ `chu_ui_doi_co_y_t3.json`: bảng thay chữ T3-27), `test_giao_dien_danh_sach_clb.py`, và các test đi qua trình hướng dẫn (`test_ws_giao_dien.py`, `test_giao_dien_a13_12_ws.py`, `test_giao_dien_a13_13_kiem_nhan.py`, `test_giao_dien_a14_lop.py`, `test_giao_dien_t3_l1_ws.py`, `test_ws_wharton_giao_dien.py`: bước 2 mở bằng "Tuỳ chỉnh").
- **Sửa test sau CI (13 ca):** `test_giao_dien_a14_lop.py` (bỏ cột "Thứ tự", tiêu đề cột kèm ▲, 25 khoá i18n, dòng nhắc "chưa có lớp" ép bằng `kq.tang1`), `test_giao_dien_a13_10_nhan.py` (bấm "Xem chi tiết" trước khi chờ `#dcChiTiet`; ≥ 50 khoá `dc_*`), `test_giao_dien_a13_12_ngon_ngu.py` (so thứ tự CLB, nhãn buổi đổi theo ngôn ngữ), `test_giao_dien_t2_ket_qua.py` và `test_giao_dien_wharton_quan_ly.py` (chờ vẽ xong, hết chạy đua). Không đổi mã sản phẩm.
- **Không làm (Truong):** T3-41 (ô trống "—" giữ nguyên), bỏ số 01 đến 06 ở thanh bên.

## 2026-11-04 — T3-L2 fix2 (điều phối): test bảng lỗi theo nhãn buổi

- `tests/test_giao_dien_bang_loi.py`: mẫu `health_thi_qua_tran_buoi` dùng buổi chữ tự đặt ("Buổi tối") thay cho mã `thu_2`, vì từ T3-L2 giao diện đổi mã buổi sang nhãn còn `format_message` giữ mã; phần đổi mã đã có test ở `tests/test_t3_l2_buoi.py`.

## 2026-11-04 — T3-L2 (ngoài sổ, Truong duyệt 04/11/2026): bớt khối, gom nút (nghiên cứu T3, lô 2)

Chỉ đổi hiển thị; thuật toán, `match_results`, `run_history`, STB, hợp đồng cột CSV không đụng tới.

- **T3-14:** nhãn buổi (Thứ 2…) qua `i18n.js`, bảng JS phản chiếu `so_nhap.NHAN_BUOI` (đường a). **T3-07:** bỏ hai ô Từ/đến chọn buổi. **T3-02/03/04:** cảnh báo gọn + nút tới Điểm quyết tâm; ẩn nút khi chưa có tệp (sửa lỗi `.import-actions{display:flex}` đè `hidden`); một nút kiểm tra.
- **T3-06/10/12/15:** dòng kết quả gọn; một nút chính theo trạng thái (`#view-pipeline[data-trang-thai]`); chân thanh bên + menu ⋯; dòng workspace "Mở" + ⋯.
- **T3-20/24/25:** mục "Chi tiết để kiểm tra"; ba ô tóm tắt (số NV1 và suất dự trữ chuyển xuống mục chi tiết, không xoá); tiêu đề cột.
- **T3-21:** bỏ thẻ "Mức lấp đầy của từng CLB" (`#fillPanel`); ô "Sắp xếp" (`#fillSapXep`, vẫn nhớ qua `rbda_sap_xep_lap_day`) chuyển lên thẻ "Theo từng câu lạc bộ"; bảng thêm cột thanh lấp đầy (hai đoạn dự trữ/chung, `veOThanhLapDay`) và cột "Lưu ý" (nhãn `nhanCanDeY` thành chữ, không còn chỉ hiện khi rê chuột); ô tóm tắt "Chỗ còn trống" mở thẻ này và đặt "Vắng nhất". Bỏ `veBieuDoLapDay`/`veDongLapDay`, CSS `.fill-row…`, khoá `fill_panel_title`, `fill_hint`, `fill_nhom_tong`, `fill_choi`; khoá mới `th_muc_lap_day`, `th_luu_y`.
- **T3-23:** khung "Xuất dữ liệu" mặc định chỉ hai nút "Xuất kết quả (Excel)" (`btn_xuat_tuy_chon`) và "Xuất theo lớp"; các ô tích và "Chọn học sinh…" nằm trong `<details id="xuatNangCao">` "Tuỳ chọn khác" (`xuat_tuy_chon_khac`); giữ cảnh báo đỏ.
- **T3-28:** một bảng "Tải theo buổi"; bỏ khối "Lịch tuần" (`loadLichTuan`, `admin_lich_tuan_*`, CSS `.lich-*`); tỉ lệ ghi "2,3" (dấu phẩy), không "2.3×".
- **T3-29/32/33/34/35:** điểm quyết tâm mặc định "Chỉ hồ sơ có vấn đề"; hàng học sinh mới cạnh ô tìm + cuộn tới phiếu; lớp hiện dạng chữ; menu ⋯ ba nút phụ (giữ "Xuất CSV học sinh này"); bỏ mã thô, chấm "Chưa lưu" nổi hơn. Chưa làm: thu gọn danh sách kết quả sau khi chọn (T3-32).
- **Test mới:** `tests/test_t3_l2_buoi.py` (5), `tests/test_giao_dien_t3_l2_van_hanh.py` (Chromium). **Test cũ sửa:** `test_giao_dien_tom_tat_ket_qua.py` (bỏ test chú thích rê chuột và nhóm theo buổi, thêm test cột thanh/Lưu ý), `test_giao_dien_bieu_do.py`, `test_giao_dien_phong_chu.py`, `test_giao_dien_thu_gon_ket_qua.py`, `test_giao_dien_diem_chuan.py` (đọc bảng CLB thay vì `.fill-row`), `test_giao_dien_khoa_xuat.py`, `test_giao_dien_ux_xuat.py`, `test_giao_dien_xuat_du_lieu.py` (mở "Tuỳ chọn khác"), `test_ws_nhan.py` + `du_lieu_ws/chu_ui_doi_co_y_t3.json`.
- **Vòng sửa 1 (tester L2):** `btn_reset_entry` = "Xoá toàn bộ phiếu của {person_l} này" / "Clear this {person_l}'s whole entry" (khớp câu xác nhận); lỗi/cảnh báo có tham số `buoi` là mã (`thu_2`) nay hiện nhãn (`nhanHoaBuoi` trong `translateError`, `i18n.js`); dòng "Lần chạy gần nhất" ở thẻ 03 dùng `dinhDangGio` và bỏ số khởi tạo; cột "Thao tác" trống ở danh sách workspace thành `sr-only`; test `test_t3_l2_buoi.py` canh tập mã `MA_BUOI_CO_NHAN` khớp `so_nhap.NHAN_BUOI` và lỗi có `buoi` hiện nhãn. T3-32 phần "thu gọn danh sách sau khi chọn" vẫn bỏ: nhiều test UI cũ bấm thẻ khác sau khi chọn; cuộn tới phiếu đã có.
- **Bất biến:** `kiem_nhanh.py` 7/7 ĐẠT, `trung_khit` (3 bộ × 5 seed) trùng khít so với `origin/main`.

## 2026-11-04 — CI-HUY (ngoài sổ, Truong yêu cầu 04/11/2026): huỷ lượt CI cũ khi có commit mới

- **`.github/workflows/tests.yml`:** thêm `concurrency` (nhóm theo workflow + loại sự kiện + nhánh; `cancel-in-progress` trừ nhánh `main`). Workflow build `.exe` (chạy tay) không đổi.

## 2026-11-04 — T3-L1 (ngoài sổ, Truong duyệt 04/11/2026): chữ và hiển thị nhỏ (nghiên cứu T3, lô 1)

- **T3-05:** ô mã bốc thăm vào mục "Nâng cao" thu gọn (`<details id="nangCao">`, mặc định 42, mở tự động khi bấm "Bốc thăm lại"); bỏ `#seedLockHint`; `stb_locked_label` thành một dòng "Đã bốc thăm lúc {locked_at}. Muốn bốc thăm lại, bấm "Bốc thăm lại…"." (giờ dạng người đọc).
- **T3-08:** bỏ ô "đã nộp nguyện vọng" (`#statPrefs`) khỏi dải số liệu; giờ chạy dạng `dd/mm/yyyy hh:mm` (`dinhDangGio` ở `js/00_nen.js`) ở chân thanh bên và bảng lịch sử; bỏ "số khởi tạo" khỏi `#lastRunLine`.
- **T3-09:** thẻ Lịch sử sắp xếp chỉ hiện khi có từ 2 lần chạy (`capNhatTheLichSu`); không đụng `run_history`.
- **T3-13:** bỏ dòng phụ "Reserve-Based DA"; tiêu đề trang và cửa sổ không còn "RB-DA" (`page_title`, `APP_TITLE`).
- **T3-30:** tab con "Dữ liệu" đổi thành "Xoá dữ liệu" (en "Delete data").
- **T3-36:** bảng tiến độ chấm bỏ cột mã CLB và thanh tiến độ; nút "Chấm" là nút phụ không mũi tên.
- **T3-37/38/39:** tiêu đề bước hộp tạo workspace "Bước n/4: …"; tiêu đề cửa sổ và `aria-label` dùng " · " hoặc ": " thay gạch dài (`main.py`, `js/075_workspace.js`, `js/04_nhap_tai_cho.js`); khoảng số "(từ 1 đến 20)", "(từ 0 đến 20)".
- **T3-40:** chữ dự phòng của `index.html` khớp catalog (62 chỗ); test mới `tests/test_t3_l1_chu_du_phong.py` canh từng phần tử `data-i18n`, placeholder và aria-label. Sửa kèm `wh_sua_rong` (đầu câu viết thường).
- **T3-43:** chữ trong tệp Excel xuất (`api_xuat.py`, 51 chuỗi): bỏ gạch dài và đại từ "em", dùng `{person_l}` theo từ vựng workspace; hai chuỗi đếm của trang "Theo lớp" nay cũng qua `t.n` (trước đây lọt `em` cứng khi workspace đặt tên khác).
- **Bảng 5.1-5.3 (trừ mục để lô sau):** tên thẻ "Xếp CLB" (`nav_pipeline`, `pipeline_title`), "Nhập nguyện vọng" (`nav_fallback`, `fallback_title`) và mọi chỗ nhắc tên thẻ (catalog, `i18n_errors.py`, `HUONG_DAN_SU_DUNG.md`); sáu mô tả `pipeline_desc`, `others_desc`, `admin_desc`, `scoring_desc`, `fallback_desc`, `import_hint`; nhãn "Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên"; "Số đơn và số chỗ", "Học sinh trên mỗi chỗ", "Chọn là nguyện vọng 1"; `xuat_hint_hoc_sinh`, `xuat_opt_kem_csv`; nút `ws_btn_*`. Lệch khỏi bảng có chủ ý: tiếng Việt giữ "tệp nén" và en "archive file" (test `test_giao_dien_tieng_viet_sach` cấm chữ zip); "Draw code" thay "Draw seed" (cấm từ kỹ thuật); `pipeline_desc`/`import_hint` viết "sổ nhập" thường, không "Sổ nhập CLB" (từ vựng workspace). Chưa làm ở lô này (để L2/L3): hai dòng cảnh báo gộp T3-02 (hàng 213, 214 của bảng 5.3), `nav_others`, `nav_admin`, `ql_tab_dc`, `kq_sx_ngay`, `kq_sap_nhan`.
- **T3-27 chia hai lô (tester L1, vòng 1):** L1 làm nhãn và placeholder của biểu mẫu CLB ở thẻ Quản lý (`th_capacity`, `th_reserve_capacity`, `th_reserve_group`, `placeholder_capacity`, `placeholder_reserve_capacity`, `placeholder_reserve_group`: Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên; en Quota / Priority seats / Priority group) và `admin_desc`. Phần còn lại của T3-27 (`th_tong_cho`, `admin_reserve_assign_title`, các chỗ khác nói "dự trữ") để L3.
- **Vòng sửa 1 (tester L1):** test Excel cũ `test_so_excel_de_dung.py` đọc theo chữ mới ("Số học sinh đã có câu lạc bộ", "Số học sinh chưa có chỗ", "mọi học sinh đều"); `th_ti_le_choi` dùng chỗ giữ danh từ (`{person} trên mỗi chỗ`, en `{person_p} per place`).
- **Khoá catalog bỏ:** `brand_sub`, `label_submitted_prefs`, `seed_locked_hint`, `seed_unlocked_for_redraw`; khoá mới `nang_cao`.
- **Test mới:** `tests/test_t3_l1_chu.py` (4), `tests/test_t3_l1_chu_du_phong.py` (1), `tests/test_giao_dien_t3_l1.py` (7, Chromium), `tests/test_giao_dien_t3_l1_ws.py` (1, Chromium). **Test cũ sửa theo chữ mới:** `test_ws_nhan.py` (bảng ảnh chụp: `KHOA_UI_DA_BO`, `THAY_CHU_T3`, `tests/du_lieu_ws/chu_ui_doi_co_y_t3.json`), `test_ws_nhan_giao_dien.py`, `test_giao_dien_khoa_hat_giong.py`, `test_giao_dien_chay.py`, `test_giao_dien_sua_loi_p1.py`, `test_giao_dien_xoa_du_lieu.py`, `test_giao_dien_quan_ly_tab_con.py`, `test_giao_dien_a13_10_diem_chuan.py`. Bản đồ mã: 188 tệp test, 3.396 ca.
- **Bất biến 1:** `kiem_nhanh.py trung_khit` (3 bộ × 5 seed) ĐẠT so với `origin/main`; lô này không đổi thuật toán.

## 2026-11-04 — T3-L0 (ngoài sổ, Truong duyệt 04/11/2026): ba lỗi sản phẩm của nghiên cứu T3 (B1/T3-26, B2/T3-01, B3/T3-42)

- **B1 / T3-26 — sửa CLB không còn xoá suất dự trữ, nhãn, buổi.** `api_quan_ly.py::create_or_update_club`: `reserve_capacity`, `reserve_group`, `buoi` mặc định `None` = "không gửi" — CLB đã có thì GIỮ giá trị đang lưu, CLB mới lấy 0 / không nhãn / không buổi; `name=None` giữ tên cũ; muốn xoá thật thì gửi 0 hoặc `""`. Kiểm suất dự trữ ≤ chỉ tiêu dùng giá trị hiệu lực (kể cả giá trị cũ). Lời gọi tường minh cũ (`("c","C",5,0,"")`) cho kết quả y như trước. Giao diện (`js/05_quan_ly.js`, `index.html`, `style.css`): sáu nhãn thường trực phía trên sáu ô (dùng lại khoá `th_*`); bấm một dòng bảng thì điền biểu mẫu từ dòng đó, khoá ô mã, nút Huỷ; khi đang sửa ô trống = xoá, gõ tay thì ô trống = không gửi (`null`).
- **B2 / T3-01 — chạy trên dữ liệu trống bị chặn.** `api.py::_run_pipeline_da_khoa`: bước 0, TRƯỚC sao lưu / khoá STB / mọi lần ghi, đếm học sinh và CLB; thiếu một trong hai thì trả `chua_co_du_lieu_de_chay` (không ghi `run_history`, không khoá seed). Giao diện (`js/02_van_hanh.js`): `khoa.thieuDuLieu` khoá nút "Chạy sắp xếp" kèm `title` lý do, ô Cảnh báo ghi "Chưa có dữ liệu để xếp…" thay cho dòng xanh.
- **B3 / T3-42 — câu `wharton_ho_so_chua_hop_le`** chỉ việc làm được (thẻ 05, tab Điểm quyết tâm, "Phóng cho đủ 100 theo tỉ lệ"), không còn bảo tắt tính năng. Chỉ đổi chữ (vi + en), không thêm công tắc.
- **Mã lỗi mới** `chua_co_du_lieu_de_chay` (`i18n_errors.py` vi+en, đã sinh lại `i18n_loi.js`); khoá UI mới `health_chua_co_du_lieu` (`i18n.js` vi+en).
- **Sửa CI L0 (fixci1):** nghiệm thu A13.13 đổi chữ theo quyết định B3 của Truong (04/11/2026): `test_a13_13_kiem_nhan.py` (D1, E3) và `test_wharton_mac_dinh_bat.py` nay đòi câu chỉ trỏ tới việc làm được (điền điểm, "Phóng cho đủ 100"), KHÔNG còn đòi chữ "tắt"; `test_a13_9_stress.py::test_8_so_rong_...` nay đòi chạy xếp trên sổ rỗng bị từ chối `chua_co_du_lieu_de_chay` (không sập, không `run_history`, không khoá STB); mã mới thêm vào `MA_MOI_SAU_ANH_CHUP` của `test_ws_nhan.py`.
- **Test mới:** `tests/test_t3_l0_backend.py` (11 ca), `tests/test_giao_dien_t3_l0.py` (7 ca, Chromium).
- **Vòng sửa 1 (tester):** ô "Suất dự trữ" mặc định để TRỐNG (trước là "0" nên gõ tay lại mã cũ vẫn xoá suất dự trữ); câu B3 bản tiếng Việt dùng "mục Điểm quyết tâm" thay "tab" (test `test_giao_dien_tieng_viet_sach`).
- **Bất biến 1:** cấu hình mặc định trùng khít `origin/main` — `kiem_nhanh.py trung_khit` (3 bộ × 5 seed) và `kiem_trung_khit` gọi trực tiếp với 20 seed (3 bộ × 20 seed).

## 2026-11-04 — T3-HT (ngoài sổ, Truong duyệt 04/11/2026): hạ tầng tự động hoá T3 (điều phối + viết mã + soát)

- **`.claude/hooks/handoff_khi_day_ngu_canh.py`:** đọc vai phiên từ `.claude/phien_vai.json` (không vào git): ngưỡng riêng (`nguong`; con 400k, điều phối 700k), tệp bàn giao theo vai (`docs/phien/<nhánh>__impl.md`, `__tester.md`), phiên con được nhắc `send_message` báo phiên điều phối; không có tệp vai thì giữ hành vi cũ. Lấy tên nhánh bằng `git branch --show-current`.
- **Tài liệu:** `docs/phien/T3_GIAO_THUC.md` (giao thức, khuôn tin nhắn, bàn giao), `docs/phien/claude__gallant-mendel-uki8j2.md` (kế hoạch bốn lô T3-L0..L3 và quyết định của Truong).
- **Test:** `tests/test_hook_ban_giao.py` (6 ca).
- **Sửa CI:** `docs/ke_hoach/CLAUDE_CHI_TIET.md` bản đồ mã đếm lại: 184 tệp test, 3.384 ca (test `test_ban_do_ma_so_tep_test_la_so_that`). `tests/test_hook_ban_giao.py` giữ PATH hệ thống (CI Windows không tìm thấy git) và chỉ `git init` một lần mỗi thư mục.

## 2026-11-04 — sửa CI main 3c67776: test giao diện A14 chập chờn

- `tests/test_giao_dien_a14_lop.py::test_theo_lop_nhieu_buoi_cot_theo_ngay_o_trong_va_dong_do`: CI Linux (run 41803199666) báo `IndexError` ở `r.split("\t", 3)[3]` — `innerText` của `<tr>` chỉ có dấu tab khi bảng đã được vẽ bố cục. Nay chờ đủ 3 hàng rồi đọc từng ô bằng `textContent`, kiểm mỗi hàng 6 ô. Chỉ sửa test; máy cloud chạy cả tệp 3 lần đều 24/24 xanh.

## 2026-11-04 — PR #8: sửa CI sau T4-K1 (Windows báo 4 lỗi ở 5a88060)

- `test_a14_sua_sau_soat.py::test_a5_...` (DROP COLUMN): đã khỏi khi gộp main (lấy bản B9 của main).
- **`docs/ke_hoach/tham_khao/_chung.py::nap_rb`:** từ T4-K1 `rbda_priority_pipeline` import `lop_hoc_sinh` theo tên; `_ten_can_nap` nạp `lop_hoc_sinh` (từ cùng thư mục hoặc cùng tệp .exe) trước mô-đun chính khi có, bản cũ không có thì bỏ như `nhan_ws`. `tests/test_tham_khao_verify_nhanh.py` chép thêm `lop_hoc_sinh.py` vào thư mục thử.
- `tests/test_mau_forms_thi_clb.py::test_raw_google_khop_tai_lieu_dinh_dang`: kỳ vọng dòng ghi RAW_PHIEU theo `.gs` mới (cột `lop` tuỳ chọn, T4-K1).

## 2026-11-03 — Z-SOAT-2 (ngoài sổ, Truong duyệt 03/11/2026): `soat-ma` tìm ruff trên PATH

- **`.claude/skills/soat-ma/scripts/kiem_nhanh.py::kiem_ruff`:** trước chỉ chạy `python -m ruff`, nên máy cài ruff bằng pipx / uv (máy cloud) luôn báo KHÔNG ĐẠT "chưa cài ruff" dù mã sạch. Nay khi Python không có mô-đun ruff thì thử `ruff` trên PATH (`shutil.which`); không có ở đâu cả mới báo chưa cài. Máy đã có mô-đun ruff: không đổi.
- **Test:** `tests/test_skill_soat_ma.py` thêm 2 ca (`test_ruff_chi_co_tren_path_van_chay`, `test_ruff_khong_co_o_dau_ca_thi_bao_chua_cai`); `_co_ruff` nhận cả ruff trên PATH nên ca cũ `test_ruff_dat_va_khong_dat` không còn bị bỏ qua trên máy đó. 47 ca xanh.

## 2026-11-03 — A14-B10 (ngoài sổ, Truong duyệt 03/11/2026): bỏ `DROP COLUMN` ở hai test A14 còn lại

Cùng kiểu rủi ro với B9 (SQLite của CI báo "incomplete input"). Chỉ sửa test, không đụng mã sản phẩm.

- Hàm phụ trợ mới `_bo_cot(conn, bang, cot)` (trong từng tệp test): đọc schema thật bằng `PRAGMA table_info`, dựng lại bảng thiếu đúng một cột (giữ khoá chính và dữ liệu) bằng `CREATE TABLE` / `INSERT ... SELECT` / `RENAME`, cú pháp có ở mọi bản SQLite. Không chép cứng schema, nên tự theo khi bảng thêm cột về sau.
- Dùng ở `tests/test_a14_tu_vung_cohort.py::test_di_tru_schema_them_cot_vao_csdl_cu_chay_lap_va_giu_du_lieu` và `tests/test_a14_sua_sau_soat.py::_csdl_cu_co_du_lieu`. Mọi assert giữ nguyên; 48 ca của hai tệp xanh.
- Trên nhánh này `test_a5_sao_luu_dung_mot_lan_truoc_buoc_di_tru_dau_tien` vẫn là bản trước B9; bản sửa B9 có ở `main`, giữ nguyên để gộp không xung đột.

## 2026-11-04 — T4-K1 sửa vòng 1 (tester soát fff0f41)

- **[Chặn] Gói skill chạy ngoài kho:** `chuan_hoa_lop` chuyển sang mô-đun gốc kho mới `lop_hoc_sinh.py` (chỉ thư viện chuẩn, hành vi y hệt). `rbda_priority_pipeline.py` nhập lại và giữ tên công khai, nên mọi nơi gọi cũ và test cũ không đổi. `xu_li_raw.py` nhập từ `lop_hoc_sinh`; `dong_goi_skill.py` đưa `lop_hoc_sinh.py` vào `xu-li-raw-forms.zip` (skill không mang mã thuật toán). PyInstaller: `rbda_priority_pipeline` nhập `lop_hoc_sinh` ở mức mô-đun nên phân tích tĩnh tự gom, không cần đổi `kiosk.spec`.
- **Báo cáo lớp:** phiếu giữ không ghi lớp thì ghi rõ "phiếu giữ N không ghi lớp, phiếu M ghi X; Sổ để trống" (cả khi các phiếu khác nhau lẫn khi chỉ có một lớp ở phiếu khác); Sổ vẫn không mượn lớp. Tiêu đề mục đổi thành "Lớp không thống nhất giữa các phiếu của cùng một mã".
- **`.gs` (hai bộ sinh vẫn trùng):** khớp mã `ma_hs` bằng cắt khoảng trắng và IN HOA ở cả hai phía (`maLop_`); đếm mã học sinh không có trong tab `hoc_sinh` (`maKhongCoLop_`), ghi một dòng vào trang Cảnh báo và Logger. Tài liệu: cột `ma_hs` định dạng văn bản `@`.
- **Test:** `tests/test_t4_k1_lop.py` lên 12 ca (thêm: khớp mã chuẩn hoá và đếm mã không khớp ở `.gs`; gói zip chạy ngoài kho với cột `lop`; mở rộng ca phiếu giữ trống lớp).
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: thêm `lop_hoc_sinh.py` vào bản đồ mã.

## 2026-11-04 — T4-K1 (ngoài sổ, Truong duyệt 03/11/2026): cột `lop` tuỳ chọn từ `hoc_sinh` tới cột Lớp của Sổ

Thay đổi số 1 ở mục 11.2 của `docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md` (DEC-2: lớp lấy từ `hoc_sinh` lúc xuất, biểu mẫu KHÔNG hỏi lớp).

- **`xu_li_raw.py`:** `COT_RAW` giữ 19 cột. RAW có cột `lop` (cột thứ 20) thì ghi vào cột Lớp của Sổ (`ghi_so_nhap(co_lop=True)`, A14), lấy lớp từ PHIẾU GIỮ, chuẩn hoá bằng `chuan_hoa_lop` của phần mềm (không viết hàm mới). Các phiếu của cùng một mã ghi lớp (khác rỗng) khác nhau thì thêm mục "lop_khac_giua_cac_phieu" vào `BAO_CAO_BAT_THUONG.md`. Không có cột `lop`: Sổ và báo cáo y như cũ.
- **`TAO_GOOGLE_FORM.gs` và `tao_google_forms.py` (sinh giống hệt):** `chamTheoCLB(ghiLop)`, chỉ `ghiLop === true` mới bật (menu/trigger truyền đối tượng sự kiện không bật nhầm); mặc định TẮT thì RAW 19 cột như cũ. Bật thì thêm cột `lop` đọc từ tab `hoc_sinh` (`ma_hs`, `lop`); hàm mới `chamTheoCLBCoLop`, `docLopHocSinh_`, `themCotLop_`, hằng `ID_BANG_HOC_SINH`. Thiếu tab thì báo lỗi trước khi tạo thư mục. `COT_RAW` của `.gs` vẫn bằng của skill.
- **Tài liệu:** `DINH_DANG_RAW.md` (cột tuỳ chọn thứ 20), `SKILL.md` của `xu-li-raw-forms` và `tao-google-form-clb`.
- **Test mới:** `tests/test_t4_k1_lop.py` (10 ca lúc đầu, 12 sau vòng sửa 1): có `lop`; không có `lop` (Sổ bằng đúng cách cũ); `lop` rỗng; lớp khác nhau giữa các phiếu; phiếu giữ trống lớp; thư mục nhiều phần có `lop`; `.gs` mặc định tắt (kể cả khi truyền sự kiện), bật, thiếu tab `hoc_sinh`; `.gs` khớp `noi_dung()`. Ca ghim `COT_RAW` ở `test_skill_xu_li_raw.py` giữ xanh.
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 180 tệp test.
- Không đụng kiosk, hợp đồng cột CSV, `match_results`.

## 2026-11-03 — T4-K3 (ngoài sổ, Truong duyệt 03/11/2026): skill `xu-li-raw-forms` đọc thư mục nhiều phần CSV

Thay đổi số 3 ở mục 11.2 của `docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md`: đợt trên 1.000 phiếu được xuất thành nhiều phần `<tên>_p01.csv`, `_p02.csv`... nên skill phải ghép được.

- **`xu_li_raw.py`:** hàm mới `doc_raw(duong)`. Tệp đơn: y như `doc_bang` cũ. Thư mục: ghép các phần theo số phần (thứ tự tự nhiên), từ chối bằng `LoiDauVao` (không ghi tệp nào) khi không có phần, nhiều bộ xuất lẫn nhau, thiếu phần / số phần trùng, tiêu đề lệch, hoặc một `phieu_so` ở hai phần. `chay` gọi `doc_raw`; `--raw` nhận thư mục. `COT_RAW` không đổi.
- **`SKILL.md`:** ghi cách dùng thư mục và các trường hợp bị từ chối.
- **Test mới:** `tests/test_skill_xu_li_raw_nhieu_phan.py` (8 ca): thư mục 3 phần cho Sổ và báo cáo giống hệt một tệp; p2 trước p10; tệp đơn như cũ; năm ca từ chối. `tests/test_skill_xu_li_raw.py` (8 ca) giữ xanh.
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 179 tệp test (canh bởi `tests/test_a13_12_tai_lieu.py`).
- Không đụng kiosk, hợp đồng cột CSV, `match_results`.

## 2026-11-03 — T1a, T1b (nhánh `claude/epic-knuth-801pkw`; Truong duyệt, bỏ qua sổ đăng ký)

- **T1a — sổ mẫu chính có cột Lớp:** `mau_csv/SO_NHAP_CLB.xlsx` là sổ TRỐNG (không có học sinh nào để gán lớp). Nó giờ có cột **Lớp** ngay sau **Họ tên**, giống hệt sổ phần mềm tạo (`tao_so_nhap_mau`, A14). `mau_csv/tao_so_nhap.py::tao_mau_trong` gọi `ghi_so_nhap(..., co_lop=True)`; tệp sinh lại bằng kịch bản, không sửa tay. `HUONG_DAN_SO_NHAP.md` ghi đây là sổ mẫu chính. Hai sổ ví dụ `vi_du_*` GIỮ NGUYÊN (khớp từng dòng với bộ ba CSV, mà CSV ví dụ không có lớp).
- **T1b — nhãn trùng cũ không chặn lưu:** `cau_hinh_ws.ghi_cau_hinh` chỉ ném `NhanTrung` khi cấu hình mới có cặp danh từ trùng nhãn mà cấu hình ĐANG LƯU chưa có. Workspace cũ đã trùng đổi tên / đổi luật được; thêm cặp trùng thứ hai vẫn bị chặn; sửa hết trùng thì qua. `chuan_hoa()` (kiểm trước khi dựng workspace) và cảnh báo nhập `so_nhap_canh_bao_nhan_trung` giữ nguyên.
- **Test:** mới `tests/test_t1b_nhan_trung_cu.py` (6); sửa `tests/test_so_nhap.py::test_mau_trong_doc_duoc_va_dung_bo_cuc` (tiêu đề có Lớp).

### T2 sửa vòng 3

- Ảnh chụp `tests/du_lieu_ws/so_nhap_truoc_khi_co_cfg.json` (bốn ca `test_mac_dinh_truong_hoc_cho_ra_dung_so_nhu_truoc`): sau vòng 2 (G3) chữ sheet "Hướng dẫn" đổi theo quy tắc chữ của chủ dự án. Đã so từng khoá: CHỈ năm ô `Hướng dẫn/o/A1, A16, A18, A23, A33` khác (hai ảnh `co_du_lieu` và `trong`, cả bốn cấu hình); mọi khoá khác trùng. Chỉ thay hai cây con `Hướng dẫn` bằng lập trình, giữ định dạng tệp; ghi chú ở `tests/test_ws_so_nhap.py`. Đã tìm ảnh chụp khác chứa chữ hướng dẫn: không còn tệp nào.

### T2 sửa vòng 2

- **G1 (T2, tràn ngang):** `.main { min-width: 0 }` (cột `1fr` của lưới không còn nở theo bảng rộng, nên bảng chỉ cuộn ngang trong `.scroll-x`, trang thì không); ô CLB `min-width` 7em. Test mới `test_khong_tran_ngang_trang_voi_ten_clb_rat_dai` (độ rộng 600, 1024, 1280; tên CLB 60 ký tự; ba cách xem; `scrollWidth <= innerWidth`). Đã thử gỡ dòng sửa: test đỏ ở 600 và 1024.
- **G2 (tài liệu):** `HUONG_DAN_SU_DUNG.md` bảng "xuất hồ sơ học sinh" đổi số thẻ (04, 03, 05) và đoạn lớp mô tả đúng: lọc và sắp theo lớp ở thẻ 03, cột Lớp và cách xem Theo lớp ở thẻ 02.
- **G3 (chữ sheet Hướng dẫn):** bỏ dấu gạch dài và xưng "em" trong các dòng hướng dẫn của `so_nhap.py` (cả bản hằng số lẫn bản dựng theo cấu hình); sinh lại `mau_csv/SO_NHAP_CLB.xlsx`. Test kiểm mọi dòng hướng dẫn của sổ mẫu: không "—", không từ "em/tôi/tớ". Các sheet khác không đổi. Sinh lại sáu sổ `du_lieu_test/SO_NHAP_DQT_*.xlsx` bằng `sinh_du_lieu_diem_quyet_tam.py` (test `test_sinh_lai_bang_script_ra_dung_noi_dung_o` đòi tệp khớp script).

### T1/T2 sửa vòng 1 (tester: 2 lớn, 5 vừa, 3 nhỏ)

- **F1 (T1b):** `cau_hinh_ws._cap_trung_day_du` liệt kê MỌI cặp danh từ cùng nhãn kèm ngôn ngữ (ba danh từ cùng nhãn cho ba cặp; `cac_cap_nhan_trung` giữ nguyên cho cảnh báo nhập). `ghi_cau_hinh` chỉ từ chối khi có cặp (ngôn ngữ, a, b) mới so với mốc; báo cặp mới đầu tiên theo thứ tự `DANH_TU`, vi trước en.
- **F2 (T1b):** `ghi_cau_hinh(..., nhan_goc=None)` và `workspace.tao(..., nhan_goc=None)`; `nhan_ban` kiểm không nghiêm phần nhãn trùng và lấy nhãn nguồn làm mốc, cả hai chế độ `kem_du_lieu`: bản sao giữ nhãn trùng cũ, trùng mới vẫn bị chặn.
- **F3 (T1b):** `luu_mau` kiểm nghiêm: workspace cũ trùng nhãn lưu mẫu thì lỗi `nhan_trung_danh_tu`, không ghi tệp.
- **F4 (T1a):** sổ mẫu tĩnh dựng bằng cấu hình mặc định như phần mềm (`chuan_hoa({})`), nên MỌI ô của MỌI sheet (cả Hướng dẫn) trùng sổ phần mềm tạo; `huong_dan(co_lop=True)` thêm một dòng nói cột Lớp tuỳ chọn. README, TAI_LIEU_DU_LIEU, BAN_GIAO ghi đây là sổ mẫu chính có cột Lớp.
- **F5:** số thẻ cũ sửa lại sau khi đánh số lại (`i18n.js`, `index.html`, `i18n_errors.py` và `i18n_loi.js` sinh lại, README, HUONG_DAN_CSV, HUONG_DAN_SO_NHAP, chú thích đầu các tệp js, `api_bao_cao.py`).
- **F6:** bỏ khoá mồ côi `results_title`, `results_desc`, `tkb_title`, `tkb_desc`, `tkb_so_clb` (`tests/test_ws_nhan.py` đổi mẫu `tkb_desc` thành `kq_desc`).
- **F7:** số ít / số nhiều ở bản tiếng Anh: `kq_dem_ma_nhieu`, `theolop_dem_nhieu` (số ít chỉ khi n = 1).
- **F8 (T2):** *Theo CLB*: tầng 2 "Theo ngày trong tuần" chia ô chọn CLB thành nhóm theo buổi (thứ tự ngày), "Theo mã học sinh" là danh sách phẳng theo vần; bảng thành viên luôn theo mã. Cột STT, mã, họ tên, lớp không xuống dòng. Ô tìm ngắn hơn (`kq_tim_ph`). Nhớ cả lớp và CLB đã chọn trong khoá `rbda_ket_qua_xem_v1` (giá trị không còn tồn tại thì lùi về mục đầu).
- **Test cũ sửa có chủ đích:** `tests/test_ws_nhan.py` (ảnh chụp chuỗi mặc định: bỏ năm khoá mồ côi khỏi phép so, cho phép đúng hai chuỗi đổi số thẻ; mẫu 20 chuỗi dùng `fill_hint`); `docs/ke_hoach/CLAUDE_CHI_TIET.md` (178 tệp, 3.299 ca).
- **Test:** `tests/test_t1b_nhan_trung_cu.py` (thêm F1, F2, F3 và so mọi sheet sổ mẫu), `tests/test_giao_dien_t2_ket_qua.py` (thêm nhóm theo buổi, nhớ lớp / CLB, số ít số nhiều); `test_giao_dien_a14_lop.py` (khoá i18n 25 thành 26, tuỳ chọn CLB có nhóm).

### T2 — gộp thẻ 02, 06, 07 thành "Kết quả" và "Dữ liệu khác" (bảy thẻ thành sáu)

- **Thanh bên:** 01 Vận hành sắp xếp, 02 Kết quả (`results`), 03 Dữ liệu khác (`others`), 04 Nhập tại chỗ, 05 Quản lý CLB & dự trữ, 06 Nhập điểm. Bỏ thẻ `members` và `theolop`; `TAB_LOADERS` (`js/01_khung.js`), khởi động (`initKetQuaHandlers`) và vẽ lại khi đổi ngôn ngữ (`reapplyDynamicTextForLangChange`) theo tên mới.
- **02 Kết quả** (`js/09_the_xem.js`, `view-results`, chỉ đọc, không điểm, không số bốc thăm): tầng 1 *Theo lớp | Theo CLB | Theo mã học sinh*; tầng 2 (cách sắp) *Theo ngày trong tuần | Theo mã học sinh | Theo lớp*, mục *Theo lớp* chỉ hiện khi tầng 1 là *Theo mã học sinh* (lựa chọn lưu ở tầng 2 mà không hợp lệ thì lùi về *Theo ngày trong tuần*, không ghi đè). Sắp theo ngày = vị trí buổi sớm nhất em có CLB (thứ tự `ds_buoi` do backend sắp theo ngày), sau đó theo mã; sắp theo mã là sắp tự nhiên (HS9 trước HS10); sắp theo lớp theo thứ tự `list_classes` (tự nhiên, lớp trống cuối). Nhớ hai tầng ở `localStorage` khoá `rbda_ket_qua_xem_v1` (try/catch). Giữ lớp và CLB đã chọn khi đổi cách xem hay rời thẻ. Dùng lại `get_thoi_khoa_bieu`, `get_danh_sach_clb`, `get_club_fill_stats`, `list_classes`, `get_trang_thai_ket_qua`; không thêm backend. Trạng thái rỗng: chưa chạy xếp, chưa có lớp nào, tìm không thấy.
- **03 Dữ liệu khác** (`view-others`, hàm vẫn tên `loadResultsTab`): mọi mục còn lại của thẻ 02 cũ, giữ nguyên thu gọn. Bảng thời khoá biểu từng học sinh (`tkbPanel`, `loadThoiKhoaBieu`) chuyển sang 02 Kết quả, không giữ hai bản.
- **Chữ:** khoá i18n mới `nav_others`, `others_*`, `kq_*` (vi và en); bỏ `nav_members`, `nav_theo_lop`, `members_title|desc|chon|chua_chon`, `theolop_title|desc|chon|chua_chon`. `style.css`: nút chọn hai tầng và `.main:has(#view-results.is-active)` để thẻ không co lại ở *Theo CLB*.
- **Test mới:** `tests/test_giao_dien_t2_ket_qua.py` (11 ca Chromium: đổi tầng 1, tầng 2 và mục *Theo lớp*, sắp theo mã / lớp / ngày, nhớ sau khi mở lại, kho lưu trữ hỏng, giữ lựa chọn, trạng thái rỗng, đổi ngôn ngữ, không điểm và không số bốc thăm). **Test cũ sửa có chủ đích** (thay đổi đã duyệt): các tệp `tests/test_giao_dien_*` bấm `data-tab="results"` cho nội dung cũ nay bấm `others` và `#view-others`; `test_giao_dien_a14_lop.py` (hai thẻ xem cũ thành các ca của thẻ Kết quả, fixture `mo` thêm tham số `them` và ngữ cảnh trình duyệt dựng tường minh, số khoá i18n 35 thành 25); `test_giao_dien_thu_gon_ket_qua.py` (`tkbPanel` bỏ, chín mục thành tám, mục thay thế `doPhuPanel`); `test_giao_dien_a13_12_tkb.py` (ô tìm nay ở *Theo mã học sinh*).

## 2026-11-02 — A14 — phần A (nền, nhập, API): lớp của học sinh

**Đã merge vào main qua PR #6 (b044c4c, 03/11/2026).**

Mỗi học sinh có thể có "lớp" (vd 10H1A) CHỈ để hiển thị, sắp, lọc, xuất cho giáo viên chủ nhiệm. Thuật toán phân bổ KHÔNG đọc lớp. Phần B (xuất + giao diện) ở nhánh `claude/a14-giao-dien`.

**NGOẠI LỆ BẤT BIẾN 7 (Truong duyệt 02/11/2026).** Hợp đồng cột CSV đổi có chủ đích: cột TUỲ CHỌN `class_id` ngay sau `reserve_group` trong CSV nguyện vọng và CSV chọn thi; Sổ nhập thêm cột "Lớp" (nhãn `cohort`) ngay sau "Họ tên". Không có cột / ô trống thì giữ lớp cũ; lần ghi sau cùng thắng. Không lớp nào thì `thanh_csv` và Sổ xuất ra giống từng byte như cũ.

- **Schema:** `students.class_id TEXT` (NULL = chưa có); `di_tru_schema` bước 7 `ALTER TABLE` có sao lưu `.bak-` khi bảng đã có dữ liệu, chạy lặp an toàn.
- **`chuan_hoa_lop(raw)`** (`rbda_priority_pipeline.py`): NFC, bỏ ký tự vô hình (Cf) và điều khiển (Cc), cắt hai đầu, gộp khoảng trắng liên tiếp, IN HOA; rỗng → None. Không ép mẫu. `LOP_TOI_DA = 50`.
- **Từ vựng:** danh từ thứ sáu `cohort` (vi "Lớp", en "Class") ở `nhan_ws.py`; cấu hình cũ thiếu `cohort` lấy mặc định. Kỹ năng `tao-workspace-tu-raw` nhận `labels.cohort` tuỳ chọn. Bản JS (`i18n.js`, `js/075_workspace.js`) thuộc phần B.
- **Nhập:** `import_preferences_csv`, `import_test_selection_csv` (dài: giá trị không trống đầu tiên); `so_nhap` đọc theo tên cột (Lớp, Mã lớp, Lop, Class, Class ID, class_id, nhãn `cohort`), `doc_so_nhap` → `class_id` (None = sổ không có cột; "" = ô trống), `ghi_so_nhap(co_lop=)`; `tao_so_nhap_mau` luôn có cột Lớp; `export_du_lieu_dau_vao` có cột Lớp khi có em có lớp (hai chỗ trong `api_xuat.py`). Cảnh báo `so_nhap_canh_bao_thieu_lop` {n} chỉ khi Sổ có cột mà n ô trống.
- **API:** `list_students_admin(sort_by, class_id)`, `set_student_class`, `list_classes`, `create_student_if_missing(class_id)`, `submit_test_selection(class_id)` và `submit_preferences(class_id)` (đối số vị trí thứ 3; lớp phải nằm trong `list_classes`, sai → `lop_khong_co_trong_danh_sach`), `get_match_results(class_id, sort_by)`. Mã lỗi mới: `error_saving_student_class`, `error_reading_classes`, `lop_khong_co_trong_danh_sach`, `so_nhap_canh_bao_thieu_lop`.
- **Test mới:** `tests/test_a14_lop_backend.py` (13), `tests/test_a14_lop_nhap.py` (18), `tests/test_a14_tu_vung_cohort.py` (22), `tests/test_a14_sua_sau_soat.py` (26, vòng sửa bên dưới) — gồm các bất biến: `match_results` giống hệt khi có / không lớp; `class_id` không có trong lõi phân bổ ngoài schema / `di_tru_schema` / `chuan_hoa_lop`; đổi lớp không làm `ket_qua_cu`; `run_history` không đụng.
- **Vòng sửa sau soát chéo (Truong duyệt 02/11/2026), commit riêng từng mục:**
  - **A1 — nhãn hai danh từ trùng nhau:** `cau_hinh_ws` từ chối (ném `NhanTrung`, mã `nhan_trung_danh_tu` {a, b, nhan}) cấu hình có hai danh từ cùng nhãn sau strip + casefold, vi và en xét riêng, mọi cặp trong sáu danh từ. Cấu hình ĐÃ LƯU mà trùng vẫn đọc được (`doc_cau_hinh` không kiểm trùng); `so_nhap._khop_cot` gán cột trùng tên theo thứ tự Sổ ghi (Lớp trước Nhóm; chỉ một cột trùng thì là Nhóm như cũ) nên khứ hồi không đảo; nạp Sổ báo `so_nhap_canh_bao_nhan_trung`. Lưu ý: ghi một cấu hình trùng đã lưu từ trước (đổi tên workspace…) cũng bị từ chối cho tới khi đặt lại nhãn.
  - **A2 — `_khoa_lop_tu_nhien`:** chỉ chữ số ASCII 0-9 là số (lớp "10²" không còn làm hỏng `list_classes` / sắp theo lớp). Giữ tên và chữ ký.
  - **A3 — `chuan_hoa_lop`:** NFC, bỏ Cf (U+200B, U+FEFF…) trước khi cắt / gộp / IN HOA.
  - **A4 — giới hạn đầu vào:** `set_student_class`, `submit_*`, `create_student_if_missing` từ chối kiểu không phải str / int / float (`lop_sai_kieu`), bỏ ký tự điều khiển (Cc), > 50 ký tự sau chuẩn hoá → `lop_qua_dai` {toi_da: 50}. Nhập CSV / Sổ không chặn: cắt còn 50 và cảnh báo `canh_bao_lop_bi_cat` {n}.
  - **A5 — `di_tru_schema`:** sao lưu chụp MỘT lần ngay trước việc di trú đầu tiên cần sửa schema (trước chỉ ở bước 7, sau các bước 1 và 6) và chỉ khi đã có dữ liệu; lỗi ghi tệp sao lưu không làm hỏng việc mở workspace.
  - **A6 — tài liệu:** mục này, `CLAUDE_CHI_TIET.md`, tiêu đề `SO_DANG_KY_33_MUC.md`, `TIEN_DO.md`, tệp bàn giao.
  - **C1 — ghi lại cấu hình đã lưu có nhãn trùng (Truong duyệt 03/11/2026):** `ghi_cau_hinh` / `chuan_hoa` / `workspace.tao` nhận `cho_phep_trung_nhu`; cặp nhãn trùng Y HỆT cấu hình đang lưu (hoặc nguồn nhân bản) được để qua, nên đổi tên workspace, cập nhật phần khác và nhân bản (có / không kèm dữ liệu) một workspace cũ trùng nhãn đều chạy, nhãn giữ nguyên. Cặp trùng MỚI hoặc bị đổi vẫn bị `nhan_trung_danh_tu`. Test: `tests/test_a14_sua_sau_soat.py` (6 ca `test_c1_*`).
  - **C2 — Sổ / CSV mẫu tĩnh có cột Lớp MÔ PHỎNG (Truong duyệt 03/11/2026: Sổ mẫu tĩnh có cột Lớp mô phỏng):** script mới `du_lieu_test/them_lop_vao_mau.py` (seed cố định 112026201–204, lớp `10A1` … `12A3`, chạy lại ra đúng cùng byte) chèn cột `class_id` NGAY SAU `reserve_group` trong CSV và dựng lại các Sổ bằng `mau_csv/tao_so_nhap.py` (cột "Lớp" ngay sau "Họ tên"). KHÔNG đụng `bo_sach` và dữ liệu của số liệu đã công bố; `SO_NHAP_CO_LOI_CO_Y.xlsx` giữ bố cục cũ (`LOI_CO_Y` trỏ vào ô cụ thể). `match_results` của mọi bộ giống hệt trước (băm chốt trước khi thêm lớp, có test). Nạp các Sổ mới: không có `so_nhap_canh_bao_thieu_lop`. Tệp đổi băm (chỉ băm TỆP, kết quả xếp không đổi):
    - `mau_csv/SO_NHAP_CLB.xlsx` — sổ mẫu trống có thêm cột Lớp.
    - `mau_csv/vi_du_day_du/SO_NHAP_CLB_vi_du.xlsx`, `mau_csv/vi_du_ca_tuan/SO_NHAP_CLB_vi_du.xlsx`, `du_lieu_test/vi_du_huong_dan/SO_NHAP_VIDU.xlsx` — dựng lại từ CSV có `class_id` (24 / 60 / 10 em, chỉ thêm lớp).
    - `mau_csv/vi_du_day_du/{02_chon_CLB_muon_thi,03_xep_hang_nguyen_vong}.csv`, `mau_csv/vi_du_ca_tuan/{02,03}_….csv`, `mau_csv/{07_chon_club_thi_nhieu_buoi,08_nguyen_vong_nhieu_buoi}.csv`, `du_lieu_test/vi_du_huong_dan/VIDU_{02,03}_….csv` và `.xlsx` — thêm cột `class_id`.
    - Tài liệu khớp: `TAI_LIEU_DU_LIEU.md` (header và cỡ tệp), `mau_csv/HUONG_DAN_SO_NHAP.md`, `mau_csv/HUONG_DAN_CSV.md`, hai `GIAI_THICH.md`. Test mới: `tests/test_a14_mau_co_lop.py` (30 ca). Test cũ sửa có chủ đích: `tests/test_so_nhap.py::test_mau_trong_doc_duoc_va_dung_bo_cuc` (bố cục sổ mẫu), `docs/ke_hoach/CLAUDE_CHI_TIET.md` (173 tệp, 3.253 ca của nhánh A). Việc để sau: skill `sinh-du-lieu-clb` chưa có tuỳ chọn lớp mô phỏng.
- **Test cũ sửa có chủ đích:** `tests/test_ws_nhan.py` và `tests/test_wharton_ma_loi.py` (danh sách danh từ thành sáu); `tests/test_ws_nhan.py` thêm đúng 4 mã lỗi mới vào `MA_MOI_SAU_ANH_CHUP` (theo tiền lệ A13).
- **Test cũ khác sửa có chủ đích (thay đổi đã duyệt: Sổ mẫu có cột Lớp, `get_student_entry_state` thêm `class_id`, thêm 3 tệp test):** `tests/test_ws_so_nhap.py` (3 ca), `tests/test_ws_luat.py`, `tests/test_ws_sua_loi_3.py` (dòng học sinh thêm một ô cho cột Lớp; vị trí NV1 dịch một cột), `tests/test_wharton_kiosk.py` (thêm khoá `class_id`), `docs/ke_hoach/CLAUDE_CHI_TIET.md` (168 → 171 tệp test).

## 2026-11-02 — A14 — phần B (xuất theo lớp và giao diện lớp)

Phần B của mục A14 "Lớp của học sinh" (phần A: cột `students.class_id`, `chuan_hoa_lop`, danh từ `cohort`, các API lớp). Lớp chỉ để hiển thị, lọc, sắp và xuất cho giáo viên chủ nhiệm; thuật toán, `match_results`, `run_history` không đổi.

- **`api_xuat.py`:** trang mới **"Theo lớp"** trong Sổ kết quả, LUÔN có, đứng sau "Theo CLB" (sổ từ 6 thành 7 trang; 8 khi bật điểm quyết tâm). Mỗi lớp một khối (thứ tự tự nhiên: 10A2 trước 10A10), ngắt trang giữa các lớp, khối cuối "Chưa có lớp" nếu có em trống lớp. Không có điểm thi, điểm quyết tâm, số bốc thăm hay diện trúng tuyển; nhiều buổi thì mỗi buổi một cột; em chưa có chỗ tô đỏ. Trang Hướng dẫn thêm một dòng nói trang này không có điểm, gửi giáo viên chủ nhiệm được.
- **`export_theo_lop(output_path="")`:** API mới, ra MỘT THƯ MỤC, mỗi lớp một `.xlsx` một trang, thêm `_chua_co_lop.xlsx` nếu cần; tên tệp qua `_ten_file_an_toan` + `_ten_chua_dung`; đường dẫn theo `_duong_xuat` (đường tuyệt đối đã có thì thành `x (2)`, không ghi đè); chạy dưới `_khoa_xuat`; chưa có kết quả → `xuat_chua_co_ket_qua`, không tạo gì. Trả {thu_muc, n_tep}.
- **Cột "Lớp" ngay sau "Họ tên"** (luôn có, kể cả trống): trang Danh sách (một buổi và bảng thời khoá biểu nhiều buổi, CHỈ bản Excel qua `du["tkb_xlsx"]`), trang "Theo CLB", CSV tổng, CSV `_theo_club`. KHÔNG đổi: CSV thời khoá biểu, CSV từng buổi, CSV số bốc thăm, `export_hoc_sinh_csv`, báo cáo Word.
- **Giao diện:** thẻ Quản lý/Học sinh có cột Lớp, ô lọc (Tất cả / từng lớp / Chưa có lớp), ô sắp theo lớp, ô sửa lớp từng em (`set_student_class`). Thẻ Kết quả có cột Lớp, ô lọc, ô sắp, nút **Xuất theo lớp** (khoá khi chưa có kết quả). Kiosk (thẻ 03) có danh sách thả xuống cố định từ `list_classes`: có lớp thì BẮT BUỘC chọn trước khi Lưu (cả tạo em mới), không có lớp nào thì ẩn. Workspace có ô nhãn thứ 6 cho `cohort`. `i18n.js` thêm `cohort` vào bản JS của danh từ (`NHAN_MAC_DINH`, `CHO_GIU_DANH_TU`); chữ mới ở `i18n.js` (vi + en), `js/075_workspace.js` thêm `cohort` vào `WS_DANH_TU`.
- **Hai thẻ XEM chỉ đọc ở thanh bên (yêu cầu thêm của Truong, thuộc A14):** thẻ **06 "Thành viên {CLB}"** (chọn CLB; nhiều buổi ghi kèm buổi, sắp theo thứ tự ngày rồi tên; bảng STT | Mã | Họ tên | Lớp, dòng đầu "Đã xếp x/y chỗ") và thẻ **07 "Theo {lớp}"** (chọn lớp, gồm "Chưa có lớp"; STT | Mã | Họ tên rồi mỗi buổi một cột theo thứ tự NGÀY, ô trống ghi "—", em chưa có CLB nào tô đỏ; một buổi thì một cột CLB). Chưa chạy xếp: cả hai hiện "chưa có kết quả"; chưa có lớp nào: thẻ 07 hiện dòng nhắc. Chỉ kết quả xếp, không điểm, điểm quyết tâm, số bốc thăm hay diện trúng tuyển. Mã: `js/09_the_xem.js` (mới), `index.html`, `js/01_khung.js` (`TAB_LOADERS`), `js/07_ngon_ngu.js`, `js/08_khoi_dong.js`, `style.css`, `i18n.js` (36 khoá vi + en). Backend `api_bao_cao.py`: `get_thoi_khoa_bieu(search="", class_id=None)` (None = hành vi cũ; `""` = chưa có lớp; mỗi em có `class_id`) và `get_danh_sach_clb` có `class_id` mỗi thành viên.
- **Đổi ngôn ngữ vẽ lại chữ trong các ô thả xuống lớp ở thẻ 03** (dòng "— Chọn lớp —" của kiosk và của ô tạo em mới).
- **`export_theo_lop` lỗi giữa chừng thì xoá thư mục dở do chính lần xuất đó tạo** (không bao giờ thư mục có sẵn; trả `error_exporting_excel`).
- **DUYỆT NGOẠI LỆ TRÙNG KHÍT TỆP XUẤT (Truong duyệt 02/11/2026):** trang **"Theo lớp"** và cột **"Lớp"** LUÔN có trong Sổ kết quả và CSV kết quả (tệp tổng, `_theo_club`) kể cả khi không em nào có lớp (cột trống, trang chỉ có khối "Chưa có lớp"). Sổ kết quả từ 6 thành 7 trang. KHÔNG đổi: `match_results`, CSV thời khoá biểu, CSV từng buổi, CSV số bốc thăm, tệp tổng hợp, `export_hoc_sinh_csv`, báo cáo Word.
- **Vòng sửa sau soát chéo (Truong duyệt, mỗi mục một commit "A14 sửa Bx"):**
  - **B1** `export_theo_lop` trả thêm `ket_qua_cu` như `export_ket_qua`; mỗi tệp lớp và trang "Theo lớp" có dòng đỏ "CHÚ Ý: … có thể đã cũ" khi dữ liệu đã sửa sau lần chạy; giao diện hiện cảnh báo `xuat_kq_cu` như các nút xuất khác.
  - **B2** Kiosk: ô lớp tính là "chưa lưu" (dấu • Chưa lưu cạnh ô, bấm sang em khác / tạo em mới phải bấm hai lần, chặn "Xuất CSV em này"); đổi lại đúng giá trị đã lưu thì hết dấu.
  - **B3** Tên tệp lớp dài (300 ký tự) từng làm hỏng cả lần xuất (`File name too long`): cắt còn ~100 ký tự và ≤200 byte UTF-8 trước `_ten_chua_dung`, vẫn khử trùng; tên thật còn đủ trong tiêu đề khối.
  - **B4** Bỏ `api_xuat._khoa_lop_xuat`; dùng `_khoa_lop_tu_nhien` của phần A. Test chặn mọi hàm riêng trùng tên giữa các mixin; test lớp "10²" (xanh khi có bản sửa `isdecimal` của A).
  - **B5** Dòng nhắc thẻ 07 "chưa có lớp nào" gọi đúng tên thẻ 04 và mục Học sinh như thanh bên bằng chỗ giữ (vi + en), theo nhãn workspace.
  - **B6** `tests/_trinh_duyet.py` tìm Chromium ở `chromium-N/chrome-linux64/chrome` và tệp `chromium` chạy được (trước chỉ `chrome-linux/chrome`, nên test giao diện bị bỏ qua im lặng khi thiếu `RBDA_TEST_CHROMIUM`); hành vi không đổi khi đã đặt biến. Test mới `tests/test_trinh_duyet_tim.py` (7 ca).
  - **B9 (CI của PR #6)** `tests/test_a14_sua_sau_soat.py::test_a5_sao_luu_dung_mot_lan_truoc_buoc_di_tru_dau_tien` dựng CSDL cũ bằng `CREATE TABLE` tường minh, không phụ thuộc phiên bản SQLite: trước đó bỏ liên tiếp hai cột bằng `ALTER TABLE ... DROP COLUMN` trên bảng có chú thích `--` làm SQLite của CI (Linux và Windows, Python 3.11) báo "incomplete input". Mọi assert cũ giữ nguyên; thêm một assert bản sao lưu có dữ liệu (em S1), nên tệp sao lưu rỗng cũng làm test đỏ.
  - **B8 (kiểm cuối của điều phối viên)** Luật văn phong (`tests/test_van_phong_tu_nhien.py`): sửa CHỮ trong `i18n.js`, không sửa test. Bỏ gạch ngang nối câu (dùng dấu chấm, dấu phẩy); lựa chọn rỗng viết "Chọn lớp…" như "Chọn học sinh…" đã có; cột "STT" thành "Thứ tự" (HOA nhấn mạnh bị cấm); ô trống thẻ 07 ghi "—" trực tiếp trong JS như các bảng cũ (bỏ khoá `theolop_o_trong`). `tests/test_diem_chuan.py::test_tep_xuat_tat_tinh_nang_giong_het_truoc` so tên bảy trang tường minh (có "Theo lớp") thay cho `== 6`, giữ ý "Điểm chuẩn" không có khi tắt.
  - **B7** Tài liệu: mục này, `js/_danh_sach.txt` thêm `09_the_xem`, bản ghi bàn giao.
- **Test mới (số ca thật):** `tests/test_a14_lop_xuat.py` (23 ca), `tests/test_a14_the_xem.py` (8 ca, backend + thứ tự tệp JS), `tests/test_giao_dien_a14_lop.py` (24 ca, Chromium), `tests/test_trinh_duyet_tim.py` (7 ca).
- **Test cũ sửa có chủ đích (trang mới luôn có):** `tests/test_so_excel_de_dung.py` (`CAC_TRANG`), `tests/test_ws_nhan.py` (3 ca danh sách tên trang), `tests/test_ws_so_nhap_giao_dien.py` (tiêu đề Sổ mẫu có cột Lớp sau Họ tên; thay đổi đã duyệt của phần A, test trình duyệt nên A chưa chạy), `tests/test_giao_dien_upload.py` (sửa ô theo vị trí D3/E4 thành E3/F4 vì Sổ ví dụ tĩnh có cột Lớp sau Họ tên: NV1 sang cột E, điểm sang F; thay đổi đã duyệt của phần A, mục C2).

## 2026-11-01 — A13.13 (phần tiếp theo) CSDL demo thể hiện điểm quyết tâm + vá đường dẫn cứng

- **`du_lieu_test/tao_db_demo.py`:** mặc định dựng CSDL demo với Wharton BẬT (không ghi `wharton: false`), nạp `SO_NHAP_DQT_120HS_HOP_LE.xlsx` qua `import_so_nhap` (chọn bản 120HS vì giữ nguyên nguyện vọng và điểm thi của `SO_NHAP_MAU_120HS_3BUOI.xlsx`, chỉ thêm điểm quyết tâm MÔ PHỎNG; nhỏ, demo nhanh). Vẫn dừng trước khi chạy phân bổ. Cờ mới `--tat-wharton` dựng y như trước (TEST_01..03, `wharton: false`); cờ `--ra` chọn tệp đầu ra (mặc định giữ chỗ cũ). Đã so với bản dựng ở `cee2940`: 14/15 bảng trùng khít từng dòng, chỉ `workspace_settings` khác (có khoá `wharton=false`) — đúng dự kiến.
- **`du_lieu_test/app_DEMO_da_cham_diem.db`:** commit bản dựng mới (Wharton bật; 3 cảnh báo mức thường `health_oversubscribed_buoi`, 0 nghiêm trọng).
- **Tài liệu đổi lệnh sang `--tat-wharton` (để số cũ tái lập):** `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`, `poster/chup_giao_dien.py` (ảnh poster đứng cạnh số đã công bố nên dựng bản cũ vào thư mục tạm). Lời hướng dẫn cập nhật: `du_lieu_test/README.md`, `TAI_LIEU_DU_LIEU.md`, `poster/DU_LIEU_POSTER.md`, `BAN_GIAO.md`. Không sửa con số nào.
- **`du_lieu_test/do_do_dai_nguyen_vong.py`:** bỏ đường dẫn cứng `/home/user/truong/rbda-kiosk`, tính từ `__file__`; ghi bước chuẩn bị dữ liệu vào docstring (`bo_sach/` có sẵn trong kho, sinh lại bằng `bo_sach/tao_bo_sach.py`). Đầu ra trùng khít bản `cee2940` (đã vá tạm đường dẫn trong worktree).
- **Test:** mới `tests/test_db_demo_wharton.py` (6 ca: bật/tắt, chạy trên bản sao, `luat_xep.wharton`, trùng khít `match_results` seed 42, không còn `/home/user/truong`); `tests/test_a13_13_kiem_nhan.py` thêm `tao_db_demo.py` vào `NGOAI_LE_F1`; `tests/test_rang_buoc_csdl.py` tắt Wharton tường minh trong `_nap_nhieu_buoi` (3 test này đỏ sẵn từ nhánh cha vì dữ liệu CSV không có điểm quyết tâm).

## 2026-11-01 — A13.13 Điểm quyết tâm (Wharton) BẬT mặc định cho workspace trường học

**NGOẠI LỆ BẤT BIẾN 1 (đã duyệt).** Bất biến 1 ("cấu hình mặc định cho kết quả trùng khít với trước khi sửa") bị phá có chủ đích, theo quyết định rõ ràng của Truong. Các bất biến 2–8 vẫn giữ. Tắt RÕ RÀNG (`wharton: false`) thì kết quả, dấu vân tay và `run_history.luat_xep` trùng khít bản trước (đã chạy lại `do_anh_huong_seed.py` và `bao_cao_phan_bo.py`, so với bản gốc: đầu ra giống hệt).

- **Mã:** `cau_hinh_ws.py` — `MAC_DINH_TRUONG_HOC["rules"]["wharton"] = True`. Tổ hợp không bật được (`priority = "tier"` hoặc `score_scope = "per_person"`) mà người dùng KHÔNG ghi rõ `wharton` thì tự tắt (`_chuan_hoa`, và `tron_len` khi cập nhật); ghi rõ `wharton: true` với tổ hợp sai vẫn báo lỗi như cũ.
- **Giữ nguyên có chủ ý:** `rbda_priority_pipeline.LUAT_XEP_MAC_DINH["wharton"] = False`. Đây là mặc định ở tầng thuật toán thuần (gọi `run_full_pipeline`, `luat_xep_de_ghi`… không kèm cấu hình workspace) nên số liệu cũ vẫn tái lập; mặc định BẬT chỉ nằm ở cấu hình workspace.
- **Thông báo:** `wharton_ho_so_chua_hop_le` (`i18n_errors.py` → `tao_i18n_js.py`) nay chỉ cách khắc phục: điền đủ điểm quyết tâm, hoặc tắt "Dùng điểm quyết tâm" trong cấu hình workspace.
- **Tài liệu:** `HUONG_DAN_SU_DUNG.md` (mục "Bật ở đâu"), `mau_csv/HUONG_DAN_SO_NHAP.md`, hai chú thích trong `api_nhap.py`, `rbda_priority_pipeline.py`.
- **Công cụ:** `.claude/skills/soat-ma/scripts/kiem_nhanh.py` (kiểm `trung_khit`) tắt Wharton rõ ràng cho cả hai bản so sánh; không thì kiểm này lặng lẽ so hai kết quả "bị chặn" với nhau. 15 script trong `du_lieu_test/` (và `stress/_chung.py`, `stress/s8_bao_mat.py`, `bo_thu_workspace/tao_bo_workspace.py`) truyền `wharton: false` tường minh để tái lập số liệu cũ (quy tắc 4).

**Ảnh hưởng tới workspace cũ**
- Workspace đã lưu từ phiên bản có khoá `wharton` (A13.2 trở đi) ghi rõ `wharton: false` nên KHÔNG đổi.
- Cấu hình lưu TRƯỚC khi có khoá `wharton`, CSDL chưa có hàng `workspace_settings` (kể cả `app.db` cũ được di trú), và mẫu dựng sẵn "Trường học" nay ĐỌC THÀNH BẬT. Không viết di trú (đúng yêu cầu gốc).
- Hệ quả: dữ liệu mà một quỹ có từ hai CLB trở lên và chưa có điểm quyết tâm bị chặn khi chạy (`wharton_ho_so_chua_hop_le` + `wharton_chua_dung_het`); quỹ chỉ có một CLB được tự điền 100 trong bộ nhớ (quyết định "cách A"). Muốn chạy như cũ: tắt "Dùng điểm quyết tâm" trong cấu hình workspace. Không nới luật kiểm Wharton.
- `run_history.luat_xep` và dấu vân tay của workspace mặc định đổi (có khoá `wharton: true`): kết quả đã chạy trước đó của workspace đọc thành bật sẽ báo "đã cũ".
- Sổ mẫu `mau_csv/SO_NHAP_CLB.xlsx` và hai sổ `vi_du_*` nạp với mặc định mới: các sổ `vi_du_*` chưa điền cột Điểm quyết tâm nên bị chặn khi chạy; tắt rõ ràng thì nạp và chạy trùng khít bộ ba CSV (seed 1, 7, 42).

**Nhóm B (tệp mẫu / ví dụ giao người dùng) — Truong chốt hướng (c), làm xong:**
- **Bộ ví dụ THÊM điểm quyết tâm MÔ PHỎNG hợp lệ** (mỗi quỹ mỗi buổi đủ 100), bằng script có seed cố định `du_lieu_test/them_diem_quyet_tam_vao_mau.py` (không gõ tay; chạy lại ra đúng cùng nội dung): `du_lieu_test/vi_du_huong_dan` (VIDU_03 `.csv`/`.xlsx`, `SO_NHAP_VIDU.xlsx`), `mau_csv/vi_du_day_du`, `mau_csv/vi_du_ca_tuan` (bộ ba CSV + `SO_NHAP_CLB_vi_du.xlsx`), `mau_csv/08_nguyen_vong_nhieu_buoi.csv`. Hợp đồng cột CSV không đổi (chỉ thêm `wp_k` / `<buổi>_wp_k` mà bộ nhập đã hỗ trợ). `mau_csv/tao_so_nhap.py` đọc cột `wp` từ CSV để dựng sổ. Test giữ nguyên assert, chỉ đổi dữ liệu. Kết quả của `vi_du_huong_dan` và `08` không đổi. Riêng `vi_du_day_du`: với điểm quyết tâm, HS024 (mỗi buổi khai 2 CLB không thi, nên ≤ 75 điểm) luôn thua các em chỉ khai một CLB (100 điểm) — bỏ nguyện vọng thứ Hai `clb_bongro` của HS024 trong `tao_bo_mau.py` để đúng một em trắng tay như `GIAI_THICH.md` kể; 23 / 24 em và 1,88 CLB/em giữ nguyên. **Truong đã duyệt 01/11/2026** (thay đổi HS024, mã băm mới của `test_ket_qua_khong_doi[vi_du_day_du]`, và 4 ca test chỉnh theo bộ ví dụ có điểm quyết tâm). Tài liệu cập nhật: `GIAI_THICH.md` (hai bộ), `README.md` của `vi_du_huong_dan`, `HUONG_DAN_SU_DUNG.md`, `TAI_LIEU_DU_LIEU.md`; ghi rõ là dữ liệu MÔ PHỎNG.
- **`bo_sach` (dữ liệu của báo cáo đề tài): GIỮ NGUYÊN dữ liệu.** Mọi nơi chạy bộ này tắt Wharton RÕ RÀNG (`test_bo_sach`, phần `bo_sach` của `test_diem_bat_thuong`, các script `du_lieu_test/`) để số liệu đã công bố tái lập được. Không sửa con số nào trong báo cáo.
- **Skill `sinh-du-lieu-clb`:** mặc định sinh KÈM điểm quyết tâm MÔ PHỎNG hợp lệ (`--diem-quyet-tam hop_le`); thêm cờ `--khong-diem-quyet-tam` để tắt (đầu ra như trước). `SKILL.md` và `TAI_LIEU_DU_LIEU.md` cập nhật.
- **Skill `tao-workspace-tu-raw`** (dữ liệu THẬT, không bịa điểm): spec không ghi `rules.wharton` thì workspace ghi `wharton: false` và báo "Dữ liệu không có điểm quyết tâm nên đã tắt tính năng này" (CLI, `ghi_chu` trong `--json`, `BAO_CAO_SOAT.md`). **Skill `xu-li-raw-forms`** và bộ chuyển Forms mẫu `mau_forms_thi_clb`: sổ không chứa được cấu hình nên báo trong báo cáo/CLI "cần TẮT 'Dùng điểm quyết tâm' trước khi nạp". Test đi theo nhánh này.
- **`du_lieu_test/NHAP_TAY.md`:** thêm Bước 3 "chia điểm quyết tâm" (số MÔ PHỎNG do `random.Random(112026105)` sinh, test canh bảng khớp tài liệu); đánh số lại các bước sau. Bảng kết quả không đổi (mọi em đã thi mọi CLB mình ghi; không có cặp bằng điểm thi) — test canh cả hai cấu hình.
- **CSDL demo:** đã gộp `claude/demo-wharton-va-duong-dan` (merge); `test_csdl_demo_that_duoc_nang_len` xanh với CSDL demo mới.
- **Để sau:** biểu mẫu Google Forms (`tao-google-form-clb`) chưa đổi; việc để sau là thêm phần thu điểm quyết tâm vào biểu mẫu.

**Đính chính phạm vi chạy test (01/11/2026, sau CI):** lần báo "0 đỏ" trước đó chỉ đúng trên danh sách test chọn bằng grep (`wharton|MAC_DINH_TRUONG_HOC|luat_xep|dau_van_tay|trung_khit`); danh sách đó bỏ sót phần lớn các tệp chạy pipeline với dữ liệu không có điểm quyết tâm, nên CI toàn bộ báo thêm 241 ca đỏ (40 tệp). Sửa nhóm A (fixture nội bộ, không phải mẫu giao người dùng): 27 tệp được thêm fixture `api` cục bộ gọi `tat_wharton` (KHÔNG autouse toàn cục, không nới assert, không skip): `test_so_excel_de_dung`, `test_export_ket_qua`, `test_du_lieu_ket_qua`, `test_xoa_du_lieu`, `test_nghich_canh`, `test_api`, `test_bo_kich_tran`, `test_diem_theo_o_tick`, `test_bo_toan_tuan`, `test_xuat_khoa_chua_co_ket_qua`, `test_xuat_du_lieu`, `test_thi_qua_tran_sau_doi_buoi`, `test_nap_diem_tu_file`, `test_diem_bat_thuong`, `test_khoa_hat_giong`, `test_data_durability`, `test_rang_buoc_csdl`, `test_a13_9_stress`, `test_ket_qua_khong_doi` và 9 tệp `test_giao_dien_*` (`chay`, `chon_buoi`, `khoa_hat_giong`, `tom_tat_ket_qua`, `thu_gon_ket_qua`, `danh_sach_clb`, `a13_11_csdl_ban`, `a13_12_tkb`). Thêm một lỗi thật do chính A13.13 gây ra: câu tiếng Việt của `wharton_ho_so_chua_hop_le` có từ "workspace" (bị `test_giao_dien_tieng_viet_sach` bắt) — đổi thành "không gian làm việc". Nhóm B (tệp mẫu / ví dụ giao người dùng, KHÔNG che bằng `tat_wharton`; chờ Truong quyết) còn đỏ có chủ ý; danh sách trong tệp bàn giao `docs/phien/claude__wharton-mac-dinh-bat.md`.

**Kiểm nhận độc lập (phiên cha thiết kế):** `tests/test_a13_13_kiem_nhan.py` (45 ca, nhóm A–F) và `tests/test_giao_dien_a13_13_kiem_nhan.py` (2 ca, nhóm G): đều qua, không phải sửa mã. So hai script đo với bản gốc `cee2940` bằng `git worktree`: `do_anh_huong_seed.py --so-seed 5` và `bao_cao_phan_bo.py` cho đầu ra giống hệt.

**Test** (`tests/test_wharton_mac_dinh_bat.py`, 16 ca mới; helper `tests/_wharton.py::tat_wharton`, KHÔNG autouse). Test cũ sửa, không xoá, không skip: (a) đổi sang mặc định mới + giữ khẳng định cũ dưới dạng ca `wharton: false` tường minh: `test_wharton_luat`, `test_ws_cau_hinh`, `test_ws_api`, `test_ws_sua_loi_2`, `test_ws_so_nhap`, `test_ws_nhan`, `test_so_mau_co_cot_quyet_tam`, `test_wharton_so_nhap`; (b) truyền `wharton: false` ở fixture / đầu test (hành vi cũ làm nền): `test_nhieu_buoi`, `test_wharton_pipeline`, `test_thay_doi_ket_qua`, `test_ws_luat`, `test_ws_sua_loi_3`, `test_diem_chuan`, `test_wharton_{quan_ly,hang_loat,kiosk,khoa,nhap,suc_khoe,dau_cuoi}`, `test_so_nhap_hai_hang`.

## 2026-11-01 — Công cụ phiên (ngoài sổ): sửa test tài liệu sau khi rút gọn CLAUDE.md

- `tests/test_a13_12_tai_lieu.py::_doan_ban_do` đọc "Bản đồ mã" ở `docs/ke_hoach/CLAUDE_CHI_TIET.md` (bảng đã chuyển nguyên văn khỏi `CLAUDE.md` ở `5fd624b`). Trước đó hai ca `test_ban_do_ma_co_nhom_ham_diem_quyet_tam`, `test_ban_do_ma_so_tep_test_la_so_that` đỏ trên `cee2940`. Không đổi mã sản phẩm. `kiem_nhanh.py --co-so cee2940`: 7/7 ĐẠT.
- `TAI_LIEU_DU_LIEU.md` mục 4 nay tả `.claude/settings.json` và hook bàn giao (thêm ở `5fd624b`); `tests/test_tai_lieu_du_lieu.py`: `VANG_MAT_CO_Y` thành tập rỗng. Trước đó `test_nhung_tep_tai_lieu_noi_khong_co_thi_van_khong_co` đỏ trên nhánh này và mọi nhánh tách từ nó.
- Lưu ý khi gộp nhánh `claude/wharton-mac-dinh-bat`: nhánh đó thêm tệp test, nên phải cập nhật số tệp ở dòng `tests/` của bản đồ mã trong `CLAUDE_CHI_TIET.md`.

## 2026-10-28 — A13.12 Sửa Tầng 4 của đợt soát A13 và toàn bộ mục chặn / nên sửa của đợt soát hệ thống nhập

Theo yêu cầu của Truong qua phiên điều phối. Mô phỏng. Tắt Điểm quyết tâm: kết quả trùng khít `e08af78`. Mỗi mục có test đỏ trước, xanh sau (mục chỉ thêm test: ghi rõ). Bảng xử lý từng mục (commit hoặc "không sửa – lý do"): `docs/ke_hoach/BAO_CAO_SOAT_NHAP.md` (cột cuối mỗi bảng) và mục "Vòng sửa A13.12" cuối `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md`.

**Phần 1 — Tầng 4 (`BAO_CAO_SOAT_MA_A13.md`, Truong đã chốt)**
- **4.5 (`f1292c8`):** `tests/test_wharton_khoa.py::test_loi_o_buoc_nhat_ky_khoa_rollback_ca_giao_dich` làm `_ghi_nhat_ky_wharton("khoa")` ném lỗi SAU khi dòng khoá đã chèn và khẳng định `match_results`, `run_history`, `wharton_lock`, `stb_lock`, nhật ký nguyên vẹn; gây hỏng `rollback()` → `commit()` thì tệp chủ đề nay đỏ. `tests/test_wharton.py::TestKiemHoSo::test_bien_ngan_sach_99_100_101` bắt đột biến `> ngan_sach + 1`. Chỉ thêm test, không đổi mã sản phẩm.
- **4.1 (`047b2cb`):** `CLAUDE.md` bản đồ mã định vị theo TÊN HÀM, không ghi số dòng; thêm hàng "Điểm quyết tâm"; số tệp test thật; `DOI_CHIEU_KHO_MA.md` mục "Cập nhật 28/10/2026". Test `tests/test_a13_12_tai_lieu.py` canh: không số dòng, mọi tên trong dấu huyền đều tồn tại, số tệp test đúng.
- **4.2 (`1ab2174`):** `xu-li-raw-forms/SKILL.md` tả đúng bố cục (sổ mẫu có cột Điểm quyết tâm, sổ của kỹ năng không có); `HUONG_DAN_SU_DUNG.md` "điểm của em khác".
- **4.3 (`56cc766`, `9a19068`):** xoá khoá i18n chết `dc_cot_buoi` (`dc_tooltip_so` đã xoá từ A13.10); test `tests/test_i18n_khoa_dc_khong_chet.py`.
- **Hai chuỗi đổi ngôn ngữ (`fallback_phu_buoi`, `btn_remove_ranked`) (`8021916`):** KHÔNG tái hiện được ở mã hiện tại (đã đúng từ A13.7: `js/07_ngon_ngu.js` gọi lại `renderRankingList()`); chỉ thêm `tests/test_giao_dien_a13_12_ngon_ngu.py` (bỏ dòng đó thì cả hai ca đỏ).

**Phần 2 — `BAO_CAO_SOAT_NHAP.md` (39 mục: 1 chặn, 21 nên sửa, 17 nhỏ)**
- **1.1 CHẶN (`173e017`):** F5 ở chế độ trình duyệt không còn tắt máy chủ. `/__closed__` chỉ đánh dấu; watchdog (kiểm mỗi giây) tắt khi ≥ 4,5 s sau đó không có ping hay kết nối sống mới (`_CHO_SAU_BAO_DONG_SECONDS`). Test: `tests/test_giao_dien_a13_12_f5.py` (Chromium, F5 ×3 rồi gọi API; đỏ trước với `ERR_CONNECTION_REFUSED`), `tests/test_a13_12_browser_host.py`. Chưa thử trên cửa sổ `--app` Edge/Chrome thật.
- **1.2 (`173e017`):** mọi lỗi HTTP trả `errors = [{code, params}]`; 4 mã mới `http_bi_tu_choi`, `http_khong_co_dich`, `http_khong_co_ham`, `http_than_qua_lon`.
- **1.4, 1.5 (`c8f986e`):** cột phụ bên phải nhóm cuối của Sổ hai hàng không làm cả sổ bị từ chối (nhóm cuối rộng bằng nhóm liền trước; cột lạ TRONG nhóm vẫn là lỗi); `re.fullmatch(r"[0-9]+", …)` cho ô điểm quyết tâm khi ghi sổ.
- **Backend (`a6738ca`):** 1.6/3.3 `page` vượt tổng được kẹp về trang cuối ở `list_students_admin`, `list_wharton_admin`, `get_wharton_nhat_ky`; 3.1 `create_student_if_missing` bỏ khoảng trắng đầu / cuối, từ chối mã rỗng (mã mới `student_id_required`); 3.2 `delete_club` sao lưu rồi xoá và trả `n_scores_removed`, `n_tests_removed`, `backup_path` (Truong chọn); 4.1 `delete_workspace` kiểm "đang mở" trong khoá; 4.2 xoá hết workspace thì dựng lại "Trường học"; 4.3/4.4 workspace `priority = tier`: `submit_person_scores`, `get_club_applicants_for_scoring`, `get_scoring_overview` trả `scoring_not_per_slot` (Truong chọn: không chắn `per_person`); 4.5 mã không băm được thì bỏ qua mục đó; 4.6 `export_workspace` lùi về thư mục gốc chương trình; 2.7 bộ nhớ xuất nhận keyword; 2.8 bỏ trần 1.000 bản của `duong_dan_khong_de`; 2.9 số âm dạng chuỗi (`-1,5`) không thêm dấu nháy; 1.10 `api_nhap._doc_diem` / `_o_excel_thanh_chu` là CHÍNH `so_nhap.doc_diem` / `o_thanh_chu`. Test: `tests/test_a13_12_backend.py` (38 ca).
- **Kiosk (`15eabd9`):** 2.2 ô tự điền 100 (ô bị khoá) không gửi lên khi Lưu; 1.8/2.4 ô tự điền không còn báo "Chưa lưu" giả; 1.7/2.3 mốc "đã lưu" và dòng thông báo theo bản chụp LÚC BẤM; 1.9/2.6 xoá em đang mở dọn sạch Bước 3, xếp hạng, mốc, hẹn giờ; 2.5 chọn em khác xoá dòng "Đã lưu" của em trước; đồng bộ trang. **Bốn test cũ sửa có duyệt (Truong chọn A):** `tests/test_giao_dien_wharton.py::test_luu_thieu_40_…`, `test_o_chua_luu_hien_dau_chua_luu_…`, `test_bo_clb_o_buoc_2_…`, `test_nhieu_buoi_moi_buoi_…` (sau Lưu, CSDL không còn dòng 100 tự điền; ô tự điền không hiện "Chưa lưu"). Test mới: `tests/test_giao_dien_a13_12_nhap.py` (7 ca).
- **Quản lý và workspace (`dd94e50`):** 3.2 toast xoá CLB nêu số điểm / ô tick đã xoá và tên tệp sao lưu; 3.4 sau thao tác đổi dữ liệu (xoá một, phóng, mở khoá…) màn sửa không điền lại chữ cũ (`loadAdminWharton(giuTrang, giuChu)`); 3.6 tìm TKB không khớp giữ ô tìm; 3.9 chi tiết điểm chuẩn dùng `callApiMoiNhat`; 3.10 lưu / xoá CLB làm mới bảng tải theo buổi; 4.8 tạo workspace mà mở lỗi thì bấm "Tạo" lại chỉ thử mở lại; 4.10 wizard chặn nhãn bắt đầu bằng `= + - @` (khoá mới `ws_v_cong_thuc`). Test: `tests/test_giao_dien_a13_12_ql_diem_chuan.py`, `_ql_wharton.py`, `_tkb.py`, `_ws.py`.
- **Không sửa:** 3.8 (đo 800 × 20: mỗi hàm đọc ≤ 0,05 s), 4.7 (tên workspace không vào ô Excel nào; chặn sẽ từ chối tên hợp lệ), 4.9 (cần giao diện mới, ngoài ít mã). **Đã sửa trước đó:** 1.3 (A13.9 `1dac117`), 2.1 (A13.8 `04740a5`), 3.5 (A13.8 `a710a31`), 3.7 (A13.8 `d4dc297`).
- **Mã lỗi / khoá mới:** `http_bi_tu_choi`, `http_khong_co_dich`, `http_khong_co_ham`, `http_than_qua_lon`, `student_id_required` (thêm vào `MA_MOI_SAU_ANH_CHUP`, sinh lại `i18n_loi.js`); khoá giao diện `toast_club_deleted_removed`, `ws_v_cong_thuc`.
- **CI Windows (`e1f6d56`) và `ws_v_cong_thuc` (`2f313ec`):** `chan_doan` chuẩn hoá `\r\n` trước khi so mục trùng; `sinh_du_lieu_diem_quyet_tam.py` và `kiem_nhanh.py` reconfigure stdout/stderr utf-8, `kiem_nhanh` thêm `errors="replace"`; chuỗi `ws_v_cong_thuc` không còn " - " đứng riêng. Test giả lập: `tests/test_a13_12_windows.py` (CRLF, cp1252). Chưa có Windows thật để xác nhận.
- **Kiểm (28/10/2026):** toàn bộ test có Chromium, `-rs`, phủ **92,98 %**: 3.051 qua, 1 bỏ qua (cần người dùng thường trên POSIX), 2 ca đỏ ở `tests/test_i18n_sync.py` do lượt chạy trùng lúc sửa `i18n_errors.py` (chưa sinh lại `i18n_loi.js`); chạy lại tệp đó sau khi sinh lại: 9 qua. Lượt chạy này có trước ba commit cuối (`4d02c6d`, `2f313ec`, `e1f6d56`); các tệp test liên quan đã chạy lại riêng: 135 qua (`test_a13_9_stress`, `test_du_lieu_mau_diem_quyet_tam`, `test_skill_soat_ma`, `test_a13_12_windows`) và 25 qua (`test_van_phong_tu_nhien`, `test_i18n_sync`, `test_giao_dien_a13_12_ws`). `kiem_nhanh.py --co-so e08af78`: **7/7**, trùng khít 15 ca. `ruff check .` sạch.


## 2026-10-28 — A13.11 Sửa 4 phát hiện N1–N4 của đợt stress test (trên đỉnh A13.9)

Theo danh sách Truong chọn trong phiên điều phối (`docs/ke_hoach/VAN_DE_STRESS_TEST.md`, N1–N4). Mô phỏng. Test mới: `tests/test_a13_11_stress.py`, `tests/test_giao_dien_a13_11_csdl_ban.py` (mỗi mục đỏ trước, xanh sau). Không đụng màn Điểm chuẩn (phiên A13.10).
- **N1 (`902cb6b`, `02c3089`):** đường xuất tuyệt đối là THƯ MỤC có sẵn → lỗi mới `xuat_duong_la_thu_muc` (`LoiDuongXuat` ở `api_workspace.py`; mọi hàm xuất và `export_workspace` trả lỗi có tên, không đẻ tệp `x (2)` cạnh thư mục). Phản hồi chỉ mang TÊN thư mục, không lộ đường dẫn máy (s8 T7 sạch).
- **N2 (`442725f`):** nạp Sổ / CSV ghi MỘT dòng `wharton_nhat_ky` (`nguon = nap_tep`, `hanh_dong = luu_hang_loat`, `student_id` rỗng, `moi_json = {so_em_doi, so_dong_nap}`) thay vì một dòng mỗi em; không em nào đổi điểm thì không ghi gì; vẫn chỉ ghi thêm, trong cùng giao dịch. Giao diện thẻ Quản lý hiện dòng tóm tắt (`wh_nk_luu_hang_loat`, `wh_nk_tom_tat`). s6 phần B (100 vòng nạp-xoá-nạp, 800 em): `app.db` 16,7 → **1,66 MB**, sao lưu 158 → **16,1 MB**.
- **N3 (`49c7319`):** `_BUSY_TIMEOUT_MS` 15.000 → 3.000; `err()` đổi MỌI lỗi có `detail` là "database is locked / busy" thành `csdl_dang_ban` (một chỗ, phủ hàng trăm khối `except`); `get_data_health_report` báo ngay; `run_pipeline` dừng với `csdl_dang_ban` khi bước sao lưu gặp CSDL bận (không chạy tiếp thiếu lưới an toàn; lỗi sao lưu khác vẫn không chặn); giao diện: "Kiểm tra dữ liệu" và "Chạy sắp xếp" nói "CSDL đang bận" thay vì "chưa hợp lệ" / "không thành công" (`coLoiCsdlBan` ở `js/00_nen.js`); ô cảnh báo dữ liệu và thống kê tổng quan vốn đã hiện đúng. s3 phép D: `list_students_admin` 15,0 → **3,0 s**, `reset_data` 15,0 → **3,0 s**, `run_pipeline` 17,6 → **3,0 s**, `submit_preferences` / `import_so_nhap` 15,0 → 2,5 s; tất cả `csdl_dang_ban`, CSDL không đổi, mở khoá xong chạy lại bình thường.
- **N4 (`2fb9680`):** NGUYÊN NHÂN (đo bằng `server`/`browser` tách tiến trình): KHÔNG phải vẽ DOM và không phải một lời gọi chậm — từng hàm đọc chỉ 10 – 50 ms khi chạy riêng, nhưng thẻ Kết quả bắn 13 lời gọi đọc cùng lúc và chúng tranh GIL (mỗi bước `sqlite3` nhả rồi giành lại GIL), nên trong máy chủ `get_match_results` mất 3,1 s, `get_em_chua_co_cho` 3,6 s. Sửa: `PipelineAPI._xep_hang_doc` xếp hàng mọi hàm đọc (`get_*`, `list_*`, `check_*`, `xem_truoc_*`) bằng một RLock `_cong_doc`; ghi vẫn dùng `_khoa_ghi`, không bị chặn. 5.000 × 100: lần đầu mở thẻ Kết quả **13,6 s → 1,06 s**; trang chậm nhất của danh sách học sinh **6,5 s → 0,34 s** (không trang nào > 1 s). 800 × 20 không chậm đi (`--nhanh`: mở thẻ Kết quả lớn nhất 500 → 249 ms; mỗi trang trung vị 92 → 91 ms).
- **Test cũ sửa có duyệt (Truong chọn A, 28/10/2026), do N2:** `tests/test_wharton_nhat_ky.py::test_nap_tep_ghi_nguon_nap_tep` (chờ MỘT dòng `("nap_tep", "luu_hang_loat", None, None, {so_em_doi: 1, so_dong_nap: 1})`; nạp lại y nguyên vẫn không ghi thêm) và `tests/test_wharton_quan_ly_dau_cuoi.py::test_kich_ban_dau_cuoi` (một dòng `luu_hang_loat` thay 15 dòng `luu`, hai chỗ).
- **Lỗi xuất không lộ đường dẫn máy (Truong chọn, 28/10/2026):** `error_exporting_csv`, `error_exporting_excel`, `so_nhap_mau_loi` và `export_workspace` trước đây đưa `str(e)` (có tên tệp / đường dẫn máy) vào `detail`. Nay `detail` chỉ là kiểu lỗi + lý do của hệ điều hành (`FileNotFoundError: No such file or directory`); đường dẫn đầy đủ vào `loi_ung_dung.txt` (`XuatKetQuaMixin._chi_tiet_loi_xuat`). Test: `tests/test_a13_11_stress.py` (nhóm `n1b`, 9 ca).
- **Kiểm:** `kiem_nhanh.py` 7/7. Toàn bộ test có Chromium, `-rs`, phủ 92 %: 2.938 qua, 2 đỏ (hai ca trên), 1 bỏ qua (cần người dùng thường trên POSIX). `ruff check .` sạch.

## 2026-10-28 — A13.10 Nhãn "Xét điểm thi / Xét điểm quyết tâm" và thiết kế lại màn Điểm chuẩn

Theo yêu cầu của Truong (duyệt ba điểm: sửa bộ chọn test giao diện cũ; biểu đồ chỉ khối Điểm chuẩn tự đổi nền tối vì ứng dụng chưa có giao diện tối chung; EN dùng "commitment points" trong cả khối). Chỉ đổi cách hiện; API `get_diem_chuan` / `get_diem_chuan_clb`, schema, hợp đồng cột CSV, thuật toán và kết quả xếp KHÔNG đổi. Mô phỏng.
- **1. Nhãn hiển thị:** "Tầng 1" thành "Xét điểm thi" / "Exam-based", "Tầng 2" thành "Xét điểm quyết tâm" / "Commitment points" ở giao diện (`i18n.js`, khoá `dc_*`, VI và EN), tệp xuất Excel (`api_xuat.py`: tiêu đề cột và mô tả trang Điểm chuẩn) và hướng dẫn (`HUONG_DAN_SU_DUNG.md`, `README.md`, `TAI_LIEU_DU_LIEU.md`, `GIAI_THICH_DE_HIEU.html`, `BAO_CAO_CACH_CHAY.html`, `mau_csv/vi_du_day_du/GIAI_THICH.md`). Nơi cần danh từ thì ghi "nhóm xét điểm thi / nhóm xét điểm quyết tâm". Mã, biến, cột, mã lỗi giữ `tier`, `tang1`, `tang2`. Chưa đổi: `poster/`, chú thích trong `.py`, `BAN_GIAO.md` và các tài liệu kế hoạch nội bộ.
- **2a. Bảng tổng** (`js/05_quan_ly.js`, `veTongQuanDiemChuan`): hai cột điểm chuẩn riêng, mỗi ô một thanh SVG (thang điểm thi 10 / 100 tự chọn theo dữ liệu, điểm quyết tâm 0 đến 100); bỏ dòng chữ nhỏ dưới tên CLB (mã `dc-phu`).
- **2b. Đơn và chỗ (làm lại sau góp ý của Truong: bản đầu khó hiểu):** cột "Đơn và chỗ" có nhãn mức bằng chữ (`dc-chip`: Đủ chỗ / Đông / Rất đông, `data-muc` = `thap` / `vua` / `cao`, ngưỡng đơn / chỗ 1 và 2), "N đơn · M chỗ" có đơn vị, và một thanh chung một thang cho cả bảng gồm ba phần: đơn nằm trong số chỗ (xám đậm), đơn vượt chỗ (màu theo mức), chỗ còn trống (khung rỗng); chú giải ba phần và một câu giải thích ba mức. Bỏ thanh tối đa 5 lần chỗ có vạch mốc và các khoá `dc_ti_le_thap/vua/cao`; khoá mới `dc_muc_*`, `dc_don_chu`, `dc_bar_*`, `dc_muc_giai_thich`. Thay chấm đỏ.
- **2c. Chi tiết một CLB:** histogram và dải chấm cũ gộp thành MỘT SVG beeswarm (`veChiTietDiemChuan`, `svg[data-bieu-do=chi-tiet]`): chấm cùng điểm xếp cột không chồng nhau, vạch chuẩn ghi số, vùng nhạt bên phải vạch là vùng được nhận, chấm đặc xanh được nhận / chấm rỗng xám không được nhận, chú giải ba mục, tooltip và bảng chữ ẩn giữ nguyên. Xoá `veCotPhanBoQuyetTam`, `veDaiChamQuyetTam`, `dcCotTronTren` và khoá i18n không còn dùng (`dc_cot_chuan`, `dc_nong`, `dc_cot_tieu_de`, `dc_truc_y`, `dc_tooltip_khoang`, `dc_tooltip_so`); khoá mới `dc_ti_le_*`.
- **Sáng / tối, chuyển động** (`style.css`): màu qua biến; `prefers-color-scheme: dark` (và `[data-theme=dark]`) chỉ đổi khối Điểm chuẩn sang nền tối; hiệu ứng chấm vào dần chỉ chạy khi `prefers-reduced-motion: no-preference`. Không thư viện ngoài.
- **Test mới:** `tests/test_giao_dien_a13_10_nhan.py` (5 ca: nhãn VI / EN, khoá `dc_*`, tài liệu) và `tests/test_giao_dien_a13_10_diem_chuan.py` (9 ca: hai cột, bỏ chữ phụ, nhãn mức / đơn vị / thang chung của cột Đơn và chỗ, một SVG, chấm không chồng, chú giải và tooltip, reduced-motion, chế độ tối, EN). **Test cũ sửa có duyệt:** `tests/test_giao_dien_diem_chuan.py` đổi bộ chọn (`svg[data-bieu-do=cot|cham]`, `#dcCot`, `#dcCham` thành `svg[data-bieu-do=chi-tiet]`, `#dcBieuDo`; hai test (a), (b) gộp một); `tests/test_diem_chuan.py` đổi chữ tiêu đề cột Excel.
- **EN: một tên "commitment points" cho toàn giao diện (Truong yêu cầu, chỉ chữ giao diện):** mọi "preference point(s)" trong `i18n.js` (18 chỗ) và thông báo lỗi EN `i18n_errors.py` (24 chỗ, sinh lại `i18n_loi.js`) đổi thành "commitment point(s)" (tab Quản lý, bước 3 nhập tại chỗ, nút lưu / mở khoá / xoá, tên tính năng ở workspace, lỗi nhập). "Preference(s)" nghĩa là nguyện vọng giữ nguyên. Sổ nhập: `so_nhap.py` nhận thêm tên cột "commitment points" (vẫn nhận "preference points" cũ). Sáu test giao diện cũ đổi chữ EN mong đợi; test mới `test_en_moi_cho_deu_la_commitment_points_khong_con_preference_points`. Không đổi mã, schema, tài liệu.
- **Ảnh trước / sau:** `docs/anh/a13_10/{truoc,sau}_{vi,en}_{sang,toi}.png` từ `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`, seed 3, chụp bằng `docs/anh/a13_10/chup_anh.py`. Ảnh "trước" có "Tầng 1/2" vì chụp từ bản gốc; ứng dụng chưa có giao diện tối chung nên ảnh "tối" chỉ khác ở khối Điểm chuẩn.
- **Kiểm (28/10/2026):** toàn bộ test có Chromium, `-rfs`, phủ 92,57 %: 2.911 qua, 3 bỏ qua (numpy ×2, POSIX ×1), 4 ca đỏ ở `test_giao_dien_tro_nang.py` (WCAG đọc mã màu cuối cùng của từng biến trong `style.css`, nên bảng màu tối của khối Điểm chuẩn bị tính nhầm); đã sửa bằng cách đặt màu tối ở biến `--dcd-*` rồi gán qua `var()`, chạy lại các tệp đọc `style.css` (57 qua) và các tệp Điểm chuẩn (37 qua). `kiem_nhanh.py` (`--co-so 167be48`, trước A13.10): trước khi rebase 6/7 (12 lỗi `ruff`, tất cả trong `du_lieu_test/stress/*` của phiên stress test); sau `git pull --rebase` lên A13.11: **7/7**, trùng khít 15 ca; chạy lại 100 ca giao diện / điểm chuẩn / WCAG sau rebase, qua cả.

## 2026-10-28 — A13.9 Sửa 9 vấn đề từ đợt stress test

Theo danh sách Truong đã chốt (mục 1–9; #10 numpy không làm). Mô phỏng. Tắt Điểm quyết tâm: kết quả trùng khít `e08af78` (`kiem_nhanh.py --co-so e08af78`, 15 ca, 3 bộ × 5 seed). Test mới: `tests/test_a13_9_stress.py` (mỗi mục đỏ trước, xanh sau).
- **1. CSDL bận:** mã lỗi mới `csdl_dang_ban` (`CsdlBan`, con của `CauHinhHong`, nên mọi nơi đang dừng vẫn dừng; `loi_cau_hinh(e)` chọn mã). `connect_db(cho_khoa_ms=)`; `cau_hinh_ws.CHO_KHOA_DOC_CAU_HINH_MS = 2500`. Tệp: `rbda_priority_pipeline.py`, `cau_hinh_ws.py`, `api_workspace.py`, `api*.py`, `i18n_errors.py`, `i18n_loi.js`. Lưu ý: `run_pipeline` vẫn chờ tới 15 s ở bước sao lưu (cố ý: rút ngắn là bỏ qua sao lưu khi khoá ngắn).
- **2, 3, 5. `browser_host.py`:** `_Handler.timeout = 45`; `_token_khop` so token trên byte (token không ASCII ở tiêu đề / `?t=` → 403); `loi_ngoai_du_kien` chỉ trả tên kiểu ngoại lệ, thông điệp thật nằm ở `loi_ung_dung.txt`.
- **4. `chan_doan.py`:** `loi_ung_dung.txt` trần `TRAN_LOG_UNG_DUNG_BYTE` = 1.000.000, cắt xuống 75 % giữ phần cuối ở ranh giới mục; bỏ mục trùng hệt mục ngay trước (khác giờ). Log khởi động không đổi.
- **6. `api_xuat.py`:** `_duong_xuat` với đường tuyệt đối cũng đi qua `duong_dan_khong_de` (kể cả `kem_duoi`): `x (2).xlsx`. Áp cho mọi hàm xuất và `export_workspace`.
- **7. `workspace.py`:** `nhap_zip` — `TRAN_SO_TEP_ZIP = 1000`, `TRAN_GIAI_NEN_BYTE` hạ 500 → 200 MB, từ chối tên trùng (chuẩn hoá dấu phân cách, hoa/thường), kiểm NUL trên `orig_filename` (trước đây `zipfile` cắt tên nên kiểm NUL không bao giờ bắt được).
- **8. Sổ rỗng:** `so_nhap.py` bỏ lỗi `so_nhap_khong_co_clb`; `api_nhap.py` báo `so_nhap_canh_bao_khong_co_clb` / `so_nhap_canh_bao_khong_co_hs`, bỏ bước nạp CLB khi sổ không có CLB; `run_pipeline` sau đó chạy được.
- **9. Skill `sinh-du-lieu-clb`:** quá 20 CLB tự sinh "CLB Chuyên đề N"; ≤ 20 giữ đúng từng byte (băm 6 cấu hình so với `0f13771`).
- **Test cũ (Truong chọn 1A, 2A, 28/10/2026):** thêm 3 mã vào `MA_MOI_SAU_ANH_CHUP` (`tests/test_ws_nhan.py`); hai test sửa có duyệt — `test_nap_xuat_ca_hiem.py::test_khong_con_tep_cua_lan_xuat_truoc` gọi thẳng `_ghi_bo_csv` hai lần trên cùng đường (qua `export_csv` giờ ra `x (2).csv`, không còn ghi đè tại chỗ); `test_so_nhap.py::test_ma_trong_dung_lai_clb_cung_ten_va_bao_clb_ngoai_so` thêm một em vào sổ để không dính cảnh báo sổ rỗng.
- **Kiểm:** `kiem_nhanh.py` 7/7. Toàn bộ test có Chromium, `-rs`, phủ 93 %: 2.902 qua, 2 đỏ trước khi sửa hai test trên (chạy lại hai tệp đó: 95 qua), 1 bỏ qua (cần người dùng thường trên POSIX). `ruff check .` sạch. **Chưa làm:** chạy lại s3/s8 `--nhanh` và cột "Đã sửa ở commit" — `VAN_DE_STRESS_TEST.md`, `BAO_CAO_STRESS_TEST.md` và kịch bản s3/s8 chưa có trên nhánh (Truong chọn 4A: chờ đẩy lên rồi làm).

## 2026-10-28 — A13.8 Sửa 12 lỗi từ đợt soát A13

Theo danh sách Truong đã chốt (báo cáo `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md`, mục "Vòng sửa A13.8"). Mô phỏng. Tắt Điểm quyết tâm: kết quả, dấu vân tay, run_history trùng khít `e08af78` (`kiem_nhanh.py`: 15 ca, 3 bộ × 5 seed).
- **2.1 + 3.2:** khoá đang bật và em đã có điểm thì `submit_preferences` / `submit_test_selection` trả `wharton_da_khoa` (gửi lại đúng danh sách cũ vẫn ok); nạp CSV / Sổ nhập bỏ qua em đó, cảnh báo `csv_wharton_khoa_giu_nguyen`; kiosk vô hiệu hai nút lưu kèm ghi chú. Tệp: `api_quan_ly.py`, `api_nhap.py`, `js/04_nhap_tai_cho.js`, `index.html`, `i18n.js`, `i18n_errors.py`. Test: `test_a13_8_khoa_nguyen_vong.py`, `test_giao_dien_a13_8_khoa.py`. **Hai test cũ sửa** (`tests/test_wharton_khoa.py`: nạp tệp khi khoá, cửa xoá khi khoá) vì mã hoá hành vi tỉa mà quyết định này đổi.
- **2.2:** docstring bốn API đúng thực tế; `HUONG_DAN_SU_DUNG.md` ghi "thẻ Quản lý cần người giám sát máy". Không PIN.
- **2.3:** `_trang_diem_chuan` ghi lý do lên trang và `export_ket_qua` trả `canh_bao` (`xuat_diem_chuan_loi`). Test: `test_a13_8_xuat_diem_chuan.py`.
- **3.1, 3.3, 3.4:** `js/05_quan_ly.js` chỉ ẩn tab khi `wharton_chua_bat`, lỗi khác hiện thông báo; tắt tính năng không gọi `list_wharton_canh_bao` / `get_diem_chuan` (cờ `WHARTON_BAT` đặt ở `js/075_workspace.js`); `style.css` `#dcKhongXet`. Test: `test_giao_dien_a13_8_quan_ly.py`.
- **2.4:** `phong_wharton_hang_loat` một giao dịch, đọc lại điểm hiện tại (`ly_do = "da_doi"`), rollback toàn bộ kèm `backup_path`; `_luu_wharton` tách `_luu_wharton_cur`. Test: `test_a13_8_phong_mot_giao_dich.py`.
- **2.5:** `_ngu_canh_diem_chuan` đọc trong một giao dịch (`load_wharton_kem_doc_them`, hàm mới ở `rbda_priority_pipeline.py`; hàm cũ giữ nguyên). Test: `test_a13_8_diem_chuan_mot_giao_dich.py`.
- **2.6, 2.7, 2.8:** `so_nhap.py` — cột W của sổ mẫu chỉ khi workspace bật được (`wharton_bat_duoc`); hằng `CHO_CHEN_GHI_CHU_W` thay việc dò "Bước 5."; test so `lam_tron_100` với `phong_theo_ti_le`. Test: `test_a13_8_so_mau.py`.
- **1.1 `submit_club_scores` (Truong chọn B, 28/10/2026):** lượt không lưu và không xoá được dòng nào vì ô điểm sai (`nan`, `inf`, `"1e999"`, `-1`, chữ) trả `ok=false`, `errors` liệt kê từng (student_id, giá trị) bằng `score_not_a_number` / `score_negative`; lượt lẫn ô đúng và sai vẫn lưu phần đúng, `ok=true` + `warnings` như cũ. `js/06_cham_diem.js` tô đỏ các ô sai cả khi thất bại. **Test cũ sửa có duyệt** (`tests/test_diem_bat_thuong.py`, đúng các ca một-ô-sai): `test_man_hinh_cham_diem_tu_choi_diem_am`, `test_hai_duong_nhap_cung_mot_luat_voi_diem_am`, `test_gia_tri_khong_doc_duoc_thi_khong_ghi_de_diem_cu`, `test_diem_am_viet_bang_dau_phay_van_bi_chan`; ca mới thêm ở cuối tệp. `js/06_cham_diem.js` hiện thông báo vàng liệt kê hết các ô sai khi lượt thất bại (nên test giao diện `test_o_bi_bo_qua_duoc_to_do_va_khong_bao_xanh` giữ nguyên). Hai test cũ ở `tests/test_wharton_khoa.py` (lỗi 2.1) cũng được Truong đồng ý giữ nguyên bản sửa.
- **Kiểm:** toàn bộ test có Chromium, `-rs`, độ phủ 92,47 %: 2.859 qua (sau khi sửa 1 ca giao diện chấm điểm, đã chạy lại riêng và qua), 3 bỏ qua (numpy ×2, POSIX ×1; không ca giao diện nào bị bỏ qua). `ruff check .` sạch.

## 2026-10-28 — Z-SOAT Skill `soat-ma`: soát mã trước khi push

Theo yêu cầu của Truong (28/10/2026, "làm bước cuối" của đợt soát A13). Mã mục `Z-SOAT` do Claude đề xuất, chưa có trong sổ đăng ký 33 mục (quy ước khác thì đổi tên). Đây là lần duy nhất đợt soát được thêm mã; KHÔNG sửa lỗi nào trong `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md` (sẽ làm ở A13.8, dùng chính skill này).

- **Tệp mới:** `.claude/skills/soat-ma/SKILL.md` (luật không subagent / chỉ báo cáo, phạm vi diff so với `main`, cách ghi phát hiện, checklist bốn tầng viết tổng quát kèm bài học rút từ đợt soát A13, lệnh, mẫu báo cáo); `.claude/skills/soat-ma/scripts/kiem_nhanh.py` (một lệnh, bảy mục in ĐẠT / KHÔNG ĐẠT: `ruff`, `chu_cam`, `ma_loi_js`, `i18n_loi_khop`, `i18n_khoa`, `trung_khit` so với `main` 3 bộ × 5 seed, `khong_sua_nhat_ky`; chỉ thư viện chuẩn, `ruff` là công cụ ngoài đã có ở requirements-dev; mục không chạy được tính KHÔNG ĐẠT kèm lý do, không bỏ qua im lặng); `tests/test_skill_soat_ma.py`.
- **Tệp sửa:** `CLAUDE.md` — đúng MỘT dòng mới ở "Quy tắc làm việc" (quy tắc 8: "Trước khi push: chạy skill `soat-ma`"); bản đồ mã KHÔNG đụng (để A13.8).
- **Không đổi** mã sản phẩm, schema, hợp đồng cột CSV, hay kết quả xếp (bất biến 1–8 giữ nguyên). Skill KHÔNG vào `mau_forms_thi_clb/dong_goi_skill.py` (danh sách đó chỉ đóng .zip cho người dùng cuối); đăng ký theo kiểu của `sinh-du-lieu-clb` và `tao-workspace-tu-raw`: nằm trong `.claude/skills/`, có test riêng.
- **Test mới (45 ca):** `tests/test_skill_soat_ma.py` — mỗi mục một ca ĐẠT và các ca KHÔNG ĐẠT dựng trong thư mục tạm (xưng hô cấm ở VI / EN / lỗi / HTML, "Wharton" lộ ra chữ, mã lỗi lạ ở `.js` và `.html`, `i18n_loi.js` lệch và thiếu, khoá thiếu một ngôn ngữ hay rỗng, `DELETE` / `UPDATE` / `DROP` một dòng và nhiều dòng trên bảng dấu vết, tên bảng nằm trong danh sách `_RESET_BANG`-kiểu, hai bản mã khác thứ tự ưu tiên cho kết quả lệch, nhánh so sánh không có); khung `SKILL.md`, dòng trong `CLAUDE.md`, skill không nằm trong gói zip; và MỘT ca chạy script thật trên kho thật (năm mục nhanh phải ĐẠT: ai thêm xưng hô cấm, mã lỗi lạ, khoá i18n lệch hay xoá nhật ký thì test đỏ).
- **Chạy trên kho thật:** `kiem_nhanh.py` 7/7 ĐẠT (so với `main` và so với `e08af78`; trùng khít 15 ca). Hai điều chỉnh ghi trong mã và SKILL.md: chữ trong phần tử có `data-i18n` ở `index.html` là chữ dự phòng (có "em" từ trước A13) nên không soát lần hai; mã `loi_giao_dien_ngoai_du_kien` (từ trước A13) trùng một khoá UI nên được chấp nhận.
- **Kiểm toàn bộ (28/10/2026, Chromium thật, `-rs`):** 2.806 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua) — 2.761 của A13.7 cộng 45 ca mới. `ruff check .` sạch.

## 2026-10-27 — A13.7 Sổ nhập mẫu luôn có cột Điểm quyết tâm

Theo quyết định của Truong (27/10/2026): sổ MẪU luôn có cột "Điểm quyết tâm" kèm ghi chú "chỉ dùng khi bật tính năng". Không đổi mặc định `rules.wharton` (vẫn tắt), thuật toán, schema, hợp đồng CSV. Các đường ghi sổ khác (xuất dữ liệu đầu vào, ba skill, `du_lieu_test/`) giữ hành vi cũ.
- **Mã:** `so_nhap.ghi_so_nhap(..., luon_co_cot_w=False)` (mặc định = hành vi cũ; `True` thì `co_w` bật dù workspace tắt, trừ điểm theo người); `so_nhap.huong_dan(cfg, ghi_chu_cot_w)` thêm đoạn ghi chú trong sheet Hướng dẫn (chữ qua biến nhãn); `tao_so_nhap_mau` (`api_xuat.py`) và `mau_csv/tao_so_nhap.py` (mẫu trống và hai sổ `vi_du_*`) truyền `True`. Sinh lại ba sổ trong `mau_csv/`; các sổ trong `du_lieu_test/` (kịch bản đổi luôn chúng sang hai hàng) khôi phục bằng `git checkout`.
- **Khi tắt tính năng mà sổ có cột:** ô trống bỏ qua hoàn toàn; ô có số chỉ báo cảnh báo `csv_wp_bo_qua`, không chặn; không có dòng `wharton_bids`. `match_results` của sổ ví dụ trùng khít nạp bộ ba CSV cũ (seed 1, 7, 42).
- **Test mới (19 ca):** `tests/test_so_mau_co_cot_quyet_tam.py`.
- **Test cũ được sửa (Truong đã duyệt, 27/10/2026), chỉ hai kỳ vọng trong `tests/test_ws_so_nhap.py`:** `test_api_company_xuat_mau_roi_nap_lai` (hàng 1 của sổ mẫu là `["Nguyện vọng 1", None, None, "Nguyện vọng 2"]` thay vì `["Nguyện vọng 1", None, "Nguyện vọng 2"]`) và `test_api_mau_truong_hoc_giong_het_truoc_day` (`3 * 15` ô ở hàng 2 thay vì `2 * 15`). Lý do: đó đúng là thay đổi được chọn, sổ mẫu có ba cột mỗi nhóm. Không test nào bị `skip` hay nới.
- **Giao diện (`browser_host`):** workspace mặc định, bấm "Tải sổ nhập mẫu" ra sổ có cột ở 15/15 nhóm; nạp `vi_du_day_du` và chạy xếp xong, không lỗi JS.
- **Kiểm toàn bộ cho A13.6 và A13.7 (27/10/2026, Chromium thật, `-rs`):** 2.761 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua), `ruff check .` sạch, độ phủ 92,37 % (CI đòi 85 %). Sau đó chỉ sửa chữ ở tài liệu; các test đọc CHANGELOG / TIEN_DO / sổ đăng ký / HUONG_DAN_SO_NHAP chạy lại (2.468 qua) và xanh.

## 2026-10-27 — A13.6 Dữ liệu mẫu có Điểm quyết tâm (vòng 6)

Thêm bộ sổ nhập mẫu có Điểm quyết tâm (trong mã: `wharton`, cột CSV `wp_k`), sinh lại được bằng một lệnh, và cho kỹ năng `sinh-du-lieu-clb` sinh điểm khi được yêu cầu. Mọi số liệu là dữ liệu MÔ PHỎNG. Không đổi thuật toán, schema, hợp đồng CSV, định dạng sổ; không thêm thư viện. Mặc định của kỹ năng (`--diem-quyet-tam khong`) cho đầu ra cũ từng ô.
- **Sáu tệp** trong `du_lieu_test/`: `SO_NHAP_DQT_{120HS,800HS}_{HOP_LE,CO_LOI,TRONG}.xlsx`. NHỎ (120 em, 3 buổi) giữ nguyên nguyện vọng và điểm thi của `SO_NHAP_MAU_120HS_3BUOI.xlsx`; LỚN (800 em, 20 CLB, 4 buổi) sinh bằng `sinh_ngau_nhien` (seed 8002026). Điểm chia kiểu TRỘN (`don_dau`, `deu`, `all_in`, `ngau_nhien`; seed 27102026), làm tròn theo phần dư lớn nhất, hoà theo mã CLB.
- **`CO_LOI`:** năm loại lỗi (`thieu`, `thua`, `ngoai_nguyen_vong`, `tang_lech`, `toan_0`), 3 em mỗi loại ở bản nhỏ, 8 ở bản lớn, ghi trong `DQT_BANG_LOI.json` (kèm mã lỗi, quỹ, buổi mà bước Kiểm tra dữ liệu phải báo). Vì sổ chỉ có một ô điểm cạnh mỗi nguyện vọng và tầng do ô tick thi quyết định, `ngoai_nguyen_vong` thể hiện bằng điểm đặt cạnh ô nguyện vọng trống (phần mềm bỏ ô đó lúc nạp, quỹ còn thiếu) và `tang_lech` bằng một quỹ chung cho cả CLB có thi lẫn không thi của một buổi.
- **Kỹ năng:** `sinh_du_lieu.py` thêm `--diem-quyet-tam {khong,hop_le,co_loi,trong}`, `--kieu-chia {tron,don_dau,deu,all_in,ngau_nhien}` (cho `ngau`, `tao`), lệnh `ap` (áp điểm lên sổ có sẵn), `ap_diem_quyet_tam`, `soat_diem_quyet_tam` (`soat` tự soát hồ sơ điểm nếu sổ có điểm), `lam_tron_100`. Ghi sổ vẫn qua `so_nhap.ghi_so_nhap`. `SKILL.md` thêm mục "Điểm quyết tâm"; hai skill còn lại không đổi.
- **Script:** `du_lieu_test/sinh_du_lieu_diem_quyet_tam.py` (sinh sáu tệp và hai JSON `DQT_BANG_LOI.json`, `DQT_KIEU_CHIA.json`).
- **Tài liệu:** `du_lieu_test/README.md`, `TAI_LIEU_DU_LIEU.md` (bản dán `SKILL.md` và mục 5.3b), `docs/ke_hoach/TIEN_DO.md`, mục A13 của `SO_DANG_KY_33_MUC.md`.
- **Test mới (43 ca):** `tests/test_du_lieu_mau_diem_quyet_tam.py` (nạp 6 tệp; HOP_LE chạy xếp ok, có điểm chuẩn, mọi quỹ đúng 100; CO_LOI bị chặn đúng em đúng loại; TRONG không có `wharton_bids`, tự điền như cũ, kiosk nhập được; tắt tính năng thì `match_results` trùng khít với cùng sổ bỏ cột điểm, seed 1, 7, 42 ở cỡ nhỏ và seed 42 ở cỡ lớn; bản nhỏ giữ nguyên nguyện vọng và điểm thi; sinh lại ra đúng nội dung ô; kỹ năng). Không sửa test cũ nào.
- **Thử qua giao diện:** nạp `SO_NHAP_DQT_120HS_HOP_LE.xlsx` bằng `browser_host`, bật tính năng, chạy xếp (88/120 em được xếp, seed 42), tab Điểm chuẩn có bảng và biểu đồ, không lỗi JS.
- **Kiểm toàn bộ (27/10/2026, Chromium thật):** lần chạy đầy đủ 2.741 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua), 1 đỏ: `test_tai_lieu_du_lieu::test_toan_van_skill_md_con_dung` (bản dán `SKILL.md` trong `TAI_LIEU_DU_LIEU.md` thiếu mục mới). Đã sửa tài liệu, chạy lại bốn tệp liên quan (69 ca) xanh; chưa chạy lại toàn bộ sau sửa tài liệu. `ruff check .` sạch; độ phủ 92,34 % (CI đòi 85 %).

## 2026-10-27 — A13.5 Sửa 5 việc từ báo cáo đóng vai

Sửa các vấn đề #1 đến #5 của `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md` (#6, #7 để sau), cộng một lỗi chập chờn của vòng 4 và đóng vai lần 2. Tắt `rules.wharton` thì kết quả, dấu vân tay và `run_history` y hệt trước vòng 5 (bất biến 1): 15 lần chạy (3 bộ dữ liệu x 5 seed, `PipelineAPI.run_pipeline`) so với bản `d85fe2c`, `match_results` từng dòng, `run_history.luat_xep` và mã băm dấu vân tay GIỐNG HỆT (chỉ cột thời điểm chạy `luc` khác, đúng bản chất); `TestTrungKhit` qua. Không đụng thuật toán, `api.py`, schema, STB, thứ tự 5 bước.
- **Lỗi chập chờn của vòng 4 (Bước 0b):** `test_tieng_anh_chu_cua_khoi_doi_theo_va_khong_con_chu_co_dau` hỏng 1/20 lần. Nguyên nhân: đổi ngôn ngữ thì khối Điểm quyết tâm ở tab Quản lý nạp lại qua nhiều lời gọi API, và chữ cũ còn trên màn hình tới khi từng lời gọi về. Nay khối giữ dữ liệu lần vẽ gần nhất (`whBoNho`) và vẽ lại ngay khi đổi ngôn ngữ (`veLaiWhTuBoNho`, `js/05_quan_ly.js`). Sau sửa: 20/20 xanh. Kiosk Bước 3 đã vẽ lại ngay từ trước.
- **#1 Lỗi chặn gọn (`js/02_van_hanh.js`):** khung lỗi chỉ còn một dòng tóm tắt (`wharton_tom_tat_chua_hop_le`), 5 em đầu (mỗi em một dòng gộp mọi lỗi), "và M ... khác" và nút "Mở danh sách cần xử lý" (sang tab con Điểm quyết tâm, bộ lọc "chỉ hồ sơ có vấn đề" đã bật). Bước "Kiểm tra dữ liệu" trong danh sách bước cũng chỉ còn câu tóm tắt (`chuLoiBuocGon`, phát hiện khi đóng vai). Hợp đồng `{ok, data, errors}` KHÔNG đổi (bất biến 6): backend vẫn trả đủ mọi lỗi; gộp theo em làm ở JS bằng `params.student_id`.
- **#2 Hai nút hàng loạt:** "Tải danh sách cần sửa" (`export_wharton_can_sua`, `api_xuat.py`: Excel gồm mã, họ tên, buổi, quỹ, tổng hiện tại, thiếu, thừa, câu lỗi; không đổi điểm nào) và "Phóng cho đủ 100 theo tỉ lệ" (`phong_wharton_hang_loat`, `api_quan_ly.py`). Hàm thuần `phong_theo_ti_le(diem, ngan_sach=100)`: làm tròn theo phần dư lớn nhất, hoà phần dư xét theo MÃ CLB tăng dần, không nhận thứ hạng nguyện vọng (bất biến 2), không phụ thuộc thứ tự dict, tổng 0 trả `None`. Phải gõ `PHONG`; sao lưu trước; mỗi em qua `_luu_wharton(..., "quan_ly")` nên có kiểm khoá, kiểm hồ sơ và nhật ký giá trị cũ / mới; em tổng 0 (`tong_0`) hoặc còn lỗi khác (`loi_khac`) được bỏ qua và liệt kê; đang khoá thì `wharton_da_khoa`.
- **#3 Tab con của tab Quản lý:** CLB · Học sinh · Điểm quyết tâm · Điểm chuẩn · Dữ liệu. Hai tab điểm chỉ hiện khi bật tính năng (tắt thì ba tab con, nội dung y như cũ). Nhớ tab đang mở bằng `localStorage` (có `try/catch`; không đọc được thì mở tab đầu); `role="tablist"` / `tab` / `tabpanel`, `aria-selected`, phím mũi tên, Home, End. Id phần tử bên trong giữ nguyên.
- **#4 Khoá xuất khi chưa có kết quả (TOÀN ứng dụng, NGOÀI PHẠM VI A13, theo yêu cầu của Truong):** `export_ket_qua` và `export_csv` từ chối với `xuat_chua_co_ket_qua` TRƯỚC khi tạo tệp (`_chua_co_ket_qua`, cùng phép đo với `get_trang_thai_ket_qua`); ô xuất kết quả ở thẻ Kết quả bị khoá kèm dòng vàng (`khoaXuatKetQua`). Xuất dữ liệu đầu vào, Sổ nhập mẫu và hồ sơ học sinh dùng như cũ.
- **#5 Thông báo (TOÀN ứng dụng, NGOÀI PHẠM VI A13, theo yêu cầu của Truong):** nguyên nhân thông báo "Xong: ..." sau khi nạp Sổ "không tự tắt": mã cũ ĐÃ tự đóng thông báo thường sau `min(10000, 4000 + 40 x độ dài)` ms (khoảng 7 giây; `test_giao_dien_chay` canh), không phải thiếu hẹn giờ. Điều người đóng vai thấy là thông báo nằm lại vài giây giữa các ảnh chụp và vùng thông báo ở góc trên phải đè lên tiêu đề trang. Quy tắc mới (`js/00_nen.js`, `style.css`): thành công tự đóng sau 6 giây, câu dài thêm thời gian, tối đa 10 giây; rê chuột hoặc có tiêu điểm thì tạm dừng đếm; lỗi và cảnh báo giữ tới khi bấm ×; thành công kèm cảnh báo (`opts.canhBao`) tách thành thông báo xanh tự đóng và thông báo vàng giữ; vùng thông báo ở góc dưới phải, không nhận chuột ngoài từng thông báo; `prefers-reduced-motion` bỏ hiệu ứng; `aria-live` `polite` cho thông báo thường và `assertive` kèm `role="alert"` cho lỗi. Chữ của thông báo không đổi.
- **Mã lỗi mới:** `xuat_chua_co_ket_qua`, `wharton_phong_sai_xac_nhan`, `wharton_da_phong`, `wharton_tom_tat_chua_hop_le` (thêm vào `MA_MOI_SAU_ANH_CHUP`, `tests/test_ws_nhan.py`).
- **Test mới (60 ca):** `test_wharton_hang_loat` (21), `test_giao_dien_thong_bao` (11), `test_giao_dien_quan_ly_tab_con` (9), `test_giao_dien_loi_chan_gon` (6), `test_xuat_khoa_chua_co_ket_qua` (6), `test_giao_dien_khoa_xuat` (5), cộng hai test đổi ngôn ngữ khi lời gọi API còn treo (`test_giao_dien_wharton_quan_ly`, `test_giao_dien_wharton`).
- **Test cũ đã sửa theo ngoại lệ:** thêm thao tác bấm sang đúng tab con ở `test_giao_dien_diem_chuan`, `test_giao_dien_wharton_quan_ly`, `test_giao_dien_diem_quyet_tam_gon`, `test_giao_dien_xoa_du_lieu`, `test_giao_dien_ux_xuat`, `test_giao_dien_xuat_du_lieu`, `test_giao_dien_doi_ngon_ngu`, `test_khoi_dong_backend`, `test_giao_dien_sua_loi_p1`; xuất kết quả khi chưa có kết quả: `test_so_excel_de_dung` (`test_chua_chay_thi_van_xuat_duoc` đổi thành kiểm bị từ chối; `test_qua_nhieu_clb_khong_vuot_gioi_han_ngat_trang_cua_excel` thêm một em và chạy xếp) và `test_giao_dien_chay` (`test_loi_goi_phan_loi_hien_cau_tieng_viet` chạy xếp trước khi bấm xuất). Không test nào bị `skip` hay nới.
- **Kiểm toàn bộ (27/10/2026):** 2.699 qua, 3 bỏ qua (thiếu `numpy`; cần người dùng thường trên POSIX), không có test giao diện nào bị bỏ qua; `ruff` sạch; độ phủ 92,34 % (CI đòi 85 %).
- **Đóng vai lần 2** (có sửa mã với lỗi mức "chặn"): `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md`, mục "Lần 2 (27/10/2026)". Còn lại: #6, #7, biểu mẫu Google, mô phỏng VISEF, ngưỡng điểm tối thiểu, giải trình từng em.

## 2026-10-25 — A13.4 Giao diện Điểm quyết tâm và điểm chuẩn

Đổi tên hiển thị, đổi Sổ nhập sang hai hàng tiêu đề, thêm điểm chuẩn từng CLB (API, tab Kết quả, tab Quản lý, trang trong tệp xuất, ba biểu đồ SVG ngoại tuyến) và dọn gọn các màn của tính năng.
Tắt `rules.wharton` thì kết quả, dấu vân tay và `run_history` y hệt trước vòng 4: 15 lần chạy (3 bộ dữ liệu x 5 seed) so từng dòng `match_results` GIỐNG HỆT bản `4c448ae`; sổ Excel kết quả so từng ô cũng giống hệt. Mọi số liệu trong test là dữ liệu MÔ PHỎNG.
- **Tên hiển thị (Điểm quyết tâm; trong mã: wharton):** tiếng Việt "Điểm quyết tâm", tiếng Anh "Preference points" ở `i18n.js`, `i18n_errors.py` (sinh lại `i18n_loi.js`), Sổ nhập, tệp xuất, `HUONG_DAN_SU_DUNG.md`. Giữ nguyên tên hàm, bảng, mã lỗi `wharton_*`, khoá `rules.wharton`, cột CSV `wp_k`, id HTML.
- **Sổ nhập hai hàng (đổi hợp đồng, bất biến 7):** sheet học sinh luôn có hai hàng tiêu đề (hàng 1 ô gộp "Nguyện vọng k"; hàng 2 "CLB", "Điểm thi", "Điểm quyết tâm" khi bật), cột đầu gộp dọc, dữ liệu từ hàng 3, sheet CLB một hàng. Nạp đọc ba dạng (một hàng cũ, một hàng có "Điểm W k", hai hàng), nhận dạng bằng hàng 1. Cột lệch nhóm báo `so_nhap_cot_lech_nhom` / `so_nhap_nhom_thieu_cot` (sheet, cột, nhóm) và không nạp gì. CSV không đổi. `so_nhap.py` vẫn chạy một mình. Sổ mẫu trong `mau_csv/` sinh lại; `du_lieu_test/` giữ nguyên dạng một hàng.
- **Ba skill** `sinh-du-lieu-clb`, `xu-li-raw-forms`, `tao-workspace-tu-raw`: cập nhật SKILL.md (script đã ghi sổ qua `so_nhap.ghi_so_nhap` nên tự theo bố cục mới); chạy thử sinh sổ 60 em rồi `import_so_nhap` thành công.
- **Điểm chuẩn:** `tinh_diem_chuan` (hàm thuần, ở `api_quan_ly.py`), API `get_diem_chuan` và `get_diem_chuan_clb` (chỉ quản trị; kiosk không có đường gọi), trang "Điểm chuẩn" trong sổ Excel kết quả (chỉ khi bật). Tầng 2: điểm hiệu lực thấp nhất đã được nhận; tầng 1: điểm thi thấp nhất kèm điểm quỹ 1 của em cuối; tách suất thường và suất dự trữ theo `matched_tier`; CLB còn chỗ ghi 0 kèm số chỗ còn.
- **Giao diện:** mục "Điểm chuẩn" ở tab Kết quả luôn đóng mỗi lần vào thẻ (không nhớ trạng thái); khối chi tiết ở tab Quản lý; ba biểu đồ SVG (cột phân bố, dải chấm, bảng tổng quan) chọn màu theo kỹ năng dataviz, có tiêu đề, chú giải, bảng chữ ẩn, không tải gì từ mạng. Dọn gọn: hai khung Bước 3 cạnh nhau (màn hẹp xếp dọc) kèm thanh tiến độ, ô sai tô màu và dòng lỗi tại chỗ, giải thích sau nút (i); khối Quản lý có mục "Thao tác khác" đóng sẵn (mở khoá, xem nhật ký, xoá tất cả), bộ lọc một hàng; công tắc workspace một dòng ngắn kèm nút (i).
- **Test mới (110 ca):** `test_diem_quyet_tam_chu` (18), `test_so_nhap_hai_hang` (20), `test_diem_chuan` (53), `test_giao_dien_diem_chuan` (11), `test_giao_dien_diem_quyet_tam_gon` (8).
- **Test cũ đã sửa theo ngoại lệ:** chữ "Wharton" trong `test_giao_dien_wharton.py`, `test_giao_dien_wharton_quan_ly.py`, `test_ws_wharton_giao_dien.py`; tiêu đề và toạ độ Sổ nhập một hàng trong `test_so_nhap.py`, `test_wharton_so_nhap.py`, `test_ws_so_nhap.py` (kèm làm mới bản chụp `tests/du_lieu_ws/so_nhap_truoc_khi_co_cfg.json`: chỉ sheet học sinh và sheet hướng dẫn đổi, sheet CLB giống hệt), `test_ws_so_nhap_giao_dien.py`, `test_giao_dien_upload.py`. Ngoài ngoại lệ, buộc phải thêm bước "mở mục Thao tác khác" vào ba test của `test_giao_dien_wharton_quan_ly.py` (mục đóng sẵn theo yêu cầu thiết kế); `tests/test_ws_nhan.py` thêm hai mã mới vào danh sách cho phép.
- **Kiểm toàn bộ (27/10/2026):** lần chạy đầu 2.636 xanh, 3 đỏ, 3 bỏ qua; đã xử lý cả 3 (một câu `ORDER BY buoi` thiếu `COLLATE THU_TU_BUOI` ở `get_diem_chuan`; hai test cũ theo ngoại lệ: chữ "Wharton" trong `test_wharton.py` và tiêu đề Sổ một hàng trong `test_so_nhap.py`), chạy lại các tệp liên quan 288 ca xanh. Tổng sau sửa: 2.639 xanh, 3 bỏ qua (2 do thiếu `numpy`, 1 do cần người dùng thường trên POSIX; không ca giao diện nào bị bỏ qua, 278 ca giao diện dùng Chromium thật), `ruff check .` sạch, độ phủ 92,42 % (sàn CI: 85 %), `TestTrungKhit` 7/7.
- **Đóng vai người dùng** (chỉ báo cáo, không sửa mã): `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md`.

## 2026-10-25 — A13.3 Quản lý điểm Wharton

Thêm khối **Điểm Wharton** vào thẻ Quản lý (chỉ hiện khi workspace bật `rules.wharton`): bảng điểm, sửa từng em, xoá, cảnh báo hồ sơ có vấn đề; kèm nhật ký và khoá riêng.
Tắt Wharton thì thẻ Quản lý, mọi API cũ, kết quả, dấu vân tay và `run_history` y hệt trước vòng 3 (bất biến 1). Mọi số liệu trong test là dữ liệu MÔ PHỎNG.
- **Quyết định đã chốt (25/10/2026):** (1) nhật ký mọi lần ghi hoặc xoá điểm: lúc nào, nguồn (`quan_ly`, `kiosk`, `nap_tep`, `xoa_du_lieu`, `he_thong`), tên tài khoản máy
  (`getpass.getuser()`, lỗi thì rỗng), giá trị cũ và mới; không bao giờ bị xoá hay ghi đè, kể cả `reset_data`. (2) Khoá Wharton RIÊNG (không dính STB): lần chạy xếp thành công
  khi Wharton bật tự khoá, kể cả chạy riêng một số buổi; đang khoá thì mọi cửa GHI điểm trả `wharton_da_khoa`; mở bằng `mo_khoa_wharton("MO")`. (3) Các cửa xoá dữ liệu
  vẫn chạy khi khoá nhưng ghi nhật ký; `reset_data` mở luôn khoá Wharton. (4) Chỉ hiện khi bật Wharton. (5) Màn dành cho quản trị. (6) Giữ STB; thứ tự 5 bước pipeline không đổi.
- **Sửa "cách A" (Bước 2, Truong đã duyệt):** `submit_wharton` chỉ ghi ô em đã GỬI (ô 100 tự điền chỉ có trong bộ nhớ), nên thêm CLB thứ hai vào quỹ đó sau này thì hồ sơ bị coi là
  chưa chia thay vì "hợp lệ" nhờ một ô em chưa từng đặt; cảnh báo sau khi nạp tệp (`_soat_ho_so_wharton`) cũng tự điền trong bộ nhớ như pipeline và báo cáo sức khoẻ dữ liệu.
- **Hai bảng mới** trong `DEFAULT_SCHEMA` (chỉ `CREATE TABLE IF NOT EXISTS`, không vào `_BANG_RANG_BUOC`; `di_tru_schema` chạy lặp an toàn): `wharton_nhat_ky(id, luc, nguon, nguoi, hanh_dong, student_id, cu_json, moi_json)`,
  không khoá ngoại, `nguon` bị CHECK; `wharton_lock(id = 1, is_locked, locked_at, unlocked_at)`. Không câu `DELETE` / `UPDATE` nào chạm nhật ký.
- **API mới** (`api_quan_ly.py`): `list_wharton_admin`, `list_wharton_canh_bao`, `get_wharton_nhat_ky`, `admin_save_wharton` (dùng lại lõi `_luu_wharton` với `submit_wharton`), `clear_wharton`
  (một em, hoặc tất cả khi gõ `XOA`, có sao lưu), `mo_khoa_wharton`, `get_wharton_lock_status`; `get_student_entry_state` có thêm cờ `khoa` trong khoá `wharton`. `_ho_so_wharton_tat_ca` là MỘT hàm đọc
  một lần, dùng chung cho bảng điểm, danh sách cảnh báo và `get_data_health_report` (số liệu báo cáo không đổi).
- **Cửa có nhật ký:** `submit_wharton` (`kiosk` / `luu`), `admin_save_wharton` (`quan_ly` / `luu`), nạp tệp kể cả Sổ nhập (`nap_tep` / `luu`), tỉa trong `submit_preferences` (`kiosk` / `tia_nguyen_vong`),
  `reset_student_entry` (`kiosk` / `xoa_mot_em`), `delete_student` (`quan_ly` / `xoa_mot_em`), `delete_club` (`quan_ly` / `xoa_theo_clb`, mỗi em một dòng), `reset_data` (`xoa_du_lieu` / `xoa_tat_ca`, một dòng tổng),
  `clear_wharton`, khoá sau khi chạy (`he_thong` / `khoa`) và mở khoá (`mo_khoa`). Nhật ký nằm trong CÙNG giao dịch với thao tác. Cửa ghi có kiểm khoá trong giao dịch ghi: `submit_wharton`, `admin_save_wharton`,
  `clear_wharton`, nạp cột `wp_*` (nguyện vọng vẫn nạp, phần điểm bị bỏ kèm cảnh báo `wharton_da_khoa`).
- **Pipeline** (`api.py`, chỉ bước 5/6): đặt khoá trong cùng giao dịch ghi `run_history` khi Wharton bật; thứ tự năm bước không đổi; khoá và nhật ký không vào dấu vân tay.
- **Giao diện:** `js/04_nhap_tai_cho.js` tách `whartonVeKhung` / `whartonThuThapTu` / `whartonChuoiTu` / `whartonGiuTamTu` dùng chung (hành vi kiosk không đổi) và Bước 3 chỉ đọc khi khoá;
  `js/05_quan_ly.js` khối mới (bảng, lọc, phân trang, cảnh báo, màn sửa, nhật ký, hộp xác nhận `MO` / `XOA`); `index.html`, `style.css`, `i18n.js` (vi/en).
- **Mã lỗi** (`i18n_errors.py` rồi `python tao_i18n_js.py`, `i18n_loi.js` chỉ thêm dòng): `wharton_da_khoa`, `wharton_mo_khoa_sai_xac_nhan`, `wharton_xoa_sai_xac_nhan`, `wharton_da_xoa`,
  `wharton_da_mo_khoa`, `error_wharton_quan_ly`; thêm vào `MA_MOI_SAU_ANH_CHUP` của `tests/test_ws_nhan.py`.
- **Test cũ đã sửa theo ngoại lệ A.3:** `tests/test_wharton_kiosk.py::test_tu_dien_khi_quy_chi_co_mot_clb` (ô tự điền không còn được ghi, Bước 2) và
  `tests/test_wharton_kiosk.py::test_bat_wharton_trang_thai_co_khoa_wharton_dung_dang` (khoá `khoa` do vòng này cố ý thêm). `tests/test_ws_nhan.py`: chỉ thêm 6 mã vào danh sách cho phép.
- **Test mới (141 ca):** `test_wharton_cach_a` (6), `test_wharton_nhat_ky` (22), `test_wharton_khoa` (21), `test_wharton_quan_ly` (23), `test_wharton_quan_ly_ghi` (21),
  `test_wharton_quan_ly_dau_cuoi` (1), `test_giao_dien_wharton_quan_ly` (10, Chromium thật), cộng 37 ca vòng 3 trong `test_wharton_ma_loi`.
- **Trùng khít (bất biến 1):** Wharton tắt: 15 lần chạy `run_pipeline` (3 bộ trong `du_lieu_test/do_anh_huong_seed.BO_DU_LIEU` × seed 1, 7, 42, 3, 11) cho `match_results` đầy đủ cột (1.350 dòng),
  `dau_van_tay_chay` và `run_history.luat_xep` GIỐNG HỆT bản chụp lấy trước khi sửa (đỉnh vòng 2, `a8b077d`); `tests/test_nhieu_buoi.py::TestTrungKhit` 7/7 xanh. Toàn bộ: 2.529 ca xanh, 3 ca bỏ qua (2 do thiếu
  `numpy`, 1 do cần người dùng thường trên POSIX; không ca giao diện nào bị bỏ qua, 212 ca giao diện chạy bằng Chromium thật), `ruff check .` sạch, độ phủ 92,34 % (sàn của CI: 85 %). Một ca trợ năng
  (`test_giao_dien_tro_nang::test_moi_o_nhap_deu_co_ten_doc_duoc`) bắt được hai ô gõ chữ xác nhận thiếu tên đọc được; đã sửa bằng `aria-label` qua `i18n.js`.
- **Cần biết:** ở màn (kiosk và thẻ Quản lý) khung chỉ có một CLB tự điền 100 và khoá ô; giao diện gửi cả ô đó khi bấm Lưu nên server GHI ô đó (đúng với "ô người dùng gửi thì được ghi"). Cách A (không ghi ô tự điền)
  vì vậy giữ trọn với gọi API trực tiếp, nạp tệp và Sổ nhập; đường bấm Lưu trên giao diện vẫn ghi ô 100 như vòng 2 (`js/04_nhap_tai_cho.js` ngoài phạm vi vòng này để sửa phần thu thập).


## 2026-10-25 — A13 Điểm Wharton: pipeline tự điền quỹ một CLB trong bộ nhớ (theo quyết định của Truong, cách A)

Quỹ (mỗi buổi) chỉ có MỘT CLB mà em chưa đặt điểm: lúc chạy xếp và lúc lập báo cáo sức khoẻ dữ liệu, `api.py` gọi `tu_dien_wharton_mot_clb`
trong bộ nhớ TRƯỚC `kiem_ho_so_wharton` / `diem_wharton_hieu_luc`. Không ghi `wharton_bids`; kết quả vẫn tất định (hàm thuần của nguyện vọng,
ô tick và điểm đã lưu, đều nằm trong dấu vân tay). Quỹ đã có khoá (kể cả 0) hoặc có từ hai CLB mà chưa chia thì vẫn bị chặn. Tắt Wharton: không đổi.
Test mới (5 ca, trong `tests/test_wharton_pipeline.py`): chạy được khi chưa lưu, CSDL không đổi, bằng kết quả khi đã lưu 100, không che lỗi thật,
sức khoẻ dữ liệu cùng cách tính. Sửa mục 14 của `HUONG_DAN_SU_DUNG.md` cho khớp.

## 2026-10-24 — A13 Điểm Wharton (vòng 2: lưu trữ, nhập liệu, kiosk, pipeline)

Làm tiếp mục A13 theo quyết định của Truong: chỉ bật được khi `priority` là `score` / `score+tier` và `score_scope` là
`per_slot`; hồ sơ Wharton sai CHẶN cả lần chạy ở bước Kiểm tra dữ liệu, trước khi bốc hay khoá STB; nhập bằng tệp (CSV, Sổ
nhập) và bằng một màn kiosk; lưu tầng lúc nhập; mặc định **TẮT** — mọi hành vi, tệp, dấu vân tay và kết quả giống hệt trước
vòng 2 (bất biến 1). Giữ STB (không SHA-256, không `public_value`; bất biến 3 nguyên). Mọi số liệu trong test là dữ liệu
MÔ PHỎNG. Ghi hợp đồng cột vào sổ đăng ký TRƯỚC khi làm (bất biến 7).
- **Bảng `wharton_bids(student_id, club_id, tier, points)`** trong `DEFAULT_SCHEMA` (khoá chính `(student_id, club_id)`, `tier IN (1, 2)`,
  `points >= 0`, khoá ngoại tới `students`, `clubs`); bảng mới hoàn toàn nên chỉ cần `CREATE TABLE IF NOT EXISTS`, không vào
  `_BANG_RANG_BUOC`. `tier` = quỹ lúc NỘP (1 = lúc ghi em đang tick thi CLB đó). Đổi ô tick sau khi chia điểm thì hồ sơ thành chưa
  hợp lệ (`wharton_ngoai_tap`); phần mềm KHÔNG tự chuyển điểm sang quỹ kia. Dọn ở mọi cửa xoá: `delete_student`, `delete_club`,
  `reset_student_entry`, `reset_data` (`_RESET_BANG`), `submit_preferences` (bỏ CLB thì xoá điểm CLB đó), `seed_sample_data`; nạp CSV
  nguyện vọng cũng dọn dòng của CLB bị bỏ.
- **Thay đổi hợp đồng cột (bất biến 7), chỉ khi workspace bật Wharton:** CSV nguyện vọng thêm `wp_k` đi cặp `pref_k`, `<buoi>_wp_k`
  đi cặp `<buoi>_pref_k`, và cột `wp` cho dạng dài (ghép theo HẬU TỐ SỐ, không theo vị trí); Sổ nhập thêm cột "Điểm W k" ngay sau
  "Điểm k" (kèm kiểm số nguyên ở Excel, màu riêng, đoạn hướng dẫn hai quỹ). Tệp không có các cột này nạp như cũ; chưa bật mà có thì bỏ
  qua kèm `csv_wp_bo_qua`. Xuất "dữ liệu đầu vào" ra Sổ nhập có cột W khi bật; nạp lại ra `wharton_bids` giống hệt.
- **Khoá luật `rules.wharton`** (bool, mặc định `False`): `cau_hinh_ws` từ chối tổ hợp khác; `LUAT_XEP_MAC_DINH["wharton"]`, `dung_wharton`.
  Khoá `wharton` chỉ vào chuỗi ghi `run_history.luat_xep` và phần băm dấu vân tay khi BẬT (`_luat_de_ghi_hoac_bam`), nên workspace
  tuỳ biến cũ giữ nguyên từng byte. Dấu vân tay có thêm bảng `wharton_bids` khi bật.
- **Đọc dữ liệu:** `doc_du_lieu_wharton`, `load_from_sqlite_kem_dau_van_tay_wharton` (dữ liệu, dấu vân tay và Wharton trong MỘT giao
  dịch đọc); `_doc_du_lieu`, `load_from_sqlite_kem_dau_van_tay` giữ nguyên chữ ký và giá trị trả về.
- **API kiosk:** `submit_wharton(student_id, w1, w2)` (kiểm ở server theo V6: tự điền một CLB → `kiem_ho_so_wharton` → thay toàn bộ dòng
  của em; hồ sơ sai thì không ghi gì và trả đúng danh sách lỗi); `get_student_entry_state` có thêm khoá `wharton` CHỈ khi bật (tắt thì
  y hệt trước).
- **Nối pipeline** (`_run_pipeline_da_khoa`, chỉ bước 2 và 4): bước Kiểm tra dữ liệu đọc bằng bản có Wharton, chạy `kiem_ho_so_wharton` và
  `diem_wharton_hieu_luc` NGAY SAU `validate_data_integrity` — trước soát buổi, bốc, khoá STB; có lỗi (mọi mã trừ `wharton_vang_thi`) thì
  trả `wharton_ho_so_chua_hop_le` cùng đủ lỗi, không vẽ số, không ghi, không thêm dòng `run_history`. Vắng thi chỉ là cảnh báo trong chi
  tiết bước validate. Bước 4 truyền `diem_wharton` cho `run_rbda_nhieu_buoi`. Thứ tự năm bước giữ nguyên.
- **Sức khoẻ dữ liệu:** `health_wharton_chua_hop_le` (mức high) và `health_wharton_vang_thi` (mức medium), chỉ khi bật, đặt sau các mục sẵn có.
- **Giao diện:** ô "Dùng điểm Wharton" ở bước luật của trình hướng dẫn workspace (khoá và tự bỏ chọn khi không dùng được) và hàng tóm tắt
  `rvWharton`; màn "Bước 3. Điểm Wharton" ở tab Nhập tại chỗ (hai khung mỗi buổi, bộ đếm "Đã dùng X / 100", tự điền và khoá khung một CLB,
  "Cần chia lại điểm" khi lệch tier, vẽ lại sau khi lưu Bước 1 / 2, chung cơ chế "chưa lưu"; học sinh chỉ thấy điểm của chính mình).
- **Mã lỗi song ngữ (8):** `csv_wp_khong_hop_le`, `csv_wp_khong_co_nguyen_vong`, `csv_wp_bo_qua`, `wharton_chua_bat`,
  `wharton_ho_so_chua_hop_le`, `health_wharton_chua_hop_le`, `health_wharton_vang_thi`, `error_saving_wharton`; `i18n_loi.js` sinh lại, chỉ thêm dòng.
- **Test mới: 252 ca** (viết trước, thấy đỏ rồi mới viết mã): `test_wharton_luu_tru` (21), `test_wharton_luat` (30), `test_wharton_doc` (15),
  `test_wharton_ma_loi` (56), `test_wharton_nhap` (24), `test_wharton_so_nhap` (23), `test_wharton_kiosk` (29), `test_wharton_pipeline` (24),
  `test_wharton_suc_khoe` (6), `test_wharton_dau_cuoi` (1), `test_ws_wharton_giao_dien` (9), `test_giao_dien_wharton` (14). Bản chụp mốc
  `tests/du_lieu_ws/wharton_moc_truoc_vong2.json` (`match_results`, `dau_van_tay_chay`, `luat_xep` của 3 bộ × 3 seed, chụp bằng mã TRƯỚC
  vòng 2) được so trong `test_wharton_pipeline`. Đã thử phá hoại có chủ đích (bỏ truyền `diem_wharton` ở bước 4): bị bắt.
- **Xác nhận.** Tắt Wharton: giống hệt mốc (810 dòng `match_results`, dấu vân tay, `luat_xep`); `TestTrungKhit` 7/7. Toàn bộ test (kèm Chromium
  thật): 2.383 qua, 3 bỏ qua (thiếu `numpy`; cần người dùng không phải root), 0 đỏ; `ruff check .` 0 lỗi; độ phủ 92,43 % (sàn 85 %).
- **Chỗ lệch yêu cầu, có lý do.** (1) Câu chữ màn kiosk không dùng "bạn" ("Các CLB bạn đã thi" thành "Các {slot_sl} đã thi") vì
  `tests/test_van_phong_tu_nhien.py` cấm xưng hô "bạn/em" trong mọi chuỗi giao diện; câu báo lỗi vẫn là "Chưa dùng hết điểm Wharton…".
  (2) `{detail}` của `error_saving_wharton` không nằm trong câu (test văn phong cấm); `format_message` tự thêm chi tiết ở cuối như các mã
  `error_*` khác. (3) `tests/test_ws_nhan.py`: chỉ THÊM 8 mã mới vào `MA_MOI_SAU_ANH_CHUP` (test đó tự quy định cách này; ngoại lệ "wharton: False"
  của luật KHÔNG phải dùng cho test nào). (4) `get_student_entry_state` có thêm `tu_dien_mot_clb` và `ds_buoi` trong khoá `wharton`.
  (5) Khoá `wharton` chỉ được ghi vào `luat_xep` / băm khi bật, để bất biến 1 đúng cả với workspace tuỳ biến cũ.
- **Việc sau:** cập nhật ba skill trong `.claude/skills/` (sinh dữ liệu, xử lí raw forms, tạo workspace) cho cột mới; biểu mẫu Google hai khung;
  mô phỏng VISEF; ngưỡng điểm tối thiểu; công bố điểm chuẩn; giải trình từng em (C3). Điểm cần Truong quyết: em có quỹ chỉ một CLB mà chưa
  bấm Lưu ở kiosk thì lần chạy bị chặn (màn kiosk tự điền 100 nhưng chưa ghi) — có muốn tự điền ngay trong pipeline không.

## 2026-10-24 — A13 Điểm Wharton (vòng 1: lõi thuật toán và test)

Mục mới A13 trong sổ đăng ký (`docs/ke_hoach/`), làm theo quyết định của Truong ngày 24/10: **giữ nguyên STB**
(bộ số đã khoá, chế độ `stb_ngay`, cách chèn em đến muộn), điểm Wharton xét **TRƯỚC** STB, mỗi quỹ **100 điểm
MỖI BUỔI**, vòng này **chỉ làm lõi thuật toán, test, mã lỗi và tài liệu sổ**. Không đổi schema, `api*.py`, sổ nhập,
giao diện hay `compute_club_priority` (không đổi một ký tự). Mọi số liệu dưới đây là dữ liệu MÔ PHỎNG.
- **Cơ chế.** Mỗi học sinh có hai quỹ cho mỗi buổi: quỹ 1 chia cho CLB có thi (chỉ phá hoà khi bằng điểm thi),
  quỹ 2 chia cho CLB không thi (tiêu chí chính tầng 2). Khoá ưu tiên: tầng 1 `(0, -điểm thi, (), -w1, stb, mã)`,
  tầng 2 `(1, -w2, stb, mã)`; `()` là chỗ dành cho tiêu chí phụ của mục A1. Gale–Shapley vẫn chạy MỘT lần cho cả
  hai tầng; thứ hạng nguyện vọng không vào khoá.
- **Hàm mới** (`rbda_priority_pipeline.py`, khối `BƯỚC A2` L252–L574): `khoa_uu_tien_wharton`, `uu_tien_wharton`
  (hàm bọc như `uu_tien_theo_nhom`, nhận `tier_rank`), `kiem_ho_so_wharton` (V1–V5, theo từng buổi, trả đủ mọi
  lỗi theo thứ tự cố định), `tu_dien_wharton_mot_clb`, `diem_wharton_hieu_luc` (lúc khoá: vắng thi rơi xuống tầng
  2, T2 chuyển lên T1 là lỗi); ba hằng `WHARTON_NGAN_SACH = 100`, `WHARTON_TU_DIEN_MOT_CLB = True`,
  `WHARTON_VANG_THI = "tier2_zero_points"` (hai hằng sau chờ chủ dự án quyết).
- **Hai tham số mới**, mặc định `None` = hành vi cũ: `diem_wharton` của `run_rbda` (thay NGUỒN `base_rank`; dự
  trữ mềm, `verify_stability` giữ nguyên) và của `run_rbda_nhieu_buoi` (chuyển nguyên cho mọi buổi).
- **7 mã lỗi song ngữ** trong `i18n_errors.py` (`wharton_nguyen_vong_chua_xep`, `wharton_chua_dung_het`,
  `wharton_vuot_ngan_sach`, `wharton_diem_khong_hop_le`, `wharton_ngoai_tap`, `wharton_tang_lech`,
  `wharton_vang_thi`); `i18n_loi.js` sinh lại bằng `tao_i18n_js.py`, chỉ thêm 28 dòng. Câu chữ dùng chỗ giữ nhãn
  workspace (`{person}`, `{slot_sl}`, `{session_l}`…), không viết cứng "học sinh" / "CLB".
- **Test mới.** Phần hàm và mã lỗi viết trước, thấy đỏ rồi mới viết mã; nhóm test tính chất viết sau, trên mã đã
  xong, đúng theo đặc tả của bước đó. `tests/test_wharton.py`, 144 ca: khoá ưu tiên và W1, W3;
  hàm bọc (200 bộ ngẫu nhiên: bằng điểm Wharton thì y hệt `compute_club_priority` / `uu_tien_theo_nhom`); VD1–VD5
  qua `run_rbda`, W7, mặc định `None` trùng khít trên 30 bộ, và hai buổi khớp `run_rbda` chạy riêng; mã lỗi;
  `kiem_ho_so_wharton` (W5, 32 ca); `tu_dien_wharton_mot_clb`; `diem_wharton_hieu_luc` (VD6, W4); VD1–VD5 đi từ
  `w1`/`w2` thô (W9); test tính chất: W1 (hoán vị nguyện vọng không đổi `base_rank`), W2, W6 (50 bộ một buổi có
  dự trữ / nhóm xếp cứng + bốn cấu hình nhiều buổi), W8 (mọi hoán vị nguyện vọng của từng em trên 15 bộ nhỏ,
  không hoán vị nào cho CLB tốt hơn kết quả thật). Thử phá hoại có chủ đích: đổi dấu `w1`, đặt STB trước Wharton ở
  tầng 2, bỏ qua `diem_wharton` trong `run_rbda`, xác định tầng bằng "điểm > 0" — cả bốn đều bị bắt.
  `tests/test_ws_nhan.py`: chỉ THÊM 7 mã vào `MA_MOI_SAU_ANH_CHUP` (cách test đó quy định).
- **Bất biến.** Bất biến 1: `TestTrungKhit` 7/7 qua, cùng test mặc định `None` trùng khít. Bất biến 8: test thay
  thế được và luật tổng cầu (400 nhóm ứng viên, thứ tự nền của `uu_tien_wharton` + dự trữ mềm, có và không
  `tier_rank`) qua. Toàn bộ test: 1.923 qua, 211 bỏ qua do máy không tìm thấy Chromium (trình trợ giúp tìm
  `chrome-linux/chrome`, bản cài sẵn nằm ở `chrome-linux64/chrome`); chạy riêng 28 tệp giao diện với
  `RBDA_TEST_CHROMIUM` đặt tay: 253 qua, 0 bỏ qua. `ruff check .` 0 lỗi (mốc 0); độ phủ 92,11 % (sàn 85 %).
- **Chỗ cố ý lệch đặc tả.** (1) Điểm thi giữ `float`, không đổi `Decimal`: so `float` cho cùng thứ tự với
  `Decimal(str(x))` và điểm đọc thẳng từ cột REAL (ghi trong docstring). (2) Không có `round_id`, không làm số bốc
  SHA-256 / `public_value` (giữ STB). (3) Câu `wharton_chua_dung_het` mở đầu "Chưa dùng hết điểm Wharton…", không
  phải "Bạn chưa dùng hết…": `tests/test_van_phong_tu_nhien.py` cấm xưng hô "bạn/em" trong câu báo lỗi. (4) Câu
  `wharton_nguyen_vong_chua_xep` dùng `{session_l}` thay chữ "buổi" viết cứng, để workspace gọi là "ca" cũng đúng.
  (5) `kiem_ho_so_wharton` có thêm tham số tuỳ chọn `tran_nguyen_vong` (mặc định `TRAN_NGUYEN_VONG_MOI_BUOI`) vì
  workspace có thể đặt trần khác. (6) Mỗi ô điểm có tối đa một lỗi: khoá ngoài tập chỉ báo `wharton_ngoai_tap`.
  (7) W2 chỉ kiểm khi không dự trữ và không nhóm xếp cứng: có dự trữ thì em tầng 2 đủ diện dự trữ được giữ suất
  trước em tầng 1, có `tier_rank` thì nhóm đứng trước cả tầng — đo thử trên dữ liệu mô phỏng thấy đúng như vậy; đó
  là đặc tính cũ của dự trữ và nhóm, không do A13. Hai chế độ ấy được canh bằng W6 (ổn định).
- **Rủi ro đã ghi trong sổ.** "Khai thật là tốt nhất" chỉ được bảo đảm với THỨ TỰ nguyện vọng (W8), KHÔNG với
  cách chia điểm Wharton: người biết tính có thể lợi hơn người ngây thơ; cần đo bằng mô phỏng.
- **Việc vòng sau** (chưa làm): bảng `wharton_bids`; cột CSV / Sổ nhập (đổi hợp đồng cột, bất biến 7); nối
  pipeline (kiểm hồ sơ ở bước "kiểm dữ liệu", TRƯỚC khoá STB; thứ tự tự điền → kiểm hồ sơ → khoá STB → điểm hiệu
  lực → chạy); khoá luật workspace; biểu mẫu hai khung "Đã dùng X / 100"; mô phỏng VISEF; ngưỡng điểm tối thiểu;
  công bố điểm chuẩn.

## 2026-10-15 — Workspace: Việt hoá sạch màn chọn và sửa bảng (ngoài sổ đăng ký, theo yêu cầu chủ dự án; chồng lấn Z1)

Ở giao diện tiếng Việt, màn chọn workspace còn "workspace" và ".zip" lẫn trong câu, và bảng bị vỡ.
Giao diện tiếng Anh giữ nguyên chữ cũ. Không đổi backend, thuật toán hay hợp đồng `{ok, data, errors}`.
- **Chữ tiếng Việt.** "workspace" → "không gian làm việc"; ".zip" → "tệp nén" (nút Xuất tệp nén / Nhập tệp nén,
  câu nhắc, thông báo). Sửa trong `i18n.js` (khối `vi`, các khoá `ws_*`), `i18n_errors.py` (sáu mã `ws_*` và bốn
  câu có "Workspace này"), `index.html` (chữ mặc định của nút thanh bên); `i18n_loi.js` sinh lại bằng
  `tao_i18n_js.py`. "thư mục _trash" giữ nguyên vì là tên thư mục thật trên đĩa.
- **Chuỗi do backend đặt, không đổi theo ngôn ngữ.** Tên mẫu dựng sẵn "Trường học" nay dịch ở JS theo khoá mới
  `ws_mau_truong_hoc` (vi "Trường học", en "School"); cột "Sửa lần cuối" hiện `15/10/2026 12:19:20` ở tiếng Việt,
  giữ `2026-10-15 12:19:20` ở tiếng Anh (`js/075_workspace.js`: `wsTenMau`, `wsDinhDangNgay`).
- **Bảng.** `display:flex` đặt thẳng lên `<td>` làm ô mất kiểu `table-cell`: nền hàng "Đang mở" dừng giữa chừng,
  đường kẻ lệch, nút Xoá rớt dòng. Nay `<td class="ws-cot-hanh-dong">` chứa `<div class="ws-hanh-dong">` (flex);
  hộp thoại rộng 1040px; cột Tên về font chữ thường (trước đó dùng font mã của `.data-table td:first-child`);
  `select` / `textarea` trong trình hướng dẫn kế thừa font. Màn hẹp thì sáu nút xuống dòng gọn trong ô.
- **Test mới (viết trước, thấy đỏ rồi mới sửa).** `tests/test_giao_dien_tieng_viet_sach.py`: thêm "workspace" vào
  danh sách cấm và một test quét thô chữ "zip". `tests/test_ws_giao_dien.py`: tiếng Việt không còn
  workspace/zip ở màn chọn và cả bốn bước hướng dẫn; tiếng Anh không còn chữ có dấu tiếng Việt ở màn chọn và ba
  bước đầu; tên mẫu và ngày đổi theo ngôn ngữ; bảng vẽ đúng (ô hành động là `table-cell`, mọi ô cao bằng hàng,
  sáu nút một dòng, nền phủ cả hàng, tên không dùng font mã).
- **Ảnh chụp chuỗi làm mới có chủ đích.** `tests/du_lieu_ws/chuoi_truoc_khi_co_nhan.json`: chỉ 24 chuỗi `vi` đã đổi
  (5 mã lỗi `ws_*`, 19 khoá `ws_*` của giao diện); `test_ws_nhan.py` vẫn so toàn bộ phần còn lại như cũ.

## 2026-10-15 — Skill `tao-workspace-tu-raw` và hai bộ dữ liệu thử (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

- **Skill mới `.claude/skills/tao-workspace-tu-raw/`**: raw bất kỳ (Excel/CSV tự do, Google/Microsoft Forms, hai
  tệp tách rời, văn bản dán) → workspace `.zip` nạp sẵn dữ liệu + Sổ nhập theo nhãn + `BAO_CAO_SOAT.md`.
  Bốn dạng nguyện vọng (`cot_xep_hang`, `mot_o`, `dong_dai`, `ma_tran`), đủ luật workspace, điểm theo chỗ / theo
  người. Đoán rồi hỏi duyệt; chỉ tiêu bắt buộc hỏi; sai một điều không ghi tệp nào; kiểm bằng `import_so_nhap` +
  báo cáo sức khoẻ + chạy thử; từ chối ghi đầu ra vào kho git (dữ liệu người thật). Không đụng mã sản phẩm.
  Test: `tests/test_skill_tao_workspace.py` (21 ca).
- **Bộ dữ liệu thử (mô phỏng)**: `du_lieu_test/bo_thu_chuong_trinh/` (trường 3 buổi, 180 học sinh) và
  `du_lieu_test/bo_thu_workspace/` (workspace "Công ty Bình Minh", zip nạp sẵn, kèm script sinh lại).

## 2026-10-14 — Sửa lỗi CI Windows của PR #1 (24 test đỏ; Linux đạt)

Bộ test Windows đỏ 24 ca trong khi Linux xanh. Hai nguyên nhân, một thật của sản phẩm và một của test:
- **Lỗi sản phẩm — `connect_db` rò kết nối khi tệp không phải SQLite.** PRAGMA đầu tiên ném mà kết nối chưa
  được đóng. Trên Linux không ai hay; trên Windows tệp đang mở không dời / xoá / đổi tên được (WinError 32 / 5),
  nên **xoá một workspace hỏng, nhập zip có `app.db` hỏng (thư mục tạm không dọn được), di trú `app.db` cũ hỏng**
  đều hỏng đúng lúc người dùng cần. Nay `connect_db` đóng kết nối rồi mới ném lại. Bộ dò
  `tests/test_ws_ket_noi_dong.py` bắt lỗi kiểu này NGAY TRÊN LINUX (kết nối bị huỷ mà chưa `close()`), và phủ các
  đường workspace / zip / di trú / chạy xếp. Vì sao Linux không thấy: kết nối sqlite3 của CPython 3.11 nằm trong vòng
  tham chiếu vòng (bộ nhớ đệm câu lệnh) nên chỉ nhả tệp khi GC chạy.
- **Lỗi của test.** (1) `with sqlite3.connect(db) as c` chỉ commit, KHÔNG đóng — các helper của
  `test_ws_registry.py` / `test_ws_sua_loi_3.py` nay dùng `contextlib.closing`. (2) Tiến trình con của
  `test_tham_khao_verify_nhanh.py` in tiếng Việt ra cp1252 nên `UnicodeEncodeError`: nay chạy `python -X utf8` và
  đọc đầu ra bằng UTF-8 (tái hiện được trên Linux bằng `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`: 33 ca đỏ
  trước, 0 sau). (3) So đường dẫn bằng `'/'` ghép tay: dùng `os.path.join`. (4) `write_text` / `open(..., "w")` thiếu
  `encoding="utf-8"` với nội dung tiếng Việt.

## 2026-10-14 — Workspace: vòng sửa lỗi thứ ba (hai lượt /code-review cuối, trước khi gộp vào main)

Mỗi mục có test trong `tests/test_ws_sua_loi_3.py` (viết trước, đỏ trước khi sửa):
- **Đọc cấu hình NGHIÊM ở nơi quyết định.** `run_pipeline`, `check_data_integrity`, trần nguyện vọng / thi
  (nhập tay, CSV, sổ), chấm điểm theo CLB đọc bằng `doc_cau_hinh(nghiem=True)` (`PipelineAPI._luat_nghiem`).
  Cấu hình có mà đọc không được (JSON hỏng, khoá của bản khác, CSDL bị khoá) thì dừng với lỗi mới
  `ws_cau_hinh_hong`, không lặng lẽ chạy bằng luật trường học rồi ghi `luat_xep = NULL`. `get_data_health_report`
  vẫn trả báo cáo nhưng thêm cảnh báo mức cao. `run_pipeline` đọc cấu hình MỘT lần (trước: hai lần, hai kết
  nối). Không có hàng cấu hình = mặc định, như cũ.
- `workspace.nhap_zip`: cấu hình trong zip đọc không được thì từ chối cả zip (trước: ghi mặc định đè lên luật thật).
- `update_workspace_config`: cập nhật MỘT PHẦN giữ nguyên phần không nhắc tới (`cau_hinh_ws.tron_len`); trước
  đây trộn lên mặc định trường học nên `{"name": "X"}` đặt lại mọi luật. Cấu hình cũ hỏng thì từ chối.
- `reset_student_entry` ("Sửa lại từ đầu") KHÔNG xoá `diem_ca_nhan` nữa (điểm do giáo viên chấm, không gắn
  với ô tick). *Đổi hành vi so với bản trước; test cũ đổi theo.*
- `delete_workspace` trên workspace "mở tạm" chuyển `db_path` sang workspace còn lại (không để trỏ vào `_trash`).
- `submit_club_scores` từ chối (`scoring_not_per_slot`) khi workspace chấm theo người hoặc `priority = tier`;
  CSV có điểm ở các chế độ đó: không lưu, cảnh báo `csv_score_ignored_mode`.
- Dấu vân tay kết quả, `run_history.luat_xep` và `run_full_pipeline` dùng luật HIỆU LỰC
  (`luat_xep_hieu_luc`): danh sách nhóm khi nhóm không cứng, `score_scope` khi chỉ theo nhóm... không còn
  làm kết quả báo "cũ". Luật mặc định không đổi (vân tay cũ giữ nguyên).
- Sổ nhập: cột điểm sai kiểu chấm (cột "Điểm k" ở workspace chấm theo người, hoặc cột "Điểm" đơn ở workspace
  chấm theo CLB) mà có dữ liệu thì báo `so_nhap_diem_sai_che_do` (trước: bỏ lặng lẽ, điểm mất).
- `xuat_zip` không nén chính zip đích (nằm trong thư mục workspace) và bỏ mọi `*.zip` trong thư mục.
- `main.khoi_dong_workspace`: bỏ qua workspace hỏng khi còn workspace lành (không còn rơi vào màn phục hồi vì một
  workspace hỏng); chỉ khi không cái nào mở được mới ném `WorkspaceKhoiDongHong(db_path)` cho màn phục hồi. Màn
  phục hồi dùng đúng tệp hỏng, hoặc workspace gần nhất khi `app.db` cũ đã di trú (trước: trỏ vào `app.db` không
  còn, "bắt đầu lại" đẻ ra tệp mồ côi).
- Nhóm cứng: nhập CSV không còn cảnh báo `csv_reserve_group_unknown` cho tên nhóm.
- Dọn: bỏ `main.chon_db_path` (chỉ test dùng) và khoá `bo_diem` của `tham_so_luat` (không ai đọc); tên trang
  Excel của tệp xuất dùng chung `so_nhap._ten_sheet`; docstring `cau_hinh_ws.py` nói đúng việc cấu hình
  nối vào thuật toán.
- `docs/ke_hoach/TIEN_DO.md`: thêm hàng WS (ngoài sổ) và ghi chú chồng lấn ở Z1, Z2 (chưa đóng mục).
- Hai việc còn lại sau vòng này (cùng ngày):
  - Mã lỗi riêng `ws_cau_hinh_hong` ở MỌI chỗ phụ thuộc cấu hình (trước chỉ ở chạy xếp / kiểm tra dữ liệu / báo
    cáo sức khoẻ; còn lại ra lỗi chung): nhập tay nguyện vọng và thi, nhập CSV, chấm điểm theo CLB và theo
    người, đọc / xem trước sổ nhập, tạo sổ mẫu, xuất dữ liệu đầu vào, hồ sơ học sinh, trạng thái kết quả. Bố
    cục sổ và tệp xuất cũng đọc cấu hình NGHIÊM (trước: đoán bằng mặc định trường học). Nhãn hiển thị vẫn
    đọc dễ tính. Test: `tests/test_ws_sua_loi_3.py` (mục P).
  - Màn phục hồi lúc khởi động được kiểm bằng `main.main()` thật và Chromium thật
    (`tests/test_ws_phuc_hoi.py`): đúng tệp hỏng trong thư mục workspace, thấy bản sao lưu cạnh nó, bấm
    "Khôi phục" đưa workspace về đúng dữ liệu, lần khởi động sau vào giao diện chính, và lỗi không nêu tệp thì
    dùng workspace gần nhất chứ không phải `app.db` cũ đã di trú.

## 2026-10-14 — Workspace: ghép các nhánh và vòng sửa lỗi sau review (/code-review trên 4 nhánh)

Ghép `practical-faraday` (nền), `cool-hamilton` (tài liệu) và `upbeat-ride` vào nhánh này; bản workspace
cũ của nhánh còn ở `backup/nifty-truoc-khi-ghep`. Sửa các lỗi còn lại, mỗi lỗi một test
(`tests/test_ws_sua_loi_2.py`):
- `workspace.xoa`: workspace có `app.db` hỏng vẫn xoá được (sao lưu rơi về chép tệp thô, rồi dời vào `_trash`).
- `workspace.nhap_zip`: trần 500 MB giải nén cho cả zip, đếm BYTE THẬT khi chép (tiêu đề zip khai sao cũng
  được); bỏ `app.db-journal/-wal/-shm` và `*.bak-*` trong zip (SQLite tự phát lại nhật ký có sẵn); từ chối mục mã hoá.
- Slug: cắt ở 60 ký tự; `con`, `nul`, `com1`... (tên thiết bị Windows) thành `ws-<tên>`.
- `delete_workspace`: workspace "mở tạm" lúc khởi động nhiều workspace (người dùng chưa chọn) xoá được.
- `run_history.luat_xep` (cột mới, `ADD COLUMN`, không dựng lại bảng): JSON luật xếp đã dùng; NULL = luật mặc
  định của trường học (dòng cũ và workspace mặc định không đổi). `get_run_history` trả cột này.
- `run_full_pipeline` (đường thử nghiệm) từ chối chạy khi workspace có luật khác mặc định, thay vì xếp sai
  âm thầm.
- Nhãn workspace bắt đầu bằng `=`, `+`, `-`, `@` bị từ chối (`cau_hinh_ws.chuan_hoa`): nhãn thành tiêu đề cột / tên
  sheet của Sổ nhập, và openpyxl ghi `=...` thành ô công thức thật; nhãn có thể đến từ zip nhập vào. Cấu hình
  như thế đọc lại ra mặc định.
- Test giao diện `test_moi_o_so_tren_man_hinh_cap_nhat_ngay_sau_khi_xoa` hết chập chờn: `#lastRunLine` và
  `#statStudents` do hai lời gọi API riêng điền, test từng assert ngay mà không chờ. Nay chờ `#lastRunLine`, và
  làm chậm `get_last_run_info` 600 ms để thứ tự trả về là chắc chắn (bản assert ngay đỏ ổn định với độ trễ này).
- `docs/ke_hoach/tham_khao`: `verify_stability_nhanh` nhận `bo_qua_du_tru`; bộ nạp `_chung.nap_rb` nạp thêm
  `nhan_ws` (từ bản có workspace, `i18n_errors` import nó), bản build cũ không có thì vẫn nạp được.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng S (/code-review trên vòng R: 6 điểm, không lỗi đúng/sai — vòng sạch)

- Không sửa hành vi. Ba điểm "móc lỗi chặn cả `import json`" là đúng hành vi: tệp `json.py` cạnh mã vẫn che được
  `json`, và lần chạy thật (thư mục đứng đầu sys.path) cũng hỏng ở chính móc đó — sai là ở LỜI: dòng CHANGELOG
  vòng R và chú thích test ghi "thư viện chuẩn" thay vì "dựng sẵn / đóng băng". Đã sửa lời (đánh dấu tại chỗ),
  docstring `_tu_thu_muc` (dòng tóm tắt còn ghi "nghi ngờ thì coi là có"), và thêm ca `import json` bị từ chối
  vào test làm chốt (228 ca, 2 bỏ qua tuỳ môi trường).
- `_khong_the_bi_che` nhớ theo tên (`functools.cache`).
- Bác: tên đã có trong `sys.modules` của tiến trình đo — `sys.modules` của lần chạy thật là của tiến trình khác;
  chỉ đáng kể khi có móc đường dẫn hỏng, đã báo lỗi rõ.
- Vòng lặp 2 dừng tại đây theo tiêu chí "một vòng không còn lỗi đúng/sai được xác nhận".

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng R (/code-review trên vòng Q: 6 điểm, sửa 5, bác 1)

Không điểm nào làm phép đo chạy nhầm mã; đều là chẩn đoán, độ chặt của test và một ca từ chối thừa hiếm gặp.
- `_chung`: lỗi khi xét một tên (móc đường dẫn hỏng với thư mục, lỗi trong bộ tìm / PathFinder) -> SystemExit nêu
  đúng tên và lỗi gốc, thay vì báo nhầm thành "mô-đun anh em"; lỗi móc với thư mục chỉ nêu khi thật sự cần xét
  một tên (mã chỉ import mô-đun dựng sẵn / đóng băng không bị chặn; *sửa ở vòng S: bản đầu ghi nhầm
  "thư viện chuẩn"*).
- Luật "dựng sẵn / đóng băng không bị che" còn một chỗ, đứng trước phép xét thư mục trong `la_ten`.
- Test (227 ca, 2 bỏ qua tuỳ môi trường): bộ tìm cài thêm ghi mọi tên ngoài thư viện chuẩn (không chỉ hai tên);
  ca lỗi PathFinder kiểm cả lỗi gốc và đặt mục lỗi cuối sys.path; 1 ca mới. 3 ca thất bại với bản vòng Q.
- Bác: PathFinder chạy các móc đường dẫn trên sys.path khi xét phần namespace — đó chính là việc mọi import của
  mã được đo làm trong cùng tiến trình; docstring ghi rõ điều này.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng Q (/code-review trên vòng P: 7 điểm, sửa 5, bác 2)

- `_chung`: mô-đun dựng sẵn / đóng băng ngoài `sys.stdlib_module_names` (`__phello__`, `xxsubtype`) lại được nhận
  (hồi quy của vòng P: bỏ ngoại lệ của vòng O mà không thay bằng `_khong_the_bi_che`).
- Móc đường dẫn ném lỗi khác ImportError với thư mục đã chọn -> SystemExit rõ (PathFinder cũng chỉ bỏ qua
  ImportError); mọi lỗi khi tìm phần namespace (kể cả PathFinder trên sys.path) -> coi là có, từ chối rõ — không
  còn traceback. Không móc nào nhận thư mục -> trả ngay hàm luôn "không".
- Test (226 ca, 2 bỏ qua tuỳ môi trường): 3 ca mới, đều thất bại với bản vòng P (đã kiểm là lỗi thật, không phải
  lỗi cú pháp của mã test); bộ tìm cài thêm trong test chỉ ghi tên đang xét (không bắt nhầm import khác);
  `_chay_tien_trinh_moi` nối mã test sau một dòng mới (mã bắt đầu bằng `def` / `try` không còn thành lỗi cú pháp
  lặng lẽ).
- Bác:
  - Không dùng `sys.path_importer_cache[thu_muc]` của tiến trình đo: lần chạy thật là một tiến trình khác, bộ
    nhớ đệm trống, dựng bộ tìm từ `sys.path_hooks` — đúng như kịch bản làm.
  - Mô-đun đóng băng ở tiến trình đo nhưng không đóng băng ở lần chạy thật với cờ / bản Python khác: như vòng O —
    phép đo chạy trong chính trình thông dịch này, đối chiếu là nạp bình thường trong cùng trình thông dịch.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng P (/code-review trên vòng O: 7 điểm, sửa 7)

- `_chung`: **rút lại** việc hỏi các bộ tìm cài thêm trong `sys.meta_path` (vòng O). Đã tái hiện: hỏi
  `DistutilsMetaFinder` của setuptools về `distutils` / `pip` làm đổi trạng thái tiến trình đo; một bộ tìm chuyển
  tiếp cho PathFinder (kiểu móc của pytest / typeguard) làm tệp `pytest.py` cạnh mã lọt qua — lần chạy thật thư
  mục đứng đầu sys.path nên chính bộ tìm đó trả tệp cạnh mã (đo nhầm mã, lặng lẽ).
- Luật mới, bảo thủ (nghi ngờ thì từ chối rõ, không bao giờ đo nhầm): chỉ mô-đun dựng sẵn / đóng băng (hai bộ
  tìm của CPython, không tác dụng phụ) được coi là không thể bị che; bộ tìm của thư mục dựng từ `sys.path_hooks`
  như PathFinder làm (móc đường dẫn kiểu Hy thêm đuôi mới cũng được tính), lỗi khi tìm thì coi là có; phần
  namespace chỉ được nhận khi PathFinder trên sys.path tìm được mô-đun / gói thường. Tên do bộ tìm cài thêm cung
  cấp mà thư mục cũng có thì bị từ chối (ca `hookmod/` của vòng O đổi từ "nhận" sang "từ chối, không gọi bộ tìm").
- Một hàm phân loại duy nhất (`_tu_thu_muc`, nhớ theo tên); bỏ `_bo_tim_truoc_cung_cap` và lần gọi lặp trong
  `la_ten`.
- Test (223 ca, 2 bỏ qua tuỳ môi trường): ca bộ tìm cài thêm của vòng O thay bằng 2 ca bảo thủ (kèm kiểm bộ tìm
  không bị gọi lần nào) + 1 ca `sys.path_hooks`; cả 3 thất bại với bản vòng O.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng O (/code-review trên vòng N: 7 điểm, sửa 5, bác 2)

- `_chung`: sửa tận gốc luật mô-đun anh em — bỏ các luật tự bắt chước hệ thống import (`_anh_em`,
  `_nap_truoc_filefinder`, `_mo_dun_thuong_ngoai`; bốn vòng K–N mỗi vòng lại thấy một chỗ lệch) và hỏi chính các
  bộ tìm theo đúng thứ tự import: bộ tìm trong `sys.meta_path` đứng trước PathFinder (dựng sẵn, đóng băng, móc
  cài thêm) → FileFinder của thư mục đã chọn → PathFinder trên sys.path (gói thường thắng phần namespace).
  Không gọi PathFinder với thư mục đã chọn (giữ sys.path_importer_cache sạch); kết quả nhớ theo tên trong một lần nạp.
- Tên do bộ tìm đứng trước PathFinder cung cấp được nhận (vòng N từ chối nhầm khi có thư mục dữ liệu cùng tên).
- Docstring `_import_la` theo luật mới. Test dựng sẵn / đóng băng bỏ qua trên trình thông dịch không đóng băng `os`.
- Test (221 ca, 2 bỏ qua tuỳ môi trường): 1 ca mới thất bại với bản vòng N; mọi ca của vòng K–N vẫn qua với
  cách làm mới (lưới hồi quy cho lần viết lại).
- Bác:
  - Tệp cạnh mã trùng tên mô-đun đóng băng trên một trình thông dịch KHÁC (phiên bản cũ, `-X frozen_modules=off`):
    kịch bản đo chạy mã trong chính trình thông dịch đang chạy; đối chiếu là nạp bình thường trong cùng trình
    thông dịch đó, không phải một bản Python khác.
  - Thư mục hiện hành nằm trên sys.path của tiến trình kiểm (`python -m`, pytest) che phần namespace: cách chạy
    ghi trong CLAUDE.md (`python <kịch bản> <thư mục>`) không đưa thư mục hiện hành vào sys.path; tình huống cần
    hai bản kho mã lệch nhau ở đúng một tên — xa thực tế, không đáng thêm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng N (/code-review trên vòng M: 8 điểm, sửa 5, bác 3)

- `_chung` (luật mô-đun anh em): mô-đun dựng sẵn / đóng băng (`time`, `os`…) xét TRƯỚC — BuiltinImporter /
  FrozenImporter chạy trước FileFinder nên tệp cùng tên cạnh mã không che được (vòng M từ chối nhầm). Thư mục
  không `__init__` cạnh mã chỉ được nhận khi tên là mô-đun / gói THƯỜNG trên sys.path (PathFinder); gói
  namespace đã cài thì thư mục được gộp vào (`nsgoi.helper` chạy thật lấy từ thư mục) — từ chối (vòng M nhận nhầm).
- Docstring `_import_la` theo luật hiện hành; `importlib.machinery.all_suffixes()`; `with os.scandir(...)`.
- Test (220 ca, 1 bỏ qua khi chạy bằng root): 2 ca mới, đều thất bại với bản vòng M.
- Bác, kèm đường đã lần:
  - Thoát tiến trình qua bí danh (`_s.exit`, `from os import _exit`, `os.abort`) và nhánh except ghi bằng
    thuộc tính / biến bộ (`except errors.ImportError`, `except _LOI`): luật import tuỳ chọn chỉ còn áp cho tên
    KHÔNG có trong thư mục; với tên đó, chạy thật và chạy dưới kịch bản tìm trên cùng sys.path nên hành xử
    giống nhau — sai ở đây chỉ làm thông báo lỗi muộn hơn, không làm phép đo đo nhầm mã. Theo dõi bí danh tốn
    mã hơn lợi ích.
  - Thư mục dữ liệu namespace (vd `mau_csv/`) trong try/except ImportError vẫn bị từ chối: chạy thật gán một
    gói namespace rỗng, dưới kịch bản gán None — hai lần chạy đi hai nhánh khác nhau, từ chối là đúng.
  - Chi phí stat cho mỗi thư mục con: vài chục lần stat mỗi lần nạp, không đáng kể.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng M (/code-review trên vòng L: 10 điểm, sửa 9, bác 1)

- `_chung` (luật mô-đun anh em) bám đúng FileFinder: tính cả bản biên dịch không nguồn (`.pyc`); tên tệp là
  phần trước ĐÚNG đuôi (tệp `random.old.py` không phải `random`); thư mục không có `__init__` chỉ là phần gói
  namespace — không che thư viện chuẩn / gói đã cài, chỉ bị coi là anh em khi tên không có ở đâu khác (vòng L
  từ chối nhầm mã hợp lệ khi có thư mục dữ liệu tên `random/`, `csv/`...).
- Import tuỳ chọn: thân lớp chạy ngay nên được đường lui che (vòng L từ chối nhầm); xét nhánh except ĐẦU TIÊN
  bắt được ImportError theo thứ tự (kể cả `except Exception`), nhánh kết thúc bằng ném lại hay
  `sys.exit` / `os._exit` / `exit` / `quit` không phải đường lui. Điều kiện động (`if STRICT: raise`) không xét
  được tĩnh — coi là đường lui, ghi trong docstring.
- Chỉ kiểm / biên dịch các mô-đun CÒN THIẾU (i18n_errors đã nạp đúng bản thì không đọc lại), dựng đủ rồi mới
  gán. Spec không có bộ nạp và `cached = None` (vòng L chỉ đặt `__cached__`, `__spec__` vẫn trỏ .pyc và
  `importlib.reload` đi vòng qua phép kiểm). `functools.cache` thay danh sách tự chế.
- Test (218 ca, 1 bỏ qua khi chạy bằng root): 8 ca mới thất bại với bản vòng L (ca gói thường `random/__init__.py` đã đúng từ vòng L, giữ
  làm chốt chặn khi thu hẹp luật thư mục).
- Bác: nhãn "ngoài sổ" trái quy tắc 1 của CLAUDE.md — quy tắc cho phép khi đã hỏi; việc này do Truong (chủ dự
  án) yêu cầu trực tiếp, nhãn ghi đúng điều đó.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng L (/code-review trên vòng K: 9 điểm, sửa 8, sửa một phần 1)

- `_chung` (kiểm import): thêm luật **mô-đun anh em** — tên có mặt trong thư mục đã chọn (tệp .py, mô-đun mở
  rộng, thư mục) mà không được phép thì luôn bị từ chối, kể cả nằm trong `try/except ImportError` hay trùng tên
  gói đã cài (vòng K để lọt: `try: import rbda_priority_pipeline` trong i18n_errors; tệp `openpyxl.py` cạnh mã).
  Import tuỳ chọn chỉ được che khi nằm trực tiếp trong khối try (không vào thân hàm / lớp định nghĩa ở đó) và
  nhánh except không chỉ ném lại; nhận cả `except*`. Danh sách gói đã cài quét một lần, chỉ khi cần.
- Kiểm và biên dịch CẢ HAI tệp trước khi chạy tệp nào (vòng K chạy i18n_errors rồi mới đọc mô-đun chính).
  Thông báo nêu đúng tệp được import gì (i18n_errors: không mô-đun nào của kho mã, vì nó nạp trước).
- `__cached__ = None` (không trỏ tới .pyc không tồn tại); `compile(..., dont_inherit=True)`.
- Test (209 ca): khôi phục test "không thêm mục cache bộ tìm" (bỏ ở vòng K là sai: nó chặn hồi quy kiểu chèn
  tạm sys.path); 9 ca mới, đều thất bại với bản vòng K.
- Bác phần còn lại của điểm 6 (không dùng bộ nhớ đệm .pyc): cố ý từ vòng H–I (bản .pyc cũ từng bị dùng nhầm);
  phân tích + biên dịch mô-đun chính tốn ~46 ms mỗi tiến trình, không đáng kể so với phép đo.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng K (/code-review trên vòng J: 10 điểm, sửa 9, bác 1)

- `_chung` (kiểm import tĩnh của vòng J): nhận cả gói đã cài trong site-packages (theo `importlib.metadata.packages_distributions`) — vòng J đã thu hẹp quá mức mà CHANGELOG không ghi; bỏ qua import tuỳ chọn trong khối `try/except ImportError`; `i18n_errors` (nạp trước) không được import `rbda_priority_pipeline` (sẽ lấy nhầm bản khác); import tương đối báo đúng tên mô-đun (`.helpers`, không phải `.helpers.f`); bỏ điều kiện thừa `__future__`.
- Kiểm và biên dịch NGAY LÚC NẠP từ đúng bản đã đọc (`compile(cây ast)` rồi `exec`): không còn khe giữa lúc kiểm và lúc chạy; lỗi đọc / cú pháp / byte NUL thành SystemExit rõ; đã nạp đúng thư mục thì trả bản đã nạp mà không đọc lại tệp.
- Test (199 ca): bỏ test cache không thể thất bại (vòng J); 5 test mới, đều thất bại với bản vòng J.
- Bác: một tệp tên trùng thư viện chuẩn (vd `random.py`) chen trên sys.path — mối nguy chung của mọi chương trình Python, ngoài phạm vi kịch bản; phép kiểm theo đường dẫn của vòng I từng có báo nhầm nặng hơn.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng J (/code-review trên vòng I: 9 điểm, sửa 9)

- `_chung`: đính chính vòng I — phép kiểm "mô-đun anh em" chạy SAU khi nạp nên bỏ lọt import bên trong hàm (đúng kiểu import của mã này; đã tái hiện), từ chối nhầm mô-đun C của thư viện chuẩn trên Windows (`<base>\DLLs`), không dùng tham số `thu_muc`, và để lại mô-đun lạ trong sys.modules. Thay bằng kiểm TĨNH trước khi chạy gì: đọc cả hai tệp nguồn bằng `ast`, lấy mọi import (đầu tệp lẫn trong hàm, kể cả import tương đối) và từ chối tên không thuộc `sys.stdlib_module_names` hay `i18n_errors` / `rbda_priority_pipeline`. Bỏ `_thu_muc_chuan`, `_phu_thuoc_la` (không còn đoán theo đường dẫn, không còn sysconfig). Hai tệp thật của kho qua kiểm (không import lạ).
- Test (195 ca): 4 ca import lạ (đầu tệp, trong hàm, anh em ngay thư mục chọn, import tương đối — đều thất bại với bản vòng I) và kiểm không mô-đun nào bị nạp; 1 ca nhận mô-đun C của thư viện chuẩn; 1 ca thư mục chưa có mục cache vẫn không có sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng I (/code-review trên vòng H: 9 điểm, sửa 8, bác 1)

- `_chung.nap_rb` (thư mục), sửa tận gốc theo điểm "sai tầng": bỏ hẳn cơ chế đoán tệp Python sẽ nạp (`sys.path_hooks`, bộ tìm riêng, các ca .so / gói / namespace — thêm dần từ vòng C tới H). Nay nạp THẲNG `<thư mục>/<tên>.py` bằng `spec_from_file_location`: bản biên dịch cũ, gói cùng tên, gói namespace nằm cạnh không thể chen vào; không đụng sys.path hay cache bộ tìm; không còn đường lỗi traceback từ bộ tìm hay loader cũ. Đổi hành vi có chủ đích: thư mục chỉ có bản biên dịch không kèm nguồn (.pyc) nay bị TỪ CHỐI (kịch bản đo mã nguồn) — đảo lại phần nhận .pyc của vòng C–D.
- Mới: nếu mã được nạp import thêm mô-đun ngoài thư viện chuẩn / site-packages (vd một phiên bản khác import mô-đun anh em, lấy nhầm từ thư mục khác trên sys.path), từ chối thay vì đo lẫn mã. Mã hiện tại chỉ import thư viện chuẩn và `i18n_errors` (đã kiểm).
- Test (190 ca): viết lại nhóm test bộ nạp thư mục theo thiết kế mới (8 test thất bại với bản vòng H vì hành vi đổi có chủ đích hoặc vì mô-đun anh em trước đây lọt).
- Bác: khoá import và "đọc lại sys.modules sau exec" của bộ import — kịch bản chạy một luồng, và `_nap_co_kiem` đã kiểm nguồn của mục sys.modules sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng H (/code-review trên vòng G: 6 điểm, sửa 6)

- `_chung.nap_rb` (thư mục), sửa tận gốc: không còn import theo tên qua sys.path nữa. Hỏi bộ tìm mà CHÍNH Python dùng (gọi `sys.path_hooks` như PathFinder, kể cả hook tuỳ biến, nhưng tạo mới và không ghi cache) lấy spec cho từng mô-đun, rồi nạp ĐÚNG spec đó (`module_from_spec` + `exec_module`, đặt vào sys.modules trước như import). Hệ quả: dự đoán và lần nạp thật không thể lệch; bỏ toàn bộ phần sửa / khôi phục sys.path và `sys.path_importer_cache` (vòng G bỏ sót bước xoá mục cũ trước khi import nên có thể đi qua bộ tìm cũ hoặc mục None — đã tái hiện bằng test); thư mục mất quyền giữa chừng vẫn báo lỗi đọc.
- Test (193 ca): test cache tự gieo mục sẵn có (không còn đúng vô nghĩa khi cache trống); test thư mục đã ở trên sys.path với mục cache cũ None (thất bại với bản vòng G).

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng G (/code-review trên vòng F: 8 điểm, sửa 7, bác 1)

- `_chung`: đính chính vòng F — `nap_rb` vẫn để lại bộ tìm tệp của thư mục trong `sys.path_importer_cache` (vòng F chỉ dọn ở `_tep_se_nap`; đã tái hiện). Nay `_tep_se_nap` dùng một `FileFinder` RIÊNG (cùng thứ tự loại tệp như mặc định) nên không đụng cache toàn cục, và bước import của `nap_rb` trả mục cache về như cũ (không để lại cho thư mục tạm, không thay bộ tìm sẵn có). Kiểm đọc được thư mục bằng `os.scandir` (rẻ); lỗi OSError khi tìm thành SystemExit; docstring nói rõ thư mục không có `<tên>.py` thì nhận đúng thứ Python nạp.
- Test (192 ca): test chmod 000 thật (bỏ qua khi chạy root hay Windows; CI Linux chạy được); `.pyc` trong `__pycache__` bỏ qua khi `cache_tag` là None; 2 test cache bộ tìm (thất bại với bản vòng F); test giả lập lỗi quyền đổi sang `os.scandir` (thất bại với bản vòng F chỉ vì vòng F dùng `os.listdir`).
- Bác: thư mục chỉ có gói `rbda_priority_pipeline/__init__.py` (không có `.py`) được nhận — đúng ý: đó là mã Python sẽ chạy khi import từ thư mục đó; docstring đã ghi rõ.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng F (/code-review trên vòng E: 7 điểm, sửa 6, bác 1)

Không điểm nào làm phép đo sai; đều là thông báo lỗi và độ vững của test.
- `_chung._tep_se_nap`: thư mục không đọc được báo đúng "Không đọc được thư mục" (FileFinder nuốt lỗi quyền rồi trả None nên trước đây báo nhầm "không có mô-đun"); tạo bộ tìm tệp mới mỗi lần và không để lại trong `sys.path_importer_cache`; thông báo nêu cả khả năng "gói cùng tên nằm cạnh". `nap_rb` kiểm mô-đun chính trước, nên thư mục sai báo thiếu `rbda_priority_pipeline`.
- Test (190 ca): test `__pycache__` ghi .pyc vào đúng chỗ và kiểm là có (không thành vô nghĩa khi đặt PYTHONPYCACHEPREFIX); 4 test mới, đều thất bại với bản vòng E.
- Bác: gọi `nap_rb` lần hai trên cùng thư mục sau khi tệp trong đó đổi giữa chừng thì bị từ chối — chỉ là từ chối (đòi tiến trình mới), không bao giờ đo nhầm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng E (/code-review trên vòng D: 8 điểm, sửa 7, bác 1)

- `_chung.nap_rb`, sửa tận gốc: bỏ các luật đoán theo tên tệp (`_co_mo_dun`, phần tiền tố của `_cung_nguon`); hỏi chính bộ import của Python (`importlib.machinery.PathFinder.find_spec`) tệp nào sẽ được nạp từ thư mục, rồi đòi đúng tệp đó sau khi nạp. Hệ quả: .pyc có thẻ trong `__pycache__` (Python không nạp) và hậu tố mở rộng của hệ khác không còn bị nhận nhầm; thư mục chỉ có `__pycache__` báo SystemExit rõ thay vì traceback; bản mở rộng cũ chen trước tệp nguồn vẫn bị từ chối; gói namespace bị chặn ngay ở bước kiểm trước (không phụ thuộc sys.path của máy); thông báo nêu đúng tệp mong đợi; lỗi đọc thư mục thành SystemExit; thông báo "đã nạp nơi khác" nêu nguồn thật (gói namespace, mục None).
- Test (186 ca): 2 test cho hàm mới `_tep_se_nap` (thất bại với bản vòng D chỉ vì hàm chưa có) và 1 test hành vi qua `nap_rb` (thất bại thật với bản vòng D).
- Bác: điểm cũ float và điểm mới Decimal cùng giá trị bị coi là "đổi" — giữ, vì đổi kiểu có thể đổi thứ hạng thật: `Decimal('7.1') > 7.1` (float 7.1 là 7,0999…), nên từ chối là đúng.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng D (/code-review trên vòng C: 6 điểm, sửa 6)

- `_chung.nap_rb`: sửa lỗi do vòng C đưa vào — khi thư mục CÓ `<tên>.py`, chỉ nhận đúng tệp đó; một bản biên dịch cũ (.so/.pyd) nằm cạnh mà Python ưu tiên nạp trước bị từ chối (trước đây vòng C nhận nó và đo nhầm mã cũ). Bản biên dịch không kèm nguồn chỉ được nhận khi KHÔNG có .py, nay cho cả mô-đun chính; gói namespace chen vào được nêu đúng nơi (thay vì "None").
- `exp_resume.kiem_tien_de`: nhận điểm Decimal (không là numbers.Real); chỉ kiểm điểm của dữ liệu mới (điểm em cũ đã phải bằng hệt dữ liệu cũ).
- Test (184 ca): bỏ test tiền đề không có khẳng định (luôn xanh), giữ lý do thành chú thích; 4 test mới, đều thất bại với bản vòng C.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng C (/code-review trên vòng B: 8 điểm, sửa 7, bác 1)

- `exp_resume.kiem_tien_de`: một luật `_so_hop_le` cho mọi số mà `compute_club_priority` sắp (số bốc thăm và điểm): điểm là chuỗi CSV, None, bool, pd.NA hay NaN đều bị từ chối bằng ValueError rõ (trước đây chuỗi / None lọt kiểm rồi gây TypeError giữa `resume_da` — đã tái hiện).
- `_chung.nap_rb`: nhận bản biên dịch không kèm nguồn (`i18n_errors.pyc` trong đúng thư mục) thay vì báo "nạp nhầm"; thông báo lỗi sau khi nạp nêu đúng nguồn thực và nguồn mong đợi.
- Test (181 ca): test tiền đề về NaN chuyển thành tự bỏ qua nếu sau này mã sản phẩm xử lý NaN xác định (không chặn bản sửa đúng); thêm 8 ca điểm không hợp lệ (2 ca NaN thất bại với bản vòng B chỉ vì đổi thông báo lỗi; 6 ca chuỗi / None / bool là lỗi thật) và 1 ca `.pyc`.
- Hồ sơ: đính chính câu "6 test mới đều thất bại" của vòng B; cập nhật ngày ở TIEN_DO.md.
- Bác: từ chối NaN cả ở điểm không ảnh hưởng thứ hạng (em không có trong apps, điểm nhập trước của em mới) — giữ, vì thận trọng: chỉ tốn một lần chạy lại toàn bộ, không bao giờ cho kết quả sai.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng B (/code-review trên vòng A: 7 điểm, sửa 5, bác 2)

- `_chung.nap_rb`: kiểm SAU khi nạp rằng mỗi mô-đun đến đúng từ thư mục / bản build đã chọn — thư mục thiếu `i18n_errors.py` trước đây lặng lẽ lấy tệp cùng tên ở chỗ khác trên sys.path (đã tái hiện), nay từ chối và gỡ mô-đun; mục sys.modules không rõ nguồn (None, mô-đun giả) báo rõ; tệp build không chứa mô-đun cần thiết báo SystemExit thay vì KeyError.
- `exp_resume.kiem_tien_de`: TỪ CHỐI điểm NaN (cả em cũ lẫn em mới) — `compute_club_priority` cho thứ tự phụ thuộc thứ tự đầu vào khi có NaN (đã tái hiện), nên vòng A coi NaN == NaN là sai; chưa nạp mô-đun rbda là RuntimeError (lỗi cài đặt, để người gọi bắt ValueError rồi chạy lại toàn bộ không nuốt mất).
- Test (174 ca): 7 test mới — 6 thất bại với bản vòng A; 1 là test tiền đề chỉ chạy mã sản phẩm (`compute_club_priority` với NaN) nên không phân biệt hai bản (đính chính ở vòng C).
- Bác: (1) em mới đã có trong apps/điểm của dữ liệu cũ làm `resume_da` lệch — thử 5.000 thể hiện ngẫu nhiên có trường hợp này: 0 lệch; (2) bản nhanh gọi `club_choice_function` một lần mỗi CLB làm chậm — đo 10.000 HS: 0,037 s so với 0,034 s, không đáng kể so với giá trị (khớp mọi kiểm tra đầu vào của bản gốc).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng A (2 lần /code-review trên 2386dd7: 20 điểm ~15 khác nhau)

Quyết định của Truong: KHÔNG sửa mã sản phẩm (phân xử em không có thứ hạng trong `club_choice_function` vẫn hoãn); lặp tới khi một vòng không còn lỗi đúng đắn.
- `exp_resume.kiem_tien_de`: mọi vi phạm là ValueError (kể cả chưa nạp rbda); bỏ em mới ở CẢ dữ liệu cũ khi so điểm / apps (điểm nhập trước cho em đến muộn không còn báo nhầm "em cũ đổi"); nhóm dự trữ '' và None coi như một (như `default_reserve_eligible_fn`); điểm NaN không đổi không bị báo đổi; kiểm thứ tự bốc thăm sắp một lần; `resume_test` dùng bản rbda đã nạp.
- `de_xuat_verify_nhanh.py`: lần đầu xét mỗi CLB, gọi đúng lời gọi `club_choice_function` của bản gốc (đang giữ + ứng viên, hàm đủ tư cách và thứ hạng thật) — mọi kiểm tra đầu vào, hiện tại và sau này, chạy y hệt.
- `_chung.py`: một hàm `_nap_co_kiem` cho cả thư mục lẫn bản build (kiểm "đã nạp nơi khác", trả bản đã nạp, gỡ mô-đun dở dang); thư mục lấy theo đường dẫn người dùng đưa (không theo đích liên kết); đường dẫn không tồn tại báo rõ; đọc được tệp PyInstaller < 6 (mục `PYZ-00.pyz`, mục lục dict).
- Test (169 ca): 7 test mới, đều thất bại với bản trước; chuỗi so lỗi chính xác ("thứ tự bốc thăm"); đường dẫn Windows dự phòng thật sự viết khác.
- Bác: gộp đoạn mồi 4 dòng (lý do như trước); thay `compute_club_priority` bằng chèn bisect trong `resume_da` (ghi ở DOI_CHIEU, để khi làm G1); sửa phân xử trong `club_choice_function` (chủ dự án hoãn).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 4 (/code-review trên vòng 3: 9 điểm, sửa 8, bác một phần 1)

- `exp_resume.kiem_tien_de`: số bốc thăm phải là số thực (không chuỗi CSV, không bool, không NaN) — báo ValueError rõ; kiểm sức chứa dùng bản rbda đã nạp kể cả khi `exp_resume.rb` chưa gán (trước đây lặng lẽ bỏ qua).
- `_chung.nap_rb`: so đường dẫn như hệ điều hành (liên kết, hoa/thường Windows) khi nạp lại cùng .exe; nhánh thư mục nạp hỏng cũng gỡ mô-đun dở dang như nhánh bản build.
- Test (162 ca): lần đầu có test cho đường nạp `.exe` (tệp PyInstaller tối thiểu dựng trong test): nạp, nạp lại qua đường dẫn khác, nạp hỏng không để mô-đun dở dang, lệch phiên bản Python; danh sách cấm cả `.index`/`.count`; dùng đúng một bản `_chung` trong tiến trình; sửa chú thích sai (v + 20).
- Bác một phần: kiểm sức chứa trong `kiem_tien_de` lặp lại luật của `club_choice_function` — giữ, vì cần nêu tên CLB trước khi làm việc và chỉ tốn một lần gọi mỗi CLB.

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)

- `exp_resume.kiem_tien_de`: nhận số bốc thăm kiểu số bất kỳ (numpy.int64...), chỉ thiếu / None mới là lỗi; báo rõ CLB có sức chứa mới không hợp lệ (giảm dưới suất dự trữ) thay vì lỗi chung chung về sau.
- `_chung.nap_rb`: thư mục — luôn nạp cả `i18n_errors` từ cùng thư mục (kể cả khi mô-đun chính đã có sẵn); bản build — nạp lại cùng tệp .exe trả bản đã nạp thay vì từ chối; nạp hỏng thì gỡ mô-đun dở dang khỏi sys.modules.
- Test (154 ca): test khoá phá hoà nay phân biệt được bản đúng với bản cũ (thêm ca tách cặp trùng giữ thứ tự, bản chỉ so số bốc thăm từ chối nhầm; đã thử đột biến); bỏ test đo giây, thay bằng danh sách cấm tra `in` (bảo đảm không quét danh sách); dùng chung bộ nạp `_chung.nap_canh`.
- Bác: (1) `verify_stability_nhanh` import `i18n_errors` theo tên — giống hệt bản gốc `verify_stability`, và `nap_rb` bảo đảm cùng thư mục; (2) sửa cách phân xử em không có thứ hạng trong `club_choice_function` — mã sản phẩm, cần mục trong sổ (đã ghi ở DOI_CHIEU_KHO_MA.md).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)

- `exp_resume.kiem_tien_de`: so thứ tự bốc thăm bằng đúng khoá phá hoà của `compute_club_priority` (số bốc thăm, mã em) — số trùng trước đây lọt kiểm; thiếu hoặc rỗng số bốc thăm báo ValueError rõ thay vì KeyError/TypeError.
- `de_xuat_verify_nhanh.py`: luôn gọi hàm đủ tư cách cho ứng viên như bản gốc (trước đây bỏ qua khi CLB còn chỗ, nên lỗi của hàm đó không lộ ra giống bản gốc).
- `_chung.nap_rb`: từ chối cả `i18n_errors` nạp từ nơi khác; bỏ đường dẫn khỏi sys.path sau khi nạp; bản build từ chối khi tiến trình đã nạp mô-đun, và `__file__` của mô-đun nạp từ .exe là đường dẫn ảo trong tệp .exe (trước đây là đường dẫn tương đối, có thể trùng tệp của kho).
- Test: 150 ca; bỏ ngưỡng giây tuyệt đối (chập chờn trên CI), thay bằng tỉ lệ thời gian khi dữ liệu gấp 8 lần.
- Bác: gộp đoạn mồi nạp `_chung` (5 dòng) trong hai kịch bản — không gộp được mà không sửa sys.path (chính là lỗi đã sửa ở vòng trước).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)

- `exp_resume.py` (G1), sửa tận gốc: `resume_da(res0, cu, moi, new_ids)` nhận cả dữ liệu cũ lẫn mới; `kiem_tien_de` (O(dữ liệu), dùng tập hợp) kiểm và TỪ CHỐI với thông báo rõ mọi thay đổi không phải "thêm ràng buộc": em nộp lại / mã trùng, đóng CLB, tăng sức chứa, đổi dự trữ, đổi nguyện vọng / điểm / nhóm / thứ tự bốc thăm của em cũ, em cũ xếp CLB mới mở, apps thiếu nguyện vọng (kể cả res0 lập từ apps thiếu). Hỗ trợ thêm GIẢM sức chứa (chọn lại trên tập đang giữ). Em mới không có dòng nguyện vọng không còn KeyError. `resume_test` đo riêng thời gian kiểm tiền đề.
- `de_xuat_verify_nhanh.py` (Z4): chữ ký trùng `verify_stability` (bỏ tham số `err`, dùng `err` của i18n_errors); chuẩn bị từng CLB một cách lười (chỉ CLB thật sự được xét, như bản gốc); kiểm sức chứa bằng `club_choice_function` của mô-đun đã nạp với ứng viên thật.
- `_chung.py`: `nap_canh` là bản duy nhất của bộ nạp theo đường dẫn; `nap_rb(thu_muc)` báo lỗi khi tiến trình đã nạp bản từ nơi khác (trước đây lặng lẽ trả bản cũ); bản build: báo rõ khi lệch phiên bản Python, đọc được mục lục PYZ dạng dict của PyInstaller cũ.
- `kiem_verify_nhanh.py`: `is not None` khi chọn em để hoán đổi.
- Test: 145 ca (vi sai tiếp tục/chạy lại có giảm sức chứa, CLB mới, em không nguyện vọng; một ca từ chối cho mỗi vi phạm; kiểm tiền đề tuyến tính; bản nhanh không đọc CLB không ai xét; `nap_rb` cùng thư mục / khác thư mục / tiến trình mới).
- Kiểm vi sai ngoài bộ test: `resume_da` = `run_rbda` trên 20.000 thể hiện ngẫu nhiên (có giảm sức chứa, CLB mới); bản nhanh = bản gốc trên 60.000 thể hiện (gồm 3.195 ca sức chứa sai, cùng thông báo lỗi).
- Chưa sửa (mã sản phẩm, cần mục trong sổ): `club_choice_function` xếp em không có thứ hạng bằng `len(rank)` rồi theo thứ tự pool — ghi trong DOI_CHIEU_KHO_MA.md.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)

- `de_xuat_verify_nhanh.py` (Z4): không còn nhập `loi_suc_chua` theo tên và không chép thông báo lỗi; kiểm sức chứa bằng chính `club_choice_function` của mô-đun đã nạp (kho mã hay bản build cũ), nên cùng luật, cùng thông báo.
- `exp_resume.py` (G1): `is not None` ở mọi chỗ (trước đây `held` và `nxt` lệch nhau với CLB có mã rỗng); bỏ ID CLB không tồn tại khỏi tập tính lại thứ hạng; CLB mới sau lần chạy cũ không còn KeyError; em không có dòng nguyện vọng dùng `prefs.get(s, [])` như `run_rbda`.
- `kiem_verify_nhanh.py`, `exp_resume.py`: nạp `_chung` và bản nhanh theo đường dẫn (không sửa sys.path); phần chạy của `kiem_verify_nhanh.py` đặt trong `main()`.
- `tests/test_tham_khao_verify_nhanh.py`: 85 ca (86 sau rà soát bổ sung). Thêm biến đổi kết quả làm CLB thừa/thiếu người, bỏ chỗ; ca thật "em trong nguyện vọng nhưng không trong apps"; dự trữ 0 / một phần / bằng sức chứa; so thông báo lỗi; em mới có diện dự trữ và điểm thi, CLB mới, nguyện vọng trỏ CLB không có, em không có nguyện vọng; kiểm `nap_rb` và `gen`; kiểm phép so sánh không rỗng. Nạp kịch bản theo đường dẫn. 16 ca thất bại với bản `exp_resume.py` trước sửa.
- Rà soát bổ sung (Sonnet, kiểm vi sai ngẫu nhiên): bản nhanh khớp bản gốc trên 600.000 thể hiện (kể cả thứ hạng trùng, sức chứa sai); `resume_da` lệch chạy lại khi em có trong nguyện vọng nhưng không trong apps (em không thứ hạng trùng nhau, phân xử theo thứ tự pool). Đường thật không có ca này (`hop_ung_vien`); `resume_da` nay ghi rõ tiền đề và từ chối dữ liệu như vậy; thêm test phản ví dụ (86 ca).
- Tài liệu: mã tiến độ `RS` (không có trong sổ) đổi thành `GĐ0`; số test trong CLAUDE.md đếm lại; sửa hai dòng mâu thuẫn / lỗi thời trong `DOI_CHIEU_KHO_MA.md`.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)

- `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản đề xuất cho Z4): khớp `club_choice_function` ở mọi ca biên — em đang giữ chỗ không có trong `base_rank` xếp cuối (`rank.get(s, len(rank))`) thay vì ném KeyError; thứ hạng trùng dùng `bisect_right` (khớp sắp xếp ổn định; test mới tìm ra lệch khi dùng `bisect_left`); kiểm `loi_suc_chua` và ném cùng ValueError; `is not None` khi gom em đang giữ; gọi hàm đủ tư cách một lần cho mỗi em.
- `exp_resume.py` (nguyên mẫu G1): bỏ qua nguyện vọng trỏ tới CLB không tồn tại như `run_rbda`; nhập được từ test (phần chạy đặt trong `__main__`, numpy chỉ nạp khi đo).
- Mới `docs/ke_hoach/tham_khao/_chung.py`: một bản duy nhất của bộ nạp `nap_rb` (báo lỗi rõ khi tệp không phải PyInstaller) và bộ sinh `gen`; bỏ bản sao và import thừa trong hai kịch bản.
- `pyproject.toml`: bỏ loại trừ ruff cho `docs/ke_hoach/tham_khao` (đã sửa lỗi lint); giữ loại `docs/*` khỏi đo phủ.
- Test mới `tests/test_tham_khao_verify_nhanh.py` (43 ca, không cần numpy).
- `CLAUDE.md`: cập nhật bản đồ mã theo kho (api.py L784–1364, rollback L1107–1119, `_BANG_RANG_BUOC`, Sổ nhập), số test, thời gian chạy, lệnh verify cần numpy, `CHANGELOG.md`.
- Chạy lại: `kiem_verify_nhanh.py` → `TAT_CA_GIONG_NHAU True` (7/7); `exp_resume.py` → 38/38 khớp chạy lại.

## 2026-10-08 — Giai đoạn 0 (chỉ đọc và đo)

- Môi trường: `.venv` (Python 3.11.17) cài `requirements-dev.txt` và `numpy`; `matching` 1.4.3 cài thêm chỉ để so sánh sau này (Q5), không thêm vào requirements.
- Gói kế hoạch đã có trước đó (commit 7c4f423): `CLAUDE.md`, `docs/ke_hoach/*`, và các loại trừ trong `pyproject.toml` (ruff: `docs/ke_hoach/tham_khao`; phủ: `docs/*`). Giai đoạn 0 không sửa các tệp này.
- Thêm `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`: đối chiếu 33 mục của sổ với kho, kết quả đo và trả lời câu hỏi mở mục 9 của `BOI_CANH_DU_AN.md`.
- Cập nhật `docs/ke_hoach/TIEN_DO.md`: GĐ0 xong; Z1–Z7 đánh dấu chưa.
- Không sửa mã sản phẩm (`.py`, `.js`, `.html`, `.css`).

Số đo chính (dữ liệu mô phỏng):
- Bộ test: 1.287 ca đạt, 0 hỏng, 0 bỏ qua, 0 lỗi; phủ 91,06 %; thời gian 1.352 s. Ruff: sạch.
- Verify nhanh: khớp hoàn toàn ở 7/7 cấu hình (`TAT_CA_GIONG_NHAU True`); 10.000 HS: 6,53 s so với 0,042 s.
- 5.000 HS, 10 CLB: `run_rbda` 0,18 s; `verify_stability` 2,09 s (≈92 % thời gian kiểm tra); 0 cặp phá vỡ.
- Tiếp tục DA từ trạng thái cũ: khớp chạy lại 38/38 lần.
- Sổ 33 mục: 29 đúng, 3 khác (Z1, Z4, Z6), 1 sai (C1).

## CI song song (FA-SC, Truong 2026-11-15)
- `.github/workflows/tests.yml`: bộ test Linux chia 4 phần chạy song song (`.github/chia_test.py`, chia tất định theo kích thước tệp, tệp giao diện nặng ×4), Windows chia 2; job `do-phu` gộp độ phủ (vẫn ≥ 85 %). Mỗi phần chạy lại TRƯỚC các test hỏng ở lần chạy trước của nhánh (`--lf`, cache). Không thư viện mới; mã sản phẩm không đổi.
- `pyproject.toml`: bỏ `.github/*` khỏi đo độ phủ.
