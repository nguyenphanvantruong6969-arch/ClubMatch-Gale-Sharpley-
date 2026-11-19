"""XP1 — lõi xuất PDF (không biết gì về dữ liệu CLB; các lô sau dựng nội dung từ dữ liệu có sẵn).

Khối dựng sẵn: `tieu_de`, `dong_khoa_gia_tri`, `bang` (lặp tiêu đề cột khi sang trang, ô tự xuống
dòng), `ngat_trang`. `dung_pdf(duong, khoi)` ghi A4 dọc, chân trang "Trang x/y", ghi qua tệp tạm rồi
đổi tên và KHÔNG ghi đè (trùng tên thì "x (2).pdf", cùng luật `duong_dan_khong_de`).
Phông: Be Vietnam Pro .ttf (SIL OFL) trong `assets/fonts/`, tìm như phần mềm tìm `assets/` khác.
"""
import os
import sys
import tempfile
from xml.sax.saxutils import escape

from api_chung import duong_dan_khong_de

_GOC = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
_THU_MUC_PHONG = os.path.join(_GOC, "assets", "fonts")
_PHONG = {"BeVietnamPro": "BeVietnamPro-Regular.ttf", "BeVietnamPro-Bold": "BeVietnamPro-Bold.ttf"}
_da_dang_ky = False


class ThieuThuVienPdf(Exception):
    """Thiếu reportlab hoặc tệp phông: lô UI ánh xạ sang mã lỗi `xp1_thieu_thu_vien_pdf`."""


def _rl():
    try:
        import reportlab  # noqa: F401
        return reportlab
    except ImportError as e:
        raise ThieuThuVienPdf("reportlab") from e


def _dang_ky_phong():
    global _da_dang_ky
    if _da_dang_ky:
        return
    _rl()
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    duong = {ten: os.path.join(_THU_MUC_PHONG, tep) for ten, tep in _PHONG.items()}
    for d in duong.values():
        if not os.path.isfile(d):
            raise ThieuThuVienPdf(d)
    for ten, d in duong.items():
        pdfmetrics.registerFont(TTFont(ten, d))
    addMapping("BeVietnamPro", 0, 0, "BeVietnamPro")
    addMapping("BeVietnamPro", 1, 0, "BeVietnamPro-Bold")
    addMapping("BeVietnamPro", 0, 1, "BeVietnamPro")
    addMapping("BeVietnamPro", 1, 1, "BeVietnamPro-Bold")
    _da_dang_ky = True


def san_sang():
    """Kiểm reportlab và phông có dùng được không; không thì ném `ThieuThuVienPdf` (gọi TRƯỚC khi tạo thư mục/tệp)."""
    _dang_ky_phong()


_KIEU: dict = {}


def _kieu(ten):
    """Kiểu đoạn dùng chung (tạo MỘT lần mỗi tên: bảng 800 phiếu có hàng chục nghìn ô)."""
    if ten not in _KIEU:
        _KIEU[ten] = _tao_kieu(ten)
    return _KIEU[ten]


def _tao_kieu(ten):
    from reportlab.lib.styles import ParagraphStyle
    mau = {
        "tieu_de": dict(fontName="BeVietnamPro-Bold", fontSize=15, leading=20, spaceAfter=8),
        "kv": dict(fontName="BeVietnamPro", fontSize=10, leading=14, spaceAfter=2),
        "o": dict(fontName="BeVietnamPro", fontSize=9, leading=12),
        "o_dau": dict(fontName="BeVietnamPro-Bold", fontSize=9, leading=12),
    }
    return ParagraphStyle(ten, **mau[ten])


def _p(chu, kieu):
    from reportlab.platypus import Paragraph
    return Paragraph(escape("" if chu is None else str(chu)), _kieu(kieu))


def tieu_de(chu):
    _dang_ky_phong()
    return _p(chu, "tieu_de")


def dong_khoa_gia_tri(khoa, gia_tri):
    _dang_ky_phong()
    from reportlab.platypus import Paragraph
    return Paragraph(f"<b>{escape(str(khoa))}:</b> {escape('' if gia_tri is None else str(gia_tri))}",
                     _kieu("kv"))


def ngat_trang():
    from reportlab.platypus import PageBreak
    return PageBreak()


def bang(tieu_de_cot, hang, do_rong=None, cot_dau_mm=None):
    """Bảng có tiêu đề cột lặp lại ở mỗi trang; `do_rong` (tuỳ chọn) là tỉ lệ các cột.
    `cot_dau_mm`: cột đầu (số thứ tự) rộng CỐ ĐỊNH tính bằng mm; các cột còn lại chia phần còn lại theo tỉ lệ
    (tỉ lệ cột đầu trong `do_rong` bị bỏ qua). Cố định để chữ "STT" và số nhiều chữ số không bị cắt dọc."""
    _dang_ky_phong()
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import Table, TableStyle
    rong = A4[0] - 36 * mm
    n = len(tieu_de_cot)
    ti_le = do_rong or [1] * n
    if cot_dau_mm is not None and n > 1:
        con_lai = rong - cot_dau_mm * mm
        cot = [cot_dau_mm * mm] + [con_lai * t / sum(ti_le[1:]) for t in ti_le[1:]]
    else:
        cot = [rong * t / sum(ti_le) for t in ti_le]
    du_lieu = [[_p(c, "o_dau") for c in tieu_de_cot]] + [[_p(o, "o") for o in h] for h in hang]
    b = Table(du_lieu, colWidths=cot, repeatRows=1)
    b.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8ECF0")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA5B1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return b


def _canvas_so_trang():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    class _C(canvas.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._trang = []

        def showPage(self):
            self._trang.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            n = len(self._trang)
            for tt in self._trang:
                self.__dict__.update(tt)
                self.setFont("BeVietnamPro", 8)
                self.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Trang {self._pageNumber}/{n}")
                super().showPage()
            super().save()
    return _C


def dem_trang(duong):
    """Số trang của một PDF do `dung_pdf` ghi (đọc `/Count` ở nút gốc cây trang; không cần thư viện đọc PDF)."""
    import re
    with open(duong, "rb") as f:
        return max(int(m) for m in re.findall(rb"/Count (\d+)", f.read()))


def dung_pdf(duong, khoi):
    """Ghi `khoi` ra `duong` (A4 dọc). Trả về đường dẫn THẬT đã ghi (có thể là "x (2).pdf")."""
    _dang_ky_phong()
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate
    thu_muc = os.path.dirname(os.path.abspath(duong))
    os.makedirs(thu_muc, exist_ok=True)
    fd, tam = tempfile.mkstemp(suffix=".pdf.tmp", dir=thu_muc)
    os.close(fd)
    try:
        doc = SimpleDocTemplate(tam, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                                topMargin=16 * mm, bottomMargin=18 * mm)
        doc.build(list(khoi), canvasmaker=_canvas_so_trang())
        dich = duong_dan_khong_de(os.path.abspath(duong))
        os.replace(tam, dich)
        return dich
    finally:
        if os.path.exists(tam):
            os.remove(tam)
