# -*- coding: utf-8 -*-
"""Xuất hai PDF phiếu giải trình (chức năng "Lưu PDF" thật của phần mềm) cho bộ 300 HS — DỮ LIỆU MÔ PHỎNG.

    python docs/bao_cao_300hs/xuat_pdf_giai_trinh.py

  GIAI_TRINH_THANH_CONG.pdf       : các em đạt nguyện vọng 1 ở cả hai buổi.
  GIAI_TRINH_KHONG_THANH_CONG.pdf : các em không đạt nguyện vọng 1 ở ít nhất một buổi, đủ bốn loại lý do
                                    (huy chương, bốc thăm, dưới điểm sàn, thua điểm).
Chế độ Huy chương, seed 42 — giống mục 2 của báo cáo. Mỗi tệp có một trang tóm tắt đứng đầu, sau đó là
phiếu của phần mềm, mỗi em một trang.
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


def xuat(api, ma, ten_tep, tieu_de, mo_ta):
    tam = tempfile.mkdtemp()
    bia = os.path.join(tam, "bia.pdf")
    trang_bia(bia, tieu_de, mo_ta, [dong_tom_tat(api, s) for s in ma])
    r = api.export_phieu_giai_trinh_pdf(os.path.join(tam, "phieu.pdf"), student_ids=ma)
    assert r["ok"], r
    phieu = r["data"].get("path")
    # Phần mềm xếp phiếu theo lớp rồi theo mã; ghép lại đúng thứ tự trong bảng tóm tắt.
    doc_phieu = PdfReader(phieu)
    vi_tri = {}
    for i, pg in enumerate(doc_phieu.pages):
        chu = pg.extract_text() or ""
        for s in ma:
            if s not in vi_tri and ("Mã: %s" % s in chu or s in chu.split("\n")[1:3]):
                vi_tri[s] = i
    w = PdfWriter()
    for pg in PdfReader(bia).pages:
        w.add_page(pg)
    thu_tu = [vi_tri[s] for s in ma if s in vi_tri]
    con_lai = [i for i in range(len(doc_phieu.pages)) if i not in thu_tu]
    for i in thu_tu + con_lai:
        w.add_page(doc_phieu.pages[i])
    ra = os.path.join(D, ten_tep)
    with open(ra, "wb") as f:
        w.write(f)
    print(ra, "· trang:", len(w.pages), "· khớp thứ tự:", len(thu_tu), "/", len(ma))
    return ra


if __name__ == "__main__":
    api = moi_api()
    kq = api.get_match_results()["data"]
    kq = kq["rows"] if isinstance(kq, dict) else kq
    nv = collections.defaultdict(list)
    for r in kq:
        nv[r["student_id"]].append(r["rank_in_student_pref"])
    tc = [s for s, v in nv.items() if all(x == 1 for x in v)]
    xuat(api, [s for s in THANH_CONG if s in tc] or tc[:8], "GIAI_TRINH_THANH_CONG.pdf",
         "Giải trình các ca phân bổ THÀNH CÔNG",
         "Chế độ Huy chương, mã bốc thăm %d, 300 học sinh × 2 buổi. Trong lần chạy này %d/300 em đạt "
         "nguyện vọng 1 ở cả hai buổi; dưới đây là %d em tiêu biểu (có em đỗ CLB Tuyển chọn nhờ điểm thi, có "
         "em vào CLB Giới hạn nhờ huy chương)." % (SEED, len(tc), len([s for s in THANH_CONG if s in tc])))
    xuat(api, KHONG_THANH_CONG, "GIAI_TRINH_KHONG_THANH_CONG.pdf",
         "Giải trình các ca phân bổ KHÔNG THÀNH CÔNG",
         "Chế độ Huy chương, mã bốc thăm %d. Trong lần chạy này %d/300 em không đạt nguyện vọng 1 ở ít nhất "
         "một buổi. Dưới đây là %d em tiêu biểu, đủ bốn loại lý do phần mềm đưa ra: huy chương thấp hơn, bốc "
         "thăm chưa trúng, dưới điểm sàn, thua điểm thi." % (SEED, 300 - len(tc), len(KHONG_THANH_CONG)))
