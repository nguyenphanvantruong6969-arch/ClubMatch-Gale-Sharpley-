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
BUOI_MAC_DINH = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
KHOI_MAC_DINH = [6, 12]


class _Loi(Exception):
    def __init__(self, ma, **tham_so):
        self.loi = err(ma, **tham_so)
        super().__init__(ma)


def _bam(pin: str, muoi: bytes = None):
    muoi = muoi or secrets.token_bytes(16)
    return hashlib.pbkdf2_hmac("sha256", unicodedata.normalize("NFC", str(pin)).encode(), muoi, SO_VONG_PIN), muoi


def _dung(pin, bam, muoi) -> bool:
    return hmac.compare_digest(_bam(pin, bytes(muoi))[0], bytes(bam))


def _pin_moi() -> str:
    return "%04d" % secrets.randbelow(10000)


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
            if not ma:
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

    def dk_dang_nhap(self, vai, ten, ma):
        """`vai` = quan_tri (ten bỏ qua, ma = mật khẩu) | giao_vien (ten, ma = PIN) | hoc_sinh (ten = mã học sinh, ma = PIN).
        Trả `{token, vai, ten, ...}`. Sai thì cùng MỘT lỗi cho mọi trường hợp (không lộ tên nào có thật)."""
        def lam(cur, _):
            if self._dk_cai_dat(cur, "mk_bam") is None:
                raise _Loi("dk_chua_khoi_tao")
            ma_s = str(ma or "")
            if vai == QUAN_TRI:
                ok = _dung(ma_s, bytes.fromhex(self._dk_cai_dat(cur, "mk_bam")), bytes.fromhex(self._dk_cai_dat(cur, "mk_muoi")))
                thong = {"ten": "Quản trị"}
            elif vai == GIAO_VIEN:
                r = cur.execute("SELECT gv_id, ten, pin_bam, pin_muoi FROM dk_giao_vien WHERE ten = ?",
                                (str(ten or "").strip(),)).fetchone()
                ok = bool(r) and _dung(ma_s, r[2], r[3])
                thong = {"ten": r[1], "id": r[0]} if r else {}
            elif vai == HOC_SINH:
                r = cur.execute("SELECT student_id, ho_ten, lop, khoi, pin_bam, pin_muoi FROM dk_hoc_sinh WHERE student_id = ?",
                                (str(ten or "").strip(),)).fetchone()
                ok = bool(r) and _dung(ma_s, r[4], r[5])
                thong = {"ten": r[1], "id": r[0], "lop": r[2], "khoi": r[3]} if r else {}
            else:
                ok, thong = False, {}
            if not ok:
                _dung(ma_s, b"x", b"y")        # thời gian phản hồi như nhau
                raise _Loi("dk_sai_dang_nhap")
            token = secrets.token_urlsafe(24)
            self._dk_phien_dict()[token] = {"vai": vai, "luc": self._dk_dong_ho(), **thong}
            return {"token": token, "vai": vai, **thong}
        return self._dk_chay(lam, ghi=False)

    def dk_dang_xuat(self, token):
        self._dk_phien_dict().pop(token, None)
        return _ok({})

    def dk_trang_thai(self):
        """Công khai: giai đoạn hiện tại, hạn chót, buổi, khối. Không có dữ liệu cá nhân."""
        def lam(cur, _):
            if self._dk_cai_dat(cur, "mk_bam") is None:
                return {"khoi_tao": False}
            buoi, khoi = self._dk_buoi_khoi(cur)
            gd = self._dk_giai_doan_hien_tai(cur)
            han = cur.execute("SELECT han_chot FROM dk_giai_doan WHERE ten = ?", (gd,)).fetchone()
            return {"khoi_tao": True, "giai_doan": gd, "han_chot": han[0] if han else None, "buoi": buoi, "khoi": khoi}
        return self._dk_chay(lam)

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
        if thieu:
            return err("dk_thieu_clb_tu_do", buoi=", ".join(thieu))
        return None

    def dk_chuyen_giai_doan(self, token, giai_doan):
        """Sang giai đoạn kế (hoặc lùi — có ghi nhật ký). Mở cho học sinh phải qua `_dk_kiem_dieu_kien_mo_hs`."""
        def lam(cur, p):
            if giai_doan not in CAC_GIAI_DOAN:
                raise _Loi("dk_giai_doan_la")
            hien = self._dk_gd
            if giai_doan == "hs_dang_ky" and CAC_GIAI_DOAN.index(hien) < CAC_GIAI_DOAN.index("hs_dang_ky"):
                loi = self._dk_kiem_dieu_kien_mo_hs(cur)
                if loi:
                    raise _Loi(loi["code"], **loi["params"])
            if giai_doan == "nhap_diem" and hien == "hs_dang_ky":
                pass
            if giai_doan == "xuat":
                thieu = cur.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE thi = 1 AND diem IS NULL").fetchone()[0]
                if thieu:
                    raise _Loi("dk_thieu_diem", n=thieu)
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
            if cur.execute("SELECT 1 FROM dk_phong WHERE ten = ?", (t,)).fetchone():
                raise _Loi("dk_phong_trung")
            cur.execute("INSERT INTO dk_phong (ten, suc_chua) VALUES (?, ?)", (t, sc))
            self._dk_ghi_nk(cur, QUAN_TRI, "them_phong", t)
            return {"phong_id": cur.lastrowid}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_phong_xoa(self, token, phong_id):
        def lam(cur, p):
            if cur.execute("SELECT 1 FROM dk_clb WHERE phong_id = ? AND trang_thai != 'tu_choi'", (phong_id,)).fetchone():
                raise _Loi("dk_phong_dang_dung")
            cur.execute("DELETE FROM dk_phong WHERE phong_id = ?", (phong_id,))
            self._dk_ghi_nk(cur, QUAN_TRI, "xoa_phong", phong_id)
            return {}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_phong_danh_sach(self, token):
        def lam(cur, p):
            return [dict(phong_id=r[0], ten=r[1], suc_chua=r[2]) for r in cur.execute(
                "SELECT phong_id, ten, suc_chua FROM dk_phong ORDER BY ten")]
        return self._dk_chay(lam, QUAN_TRI, GIAO_VIEN, ghi=False, token=token)

    # ------------------------------------------------------------ giáo viên
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
            if cur.execute("SELECT 1 FROM dk_giao_vien WHERE ten = ?", (t,)).fetchone():
                raise _Loi("dk_gv_trung")
            b, m = _bam(pin)
            cur.execute("INSERT INTO dk_giao_vien (ten, pin_bam, pin_muoi, cach_tao) VALUES (?, ?, ?, 'tu_dang_ky')", (t, b, m))
            self._dk_ghi_nk(cur, GIAO_VIEN, "tu_dang_ky", t)
            return {"gv_id": cur.lastrowid}
        return self._dk_chay(lam)

    def dk_gv_tao_hang_loat(self, token, van_ban):
        """Quản trị dán tên (mỗi dòng một giáo viên), PIN tự sinh. Trả danh sách `{ten, pin}` (PIN chỉ hiện lần này)."""
        def lam(cur, p):
            ra, bo_qua = [], []
            for dong in str(van_ban or "").splitlines():
                t = unicodedata.normalize("NFC", dong).strip()
                if not t:
                    continue
                if len(t) > 60 or cur.execute("SELECT 1 FROM dk_giao_vien WHERE ten = ?", (t,)).fetchone():
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

    def dk_gv_dat_lai_pin(self, token, gv_id):
        def lam(cur, p):
            if not cur.execute("SELECT 1 FROM dk_giao_vien WHERE gv_id = ?", (gv_id,)).fetchone():
                raise _Loi("dk_khong_thay")
            pin = _pin_moi()
            b, m = _bam(pin)
            cur.execute("UPDATE dk_giao_vien SET pin_bam = ?, pin_muoi = ? WHERE gv_id = ?", (b, m, gv_id))
            self._dk_ghi_nk(cur, QUAN_TRI, "dat_lai_pin_gv", gv_id)
            return {"pin": pin}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_gv_danh_sach(self, token):
        def lam(cur, p):
            return [dict(gv_id=r[0], ten=r[1], cach_tao=r[2]) for r in cur.execute(
                "SELECT gv_id, ten, cach_tao FROM dk_giao_vien ORDER BY ten")]
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
                if any(h[0] == ma for h in hop_le):
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
            for ma, ten, lop, khoi in hop_le:
                if cur.execute("SELECT 1 FROM dk_hoc_sinh WHERE student_id = ?", (ma,)).fetchone():
                    cur.execute("UPDATE dk_hoc_sinh SET ho_ten = ?, lop = ?, khoi = ? WHERE student_id = ?", (ten, lop, khoi, ma))
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
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_hs_dat_lai_pin(self, token, student_id):
        def lam(cur, p):
            if not cur.execute("SELECT 1 FROM dk_hoc_sinh WHERE student_id = ?", (student_id,)).fetchone():
                raise _Loi("dk_khong_thay")
            pin = _pin_moi()
            b, m = _bam(pin)
            cur.execute("UPDATE dk_hoc_sinh SET pin_bam = ?, pin_muoi = ? WHERE student_id = ?", (b, m, student_id))
            self._dk_ghi_nk(cur, QUAN_TRI, "dat_lai_pin_hs", student_id)
            return {"pin": pin}
        return self._dk_chay(lam, QUAN_TRI, token=token)

    def dk_hs_danh_sach(self, token):
        def lam(cur, p):
            return [dict(ma=r[0], ho_ten=r[1], lop=r[2], khoi=r[3], da_nop=bool(r[4])) for r in cur.execute(
                "SELECT student_id, ho_ten, lop, khoi, nop_luc FROM dk_hoc_sinh ORDER BY lop, student_id")]
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    # ------------------------------------------------------------ CLB
    def _dk_kiem_clb(self, cur, d, gv_id, clb_id):
        """Kiểm D14 / D15 và trả bản ghi sạch. `d` từ giao diện; ném `_Loi` ở lỗi đầu tiên."""
        buoi, (k_tu, k_den) = self._dk_buoi_khoi(cur)
        ten = unicodedata.normalize("NFC", str(d.get("ten") or "")).strip()
        if not ten or len(ten) > 80:
            raise _Loi("dk_ten_trong")
        if cur.execute("SELECT 1 FROM dk_clb WHERE ten = ? AND clb_id IS NOT ?", (ten, clb_id)).fetchone():
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

    def dk_clb_duyet(self, token, clb_id, quyet_dinh, chi_tieu=None, phong_id=None, ly_do=""):
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
                cur.execute("UPDATE dk_clb SET trang_thai = 'tu_choi', ly_do_tu_choi = ? WHERE clb_id = ?", (str(ly_do or "")[:300], clb_id))
            else:
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
            return [dict(zip(cot, r)) for r in cur.execute(sql + " ORDER BY c.buoi, c.ten", tham)]
        return self._dk_chay(lam, QUAN_TRI, GIAO_VIEN, ghi=False, token=token)

    # ------------------------------------------------------------ học sinh đăng ký
    def dk_hs_clb_hop_le(self, token):
        """D21: chỉ CLB đã duyệt thuộc khối của em. Không có số đông (D26)."""
        def lam(cur, p):
            cot = "clb_id ten buoi loai phong khoi_tu khoi_den diem_san link_forms mo_ta yeu_cau".split()
            return [dict(zip(cot, r)) for r in cur.execute(
                "SELECT c.clb_id, c.ten, c.buoi, c.loai, ph.ten, c.khoi_tu, c.khoi_den, c.diem_san, c.link_forms, c.mo_ta, c.yeu_cau "
                "FROM dk_clb c LEFT JOIN dk_phong ph ON ph.phong_id = c.phong_id WHERE c.trang_thai = 'duyet' AND ? BETWEEN "
                "c.khoi_tu AND c.khoi_den ORDER BY c.buoi, c.ten", (p["khoi"],))]
        return self._dk_chay(lam, HOC_SINH, ghi=False, token=token)

    def dk_hs_nguyen_vong(self, token):
        """Nguyện vọng đã lưu của chính em (theo buổi, theo thứ hạng) và giờ nộp."""
        def lam(cur, p):
            nv = [dict(buoi=r[0], hang=r[1], clb_id=r[2], thi=bool(r[3]), diem=r[4], huy_chuong=r[5]) for r in cur.execute(
                "SELECT buoi, hang, clb_id, thi, diem, huy_chuong FROM dk_nguyen_vong WHERE student_id = ? ORDER BY buoi, hang", (p["id"],))]
            nop = cur.execute("SELECT nop_luc FROM dk_hoc_sinh WHERE student_id = ?", (p["id"],)).fetchone()[0]
            return {"nguyen_vong": nv, "nop_luc": nop}
        return self._dk_chay(lam, HOC_SINH, ghi=False, token=token)

    def dk_hs_luu(self, token, nguyen_vong, buoi_tay=None):
        """Lưu (ghi đè) nguyện vọng của em. `nguyen_vong` = danh sách `{clb_id, thi, huy_chuong}` theo THỨ TỰ em xếp; thứ hạng
        tính trong từng buổi. Huy chương: buổi nào KHÔNG nằm trong `buoi_tay` thì dùng mặc định (3 CLB không Tự do đứng đầu = Vàng,
        Bạc, Đồng), buổi trong `buoi_tay` thì giữ đúng huy chương em chọn (D2 đường A). Trả `{canh_bao: [...], nop_luc}`."""
        def lam(cur, p):
            if self._dk_gd != "hs_dang_ky":
                raise _Loi("dk_hs_chua_mo")
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
            for b, ds in theo_buoi.items():
                if len(ds) > TOI_DA_NV_BUOI:
                    raise _Loi("dk_qua_nguyen_vong", buoi=b, toi_da=TOI_DA_NV_BUOI)
                if sum(d["thi"] for d in ds) > TOI_DA_THI_BUOI:
                    raise _Loi("dk_qua_bai_thi", buoi=b, toi_da=TOI_DA_THI_BUOI)
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
                if not any(d["loai"] == TU_DO for d in ds):
                    canh_bao.append(err("dk_khong_co_tu_do", buoi=b))
                for hang, d in enumerate(ds, start=1):
                    hang_ra.append((p["id"], b, hang, d["clb_id"], int(d["thi"]), cu.get(d["clb_id"]) if d["thi"] else None, d["hc"]))
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

    # ------------------------------------------------------------ L4: xuất Sổ nhập
    def _dk_ban_mau(self, cur):
        """Dữ liệu xuất `dinhDang` 1 (đúng dạng `dk2_so_nhap.tu_ban_mau`) từ các bảng `dk_*`."""
        buoi = self._dk_buoi_khoi(cur)[0]
        clb, ma_cua = [], {}
        for r in cur.execute("SELECT c.clb_id, c.ten, c.buoi, c.loai, c.chi_tieu, c.diem_san, ph.ten, ph.suc_chua FROM dk_clb c "
                             "LEFT JOIN dk_phong ph ON ph.phong_id = c.phong_id WHERE c.trang_thai = 'duyet' ORDER BY c.buoi, c.ten"):
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
            self._dk_ghi_nk(cur, QUAN_TRI, "xuat_so_nhap", "%d clb %d hs" % (kq["so_clb"], kq["so_hs"]))
            return {"duong_dan": dich, **kq}
        return self._dk_chay(lam, QUAN_TRI, token=token)
