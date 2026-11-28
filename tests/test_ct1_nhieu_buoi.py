"""CT1-FIX — trường có NHIỀU buổi (bộ MÔ PHỎNG `SO_NHAP_DQT_800HS_HOP_LE`, 800 học sinh, 4 buổi).

Phát hiện 1 và 2 của `docs/ke_hoach/BAO_CAO_SOAT_MA_CT1.md`: số đếm là lượt (học sinh × buổi) nên dữ liệu phải nói
rõ `so_buoi`; ô "chưa có CLB" chỉ tính lượt CÓ nguyện vọng (khớp `truoc.chua_co`).
"""

import base64
import os

import pytest

import api as api_mod
import cau_hinh_ws

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_800 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_800HS_HOP_LE.xlsx")


@pytest.fixture(scope="module")
def d800(tmp_path_factory):
    db = str(tmp_path_factory.mktemp("ct1_800") / "app.db")
    a = api_mod.PipelineAPI(db)
    with open(BO_800, "rb") as f:
        assert a.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    assert a.run_pipeline(seed=42)["ok"]
    r = a.get_xem_xet_chi_tieu()
    assert r["ok"], r
    return r["data"]


def test_nhieu_buoi_bao_so_buoi_va_dem_theo_luot(d800):
    assert d800["so_buoi"] == 4
    assert d800["truoc"]["tong"] > d800["so_hoc_sinh"]        # lượt (học sinh × buổi), không phải học sinh


def test_o_chua_co_khop_so_chua_co(d800):
    assert len(d800["o_chua_co"]) == d800["truoc"]["chua_co"]


def test_mot_buoi_so_buoi_la_mot(tmp_path):
    import tests.test_ct1_api as t  # noqa: PLC0415
    a, _ = t._mo(tmp_path)
    assert a.get_xem_xet_chi_tieu()["data"]["so_buoi"] == 1
