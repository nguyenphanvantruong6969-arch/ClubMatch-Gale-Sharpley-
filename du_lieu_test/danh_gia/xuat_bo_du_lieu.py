# -*- coding: utf-8 -*-
"""Xuất TOÀN BỘ trường mô phỏng của lượt quét DG1 ra Sổ nhập Excel + một sổ MỤC LỤC, nén thành .zip.

    python du_lieu_test/danh_gia/xuat_bo_du_lieu.py THƯ_MỤC_RA

Mỗi trường được tạo lại y hệt lúc đo (`_sinh.sinh_truong(seed, n_hs, n_clb, alpha, rho, kappa)`, cùng lưới trong
`quet_quy_mo.json`) và ghi bằng `so_nhap.ghi_so_nhap` — kéo thẳng vào phần mềm được. Mục lục ghi tình huống của từng
trường và kết quả TRUNG BÌNH của tình huống (5 trường × 10 lần bốc thăm, đọc từ JSON). Mọi dữ liệu là MÔ PHỎNG.
Tệp .zip lớn (vài chục MB) nên KHÔNG commit; chạy lại lệnh này để có lại đúng các tệp.
"""

import os
import sys
import zipfile

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
sys.path[:0] = [GOC, THU_MUC]

import _sinh  # noqa: E402
import in_bang as ib  # noqa: E402

SO_THICH = {0.0: "rat-khac", 0.25: "khac", 0.5: "vua", 0.75: "kha-giong", 0.9: "rat-giong"}
SO_THICH_VN = {0.0: "rất khác", 0.25: "khác", 0.5: "vừa", 0.75: "khá giống", 0.9: "rất giống"}


def main(argv=None):
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    a = list(sys.argv[1:] if argv is None else argv)
    ra = os.path.abspath(a[0])
    q = ib.doc(ib.MAC_DINH, "quet_quy_mo.json")
    ten_zip = os.path.join(ra, "BO_DU_LIEU_MO_PHONG_450_TRUONG.zip")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mục lục"
    ws.append(["DỮ LIỆU MÔ PHỎNG — không phải học sinh thật. Mỗi dòng là một trường; kết quả là TRUNG BÌNH của cả tình huống "
               "(5 trường × 10 lần bốc thăm)."])
    cot = ["STT", "Tệp trong .zip", "Số học sinh", "Số CLB", "Sở thích giống nhau", "Số chỗ / số học sinh", "Điểm thi", "Mã trường",
           "Tổng số chỗ", "CLB có thi", "Tình huống: % vào NV1", "Tình huống: % vào 3 NV đầu", "Tình huống: % chưa có chỗ",
           "Tình huống: % lấp đầy", "Tình huống: số trường hợp bất công"]
    ws.append(cot)
    for c in ws[2]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="DCE6F2")
    stt = 0
    with zipfile.ZipFile(ten_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for cfg in q["cac_cau_hinh"]:
            t = cfg["tham_so"]
            cs = cfg["chi_so"]
            thu_muc = "%dHS_%dCLB/sothich-%s_cho-%d_diem-%s" % (t["n_hs"], t["n_clb"], SO_THICH[t["alpha"]], round(t["kappa"] * 100),
                                                               "nangluc" if t["rho"] else "ngaunhien")
            for sdl in cfg["seed_du_lieu"]:
                stt += 1
                truong = _sinh.sinh_truong(seed=sdl, **t)
                tep = "%s/SO_NHAP_truong_%d.xlsx" % (thu_muc, sdl)
                tam = os.path.join(ra, "_tam.xlsx")
                _sinh.sinh_so_nhap(truong, tam)
                z.write(tam, tep)
                clbs = truong["clubs"]
                ws.append([stt, tep, len(truong["students"]), len(clbs), SO_THICH_VN[t["alpha"]], "%d %%" % round(t["kappa"] * 100),
                           "theo năng lực" if t["rho"] else "ngẫu nhiên", sdl, sum(v["capacity"] for v in clbs.values()),
                           sum(1 for c in truong["tested_scores"] if truong["tested_scores"][c]),
                           round(cs["a.pct_nv1_tat_ca"]["tb"], 1), round(cs["a.pct_top3_tat_ca"]["tb"], 1),
                           round(cs["b.pct_chua_xep"]["tb"], 1), round(cs["c.ty_le_lap_day"]["tb"], 1), round(cs["a.cap_chan"]["tb"])])
                if stt % 50 == 0:
                    print("  %d / %d" % (stt, len(q["cac_cau_hinh"]) * 5))
        os.remove(tam)
        for c, w in zip("ABCDEFGHIJKLMNO", [6, 62, 11, 8, 18, 18, 14, 10, 11, 10, 14, 14, 14, 14, 14]):
            ws.column_dimensions[c].width = w
        ws.freeze_panes = "A3"
        ws.auto_filter.ref = "A2:O%d" % (stt + 2)
        muc = os.path.join(ra, "MUC_LUC_450_TRUONG.xlsx")
        wb.save(muc)
        z.write(muc, "MUC_LUC_450_TRUONG.xlsx")
    print("Đã ghi %s (%d trường, %.1f MB) và %s" % (ten_zip, stt, os.path.getsize(ten_zip) / 1e6, muc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
