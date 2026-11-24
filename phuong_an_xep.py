"""CB1-L1: "Văn bản phương án xếp" — bộ dựng NỘI DUNG, hàm thuần (không đọc CSDL, không ghi gì, không bốc thăm).

Một văn bản bằng lời thường cho học sinh, phụ huynh, nhà trường và ban giám khảo: luật xếp (lấy từ
`tieu_chi.mo_ta_tieu_chi`) và quy trình minh bạch. Hai bản: "du_kien" (trước lần xếp chính thức) và "chot" (sau đó).
`dung_noi_dung` chỉ trả CÁC KHOÁ TRONG DANH SÁCH TRẮNG (`KHOA_NOI_DUNG`): không mã, tên, điểm hay số bốc thăm của
học sinh nào. Hạt giống chỉ ra ở bản chốt khi người dùng tick VÀ số bốc thăm đã khoá; bản dự kiến không bao giờ có.
Biên bản bốc thăm (`fa_bien_ban`) vẫn là trang ký; module này dùng lại `THU_TU_LE`, không in mã băm danh sách,
số liệu từng buổi hay dòng ký.
"""

import hashlib
import json

import fa_bien_ban

BAN = ("du_kien", "chot")
KHOA_NOI_DUNG = frozenset({"ban", "lang", "tieu_de", "muc_tieu", "tieu_chi", "ghi_chu", "quy_trinh", "chot",
                           "dau_van_tay", "hat_giong", "canh_bao", "buoc_le", "cau", "truong"})
MOC = ("cong_bo", "chot_du_lieu", "boc_hat_giong", "chay_xep", "cong_bo_ket_qua")

# Câu của văn bản, mỗi ngôn ngữ một bộ (cùng kiểu `tieu_chi.GHI_CHU`). Xuất tệp luôn bằng tiếng Việt;
# bộ tiếng Anh để dành cho khi cần.
CAU = {
    "vi": {
        "tieu_de": {"du_kien": "Phương án xếp — BẢN DỰ KIẾN", "chot": "Phương án xếp — BẢN CHỐT"},
        "gioi_thieu": {
            "du_kien": "Nhà trường gửi đến các em và quý phụ huynh cách dự định xếp học sinh vào câu lạc bộ. Mọi người cùng xem trước, rồi mới đến lần xếp chính thức.",
            "chot": "Đây là cách nhà trường đã chốt để xếp học sinh vào câu lạc bộ. Luật dưới đây sẽ được dùng cho lần xếp chính thức.",
        },
        "banner": "CÁCH XẾP HỌC SINH VÀO CÂU LẠC BỘ",
        "nhan_ban": {"du_kien": "BẢN DỰ KIẾN", "chot": "BẢN CHỐT"},
        "muc_tieu": "Nhà trường ưu tiên điều gì?",
        "tieu_chi": "Khi một câu lạc bộ hết chỗ, ai được xét trước?",
        "quy_trinh": "Từng bước đi đến kết quả",
        "tang_1_tt": "Trước hết", "tang_1": "Các bạn đã làm bài thi của CLB",
        "tang_2_tt": "Sau đó", "tang_2": "Các bạn còn lại",
        "tang_chung_tt": "Với tất cả", "tang_chung": "Mọi học sinh cùng một thứ tự",
        "luu_y": "Lưu ý",
        "xac_nhan": "Dấu xác nhận",
        "xac_nhan_mo_ta": "Dấu vân tay là chuỗi ký tự cho biết luật và dữ liệu không bị thay đổi sau khi chốt.",
        "khong_dung": "Cài đặt không có tác dụng",
        "da": "Đã làm", "chua": "Chưa làm",
        "chot_nguoi": "Người chốt phương án", "chot_luc": "Thời điểm chốt", "bam_luat": "Dấu vân tay của luật xếp",
        "dau_van_tay": "Dấu vân tay dữ liệu", "hat_giong": "Hạt giống", "khoa_luc": "Khoá số bốc thăm lúc",
        "le_ky": "Biên bản bốc thăm có chữ ký là tài liệu riêng; văn bản này không thay thế biên bản đó.",
        "buoc_le": "Bốc thăm có người chứng kiến",
        "moc": {
            "cong_bo": ("Công bố phương án", "Phương án đã được công bố"),
            "chot_du_lieu": ("Chốt dữ liệu và lấy dấu vân tay", "Dữ liệu đã chốt, có dấu vân tay"),
            "boc_hat_giong": ("Bốc hạt giống có người chứng kiến và khoá số bốc thăm", "Hạt giống đã bốc, số bốc thăm đã khoá"),
            "chay_xep": ("Chạy xếp chính thức", "Đã chạy xếp chính thức"),
            "cong_bo_ket_qua": ("Công bố kết quả và nhận khiếu nại", "Đã công bố kết quả"),
        },
        "chua_chot_du_lieu": "chưa chốt dữ liệu",
        "han": "Nhận khiếu nại trong {n} ngày kể từ khi công bố kết quả.",
        "sau_cong_bo": "Hạn khiếu nại tính từ khi công bố kết quả.",
        "khong_khieu_nai": "Không áp dụng bước nhận khiếu nại.",
        "canh_bao": {
            "doi_sau_chot": "Phương án đã đổi sau khi chốt: luật đang cài khác luật đã chốt. Hãy chốt lại rồi xuất lại.",
            "xep_khac_chot": "Lần xếp chính thức không dùng phương án đã chốt.",
        },
    },
    "en": {
        "tieu_de": {"du_kien": "Allocation plan — DRAFT", "chot": "Allocation plan — FINAL"},
        "gioi_thieu": {
            "du_kien": "This is the draft: the rules the school plans to use, published before the official allocation.",
            "chot": "This is the final version: the rules the school has fixed and published for the official allocation.",
        },
        "banner": "HOW STUDENTS ARE PLACED IN CLUBS",
        "nhan_ban": {"du_kien": "DRAFT", "chot": "FINAL"},
        "muc_tieu": "What the school prioritises",
        "tieu_chi": "When a club is full, who is considered first?",
        "quy_trinh": "Step by step to the result",
        "tang_1_tt": "First", "tang_1": "Students who took the club's test",
        "tang_2_tt": "Then", "tang_2": "Everyone else",
        "tang_chung_tt": "Everyone", "tang_chung": "All students in one order",
        "luu_y": "Note",
        "xac_nhan": "Confirmation",
        "xac_nhan_mo_ta": "A fingerprint is a string of characters showing the rules and data were not changed after fixing.",
        "khong_dung": "Settings with no effect",
        "da": "Done", "chua": "Not yet",
        "chot_nguoi": "Plan fixed by", "chot_luc": "Time fixed", "bam_luat": "Fingerprint of the rules",
        "dau_van_tay": "Data fingerprint", "hat_giong": "Seed", "khoa_luc": "Lottery numbers locked at",
        "le_ky": "The signed draw record is a separate document; this text does not replace it.",
        "buoc_le": "The draw, with a witness",
        "moc": {
            "cong_bo": ("Publish the plan", "Plan published"),
            "chot_du_lieu": ("Fix the data and take its fingerprint", "Data fixed, fingerprint taken"),
            "boc_hat_giong": ("Draw the seed with a witness and lock the lottery numbers", "Seed drawn, lottery numbers locked"),
            "chay_xep": ("Run the official allocation", "Official allocation run"),
            "cong_bo_ket_qua": ("Publish results and take complaints", "Results published"),
        },
        "chua_chot_du_lieu": "data not yet fixed",
        "han": "Complaints are accepted for {n} days after the results are published.",
        "sau_cong_bo": "The complaint period starts when the results are published.",
        "khong_khieu_nai": "No complaint step applies.",
        "canh_bao": {
            "doi_sau_chot": "The plan changed after it was fixed: the current rules differ from the fixed ones. Fix it again and re-export.",
            "xep_khac_chot": "The official allocation did not use the fixed plan.",
        },
    },
}


def _lang(lang):
    return "en" if lang == "en" else "vi"


def _muc_tieu_gon(muc_tieu):
    if not isinstance(muc_tieu, dict) or not muc_tieu.get("id"):
        return None
    return {"id": muc_tieu["id"], "nhom": muc_tieu.get("nhom")}


def bam_luat(cfg) -> str:
    """SHA-256 (hex) của luật xếp VÀ mục tiêu đã chọn: `{"rules", "muc_tieu": {id, nhom}|None}` theo khoá sắp xếp.

    Chỉ hai thứ đó (không `truoc`, tên, nhãn…): đổi luật hay đổi thẻ là đổi dấu vân tay, đổi cách gọi thì không."""
    cfg = cfg or {}
    goc = {"rules": cfg.get("rules") or {}, "muc_tieu": _muc_tieu_gon(cfg.get("muc_tieu"))}
    return hashlib.sha256(json.dumps(goc, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def trang_thai_quy_trinh(moc, lang="vi") -> list:
    """Năm mốc của quy trình, mỗi mốc `{ma, da, luc, chu}`.

    `moc` = `{chot: {luc, nguoi}|None, dvt: {dau_van_tay, luc}|None, khoa: {is_locked, locked_at}|None,
    run: {run_at}|None, rules: {...}}` (bên gọi đọc từ CSDL). Mốc chưa làm: `da=False`, `luc=None`."""
    c = CAU[_lang(lang)]
    moc = moc or {}
    chot, dvt, khoa, run = moc.get("chot"), moc.get("dvt"), moc.get("khoa"), moc.get("run")
    khoa_ok = bool(khoa and khoa.get("is_locked"))
    xong = {
        "cong_bo": (bool(chot), (chot or {}).get("luc")),
        "chot_du_lieu": (bool(dvt), (dvt or {}).get("luc")),
        "boc_hat_giong": (khoa_ok, (khoa or {}).get("locked_at") if khoa_ok else None),
        "chay_xep": (bool(run), (run or {}).get("run_at")),
        "cong_bo_ket_qua": (False, None),
    }
    ra = []
    for ma in MOC:
        da, luc = xong[ma]
        ten, ten_xong = c["moc"][ma]
        chu = ten_xong if da else ten
        if ma == "chot_du_lieu" and not da:
            chu = "%s (%s)" % (ten, c["chua_chot_du_lieu"])
        if ma == "cong_bo_ket_qua":
            r = moc.get("rules") or {}
            chu = "%s. %s" % (ten, c["han"].format(n=int(r.get("fa_khieu_nai_so_ngay", 3)))
                              if r.get("fa_khieu_nai") else c["khong_khieu_nai"])
        ra.append({"ma": ma, "da": da, "luc": luc, "chu": chu})
    return ra


def _canh_bao(ban, chot, bam_hien_tai, moc, lang):
    c = CAU[_lang(lang)]["canh_bao"]
    ra = []
    if chot and bam_hien_tai and chot.get("bam_luat") and bam_hien_tai != chot["bam_luat"]:
        ra.append({"ma": "doi_sau_chot", "chu": c["doi_sau_chot"]})
    if chot and (moc or {}).get("lan_xep_khop") is False:
        ra.append({"ma": "xep_khac_chot", "chu": c["xep_khac_chot"]})
    return ra


def _cau_muc_tieu(muc_tieu, lang):
    """Tên + câu một dòng của thẻ mục tiêu (nguồn `muc_tieu.BO_MUC_TIEU`); nhóm giữ chỗ nêu tên nhóm."""
    import muc_tieu as mt
    mtg = _muc_tieu_gon(muc_tieu)
    if mtg is None or mtg["id"] not in mt.BO_MUC_TIEU:
        return None
    the = mt.BO_MUC_TIEU[mtg["id"]]
    ln = _lang(lang)
    cau = the["cau"][ln]
    if mtg["nhom"]:
        cau = "%s (%s)" % (cau, mtg["nhom"])
    return {"id": mtg["id"], "tieu_de": the["tieu_de"][ln], "cau": cau}


def dung_noi_dung(ban, tieu_chi, muc_tieu, moc, chot, bam_hien_tai, in_hat_giong, hat_giong, lang="vi", truong=None) -> dict:
    """Nội dung văn bản (dict chỉ gồm khoá trong `KHOA_NOI_DUNG`).

    `ban`: "du_kien" | "chot" (khác: ValueError). `tieu_chi`: kết quả `tieu_chi.mo_ta_tieu_chi(rules, lang)`.
    `chot`: giá trị khoá `chot_phuong_an` hoặc None. `hat_giong`: `{seed, locked_at}` hoặc None (chưa khoá).
    Bản dự kiến: không dấu vân tay dữ liệu, không người chốt, KHÔNG BAO GIỜ hạt giống (kể cả `in_hat_giong=True`).
    Bản chốt: hạt giống chỉ khi `in_hat_giong` và đã khoá (có `seed`)."""
    if ban not in BAN:
        raise ValueError("ban phải là 'du_kien' hoặc 'chot', nhận %r." % (ban,))
    import tieu_chi as tc
    ln = _lang(lang)
    c = CAU[ln]
    moc = moc or {}
    nd = {
        "ban": ban, "lang": ln, "tieu_de": c["tieu_de"][ban], "cau": c["gioi_thieu"][ban],
        "muc_tieu": _cau_muc_tieu(muc_tieu, ln),
        "tieu_chi": [dict(d) for d in (tieu_chi or [])],
        "ghi_chu": tc.GHI_CHU[ln],
        "quy_trinh": trang_thai_quy_trinh(moc, ln),
        "canh_bao": _canh_bao(ban, chot, bam_hien_tai, moc, ln),
        "buoc_le": list(fa_bien_ban.THU_TU_LE),
    }
    if truong and str(truong).strip():
        nd["truong"] = str(truong).strip()        # tên trường/không gian làm việc, in lên băng đầu trang
    if ban == "chot":
        if chot:
            nd["chot"] = {"nguoi": chot.get("nguoi"), "luc": chot.get("luc"), "bam_luat": chot.get("bam_luat")}
        dvt = moc.get("dvt")
        if dvt and dvt.get("dau_van_tay"):
            nd["dau_van_tay"] = dvt["dau_van_tay"]
        if in_hat_giong and hat_giong and hat_giong.get("seed") is not None:
            nd["hat_giong"] = {"seed": hat_giong["seed"], "locked_at": hat_giong.get("locked_at")}
    return nd


# Bảng màu của PDF: CHỈ các mức xám (Truong, 24/11: không dùng màu), nên in đen trắng vẫn đọc được.
_MAU = {"ink": "#141414", "ink2": "#333333", "slate": "#666666", "nhan": "#4D4D4D", "nhat": "#BDBDBD",
        "nen": "#F5F5F5", "nen2": "#E9E9E9", "vien": "#CFCFCF"}
_RONG_MM = 186          # A4 210 mm trừ lề 12 mm mỗi bên (`xuat_pdf.LE_MM`)
_THUT_MM = 10           # thụt hai bên cho phần thân (banner ăn hết bề ngang)


def _chia32(h):
    """Dấu vân tay 64 ký tự: ngắt hai dòng cho vừa thẻ (văn bản trích ra vẫn liền khi bỏ xuống dòng)."""
    h = str(h)
    return "<br/>".join(h[i:i + 32] for i in range(0, len(h), 32))


def dung_pdf(nd: dict, duong: str) -> str:
    """Ghi `nd` (kết quả `dung_noi_dung`) ra PDF A4 qua `xuat_pdf`. Trả đường dẫn thật đã ghi.

    Chỉ in chữ có trong `nd` (cộng câu dẫn cố định ở `CAU`); không thêm gì khác (không bảng so sánh, không phụ lục).
    Bố cục: băng đầu trang, mục tiêu, hai cột thứ tự xét, ghi chú, các mốc quy trình có chấm trạng thái, thẻ dấu xác
    nhận (bản chốt), các bước bốc thăm."""
    import xuat_pdf
    xuat_pdf.san_sang()
    from reportlab.graphics.shapes import Circle, Drawing, String
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Indenter, KeepTogether, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus.flowables import HRFlowable
    from xml.sax.saxutils import escape as e

    c = CAU[nd["lang"]]
    mau = {k: colors.HexColor(v) for k, v in _MAU.items()}
    dam, thuong = "BeVietnamPro-Bold", "BeVietnamPro"
    kieu = {}

    def st(ten, **kw):
        if ten not in kieu:
            base = dict(fontName=thuong, fontSize=10.5, leading=15, textColor=mau["ink2"])
            base.update(kw)
            kieu[ten] = ParagraphStyle(ten, **base)
        return kieu[ten]

    def p(chu, ten="than", **kw):
        return Paragraph(e("" if chu is None else str(chu)), st(ten, **kw))

    def px(html, ten="than", **kw):
        return Paragraph(html, st(ten, **kw))

    def tieu(chu):
        return [Spacer(1, 4), p(chu, "h2", fontName=dam, fontSize=13.5, leading=17, textColor=mau["ink"]),
                HRFlowable(width=16 * mm, thickness=2.2, color=mau["nhan"], spaceBefore=2, spaceAfter=5, hAlign="LEFT")]

    def the(noi_dung, nen, vien=None, vach=None, rong=None, dem=8):
        t = Table([[noi_dung]], colWidths=[rong or (_RONG_MM - 2 * _THUT_MM) * mm])
        lenh = [("BACKGROUND", (0, 0), (-1, -1), nen), ("LEFTPADDING", (0, 0), (-1, -1), dem + 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), dem), ("TOPPADDING", (0, 0), (-1, -1), dem),
                ("BOTTOMPADDING", (0, 0), (-1, -1), dem)]
        if vien:
            lenh.append(("BOX", (0, 0), (-1, -1), 0.6, vien))
        if vach:
            lenh.append(("LINEBEFORE", (0, 0), (0, -1), 3.5, vach))
        t.setStyle(TableStyle(lenh))
        return t

    def cham(xong):
        d = Drawing(14, 14)
        d.add(Circle(7, 7, 5.2, fillColor=mau["ink"] if xong else colors.white,
                     strokeColor=mau["ink"] if xong else mau["slate"], strokeWidth=1.4))
        if xong:
            d.add(Circle(7, 7, 1.9, fillColor=colors.white, strokeColor=colors.white))
        return d

    def so(n):
        d = Drawing(16, 16)
        d.add(Circle(8, 8, 7.4, fillColor=mau["nhan"], strokeColor=mau["nhan"]))
        d.add(String(8, 4.6, str(n), fontName=dam, fontSize=9, fillColor=colors.white, textAnchor="middle"))
        return d

    def gio(x):
        """"2026-11-24T11:13:36" hoặc "2026-11-24 11:13:36" -> "24/11/2026, 11:13"; không đọc được thì giữ nguyên."""
        import datetime
        try:
            return datetime.datetime.fromisoformat(str(x)).strftime("%d/%m/%Y, %H:%M")
        except ValueError:
            return str(x)

    khoi = []
    # ---- băng đầu trang
    nhan = Table([[p(c["nhan_ban"][nd["ban"]], "nhan", fontName=dam, fontSize=9.5, leading=12, textColor=mau["ink"])]],
                 colWidths=[(34 if nd["ban"] == "chot" else 38) * mm])
    nhan.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("LEFTPADDING", (0, 0), (-1, -1), 9),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 3),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    nhan.hAlign = "LEFT"
    ten_ban = Table([[p(c["banner"], "bn", fontName=dam, fontSize=8.5, leading=11, textColor=mau["nhat"])],
                     [p(nd["tieu_de"].split(" — ")[0], "bt", fontName=dam, fontSize=19, leading=23, textColor=colors.white)]]
                    + [[Table([[nhan, p(nd["truong"], "tr", fontSize=12, leading=15, textColor=mau["nhat"])
                                if nd.get("truong") else ""]], colWidths=[(34 if nd["ban"] == "chot" else 38) * mm + 10,
                                                                     (_RONG_MM - 2 * _THUT_MM - 40) * mm],
                                    style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                           ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                                           ("BOTTOMPADDING", (0, 0), (-1, -1), 0)])]],
                    colWidths=[_RONG_MM * mm])
    ten_ban.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), mau["ink"]),
                                 ("LEFTPADDING", (0, 0), (-1, -1), _THUT_MM * mm),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), _THUT_MM * mm),
                                 ("TOPPADDING", (0, 0), (0, 0), 11), ("BOTTOMPADDING", (0, 0), (0, 0), 1),
                                 ("TOPPADDING", (0, 1), (0, 1), 2), ("BOTTOMPADDING", (0, 1), (0, 1), 6),
                                 ("TOPPADDING", (0, 2), (0, -1), 0), ("BOTTOMPADDING", (0, 2), (0, -1), 11)]))
    khoi += [ten_ban, Spacer(1, 8), Indenter(left=_THUT_MM * mm, right=_THUT_MM * mm),
             p(nd["cau"], "gt", fontSize=10.5, leading=15.5, textColor=mau["ink2"])]
    for cb in nd["canh_bao"]:
        khoi += [Spacer(1, 8), the(p(cb["chu"], "cb", fontName=dam, textColor=mau["ink"]),
                                   mau["nen2"], vach=mau["ink"])]

    # ---- mục tiêu
    if nd["muc_tieu"]:
        mt = nd["muc_tieu"]
        khoi += tieu(c["muc_tieu"])
        khoi.append(the([p(mt["tieu_de"], "mt", fontName=dam, fontSize=14, leading=18, textColor=mau["ink"]),
                         Spacer(1, 1), p(mt["cau"], "mt2", fontSize=11, leading=16)], mau["nen"], vach=mau["nhan"]))

    # ---- thứ tự xét: hai cột
    khoi += tieu(c["tieu_chi"])
    cot, khong_dung = {}, []
    for d in nd["tieu_chi"]:
        (khong_dung if d["nhom"] == "khong_dung" else cot.setdefault(d["nhom"], [])).append(d)
    rong_in = (_RONG_MM - 2 * _THUT_MM) * mm

    def cot_the(nhom, rong):
        tt = c[nhom + "_tt"] if nhom + "_tt" in c else ""
        mo_ta = c[nhom]
        if len(cot) == 1:                       # chỉ xét một nhóm (luật "chỉ theo nhóm ưu tiên")
            tt, mo_ta = c["tang_chung_tt"], c["tang_chung"]
        hang = [[p(tt.upper(), "ct", fontName=dam, fontSize=8.5, leading=11, textColor=mau["slate"]), ""],
                [p(mo_ta, "cm", fontName=dam, fontSize=11, leading=15, textColor=mau["ink"]), ""]]
        for d in cot[nhom]:
            hang.append([so(d["thu_tu"]), p(d["chu"], "cd", fontSize=10.5, leading=14.5)])
        b = Table(hang, colWidths=[9 * mm, rong - 9 * mm], hAlign="LEFT")
        b.setStyle(TableStyle([("SPAN", (0, 0), (1, 0)), ("SPAN", (0, 1), (1, 1)), ("VALIGN", (0, 2), (-1, -1), "MIDDLE"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                               ("BOTTOMPADDING", (0, 1), (-1, 1), 5)]))
        return b

    nhom_co = [n for n in ("tang_1", "tang_2") if n in cot]
    if len(nhom_co) == 2:
        rc = (rong_in - 6 * mm) / 2
        trai = the(cot_the(nhom_co[0], rc - 22), mau["nen"], vien=mau["vien"], rong=rc)
        phai = the(cot_the(nhom_co[1], rc - 22), mau["nen"], vien=mau["vien"], rong=rc)
        hai = Table([[trai, "", phai]], colWidths=[rc, 6 * mm, rc])
        hai.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        khoi.append(hai)
    elif nhom_co:
        khoi.append(the(cot_the(nhom_co[0], rong_in - 22), mau["nen"], vien=mau["vien"]))
    if khong_dung:
        khoi += [Spacer(1, 6), p(c["khong_dung"], "kd", fontName=dam, fontSize=9.5, textColor=mau["slate"])]
        khoi += [p("– " + d["chu"], "kd2", fontSize=9.5, leading=13, textColor=mau["slate"]) for d in khong_dung]
    khoi += [Spacer(1, 5), the([p(c["luu_y"].upper(), "ly", fontName=dam, fontSize=8.5, leading=11, textColor=mau["ink"]),
                                Spacer(1, 2), p(nd["ghi_chu"], "ly2", fontSize=10.5, leading=15, textColor=mau["ink"])],
                               mau["nen2"], vach=mau["ink"], dem=7)]

    # ---- quy trình: chấm trạng thái, giờ nhỏ bên dưới, chữ Đã làm / Chưa làm bên phải
    hang = []
    for m in nd["quy_trinh"]:
        luc = '  <font name="%s" size="8.5" color="%s">%s</font>' % (thuong, _MAU["slate"], e(gio(m["luc"]))) if m["luc"] else ""
        hang.append([cham(m["da"]), px(e(m["chu"]) + luc, "mc", fontName=dam if m["da"] else thuong, textColor=mau["ink"],
                                       fontSize=10, leading=13.5),
                     p(c["da"] if m["da"] else c["chua"], "tt", fontName=dam, fontSize=9.5, leading=13,
                       textColor=mau["ink"] if m["da"] else mau["slate"], alignment=2)])
    qt = Table(hang, colWidths=[9 * mm, rong_in - 9 * mm - 24 * mm, 24 * mm])
    qt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 2),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("LINEBELOW", (1, 0), (-1, -2), 0.5, mau["vien"])]))
    khoi.append(KeepTogether(tieu(c["quy_trinh"]) + [qt]))

    # ---- dấu xác nhận (bản chốt) cạnh các bước bốc thăm: hai cột để cả văn bản vừa MỘT trang
    dong = []
    if "chot" in nd:
        ch = nd["chot"]
        if ch.get("nguoi"):
            dong.append((c["chot_nguoi"], e(str(ch["nguoi"])), False))
        dong.append((c["chot_luc"], e(gio(ch["luc"]) if ch.get("luc") else ""), False))
        dong.append((c["bam_luat"], _chia32(e(str(ch.get("bam_luat") or ""))), True))
    if "dau_van_tay" in nd:
        dong.append((c["dau_van_tay"], _chia32(e(nd["dau_van_tay"])), True))
    if "hat_giong" in nd:
        hg = nd["hat_giong"]
        dong.append((c["hat_giong"], e(str(hg["seed"])), True))
        if hg.get("locked_at"):
            dong.append((c["khoa_luc"], e(gio(hg["locked_at"])), False))

    def khung_trai(rong):
        noi = []
        for k, v, may in dong:
            noi += [p(k, "k", fontSize=8.5, leading=11, textColor=mau["slate"]),
                    px(v, "v_ma" if may else "v", fontName="Courier" if may else thuong, fontSize=8.5 if may else 10,
                       leading=11 if may else 13, textColor=mau["ink"], spaceAfter=3)]
        noi.append(p(c["xac_nhan_mo_ta"], "xm", fontSize=8.5, leading=11.5, textColor=mau["slate"]))
        return the(noi, mau["nen"], vien=mau["vien"], rong=rong, dem=8)

    def khung_phai(rong):
        buoc = [[so(i), p(b, "bl", fontSize=9.5, leading=12.5)] for i, b in enumerate(nd["buoc_le"], 1)]
        bt = Table(buoc, colWidths=[8 * mm, rong - 8 * mm])
        bt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 2),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        return [bt, Spacer(1, 4), p(c["le_ky"], "le", fontSize=8.5, leading=11.5, textColor=mau["slate"])]

    if dong:
        rc = (rong_in - 8 * mm) / 2
        trai = tieu(c["xac_nhan"]) + [khung_trai(rc)]
        phai = tieu(c["buoc_le"]) + khung_phai(rc)
        hai = Table([[trai, "", phai]], colWidths=[rc, 8 * mm, rc])
        hai.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        khoi.append(hai)
    else:
        khoi.append(KeepTogether(tieu(c["buoc_le"]) + khung_phai(rong_in)))
    return xuat_pdf.dung_pdf(duong, khoi)
