"""Sổ mẫu đầy đủ (`du_lieu_test/tao_so_nhap_day_du.py`) luôn nạp và xếp được ở chế độ FA.

Canh để sổ mẫu không lệch khi định dạng sổ nhập (`so_nhap.py`) đổi. Dữ liệu MÔ PHỎNG.
"""
import base64
import os
import sys

import cau_hinh_ws as ch
import openpyxl
import so_nhap

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "du_lieu_test"))
import tao_so_nhap_day_du as sm  # noqa: E402


def _so(tmp_path):
    ra = str(tmp_path / "SO_NHAP_MAU_DAY_DU.xlsx")
    sm.ghi(ra)
    return ra


def test_so_co_du_cot_va_sheet(tmp_path):
    wb = openpyxl.load_workbook(_so(tmp_path))
    assert so_nhap.SHEET_GIU_CHO in wb.sheetnames
    tieu_de = [o.value for o in wb[so_nhap.SHEET_CLB][1]]
    for cot in so_nhap.COT_CLB + so_nhap.COT_FA + so_nhap.COT_GIO:
        assert cot in tieu_de
    hang1 = [o.value for o in wb[so_nhap.SHEET_HS][1]]      # hai hàng tiêu đề (A13.4)
    hang2 = [o.value for o in wb[so_nhap.SHEET_HS][2]]
    assert "Lớp" in hang1
    assert so_nhap.TEN_COT_HUY_CHUONG in hang2


def test_nap_va_xep_duoc_o_che_do_fa(api, tmp_path):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    with open(_so(tmp_path), "rb") as f:
        r = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert r["ok"], r["errors"]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM clubs WHERE loai IS NULL").fetchone()[0] == 0
        assert cur.execute("SELECT COUNT(*) FROM clubs WHERE loai='TUYEN_CHON' AND diem_san IS NULL").fetchone()[0] == 0
        assert cur.execute("SELECT COUNT(*) FROM giu_cho").fetchone()[0] == 3
        assert cur.execute("SELECT COUNT(DISTINCT class_id) FROM students").fetchone()[0] == len(sm.LOP)
    p = api.run_pipeline(3)
    assert p["ok"], p["errors"]
    assert p["data"]["n_matched"] == p["data"]["n_total"] == sm.N_HOC_SINH
