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
                           "dau_van_tay", "hat_giong", "canh_bao", "buoc_le", "cau"})
MOC = ("cong_bo", "chot_du_lieu", "boc_hat_giong", "chay_xep", "cong_bo_ket_qua")

# Câu của văn bản, mỗi ngôn ngữ một bộ (cùng kiểu `tieu_chi.GHI_CHU`). Xuất tệp luôn bằng tiếng Việt;
# bộ tiếng Anh để dành cho khi cần.
CAU = {
    "vi": {
        "tieu_de": {"du_kien": "Phương án xếp — BẢN DỰ KIẾN", "chot": "Phương án xếp — BẢN CHỐT"},
        "gioi_thieu": {
            "du_kien": "Đây là bản dự kiến: các nguyên tắc xếp nhà trường dự định dùng, công bố trước lần xếp chính thức.",
            "chot": "Đây là bản chốt: các nguyên tắc xếp đã được nhà trường chốt và công bố cho lần xếp chính thức.",
        },
        "muc_tieu": "Mục tiêu đã chọn",
        "tieu_chi": "Thứ tự xét",
        "quy_trinh": "Quy trình",
        "tang_1": "Nhóm thứ nhất: người đã có điểm bài thi của câu lạc bộ",
        "tang_2": "Nhóm thứ hai: những người còn lại",
        "khong_dung": "Cài đặt không có tác dụng",
        "da": "Đã làm", "chua": "Chưa làm",
        "chot_nguoi": "Người chốt phương án", "chot_luc": "Thời điểm chốt", "bam_luat": "Dấu vân tay của luật xếp",
        "dau_van_tay": "Dấu vân tay dữ liệu", "hat_giong": "Hạt giống", "khoa_luc": "Khoá số bốc thăm lúc",
        "le_ky": "Biên bản bốc thăm có chữ ký là một tài liệu riêng; văn bản này không thay thế biên bản đó.",
        "buoc_le": "Các bước bốc thăm có người chứng kiến",
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
        "muc_tieu": "Chosen goal",
        "tieu_chi": "Order of consideration",
        "quy_trinh": "Procedure",
        "tang_1": "First group: people who have a test score for the club",
        "tang_2": "Second group: everyone else",
        "khong_dung": "Settings with no effect",
        "da": "Done", "chua": "Not yet",
        "chot_nguoi": "Plan fixed by", "chot_luc": "Time fixed", "bam_luat": "Fingerprint of the rules",
        "dau_van_tay": "Data fingerprint", "hat_giong": "Seed", "khoa_luc": "Lottery numbers locked at",
        "le_ky": "The signed draw record is a separate document; this text does not replace it.",
        "buoc_le": "Steps of the witnessed draw",
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


def dung_noi_dung(ban, tieu_chi, muc_tieu, moc, chot, bam_hien_tai, in_hat_giong, hat_giong, lang="vi") -> dict:
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
    if ban == "chot":
        if chot:
            nd["chot"] = {"nguoi": chot.get("nguoi"), "luc": chot.get("luc"), "bam_luat": chot.get("bam_luat")}
        dvt = moc.get("dvt")
        if dvt and dvt.get("dau_van_tay"):
            nd["dau_van_tay"] = dvt["dau_van_tay"]
        if in_hat_giong and hat_giong and hat_giong.get("seed") is not None:
            nd["hat_giong"] = {"seed": hat_giong["seed"], "locked_at": hat_giong.get("locked_at")}
    return nd


def dung_pdf(nd: dict, duong: str) -> str:
    """Ghi `nd` (kết quả `dung_noi_dung`) ra PDF A4 qua `xuat_pdf`. Trả đường dẫn thật đã ghi.

    Chỉ in chữ có trong `nd`; không thêm gì khác (không bảng so sánh, không phụ lục)."""
    import xuat_pdf
    c = CAU[nd["lang"]]
    k = [xuat_pdf.tieu_de(nd["tieu_de"]), xuat_pdf.doan(nd["cau"])]
    for cb in nd["canh_bao"]:
        k.append(xuat_pdf.dong_khoa_gia_tri("!", cb["chu"]))
    if nd["muc_tieu"]:
        k.append(xuat_pdf.tieu_de(c["muc_tieu"]))
        k.append(xuat_pdf.doan("%s. %s" % (nd["muc_tieu"]["tieu_de"], nd["muc_tieu"]["cau"])))
    k.append(xuat_pdf.tieu_de(c["tieu_chi"]))
    hien = None
    for d in nd["tieu_chi"]:
        if d["nhom"] == "khong_dung":
            if hien != "khong_dung":
                k.append(xuat_pdf.dong_khoa_gia_tri(c["khong_dung"], ""))
                hien = "khong_dung"
            k.append(xuat_pdf.doan("– " + d["chu"]))
            continue
        if d["nhom"] != hien:
            k.append(xuat_pdf.dong_khoa_gia_tri(c[d["nhom"]], ""))
            hien = d["nhom"]
        k.append(xuat_pdf.doan("%d. %s" % (d["thu_tu"], d["chu"])))
    k.append(xuat_pdf.doan(nd["ghi_chu"]))
    k.append(xuat_pdf.tieu_de(c["quy_trinh"]))
    for m in nd["quy_trinh"]:
        luc = " (%s)" % m["luc"] if m["luc"] else ""
        k.append(xuat_pdf.doan("%s — %s%s" % (c["da"] if m["da"] else c["chua"], m["chu"], luc)))
    if "chot" in nd:
        ch = nd["chot"]
        if ch.get("nguoi"):
            k.append(xuat_pdf.dong_khoa_gia_tri(c["chot_nguoi"], ch["nguoi"]))
        k.append(xuat_pdf.dong_khoa_gia_tri(c["chot_luc"], ch.get("luc")))
        k.append(xuat_pdf.dong_khoa_gia_tri(c["bam_luat"], ch.get("bam_luat")))
    if "dau_van_tay" in nd:
        k.append(xuat_pdf.dong_khoa_gia_tri(c["dau_van_tay"], nd["dau_van_tay"]))
    if "hat_giong" in nd:
        hg = nd["hat_giong"]
        k.append(xuat_pdf.dong_khoa_gia_tri(c["hat_giong"], hg["seed"]))
        if hg.get("locked_at"):
            k.append(xuat_pdf.dong_khoa_gia_tri(c["khoa_luc"], hg["locked_at"]))
    k.append(xuat_pdf.tieu_de(c["buoc_le"]))
    for i, b in enumerate(nd["buoc_le"], 1):
        k.append(xuat_pdf.doan("%d. %s" % (i, b)))
    k.append(xuat_pdf.doan(c["le_ky"]))
    return xuat_pdf.dung_pdf(duong, k)
