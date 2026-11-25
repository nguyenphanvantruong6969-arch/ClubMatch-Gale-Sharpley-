"""DK3-L1: các bảng MỚI của cổng đăng ký thật (phòng, giáo viên, giai đoạn, CLB đăng ký, học sinh, nguyện vọng).

Toàn bộ là bảng mới (`CREATE TABLE IF NOT EXISTS`), tiền tố `dk_`, KHÔNG khoá ngoại sang bảng của bộ xếp, nên
chạy lại bao nhiêu lần cũng như nhau và không đụng dữ liệu cũ. `di_tru_schema` gọi `dam_bao_bang` (sao lưu trước
khi tạo lần đầu nếu CSDL đã có dữ liệu). Huy chương chỉ được LƯU ở đây; `compute_club_priority` không đọc bảng này
(bất biến 2, ngoại lệ D2 đường A).
"""

from rbda_priority_pipeline import SCHEMA_DK3, TEN_BANG_DK3, dam_bao_bang  # noqa: F401
