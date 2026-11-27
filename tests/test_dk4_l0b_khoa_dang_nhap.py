"""DK4-L0b: sai PIN 5 lần cho một mã -> khoá 5 phút; quản trị mở khoá."""
import datetime

import test_dk3_api as _t3
from test_dk3_api import _dung_san, ma, ok

cd = _t3.cd


def _hs(api, qt):
    _dung_san(api, qt)
    return ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]


def _sai(pin="1234"):
    """VG1-L1: PIN sai nhưng ĐÚNG DẠNG 4 chữ số (PIN sai dạng bị chặn trước, không tính một lần sai)."""
    return "0000" if pin != "0000" else "1111"


def _gio(api, phut):
    goc = datetime.datetime(2026, 11, 25, 9, 0, 0)
    api._dk_bay_gio = lambda: goc + datetime.timedelta(minutes=phut)


def test_sai_5_lan_thi_khoa_ca_khi_nhap_dung(cd):
    api, qt = cd
    pin = _hs(api, qt)
    _gio(api, 0)
    for _ in range(4):
        assert ma(api.dk_dang_nhap("hoc_sinh", "H1", _sai(pin))) == "dk_sai_dang_nhap"
    assert ma(api.dk_dang_nhap("hoc_sinh", "H1", _sai(pin))) == "dk_sai_dang_nhap"      # lần 5
    assert ma(api.dk_dang_nhap("hoc_sinh", "H1", pin)) == "dk_tam_khoa"                # đúng PIN cũng bị từ chối
    _gio(api, 4)
    assert ma(api.dk_dang_nhap("hoc_sinh", "H1", pin)) == "dk_tam_khoa"
    _gio(api, 6)
    assert ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]                        # hết 5 phút


def test_mot_ma_bi_khoa_khong_anh_huong_ma_khac(cd):
    api, qt = cd
    _hs(api, qt)
    pin2 = ok(api.dk_hs_dat_lai_pin(qt, "H2"))["pin"]
    _gio(api, 0)
    for _ in range(5):
        api.dk_dang_nhap("hoc_sinh", "H1", _sai())
    assert ok(api.dk_dang_nhap("hoc_sinh", "H2", pin2))["token"]


def test_dang_nhap_dung_xoa_bo_dem_sai(cd):
    api, qt = cd
    pin = _hs(api, qt)
    _gio(api, 0)
    for _ in range(4):
        api.dk_dang_nhap("hoc_sinh", "H1", _sai(pin))
    ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))
    for _ in range(4):
        assert ma(api.dk_dang_nhap("hoc_sinh", "H1", _sai(pin))) == "dk_sai_dang_nhap"
    assert ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]


def test_ma_khong_co_that_cung_bi_khoa_cung_ma_loi(cd):
    api, qt = cd
    _hs(api, qt)
    _gio(api, 0)
    for _ in range(5):
        api.dk_dang_nhap("hoc_sinh", "KHONG_CO", _sai())
    assert ma(api.dk_dang_nhap("hoc_sinh", "KHONG_CO", _sai())) == "dk_tam_khoa"      # không lộ mã nào có thật


def test_quan_tri_mo_khoa(cd):
    api, qt = cd
    pin = _hs(api, qt)
    _gio(api, 0)
    for _ in range(5):
        api.dk_dang_nhap("hoc_sinh", "H1", _sai(pin))
    ds = {x["ma"]: x for x in ok(api.dk_hs_danh_sach(qt))}
    assert ds["H1"]["bi_khoa"] is True and ds["H2"]["bi_khoa"] is False
    assert ma(api.dk_mo_khoa("sai", "hoc_sinh", "H1")) == "dk_can_dang_nhap"
    ok(api.dk_mo_khoa(qt, "hoc_sinh", "H1"))
    assert ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]
    assert not {x["ma"]: x for x in ok(api.dk_hs_danh_sach(qt))}["H1"]["bi_khoa"]
    assert any(x["hanh_dong"] == "mo_khoa" for x in ok(api.dk_nhat_ky(qt)))


def test_giao_vien_khoa_va_hs_khong_mo_khoa_duoc(cd):
    api, qt = cd
    pin = _hs(api, qt)               # _dung_san đã tạo giáo viên "Cô An"
    _gio(api, 0)
    for _ in range(5):
        api.dk_dang_nhap("giao_vien", "Cô An", _sai())
    assert ma(api.dk_dang_nhap("giao_vien", "Cô An", _sai())) == "dk_tam_khoa"
    assert ok(api.dk_gv_danh_sach(qt))[0]["bi_khoa"] is True
    h = ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]
    assert ma(api.dk_mo_khoa(h, "giao_vien", "Cô An")) == "dk_khong_du_quyen"
    ok(api.dk_mo_khoa(qt, "giao_vien", "Cô An"))
    assert not ok(api.dk_gv_danh_sach(qt))[0]["bi_khoa"]
