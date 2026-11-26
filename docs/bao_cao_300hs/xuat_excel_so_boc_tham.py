# -*- coding: utf-8 -*-
"""Xuất bảng "Số bốc thăm theo buổi" của từng học sinh ra Excel — DỮ LIỆU MÔ PHỎNG.

    python docs/bao_cao_300hs/xuat_excel_so_boc_tham.py

Nguồn: SO_NHAP_300HS_DOI_CHE_DO.xlsx, nạp vào phần mềm, chạy xếp; số đọc bằng
api.get_so_boc_tham_theo_buoi (đúng bảng ở thẻ Chi tiết và xuất tệp). Mỗi seed một sheet.
Số nhỏ hơn được xét trước khi các em bằng nhau ở mọi tiêu chí khác.
"""
import base64
import os
import sys
import tempfile

D = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, GOC)

import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402

SEEDS = [42, 7, 2026, 12345]
BUOI = {"thu_3": "Thứ 3", "thu_6": "Thứ 6"}

d = tempfile.mkdtemp()
goc = os.path.join(d, "goc")
os.makedirs(goc)
api = PipelineAPI(ws.duong_dan_db(goc, ws.tao(goc, "Trường học", None)), thu_muc_goc_ws=goc, ws_da_chon=True)
api.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})
with open(os.path.join(D, "SO_NHAP_300HS_DOI_CHE_DO.xlsx"), "rb") as f:
    assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]

wb = Workbook()
wb.remove(wb.active)
for i, s in enumerate(SEEDS):
    assert api.run_pipeline(seed=s, force_redraw_stb=i > 0)["ok"]
    st = api.get_so_boc_tham_theo_buoi("")["data"]
    sh = wb.create_sheet("Seed %d" % s)
    sh.append(["DỮ LIỆU MÔ PHỎNG — nguồn SO_NHAP_300HS_DOI_CHE_DO.xlsx, xuất từ phần mềm, seed %d" % s])
    sh["A1"].font = Font(bold=True, color="A03020")
    dau = ["Mã HS", "Họ tên"] + ["Số bốc thăm %s" % BUOI.get(b, b) for b in st["ds_buoi"]]
    sh.append(dau)
    for c in sh[2]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E3D")
        c.alignment = Alignment(horizontal="center", wrap_text=True)
    for h in st["hoc_sinh"]:
        sh.append([h["student_id"], h["name"]] + [h["so"].get(b) for b in st["ds_buoi"]])
    for col, w in zip("ABCD", (10, 24, 16, 16)):
        sh.column_dimensions[col].width = w
    sh.freeze_panes = "A3"
    sh.auto_filter.ref = "A2:%s%d" % (chr(64 + len(dau)), sh.max_row)
ra = os.path.join(D, "SO_BOC_THAM_300HS.xlsx")
wb.save(ra)
print(ra, [ (x.title, x.max_row - 2) for x in wb.worksheets])
