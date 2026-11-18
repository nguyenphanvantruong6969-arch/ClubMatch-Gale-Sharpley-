# GT4 — Rà soát nhánh `claude/gt-tich-hop` so với `main`

> Ngày 2026-11-17. Người soát: phiên Sonnet, theo yêu cầu của Truong ("review mọi thay đổi so với main, nêu tác động trung thực,
> lập kế hoạch cải thiện, đóng vai người dùng"). Chỉ báo cáo: không sửa mã sản phẩm. Dữ liệu thử đều là MÔ PHỎNG.
> Kế hoạch sửa nằm ở `GT4_HOAN_THIEN.md`; hai prompt chạy tự động ở `docs/phien/GT4_PROMPT_1_WRITER.md` và `GT4_PROMPT_2_CHECKER.md`.

## 1. Phạm vi và cách soát
- Nhánh `claude/admiring-fermat-yf077m` = `claude/gt-tich-hop` (c9e3830) = `main` (35609f7) + 129 commit: **84 tệp, +11 308 / −20 dòng**.
  Gồm GT1 (giải trình từng học sinh, phiếu in, mã tra cứu), GT2 (tiêu chí bằng lời, chạy thử, so sánh, áp dụng),
  GT3 (tài khoản + 2 vai, cổng phân quyền, nhật ký thao tác, tài liệu minh chứng), tích hợp I0–I4.
- Đã làm: đọc mã lõi (`tai_khoan.py`, `phan_quyen.py`, `api_tai_khoan.py`, `nhat_ky.py`, `api_tieu_chi.py`, `tieu_chi.py` nửa đầu,
  `giai_trinh.py`, phần GT của `api_xuat.py`, `recovery.py`, diff của `rbda_priority_pipeline.py` / `fa_sau_xep.py`, `fa_ly_do.py`);
  quét JS mới (không có `innerHTML`); chạy `ruff`, `kiem_nhanh.py` (7/7 ĐẠT, trùng khít 9 ca), 12 tệp test GT (≈334 ca, không ca nào lỗi — nhưng chúng **không** có ca chính thức → chạy thử → giải trình, nên không thấy R0);
  đo thời gian trên bộ 800 học sinh; **chạy giao diện thật bằng Chromium với ba vai: quản trị, giáo viên, học sinh**.
- Chưa làm (nói rõ): không đọc từng dòng 1 000 dòng JS mới; không chạy toàn bộ bộ test (22 phút, để CI); không thử bản `.exe` trên Windows;
  không đọc nội dung gói minh chứng `.docx/.pdf`.

## 2. Hội đồng (bốn góc nhìn)
| Chuyên gia | Nói gì |
|---|---|
| **Kỹ sư bảo mật** | Phần cứng của tài khoản làm tốt (PBKDF2 200 000 vòng, so sánh hằng thời gian, khoá 5 lần sai, nhật ký chỉ-thêm bằng trigger, không xoá quản trị cuối). Nhưng có **một rò rỉ thật**: mã tra cứu của học sinh bị ghi nguyên văn vào nhật ký. Và lối thoát khi quên mật khẩu không dùng được với bản `.exe`. |
| **Giáo viên điều phối kiosk** | Tôi thấy nút mà bấm vào bị từ chối; vào "chế độ học sinh" xong thì tôi không thoát được vì cần quản trị. Nhật ký đọc không hiểu (`tao_tai_khoan`, `quan_tri`, `ok`). |
| **Học sinh (và phụ huynh)** | Điểm em 7,9, "mức vào được 6,2", mà vẫn trượt — nhìn như phần mềm sai. Ô nhập chỉ ghi "Mã" — mã nào? |
| **Kỹ sư kiểm thử** | Bất biến lõi giữ vững, test nhiều và có test giao diện thật. Lỗ hổng nằm ở chỗ test **không chạy luồng thật đầu-cuối** (tra cứu → nhật ký) và **không quét nút theo vai**. |

## 3. Tác động trung thực
**Tốt (đã kiểm):**
1. Lõi thuật toán không đổi: `compute_club_priority` không bị đụng; `kiem_nhanh.py` 7/7 ĐẠT; mọi tính năng mới mặc định TẮT (chưa có tài khoản = chạy như cũ).
2. Lược đồ chỉ thêm (cột `loai_chay`, bảng `ket_qua_thu`, `ma_tra_cuu`, `tai_khoan`, `nhat_ky_thao_tac`), idempotent, sao lưu trước.
3. Chạy thử **không ghi** vào `match_results` và hầu hết nơi đọc `run_history` đã lọc `loai_chay IS NULL` — **trừ một nơi bị sót (R0)**.
4. Hiệu năng ổn: 800 học sinh — chạy xếp 0,2 s, một lần giải trình 0,1 s, in phiếu cả 800 em 0,35 s, chạy thử 0,2 s.
5. Giao diện dùng `textContent`; HTML xuất đều qua `escape`; chống dò mã bằng so sánh hằng thời gian + khoá 60 s sau 5 lần sai; màn học sinh tự xoá kết quả khi bỏ không.

**Xấu / rủi ro (xếp theo mức):**
| # | Mức | Vấn đề | Đã tái hiện? |
|---|---|---|---|
| R0 | **Chặn** | **Lỗi tích hợp GT1 × GT2.** `api_xuat._giai_trinh_dung_lai` đọc `run_history ... ORDER BY run_id DESC` **không lọc `loai_chay IS NULL`**. Sau MỘT lần "Chạy thử", mọi lời giải trình (màn tra cứu, phiếu in, học sinh tự tra cứu) được dựng lại bằng luật và run_id của lần THỬ, nên hiện **kết quả của lần thử chưa công bố** thay cho kết quả chính thức trong `match_results`. Đo trên 120 em: 49 em hiện CLB khác với kết quả chính thức (HS002: giải trình "CLB Bóng đá", chính thức "CLB Âm nhạc"); cờ `du_lieu_da_doi = True` bật nhưng kết quả sai vẫn được hiện. Trước thử: 0 lệch. Test hiện có không bắt được vì không có test "chính thức → chạy thử → giải trình". | Có (script, 49/120 lệch) |
| R1 | **Cao** | `nhat_ky.tom_tat_tham_so` không lọc tham số `ma` của `tra_cuu_hoc_sinh` (regex chỉ bắt `tra_cuu` trong *tên khoá*). Mỗi lần học sinh tra cứu, **mã tra cứu đúng lẫn mã gõ sai** vào bảng `nhat_ky_thao_tac` (chỉ-thêm, không xoá được; vào cả bản sao lưu và CSV xuất). Trái lời hứa trong tài liệu "mã bí mật không bao giờ vào nhật ký". Thêm: dòng nhật ký ghi tên **quản trị đang đăng nhập** thay vì "học sinh" (chế độ học sinh dùng chung phiên). | Có: `{"student_id": "HS002", "ma": "JEM66MN5"}` |
| R2 | **Cao** | Quên mật khẩu quản trị chỉ có lối `python recovery.py --xoa-tai-khoan` (cần Python + venv). Bản triển khai là `.exe` PyInstaller: không có Python, `main.py` và `recovery.html` không có lối này. Trường bị khoá chỉ còn cách xoá `app.db` (mất dữ liệu). Hộp tạo tài khoản đầu tiên lại **không có ô nhập lại mật khẩu** → gõ nhầm là khoá. | Có (đọc mã + grep) |
| R3 | **Trung bình-cao** | Giáo viên thấy nút dành cho quản trị ("Tạo mã tra cứu", "Xuất mã") → bấm là bị từ chối. Giáo viên bấm "Chế độ học sinh tra cứu" được nhưng **không thoát được** (thoát cần quản trị) → kiosk bị khoá tới khi quản trị tới. | Có (Chromium) + đọc mã (`thoat_che_do_hoc_sinh`) |
| R4 | Trung bình | Người đầu tiên bấm "Tài khoản" khi chưa có ai trở thành quản trị (một học sinh ở kiosk cũng làm được). Rủi ro nằm ở khoảng chưa bật tài khoản. | Suy luận từ mã |
| R5 | Trung bình | Câu giải trình dễ gây hiểu sai: học sinh điểm 7,9, cột "Mức vào được 6,2 điểm", lý do "CLB dành một số chỗ cho nhóm được giữ chỗ" (RESERVED). Con số 6,2 là mức của người nhận cuối, không phải ngưỡng cho em. | Có (ảnh `12_gt_result.png`) |
| R6 | Trung bình | Câu giải trình cố định tiếng Việt, xưng "em", "các bạn", "CLB", "điểm thử thách", "điểm quyết tâm"; **cùng một câu cho giáo viên, phiếu in, học sinh** (giáo viên đọc "Em chưa có chỗ…"). Không theo từ vựng workspace → cản mục tiêu 12 ngành. Không có tiếng Anh. | Có |
| R7 | Trung bình | Nhật ký thao tác hiển thị tên nội bộ (`tao_tai_khoan`, `quan_tri`, `ok`, JSON thô), thời gian ISO, ô lọc "Thao tác" gõ tay phải biết tên hàm. Xem lời giải trình của một học sinh (`get_giai_trinh_hoc_sinh`) **không được ghi** (dữ liệu riêng tư). | Có |
| R8 | **Trung bình (trải nghiệm, Truong: "thiết kế rất tệ")** | Nguyên nhân: nhãn và ô chọn là các phần tử flex RỜI NHAU trong `.admin-form-grid`, `.check-row` không có CSS, danh sách `<ol>` mặc định; trong khi biểu mẫu CLB cùng thẻ đã có mẫu tốt (`.club-field`). Giao diện "Tiêu chí xếp / Thử cấu hình" vỡ bố cục (nhãn và ô chọn chảy một dòng, ô tích đè lên chữ gợi ý, danh sách số mặc định trình duyệt); trang so sánh: lẫn tiêu chí hai tầng thành một đoạn, cột Buổi hiện `__mac_dinh__`; không cảnh báo khi cấu hình thử vô nghĩa (chỉ theo nhóm mà chưa khai báo nhóm → thực chất bốc thăm thuần). | Có (ảnh `50`, `53`) |
| R9 | Thấp | Ô tra cứu nằm cuối thẻ Kết quả sau bảng 120 dòng; không bấm vào dòng để xem; luồng 4 bước (tạo mã → xuất → in → chế độ học sinh) không có hướng dẫn. Màn học sinh: ô chỉ có chữ mờ "Mã"/"Mã tra cứu", không logo/tên trường, không đếm ngược lúc bị khoá. Phụ đề thẻ Kết quả nói "Không có điểm hay số bốc thăm" trong khi ô tra cứu ngay bên dưới hiện cả hai. | Có |
| R10 | Thấp | Khoá 60 s theo mã học sinh / theo tên tài khoản: ai cũng khoá được người khác lặp lại (kiosk một máy nên chấp nhận được). Dòng bị từ chối khi chưa đăng nhập vẫn tăng nhật ký không giới hạn (đã có trong "Needs Truong" #3). Sau khi tạo quản trị đầu, hộp giữ nguyên và con trỏ nằm ở "Mật khẩu hiện tại" (sai bước). | Có / đọc mã |

Không phải lỗi: kiểm RESERVED (R5) thuật toán đúng theo suất dự trữ mềm; lỗi là cách **trình bày** (chỉ báo cáo, không đụng `compute_club_priority`).

## 4. Đóng vai người dùng — nhận xét tổng hợp
- **Quản trị lần đầu:** bật tài khoản dễ (một hộp), nhưng không có hướng dẫn bước kế (tạo giáo viên, lưu mật khẩu, cách khôi phục), hộp rất dài (đổi mật khẩu + danh sách + thêm + nhật ký chung một cửa sổ).
- **Giáo viên:** thanh bên sạch (chỉ Kết quả / Chi tiết / Nhập NV / Nhập điểm), nhưng còn nút không có quyền (R3).
- **Học sinh:** màn riêng đơn giản, lỗi sai mã ghi rõ và không lộ phần nào sai; tự xoá sau khi bỏ không — tốt. Nhưng nhãn ô mơ hồ (R9), câu giải thích khó hiểu ở ca RESERVED (R5).
- **Người hội đồng/phụ huynh:** phiếu in sạch, một trang một em, có mã tra cứu; cần câu giải thích RESERVED rõ hơn và bản tiếng Anh (R6).

## 5. Thêm để dễ dùng hơn (backlog, không nằm trong lô bắt buộc)
1. Nút **"In ngay"** cạnh "Mở thư mục" sau khi xuất phiếu (hiện chỉ in đường dẫn tệp dài).
2. **Cảnh báo 2 phút** trước khi phiên 15 phút hết hạn (hiện tự đăng xuất im lặng; kiểm lại: có mất dữ liệu đang gõ không).
3. Tìm học sinh: Enter chọn dòng đầu, phím mũi tên chọn dòng; chấp nhận gõ không dấu.
4. Mã QR/mã vạch trên phiếu → quét thay gõ (bớt gõ sai, bớt khoá).
5. Dòng **tóm tắt một câu** ở đầu trang so sánh ("49 em đổi CLB; nhóm X được nguyện vọng 1 tăng 10 điểm %…" — chỉ số, không kết luận).
6. Màn học sinh: chữ to, nút lớn, nút đổi ngôn ngữ ngay trên màn, đếm ngược lúc bị khoá.
7. Trình hướng dẫn "Bật tài khoản" 3 bước và trang "Quy trình giải trình" (tạo mã → in phiếu → chế độ học sinh).
8. Nhật ký: lọc theo ngày, theo "chỉ bị từ chối"; ẩn dòng đăng nhập/đăng xuất mặc định.
9. Nhớ tab/bộ lọc lần trước (đã có sẵn `localStorage` trong mẫu của dự án).

## 6. Kết luận của hội đồng
**Quyết định:** thuật toán phân bổ và hiệu năng đạt; kết quả chính thức (`match_results`) không bị đổi. **Nhưng không nên đưa cho học sinh dùng thật trước khi sửa R0–R3**: R0 làm lời giải trình nói sai kết quả sau khi chạy thử (nghiêm trọng nhất vì học sinh đọc được), R1 rò mã bí mật vào nhật ký, R2 khoá vĩnh viễn khi quên mật khẩu bản `.exe`, R3 giáo viên tự khoá kiosk. R4–R10 là chất lượng trải nghiệm, làm sau.
**Vì sao:** R0–R3 là lỗi về độ đúng, niềm tin và khả năng phục hồi, mỗi lỗi sửa nhỏ nhưng hậu quả lớn nếu gặp tại trường; phần còn lại không làm hỏng kết quả phân bổ.
**Việc tiếp theo (theo thứ tự):**
1. Chạy hai prompt GT4 (một phiên viết + một phiên soát): lô **L0** lọc chạy thử, **L1** nhật ký, **L2** nút theo vai, **L3** thiết lập + khôi phục.
2. Lô **L4–L7**: câu giải thích, màn học sinh/tra cứu, nhật ký dễ đọc, giao diện tiêu chí/so sánh.
3. Truong tự thử trên Windows: bản `.exe` + lối khôi phục mật khẩu (Linux không kiểm được).
4. Quyết các mục "Needs Truong" của `GT4_HOAN_THIEN.md` (chế độ học sinh chỉ quản trị vào; có ghi lượt xem giải trình; v.v.).
