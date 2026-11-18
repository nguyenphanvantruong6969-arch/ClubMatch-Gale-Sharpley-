"""Dựng gói minh chứng `GOI_MINH_CHUNG.docx` và `GOI_MINH_CHUNG.pdf` từ các tệp `docs/giai_trinh/*.md`.

Chạy: python docs/giai_trinh/tao_goi_minh_chung.py
- `.docx`: python-docx (đã có trong requirements-dev.txt; thiếu thì bỏ riêng .docx, .pdf vẫn dựng).
- `.pdf`: Chromium in từ một trang HTML tự đủ (Playwright; thiếu Chromium thì bỏ riêng .pdf).
Không có thư viện Markdown: chỉ đọc đúng phần cú pháp mà các tệp này dùng (tiêu đề, trích dẫn, bảng, danh sách,
khối mã, đoạn văn; in đậm và mã nội dòng). Gói chỉ GỘP các tệp, không thêm nhận xét hay kết luận.
Dữ liệu trong gói là dữ liệu MÔ PHỎNG; dòng cảnh báo nằm ở đầu gói.
"""

import html
import os
import re
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
# Thứ tự đọc: luồng -> dữ liệu -> chạy -> ca mẫu -> vai trò AI -> phân công -> kịch bản.
THU_TU = ["SO_DO_LUONG.md", "DU_LIEU_DAU_VAO.md", "HUONG_DAN_CHAY.md", "CA_MAU.md", "VAI_TRO_AI.md",
          "PHAN_CONG.md", "KICH_BAN_VIDEO.md", "KICH_BAN_DEMO.md"]
TIEU_DE = "Gói minh chứng — phần mềm xếp câu lạc bộ"
CANH_BAO = ("DỮ LIỆU MÔ PHỎNG: mọi tên, điểm và số liệu trong gói do máy sinh (hạt giống cố định); "
            "không phải học sinh hay khảo sát thật.")
DUONG_DOCX = os.path.join(THU_MUC, "GOI_MINH_CHUNG.docx")
DUONG_PDF = os.path.join(THU_MUC, "GOI_MINH_CHUNG.pdf")
DUONG_SVG = os.path.join(THU_MUC, "so_do_luong.svg")


# ------------------------------------------------------------------------------------------ đọc Markdown
def doc_khoi(van_ban: str) -> list:
    """-> [("h", cấp, chữ) | ("q", chữ) | ("bang", [[ô]]) | ("li", chữ) | ("ma", chữ) | ("p", chữ)]."""
    khoi, dong, i = [], van_ban.splitlines(), 0
    while i < len(dong):
        d = dong[i]
        if d.startswith("```"):
            j, mau = i + 1, []
            while j < len(dong) and not dong[j].startswith("```"):
                mau.append(dong[j])
                j += 1
            khoi.append(("ma", "\n".join(mau)))
            i = j + 1
        elif re.match(r"^#{1,4}\s", d):
            cap = len(d) - len(d.lstrip("#"))
            khoi.append(("h", cap, d[cap:].strip()))
            i += 1
        elif d.startswith(">"):
            khoi.append(("q", d.lstrip("> ").rstrip()))
            i += 1
        elif d.startswith("|"):
            hang = []
            while i < len(dong) and dong[i].startswith("|"):
                o = [x.strip() for x in dong[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", x) for x in o):
                    hang.append(o)
                i += 1
            khoi.append(("bang", hang))
        elif re.match(r"^\s*([-*]|\d+\.)\s", d):
            khoi.append(("li", re.sub(r"^\s*([-*]|\d+\.)\s+", "", d)))
            i += 1
        elif d.strip():
            khoi.append(("p", d.strip()))
            i += 1
        else:
            i += 1
    return khoi


def _doan(chu: str):
    """Tách `chữ` thành [(đoạn, in_đậm, mã)] theo **đậm** và `mã`."""
    ra = []
    for m in re.finditer(r"\*\*(.+?)\*\*|`([^`]+)`|([^*`]+|[*`])", chu):
        if m.group(1) is not None:
            ra.append((m.group(1), True, False))
        elif m.group(2) is not None:
            ra.append((m.group(2), False, True))
        else:
            ra.append((m.group(3), False, False))
    return ra


def _html_dong(chu: str) -> str:
    ra = []
    for t, dam, ma in _doan(chu):
        t = html.escape(t)
        ra.append("<strong>%s</strong>" % t if dam else "<code>%s</code>" % t if ma else t)
    return "".join(ra)


# ------------------------------------------------------------------------------------------ HTML / PDF
def dung_html(cac_tep: list) -> str:
    ra = ["<!doctype html><html lang=\"vi\"><head><meta charset=\"utf-8\"><title>%s</title><style>" % html.escape(TIEU_DE),
          "body{font:11pt/1.5 'Segoe UI',Arial,sans-serif;color:#0f172a;background:#fff;margin:0;padding:0 8mm}",
          "h1{font-size:20pt;margin:1.2em 0 .4em;page-break-before:always}h1:first-of-type{page-break-before:avoid}",
          "h2{font-size:15pt;margin:1em 0 .3em}h3{font-size:12.5pt;margin:.9em 0 .3em}h4{font-size:11pt}",
          "blockquote{margin:.5em 0;padding:.3em .8em;border-left:3px solid #94a3b8;background:#f1f5f9}",
          "table{border-collapse:collapse;width:100%;margin:.5em 0;font-size:9.5pt}",
          "td,th{border:1px solid #94a3b8;padding:3px 6px;vertical-align:top;text-align:left}th{background:#e2e8f0}",
          "pre{background:#f1f5f9;padding:6px 8px;white-space:pre-wrap;font-size:9pt}code{font-family:Consolas,monospace;font-size:.92em}",
          "li{margin:.15em 0}.canh-bao{border:2px solid #b45309;background:#fef3c7;padding:6px 10px;font-weight:600}",
          "img{max-width:100%}</style></head><body>",
          "<h1>%s</h1><p class=\"canh-bao\">%s</p>" % (html.escape(TIEU_DE), html.escape(CANH_BAO))]
    ra.append("<h2>Mục lục</h2><ol>%s</ol>" % "".join(
        "<li>%s</li>" % html.escape(ten) for ten, _ in cac_tep))
    for ten, van_ban in cac_tep:
        ra.append("<!-- %s -->" % html.escape(ten))
        mo_li = False
        for k in doc_khoi(van_ban):
            if k[0] != "li" and mo_li:
                ra.append("</ul>")
                mo_li = False
            if k[0] == "h":
                ra.append("<h%d>%s</h%d>" % (k[1], _html_dong(k[2]), k[1]))
            elif k[0] == "q":
                ra.append("<blockquote>%s</blockquote>" % _html_dong(k[1]))
            elif k[0] == "bang":
                ra.append("<table>")
                for n, hang in enumerate(k[1]):
                    the = "th" if n == 0 else "td"
                    ra.append("<tr>%s</tr>" % "".join("<%s>%s</%s>" % (the, _html_dong(o), the) for o in hang))
                ra.append("</table>")
            elif k[0] == "li":
                if not mo_li:
                    ra.append("<ul>")
                    mo_li = True
                ra.append("<li>%s</li>" % _html_dong(k[1]))
            elif k[0] == "ma":
                ra.append("<pre>%s</pre>" % html.escape(k[1]))
            else:
                ra.append("<p>%s</p>" % _html_dong(k[1]))
        if mo_li:
            ra.append("</ul>")
        if ten == "SO_DO_LUONG.md" and os.path.exists(DUONG_SVG):
            ra.append("<img alt=\"Sơ đồ luồng\" src=\"so_do_luong.svg\">")
    ra.append("</body></html>")
    return "\n".join(ra)


def ghi_pdf(van_ban_html: str) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Thiếu playwright: bỏ qua .pdf")
        return False
    sys.path.insert(0, os.path.join(GOC, "tests"))
    try:
        from _trinh_duyet import CHROMIUM       # cùng cách tìm Chromium với các test giao diện
    except ImportError:
        CHROMIUM = None
    tam = os.path.join(THU_MUC, "_goi_minh_chung_tam.html")
    with open(tam, "w", encoding="utf-8") as f:
        f.write(van_ban_html)
    try:
        with sync_playwright() as pw:
            tr = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
            try:
                trang = tr.new_page()
                trang.goto("file://" + tam)
                trang.pdf(path=DUONG_PDF, format="A4", print_background=True,
                          margin={"top": "15mm", "bottom": "15mm", "left": "10mm", "right": "10mm"})
            finally:
                tr.close()
    except Exception as e:          # noqa: BLE001
        print("Không in được .pdf (%s: %s)" % (type(e).__name__, str(e).splitlines()[0] if str(e) else ""))
        return False
    finally:
        if os.path.exists(tam):
            os.remove(tam)
    return True


# ------------------------------------------------------------------------------------------ DOCX
def ghi_docx(cac_tep: list) -> bool:
    try:
        import docx
    except ImportError:
        print("Thiếu python-docx: bỏ qua .docx")
        return False

    def them_dong(doan_van, chu):
        for t, dam, ma in _doan(chu):
            r = doan_van.add_run(t)
            r.bold = dam or None
            if ma:
                r.font.name = "Consolas"

    tai_lieu = docx.Document()
    tai_lieu.add_heading(TIEU_DE, 0)
    them_dong(tai_lieu.add_paragraph(), "**%s**" % CANH_BAO)
    tai_lieu.add_heading("Mục lục", 1)
    for ten, _ in cac_tep:
        tai_lieu.add_paragraph(ten, style="List Number")
    for ten, van_ban in cac_tep:
        tai_lieu.add_page_break()
        for k in doc_khoi(van_ban):
            if k[0] == "h":
                tai_lieu.add_heading(re.sub(r"[*`]", "", k[2]), min(k[1], 4))
            elif k[0] == "q":
                them_dong(tai_lieu.add_paragraph(style="Intense Quote"), k[1])
            elif k[0] == "bang":
                if not k[1]:
                    continue
                n_cot = max(len(h) for h in k[1])
                b = tai_lieu.add_table(rows=len(k[1]), cols=n_cot)
                b.style = "Table Grid"
                for r, hang in enumerate(k[1]):
                    for c in range(n_cot):
                        o = b.cell(r, c)
                        them_dong(o.paragraphs[0], ("**%s**" % hang[c]) if r == 0 and c < len(hang) and hang[c]
                                  else (hang[c] if c < len(hang) else ""))
                tai_lieu.add_paragraph()
            elif k[0] == "li":
                them_dong(tai_lieu.add_paragraph(style="List Bullet"), k[1])
            elif k[0] == "ma":
                p = tai_lieu.add_paragraph()
                r = p.add_run(k[1])
                r.font.name = "Consolas"
            else:
                them_dong(tai_lieu.add_paragraph(), k[1])
    tai_lieu.save(DUONG_DOCX)
    return True


def doc_cac_tep() -> list:
    ra = []
    for ten in THU_TU:
        with open(os.path.join(THU_MUC, ten), encoding="utf-8") as f:
            ra.append((ten, f.read()))
    return ra


def main() -> int:
    cac_tep = doc_cac_tep()
    ok_docx = ghi_docx(cac_tep)
    ok_pdf = ghi_pdf(dung_html(cac_tep))
    print("docx:", DUONG_DOCX if ok_docx else "không dựng")
    print("pdf:", DUONG_PDF if ok_pdf else "không dựng")
    return 0 if ok_docx and ok_pdf else 1


if __name__ == "__main__":
    sys.exit(main())
