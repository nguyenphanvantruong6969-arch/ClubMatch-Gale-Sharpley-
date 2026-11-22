"""Dựng `BAO_CAO_MINH_CHUNG_TONG_HOP.docx`: MỘT báo cáo Word gộp ba kho mã, viết bằng lời đơn giản.

Chạy: python docs/giai_trinh/tao_bao_cao_tong_hop.py   (cần clone đủ lịch sử, python-docx, Node + Playwright để chụp sơ đồ)
Nguồn:
- Kho này (ClubMatch): đọc trực tiếp từ git qua `tao_lich_su.py` (số commit, ngày, tiêu đề).
- Hai kho còn lại (rbda-kiosk, DU-AN-PHAN-2GALESHARPLEY): số liệu và mã commit lấy từ hai báo cáo sự việc do chính hai kho đó lập
  (`LICH_SU_rbda-kiosk.docx`, `LICH_SU_DU-AN-PHAN-2GALESHARPLEY.docx`), chép vào các hằng số bên dưới. Kho này không đọc được
  commit của hai kho kia, nên chỗ nào dùng mã của chúng đều ghi rõ tên kho.
Chỉ nêu SỰ VIỆC. Không nhận xét mức đóng góp, không kết luận: phần đó do học sinh tự viết. Dữ liệu trong báo cáo là dữ liệu MÔ PHỎNG.
"""

import os
import re
import sys

import docx
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

THU_MUC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC)
import tao_lich_su as ls  # noqa: E402

DUONG_DOCX = os.path.join(THU_MUC, "BAO_CAO_MINH_CHUNG_TONG_HOP.docx")
XANH = RGBColor(0x1F, 0x3A, 0x5F)
XAM = RGBColor(0x55, 0x5B, 0x66)
K_RB, K_DA, K_CM = "rbda-kiosk", "DU-AN-PHAN-2GALESHARPLEY", "ClubMatch (kho này)"

# --------------------------------------------------------------------------- dữ liệu của hai kho kia (từ báo cáo của chúng)
RB = {"tong": 288, "main": 264, "dau": "26/08/2026", "cuoi": "05/10/2026", "claude": 276, "hs": 12, "pr": 5,
      "test_tep": 88, "test_ham": 1078}
DA = {"tong": 66, "dau": "08/10/2026", "cuoi": "15/10/2026", "claude": 64, "hs": 2, "pr": 2, "test_tep": 105, "test_ca": 1764}

# (kho, mã, ngày, việc) theo từng nhóm yêu cầu; ClubMatch lấy từ tao_lich_su.MINH_CHUNG.
THEM = {
    "A": [(K_RB, "26be1a4", "26/08/2026", "Commit gốc: nhập 32 tệp (5.527 dòng) gồm thuật toán lõi, giao diện, bộ test đầu tiên. Thân commit nói mã được mang từ nơi khác vào"),
          (K_RB, "da7f6b3", "29/08/2026", "Thêm tệp bàn giao BAN_GIAO.md (nơi ghi ai viết phần nào)"),
          (K_RB, "52981bb", "04/10/2026", "Gộp PR #7 (Sổ nhập CLB một tệp): đầu của nhánh chính, nguồn của bản chụp ở kho DU-AN"),
          (K_DA, "0e4d774", "08/10/2026", "Commit gốc: bản chụp rbda-kiosk (342 tệp). Thân commit ghi lịch sử cố ý không mang theo"),
          (K_DA, "c4c66e5", "14/10/2026", "Gộp PR #1 (không gian làm việc nhiều ngành)"),
          (K_DA, "3904496", "15/10/2026", "Gộp PR #2, commit cuối của kho")],
    "B": [(K_RB, "26be1a4", "26/08/2026", "Có sẵn các hàm lõi: xếp theo vòng, hàm chọn của CLB, bốc thăm, kiểm ổn định, kiểm dữ liệu"),
          (K_RB, "b5fe827", "01/09/2026", "Bốc thăm không phụ thuộc thứ tự nhập học sinh, kèm test"),
          (K_RB, "9253418", "05/09/2026", "Học sinh vào muộn được chèn số bốc thăm công bằng (thay vì luôn xếp cuối)"),
          (K_RB, "ecb7128", "11/09/2026", "Xếp theo nhiều buổi trong tuần"),
          (K_RB, "5ad9bfc", "27/09/2026", "Khoá hạt giống cùng số bốc thăm"),
          (K_DA, "d0c22ac", "14/10/2026", "Luật xếp theo không gian làm việc: nhóm cứng, chỉ theo nhóm, điểm theo người")],
    "C": [(K_RB, "ee1e7b1", "29/08/2026", "Đọc trực tiếp tệp Excel; cột nhóm dự trữ"),
          (K_RB, "06d83ac", "30/08/2026", "Cảnh báo khi Excel làm mất số 0 đầu mã học sinh"),
          (K_RB, "a69df53", "01/09/2026", "Kiểm điểm bất thường (ví dụ nhập 70 thay vì 7,0)"),
          (K_RB, "7e92d29", "27/09/2026", "Ràng buộc trong cơ sở dữ liệu: khoá ngoại và kiểm giá trị (chỉ tiêu, suất dự trữ)"),
          (K_RB, "ed84f75", "03/10/2026", "Sổ nhập CLB: một tệp Excel thay ba tệp"),
          (K_RB, "b9b99f8", "04/10/2026", "Nạp sổ theo kiểu tất cả hoặc không gì cả (lỗi giữa chừng thì quay về như cũ)"),
          (K_DA, "73ab1d4", "14/10/2026", "Trần số nguyện vọng và số bài thi lấy theo cấu hình của không gian làm việc")],
    "D": [(K_RB, "26be1a4", "26/08/2026", "Hết nguyện vọng thì không xếp (chưa có chỗ); nguyện vọng trỏ tới CLB không có thì bỏ qua"),
          (K_RB, "2f1d828", "28/09/2026", "Cảnh báo thiếu chỗ theo từng buổi thay vì cả tuần"),
          (K_RB, "15b3655", "27/09/2026", "Cảnh báo khi đổi CLB đẩy một học sinh quá 5 bài thi trong một buổi"),
          (K_RB, "a963bcc", "02/09/2026", "Đo riêng \"mất chỗ\" và \"đổi CLB\" qua 200 hạt giống (dữ liệu mô phỏng)")],
    "E": [(K_RB, "da7f6b3", "29/08/2026", "BAN_GIAO.md: tuyên bố học sinh tự viết gì, AI viết gì (lời trong tệp, git không kiểm được)"),
          (K_RB, "8916f00", "30/09/2026", "Nhật ký AI dạng Word (chỉ ở nhánh nhat-ky-ai-phan-mem, không vào nhánh chính)"),
          (K_DA, "7c4f423", "08/10/2026", "CLAUDE.md: quy tắc liêm chính (nhận xét và kết luận do học sinh viết)")],
    "F": [(K_RB, "04e02e9", "02/09/2026", "CO_CHE_THUAT_TOAN: mô tả năm lớp cơ chế"),
          (K_RB, "922a9ef", "16/09/2026", "Báo cáo \"phần mềm chạy thế nào\""),
          (K_RB, "72d1e44", "29/09/2026", "Sơ đồ năm lớp vẽ lại cho poster"),
          (K_DA, "7c4f423", "08/10/2026", "Gói kế hoạch tổng quát hoá: bối cảnh, sổ đăng ký 33 mục")],
    "G": [(K_RB, "d869976", "30/08/2026", "Bộ dữ liệu mô phỏng quy mô thật (hạt giống 2026, tên và mã do máy sinh)"),
          (K_RB, "47b8ec8", "30/08/2026", "Cơ sở dữ liệu demo 120 học sinh đã chấm điểm"),
          (K_RB, "92e43c5", "01/09/2026", "Bộ sạch 140 học sinh, nạp không cảnh báo"),
          (K_RB, "c171d3b", "12/09/2026", "Bộ \"giống trường thật\" 200 học sinh"),
          (K_DA, "7932934", "15/10/2026", "Hai bộ thử: trường 3 buổi (180 học sinh) và công ty Bình Minh (54 nhân viên, 8 dự án), ghi \"mọi tên đều bịa\"")],
    "H": [(K_RB, "47b8ec8", "30/08/2026", "Cơ sở dữ liệu demo để khỏi gõ 356 ô điểm"),
          (K_RB, "7ac73ec", "11/09/2026", "Bỏ ô chọn kiểu bốc thăm; chỉ giữ một thiết kế đã đo"),
          (K_DA, "ddec7be", "14/10/2026", "Lưu từ vựng và luật xếp riêng cho từng không gian làm việc"),
          (K_DA, "0007c7f", "15/10/2026", "Bộ demo một tệp .zip: nhập rồi bấm chạy")],
    "I": [(K_RB, "ac32b92", "06/09/2026", "Quy trình dựng tệp .exe tự động"),
          (K_RB, "c09a0c1", "27/09/2026", "Chạy test mỗi lần đẩy mã, ghim phiên bản thư viện, kiểm lỗi cú pháp"),
          (K_RB, "163b1c9", "12/09/2026", "Làm cho bộ test chạy được trên Windows"),
          (K_DA, "567ef3f", "14/10/2026", "Sửa lỗi CI Windows (rò kết nối cơ sở dữ liệu)")],
}
THU_TU_NHOM = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
TEN_NHOM = {"A": "Kho mã và lịch sử", "B": "Thuật toán ghép", "C": "Dữ liệu đầu vào và ràng buộc", "D": "Khi không đủ chỗ",
            "E": "Vai trò của AI", "F": "Sơ đồ và tài liệu thiết kế", "G": "Bộ dữ liệu thử ẩn danh",
            "H": "Demo chỉnh quy tắc phân bổ", "I": "Hướng dẫn chạy và kiểm tự động"}

# --------------------------------------------------------------------------- tiện ích Word


def mau_nen(o, ma: str) -> None:
    tc = o._tc.get_or_add_tcPr()
    for c in tc.findall(qn("w:shd")):
        tc.remove(c)
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), ma)
    tc.append(s)


def them_chu(doan, chu: str, co: float = None, mau=None) -> None:
    """Viết `chu` vào `doan`, hiểu **đậm** và `mã`."""
    for m in re.finditer(r"\*\*(.+?)\*\*|`([^`]+)`|([^*`]+|[*`])", chu):
        if m.group(1) is not None:
            r = doan.add_run(m.group(1))
            r.bold = True
        elif m.group(2) is not None:
            r = doan.add_run(m.group(2))
            r.font.name = "Consolas"
        else:
            r = doan.add_run(m.group(3))
        if co:
            r.font.size = Pt(co)
        if mau is not None:
            r.font.color.rgb = mau


class Bao:
    def __init__(self):
        self.d = docx.Document()
        s = self.d.sections[0]
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin = s.right_margin = Cm(2)
        s.top_margin = s.bottom_margin = Cm(2)
        st = self.d.styles["Normal"]
        st.font.name = "Calibri"
        st.font.size = Pt(11)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = 1.15
        for ten, co in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
            h = self.d.styles[ten]
            h.font.name = "Calibri"
            h.font.size = Pt(co)
            h.font.bold = True
            h.font.color.rgb = XANH
            h.paragraph_format.space_before = Pt(14 if ten != "Heading 1" else 6)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
        self.chan_trang(s)

    def chan_trang(self, s):
        p = s.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("Dữ liệu mô phỏng · Báo cáo minh chứng kỹ thuật · Trang ")
        r.font.size = Pt(9)
        r.font.color.rgb = XAM
        for loai, chu in (("begin", None), (None, "PAGE"), ("end", None)):
            r = p.add_run()
            r.font.size = Pt(9)
            r.font.color.rgb = XAM
            if loai:
                f = OxmlElement("w:fldChar")
                f.set(qn("w:fldCharType"), loai)
                r._r.append(f)
            else:
                t = OxmlElement("w:instrText")
                t.set(qn("xml:space"), "preserve")
                t.text = chu
                r._r.append(t)

    def h(self, chu, cap=1):
        return self.d.add_heading(chu, cap)

    def p(self, chu, co=None, mau=None, can=None, sau=None):
        dv = self.d.add_paragraph()
        them_chu(dv, chu, co, mau)
        if can:
            dv.alignment = can
        if sau is not None:
            dv.paragraph_format.space_after = Pt(sau)
        return dv

    def ds(self, muc, kieu="List Bullet"):
        for m in muc:
            dv = self.d.add_paragraph(style=kieu)
            dv.paragraph_format.space_after = Pt(3)
            them_chu(dv, m)

    def hop(self, tieu_de, dong, nen="EAF1FB", vien="1F3A5F"):
        b = self.d.add_table(rows=1, cols=1)
        b.alignment = WD_TABLE_ALIGNMENT.CENTER
        o = b.rows[0].cells[0]
        tc = o._tc.get_or_add_tcPr()
        vb = OxmlElement("w:tcBorders")
        for canh in ("top", "left", "bottom", "right"):
            e = OxmlElement("w:" + canh)
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "10" if canh == "left" else "4")
            e.set(qn("w:color"), vien)
            vb.append(e)
        tc.append(vb)
        mau_nen(o, nen)
        o.paragraphs[0].paragraph_format.space_after = Pt(3)
        them_chu(o.paragraphs[0], "**%s**" % tieu_de)
        for d in dong:
            dv = o.add_paragraph()
            dv.paragraph_format.space_after = Pt(3)
            them_chu(dv, d)
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)

    def bang(self, tieu_de, hang, rong, co=9.5, dam_cot0=False, nen_dau="1F3A5F"):
        b = self.d.add_table(rows=1, cols=len(tieu_de))
        b.style = "Table Grid"
        b.alignment = WD_TABLE_ALIGNMENT.CENTER
        b.autofit = False
        for i, t in enumerate(tieu_de):
            o = b.rows[0].cells[i]
            mau_nen(o, nen_dau)
            o.paragraphs[0].paragraph_format.space_after = Pt(0)
            r = o.paragraphs[0].add_run(t)
            r.bold = True
            r.font.size = Pt(co)
            r.font.color.rgb = RGBColor(255, 255, 255)
        tr = b.rows[0]._tr.get_or_add_trPr()
        e = OxmlElement("w:tblHeader")
        e.set(qn("w:val"), "true")
        tr.append(e)
        for n, h_ in enumerate(hang):
            ro = b.add_row()
            e = OxmlElement("w:cantSplit")
            ro._tr.get_or_add_trPr().append(e)
            for i, v in enumerate(h_):
                o = ro.cells[i]
                if n % 2 == 1:
                    mau_nen(o, "F4F6F9")
                o.paragraphs[0].paragraph_format.space_after = Pt(0)
                o.paragraphs[0].paragraph_format.line_spacing = 1.05
                them_chu(o.paragraphs[0], ("**%s**" % v) if (dam_cot0 and i == 0 and v) else str(v), co)
        for ro in b.rows:
            for o, cm in zip(ro.cells, rong):
                o.width = Cm(cm)
        for c, cm in zip(b.columns, rong):
            c.width = Cm(cm)
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)
        return b

    def anh(self, duong, rong_cm=None, cao_cm=None, chu_thich=None):
        dv = self.d.add_paragraph()
        dv.alignment = WD_ALIGN_PARAGRAPH.CENTER
        dv.add_run().add_picture(duong, width=Cm(rong_cm) if rong_cm else None, height=Cm(cao_cm) if cao_cm else None)
        if chu_thich:
            c = self.p(chu_thich, 9, XAM, WD_ALIGN_PARAGRAPH.CENTER)
            c.runs[0].italic = True

    def trang_moi(self):
        self.d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# --------------------------------------------------------------------------- hình: dòng thời gian


def svg_png(svg: str, png: str) -> bool:
    """Chụp SVG thành PNG rồi cắt đúng khung của hình (Playwright chụp cả vùng trắng thừa)."""
    if not ls.svg_ra_png(svg, png):
        return False
    with open(svg, encoding="utf-8") as f:
        dau = f.read(600)
    w, h = (int(re.search(r'%s="(\d+)"' % k, dau).group(1)) for k in ("width", "height"))
    from PIL import Image
    im = Image.open(png)
    im.crop((0, 0, min(im.width, int(w * 1.5)), min(im.height, int(h * 1.5)))).save(png)
    return True


def svg_thoi_gian(tq: dict) -> str:
    from datetime import date
    g0 = date(2026, 8, 20)
    W, H, X0, X1 = 1100, 450, 40, 1060

    def x(d, m, y=2026):
        return X0 + (date(y, m, d) - g0).days / 98 * (X1 - X0)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         '<text x="40" y="28" font-size="18" font-weight="700" fill="#0f172a">Ba kho mã trên một dòng thời gian</text>']
    for m, ten in ((9, "Tháng 9"), (10, "Tháng 10"), (11, "Tháng 11")):
        xx = x(1, m)
        o.append(f'<line x1="{xx}" y1="48" x2="{xx}" y2="360" stroke="#cbd5e1" stroke-dasharray="4 4"/>')
        o.append(f'<text x="{xx + 6}" y="62" font-size="13" fill="#475569">{ten}</text>')
    gx0, gx1 = x(15, 10), x(24, 10)
    o.append(f'<rect x="{gx0}" y="80" width="{gx1 - gx0}" height="150" fill="#f1f5f9" stroke="#94a3b8" stroke-dasharray="5 4"/>')
    barras = [("rbda-kiosk", (26, 8), (5, 10), "#bfdbfe", "26/08 đến 05/10 · %d commit" % RB["tong"], 90),
              ("DU-AN-PHAN-2GALESHARPLEY", (8, 10), (15, 10), "#bbf7d0", "08/10 đến 15/10 · %d commit" % DA["tong"], 140),
              ("ClubMatch (kho này)", (24, 10), (22, 11), "#ddd6fe", "24/10 đến 22/11 · %d commit" % tq["tong"], 190)]
    for ten, a, b, mau, nhan, yy in barras:
        xa, xb = x(a[0], a[1]), x(b[0], b[1])
        o.append(f'<rect x="{xa}" y="{yy}" width="{xb - xa}" height="30" rx="6" fill="{mau}" stroke="#334155"/>')
        o.append(f'<text x="{min(xa, 640)}" y="{yy - 6}" font-size="13" font-weight="700" fill="#0f172a">{ten}</text>')
        o.append(f'<text x="{xa + 8}" y="{yy + 20}" font-size="12" fill="#0f172a">{nhan if xb - xa > 200 else ""}</text>')
        if xb - xa <= 200:
            o.append(f'<text x="{xb + 8}" y="{yy + 20}" font-size="12" fill="#0f172a">{nhan}</text>')
    o.append(f'<text x="{(gx0 + gx1) / 2}" y="250" font-size="12" text-anchor="middle" fill="#475569">15/10 đến 24/10:</text>')
    o.append(f'<text x="{(gx0 + gx1) / 2}" y="266" font-size="12" text-anchor="middle" fill="#475569">chưa có commit nào</text>')
    o.append(f'<text x="{(gx0 + gx1) / 2}" y="282" font-size="12" text-anchor="middle" fill="#475569">trong ba kho</text>')
    moc = [((26, 8), "26/08 bản gốc", 0), ((12, 9), "12/09 xếp nhiều buổi", 1), ((27, 9), "27/09 rà soát thiết kế", 0),
           ((4, 10), "04/10 Sổ nhập một tệp", 1), ((14, 10), "14/10 nhiều ngành", 0), ((27, 10), "27/10 điểm quyết tâm", 1),
           ((9, 11), "09/11 cơ chế FA-DAA", 0), ((16, 11), "16/11 giải trình kết quả", 1), ((20, 11), "20/11 thẻ mục tiêu", 2)]
    for (d, m), ten, lech in moc:
        xx = x(d, m)
        yy = 318 + lech * 38
        o.append(f'<line x1="{xx}" y1="300" x2="{xx}" y2="{yy - 12}" stroke="#334155"/>')
        o.append(f'<circle cx="{xx}" cy="300" r="4" fill="#1f3a5f"/>')
        o.append(f'<text x="{xx}" y="{yy}" font-size="12" text-anchor="middle" fill="#0f172a">{ten}</text>')
    o.append('<text x="40" y="436" font-size="12" fill="#475569">Mốc chọn từ lịch sử commit. Dữ liệu trong cả ba kho là dữ liệu mô phỏng.</text>')
    o.append("</svg>")
    return "\n".join(o)


# --------------------------------------------------------------------------- nội dung


def dung(tq: dict) -> docx.Document:
    b = Bao()
    # ---- bìa
    for _ in range(4):
        b.p("")
    b.p("BÁO CÁO MINH CHỨNG KỸ THUẬT\nVÀ VAI TRÒ CỦA AI", 26, XANH, WD_ALIGN_PARAGRAPH.CENTER).runs[0].bold = True
    b.p("Phần mềm xếp học sinh vào câu lạc bộ (RB-DA)", 15, XAM, WD_ALIGN_PARAGRAPH.CENTER)
    b.p("Gộp lịch sử của ba kho mã, từ 26/08/2026 đến 22/11/2026", 12, XAM, WD_ALIGN_PARAGRAPH.CENTER)
    b.p("")
    b.hop("Đọc trước", ["**Mọi tên và điểm trong báo cáo là dữ liệu mô phỏng** do máy sinh, không phải học sinh hay khảo sát thật.",
                         "Báo cáo chỉ nêu sự việc đọc từ lịch sử commit và từ tệp trong kho. Nhận xét về mức đóng góp và mọi kết luận do học sinh thực hiện đề tài tự viết.",
                         "Mỗi mã commit (ví dụ `e08af78`) là một dấu vết kiểm được bằng lệnh `git show <mã>`."],
          nen="FFF7E0", vien="B45309")
    b.p("")
    b.p("Mục lục", 13, XANH).runs[0].bold = True
    b.ds(["1. Tóm tắt một trang", "2. Dự án làm gì", "3. Ba kho mã và dòng thời gian", "4. Sơ đồ luồng xử lý",
          "5. Dữ liệu đầu vào và ràng buộc", "6. Thuật toán ghép, nói bằng lời thường", "7. Khi không đủ chỗ",
          "8. AI nằm ở đâu và không nằm ở đâu", "9. Phần việc của từng thành viên", "10. Bộ dữ liệu thử ẩn danh",
          "11. Demo chỉnh một quy tắc và đối chiếu kết quả", "12. Cách chạy phần mềm", "13. Lịch sử thay đổi theo giai đoạn",
          "14. Điều chưa đầy đủ và việc cần Truong xác nhận", "Phụ lục A. Minh chứng theo từng yêu cầu", "Phụ lục B. Cách tự kiểm lại"], "List Paragraph")
    b.trang_moi()

    # ---- 1
    tong_cm = RB["tong"] + DA["tong"] + tq["tong"]
    hs_tk = RB["hs"] + DA["hs"] + sum(n for t, n in tq["tac_gia"].items() if "Tài khoản" in t)
    ai_tk = RB["claude"] + DA["claude"] + sum(n for t, n in tq["tac_gia"].items() if "Claude" in t)
    b.h("1. Tóm tắt một trang")
    b.p("Hội đồng yêu cầu: cung cấp mã nguồn và hướng dẫn chạy; giải thích dữ liệu đầu vào, ràng buộc, thuật toán ghép, cách xử lý khi không đủ chỗ "
        "và phần việc từng thành viên; nói rõ bộ phận nào dùng AI. Bảng dưới trả lời ngắn từng ý và chỉ chỗ xem.")
    b.bang(["Hội đồng hỏi", "Trả lời ngắn", "Xem"], [
        ("Mã nguồn và hướng dẫn chạy", "Mã nằm trong ba kho; kho này là bản mới nhất, chạy bằng một lệnh `python main.py`.", "Mục 3, 12"),
        ("Dữ liệu đầu vào, ràng buộc", "Một tệp Excel (Sổ nhập CLB). Phần mềm kiểm từng dòng; sai thì dừng và nói rõ, không nạp một nửa.", "Mục 5"),
        ("Thuật toán ghép", "Học sinh lần lượt xin vào CLB theo thứ tự yêu thích; CLB giữ tạm người xếp trên. Có suất dự trữ, bốc thăm một lần và kiểm lại kết quả.", "Mục 6"),
        ("Khi không đủ chỗ", "CLB đầy thì em xếp sau thử nguyện vọng kế tiếp; hết nguyện vọng thì ghi \"chưa có chỗ\", không xếp bừa.", "Mục 7"),
        ("Bộ phận nào dùng AI", "Phần mềm khi chạy **không có AI**. AI (Claude Code) chỉ giúp lúc viết mã và tài liệu, theo yêu cầu và duyệt của Truong.", "Mục 8"),
        ("Phần việc từng thành viên", "Git không cho biết ai gõ phần nào. Bảng phân công để học sinh tự điền.", "Mục 9"),
        ("Kho mã và lịch sử thay đổi", "%s commit trong ba kho, từ 26/08/2026; bảng giai đoạn và mã commit." % format(tong_cm, ",").replace(",", "."), "Mục 3, 13, Phụ lục A"),
        ("Sơ đồ luồng xử lý", "Một sơ đồ các bước và điểm quyết định, gồm nhánh không đủ chỗ.", "Mục 4"),
        ("Bộ dữ liệu thử ẩn danh", "Mọi bộ do máy sinh, tên bịa, mã dạng HS001; không có học sinh thật.", "Mục 10"),
        ("Demo chỉnh quy tắc", "Đổi một quy tắc ở chế độ chạy thử, so với kết quả chính thức, rồi áp dụng hoặc bỏ.", "Mục 11"),
    ], [4.2, 10.6, 2.2], dam_cot0=True)
    b.hop("Ba điều nói thẳng", [
        "**1. Phần mềm khi chạy không dùng AI.** Kết quả do một thuật toán cố định quyết định; cùng dữ liệu và cùng hạt giống thì ra đúng kết quả cũ.",
        "**2. Trong lịch sử commit, hầu hết commit mang tên công cụ AI** (%s trên %s). Các commit của tài khoản học sinh (%d) đều là lần gộp mã, hoặc có công cụ AI cùng ghi tên. Git không chứng minh được ai gõ phần nào." % (
            format(ai_tk, ",").replace(",", "."), format(tong_cm, ",").replace(",", "."), hs_tk),
        "**3. Lịch sử trước 26/08/2026 không có trong ba kho.** Commit đầu tiên của bản gốc nói mã được mang từ nơi khác vào."],
          nen="EAF1FB")
    b.trang_moi()

    # ---- 2
    b.h("2. Dự án làm gì")
    b.p("Một trường có khoảng 800 học sinh và khoảng 20 câu lạc bộ (CLB). Mỗi em chọn nhiều CLB theo thứ tự yêu thích, mỗi CLB chỉ có số chỗ giới hạn. "
        "Phần mềm chạy ngoại tuyến trên máy Windows của trường, nhận một tệp Excel, rồi xếp mỗi em vào nhiều nhất một CLB theo cách công bằng và giải thích được.")
    b.p("Tên cách xếp là **RB-DA**: học sinh đề xuất theo thứ tự yêu thích (thuật toán Gale–Shapley), CLB có thể dành riêng một số suất, "
        "ai ngang điểm thì bốc thăm một lần duy nhất.")
    b.h("Vài từ dùng trong báo cáo", 2)
    b.bang(["Từ", "Nghĩa đơn giản"], [
        ("Nguyện vọng", "Danh sách CLB một học sinh muốn vào, theo thứ tự."),
        ("Chỉ tiêu", "Số chỗ của một CLB."),
        ("Suất dự trữ", "Một phần chỗ để dành cho một nhóm học sinh. Nếu không đủ người thuộc nhóm thì chỗ thừa được trả về cho mọi người."),
        ("Bốc thăm một lần", "Mỗi học sinh có một số may rủi, dùng chung cho mọi CLB. Chỉ dùng để phân xử khi bằng nhau về mọi điều kiện khác."),
        ("Ổn định", "Sau khi xếp, không có cặp (học sinh, CLB) nào cùng thích nhau hơn kết quả hiện tại."),
        ("Hạt giống (seed)", "Con số để bốc thăm có thể làm lại đúng như cũ."),
        ("Commit", "Một lần lưu thay đổi mã, có ngày và lời mô tả. Lịch sử commit là bằng chứng ai thay đổi gì và khi nào."),
    ], [4.0, 13.0], dam_cot0=True)

    # ---- 3
    b.h("3. Ba kho mã và dòng thời gian")
    b.p("Dự án nằm ở ba kho mã nối tiếp nhau. Kho sau lấy một bản chụp của kho trước rồi làm tiếp, nên mã lõi có mặt từ commit đầu của mỗi kho.")
    b.bang(["Kho", "Thời gian", "Số commit", "Nội dung chính"], [
        (K_RB, "%s đến %s" % (RB["dau"], RB["cuoi"]), "%d (%d trên nhánh chính)" % (RB["tong"], RB["main"]),
         "Bản gốc, sửa lỗi Windows, nhập dữ liệu, bốc thăm tái lập, xếp nhiều buổi, Sổ nhập một tệp, rà soát thiết kế"),
        (K_DA, "%s đến %s" % (DA["dau"], DA["cuoi"]), str(DA["tong"]),
         "Bản chụp của kho trên, gói kế hoạch tổng quát hoá cho 12 ngành, không gian làm việc nhiều ngành, bộ thử công ty"),
        (K_CM, "24/10/2026 đến 22/11/2026", "%d" % tq["tong"],
         "Điểm quyết tâm, lớp học sinh, bộ công cụ Microsoft Forms, cơ chế FA-DAA, giải trình kết quả, thử tiêu chí, tài khoản, nhật ký thao tác, giao diện, PDF"),
    ], [4.0, 3.6, 2.6, 6.8], dam_cot0=True)
    svg = os.path.join(THU_MUC, "_tg_tam.svg")
    with open(svg, "w", encoding="utf-8") as f:
        f.write(svg_thoi_gian(tq))
    png = os.path.join(THU_MUC, "_tg_tam.png")
    ok = svg_png(svg, png)
    os.remove(svg)
    if ok:
        b.anh(png, rong_cm=17, chu_thich="Hình 1. Ba kho mã trên một dòng thời gian")
        os.remove(png)
    b.p("**Tổng cộng khoảng %s commit** (không trùng: mỗi bản chụp nhập hàng loạt chỉ tính một commit). Hai kho đầu cộng lại %d commit." % (
        format(tong_cm, ",").replace(",", "."), RB["tong"] + DA["tong"]))
    b.ds(["**Hai bản chụp nhập hàng loạt:** `0e4d774` (kho DU-AN, 342 tệp) và `e08af78` (kho này, 392 tệp). Vì thế với mọi tệp lõi, \"commit đầu tiên\" ở hai kho này đều là bản chụp.",
          "**Kho thứ tư chưa đọc:** tên `RB-STUFF-AFTER-UP` xuất hiện trong lời mô tả commit gộp của kho DU-AN và trong commit đầu của kho này (\"chuyển từ RB-STUFF-AFTER-UP sang TESTING-DEV\"). Em chưa có báo cáo về kho đó (xem mục 14).",
          "Kho này từng mang tên TESTING-DEV; lời mô tả các commit gộp cũ còn ghi tên đó."])

    # ---- 4
    b.trang_moi()
    b.h("4. Sơ đồ luồng xử lý")
    b.p("Sơ đồ dưới là một lần bấm \"Chạy xếp\". Hình thoi là chỗ phần mềm kiểm tra; nếu không đạt thì dừng và dữ liệu giữ nguyên như trước khi chạy.")
    png = os.path.join(THU_MUC, "_xl_tam.png")
    if svg_png(ls.DUONG_SVG_XU_LY, png):
        b.anh(png, cao_cm=21.5)
        os.remove(png)
    b.p("Hình 2. Luồng xử lý một lần chạy xếp (tên hàm trong ngoặc là tên thật trong mã).", 9, XAM, WD_ALIGN_PARAGRAPH.CENTER)
    b.h("Đọc sơ đồ trong sáu câu", 2)
    b.ds(["**Nạp dữ liệu:** phần mềm đọc tệp Excel; dòng nào sai thì báo kèm số dòng và không nạp gì.",
          "**Chuẩn bị:** sao lưu cơ sở dữ liệu, kiểm dữ liệu có đủ và khớp nhau không.",
          "**Bốc thăm:** mỗi học sinh một số, bốc lần đầu rồi khoá, các lần sau dùng lại đúng số cũ.",
          "**Xếp theo vòng:** mỗi vòng, em chưa có chỗ xin vào CLB kế tiếp trong danh sách của mình; CLB giữ tạm người xếp trên, từ chối người còn lại.",
          "**Kiểm lại:** phần mềm tự kiểm xem có cặp học sinh và CLB nào cùng thích nhau hơn kết quả không; có thì dừng.",
          "**Ghi kết quả:** ghi trong một lần duy nhất (lỗi thì quay về như cũ), rồi xuất Excel và CSV; mỗi lần chạy thêm một dòng vào lịch sử chạy, không sửa, không xoá."])
    b.p("Sơ đồ thứ hai, thể hiện đường đi của dữ liệu qua 12 bước, nằm ở Phụ lục B.", 10, XAM)

    # ---- 5
    b.trang_moi()
    b.h("5. Dữ liệu đầu vào và ràng buộc")
    b.p("Phần mềm nhận **một tệp Excel** gọi là Sổ nhập CLB, có hai trang:")
    b.bang(["Trang", "Mỗi dòng là", "Các cột chính"], [
        ("1. CLB", "Một câu lạc bộ", "Tên, mã, buổi sinh hoạt, chỉ tiêu, suất ưu tiên (dự trữ), nhóm được dùng suất đó"),
        ("2. Học sinh", "Một học sinh", "Mã, họ tên, nguyện vọng 1 đến 5 (chọn từ danh sách), điểm thi vào từng CLB (để trống nếu CLB không thi), nhóm ưu tiên")],
        [3.0, 3.4, 10.6], dam_cot0=True)
    b.h("Phần mềm kiểm gì và làm gì khi sai", 2)
    b.p("Nguyên tắc: **dừng và nói rõ, không đoán, không tự sửa.** Lỗi lúc nạp thì không nạp gì; lỗi lúc chạy thì lần chạy dừng, dữ liệu không đổi.")
    b.bang(["Phần mềm kiểm", "Nếu sai", "Từ commit (kho)"], [
        ("Chỉ tiêu phải lớn hơn 0; suất dự trữ không lớn hơn chỉ tiêu", "Báo lỗi kèm tên CLB và số dòng", "`7e92d29` (rbda-kiosk), `e08af78` (kho này)"),
        ("Mã học sinh và mã CLB không trùng; nguyện vọng không lặp CLB", "Báo lỗi, không nạp", "`ed84f75` (rbda-kiosk, Sổ nhập)"),
        ("Học sinh có nguyện vọng phải có trong danh sách; CLB phải tồn tại", "Dừng lần chạy, nêu rõ mã nào", "`26be1a4` (rbda-kiosk)"),
        ("Điểm bất thường (ví dụ 70 thay vì 7,0), mất số 0 đầu mã do Excel", "Cảnh báo", "`a69df53`, `06d83ac` (rbda-kiosk)"),
        ("Công thức độc hại trong ô Excel hoặc CSV", "Chặn", "`dac7946` (rbda-kiosk)"),
        ("Một học sinh bị đẩy quá 5 bài thi trong một buổi khi đổi CLB", "Cảnh báo", "`15b3655` (rbda-kiosk)"),
        ("Nạp sổ theo kiểu tất cả hoặc không gì cả", "Lỗi giữa chừng thì quay về như cũ", "`b9b99f8` (rbda-kiosk)"),
        ("CLB có người đăng ký thi nhưng chưa chấm điểm ai", "Chặn hoặc cảnh báo trước khi chạy", "`09af633` (rbda-kiosk), `9934af2` (kho này)"),
    ], [7.2, 4.8, 5.0])
    b.p("Chi tiết từng cột, từng thông báo lỗi nguyên văn nằm ở `docs/giai_trinh/DU_LIEU_DAU_VAO.md`. "
        "Ví dụ thật: sổ lỗi cố ý `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx` làm phần mềm báo đúng 5 lỗi và không nạp gì.")
    b.hop("Một điều cố ý không làm", ["Thứ hạng nguyện vọng của học sinh và kết cục của buổi trước **không** được đưa vào thứ tự ưu tiên của CLB. "
                                       "Nếu CLB biết em xếp mình thứ mấy rồi ưu tiên theo đó, học sinh sẽ có lý do khai không thật."])

    # ---- 6
    b.h("6. Thuật toán ghép, nói bằng lời thường")
    b.p("Mô tả kỹ thuật đầy đủ: `docs/CO_CHE_THUAT_TOAN.md`. Ở đây là năm ý, mỗi ý một câu chuyện nhỏ.")
    b.bang(["#", "Ý chính", "Hiểu đơn giản"], [
        ("1", "Học sinh đề xuất, CLB giữ tạm", "Giống như xin việc: em nộp đơn vào lựa chọn số 1. CLB giữ lại những em tốt nhất đến mức đủ chỗ, từ chối phần còn lại. Em bị từ chối nộp đơn vào lựa chọn kế tiếp. CLB chỉ chốt khi không còn ai nộp thêm, nên một em đến sau vẫn có thể đẩy em kém hơn ra."),
        ("2", "Suất dự trữ mềm", "CLB có thể để dành một vài chỗ cho một nhóm. Chỗ đó không khoá cứng: nếu không đủ người trong nhóm thì chỗ thừa được trả về cho tất cả."),
        ("3", "Bốc thăm một lần", "Nhiều em ngang nhau thì cần cách phân xử công bằng và làm lại được. Mỗi em có một số, dùng cho mọi CLB, bốc một lần rồi khoá. Em đến muộn được chèn vào vị trí ngẫu nhiên, thứ tự của các em cũ giữ nguyên."),
        ("4", "Hai tầng ưu tiên", "CLB có thi tuyển: em có điểm thi xếp trước, điểm cao hơn đứng trên, bằng điểm thì xét số bốc thăm. Em đăng ký nhưng không thi chỉ xét số bốc thăm. Tầng có điểm luôn đứng trước tầng không điểm."),
        ("5", "Tự kiểm lại kết quả", "Sau khi xếp, phần mềm thử xem có em nào và CLB nào cùng thích nhau hơn kết quả hiện tại không. Có thì lần chạy dừng, không ghi kết quả."),
    ], [0.8, 4.2, 12.0])
    b.h("Một ví dụ nhỏ (tự dựng để minh hoạ, không phải dữ liệu thật)", 2)
    b.p("CLB Robot có 2 chỗ. Bốn em đều chọn Robot đầu tiên và đã thi: An 9 điểm, Bình 8 điểm, Chi 7 điểm, Dũng 7 điểm.")
    b.ds(["Vòng 1: bốn em cùng nộp đơn vào Robot. Robot giữ An và Bình (điểm cao nhất), từ chối Chi và Dũng.",
          "Chi và Dũng chuyển sang lựa chọn số 2 của mình ở vòng sau, và cứ thế đến khi có chỗ hoặc hết danh sách.",
          "Nếu hai em bằng điểm tranh nhau chỗ cuối cùng, số bốc thăm đã khoá quyết định, và lần chạy lại vẫn ra đúng như vậy."])
    b.hop("Thuật toán tối ưu không phải là AI", [
        "Cách xếp ở đây là một **quy trình có các bước cố định**: cùng dữ liệu và cùng hạt giống thì luôn ra cùng kết quả, kiểm được từng dòng. "
        "Không có bước nào \"học\" từ dữ liệu, không có mô hình huấn luyện, không gọi dịch vụ AI nào. Lệnh kiểm có sẵn `kiem_nhanh.py` so từng dòng kết quả của 3 bộ dữ liệu với 20 hạt giống và báo \"trùng khít\"."])

    # ---- 7
    b.h("7. Khi không đủ chỗ")
    b.p("Bảng dưới nói phần mềm làm gì ở từng tình huống, và commit nào đưa hành vi đó vào.")
    b.bang(["Tình huống", "Phần mềm làm gì", "Từ commit (kho)"], [
        ("CLB nhận nhiều đơn hơn chỉ tiêu", "Giữ đúng chỉ tiêu theo thứ tự ưu tiên của CLB; em còn lại bị từ chối và được ghi vào nhật ký từ chối", "`26be1a4` (rbda-kiosk), có sẵn từ đầu"),
        ("Em bị từ chối", "Vòng sau nộp đơn vào nguyện vọng kế tiếp", "`26be1a4` (rbda-kiosk)"),
        ("Hết nguyện vọng mà vẫn bị từ chối", "Ghi **\"chưa có chỗ\"**, không xếp bừa vào CLB khác. Có trang riêng \"Chưa có chỗ\" trong tệp Excel kết quả", "`26be1a4` (rbda-kiosk)"),
        ("Nguyện vọng trỏ tới CLB không tồn tại", "Bỏ qua, coi như bị từ chối, thử nguyện vọng kế tiếp", "`26be1a4` (rbda-kiosk)"),
        ("Dữ liệu cho thấy trước là sẽ thiếu chỗ", "Cảnh báo thiếu chỗ theo từng buổi trước khi chạy", "`2f1d828`, `e541a62` (rbda-kiosk)"),
        ("Học sinh vào muộn sau khi đã bốc thăm", "Chèn số bốc thăm ngẫu nhiên, giữ thứ tự cũ của các em khác", "`9253418` (rbda-kiosk)"),
        ("Vòng lặp chạm trần số vòng cho phép", "Báo lỗi, không trả kết quả dở dang", "`0e4d774` (DU-AN)"),
        ("Chế độ FA-DAA: CLB thiếu thành viên tối thiểu", "Đóng CLB đó, các em chuyển sang lựa chọn khác", "`1037920` (kho này)"),
        ("Chế độ FA-DAA: có suất được nhả ra", "Điểm danh 3 buổi đầu, vắng không phép 2 trên 3 thì nhả suất; mời người trong danh sách chờ", "`bb49d11`, `628cfb2` (kho này)"),
        ("Chế độ FA-DAA: em chưa có CLB mong muốn", "Vòng 2: chọn trong các chỗ còn trống; chỗ \"lùi\" được lưu riêng và hiển thị riêng", "`e76bf48`, `f2e7702` (kho này)"),
        ("Sau xếp: nên tăng chỉ tiêu CLB nào", "Gợi ý chỉ tiêu kỳ sau từ nhu cầu thật", "`18fb8d7` (kho này)"),
    ], [4.6, 8.0, 4.4])
    b.p("**Lưu ý trung thực:** ở hai kho đầu không có danh sách chờ (đã tìm trong mã); danh sách chờ, vòng 2 và nhả suất chỉ có ở kho này, trong chế độ FA-DAA.")
    b.h("Ví dụ thật từ ca mẫu", 2)
    b.p("Bộ dữ liệu mô phỏng 120 học sinh, 10 CLB, hạt giống 42 (`docs/giai_trinh/CA_MAU.md`). Phần mềm giải thích bằng câu cho từng em:")
    b.bang(["Em", "Kết quả", "Phần mềm giải thích"], [
        ("HS001", "Chưa có chỗ", "Hai CLB em chọn (Tin học, Mỹ thuật) đều đã đủ chỗ; hai CLB dành một số chỗ cho nhóm được giữ chỗ nên em chưa vào được"),
        ("HS002", "CLB Âm nhạc (nguyện vọng 4)", "Ba CLB đầu đã đủ chỗ với các em điểm cao hơn. Ví dụ Bóng đá có điểm chuẩn 5,9 còn em được 5,8"),
        ("HS003", "CLB Tin học (nguyện vọng 1)", "Điểm 6,7, điểm chuẩn 6,2; nhận được chỗ ngay"),
    ], [2.0, 4.6, 10.4], dam_cot0=True)

    # ---- 8
    b.trang_moi()
    b.h("8. AI nằm ở đâu và không nằm ở đâu")
    b.h("8.1. Phần mềm khi chạy: không có AI", 2)
    b.ds(["Danh sách thư viện (`requirements.txt`) chỉ có thư viện tạo cửa sổ và đọc Excel; không có thư viện học máy nào.",
          "Tệp thuật toán `rbda_priority_pipeline.py` chỉ dùng thư viện chuẩn của Python. Ở kho rbda-kiosk, tìm trong toàn bộ mã không thấy `anthropic`, `openai`, `sklearn`, `torch`, `tensorflow`, `transformers`, `langchain`.",
          "Phần mềm chạy ngoại tuyến, không gọi dịch vụ nào qua mạng.",
          "Cùng dữ liệu và cùng hạt giống thì ra cùng kết quả; có lệnh kiểm tự động (`kiem_nhanh.py`)."])
    b.h("8.2. Lúc làm phần mềm: công cụ AI giúp", 2)
    b.bang(["Việc", "Ai làm (theo ghi chép trong kho)", "Kiểm được bằng git?"], [
        ("Thuật toán xếp cốt lõi, giao diện đầu tiên, tệp đóng gói (bản gốc 26/08/2026)", "Học sinh tự viết (BAN_GIAO.md, mục 3)", "Không: commit gốc ghi tên công cụ AI và nói mã được mang từ nơi khác vào"),
        ("Sửa lỗi, bộ kiểm thử tự động, tính năng mới (không gian nhiều ngành, điểm quyết tâm, lớp, FA-DAA, tài khoản, nhật ký thao tác)", "Công cụ AI (Claude Code) theo yêu cầu và duyệt của Truong", "Có: tên tác giả commit và dòng Co-Authored-By"),
        ("Lập kế hoạch từng đợt, điều phối", "Mô hình Opus lập kế hoạch; mô hình Sonnet viết mã; Truong duyệt", "Có một phần: dòng Co-Authored-By ghi tên mô hình, tệp kế hoạch có trong kho"),
        ("Đặt yêu cầu, duyệt kế hoạch, chọn phương án, cho phép hay từ chối ngoại lệ, quyết định gộp mã", "Truong", "Một phần: %d commit mang tài khoản học sinh (phần lớn là gộp mã); các quyết định được ghi trong CHANGELOG và tệp kế hoạch (ví dụ `4a59947`)" % hs_tk),
    ], [6.4, 5.4, 5.2])
    b.p("Hai nơi ghi việc dùng AI: nhật ký AI trong kho này (`docs/nhat_ky_ai/`, bản đọc nhanh và bản chi tiết) và `CHANGELOG.md` (mỗi thay đổi một mục: mã, tệp, test mới).")
    b.h("8.3. Những gì git ghi lại về tác giả", 2)
    b.bang(["Kho", "Commit mang tên công cụ AI", "Commit mang tài khoản học sinh", "Ghi chú"], [
        (K_RB, "%d" % RB["claude"], "%d" % RB["hs"], "5 commit gộp PR trên nhánh chính; 7 commit ngày 05/10 có công cụ AI cùng ghi tên, chưa vào nhánh chính"),
        (K_DA, "%d" % DA["claude"], "%d" % DA["hs"], "Cả 2 là commit gộp PR"),
        (K_CM, "%d" % sum(n for t, n in tq["tac_gia"].items() if "Claude" in t),
         "%d" % sum(n for t, n in tq["tac_gia"].items() if "Tài khoản" in t), "Cả hai nhóm đều ghi tên theo cấu hình của máy; commit của học sinh đều là gộp PR"),
    ], [4.2, 3.6, 3.6, 5.6], dam_cot0=True)
    b.p("Con số này chỉ nói **tên ghi trong git**. Nó không cho biết ai quyết định nội dung, ai đọc và sửa; vì vậy báo cáo không dùng nó để kết luận về đóng góp.")
    b.h("8.4. Quy tắc áp dụng với AI", 2)
    b.ds(["Mọi số liệu kiểm thử là số mô phỏng, không trình bày như khảo sát thật.",
          "Nhận xét, diễn giải và kết luận trong báo cáo đề tài do học sinh tự viết (ghi trong `CLAUDE.md`, mục *Academic integrity*).",
          "Mỗi lần AI giúp đáng kể được ghi vào nhật ký AI của đề tài."])

    # ---- 9
    b.h("9. Phần việc của từng thành viên")
    b.p("Git không cho biết thành viên nào làm phần nào: các kho chỉ có hai tên tác giả (công cụ AI và tài khoản học sinh), và không có tệp phân công. "
        "Vì vậy bảng dưới để **học sinh thực hiện đề tài tự điền**; báo cáo này không điền hộ.")
    b.bang(["Thành viên", "Họ tên", "Phần mã nguồn", "Phần nghiên cứu và viết", "Bằng chứng (mã commit, tệp, biên bản)"],
           [("Thành viên 1", "", "", "", ""), ("Thành viên 2", "", "", "", "")], [2.6, 2.8, 3.6, 3.8, 4.2], dam_cot0=True)
    b.p("Gợi ý bằng chứng: mã commit trong Phụ lục A, mục tương ứng của `CHANGELOG.md`, quyết định ghi trong `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md` (mục 4).", 10, XAM)

    # ---- 10
    b.h("10. Bộ dữ liệu thử ẩn danh")
    b.p("**Không có dữ liệu học sinh thật.** Tên được ghép ngẫu nhiên từ bảng họ, chữ đệm, tên; mã dạng HS001; điểm do máy sinh với hạt giống cố định. "
        "Các tệp ghi rõ \"mô phỏng\" hoặc \"mọi tên đều bịa\".")
    b.bang(["Bộ dữ liệu", "Quy mô", "Dùng để", "Kho / commit"], [
        ("Bộ 120 học sinh (hạt giống 2026) và cơ sở dữ liệu demo đã chấm điểm", "120 học sinh, 10 CLB", "Demo và đo", "`d869976`, `47b8ec8` (rbda-kiosk)"),
        ("Bộ sạch (nạp không cảnh báo)", "140 học sinh", "Kiểm đường nhập", "`92e43c5` (rbda-kiosk)"),
        ("Bộ \"giống trường thật\"", "200 học sinh", "Đo kết quả", "`c171d3b` (rbda-kiosk)"),
        ("Sáu sổ mô phỏng có điểm quyết tâm (hợp lệ, có lỗi, trống)", "120 và 800 học sinh", "Thử tải, thử lỗi", "`2df59ce` (kho này)"),
        ("Sổ mẫu chế độ huy chương", "8 CLB, 2 buổi, 120 học sinh, 829 nguyện vọng, 194 lượt thi", "Demo FA-DAA", "`9db3039` (kho này)"),
        ("Sổ có lỗi cố ý", "Có 5 loại lỗi", "Thử báo lỗi", "`e08af78` (kho này)"),
        ("Trường 3 buổi", "180 học sinh", "Thử nhiều buổi", "`7932934` (kho DU-AN)"),
        ("Công ty Bình Minh (không gian ngành khác)", "54 nhân viên, 8 dự án", "Thử tổng quát hoá", "`7932934`, `0007c7f` (kho DU-AN)"),
        ("Mẫu xuất từ biểu mẫu Microsoft Forms", "60 học sinh giả, cột email = anonymous", "Thử bộ chuyển đổi", "`7cbd7ee` (rbda-kiosk)"),
        ("Ví dụ viết tay", "10 em, 4 CLB", "Hướng dẫn", "`5931dad` (rbda-kiosk)"),
    ], [5.8, 4.2, 3.0, 4.0])
    b.p("Một sự việc cần ghi: ở kho rbda-kiosk, một tệp kết quả giả 4 dòng (chỉ có mã HS001… và mã CLB, không có tên) từng bị lưu nhầm rồi được xoá ở commit `977142d`.")

    # ---- 11
    b.h("11. Demo chỉnh một quy tắc và đối chiếu kết quả")
    b.p("Kịch bản đầy đủ từng bước: `docs/giai_trinh/KICH_BAN_DEMO.md`. Ý chính: người quản lý đổi một tiêu chí **ở chế độ chạy thử**, "
        "so với kết quả chính thức, rồi chọn áp dụng hoặc bỏ. Chạy thử không ghi đè kết quả chính thức.")
    b.ds(["Mở thẻ **Quản lý**, xem tiêu chí đang dùng bằng lời thường.", "Đổi tiêu chí trong **Thử cấu hình** rồi bấm **Chạy thử**.",
          "Chọn hai lần chạy, bấm **So sánh**: phần mềm cho biết ai đổi chỗ, theo nhóm và theo CLB.", "Bấm áp dụng hoặc bỏ. Mọi thao tác được ghi vào nhật ký thao tác."])
    b.h("Ví dụ thật: cho nhóm \"chính sách\" đứng trước mọi nhóm khác", 2)
    b.p("Cùng bộ 120 học sinh, hạt giống 42. Tiêu chí thử đặt nhóm chính sách (19 em) xếp trước các nhóm khác bất kể điểm.")
    b.bang(["Chỉ số", "Chính thức", "Chạy thử"], [
        ("Số em có chỗ", "108", "110"), ("Số em chưa có chỗ", "12", "10"),
        ("Tỉ lệ được nguyện vọng 1", "53,3%", "55,0%"),
        ("Nhóm chính sách: số em có chỗ", "17 trên 19", "19 trên 19"),
        ("Nhóm chính sách: được nguyện vọng 1", "57,9%", "100%"),
        ("Em không thuộc nhóm nào: được nguyện vọng 1", "53,2%", "47,9%"),
        ("Số em đổi chỗ", "", "21")], [8.0, 4.5, 4.5], dam_cot0=True)
    b.p("Đối chiếu một em: HS002 chính thức vào CLB Âm nhạc; ở bản chạy thử vào CLB Bóng đá. Điểm chuẩn Bóng đá là 5,9 ở bản chính thức và 5,0 ở bản thử; em được 5,8. "
        "Số liệu lấy từ `docs/giai_trinh/CA_MAU.md`, mục 5; bảng sinh bằng `du_lieu_test/tao_ca_mau_giai_trinh.py` nên chạy lại ra đúng số này.")
    b.p("Commit của tính năng (kho này): `ecf2130` (tiêu chí bằng lời), `3f5957c` (chạy thử), `e92d544` (so sánh), `20f396d` (áp dụng), `bd93958` (ba thẻ mục tiêu, đổi quy tắc 1 đến 2 lần bấm). "
        "Kho DU-AN: `d0c22ac` (luật xếp theo không gian làm việc).", 10, XAM)

    # ---- 12
    b.trang_moi()
    b.h("12. Cách chạy phần mềm")
    b.p("Chi tiết: `README.md` và `docs/giai_trinh/HUONG_DAN_CHAY.md`. Tóm tắt (Linux; trên Windows thay `.venv/bin/` bằng `.venv\\Scripts\\`):")
    for dong in ["python3 -m venv .venv", ".venv/bin/pip install -r requirements-dev.txt", ".venv/bin/python main.py"]:
        dv = b.p("`%s`" % dong)
        dv.paragraph_format.left_indent = Cm(1)
        dv.paragraph_format.space_after = Pt(2)
    b.ds(["Nạp thử `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` (nhớ bật chế độ huy chương trước). Mong đợi: 8 CLB, 2 buổi, 120 học sinh, 829 nguyện vọng, 194 lượt thi, không lỗi.",
          "Bấm chạy xếp với hạt giống 42: các bước sao lưu, kiểm, bốc thăm, xếp, ghi, xuất đều xong; 120 trên 120 học sinh có chỗ.",
          "Nạp `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx` để xem phần mềm báo 5 lỗi và không nạp gì.",
          "Bản dành cho trường: `build_windows.bat` dựng tệp `.exe`; quy trình tự động dựng cũng có sẵn."], "List Number")
    b.h("Kiểm thử tự động", 2)
    b.bang(["Kho", "Tệp test", "Số ca test", "Quy trình kiểm tự động"], [
        (K_RB, "%d" % RB["test_tep"], "%s (đếm hàm test)" % format(RB["test_ham"], ",").replace(",", "."), "Có (Linux và Windows)"),
        (K_DA, "%d" % DA["test_tep"], "%s (thu thập, chưa chạy)" % format(DA["test_ca"], ",").replace(",", "."), "Có"),
        (K_CM, "%d" % tq["test"], "6.361 (thu thập ngày 22/11/2026, chưa chạy toàn bộ)", "Có; độ phủ yêu cầu từ 85%"),
    ], [4.2, 2.6, 6.0, 4.2], dam_cot0=True)
    b.p("Em chưa chạy toàn bộ bộ test cho báo cáo này (mất khoảng 22 phút); các số trên là số đếm. Phần đã kiểm trước khi lập báo cáo: lệnh `kiem_nhanh.py` đạt 7 trên 7 mục, kể cả việc kết quả trùng khít với bản gốc.", 10, XAM)

    # ---- 13
    b.h("13. Lịch sử thay đổi theo giai đoạn")
    b.p("Mỗi dòng là một giai đoạn làm việc; mã commit tiêu biểu để tra bằng `git show`. Kho ghi trong ngoặc.")
    b.bang(["Ngày", "Giai đoạn", "Việc chính", "Mã tiêu biểu"], [
        ("26/08/2026", "Bản gốc", "Nhập thuật toán, giao diện, bộ test đầu tiên", "`26be1a4` (RB)"),
        ("26/08 đến 06/09", "Chạy được trên Windows", "Sửa đóng gói .exe, bộ test đầu, quy trình dựng tự động", "`bc3ad6b`, `713ec4c`, `ac32b92` (RB)"),
        ("29/08 đến 05/09", "Nhập dữ liệu và bốc thăm tái lập", "Nhập CSV và Excel, kiểm lỗi, bốc thăm không phụ thuộc thứ tự, học sinh vào muộn", "`ee1e7b1`, `b5fe827`, `9253418` (RB)"),
        ("02 đến 09/09", "Đo và giải đáp", "Đo chi phí của tính ổn định, đo xem có phải cặp ghép tốt nhất, trả lời câu hỏi bốc thăm", "`0137964`, `db6f7b0`, `5cdee4b` (RB)"),
        ("11 đến 12/09", "Xếp nhiều buổi", "Mỗi học sinh một tuần thay vì một CLB, chọn một buổi hay một dải ngày", "`ecb7128`, `2461e17` (RB)"),
        ("24 đến 29/09", "Rà soát thiết kế", "Tách mã thành mô-đun, ràng buộc cơ sở dữ liệu, khoá hạt giống, vá lỗ hổng bảo mật, CI chạy test", "`2638949`, `7e92d29`, `5ad9bfc`, `dac7946`, `c09a0c1` (RB)"),
        ("03 đến 04/10", "Sổ nhập một tệp", "Một tệp Excel thay ba tệp; nạp tất cả hoặc không gì", "`ed84f75`, `b9b99f8`, `52981bb` (RB)"),
        ("08 đến 15/10", "Kho thứ hai; nhiều ngành", "Bản chụp, kế hoạch tổng quát hoá, không gian làm việc, bộ thử công ty, kỹ năng dựng workspace", "`0e4d774`, `7c4f423`, `ddec7be`, `7932934` (DA)"),
        ("24/10", "Kho thứ ba", "Nhập toàn bộ mã vào kho này", "`e08af78`"),
        ("24/10 đến 04/11", "Điểm quyết tâm; lớp học sinh", "Học sinh chia 100 điểm giữa các lựa chọn; thêm lớp; điểm chuẩn từng CLB", "`c011f69`, `54a5cf4`, `fbc82c9`"),
        ("05 đến 06/11", "Bộ công cụ Microsoft Forms", "Biểu mẫu và bộ chuyển đổi cho hệ thống của trường", "`6947ec2`, `0b2bbc8`"),
        ("08 đến 15/11", "Cơ chế FA-DAA", "Huy chương, loại CLB, đóng CLB thiếu người, danh sách chờ, điểm danh, vòng 2", "`74ea6be`, `3c22e0b`, `1037920`, `628cfb2`, `e76bf48`"),
        ("15 đến 18/11", "Giải trình kết quả", "Giải thích từng học sinh, chạy thử tiêu chí, tài khoản và quyền, nhật ký thao tác, gói minh chứng", "`5926107`, `6fda292`, `ecf2130`, `0554e0b`, `385afc1`, `6674e67`"),
        ("18 đến 21/11", "Giao diện, PDF, mục tiêu", "Làm lại giao diện, xuất PDF, ba thẻ mục tiêu, sổ mẫu", "`bd93958`, `3a70029` (PR #27)"),
        ("22/11", "Báo cáo minh chứng", "Báo cáo lịch sử và sơ đồ luồng xử lý (kho này)", "xem `git log -- docs/giai_trinh`"),
    ], [2.6, 3.4, 6.4, 4.6])
    b.p("Gộp mã vào nhánh chính: %d yêu cầu gộp PR ở kho này (từ #1 đến #27), 5 ở kho rbda-kiosk, 2 ở kho DU-AN. Bảng đầy đủ mọi commit của kho này: `docs/giai_trinh/LICH_SU_COMMIT.csv`." % len(ls.danh_sach_pr()))

    # ---- 14
    b.h("14. Điều chưa đầy đủ và việc cần Truong xác nhận")
    b.p("Phần này nói thẳng những chỗ bằng chứng còn thiếu hoặc yếu.")
    b.bang(["#", "Điều còn thiếu hoặc không chắc", "Việc cần làm"], [
        ("1", "Lịch sử trước 26/08/2026 không có ở đâu. Commit gốc ghi mã được mang từ nơi khác vào; không biết ai viết mã có trước.", "Truong bổ sung nguồn (kho hay tệp cũ), hoặc ghi rõ đây là phần học sinh tự viết trước khi đưa lên kho"),
        ("2", "Ba commit nhập hàng loạt (`26be1a4`, `0e4d774`, `e08af78`) khiến \"commit đầu tiên\" của các tệp lõi đều là bản chụp.", "Không sửa được; báo cáo ghi rõ"),
        ("3", "Kho `RB-STUFF-AFTER-UP` được nhắc nhưng chưa có báo cáo; khoảng 15/10 đến 24/10 chưa có commit nào trong ba kho.", "Truong cho biết kho đó có phải tên cũ của kho DU-AN không; nếu là kho khác thì chạy lại lệnh lập báo cáo cho kho đó"),
        ("4", "Ở kho rbda-kiosk có dấu hiệu lịch sử được viết lại hoặc ghép từ nguồn khác: hai mã commit được nhắc trong lời mô tả (`f483ebf`, `57f2e82`) không còn tồn tại; 10 commit có ngày tác giả khác ngày commit.", "Chỉ ghi nhận; kho không cho biết nguyên nhân"),
        ("5", "Gần như mọi commit mang tên công cụ AI, nên git không phân biệt phần học sinh yêu cầu, duyệt, sửa tay với phần AI tự quyết.", "Học sinh tự mô tả phần việc của mình ở mục 9"),
        ("6", "Bảng \"học sinh viết gì, AI viết gì\" nằm trong BAN_GIAO.md, tệp này do công cụ AI ghi vào kho; chưa có nguồn độc lập.", "Học sinh xác nhận hoặc sửa nội dung đó"),
        ("7", "Nhật ký AI chính thức (`Nhat_Ky_AI_RB-DA.pdf`) nằm ngoài kho; bản Word chỉ ở một nhánh chưa gộp của kho rbda-kiosk. Trong kho này có `docs/nhat_ky_ai/`.", "Gộp hoặc nộp kèm bản nhật ký chính thức"),
        ("8", "Số ca test ghi trong tài liệu khác nhau theo thời điểm (ví dụ 1.515, 1.764, 6.361).", "Dùng một con số, ghi ngày đếm; chạy toàn bộ bộ test một lần trước khi nộp"),
        ("9", "Phần quy tắc của Sở trong BAN_GIAO.md (Phụ lục 1) nói AI được viết mã nhưng không được viết kế hoạch, tóm tắt, bài báo, kết luận; trong kho có nhiều tệp kế hoạch và tài liệu do công cụ AI soạn.", "Học sinh đối chiếu với quy định hiện hành và quyết định cách ghi nhận"),
        ("10", "Tên hiển thị git của tài khoản học sinh là một biệt danh không phù hợp cho hội đồng đọc; báo cáo chỉ dùng nhãn \"tài khoản học sinh\".", "Truong quyết định có thêm tệp `.mailmap` để ẩn tên khi xem log hay không"),
        ("11", "Địa chỉ email giả `a@truong.vn` còn trong vài tệp test (dữ liệu thử).", "Truong quyết định giữ hay đổi sang tên miền ví dụ"),
    ], [0.8, 9.4, 6.8])
    b.p("Đã xử lý: đường dẫn máy cá nhân trong `du_lieu_test/do_do_dai_nguyen_vong.py` (kho DU-AN từng có) không còn ở kho này. Không tìm thấy mật khẩu, khoá bí mật hay dữ liệu học sinh thật trong ba kho.", 10, XAM)

    # ---- Phụ lục A
    b.trang_moi()
    b.h("Phụ lục A. Minh chứng theo từng yêu cầu")
    b.p("Mỗi bảng là một nhóm yêu cầu. Ngày và tiêu đề của kho này đọc trực tiếp từ git; hai kho còn lại lấy từ báo cáo sự việc của chính chúng.")
    ycau = {"A": "Kho mã và lịch sử thay đổi", "B": "Mã cốt lõi và thuật toán ghép", "C": "Dữ liệu đầu vào, ràng buộc",
            "D": "Cách xử lý khi không đủ chỗ", "E": "Vai trò của AI, phần việc từng thành viên", "F": "Sơ đồ luồng xử lý và tài liệu",
            "G": "Bộ dữ liệu thử ẩn danh", "H": "Demo chỉnh một quy tắc phân bổ", "I": "Hướng dẫn chạy và kiểm tự động"}
    cm_theo_nhom = {k: ds for k, (_, _, _, ds) in zip(THU_TU_NHOM, ls.MINH_CHUNG)}
    for k in THU_TU_NHOM:
        b.h("%s. %s" % (k, ycau[k]), 2)
        hang = []
        for kho, ma, ngay, viec in THEM.get(k, []):
            hang.append(({K_RB: "rbda-kiosk", K_DA: "DU-AN"}[kho], "`%s`" % ma, ngay, viec))
        for ma, viec in cm_theo_nhom[k]:
            c = ls.doc_commit(ma)
            hang.append(("ClubMatch", "`%s`" % c["ngan"], "/".join(reversed(c["ngay"].split("-"))), viec.replace("`", "")))
        b.bang(["Kho", "Mã", "Ngày", "Việc commit đó chứng minh"], hang, [3.2, 2.0, 2.2, 9.6], co=9)

    # ---- Phụ lục B
    b.trang_moi()
    b.h("Phụ lục B. Cách tự kiểm lại")
    b.h("Đường đi của dữ liệu qua 12 bước", 2)
    png = os.path.join(THU_MUC, "_12_tam.png")
    if svg_png(ls.DUONG_SVG_BUOC, png):
        b.anh(png, rong_cm=17)
        os.remove(png)
    b.p("Hình 3. Đường đi của dữ liệu từ biểu mẫu đến kết quả. Từng bước, tệp mã và cách xử lý lỗi: `docs/giai_trinh/SO_DO_LUONG.md`.", 9, XAM, WD_ALIGN_PARAGRAPH.CENTER)
    b.h("Lệnh để xem một dấu vết", 2)
    for dong in ["git show --stat <mã commit>", "git log --oneline --follow -- rbda_priority_pipeline.py",
                 "git log -S\"def run_rbda\" --reverse --format='%h %ad %s' --date=short",
                 "git rev-parse --is-shallow-repository      # nếu in true thì chạy: git fetch --unshallow origin",
                 "python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20"]:
        dv = b.p("`%s`" % dong, 10)
        dv.paragraph_format.left_indent = Cm(0.8)
        dv.paragraph_format.space_after = Pt(2)
    b.h("Tệp đi kèm trong kho này (thư mục docs/giai_trinh)", 2)
    b.ds(["`LICH_SU_COMMIT.csv`: mọi commit của kho này (mã, ngày, nhãn tác giả, gộp hay không, số tệp đổi, tiêu đề).",
          "`LICH_SU_THAY_DOI.docx` và `.pdf`: báo cáo lịch sử riêng của kho này, có bảng 23 yêu cầu gộp PR.",
          "`so_do_xu_ly.svg`, `so_do_luong.svg`: hai sơ đồ dạng vector, phóng to không vỡ.",
          "`DU_LIEU_DAU_VAO.md`, `CA_MAU.md`, `HUONG_DAN_CHAY.md`, `KICH_BAN_DEMO.md`, `VAI_TRO_AI.md`: các tài liệu nguồn của báo cáo này.",
          "Hai báo cáo lịch sử của kho rbda-kiosk và DU-AN-PHAN-2GALESHARPLEY (tệp Word riêng, kèm bảng CSV đầy đủ, do chính hai kho lập)."])
    return b.d


def main() -> int:
    tq = ls.tong_quan()
    d = dung(tq)
    d.save(DUONG_DOCX)
    print("docx:", DUONG_DOCX)
    return 0


if __name__ == "__main__":
    sys.exit(main())
