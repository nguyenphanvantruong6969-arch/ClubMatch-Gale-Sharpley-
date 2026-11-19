"""UX1B-L4-B: "Báo cáo tổng hợp" cho hiệu trưởng — chỉ chỉ số gộp, MỘT tệp HTML tự đủ.

`gom_du_lieu(api)` lấy số liệu từ chính các hàm tổng hợp sẵn có (`get_dashboard_status`, `get_do_phu`,
`get_club_fill_stats`, `get_phan_bo_nguyen_vong`) cộng số em chưa có chỗ theo lớp, và CHỈ giữ các khoá cho phép
(danh sách trắng): không mã, tên, điểm hay số bốc thăm của học sinh nào. `dung_html(du, nhan)` là hàm thuần,
mọi giá trị qua `html.escape`; không tệp hay địa chỉ ngoài. Chỉ đọc: không dính `compute_club_priority`.
"""

from html import escape

from nhan_ws import dien as dien_nhan

_CSS = """
body{font-family:Arial,"Segoe UI",sans-serif;color:#111;margin:0;padding:14mm 16mm}
h1{font-size:18pt;margin:0 0 2mm}
h2{font-size:13pt;margin:7mm 0 2mm}
.phu{font-size:10pt;color:#444;margin:0 0 4mm}
.the{display:flex;gap:4mm;flex-wrap:wrap}
.o{border:1px solid #444;padding:2mm 4mm;min-width:32mm}
.o b{display:block;font-size:16pt}
table{border-collapse:collapse;width:100%;font-size:10pt;margin-top:2mm}
th,td{border:1px solid #444;padding:1.5mm 2mm;text-align:left}
th{background:#eee}
td.so{text-align:right}
.thanh{background:#dcfce7;border:1px solid #444;height:3mm}
@media print{body{padding:0}}
"""


def gom_du_lieu(api) -> dict:
    """Số liệu tổng hợp (danh sách trắng khoá). Trả dict {the, clb, nguyen_vong, lop}; KHÔNG có mã/tên học sinh."""
    dash = api.get_dashboard_status()["data"]
    phu = api.get_do_phu()["data"]
    fill = api.get_club_fill_stats()["data"]
    nv = api.get_phan_bo_nguyen_vong()["data"]
    with api._ket_noi_doc() as cur:
        lop_rows = cur.execute("""
            SELECT s.class_id AS lop, COUNT(*) AS n,
                   SUM(CASE WHEN x.so_clb = 0 THEN 1 ELSE 0 END) AS chua_xep
            FROM (SELECT student_id, SUM(CASE WHEN club_id IS NOT NULL THEN 1 ELSE 0 END) AS so_clb
                  FROM match_results GROUP BY student_id) x
            JOIN students s ON s.student_id = x.student_id
            GROUP BY s.class_id
        """).fetchall()
    lop = [{"lop": (r[0] or None) if r[0] != "" else None, "n": r[1], "chua_xep": r[2] or 0} for r in lop_rows]
    lop.sort(key=lambda d: (d["lop"] is None, api._khoa_lop_tu_nhien(d["lop"]) if d["lop"] else ()))
    n_chua = phu["so_em_trang_tay"]
    tong = phu["tong_hoc_sinh"]
    return {
        "ket_qua_cu": bool(api._ket_qua_cu()),
        "the": {
            "n_students": dash["n_students"], "n_clubs": dash["n_clubs"], "n_matched": dash["n_matched"],
            "n_chua_xep": n_chua,
            "ti_le_xep": round(100.0 * (tong - n_chua) / tong, 1) if tong else 0.0,
            "trung_binh_clb": phu["trung_binh_clb"],
        },
        "clb": [{"name": c["name"], "buoi": c.get("buoi"), "capacity": c["capacity"], "matched": c["matched"],
                 "so_dang_ky": c["so_dang_ky"], "tu_do": bool(c.get("tu_do"))} for c in fill],
        "nguyen_vong": {"phan_bo": nv["phan_bo"], "ngoai_danh_sach": nv["ngoai_danh_sach"],
                        "tong_da_xep": nv["tong_da_xep"]},
        "lop": lop,
    }


def _e(v):
    return escape(str(v))


def dung_html(du: dict, nhan: dict | None = None) -> str:
    """HTML một tệp từ `gom_du_lieu`. `nhan` = nhãn workspace (điền {person_l}, {slot_l}, {cohort_l}…)."""
    def d(mau):
        return dien_nhan(mau, nhan)
    the = du["the"]
    o = [("Số {person_l}", the["n_students"]), ("Số {slot_l}", the["n_clubs"]),
         ("Đã có {slot_l}", the["n_matched"]), ("Chưa có {slot_l}", the["n_chua_xep"]),
         ("Tỉ lệ có {slot_l}", "%s%%" % the["ti_le_xep"])]
    p = ['<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>'
         % (_e(d("Báo cáo tổng hợp")), _CSS),
         "<h1>%s</h1>" % _e(d("Báo cáo tổng hợp")),
         '<p class="phu">%s</p>' % _e(d("Chỉ số gộp, không có tên, mã, điểm hay số bốc thăm của từng {person_l}.")),
         ('<p class="phu"><b>%s</b></p>' % _e(d("Dữ liệu đã được sửa sau lần xếp gần nhất, nên số liệu có thể đã cũ. Hãy xếp lại trước khi công bố."))
          if du.get("ket_qua_cu") else ""),
         '<div class="the">' + "".join('<div class="o">%s<b>%s</b></div>' % (_e(d(a)), _e(b)) for a, b in o) + "</div>",
         "<h2>%s</h2>" % _e(d("Mức lấp đầy từng {slot_l}")),
         "<table><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>" % tuple(
             _e(d(x)) for x in ("{slot}", "{session}", "Chỉ tiêu", "Đã nhận", "Số đăng ký"))]
    for c in du["clb"]:
        ct = "—" if c["tu_do"] or c["capacity"] is None else c["capacity"]
        p.append('<tr><td>%s</td><td>%s</td><td class="so">%s</td><td class="so">%s</td><td class="so">%s</td></tr>'
                 % (_e(c["name"]), _e(c.get("buoi") or ""), _e(ct), _e(c["matched"]), _e(c["so_dang_ky"])))
    p.append("</table>")
    p.append("<h2>%s</h2><table><tr><th>%s</th><th>%s</th></tr>" % (
        _e(d("Mức hài lòng về nguyện vọng")), _e(d("Được nguyện vọng")), _e(d("Số {person_l}"))))
    for x in du["nguyen_vong"]["phan_bo"]:
        p.append('<tr><td>%s%s</td><td class="so">%s</td></tr>' % (_e(x["hang"]), "+" if x["gop"] else "", _e(x["so_em"])))
    if du["nguyen_vong"]["ngoai_danh_sach"]:
        p.append('<tr><td>%s</td><td class="so">%s</td></tr>' % (
            _e(d("Ngoài danh sách nguyện vọng")), _e(du["nguyen_vong"]["ngoai_danh_sach"])))
    p.append("</table>")
    p.append("<h2>%s</h2><table><tr><th>%s</th><th>%s</th><th>%s</th></tr>" % (
        _e(d("{person_l} chưa có {slot_l} theo {cohort_l}")), _e(d("{cohort}")), _e(d("Số {person_l}")),
        _e(d("Chưa có {slot_l}"))))
    for x in du["lop"]:
        p.append('<tr><td>%s</td><td class="so">%s</td><td class="so">%s</td></tr>' % (
            _e(x["lop"] if x["lop"] is not None else d("Chưa có {cohort_l}")), _e(x["n"]), _e(x["chua_xep"])))
    p.append("</table></body></html>")
    return "".join(p)
