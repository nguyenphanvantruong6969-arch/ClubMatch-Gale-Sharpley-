"""ST-DEM (stress đêm 26/11): ô số có dấu gạch dưới bị đọc SAI im lặng.

Python `float("1_5") == 15.0` và `int("1_0") == 10` (PEP 515). Người nhập gõ nhầm
"1_5" thì phần mềm nhận điểm 15 / chỉ tiêu 10 mà không báo gì. Phải coi là ô sai.
Dữ liệu MÔ PHỎNG.
"""
import io

import openpyxl
import pytest

import so_nhap
from tests.test_so_nhap import CLB, b64_wb, chup_csdl, hs


def _so_co(o, gia_tri):
    buf = io.BytesIO()
    so_nhap.ghi_so_nhap(buf, CLB, [hs("HS1", ("CLB Tin học", 9)), hs("HS2", "CLB Bóng rổ")])
    wb = openpyxl.load_workbook(io.BytesIO(buf.getvalue()))
    sheet = so_nhap.SHEET_HS if o == "E3" else so_nhap.SHEET_CLB
    wb[sheet][o] = gia_tri
    return b64_wb(wb)


@pytest.mark.parametrize("chuoi", ["1_5", "1_0", "_7", "8_"])
def test_doc_diem_tu_choi_gach_duoi(chuoi):
    assert so_nhap.doc_diem(chuoi) is None


def test_doc_diem_van_nhan_so_thuong():
    assert so_nhap.doc_diem("7,5") == 7.5
    assert so_nhap.doc_diem(" 8 ") == 8.0
    assert so_nhap.doc_diem("10") == 10.0


@pytest.mark.parametrize("o,ma_loi", [("E3", "so_nhap_diem_sai"), ("C2", "so_nhap_chi_tieu_sai")])
def test_so_nhap_gach_duoi_bi_bao_loi_khong_ghi(api, o, ma_loi):
    b64 = _so_co(o, "1_0")
    kq = api.import_so_nhap(b64)
    assert not kq["ok"], kq
    assert ma_loi in [e["code"] for e in kq["errors"]], kq["errors"]
    db = chup_csdl(api)
    assert db["clubs"] == [] and db["scores"] == []


def test_csv_clb_chi_tieu_gach_duoi_khong_thanh_10(api):
    kq = api.import_clubs_csv("club_id,name,capacity\nA,CLB A,1_0\nB,CLB B,3\n")
    caps = dict((r[0], r[2]) for r in chup_csdl(api)["clubs"])
    assert caps.get("A") != 10, (kq, caps)


@pytest.mark.parametrize("gia_tri", ["1_0", "1_5"])
def test_tao_clb_bang_tay_chi_tieu_gach_duoi_bi_tu_choi(api, gia_tri):
    kq = api.create_or_update_club("C", "CLB C", gia_tri, 0, "")
    assert not kq["ok"], kq
    assert [e["code"] for e in kq["errors"]] == ["club_capacity_not_integer"]
    assert chup_csdl(api)["clubs"] == []


def test_diem_nhap_tay_gach_duoi_bi_tu_choi(api):
    api.create_or_update_club("A", "CLB A", 3, 0, "")
    api.create_student_if_missing("S1", "Em 1")
    api.submit_test_selection("S1", ["A"])
    api.submit_preferences("S1", ["A"])
    kq = api.submit_club_scores("A", [{"student_id": "S1", "score": "1_5"}])
    assert not kq["ok"] and kq["errors"][0]["code"] == "score_not_a_number", kq
    assert chup_csdl(api)["scores"] == []
