# UX5B-L1 — Kiểm kê + bảng từ ngữ + bản đồ lựa chọn: Xếp CLB, Nhập nguyện vọng, Nhập điểm

> Nhánh `claude/ux5b-nap-xep-nhap-tay`. Người soạn: Sonnet (coder). **MILESTONE 1 ĐÃ DUYỆT (Truong, 2026-11-23): bảng từ ngữ §2, mặc định D1–D6 (§0), bản đồ §3, câu hỏi mở §5 theo mặc định (1: chỉ gập chip; 2: có "Chấm tiếp"; 3: đo ở trạng thái đã chọn một em). Được viết mã L2–L4.**
> Luật: Hick (ít lựa chọn mỗi màn, ≤ 7 ô trước khi mở "thêm") + Von Restorff (một nút vàng mỗi thẻ, đỏ chỉ khi xoá dữ liệu).
> Chỉ giao diện + chữ. Số "hiện nay" đo bằng Chromium thật (dữ liệu MÔ PHỎNG: sổ 120 học sinh, 9 CLB, 3 buổi, điểm quyết tâm bật).
> Cách đếm = đúng cách của test UX4: nút/ô/`summary`/liên kết nhìn thấy và bật, **không tính** hàng trong `tbody`. Thẻ CLB dạng ô chọn
> (`#testSelectionGrid`, `#rankingSourceGrid`) và ô trên khối quyết tâm không phải `button/input` chuẩn nên KHÔNG vào số đếm; xem quyết định D5.
> `{...}` là chỗ giữ của ngành: giữ nguyên ở VI và EN. Khoá có sẵn: đổi chữ tại chỗ; khoá mới tiền tố `ux5b_`.
> Ảnh: `docs/ke_hoach/ux/anh/ux5b/` (3 ảnh, vai quản trị).

## 0. Sáu điều Truong cần quyết (em đã chọn sẵn mặc định; không nói gì = dùng mặc định)

| # | Phát hiện | Mặc định em đề xuất | Vì sao |
|---|---|---|---|
| D1 | Xếp CLB: khi có tệp chờ nhập, **hai nút vàng** cùng hiện (`btnImportAll` "Nhập sổ" và `btnRun` "Chạy sắp xếp"). Bốn khối đều ngang hàng, ba dòng cảnh báo vàng nâu đè lên nút Chạy. | Nút vàng **đi theo bước kế tiếp**: có tệp chờ → "Nhập sổ" vàng, "Chạy" thường; không có tệp chờ → "Chạy" vàng. Cảnh báo thu thành một dòng tóm tắt, mở danh sách khi bấm (tự mở nếu có mục "Nghiêm trọng"). | Luật Von Restorff: một nút nổi bật = việc phải làm ngay. Không mất khả năng nào. |
| D2 | Nhập nguyện vọng: sau khi chọn một em, **ba nút vàng** (Lưu CLB dự thi, Lưu nguyện vọng, Lưu điểm quyết tâm; giáo viên thấy hai) cùng một màn. | Ba bước thành **ba mục gập (accordion), chỉ mục đang làm mở**; nút vàng là nút Lưu của mục đang mở, hai mục kia là dòng tóm tắt một dòng + nút "Sửa". Lưu xong bước 1 thì bước 2 tự mở. **Giữ ba API riêng** (không gộp ba lần lưu), nên payload y như cũ. | Không đổi luồng lưu; giảm 3 vàng → 1. |
| D3 | Giáo viên thấy **ô nhập Điểm quyết tâm đang bật** nhưng không có nút Lưu (nút mang `data-quyen="quan_tri"`) → ô gõ được mà không lưu được. | Giáo viên: ẩn cả mục "Điểm quyết tâm" ở thẻ Nhập nguyện vọng (ẩn, không làm mờ). Quản trị giữ nguyên. | Ô hiện mà không lưu được là nút chết; luật "hidden-not-disabled". Cần Truong duyệt vì đổi những gì giáo viên thấy. |
| D4 | Nhập điểm, trong bảng chấm của một CLB **không có nút quay về danh sách** (muốn quay lại phải bấm lại tên thẻ). | Thêm một nút `.btn-ghost` "‹ Danh sách {slot_sl}" (id mới `btnScoringQuayLai`, gọi lại `loadScoringTab`). | Lối ra rõ ràng; không đổi API. |
| D5 | Ngân sách Hick cho danh sách thẻ {slot_sl} (9 ô ở Bước 1, 9 ô ở Bước 2) là dữ liệu, không phải "lựa chọn ngang hàng". | Test coi cả lưới là **một nhóm** (như `tbody`), đếm riêng ô có `button/input` chuẩn. | Không thể giảm số CLB của một trường; giữ test có ý nghĩa. |
| D6 | "Làm lại từ đầu" trong Nhập nguyện vọng: "Xoá toàn bộ phiếu của {person_l} này" và "Xoá {person_l}" đã nằm trong menu ⋯ (giữ). "Xoá hết" (bỏ thứ tự nguyện vọng trên màn hình, chưa lưu) đang là nút thường cạnh nút vàng. | "Xoá hết" chỉ hiện khi đã có ít nhất một nguyện vọng; vẫn thường (không đỏ: chưa xoá dữ liệu đã lưu). | Giảm một ô khi chưa chọn gì. |

## 1. Kiểm kê số ô nhìn thấy (đo thật, ô bật, ngoài hàng bảng)

| Thẻ / trạng thái | Quản trị: ô | Quản trị: vàng | Giáo viên: ô | Giáo viên: vàng | Ghi chú |
|---|---|---|---|---|---|
| Xếp CLB, chưa nạp sổ | 3 (Tải sổ mẫu, Kiểm tra lại, Nâng cao) + ô thả tệp | 0 | thẻ **ẩn** | — | Chưa có nút nào vàng: người mới không biết bắt đầu từ đâu. |
| Xếp CLB, đã nạp sổ 120 HS | 8 (+ ô thả tệp) | 1 (Chạy) | thẻ **ẩn** | — | Hơn ngân sách 7. Khối "Buổi sẽ xếp" (3 ô buổi + Chọn tất cả) và ô "Nâng cao" chiếm 5 ô. Khi có tệp chờ: +2 ô (Nhập sổ vàng, Bỏ tệp) = **2 vàng**. |
| Nhập nguyện vọng, chưa chọn em | 6 | 0 | 3 | 0 | Admin: thêm 3 ô "tạo em mới" (Mã, Họ tên, Tạo) luôn hiện. |
| Nhập nguyện vọng, đã chọn một em | 27 | **3** | 23 | **2** | Vượt ngân sách (7) gấp ba: 7 nút "xoá" từng nguyện vọng + 4 ô điểm quyết tâm + 4 nút giải thích "i" + ba nút Lưu. |
| Nhập điểm, danh sách CLB | 4 (các nút "Chấm") | 0 | 4 | 0 | Đạt ngân sách. |
| Nhập điểm, đang chấm một CLB | 1 ngoài bảng (+ 64 ô điểm trong bảng) | 1 (Lưu điểm) | 1 | 1 | Đạt ngân sách; thiếu lối quay lại (D4). |

Phát hiện thêm từ ảnh/mã: (a) Xếp CLB lặp hai lần "tiến trình": dải 4 pha (Kiểm tra / Xếp / Ghi / Xuất) **và** danh sách 6 bước dọc; (b) dòng khoá bốc thăm hiện ngay cả khi chưa có gì cần làm với nó; (c) các nút "i" (giải thích điểm quyết tâm) là chữ trần "i" như UX4 đã sửa ở tab Quản lý.

## 2. Bảng từ ngữ (chuỗi nhìn thấy; `=` là giữ nguyên chữ, đã rõ)

### 2.1 Xếp CLB (`#view-pipeline`, chỉ quản trị)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| pipeline_title | Xếp {slot_sl} | = | = | |
| pipeline_desc | Nhập sổ nhập, bấm Chạy để xếp {person_l} vào {slot_sl}, rồi tải kết quả. | Làm ba việc theo thứ tự: nhập sổ, xem cảnh báo, bấm Chạy. | Do three things in order: import the workbook, read the warnings, press Run. | Nói đúng đường đi; bỏ "sổ nhập" lặp |
| ux5b_tt_buoc_nhap (mới) | — | Việc tiếp theo: nhập sổ. | Next: import the workbook. | Dòng trạng thái (chưa có dữ liệu) |
| ux5b_tt_buoc_cho_nhap (mới) | — | Có tệp đang chờ. Bấm "Nhập sổ". | A file is waiting. Press "Import workbook". | Có tệp chờ (D1) |
| ux5b_tt_buoc_chay (mới) | — | Đã nạp {n} {person_l}. Xem cảnh báo rồi bấm "Chạy sắp xếp". | {n} {person_pl} loaded. Read the warnings, then press "Run allocation". | Có dữ liệu, chưa chạy |
| ux5b_tt_buoc_xong (mới) | — | Đã xếp xong. Xem kết quả ở thẻ "Kết quả". | Allocation done. See the results on the "Results" tab. | Sau khi chạy (tên thẻ lấy từ nav) |
| import_panel_title | Nhập dữ liệu | 1. Nhập sổ | 1. Import the workbook | Đánh số bước |
| btn_tai_so_mau | Tải sổ nhập mẫu | = (nút thường, nhỏ) | = | |
| import_hint | Chưa có sổ nhập? Bấm "Tải sổ nhập mẫu" (sổ có đủ mọi cột và bảng giải thích từng cột), điền xong rồi kéo vào ô bên dưới. | Chưa có sổ? Tải sổ mẫu, điền xong rồi kéo vào ô bên dưới. | No workbook yet? Download the sample, fill it in, then drag it into the box below. | Bỏ ngoặc dài |
| health_panel_title | Cảnh báo dữ liệu | 2. Xem cảnh báo | 2. Read the warnings | |
| btn_validate | Kiểm tra lại dữ liệu | Kiểm tra lại | Re-check | Ngắn |
| health_panel_hint | Mục "Nghiêm trọng" sẽ chặn việc chạy cho đến khi sửa xong; các mục còn lại không chặn nhưng có thể làm kết quả sai lệch. Nên xem trước khi chạy. | Cảnh báo "Nghiêm trọng" chặn việc chạy cho đến khi sửa xong. Các cảnh báo khác không chặn. | "Serious" warnings block the run until fixed. Other warnings do not block it. | Một ý mỗi câu |
| ux5b_canh_bao_tom (mới) | — | {n} cảnh báo, {s} nghiêm trọng. Xem chi tiết | {n} warnings, {s} serious. Show details | Dòng gập (tự mở khi s > 0) |
| steps_panel_title | Các bước xử lý | 3. Chạy xếp | 3. Run | |
| ux5b_tuy_chon_chay (mới) | Nâng cao (`nang_cao`, dùng chung) | Tuỳ chọn khi chạy | Run options | Nói rõ bên trong có gì; `nang_cao` giữ cho nơi khác |
| label_seed | Mã bốc thăm | = | = | |
| chon_buoi_title | {session} sẽ xếp | = | = | Đưa vào "Tuỳ chọn khi chạy" |
| btn_run_pipeline | Chạy sắp xếp | = | = | Nút vàng duy nhất (D1) |
| ux2_pha_* (4 pha) | Kiểm tra / Xếp / Ghi / Xuất | = | = | Giữ; danh sách 6 bước dọc gập sau nút "Chi tiết" (đã có `btnChiTietBuoc`) |
| btn_toggle | Hiện/ẩn | Xem lịch sử | Show history | Nói việc làm |

### 2.2 Nhập nguyện vọng (`#view-fallback`, quản trị và giáo viên)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| fallback_title / fallback_desc | Nhập nguyện vọng / Tìm hoặc tạo {person_l}, rồi chọn {slot_sl} dự thi và xếp hạng nguyện vọng. | = (giáo viên) · quản trị: Tìm {person_l}, rồi chọn {slot_sl} dự thi và xếp hạng nguyện vọng. | Find a {person_l}, then choose test {slot_pl} and rank preferences. | Việc "tạo mới" là việc ít dùng, vào mục gập |
| fallback_step0_title | Tìm hoặc tạo {person_l} | Tìm {person_l} | Find a {person_l} | |
| ux5b_tao_moi (mới) | — | Tạo {person_l} mới ▾ | Create a new {person_l} ▾ | Mục gập (`<details>`, chỉ quản trị); chứa ba ô + `btnCreateStudent` (giữ id, giữ chữ) |
| ux5b_tt_chua_chon (mới) | — | Chọn một {person_l} ở trên để bắt đầu. | Pick a {person_l} above to start. | Hiện khi chưa chọn em |
| fallback_step1_title | Bước 1. Chọn {slot_sl} dự thi | = | = | |
| fallback_step1_hint | Mỗi {session_l} chọn tối đa {max_tests} {slot_sl}. Bỏ chọn một {slot_sl} đã chấm {score_l} thì {score_l} đó bị xoá khi bấm Lưu. | = | = | Cảnh báo mất dữ liệu: giữ nguyên |
| btn_save_test_selection | Lưu {slot_sl} dự thi | = | = | Vàng khi Bước 1 đang mở |
| fallback_step2_title | Bước 2. Xếp hạng nguyện vọng | = | = | |
| fallback_step2_hint | Bấm vào {slot_sl} theo thứ tự muốn vào nhất trước, mỗi {session_l} tối đa {max_choices} {slot_sl}. Có thể chọn cả {slot_sl} không có ở Bước 1. | = | = | |
| ranking_current_label | Thứ tự nguyện vọng | = | = | |
| btn_clear_all | Xoá hết | = (chỉ hiện khi đã có nguyện vọng) | = | D6 |
| btn_save_preferences | Lưu nguyện vọng | = | = | Vàng khi Bước 2 đang mở |
| fallback_step3_title | Bước 3. Điểm quyết tâm | = | = | Chỉ quản trị (D3), chỉ khi tính năng bật |
| btn_save_wharton | Lưu điểm quyết tâm | = | = | Vàng khi Bước 3 đang mở |
| fallback_step3_hc_title / btn_save_huy_chuong | Bước 3. Huy chương / Lưu huy chương | = | = | Cùng quy tắc: chỉ mục đang mở có nút vàng |
| ux5b_buoc_xong (mới) | — | Đã lưu: {tom_tat} | Saved: {tom_tat} | Dòng tóm tắt khi mục gập (`{tom_tat}` = "3 {slot_sl} dự thi", "7 nguyện vọng"…) |
| ux5b_sua (mới) | — | Sửa | Edit | Nút thường mở lại mục đã gập |
| btn_xuat_em_nay, btn_reset_entry, btn_delete_student | (menu ⋯) | = | = | Đã đúng chỗ; "Xoá {person_l}" giữ kiểu `nguy-hiem` |
| nút "i" của khối quyết tâm | i | Giải thích | Explain | Cùng sửa như tab Quản lý (UX4) |

### 2.3 Nhập điểm (`#view-scoring`, quản trị và giáo viên)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| scoring_title | Nhập {score_l} | = | = | |
| scoring_desc / scoring_desc_person | Chọn {slot_sl} để chấm. Danh sách chỉ có mã và họ tên, để chấm khách quan. | = | = | Đã rõ, giữ |
| ux5b_tt_diem (mới) | — | {m} {slot_sl} còn {person_l} chưa chấm. | {m} {slot_pl} still have {person_pl} to score. | Dòng trạng thái ở danh sách; "Đã chấm xong hết" khi m = 0 |
| scoring_overview_title | Tiến độ chấm của từng {slot_sl} | = | = | |
| btn_score_link | Chấm | = (nút của {slot_sl} đầu tiên chưa chấm xong là **vàng**: "Chấm tiếp") | = | Một vàng mỗi thẻ; tuỳ chọn (xem câu hỏi mở 2) |
| ux5b_quay_lai (mới) | — | ‹ Danh sách {slot_sl} | ‹ {slot_p} list | D4 |
| btn_save_scores | Lưu {score_l} | = | = | Vàng duy nhất khi đang chấm |
| ux2_rong_chu_cham_nguoi_gv / huong_gv | Chưa có {person_l} nào để chấm. / Nhờ quản trị viên nạp danh sách. | = | = | Đã tốt (UX2-L6) |

## 3. Bản đồ lựa chọn (một nút vàng, cái nào vào "gập")

| Thẻ | Vàng duy nhất | Hiện ngay (≤ 7) | Vào "Tuỳ chọn khi chạy ▾" / mục gập | Ẩn đến khi cần |
|---|---|---|---|---|
| **Xếp CLB** (admin) | "Chạy sắp xếp"; khi có tệp chờ thì "Nhập sổ" (D1) | Ô thả tệp, Tải sổ mẫu, Kiểm tra lại, Chạy, Tuỳ chọn khi chạy (5; +2 khi có tệp: Nhập sổ, Bỏ tệp = 7) | Mã bốc thăm, Buổi sẽ xếp (3 ô + Chọn tất cả), Bốc thăm lại… (8 → 0 ngoài lúc mở) | Danh sách cảnh báo (gập), 6 bước dọc (sau "Chi tiết"), Lịch sử |
| **Nhập nguyện vọng** (admin) | Lưu của mục đang mở | Ô tìm + Tìm, "Tạo {person_l} mới ▾", ⋯, Lưu của mục mở, "Xoá hết" (khi có nguyện vọng) | Ba ô tạo mới, Xuất CSV / Xoá phiếu / Xoá {person_l} (menu ⋯ đã có) | Mục đã lưu gập thành 1 dòng + Sửa; 7 nút "xoá" từng dòng là hàng danh sách |
| **Nhập nguyện vọng** (giáo viên) | Lưu của mục đang mở | Ô tìm + Tìm, ⋯ (chỉ Xuất CSV), Lưu của mục mở | — | Không thấy "Tạo mới", Bước 3 quyết tâm (D3), Xoá phiếu/Xoá {person_l} (đã ẩn) |
| **Nhập điểm** (cả hai vai) | "Lưu điểm" khi đang chấm; ở danh sách: "Chấm tiếp" (tuỳ chọn) | Danh sách: các nút "Chấm" (≤ 7 CLB có người đăng ký hiện nay) + dòng trạng thái; đang chấm: ‹ Danh sách + Lưu điểm | — | 64 ô điểm là hàng bảng |

Ước tính sau thiết kế (đo lại ở L2–L4): Xếp CLB 5 (7 khi có tệp); Nhập nguyện vọng quản trị ≤ 7 khi chưa mở mục nào hiếm; giáo viên ≤ 6; Nhập điểm ≤ 2 khi chấm.

## 4. Không đổi (cam kết)

- Không sửa backend, API, schema, thứ tự pipeline (bất biến 5); mọi `id` giữ nguyên (id mới chỉ thêm: `btnScoringQuayLai`, vài `details`).
- Ba lần Lưu của nhập nguyện vọng vẫn là ba lời gọi riêng, cùng tham số (test "cùng payload" ở L4).
- `data-quyen="quan_tri"` giữ nguyên nghĩa; chuỗi cũ không đổi nghĩa thì không đổi chữ (giữ `test_ws_nhan.py` xanh; chuỗi đổi được thêm vào `SUA_CO_Y` ghi chú `UX5B`).

## 5. Câu hỏi mở (không chặn; em chọn mặc định)

1. Có dựng lại khối "Buổi sẽ xếp" thành một dòng tóm tắt ("Xếp cả 3 buổi") + nút Đổi thay vì để chip trong mục gập? Mặc định: chỉ gập chip vào "Tuỳ chọn khi chạy", dòng tóm tắt khi chỉ chọn một phần.
2. "Chấm tiếp" (vàng) trên CLB đầu tiên chưa chấm xong: có làm không? Mặc định: **có**, vì thẻ danh sách hiện không có nút vàng nào.
3. Test Hick cho thẻ Nhập nguyện vọng đo ở trạng thái "đã chọn một em" (trạng thái đông nhất) cho cả hai vai.
