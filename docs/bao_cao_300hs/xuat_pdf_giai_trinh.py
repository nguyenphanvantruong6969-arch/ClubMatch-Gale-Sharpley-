# -*- coding: utf-8 -*-
"""Xuất hai PDF phiếu giải trình (chức năng "Lưu PDF" thật của phần mềm) cho bộ 300 HS — DỮ LIỆU MÔ PHỎNG.

    python docs/bao_cao_300hs/xuat_pdf_giai_trinh.py

  GIAI_TRINH_THANH_CONG.pdf       : các em đạt nguyện vọng 1 ở cả hai buổi.
  GIAI_TRINH_KHONG_THANH_CONG.pdf : các em không đạt nguyện vọng 1 ở ít nhất một buổi, đủ bốn loại lý do
                                    (huy chương, bốc thăm, dưới điểm sàn, thua điểm).
Chế độ Huy chương, seed 42 — giống mục 2 của báo cáo. Tệp là đúng bản phần mềm xuất, mỗi em một trang;
chỉ in đè dòng nhãn DỮ LIỆU MÔ PHỎNG ở mép trên.
"""
import base64
import collections
import os
import sys
import tempfile

D = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, GOC)

import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402
from pypdf import PdfReader, PdfWriter  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

SEED = 42
THANH_CONG = ["DC002", "DC005", "DC014", "DC035", "DC040", "DC044", "DC051", "DC053"]
KHONG_THANH_CONG = ["DC034", "DC008", "DC022", "DC001", "DC006", "DC013", "DC016", "DC010"]
BUOI = {"thu_3": "Thứ 3", "thu_6": "Thứ 6"}
MA_VI = {"MEDAL": "huy chương thấp hơn", "LOTTERY": "bốc thăm chưa trúng", "BELOW_PASS": "dưới điểm sàn",
         "SCORE": "thua điểm thi", "ACCEPTED": "được nhận"}

for ten, tep in (("BVP", "BeVietnamPro-Regular.ttf"), ("BVP-B", "BeVietnamPro-Bold.ttf")):
    pdfmetrics.registerFont(TTFont(ten, os.path.join(GOC, "assets", "fonts", tep)))
XANH = colors.HexColor("#1F4E3D")
S_TIEU = ParagraphStyle("t", fontName="BVP-B", fontSize=17, textColor=XANH, leading=22, spaceAfter=6)
S_THUONG = ParagraphStyle("n", fontName="BVP", fontSize=9.5, leading=13.5, spaceAfter=4)
S_O = ParagraphStyle("o", fontName="BVP", fontSize=8.5, leading=11)
S_O_DAM = ParagraphStyle("od", parent=S_O, fontName="BVP-B", textColor=colors.white)
S_LUU_Y = ParagraphStyle("l", parent=S_THUONG, textColor=colors.HexColor("#A03020"), fontName="BVP-B")


def moi_api():
    d = tempfile.mkdtemp()
    goc = os.path.join(d, "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Trường học", None)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc, ws_da_chon=True)
    api.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})
    with open(os.path.join(D, "SO_NHAP_300HS_DOI_CHE_DO.xlsx"), "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert api.run_pipeline(SEED)["ok"]
    return api


def dong_tom_tat(api, sid):
    """(mã, tên, kết quả từng buổi, lý do chính) cho bảng tóm tắt."""
    g = api.get_giai_trinh_hoc_sinh(sid)["data"]
    kq, ly = [], []
    for b in g["buoi"]:
        nv = next((x["hang"] for x in b["cac_lua_chon"] if x["duoc_xep"]), None)
        kq.append("%s: %s (%s)" % (BUOI[b["buoi"]], b.get("ten_clb") or "—",
                                   "NV%s" % nv if isinstance(nv, int) else "ngoài DS nguyện vọng"))
        bi_loai = [x["ma"] for x in b["cac_lua_chon"] if not x["duoc_xep"] and x["ma"] in MA_VI]
        ly += [MA_VI[m] for m in bi_loai]
    ten = api.get_match_results(sid)["data"]
    ten = (ten["rows"] if isinstance(ten, dict) else ten)[0]["name"]
    ly_do = ", ".join(sorted(set(ly), key=ly.index)) if ly else "đạt nguyện vọng 1 ở cả hai buổi"
    return sid, ten, "<br/>".join(kq), ly_do


def trang_bia(duong, tieu_de, mo_ta, dong):
    doc = SimpleDocTemplate(duong, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    bang = [[Paragraph(x, S_O_DAM) for x in ("Mã HS", "Họ tên", "Kết quả (CLB, nguyện vọng thứ mấy)",
                                             "Lý do ở các nguyện vọng không được nhận")]]
    bang += [[Paragraph(str(c), S_O) for c in d] for d in dong]
    t = Table(bang, colWidths=[1.7 * cm, 3.4 * cm, 6.0 * cm, 6.3 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), XANH),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF4F1")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7C4BE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    doc.build([Paragraph(tieu_de, S_TIEU), Paragraph(mo_ta, S_THUONG),
               Paragraph("DỮ LIỆU MÔ PHỎNG — tên học sinh do máy bịa, không phải học sinh thật.", S_LUU_Y),
               Spacer(1, 6), t, Spacer(1, 10),
               Paragraph("Các trang sau là phiếu giải trình do phần mềm xuất (thẻ Kết quả > Tra cứu một học sinh "
                         "> Lưu PDF), mỗi em một trang, theo đúng thứ tự trong bảng.", S_THUONG)])


def _nhan_mo_phong():
    """Trang trong suốt chỉ có dòng "DỮ LIỆU MÔ PHỎNG" ở mép trên, để in đè lên phiếu."""
    import io
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("BVP-B", 8)
    c.setFillColor(colors.HexColor("#A03020"))
    c.drawRightString(A4[0] - 1.5 * cm, A4[1] - 0.8 * cm, "DỮ LIỆU MÔ PHỎNG — không phải học sinh thật")
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def xuat(api, ma, ten_tep):
    """Đúng tệp phần mềm xuất (Lưu PDF), không thêm trang nào; chỉ in đè nhãn dữ liệu mô phỏng."""
    r = api.export_phieu_giai_trinh_pdf(os.path.join(tempfile.mkdtemp(), "phieu.pdf"), student_ids=ma)
    assert r["ok"], r
    w = PdfWriter()
    for pg in PdfReader(r["data"]["path"]).pages:
        pg.merge_page(_nhan_mo_phong())
        w.add_page(pg)
    ra = os.path.join(D, ten_tep)
    with open(ra, "wb") as f:
        w.write(f)
    print(ra, "· trang:", len(w.pages))


if __name__ == "__main__":
    api = moi_api()
    kq = api.get_match_results()["data"]
    kq = kq["rows"] if isinstance(kq, dict) else kq
    nv = collections.defaultdict(list)
    for r in kq:
        nv[r["student_id"]].append(r["rank_in_student_pref"])
    tc = [s for s, v in nv.items() if all(x == 1 for x in v)]
    xuat(api, [s for s in THANH_CONG if s in tc] or tc[:8], "GIAI_TRINH_THANH_CONG.pdf")
    xuat(api, KHONG_THANH_CONG, "GIAI_TRINH_KHONG_THANH_CONG.pdf")
