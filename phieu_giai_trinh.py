"""GT1-L3: phiếu giải trình in cho từng học sinh — MỘT tệp HTML tự đủ (không tệp / địa chỉ ngoài), mỗi học sinh một trang.

Hàm thuần: nhận kết quả đã dựng (`giai_trinh.giai_trinh_mot_hoc_sinh`) cho từng em, trả chuỗi HTML. Mọi giá trị đều qua
`html.escape`. Mỗi trang CHỈ mang mã, tên, lớp, nguyện vọng, điểm và câu giải thích của chính em đó; không số bốc thăm,
không tên hay điểm em khác. Chữ chỉ dành cho người đọc (tiếng Việt phổ thông), không mã nội bộ.
"""

from html import escape

from so_nhap import NHAN_BUOI

_NHAN_BUOI = {ma: nhan for nhan, ma in NHAN_BUOI}
CANH_BAO_DA_DOI = ("Dữ liệu đã thay đổi sau lần xếp này, nên lời giải thích dưới đây có thể không còn khớp kết quả "
                   "đã lưu. Hãy hỏi giáo viên phụ trách trước khi dùng.")

_CSS = """
body{font-family:Arial,"Segoe UI",sans-serif;color:#111;margin:0}
.trang{padding:18mm 16mm;page-break-after:always;break-after:page}
.trang:last-child{page-break-after:auto;break-after:auto}
h1{font-size:18pt;margin:0 0 4mm}
h2{font-size:13pt;margin:6mm 0 2mm}
.thong-tin{font-size:11pt;margin:0 0 3mm}
.canh-bao{border:1px solid #b45309;background:#fef3c7;padding:2mm 3mm;margin:3mm 0;font-size:10.5pt}
table{border-collapse:collapse;width:100%;font-size:10pt;margin-top:2mm}
th,td{border:1px solid #444;padding:1.5mm 2mm;text-align:left;vertical-align:top}
th{background:#eee}
tr.duoc-xep td{background:#dcfce7;font-weight:bold}
.ma-tra-cuu{margin-top:8mm;font-size:12pt;min-height:8mm}
.chu-thich{margin:2mm 0 0;font-size:10pt;font-style:italic}
.khieu-nai{margin-top:6mm;font-size:10.5pt}
@media print{.trang{padding:0}}
"""


def _nhan_buoi(buoi):
    if not buoi or buoi == "__mac_dinh__":
        return ""
    return _NHAN_BUOI.get(buoi, str(buoi))


def _o_chuan(x):
    loai = x.get("diem_chuan_loai")
    if loai == "diem" and x.get("diem_chuan") is not None:
        return "%s điểm" % x["diem_chuan"]
    return {"boc_tham": "Bốc thăm", "con_cho": "Còn chỗ", "giu_cho": "Chỗ dành riêng"}.get(loai, "—")


def _bang(b):
    dong = []
    for x in b["cac_lua_chon"]:
        cau = x.get("cau") or ""
        if x.get("vi_tri_cho"):
            cau = (cau + " " if cau else "") + "Hàng chờ: %s." % x["vi_tri_cho"]
        diem = x.get("diem_em") if x.get("chon_loc") else None
        dong.append(
            '<tr%s><td>%s</td><td>%s</td><td>%s</td><td>%s / %s</td><td>%s</td><td>%s</td></tr>' % (
                ' class="duoc-xep"' if x.get("duoc_xep") else "",
                "ngoài nguyện vọng" if x.get("hang") is None else escape(str(x["hang"])),
                escape(str(x["ten_clb"])), "—" if diem is None else escape(str(diem)),
                escape(str(x.get("da_nhan", "?"))), "—" if x.get("suc_chua") is None else escape(str(x["suc_chua"])),
                escape(_o_chuan(x)), escape(cau)))
    return ("<table><thead><tr><th>Nguyện vọng</th><th>CLB</th><th>Điểm của em</th><th>Chỗ (đã nhận / tối đa)</th>"
            "<th>Mức vào được</th><th>Vì sao</th></tr></thead><tbody>%s</tbody></table>" % "".join(dong))


def _trang(gt, hs, so_ngay, ma_tra_cuu, tieu_de):
    sid, ten, lop = hs
    p = ['<section class="trang">', "<h1>%s</h1>" % escape(tieu_de)]
    p.append('<p class="thong-tin"><b>Mã:</b> %s &nbsp; <b>Họ tên:</b> %s%s</p>' % (
        escape(str(sid)), escape(ten or ""), (" &nbsp; <b>Lớp:</b> %s" % escape(lop)) if lop else ""))
    run = gt.get("run") or {}
    if run.get("run_at"):
        p.append('<p class="thong-tin">Lần xếp lúc: %s</p>' % escape(str(run["run_at"]).replace("T", " ")[:16]))
    if gt.get("du_lieu_da_doi"):
        p.append('<p class="canh-bao" role="alert">%s</p>' % escape(CANH_BAO_DA_DOI))
    for b in gt["buoi"]:
        nhan = _nhan_buoi(b["buoi"])
        if nhan:
            p.append("<h2>%s</h2>" % escape(nhan))
        p.append("<p><b>%s</b></p>" % escape(
            "Kết quả: %s." % (b.get("ten_clb") or b["ket_qua"]) if b["ket_qua"] else "Kết quả: chưa được xếp CLB nào."))
        if b.get("cau_tom_tat"):
            p.append("<p>%s</p>" % escape(b["cau_tom_tat"]))
        if b["cac_lua_chon"]:
            p.append(_bang(b))
            if b.get("chu_thich"):
                p.append('<p class="chu-thich">%s</p>' % escape(b["chu_thich"]))
    if not gt["buoi"]:
        p.append("<p>Chưa có thông tin xếp cho em.</p>")
    p.append('<div class="khieu-nai">%s</div>' % escape(
        "Nếu thấy kết quả chưa đúng, hãy liên hệ giáo viên phụ trách" +
        (" trong %s ngày." % so_ngay if so_ngay else ".")))
    p.append('<div class="ma-tra-cuu">%s</div>' % (
        escape("Mã tra cứu: %s" % ma_tra_cuu) if ma_tra_cuu else ""))
    p.append("</section>")
    return "".join(p)


def dung_phieu_html(cac_em, so_ngay=None, tieu_de="Phiếu giải trình kết quả xếp CLB") -> str:
    """`cac_em`: danh sách `(giai_trinh_cua_em, (mã, tên, lớp), mã_tra_cứu_hoặc_None)`. Trả cả tệp HTML."""
    than = "".join(_trang(gt, hs, so_ngay, ma, tieu_de) for gt, hs, ma in cac_em)
    return ('<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><title>%s</title>'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><style>%s</style></head>'
            '<body>%s</body></html>' % (escape(tieu_de), _CSS, than))
