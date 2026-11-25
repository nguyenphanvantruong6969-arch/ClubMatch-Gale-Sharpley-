"""DK4-L0a: không bao giờ gửi str(e) lên giao diện; chi tiết kỹ thuật chỉ vào nhật ký."""
import logging
import sqlite3

import test_dk3_api as _t3
from test_dk3_api import ma
from test_dk4_chot_va_xep import _dang_ky_va_cham

cd = _t3.cd
BI_MAT = "SELECT bi_mat FROM bang_that"


def _khong_lo(r):
    s = repr(r)
    assert BI_MAT not in s and "bang_that" not in s, r


def test_dk_chay_khong_lo_chi_tiet_loi(cd, monkeypatch, caplog):
    api, qt = cd

    def hong(*a, **k):
        raise sqlite3.OperationalError("no such table: bang_that (%s)" % BI_MAT)
    monkeypatch.setattr(api, "_dk_giai_doan_hien_tai", hong)
    with caplog.at_level(logging.ERROR):
        r = api.dk_trang_thai()
    assert ma(r) == "dk_loi_chung"
    _khong_lo(r)
    assert any("bang_that" in (x.getMessage() + str(x.exc_info)) for x in caplog.records)


def test_chot_va_xep_khong_lo_chi_tiet_loi(cd, monkeypatch, caplog):
    api, qt = cd
    _dang_ky_va_cham(api, qt)

    def hong(**k):
        raise RuntimeError("no such table: bang_that (%s)" % BI_MAT)
    monkeypatch.setattr(api, "run_pipeline", hong)
    with caplog.at_level(logging.ERROR):
        r = api.dk_chot_va_xep(qt)
    assert ma(r) == "dk_chot_loi_he_thong"
    _khong_lo(r)
    assert any("bang_that" in (x.getMessage() + str(x.exc_info)) for x in caplog.records)
