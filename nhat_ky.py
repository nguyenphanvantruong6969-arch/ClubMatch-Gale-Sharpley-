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

_log = logging.getLogger(__name__)

# Tên tham số / khoá nghe như bí mật hoặc là nội dung tệp: bỏ hẳn.
_AN = re.compile(r"mat_khau|password|passwd|(^|_)pw($|_)|token|secret|tra_cuu|bi_mat|base64|^cu$|^moi$", re.I)
# Hàm có tham số vị trí khó đoán: chỉ giữ đúng những tên này.
_CHI_GIU = {
    "dang_nhap": ("ten",),
    "tao_tai_khoan": ("ten", "vai"),
    "xoa_tai_khoan": ("ten",),
    "doi_mat_khau": (),
}
_GIOI_HAN_GIA_TRI = 80
_GIOI_HAN_TONG = 300
_TOI_DA_PHAN_TU = 8
_TOI_DA_KHOA = 12

# Không ghi: chỉ đọc / chuẩn hoá / tiện ích giao diện.
_DOC = ("get_", "list_", "search_", "xem_truoc", "check_", "detect_", "preview_", "liet_ke")
_KHONG_GHI = frozenset("""chuan_hoa_buoi chuan_hoa_nhom_du_tru dat_tieu_de_cua_so mo_thu_muc xlsx_to_csv_text
kiem_chi_tieu_ky_sau lay_so_nhap_nap nhan_dien_tep_forms tai_mau_de_thi get_phien_dang_nhap""".split())


def nen_ghi(ten: str) -> bool:
    """Hàm này có để lại dòng nhật ký khi đã có tài khoản không? Mặc định CÓ (ghi thừa còn hơn thiếu)."""
    if ten in _KHONG_GHI:
        return False
    if ten in _CHI_GIU:
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


def ghi(api, nguoi, vai, hanh_dong: str, ket_qua: str, chi_tiet=None) -> None:
    """Thêm MỘT dòng. Hỏng thì chỉ cảnh báo trong log, không ném."""
    try:
        with api._ket_noi_ghi() as cur:
            cur.execute(
                "INSERT INTO nhat_ky_thao_tac (luc, nguoi, vai, hanh_dong, ket_qua, chi_tiet) VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(timespec="seconds"), nguoi, vai, hanh_dong, ket_qua, chi_tiet))
    except Exception as e:                                  # noqa: BLE001
        _log.warning("không ghi được nhật ký thao tác %s (%s)", hanh_dong, type(e).__name__)


# --------------------------------------------------------------------- đọc
COT = ("id", "luc", "nguoi", "vai", "hanh_dong", "ket_qua", "chi_tiet")


def _loc(nguoi, hanh_dong):
    dk, tham = [], []
    if nguoi:
        dk.append("nguoi = ?")
        tham.append(str(nguoi))
    if hanh_dong:
        dk.append("hanh_dong = ?")
        tham.append(str(hanh_dong))
    return (" WHERE " + " AND ".join(dk)) if dk else "", tham


def doc_trang(cur, page, page_size, nguoi=None, hanh_dong=None):
    """`(dòng, tổng)` — mới nhất trước. `page` tính từ 1; `page_size` 1..500."""
    try:
        page = max(1, int(page))
        page_size = min(500, max(1, int(page_size)))
    except (TypeError, ValueError):
        page, page_size = 1, 50
    where, tham = _loc(nguoi, hanh_dong)
    tong = cur.execute("SELECT COUNT(*) FROM nhat_ky_thao_tac" + where, tham).fetchone()[0]
    dong = cur.execute(
        "SELECT " + ", ".join(COT) + " FROM nhat_ky_thao_tac" + where + " ORDER BY id DESC LIMIT ? OFFSET ?",
        tham + [page_size, (page - 1) * page_size]).fetchall()
    return [dict(zip(COT, r)) for r in dong], tong, page, page_size


def doc_het(cur, nguoi=None, hanh_dong=None):
    where, tham = _loc(nguoi, hanh_dong)
    return cur.execute("SELECT " + ", ".join(COT) + " FROM nhat_ky_thao_tac" + where + " ORDER BY id", tham).fetchall()
