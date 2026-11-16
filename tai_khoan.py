"""GT3-L1: tài khoản + đăng nhập — phần LOGIC thuần (băm mật khẩu, bảng `tai_khoan`, phiên trong bộ nhớ).

Chỉ thư viện chuẩn. Nguyên tắc:
- Mật khẩu KHÔNG bao giờ được lưu, ghi nhật ký hay trả ra ngoài; chỉ lưu băm PBKDF2 + muối.
- Bảng rỗng = phần mềm chạy y như trước (không màn đăng nhập).
- Đây là lớp điều khiển/báo cáo; không dính gì tới `compute_club_priority`.
"""

import datetime
import hashlib
import hmac
import secrets
import time
import unicodedata

VAI_QUAN_TRI = "quan_tri"
VAI_GIAO_VIEN = "giao_vien"
CAC_VAI = (VAI_QUAN_TRI, VAI_GIAO_VIEN)

SO_VONG_BAM = 200_000
MAT_KHAU_TOI_THIEU = 8
TEN_TOI_DA = 60
SO_LAN_SAI_TOI_DA = 5
GIAY_KHOA = 60
GIAY_NGHI_TOI_DA = 15 * 60


def bam_mat_khau(mat_khau: str, muoi: bytes = None):
    """Trả `(bam, muoi)`. Muối ngẫu nhiên 16 byte nếu không đưa vào."""
    if muoi is None:
        muoi = secrets.token_bytes(16)
    bam = hashlib.pbkdf2_hmac("sha256", unicodedata.normalize("NFC", mat_khau).encode("utf-8"), muoi, SO_VONG_BAM)
    return bam, muoi


def kiem_tra_mat_khau(mat_khau: str, bam, muoi) -> bool:
    ung_vien, _ = bam_mat_khau(mat_khau, bytes(muoi))
    return hmac.compare_digest(ung_vien, bytes(bam))


def chuan_hoa_ten(ten):
    """Tên đã cắt khoảng trắng, hoặc None nếu không hợp lệ (rỗng / quá dài / không phải chuỗi)."""
    if not isinstance(ten, str):
        return None
    ten = unicodedata.normalize("NFC", ten).strip()
    if not ten or len(ten) > TEN_TOI_DA:
        return None
    return ten


def mat_khau_hop_le(mat_khau) -> bool:
    return isinstance(mat_khau, str) and len(mat_khau) >= MAT_KHAU_TOI_THIEU and bool(mat_khau.strip())


def _khoa_ten(ten: str) -> str:
    return unicodedata.normalize("NFC", ten).casefold()


# ----------------------------------------------------------------- bảng tai_khoan
def dem_tai_khoan(cur) -> int:
    return cur.execute("SELECT COUNT(*) FROM tai_khoan").fetchone()[0]


def dem_quan_tri(cur) -> int:
    return cur.execute("SELECT COUNT(*) FROM tai_khoan WHERE vai = ?", (VAI_QUAN_TRI,)).fetchone()[0]


def tim_ten(cur, ten: str):
    """Tên đúng như đã lưu (không phân biệt hoa/thường), hoặc None."""
    k = _khoa_ten(ten)
    for (t,) in cur.execute("SELECT ten FROM tai_khoan").fetchall():
        if _khoa_ten(t) == k:
            return t
    return None


def lay(cur, ten: str):
    """Dòng `(ten, vai, bam, muoi)` hoặc None."""
    t = tim_ten(cur, ten)
    if t is None:
        return None
    return cur.execute("SELECT ten, vai, bam, muoi FROM tai_khoan WHERE ten = ?", (t,)).fetchone()


def them(cur, ten: str, mat_khau: str, vai: str) -> None:
    bam, muoi = bam_mat_khau(mat_khau)
    cur.execute(
        "INSERT INTO tai_khoan (ten, vai, bam, muoi, tao_luc) VALUES (?, ?, ?, ?, ?)",
        (ten, vai, bam, muoi, datetime.datetime.now().isoformat(timespec="seconds")))


def dat_mat_khau(cur, ten: str, mat_khau: str) -> None:
    bam, muoi = bam_mat_khau(mat_khau)
    cur.execute("UPDATE tai_khoan SET bam = ?, muoi = ? WHERE ten = ?", (bam, muoi, ten))


def xoa(cur, ten: str) -> None:
    cur.execute("DELETE FROM tai_khoan WHERE ten = ?", (ten,))


def liet_ke(cur) -> list:
    return [{"ten": t, "vai": v, "tao_luc": l}
            for t, v, l in cur.execute("SELECT ten, vai, tao_luc FROM tai_khoan ORDER BY tao_luc, ten").fetchall()]


# ------------------------------------------------------------------ phiên + khoá
class TrangThaiDangNhap:
    """Phiên đăng nhập duy nhất của tiến trình kiosk, cùng bộ đếm sai/khoá theo từng tên.

    Đồng hồ tiêm được (`dong_ho`, mặc định `time.monotonic`) để test không phải chờ thật.
    """

    def __init__(self, dong_ho=None):
        self.dong_ho = dong_ho or time.monotonic
        self.phien = None            # {"ten", "vai", "db", "hoat_dong"}
        self._sai = {}               # khoá tên -> số lần sai liên tiếp
        self._khoa_den = {}          # khoá tên -> mốc đồng hồ hết khoá

    # --- khoá
    def giay_con_khoa(self, ten: str) -> int:
        den = self._khoa_den.get(_khoa_ten(ten))
        if den is None:
            return 0
        con = den - self.dong_ho()
        if con <= 0:
            self._khoa_den.pop(_khoa_ten(ten), None)
            self._sai.pop(_khoa_ten(ten), None)
            return 0
        return int(con) + (1 if con > int(con) else 0)

    def ghi_sai(self, ten: str) -> int:
        """Tăng đếm sai; đủ 5 lần thì khoá 60 giây. Trả số giây còn khoá (0 nếu chưa khoá)."""
        k = _khoa_ten(ten)
        self._sai[k] = self._sai.get(k, 0) + 1
        if self._sai[k] >= SO_LAN_SAI_TOI_DA:
            self._khoa_den[k] = self.dong_ho() + GIAY_KHOA
            return GIAY_KHOA
        return 0

    def xoa_dem(self, ten: str) -> None:
        k = _khoa_ten(ten)
        self._sai.pop(k, None)
        self._khoa_den.pop(k, None)

    # --- phiên
    def bat_dau(self, ten: str, vai: str, db: str) -> None:
        self.phien = {"ten": ten, "vai": vai, "db": db, "hoat_dong": self.dong_ho()}

    def ket_thuc(self) -> None:
        self.phien = None

    def phien_hien_tai(self, db: str):
        """Phiên còn hiệu lực với CSDL `db` (không làm mới giờ), hoặc None. Hết hạn thì tự đăng xuất."""
        p = self.phien
        if p is None:
            return None
        if p["db"] != db or self.dong_ho() - p["hoat_dong"] > GIAY_NGHI_TOI_DA:
            self.phien = None
            return None
        return p

    def cham_hoat_dong(self, db: str):
        """Như `phien_hien_tai` nhưng làm mới giờ nghỉ — dùng cho thao tác thật của người dùng."""
        p = self.phien_hien_tai(db)
        if p is not None:
            p["hoat_dong"] = self.dong_ho()
        return p
