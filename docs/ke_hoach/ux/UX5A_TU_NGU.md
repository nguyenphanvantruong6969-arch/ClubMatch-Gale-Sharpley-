# UX5A-L1 — Đo hiện nay, bảng từ ngữ, bản đồ lựa chọn của nhóm "Kết quả & phiếu"

> Nhánh `claude/ux5a-ket-qua-de-hieu`. Người soạn: Sonnet (coder). **Chờ Truong duyệt trước khi viết mã L2–L4.**
> Phạm vi: thẻ `Kết quả` (`#view-results`) và thẻ `Chi tiết và xuất tệp` (`#view-others`), cả quản trị lẫn giáo viên (`body[data-vai="giao_vien"]`).
> Luật: Hick (ít lựa chọn mỗi màn) + Von Restorff (một nút vàng; đỏ chỉ cho việc phá dữ liệu). Chỉ giao diện + chữ.
> Số đo bằng Chromium thật (1280×900), dữ liệu MÔ PHỎNG: sổ 120 học sinh, 9 CLB, 4 lớp 10A1–10A4, đã chạy xếp (seed 42), điểm quyết tâm tắt, các cờ FA (điểm danh, khiếu nại, vòng 2, phản hồi) tắt.
> "Điều khiển" = nút, ô chọn, ô gõ, ô tick, dòng `<summary>` nhìn thấy và bật; không tính hàng trong `tbody`. `{...}` là chỗ giữ của ngành, giữ nguyên VI + EN.

## 0. Sáu điều Truong cần quyết (em đã chọn sẵn mặc định; không nói gì = dùng mặc định)

| # | Phát hiện | Mặc định em đề xuất | Vì sao |
|---|---|---|---|
| D1 | Thẻ Kết quả hiện **không có nút vàng nào** khi đóng nếp gập "Mã tra cứu…"; khi mở thì nút vàng là `btnGtCheDoHs` ("Chế độ học sinh tra cứu"), tức bước **cuối** của 4 bước và là bước khoá cả máy. | Nút vàng duy nhất của thẻ = **"Tải bảng này (Excel)"** (`btnKqTaiBang`), việc kế tiếp tự nhiên sau khi xem bảng. Cả ba nút trong "Mã tra cứu…" là nút thường. | Vàng phải chỉ việc nên làm tiếp, không phải việc hiếm và nặng. Giáo viên cũng thấy nút này. |
| D2 | Luật chấm "≤ 1 vàng mỗi khung" cho phép thẻ **Chi tiết và xuất tệp** có tới 4 nút vàng cùng lúc khi bật cờ FA ("Xuất kết quả (Excel)", "Gửi khiếu nại", "Chạy vòng 2", và "Gửi" ở thẻ Kết quả). | Siết thành **≤ 1 vàng mỗi THẺ**: vàng của thẻ Chi tiết = "Xuất kết quả (Excel)"; "Chạy vòng 2" và "Gửi khiếu nại" thành nút thường; "Gửi" (phản hồi, thẻ Kết quả) thành nút thường vì vàng của thẻ là "Tải bảng này". | Nếu bốn nút cùng vàng thì không nút nào nổi (Von Restorff). Không mất khả năng nào. |
| D3 | Ngân sách Hick đếm ở **trạng thái nếp gập đóng**; cột tiêu đề bảng (nút sắp xếp trong `thead`) **không tính** là lựa chọn (đó là chính cái bảng). | Chốt như vậy và ghi vào test. | Cùng quy ước UX4 (không tính `tbody`). Nếu tính cả `thead` thì bảng kết quả luôn thừa 5–6 điều khiển, vô nghĩa. |
| D4 | Nút "Xuất CSV học sinh đã chọn" / "Bỏ chọn" và ô tick "Hồ sơ học sinh đã chọn" đang **hiện nhưng tắt** từ đầu (trái luật "ẩn, không chỉ tắt"). | Ẩn cho tới khi tick ít nhất một em (ô đếm `hsDaChonDem` vẫn hiện số em đã chọn). Giữ id. | Luật Hick của UX4: việc trên hàng đã chọn chỉ hiện sau khi chọn. |
| D5 | Chữ **do JS ghi** ở thẻ Chi tiết còn "suất" ("0 suất chưa dùng", "Suất ưu tiên bỏ phí: 0/9", chú giải "Suất thường / Vào bằng suất ưu tiên", tiêu đề "Suất ưu tiên đã dùng"), "Chọi cao nhất", "Được CLB nguyện vọng 1". | Thay bằng từ UX4 đã dùng ("chỗ dành riêng", "chỗ thường"): đổi chữ khoá có sẵn tại chỗ khi khoá chỉ dùng ở thẻ này; khoá dùng chung với thẻ khác thì thêm khoá `ux5a_*`. Không sửa backend. | Học sinh/giáo viên không hiểu "suất". Từ vựng thống nhất với thẻ Quản lý. |
| D6 | Giáo viên thấy ở thẻ Chi tiết: ô tick "Dữ liệu đầu vào hiện tại: một Sổ nhập CLB" và bảng "Số bốc thăm theo buổi". | **Giữ nguyên.** `phan_quyen.py` cho giáo viên `export_du_lieu_dau_vao`, `export_ket_qua`... chủ ý ("xem, xuất, nhập điểm và điểm danh"); bảng bốc thăm được công bố để kiểm lại. Em chỉ đổi chữ, không đổi quyền. | Đổi quyền là việc backend, ngoài UX5A. Em ghi lại để Truong biết, không tự đổi. |

## 1. Số đo hiện nay (điều khiển nhìn thấy, bật, mỗi khung)

### 1.1 Thẻ Kết quả

| Khung | Quản trị (nếp gập đóng) | Quản trị (mở "Mã tra cứu…") | Giáo viên | Nút vàng (quản trị / giáo viên) |
|---|---|---|---|---|
| Tra cứu một học sinh (`gtPanel`) | 2 (ô gõ, "Mã tra cứu…") | 5 (+ Tạo mã, Xuất mã CSV, Chế độ học sinh tra cứu) | 1 (ô gõ) | 0 / 0 → khi mở: **1** (`btnGtCheDoHs`) |
| Theo lớp và báo cáo (`ux1bPanel`) | **5** (Chọn lớp + 4 nút ngang hàng) | 5 | **5** | 0 / 0 |
| Bảng kết quả (khung thứ ba) | 10 (3 nút xem theo, Tải bảng, ô chọn lớp, 5 tiêu đề cột sắp xếp) → **5** nếu không tính `thead` | 10 | 10 → 5 | 0 / 0 |
| **Cả thẻ** | **17** | 20 | **16** | **0 / 0** (1 khi mở nếp) |
| Chiều cao thẻ | ~1840 px (bảng 120 dòng) | | ~1720 px | |

Khung "Ý kiến về kết quả xếp CLB" (`phanHoiPanel`, chỉ khi bật cờ phản hồi): 1 ô gõ + 5 nút điểm 1–5 + 2 nút Có/Không + 5 nút "khó nhất" + "Gửi" (vàng) = **14**, không đo trên dữ liệu thử vì cờ tắt. Xử lý ở mục O1 (tuỳ chọn).

### 1.2 Thẻ Chi tiết và xuất tệp

| Khung | Quản trị (đóng) | Quản trị (mở hết) | Giáo viên (đóng / mở hết) | Vàng |
|---|---|---|---|---|
| Đầu trang (`btnThuGonTatCa`) | 1 | 1 | 1 / 1 | 0 |
| Xuất dữ liệu (`xuatPanel`) | 4 ("Tuỳ chọn khác", **Xuất kết quả (Excel)**, Xuất theo lớp, "Xuất…") | 8 (+ 3 ô tick, "Chọn học sinh…") | 3 / 7 | **1** |
| Theo từng CLB / Chỗ dành riêng / Số CLB mỗi học sinh / Mức đáp ứng / Chưa có CLB | 1–2 mỗi khung (nút thu gọn, + ô sắp xếp ở khung đầu) | 1–2 | 1–2 | 0 |
| Số bốc thăm theo buổi | 2 (nút thu gọn, ô tìm) | 2 | 2 | 0 |
| Chi tiết để kiểm tra (`dsXepPanel`) | 4 (nút thu gọn, tìm, lọc lớp, sắp xếp) | 6 (+ "Hiện cả học sinh chưa xếp", chọn tất cả) → 8 khi đã tick em | 4 / 6 | 0 |
| **Cả thẻ** | **21** | **27** | **19 / 25** | **1** |

Khung chỉ hiện khi bật cờ FA (không đo): Điểm danh (1 ô chọn + Xuất), Mời vào chỗ trống, Khiếu nại (3 ô nhập + **Gửi khiếu nại vàng**), Vòng 2 (ô chọn + **Chạy vòng 2 vàng**), Phản hồi học sinh (3 nút nạp/xuất). Khi bật hết, thẻ có tới 3 nút vàng ở thẻ này (xem D2).

### 1.3 Chữ khó nhìn thấy khi mở hết nếp gập

| Chỗ | Chữ | Vấn đề |
|---|---|---|
| Thẻ Chi tiết | "Suất ưu tiên đã dùng", "0 suất chưa dùng", "Suất ưu tiên bỏ phí: 0/9", "Suất thường", "Vào bằng suất ưu tiên" | "suất" |
| Thẻ Chi tiết | "Chọi cao nhất" (ô sắp xếp), "Học sinh trên mỗi chỗ" | khẩu ngữ khó hiểu |
| Thẻ Chi tiết | "Được CLB nguyện vọng 1: 24.2%" (dòng mục tiêu) | lẫn "CLB nguyện vọng 1" |
| Thẻ Kết quả | mô tả thẻ dài 2 dòng, nhắc "khung tra cứu (dành cho quản trị và giáo viên)" | dài, trộn ba việc |
| Cả hai thẻ | không còn ngày ISO, "cấu hình", "quỹ" (đã quét) | đạt |

## 2. Bản đồ lựa chọn (một nút vàng mỗi thẻ; mọi thứ ẩn vẫn tới được ≤ 2 lần bấm, id giữ nguyên)

### 2.1 Thẻ Kết quả

| Khung | Nay (QT/GV) | Sau (QT/GV) | Đi đâu | Vàng |
|---|---|---|---|---|
| Tra cứu một học sinh | 2 / 1 | 2 / 1 | Giữ ô gõ; "Mã tra cứu…" vẫn là nếp gập (quản trị); trong nếp: Tạo mã, Xuất mã, Chế độ học sinh tra cứu đều nút thường (D1); thêm 1 dòng mục đích | — |
| Theo {cohort_l} và báo cáo | 5 / 5 | **3 / 3** (Chọn {cohort_l}, **Xuất theo {cohort_l}**, nếp "Báo cáo và phiếu in ▾") | "Báo cáo tổng hợp", "Báo cáo tổng hợp (PDF)", "In phiếu cả {cohort_l}" vào nếp `<details class="menu-khac">` mới `ux1bThemMenu` (≤ 2 lần bấm) | — |
| Bảng kết quả | 5 / 5 (không tính `thead`) | 5 / 5 | Không đổi; "Tải bảng này (Excel)" thành nút vàng; 1 dòng mục đích ngắn trên bảng | **`btnKqTaiBang`** |
| Ý kiến về kết quả (O1, cờ bật) | 14 | ≤ 7 | Nút "Gửi" thường; câu "Phần nào khó nhất?" (5 lựa chọn) vào nếp "Thêm ý kiến ▾" | — |
| **Cả thẻ** | **17 / 16** | **10 / 9** | | **1** |

### 2.2 Thẻ Chi tiết và xuất tệp

| Khung | Nay (QT/GV) | Sau (QT/GV) | Đi đâu | Vàng |
|---|---|---|---|---|
| Đầu trang + Tóm tắt | 1 | 1 | `btnThuGonTatCa` giữ; thêm tiêu đề nhóm "Số liệu chi tiết" trên 7 khung gập để trang đọc thành ba phần: Tóm tắt → Xuất → Số liệu chi tiết | — |
| Xuất dữ liệu | 4 / 3 | 4 / 3 (đóng nếp) | "Tuỳ chọn khác" đổi tên "Chọn thêm tệp để xuất"; menu "Xuất…" đổi "Xuất tệp khác ▾" (quản trị, giữ id `xuatMenu`); dòng gợi ý về chế độ huy chương chuyển **vào trong menu**; 3 đoạn gợi ý hiện luôn → 1 đoạn + dòng cảnh báo đỏ | **`btnXuatTuyChon`** |
| 5 khung số liệu gập sẵn + Bốc thăm | 1–2 mỗi khung | không đổi | giữ gập sẵn; đổi chữ (D5) | — |
| Chi tiết để kiểm tra | 4 → 8 | 4 (đóng) → 6 khi mở → "Xuất CSV…/Bỏ chọn" chỉ hiện khi đã tick (D4) | | — |
| Khung FA (O2, cờ bật) | mỗi khung 1 vàng | "Chạy vòng 2", "Gửi khiếu nại" thường (D2) | | — |
| **Cả thẻ** | **21 / 19** | **21 / 19** (đóng); chữ ít hơn 2 đoạn | | **1** |

Ghi chú: thẻ Chi tiết đã khá gọn về số điều khiển (phần lớn là nút gập). Lợi ích chính của L3 là **chữ** (D5), một nút vàng chắc chắn, và bớt đoạn gợi ý, không phải bớt nút.

## 3. Bảng từ ngữ

Ghi chú cột: **=** giữ nguyên. Khoá mới tiền tố `ux5a_`. "Chung" = khoá dùng ở thẻ khác → thêm khoá mới, không sửa khoá cũ. Mọi khoá đổi tại chỗ được thêm vào `SUA_CO_Y` (nhãn `UX5A`) của `tests/test_ws_nhan.py`.

### 3.1 Thẻ Kết quả

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| kq_title | Kết quả | = | = | đã rõ |
| kq_desc | Xem {person_l} học {slot_sl} nào. Bảng này không có điểm hay số bốc thăm; khung tra cứu (dành cho quản trị và giáo viên) cho xem chi tiết riêng của từng {person_l}. | Xem {person_l} học {slot_sl} nào, tra vì sao một {person_l} được xếp như vậy, hoặc xuất theo {cohort_l}. Bảng không có điểm hay số bốc thăm. | See which {slot_sl} each {person_l} is in, look up why, or export by {cohort_l}. The table shows no scores or draw numbers. | một câu nói đủ ba việc của thẻ |
| gt_tieu_de | Tra cứu một {person_l} | = | = | |
| ux5a_gt_mo_ta (mới) | — | Gõ tên hoặc mã để xem vì sao {person_l} đó được (hoặc không được) vào từng {slot_sl}. | Type a name or ID to see why that {person_l} did or did not get each {slot_sl}. | một dòng mục đích cho khung |
| gt_tim_ph | Gõ tên hoặc mã {person_l} để xem vì sao | Tên hoặc mã {person_l} | {person_l} name or ID | mô tả đã chuyển lên dòng mục đích |
| ux1b_ma_tra_cuu | Mã tra cứu… | Mã tra cứu cho {person_l} tự xem… | Lookup codes for {person_pl}… | nói việc làm được |
| gt_che_do_hs | Chế độ {person_l} tra cứu | Khoá máy cho {person_l} tự tra cứu | Lock this screen for {person_pl} to look themselves up | nút này khoá cả máy; nói rõ |
| gt_buoc_3 | Chế độ {person_l} tra cứu | Khoá máy cho {person_l} tự tra cứu | Lock this screen for {person_pl} to look themselves up | cùng nhãn với nút |
| gt_tao_ma, gt_xuat_ma, gt_buoc_1/2/4, gt_in_mot, xp1_luu_pdf | | = | = | đã rõ |
| ux1b_tieu_de | Theo {cohort_l} và báo cáo | = | = | |
| ux5a_ux1b_them (mới) | — | Báo cáo và phiếu in ▾ | Reports and printouts ▾ | nhãn nếp gập |
| btn_xuat_theo_lop | Xuất theo {cohort_l} | = | = | giữ (dùng ở hai thẻ) |
| ux1b_bao_cao_hint | Báo cáo tổng hợp chỉ có số liệu gộp (lấp đầy từng {slot_l}, mức hài lòng, số {person_l} chưa có {slot_l} theo {cohort_l}); không có tên, mã hay điểm. | Báo cáo tổng hợp chỉ có số liệu gộp: mức lấp đầy từng {slot_l}, mức hài lòng, số {person_l} chưa có {slot_l} theo {cohort_l}. Không có tên, mã hay điểm. | The summary report has totals only: how full each {slot_l} is, satisfaction, and {person_pl} without a {slot_l} by {cohort_l}. No names, IDs or scores. | hai câu ngắn; hiện trong nếp |
| kq_aria_tang1, kq_theo_lop/clb/ma | | = | = | |
| kq_tai_bang | Tải bảng này (Excel) | = | = | |
| ux5a_kq_mo_bang (mới) | — | Bảng cho biết mỗi {person_l} học {slot_sl} nào ở từng {session_l}. | The table shows which {slot_sl} each {person_l} attends in each {session_l}. | một dòng trên bảng |
| ph_tieu_de (O1) | Ý kiến về kết quả xếp CLB | Ý kiến của {person_l} về kết quả | {person_pl}' views on the result | ít từ viết tắt |
| ph_cau_kho | Phần nào khó nhất? | Phần nào khó nhất? (không bắt buộc) | Which part was hardest? (optional) | nằm trong nếp "Thêm ý kiến" |
| ux5a_ph_them (mới, O1) | — | Thêm ý kiến ▾ | More feedback ▾ | |

### 3.2 Thẻ Chi tiết và xuất tệp

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| others_title | Chi tiết và xuất tệp | = | = | đã rõ |
| others_desc | Xuất tệp Excel và xem số liệu chi tiết của lần xếp. | Tải kết quả về máy và xem số liệu chi tiết của lần xếp vừa chạy. | Save the result to this computer and see the figures behind the latest run. | "tải về" dễ hiểu hơn "xuất tệp" |
| ux5a_nhom_chi_tiet (mới) | — | Số liệu chi tiết | Detailed figures | tiêu đề nhóm cho 7 khung gập |
| xuat_title | Xuất dữ liệu | Tải kết quả về máy | Save results | nói việc làm được |
| xuat_tuy_chon_khac | Tuỳ chọn khác | Chọn thêm tệp để xuất | Choose more files to save | nói rõ bên trong có gì |
| btn_xuat_tuy_chon | Xuất kết quả (Excel) | = | = | nút vàng, giữ |
| ux1a_xuat_menu | Xuất… | Xuất tệp khác ▾ | More files ▾ | khớp mẫu "Thêm ▾" của UX4 |
| xuat_opt_ket_qua | Kết quả sắp xếp: một tệp Excel (danh sách {person_l}, từng {slot_sl}, {person_l} chưa có chỗ, thống kê) | Kết quả xếp, một tệp Excel (danh sách {person_l}, từng {slot_sl}, {person_l} chưa có chỗ, thống kê) | Placement result, one Excel file ({person_pl}, each {slot_sl}, {person_pl} without a place, statistics) | bỏ chữ "sắp xếp" lặp |
| xuat_opt_dau_vao | Dữ liệu đầu vào hiện tại: một Sổ nhập CLB nạp lại được | Dữ liệu đầu vào hiện tại, một Sổ nhập CLB để nạp lại | Current input data, one workbook that can be loaded again | |
| xuat_opt_kem_csv, xuat_opt_thay_doi, xuat_opt_hoc_sinh, btn_chon_hoc_sinh | | = | = | đã rõ |
| xuat_hint_hoc_sinh | Hồ sơ {person_l}: bấm "Chọn {person_l}…" rồi đánh dấu trong bảng bên dưới. | = | = | giữ (có test snapshot) |
| xuat_fa_an_goi_y | Các nút xuất lý do kết quả, bảng nhu cầu, gợi ý chỉ tiêu và biên bản bốc thăm chỉ hiện khi bật chế độ "Xếp theo loại {slot_l} và huy chương". | Muốn xuất thêm lý do kết quả, bảng nhu cầu, gợi ý chỉ tiêu, biên bản bốc thăm: bật chế độ "Xếp theo loại {slot_l} và huy chương" ở thẻ Quản lý. | To also save reasons, demand table, capacity hints or the draw record, turn on "Placement by {slot_l} type and medals" in Manage. | nói việc cần làm; chuyển vào trong menu |
| xuat_theo_lop_hint | Xuất theo {cohort_l}: mỗi {cohort_l} một tệp bảng tính, chỉ có kết quả xếp, không có điểm hay số bốc thăm. Gửi được cho giáo viên chủ nhiệm. | Xuất theo {cohort_l}: mỗi {cohort_l} một tệp, chỉ có kết quả xếp, không có điểm. Gửi được cho giáo viên chủ nhiệm. | Export by {cohort_l}: one file per {cohort_l}, placement only, no scores. Safe to send to form teachers. | ngắn hơn |
| xuat_canh_bao_diem | Tệp xuất có {score_l} chấm và số bốc thăm. Không gửi các tệp này cho giáo viên chấm {score_l}. | Các tệp khác có {score_l} chấm và số bốc thăm. Đừng gửi cho giáo viên chấm {score_l}. | The other files contain scores and draw numbers. Do not send them to teachers who mark scores. | rõ "tệp nào"; giữ dòng đỏ (cảnh báo riêng) |
| clb_title | Theo từng {slot_l} | = | = | |
| fill_sap_xep_choi | Chọi cao nhất | Nhiều {person_l} muốn nhất | Most {person_pl} wanting it | bỏ khẩu ngữ |
| ux5a_th_ti_le_choi (mới; th_ti_le_choi chung) | {person} trên mỗi chỗ | {person} muốn mỗi chỗ | {person} per place | rõ hơn (giữ nếu Truong thấy ổn) |
| legend_general | Suất thường | Chỗ thường | Normal places | bỏ "suất" (khoá chỉ dùng thẻ này, đổi tại chỗ) |
| legend_reserve | Vào bằng suất ưu tiên | Vào bằng chỗ dành riêng | Filled from kept places | |
| du_tru_title | Suất ưu tiên đã dùng | Chỗ dành riêng đã dùng | Kept places used | |
| du_tru_desc | Suất ưu tiên không ai dùng sẽ thành suất thường, và phần ưu tiên dành cho nhóm đó không còn tác dụng. | Chỗ dành riêng không ai dùng sẽ thành chỗ thường. | Kept places nobody uses become normal places. | một câu |
| du_tru_khong_co | Chưa {slot_l} nào đặt suất ưu tiên. | Chưa {slot_l} nào dành riêng chỗ cho nhóm ưu tiên. | No {slot_l} keeps places for a priority group yet. | |
| dem_suat | {n} suất chưa dùng | {n} chỗ dành riêng chưa dùng | {n} kept places unused | |
| du_tru_tieu_diem | Suất ưu tiên bỏ phí: {thua}/{tong} | Chỗ dành riêng chưa ai dùng: {thua}/{tong} | Kept places nobody used: {thua}/{tong} | |
| kpi_du_tru_thua | Suất ưu tiên bỏ phí | Chỗ dành riêng chưa ai dùng | Kept places nobody used | |
| th_reserve_capacity (chung) | Suất ưu tiên | dùng `ux4_cho_rieng_cot` ("Chỗ dành riêng", đã có từ UX4) | Kept places | không thêm khoá mới |
| mt1_kq_nv1 | Được {slot_s} nguyện vọng 1: {pct}% | {pct}% {person_l} được {slot_sl} mình xếp đầu tiên | {pct}% of {person_pl} got their first choice | bỏ "CLB nguyện vọng 1" |
| nv_title, do_phu_title, chua_co_cho_title, tham_title, results_list_title | | = | = | đã rõ |
| aria_thu_gon_muc | Thu gọn hoặc mở rộng mục này | = | = | |
| v2_chay (O2) | Chạy vòng 2 | = | = | chỉ đổi kiểu nút thành thường |
| kn_gui (O2) | Gửi khiếu nại | = | = | chỉ đổi kiểu nút thành thường |

### 3.3 Từ cấm trong chữ nhìn thấy (test L4)

"cấu hình", "suất", "Chọi", ngày ISO `yyyy-mm-dd hh:mm:ss`, "quỹ", "tier", "reserve" — đều không được xuất hiện trong chữ thấy được của hai thẻ, cho cả quản trị lẫn giáo viên, khi đã mở hết nếp gập.

## 4. Phần tuỳ chọn (bỏ được không cần hỏi)

- **O1** khung Phản hồi học sinh ở thẻ Kết quả (cờ bật): gập câu "khó nhất" vào "Thêm ý kiến ▾".
- **O2** khung FA ở thẻ Chi tiết (điểm danh, mời, khiếu nại, vòng 2, phản hồi): chỉ đổi kiểu nút theo D2; không dời bố cục.
- **O3** dòng trạng thái xuất (`xuatFeedback`, `ux1bPhanHoi`, `kqXuatPhanHoi`) nháy sáng ngắn sau khi xuất xong (tôn trọng `prefers-reduced-motion` và `html.tat-hieu-ung`; ý nghĩa vẫn có trong chữ).

## 5. Kế hoạch L2–L4 sau khi duyệt (tóm tắt)

- **L2 thẻ Kết quả:** dòng mục đích (`kq_desc` mới + `ux5a_gt_mo_ta`), nếp `ux1bThemMenu`, `btnKqTaiBang` thành vàng, `btnGtCheDoHs` thành thường, bỏ vàng của "Gửi" (O1).
- **L3 thẻ Chi tiết và xuất tệp:** đổi chữ D5, tiêu đề nhóm, dời gợi ý huy chương vào menu, gộp gợi ý, ẩn nút theo hàng đã chọn (D4), O2.
- **L4 giáo viên + test:** `tests/test_giao_dien_ux5a_*.py` (ngân sách Hick và Von Restorff cho hai thẻ × hai vai, mở hết nếp, chữ cấm, id còn nguyên, EN khớp VI); `SUA_CO_Y`; `kiem_nhanh.py` 7/7; `test_i18n_sync.py`, `test_ws_nhan.py` xanh.

Ngân sách chốt cho test (quản trị / giáo viên, nếp đóng, không tính `thead`/`tbody`): Tra cứu ≤ 2/1 · Theo lớp và báo cáo ≤ 3 · Bảng ≤ 5 · Xuất dữ liệu ≤ 4/3 · mỗi khung số liệu ≤ 2 · Chi tiết để kiểm tra ≤ 4 (≤ 6 khi mở, ≤ 8 sau khi tick); nút vàng thấy được: đúng 1 mỗi thẻ; `.btn-danger` thấy được: 0.
