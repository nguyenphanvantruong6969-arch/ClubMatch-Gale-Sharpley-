"""MT1-L3 — các phép ĐO thuần của thẻ mục tiêu (không đọc CSDL, không chạy xếp).

Kết quả một lần xếp được đưa vào dạng `{(student_id, buoi): (club_id | None, rank | None)}`: `rank` là vị trí
CLB đó trong danh sách nguyện vọng của em (`rank_in_student_pref`); `club_id` None = em chưa có chỗ buổi đó.
Số trả ra dùng để mô tả một lần xếp ĐÃ có hoặc ước tính; không phép nào đọc thứ hạng nguyện vọng để xếp ai
(bất biến 2 chỉ cấm điều đó ở `compute_club_priority`; ở đây chỉ ĐỌC kết quả để báo cáo).
"""

from __future__ import annotations

NGUONG_AN_SO = 5            # số đếm 1–4 hiện là "dưới 5" (người nhận báo cáo không nhận ra được từng em)
NGAY_HANG_KEM = 10 ** 6     # em chưa có chỗ xếp sau mọi em có chỗ
HANG_KHONG_BIET = 999       # em có chỗ nhưng không có thứ hạng (CLB không nằm trong danh sách) xếp sau mọi hạng


def an_so(n: int, nguong: int = NGUONG_AN_SO) -> dict:
    """`{"n": số hoặc None, "duoi_5": bool}`: số 1…nguong-1 bị ẩn ngay trong dữ liệu (không chỉ ở giao diện)."""
    if 1 <= n < nguong:
        return {"n": None, "duoi_5": True}
    return {"n": n, "duoi_5": False}


def _diem(clb_hang) -> int:
    """Càng nhỏ càng tốt: hạng 1 < hạng 2 < … < có chỗ không rõ hạng < chưa có chỗ."""
    clb, hang = clb_hang
    if clb is None:
        return NGAY_HANG_KEM
    return hang if isinstance(hang, int) and hang > 0 else HANG_KHONG_BIET


def so_sanh_hang(truoc: dict, sau: dict) -> tuple[set, set]:
    """`(em tốt hơn, em xuống sau)` của kết quả `sau` so với `truoc`, đếm theo (em, buổi) có ở CẢ HAI.

    Một em có buổi tốt hơn thì vào "tốt hơn"; có buổi kém hơn thì vào "xuống sau" (em hai chiều có mặt ở cả hai)."""
    tot, xuong = set(), set()
    for khoa in truoc.keys() & sau.keys():
        a, b = _diem(truoc[khoa]), _diem(sau[khoa])
        if b < a:
            tot.add(khoa[0])
        elif b > a:
            xuong.add(khoa[0])
    return tot, xuong


def clb_dong_nhat(so_nv1: dict, so_luong: int = 5) -> list[str]:
    """Các CLB được xếp nguyện vọng 1 nhiều nhất: nhiều trước, bằng nhau thì theo mã."""
    return [c for c, _ in sorted(so_nv1.items(), key=lambda x: (-x[1], x[0]))[:so_luong]]


def dat_o_clb(sau: dict, thanh_vien: set, tong_em: int, clb_xet, ti_le: float = 0.9) -> tuple[int, int]:
    """`(số CLB đạt, số CLB xét)`: CLB đạt khi tỉ lệ nhóm trong số em được nhận ≥ `ti_le` × tỉ lệ nhóm toàn trường."""
    chung = len(thanh_vien) / tong_em if tong_em else 0.0
    dat = 0
    for cid in clb_xet:
        nhan = {k[0] for k, (clb, _r) in sau.items() if clb == cid}
        if nhan and len(nhan & thanh_vien) / len(nhan) >= ti_le * chung:
            dat += 1
    return dat, len(list(clb_xet))


def ty_le_top(kq: dict, thanh_vien: set, top: int = 3) -> tuple | None:
    """`(tỉ lệ em của nhóm, tỉ lệ em ngoài nhóm)` có chỗ trong `top` nguyện vọng đầu; None nếu một phía rỗng."""
    trong = [v for k, v in kq.items() if k[0] in thanh_vien]
    ngoai = [v for k, v in kq.items() if k[0] not in thanh_vien]
    if not trong or not ngoai:
        return None

    def ty_le(ds):
        return sum(1 for clb, hang in ds if clb is not None and isinstance(hang, int) and hang <= top) / len(ds)
    return ty_le(trong), ty_le(ngoai)


def co_khoang_cach(kq: dict, thanh_vien: set, top: int = 3) -> bool:
    """Nhóm có KÉM hơn phần còn lại về tỉ lệ có chỗ trong `top` nguyện vọng đầu không (MT0 F5)."""
    r = ty_le_top(kq, thanh_vien, top)
    return bool(r) and r[0] < r[1]


def pct_nguyen_vong_1(kq: dict) -> float:
    """% (em, buổi) được CLB nguyện vọng 1, làm tròn một chữ số."""
    if not kq:
        return 0.0
    return round(100.0 * sum(1 for clb, hang in kq.values() if clb is not None and hang == 1) / len(kq), 1)


def so_chua_co_cho(kq: dict) -> int:
    """Số em còn thiếu chỗ ở ít nhất một buổi."""
    return len({k[0] for k, (clb, _r) in kq.items() if clb is None})
