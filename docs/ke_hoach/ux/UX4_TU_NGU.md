# UX4-L1 — Bảng từ ngữ + bản đồ lựa chọn của thẻ Quản lý

> Nhánh `claude/ux4-quan-ly-de-hieu`. Người soạn: Sonnet (coder). **Chờ Truong duyệt trước khi viết mã L2–L4.**
> Quy tắc: luật Hick (ít lựa chọn mỗi màn) + Von Restorff (một nút vàng, đỏ cô lập). Chỉ giao diện + chữ.
> Số "hiện nay" đo bằng Chromium thật (dữ liệu MÔ PHỎNG: sổ 120 học sinh, 9 CLB, một workspace, điểm quyết tâm tắt).
> `{...}` là chỗ giữ của ngành (`{person_l}`, `{slot_sl}`, `{session_l}`…): giữ nguyên ở cả VI và EN.
> Khoá có sẵn: đổi chữ tại chỗ (VI + EN). Khoá dùng chung với thẻ khác (th_capacity, th_buoi, th_reserve_*, th_club_id, th_name_short): thêm khoá mới `ux4_*` cho thẻ Quản lý, giữ khoá cũ.

## 0. Năm điều Truong cần quyết (em đã chọn sẵn mặc định; không nói gì = dùng mặc định)

| # | Phát hiện | Mặc định em đề xuất | Vì sao |
|---|---|---|---|
| D1 | **Đã có sẵn một câu hỏi ba thẻ trùng ý L4**: MT1 ("Khi một CLB đông người, trường ưu tiên điều gì?": Theo năng lực / Cơ hội như nhau / Dành chỗ cho một nhóm, `js/19_muc_tieu.js`, lưu qua `chon_muc_tieu`, có Hoàn tác). Ba thẻ L4 trong kế hoạch (Điểm cao hơn / Nhóm ưu tiên / Cả hai) KHÔNG cùng ý với ba thẻ MT1 (MT1 có thêm "bốc thăm" và tự đặt số chỗ giữ). | **Không dựng bộ thẻ thứ hai.** Dùng lại ba thẻ MT1 làm "câu hỏi duy nhất", đổi chữ cho dễ hiểu; ba ô chọn cũ (`priority/tier_mode/score_scope`) nằm trong "Tuỳ chỉnh thêm". | Hai bộ thẻ cùng ghi vào một luật xếp dễ mâu thuẫn; MT1 đã có lưu ngay + Hoàn tác + ước tính tác động. Bài test "cùng payload" vẫn giữ: ba ô chọn cũ lưu y như trước. |
| D2 | Nút đỏ "Xoá điểm quyết tâm của tất cả" (`btnWhXoaTatCa`, `btnWhXoaTatCaXn`) đang nằm trong tab Điểm quyết tâm, trái luật "đỏ chỉ ở Làm lại từ đầu". | Đổi thành nút thường (`.btn-secondary`), **giữ nguyên bước gõ chữ xác nhận**. Đỏ chỉ còn hai nút ở "Làm lại từ đầu". | Chuyển nút sang tab khác phải sửa luồng nạp khối điểm quyết tâm; đổi kiểu nút rẻ hơn, không mất khả năng nào. |
| D3 | Khung "Cài đặt · {ten}" (6 thẻ + "Thay đổi…" = **7 ô chọn**) nằm trên đầu MỌI tab con, kể cả "Xoá dữ liệu". | Chuyển nguyên khung (giữ id) vào tab **Cách xếp**, làm hai câu hỏi 1 và 2 của tab. | Tab Danh sách CLB / Học sinh / Làm lại không còn gánh 7 ô chọn không liên quan. |
| D4 | "Bảng điều khiển" (chỉ hiện khi FA-DAA bật, 1 nút) cũng nằm trên mọi tab con. | Thành mục thứ tư trong "Thêm ▾" (chỉ hiện khi FA-DAA bật). | Giữ dải tab ≤ 4, không bỏ gì. |
| D5 | Một số chữ do **backend** trả về (`tieu_chi.py`: nhãn ba ô chọn, tiêu đề ô, các dòng thứ tự, dòng "chưa dùng") có từ "suất", "Phạm vi điểm". | **Không sửa backend.** Giao diện thay chữ theo mã (`ma`/giá trị) bằng khoá `ux4_*`; thiếu mã thì dùng chữ backend. | Giữ "không đổi backend/API"; test API không bị ảnh hưởng. |

## 1. Bảng từ ngữ (mọi chuỗi nhìn thấy trong `#view-admin`)

Ghi chú cột: **=** nghĩa là giữ nguyên chữ (đã rõ). Khoá mới có tiền tố `ux4_`. Lý do viết ngắn.

### 1.1 Đầu trang, dải tab, dòng mục đích, dòng trạng thái

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| admin_title | Quản lý | = | = | Tên thẻ đã rõ |
| admin_desc | Thêm hoặc sửa {slot_sl}, chỉ tiêu và suất ưu tiên. Nhóm ưu tiên của {person_l} chỉ được hưởng suất khi cùng nhãn với {slot_sl}. | Sửa danh sách {slot_sl} và {person_l}, chọn cách xếp, hoặc làm lại từ đầu. Chọn một mục bên dưới. | Edit the list of {slot_pl} and {person_pl}, choose how places are given out, or start over. Pick a section below. | Mô tả cả thẻ, bỏ "suất/nhãn" |
| ql_tab_nhom_aria | Các mục của thẻ Quản lý | = | = | |
| ql_tab_clb | {slot_p} | Danh sách {slot_sl} | {slot_p} | Danh từ → nói việc làm được |
| ql_tab_hs | {person_p} | = | = | Ngắn, đã rõ |
| ux4_ql_tab_cach_xep (mới) | Tiêu chí xếp + Thử cấu hình (nằm trong "Nâng cao") | Cách xếp | How to rank | Việc quan trọng nhất không còn bị giấu |
| ux4_ql_tab_them (mới) | — | Thêm ▾ | More ▾ | Gom mục ít dùng/nguy hiểm |
| ql_tab_wh | Điểm quyết tâm | = (trong Thêm ▾) | = | |
| ql_tab_dc | Điểm chuẩn | = (trong Thêm ▾) | = | |
| ql_tab_du_lieu | Xoá dữ liệu | Làm lại từ đầu (trong Thêm ▾) | Start over | Nói việc người dùng muốn làm |
| ux4_mo_clb (mới) | — | Thêm {slot_sl} mới, hoặc sửa số chỗ và {session_l} của {slot_sl} đã có. | Add a new {slot_l}, or change the places and {session_l} of an existing one. | Một dòng mục đích |
| ux4_tt_clb (mới) | — | {n} {slot_sl} · {cho} chỗ · {b} {session_l} | {n} {slot_pl} · {cho} places · {b} {session_l} | Dòng trạng thái (từ dữ liệu đã tải, không thêm API) |
| ux4_mo_hs (mới) | — | Tìm {person_l}, chọn nhiều em rồi gán nhóm ưu tiên hoặc xuất danh sách. | Find {person_pl}, tick several, then give them a priority group or export the list. | |
| ux4_tt_hs (mới) | — | {n} {person_l} · {g} đã có nhóm ưu tiên | {n} {person_pl} · {g} already in a priority group | |
| ux4_mo_cach_xep (mới) | — | Chọn ai được xét trước khi {slot_sl} hết chỗ, rồi thử xem kết quả đổi thế nào. Kết quả chính thức chỉ đổi ở lần xếp tiếp theo. | Choose who is considered first when a {slot_l} runs out of places, then try it out. The official result changes only at the next run. | |
| ux4_tt_cach_xep (mới) | — | Đang dùng: {cach} | In use: {cach} | `{cach}` = tên thẻ MT1 đang chọn |
| ux4_mo_lam_lai (mới) | — | Dùng khi bắt đầu một đợt mới. Mỗi nút đều tự sao lưu trước khi xoá. | Use this to begin a new round. Each button backs up first. | |
| ux4_mo_wh / ux4_mo_dc (mới) | — | Xem và sửa điểm quyết tâm của từng {person_l}. / Xem điểm thấp nhất đã được nhận ở từng {slot_sl}. | View and edit each {person_l}'s commitment points. / See the lowest points accepted in each {slot_l}. | (tuỳ chọn, L4) |

### 1.2 Danh sách CLB (khung thêm/sửa + bảng + tải theo buổi)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| admin_club_form_title | Thêm hoặc sửa {slot_sl} | = | = | |
| th_name_short (nhãn ô) | Tên | = | = | |
| ux4_so_cho (mới; thay th_capacity trong thẻ này) | Chỉ tiêu | Số chỗ | Places | "Chỉ tiêu" là từ hệ thống |
| th_buoi (nhãn ô) | {session} | = (ô chọn thả xuống) | = | Chọn trong danh sách buổi đã có, không gõ mã |
| ux4_buoi_chung (mới; thay buoi_chua_chia) | Chưa chia {session_l} | Một {session_l} chung | One shared {session_l} | "Chưa chia" nghe như lỗi |
| ux4_buoi_them_moi (mới) | — | Thêm {session_l} mới… | Add a new {session_l}… | Mục cuối của ô thả xuống |
| placeholder_buoi | {session} sinh hoạt (ví dụ: thu_3) | (ô nhập chỉ hiện khi chọn "Thêm … mới": "Tên {session_l}, ví dụ: Thứ ba") | Name of the {session_l}, e.g. Tuesday | Bỏ mã thô `thu_3` |
| ux4_them_tuy_chon (mới) | — | Thêm tuỳ chọn | More options | Gập: Mã, Chỗ dành riêng, Nhóm |
| ux4_ma_clb (mới; thay th_club_id/placeholder_club_id trong ô) | Mã {slot_sl} (ví dụ: clb_01) | Mã {slot_sl} (tự điền theo tên, có thể sửa) | {slot} ID (filled in from the name, you can edit it) | Bỏ ví dụ mã thô |
| ux4_cho_rieng (mới; thay th_reserve_capacity trong thẻ này) | Suất ưu tiên | Chỗ dành riêng cho nhóm ưu tiên | Places kept for the priority group | Bỏ "suất" |
| ux4_nhom_duoc_cho (mới; thay th_reserve_group trong ô) | Nhóm ưu tiên (để trống nếu không có) | Nhóm được dành chỗ (để trống nếu không có) | Group the places are kept for (leave blank if none) | |
| btn_save_club | Lưu {slot_sl} | = | = | Nút vàng duy nhất của tab |
| btn_cancel | Huỷ | = | = | |
| th_club_id (cột) | Mã {slot_sl} | = | = | |
| th_name_short (cột) | Tên | = | = | |
| ux4_so_cho (cột) | Chỉ tiêu | Số chỗ | Places | |
| ux4_cho_rieng_cot (mới) | Suất ưu tiên | Chỗ dành riêng | Kept places | |
| th_reserve_group (cột, qua ux4) | Nhóm ưu tiên | = | = | |
| ux4_cot_buoi (mới) | {session} (cột không rõ) | {session} sinh hoạt | Meets on ({session_l}) | Cột có nhãn rõ |
| btn_delete | Xoá | = | = | |
| admin_club_empty | Chưa có {slot_sl} nào. Thêm {slot_sl} đầu tiên bằng biểu mẫu ở trên. | = | = | |
| buoi_hint_form | Hai {slot_sl} cùng {session_l} là trùng giờ, mỗi {person_l} chỉ vào được một. Để trống nếu trường chỉ có một {session_l}. | Hai {slot_sl} cùng {session_l} thì trùng giờ, mỗi {person_l} chỉ vào được một. Chọn "Một {session_l} chung" nếu trường chỉ có một {session_l}. | Two {slot_pl} in the same {session_l} clash, so a {person_l} can join only one. Choose "One shared {session_l}" if the school has only one. | Khớp với lựa chọn mới |
| admin_tai_buoi_title / desc | Tải theo {session_l} / Nên xem trước khi sắp xếp… | = | = | Đã rõ |
| th_so_clb, th_em_muon_buoi, th_ti_le_choi, th_muc | Số {slot_sl} / {person} chọn {session_l} này / {person} trên mỗi chỗ / Mức | = | = | |
| ux4_so_cho (th_tong_cho) | Chỉ tiêu | Số chỗ | Places | |
| ti_le_choi_giai_thich | Tỉ lệ chọi tính theo số {person_l}, không theo số nguyện vọng, vì mỗi {person_l} chỉ nhận một chỗ mỗi {session_l}. | Số {person_l} trên mỗi chỗ tính theo số {person_l}, không tính theo số nguyện vọng, vì mỗi {person_l} chỉ nhận một chỗ mỗi {session_l}. | Applicants per place counts {person_pl}, not preferences, because each {person_l} gets at most one place per {session_l}. | Bỏ "tỉ lệ chọi" |

### 1.3 Học sinh

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| admin_reserve_assign_title | Gán nhóm ưu tiên và xuất hồ sơ {person_l} | {person_p} và nhóm ưu tiên | {person_p} and priority groups | |
| placeholder_admin_student_search | Tìm {person_l} theo mã hoặc tên… | = | = | |
| lop_loc_nhan | Lọc theo {cohort_l} | = | = | |
| lop_sap_nhan + 2 lựa chọn sắp xếp | Sắp xếp / Theo mã {person_l} / Theo {cohort_l} | = (nằm trong "Thêm tuỳ chọn") | = | Ít dùng |
| ux4_da_chon (thay admin_dem_danh_dau) | Đã đánh dấu {n} {person_l} | Đã chọn {n} {person_l} | {n} {person_pl} selected | "Đánh dấu" → "chọn" |
| placeholder_reserve_group_apply | Nhóm ưu tiên cần gán | Gán vào nhóm nào? (ví dụ: khối 10) | Which group? (e.g. grade 10) | Chỉ hiện sau khi chọn ≥ 1 em |
| btn_bulk_assign | Gán cho {person_l} đã đánh dấu | Gán nhóm ưu tiên cho {person_l} đã chọn | Give the selected {person_pl} a priority group | Nút vàng (chỉ hiện khi ≥ 1 em) |
| btn_admin_xuat_hs | Xuất CSV {person_l} đã đánh dấu | Xuất danh sách {person_l} đã chọn (CSV) | Export the selected {person_pl} (CSV) | Nút thường |
| xuat_canh_bao_diem | Tệp xuất có {score_l} chấm và số bốc thăm. Không gửi các tệp này cho giáo viên chấm {score_l}. | = | = | Cảnh báo quan trọng, giữ |
| th_student_id / th_name / th_cohort | Mã {person_l} / Họ tên / {cohort} | = | = | |
| th_current_reserve_group | Nhóm ưu tiên hiện tại | Nhóm ưu tiên | Priority group | Gọn |
| aria_chon_tat_ca_trang | Chọn tất cả {person_l} trên trang này | = | = | |
| admin_student_empty | Chưa có {person_l} nào. Thêm ở thẻ "Nhập nguyện vọng" hoặc nạp tệp từ Microsoft Forms. | = | = | |
| btn_prev_page / btn_next_page | ‹ Trước / Sau › | = | = | |

### 1.4 Cách xếp (khung Cài đặt chuyển vào + Tiêu chí xếp + Thử cấu hình)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| ux1a_cd_tieu_de | Cài đặt · {ten} | Cách xếp · {ten} | How to rank · {ten} | Khớp tên tab |
| ux1a_cd_cau_hoi (câu 1) | {person} cho biết mình muốn {slot_sl} nào nhiều hơn bằng cách nào? | = | = | Đã rõ |
| ux1a_the_chi_xep_tt/mt, chia_100_tt/mt, huy_chuong_tt/mt | Chỉ xếp thứ tự – NV1, NV2, NV3… / Chia 100 điểm – cho các nguyện vọng (mặc định) / Huy chương – Vàng · Bạc · Đồng (60 · 30 · 10) | = (bỏ "(mặc định)" trong mô tả, thay bằng nhãn nhỏ "Đề xuất") | = | Von Restorff: một nhãn "Đề xuất" duy nhất |
| ux4_de_xuat (mới) | — | Đề xuất | Suggested | Nhãn nhỏ trên thẻ mặc định |
| mt1_cau_hoi (câu 2) | Khi một {slot_s} đông người, trường ưu tiên điều gì? | Khi {slot_s} hết chỗ, ai được xét trước? | When a {slot_l} runs out of places, who is considered first? | Câu hỏi của Truong |
| mt1_the_nang_luc_tt | Theo năng lực | Điểm bài thi cao hơn | Higher exam score | Từ của Truong |
| mt1_the_nang_luc_mt | Xếp theo điểm thi, rồi điểm quyết tâm (nếu có), cuối cùng là bốc thăm. | = | = | |
| mt1_the_co_hoi_tt | Cơ hội như nhau | Bốc thăm | Lottery | Nói đúng việc làm |
| mt1_the_co_hoi_mt | Mọi {person_l} có cơ hội như nhau: bốc thăm, không xét điểm thi. | = | = | |
| mt1_the_danh_cho_tt/mt | Dành chỗ cho một nhóm / Giữ một số chỗ ở mỗi {slot_s} cho một nhóm… | = | = | Đã rõ |
| ux4_voi_lua_chon (mới) | — | Với lựa chọn này: | With this choice: | Tiền tố dòng tác động có sẵn (`uoc_tinh_muc_tieu`, chỉ đọc) |
| ux1a_cd_thay_doi | Thay đổi… | (ẩn; thay bằng "Tuỳ chỉnh thêm") | | Bớt một nút trùng ý |
| ux1a_nang_cao | Nâng cao: tiêu chí xếp, thử cấu hình | (bỏ chữ "Nâng cao") → ux4_tuy_chinh_them: Tuỳ chỉnh thêm | Fine-tune | Gập chứa ba ô chọn cũ |
| gt2_tc_tieu_de | Tiêu chí xếp | Tuỳ chỉnh chi tiết | Detailed settings | |
| gt2_tc_mo_ta | Thứ tự dưới đây là cách phần mềm xếp những người cùng đăng ký một suất. Chỉ chọn được trong các lựa chọn có sẵn. | Danh sách dưới đây là thứ tự phần mềm dùng để chọn khi nhiều {person_l} cùng muốn một chỗ. Chỉ chọn được trong các lựa chọn có sẵn. | The list below is the order the software uses when several {person_pl} want the same place. Only the options provided can be chosen. | |
| gt2_tc_thu_tu | Thứ tự xếp hiện tại | Thứ tự đang dùng | Order in use | |
| gt2_tc_chon | Chọn cách xếp | Đổi cách xếp | Change how to rank | |
| (backend) tiêu đề ô `priority` | Xếp theo | Khi {slot_sl} hết chỗ, ai được xét trước? | When a {slot_l} runs out of places, who is considered first? | Trùng câu hỏi của Truong |
| (backend) tiêu đề ô `tier_mode` | Cách dùng nhóm ưu tiên | Nhóm ưu tiên được xét thế nào? | How is the priority group treated? | |
| (backend) tiêu đề ô `score_scope` | Phạm vi điểm | Điểm bài thi tính thế nào? | How are exam scores counted? | |
| (backend) tiêu đề ô `tiers` | Danh sách nhóm ưu tiên (nhóm đầu được ưu tiên nhất) | Các nhóm ưu tiên (nhóm đầu được xét trước) | Priority groups (the first is considered first) | |
| gt2_tc_nhom_goi_y | Mỗi dòng một nhóm, nhóm đầu được ưu tiên nhất | = | = | |
| (backend) `priority=score` | Chỉ theo điểm bài thi | Điểm bài thi cao hơn | Higher exam score | Từ của Truong |
| (backend) `priority=tier` | Chỉ theo nhóm ưu tiên | Học sinh thuộc nhóm ưu tiên | {person_pl} in a priority group | Từ của Truong |
| (backend) `priority=score+tier` | Điểm bài thi và nhóm ưu tiên | Cả hai | Both | Từ của Truong |
| (backend) `tier_mode=reserve` | Giữ suất riêng cho nhóm | Giữ một số chỗ riêng cho nhóm | Keep some places for the group | |
| (backend) `tier_mode=strict` | Nhóm đứng trước điểm | Nhóm luôn được xét trước | The group is always considered first | |
| (backend) `score_scope=per_slot` | Điểm theo từng CLB | Mỗi {slot_sl} một bài thi riêng | A separate test for each {slot_l} | |
| (backend) `score_scope=per_person` | Một điểm cho cả người | Một điểm chung cho mọi {slot_sl} | One shared score for all {slot_pl} | |
| (backend) dòng `du_tru` | Nhóm ưu tiên – giữ suất riêng | Nhóm ưu tiên: giữ một số chỗ riêng | Priority group: some places kept | Bỏ "suất" |
| (backend) dòng "chưa dùng" `tiers`, `priority` | …nhóm đang là suất giữ riêng… | …các nhóm chỉ đang giữ chỗ riêng nên không đứng trước điểm… | …the groups only keep places, so they do not rank before the score… | Bỏ "suất" |
| (backend) ghi chú bất biến 2 (`GHI_CHU`) | Phần mềm không dùng thứ hạng nguyện vọng, kết quả kỳ trước hay hoàn cảnh cá nhân để xếp. | = (giữ nguyên, hiện dưới danh sách thứ tự) | = | Bất biến 2: phải còn nguyên |
| gt2_tc_khong_dung | Chưa dùng: | = | = | |
| gt2_tc_luu | Lưu tiêu chí | Lưu tuỳ chỉnh (nút thường, không vàng) | Save changes | Vàng dành cho "Thử cách xếp này" |
| gt2_tc_da_luu | Đã lưu tiêu chí. Có hiệu lực từ lần xếp chính thức tiếp theo. | Đã lưu. Áp dụng từ lần xếp chính thức tiếp theo. | Saved. Applies from the next official run. | |
| gt2_thu_tieu_de | Thử cấu hình | Thử cách xếp khác | Try another way to rank | Bỏ "cấu hình" |
| gt2_thu_buoc_1/2/3 + aria | Chạy thử / Chọn hai lần để so sánh / So sánh, xuất tệp | (ẩn danh sách ba bước; giữ phần tử) / aria: Các bước thử cách xếp | / Steps for trying another way | Bớt chữ; mô tả đã nói đủ |
| gt2_thu_mo_ta | Chạy thử dùng đúng các lựa chọn đang hiện ở khung Tiêu chí xếp phía trên. Kết quả thử không được công bố và không thay kết quả chính thức. | Thử xếp lại bằng các lựa chọn đang hiện ở trên. Kết quả thử không được công bố và không thay kết quả chính thức. | Try the allocation again with the choices shown above. A trial is not published and does not replace the official result. | |
| gt2_thu_chay | Chạy thử | Thử cách xếp này | Try this way | Nút vàng duy nhất của tab |
| gt2_thu_da_chay | Đã chạy thử xong. Kết quả chính thức không đổi. | = | = | |
| ux4_so_sanh_khac (mới) | — | So sánh với lần khác | Compare with another run | Gập chứa hai ô chọn lần chạy |
| gt2_thu_lan_a / lan_b | Lần thứ nhất / Lần thứ hai | = | = | |
| gt2_thu_lan_chinh_thuc | Chính thức số {id} | Xếp chính thức lần {id} ({luc}) | Official run {id} ({luc}) | Ngày giờ dd/mm/yyyy HH:mm; nếu thiếu thì bỏ ngoặc |
| gt2_thu_lan_thu | Chạy thử số {id} | Thử lần {id} ({luc}) | Trial {id} ({luc}) | |
| gt2_thu_chua_co | Chưa có lần chạy nào để so sánh. Hãy chạy xếp chính thức rồi chạy thử. | Chưa có kết quả nào để so sánh. Hãy chạy xếp chính thức trước, rồi bấm "Thử cách xếp này". | There is nothing to compare yet. Run the official allocation first, then press "Try this way". | |
| gt2_thu_so_sanh / xuat_html / xuat_csv | So sánh / Xuất trang so sánh / Xuất danh sách đổi chỗ (CSV) | = | = | |
| gt2_canh_khong_nhom | …Hãy nhập danh sách nhóm ở khung Tiêu chí xếp, hoặc chọn cách xếp khác. | …Hãy nhập danh sách nhóm ở mục "Tuỳ chỉnh thêm", hoặc chọn cách xếp khác. | …Enter the groups under "Fine-tune", or choose another way. | Đúng tên mới |
| gt2_canh_nhom_rong | Đã chọn nhóm đứng trước điểm nhưng danh sách nhóm đang trống nên cách này chưa có tác dụng. | Đã chọn "Nhóm luôn được xét trước" nhưng chưa có nhóm nào nên cách này chưa có tác dụng. | "The group is always considered first" is chosen but there are no groups yet, so it has no effect. | |
| gt2_ad_tieu_de | Dùng tiêu chí của một lần chạy thử | Dùng cách xếp của một lần thử | Use the way of ranking from a trial | |
| gt2_ad_ghi_chu | Nút dưới đây chỉ lưu tiêu chí của lần thử vào cấu hình. Kết quả chính thức chỉ đổi khi quản trị chạy xếp chính thức lần kế tiếp. | Nút dưới đây chỉ lưu cách xếp của lần thử. Kết quả chính thức chỉ đổi khi quản trị chạy xếp chính thức lần kế tiếp. | The button below only saves the trial's way of ranking. The official result changes only at the next official run. | Bỏ "cấu hình" |
| gt2_ad_nut / hoi / xac_nhan / huy / da_luu | Dùng tiêu chí này cho lần chạy chính thức / Lưu tiêu chí của chạy thử số {id} làm tiêu chí đang dùng? Thứ tự sẽ là: / Lưu tiêu chí này / Không lưu / Đã lưu tiêu chí. Kết quả chính thức chưa đổi. Hãy chạy xếp chính thức để áp dụng. | Dùng cách xếp này cho lần xếp chính thức / Dùng cách xếp của lần thử {id} từ nay? Thứ tự sẽ là: / Dùng cách xếp này / Không dùng / Đã lưu. Kết quả chính thức chưa đổi; hãy chạy xếp chính thức để áp dụng. | Use this way for the official run / Use the way from trial {id} from now on? The order will be: / Use this way / Don't use / Saved. The official result is unchanged; run the official allocation to apply it. | |
| gt2_ss_n | Số suất xét | Số {person_l} được xét | {person_pl} considered | Bỏ "suất" |
| gt2_ss_* còn lại (bảng so sánh) | Đã có chỗ, Chưa có chỗ, Điểm chuẩn, Tỉ lệ… | = | = | Đã rõ |

### 1.5 Làm lại từ đầu (đỏ cô lập)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| danger_zone_title | Vùng nguy hiểm: xoá dữ liệu để làm lại | Làm lại từ đầu | Start over | |
| danger_zone_desc | Nạp tệp chỉ thêm {person_l} mới… hãy xoá ở đây trước, nếu không {person_l} cũ vẫn chiếm chỗ. | Nạp tệp chỉ thêm {person_l} mới, không xoá {person_l} cũ. Muốn làm lại với bộ dữ liệu khác, hãy xoá ở đây trước, nếu không {person_l} cũ vẫn chiếm chỗ. | = | Giữ ý, bỏ "vùng nguy hiểm" ở tiêu đề |
| danger_zone_safety | Cả hai nút đều tự sao lưu dữ liệu trước khi xoá. Lịch sử các lần sắp xếp được giữ lại. | Cả hai nút đều tự sao lưu trước khi xoá. Lịch sử các lần xếp vẫn được giữ lại. | Both buttons back up first. The history of runs is kept. | |
| btn_reset_students | Xoá toàn bộ {person_l} (giữ {slot_sl}) | Xoá hết {person_l}, giữ lại danh sách {slot_sl} | Delete all {person_pl}, keep the list of {slot_pl} | Nút đỏ + xác nhận hai bước giữ nguyên |
| btn_reset_all | Xoá toàn bộ dữ liệu (cả {slot_sl}) | Xoá hết dữ liệu, kể cả danh sách {slot_sl} | Delete all data, including the list of {slot_pl} | |

### 1.6 Điểm quyết tâm (trong Thêm ▾; phần tuỳ chọn của L4)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| wh_ql_title / wh_ql_desc | Điểm quyết tâm / Xem, sửa và xoá điểm quyết tâm… | = | = | |
| nút "i" (`btnWhThongTin`) | i | Giải thích (chữ hiện, không chỉ chữ "i") | Explain | Nút "i" trơ trọi |
| wh_ql_giai_thich (aria) | Giải thích về điểm quyết tâm | = | = | |
| wh_ql_dang_khoa | Đang khoá từ {luc} (hiện "2026-11-22 03:36:59") | Đã khoá từ {luc} để kết quả không bị đổi (luc dạng dd/mm/yyyy HH:mm) | Locked since {luc} so the results do not change | Bỏ giờ ISO |
| wh_ql_dang_mo | Đang mở, có thể sửa điểm | = | = | |
| wh_canh_bao_title | Hồ sơ cần xử lý | = | = | |
| wh_hl_tai | Tải danh sách cần sửa | = | = | |
| wh_hl_phong | Phóng cho đủ 100 theo tỉ lệ | Tự cộng cho đủ 100 (giữ tỉ lệ) | Fill up to 100 (keep the proportions) | Bỏ "phóng" |
| wh_hl_phong_hoi | Phần mềm sẽ đổi điểm… mỗi quỹ đủ 100… | Phần mềm sẽ sửa điểm quyết tâm của các {person_pl} chia thiếu hoặc thừa, giữ nguyên tỉ lệ các điểm đã đặt để mỗi nhóm điểm cộng lại đủ 100. Dữ liệu được sao lưu trước và mỗi thay đổi đều ghi nhật ký. Gõ {can_go} để xác nhận. | The software will fix the commitment points of {person_pl} who split too little or too much, keeping the proportions, so each group adds up to 100. Data is backed up first and every change is logged. Type {can_go} to confirm. | Bỏ "quỹ" |
| wh_hl_phong_xn / aria_wh_go_phong | Xác nhận phóng điểm / Gõ chữ xác nhận để phóng điểm | Xác nhận tự cộng / Gõ chữ xác nhận để tự cộng điểm | Confirm / Type the confirmation word to fill the points | |
| wh_hl_bo_qua_tieu_de | Chưa phóng được {n} {person_pl}, cần sửa tay: | Chưa tự cộng được cho {n} {person_pl}, cần sửa tay: | Could not fill up {n} {person_pl}, fix by hand: | |
| wh_loc_quy | Quỹ | Loại điểm | Kind of points | |
| wh_quy_1 / wh_quy_2 | Quỹ 1, đã thi / Quỹ 2, không thi | Điểm cho {slot_sl} có thi / Điểm cho {slot_sl} không thi | Points for {slot_pl} with a test / without a test | Từ của Truong |
| wh_quy_ngan | Quỹ {q} | ux4_wh_loai_1 "Có thi" / ux4_wh_loai_2 "Không thi" | With a test / No test | Bỏ số trơ |
| wh_sua_title, btn_save_wharton, fallback_chua_luu, btn_wh_xoa_mot, wh_sua_dong, wh_sua_khoa, wh_sua_rong | Sửa điểm của {name}… | = | = | Đã rõ |
| wh_tim_placeholder, wh_loc_buoi, wh_loc_clb, wh_loc_chi_loi, wh_loc_tat_ca, wh_xem_tat_ca, th_wh_diem, th_wh_tt, wh_tt_ok/lech/loi/vang, wh_bang_rong | = | = | = | Đã rõ |
| wh_thao_tac_khac | Thao tác khác | = | = | Gập có sẵn |
| btn_wh_mo_khoa, wh_dang_mo_khong_can, btn_wh_mo_khoa_xn, btn_wh_xem_nhat_ky, wh_nk_chon_em, wh_nhat_ky_title, wh_nhat_ky_rong, btn_wh_xem_them, btn_wh_xoa_tat_ca, btn_wh_xoa_tat_ca_xn | = | = (D2: hai nút xoá tất cả thành nút thường) | = | |

### 1.7 Điểm chuẩn (trong Thêm ▾; phần tuỳ chọn của L4)

| Khoá | VI cũ | VI mới | EN mới | Vì sao |
|---|---|---|---|---|
| dc_title | Điểm chuẩn | = | = | |
| dc_mo_ta | …tách theo hai cách xét (xét điểm thi và xét điểm quyết tâm) và theo suất thường hay suất ưu tiên… {slot_sl} còn chỗ ghi 0 điểm. | Điểm thấp nhất đã được nhận ở từng {slot_l}, tách theo hai cách xét (theo điểm thi và theo điểm quyết tâm) và theo chỗ thường hay chỗ dành riêng. {slot_sl} còn chỗ trống thì ghi "chưa cần điểm". Chỉ dành cho quản trị. | The lowest points accepted in each {slot_l}, split by the two ways of judging (by test score and by commitment points) and by normal or kept places. A {slot_l} with free places shows "no points needed". Admins only. | Giải thích cả "—" và "0" |
| dc_tang1 / dc_tang2 | Xét điểm thi / Xét điểm quyết tâm | Theo điểm thi / Theo điểm quyết tâm | By test score / By commitment points | Hết nhãn trơ "XÉT ĐIỂM THI —" |
| ux4_dc_trong (mới) | — (dấu gạch) | Chưa có ai | No one yet | Thay "—" |
| dc_con_cho | 0 (còn {n} chỗ) | Chưa cần điểm (còn {n} chỗ trống) | No points needed ({n} places free) | Thay số 0 khó hiểu |
| dc_thuong / dc_du_tru | Suất thường / Suất ưu tiên | Chỗ thường / Chỗ dành riêng | Normal places / Kept places | Bỏ "suất" |
| dc_cu, dc_chua_co_ket_qua, dc_dong_chi_tiet, dc_xem_chi_tiet, dc_tong_quan_tieu_de, dc_bang_tieu_de, dc_cot_*, dc_don_chu, dc_duoc, dc_khong, dc_khong_ai, … | = | = | = | Đã rõ |

### 1.8 Thanh "Việc tiếp theo" (ngoài `#view-admin`, nhưng hiện cùng màn)

| Khoá | VI cũ | VI mới | Vì sao |
|---|---|---|---|
| ux1a_cau_* / ux1a_nut_* | (Nạp sổ, Xem cảnh báo, Chạy sắp xếp, Xử lý…, Xuất kết quả) | = (chữ giữ nguyên) | Chỉ đổi **kiểu nút**: từ vàng (`.btn-primary`) sang kiểu cảnh báo viền (`.btn-canh-bao`, màu cảnh báo), để không tranh với nút vàng của tab. |

## 2. Bản đồ lựa chọn theo từng khung

Cách đếm (cũng là cách bài test Hick sẽ đếm): nút, ô chọn, ô nhập, tab, liên kết, `<summary>` đang **nhìn thấy và bật** trong `#view-admin`, **không tính** nút/ô tick nằm trong hàng bảng (`tbody`) và dải tab (đếm riêng, ≤ 4).
Ngân sách: mỗi nhóm lựa chọn ≤ 3; mỗi khung ≤ 7 ô trước khi mở "Thêm tuỳ chọn"; một tab con ≤ 9 ô ngoài dải tab; ≤ 1 nút vàng mỗi khung.

| Khung | Hiện nay (đếm) | Sau thiết kế (đếm) | Ô ẩn đi nằm ở đâu | MỘT nút vàng |
|---|---|---|---|---|
| **Dải tab** | 5 (CLB, Học sinh, Điểm quyết tâm*, Điểm chuẩn*, Xoá dữ liệu); tab hiện bật-tắt theo tính năng | **4**: Danh sách CLB · Học sinh · Cách xếp · Thêm ▾ | Thêm ▾ chứa Điểm quyết tâm*, Điểm chuẩn*, Bảng điều khiển* (D4), Làm lại từ đầu (≤ 4 mục; * chỉ hiện khi tính năng bật) | — |
| **Thanh Việc tiếp theo** | 1 vàng | 1 nút kiểu cảnh báo (viền, màu cảnh báo) | — | không phải vàng |
| **Khung Cài đặt (đầu mọi tab)** | 7 (6 thẻ + "Thay đổi…") trên MỌI tab con | 0 trên ba tab đầu; chuyển vào Cách xếp (D3) | Tab Cách xếp | — |
| **Danh sách CLB** | 35 đo được: 7 Cài đặt + 5 dải + 7 form (Mã, Tên, Chỉ tiêu, Suất ưu tiên, Nhóm, Buổi, Lưu) + 9 nút Xoá + 6 trong "Nâng cao" | **5**: Tên, Số chỗ, Buổi (ô thả xuống), Thêm tuỳ chọn, Lưu CLB (+ nút Xoá từng hàng như cũ) | Mã (tự điền), Chỗ dành riêng, Nhóm được dành chỗ → "Thêm tuỳ chọn"; Tiêu chí/Thử → tab Cách xếp | **Lưu CLB** |
| **Tải theo buổi** (chỉ đọc) | 0 | 0 | — | — |
| **Học sinh** | 127 đo được (gồm ô tick của hàng): ngoài hàng có 7 Cài đặt + 5 dải + tìm, nhóm cần gán, Gán, Xuất, Lọc lớp, Sắp xếp, tick-tất-cả, 2 nút trang + 6 "Nâng cao" | Chưa chọn em nào: **6** (Tìm, Lọc lớp, tick-tất-cả, Thêm tuỳ chọn, Trước, Sau). Có ≥ 1 em chọn: thêm khung "Đã chọn n học sinh" với 3 ô (Nhóm, **Gán**, Xuất) | Sắp xếp → "Thêm tuỳ chọn"; Gán/Xuất/ô nhóm chỉ hiện sau khi chọn ≥ 1 em (hiện tại bấm được mà chưa có ai) | **Gán nhóm ưu tiên** (chỉ khi ≥ 1 em được chọn; chưa chọn thì không có nút vàng) |
| **Cách xếp** (gộp) | Rải ở 3 chỗ: Cài đặt 7 + 3 ô chọn + 1 ô nhập + Lưu + Chạy thử + 2 ô chạy + 3 nút so sánh/xuất | **9**: 3 thẻ (câu 1) · 3 thẻ (câu 2) · Tuỳ chỉnh thêm · **Thử cách xếp này** · So sánh với lần khác; mỗi nhóm ≤ 3 thẻ | 3 ô chọn cũ + ô nhập nhóm + Lưu tuỳ chỉnh → "Tuỳ chỉnh thêm" (ẩn ô không áp dụng: ô nhóm khi không dùng nhóm); hai ô chọn lần chạy + So sánh/Xuất → "So sánh với lần khác" | **Thử cách xếp này** (thẻ lưu ngay, Lưu tuỳ chỉnh là nút thường) |
| **Làm lại từ đầu** | 2 đỏ + 7 Cài đặt + 6 "Nâng cao" = 21 | **2** (hai nút đỏ, xác nhận hai bước giữ nguyên) | — | không có (đỏ cô lập, không dùng vàng) |
| **Điểm quyết tâm*** (L4 tuỳ chọn) | nhiều (bảng + lọc 6 + hàng loạt 2 + gập Thao tác khác 3) | lọc còn: Tìm, Loại điểm, Chỉ hồ sơ có vấn đề, Xem tất cả (≤ 7); Buổi/CLB vào "Thêm bộ lọc" | Thao tác khác (gập sẵn); xoá tất cả thành nút thường (D2) | **Lưu điểm quyết tâm** (chỉ khi mở sửa một em) |
| **Điểm chuẩn*** (L4 tuỳ chọn) | chỉ đọc + "Xem chi tiết" từng CLB | không đổi cấu trúc; chỉ đổi chữ | — | không có |

Ghi chú:
- Tab nhớ (`localStorage` `rbda_ql_tab_con`, có try/catch) vẫn hiểu giá trị cũ: `clb`→Danh sách CLB, `hs`→Học sinh, `du_lieu`→Làm lại từ đầu, `wh`/`dc`→mục trong Thêm ▾. Giá trị tab đang ẩn thì quay về Danh sách CLB.
- Mọi `id` giữ nguyên (kể cả `qlTabDuLieu`, `ux1aNangCao`, `gt2TcPriority`…); phần tử "ẩn" vẫn có trong DOM.
- Màu: đỏ (`.btn-danger`) chỉ còn `btnResetStudents`, `btnResetAll` (D2 xử lý hai nút xoá điểm quyết tâm). Thẻ đang chọn có viền đậm + dấu ✓ (không chỉ màu).
- Sau khi lưu/chạy: dòng trạng thái đổi + hàng/khung đổi sáng ngắn (tôn trọng `prefers-reduced-motion` và `html.tat-hieu-ung`); ý nghĩa luôn có cả bằng chữ.
- Chữ cấm cho bài test: "cấu hình", "suất", "nhãn", "Quỹ 1", "Phóng", giờ ISO `\d{4}-\d\d-\d\d \d\d:`, và chữ "Nâng cao" của gập cũ.

## 3. Ảnh hưởng tới test (dự kiến, ghi vào CHANGELOG ở từng lô)
- `tests/test_ws_nhan.py` (`SUA_CO_Y`, chú thích "UX4"): các khoá đổi chữ ở mục 1.
- `tests/test_giao_dien_ux1_dieu_huong.py` (`test_nang_cao_dong_mac_dinh…`, tab Câu lạc bộ/Xoá dữ liệu), `tests/test_giao_dien_ux1_cai_dat.py` (chữ "Học sinh cho biết…" giữ; vị trí khung đổi), các test MT1 (tên thẻ "Theo năng lực" → "Điểm bài thi cao hơn"), test GT2/GT4 chọn theo id (giữ), test chữ cũ ("Chỉ tiêu", "Chạy thử"): cập nhật có chủ ý, liệt kê trong CHANGELOG.
