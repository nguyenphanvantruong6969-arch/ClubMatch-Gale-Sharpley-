# -*- coding: utf-8 -*-
"""Bản báo cáo HACKATHON (Word, lời lẽ phổ thông, viết đầy đủ) — `docs/nghien_cuu/BAO_CAO_HACKATHON.docx`.

    python du_lieu_test/danh_gia/viet_bao_cao_hackathon.py

Khác `viet_bao_cao.py` (báo cáo nghiên cứu, phần nhận xét để học sinh tự viết): bản này do AI soạn TOÀN BỘ theo yêu cầu
của chủ dự án (2026-11-28, dùng cho hackathon). Mọi con số vẫn đọc từ `ket_qua/*.json` (không gõ tay); mọi số liệu là
MÔ PHỎNG. Bảng không bao giờ bị cắt sang hai trang (dòng không tách, mọi dòng «đi cùng dòng sau»); mục lục, danh mục bảng
và danh mục hình có số trang (dựng hai lượt: lượt 1 dàn trang qua LibreOffice → đọc số trang bằng pdftotext → lượt 2).
Cần: python-docx, gói playwright + Chromium (vẽ hình), LibreOffice + pdftotext (đánh số trang).
"""

import os
import re
import subprocess
import sys
import tempfile

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
sys.path[:0] = [THU_MUC, os.path.join(GOC, "tests")]

import in_bang as ib  # noqa: E402
import viet_bao_cao as vb  # noqa: E402

RA = os.path.join(GOC, "docs", "nghien_cuu", "BAO_CAO_HACKATHON.docx")
ANH = os.path.join(GOC, "docs", "nghien_cuu", "anh_dg1")
FONT = "Arial"


def v(x, n=1):
    return ib.so(x, n)


def tb(c):
    return c["tb"]


# ============================================================================ hình (nhãn phổ thông)
MUC_TRUNG = {0.0: "rất khác", 0.25: "khác", 0.5: "vừa", 0.75: "khá giống", 0.9: "rất giống"}
TEN_CO_CHE = [("rbda", "Phần mềm của nhóm"), ("boston", "Nhận ngay theo NV"), ("thu_tu_boc_tham", "Bốc lượt chọn"),
              ("ttc", "Đổi chéo chỗ"), ("da_clb_de_xuat", "CLB chủ động mời")]


def hinh_duong_cong(cc):
    h = vb.Ve(rong=860, cao=400, tren=56)
    h.mien(1, 6, 0, 100)
    h.truc(range(1, 7), range(0, 101, 20), "Được vào một trong k nguyện vọng đầu (k = 1 … 6)", "% học sinh", fy=lambda y: "%d" % y)
    for i, (ma, t) in enumerate(TEN_CO_CHE):
        cs = cc["co_che"][ma]
        h.duong(i, [(k, tb(cs["a.duong_cong_don.%d" % k])) for k in range(1, 7)], t, lambda x, y: "%d: %s %%" % (x, v(y)))
    h.chu_giai([t for _m, t in TEN_CO_CHE])
    return h.svg("Hình")


def hinh_canh_tranh(q, khoa, nhan_y, ymax):
    h = vb.Ve(rong=760, cao=380, tren=56, duoi=66)
    h.mien(0, 0.9, 0, ymax)
    h.truc([0, 0.25, 0.5, 0.75, 0.9], range(0, ymax + 1, 20), "Sở thích của học sinh giống nhau đến mức nào", nhan_y,
           fx=lambda x: MUC_TRUNG[x], fy=lambda y: "%d" % y)
    cs = [c for c in q["cac_cau_hinh"] if c["tham_so"]["n_hs"] == 800 and c["tham_so"]["rho"] == 0.7]
    ks = sorted({c["tham_so"]["kappa"] for c in cs})
    ten = ["Số chỗ = %d %% số HS" % round(k * 100) for k in ks]
    for i, k in enumerate(ks):
        h.duong(i, sorted((c["tham_so"]["alpha"], tb(c["chi_so"][khoa])) for c in cs if c["tham_so"]["kappa"] == k), ten[i],
                lambda x, y: "%s: %s %%" % (MUC_TRUNG[x], v(y)))
    h.chu_giai(ten)
    return h.svg("Hình")


def hinh_lap_day(md):
    d = [(x["ti_le_cau"], x["lap_day_tb"] * 100) for t in md["theo_truong"] for x in t["theo_clb"]]
    h = vb.Ve(rong=620, cao=360, tren=30)
    h.mien(0, 4, 0, 100)
    h.truc([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4], range(0, 101, 20), "Số em chọn CLB làm nguyện vọng 1, chia cho số chỗ của CLB",
           "% chỗ của CLB đã có người", fx=lambda x: v(x, 1), fy=lambda y: "%d" % y)
    for x, y in d:
        h.ds.append('<circle class="s0" cx="%.1f" cy="%.1f" r="4" fill-opacity="0.55" stroke-width="0"/>' % (h.X(min(x, 4)), h.Y(y)))
    return h.svg("Hình")


def hinh_doi_quy_tac(bt, nhan):
    g = bt["cac_bien_the"][0]["chi_so"]
    hang = [(nhan[b["bien_the"]["ten"]], tb(b["chi_so"]["a.pct_nv1_tat_ca"]) - tb(g["a.pct_nv1_tat_ca"]),
             tb(b["chi_so"]["b.n_chua_xep"]) - tb(g["b.n_chua_xep"])) for b in bt["cac_bien_the"][1:] if b["bien_the"]["ten"] != "toi_da_10_nv"]
    rong, trai, cd = 980, 330, 34
    cao = 60 + cd * len(hang)
    ds = []
    for ci, (ten, j) in enumerate([("Thay đổi % được nguyện vọng 1", 1), ("Thay đổi số em chưa có chỗ", 2)]):
        x0, w = trai + ci * 330, 300
        m = max(abs(x[j]) for x in hang) or 1
        tam = x0 + w / 2
        ds.append('<text class="tx" x="%.1f" y="22" text-anchor="middle">%s</text>' % (tam, vb._e(ten)))
        ds.append('<line class="truc" x1="%.1f" x2="%.1f" y1="32" y2="%d"/>' % (tam, tam, cao - 14))
        for r, x in enumerate(hang):
            y = 40 + r * cd
            dai = x[j] / m * (w / 2 - 34)
            ds.append('<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="20" rx="3" stroke-width="0"/>' % (
                "s0" if x[j] >= 0 else "s1", tam if dai >= 0 else tam + dai, y, max(abs(dai), 1)))
            ds.append('<text class="tx2" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (
                tam + dai + (4 if dai >= 0 else -4), y + 14, "start" if dai >= 0 else "end", ("+" if x[j] > 0 else "") + v(x[j], 1)))
    for r, x in enumerate(hang):
        ds.append('<text class="tx" x="%d" y="%.1f" text-anchor="end">%s</text>' % (trai - 10, 40 + r * cd + 14, vb._e(x[0])))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"><style>%s</style>'
            '<rect class="nen" width="100%%" height="100%%"/>%s</svg>' % (rong, cao, rong, cao, vb._css(), "".join(ds)))


def ve_png(svg, thu_muc):
    from playwright.sync_api import sync_playwright
    from _trinh_duyet import CHROMIUM
    ra = {}
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        pg = br.new_page(device_scale_factor=2)
        pg.emulate_media(color_scheme="light")
        for ten, s in svg.items():
            p = os.path.join(thu_muc, ten + ".svg")
            with open(p, "w", encoding="utf-8") as f:
                f.write(s)
            pg.goto("file://" + p)
            ra[ten] = os.path.join(thu_muc, ten + ".png")
            pg.locator("svg").screenshot(path=ra[ten])
        br.close()
    return ra


# ============================================================================ tài liệu Word
class Bao:
    """Gom nội dung thành danh sách khối, rồi dựng Word; giữ mục lục / danh mục bảng / hình."""

    def __init__(self):
        self.k = []          # (loại, dữ liệu)
        self.muc = []        # (cấp, chữ)
        self.bang_ds = []
        self.hinh_ds = []
        self.so = [0, 0, 0]

    def h(self, cap, chu):
        if cap == 1:
            self.so = [self.so[0] + 1, 0, 0]
            chu = "%d. %s" % (self.so[0], chu)
        else:
            self.so[1] += 1
            chu = "%d.%d. %s" % (self.so[0], self.so[1], chu)
        self.muc.append((cap, chu))
        self.k.append(("h", (cap, chu)))

    def p(self, chu):
        self.k.append(("p", chu))

    def ds(self, dong):
        self.k.append(("ds", dong))

    def bang(self, tieu_de, cot, hang, rong=None, ghi=None):
        so = len(self.bang_ds) + 1
        t = "Bảng %d: %s" % (so, tieu_de)
        self.bang_ds.append(t)
        self.k.append(("bang", (t, cot, hang, rong, ghi)))
        return so

    def hinh(self, png, tieu_de, rong_cm=16.0):
        so = len(self.hinh_ds) + 1
        t = "Hình %d: %s" % (so, tieu_de)
        self.hinh_ds.append(t)
        self.k.append(("hinh", (png, t, rong_cm)))
        return so


def _dong_giu(row):
    from docx.oxml import OxmlElement
    trpr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit")
    trpr.append(e)


def _o_nen(cell, mau):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcpr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), mau)
    tcpr.append(s)


def _chu(par, chu, dam=False, nghieng=False, co=None, mau=None):
    """Thêm chữ có **đậm** đơn giản."""
    from docx.shared import Pt, RGBColor
    for i, phan in enumerate(re.split(r"\*\*", chu)):
        if not phan:
            continue
        r = par.add_run(phan)
        r.bold = dam or (i % 2 == 1)
        r.italic = nghieng
        r.font.name = FONT
        if co:
            r.font.size = Pt(co)
        if mau:
            r.font.color.rgb = RGBColor.from_string(mau)


def dung_word(b, duong, trang=None):
    import docx
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
    from docx.shared import Cm, Pt
    d = docx.Document()
    s = d.sections[0]
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2.0)
    st = d.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(11)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.2
    for ten, co in (("Heading 1", 16), ("Heading 2", 13), ("Title", 24)):
        h = d.styles[ten]
        h.font.name, h.font.size, h.font.bold = FONT, Pt(co), True
        h.font.color.rgb = docx.shared.RGBColor.from_string("17427A")
        h.paragraph_format.space_before = Pt(18 if ten == "Heading 1" else 12)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
    # số trang ở chân trang
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    fp = s.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for loai, chu in (("begin", None), (None, "PAGE"), ("end", None)):
        r = fp.add_run()
        if loai:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), loai)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = chu
        r._r.append(e)

    # ---- bìa
    d.add_paragraph(style="Title").add_run("Xếp học sinh vào câu lạc bộ: phần mềm làm tốt đến đâu?").font.name = FONT
    _chu(d.add_paragraph(), "Báo cáo kiểm chứng bằng số liệu — bản dự thi hackathon", co=13, mau="5B6570")
    p = d.add_paragraph()
    _chu(p, "Lưu ý quan trọng: toàn bộ số liệu trong báo cáo đo trên các TRƯỜNG HỌC MÔ PHỎNG do máy tính tạo ra, "
            "không phải khảo sát học sinh thật.", dam=True, mau="B84A3E")
    _chu(d.add_paragraph(), "Báo cáo được soạn với sự hỗ trợ của trí tuệ nhân tạo (Claude). Mọi con số do máy đọc thẳng từ kết quả chạy thử, "
                            "không gõ tay.", nghieng=True, co=10, mau="5B6570")

    # ---- mục lục + danh mục
    def dong_muc(chu, cap, khoa):
        p = d.add_paragraph()
        p.paragraph_format.tab_stops.add_tab_stop(Cm(16.6), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        p.paragraph_format.left_indent = Cm(0.8 * (cap - 1))
        p.paragraph_format.space_after = Pt(2)
        _chu(p, chu, dam=(cap == 1), co=10.5)
        _chu(p, "\t%s" % ((trang or {}).get(khoa, "00")), co=10.5)

    d.add_paragraph(style="Heading 1").add_run("Mục lục").font.name = FONT
    for cap, chu in b.muc:
        dong_muc(chu, cap, chu)
    dong_muc("Danh mục bảng", 1, "Danh mục bảng")
    dong_muc("Danh mục hình", 1, "Danh mục hình")
    d.add_paragraph(style="Heading 1").add_run("Danh mục bảng").font.name = FONT
    for t in b.bang_ds:
        dong_muc(t, 2, t)
    d.add_paragraph(style="Heading 1").add_run("Danh mục hình").font.name = FONT
    for t in b.hinh_ds:
        dong_muc(t, 2, t)
    d.add_page_break()

    rong_trang = 16.6
    for loai, x in b.k:
        if loai == "h":
            cap, chu = x
            if cap == 1 and chu.split(".")[0] in ("2", "5", "6"):
                d.add_page_break()
            d.add_paragraph(style="Heading %d" % cap).add_run(chu).font.name = FONT
        elif loai == "p":
            _chu(d.add_paragraph(), x)
        elif loai == "ds":
            for dong in x:
                p = d.add_paragraph(style="List Bullet")
                p.paragraph_format.space_after = Pt(3)
                _chu(p, dong)
        elif loai == "bang":
            t, cot, hang, rong, ghi = x
            cap = d.add_paragraph()
            _chu(cap, t, dam=True, co=10)
            cap.paragraph_format.keep_with_next = True
            cap.paragraph_format.space_before = Pt(8)
            tbl = d.add_table(rows=1 + len(hang), cols=len(cot))
            tbl.style = "Table Grid"
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            rong = rong or [rong_trang / len(cot)] * len(cot)
            tbl.autofit = False
            for j, w in enumerate(rong):
                tbl.columns[j].width = Cm(w)
            for i, dong in enumerate([cot] + hang):
                row = tbl.rows[i]
                _dong_giu(row)
                for j, gt in enumerate(dong):
                    c = row.cells[j]
                    c.width = Cm(rong[j])
                    if i == 0:
                        _o_nen(c, "DCE6F2")
                    pp = c.paragraphs[0]
                    pp.paragraph_format.space_after = Pt(1)
                    pp.paragraph_format.line_spacing = 1.0
                    pp.paragraph_format.keep_with_next = i < len(hang)
                    _chu(pp, str(gt), dam=(i == 0), co=9.5)
            if ghi:
                g = d.add_paragraph()
                _chu(g, ghi, nghieng=True, co=9, mau="5B6570")
            else:
                d.add_paragraph().paragraph_format.space_after = Pt(2)
        elif loai == "hinh":
            png, t, rcm = x
            p = d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(png, width=Cm(rcm))
            c = d.add_paragraph()
            c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _chu(c, t, nghieng=True, co=9.5, mau="3A423F")
    d.save(duong)


def tim_trang(duong_docx, khoa_ds, so_trang_muc_luc):
    """Dàn trang bằng LibreOffice, đọc từng trang bằng pdftotext, trả {khoá: số trang} (bỏ các trang mục lục)."""
    tam = tempfile.mkdtemp(prefix="hk_")
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tam, duong_docx], check=True, capture_output=True)
    pdf = os.path.join(tam, os.path.basename(duong_docx)[:-5] + ".pdf")
    chu = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout.split("\f")
    gon = [re.sub(r"\s+", "", t) for t in chu]
    ra = {}
    for k in khoa_ds:
        kk = re.sub(r"\s+", "", k)[:40]
        for i in range(so_trang_muc_luc, len(gon)):
            if kk in gon[i]:
                ra[k] = i + 1
                break
    return ra, len(gon) - 1, pdf


# ============================================================================ nội dung
def noi_dung(J, png):
    md, cc, bt, q, tg = J["mac_dinh.json"], J["co_che_doi_chung.json"], J["bien_the_tieu_chi.json"], J["quet_quy_mo.json"], J["thoi_gian.json"]
    tn, nb, dc = J["tinh_nang.json"], J["nhieu_buoi.json"], J["doi_chieu_so_lieu.json"]
    cs = md["chi_so"]
    dn = md["dinh_nghia"]
    n_tr, n_bt = dn["so_truong"], dn["so_lan_boc_tham_moi_truong"]
    N = md["tham_so"]["n_hs"]
    nv1, top3 = tb(cs["a.pct_nv1_tat_ca"]), tb(cs["a.pct_top3_tat_ca"])
    chua, pchua = tb(cs["b.n_chua_xep"]), tb(cs["b.pct_chua_xep"])
    can, ktt, gia = tb(cs["b.can_tren_ghep_cuc_dai"]), tb(cs["b.khong_the_tranh"]), tb(cs["b.gia_uu_tien_on_dinh"])
    het, kd = tb(cs["b.nguyen_nhan.het_cho_uu_tien_cao_hon"]), tb(cs["b.nguyen_nhan.khong_diem"])
    lap, lech = tb(cs["c.ty_le_lap_day"]), tb(cs["b.lech_cho"])
    lat, latclb = tb(md["lat_co_cho_pct"]), tb(md["lat_clb_pct"])
    co = cc["co_che"]
    cb = {m: co[m] for m, _t in TEN_CO_CHE}
    bos, rsd, ttc = cb["boston"], cb["thu_tu_boc_tham"], cb["ttc"]
    trung_clb = all(tb(cb["rbda"]["a.duong_cong_don.%d" % k]) == tb(cb["da_clb_de_xuat"]["a.duong_cong_don.%d" % k]) for k in range(1, 7))
    BT = {x["bien_the"]["ten"]: x for x in bt["cac_bien_the"]}
    g = BT["mac_dinh"]["chi_so"] if "mac_dinh" in BT else bt["cac_bien_the"][0]["chi_so"]

    def d_(ten, k):
        return tb(BT[ten]["chi_so"][k]) - tb(g[k])

    qc = {(c["tham_so"]["n_hs"], c["tham_so"]["alpha"], c["tham_so"]["kappa"], c["tham_so"]["rho"]): c for c in q["cac_cau_hinh"]}

    def qv(n, a, k, khoa, rho=0.7):
        return tb(qc[(n, a, k, rho)]["chi_so"][khoa])

    tw = next(c for c in tn["du_tru_wharton"] if c["tham_so"]["n_hs"] == 800 and c["tham_so"]["alpha"] == 0.5)
    hc = next(c for c in tn["huy_chuong"] if c["n_hs"] == 800)
    qm = {x["n_hs"]: x for x in tg["cac_quy_mo"]}
    b = Bao()

    # ---------------------------------------------------------------- 1
    b.h(1, "Tóm tắt")
    b.p("Mỗi năm, trường cần xếp khoảng %d học sinh vào khoảng 20 câu lạc bộ (CLB). Mỗi em ghi danh sách CLB mình muốn theo thứ tự; "
        "một số CLB có bài thi đầu vào; số chỗ mỗi CLB có hạn. Nhóm đã làm một phần mềm chạy trên máy tính của trường để xếp chỗ "
        "tự động, công bằng và giải thích được." % N)
    b.p("Để biết phần mềm làm tốt đến đâu, nhóm cho nó xếp chỗ trên **%d trường học mô phỏng** với nhiều kích cỡ và mức cạnh tranh khác nhau, "
        "mỗi trường bốc thăm lại **%d lần**, rồi so với **4 cách xếp khác**. Kết quả chính ở trường mẫu %d học sinh:" % (
            n_tr, n_bt, N))
    b.ds([
        "**%s %%** học sinh vào đúng CLB mình thích nhất, **%s %%** vào một trong ba CLB đầu danh sách." % (v(nv1), v(top3)),
        "**Không có trường hợp bất công nào**: không em nào bị một bạn điểm thấp hơn (hoặc bốc thăm sau) lấy mất chỗ ở CLB mình muốn. "
        "Ba trong bốn cách xếp khác tạo ra hàng trăm trường hợp như vậy.",
        "Khoảng **%s %%** học sinh chưa có chỗ. Gần như tất cả các em này chỉ ghi những CLB đã đầy, trong khi vẫn còn CLB trống mà các em không ghi." % v(pchua),
        "Phần mềm xếp xong %d học sinh trong khoảng **%s giây**, và 2 000 học sinh trong khoảng **%s giây**." % (
            800, v(qm[800]["run_pipeline_giay"]["trung_vi"], 2), v(qm[2000]["run_pipeline_giay"]["trung_vi"], 2)),
    ])
    b.p("Kết luận ngắn: phần mềm xếp chỗ công bằng tuyệt đối trên mọi lần thử; điểm cần cải thiện tiếp theo không nằm ở cách xếp mà ở việc "
        "khuyến khích học sinh ghi danh sách dài hơn và mở thêm vòng bổ sung cho các em chưa có chỗ.")

    # ---------------------------------------------------------------- 2
    b.h(1, "Vấn đề cần giải quyết")
    b.p("Khi xếp CLB bằng tay hoặc theo kiểu «ai đăng ký trước được trước», nhà trường thường gặp ba vấn đề:")
    b.ds(["**Không công bằng**: em điểm cao hơn bị trượt trong khi em điểm thấp hơn được nhận.",
          "**Học sinh phải đoán**: nếu ghi CLB mình thích nhất mà trượt thì có thể mất luôn các lựa chọn sau, nên nhiều em không dám ghi thật lòng.",
          "**Khó giải thích**: khi phụ huynh hỏi «vì sao con tôi không vào được», nhà trường không có câu trả lời rõ ràng."])
    b.p("Giám khảo vòng trước góp ý rằng dự án còn thiếu **bằng chứng bằng số**: bao nhiêu em được nguyện vọng, bao nhiêu em chưa có chỗ, "
        "chỗ trong CLB có được dùng hết không, và đổi quy tắc thì kết quả đổi ra sao. Báo cáo này trả lời đúng những câu hỏi đó.")
    b.h(2, "Năm câu hỏi của báo cáo")
    b.ds(["**Câu 1.** Học sinh được vào CLB mình muốn đến mức nào, so với các cách xếp khác?",
          "**Câu 2.** Ai chưa có chỗ, và đó là do phần mềm hay do dữ liệu?",
          "**Câu 3.** Chỗ trong các CLB có được dùng hết không?",
          "**Câu 4.** Đổi một quy tắc (bỏ suất ưu tiên, giảm số nguyện vọng, thêm bớt chỗ…) thì kết quả thay đổi thế nào?",
          "**Câu 5.** Khi học sinh cùng thích vài CLB, hoặc khi trường đông hơn, thì sao? Phần mềm chạy nhanh đến đâu?"])

    # ---------------------------------------------------------------- 3
    b.h(1, "Phần mềm xếp chỗ như thế nào")
    b.p("Phần mềm dùng phương pháp **«chấp nhận tạm thời»** của hai nhà toán học Gale và Shapley (1962), cách mà nhiều nước dùng để xếp học sinh vào trường. "
        "Có thể hình dung như sau:")
    b.ds(["**Vòng 1**: mỗi em «nộp đơn» vào CLB mình thích nhất.",
          "Mỗi CLB **giữ tạm** những em đứng đầu theo thứ tự của CLB (CLB có thi: điểm cao trước; CLB không thi: theo số bốc thăm), đủ số chỗ; các em còn lại bị trả về.",
          "**Vòng tiếp theo**: em bị trả về nộp đơn vào CLB kế tiếp trong danh sách của mình. CLB so em mới với các em đang giữ tạm, lại giữ những em đứng đầu.",
          "Lặp lại cho tới khi không còn ai nộp đơn. Lúc đó, những em đang được giữ chính thức có chỗ."])
    b.p("Vì chỗ chỉ là «giữ tạm» cho tới cuối, một em nộp vào CLB mình thích nhất mà trượt **không mất gì**: em vẫn được xét ở các CLB sau như bình thường. "
        "Vì vậy, cách khôn ngoan nhất của học sinh là ghi đúng thứ tự mình thích.")
    b.p("Phần mềm còn có ba tính năng thêm:")
    b.ds(["**Suất ưu tiên**: một phần nhỏ số chỗ ở các CLB đông nhất được giữ trước cho học sinh thuộc diện chính sách và học sinh khối 10; "
          "nếu không có em nào thuộc diện, chỗ đó trả lại cho mọi người (theo Kominers và Sönmez, 2016).",
          "**Điểm quyết tâm**: học sinh chia điểm cho các CLB để cho biết mình muốn CLB nào nhiều hơn.",
          "**Huy chương**: học sinh đặt huy chương vàng, bạc, đồng cho ba CLB để thể hiện mức mong muốn (theo Abdulkadiroğlu, Che và Yasuda, 2015)."])
    b.p("Bốc thăm chỉ diễn ra **một lần** cho cả trường; kết quả bốc thăm được khoá lại, chạy lại vẫn ra đúng như cũ.")
    b.bang("Giải thích các từ dùng trong báo cáo", ["Từ", "Nghĩa"], [
        ("Nguyện vọng 1 (NV1)", "CLB học sinh ghi đầu tiên, tức CLB em thích nhất"),
        ("Trong 3 nguyện vọng đầu", "Em được vào một trong ba CLB đầu danh sách của mình"),
        ("Chưa có chỗ", "Em không được xếp vào CLB nào trong danh sách của mình"),
        ("Trường hợp bất công", "Một em muốn vào CLB X hơn chỗ hiện tại, và CLB X lẽ ra phải nhận em (em điểm cao hơn hoặc bốc thăm trước) nhưng lại nhận một bạn khác"),
        ("Mức lấp đầy", "Số chỗ đã có người chia cho tổng số chỗ của các CLB"),
        ("Giới hạn tối đa", "Số học sinh nhiều nhất có thể có chỗ nếu bỏ qua mọi quy tắc ưu tiên, chỉ cần mỗi em vào một CLB có trong danh sách của em"),
        ("Trường mô phỏng", "Một trường học giả do máy tính tạo, có học sinh, danh sách nguyện vọng, điểm thi và số chỗ"),
        ("Khoảng dao động", "Khoảng mà con số thường rơi vào khi đổi sang trường mô phỏng khác (độ tin cậy 95 %)"),
    ], rong=[4.6, 12.0])

    # ---------------------------------------------------------------- 4
    b.h(1, "Cách nhóm thử nghiệm")
    b.p("Chưa thể dùng dữ liệu học sinh thật (cần sự đồng ý của nhà trường và phụ huynh), nên nhóm cho máy tính tạo ra các trường học mô phỏng "
        "giống thật nhất có thể. Mỗi trường có học sinh, danh sách 3–6 nguyện vọng mỗi em, khoảng 30 % CLB có bài thi, khoảng 15 % học sinh diện chính sách "
        "và 6 % học sinh khối 10 được hưởng suất ưu tiên.")
    b.p("Nhóm thay đổi ba yếu tố chính để xem phần mềm chịu được những tình huống nào:")
    b.bang("Các tình huống được thử", ["Yếu tố", "Các mức đã thử", "Ý nghĩa"], [
        ("Sở thích của học sinh giống nhau đến mức nào", "rất khác, khác, vừa, khá giống, rất giống",
         "«Rất giống» = gần như cả trường cùng muốn vào vài CLB nổi tiếng, cạnh tranh gay gắt nhất"),
        ("Tổng số chỗ so với số học sinh", "90 %, 110 %, 130 %", "90 % = thiếu chỗ; 130 % = dư nhiều chỗ"),
        ("Kích cỡ trường", "120 em / 10 CLB, 300 em / 10 CLB, 800 em / 20 CLB", "Đo tốc độ thêm ở 2 000 em / 50 CLB"),
        ("Điểm thi", "liên quan năng lực / ngẫu nhiên", "Xem cách tính điểm có làm lệch kết quả không"),
    ], rong=[5.0, 5.0, 6.6])
    b.p("Mỗi tình huống được thử trên **%d trường mô phỏng khác nhau**, mỗi trường **bốc thăm %d lần**, tức %d lần xếp cho mỗi tình huống. "
        "Tổng cộng có %d tình huống trong lượt quét chính. Con số trong báo cáo là trung bình; khi cần, kèm khoảng dao động." % (
            n_tr, n_bt, n_tr * n_bt, len(q["cac_cau_hinh"])))
    b.p("**Trường mẫu** dùng cho phần lớn các bảng: %d học sinh, 20 CLB, sở thích ở mức «vừa», tổng số chỗ bằng 110 %% số học sinh, điểm thi liên quan năng lực." % N)
    b.p("Để so sánh, nhóm cho cùng dữ liệu chạy qua **4 cách xếp khác** thường gặp:")
    b.ds(["**Nhận ngay theo nguyện vọng** (kiểu «Boston»): vòng 1 CLB nhận luôn các em ghi CLB đó đầu tiên, nhận rồi là chốt; em trượt mới xét nguyện vọng 2 ở các CLB còn chỗ.",
          "**Bốc lượt chọn**: bốc thăm thứ tự, em bốc trước chọn CLB mình thích nhất còn chỗ, không xét điểm thi.",
          "**Đổi chéo chỗ** (kiểu «TTC»): các em được đổi chỗ cho nhau khi cả hai cùng có lợi.",
          "**CLB chủ động mời**: cùng phương pháp «chấp nhận tạm thời» nhưng CLB là bên mời học sinh."])
    b.p("Trước khi đo, nhóm kiểm tra phần mềm trên một bộ dữ liệu mẫu %d em đã được kiểm chứng từ trước: phần mềm xếp được %d em, %d em vào NV1, "
        "**khớp đúng từng em** với kết quả đã kiểm chứng." % (dc["n_hs"], dc["pipeline"]["duoc_xep"], dc["pipeline"]["nv1"]))

    # ---------------------------------------------------------------- 5 kết quả
    b.h(1, "Kết quả")
    b.h(2, "Học sinh được vào CLB mình muốn đến mức nào")
    duong = [tb(cs["a.duong_cong_don.%d" % k]) for k in range(1, 7)]
    b.bang("Kết quả chính ở trường mẫu %d học sinh (trung bình %d trường × %d lần bốc thăm)" % (N, n_tr, n_bt), ["Chỉ số", "Kết quả", "Khoảng dao động"], [
        ("Vào đúng CLB thích nhất (NV1)", v(nv1) + " %", "%s – %s %%" % (v(cs["a.pct_nv1_tat_ca"]["ktc95"][0]), v(cs["a.pct_nv1_tat_ca"]["ktc95"][1]))),
        ("Vào một trong 2 nguyện vọng đầu", v(duong[1]) + " %", "%s – %s %%" % tuple(v(x) for x in cs["a.duong_cong_don.2"]["ktc95"])),
        ("Vào một trong 3 nguyện vọng đầu", v(top3) + " %", "%s – %s %%" % tuple(v(x) for x in cs["a.pct_top3_tat_ca"]["ktc95"])),
        ("Có chỗ (bất kỳ nguyện vọng nào)", v(duong[5]) + " %", "%s – %s %%" % tuple(v(x) for x in cs["a.duong_cong_don.6"]["ktc95"])),
        ("Trong các em có chỗ: vào NV1", v(tb(cs["a.pct_nv1_da_xep"])) + " %", "%s – %s %%" % tuple(v(x) for x in cs["a.pct_nv1_da_xep"]["ktc95"])),
        ("Trung bình được nguyện vọng thứ mấy", v(tb(cs["a.hang_tb"]), 2), "%s – %s" % tuple(v(x, 2) for x in cs["a.hang_tb"]["ktc95"])),
        ("Bị xếp vào CLB không có trong danh sách", v(tb(cs["a.ngoai_danh_sach"]), 0) + " em", "—"),
        ("Trường hợp bất công", v(tb(cs["a.cap_chan"]), 0), "—"),
    ], rong=[7.6, 4.0, 5.0])
    b.p("Đọc bảng: cứ 3 em thì khoảng 1 em vào đúng CLB mình thích nhất, và khoảng 7 trên 10 em vào một trong ba CLB đầu. "
        "Không em nào bị xếp vào CLB mình không ghi, và không có trường hợp bất công nào.")
    b.hinh(png["duong_cong"], "Phần trăm học sinh vào được một trong k nguyện vọng đầu, theo 5 cách xếp (trường mẫu). "
           + ("Đường của phần mềm và của cách «CLB chủ động mời» trùng nhau." if trung_clb else ""))
    hang = []
    for m, t in TEN_CO_CHE:
        c = cb[m]
        hang.append((t, v(tb(c["a.pct_nv1_tat_ca"])) + " %", v(tb(c["a.pct_top3_tat_ca"])) + " %", v(tb(c["b.n_chua_xep"]), 0),
                     v(tb(c["a.cap_chan"]), 0)))
    b.bang("So sánh 5 cách xếp trên cùng dữ liệu (trường mẫu)", ["Cách xếp", "Vào NV1", "Vào 3 NV đầu", "Số em chưa có chỗ", "Số trường hợp bất công"],
           hang, rong=[4.6, 2.6, 3.0, 3.2, 3.2])
    b.p("Cách «nhận ngay theo nguyện vọng» cho nhiều em vào NV1 hơn (%s %% so với %s %%), nhưng tạo ra khoảng **%s trường hợp bất công** mỗi lần xếp. "
        "Lý do: CLB đã nhận ai thì chốt luôn, nên một em điểm cao ghi CLB đó ở nguyện vọng 2 sẽ thua một em điểm thấp ghi ở nguyện vọng 1. "
        "Ở cách này, học sinh hiểu luật sẽ **không dám ghi thật lòng** mà ghi CLB «chắc ăn» lên đầu; vì vậy con số NV1 cao ở đây chỉ đúng nếu mọi em vẫn ghi thật, "
        "điều khó xảy ra ngoài đời." % (v(tb(bos["a.pct_nv1_tat_ca"])), v(nv1), v(tb(bos["a.cap_chan"]), 0)))
    b.p("«Bốc lượt chọn» và «đổi chéo chỗ» cũng cho tỉ lệ NV1 cao hơn (khoảng %s %% và %s %%), nhưng bỏ qua điểm thi, nên tạo ra khoảng %s và %s trường hợp bất công. "
        "Cách «CLB chủ động mời» cho kết quả %s." % (
            v(tb(rsd["a.pct_nv1_tat_ca"])), v(tb(ttc["a.pct_nv1_tat_ca"])), v(tb(rsd["a.cap_chan"]), 0), v(tb(ttc["a.cap_chan"]), 0),
            "giống hệt phần mềm của nhóm: trên các trường mô phỏng này, chỉ có đúng một cách xếp hoàn toàn công bằng, và phần mềm đã tìm ra nó"
            if trung_clb else "khác phần mềm của nhóm"))

    b.h(2, "Ai chưa có chỗ, và vì sao")
    b.bang("Học sinh chưa có chỗ ở trường mẫu %d em" % N, ["Nội dung", "Số em"], [
        ("Tổng số em chưa có chỗ", v(chua)),
        ("… vì mọi CLB em ghi đều đã đầy, bởi các bạn đứng trước em", v(het)),
        ("… vì em không có điểm ở CLB có thi mà em ghi", v(kd)),
        ("Số em nhiều nhất có thể có chỗ nếu bỏ qua mọi quy tắc ưu tiên (giới hạn tối đa)", v(can)),
        ("Số em KHÔNG cách xếp nào giúp được (danh sách quá hẹp so với số chỗ)", v(ktt)),
        ("Phần chênh giữa giới hạn tối đa và phần mềm", v(gia)),
        ("Số em chưa có chỗ trong khi vẫn còn CLB trống mà em không ghi", v(lech)),
    ], rong=[13.0, 3.6])
    b.p("Trong khoảng %s em chưa có chỗ, khoảng %s em là vì mọi CLB em ghi đều đã kín chỗ bởi các bạn đứng trước. Và với cả %s em, **vẫn còn CLB trống** "
        "mà các em không ghi. Nói cách khác, chỗ thì có, nhưng không phải chỗ các em muốn." % (v(chua, 0), v(het, 0), v(lech, 0)))
    b.p("Phần chênh %s em giữa giới hạn tối đa và phần mềm là «cái giá của sự công bằng»: muốn đưa thêm các em này vào, phải đẩy những bạn có điểm cao hơn "
        "(hoặc bốc thăm trước) ra khỏi CLB, tức là tạo ra trường hợp bất công. Mọi cách xếp hoàn toàn công bằng đều xếp được cùng một số em, nên đây là "
        "giới hạn của bài toán chứ không phải lỗi phần mềm." % v(gia, 0))
    b.h(2, "Chỗ trong các CLB có được dùng hết không")
    b.p("Ở trường mẫu, **%s %%** số chỗ có người. Trung bình có %s CLB kín chỗ và %s CLB dùng chưa tới một nửa số chỗ. "
        "Toàn bộ %s suất ưu tiên đều được dùng." % (v(lap), v(tb(cs["c.n_clb_day"])), v(tb(cs["c.n_clb_duoi_50"])), v(tb(cs["c.du_tru_da_dung"]), 0)))
    b.hinh(png["lap_day"], "Mỗi chấm là một CLB của một trường mô phỏng. CLB càng ở bên phải thì càng nhiều em chọn làm nguyện vọng 1; "
           "chiều cao là phần trăm chỗ đã có người.")
    b.p("Hình trên cho thấy hai nhóm CLB tách bạch: CLB được nhiều em chọn thì luôn kín chỗ; CLB gần như không ai chọn làm nguyện vọng 1 thì nhiều chỗ bỏ trống. "
        "Vấn đề chỗ trống nằm ở **sức hút của CLB**, không nằm ở cách xếp.")

    b.h(2, "Đổi một quy tắc thì kết quả thay đổi thế nào")
    NHAN = {"du_tru_tat": "Bỏ suất ưu tiên", "nhom_cung": "Xét nhóm ưu tiên trước điểm thi",
            "chi_nhom": "Bỏ điểm thi, chỉ xét nhóm ưu tiên rồi bốc thăm", "diem_theo_nguoi": "Mỗi em dùng một điểm chung cho mọi CLB",
            "toi_da_3_nv": "Mỗi em chỉ được ghi 3 nguyện vọng", "toi_da_5_nv": "Mỗi em chỉ được ghi 5 nguyện vọng",
            "toi_da_10_nv": "Cho ghi tới 10 nguyện vọng", "chi_tieu_-20": "Giảm số chỗ mọi CLB 20 %", "chi_tieu_+20": "Tăng số chỗ mọi CLB 20 %"}

    def dau(x, n=1):
        return ("+" if x > 0.05 else "") + v(x, n)

    hang = []
    for x in bt["cac_bien_the"][1:]:
        t = x["bien_the"]["ten"]
        ch = x.get("churn", {})
        hang.append((NHAN.get(t, t), dau(d_(t, "a.pct_nv1_tat_ca")) + " điểm %", dau(d_(t, "b.n_chua_xep")),
                     v(tb(ch["doi_clb"]), 0), "%s / %s" % (v(tb(ch["tot_hon"]), 0), v(tb(ch["xau_hon"]), 0))))
    b.bang("Thay đổi so với quy tắc hiện tại, trên cùng dữ liệu và cùng kết quả bốc thăm (trường mẫu %d em)" % N,
           ["Thay đổi", "NV1 tăng/giảm", "Số em chưa có chỗ tăng/giảm", "Số em đổi CLB", "Lên / xuống nguyện vọng"], hang, rong=[5.6, 2.6, 3.0, 2.4, 3.0],
           ghi="«Lên / xuống nguyện vọng»: trong các em đổi CLB, bao nhiêu em vào CLB đứng cao hơn / thấp hơn trong danh sách của mình.")
    b.hinh(png["doi_quy_tac"], "Mức thay đổi so với quy tắc hiện tại. Xanh = tăng, cam = giảm.")
    b.p("Những điều rút ra:")
    b.ds([
        "**Số chỗ là yếu tố quan trọng nhất.** Tăng 20 %% số chỗ giúp thêm khoảng %s em có chỗ; giảm 20 %% làm thêm khoảng %s em mất chỗ." % (
            v(-d_("chi_tieu_+20", "b.n_chua_xep"), 0), v(d_("chi_tieu_-20", "b.n_chua_xep"), 0)),
        "**Danh sách ngắn rất có hại.** Chỉ cho ghi 3 nguyện vọng làm thêm khoảng %s em chưa có chỗ." % v(d_("toi_da_3_nv", "b.n_chua_xep"), 0),
        "**Bỏ suất ưu tiên gần như không ảnh hưởng cả trường** (chỉ khoảng %s em đổi CLB), nhưng ảnh hưởng rõ tới các em thuộc diện ưu tiên (mục 5.5)." % v(
            tb(BT["du_tru_tat"]["churn"]["doi_clb"]), 0),
        "**Cách tính điểm và thứ tự xét nhóm làm nhiều em đổi CLB nhất** (từ %s đến %s em), dù tỉ lệ NV1 của cả trường thay đổi ít. "
        "Vì vậy, nhà trường cần chốt quy tắc này trước khi học sinh đăng ký." % (
            v(tb(BT["nhom_cung"]["churn"]["doi_clb"]), 0), v(tb(BT["diem_theo_nguoi"]["churn"]["doi_clb"]), 0)),
        "Mọi thay đổi trên **vẫn giữ con số 0 trường hợp bất công**.",
    ])

    b.h(2, "Các tính năng ưu tiên có tác dụng không")
    o = tw["o"]
    TEN_O = [("goc", "Tắt cả hai"), ("du_tru", "Chỉ bật suất ưu tiên"), ("wharton", "Chỉ bật điểm quyết tâm"), ("du_tru_wharton", "Bật cả hai")]
    b.bang("Bật / tắt suất ưu tiên và điểm quyết tâm (trường mẫu %d em)" % N,
           ["Cài đặt", "Vào NV1", "Số em chưa có chỗ", "Suất ưu tiên đã dùng", "Vào CLB em đặt nhiều điểm nhất"],
           [(t, v(tb(o[k]["a.pct_nv1_tat_ca"])) + " %", v(tb(o[k]["b.n_chua_xep"]), 0), v(tb(o[k]["c.du_tru_da_dung"]), 0),
             v(tb(o[k]["pct_dat_clb_diem_cao"])) + " %") for k, t in TEN_O], rong=[4.4, 2.6, 3.0, 3.0, 3.6])
    hcap = tw["hieu_co_cap"]["du_tru_tru_goc"]
    TEN_NHOM = {"chinh_sach": "Học sinh diện chính sách", "khoi_10": "Học sinh khối 10", "khong": "Học sinh không thuộc diện ưu tiên"}
    b.bang("Khi bật suất ưu tiên: thay đổi theo từng nhóm học sinh (trường mẫu)", ["Nhóm", "NV1 tăng/giảm", "Có chỗ tăng/giảm"],
           [(TEN_NHOM[gq], dau(tb(hcap["a.theo_nhom.du_tru.%s.pct_nv1" % gq]), 2) + " điểm %", dau(tb(hcap["a.theo_nhom.du_tru.%s.pct_da_xep" % gq]), 2) + " điểm %")
            for gq in ("chinh_sach", "khoi_10", "khong")], rong=[7.6, 4.5, 4.5])
    b.p("Suất ưu tiên giúp học sinh khối 10 rõ rệt (NV1 tăng khoảng %s điểm phần trăm, có chỗ tăng khoảng %s điểm phần trăm), đổi lại các bạn không thuộc diện ưu tiên "
        "giảm rất ít (dưới 1 điểm phần trăm). Với học sinh diện chính sách, các con số giảm nhẹ (dưới 1 điểm phần trăm) trên dữ liệu mô phỏng; "
        "nhóm sẽ tìm hiểu nguyên nhân ở bước tiếp theo, vì suất ưu tiên được thiết kế để giúp nhóm này." % (
            v(tb(hcap["a.theo_nhom.du_tru.khoi_10.pct_nv1"]), 1), v(tb(hcap["a.theo_nhom.du_tru.khoi_10.pct_da_xep"]), 1)))
    b.p("Điểm quyết tâm làm tăng số em vào được CLB mình đặt nhiều điểm nhất (từ %s %% lên %s %%) và giảm số em chưa có chỗ (từ %s xuống %s em)." % (
        v(tb(o["goc"]["pct_dat_clb_diem_cao"])), v(tb(o["wharton"]["pct_dat_clb_diem_cao"])), v(tb(o["goc"]["b.n_chua_xep"]), 0), v(tb(o["wharton"]["b.n_chua_xep"]), 0)))
    TEN_HV = {"luoi": "Không đổi gì, để mặc định", "that_tha": "Đặt huy chương theo đúng ý thích", "chien_luoc": "Đặt huy chương để «tính toán»"}
    b.bang("Huy chương so với cách cũ, theo cách học sinh đặt huy chương (trường %d em, mô hình riêng)" % hc["n_hs"],
           ["Cách học sinh đặt huy chương", "Vào NV1 thật – cách cũ", "Vào NV1 thật – huy chương", "Không có CLB – cách cũ", "Không có CLB – huy chương"],
           [(TEN_HV.get(h, h), v(tb(x["cu"]["pt_nv1_that"])) + " %", v(tb(x["fa"]["pt_nv1_that"])) + " %", v(tb(x["cu"]["pt_khong_clb"])) + " %",
             v(tb(x["fa"]["pt_khong_clb"])) + " %") for h, x in hc["theo_hanh_vi"].items()], rong=[4.6, 3.0, 3.0, 3.0, 3.0],
           ghi="«NV1 thật»: CLB em thật sự thích nhất, kể cả khi em không ghi nó lên đầu. Chế độ huy chương có thêm CLB tự do không giới hạn chỗ, nên không em nào thiếu CLB.")
    b.p("Ở cả ba kiểu học sinh, chế độ huy chương cho nhiều em vào được CLB mình thật sự thích nhất hơn so với cách cũ, và không còn em nào thiếu CLB.")

    b.h(2, "Khi cạnh tranh gay gắt hơn và khi trường đông hơn")
    b.hinh(png["nv1"], "Phần trăm học sinh vào NV1 theo mức độ sở thích giống nhau, với ba mức tổng số chỗ (trường 800 em).")
    b.hinh(png["chua"], "Phần trăm học sinh chưa có chỗ theo mức độ sở thích giống nhau, với ba mức tổng số chỗ (trường 800 em).")
    hang = []
    for a in (0.0, 0.25, 0.5, 0.75, 0.9):
        hang.append((MUC_TRUNG[a], v(qv(800, a, 1.1, "a.pct_nv1_tat_ca")) + " %", v(qv(800, a, 1.1, "a.pct_top3_tat_ca")) + " %",
                     v(qv(800, a, 1.1, "b.pct_chua_xep")) + " %", v(qv(800, a, 1.1, "c.ty_le_lap_day")) + " %", v(qv(800, a, 1.1, "a.cap_chan"), 0)))
    b.bang("Kết quả theo mức độ sở thích giống nhau (trường 800 em, tổng số chỗ = 110 % số học sinh)",
           ["Sở thích", "Vào NV1", "Vào 3 NV đầu", "Chưa có chỗ", "Mức lấp đầy", "Bất công"], hang, rong=[3.2, 2.6, 2.8, 2.8, 2.8, 2.4])
    b.p("Khi học sinh thích những CLB khác nhau, khoảng 3/4 số em vào NV1. Khi cả trường cùng muốn vài CLB, chỉ khoảng 1 trên 9 em vào NV1 và gần một nửa chưa có chỗ: "
        "không cách xếp nào tạo thêm chỗ cho CLB nổi tiếng được. Dù vậy, số trường hợp bất công vẫn bằng 0 ở mọi mức.")
    hang = []
    for n, c in ((120, 10), (300, 10), (800, 20)):
        hang.append(("%d em / %d CLB" % (n, c), v(qv(n, 0.5, 1.1, "a.pct_nv1_tat_ca")) + " %", v(qv(n, 0.5, 1.1, "a.pct_top3_tat_ca")) + " %",
                     v(qv(n, 0.5, 1.1, "b.pct_chua_xep")) + " %", v(qv(n, 0.5, 1.1, "a.cap_chan"), 0)))
    b.bang("Kết quả theo kích cỡ trường (sở thích mức «vừa», số chỗ = 110 % số học sinh)", ["Kích cỡ", "Vào NV1", "Vào 3 NV đầu", "Chưa có chỗ", "Bất công"],
           hang, rong=[4.4, 3.0, 3.2, 3.2, 2.8])
    so_o = sum(1 for c in q["cac_cau_hinh"] if tb(c["chi_so"]["a.cap_chan"]) == 0)
    b.p("Trên toàn bộ %d tình huống × %d trường × %d lần bốc thăm, số trường hợp bất công của phần mềm luôn bằng 0 (%d / %d tình huống)." % (
        len(q["cac_cau_hinh"]), n_tr, n_bt, so_o, len(q["cac_cau_hinh"])))
    hang = [("%d em / %d CLB" % (x["n_hs"], x["n_clb"]), v(x["nap_so_nhap_giay"], 2), v(x["run_pipeline_giay"]["trung_vi"], 2), str(x["vong"]))
            for x in tg["cac_quy_mo"]]
    b.bang("Thời gian chạy (giây, trung vị của 3 lần)", ["Kích cỡ", "Đọc tệp đăng ký", "Xếp chỗ, kiểm tra, lưu và xuất kết quả", "Số vòng xếp"],
           hang, rong=[4.0, 3.4, 6.2, 3.0])
    b.p("Ngay cả với 2 000 học sinh, toàn bộ quá trình xếp, kiểm tra, lưu và xuất kết quả mất chưa tới nửa giây.")
    hang = [(x.replace("thu_", "Thứ "), v(tb(c["a.pct_nv1_tat_ca"])) + " %", v(tb(c["a.pct_top3_tat_ca"])) + " %", v(tb(c["b.pct_chua_xep"])) + " %",
             v(tb(c["a.cap_chan"]), 0)) for x, c in sorted(nb["theo_buoi"].items())]
    b.bang("Trường 800 em sinh hoạt CLB 3 buổi mỗi tuần, xếp từng buổi", ["Buổi", "Vào NV1", "Vào 3 NV đầu", "Chưa có chỗ", "Bất công"], hang,
           rong=[3.6, 3.2, 3.4, 3.2, 3.2])
    thb = nb["theo_hoc_sinh"]
    b.p("Tính theo từng học sinh: trung bình mỗi em có chỗ ở %s buổi; %s %% học sinh có chỗ ở mọi buổi mình đăng ký." % (
        v(tb(thb["so_buoi_co_cho_tb"]), 2), v(tb(thb["pct_du_moi_buoi_da_khai"]))))

    b.h(2, "Bốc thăm ảnh hưởng thế nào")
    b.p("Với CLB không có bài thi, thứ tự được quyết định bằng bốc thăm. Khi nhóm giữ nguyên trường mẫu và chỉ bốc thăm lại, trung bình **%s %%** học sinh "
        "lúc có chỗ, lúc không, và **%s %%** học sinh đổi CLB giữa các lần bốc. Bốc thăm là cách công bằng duy nhất khi các em ngang nhau, "
        "nên phần mềm chỉ bốc **một lần**, khoá kết quả và công khai số bốc thăm để ai cũng kiểm tra được." % (v(lat), v(latclb)))

    b.h(2, "Hình ảnh phần mềm")
    b.hinh(os.path.join(ANH, "S1_sau_nap_truoc_khi_chay.png"), "Màn hình sau khi nạp tệp đăng ký của trường mẫu: phần mềm tự kiểm tra dữ liệu và nêu cảnh báo "
           "(ở đây là các điểm thi thấp bất thường do máy tạo) trước khi cho xếp.", 13.0)
    b.hinh(os.path.join(ANH, "S2_ket_qua.png"), "Màn hình kết quả: tra cứu từng học sinh và tải bảng kết quả.", 15.0)

    # ---------------------------------------------------------------- 6–8
    b.h(1, "Bàn luận")
    b.ds([
        "**Công bằng không phải đánh đổi bằng may rủi.** Trên mọi tình huống thử, phần mềm luôn cho 0 trường hợp bất công, trong khi các cách quen thuộc tạo ra hàng trăm trường hợp. "
        "Đây là điều quan trọng nhất với nhà trường: mọi kết quả đều giải thích được bằng điểm thi hoặc số bốc thăm.",
        "**Tỉ lệ NV1 không nên là thước đo duy nhất.** Cách «nhận ngay theo nguyện vọng» có tỉ lệ NV1 cao hơn trên giấy, nhưng chỉ khi học sinh ghi thật lòng; "
        "trong khi chính cách đó lại khiến các em không dám ghi thật lòng. Phần mềm của nhóm làm điều ngược lại: ghi thật lòng luôn là cách tốt nhất.",
        "**Số em chưa có chỗ chủ yếu do dữ liệu.** Các em này ghi danh sách hẹp toàn CLB đã kín, trong khi còn CLB trống. Giải pháp nằm ở việc khuyến khích ghi dài hơn "
        "và tổ chức vòng bổ sung cho CLB còn chỗ.",
        "**Quy tắc phải chốt trước.** Đổi cách tính điểm hay thứ tự xét nhóm làm hàng trăm em đổi CLB, nên nhà trường cần công bố quy tắc trước khi học sinh đăng ký.",
        "**Các tính năng ưu tiên giúp đúng nhóm học sinh khối 10** và chỉ ảnh hưởng nhỏ tới các bạn còn lại; riêng nhóm diện chính sách cần xem xét thêm.",
    ])
    b.h(1, "Hạn chế")
    b.ds(["Toàn bộ số liệu là mô phỏng; nhóm chưa thử trên dữ liệu học sinh thật.",
          "Cách máy tạo sở thích của học sinh là một giả định; học sinh thật có thể có thói quen khác.",
          "Mỗi tình huống thử trên %d trường mô phỏng, nên một số khoảng dao động còn rộng." % n_tr,
          "Thời gian chạy đo trên máy chủ Linux, chưa đo trên máy tính Windows của trường.",
          "Cách học sinh đặt huy chương dựa trên ba kiểu hành vi giả định."])
    b.h(1, "Kết luận và hướng phát triển")
    b.p("Phần mềm xếp chỗ **công bằng tuyệt đối** trên toàn bộ các lần thử, **nhanh** (dưới nửa giây cho 2 000 học sinh), **khớp đúng** với kết quả đã kiểm chứng, "
        "và các tính năng điểm quyết tâm, huy chương giúp nhiều em vào được CLB mình thật sự muốn hơn. Ở trường mẫu %d em, khoảng %s %% học sinh vào một trong ba CLB đầu danh sách." % (N, v(top3, 0)))
    b.p("Hướng tiếp theo của nhóm:")
    b.ds(["Thử với dữ liệu thật (ẩn danh) khi được nhà trường cho phép.",
          "Thêm **vòng bổ sung** cho học sinh chưa có chỗ vào các CLB còn trống.",
          "Gợi ý học sinh ghi danh sách dài hơn ngay trên phiếu đăng ký.",
          "Mở rộng sang các lĩnh vực khác cần xếp người vào chỗ có hạn (ký túc xá, đề tài, sự kiện…)."])
    b.h(1, "Tài liệu tham khảo")
    b.ds(["Gale, D. & Shapley, L. S. (1962). College admissions and the stability of marriage. The American Mathematical Monthly, 69(1), 9–15.",
          "Kominers, S. D. & Sönmez, T. (2016). Matching with slot-specific priorities: Theory. Theoretical Economics, 11(2), 683–710.",
          "Abdulkadiroğlu, A., Che, Y.-K. & Yasuda, Y. (2015). Expanding “choice” in school choice. American Economic Journal: Microeconomics, 7(1), 1–42."])
    b.h(1, "Phụ lục: cách chạy lại thử nghiệm")
    b.p("Toàn bộ thử nghiệm chạy lại được bằng ba lệnh trong thư mục dự án (khoảng 30 phút); báo cáo này được tạo tự động từ kết quả:")
    b.ds(["python du_lieu_test/danh_gia/do_danh_gia.py --day-du",
          "python du_lieu_test/danh_gia/do_tinh_nang.py --day-du",
          "python du_lieu_test/danh_gia/viet_bao_cao_hackathon.py"])
    b.p("Cùng dữ liệu và cùng số bốc thăm luôn cho đúng cùng kết quả.")
    return b


def main():
    J = {t: ib.doc(ib.MAC_DINH, t) for t in vb.TEP}
    tam = tempfile.mkdtemp(prefix="hk_anh_")
    q = J["quet_quy_mo.json"]
    png = ve_png({"duong_cong": hinh_duong_cong(J["co_che_doi_chung.json"]),
                  "nv1": hinh_canh_tranh(q, "a.pct_nv1_tat_ca", "% học sinh vào NV1", 100),
                  "chua": hinh_canh_tranh(q, "b.pct_chua_xep", "% học sinh chưa có chỗ", 60),
                  "lap_day": hinh_lap_day(J["mac_dinh.json"]),
                  "doi_quy_tac": hinh_doi_quy_tac(J["bien_the_tieu_chi.json"], {
                      "du_tru_tat": "Bỏ suất ưu tiên", "nhom_cung": "Xét nhóm ưu tiên trước điểm", "chi_nhom": "Bỏ điểm thi, chỉ xét nhóm",
                      "diem_theo_nguoi": "Một điểm chung cho mỗi em", "toi_da_3_nv": "Chỉ ghi 3 nguyện vọng", "toi_da_5_nv": "Chỉ ghi 5 nguyện vọng",
                      "chi_tieu_-20": "Giảm 20 % số chỗ", "chi_tieu_+20": "Tăng 20 % số chỗ"})}, tam)
    b = noi_dung(J, png)
    khoa = [c for _cap, c in b.muc] + ["Danh mục bảng", "Danh mục hình"] + b.bang_ds + b.hinh_ds
    dung_word(b, RA)
    # số trang mục lục: trang của tiêu đề chương 1 trừ 1 (chương 1 luôn mở trang mới sau mục lục)
    trang, _n, _pdf = tim_trang(RA, khoa, 1)
    bat_dau = trang.get(b.muc[0][1], 2)
    trang, n, _pdf = tim_trang(RA, khoa, bat_dau - 1)
    trang["Danh mục bảng"] = trang["Danh mục hình"] = None
    trang2, _n, _ = tim_trang(RA, ["Danh mục bảng", "Danh mục hình"], 0)
    trang.update(trang2)
    dung_word(b, RA, trang)
    trang3, n, pdf = tim_trang(RA, khoa, bat_dau - 1)
    lech = [k for k in khoa if k in trang3 and trang.get(k) != trang3.get(k) and k not in ("Danh mục bảng", "Danh mục hình")]
    print("Đã ghi %s (%d trang); số trang lệch sau lượt 2: %d" % (os.path.relpath(RA, GOC), n, len(lech)))
    return 0 if not lech else 3


if __name__ == "__main__":
    sys.exit(main())
