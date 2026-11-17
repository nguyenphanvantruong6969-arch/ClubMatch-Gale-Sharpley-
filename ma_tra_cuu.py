"""GT1-L4: mã tra cứu của học sinh. CHỈ để một em tự xem lời giải thích của chính mình.

Mã sinh bằng `secrets` (không dùng `random`, `hash()` hay số khoá bốc thăm), nên KHÔNG liên quan tới kết quả xếp
và không đụng bất biến 3. Không ký tự dễ nhầm (không O, 0, I, 1, L).
"""

import secrets

BANG_CHU = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
DO_DAI = 8
SO_LAN_SAI_TOI_DA = 5
GIAY_KHOA = 60


def sinh_ma() -> str:
    return "".join(secrets.choice(BANG_CHU) for _ in range(DO_DAI))


def sinh_ma_moi(da_dung) -> str:
    """Một mã chưa có trong `da_dung` (tập hợp). Va chạm thì thử lại."""
    while True:
        m = sinh_ma()
        if m not in da_dung:
            return m


def chuan_hoa(ma) -> str:
    """Bỏ khoảng trắng hai đầu, viết hoa. Không phải chuỗi -> chuỗi rỗng."""
    return ma.strip().upper() if isinstance(ma, str) else ""
