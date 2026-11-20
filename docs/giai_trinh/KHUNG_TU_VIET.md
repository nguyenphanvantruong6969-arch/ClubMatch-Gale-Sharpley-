# Khung các phần học sinh phải tự viết

> **Chỉ là khung.** Tệp này liệt kê những tài liệu Truong phải **tự viết bằng lời của mình**, kèm đề mục, câu hỏi gợi ý và
> nguồn số liệu. Không có câu viết sẵn. Theo `CLAUDE.md` mục *Academic integrity*: nhận xét, diễn giải và kết luận của đề
> tài do học sinh viết; AI không soạn. Mọi số liệu trong kho là **dữ liệu mô phỏng**, phải ghi rõ như vậy khi dùng.
> Lập ngày 20/11/2026. Khi dùng khung này, ghi vào nhật ký AI: "AI lập khung đề mục và câu hỏi gợi ý; học sinh tự viết nội dung."

## 0. Danh sách và tình trạng

| # | Tài liệu | Nằm ở đâu | Phần phải tự viết | Tình trạng (20/11) |
|---|---|---|---|---|
| 1 | Báo cáo đề tài 15 trang | ngoài kho (`Xay_dung_phan_mem_sap_xep_hoc_sinh_15trang_*.docx`) | nhận xét, diễn giải, kết luận, giới hạn | Bản rà soát `BAO_VE_RA_SOAT_BAO_CAO.md` (24/10) chỉ ra 13 chỗ cần em sửa; chưa có các phần mới từ 11/11 |
| 2 | Bảng phân công | `docs/giai_trinh/PHAN_CONG.md` | toàn bộ bảng | Trống |
| 3 | Đánh giá vai trò của AI | `docs/giai_trinh/VAI_TRO_AI.md` §4 | nhận xét mức đóng góp, so sánh phần của em với phần của AI | Trống |
| 4 | Poster | `poster/DU_LIEU_POSTER.md` (bảng tra ô) | chữ trong các ô H2, G1, S1–S3 (dòng nghiêng), G2, T1–T3, P1–P6 | Chưa điền; ngân hàng số liệu §4 có số cũ (ví dụ số ca kiểm thử), cần đối chiếu lại |
| 5 | Lời dẫn video | `docs/giai_trinh/KICH_BAN_VIDEO.md` | cột lời dẫn | Chưa có lời dẫn |
| 6 | Trả lời câu hỏi bảo vệ | `BAO_VE_BO_CAU_HOI.md` | câu trả lời của em (để luyện, không nộp) | Tự luyện |

## 1. Báo cáo đề tài — khung đề mục

Giữ cấu trúc báo cáo hiện có của em; dưới đây chỉ là các mục **cần có** và câu hỏi để em tự trả lời.

### 1.1 Đặt vấn đề
- [em viết] Trường em gặp vấn đề gì khi xếp học sinh vào CLB? Ai bị ảnh hưởng?
- [em viết] Vì sao cách làm thủ công / bằng biểu mẫu chưa đủ?
- Nguồn: `docs/ke_hoach/BOI_CANH_DU_AN.md` §1, phần mô tả bài toán.

### 1.2 Câu hỏi nghiên cứu và giả thuyết
- [em viết] Câu hỏi chính (một câu). Câu hỏi phụ (tối đa ba).
- [em viết] Giả thuyết — lưu ý mục B2 trong `BAO_VE_RA_SOAT_BAO_CAO.md` (giả thuyết đang tự làm yếu chính nó).

### 1.3 Phương pháp
- [em viết] Thuật toán Gale–Shapley học sinh đề nghị, suất dự trữ mềm, một lần bốc thăm, ưu tiên hai tầng: giải thích bằng lời của em.
- [em viết] Cách kiểm chứng: dữ liệu mô phỏng, số seed, các phép đo (ổn định, chống khai gian, thời gian).
- Nguồn: `docs/CO_CHE_THUAT_TOAN.md`, `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`, `du_lieu_test/thu_tai/ket_qua_thu_tai.csv`.

### 1.4 Kết quả
- [em viết] Bảng số chính (ghi "dữ liệu mô phỏng" dưới mỗi bảng). Chọn số từ nguồn, không làm tròn khác nguồn.
- [em viết] So sánh với cơ chế khác (mục B4 của bản rà soát: Boston, TTC).
- Nguồn: `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`, `docs/NGHIEN_CUU_TOI_UU.md`.

### 1.5 Phần mới (nếu em đưa vào báo cáo): ra quyết định theo mục tiêu giáo dục
- [em viết] Vì sao một trường cần chọn mục tiêu (năng lực / cơ hội như nhau / dành chỗ cho một nhóm)?
- [em viết] Cái giá của việc giữ chỗ cho một nhóm: em đọc bảng số thế nào? Điều gì làm em bất ngờ?
- [em viết] Vì sao nên công bố *cách tính* thay vì *con số*? Em có đồng ý không, vì sao?
- [em viết] Giới hạn của phép đo này (dữ liệu tự sinh, một nhóm, một buổi).
- Nguồn số liệu: `docs/fable/08_MT0_MEMO.md` (bảng F1–F8), chạy lại: `python du_lieu_test/do_muc_tieu_mt0.py`.

### 1.6 Thảo luận
- [em viết] Kết quả trả lời câu hỏi nghiên cứu đến đâu? Chỗ nào chưa trả lời được?
- [em viết] Điều em sẽ làm khác nếu làm lại.

### 1.7 Giới hạn nghiên cứu (mục B5 của bản rà soát: hiện chưa có)
- [em viết] Dữ liệu mô phỏng, chưa chạy với học sinh thật; chưa thử trên máy kiosk và hệ thống Microsoft thật; các giới hạn khác em thấy.

### 1.8 Kết luận và hướng phát triển
- [em viết] Ba điều chính em rút ra.
- [em viết] Hướng tiếp (ví dụ: thay đổi theo thời gian, các ngành khác) — em chọn và tự lý giải.

### 1.9 Tài liệu tham khảo, Phụ lục
- [em viết] Kiểm lại tên tác giả, năm, tên bài (danh sách cũ có lỗi; tên đúng là **Gale–Shapley**).
- Phụ lục 1 = nhật ký AI: `docs/nhat_ky_ai/NHAT_KY_AI.docx` (đã cập nhật đến 20/11/2026).

## 2. Bảng phân công (`PHAN_CONG.md`)
| Thành viên | Họ tên | Mã nguồn | Nghiên cứu | Ghi chú (ngày, bằng chứng) |
|---|---|---|---|---|
| Thành viên 1 | [em điền] | [em điền] | [em điền] | [em điền] |
| Thành viên 2 | [em điền] | [em điền] | [em điền] | [em điền] |

## 3. Vai trò của AI — §4 (`VAI_TRO_AI.md`)
- [em viết] Phần nào em tự làm, phần nào AI làm theo yêu cầu của em? (đối chiếu `NHAT_KY_AI_DE_DOC.md` mục 2, 4)
- [em viết] Em kiểm tra việc AI làm bằng cách nào?
- [em viết] Một lần AI làm sai hoặc hiểu sai và em đã xử lý ra sao (ví dụ có ghi trong nhật ký: Giai đoạn 15).
- [em viết] Em học được gì từ việc làm cùng AI?

## 4. Poster (`poster/DU_LIEU_POSTER.md`)
| Ô | Em viết gì | Nguồn |
|---|---|---|
| H2 | Thông điệp chính, một câu | §7 bảng H2 (chỉ chọn hướng, tự đặt câu) |
| G1, G2 | Chú thích ảnh, tóm tắt sơ đồ | §7 |
| S1–S3 | Dòng nghiêng giải nghĩa ba con số | §1, §4 — **đối chiếu lại số mới nhất trước khi in** |
| T1–T3 | Vấn đề, cách dùng, xem thử | §2 |
| P1–P6 | Bốn lợi ích, hai biểu đồ nói gì, tuyên bố sử dụng AI | §3, §5 (câu không được viết) |

## 5. Lời dẫn video (`KICH_BAN_VIDEO.md`)
| Cảnh (đã có) | Lời dẫn |
|---|---|
| Mỗi cảnh trong kịch bản | [em viết] 1–3 câu, nói điều người xem cần hiểu ở cảnh đó |
| Cảnh mở đầu | [em viết] vấn đề của trường em |
| Cảnh kết | [em viết] điều em muốn người xem nhớ |
