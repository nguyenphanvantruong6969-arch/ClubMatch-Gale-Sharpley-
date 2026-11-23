"""GT3-L3: nhật ký thao tác (chỉ thêm) — chỉ ghi khi đã có tài khoản.

Bảng `nhat_ky_thao_tac` nằm trong schema (rbda_priority_pipeline.py), hai trigger chặn UPDATE / DELETE.
Một dòng ghi KHÔNG BAO GIỜ làm hỏng thao tác chính: ghi lỗi thì chỉ đưa cảnh báo vào log (không kèm tham số).
Mật khẩu, mã bí mật, nội dung tệp (base64) không bao giờ vào `chi_tiet`. Chỉ là báo cáo, không dính `compute_club_priority`.
"""

import datetime
import inspect
import json
import logging
import re
import threading

_log = logging.getLogger(__name__)

# Tên tham số / khoá nghe như bí mật hoặc là nội dung tệp: bỏ hẳn.
_AN = re.compile(r"mat_khau|password|passwd|(^|_)pw($|_)|token|secret|tra_cuu|bi_mat|base64|^cu$|^moi$|^ma$", re.I)   # GT4-L1: `ma` = mã tra cứu của học sinh
# Hàm có tham số vị trí khó đoán: chỉ giữ đúng những tên này.
_CHI_GIU = {
    "dang_nhap": ("ten",),
    "tao_tai_khoan": ("ten", "vai"),
    "xoa_tai_khoan": ("ten",),
    "doi_mat_khau": (),
    "thoat_che_do_hoc_sinh": (),      # I2: tên gõ vào có thể là mật khẩu gõ nhầm ô
    "tra_cuu_hoc_sinh": ("student_id",),            # GT4-L1: mã tra cứu (đúng hay gõ sai) không bao giờ vào nhật ký
    "get_giai_trinh_hoc_sinh": ("student_id", "run_id"),   # GT4-L1 (D4-2): xem lời giải trình của một em
}
# Tên bắt đầu bằng `get_` nhưng đọc dữ liệu riêng tư của một học sinh: vẫn để lại một dòng nhật ký (D4-2).
_GHI_DU_LA_DOC = frozenset({"get_giai_trinh_hoc_sinh"})
_GIOI_HAN_GIA_TRI = 80
_GIOI_HAN_TONG = 300
_TOI_DA_PHAN_TU = 8
_TOI_DA_KHOA = 12

# Không ghi: chỉ đọc / chuẩn hoá / tiện ích giao diện.
_DOC = ("get_", "list_", "search_", "xem_truoc", "check_", "detect_", "preview_", "liet_ke")
_KHONG_GHI = frozenset("""chuan_hoa_buoi chuan_hoa_nhom_du_tru chuan_hoa_o_nhom_clb o_nhom_hs_co_gach dat_tieu_de_cua_so mo_thu_muc mo_tep xlsx_to_csv_text
kiem_chi_tieu_ky_sau lay_so_nhap_nap nhan_dien_tep_forms tai_mau_de_thi get_phien_dang_nhap
uoc_tinh_muc_tieu bao_cao_muc_tieu""".split())


def nen_ghi(ten: str) -> bool:
    """Hàm này có để lại dòng nhật ký khi đã có tài khoản không? Mặc định CÓ (ghi thừa còn hơn thiếu)."""
    if ten in _KHONG_GHI:
        return False
    if ten in _CHI_GIU or ten in _GHI_DU_LA_DOC:
        return True
    return not ten.startswith(_DOC)


def _gon(v, sau=0):
    if v is None or isinstance(v, (bool, int, float)):
        return v
    if isinstance(v, (bytes, bytearray)):
        return f"<{len(v)} byte>"
    if isinstance(v, str):
        return v if len(v) <= _GIOI_HAN_GIA_TRI else f"<chuỗi {len(v)} ký tự>"
    if sau >= 3:
        return "<...>"
    if isinstance(v, (list, tuple, set, frozenset)):
        v = list(v)
        if len(v) > _TOI_DA_PHAN_TU:
            return f"<danh sách {len(v)} phần tử>"
        return [_gon(x, sau + 1) for x in v]
    if isinstance(v, dict):
        ra = {}
        for k, x in list(v.items())[:_TOI_DA_KHOA]:
            if not _AN.search(str(k)):
                ra[str(k)] = _gon(x, sau + 1)
        if len(v) > _TOI_DA_KHOA:
            ra["..."] = f"+{len(v) - _TOI_DA_KHOA}"
        return ra
    return str(v)[:_GIOI_HAN_GIA_TRI]


def tom_tat_tham_so(ham, ten: str, args, kwargs) -> str:
    """Chuỗi JSON ngắn mô tả tham số lời gọi, đã bỏ bí mật. Không bao giờ ném lỗi."""
    try:
        try:
            ten_tham_so = inspect.signature(ham).bind(None, *args, **kwargs).arguments
            ten_tham_so = {k: v for k, v in ten_tham_so.items() if k != "self"}
        except TypeError:
            ten_tham_so = {f"#{i}": v for i, v in enumerate(args)}
            ten_tham_so.update(kwargs)
        giu = _CHI_GIU.get(ten)
        ra = {}
        for k, v in ten_tham_so.items():
            if giu is not None and k not in giu:
                continue
            if _AN.search(k):
                continue
            ra[k] = _gon(v)
        s = json.dumps(ra, ensure_ascii=False, default=str)
        return s if len(s) <= _GIOI_HAN_TONG else s[:_GIOI_HAN_TONG - 1] + "…"
    except Exception:
        return "{}"


def ket_qua_tu(r) -> str:
    """'ok' hoặc mã lỗi đầu tiên của phản hồi `{ok, data, errors}`."""
    if isinstance(r, dict) and r.get("ok") is False:
        loi = r.get("errors") or []
        if loi and isinstance(loi[0], dict) and loi[0].get("code"):
            return str(loi[0]["code"])
        return "loi"
    return "ok"


_CHO_KHOA_GIAY = 1.0      # chờ khoá ghi tối đa chừng này; quá thì ghi bù sau, lời gọi chính không bị giữ
_SQL_GHI = "INSERT INTO nhat_ky_thao_tac (luc, nguoi, vai, hanh_dong, ket_qua, chi_tiet) VALUES (?, ?, ?, ?, ?, ?)"


def _ghi_tai(api, duong, dong_ghi):
    """Ghi thẳng vào CSDL `duong` (đã chụp TRƯỚC lời gọi). Gọi khi đang giữ khoá ghi."""
    import os
    from rbda_priority_pipeline import connect_db
    chung = getattr(api._giao_dich, "conn", None)
    if chung is not None and duong == api.db_path:
        chung.cursor().execute(_SQL_GHI, dong_ghi)
        return
    if not os.path.exists(duong):         # workspace vừa bị dời đi: không tạo tệp rỗng
        raise FileNotFoundError("CSDL không còn")
    conn = connect_db(duong)
    try:
        conn.execute(_SQL_GHI, dong_ghi)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ghi(api, nguoi, vai, hanh_dong: str, ket_qua: str, chi_tiet=None, db_path=None) -> None:
    """Thêm MỘT dòng vào `db_path` (mặc định: CSDL hiện tại). Hỏng thì chỉ cảnh báo trong log, không ném.

    Không bao giờ chờ khoá ghi quá `_CHO_KHOA_GIAY`: lời gọi bị từ chối / chạy song song với một lần chạy xếp
    dài phải trả về ngay. Hết hạn chờ thì một luồng nền ghi bù khi khoá được nhả.
    """
    duong = db_path or api.db_path
    dong_ghi = (datetime.datetime.now().isoformat(timespec="seconds"), nguoi, vai, hanh_dong, ket_qua, chi_tiet)

    def lam():
        try:
            _ghi_tai(api, duong, dong_ghi)
        except Exception as e:                              # noqa: BLE001
            _log.warning("không ghi được nhật ký thao tác %s (%s)", hanh_dong, type(e).__name__)

    khoa = api._khoa_ghi
    if khoa.acquire(timeout=_CHO_KHOA_GIAY):
        try:
            lam()
        finally:
            khoa.release()
        return

    def sau():
        with khoa:
            lam()
    threading.Thread(target=sau, name="nhat_ky_ghi_bu", daemon=True).start()


# --------------------------------------------------------------------- đọc
COT = ("id", "luc", "nguoi", "vai", "hanh_dong", "ket_qua", "chi_tiet")


_RE_NGAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _loc(cur, nguoi, hanh_dong, chi_tu_choi=False, ngay=None):
    """Điều kiện lọc. `chi_tu_choi`: chỉ dòng có kết quả khác `ok` (bị từ chối hoặc lỗi). `ngay`: `YYYY-MM-DD` (ngày
    giờ máy, đúng như cột `luc`); sai dạng -> `ValueError` (API đổi thành `gt4_ngay_sai`); rỗng/None = không lọc."""
    import tai_khoan as tk
    dk, tham = [], []
    if nguoi:
        # Tên không phân biệt hoa/thường và NFC như tên tài khoản; không khớp tài khoản nào thì giữ nguyên chữ gõ.
        dk.append("nguoi = ?")
        tham.append(tk.tim_ten(cur, str(nguoi)) or str(nguoi))
    if hanh_dong:
        dk.append("hanh_dong = ?")
        tham.append(str(hanh_dong))
    if chi_tu_choi:
        dk.append("ket_qua <> 'ok'")
    if ngay:
        try:
            datetime.date.fromisoformat(str(ngay))
        except ValueError:
            raise ValueError("ngay") from None
        if not _RE_NGAY.match(str(ngay)):
            raise ValueError("ngay")
        dk.append("substr(luc, 1, 10) = ?")
        tham.append(str(ngay))
    return (" WHERE " + " AND ".join(dk)) if dk else "", tham


def hanh_dong_co(cur):
    """Các tên hành động đang có trong nhật ký (không trùng, xếp tên) — cho ô chọn lọc."""
    return [r[0] for r in cur.execute("SELECT DISTINCT hanh_dong FROM nhat_ky_thao_tac ORDER BY hanh_dong")]


def doc_trang(cur, page, page_size, nguoi=None, hanh_dong=None, chi_tu_choi=False, ngay=None):
    """`(dòng, tổng)` — mới nhất trước. `page` tính từ 1; `page_size` 1..500."""
    try:
        page = max(1, int(page))
        page_size = min(500, max(1, int(page_size)))
    except (TypeError, ValueError):
        page, page_size = 1, 50
    where, tham = _loc(cur, nguoi, hanh_dong, chi_tu_choi, ngay)
    tong = cur.execute("SELECT COUNT(*) FROM nhat_ky_thao_tac" + where, tham).fetchone()[0]
    dong = cur.execute(
        "SELECT " + ", ".join(COT) + " FROM nhat_ky_thao_tac" + where + " ORDER BY id DESC LIMIT ? OFFSET ?",
        tham + [page_size, (page - 1) * page_size]).fetchall()
    return [dict(zip(COT, r)) for r in dong], tong, page, page_size


def doc_het(cur, nguoi=None, hanh_dong=None, chi_tu_choi=False, ngay=None):
    where, tham = _loc(cur, nguoi, hanh_dong, chi_tu_choi, ngay)
    return cur.execute("SELECT " + ", ".join(COT) + " FROM nhat_ky_thao_tac" + where + " ORDER BY id", tham).fetchall()
