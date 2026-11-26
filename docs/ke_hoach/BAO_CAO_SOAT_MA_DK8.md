# Báo cáo soát mã DK8 (giao diện cổng đăng ký giống bản mẫu v8, L1–L5 + «L6» của phiên song song)

> Soát theo `.claude/skills/soat-ma/SKILL.md`: tự đọc và tự đo, không subagent, **chỉ báo cáo, không sửa mã**. Dữ liệu thử là MÔ PHỎNG.
> Phạm vi: `7c5dae5..1bb488d` (code) + `efe7fad`, `7dd5a83` (chỉ tài liệu). Báo cáo trung thực: chỗ chưa đo ghi "chưa đo".

## Phạm vi và mốc
- Tệp mã đổi (không tính tài liệu, test): `api_dang_ky.py` (+7/−1), `dang_ky.html`, `js/dang_ky_{nen,quan_tri,quan_tri_2,gv_hs}.js`, `style.css` (khối `.dk-*`, `#dkTop`, `body.dk-body`), `du_lieu_test/chup_dk8.py` (script chụp ảnh để so với bản mẫu).
- KHÔNG chạm: `rbda_*`, `api.py`, `api_nhap/xuat/quan_ly/bao_cao/sau_xep`, `fa_*`, `so_nhap`, `di_tru`, `wharton*`, `index.html` (đối chiếu `git diff --name-only`). Không đổi schema, CSV, thuật toán.
- Hàm cũ bị chạm (một bậc): `DK.chay`, `DK.hien`, `DK.quanTri`, `dk_trang_thai`. Không quá 40.
- Test: `dk8_l1..l5` + `dem_cong_khai` 40 ca; nhóm cổng `dkl_*`, `dk6_*`, `dk5_toan_trinh`, `dk3_cong` 54 ca; toàn bộ 20 tệp test cổng xanh ở máy trên head đã merge. CI run 1719 trên `1bb488d`: 17/17 job xanh (Linux 6/6, Windows 9/9, ruff, độ phủ ≥ 85 %).
- `kiem_nhanh.py`: **7/7 ĐẠT** (ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, trung_khit 15 ca, khong_sua_nhat_ky).

## Tầng 1 — Lõi thuật toán
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| Bất biến 1 (mặc định trùng khít) | ĐẠT | không tệp thuật toán nào đổi; `trung_khit` 15 ca |
| Bất biến 2 (ưu tiên không đọc thứ hạng) | ĐẠT | không đụng `compute_club_priority`; ô đặt huy chương học sinh vẫn dùng được (test L3 `test_d`) |
| Bất biến 3, 8 | Không áp dụng | không đổi hàm lựa chọn / bốc thăm |
Phát hiện: không có. Kết luận tầng: **Đạt**.

## Tầng 2 — Backend
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| `dk_trang_thai` công khai chỉ thêm số đếm | ĐẠT | diff: `so_gv = COUNT(*)`, `so_da_gui = COUNT(*) WHERE nop_luc IS NOT NULL`; không tên, không mã |
| Bất biến 4, 5, 6, 7 | Không áp dụng / ĐẠT | không đổi đường ghi, schema, CSV; SQL không tham số hoá là hằng, không có đầu vào người dùng |
Phát hiện: không có. Kết luận tầng: **Đạt**.

## Tầng 3 — Giao diện (chạy thật `browser_host` + Chromium, ba vai)
Script thử (không commit): tên giáo viên / CLB / học sinh chứa `<img src=x onerror=…>`.
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| XSS | ĐẠT | `window.__xss` = 0 ở học sinh, giáo viên, quản trị (các thẻ Việc bây giờ, Danh sách, Cài đặt, Thêm); không có `<img src=x>` trong DOM; `grep innerHTML` ở `js/dang_ky_*.js` chỉ ra dòng chú thích |
| Lộ dữ liệu người khác | ĐẠT | PIN giáo viên không có trong DOM học sinh |
| Lỗi mạng / HTTP 500 / đứt kết nối khi «Lưu mã» | ĐẠT | cả ba hiện thông báo đọc được («Không liên lạc được với phần lõi…»), không `undefined`; nút mở lại; không lỗi trang |
| Bấm đúp | ĐẠT | `dblclick` «Lưu mã» → đúng 1 lời gọi API |
| `prefers-reduced-motion` | ĐẠT | `test_e` (animationName `none`; dấu ✓ vẫn hiện, là trạng thái) |
| Không chỉ dựa vào màu | ĐẠT | trạng thái xong/lỗi có dấu ✓ / ! ở góc nút, không chỉ đổi màu viền |
| Dấu hợp lệ ở ô nhập | ĐẠT | chỉ mã học sinh, PIN 4 số, tên bắt buộc; `test_o` quét `[data-hl], .is-hop-le` = 0 ở bước nguyện vọng, huy chương, bài kiểm tra (bất biến 2) |
| Chữ tiếng Anh / i18n | Không áp dụng | cổng chỉ có tiếng Việt (ghi trong tệp nhánh) |
Phát hiện (xem bảng cuối). Kết luận tầng: **Đạt**, hai điều "chưa đo" ghi bên dưới.

## Tầng 4 — Vệ sinh, tài liệu, test
**Gây hỏng tạm 5 chỗ của L5 (hoàn tác bằng `git checkout`, `git status` sạch sau mỗi lần):**
| # | Hỏng | Test bắt? |
|---|---|---|
| M1 | PIN nhận mọi chuỗi số (`\d{4}` → `\d+`) | CÓ (`test_m`) |
| M2 | `ok:false` coi như «xong» | CÓ (`test_h`) |
| M3 | bỏ `animation:none` của nhánh `.dk-dau` | **KHÔNG** (xem phát hiện 1) |
| M3' | bỏ `animation:none` của nhánh `.dk-app` | không đỏ, nhưng là **mẫu hỏng tương đương**: hoạt ảnh chỉ khai báo trong `no-preference`, khối `reduce` là dự phòng thừa |
| M4 | mật khẩu quản trị có `data-hl` | CÓ (`test_l`) |
| M5 | bỏ `z-index` của dấu ✓ (dấu bị ô nhập vẽ đè, lỗi thật gặp lúc làm) | CÓ (`test_j`) |

- Chập chờn: tệp L5 chạy 3 + 3 lượt liền, 19/19 ca đều qua. 5 chỗ `wait_for_timeout` ngắn (120–400 ms) trong tệp L5; chưa thấy chập chờn, ghi nhận.
- Lỗi CI thật bắt được dọc đường (không phải do L5): `test_dk3 test_9` (đua thời gian từ L2) và `test_dk8_l1 test_d` (thanh trên không dính khi trang dài; máy nhà không tái hiện vì trang ngắn). Đã sửa ở sản phẩm, thêm `test_q` ở khổ thấp tái hiện lỗi trước khi sửa.
- Tài liệu: số tệp test 445 = `ls tests/test_*.py` (khớp `CLAUDE_CHI_TIET.md`); CHANGELOG, `SO_DANG_KY_33_MUC.md` có dòng DK8; `DK8_KHAC_BIET.md` không còn dòng «còn khác» (chưa đối chiếu lại sau thay đổi thứ tự thẻ của L6: **chưa đo**).
- Mã chết: `DK.phanHoiTiep` đã bỏ, không còn tham chiếu (`grep`); `ruff` sạch.

## Phát hiện
| # | Mức | Tệp | Vấn đề | Đường xảy ra | Đề xuất | Chắc chắn? |
|---|---|---|---|---|---|---|
| 1 | nhỏ | `style.css` khối DK8-L5 (`@media (prefers-reduced-motion: reduce)`) | Nhánh `.dk-dau .btn.is-xong/.is-loi::after` chưa có test giảm chuyển động (chỉ nút trong `#dkApp` được thử) | Bỏ dòng đó thì không test nào đỏ (M3) | Thêm một ca ở nút «Đăng xuất» với `emulate_media(reduced_motion="reduce")`; hoặc gộp hai nhánh vào một selector | đã tái hiện (M3) |
| 2 | nhỏ | `js/dang_ky_nen.js` `choNutMoi` | `MutationObserver` gắn vĩnh viễn vào `#dkApp`, mỗi lần đổi DOM chạy một hàm thoát sớm khi không có nút chờ | Mỗi lần vẽ lại màn | Chấp nhận; nếu cần, `disconnect()` khi `vuaXong` hết hạn | suy luận (chưa đo chi phí) |
| 3 | nhỏ | `docs/phien/..__checker.md` | Ghi «không sửa test cũ», nhưng «L6» có sửa selector/thứ tự ở `dk8_l1/l2/l4` (và tên tab «Thêm ▾» → «Thêm») | `git diff 37178fd..1bb488d -- tests/` | Sửa câu cho đúng; việc đổi test là theo chỉ đạo của Truong (đổi thứ tự thẻ), không thấy assertion nào bị bỏ | đã tái hiện (diff) |
| 4 | nhỏ | `tests/test_giao_dien_dk8_l5.py` | 5 `wait_for_timeout` cố định | Máy chậm | Thay bằng chờ điều kiện nếu sau này chập chờn | suy luận |
| 5 | chưa đo | lớp `RBDA.callApi` | Phản hồi `ok:false` giả bằng `page.route` bị lớp gọi API biến thành lỗi chung, nên nhánh «`ok:false` có mã lỗi thật» chưa được thử qua mạng giả (đã có test đơn vị qua `DK.chay`, `test_b`) | — | Thử bằng lỗi thật từ backend (ví dụ nhập sai) | chưa đo |
Tóm tắt: 0 chặn, 0 nên sửa, 4 nhỏ, 1 chưa đo.

## Bốn khía cạnh
- **Bảo mật:** XSS = 0 ở ba vai; không `innerHTML`; số đếm công khai không có tên/mã.
- **Hiệu năng:** không có vòng lặp truy vấn mới; hai `COUNT(*)` mỗi lần mở trang đầu (bảng cỡ vài trăm dòng; chưa đo ở 800 em).
- **Đúng đắn:** hai chỗ trả `ok:true` giả khi lỗi nhập nay trả `ok:false`; dấu ✓ không hiện cho thao tác lỗi (`test_h`).
- **Bảo trì:** cơ chế phản hồi tập trung ở một chỗ (`DK.phanHoi`), mọi nút qua `DK.chay`.

## Điểm tốt
- Dấu hợp lệ chỉ gắn có chủ đích vào ba loại ô và có test quét ngược ở bước nguyện vọng / huy chương / bài kiểm tra.
- Dấu vẽ bằng `::after` cỡ cố định: kiểm bằng `offset*` rằng bố cục không đổi ở ba loại nút trong ba trạng thái.
- Hai lỗi CI thật được tái hiện bằng test trước khi sửa.

## Kết luận
**Đạt** (4 tầng; không có phát hiện chặn hay nên sửa). Danh sách việc (Đề xuất, chờ Truong duyệt): #1 thêm test giảm chuyển động cho thanh trên; #3 sửa câu trong tệp checker; #2, #4, #5 để sau.
