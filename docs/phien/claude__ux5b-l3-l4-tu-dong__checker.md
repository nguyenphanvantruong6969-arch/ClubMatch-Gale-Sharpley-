# UX5B-L3/L4 — báo cáo checker (vòng 1)

Phạm vi: `git diff 8441218..b42cc57` (UX5B-FIX-CI, L3, L4). Môi trường: venv ngoài repo, Chromium 1243 gán nhãn 1255.
Chạy: `tests/test_giao_dien_ux5b_*.py tests/test_ws_nhan.py tests/test_i18n_sync.py tests/test_t3_l1_chu_du_phong.py` → **89 passed**.
Số đo bên dưới do checker tự đo bằng Chromium thật (dữ liệu MÔ PHỎNG: sổ 120 học sinh, em HS001), ngoài các test của coder.

**Kết luận: FIX: 1 mục (mất dữ liệu ở nút "‹ Danh sách", §8). Các mục còn lại PASS, kèm ghi chú.**

## 1. Từ ngữ đã duyệt (UX5B_TU_NGU 2.2, 2.3)
Khớp đúng: `ux5b_fallback_desc_qt` (VI+EN), `ux5b_tao_moi`, `ux5b_tt_chua_chon`, `ux5b_buoc_xong`, `ux5b_sua`, `ux5b_giai_thich`, `ux5b_tt_diem` (+ "Đã chấm xong hết"), `ux5b_quay_lai`, `fallback_step0_title` (VI "Tìm {person_l}"), "Chấm tiếp", `btn_clear_all` ẩn khi chưa có nguyện vọng (D6).
Lệch (đều nhỏ, không chặn):
- `fallback_step0_title` EN dùng `{person_la}` ("Find {person_la}" → "Find an employee") thay vì "Find a {person_l}" của bảng. Chủ ý và hợp lý (a/an, test `test_ws_nhan` đã sửa kèm `SUA_CO_Y`).
- Chữ không có trong bảng duyệt, coder tự thêm: `ux5b_tom_thi/nv/w/hc` (dòng tóm tắt: "4 CLB dự thi", "7 nguyện vọng", "điểm quyết tâm", "huy chương"), EN "Score next". Hợp lý, nhưng Truong nên biết đây là chữ mới.
- Giáo viên vẫn thấy mô tả "Tìm hoặc tạo học sinh…" dù không tạo được. Đúng bảng (§2.2 ghi "= (giáo viên)") nên không phải lỗi; chỉ ghi nhận là chỗ hơi lệch nghĩa.

## 2. Một nút vàng / không đỏ (đo `.btn-primary` nhìn thấy, `.btn-danger`/`nguy-hiem`)
| Thẻ, vai | Vàng nhìn thấy | Đỏ |
|---|---|---|
| Nhập nguyện vọng, admin, một em (mở Bước 2) | `btnSubmitPreferences` (1) | không |
| — mở Bước 3 / Bước 1 | `btnSubmitWharton` / chỉ nút của mục đó (1) | không |
| Nhập nguyện vọng, giáo viên | `btnSubmitPreferences` (1); Bước 3 mở không có vàng nào | không |
| Nhập điểm, danh sách (cả hai vai) | 0 khi đã chấm hết ("Đã chấm xong hết"); 1 "Chấm tiếp" khi còn CLB chưa chấm (test L3 phủ) | không |
| Nhập điểm, đang chấm | `btnSaveScores` (1) | không |
Ghi chú: các liên kết "xoá" từng dòng nguyện vọng có chữ màu gỉ (rust, gạch chân) — có sẵn từ trước, không phải `.btn-danger`, xoá dòng chưa lưu. Nếu Truong hiểu "không đỏ" theo nghĩa màu thì đây là ngoại lệ; coder không đổi (không thuộc diff).

## 3. Số ô nhìn thấy (trạng thái: một em đang mở; ô bật; theo `JS_DEM_NHAP`)
- Admin: **7** (`studentSearchInput, btnStudentSearch, summary "Tạo mới", summary menu ⋯, btnKioskLopSua "Đổi" lớp, btnClearRanking, btnSubmitPreferences`) + 2 nút "Sửa" bị loại (Bước 1, Bước 3) = **9 nếu tính cả**.
- Giáo viên: **6** (như trên trừ "Tạo mới") + 1 "Sửa" bị loại = **7 nếu tính cả**.
- Chưa chọn em: admin ≤ 7, giáo viên ≤ 7 (test L4). Mở Bước 3 (admin): 15 ô (vì 8 ô điểm quyết tâm là ô nhập, đếm nguyên) — vượt 7, test chỉ đo ở mục mặc định.
- Nhập điểm: danh sách = 0 (mọi nút "Chấm" nằm trong `tbody`, bị loại); đang chấm = 2 (`btnScoringQuayLai`, `btnSaveScores`), cả hai vai.
Đánh giá loại trừ: 
- Loại "Sửa": **chấp nhận được** (điều hướng giữa ba bước, mỗi lúc chỉ 1–2 nút, giống thanh tab), nhưng admin thực tế là 9 chứ không phải 7 — báo cho Truong để biết đó là phán đoán.
- Loại lưới CLB / hàng thứ tự / thẻ kết quả tìm (`.option-list`, `#rankingList`, `#studentSearchResults`): **công bằng** theo D5 (dữ liệu, không phải lựa chọn ngang hàng).
- Loại nút "Chấm" trong `tbody`: **công bằng với 4–9 CLB, nhưng yếu** — với 20 CLB màn hình có 20 nút "Chấm" mà test báo 0. Test Hick của danh sách điểm vì vậy gần như vô nghĩa; chấp nhận vì đây là danh sách việc, nhưng nên nói rõ ở báo cáo.

## 4. id, EN, quyền
- Mọi id cũ còn (`test_moi_id_cu_van_con` + tự soát diff: không id nào bị xoá). id mới: `ux5bTaoMoi, ux5bTtNhap, ux5bTtDiem, btnScoringQuayLai, fbBuoc1/2, ux5bSuaThi/Nv/W/Hc`.
- EN phản chiếu VI cho mọi khoá mới (đã đối chiếu trong `i18n.js`; `test_i18n_sync` xanh). Đổi ngôn ngữ vẽ lại dòng tóm tắt (đo: "Saved: 7 preferences", "Edit", "Create a new student ▾").
- Giáo viên: không thấy "Tạo mới" (`data-quyen`), không thấy Bước 3 điểm quyết tâm, nút Lưu của nó vẫn `data-quyen="quan_tri"`; submit_wharton không bao giờ được gọi (test). Bước Huy chương không có `data-quyen` (giữ như trước diff).

## 5. Không có tệp backend
`git diff --name-only` chỉ gồm: CHANGELOG, docs, `i18n.js`, `index.html`, `js/00_nen.js`, `js/04_nhap_tai_cho.js`, `js/06_cham_diem.js`, `style.css`, tests. Không có api*/db*/schema/pipeline/i18n_errors. **PASS.**

## 6. Payload
Diff `js/04_nhap_tai_cho.js` chỉ thêm `ux5bMucMo = ...`, `ux5bVeMuc()`, đổi chữ nút "i"; ba lời gọi `submit_test_selection(sid, ticks, lop)`, `submit_preferences(sid, ranking, lop)`, `submit_wharton(sid, w1, w2)` không đổi đối số. Hai test "cùng payload" (admin 3 API, giáo viên 2 API) bắt đúng số lời gọi, thứ tự và tham số. **PASS.**

## 7. Test cũ bị sửa (đều chỉ theo UI; không test nào bị skip/yếu đi)
- `a13_12_nhap`: thêm `mo_muc("thi")`; assert `#chuaLuuNv` hiện → đổi thành `nvChuaLuu()` + dòng tóm tắt "• Chưa lưu" (vì Bước 2 gập sau khi lưu). Ý định giữ nguyên (CLB thêm trong lúc chờ không bị coi là đã lưu); kiểm trạng thái thật mạnh hơn kiểm nhãn.
- `a13_8_khoa`: tách assert nút Lưu bị khoá theo từng bước (mở bước rồi assert). Giữ nguyên ý.
- `a14_lop`: thêm `mo_muc("nv")`, mở `<summary>` "Tạo học sinh mới". Giữ ý.
- `fa_huy_chuong`, `fa_n2_luu_mac_dinh`, `nhap_tai_cho`, `tran_moi_buoi`, `ux_xuat`, `wharton`, `wharton_quan_ly`, `ux2_loi_o`: chỉ thêm `mo_muc(...)` / mở mục gập / `state="attached"`. Giữ ý.
- `t3_l1`: nút "Chấm" đầu tiên nay có thể là "Chấm tiếp" vàng; assert được viết lại chặt hơn (vàng ⇔ "Chấm tiếp", thường ⇔ "Chấm", tối đa một "Chấm tiếp"). Giữ ý, không yếu đi.
- `t3_l2_van_hanh`: mở summary; `inner_text` → `textContent` cho lưới đang gập (vẫn kiểm không in "clb_a"). Giữ ý.
- `test_ws_nhan` (`SUA_CO_Y` thêm `fallback_step0_title`, kỳ vọng EN "Find an employee"), `test_ws_nhan_giao_dien` (đổi cách kiểm mô tả tab Xếp CLB sang tên bước vì `pipeline_desc` không còn chỗ giữ ngành). Giữ ý; các dòng ghi `UX5B`.
- `_ux5b_chung.mo_ux5b`: `chon_em` trước đây gõ vào `#fbSearch` (không tồn tại → no-op); nay thật sự chọn em. Sửa đúng.

## 8. Rủi ro mất dữ liệu
- Tick Bước 1/hạng Bước 2 chưa lưu, rồi bấm "Sửa" sang bước khác: **không mất** (đo: `thiChuaLuu()` vẫn true sau khi đổi mục và quay lại; dòng tóm tắt hiện "• Chưa lưu"). Rời sang thẻ khác rồi quay lại cũng giữ phiếu đang mở (không có hộp xác nhận, như trước).
- Lưu Bước 2 rồi tự mở Bước 3 / lưu Bước 1 rồi tự mở Bước 2: chỉ đổi mục mở, không chạm dữ liệu.
- **FIX 1 (mất điểm im lặng):** điểm đã gõ mà chưa bấm "Lưu điểm", bấm "‹ Danh sách CLB" → **mất ngay, không hỏi** (đo: gõ 7 vào ô đầu, quay lại, mở lại → ô về giá trị cũ 8). Nút này nằm ngay cạnh nút vàng "Lưu điểm", dễ bấm nhầm; đây là chấm điểm thật, gõ nhiều ô. Branch file ghi "như đổi tab" nhưng đổi tab xa, còn nút này kề nút Lưu. Đề nghị: theo dõi "điểm chưa lưu" (dùng lại mẫu `veDauChuaLuu`/hỏi xác nhận của thẻ nhập tay) và hỏi trước khi quay lại, hoặc ít nhất hiện dấu "• Chưa lưu" cạnh nút Lưu điểm. Thêm test.

## Ảnh (`docs/phien/anh_ux5b/`, 1280 px, dsf 1)
`admin_nhap_nguyen_vong.png` (toàn trang, một em), `gv_nhap_nguyen_vong.png` (toàn trang), `admin_nhap_diem_ds.png`, `gv_nhap_diem_ds.png` (sổ 120: đã chấm hết nên không có nút vàng), `admin_nhap_diem_dang_cham.png`.

---
# Vòng 2 (b42cc57..5a68872, UX5B-FIX1) — **PASS**
- FIX 1 đã xử lý: gõ điểm → hiện "• Chưa lưu" (`#chuaLuuDiem`); bấm "‹ Danh sách" lần 1 chỉ cảnh báo (toast, vẫn ở màn chấm), lần 2 trong 4 giây mới bỏ; Lưu xong thì hết "Chưa lưu" và quay lại không hỏi; ô bị đánh lỗi khi lưu một phần vẫn tính là chưa lưu (`__ux2Loi`). Khoá i18n mới có đủ VI và EN. Cùng mẫu "bấm lần hai" của thẻ Nhập nguyện vọng.
- Phạm vi: chỉ `index.html`, `i18n.js`, `js/06_cham_diem.js`, test và tài liệu; không có tệp backend. Hai test mới phủ cả hai nhánh; không test cũ nào bị sửa.
- Chạy lại cùng bộ test: **91 passed**.
- Ghi chú nhỏ (không chặn): cơ chế "bấm lại trong 4 giây" kém hiển nhiên hơn hộp xác nhận, nhưng nhất quán với phần còn lại của ứng dụng.
