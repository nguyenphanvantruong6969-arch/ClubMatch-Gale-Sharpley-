# -*- coding: utf-8 -*-
"""DG1-L5: xuất báo cáo khoa học sang Word — `docs/nghien_cuu/DG1_BAO_CAO_KHOA_HOC.docx`.

    python du_lieu_test/danh_gia/xuat_bao_cao_docx.py

Nguồn DUY NHẤT là `DG1_BAO_CAO_KHOA_HOC.md` (do `viet_bao_cao.py` sinh từ JSON): không thêm, bớt số nào.
Hình SVG được chuyển sang PNG bằng Chromium (Word hiển thị SVG không ổn định); ô «HS» thành khung trống để học sinh viết.
Cần: pandoc, gói `playwright` + Chromium (`tests/_trinh_duyet.py`), `python-docx`.
"""

import os
import re
import subprocess
import sys
import tempfile

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
sys.path[:0] = [os.path.join(GOC, "tests")]

NC = os.path.join(GOC, "docs", "nghien_cuu")
MD = os.path.join(NC, "DG1_BAO_CAO_KHOA_HOC.md")
RA = os.path.join(NC, "DG1_BAO_CAO_KHOA_HOC.docx")


def svg_sang_png(thu_muc_anh, ra):
    from playwright.sync_api import sync_playwright
    from _trinh_duyet import CHROMIUM
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        pg = br.new_page(device_scale_factor=2)
        for t in sorted(os.listdir(thu_muc_anh)):
            if t.endswith(".svg"):
                pg.goto("file://" + os.path.join(thu_muc_anh, t))
                pg.emulate_media(color_scheme="light")
                pg.locator("svg").screenshot(path=os.path.join(ra, t[:-4] + ".png"))
        br.close()


def md_cho_word(md, thu_muc_png):
    md = re.sub(r"!\[([^\]]*)\]\(anh_dg1/([^)]+)\.svg\)", lambda m: "![](%s)" % os.path.join(thu_muc_png, m.group(2) + ".png"), md)
    md = re.sub(r"!\[([^\]]*)\]\(anh_dg1/([^)]+\.png)\)", lambda m: "![](%s)" % os.path.join(NC, "anh_dg1", m.group(2)), md)
    # ô học sinh: bỏ chú thích HTML, giữ chữ đã viết (hoặc dòng «để trống») và thêm vài dòng trống để viết tay
    md = re.sub(r"<!-- HS:\w+ BẮT ĐẦU[^>]*-->\n", "", md)
    md = re.sub(r"\n<!-- HS:\w+ KẾT THÚC -->", "\n>\n>  \n>\n>  ", md)
    # ảnh: không để pandoc lấy alt làm chú thích thứ hai (chú thích *Hình k* đã có ngay dưới)
    return md


def chinh_trang(duong):
    import docx
    from docx.enum.section import WD_ORIENT
    from docx.shared import Cm, Pt
    d = docx.Document(duong)
    for s in d.sections:
        s.orientation = WD_ORIENT.LANDSCAPE
        s.page_width, s.page_height = Cm(29.7), Cm(21.0)
        for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(s, m, Cm(1.9))
    rong = Cm(29.7 - 3.8)
    for sh in d.inline_shapes:
        if sh.width > rong:
            h = int(sh.height * rong / sh.width)
            sh.width, sh.height = rong, h
    for tb in d.tables:
        for r in tb.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9)
    d.save(duong)


def main():
    with open(MD, encoding="utf-8") as f:
        md = f.read()
    tam = tempfile.mkdtemp(prefix="dg1_docx_")
    svg_sang_png(os.path.join(NC, "anh_dg1"), tam)
    p = os.path.join(tam, "bc.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(md_cho_word(md, tam))
    subprocess.run(["pandoc", p, "-f", "markdown-implicit_figures", "-o", RA, "--metadata", "lang=vi"], check=True)
    chinh_trang(RA)
    print("Đã ghi", os.path.relpath(RA, GOC))
    return 0


if __name__ == "__main__":
    sys.exit(main())
