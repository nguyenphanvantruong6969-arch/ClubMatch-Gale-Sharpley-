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
LE_MM = 12                       # UX1F-L2: lề trái/phải/trên/dưới tối thiểu 12 mm (trước: 18/18/16/18)
_CO_O = 8.5                      # cỡ chữ trong bảng (>= 8,5 pt)
_LEADING_O = 10.5                # dòng cách trong ô bảng (cùng kiểu "o" của Paragraph)
_DEM_NGANG_PT = 4                # đệm trái/phải ô, dùng để tính độ rộng tối thiểu của cột


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
        "tieu_de": dict(fontName="BeVietnamPro-Bold", fontSize=13, leading=16, spaceBefore=3, spaceAfter=3),
        "kv": dict(fontName="BeVietnamPro", fontSize=9.5, leading=12, spaceAfter=1),
        "doan": dict(fontName="BeVietnamPro", fontSize=10.5, leading=14, spaceAfter=3),
        "o": dict(fontName="BeVietnamPro", fontSize=_CO_O, leading=_LEADING_O),
        "o_dau": dict(fontName="BeVietnamPro-Bold", fontSize=_CO_O, leading=_LEADING_O),
    }
    return ParagraphStyle(ten, **mau[ten])


_LOP_DOAN = None


def _lop_doan():
    """`Paragraph` nhớ kết quả `wrap` theo bề rộng (SF-A4, ST-A-008). Một ô bảng bị đo lại 2-3 lần (đo chiều cao
    bảng, đo lúc vẽ khung, đo lúc vẽ ô); mỗi lần là `breakLines` đo từng từ bằng `stringWidth` — chiếm phần lớn
    thời gian PDF cả trường (3 000 phiếu). `wrap` chỉ phụ thuộc bề rộng; `blPara` còn nguyên từ lần đo cuối nên
    chỉ dùng lại khi bề rộng GIỐNG lần đo cuối."""
    global _LOP_DOAN
    if _LOP_DOAN is None:
        from reportlab.platypus import Paragraph

        class _DoanNho(Paragraph):
            def wrap(self, availWidth, availHeight):
                c = self.__dict__.get("_wrap_nho")
                if c is not None and c[0] == availWidth:
                    # `split` có thể đã xoá `blPara` (rồi mới gọi lại `wrap` cùng bề rộng): dựng lại đủ trạng thái.
                    self.width, self.height = c[1]
                    self.blPara = c[2]
                    return c[1]
                kq = Paragraph.wrap(self, availWidth, availHeight)
                self._wrap_nho = (availWidth, kq, self.__dict__.get("blPara"))
                return kq

        _LOP_DOAN = _DoanNho
    return _LOP_DOAN


def _p(chu, kieu):
    return _lop_doan()(escape("" if chu is None else str(chu)), _kieu(kieu))


_CHUOI_NHO: dict = {}


def _o_chuoi(chu, kieu, rong):
    """Nội dung một ô bảng: chuỗi đã xuống dòng bằng `simpleSplit` (khoảng trắng gộp như `Paragraph`); từ nào dài
    hơn `rong` thì trả `Paragraph` (tự cắt từ dài)."""
    khoa = (chu, kieu, round(rong, 3))
    if khoa in _CHUOI_NHO:
        return _CHUOI_NHO[khoa]
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfbase.pdfmetrics import stringWidth
    ten_phong = "BeVietnamPro-Bold" if kieu == "o_dau" else "BeVietnamPro"
    van = " ".join(("" if chu is None else str(chu)).split())
    dong = simpleSplit(van, ten_phong, _CO_O, rong) if van else [""]
    if any(len(d.split()) == 1 and stringWidth(d, ten_phong, _CO_O) > rong for d in dong):
        kq = _p(chu, kieu)
    else:
        kq = "\n".join(dong)
    if len(_CHUOI_NHO) > 50000:
        _CHUOI_NHO.clear()
    _CHUOI_NHO[khoa] = kq
    return kq


def tieu_de(chu):
    _dang_ky_phong()
    return _p(chu, "tieu_de")


def doan(chu):
    """CB1: một đoạn chữ thường (10,5 pt), dùng cho văn bản bằng lời; ký tự đặc biệt được thoát như mọi khối khác."""
    _dang_ky_phong()
    return _p(chu, "doan")


def dong_khoa_gia_tri(khoa, gia_tri):
    _dang_ky_phong()
    return _lop_doan()(f"<b>{escape(str(khoa))}:</b> {escape('' if gia_tri is None else str(gia_tri))}",
                       _kieu("kv"))


def ngat_trang(khi_qua=None):
    """Ngắt trang. `khi_qua` (tuỳ chọn, SF-A5): hàm không đối số, `dung_pdf` gọi NGAY SAU khi ngắt trang này xong —
    dùng để báo tiến độ (mỗi học sinh một ngắt trang)."""
    from reportlab.platypus import PageBreak
    if khi_qua is None:
        return PageBreak()

    class _NgatTrangBao(PageBreak):
        pass
    kq = _NgatTrangBao()
    kq.khi_qua = khi_qua
    return kq


def _tai_lieu_bao_tien_do():
    from reportlab.platypus import SimpleDocTemplate

    class _Doc(SimpleDocTemplate):
        def afterFlowable(self, flowable):
            khi_qua = getattr(flowable, "khi_qua", None)
            if khi_qua is not None:
                khi_qua()
    return _Doc


def giu_cung(khoi):
    """Giữ các khối liền nhau trên MỘT trang (nếu vừa): tránh chú thích/chân phiếu bị đẩy một mình sang trang sau."""
    from reportlab.platypus import KeepTogether
    return KeepTogether(list(khoi))


def _rong_toi_thieu(tieu_de_cot):
    """Độ rộng (pt) mỗi cột tối thiểu để TỪ DÀI NHẤT của tiêu đề cột nằm gọn một dòng (chỉ được xuống dòng ở dấu cách)."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    return [max((stringWidth(w, "BeVietnamPro-Bold", _CO_O) for w in str(c or "").split()), default=0)
            + 2 * _DEM_NGANG_PT + 1 for c in tieu_de_cot]


def _chia_cot(tong, ti_le, toi_thieu):
    """Chia `tong` theo `ti_le`, nhưng không cột nào dưới `toi_thieu`; phần thiếu lấy từ các cột còn dư theo tỉ lệ."""
    cot = [tong * t / sum(ti_le) for t in ti_le]
    ghim = [False] * len(cot)
    for _ in range(len(cot)):
        thieu = [i for i, c in enumerate(cot) if not ghim[i] and c < toi_thieu[i]]
        if not thieu:
            break
        for i in thieu:
            cot[i], ghim[i] = toi_thieu[i], True
        con = tong - sum(cot[i] for i in range(len(cot)) if ghim[i])
        tl = sum(ti_le[i] for i in range(len(cot)) if not ghim[i])
        if tl <= 0:
            break
        for i in range(len(cot)):
            if not ghim[i]:
                cot[i] = con * ti_le[i] / tl
    return cot


def bang(tieu_de_cot, hang, do_rong=None, cot_dau_mm=None):
    """Bảng có tiêu đề cột lặp lại ở mỗi trang; `do_rong` (tuỳ chọn) là tỉ lệ các cột.
    `cot_dau_mm`: cột đầu (số thứ tự) rộng CỐ ĐỊNH tính bằng mm; các cột còn lại chia phần còn lại theo tỉ lệ
    (tỉ lệ cột đầu trong `do_rong` bị bỏ qua). Cố định để chữ "STT" và số nhiều chữ số không bị cắt dọc."""
    _dang_ky_phong()
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import Table, TableStyle
    rong = A4[0] - 2 * LE_MM * mm
    n = len(tieu_de_cot)
    ti_le = do_rong or [1] * n
    toi_thieu = _rong_toi_thieu(tieu_de_cot)
    if cot_dau_mm is not None and n > 1:
        con_lai = rong - cot_dau_mm * mm
        cot = [cot_dau_mm * mm] + _chia_cot(con_lai, ti_le[1:], toi_thieu[1:])
    else:
        cot = _chia_cot(rong, ti_le, toi_thieu)
    # SF-A4 (ST-A-008): ô là CHUỖI đã tự xuống dòng (cache theo chữ + bề rộng), không phải `Paragraph`: bảng phiếu
    # cả trường có hàng chục nghìn ô, mỗi `Paragraph` tốn dựng + đo + vẽ. Ô có từ dài hơn bề rộng cột vẫn dùng
    # `Paragraph` (nó tự cắt từ dài); chuỗi thì tràn ra ngoài ô.
    ngang = [c - 2 * _DEM_NGANG_PT for c in cot]      # trừ đệm trái + phải của ô (UX1F-L2: _DEM_NGANG_PT)
    du_lieu = ([[_o_chuoi(c, "o_dau", ngang[i]) for i, c in enumerate(tieu_de_cot)]]
               + [[_o_chuoi(o, "o", ngang[i]) for i, o in enumerate(h)] for h in hang])
    b = Table(du_lieu, colWidths=cot, repeatRows=1)
    b.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "BeVietnamPro-Bold"), ("FONTNAME", (0, 1), (-1, -1), "BeVietnamPro"),
        ("FONTSIZE", (0, 0), (-1, -1), _CO_O), ("LEADING", (0, 0), (-1, -1), _LEADING_O),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8ECF0")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA5B1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), _DEM_NGANG_PT), ("RIGHTPADDING", (0, 0), (-1, -1), _DEM_NGANG_PT),
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
                self.drawRightString(A4[0] - LE_MM * mm, 6 * mm, f"Trang {self._pageNumber}/{n}")
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
    thu_muc = os.path.dirname(os.path.abspath(duong))
    os.makedirs(thu_muc, exist_ok=True)
    fd, tam = tempfile.mkstemp(suffix=".pdf.tmp", dir=thu_muc)
    os.close(fd)
    from reportlab import rl_config
    a85_cu = rl_config.useA85
    try:
        doc = _tai_lieu_bao_tien_do()(tam, pagesize=A4, leftMargin=LE_MM * mm, rightMargin=LE_MM * mm,
                                      topMargin=LE_MM * mm, bottomMargin=LE_MM * mm)
        # SF-A5 (ST-A-008): luồng trang chỉ nén Flate, KHÔNG bọc thêm ASCII85 (mã hoá bằng Python thuần chiếm ~10 %
        # thời gian PDF cả trường và làm tệp to thêm ~25 %). Chữ và số trang không đổi; trả cấu hình lại ngay sau đó.
        rl_config.useA85 = 0
        try:
            doc.build(list(khoi), canvasmaker=_canvas_so_trang())
        finally:
            rl_config.useA85 = a85_cu
        dich = duong_dan_khong_de(os.path.abspath(duong))
        os.replace(tam, dich)
        return dich
    finally:
        if os.path.exists(tam):
            os.remove(tam)
