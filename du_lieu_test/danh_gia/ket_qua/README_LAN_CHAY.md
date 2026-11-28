# Lần chạy đầy đủ DG1 — nguồn gốc các JSON

> **TOÀN BỘ SỐ ĐO TRÊN DỮ LIỆU MÔ PHỎNG** (bộ sinh `_sinh.py`, `mo_phong_fa_daa.py`, và các bộ mẫu trong `du_lieu_test/`), không phải khảo sát học sinh thật.
> Tệp này do `tao_readme_lan_chay.py` sinh từ trường `lan_chay` trong từng JSON.

| Tệp | Commit | Lệnh | Giây | Bắt đầu | Lưới |
|---|---|---|---|---|---|
| `bien_the_tieu_chi.json` | `d428f0851c` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan doi_chieu mac_dinh co_che bien_the quet nhieu_buoi co_san` | 289.6 | 2026-11-28 03:02:25 | 5 trường × 10 lần bốc thăm |
| `bo_co_san.json` | `17af13a152` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan co_san nhieu_buoi` | 26.1 | 2026-11-28 03:24:00 | 5 trường × 10 lần bốc thăm |
| `co_che_doi_chung.json` | `d428f0851c` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan doi_chieu mac_dinh co_che bien_the quet nhieu_buoi co_san` | 104.9 | 2026-11-28 03:02:25 | 5 trường × 10 lần bốc thăm |
| `doi_chieu_so_lieu.json` | `17af13a152` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan co_san nhieu_buoi` | 0.3 | 2026-11-28 03:24:00 | 5 trường × 10 lần bốc thăm |
| `mac_dinh.json` | `d428f0851c` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan doi_chieu mac_dinh co_che bien_the quet nhieu_buoi co_san` | 14.4 | 2026-11-28 03:02:25 | 5 trường × 10 lần bốc thăm |
| `nhieu_buoi.json` | `17af13a152` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan co_san nhieu_buoi` | 12.9 | 2026-11-28 03:24:00 | 5 trường × 10 lần bốc thăm |
| `quet_quy_mo.json` | `d428f0851c` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan doi_chieu mac_dinh co_che bien_the quet nhieu_buoi co_san` | 1162.7 | 2026-11-28 03:02:25 | 5 trường × 10 lần bốc thăm |
| `thoi_gian.json` | `c209817a57` | `python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan thoi_gian` | 23.5 | 2026-11-28 03:22:21 | 5 trường × 10 lần bốc thăm |
| `tinh_nang.json` | `d428f0851c` | `python du_lieu_test/danh_gia/do_tinh_nang.py --day-du` | 394.3 | 2026-11-28 03:02:25 | 5 trường × 10 lần bốc thăm |

**Cách đọc cột «Giây»**: thời gian tích luỹ từ lúc bắt đầu tiến trình đến lúc ghi tệp đó (các phần chạy nối nhau trong một tiến trình). Lần chạy chính (commit `d428f085`) mất 1 177 giây ≈ 19,6 phút cho phần lưới (< 60 phút nên KHÔNG phải giảm xuống lưới 3 × 5) và 394 giây cho `tinh_nang.json` (chạy song song trên máy 4 nhân).

**Nguồn gốc từng nhóm tệp** (mọi lần chạy ở cây làm việc sạch, `cay_lam_viec_sach = true`):
- `d428f085`: `mac_dinh`, `co_che_doi_chung`, `bien_the_tieu_chi`, `quet_quy_mo`, `tinh_nang` — lệnh `do_danh_gia.py --day-du --phan doi_chieu mac_dinh co_che bien_the quet nhieu_buoi co_san` và `do_tinh_nang.py --day-du`.
- `c209817a`: `thoi_gian` — chạy riêng một mình (không tranh CPU với phần khác) sau khi sửa lỗi bộ đo (`run_pipeline` bị từ chối đổi seed vì bốc thăm đã khoá).
- `17af13a1`: `bo_co_san`, `nhieu_buoi` — chạy lại sau khi sửa lỗi: bộ dữ liệu NHIỀU BUỔI có sẵn (bo_can_bang, bo_kich_tran, DQT 800) từng bị chạy gộp một buổi; nay chạy qua `run_rbda_nhieu_buoi` (test `test_bo_co_san_nhieu_buoi_khop_run_pipeline_that` so từng dòng với `run_pipeline` thật). `doi_chieu_so_lieu` ghi lại ở mỗi lần chạy; lần cuối ở commit này.
- Khác biệt mã giữa `d428f085` và lần chạy sau chỉ ở `do_danh_gia.py` (đường thời gian, bộ có sẵn nhiều buổi, `chay_tuan`), `in_bang.py` và giao diện (đổi tên lớp CSS, chữ i18n); kiểm: `git diff d428f085 HEAD -- du_lieu_test/danh_gia/do_danh_gia.py`. Không phần nào ở nhóm `d428f085` bị đổi đường tính.

**Cách tái lập** (từ thư mục gốc, môi trường có `openpyxl`; ~ 20 phút + ~ 7 phút): xem cột «Lệnh». In bảng: `python du_lieu_test/danh_gia/in_bang.py du_lieu_test/danh_gia/ket_qua`.

**Kiểm tự động trên toàn bộ JSON** (`python du_lieu_test/danh_gia/kiem_ket_qua.py`, thoát 0 = đạt): 356 ô `a.cap_chan` / `a.ngoai_danh_sach` của RB-DA đều = 0 (Boston, thứ tự bốc thăm, TTC được phép khác 0 và đúng là khác 0); `doi_chieu_so_lieu.dat = true` (bộ TEST, seed 42: 108/120, NV1 64, khớp từng dòng `match_results`); được xếp ≤ cận trên ở cả 90 cấu hình quét × 5 trường; `max_choices = 10` trùng mặc định; số em đổi CLB khớp `tieu_chi.so_sanh_lan_chay`.
