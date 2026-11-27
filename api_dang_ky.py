"""DK3-L2: API cổng đăng ký thật (quản trị, giáo viên, học sinh) trên các bảng `dk_*` (xem `dang_ky_schema.py`).

Hợp đồng `{ok, data, errors}`; lỗi là mã trong `i18n_errors.py` (tiền tố `dk_`). Cổng quyền chung của phần mềm (GT3) coi
mọi hàm `dk_*` là CÔNG KHAI vì cổng này TỰ kiểm quyền bằng phiên riêng (token trong bộ nhớ): mật khẩu quản trị và mã PIN
đều lưu băm PBKDF2 + muối, không bao giờ trả ra ngoài (PIN chỉ hiện MỘT lần lúc tạo / đặt lại).

Huy chương chỉ được LƯU (D2, đường A): mặc định theo thứ tự xếp ở tầng đăng ký, học sinh được ghi đè; `compute_club_priority`
không đọc bảng này và không bao giờ nhận hạng nguyện vọng (bất biến 2).
"""

import datetime
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
import unicodedata

from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok

_log = logging.getLogger(__name__)

QUAN_TRI, GIAO_VIEN, HOC_SINH = "quan_tri", "giao_vien", "hoc_sinh"
CAC_GIAI_DOAN = ("chuan_bi", "gv_dang_ky", "duyet", "hs_dang_ky", "nhap_diem", "xuat")
LOAI_CLB = ("Tự do", "Giới hạn", "Tuyển chọn")
HUY_CHUONG = ("Vàng", "Bạc", "Đồng")
TU_DO, TUYEN_CHON = "Tự do", "Tuyển chọn"
TOI_DA_NV_BUOI = 10
TOI_DA_THI_BUOI = 5
GIAY_NGHI_QUAN_TRI = 120
GIAY_NGHI_KHAC = 60
SO_VONG_PIN = 10_000
SO_LAN_SAI_TOI_DA = 5
PHUT_KHOA = 5
TOI_DA_GV = 300                                   # VG2-L1: trần tài khoản giáo viên (chống tạo rác)
TEN_GD_VI = {"chuan_bi": "Chuẩn bị", "gv_dang_ky": "Giáo viên đăng ký", "duyet": "Duyệt CLB", "hs_dang_ky": "Học sinh đăng ký",
             "nhap_diem": "Nhập điểm", "xuat": "Xuất"}
BUOI_MAC_DINH = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
KHOI_MAC_DINH = [6, 12]


class _Loi(Exception):
    def __init__(self, ma, **tham_so):
        if ma == "dk_sai_giai_doan" and "phan" in tham_so:          # VG2-L4: không lộ mã nội bộ («gv_dang_ky») cho người dùng
            tham_so["phan"] = TEN_GD_VI.get(tham_so["phan"], tham_so["phan"])
        self.loi = err(ma, **tham_so)
        super().__init__(ma)


def _bam(pin: str, muoi: bytes = None):
    muoi = muoi or secrets.token_bytes(16)
    return hashlib.pbkdf2_hmac("sha256", unicodedata.normalize("NFC", str(pin)).encode(), muoi, SO_VONG_PIN), muoi


def _dung(pin, bam, muoi) -> bool:
    return hmac.compare_digest(_bam(pin, bytes(muoi))[0], bytes(bam))


def _chuan_ten(v) -> str:
    """VG1-L1 (D1): khoá so khớp tên/mã khi đăng nhập: NFC, gộp khoảng trắng trong, bỏ hoa/thường. KHÔNG dùng để lưu."""
    return " ".join(unicodedata.normalize("NFC", str(v or "")).split()).casefold()


def _chuan_khong_dau(v) -> str:
    """VG2-L1 (Truong): khoá so khớp lỏng khi đăng nhập: NFKC (chữ toàn khổ / «font» khác về chữ thường), bỏ ký tự ẩn (Cf),
    bỏ dấu tiếng Việt (kể cả đ → d), gộp khoảng trắng, bỏ hoa/thường. «Đặng Văn Nam» = «DANG VAN NAM». KHÔNG dùng để lưu."""
    s = unicodedata.normalize("NFKD", str(v or ""))
    s = "".join(c for c in s if not unicodedata.combining(c) and unicodedata.category(c) != "Cf")
    return " ".join(s.replace("đ", "d").replace("Đ", "d").split()).casefold()


def _chuan_pin(v) -> str:
    """VG2-L1: PIN gõ số toàn khổ («１２３４») thành chữ số ASCII (NFKC); bỏ khoảng trắng / ký tự ẩn. Số Ả Rập vẫn sai dạng (VG1-L1)."""
    return "".join(c for c in unicodedata.normalize("NFKC", str(v or "")) if unicodedata.category(c) != "Cf").strip()


def _ung_vien(dong, k_lay, ten):
    """Khớp đúng (cùng dấu, `_chuan_ten`) trước; không có thì khớp không dấu (`_chuan_khong_dau`), có thể nhiều người."""
    k = _chuan_ten(ten)
    dung = [x for x in dong if _chuan_ten(k_lay(x)) == k]
    if dung:
        return dung
    k = _chuan_khong_dau(ten)
    return [x for x in dong if _chuan_khong_dau(k_lay(x)) == k]


def _pin_de_doan(pin) -> bool:
    """VG2-L1 (D2): 4 số giống nhau, dãy tăng / giảm liên tiếp (0123…6789, 3210…9876), 2580. Chỉ áp cho PIN MỚI."""
    p = str(pin or "")
    if not re.fullmatch(r"\d{4}", p):
        return False
    d = [int(c) for c in p]
    return len(set(d)) == 1 or p == "2580" or all(d[i + 1] - d[i] == 1 for i in range(3)) or all(d[i] - d[i + 1] == 1 for i in range(3))


def _pin_moi() -> str:
    while True:
        p = "%04d" % secrets.randbelow(10000)
        if not _pin_de_doan(p):
            return p


def _khoi_cua_lop(lop):
    m = re.match(r"\s*(\d{1,2})", str(lop or ""))
    return int(m.group(1)) if m else None


def _so_nguyen(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if isinstance(v, str) and v.strip().lstrip("-").isdigit():
        v = int(v.strip())
    return v if isinstance(v, int) else None


class DangKyMixin:
    # ---------------------------------------------------------------- nền
    def _dk_bay_gio(self) -> datetime.datetime:
        return datetime.datetime.now()

    def _dk_dong_ho(self) -> float:
        return getattr(self, "_dong_ho", time.monotonic)()

    def _dk_phien_dict(self) -> dict:
        d = getattr(self, "_dk_phien_", None)
        if d is None or d.get("_db") != self.db_path:
            d = self._dk_phien_ = {"_db": self.db_path}
        return d

    def _dk_gioi_han(self, cur):
        """(tối đa nguyện vọng, tối đa bài thi) mỗi buổi: đọc từ cài đặt, mặc định 10 và 5 (D21, D44)."""
        def doc(khoa, mac):
            v = _so_nguyen(self._dk_cai_dat(cur, khoa, str(mac)))
            return v if v and v > 0 else mac
        return doc("toi_da_nv", TOI_DA_NV_BUOI), doc("toi_da_thi", TOI_DA_THI_BUOI)

    def dk_dat_gioi_han(self, token, toi_da_nv=None, toi_da_thi=None):
        """Quản trị: đổi số nguyện vọng / bài thi tối đa mỗi buổi (1–30; bài thi không vượt nguyện vọng)."""
        def lam(cur, p):
            nv0, thi0 = self._dk_gioi_han(cur)
            nv = nv0 if toi_da_nv is None else _so_nguyen(toi_da_nv)
            thi = thi0 if toi_da_thi is None else _so_nguyen(toi_da_thi)
            if nv is None or thi is None or not (1 <= nv <= 30 and 1 <= thi <= nv):
                raise _Loi("dk_gioi_han_sai")
            self._dk_dat(cur, "toi_da_nv", str(nv))
            self._dk_dat(cur, "toi_da_thi", str(thi))
            self._dk_ghi_nk(cur, QUAN_TRI, "dat_gioi_han", "%d / %d" % (nv, thi))
            return {"toi_da_nv": nv, "toi_da_thi": thi}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def _dk_cai_dat(self, cur, khoa, mac_dinh=None):
        r = cur.execute("SELECT gia_tri FROM dk_cai_dat WHERE khoa = ?", (khoa,)).fetchone()
        return mac_dinh if r is None else r[0]

    def _dk_dat(self, cur, khoa, gia_tri):
        cur.execute("INSERT INTO dk_cai_dat (khoa, gia_tri) VALUES (?, ?) ON CONFLICT(khoa) DO UPDATE SET "
                    "gia_tri = excluded.gia_tri", (khoa, gia_tri))

    def _dk_ghi_nk(self, cur, vai, hanh_dong, chi_tiet=""):
        cur.execute("INSERT INTO dk_nhat_ky (luc, vai, hanh_dong, chi_tiet) VALUES (?, ?, ?, ?)",
                    (self._dk_bay_gio().isoformat(timespec="seconds"), vai, hanh_dong, str(chi_tiet)[:500]))

    def _dk_buoi_khoi(self, cur):
        buoi = json.loads(self._dk_cai_dat(cur, "buoi", json.dumps(BUOI_MAC_DINH, ensure_ascii=False)))
        khoi = json.loads(self._dk_cai_dat(cur, "khoi", json.dumps(KHOI_MAC_DINH)))
        return buoi, khoi

    def _dk_giai_doan_hien_tai(self, cur) -> str:
        """Giai đoạn đang mở; hết hạn theo đồng hồ thì tự đóng (giáo viên -> Duyệt, học sinh -> Nhập điểm)."""
        gd = self._dk_cai_dat(cur, "giai_doan", "chuan_bi")
        r = cur.execute("SELECT han_chot FROM dk_giai_doan WHERE ten = ?", (gd,)).fetchone()
        if r and r[0] and gd in ("gv_dang_ky", "hs_dang_ky") and r[0] <= self._dk_bay_gio().isoformat(timespec="seconds"):
            gd = "duyet" if gd == "gv_dang_ky" else "nhap_diem"
            self._dk_dat(cur, "giai_doan", gd)
            self._dk_ghi_nk(cur, "he_thong", "tu_dong_dong", gd)
        return gd

    def _dk_xet(self, cur, token, vai):
        """Phiên hợp lệ của `vai` (hoặc ném `_Loi`); làm mới giờ nghỉ. Trả dict phiên."""
        p = self._dk_phien_dict().get(token) if isinstance(token, str) else None
        if p is None:
            raise _Loi("dk_can_dang_nhap")
        gioi_han = GIAY_NGHI_QUAN_TRI if p["vai"] == QUAN_TRI else GIAY_NGHI_KHAC * 5
        if self._dk_dong_ho() - p["luc"] > gioi_han:
            self._dk_phien_dict().pop(token, None)
            raise _Loi("dk_het_phien_nghi")
        if p["vai"] not in vai:
            raise _Loi("dk_khong_du_quyen")
        p["luc"] = self._dk_dong_ho()
        return p

    def _dk_chay(self, ham, *vai_cho_phep, ghi=True, token=None, **kw):
        """Khung chung: kết nối, kiểm phiên, bắt `_Loi`. `ham(cur, phien)` trả dữ liệu."""
        try:
            with (self._ket_noi_ghi() if ghi else self._ket_noi_doc()) as cur:
                phien = self._dk_xet(cur, token, vai_cho_phep) if vai_cho_phep else None
                self._dk_gd = self._dk_giai_doan_hien_tai(cur) if ghi else self._dk_cai_dat(cur, "giai_doan", "chuan_bi")
                return _ok(ham(cur, phien))
        except _Loi as e:
            return _fail(e.loi)
        except Exception:
            _log.exception("dk_chay: loi khong du kien (chi tiet chi ghi nhat ky, khong gui len giao dien)")
            return _fail(err("dk_loi_chung"))

    # ------------------------------------------------------ khởi tạo, đăng nhập
    def dk_khoi_tao(self, mat_khau, ma_truong, buoi=None, khoi=None):
        """Lần đầu: đặt mật khẩu quản trị (≥ 4 ký tự), mã trường (giáo viên tự đăng ký), danh sách buổi, dải khối."""
        def lam(cur, _):
            if self._dk_cai_dat(cur, "mk_bam") is not None:
                raise _Loi("dk_da_khoi_tao")
            if not isinstance(mat_khau, str) or len(mat_khau) < 4:
                raise _Loi("dk_mat_khau_ngan")
            ma = str(ma_truong or "").strip()
            if len(ma) < 4:                               # VG2-L2: cùng luật với dk_cai_dat_doi
                raise _Loi("dk_ma_truong_sai")
            ds = [str(b).strip() for b in (buoi or BUOI_MAC_DINH) if str(b).strip()]
            k = [_so_nguyen(x) for x in (khoi or KHOI_MAC_DINH)]
            if not ds or len(set(ds)) != len(ds) or len(k) != 2 or None in k or not 1 <= k[0] <= k[1] <= 12:
                raise _Loi("dk_khoi_sai")
            b, m = _bam(mat_khau)
            self._dk_dat(cur, "mk_bam", b.hex())
            self._dk_dat(cur, "mk_muoi", m.hex())
            self._dk_dat(cur, "ma_truong", ma)
            self._dk_dat(cur, "buoi", json.dumps(ds, ensure_ascii=False))
            self._dk_dat(cur, "khoi", json.dumps(k))
            self._dk_dat(cur, "giai_doan", "chuan_bi")
            for g in CAC_GIAI_DOAN:
                cur.execute("INSERT OR IGNORE INTO dk_giai_doan (ten) VALUES (?)", (g,))
            self._dk_ghi_nk(cur, QUAN_TRI, "khoi_tao")
            return {"giai_doan": "chuan_bi"}
        return self._dk_chay(lam)

    @staticmethod
    def _dk_khoa_dn(vai, ten):
        return "dn_sai:%s:%s" % (vai, _chuan_khong_dau(ten)[:64])   # VG2-L1: không né khoá bằng cách đổi dấu / font

    def _dk_con_khoa(self, cur, khoa):
        """Số phút còn bị khoá (làm tròn lên) hoặc 0. Giá trị lưu: `số_lần_sai|hạn_khoá_ISO` (hạn rỗng = chưa khoá)."""
        v = self._dk_cai_dat(cur, khoa)
        han = v.split("|", 1)[1] if v and "|" in v else ""
        if not han:
            return 0
        con = (datetime.datetime.fromisoformat(han) - self._dk_bay_gio()).total_seconds()
        return int(-(-con // 60)) if con > 0 else 0

    def dk_dang_nhap(self, vai, ten, ma):
        """`vai` = quan_tri (ten bỏ qua, ma = mật khẩu) | giao_vien (ten, ma = PIN) | hoc_sinh (ten = mã học sinh, ma = PIN).
        Trả `{token, vai, ten, ...}`. Sai thì cùng MỘT lỗi cho mọi trường hợp (không lộ tên nào có thật).
        Sai `SO_LAN_SAI_TOI_DA` lần liên tiếp cho cùng một mã (kể cả mã không có thật) -> khoá `PHUT_KHOA` phút; trong
        thời gian khoá, nhập đúng cũng bị từ chối. Quản trị mở khoá bằng `dk_mo_khoa`. Bộ đếm lưu trong `dk_cai_dat`
        (không đổi lược đồ) nên mở lại phần mềm không xoá khoá."""
        khoa = self._dk_khoa_dn(vai, ten)
        ma = str(ma or "")
        if vai != QUAN_TRI:
            ma = _chuan_pin(ma)                      # VG1-L1 (D1) + VG2-L1: thừa dấu cách, số toàn khổ vẫn đúng
            if not re.fullmatch(r"[0-9]{4}", ma):       # sai dạng: chặn bằng mã riêng, KHÔNG tính một lần sai (chống khoá hộ)
                return _fail(err("dk_pin_sai_dang"))

        def lam(cur, _):
            phut = self._dk_con_khoa(cur, khoa)
            if phut:
                return {"_khoa": phut}
            kq = xac_thuc(cur)
            if kq is not None:
                cur.execute("DELETE FROM dk_cai_dat WHERE khoa = ?", (khoa,))
                if vai == QUAN_TRI:
                    cur.execute("DELETE FROM dk_cai_dat WHERE khoa = 'dn_bac:quan_tri'")      # VG2-L1 (D1): đăng nhập đúng xoá bậc khoá
                ds = self._dk_phien_dict()                                                  # VG2-L1: dọn token hết hạn (không tăng mãi)
                for t in [t for t, v in list(ds.items()) if t != "_db" and isinstance(v, dict) and      # list(): luồng đọc có thể pop cùng lúc
                          self._dk_dong_ho() - v.get("luc", 0) > (GIAY_NGHI_QUAN_TRI if v.get("vai") == QUAN_TRI else GIAY_NGHI_KHAC * 5)]:
                    ds.pop(t, None)
                return kq
            v = self._dk_cai_dat(cur, khoa)
            n = (int(v.split("|", 1)[0]) if v else 0) + 1
            han = ""
            if n >= SO_LAN_SAI_TOI_DA:
                phut = PHUT_KHOA
                if vai == QUAN_TRI:                       # VG2-L1 (D1): quản trị khoá 1 → 2 → 4 → 5 phút (người lạ khó khoá lâu)
                    bac = int(self._dk_cai_dat(cur, "dn_bac:quan_tri") or 0)
                    phut = min(PHUT_KHOA, 2 ** bac)
                    self._dk_dat(cur, "dn_bac:quan_tri", str(bac + 1))
                han = (self._dk_bay_gio() + datetime.timedelta(minutes=phut)).isoformat(timespec="seconds")
                self._dk_ghi_nk(cur, "he_thong", "khoa_dang_nhap", "%s %s" % (vai, str(ten or "")[:64]))
                n = 0
            self._dk_dat(cur, khoa, "%d|%s" % (n, han))
            return {"_sai": True}

        def xac_thuc(cur):
            if self._dk_cai_dat(cur, "mk_bam") is None:
                raise _Loi("dk_chua_khoi_tao")
            ma_s = str(ma or "")
            if vai == QUAN_TRI:
                ok = _dung(ma_s, bytes.fromhex(self._dk_cai_dat(cur, "mk_bam")), bytes.fromhex(self._dk_cai_dat(cur, "mk_muoi")))
                thong = {"ten": "Quản trị"}
            elif vai == GIAO_VIEN:
                uv = _ung_vien(cur.execute("SELECT gv_id, ten, pin_bam, pin_muoi FROM dk_giao_vien").fetchall(), lambda x: x[1], ten)
                hop = [x for x in uv if _dung(ma_s, x[2], x[3])]   # trùng tên không dấu: PIN quyết định; hai người cùng PIN -> từ chối
                r = hop[0] if len(hop) == 1 else None
                ok = r is not None
                thong = {"ten": r[1], "id": r[0]} if r else {}
            elif vai == HOC_SINH:
                uv = _ung_vien(cur.execute("SELECT student_id, ho_ten, lop, khoi, pin_bam, pin_muoi FROM dk_hoc_sinh").fetchall(),
                               lambda x: x[0], ten)
                hop = [x for x in uv if _dung(ma_s, x[4], x[5])]
                r = hop[0] if len(hop) == 1 else None
                ok = r is not None
                thong = {"ten": r[1], "id": r[0], "lop": r[2], "khoi": r[3]} if r else {}
            else:
                ok, thong = False, {}
            if not ok:
                _dung(ma_s, b"x", b"y")        # thời gian phản hồi như nhau
                return None
            token = secrets.token_urlsafe(24)
            self._dk_phien_dict()[token] = {"vai": vai, "luc": self._dk_dong_ho(), **thong}
            return {"token": token, "vai": vai, **thong}
            return None

        r = self._dk_chay(lam, ghi=True)
        if r["ok"] and r["data"].get("_khoa"):
            return _fail(err("dk_tam_khoa", phut=r["data"]["_khoa"]))
        if r["ok"] and r["data"].get("_sai"):
            return _fail(err("dk_sai_dang_nhap"))
        return r

    def dk_mo_khoa(self, token, vai, ten):
        """Quản trị: mở khoá đăng nhập của một giáo viên / học sinh (xoá bộ đếm sai)."""
        def lam(cur, p):
            if vai not in (QUAN_TRI, GIAO_VIEN, HOC_SINH):
                raise _Loi("dk_khong_thay")
            cur.execute("DELETE FROM dk_cai_dat WHERE khoa = ?", (self._dk_khoa_dn(vai, ten),))
            self._dk_ghi_nk(cur, QUAN_TRI, "mo_khoa", "%s %s" % (vai, str(ten)[:64]))
            return {}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_doi_mat_khau(self, token, mat_khau_cu, mat_khau_moi):
        """DK6-L2. Quản trị đổi mật khẩu: mật khẩu cũ phải đúng, mới ≥ 4 ký tự, băm lại với muối mới. Các phiên quản trị KHÁC bị
        huỷ (phiên của người gọi giữ lại). Nhật ký chỉ ghi «doi_mat_khau», không ghi mật khẩu. Không đếm số lần sai: phải đang
        đăng nhập quản trị mới gọi được (phiên tự khoá sau 2 phút)."""
        def lam(cur, p):
            if not _dung(str(mat_khau_cu or ""), bytes.fromhex(self._dk_cai_dat(cur, "mk_bam")), bytes.fromhex(self._dk_cai_dat(cur, "mk_muoi"))):
                raise _Loi("dk_mat_khau_cu_sai")
            if not isinstance(mat_khau_moi, str) or len(mat_khau_moi) < 4:
                raise _Loi("dk_mat_khau_ngan")
            b, m = _bam(mat_khau_moi)
            self._dk_dat(cur, "mk_bam", b.hex())
            self._dk_dat(cur, "mk_muoi", m.hex())
            self._dk_ghi_nk(cur, QUAN_TRI, "doi_mat_khau")
            return {}
        r = self._dk_chay(lam, QUAN_TRI, token=token)
        if r["ok"]:                                                  # chỉ huỷ phiên khác SAU khi đã ghi xong
            ds = self._dk_phien_dict()
            for t in [t for t, v in ds.items() if t != "_db" and t != token and isinstance(v, dict) and v.get("vai") == QUAN_TRI]:
                ds.pop(t, None)
        return r

    def dk_dang_xuat(self, token):
        self._dk_phien_dict().pop(token, None)
        return _ok({})

    def dk_trang_thai(self):
        """Công khai: giai đoạn hiện tại, hạn chót, buổi, khối, hai số đếm (so_gv, so_da_gui). Không có dữ liệu cá nhân."""
        def lam(cur, _):
            if self._dk_cai_dat(cur, "mk_bam") is None:
                return {"khoi_tao": False}
            buoi, khoi = self._dk_buoi_khoi(cur)
            gd = self._dk_giai_doan_hien_tai(cur)
            han = cur.execute("SELECT han_chot FROM dk_giai_doan WHERE ten = ?", (gd,)).fetchone()
            # DK8-L1: hai SỐ ĐẾM (không tên, không mã) cho thẻ vai trò ở trang đầu (v8: «N giáo viên đã đăng ký», «N em đã gửi»).
            # VG1-L2 (D6, mặc định an toàn): «đã đăng ký» = tự đăng ký, hoặc đã gửi ít nhất một CLB (tài khoản do quản trị tạo hộ
            # mà chưa ai dùng thì chưa tính). Đối xứng với số học sinh «đã gửi».
            so_gv = cur.execute("SELECT COUNT(*) FROM dk_giao_vien WHERE cach_tao = 'tu_dang_ky' "
                                "OR gv_id IN (SELECT gv_id FROM dk_clb)").fetchone()[0]
            so_da_gui = cur.execute("SELECT COUNT(*) FROM dk_hoc_sinh WHERE nop_luc IS NOT NULL").fetchone()[0]
            return {"khoi_tao": True, "giai_doan": gd, "han_chot": han[0] if han else None, "buoi": buoi, "khoi": khoi,
                    **dict(zip(("toi_da_nv", "toi_da_thi"), self._dk_gioi_han(cur))), "so_gv": so_gv, "so_da_gui": so_da_gui}
        return self._dk_chay(lam)

    def dk_dau_van_tay(self):
        """DKL-M. Công khai (như `dk_trang_thai`): dấu vân tay RẺ của dữ liệu — thời điểm sửa và kích thước của tệp CSDL và tệp WAL.
        Mọi thay đổi (kể cả học sinh gửi nguyện vọng, không ghi nhật ký) làm dấu đổi; đọc thì không. Màn quản trị hỏi mỗi 5 giây và chỉ
        vẽ lại khi dấu đổi. Không mở CSDL, không cần phiên và KHÔNG làm mới giờ nghỉ của phiên quản trị. Không lộ dữ liệu cá nhân."""
        try:
            phan = []
            for duong in (self.db_path, self.db_path + "-wal"):
                try:
                    s = os.stat(duong)
                    phan.append("%d:%d" % (s.st_mtime_ns, s.st_size))
                except OSError:
                    phan.append("-")
            return _ok({"dau": "|".join(phan)})
        except Exception:
            _log.exception("dk_dau_van_tay: loi khong du kien")
            return _fail(err("dk_loi_chung"))

    # ----------------------------------------------------- giai đoạn (quản trị)
    def dk_dat_han(self, token, giai_doan, han_chot):
        """Đặt hạn chót (ISO `YYYY-MM-DDTHH:MM`) cho giai đoạn giáo viên / học sinh; None = bỏ hạn."""
        def lam(cur, p):
            if giai_doan not in ("gv_dang_ky", "hs_dang_ky"):
                raise _Loi("dk_giai_doan_la")
            if han_chot:
                try:
                    datetime.datetime.fromisoformat(str(han_chot))
                except ValueError:
                    raise _Loi("dk_han_sai") from None
            cur.execute("UPDATE dk_giai_doan SET han_chot = ? WHERE ten = ?", (han_chot or None, giai_doan))
            self._dk_ghi_nk(cur, QUAN_TRI, "dat_han", "%s %s" % (giai_doan, han_chot))
            return {}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def _dk_kiem_dieu_kien_mo_hs(self, cur):
        """D2: không còn CLB chờ duyệt, ≥ 1 CLB được duyệt, và mọi buổi có CLB được duyệt đều có ≥ 1 CLB Tự do."""
        cho = cur.execute("SELECT COUNT(*) FROM dk_clb WHERE trang_thai = 'cho_duyet'").fetchone()[0]
        duyet = cur.execute("SELECT buoi, SUM(loai = 'Tự do') FROM dk_clb WHERE trang_thai = 'duyet' GROUP BY buoi").fetchall()
        if cho:
            return err("dk_con_clb_cho_duyet", n=cho)
        if not duyet:
            return err("dk_chua_co_clb_duyet")
        thieu = [b for b, td in duyet if not td]
        if thieu and self._dk_bat_buoc_tu_do(cur):
            return err("dk_thieu_clb_tu_do", buoi=", ".join(thieu))
        return None

    def dk_chuyen_giai_doan(self, token, giai_doan, xac_nhan=False):
        """Sang giai đoạn kế, nhảy tới, hoặc LÙI bất kỳ số bước (VG1-L3, D3; có ghi nhật ký, không xoá dữ liệu). Nhảy tới phải qua
        cổng của MỌI ranh giới đi ngang (mở cho học sinh: `_dk_kiem_dieu_kien_mo_hs`; xuất: đủ điểm). Lùi khỏi giai đoạn học sinh về
        trước nó mà đã có nguyện vọng đã gửi thì cần `xac_nhan=True` (không thì `dk_lui_co_nguyen_vong`, n). Lùi xoá hạn chót của giai
        đoạn đích VÀ các giai đoạn sau (hạn đã qua sẽ tự đóng giai đoạn ngay lần gọi kế tiếp)."""
        def lam(cur, p):
            if giai_doan not in CAC_GIAI_DOAN:
                raise _Loi("dk_giai_doan_la")
            hien = self._dk_gd
            i_hien, i_dich = CAC_GIAI_DOAN.index(hien), CAC_GIAI_DOAN.index(giai_doan)
            i_hs = CAC_GIAI_DOAN.index("hs_dang_ky")
            for g in CAC_GIAI_DOAN[i_hien + 1:i_dich + 1]:                  # cổng của từng ranh giới đi ngang khi tiến
                if g == "duyet" and self._dk_bat_buoc_tu_do(cur):           # VG1-L4 (a): chặn SỚM, không đợi tới lúc mở cho học sinh
                    thieu = self._dk_buoi_thieu_tu_do(cur)
                    if thieu:
                        raise _Loi("dk_thieu_clb_tu_do", buoi=", ".join(thieu))
                if g == "hs_dang_ky":
                    loi = self._dk_kiem_dieu_kien_mo_hs(cur)
                    if loi:
                        raise _Loi(loi["code"], **loi["params"])
                if g == "xuat":
                    thieu = cur.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE thi = 1 AND diem IS NULL").fetchone()[0]
                    if thieu:
                        raise _Loi("dk_thieu_diem", n=thieu)
            if i_dich < i_hien:
                if i_hien >= i_hs > i_dich:
                    n = cur.execute("SELECT COUNT(DISTINCT student_id) FROM dk_nguyen_vong").fetchone()[0]
                    if n and xac_nhan is not True:
                        raise _Loi("dk_lui_co_nguyen_vong", n=n)
                cur.execute("UPDATE dk_giai_doan SET han_chot = NULL WHERE ten IN (%s)" % ",".join("?" * len(CAC_GIAI_DOAN[i_dich:])),
                            CAC_GIAI_DOAN[i_dich:])
            self._dk_dat(cur, "giai_doan", giai_doan)
            self._dk_ghi_nk(cur, QUAN_TRI, "chuyen_giai_doan", "%s -> %s" % (hien, giai_doan))
            return {"giai_doan": giai_doan}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    # ------------------------------------------------------------ phòng
    def dk_phong_luu(self, token, ten, suc_chua):
        def lam(cur, p):
            t = str(ten or "").strip()
            sc = _so_nguyen(suc_chua)
            if not t:
                raise _Loi("dk_ten_trong")
            if sc is None or sc <= 0:
                raise _Loi("dk_phong_suc_chua")
            if any(_chuan_ten(r[0]) == _chuan_ten(t) for r in cur.execute("SELECT ten FROM dk_phong")):      # VG2-L2: p1 = P1
                raise _Loi("dk_phong_trung")
            cur.execute("INSERT INTO dk_phong (ten, suc_chua) VALUES (?, ?)", (t, sc))
            phong_id = cur.lastrowid                     # DKL-K: lấy TRƯỚC khi ghi nhật ký (nhật ký cũng là một INSERT)
            self._dk_ghi_nk(cur, QUAN_TRI, "them_phong", t)
            return {"phong_id": phong_id}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_phong_xoa(self, token, phong_id):
        def lam(cur, p):
            if cur.execute("SELECT 1 FROM dk_clb WHERE phong_id = ?", (phong_id,)).fetchone():   # VG2-L2: cả CLB đã bị từ chối (tránh phong_id lơ lửng)
                raise _Loi("dk_phong_dang_dung")
            cur.execute("DELETE FROM dk_phong WHERE phong_id = ?", (phong_id,))
            self._dk_ghi_nk(cur, QUAN_TRI, "xoa_phong", phong_id)
            return {}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_phong_danh_sach(self, token, buoi=None, bo_qua_clb=None):
        """Danh sách phòng. Có `buoi`: mỗi phòng thêm `ban` = đã có CLB khác (chưa bị từ chối) ở buổi đó (v8: chỉ hiện phòng trống)."""
        def lam(cur, p):
            ra = []
            for r in cur.execute("SELECT p.phong_id, p.ten, p.suc_chua, (SELECT COUNT(*) FROM dk_clb c WHERE c.phong_id = p.phong_id AND "
                                 "c.trang_thai != 'tu_choi') FROM dk_phong p ORDER BY p.ten").fetchall():
                d = dict(phong_id=r[0], ten=r[1], suc_chua=r[2], dang_dung=r[3])
                if buoi is not None:
                    d["ban"] = bool(cur.execute("SELECT 1 FROM dk_clb WHERE phong_id = ? AND buoi = ? AND trang_thai != 'tu_choi' "
                                                "AND clb_id IS NOT ?", (r[0], buoi, bo_qua_clb)).fetchone())
                ra.append(d)
            return ra
        return self._dk_chay(lam, QUAN_TRI, GIAO_VIEN, ghi=False, token=token)

    # ------------------------------------------------------------ giáo viên
    def _dk_bat_buoc_tu_do(self, cur) -> bool:
        """VG1-L4 (D4): ràng buộc «mỗi buổi phải có CLB Tự do» (mặc định BẬT = hành vi cũ)."""
        return self._dk_cai_dat(cur, "bat_buoc_tu_do", "1") != "0"

    @staticmethod
    def _dk_buoi_thieu_tu_do(cur, bo_qua_clb=None):
        """Các buổi đang có CLB «sống» (chờ duyệt / đã duyệt) mà không có CLB Tự do sống nào (bỏ `bo_qua_clb` ra khỏi phép đếm)."""
        co, tu_do = set(), set()
        for cid, b, loai in cur.execute("SELECT clb_id, buoi, loai FROM dk_clb WHERE trang_thai IN ('cho_duyet', 'duyet')"):
            if cid == bo_qua_clb:
                continue
            co.add(b)
            if loai == TU_DO:
                tu_do.add(b)
        return sorted(co - tu_do)

    def _dk_chan_bo_clb_tu_do_cuoi(self, cur, clb_id):
        """VG1-L4 (b): không cho gỡ (từ chối / xoá / đổi buổi) CLB Tự do CUỐI CÙNG của một buổi còn CLB sống khác."""
        r = cur.execute("SELECT buoi, loai, trang_thai FROM dk_clb WHERE clb_id = ?", (clb_id,)).fetchone()
        if r and r[1] == TU_DO and r[2] in ("cho_duyet", "duyet") and self._dk_bat_buoc_tu_do(cur) and r[0] in self._dk_buoi_thieu_tu_do(cur, clb_id):
            raise _Loi("dk_thieu_clb_tu_do", buoi=r[0])

    def _dk_huy_phien(self, vai, ids):
        """VG1-L2 (kiểm tra toàn diện #2): đặt lại PIN thì phiên đang mở của người đó chết (PIN lộ / dùng chung không còn hiệu lực)."""
        ids = set(ids)
        ds = self._dk_phien_dict()
        for t in [t for t, v in list(ds.items()) if t != "_db" and isinstance(v, dict) and v.get("vai") == vai and v.get("id") in ids]:
            ds.pop(t, None)

    @staticmethod
    def _dk_gv_trung(cur, ten) -> bool:
        """VG1-L1: trùng tên sau chuẩn hoá (NFC, khoảng trắng, hoa/thường) = trùng."""
        k = _chuan_ten(ten)
        return any(_chuan_ten(r[0]) == k for r in cur.execute("SELECT ten FROM dk_giao_vien"))

    def dk_gv_tu_dang_ky(self, ma_truong, ten, pin):
        """Giáo viên tự đăng ký (mã trường + tên + PIN riêng 4 chữ số) khi giai đoạn GV đang mở."""
        def lam(cur, _):
            if self._dk_cai_dat(cur, "mk_bam") is None:
                raise _Loi("dk_chua_khoi_tao")
            if str(ma_truong or "").strip() != self._dk_cai_dat(cur, "ma_truong"):
                raise _Loi("dk_ma_truong_sai")
            if self._dk_gd != "gv_dang_ky":
                raise _Loi("dk_sai_giai_doan", phan="gv_dang_ky")
            t = unicodedata.normalize("NFC", str(ten or "")).strip()
            if not t or len(t) > 60:
                raise _Loi("dk_ten_trong")
            if not re.fullmatch(r"\d{4}", str(pin or "")):
                raise _Loi("dk_pin_sai_dang")
            if _pin_de_doan(pin):
                raise _Loi("dk_pin_de_doan")
            if cur.execute("SELECT COUNT(*) FROM dk_giao_vien").fetchone()[0] >= TOI_DA_GV:
                raise _Loi("dk_gv_qua_nhieu", toi_da=TOI_DA_GV)
            if self._dk_gv_trung(cur, t):
                raise _Loi("dk_gv_trung")
            b, m = _bam(pin)
            cur.execute("INSERT INTO dk_giao_vien (ten, pin_bam, pin_muoi, cach_tao) VALUES (?, ?, ?, 'tu_dang_ky')", (t, b, m))
            gv_id = cur.lastrowid                        # DKL-K: lấy TRƯỚC khi ghi nhật ký
            self._dk_ghi_nk(cur, GIAO_VIEN, "tu_dang_ky", t)
            return {"gv_id": gv_id}
        return self._dk_chay(lam)

    def dk_gv_tao_hang_loat(self, token, van_ban):
        """Quản trị dán tên (mỗi dòng một giáo viên), PIN tự sinh. Trả danh sách `{ten, pin}` (PIN chỉ hiện lần này)."""
        def lam(cur, p):
            ra, bo_qua = [], []
            for dong in str(van_ban or "").splitlines():
                t = unicodedata.normalize("NFC", dong).strip()
                if not t:
                    continue
                if len(t) > 60 or self._dk_gv_trung(cur, t):
                    bo_qua.append(t)
                    continue
                pin = _pin_moi()
                b, m = _bam(pin)
                cur.execute("INSERT INTO dk_giao_vien (ten, pin_bam, pin_muoi, cach_tao) VALUES (?, ?, ?, 'quan_tri')", (t, b, m))
                ra.append({"ten": t, "pin": pin})
            if not ra and not bo_qua:
                raise _Loi("dk_danh_sach_trong")
            self._dk_ghi_nk(cur, QUAN_TRI, "tao_gv", len(ra))
            return {"da_tao": ra, "bo_qua": bo_qua}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_gv_xoa(self, token, gv_id):
        """VG2-L1 (D3): quản trị xoá một giáo viên (dọn tài khoản rác). Còn CLB chưa bị từ chối thì chặn; CLB đã bị từ chối đi theo."""
        def lam(cur, p):
            if not cur.execute("SELECT 1 FROM dk_giao_vien WHERE gv_id = ?", (gv_id,)).fetchone():
                raise _Loi("dk_khong_thay")
            if cur.execute("SELECT 1 FROM dk_clb WHERE gv_id = ? AND trang_thai != 'tu_choi'", (gv_id,)).fetchone():
                raise _Loi("dk_gv_con_clb")
            cur.execute("DELETE FROM dk_clb WHERE gv_id = ?", (gv_id,))
            cur.execute("DELETE FROM dk_giao_vien WHERE gv_id = ?", (gv_id,))
            self._dk_ghi_nk(cur, QUAN_TRI, "xoa_gv", gv_id)
            return {}
        r = self._dk_chay(lam, QUAN_TRI, token=token)
        if r["ok"]:
            self._dk_huy_phien(GIAO_VIEN, [gv_id])
        return r

    def dk_gv_dat_lai_pin(self, token, gv_id):
        def lam(cur, p):
            if not cur.execute("SELECT 1 FROM dk_giao_vien WHERE gv_id = ?", (gv_id,)).fetchone():
                raise _Loi("dk_khong_thay")
            pin = _pin_moi()
            b, m = _bam(pin)
            cur.execute("UPDATE dk_giao_vien SET pin_bam = ?, pin_muoi = ? WHERE gv_id = ?", (b, m, gv_id))
            self._dk_ghi_nk(cur, QUAN_TRI, "dat_lai_pin_gv", gv_id)
            return {"pin": pin}
        r = self._dk_chay(lam, QUAN_TRI, token=token)
        if r["ok"]:
            self._dk_huy_phien(GIAO_VIEN, [gv_id])
        return r

    def dk_gv_danh_sach(self, token):
        def lam(cur, p):
            return [dict(gv_id=r[0], ten=r[1], cach_tao=r[2], bi_khoa=bool(self._dk_con_khoa(cur, self._dk_khoa_dn(GIAO_VIEN, r[1]))))
                    for r in cur.execute(
                "SELECT gv_id, ten, cach_tao FROM dk_giao_vien ORDER BY ten").fetchall()]
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    # ------------------------------------------------------------ học sinh (danh sách)
    @staticmethod
    def _dk_tach_dong(dong):
        if "\t" in dong:
            ph = [x.strip() for x in dong.split("\t")]
        elif ";" in dong or "," in dong:
            ph = [x.strip() for x in re.split(r"[;,]", dong)]
        else:
            tk = dong.split()
            ph = [tk[0], " ".join(tk[1:-1]), tk[-1]] if len(tk) >= 3 else tk
        return [x for x in ph if x != ""] if len(ph) > 3 else ph

    def dk_hs_nap_danh_sach(self, token, van_ban, che_do="them"):
        """D6. `che_do` = "them" (mặc định: thêm / cập nhật, giữ PIN em đã có, bỏ dòng lỗi) | "thay" (thay cả danh sách).
        Trả `{moi, da_co, loi: [{dong, ly_do}], pin: [{ma, pin}]}`."""
        def lam(cur, p):
            buoi, (k_tu, k_den) = self._dk_buoi_khoi(cur)
            moi, da_co, loi, pins, hop_le = 0, 0, [], [], []
            thay = che_do == "thay"
            for i, dong in enumerate(str(van_ban or "").splitlines(), start=1):
                if not dong.strip():
                    continue
                ph = self._dk_tach_dong(unicodedata.normalize("NFC", dong).strip())
                if len(ph) < 3:
                    loi.append({"dong": i, "ly_do": "thieu_cot"})
                    continue
                ma, ten, lop = ph[0], ph[1], ph[2]
                khoi = _khoi_cua_lop(lop) or (_so_nguyen(ph[3]) if len(ph) > 3 else None)
                if not khoi or not k_tu <= khoi <= k_den:
                    loi.append({"dong": i, "ly_do": "khoi_ngoai_dai"})
                    continue
                if any(_chuan_ten(h[0]) == _chuan_ten(ma) for h in hop_le):   # VG1-L1: «H9» và «h9» là cùng một mã
                    loi.append({"dong": i, "ly_do": "trung_ma"})
                    continue
                hop_le.append((ma, ten, lop, khoi))
            if thay and loi:
                raise _Loi("dk_danh_sach_co_loi", n=len(loi))
            if not hop_le and not loi:
                raise _Loi("dk_danh_sach_trong")
            if thay:
                gd = self._dk_gd
                if CAC_GIAI_DOAN.index(gd) >= CAC_GIAI_DOAN.index("hs_dang_ky"):
                    raise _Loi("dk_sai_giai_doan", phan="chuan_bi")
                cur.execute("DELETE FROM dk_nguyen_vong")
                cur.execute("DELETE FROM dk_hoc_sinh")
            co_san = {_chuan_ten(r[0]): r[0] for r in cur.execute("SELECT student_id FROM dk_hoc_sinh")}
            for ma, ten, lop, khoi in hop_le:
                if _chuan_ten(ma) in co_san:                 # giữ nguyên cách viết mã đã lưu (hợp đồng CSV)
                    cur.execute("UPDATE dk_hoc_sinh SET ho_ten = ?, lop = ?, khoi = ? WHERE student_id = ?",
                                (ten, lop, khoi, co_san[_chuan_ten(ma)]))
                    da_co += 1
                else:
                    pin = _pin_moi()
                    b, m = _bam(pin)
                    cur.execute("INSERT INTO dk_hoc_sinh (student_id, ho_ten, lop, khoi, pin_bam, pin_muoi) VALUES (?,?,?,?,?,?)",
                                (ma, ten, lop, khoi, b, m))
                    pins.append({"ma": ma, "pin": pin})
                    moi += 1
            self._dk_ghi_nk(cur, QUAN_TRI, "nap_hs", "%s moi=%d" % (che_do, moi))
            return {"moi": moi, "da_co": da_co, "loi": loi, "pin": pins}
        r = self._dk_chay(lam, QUAN_TRI, token=token)
        if r["ok"] and che_do == "thay":                              # thay cả danh sách: mọi em được tạo lại (PIN mới) nên phiên cũ chết
            self._dk_huy_phien(HOC_SINH, [v["id"] for v in self._dk_phien_dict().values() if isinstance(v, dict) and v.get("vai") == HOC_SINH])
        return r

    def dk_hs_dat_lai_pin(self, token, student_id):
        def lam(cur, p):
            if not cur.execute("SELECT 1 FROM dk_hoc_sinh WHERE student_id = ?", (student_id,)).fetchone():
                raise _Loi("dk_khong_thay")
            pin = _pin_moi()
            b, m = _bam(pin)
            cur.execute("UPDATE dk_hoc_sinh SET pin_bam = ?, pin_muoi = ? WHERE student_id = ?", (b, m, student_id))
            self._dk_ghi_nk(cur, QUAN_TRI, "dat_lai_pin_hs", student_id)
            return {"pin": pin}
        r = self._dk_chay(lam, QUAN_TRI, token=token)
        if r["ok"]:
            self._dk_huy_phien(HOC_SINH, [student_id])
        return r

    def dk_hs_danh_sach(self, token):
        def lam(cur, p):
            return [dict(ma=r[0], ho_ten=r[1], lop=r[2], khoi=r[3], da_nop=bool(r[4]),
                         bi_khoa=bool(self._dk_con_khoa(cur, self._dk_khoa_dn(HOC_SINH, r[0]))))
                    for r in cur.execute(
                "SELECT student_id, ho_ten, lop, khoi, nop_luc FROM dk_hoc_sinh ORDER BY lop, student_id").fetchall()]
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    # ------------------------------------------------------------ CLB
    def _dk_kiem_clb(self, cur, d, gv_id, clb_id):
        """Kiểm D14 / D15 và trả bản ghi sạch. `d` từ giao diện; ném `_Loi` ở lỗi đầu tiên."""
        buoi, (k_tu, k_den) = self._dk_buoi_khoi(cur)
        ten = unicodedata.normalize("NFC", str(d.get("ten") or "")).strip()
        if not ten or len(ten) > 80:
            raise _Loi("dk_ten_trong")
        if any(r[1] != clb_id and _chuan_ten(r[0]) == _chuan_ten(ten) for r in cur.execute("SELECT ten, clb_id FROM dk_clb")):   # VG2-L2
            raise _Loi("dk_clb_ten_trung")
        b = str(d.get("buoi") or "")
        if b not in buoi:
            raise _Loi("dk_clb_buoi_la")
        loai = d.get("loai")
        if loai not in LOAI_CLB:
            raise _Loi("dk_clb_loai_la")
        if gv_id is not None and cur.execute("SELECT 1 FROM dk_clb WHERE gv_id = ? AND buoi = ? AND trang_thai != 'tu_choi' "
                                             "AND clb_id IS NOT ?", (gv_id, b, clb_id)).fetchone():
            raise _Loi("dk_gv_hai_clb_mot_buoi")
        phong_id = _so_nguyen(d.get("phong_id"))
        ph = cur.execute("SELECT suc_chua FROM dk_phong WHERE phong_id = ?", (phong_id,)).fetchone()
        if ph is None:
            raise _Loi("dk_phong_la")
        if cur.execute("SELECT 1 FROM dk_clb WHERE phong_id = ? AND buoi = ? AND trang_thai != 'tu_choi' AND clb_id IS NOT ?",
                       (phong_id, b, clb_id)).fetchone():
            raise _Loi("dk_phong_ban")
        chi_tieu = None
        if loai != TU_DO:
            chi_tieu = _so_nguyen(d.get("chi_tieu"))
            if chi_tieu is None or chi_tieu <= 0:
                raise _Loi("dk_chi_tieu_sai")
            if chi_tieu > ph[0]:
                raise _Loi("dk_chi_tieu_qua_phong", suc_chua=ph[0])
        tu, den = _so_nguyen(d.get("khoi_tu")), _so_nguyen(d.get("khoi_den"))
        if tu is None or den is None or not k_tu <= tu <= den <= k_den:
            raise _Loi("dk_khoi_sai")
        diem_san = None
        if loai == TUYEN_CHON:
            diem_san = _so_nguyen(d.get("diem_san"))
            if diem_san is None or not 0 <= diem_san <= 10:
                raise _Loi("dk_diem_san_sai")
        return {"ten": ten, "buoi": b, "loai": loai, "phong_id": phong_id, "chi_tieu_gv": chi_tieu, "chi_tieu": chi_tieu,
                "khoi_tu": tu, "khoi_den": den, "diem_san": diem_san,
                "link_forms": str(d.get("link_forms") or "").strip()[:300] if loai == TUYEN_CHON else "",
                "mo_ta": str(d.get("mo_ta") or "").strip()[:600], "yeu_cau": str(d.get("yeu_cau") or "").strip()[:300]}

    def dk_clb_luu(self, token, du_lieu, clb_id=None):
        """Giáo viên: tạo / sửa CLB của MÌNH (GV mở, CLB còn "chờ duyệt"). Quản trị: tạo / sửa CLB của một giáo viên
        (`du_lieu["gv_id"]`) trước khi mở cho học sinh. Trả `{clb_id}`."""
        def lam(cur, p):
            d = du_lieu or {}
            gd = self._dk_gd
            if p["vai"] == GIAO_VIEN:
                if gd != "gv_dang_ky":
                    raise _Loi("dk_sai_giai_doan", phan="gv_dang_ky")
                gv = p["id"]
            else:
                if CAC_GIAI_DOAN.index(gd) >= CAC_GIAI_DOAN.index("hs_dang_ky"):
                    raise _Loi("dk_sai_giai_doan", phan="duyet")
                gv = _so_nguyen(d.get("gv_id"))
                if gv is not None and not cur.execute("SELECT 1 FROM dk_giao_vien WHERE gv_id = ?", (gv,)).fetchone():
                    raise _Loi("dk_khong_thay")
            cid = clb_id
            if cid is not None:
                r = cur.execute("SELECT gv_id, trang_thai FROM dk_clb WHERE clb_id = ?", (cid,)).fetchone()
                if r is None:
                    raise _Loi("dk_khong_thay")
                if p["vai"] == GIAO_VIEN and (r[0] != gv or r[1] != "cho_duyet"):
                    raise _Loi("dk_clb_khong_sua_duoc")
            v = self._dk_kiem_clb(cur, d, gv, cid)
            if cid is None:
                cur.execute("INSERT INTO dk_clb (ten, buoi, loai, phong_id, gv_id, chi_tieu_gv, chi_tieu, khoi_tu, khoi_den, diem_san,"
                            " link_forms, mo_ta, yeu_cau) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (v["ten"], v["buoi"], v["loai"], v["phong_id"], gv, v["chi_tieu_gv"], v["chi_tieu"], v["khoi_tu"],
                             v["khoi_den"], v["diem_san"], v["link_forms"], v["mo_ta"], v["yeu_cau"]))
                cid = cur.lastrowid
            else:
                cur.execute("UPDATE dk_clb SET ten=?, buoi=?, loai=?, phong_id=?, chi_tieu_gv=?, chi_tieu=?, khoi_tu=?, khoi_den=?,"
                            " diem_san=?, link_forms=?, mo_ta=?, yeu_cau=? WHERE clb_id=?",
                            (v["ten"], v["buoi"], v["loai"], v["phong_id"], v["chi_tieu_gv"], v["chi_tieu"], v["khoi_tu"],
                             v["khoi_den"], v["diem_san"], v["link_forms"], v["mo_ta"], v["yeu_cau"], cid))
            self._dk_ghi_nk(cur, p["vai"], "luu_clb", v["ten"])
            return {"clb_id": cid}
        return self._dk_chay(lam, GIAO_VIEN, QUAN_TRI, token=token)

    def dk_clb_xoa(self, token, clb_id):
        """DKL-S8 (D17): giáo viên xoá CLB của MÌNH khi GV còn mở và CLB chưa được duyệt; quản trị xoá CLB chưa duyệt trước khi
        mở cho học sinh. CLB đã duyệt thì không xoá ở đây (dùng `dk_clb_sua_sau_mo`)."""
        def lam(cur, p):
            gd = self._dk_gd
            r = cur.execute("SELECT gv_id, trang_thai FROM dk_clb WHERE clb_id = ?", (clb_id,)).fetchone()
            if r is None:
                raise _Loi("dk_khong_thay")
            if p["vai"] == GIAO_VIEN:
                if gd != "gv_dang_ky":
                    raise _Loi("dk_sai_giai_doan", phan="gv_dang_ky")
                if r[0] != p["id"]:
                    raise _Loi("dk_clb_khong_sua_duoc")
            elif CAC_GIAI_DOAN.index(gd) >= CAC_GIAI_DOAN.index("hs_dang_ky"):
                raise _Loi("dk_sai_giai_doan", phan="duyet")
            if r[1] == "duyet":
                raise _Loi("dk_clb_khong_sua_duoc")
            if p["vai"] == QUAN_TRI:
                self._dk_chan_bo_clb_tu_do_cuoi(cur, clb_id)
            cur.execute("DELETE FROM dk_clb WHERE clb_id = ?", (clb_id,))
            self._dk_ghi_nk(cur, p["vai"], "xoa_clb", clb_id)
            return {}
        return self._dk_chay(lam, GIAO_VIEN, QUAN_TRI, token=token)

    @staticmethod
    def _dk_go_nguyen_vong_clb(cur, clb_id):
        """Gỡ nguyện vọng trỏ `clb_id`, đánh lại `hang` 1..n theo (học sinh, buổi) giữ thứ tự; `nop_luc` giữ nguyên."""
        ai = cur.execute("SELECT DISTINCT student_id, buoi FROM dk_nguyen_vong WHERE clb_id = ?", (clb_id,)).fetchall()
        cur.execute("DELETE FROM dk_nguyen_vong WHERE clb_id = ?", (clb_id,))
        for sid, buoi in ai:
            cur.execute("UPDATE dk_nguyen_vong SET hang = hang + 100000 WHERE student_id = ? AND buoi = ?", (sid, buoi))
            for k, (cid,) in enumerate(cur.execute("SELECT clb_id FROM dk_nguyen_vong WHERE student_id = ? AND buoi = ? ORDER BY hang",
                                                   (sid, buoi)).fetchall(), start=1):
                cur.execute("UPDATE dk_nguyen_vong SET hang = ? WHERE student_id = ? AND clb_id = ?", (k, sid, cid))

    def dk_clb_duyet(self, token, clb_id, quyet_dinh, chi_tieu=None, phong_id=None, ly_do="", xac_nhan=False):
        """D18/D19: duyệt (có thể đổi chỉ tiêu của quản trị / phòng) hoặc từ chối. Chỉ trước khi mở cho học sinh."""
        def lam(cur, p):
            if quyet_dinh not in ("duyet", "tu_choi"):
                raise _Loi("dk_giai_doan_la")
            if CAC_GIAI_DOAN.index(self._dk_gd) >= CAC_GIAI_DOAN.index("hs_dang_ky"):
                raise _Loi("dk_sai_giai_doan", phan="duyet")
            r = cur.execute("SELECT clb_id, buoi, loai, phong_id, chi_tieu_gv FROM dk_clb WHERE clb_id = ?", (clb_id,)).fetchone()
            if r is None:
                raise _Loi("dk_khong_thay")
            if quyet_dinh == "tu_choi":
                self._dk_chan_bo_clb_tu_do_cuoi(cur, clb_id)
                n_nv = cur.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE clb_id = ?", (clb_id,)).fetchone()[0]
                if n_nv and xac_nhan is not True:                       # VG1-L3 (D3): không để nguyện vọng mồ côi trỏ CLB đã từ chối
                    raise _Loi("dk_clb_co_nguyen_vong", n=n_nv)
                if n_nv:
                    self._dk_go_nguyen_vong_clb(cur, clb_id)
                cur.execute("UPDATE dk_clb SET trang_thai = 'tu_choi', ly_do_tu_choi = ? WHERE clb_id = ?", (str(ly_do or "")[:300], clb_id))
                if n_nv:
                    self._dk_ghi_nk(cur, QUAN_TRI, "go_nguyen_vong_tu_choi", "%s n=%d" % (clb_id, n_nv))
            else:
                if r[2] != TU_DO and self._dk_bat_buoc_tu_do(cur) and r[1] in self._dk_buoi_thieu_tu_do(cur):
                    raise _Loi("dk_thieu_clb_tu_do", buoi=r[1])      # VG1-L4 (d): buổi chưa có CLB Tự do sống thì chưa duyệt CLB khác
                ph = _so_nguyen(phong_id) if phong_id is not None else r[3]
                sc = cur.execute("SELECT suc_chua FROM dk_phong WHERE phong_id = ?", (ph,)).fetchone()
                if sc is None:
                    raise _Loi("dk_phong_la")
                if cur.execute("SELECT 1 FROM dk_clb WHERE phong_id = ? AND buoi = ? AND trang_thai != 'tu_choi' AND clb_id != ?",
                               (ph, r[1], clb_id)).fetchone():
                    raise _Loi("dk_phong_ban")
                ct = None
                if r[2] != TU_DO:
                    ct = _so_nguyen(chi_tieu) if chi_tieu is not None else r[4]
                    if ct is None or ct <= 0:
                        raise _Loi("dk_chi_tieu_sai")
                    if ct > sc[0]:
                        raise _Loi("dk_chi_tieu_qua_phong", suc_chua=sc[0])
                cur.execute("UPDATE dk_clb SET trang_thai = 'duyet', chi_tieu = ?, phong_id = ?, ly_do_tu_choi = NULL WHERE clb_id = ?",
                            (ct, ph, clb_id))
            self._dk_ghi_nk(cur, QUAN_TRI, "duyet_clb", "%s %s" % (clb_id, quyet_dinh))
            return {}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_clb_sua_sau_mo(self, token, clb_id, chi_tieu=None, phong_id=None, buoi=None, xoa=False, xac_nhan=False):
        """Sau khi mở cho học sinh: chỉ TĂNG chỉ tiêu thì tự do; đổi phòng / buổi hoặc xoá phải `xac_nhan=True`, khi đó báo
        "N học sinh bị ảnh hưởng" (đã chọn CLB này) và ghi nhật ký. Chưa xác nhận thì chỉ trả số em bị ảnh hưởng."""
        def lam(cur, p):
            if CAC_GIAI_DOAN.index(self._dk_gd) < CAC_GIAI_DOAN.index("hs_dang_ky"):
                raise _Loi("dk_sai_giai_doan", phan="hs_dang_ky")
            r = cur.execute("SELECT clb_id, buoi, phong_id, chi_tieu, loai FROM dk_clb WHERE clb_id = ? AND trang_thai = 'duyet'",
                            (clb_id,)).fetchone()
            if r is None:
                raise _Loi("dk_khong_thay")
            n = cur.execute("SELECT COUNT(DISTINCT student_id) FROM dk_nguyen_vong WHERE clb_id = ?", (clb_id,)).fetchone()[0]
            nguy_hiem = xoa or (phong_id is not None and _so_nguyen(phong_id) != r[2]) or (buoi is not None and buoi != r[1])
            if xoa or (buoi is not None and buoi != r[1]):
                self._dk_chan_bo_clb_tu_do_cuoi(cur, clb_id)          # VG1-L4 (b)
            if buoi is not None and buoi != r[1] and r[4] != TU_DO and self._dk_bat_buoc_tu_do(cur) and not cur.execute(
                    "SELECT 1 FROM dk_clb WHERE buoi = ? AND loai = ? AND trang_thai IN ('cho_duyet', 'duyet')", (buoi, TU_DO)).fetchone():
                raise _Loi("dk_thieu_clb_tu_do", buoi=buoi)           # buổi đích chưa có CLB Tự do sống
            if nguy_hiem and not xac_nhan:
                return {"can_xac_nhan": True, "anh_huong": n}
            if xoa:
                cur.execute("DELETE FROM dk_nguyen_vong WHERE clb_id = ?", (clb_id,))
                cur.execute("DELETE FROM dk_clb WHERE clb_id = ?", (clb_id,))
                self._dk_ghi_nk(cur, QUAN_TRI, "xoa_clb_sau_mo", "%s anh_huong=%d" % (clb_id, n))
                return {"anh_huong": n}
            moi_buoi, moi_ph, moi_ct = (buoi or r[1]), (_so_nguyen(phong_id) if phong_id is not None else r[2]), r[3]
            if moi_buoi not in self._dk_buoi_khoi(cur)[0]:
                raise _Loi("dk_clb_buoi_la")
            sc = cur.execute("SELECT suc_chua FROM dk_phong WHERE phong_id = ?", (moi_ph,)).fetchone()
            if sc is None:
                raise _Loi("dk_phong_la")
            if cur.execute("SELECT 1 FROM dk_clb WHERE phong_id = ? AND buoi = ? AND trang_thai = 'duyet' AND clb_id != ?",
                           (moi_ph, moi_buoi, clb_id)).fetchone():
                raise _Loi("dk_phong_ban")
            if chi_tieu is not None and r[4] != TU_DO:
                ct = _so_nguyen(chi_tieu)
                if ct is None or ct < (r[3] or 0):
                    raise _Loi("dk_chi_tieu_sai")
                moi_ct = ct
            if moi_ct is not None and moi_ct > sc[0]:
                raise _Loi("dk_chi_tieu_qua_phong", suc_chua=sc[0])
            if moi_buoi != r[1]:
                cur.execute("DELETE FROM dk_nguyen_vong WHERE clb_id = ?", (clb_id,))
            cur.execute("UPDATE dk_clb SET buoi = ?, phong_id = ?, chi_tieu = ? WHERE clb_id = ?", (moi_buoi, moi_ph, moi_ct, clb_id))
            self._dk_ghi_nk(cur, QUAN_TRI, "sua_clb_sau_mo", "%s anh_huong=%d" % (clb_id, n if nguy_hiem else 0))
            return {"anh_huong": n if nguy_hiem else 0}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_clb_danh_sach(self, token):
        """Quản trị: mọi CLB. Giáo viên: CLB của mình."""
        def lam(cur, p):
            sql = ("SELECT c.clb_id, c.ten, c.buoi, c.loai, c.phong_id, ph.ten, c.gv_id, g.ten, c.chi_tieu_gv, c.chi_tieu, c.khoi_tu,"
                   " c.khoi_den, c.diem_san, c.link_forms, c.mo_ta, c.yeu_cau, c.trang_thai, c.ly_do_tu_choi FROM dk_clb c "
                   "LEFT JOIN dk_phong ph ON ph.phong_id = c.phong_id LEFT JOIN dk_giao_vien g ON g.gv_id = c.gv_id")
            tham = ()
            if p["vai"] == GIAO_VIEN:
                sql += " WHERE c.gv_id = ?"
                tham = (p["id"],)
            cot = ("clb_id ten buoi loai phong_id phong gv_id giao_vien chi_tieu_gv chi_tieu khoi_tu khoi_den diem_san link_forms "
                   "mo_ta yeu_cau trang_thai ly_do_tu_choi").split()
            return [dict(zip(cot, r)) for r in cur.execute(sql + " ORDER BY c.buoi COLLATE THU_TU_BUOI, c.ten", tham)]
        return self._dk_chay(lam, QUAN_TRI, GIAO_VIEN, ghi=False, token=token)

    # ------------------------------------------------------------ học sinh đăng ký
    def dk_hs_clb_hop_le(self, token):
        """D21: chỉ CLB đã duyệt thuộc khối của em. Không có số đông (D26)."""
        def lam(cur, p):
            cot = "clb_id ten buoi loai phong khoi_tu khoi_den diem_san link_forms mo_ta yeu_cau giao_vien chi_tieu".split()
            return [dict(zip(cot, r)) for r in cur.execute(
                "SELECT c.clb_id, c.ten, c.buoi, c.loai, ph.ten, c.khoi_tu, c.khoi_den, c.diem_san, c.link_forms, c.mo_ta, c.yeu_cau, "
                "g.ten, c.chi_tieu FROM dk_clb c LEFT JOIN dk_phong ph ON ph.phong_id = c.phong_id "
                "LEFT JOIN dk_giao_vien g ON g.gv_id = c.gv_id WHERE c.trang_thai = 'duyet' AND ? BETWEEN "
                "c.khoi_tu AND c.khoi_den ORDER BY c.buoi COLLATE THU_TU_BUOI, c.ten", (p["khoi"],))]
        return self._dk_chay(lam, HOC_SINH, ghi=False, token=token)

    def dk_hs_nguyen_vong(self, token):
        """Nguyện vọng đã lưu của chính em (theo buổi, theo thứ hạng) và giờ nộp."""
        def lam(cur, p):
            nv = [dict(buoi=r[0], hang=r[1], clb_id=r[2], thi=bool(r[3]), diem=r[4], huy_chuong=r[5]) for r in cur.execute(
                "SELECT buoi, hang, clb_id, thi, diem, huy_chuong FROM dk_nguyen_vong WHERE student_id = ? ORDER BY buoi COLLATE THU_TU_BUOI, hang", (p["id"],))]
            nop = cur.execute("SELECT nop_luc FROM dk_hoc_sinh WHERE student_id = ?", (p["id"],)).fetchone()
            if nop is None:
                raise _Loi("dk_can_dang_nhap")
            return {"nguyen_vong": nv, "nop_luc": nop[0]}
        return self._dk_chay(lam, HOC_SINH, ghi=False, token=token)

    def dk_hs_luu(self, token, nguyen_vong, buoi_tay=None):
        """Lưu (ghi đè) nguyện vọng của em. `nguyen_vong` = danh sách `{clb_id, thi, huy_chuong}` theo THỨ TỰ em xếp; thứ hạng
        tính trong từng buổi. Huy chương: buổi nào KHÔNG nằm trong `buoi_tay` thì dùng mặc định (3 CLB không Tự do đứng đầu = Vàng,
        Bạc, Đồng), buổi trong `buoi_tay` thì giữ đúng huy chương em chọn (D2 đường A). Trả `{canh_bao: [...], nop_luc}`."""
        def lam(cur, p):
            if self._dk_gd != "hs_dang_ky":
                raise _Loi("dk_hs_chua_mo")
            if not cur.execute("SELECT 1 FROM dk_hoc_sinh WHERE student_id = ?", (p["id"],)).fetchone():
                raise _Loi("dk_can_dang_nhap")                       # em đã bị gỡ khỏi danh sách: phiên cũ không còn giá trị
            if nguyen_vong is not None and (not isinstance(nguyen_vong, (list, tuple)) or not all(isinstance(x, dict) for x in nguyen_vong)):
                raise _Loi("dk_nv_sai_dang")                       # VG2-L2: dữ liệu sai dạng có mã lỗi riêng
            tay = set(buoi_tay or [])
            theo_buoi, thay = {}, set()
            for x in nguyen_vong or []:
                cid = _so_nguyen((x or {}).get("clb_id"))
                r = cur.execute("SELECT clb_id, buoi, loai, khoi_tu, khoi_den FROM dk_clb WHERE clb_id = ? AND trang_thai = 'duyet'",
                                (cid,)).fetchone()
                if r is None or not r[3] <= p["khoi"] <= r[4]:
                    raise _Loi("dk_clb_khong_hop_le", clb=cid)
                if cid in thay:
                    raise _Loi("dk_nv_trung")
                thay.add(cid)
                theo_buoi.setdefault(r[1], []).append({"clb_id": cid, "loai": r[2], "thi": bool(x.get("thi")),
                                                        "huy_chuong": x.get("huy_chuong")})
            cu = {r[0]: r[1] for r in cur.execute("SELECT clb_id, diem FROM dk_nguyen_vong WHERE student_id = ?", (p["id"],))}
            hang_ra, canh_bao = [], []
            toi_da_nv, toi_da_thi = self._dk_gioi_han(cur)
            for b, ds in theo_buoi.items():
                if len(ds) > toi_da_nv:
                    raise _Loi("dk_qua_nguyen_vong", buoi=b, toi_da=toi_da_nv)
                if sum(d["thi"] for d in ds) > toi_da_thi:
                    raise _Loi("dk_qua_bai_thi", buoi=b, toi_da=toi_da_thi)
                if any(d["thi"] and d["loai"] != TUYEN_CHON for d in ds):
                    raise _Loi("dk_thi_sai_loai")
                if b in tay:
                    dung = set()
                    for d in ds:
                        hc = d["huy_chuong"] or None
                        if hc is not None:
                            if hc not in HUY_CHUONG:
                                raise _Loi("dk_huy_chuong_sai")
                            if d["loai"] == TU_DO:
                                raise _Loi("dk_huy_chuong_tu_do")
                            if hc in dung:
                                raise _Loi("dk_huy_chuong_trung")
                            dung.add(hc)
                        d["hc"] = hc
                else:
                    non_tu_do = [d for d in ds if d["loai"] != TU_DO]
                    for d in ds:
                        d["hc"] = None
                    for d, hc in zip(non_tu_do, HUY_CHUONG):
                        d["hc"] = hc
                if not any(d["loai"] == TU_DO for d in ds) and self._dk_bat_buoc_tu_do(cur):
                    canh_bao.append(err("dk_khong_co_tu_do", buoi=b))
                for hang, d in enumerate(ds, start=1):
                    hang_ra.append((p["id"], b, hang, d["clb_id"], int(d["thi"]), cu.get(d["clb_id"]) if d["thi"] else None, d["hc"]))
            moi_thi = {r[3] for r in hang_ra if r[4]}
            for cid_mat in sorted(c for c, d_ in cu.items() if d_ is not None and c not in moi_thi):      # VG2-L2: bỏ tick thi CLB đã có điểm
                canh_bao.append(err("dk_mat_diem", clb=cid_mat))
            cur.execute("DELETE FROM dk_nguyen_vong WHERE student_id = ?", (p["id"],))
            cur.executemany("INSERT INTO dk_nguyen_vong (student_id, buoi, hang, clb_id, thi, diem, huy_chuong) VALUES (?,?,?,?,?,?,?)",
                            hang_ra)
            nop = self._dk_bay_gio().isoformat(timespec="seconds")
            cur.execute("UPDATE dk_hoc_sinh SET nop_luc = ? WHERE student_id = ?", (nop, p["id"]))
            return {"canh_bao": canh_bao, "nop_luc": nop}
        return self._dk_chay(lam, HOC_SINH, token=token)

    # ------------------------------------------------------------ điểm
    def dk_diem_dat(self, token, student_id, clb_id, diem):
        """Ghi điểm 0–10 (số hoặc chuỗi dùng dấu phẩy) cho một em đã đánh dấu thi CLB Tuyển chọn đó; None = xoá điểm."""
        def lam(cur, p):
            if self._dk_gd not in ("hs_dang_ky", "nhap_diem"):
                raise _Loi("dk_sai_giai_doan", phan="nhap_diem")
            v = None
            if diem not in (None, ""):
                try:
                    v = float(str(diem).replace(",", "."))
                except ValueError:
                    raise _Loi("dk_diem_sai") from None
                if not 0 <= v <= 10:
                    raise _Loi("dk_diem_sai")
            cur.execute("UPDATE dk_nguyen_vong SET diem = ? WHERE student_id = ? AND clb_id = ? AND thi = 1", (v, student_id, clb_id))
            if cur.rowcount != 1:
                raise _Loi("dk_khong_thay")
            return {}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_diem_dan(self, token, clb_id, van_ban):
        """Dán "mã ⇥ điểm" (mỗi dòng một em) cho MỘT CLB. Dòng sai bị bỏ qua và liệt kê; dòng đúng được lưu."""
        def lam(cur, p):
            if self._dk_gd not in ("hs_dang_ky", "nhap_diem"):
                raise _Loi("dk_sai_giai_doan", phan="nhap_diem")
            da, loi = 0, []
            for i, dong in enumerate(str(van_ban or "").splitlines(), start=1):
                ph = [x for x in re.split(r"[\t;]|\s{2,}|\s", dong.strip(), maxsplit=1) if x != ""]
                if not ph:
                    continue
                try:
                    if len(ph) != 2:
                        raise ValueError
                    v = float(ph[1].replace(",", "."))
                    if not 0 <= v <= 10:
                        raise ValueError
                except ValueError:
                    loi.append({"dong": i, "ly_do": "diem_sai"})
                    continue
                cur.execute("UPDATE dk_nguyen_vong SET diem = ? WHERE student_id = ? AND clb_id = ? AND thi = 1", (v, ph[0], clb_id))
                if cur.rowcount == 1:
                    da += 1
                else:
                    loi.append({"dong": i, "ly_do": "khong_thi_clb_nay"})
            self._dk_ghi_nk(cur, QUAN_TRI, "dan_diem", "%s da=%d" % (clb_id, da))
            return {"da_luu": da, "loi": loi}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_diem_thieu(self, token):
        """Danh sách (em, CLB) đã đánh dấu thi nhưng chưa có điểm."""
        def lam(cur, p):
            return [dict(ma=r[0], ho_ten=r[1], clb_id=r[2], clb=r[3]) for r in cur.execute(
                "SELECT n.student_id, h.ho_ten, n.clb_id, c.ten FROM dk_nguyen_vong n JOIN dk_hoc_sinh h ON h.student_id = n.student_id "
                "JOIN dk_clb c ON c.clb_id = n.clb_id WHERE n.thi = 1 AND n.diem IS NULL ORDER BY c.ten, n.student_id")]
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    def dk_diem_danh_sach(self, token):
        """DKL-A2: mọi CLB Tuyển chọn có em đánh dấu thi: điểm sàn và từng em (mã, họ tên, lớp, điểm hoặc None)."""
        def lam(cur, p):
            ra = []
            for cid, ten, san in cur.execute(
                    "SELECT DISTINCT c.clb_id, c.ten, c.diem_san FROM dk_clb c JOIN dk_nguyen_vong n ON n.clb_id = c.clb_id "
                    "WHERE n.thi = 1 ORDER BY c.ten").fetchall():
                hs = [dict(ma=r[0], ho_ten=r[1], lop=r[2], diem=r[3]) for r in cur.execute(
                    "SELECT n.student_id, h.ho_ten, h.lop, n.diem FROM dk_nguyen_vong n JOIN dk_hoc_sinh h ON h.student_id = n.student_id "
                    "WHERE n.clb_id = ? AND n.thi = 1 ORDER BY h.lop, n.student_id", (cid,))]
                ra.append(dict(clb_id=cid, ten=ten, diem_san=san, hoc_sinh=hs))
            return ra
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    # ------------------------------------------------------------ đọc thêm cho quản trị
    def dk_tien_do(self, token):
        """D31: tiến độ nộp theo lớp (lớp chậm nhất trước) và số em chọn từng CLB (chỉ quản trị)."""
        def lam(cur, p):
            lop = [dict(lop=r[0], tong=r[1], da_nop=r[2]) for r in cur.execute(
                "SELECT lop, COUNT(*), SUM(nop_luc IS NOT NULL) FROM dk_hoc_sinh GROUP BY lop ORDER BY 1.0 * SUM(nop_luc IS NOT NULL) / "
                "COUNT(*), lop")]
            cau = [dict(clb_id=r[0], ten=r[1], so_em=r[2]) for r in cur.execute(
                "SELECT c.clb_id, c.ten, COUNT(n.student_id) FROM dk_clb c LEFT JOIN dk_nguyen_vong n ON n.clb_id = c.clb_id "
                "WHERE c.trang_thai = 'duyet' GROUP BY c.clb_id ORDER BY 3 DESC, c.ten")]
            return {"theo_lop": lop, "theo_clb": cau}
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    def dk_nhat_ky(self, token, gioi_han=100):
        def lam(cur, p):
            return [dict(luc=r[0], vai=r[1], hanh_dong=r[2], chi_tiet=r[3]) for r in cur.execute(
                "SELECT luc, vai, hanh_dong, chi_tiet FROM dk_nhat_ky ORDER BY id DESC LIMIT ?", (int(gioi_han),))]
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    # ------------------------------------------------------------ DKL-L4: cài đặt, xem trước, sao lưu
    def dk_cai_dat_doc(self, token):
        """Quản trị: mã trường, buổi, khối, giới hạn, số lần đã xuất, lần sao lưu cuối (đọc, không trả mật khẩu)."""
        def lam(cur, p):
            buoi, khoi = self._dk_buoi_khoi(cur)
            nv, thi = self._dk_gioi_han(cur)
            return {"ma_truong": self._dk_cai_dat(cur, "ma_truong", ""), "buoi": buoi, "khoi": khoi, "toi_da_nv": nv, "toi_da_thi": thi,
                    "so_lan_xuat": _so_nguyen(self._dk_cai_dat(cur, "so_lan_xuat", "0")) or 0, "sao_luu_luc": self._dk_cai_dat(cur, "sao_luu_luc"),
                    "giai_doan": self._dk_gd, "bat_buoc_tu_do": self._dk_bat_buoc_tu_do(cur),
                    "buoi_thieu_tu_do": self._dk_buoi_thieu_tu_do(cur) if self._dk_bat_buoc_tu_do(cur) else []}
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    def dk_cai_dat_doi(self, token, ma_truong=None, buoi=None, khoi=None, bat_buoc_tu_do=None, xac_nhan_rui_ro=False):
        """D4/D36: đổi mã trường (≥ 4 ký tự), danh sách buổi, dải khối. Buổi và khối chỉ đổi được ở giai đoạn Chuẩn bị
        (sau đó CLB và học sinh đã dựa vào chúng). Trả cài đặt hiện tại."""
        def lam(cur, p):
            if ma_truong is not None:
                ma = str(ma_truong).strip()
                if len(ma) < 4:
                    raise _Loi("dk_ma_truong_sai")
                self._dk_dat(cur, "ma_truong", ma)
            if buoi is not None or khoi is not None:
                if self._dk_gd != "chuan_bi":
                    raise _Loi("dk_sai_giai_doan", phan="chuan_bi")
                b0, k0 = self._dk_buoi_khoi(cur)
                ds = b0 if buoi is None else [str(b).strip() for b in buoi if str(b).strip()]
                k = k0 if khoi is None else [_so_nguyen(x) for x in khoi]
                if not ds or len(set(ds)) != len(ds) or len(k) != 2 or None in k or not 1 <= k[0] <= k[1] <= 12:
                    raise _Loi("dk_khoi_sai")
                if cur.execute("SELECT 1 FROM dk_clb LIMIT 1").fetchone() or (
                        khoi is not None and cur.execute("SELECT 1 FROM dk_hoc_sinh WHERE khoi < ? OR khoi > ? LIMIT 1", tuple(k)).fetchone()):
                    raise _Loi("dk_khoi_sai")
                self._dk_dat(cur, "buoi", json.dumps(ds, ensure_ascii=False))
                self._dk_dat(cur, "khoi", json.dumps(k))
            if bat_buoc_tu_do is not None:                              # VG1-L4 (D4): công tắc «bắt buộc có CLB Tự do»
                if not isinstance(bat_buoc_tu_do, bool):
                    raise _Loi("dk_khoi_sai")
                if CAC_GIAI_DOAN.index(self._dk_gd) > CAC_GIAI_DOAN.index("duyet"):
                    raise _Loi("dk_sai_giai_doan", phan="duyet")
                if not bat_buoc_tu_do and xac_nhan_rui_ro is not True:
                    raise _Loi("dk_can_xac_nhan_rui_ro")
                if bat_buoc_tu_do:                                       # bật lại: chạy lại kiểm (a)–(b)
                    thieu = self._dk_buoi_thieu_tu_do(cur)
                    if thieu:
                        raise _Loi("dk_thieu_clb_tu_do", buoi=", ".join(thieu))
                self._dk_dat(cur, "bat_buoc_tu_do", "1" if bat_buoc_tu_do else "0")
                self._dk_ghi_nk(cur, QUAN_TRI, "bat_buoc_tu_do", "bat" if bat_buoc_tu_do else "tat; xac_nhan_rui_ro")
            self._dk_ghi_nk(cur, QUAN_TRI, "doi_cai_dat", ",".join(x for x, v in (("ma", ma_truong), ("buoi", buoi), ("khoi", khoi)) if v is not None))
            return {}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_xuat_xem_truoc(self, token, toi_da=40):
        """DKL-A10 (D30): xem trước hai trang của Sổ nhập (`1. CLB`, `2. Học sinh`) và số lần đã xuất. Chỉ đọc."""
        def lam(cur, p):
            bm = self._dk_ban_mau(cur)
            clb = [[c["ten"], c["buoi"], c["loai"], c["chiTieu"], c["diemSan"], c["ma"], c["phong"], c["sucChuaPhong"]] for c in bm["clb"]]
            ten = {c["ma"]: c["ten"] for c in bm["clb"]}
            hs = [[x["ma"], x["hoTen"], x["lop"], "; ".join("%s%s%s" % (ten.get(n["clb"], n["clb"]), "" if n["diem"] is None else " · " + str(n["diem"]),
                                                              "" if not n["huyChuong"] else " · " + n["huyChuong"]) for n in x["nv"])]
                  for x in bm["hocSinh"][:max(1, int(toi_da))]]
            return {"clb": clb, "hoc_sinh": hs, "tong_hoc_sinh": len(bm["hocSinh"]),
                    "so_lan_xuat": _so_nguyen(self._dk_cai_dat(cur, "so_lan_xuat", "0")) or 0}
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    def dk_sao_luu(self, token):
        """DKL-A11 (D11): sao lưu `app.db` ngay (cùng cơ chế `_backup_db` của phần mềm, giữ vài bản gần nhất). Ghi giờ sao lưu."""
        kiem = self._dk_chay(lambda cur, p: {}, QUAN_TRI, ghi=False, token=token)
        if not kiem["ok"]:
            return kiem
        try:
            tep = os.path.basename(self._backup_db())
        except Exception:
            _log.exception("dk_sao_luu")
            return _fail(err("dk_loi_chung"))
        luc = self._dk_bay_gio().isoformat(timespec="seconds")

        def lam(cur, p):
            self._dk_dat(cur, "sao_luu_luc", luc)
            self._dk_ghi_nk(cur, QUAN_TRI, "sao_luu", "")
            return {"tep": tep, "luc": luc}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    # ------------------------------------------------------------ L4: xuất Sổ nhập
    def _dk_ban_mau(self, cur):
        """Dữ liệu xuất `dinhDang` 1 (đúng dạng `dk2_so_nhap.tu_ban_mau`) từ các bảng `dk_*`."""
        buoi = self._dk_buoi_khoi(cur)[0]
        clb, ma_cua = [], {}
        for r in cur.execute("SELECT c.clb_id, c.ten, c.buoi, c.loai, c.chi_tieu, c.diem_san, ph.ten, ph.suc_chua FROM dk_clb c "
                             "LEFT JOIN dk_phong ph ON ph.phong_id = c.phong_id WHERE c.trang_thai = 'duyet' ORDER BY c.buoi COLLATE THU_TU_BUOI, c.ten"):
            ma_cua[r[0]] = "CLB%03d" % r[0]
            clb.append({"ma": ma_cua[r[0]], "ten": r[1], "buoi": r[2], "loai": r[3],
                        "chiTieu": None if r[3] == TU_DO else r[4], "diemSan": r[5], "phong": r[6], "sucChuaPhong": r[7]})
        thu_tu = {b: i for i, b in enumerate(buoi)}
        nv_cua = {}
        for r in cur.execute("SELECT student_id, buoi, hang, clb_id, thi, diem, huy_chuong FROM dk_nguyen_vong"):
            if r[3] in ma_cua:
                nv_cua.setdefault(r[0], []).append((thu_tu.get(r[1], len(thu_tu)), r[2], {
                    "clb": ma_cua[r[3]], "thi": bool(r[4]), "diem": r[5], "huyChuong": r[6]}))
        hs = [{"ma": r[0], "hoTen": r[1], "lop": r[2], "nv": [x[2] for x in sorted(nv_cua.get(r[0], []), key=lambda x: x[:2])]}
              for r in cur.execute("SELECT student_id, ho_ten, lop FROM dk_hoc_sinh ORDER BY lop, student_id")]
        return {"dinhDang": 1, "buoi": buoi, "clb": clb, "hocSinh": hs}

    def dk_xuat_ban_mau(self, token):
        """Quản trị: JSON `dinhDang` 1 (cùng dạng với "Chép dữ liệu xuất" của bản mẫu). Chỉ đọc."""
        def lam(cur, p):
            return self._dk_ban_mau(cur)
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    def dk_xuat_so_nhap(self, token, duong_dan=""):
        """Quản trị: ghi `SO_NHAP_CLB.xlsx` qua `dk2_so_nhap.ghi_tu_ban_mau` (mặc định: cạnh app.db). Từ giai đoạn Nhập điểm
        trở đi; còn bài thi chưa có điểm thì từ chối. Dữ liệu sai thì KHÔNG ghi tệp, trả lỗi `dk_khong_xuat_duoc`."""
        import dk2_so_nhap

        def lam(cur, p):
            if CAC_GIAI_DOAN.index(self._dk_gd) < CAC_GIAI_DOAN.index("nhap_diem"):
                raise _Loi("dk_sai_giai_doan", phan="nhap_diem")
            thieu = cur.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE thi = 1 AND diem IS NULL").fetchone()[0]
            if thieu:
                raise _Loi("dk_thieu_diem", n=thieu)
            du_lieu = self._dk_ban_mau(cur)
            dich = duong_dan or os.path.join(os.path.dirname(os.path.abspath(self.db_path)), "SO_NHAP_CLB.xlsx")
            try:
                kq = dk2_so_nhap.ghi_tu_ban_mau(du_lieu, dich)
            except dk2_so_nhap.LoiBanMau as e:
                raise _Loi("dk_khong_xuat_duoc", detail="; ".join(e.loi[:3])) from None
            lan = (_so_nguyen(self._dk_cai_dat(cur, "so_lan_xuat", "0")) or 0) + 1
            self._dk_dat(cur, "so_lan_xuat", str(lan))
            self._dk_ghi_nk(cur, QUAN_TRI, "xuat_so_nhap", "lan %d: %d clb %d hs" % (lan, kq["so_clb"], kq["so_hs"]))
            return {"duong_dan": dich, "phien_ban": lan, **kq}
        return self._dk_chay(lam, QUAN_TRI, token=token)
