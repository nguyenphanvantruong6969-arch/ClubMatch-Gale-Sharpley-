# -*- coding: utf-8 -*-
"""DG1-L5: sinh báo cáo khoa học `docs/nghien_cuu/DG1_BAO_CAO_KHOA_HOC.md` (+ `.html`) và hình SVG
`docs/nghien_cuu/anh_dg1/F1..F6.svg` CHỈ từ `du_lieu_test/danh_gia/ket_qua/*.json`.

    python du_lieu_test/danh_gia/viet_bao_cao.py [THƯ_MỤC_JSON]

Không có con số gõ tay: mọi số đọc từ JSON (bảng dùng lại `in_bang.py`). Chú thích hình/bảng chỉ mô tả
CÁI GÌ được vẽ, không diễn giải. Các mục 0, 2, 6, 7, 8 (và đoạn động cơ ở mục 1) là phần HỌC SINH viết:
script chỉ để lại tiêu đề + ô trống (và tối đa 6 câu hỏi gợi ý trung tính ở mục 6).
Nếu tệp .md đã có chữ học sinh trong các ô «HS», script GIỮ NGUYÊN chữ đó khi sinh lại.
"""

import html
import os
import re
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC)
import in_bang as ib  # noqa: E402

GOC = os.path.dirname(os.path.dirname(THU_MUC))
RA_MD = os.path.join(GOC, "docs", "nghien_cuu", "DG1_BAO_CAO_KHOA_HOC.md")
RA_HTML = os.path.join(GOC, "docs", "nghien_cuu", "DG1_BAO_CAO_KHOA_HOC.html")
THU_MUC_ANH = os.path.join(GOC, "docs", "nghien_cuu", "anh_dg1")

BANNER = "Toàn bộ số liệu đo trên DỮ LIỆU MÔ PHỎNG, không phải khảo sát học sinh thật"
TU_CAM = ("cho thấy", "chứng tỏ", "tốt hơn", "vượt trội")  # không dùng trong phần AI viết (DG1_GIAO_THUC §2)

# ----------------------------------------------------------------------------- ô học sinh (giữ chữ đã viết)
MO_HS = "<!-- HS:%s BẮT ĐẦU — phần học sinh viết; script sinh lại KHÔNG ghi đè -->"
DONG_HS = "<!-- HS:%s KẾT THÚC -->"
TRONG_HS = "> ✍ *Phần học sinh tự viết. (Để trống.)*"


def doc_o_hs(md_cu):
    o = {}
    for m in re.finditer(r"<!-- HS:(\w+) BẮT ĐẦU[^>]*-->\n(.*?)\n<!-- HS:\1 KẾT THÚC -->", md_cu or "", re.S):
        o[m.group(1)] = m.group(2)
    return o


def o_hs(ma, cu):
    return "\n".join([MO_HS % ma, cu.get(ma, TRONG_HS), DONG_HS % ma])


# ----------------------------------------------------------------------------- SVG
# Bảng màu phân loại mặc định đã kiểm mù màu (skill dataviz, palette.md, khe 1–5), cả sáng lẫn tối.
MAU = [("#257de0", "#338ced"), ("#f47230", "#e76624"), ("#00b894", "#00a888"), ("#f2a600", "#d28e05"), ("#ee7fac", "#e24d8b")]
NET = ["", "6 4", "2 3", "8 3 2 3", "3 5"]  # nét đứt: mã hoá phụ, không chỉ dựa vào màu
DAU = ["tron", "vuong", "tamgiac", "thoi", "tron"]


def _css():
    s = [".nen{fill:#ffffff}.tx{fill:#1c2321;font:12px 'IBM Plex Sans',system-ui,sans-serif}.tx2{fill:#5b6570;font:11px 'IBM Plex Sans',system-ui,sans-serif}",
         ".luoi{stroke:#e3e4de;stroke-width:1}.truc{stroke:#8f8c82;stroke-width:1}"]
    for i, (sang, _t) in enumerate(MAU):
        s.append(".s%d{stroke:%s;fill:%s}" % (i, sang, sang))
    s.append("@media (prefers-color-scheme: dark){.nen{fill:#191919}.tx{fill:#efefef}.tx2{fill:#9c9c9c}.luoi{stroke:#333}.truc{stroke:#777}")
    for i, (_s, toi) in enumerate(MAU):
        s.append(".s%d{stroke:%s;fill:%s}" % (i, toi, toi))
    s.append("}")
    return "".join(s)


def _e(x):
    return html.escape(str(x), quote=True)


class Ve:
    """Một khung SVG đơn giản: trục x/y tuyến tính hoặc log, lưới mờ, chú giải."""

    def __init__(self, rong=640, cao=360, trai=64, phai=24, tren=40, duoi=56, tieu_de=""):
        self.r, self.c, self.l, self.p, self.t, self.d = rong, cao, trai, phai, tren, duoi
        self.ds = []
        self.tieu_de = tieu_de

    def mien(self, x0, x1, y0, y1, logy=False, logx=False):
        import math
        self.x0, self.x1, self.y0, self.y1, self.logy, self.logx = x0, x1, y0, y1, logy, logx
        self._f = math.log10

    def X(self, x):
        a, b, v = self.x0, self.x1, x
        if self.logx:
            a, b, v = self._f(a), self._f(b), self._f(x)
        return self.l + (v - a) / (b - a) * (self.r - self.l - self.p)

    def Y(self, y):
        a, b, v = self.y0, self.y1, y
        if self.logy:
            a, b, v = self._f(a), self._f(b), self._f(y)
        return self.c - self.d - (v - a) / (b - a) * (self.c - self.t - self.d)

    def truc(self, xt, yt, nhan_x, nhan_y, fx=str, fy=str):
        for y in yt:
            self.ds.append('<line class="luoi" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f"/>' % (self.l, self.r - self.p, self.Y(y), self.Y(y)))
            self.ds.append('<text class="tx2" x="%.1f" y="%.1f" text-anchor="end">%s</text>' % (self.l - 6, self.Y(y) + 4, _e(fy(y))))
        for x in xt:
            self.ds.append('<text class="tx2" x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (self.X(x), self.c - self.d + 16, _e(fx(x))))
        self.ds.append('<line class="truc" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>' % (self.l, self.r - self.p, self.c - self.d, self.c - self.d))
        self.ds.append('<text class="tx2" x="%.1f" y="%d" text-anchor="middle">%s</text>' % ((self.l + self.r - self.p) / 2, self.c - 12, _e(nhan_x)))
        self.ds.append('<text class="tx2" transform="translate(14,%.1f) rotate(-90)" text-anchor="middle">%s</text>' % ((self.t + self.c - self.d) / 2, _e(nhan_y)))

    def dau(self, i, x, y, meo):
        k = DAU[i % len(DAU)]
        if k == "vuong":
            h = '<rect class="s%d" x="%.1f" y="%.1f" width="8" height="8"' % (i, x - 4, y - 4)
        elif k == "tamgiac":
            h = '<path class="s%d" d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ"' % (i, x, y - 5, x + 5, y + 4, x - 5, y + 4)
        elif k == "thoi":
            h = '<path class="s%d" d="M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ"' % (i, x, y - 5, x + 5, y, x, y + 5, x - 5, y)
        else:
            h = '<circle class="s%d" cx="%.1f" cy="%.1f" r="4"' % (i, x, y)
        the = {"tron": "circle", "vuong": "rect"}.get(k, "path")
        self.ds.append(h + ' stroke-width="0"><title>%s</title></%s>' % (_e(meo), the))

    def duong(self, i, diem, ten, fmeo):
        pts = " ".join("%.1f,%.1f" % (self.X(x), self.Y(y)) for x, y in diem)
        net = NET[i % len(NET)]
        self.ds.append('<polyline class="s%d" fill="none" style="fill:none" stroke-width="2" %s points="%s"/>' % (
            i, ('stroke-dasharray="%s"' % net) if net and net != "1 0" else "", pts))
        for x, y in diem:
            self.dau(i, self.X(x), self.Y(y), "%s — %s" % (ten, fmeo(x, y)))

    def chu_giai(self, ten, x=None, y=None):
        x = self.l + 8 if x is None else x
        y = self.t - 22 if y is None else y
        cx = x
        for i, t in enumerate(ten):
            net = NET[i % len(NET)]
            self.ds.append('<line class="s%d" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke-width="2" %s/>' % (
                i, cx, cx + 22, y, y, ('stroke-dasharray="%s"' % net) if net and net != "1 0" else ""))
            self.dau(i, cx + 11, y, t)
            self.ds.append('<text class="tx" x="%.1f" y="%.1f">%s</text>' % (cx + 28, y + 4, _e(t)))
            cx += 34 + 7.2 * len(t)

    def svg(self, nhan):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">'
                '<style>%s</style><rect class="nen" width="100%%" height="100%%"/>%s</svg>' % (
                    self.r, self.c, self.r, self.c, _e(nhan), _css(), "".join(self.ds)))


def _vn(x, n=1):
    return ib.so(x, n)


def hinh_f1(cc):
    nhan = [("rbda", "RB-DA"), ("boston", "Boston"), ("thu_tu_boc_tham", "RSD"), ("ttc", "TTC"), ("da_clb_de_xuat", "DA (CLB đề xuất)")]
    v = Ve(rong=680, cao=380, tren=56)
    v.mien(1, 6, 0, 100)
    v.truc(range(1, 7), range(0, 101, 20), "k (nguyện vọng thứ k trở lên)", "% học sinh (mẫu số: mọi HS)", fy=lambda y: "%d" % y)
    for i, (ma, t) in enumerate(nhan):
        cs = cc["co_che"][ma]
        diem = [(k, cs["a.duong_cong_don.%d" % k]["tb"]) for k in range(1, 7)]
        v.duong(i, diem, t, lambda x, y: "k = %d: %s %%" % (x, _vn(y)))
    v.chu_giai([t for _m, t in nhan])
    return v.svg("Hình 1: đường cong tích luỹ theo cơ chế")


def _quet(q, n_hs, rho):
    return [c for c in q["cac_cau_hinh"] if c["tham_so"]["n_hs"] == n_hs and c["tham_so"]["rho"] == rho]


def hinh_f2(q, khoa, nhan_y, tieu_de, n_hs=800, rho=0.7, ymax=100):
    v = Ve(rong=560, cao=340, tren=56)
    v.mien(0, 0.9, 0, ymax)
    v.truc([0, 0.25, 0.5, 0.75, 0.9], range(0, ymax + 1, 20), "α (mức «mọi em thích cùng CLB»)", nhan_y,
           fx=lambda x: _vn(x, 2), fy=lambda y: "%d" % y)
    ks = sorted({c["tham_so"]["kappa"] for c in _quet(q, n_hs, rho)})
    for i, k in enumerate(ks):
        dd = sorted((c["tham_so"]["alpha"], c["chi_so"][khoa]["tb"]) for c in _quet(q, n_hs, rho) if c["tham_so"]["kappa"] == k)
        v.duong(i, dd, "κ = %s" % _vn(k, 1), lambda x, y: "α = %s: %s" % (_vn(x, 2), _vn(y)))
    v.chu_giai(["κ = %s" % _vn(k, 1) for k in ks])
    return v.svg(tieu_de)


def hinh_f3(md):
    diem = [(x["ti_le_cau"], x["lap_day_tb"] * 100, x["club_id"], t["seed_du_lieu"]) for t in md["theo_truong"] for x in t["theo_clb"]]
    xm = max(3.5, max(d[0] for d in diem) + 0.2)
    v = Ve(rong=620, cao=360, tren=36)
    v.mien(0, xm, 0, 100)
    import math
    v.truc([x / 2 for x in range(0, int(math.ceil(xm * 2)) + 1)], range(0, 101, 20), "Tỉ lệ cầu = số em đặt CLB làm NV1 / chỉ tiêu",
           "Lấp đầy CLB (%)", fx=lambda x: _vn(x, 1), fy=lambda y: "%d" % y)
    for x, y, clb, s in diem:
        v.ds.append('<circle class="s0" cx="%.1f" cy="%.1f" r="4" fill-opacity="0.55" stroke-width="0"><title>trường %s, %s: tỉ lệ cầu %s, lấp đầy %s %%</title></circle>'
                    % (v.X(x), v.Y(y), s, clb, _vn(x, 2), _vn(y)))
    v.ds.append('<text class="tx2" x="%d" y="20">Mỗi chấm = một CLB của một trường mô phỏng (%d chấm)</text>' % (v.l, len(diem)))
    return v.svg("Hình 3: lấp đầy theo tỉ lệ cầu")


def hinh_f4(bt):
    g = bt["cac_bien_the"][0]["chi_so"]
    hang = [(b["bien_the"]["ten"], b["chi_so"]["a.pct_nv1_tat_ca"]["tb"] - g["a.pct_nv1_tat_ca"]["tb"],
             b["chi_so"]["b.n_chua_xep"]["tb"] - g["b.n_chua_xep"]["tb"], (b.get("churn", {}).get("doi_clb") or {}).get("tb"))
            for b in bt["cac_bien_the"][1:]]
    hang.sort(key=lambda h: -abs(h[1]))
    cao_dong = 30
    rong, trai = 1000, 120
    cao = 70 + cao_dong * len(hang)
    ds = []
    cot = [("Δ % NV1 (điểm %)", 1, 300), ("Δ số em chưa xếp", 2, 300)]
    for ci, (ten, j, w) in enumerate(cot):
        x0 = trai + ci * (w + 60)
        m = max(abs(h[j]) for h in hang) or 1
        tam = x0 + w / 2
        ds.append('<text class="tx" x="%.1f" y="22" text-anchor="middle">%s</text>' % (tam, _e(ten)))
        ds.append('<line class="truc" x1="%.1f" x2="%.1f" y1="34" y2="%d"/>' % (tam, tam, cao - 20))
        for r, h in enumerate(hang):
            y = 40 + r * cao_dong
            dai = h[j] / m * (w / 2 - 30)
            x = tam if dai >= 0 else tam + dai
            lop = "s0" if h[j] >= 0 else "s1"
            ds.append('<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="18" rx="3" stroke-width="0"><title>%s: %s</title></rect>' % (
                lop, x, y, max(abs(dai), 1), _e(h[0]), _vn(h[j], 2)))
            ds.append('<text class="tx2" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (
                tam + dai + (4 if dai >= 0 else -4), y + 13, "start" if dai >= 0 else "end", _vn(h[j], 1)))
    x0 = trai + 2 * (300 + 60)
    ds.append('<text class="tx" x="%.1f" y="22" text-anchor="start">Đổi CLB (số em)</text>' % x0)
    for r, h in enumerate(hang):
        y = 40 + r * cao_dong
        ds.append('<text class="tx" x="%d" y="%.1f" text-anchor="end">%s</text>' % (trai - 8, y + 13, _e(h[0])))
        ds.append('<text class="tx2" x="%.1f" y="%.1f">%s</text>' % (x0, y + 13, _vn(h[3], 1)))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="Hình 4">'
            '<style>%s</style><rect class="nen" width="100%%" height="100%%"/>%s</svg>' % (rong, cao, rong, cao, _css(), "".join(ds)))


def hinh_f6(tg):
    qm = tg["cac_quy_mo"]
    v = Ve(rong=600, cao=340, tren=56)
    v.mien(100, 2500, 0.0003, 3, logy=True, logx=True)
    v.truc([q["n_hs"] for q in qm], [0.001, 0.01, 0.1, 1], "Số học sinh (thang log; 120×10, 300×10, 800×20, 2000×50 CLB)", "Giây (thang log)",
           fx=lambda x: "%d" % x, fy=lambda y: ("%g" % y).replace(".", ","))
    ser = [("run_rbda (lõi)", lambda q: q["run_rbda_giay"]["trung_vi"]), ("run_pipeline (5 bước)", lambda q: q["run_pipeline_giay"]["trung_vi"]),
           ("Nạp sổ nhập", lambda q: q["nap_so_nhap_giay"])]
    for i, (t, f) in enumerate(ser):
        v.duong(i, [(q["n_hs"], f(q)) for q in qm], t, lambda x, y: "%d HS: %s s" % (x, _vn(y, 4)))
    v.chu_giai([t for t, _f in ser])
    return v.svg("Hình 6: thời gian chạy theo quy mô")


ANH_QUY_TRINH = [
    ("S1_sau_nap_truoc_khi_chay.png", "màn «Xếp CLB» sau khi nạp Sổ nhập của trường mô phỏng mặc định (seed dữ liệu 101), trước khi chạy; "
     "mục «Xem cảnh báo» liệt kê các cảnh báo kiểm dữ liệu mà phần mềm sinh ra cho bộ này."),
    ("S2_ket_qua.png", "màn «Kết quả» sau một lần chạy (seed bốc thăm 1), chế độ xem theo mã học sinh; chỉ chụp khung nhìn đầu."),
    ("S3_chi_tiet_chi_so_phan_bo.png", "màn «Chi tiết và xuất tệp» với khối «Chỉ số phân bổ» (mục L4 của DG1) cho cùng lần chạy."),
    ("S4_khoi_chi_so_phan_bo.png", "khối «Chỉ số phân bổ» chụp riêng."),
    ("S5_excel_thong_ke.png", "trang «Thống kê» của sổ Excel kết quả xuất từ cùng lần chạy, gồm mục «CHỈ SỐ PHÂN BỔ»; dựng lại thành bảng HTML bằng openpyxl để chụp."),
    ("S6_bao_cao_trang_dau.png", "trang đầu bản HTML của báo cáo này."),
]

# ----------------------------------------------------------------------------- Markdown
def _bo_tu_danh_gia(s):
    """Cột «Tốt hơn/Xấu hơn» của in_bang là nhãn đếm hạng — đổi chữ cho khỏi lẫn với câu đánh giá."""
    return (s.replace("Tốt hơn", "Lên hạng").replace("Xấu hơn", "Xuống hạng")
            .replace("tốt hơn", "lên hạng").replace("xấu hơn", "xuống hạng"))


def _cat_tieu_de(s):
    """Bỏ dòng tiêu đề ### đầu khối in_bang (báo cáo tự đặt tiêu đề), hạ ### còn lại xuống ####."""
    dong = s.split("\n")
    if dong and dong[0].startswith("### "):
        dong = dong[1:]
    return "\n".join(("#" + d) if d.startswith("### ") else d for d in dong).strip()


def _hinh(so_hinh, ten_tep, chu_thich):
    return "![Hình %d](anh_dg1/%s)\n\n*Hình %d: %s*" % (so_hinh, ten_tep, so_hinh, chu_thich)


def viet_md(J, cu):
    md, cc, bt, q, tg = J["mac_dinh.json"], J["co_che_doi_chung.json"], J["bien_the_tieu_chi.json"], J["quet_quy_mo.json"], J["thoi_gian.json"]
    dn = md["dinh_nghia"]
    ch = dn["cau_hinh_chay"]
    ts = dn["tham_so_sinh"]
    lc = md["lan_chay"]
    cs = md["chi_so"]
    R = []
    a = R.append
    a("# DG1 — Đánh giá định lượng thuật toán phân bổ RB-DA trên dữ liệu mô phỏng")
    a("")
    a("> ⚠ **%s.** Bộ sinh dữ liệu: `du_lieu_test/danh_gia/_sinh.py`, `mo_phong_fa_daa.py` và các bộ mẫu trong `du_lieu_test/`." % BANNER)
    a(">")
    a("> Mọi con số trong tệp này do `du_lieu_test/danh_gia/viet_bao_cao.py` đọc từ `du_lieu_test/danh_gia/ket_qua/*.json`; không số nào gõ tay. "
      "Nguồn gốc từng JSON (commit, lệnh, thời gian): `du_lieu_test/danh_gia/ket_qua/README_LAN_CHAY.md` và mục 9.")
    a(">")
    a("> **Phân công viết** (quy định liêm chính của dự án): các mục đánh dấu ✍ (0, phần động cơ ở 1, 2, 6, 7, 8) do **học sinh** viết; "
      "AI chỉ soạn phần mô tả cơ chế, phương pháp, bảng/hình với chú thích mô tả, và cách tái lập.")
    a("")
    a("## 0. Tóm tắt ✍")
    a("")
    a(o_hs("tom_tat", cu))
    a("")
    a("## 1. Đặt vấn đề và câu hỏi nghiên cứu")
    a("")
    a("### 1.1 Động cơ ✍")
    a("")
    a(o_hs("dong_co", cu))
    a("")
    a("### 1.2 Câu hỏi nghiên cứu")
    a("")
    a("- **Q1.** Nguyện vọng của học sinh được đáp ứng đến mức nào, khi đặt cạnh các cơ chế đối chứng (Boston, thứ tự bốc thăm, TTC, DA do CLB đề xuất)?")
    a("- **Q2.** Những em nào chưa được xếp, và phần chưa xếp đó do dữ liệu (không thể tránh) hay do ưu tiên + ổn định?")
    a("- **Q3.** Chỉ tiêu các CLB và suất dự trữ được dùng đến mức nào?")
    a("- **Q4.** Khi đổi MỘT tiêu chí (suất dự trữ, cách xếp nhóm, phạm vi điểm, số nguyện vọng tối đa, chỉ tiêu), các chỉ số Q1–Q3 thay đổi bao nhiêu và bao nhiêu em đổi CLB? "
      "Các tính năng suất dự trữ, điểm quyết tâm, huy chương thay đổi gì khi bật/tắt?")
    a("- **Q5.** Các chỉ số Q1–Q3 thay đổi thế nào khi mức cạnh tranh (α) và tổng chỉ tiêu (κ) thay đổi, và khi trường lớn lên (thời gian chạy)?")
    a("")
    a("## 2. Giả thuyết ✍")
    a("")
    a("> Ghi chú về trình tự (sự kiện): lần chạy đầy đủ bắt đầu lúc %s (commit `%s`). Nếu mục này được viết SAU thời điểm đó, "
      "học sinh ghi rõ «giả thuyết viết sau khi đã có số liệu»." % (lc["bat_dau"], lc["commit"][:10]))
    a("")
    a(o_hs("gia_thuyet", cu))
    a("")
    a("## 3. Cơ chế RB-DA (tóm tắt)")
    a("")
    a("Mô tả đầy đủ: `docs/CO_CHE_THUAT_TOAN.md`. Tóm tắt các thành phần mà phần đo dùng tới:")
    a("")
    a("1. **Chấp nhận hoãn, học sinh đề xuất** (Gale & Shapley, 1962): mỗi vòng, em chưa có chỗ nộp vào CLB kế tiếp trong danh sách; "
      "CLB giữ tạm những em xếp cao nhất theo thứ tự ưu tiên của mình, trả lại phần dư; lặp đến khi không còn ai nộp.")
    a("2. **Suất dự trữ mềm hai lượt** (Kominers & Sönmez, 2016): ở CLB có suất dự trữ, lượt 1 lấp suất dự trữ bằng em thuộc diện "
      "(`chinh_sach`, `khoi_10`), lượt 2 lấp suất thường bằng mọi em còn lại; suất dự trữ không ai dùng được chuyển sang suất thường.")
    a("3. **Thứ tự ưu tiên hai tầng**: CLB tuyển chọn (có thi) xếp theo điểm giảm dần rồi số bốc thăm; CLB không thi xếp theo số bốc thăm.")
    a("4. **Một lần bốc thăm chung (STB)** cho mọi CLB; số bốc thăm sinh bằng `crc32`, khoá sau lần chạy đầu.")
    a("5. **Kiểm sau giải**: `verify_stability` đếm cặp phá vỡ (một em và một CLB cùng muốn đổi sang nhau theo hàm lựa chọn thật).")
    a("")
    a("Thứ tự ưu tiên không đọc thứ hạng nguyện vọng và không đọc kết quả lần chạy trước (bất biến 2 của dự án).")
    a("")
    a("## 4. Phương pháp")
    a("")
    a("### 4.1 Bộ sinh dữ liệu mô phỏng")
    a("")
    a("Độ thích của học sinh *i* với CLB *j*: u(i, j) = α·pop(j) + (1 − α)·ε(i, j), ε ~ U(0, 1); pop(j) sinh một lần mỗi trường, giảm tuyến tính 1 → 0. "
      "Danh sách nguyện vọng = %d–%d CLB có u cao nhất (độ dài đều). α = 0: mọi em thích những CLB khác nhau; α = 0,9: gần như mọi em thích cùng các CLB." % tuple(ts["dai_danh_sach"]))
    a("")
    a(ib.bang(["Tham số", "Giá trị"], [
        ("α (mức trùng sở thích)", ", ".join(_vn(x, 2) for x in ch["alpha"])),
        ("κ = Σ chỉ tiêu / số HS", ", ".join(_vn(x, 1) for x in ch["kappa"])),
        ("ρ (điểm thi liên quan năng lực)", ", ".join(_vn(x, 1) for x in ch["rho"]) + " — điểm = %s" % ts["diem"]),
        ("Quy mô (HS × CLB)", ", ".join("%d × %d" % tuple(x) for x in ch["quy_mo"]) + "; thời gian thêm 2000 × 50"),
        ("Cấu hình mặc định", "%d HS × %d CLB, α = %s, ρ = %s, κ = %s" % (ch["mac_dinh"]["n_hs"], ch["mac_dinh"]["n_clb"], _vn(ch["mac_dinh"]["alpha"], 2),
                                                                         _vn(ch["mac_dinh"]["rho"], 1), _vn(ch["mac_dinh"]["kappa"], 1))),
        ("Tỉ lệ CLB tuyển chọn (có thi)", _vn(ts["ty_le_clb_tuyen_chon"] * 100, 0) + " %"),
        ("Xác suất em đăng ký thi một CLB tuyển chọn trong danh sách", _vn(ts["xac_suat_tick_thi"] * 100, 0) + " %%, tối đa %d bài" % ts["tran_thi_moi_buoi"]),
        ("Diện dự trữ", "chinh_sach %s %%, khoi_10 %s %%" % (_vn(ts["ty_le_chinh_sach"] * 100, 0), _vn(ts["ty_le_khoi_10"] * 100, 0))),
        ("Suất dự trữ", "%s %% chỉ tiêu ở %d CLB được thích nhất" % (_vn(ts["ty_le_suat_du_tru"] * 100, 0), ts["so_clb_du_tru"])),
        ("Chia chỉ tiêu", ts["chia_chi_tieu"]),
        ("Hạt giống ngẫu nhiên", ts["hat_giong"]),
    ]))
    a("")
    a("### 4.2 Lưới hạt giống và khoảng tin cậy")
    a("")
    a("Hai nguồn ngẫu nhiên tách riêng: **seed dữ liệu** = một trường mô phỏng khác (%s); **seed bốc thăm** = cùng trường, lần bốc thăm khác (%s). "
      "Mỗi cấu hình: %d trường × %d lần bốc thăm. %s" % (", ".join(map(str, dn["seed_du_lieu"])), ", ".join(map(str, dn["seed_boc_tham"])),
                                                        dn["so_truong"], dn["so_lan_boc_tham_moi_truong"], dn["cach_tinh_ktc"]))
    a("")
    a("### 4.3 Cơ chế đối chứng và cận trên")
    a("")
    a("- **Boston** (chấp nhận ngay), **thứ tự bốc thăm (RSD)**, **TTC** (chu trình giao dịch hàng đầu), **DA do CLB đề xuất**: `du_lieu_test/co_che_doi_chung.py`; "
      "cả bốn gọi đúng hàm lựa chọn `club_choice_function` của phần mềm.")
    a("- **Cận trên** = kích thước ghép cực đại trên đồ thị (học sinh × CLB em đã liệt kê, sức chứa CLB), bỏ qua ưu tiên và ổn định "
      "(`_chi_so.py`, đường tăng). Số em mà không cơ chế nào trên cùng danh sách xếp được = N − cận trên.")
    a("- **Biến thể tiêu chí**: cùng dữ liệu, cùng seed bốc thăm, đổi đúng một tham số so với mặc định.")
    a("")
    a("### 4.4 Định nghĩa chỉ số")
    a("")
    a(ib.bang(["Nhóm", "Chỉ số", "Công thức", "Mẫu số"],
              [(v["nhom"], v["ten"], v["cong_thuc"], v["mau_so"]) for _k, v in dn["chi_so"].items()]))
    a("")
    a("Thêm: «%s» = %s; «%s» = %s." % ("lật có chỗ", dn["lat_co_cho_pct"], "lật CLB", dn["lat_clb_pct"]))
    a("")

    # ------------------------------------------------------------------ 5 kết quả
    a("## 5. Kết quả")
    a("")
    a("Quy ước: «tb [KTC 95 %]» = trung bình qua các trường mô phỏng và khoảng tin cậy t; «sd bốc» = độ lệch chuẩn giữa các lần bốc thăm trong một trường. "
      "Ở n = 5 trường, KTC của tỉ lệ có thể vượt ra ngoài [0; 100].")
    a("")
    a("### 5.0 Đối chiếu với số liệu đã kiểm chứng")
    a("")
    a("*Bảng 1: bộ TEST, seed 42, so với `SO_LIEU_DA_KIEM_CHUNG.md` §2; «Đo» chạy qua `run_pipeline` thật và qua lõi trong bộ nhớ.*")
    a("")
    a(_cat_tieu_de(ib.in_doi_chieu(J["doi_chieu_so_lieu.json"])))
    a("")
    a("### 5.1 Q1 — Mức đáp ứng nguyện vọng")
    a("")
    a("*Bảng 2: cấu hình mặc định, mọi chỉ số A–C, %d trường × %d lần bốc thăm.*" % (dn["so_truong"], dn["so_lan_boc_tham_moi_truong"]))
    a("")
    a(_bo_tu_danh_gia(_cat_tieu_de(ib.in_mac_dinh(md))))
    a("")
    trung = all(cc["co_che"]["rbda"]["a.duong_cong_don.%d" % k]["tb"] == cc["co_che"]["da_clb_de_xuat"]["a.duong_cong_don.%d" % k]["tb"] for k in range(1, 7))
    a(_hinh(1, "F1_duong_cong_co_che.svg", "đường cong tích luỹ — %% học sinh (mẫu số: mọi HS) được xếp ở nguyện vọng ≤ k, năm cơ chế, cấu hình mặc định, "
            "trung bình %d trường × %d lần bốc thăm.%s" % (dn["so_truong"], dn["so_lan_boc_tham_moi_truong"],
                                                          " Đường RB-DA và DA do CLB đề xuất trùng nhau trên cấu hình này." if trung else "")))
    a("")
    a("*Bảng 3: năm cơ chế trên cùng dữ liệu và cùng seed bốc thăm, cấu hình mặc định.*")
    a("")
    a(_cat_tieu_de(ib.in_co_che(cc)))
    a("")
    a("### 5.2 Q2 — Học sinh chưa được xếp")
    a("")
    a("Cấu hình mặc định (Bảng 2): chưa xếp = %s em; cận trên = %s; không thể tránh = %s; phần chênh cận − được xếp = %s. "
      "Phân theo nguyên nhân: hết chỗ (người ưu tiên cao hơn) %s, không điểm ở CLB tuyển chọn %s, danh sách rỗng %s." % (
          ib.ktc(cs["b.n_chua_xep"]), ib.ktc(cs["b.can_tren_ghep_cuc_dai"]), ib.ktc(cs["b.khong_the_tranh"]), ib.ktc(cs["b.gia_uu_tien_on_dinh"]),
          ib.ktc(cs["b.nguyen_nhan.het_cho_uu_tien_cao_hon"]), ib.ktc(cs["b.nguyen_nhan.khong_diem"]), ib.ktc(cs["b.nguyen_nhan.danh_sach_rong"])))
    a("")
    a(_hinh(5, "F5_can_tren.svg", "phần chênh cận trên − số em được xếp (số em) theo α, ba mức κ; 800 HS × 20 CLB, ρ = 0,7; trung bình %d trường." % dn["so_truong"]))
    a("")
    a("### 5.3 Q3 — Sử dụng chỉ tiêu")
    a("")
    a("Cấu hình mặc định (Bảng 2): lấp đầy %s %%; suất dự trữ đã dùng %s / cung cấp %s; số CLB đầy %s; số CLB lấp đầy < 50 %% %s." % (
        ib.ktc(cs["c.ty_le_lap_day"]), ib.ktc(cs["c.du_tru_da_dung"]), ib.ktc(cs["c.du_tru_cung_cap"]), ib.ktc(cs["c.n_clb_day"]), ib.ktc(cs["c.n_clb_duoi_50"])))
    a("")
    a(_hinh(3, "F3_lap_day_ti_le_cau.svg", "lấp đầy của từng CLB (trục dọc, %%) theo tỉ lệ cầu NV1 / chỉ tiêu (trục ngang); %d trường mô phỏng cấu hình mặc định, "
            "lấp đầy trung bình qua %d lần bốc thăm." % (len(md["theo_truong"]), dn["so_lan_boc_tham_moi_truong"])))
    a("")
    a("### 5.4 Q4 — Đổi một tiêu chí; bật/tắt tính năng")
    a("")
    a("*Bảng 4: chín biến thể so với mặc định, cùng dữ liệu và seed; «Lên hạng / Xuống hạng» = số em được xếp ở nguyện vọng có thứ hạng cao hơn / thấp hơn so với mặc định.*")
    a("")
    a(_bo_tu_danh_gia(_cat_tieu_de(ib.in_bien_the(bt))))
    a("")
    a(_hinh(4, "F4_bien_the.svg", "thay đổi so với mặc định của % NV1 (điểm phần trăm) và số em chưa xếp, và số em đổi CLB, theo biến thể; "
            "xếp theo độ lớn |Δ % NV1|. Màu xanh = tăng, cam = giảm."))
    a("")
    a("*Bảng 5: tính năng suất dự trữ × điểm quyết tâm (lưới 2×2) và huy chương (FA-DAA) so với chế độ cũ, theo quy mô, α và hành vi khai.*")
    a("")
    a(_bo_tu_danh_gia(_cat_tieu_de(ib.in_tinh_nang(J["tinh_nang.json"]))))
    a("")
    a("### 5.5 Q5 — Mức cạnh tranh, quy mô và thời gian")
    a("")
    a(_hinh(2, "F2a_nv1_theo_alpha.svg", "%% học sinh được NV1 (mẫu số: mọi HS) theo α, ba mức κ; 800 HS × 20 CLB, ρ = 0,7; trung bình %d trường × %d lần bốc thăm."
            % (dn["so_truong"], dn["so_lan_boc_tham_moi_truong"])))
    a("")
    a("![Hình 2b](anh_dg1/F2b_chua_xep_theo_alpha.svg)")
    a("")
    a("*Hình 2b: % học sinh chưa được xếp theo α, ba mức κ; cùng cấu hình với Hình 2.*")
    a("")
    a("*Bảng 6: quét 3 quy mô × 5 α × 3 κ × 2 ρ = %d cấu hình.*" % len(q["cac_cau_hinh"]))
    a("")
    a(_cat_tieu_de(ib.in_quet(q)))
    a("")
    a(_hinh(6, "F6_thoi_gian.svg", "thời gian chạy (trung vị 3 lần, giây, thang log) theo số học sinh: lõi `run_rbda`, `run_pipeline` 5 bước, nạp Sổ nhập. %s" % tg.get("ghi_chu", "")))
    a("")
    a("*Bảng 7: thời gian chạy.*")
    a("")
    a(_cat_tieu_de(ib.in_thoi_gian(tg)))
    a("")
    a("*Bảng 8: 800 HS × 20 CLB × 3 buổi, cấu hình mặc định.*")
    a("")
    a(_cat_tieu_de(ib.in_nhieu_buoi(J["nhieu_buoi.json"])))
    a("")
    a("*Bảng 9: các bộ dữ liệu mẫu có sẵn trong `du_lieu_test/`, chạy nguyên trạng.*")
    a("")
    a(_cat_tieu_de(ib.in_co_san(J["bo_co_san.json"])))
    a("")

    a("### 5.6 Ảnh chụp quy trình trên phần mềm")
    a("")
    a("Chụp bằng `du_lieu_test/danh_gia/chup_quy_trinh.py` (Chromium, giao diện thật qua `browser_host`, CSDL tạm). Tên học sinh và CLB do bộ sinh đặt. "
      "Số trên ảnh là của MỘT trường mô phỏng và MỘT lần bốc thăm, nên khác các trung bình ở Bảng 2.")
    a("")
    for i, (t, c) in enumerate(ANH_QUY_TRINH, 1):
        a("![Ảnh %d](anh_dg1/%s)" % (i, t))
        a("")
        a("*Ảnh %d: %s*" % (i, c))
        a("")
    a("## 6. Thảo luận ✍")
    a("")
    a("Câu hỏi gợi ý (trung tính, không kèm đáp án; học sinh có thể bỏ):")
    a("")
    a("1. Ở α nào khoảng cách % NV1 giữa RB-DA và Boston lớn nhất, nhỏ nhất? Đổi lại, cột «Cặp phá vỡ» của hai cơ chế khác nhau thế nào?")
    a("2. Trong phần chưa xếp ở cấu hình mặc định, bao nhiêu là «không thể tránh» và bao nhiêu là phần chênh với cận trên? Phần chênh đó đổi ra sao khi κ tăng?")
    a("3. Vì sao «DA do CLB đề xuất» trùng RB-DA trên phần lớn dữ liệu sinh, nhưng khác trên `bo_kich_tran`?")
    a("4. Ở Bảng 4, biến thể nào làm nhiều em đổi CLB nhất, và số «lên hạng» so với «xuống hạng» của biến thể đó ra sao?")
    a("5. Khi bật suất dự trữ, nhóm `khoi_10` và nhóm `khong` thay đổi % NV1 và % được xếp bao nhiêu (Bảng 5)?")
    a("6. Giữa các lần bốc thăm của cùng một trường, bao nhiêu % học sinh lúc có chỗ lúc không? Điều đó liên quan gì đến cách công bố kết quả?")
    a("")
    a(o_hs("thao_luan", cu))
    a("")
    a("## 7. Hạn chế ✍")
    a("")
    a("Các giới hạn của thiết kế thí nghiệm (sự kiện, không đánh giá):")
    a("")
    a("- Mọi số liệu đo trên dữ liệu mô phỏng; chưa có dữ liệu học sinh thật nào trong báo cáo này.")
    a("- Một mô hình sở thích duy nhất (α·độ phổ biến + nhiễu đều); danh sách nguyện vọng dài %d–%d CLB." % tuple(ts["dai_danh_sach"]))
    a("- %d trường mô phỏng cho mỗi cấu hình; KTC kiểu t với %d bậc tự do." % (dn["so_truong"], dn["so_truong"] - 1))
    a("- Một máy đo thời gian (`%s`, Python %s); thời gian trên máy kiosk Windows chưa đo trong lần chạy này." % (lc["may"], lc["python"]))
    a("- Mô hình hành vi khai huy chương (lười / thật thà / chiến lược) lấy từ `mo_phong_fa_daa.py`, không từ quan sát.")
    a("")
    a(o_hs("han_che", cu))
    a("")
    a("## 8. Kết luận ✍")
    a("")
    a(o_hs("ket_luan", cu))
    a("")
    a("## 9. Tái lập")
    a("")
    a("```bash")
    a("python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan doi_chieu mac_dinh co_che bien_the quet nhieu_buoi co_san")
    a("python du_lieu_test/danh_gia/do_danh_gia.py --day-du --phan thoi_gian")
    a("python du_lieu_test/danh_gia/do_tinh_nang.py --day-du")
    a("python du_lieu_test/danh_gia/kiem_ket_qua.py")
    a("python du_lieu_test/danh_gia/viet_bao_cao.py")
    a("```")
    a("")
    a(ib.bang(["Tệp JSON", "Commit", "Lệnh", "Giây (tích luỹ)", "Bắt đầu", "Python"],
              [(t, "`%s`" % (J[t]["lan_chay"].get("commit") or "?")[:10], "`%s`" % J[t]["lan_chay"].get("lenh"), J[t]["lan_chay"].get("thoi_gian_giay"),
                J[t]["lan_chay"].get("bat_dau"), J[t]["lan_chay"].get("python")) for t in sorted(J)]))
    a("")
    a("Kiểm tự động: `kiem_ket_qua.py` (mọi ô cặp phá vỡ và xếp ngoài danh sách của RB-DA = 0; được xếp ≤ cận trên; đối chiếu bộ TEST). "
      "Test: `python -m pytest -q tests/test_dg1_*.py`.")
    a("")
    a("## 10. Tài liệu tham khảo")
    a("")
    a("- Gale, D., & Shapley, L. S. (1962). College admissions and the stability of marriage. *The American Mathematical Monthly*, 69(1), 9–15.")
    a("- Kominers, S. D., & Sönmez, T. (2016). Matching with slot-specific priorities: Theory. *Theoretical Economics*, 11(2), 683–710.")
    a("- Abdulkadiroğlu, A., Che, Y.-K., & Yasuda, Y. (2015). Expanding “choice” in school choice. *American Economic Journal: Microeconomics*, 7(1), 1–42.")
    a("")
    a("---")
    a("*Sinh bởi `du_lieu_test/danh_gia/viet_bao_cao.py`. %s.*" % BANNER)
    return "\n".join(R) + "\n"


# ----------------------------------------------------------------------------- HTML (Markdown con → HTML, ảnh SVG nhúng thẳng)
def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<em>\1</em>", s)
    return s


def md_sang_html(md, svg):
    out, dong, i = [], md.split("\n"), 0
    while i < len(dong):
        d = dong[i]
        if d.startswith("<!-- HS:"):
            ma = re.match(r"<!-- HS:(\w+)", d).group(1)
            j = i + 1
            noi = []
            while not dong[j].startswith("<!-- HS:%s KẾT THÚC" % ma):
                noi.append(dong[j])
                j += 1
            chu = "\n".join(noi)
            out.append('<div class="hs">%s</div>' % (md_sang_html(chu, svg) if chu.strip() != TRONG_HS else "✍ <em>Phần học sinh tự viết. (Để trống.)</em>"))
            i = j + 1
            continue
        if d.startswith("```"):
            j = i + 1
            while not dong[j].startswith("```"):
                j += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(dong[i + 1:j])))
            i = j + 1
            continue
        m = re.match(r"(#{1,4}) (.*)", d)
        if m:
            n = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (n, _inline(m.group(2)), n))
        elif d.startswith("!["):
            t = re.match(r"!\[[^\]]*\]\(anh_dg1/([^)]+)\)", d).group(1)
            out.append('<figure>%s</figure>' % (svg[t] if t in svg else '<img src="anh_dg1/%s" alt="%s" loading="lazy">' % (_e(t), _e(t))))
        elif d.startswith("|"):
            j = i
            while j < len(dong) and dong[j].startswith("|"):
                j += 1
            hang = [[c.strip() for c in x.strip().strip("|").split(" | ")] for x in dong[i:j]]
            th = "".join("<th>%s</th>" % _inline(c) for c in hang[0])
            tb = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c) for c in h) for h in hang[2:])
            out.append('<div class="bang"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, tb))
            i = j
            continue
        elif d.startswith(">"):
            j = i
            while j < len(dong) and dong[j].startswith(">"):
                j += 1
            khoi = [x[1:].strip() for x in dong[i:j]]
            out.append("<blockquote>%s</blockquote>" % "".join("<p>%s</p>" % _inline(x) for x in khoi if x))
            i = j
            continue
        elif re.match(r"(- |\d+\. )", d):
            j = i
            so = d[0].isdigit()
            while j < len(dong) and re.match(r"(- |\d+\. )", dong[j]):
                j += 1
            out.append("<%s>%s</%s>" % ("ol" if so else "ul", "".join("<li>%s</li>" % _inline(re.sub(r"^(- |\d+\. )", "", x)) for x in dong[i:j]),
                                        "ol" if so else "ul"))
            i = j
            continue
        elif d.strip() == "---":
            out.append("<hr>")
        elif d.strip():
            out.append("<p>%s</p>" % _inline(d))
        i += 1
    return "\n".join(out)


CSS_TRANG = """
:root{--ink:#1C2321;--soft:#5B6570;--paper:#F3F4F1;--raised:#FFFFFF;--line:#DBDCD5;--accent:#17427A;--warn-bg:#F1DFB8;--hs-bg:#DCE9E0}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#efefef;--soft:#9c9c9c;--paper:#121412;--raised:#191919;--line:#333;--accent:#84b9f3;--warn-bg:#3a2f17;--hs-bg:#1d2b22}}
:root[data-theme="dark"]{--ink:#efefef;--soft:#9c9c9c;--paper:#121412;--raised:#191919;--line:#333;--accent:#84b9f3;--warn-bg:#3a2f17;--hs-bg:#1d2b22}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 "IBM Plex Sans",system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 16px 64px}
h1{font:700 28px/1.25 "Be Vietnam Pro",system-ui,sans-serif;margin:8px 0 16px}h2{font:600 21px/1.3 "Be Vietnam Pro",system-ui,sans-serif;margin:36px 0 10px;border-top:1px solid var(--line);padding-top:20px}
h3{font:600 17px/1.3 "Be Vietnam Pro",system-ui,sans-serif;margin:24px 0 8px}h4{font:600 15px/1.3 system-ui,sans-serif;margin:18px 0 6px}
code{font:13px "IBM Plex Mono",ui-monospace,monospace;background:var(--raised);border:1px solid var(--line);border-radius:4px;padding:0 3px;word-break:break-word}
pre{background:var(--raised);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto}pre code{border:0;padding:0}
blockquote{margin:12px 0;padding:8px 16px;background:var(--warn-bg);border-radius:8px}blockquote p{margin:6px 0}
.hs{margin:10px 0;padding:18px 16px;min-height:72px;background:var(--hs-bg);border:2px dashed var(--soft);border-radius:8px;color:var(--soft)}
.bang{overflow-x:auto;margin:10px 0;border:1px solid var(--line);border-radius:8px;background:var(--raised)}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}th,td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{position:sticky;top:0;background:var(--raised);font-weight:600}tr:last-child td{border-bottom:0}
figure{margin:14px 0;overflow-x:auto}figure img{max-width:100%;height:auto;border-radius:8px;border:1px solid var(--line)}figure svg{max-width:100%;height:auto;border-radius:8px;border:1px solid var(--line)}
p em{color:var(--soft)}
"""


def viet_html(md, svg):
    than = md_sang_html(md, svg)
    return ('<!doctype html>\n<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Đánh giá định lượng RB-DA</title>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@600;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap">'
            '<style>%s</style></head><body><main>\n%s\n</main></body></html>\n' % (CSS_TRANG, than))


# ----------------------------------------------------------------------------- main
TEP = ["doi_chieu_so_lieu.json", "mac_dinh.json", "co_che_doi_chung.json", "bien_the_tieu_chi.json", "quet_quy_mo.json",
       "thoi_gian.json", "nhieu_buoi.json", "bo_co_san.json", "tinh_nang.json"]


def kiem_tu_cam(md):
    """Trả các dòng do AI soạn (ngoài ô HS) có từ đánh giá cấm."""
    bo = re.sub(r"<!-- HS:(\w+) BẮT ĐẦU.*?<!-- HS:\1 KẾT THÚC -->", "", md, flags=re.S)
    return [d for d in bo.split("\n") if any(t in d.lower() for t in TU_CAM)]


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    thu_muc = a[0] if a else ib.MAC_DINH
    J = {}
    for t in TEP:
        d = ib.doc(thu_muc, t)
        if d is None:
            print("Thiếu %s trong %s" % (t, thu_muc), file=sys.stderr)
            return 1
        J[t] = d
    cu = open(RA_MD, encoding="utf-8").read() if os.path.exists(RA_MD) else ""
    md = viet_md(J, doc_o_hs(cu))
    loi = kiem_tu_cam(md)
    if loi:
        print("Có từ đánh giá trong phần AI soạn:\n" + "\n".join(loi), file=sys.stderr)
        return 2
    q = J["quet_quy_mo.json"]
    svg = {
        "F1_duong_cong_co_che.svg": hinh_f1(J["co_che_doi_chung.json"]),
        "F2a_nv1_theo_alpha.svg": hinh_f2(q, "a.pct_nv1_tat_ca", "% được NV1 (mọi HS)", "Hình 2: % NV1 theo α"),
        "F2b_chua_xep_theo_alpha.svg": hinh_f2(q, "b.pct_chua_xep", "% chưa được xếp (mọi HS)", "Hình 2b: % chưa xếp theo α", ymax=60),
        "F3_lap_day_ti_le_cau.svg": hinh_f3(J["mac_dinh.json"]),
        "F4_bien_the.svg": hinh_f4(J["bien_the_tieu_chi.json"]),
        "F5_can_tren.svg": hinh_f2(q, "b.gia_uu_tien_on_dinh", "Cận trên − số em được xếp", "Hình 5: chênh với cận trên", ymax=120),
        "F6_thoi_gian.svg": hinh_f6(J["thoi_gian.json"]),
    }
    os.makedirs(THU_MUC_ANH, exist_ok=True)
    for t, s in svg.items():
        with open(os.path.join(THU_MUC_ANH, t), "w", encoding="utf-8") as f:
            f.write(s + "\n")
    with open(RA_MD, "w", encoding="utf-8") as f:
        f.write(md)
    with open(RA_HTML, "w", encoding="utf-8") as f:
        f.write(viet_html(md, svg))
    print("Đã ghi %s, %s và %d hình trong %s" % (os.path.relpath(RA_MD, GOC), os.path.relpath(RA_HTML, GOC), len(svg), os.path.relpath(THU_MUC_ANH, GOC)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
