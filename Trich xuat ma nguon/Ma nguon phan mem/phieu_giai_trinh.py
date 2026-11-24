"""GT1-L3: phiếu giải trình in cho từng học sinh — MỘT tệp HTML tự đủ (không tệp / địa chỉ ngoài), mỗi học sinh một trang.

Hàm thuần: nhận kết quả đã dựng (`giai_trinh.giai_trinh_mot_hoc_sinh`) cho từng em, trả chuỗi HTML. Mọi giá trị đều qua
`html.escape`. Mỗi trang CHỈ mang mã, tên, lớp, nguyện vọng, điểm và câu giải thích của chính em đó; không số bốc thăm,
không tên hay điểm em khác. Chữ chỉ dành cho người đọc (tiếng Việt phổ thông), không mã nội bộ.
"""

from html import escape

from so_nhap import NHAN_BUOI, NHAN_LOAI_HIEN_THI

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
.tom-tat{font-size:12pt;margin:2mm 0 3mm}
.tiep-theo{border:1px solid #444;padding:2mm 4mm;margin:5mm 0;font-size:10.5pt}
.tiep-theo ul{margin:1mm 0 0;padding-left:5mm}
table.diem-thi td.thanh{width:48mm}
svg.thanh-diem{display:block}
@media print{.trang{padding:0}}
"""


def _nhan_buoi(buoi):
    if not buoi or buoi == "__mac_dinh__":
        return ""
    return _NHAN_BUOI.get(buoi, str(buoi))


def _o_chuan(x):
    loai = x.get("diem_chuan_loai")
    if loai == "diem" and x.get("diem_chuan") is not None:
        return "%s điểm" % _so(x["diem_chuan"])
    if loai == "huy_chuong" and x.get("diem_chuan"):
        return "Huy chương %s" % x["diem_chuan"]
    return {"boc_tham": "Chọn ngẫu nhiên khi bằng điểm", "con_cho": "Còn chỗ",
            "giu_cho": "Chỗ dành riêng"}.get(loai, "—")


def _nhan_loai(x):
    """Loại CLB (Tự do / Giới hạn / Tuyển chọn); "—" khi CLB chưa có loại."""
    return NHAN_LOAI_HIEN_THI.get(x.get("loai_clb")) or "—"


def _cau_cua_dong(x):
    cau = x.get("cau") or ""
    if x.get("vi_tri_cho"):
        cau = (cau + " " if cau else "") + "Hàng chờ: %s." % x["vi_tri_cho"]
    return cau


def _so(x):
    f = float(x)
    return str(int(f)) if f.is_integer() else str(round(f, 2))


def _svg_diem(diem, chuan):
    """Thanh SVG nhỏ: điểm của em (thanh) và mức vào được của CLB (vạch đứng), cùng một thang. Chỉ số, đã thoát;
    không tệp hay địa chỉ ngoài."""
    cao = max(float(diem), float(chuan) if chuan is not None else 0.0, 1.0)
    rong, w = 180.0, float(diem) / cao * 180.0
    mo_ta = "Điểm của em %s" % _so(diem) + ("; mức vào được %s" % _so(chuan) if chuan is not None else "")
    kq = ['<svg class="thanh-diem" width="%d" height="16" viewBox="0 0 %d 16" '
          'role="img" aria-label="%s"><title>%s</title>' % (rong + 4, rong + 4, escape(mo_ta), escape(mo_ta)),
          '<rect x="0" y="3" width="%d" height="10" fill="#e5e7eb"/>' % rong,
          '<rect x="0" y="3" width="%.1f" height="10" fill="#2563eb"/>' % w]
    if chuan is not None:
        x = float(chuan) / cao * rong
        kq.append('<line x1="%.1f" y1="0" x2="%.1f" y2="16" stroke="#b91c1c" stroke-width="2"/>' % (x, x))
    kq.append("</svg>")
    return "".join(kq)


def _bang_diem_thi(b):
    """Điểm của MỌI CLB em đã thi (kể cả ngoài nguyện vọng), mỗi CLB một thanh SVG. Rỗng nếu em không thi CLB nào."""
    thi = b.get("diem_da_thi") or []
    if not thi:
        return ""
    dong = ['<tr><td>%s</td><td>%s</td><td>%s</td><td class="thanh">%s</td></tr>' % (
        escape(str(x["ten_clb"])), escape(_so(x["diem_em"])), escape(_o_chuan(x)),
        _svg_diem(x["diem_em"], x["diem_chuan"] if x.get("diem_chuan_loai") == "diem" else None)) for x in thi]
    return ('<h3>Điểm các CLB em đã thi</h3><table class="diem-thi"><thead><tr><th>CLB</th><th>Điểm thi</th>'
            '<th>Mức vào được</th><th>Em so với mức vào được (vạch đỏ)</th></tr></thead><tbody>%s</tbody></table>'
            % "".join(dong))


def _bang(b, fa=False):
    dong = []
    for x in b["cac_lua_chon"]:
        cau = _cau_cua_dong(x)
        diem = x.get("diem_em") if x.get("chon_loc") else None
        o_huy = ("<td>%s</td>" % escape(x.get("huy_chuong") or "—")) if fa else ""     # UX1B-L7: chỉ chế độ huy chương
        dong.append(
            '<tr%s><td>%s</td><td>%s</td><td>%s</td>%s<td>%s</td><td>%s / %s</td><td>%s</td><td>%s</td></tr>' % (
                ' class="duoc-xep"' if x.get("duoc_xep") else "",
                "ngoài nguyện vọng" if x.get("hang") is None else escape(str(x["hang"])),
                escape(str(x["ten_clb"])), escape(_nhan_loai(x)), o_huy, "—" if diem is None else escape(str(diem)),
                escape(str(x.get("da_nhan", "?"))), "—" if x.get("suc_chua") is None else escape(str(x["suc_chua"])),
                escape(_o_chuan(x)), escape(cau)))
    return ("<table><thead><tr><th>Nguyện vọng</th><th>CLB</th><th>Loại CLB</th>%s<th>Điểm thi</th><th>Chỗ đã nhận / tối đa</th>"
            "<th>Mức vào được</th><th>Vì sao</th></tr></thead><tbody>%s</tbody></table>"
            % ("<th>Huy chương</th>" if fa else "", "".join(dong)))


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
    if gt.get("tom_tat_dong"):
        p.append('<p class="tom-tat"><b>%s</b></p>' % escape(gt["tom_tat_dong"]))
    fa = bool(gt.get("fa_bat"))
    for b in gt["buoi"]:
        nhan = _nhan_buoi(b["buoi"])
        if nhan:
            p.append("<h2>%s</h2>" % escape(nhan))
        p.append("<p><b>%s</b></p>" % escape(
            "Kết quả: %s." % (b.get("ten_clb") or b["ket_qua"]) if b["ket_qua"] else "Kết quả: chưa được xếp CLB nào."))
        if b.get("cau_tom_tat"):
            p.append("<p>%s</p>" % escape(b["cau_tom_tat"]))
        if b["cac_lua_chon"]:
            p.append(_bang(b, fa))
            if b.get("chu_thich"):
                p.append('<p class="chu-thich">%s</p>' % escape(b["chu_thich"]))
        p.append(_bang_diem_thi(b))
    if fa and gt["buoi"] and gt.get("chu_thich_huy_chuong"):
        p.append('<p class="chu-thich">%s</p>' % escape(gt["chu_thich_huy_chuong"]))
    if gt.get("buoc_tiep"):
        p.append('<div class="tiep-theo"><b>Em nên làm gì tiếp</b><ul>%s</ul></div>' % "".join(
            "<li>%s</li>" % escape(c) for c in gt["buoc_tiep"]))
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


def _khoi_pdf(xp, gt, hs, so_ngay, ma_tra_cuu, tieu_de):
    """Các khối PDF của MỘT học sinh (cùng nội dung và thứ tự với `_trang`)."""
    sid, ten, lop = hs
    k = [xp.tieu_de(tieu_de), xp.dong_khoa_gia_tri("Mã", sid), xp.dong_khoa_gia_tri("Họ tên", ten or "")]
    if lop:
        k.append(xp.dong_khoa_gia_tri("Lớp", lop))
    run = gt.get("run") or {}
    if run.get("run_at"):
        k.append(xp.dong_khoa_gia_tri("Lần xếp lúc", str(run["run_at"]).replace("T", " ")[:16]))
    if gt.get("du_lieu_da_doi"):
        k.append(xp.dong_khoa_gia_tri("Lưu ý", CANH_BAO_DA_DOI))
    if gt.get("tom_tat_dong"):
        k.append(xp.dong_khoa_gia_tri("Tóm tắt", gt["tom_tat_dong"]))
    fa = bool(gt.get("fa_bat"))                           # UX1B-L7: cột Huy chương chỉ ở chế độ huy chương
    i_cuoi = None                                         # UX1F-L2: CẢ buổi cuối (từ tiêu đề) + chú thích + chân phiếu đi liền nhau
    for i_buoi, b in enumerate(gt["buoi"]):
        i_cuoi = len(k)
        nhan = _nhan_buoi(b["buoi"])
        if nhan:
            k.append(xp.tieu_de(nhan))
        k.append(xp.dong_khoa_gia_tri(
            "Kết quả", ("%s." % (b.get("ten_clb") or b["ket_qua"])) if b["ket_qua"]
            else "chưa được xếp CLB nào."))
        if b.get("cau_tom_tat"):
            k.append(xp.dong_khoa_gia_tri("Giải thích", b["cau_tom_tat"]))
        if b["cac_lua_chon"]:
            hang = []
            for x in b["cac_lua_chon"]:
                diem = x.get("diem_em") if x.get("chon_loc") else None
                hang.append([
                    "ngoài nguyện vọng" if x.get("hang") is None else x["hang"], x["ten_clb"], _nhan_loai(x),
                    *([x.get("huy_chuong") or "—"] if fa else []),
                    "—" if diem is None else diem, "%s / %s" % (x.get("da_nhan", "?"),
                                                                 "—" if x.get("suc_chua") is None else x["suc_chua"]),
                    _o_chuan(x), _cau_cua_dong(x) + (" (đã được xếp)" if x.get("duoc_xep") else "")])
            k.append(xp.bang(["Nguyện vọng", "CLB", "Loại CLB"] + (["Huy chương"] if fa else []) +
                             ["Điểm thi", "Chỗ đã nhận / tối đa", "Mức vào được", "Vì sao"], hang,
                             [1.1, 1.6, 1.1] + ([0.9] if fa else []) + [0.9, 1.1, 1.1, 2.6 - (0.0 if not fa else 0.3)]))
            if b.get("chu_thich"):
                k.append(xp.dong_khoa_gia_tri("Ghi chú", b["chu_thich"]))
        if b.get("diem_da_thi"):                          # UX1B-L7: điểm mọi CLB em đã thi (bản PDF: bảng chữ, không thanh)
            k.append(xp.tieu_de("Điểm các CLB em đã thi"))
            k.append(xp.bang(["CLB", "Điểm thi", "Mức vào được"], [
                [x["ten_clb"], _so(x["diem_em"]), _o_chuan(x)] for x in b["diem_da_thi"]], [2, 1, 1]))
        if i_buoi < len(gt["buoi"]) - 1:                  # mỗi buổi liền một khối: tiêu đề buổi không nằm một mình ở đáy trang
            k[i_cuoi:] = [xp.giu_cung(k[i_cuoi:])]
    if fa and gt["buoi"] and gt.get("chu_thich_huy_chuong"):
        k.append(xp.dong_khoa_gia_tri("Ghi chú", gt["chu_thich_huy_chuong"]))
    if gt.get("buoc_tiep"):
        k.append(xp.dong_khoa_gia_tri("Em nên làm gì tiếp", " ".join("(%d) %s" % (i, c) for i, c in enumerate(gt["buoc_tiep"], 1))))
    if not gt["buoi"]:
        k.append(xp.dong_khoa_gia_tri("Lưu ý", "Chưa có thông tin xếp cho em."))
    k.append(xp.dong_khoa_gia_tri(
        "Khiếu nại", "Nếu thấy kết quả chưa đúng, hãy liên hệ giáo viên phụ trách" +
        (" trong %s ngày." % so_ngay if so_ngay else ".")))
    if ma_tra_cuu:
        k.append(xp.dong_khoa_gia_tri("Mã tra cứu", ma_tra_cuu))
    if i_cuoi is not None:
        k[i_cuoi:] = [xp.giu_cung(k[i_cuoi:])]
    return k


def dung_phieu_pdf(cac_em, duong, so_ngay=None, tieu_de="Phiếu giải trình kết quả xếp CLB", khi_xong_em=None) -> str:
    """Như `dung_phieu_html` nhưng ra PDF (A4 dọc, mỗi học sinh bắt đầu một trang mới). Trả đường dẫn thật đã ghi.
    `khi_xong_em(k)` (tuỳ chọn, SF-A5): báo đã dựng xong phiếu của `k` em (k = 1, 2, ..., rồi đủ số em khi ghi xong)."""
    import xuat_pdf
    khoi = []
    xong = [0]

    def qua_mot_em():
        xong[0] += 1
        khi_xong_em(xong[0])
    for gt, hs, ma in cac_em:
        if khoi:
            khoi.append(xuat_pdf.ngat_trang(qua_mot_em if khi_xong_em else None))
        khoi.extend(_khoi_pdf(xuat_pdf, gt, hs, so_ngay, ma, tieu_de))
    duong_that = xuat_pdf.dung_pdf(duong, khoi)
    if khi_xong_em:
        khi_xong_em(len(cac_em))
    return duong_that
