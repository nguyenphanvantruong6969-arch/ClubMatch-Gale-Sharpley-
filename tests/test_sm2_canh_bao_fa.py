"""SM2-L1: không FA thì vẫn báo `wharton_chua_dung_het`; FA thì không báo nhiễu (huy chương soát bằng FA). Dữ liệu MÔ PHỎNG."""
import base64
import os

import cau_hinh_ws as ch
import so_nhap

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAU = [os.path.join(GOC, "du_lieu_test", t) for t in ("SO_NHAP_MAU_DAY_DU.xlsx", "SO_NHAP_FA_MAU_120HS.xlsx")]


def _b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _ma(ra):
    return [e["code"] for e in (ra.get("errors") or []) + ((ra.get("data") or {}).get("warnings") or [])]


def test_fa_khong_bao_wharton_chua_dung_het(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    for p in MAU:
        ra = api.import_so_nhap(_b64(p))
        assert ra["ok"], ra
        assert "wharton_chua_dung_het" not in _ma(ra), p


def test_khong_fa_quy_trong_van_bao(api, tmp_path):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": True}})
    clubs = [{"club_id": "C%d" % i, "name": "CLB %d" % i, "capacity": 10, "reserve_capacity": 0,
              "reserve_group": "", "buoi": ""} for i in range(3)]
    hs = [{"student_id": "h%d" % i, "name": "Em %d" % i, "reserve_group": "",
           "nv": [{"club_id": "C0", "thi": False, "diem": "", "diem_w": 10},
                  {"club_id": "C1", "thi": False, "diem": ""}]} for i in range(3)]
    p = str(tmp_path / "dqt.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs, luon_co_cot_w=True)
    ra = api.import_so_nhap(_b64(p))
    assert "wharton_chua_dung_het" in _ma(ra), ra


def test_fa_the_quan_ly_wharton_khong_bao_quy_chua_dung_het(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    assert api.import_so_nhap(_b64(MAU[0]))["ok"]
    ra = api.list_wharton_canh_bao()
    assert ra["ok"], ra
    assert not any("wharton_chua_dung_het" in d.get("ma_loi", []) for d in ra["data"])
