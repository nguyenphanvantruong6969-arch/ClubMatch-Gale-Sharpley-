# DG1 — bộ đo định lượng (nguyện vọng, chưa được xếp, chỉ tiêu, đổi tiêu chí)

> **Toàn bộ số đo trên DỮ LIỆU MÔ PHỎNG, không phải khảo sát học sinh thật.** Phần nhận xét / kết luận do học sinh tự viết.

| Tệp | Việc |
|---|---|
| `_chi_so.py` | Chỉ số THUẦN (A nguyện vọng, B chưa xếp + cận trên ghép cực đại, C chỉ tiêu) + bảng `DINH_NGHIA` |
| `_sinh.py` | Bộ sinh trường mô phỏng (α độ tập trung, ρ liên quan điểm–năng lực, κ chỉ tiêu/HS) + ghi Sổ nhập |
| `do_danh_gia.py` | Bộ chạy: lưới seed, biến thể tiêu chí, 4 cơ chế đối chứng, thời gian, nhiều buổi, bộ có sẵn |
| `in_bang.py` | In bảng Markdown từ JSON (không có câu diễn giải) |
| `ket_qua/` | JSON của lần chạy ĐẦY ĐỦ đã commit; `README_LAN_CHAY.md` ghi commit, lệnh, thời gian |
| `ket_qua_nhanh/`, `ket_qua_that/` | Bị `.gitignore` (chạy nhanh / dữ liệu thật — không bao giờ commit) |

## Chạy

```bash
./.venv/bin/python du_lieu_test/danh_gia/do_danh_gia.py --nhanh       # vài giây, 120 & 300 HS, ra ket_qua_nhanh/
./.venv/bin/python du_lieu_test/danh_gia/do_danh_gia.py --day-du      # đầy đủ (≈ 30 phút), ra ket_qua/
./.venv/bin/python du_lieu_test/danh_gia/do_danh_gia.py --giam        # lưới giảm 3 trường × 5 lần bốc thăm
./.venv/bin/python du_lieu_test/danh_gia/do_danh_gia.py --so-nhap SO.xlsx   # dữ liệu thật → ket_qua_that/ (KHÔNG commit)
./.venv/bin/python du_lieu_test/danh_gia/in_bang.py du_lieu_test/danh_gia/ket_qua
./.venv/bin/python -m pytest -q tests/test_dg1_chi_so.py tests/test_dg1_sinh.py tests/test_dg1_do_danh_gia.py
```

Chạy là **tự kiểm trước**: `doi_chieu_so_lieu.json` phải đạt (bộ TEST, seed 42, qua `run_pipeline` thật = 108/120,
nguyện vọng 1 = 64, khớp từng dòng `match_results` với đường lõi; 0 cặp phá vỡ), nếu không bộ chạy dừng với mã 2.

## Hai nguồn ngẫu nhiên (không trộn)
* **seed dữ liệu** (`SEED_DU_LIEU`, 5 giá trị) = một trường mô phỏng khác;
* **seed bốc thăm** (`SEED_BOC_THAM`, 10 giá trị) = cùng trường, lần bốc STB khác.

KTC 95 % kiểu t tính trên trung bình THEO TRƯỜNG; `sd_boc_tham` là độ lệch chuẩn giữa các lần bốc trong cùng trường.

## Đường chạy và giới hạn
* Lưới dùng thẳng `rbda_priority_pipeline.run_rbda` trên dữ liệu trong bộ nhớ (cùng hàm `run_pipeline` gọi); đã kiểm
  khớp `run_pipeline` thật bằng phép đối chiếu bộ TEST và `tests/test_dg1_do_danh_gia.py`. Đi qua `PipelineAPI` + Sổ nhập
  thật chỉ ở phép đối chiếu và `thoi_gian.json`.
* Cơ chế đối chứng (`co_che_doi_chung.py`) gọi `club_choice_function` thật; không ghi tầng dự trữ nên «suất dự trữ đã dùng» chỉ đúng với RB-DA.
* Danh sách mô phỏng dài 3–6 (cắt Top 1–10 của biểu mẫu); một mô hình trường duy nhất; điểm do bộ sinh tạo.
