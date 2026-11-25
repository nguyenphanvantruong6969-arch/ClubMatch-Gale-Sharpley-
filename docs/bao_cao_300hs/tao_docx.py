# -*- coding: utf-8 -*-
"""Dựng BAO_CAO_THU_NGHIEM_300HS.docx từ so_lieu.json và anh/*.png (do chay_bao_cao.py tạo).

    python docs/bao_cao_300hs/tao_docx.py

Báo cáo vận hành: chỉ mô tả cách chạy, số đo và thông báo của phần mềm. Phần nhận xét, diễn giải
và kết luận để trống cho học sinh tự viết (quy định liêm chính học thuật của dự án).
"""
import json
import os
import sys

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

D = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, GOC)
from i18n_errors import format_message  # noqa: E402

with open(os.path.join(D, "so_lieu.json"), encoding="utf-8") as _f:
    SL = json.load(_f)
ANH = os.path.join(D, "anh")
RA = os.path.join(D, "BAO_CAO_THU_NGHIEM_300HS.docx")
BUOI = {"thu_3": "Thứ 3", "thu_6": "Thứ 6"}
MAU = RGBColor(0x1F, 0x4E, 0x3D)

doc = Document()
XAM = RGBColor(0x5F, 0x6B, 0x66)
DO = RGBColor(0xA0, 0x30, 0x20)
FONT = "Times New Roman"
st = doc.styles["Normal"]
st.font.name = FONT
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
st.font.size = Pt(12)
st.paragraph_format.line_spacing = 1.15
st.paragraph_format.space_after = Pt(6)
for ten, co, truoc, sau in (("Heading 1", 16, 0, 12), ("Heading 2", 13, 14, 6), ("Heading 3", 12, 10, 4)):
    h = doc.styles[ten]
    h.font.name = FONT
    h.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    h.element.rPr.rFonts.set(qn("w:ascii"), FONT)
    h.element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    for k in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):   # bỏ phông theo theme (Calibri Light)
        h.element.rPr.rFonts.attrib.pop(qn(k), None)
    h.font.size = Pt(co)
    h.font.bold = True
    h.font.color.rgb = MAU
    h.paragraph_format.space_before = Pt(truoc)
    h.paragraph_format.space_after = Pt(sau)
    h.paragraph_format.keep_with_next = True
doc.styles["Heading 1"].paragraph_format.page_break_before = True   # mỗi mục lớn sang trang mới
doc.styles["List Bullet"].paragraph_format.space_after = Pt(3)

SO_HINH = [0]
SO_BANG = [0]


def _them(cha, ten, **thuoc):
    e = OxmlElement(ten)
    for k, v in thuoc.items():
        e.set(qn(k), str(v))
    cha.append(e)
    return e


def vien_duoi(p, mau="1F4E3D", co=12):
    """Kẻ một đường dưới đoạn (tiêu đề mục, đường phân cách trang bìa)."""
    bd = _them(p._p.get_or_add_pPr(), "w:pBdr")
    _them(bd, "w:bottom", **{"w:val": "single", "w:sz": co, "w:space": 4, "w:color": mau})


def to_nen_doan(p, nen, vien=None):
    ppr = p._p.get_or_add_pPr()
    if vien:
        bd = _them(ppr, "w:pBdr")
        _them(bd, "w:left", **{"w:val": "single", "w:sz": 24, "w:space": 8, "w:color": vien})
    _them(ppr, "w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": nen})


def truong(run, ma):
    """Chèn một trường Word (PAGE, NUMPAGES) vào `run`."""
    _them(run._r, "w:fldChar", **{"w:fldCharType": "begin"})
    t = _them(run._r, "w:instrText", **{"xml:space": "preserve"})
    t.text = ma
    _them(run._r, "w:fldChar", **{"w:fldCharType": "end"})


def doan(text, dam=False, nghieng=False, co=None, canh=WD_ALIGN_PARAGRAPH.JUSTIFY, mau=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold, r.italic = dam, nghieng
    if co:
        r.font.size = Pt(co)
    if mau:
        r.font.color.rgb = mau
    if canh is not None:
        p.alignment = canh
    return p


def gach(text):
    p = doc.add_paragraph(text, style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def muc(text, cap):
    h = doc.add_heading(text, level=cap)
    if cap == 1:
        vien_duoi(h)
    return h


def hop(text, nen="FCEFEA", vien="A03020", dam=True, mau=DO):
    """Hộp lưu ý: nền màu, vạch trái."""
    p = doan(text, dam=dam, mau=mau, co=11)
    to_nen_doan(p, nen, vien)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    return p


def ma_lenh(dong):
    for i, x in enumerate(dong):
        p = doc.add_paragraph()
        r = p.add_run(x)
        r.font.name = "Consolas"
        r._r.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), "Consolas")
        r.font.size = Pt(9.5)
        to_nen_doan(p, "F1F3F2", "1F4E3D")
        pf = p.paragraph_format
        pf.space_after = Pt(0) if i < len(dong) - 1 else Pt(10)
        pf.line_spacing = 1.0
        pf.keep_with_next = i < len(dong) - 1


def hinh(ten, chu_thich, rong=16.0):
    duong = os.path.join(ANH, ten)
    if not os.path.exists(duong):
        doan("[Thiếu ảnh %s]" % ten, nghieng=True)
        return
    doc.add_picture(duong, width=Cm(rong))
    pa = doc.paragraphs[-1]
    pa.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pa.paragraph_format.keep_with_next = True          # ảnh không rời chú thích
    pa.paragraph_format.space_before = Pt(6)
    pa.paragraph_format.space_after = Pt(2)
    SO_HINH[0] += 1
    p = doc.add_paragraph()
    r1 = p.add_run("Hình %d. " % SO_HINH[0])
    r1.bold, r1.italic = True, True
    r2 = p.add_run(chu_thich)
    r2.italic = True
    for r in (r1, r2):
        r.font.size = Pt(10)
        r.font.color.rgb = XAM
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)


def nen_o(o, mau):
    _them(o._tc.get_or_add_tcPr(), "w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": mau})


def _la_so(x):
    t = str(x).replace(",", ".").replace("%", "").strip()
    try:
        float(t)
        return True
    except ValueError:
        return t in ("–", "-", "bật", "tắt")


def bang(tieu_de, dau, dong, co=10, rong=None):
    """Bảng có tiêu đề phía trên, hàng đầu nền xanh chữ trắng, hàng xen kẽ nền nhạt.
    KHÔNG BAO GIỜ TÁCH TRANG: mọi hàng (trừ hàng cuối) 'giữ với đoạn sau', không hàng nào được ngắt giữa
    chừng, và tiêu đề bảng giữ với bảng — Word / LibreOffice đẩy cả bảng sang trang mới nếu không vừa."""
    SO_BANG[0] += 1
    cap = doc.add_paragraph()
    r1 = cap.add_run("Bảng %d. " % SO_BANG[0])
    r1.bold = True
    r2 = cap.add_run(tieu_de)
    for r in (r1, r2):
        r.font.size = Pt(10.5)
        r.font.color.rgb = MAU
    r2.bold = True
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.keep_with_next = True
    cap.paragraph_format.space_before = Pt(8)
    cap.paragraph_format.space_after = Pt(4)

    t = doc.add_table(rows=1, cols=len(dau))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tpr = t._tbl.tblPr
    bd = _them(tpr, "w:tblBorders")
    for canh in ("top", "left", "bottom", "right", "insideH", "insideV"):
        _them(bd, "w:" + canh, **{"w:val": "single", "w:sz": 4, "w:space": 0, "w:color": "B7C4BE"})
    mar = _them(tpr, "w:tblCellMar")
    for canh, v in (("top", 45), ("bottom", 45), ("left", 90), ("right", 90)):
        _them(mar, "w:" + canh, **{"w:w": v, "w:type": "dxa"})
    for i, x in enumerate(dau):
        o = t.rows[0].cells[i]
        o.text = ""
        r = o.paragraphs[0].add_run(str(x))
        r.bold = True
        r.font.size = Pt(co)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        o.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        nen_o(o, "1F4E3D")
    for j, d in enumerate(dong):
        cs = t.add_row().cells
        for i, x in enumerate(d):
            cs[i].text = ""
            r = cs[i].paragraphs[0].add_run("" if x is None else str(x))
            r.font.size = Pt(co)
            if _la_so("" if x is None else x):
                cs[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if j % 2 == 1:
                nen_o(cs[i], "EEF4F1")
    n = len(t.rows)
    for k, hang in enumerate(t.rows):
        trpr = hang._tr.get_or_add_trPr()
        _them(trpr, "w:cantSplit")
        if k == 0:
            _them(trpr, "w:tblHeader")
        for o in hang.cells:
            o.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for pa in o.paragraphs:
                pf = pa.paragraph_format
                pf.space_after = Pt(0)
                pf.space_before = Pt(0)
                pf.line_spacing = 1.0
                pf.keep_with_next = k < n - 1
                pf.keep_together = True
    if rong:
        t.autofit = False
        for i, w in enumerate(rong):           # LibreOffice đọc tblGrid, Word đọc độ rộng ô: đặt cả hai
            t.columns[i].width = Cm(w)
        for hang in t.rows:
            for i, w in enumerate(rong):
                hang.cells[i].width = Cm(w)
    sau = doc.add_paragraph()
    sau.paragraph_format.space_after = Pt(4)
    return t


def loi_vi(e):
    try:
        return format_message(e["code"], e.get("params") or {})
    except Exception:
        return e["code"]


# ------------------------------------------------------------------ Đầu trang / chân trang
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2)
    s.header_distance = s.footer_distance = Cm(1)
    s.different_first_page_header_footer = True          # trang bìa không có đầu/chân trang
    ph = s.header.paragraphs[0]
    r = ph.add_run("Báo cáo thử nghiệm RB-DA  ·  Dữ liệu mô phỏng 300 học sinh")
    r.font.size = Pt(9)
    r.font.color.rgb = XAM
    ph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    vien_duoi(ph, "B7C4BE", 4)
    pf = s.footer.paragraphs[0]
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for phan in ("Trang ", "PAGE", " / ", "NUMPAGES"):
        r = pf.add_run()
        r.font.size = Pt(9)
        r.font.color.rgb = XAM
        if phan in ("PAGE", "NUMPAGES"):
            truong(r, phan)
        else:
            r.text = phan

# ------------------------------------------------------------------ Trang bìa
for _ in range(3):
    doc.add_paragraph()
doan("DỰ ÁN KHOA HỌC KỸ THUẬT  ·  PHẦN MỀM PHÂN BỔ CÂU LẠC BỘ RB-DA", dam=True, co=10, mau=XAM,
     canh=WD_ALIGN_PARAGRAPH.CENTER)
p = doan("BÁO CÁO THỬ NGHIỆM", dam=True, co=28, mau=MAU, canh=WD_ALIGN_PARAGRAPH.CENTER)
p.paragraph_format.space_before = Pt(18)
p.paragraph_format.space_after = Pt(4)
doan("Bộ dữ liệu mô phỏng 300 học sinh", dam=True, co=16, canh=WD_ALIGN_PARAGRAPH.CENTER)
p = doan("Ca thành công / không đạt có giải thích  ·  Bảng số bốc thăm (seed)  ·  Kết quả khi đổi cấu hình  ·  "
         "Dữ liệu thiếu và tiêu chí xung đột", nghieng=True, co=11, mau=XAM, canh=WD_ALIGN_PARAGRAPH.CENTER)
vien_duoi(p, "1F4E3D", 12)
p.paragraph_format.space_after = Pt(24)
t = doc.add_table(rows=0, cols=2)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for k, v in (("Dữ liệu", "300 học sinh · 2 buổi (Thứ 3, Thứ 6) · 14 câu lạc bộ · 600 chỗ cần xếp"),
             ("Seed sinh dữ liệu", "20261122"),
             ("Seed xếp (mã bốc thăm)", "%d (mục 3 thử thêm 7, 2026, 12345)" % SL["seed"]),
             ("Chế độ đã chạy", "Chỉ xếp thứ tự · Chia 100 điểm · Chia 100 điểm + chia loại · Huy chương"),
             ("Thuật toán", "Deferred Acceptance (Gale–Shapley), học sinh đề nghị; dự trữ mềm hai lượt; "
                            "bốc thăm một lần (STB) đã khoá; ưu tiên hai tầng"),
             ("Nguồn ảnh", "Giao diện thật của phần mềm, chạy trong trình duyệt Chromium")):
    cs = t.add_row().cells
    cs[0].text, cs[1].text = "", ""
    r = cs[0].paragraphs[0].add_run(k)
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = MAU
    cs[1].paragraphs[0].add_run(v).font.size = Pt(11)
    nen_o(cs[0], "EEF4F1")
    for o in cs:
        o.paragraphs[0].paragraph_format.space_after = Pt(2)
t.autofit = False
for hang in t.rows:
    hang.cells[0].width, hang.cells[1].width = Cm(4.6), Cm(11.4)
t.columns[0].width, t.columns[1].width = Cm(4.6), Cm(11.4)
doc.add_paragraph()
hop("LƯU Ý: Mọi số liệu trong báo cáo là DỮ LIỆU MÔ PHỎNG do máy sinh (tên học sinh bịa ghép từ bảng "
    "họ/đệm/tên). Đây không phải khảo sát hay học sinh thật.")
p = doan("Nội dung", dam=True, co=12, mau=MAU, canh=None)
p.paragraph_format.space_before = Pt(18)
for x in ("1. Dữ liệu thử nghiệm và cách tái lập",
          "2. Một số ca phân bổ thành công / không đạt nguyện vọng, có giải thích",
          "3. Bảng thứ tự xét (trọng số) và số bốc thăm theo seed",
          "4. Kết quả thay đổi khi chỉnh cấu hình",
          "5. Xử lý dữ liệu thiếu và tiêu chí xung đột",
          "6. Nhận xét và kết luận (học sinh tự viết)"):
    p = doan(x, co=11, canh=None)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.6)

# ------------------------------------------------------------------ 1. Dữ liệu và cách chạy
muc("1. Dữ liệu thử nghiệm và cách tái lập", 1)
doan("Bộ dữ liệu gồm 300 học sinh, 2 buổi sinh hoạt (Thứ 3, Thứ 6), mỗi buổi 7 câu lạc bộ thuộc ba loại: "
     "1 CLB Tự do (nhận mọi em), 3 CLB Giới hạn (có chỉ tiêu, không thi), 3 CLB Tuyển chọn (có bài thi "
     "và điểm sàn). Sổ nhập được thiết kế để hợp lệ cùng lúc cho cả ba cách khai nguyện vọng (Chỉ xếp "
     "thứ tự, Chia 100 điểm, Huy chương 60/30/10) và cho công tắc “Chia CLB theo loại”, nên có thể đổi "
     "chế độ qua lại mà không phải nạp lại.")
LOAI = {"TU_DO": "Tự do", "GIOI_HAN": "Giới hạn", "TUYEN_CHON": "Tuyển chọn"}
dong = [(c["name"], BUOI.get(c["buoi"], c["buoi"]), LOAI.get(c.get("loai"), c.get("loai") or ""), c["capacity"], c.get("diem_san") or "–")
        for c in SL["clb"]]
bang("Danh sách 14 câu lạc bộ (sheet “1. CLB”)", ["Tên CLB", "Buổi", "Loại", "Chỉ tiêu", "Điểm sàn"], dong,
     co=9.5, rong=[4.6, 2.2, 3.0, 2.2, 2.2])
doan("Mỗi em, mỗi buổi, chọn ngẫu nhiên một trong ba kiểu khai: K1 không thi (xếp 3 CLB Giới hạn), "
     "K2 thi một CLB (3 CLB Giới hạn + 1 CLB Tuyển chọn), K3 thi ba CLB Tuyển chọn; 85 % em thêm CLB Tự do "
     "ở cuối danh sách. Huy chương Vàng/Bạc/Đồng (60/30/10) đặt trọn trong một quỹ 100 điểm.")
doan("Các tệp đi kèm (thư mục docs/bao_cao_300hs/):", dam=True)
for x in ("SO_NHAP_300HS_DOI_CHE_DO.xlsx — sổ nhập hợp lệ 300 em (sinh bằng sinh_300hs.py).",
          "SO_NHAP_300HS_LOI_CLB.xlsx, SO_NHAP_300HS_LOI_HS.xlsx, SO_NHAP_300HS_THIEU_XUNG_DOT.xlsx — ba sổ "
          "cố ý sai (sinh bằng sinh_so_co_loi.py).",
          "chay_bao_cao.py — điều khiển giao diện thật bằng Chromium, chụp ảnh, ghi so_lieu.json.",
          "tao_docx.py — dựng báo cáo này từ so_lieu.json và thư mục anh/."):
    gach(x)
doan("Chạy lại toàn bộ (cùng seed cho ra cùng số liệu):", dam=True)
ma_lenh(["python docs/bao_cao_300hs/sinh_300hs.py", "python docs/bao_cao_300hs/sinh_so_co_loi.py",
         "python docs/bao_cao_300hs/chay_bao_cao.py", "python docs/bao_cao_300hs/tao_docx.py"])
hinh("01_trang_dau.png", "Màn hình “Xếp CLB” trước khi nạp sổ.")
hinh("02_nap_xong.png", "Nạp sổ 300 học sinh xong: 14 CLB, 300 học sinh, 0 dòng bỏ qua; bước “Xem cảnh báo” "
     "báo không có vấn đề.")
doan("Kiểm tra sức khoẻ dữ liệu sau khi nạp: %d cảnh báo." % len(SL["suc_khoe"]))

# ------------------------------------------------------------------ 2. Ca thành công / không đạt
muc("2. Một số ca phân bổ thành công / không đạt nguyện vọng, có giải thích", 1)
doan("Các ca dưới đây chạy ở chế độ Huy chương, seed %d. Lời giải thích lấy nguyên văn từ mục “Tra cứu "
     "một học sinh” ở thẻ Kết quả: gõ mã học sinh, phần mềm liệt kê từng nguyện vọng, CLB đó còn chỗ hay "
     "đã đầy, mức vào được (điểm chuẩn / huy chương / bốc thăm) và câu “Vì sao”. Cùng nội dung ấy có thể "
     "in phiếu hoặc lưu PDF để phát cho học sinh." % SL["seed"])
TEN_CA = {"thanh_cong": ("2.1. Ca thành công — %s", "05_ca_thanh_cong_%s.png"),
          "khong_dat_huy_chuong_boc_tham": ("2.2. Ca không đạt nguyện vọng đầu vì huy chương và bốc thăm — %s",
                                            "05_ca_khong_dat_huy_chuong_boc_tham_%s.png"),
          "khong_dat_diem": ("2.3. Ca không đạt vì chưa đủ điểm sàn — %s", "05_ca_khong_dat_diem_%s.png")}
for nhan, ca in SL["ca"].items():
    sid = ca["student_id"]
    tieu, anh = TEN_CA[nhan]
    muc(tieu % sid, 2)
    for b in ca["buoi"]:
        dong = [(x["hang"], x["clb"], x["huy_chuong"] or "–", x["diem"] if x["diem"] is not None else "–",
                 x["ma"], x["cau"]) for x in b["lua_chon"]]
        bang("%s — %s: kết quả %s" % (sid, BUOI[b["buoi"]], b["ket_qua"]),
             ["NV", "CLB", "Huy chương", "Điểm thi", "Mã lý do", "Câu giải thích của phần mềm"], dong, co=9,
             rong=[0.9, 2.6, 1.6, 1.2, 4.1, 6.2])
    hinh(anh % sid, "Thẻ Kết quả → Tra cứu một học sinh: %s." % sid)
muc("2.4. Báo cáo tải về", 2)
doan("Từ thẻ Kết quả có thể tải: phiếu giải trình từng em (HTML in được / PDF), phiếu cả lớp, báo cáo tổng "
     "hợp (PDF), và ở thẻ “Chi tiết và xuất tệp”: Excel kết quả, lý do kết quả (CSV), biên bản bốc thăm.")
hinh("07_menu_bao_cao.png", "Menu “Báo cáo và phiếu in” trên thẻ Kết quả.")
hinh("06_phieu_giai_trinh_tai_ve.png", "Phiếu giải trình tải về (HTML in được) — trang của DC002.", rong=13)
hinh("06b_phieu_pdf-1.png", "Phiếu giải trình dạng PDF (nút “Lưu PDF”) — DC034.", rong=13)
hinh("07b_chi_tiet_xuat.png", "Thẻ “Chi tiết và xuất tệp”: tóm tắt lần chạy và các nút tải.")

# ------------------------------------------------------------------ 3. Bảng trọng số / seed
muc("3. Bảng thứ tự xét (trọng số) và số bốc thăm theo seed", 1)
doan("Khi nhiều em cùng muốn một chỗ, phần mềm xét theo thứ tự tiêu chí cố định (bảng “Thứ tự đang dùng” ở "
     "Quản lý → Cách xếp → Tuỳ chỉnh thêm). Tiêu chí cuối cùng luôn là số bốc thăm (STB). Số bốc thăm được "
     "sinh tất định từ seed (“Mã bốc thăm”) bằng crc32, khoá sau lần chạy đầu; muốn đổi seed phải bấm "
     "“Bốc thăm lại…” và mọi lần chạy đều được ghi vào lịch sử.")
hinh("10_thu_tu_tieu_chi_huy_chuong.png", "Thứ tự tiêu chí ở chế độ Huy chương: điểm thi → nhóm ưu tiên → "
     "số bốc thăm. Theo chú thích trên phiếu giải trình, huy chương cao hơn được xét trước khi các em bằng "
     "nhau ở các bước trước, rồi mới tới bốc thăm.")
hinh("10_thu_tu_tieu_chi_chi_xep.png", "Thứ tự tiêu chí ở chế độ Chỉ xếp thứ tự.")
hinh("09b_o_ma_boc_tham.png", "Ô “Mã bốc thăm” (seed) và nút “Bốc thăm lại…”.", rong=12)
stb42 = {h["student_id"]: h for h in SL["stb_mau"]["42"]["hoc_sinh"]}
stb7 = {h["student_id"]: h for h in SL["stb_mau"]["7"]["hoc_sinh"]}
dong = [(sid, stb42[sid]["name"], stb42[sid]["so"]["thu_3"], stb42[sid]["so"]["thu_6"],
         stb7.get(sid, {}).get("so", {}).get("thu_3", ""), stb7.get(sid, {}).get("so", {}).get("thu_6", ""))
        for sid in sorted(stb42)[:10]]
bang("Số bốc thăm của 10 em đầu với seed 42 và seed 7 (số nhỏ được xét trước)",
     ["Mã HS", "Họ tên", "Seed 42 · Thứ 3", "Seed 42 · Thứ 6", "Seed 7 · Thứ 3", "Seed 7 · Thứ 6"], dong,
     co=9.5, rong=[2.0, 4.0, 2.5, 2.5, 2.5, 2.5])
dong = [(s["seed"], s["nv"]["1"], s["ty_le_nv1"], s["ty_le_top3"], s["ngoai_nv"], s["khac_seed42"])
        for s in SL["seed_bang"]]
bang("Kết quả chế độ Chỉ xếp thứ tự với bốn seed (600 chỗ = 300 em × 2 buổi)",
     ["Seed", "Số chỗ NV1", "% NV1", "% trong 3 NV đầu", "Xếp ngoài danh sách NV", "Số chỗ khác so với seed 42"],
     dong, co=9.5, rong=[2.0, 2.4, 2.2, 2.8, 3.0, 3.6])
hinh("08_so_boc_tham_seed_42.png", "Bảng “Số bốc thăm theo buổi” với seed 42 (lọc 9 em đầu).", rong=14)
hinh("08_so_boc_tham_seed_7.png", "Cùng bảng sau khi bốc thăm lại với seed 7.", rong=14)
hinh("09_lich_su_chay.png", "Lịch sử sắp xếp: mỗi lần chạy thêm một dòng (seed, số vòng, có bốc lại hay không); "
     "không dòng nào bị ghi đè.", rong=14)

# ------------------------------------------------------------------ 4. Đổi cấu hình
muc("4. Kết quả thay đổi khi chỉnh cấu hình", 1)
doan("Cùng một sổ nhập, cùng seed %d, chỉ đổi chế độ ở Quản lý → Cách xếp (và công tắc “Chia CLB theo loại” ở "
     "Danh sách CLB) rồi bấm “Chạy sắp xếp” lại. Số liệu đọc từ bảng kết quả sau mỗi lần chạy." % SL["seed"])
dong = [(c["ten"], "bật" if c["rules"]["wharton"] else "tắt", "bật" if c["rules"]["fa_daa"] else "tắt",
         "bật" if c["rules"]["chia_loai"] else "tắt", c["nv"]["1"], c["nv"]["2"], c["nv"]["3"],
         c["nv"]["4"] + c["nv"]["5"] + c["nv_6_tro_len"], c["ngoai_nv"], c["ty_le_nv1"], c["ty_le_top3"])
        for c in SL["che_do"]]
bang("Phân bố mức đáp ứng nguyện vọng theo chế độ (600 chỗ)",
     ["Chế độ", "Chia 100", "Huy chương", "Chia loại", "NV1", "NV2", "NV3", "NV4+", "Ngoài DS", "% NV1", "% top 3"],
     dong, co=9, rong=[3.4, 1.3, 1.6, 1.3, 1.1, 1.1, 1.1, 1.1, 1.3, 1.2, 1.3])
ten = {c["khoa"]: c["ten"] for c in SL["che_do"]}
dong = [(ten[k.split("|")[0]], ten[k.split("|")[1]], v) for k, v in SL["khac_nhau"].items()]
bang("Số chỗ (học sinh × buổi) đổi CLB giữa hai chế độ", ["Chế độ A", "Chế độ B", "Số chỗ khác nhau / 600"], dong,
     co=9.5, rong=[6.0, 6.0, 4.0])
dong = [(v["student_id"], v["ten"], BUOI[v["buoi"]], v["chi_xep"], v["chia100"], v["huy_chuong"])
        for v in SL["vi_du_doi_clb"]]
bang("Ví dụ học sinh đổi CLB khi đổi chế độ", ["Mã HS", "Họ tên", "Buổi", "Chỉ xếp thứ tự", "Chia 100 điểm",
                                               "Huy chương"], dong, co=9, rong=[1.6, 3.0, 1.4, 3.5, 3.5, 3.6])
hop("Ghi chú đọc bảng: biểu đồ trên giao diện tính phần trăm trên số chỗ nằm trong danh sách nguyện vọng, "
     "còn các bảng trên tính trên đủ 600 chỗ, nên hai con số lệch nhau một chút.", nen="EEF4F1", vien="1F4E3D",
    dam=False, mau=None)
for c in SL["che_do"]:
    k = c["khoa"]
    muc("Chế độ: %s" % c["ten"], 3)
    hinh("03_%s_cach_xep.png" % k, "Chọn chế độ “%s” ở Quản lý → Cách xếp." % c["ten"], rong=13)
    if k == "chia100_loai":
        hinh("03_%s_cong_tac_loai.png" % k, "Bật công tắc “Chia CLB theo loại”: mỗi CLB có loại và điểm sàn.",
             rong=13)
    hinh("04_%s_muc_dap_ung.png" % k, "Mức đáp ứng nguyện vọng sau khi chạy ở chế độ “%s”." % c["ten"], rong=14)

# ------------------------------------------------------------------ 5. Dữ liệu thiếu / sai / xung đột
muc("5. Xử lý dữ liệu thiếu và tiêu chí xung đột", 1)
doan("Bốn tình huống được dựng từ chính sổ 300 em bằng cách sửa vài ô. Thông báo lỗi trong bảng là "
     "câu tiếng Việt phần mềm hiển thị (một nguồn duy nhất: i18n_errors.py).")
muc("5.1. Sheet CLB sai — chặn nhập", 2)
gach("CLB Bóng rổ bỏ trống Chỉ tiêu (thiếu dữ liệu bắt buộc).")
gach("CLB Cờ vua: Suất ưu tiên 80 > Chỉ tiêu 50 (hai cột mâu thuẫn).")
bang("Thông báo khi nhập SO_NHAP_300HS_LOI_CLB.xlsx", ["Mã lỗi", "Thông báo"],
     [(e["code"], loi_vi(e)) for e in SL["loi"]["loi_clb"]["import_errors"]], co=9, rong=[4.2, 12.4])
hinh("11_loi_clb_nhap.png", "Sổ có lỗi CLB: phần mềm liệt kê từng dòng sai và không nạp gì.")
muc("5.2. Sheet học sinh sai — chặn nhập", 2)
for x in ("DC003 đổi mã thành DC001 (trùng mã).", "DC004 bỏ trống mã học sinh (thiếu dữ liệu).",
          "DC005 ghi nguyện vọng “CLB Bơi lội” không có trong danh sách.", "DC006 ghi điểm thi bằng chữ “chín”."):
    gach(x)
bang("Thông báo khi nhập SO_NHAP_300HS_LOI_HS.xlsx", ["Mã lỗi", "Thông báo"],
     [(e["code"], loi_vi(e)) for e in SL["loi"]["loi_hs"]["import_errors"]], co=9, rong=[4.2, 12.4])
hinh("11_loi_hs_nhap.png", "Sổ có lỗi học sinh: bốn lỗi, mỗi lỗi chỉ đúng dòng và ô; chưa nạp gì.")
muc("5.3. Thiếu nguyện vọng và huy chương xung đột — nạp được, chặn khi chạy", 2)
gach("DC007 không khai nguyện vọng nào (thiếu dữ liệu): cảnh báo mức “Cần lưu ý”, không chặn.")
gach("DC009 đặt huy chương Vàng (60) cho hai CLB cùng buổi Thứ 3 (tiêu chí xung đột): cảnh báo “Nghiêm trọng”, "
     "chặn chạy cho đến khi sửa.")
x = SL["loi"]["thieu_xung_dot"]
bang("Cảnh báo sức khoẻ dữ liệu và lỗi khi chạy", ["Nơi báo", "Mức", "Mã", "Thông báo"],
     [("Xem cảnh báo", w.get("severity"), w["code"], loi_vi(w)) for w in x["health"]]
     + [("Chạy sắp xếp", "chặn", e["code"], loi_vi(e)) for e in x["run_errors"]], co=9, rong=[2.6, 1.6, 4.4, 8.0])
hop("Lần chạy bị chặn có ghi kết quả không? %s." % ("Có" if x["chay_duoc"] else
    "Không — không có dòng mới trong lịch sử chạy, dữ liệu giữ nguyên"), nen="EEF4F1", vien="1F4E3D", mau=MAU)
hinh("12_thieu_xung_dot_canh_bao.png", "Bước “Xem cảnh báo”: 1 nghiêm trọng (huy chương trùng), 1 cần lưu ý "
     "(học sinh không có nguyện vọng).", rong=14)
hinh("12b_thieu_xung_dot_chay_bi_chan.png", "Bấm “Chạy sắp xếp”: bước Kiểm tra dữ liệu báo lỗi, các bước sau "
     "không chạy; mục “Các lỗi cần xử lý” chỉ ra DC009.", rong=14)
muc("5.4. Xung đột giữa chế độ và dữ liệu đã nạp", 2)
doan("Nạp sổ khi đang ở chế độ mặc định (Chia 100 điểm, không chia loại): phần mềm báo đã bỏ qua các cột "
     "Loại / Điểm sàn. Sau đó bật chế độ Huy chương: phần mềm cảnh báo ngay rằng dữ liệu còn thiếu thứ chế "
     "độ này cần, và lần chạy bị chặn với các lỗi dưới đây (cách sửa: chọn Loại cho từng CLB ở bảng hiện ra, "
     "hoặc nạp lại sổ khi đã bật chế độ).")
errs = SL["loi"]["xung_dot_che_do"]["run_errors"]
gop = {}
for e in errs:
    gop.setdefault(e["code"], []).append(e)
bang("Lỗi khi chạy ở chế độ Huy chương với dữ liệu nạp ở chế độ khác",
     ["Mã lỗi", "Số lần", "Ví dụ thông báo"], [(k, len(v), loi_vi(v[0])) for k, v in gop.items()], co=9, rong=[4.0, 1.4, 11.2])
hinh("13_xung_dot_che_do_nap.png", "Nạp ở chế độ mặc định: dòng vàng báo 14 CLB có cột bị bỏ qua.")
hinh("13b_xung_dot_che_do_bat_huy_chuong.png", "Bật Huy chương sau khi nạp: cảnh báo thiếu Loại / CLB Tự do và "
     "bảng chọn loại cho từng CLB.", rong=13)

# ------------------------------------------------------------------ 6. Phần học sinh tự viết
muc("6. Nhận xét và kết luận (học sinh tự viết)", 1)
hop("Theo quy định liêm chính học thuật của dự án, phần nhận xét, diễn giải số liệu và kết luận do học sinh tự "
    "viết. Các câu hỏi gợi ý:", nen="EEF4F1", vien="1F4E3D", dam=False, mau=None)
for x in ("Vì sao tỷ lệ nguyện vọng 1 ở chế độ Chỉ xếp thứ tự khác các chế độ dùng điểm/huy chương?",
          "Đổi seed làm thay đổi bao nhiêu chỗ? Điều đó nói gì về vai trò của bốc thăm khi các em bằng nhau?",
          "Thông báo lỗi ở mục 5 có đủ rõ để người nhập tự sửa không?"):
    gach(x)
for _ in range(10):
    p = doc.add_paragraph()
    vien_duoi(p, "B7C4BE", 4)
    p.paragraph_format.space_after = Pt(14)

doc.save(RA)
print(RA, "· hình:", SO_HINH[0], "· bảng:", SO_BANG[0])
