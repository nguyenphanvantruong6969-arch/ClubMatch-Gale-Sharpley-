# -*- coding: utf-8 -*-
"""Sinh hai tệp Excel cho cổng Đăng ký CLB (thu thập dữ liệu, DK9). DỮ LIỆU MÔ PHỎNG.

    python du_lieu_test/bo_demo_hackathon/tao_excel_dang_ky.py

  DANG_KY_DEMO.xlsx         sạch: 150 học sinh (đúng mã, tên, lớp của SO_NHAP_DEMO_DOI_CHE_DO.xlsx),
                            7 giáo viên, 8 phòng. Nạp vào cổng: 0 dòng lỗi, mỗi người một PIN.
  DANG_KY_DEMO_CO_LOI.xlsx  như trên, cài thêm 8 dòng sai cố ý (mỗi loại lỗi một dòng); dòng đúng vẫn nạp,
                            dòng sai bị bỏ qua và liệt kê kèm số dòng.

Khung tệp lấy từ chính phần mềm (`dk_excel_mau`); script tự nạp thử hai tệp vào cổng thật trên CSDL tạm.
"""
import base64
import datetime
import io
import os
import sys
import tempfile

DAY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(DAY))
sys.path.insert(0, GOC)
sys.path.insert(0, DAY)

import openpyxl  # noqa: E402

import tao_so_doi_che_do_du_tru as so_demo  # noqa: E402
from api import PipelineAPI  # noqa: E402

GIAO_VIEN = ["Cô Lê Thu Hà", "Thầy Phạm Quốc Huy", "Cô Vũ Minh Chi", "Thầy Đỗ Gia Bảo",
             "Cô Ngô Thanh Lan", "Thầy Bùi Văn Nam", "Cô Hoàng Bảo Vy"]
PHONG = [("Sân trường", 160), ("Hội trường", 160), ("Phòng 101", 40), ("Phòng 102", 40),
         ("Phòng 201", 35), ("Phòng nhạc", 35), ("Phòng STEM", 30), ("Phòng máy tính", 30)]
# (trang, dòng sai, mã lỗi phần mềm phải báo)
LOI_CAI = [("Học sinh", ["", "Trần Văn Thiếu Mã", "10A1"], "dk_excel_ma_trong"),
           ("Học sinh", ["DC 999", "Lê Mã Có Cách", "10A2"], "dk_excel_ma_sai"),
           ("Học sinh", ["DC901", "", "10A3"], "dk_excel_ten_trong"),
           ("Học sinh", ["DC902", "Phạm Thiếu Lớp", ""], "dk_excel_lop_trong"),
           ("Học sinh", ["DC903", "Vũ Khối Lạ", "13A1"], "dk_excel_khoi_ngoai"),
           ("Học sinh", ["DC001", "Trùng Mã Với Dòng Đầu", "11A1"], "dk_excel_trung_ma"),
           ("Giáo viên", ["Cô Lê Thu Hà"], "dk_excel_trung_ten"),
           ("Phòng", ["Phòng 999", 0], "dk_excel_suc_chua")]


def ok(r):
    assert r["ok"] and r["errors"] == [], r
    return r["data"]


def hoc_sinh():
    with tempfile.TemporaryDirectory() as d:
        p = so_demo.ghi(os.path.join(d, "so.xlsx"))
        ws = openpyxl.load_workbook(p)["2. Học sinh"]
        dau = [a or b for a, b in zip((c.value for c in ws[1]), (c.value for c in ws[2]))]
        cot = {k: next(i for i, v in enumerate(dau) if v == k) for k in ("Mã HS", "Họ tên", "Lớp")}
        return [[r[cot["Mã HS"]], r[cot["Họ tên"]], r[cot["Lớp"]]]
                for r in ws.iter_rows(min_row=3, values_only=True) if r[cot["Mã HS"]]]


def ghi(api, qt, duong, co_loi):
    wb = openpyxl.load_workbook(io.BytesIO(base64.b64decode(ok(api.dk_excel_mau(qt))["file_base64"])))
    hs = hoc_sinh()
    for d in hs:
        wb["Học sinh"].append(d)
    for t in GIAO_VIEN:
        wb["Giáo viên"].append([t])
    for t, sc in PHONG:
        wb["Phòng"].append([t, sc])
    if co_loi:
        for trang, dong, _ in LOI_CAI:
            wb[trang].append(dong)
    for c in wb["Học sinh"]["A"]:
        c.number_format = "@"
    wb["Hướng dẫn"].append([])
    wb["Hướng dẫn"].append(["DỮ LIỆU MÔ PHỎNG (du_lieu_test/bo_demo_hackathon/tao_excel_dang_ky.py). Không phải người thật."])
    moc = datetime.datetime(2026, 11, 28)
    wb.properties.created = wb.properties.modified = moc
    wb.save(duong)
    return len(hs)


def main():
    d = tempfile.mkdtemp()
    api = PipelineAPI(os.path.join(d, "a.db"), thu_muc_xuat=d)
    ok(api.update_workspace_config({"rules": {"wharton": False}}))   # CSDL tạm chỉ dùng cổng đăng ký: tắt tường minh (luật F1)
    ok(api.dk_khoi_tao("kiem-thu", "KIEMTHU", ["Thứ 3", "Thứ 6"], [10, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "kiem-thu"))["token"]
    for ten, co_loi in (("DANG_KY_DEMO.xlsx", False), ("DANG_KY_DEMO_CO_LOI.xlsx", True)):
        p = os.path.join(DAY, ten)
        n = ghi(api, qt, p, co_loi)
        with open(p, "rb") as f:
            b = base64.b64encode(f.read()).decode()
        xt = ok(api.dk_excel_xem_truoc(qt, b, ten))
        bao = sorted(x["ly_do"] for k in ("hoc_sinh", "giao_vien", "phong") for x in xt[k]["loi"])
        mong = sorted(x[2] for x in LOI_CAI) if co_loi else []
        assert bao == mong, (ten, bao, mong)
        assert (xt["hoc_sinh"]["tong"], xt["giao_vien"]["tong"], xt["phong"]["tong"]) == \
            (n + 6 * co_loi, len(GIAO_VIEN) + co_loi, len(PHONG) + co_loi), xt
        print(ten, "hợp lệ:", xt["so_hop_le"], "· lỗi báo đúng:", bao or "không có")
    r = ok(api.dk_excel_nap(qt, b, "DANG_KY_DEMO_CO_LOI.xlsx"))     # nạp thật: dòng đúng vào, dòng sai bị bỏ
    assert (r["hoc_sinh"]["moi"], r["giao_vien"]["moi"], r["phong"]["moi"]) == (n, len(GIAO_VIEN), len(PHONG)), r
    assert len(r["hoc_sinh"]["pin"]) == n and len(r["loi"]) == len(LOI_CAI), r
    print("nạp thật:", n, "HS ·", len(GIAO_VIEN), "GV ·", len(PHONG), "phòng · PIN cấp:",
          len(r["hoc_sinh"]["pin"]) + len(r["giao_vien"]["pin"]))


if __name__ == "__main__":
    main()
