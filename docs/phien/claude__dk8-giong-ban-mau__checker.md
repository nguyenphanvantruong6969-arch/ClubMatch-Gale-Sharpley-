# DK8 checker M1+M2 — 7c5dae5..1bb488d (efe7fad chỉ là docs)

**PASS**
- Test: dk8_l1..l5 + dem_cong_khai 40 passed; dkl_* + dk6_* + dk5_toan_trinh + dk3_cong 54 passed. ruff sạch; kiem_nhanh 7/7 (trung_khit 15 ca khớp sau khi fetch origin/main).
- Tests: mọi file dk8 là file MỚI, không sửa test cũ. Commit L6 chỉ đổi chỉ mục/thứ tự (Giáo viên→Học sinh→Quản trị) và tên tab «Thêm ▾»→«Thêm» (exact=True): chevron nay là CSS; không phải làm yếu assertion. Test cũ của app chính vẫn dùng «Thêm ▾» ở index.html, không đụng.
- App chính: index.html không đổi; style.css chỉ thêm khối cuối `.dk-*`/`#dkTop`/`body.dk-body` (xoá đúng 1 dòng `.dk-chua-di`, thay bằng bản mới).
- dk_trang_thai chỉ thêm `so_gv`, `so_da_gui` (số đếm, không tên/mã). Bảo vệ tự làm mới (`coThuSeMat`, dấu vân tay) còn nguyên.
- Huy chương: bước «Đặt huy chương» còn cho mọi học sinh; `data-hl` chỉ ở mã HS, PIN, tên bắt buộc; không có ở nguyện vọng/huy chương/đáp án.
- Ảnh (landing, việc_2, hs_buoi): khớp v8 về thứ tự thẻ, thanh trên, thẻ giai đoạn; khác nhỏ chấp nhận được (ô «Chọn hạn chót khác», nút vàng đóng GV — chức năng thật).
- CI: run 1719 xanh trên code head 1bb488d (17 job); run 1720 (efe7fad, docs-only) đang chạy lúc soát.
