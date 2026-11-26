"""DK4-L0e: "Chốt và xếp" tự bật fa_daa/wharton thì phải ghi nhật ký cổng và hiện trong phần tóm tắt."""
import test_dk3_api as _t3
from test_dk3_api import ok
from test_dk4_chot_va_xep import _dang_ky_va_cham

cd = _t3.cd


def _bat_luat(api, qt):
    return [x for x in ok(api.dk_nhat_ky(qt)) if x["hanh_dong"] == "bat_luat"]


def test_lan_dau_bat_luat_ghi_nhat_ky_va_hien_trong_tom_tat(cd):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    d = ok(api.dk_chot_va_xep(qt, 7))
    assert d["da_bat_luat"] is True
    nk = _bat_luat(api, qt)
    assert len(nk) == 1 and "fa_daa" in nk[0]["chi_tiet"] and "wharton" in nk[0]["chi_tiet"]
    assert ok(api.dk_ket_qua_xep(qt))["da_bat_luat"] is True          # tóm tắt xem lại sau đó vẫn báo


def test_da_bat_san_thi_khong_bao_va_khong_ghi_them(cd):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    ok(api.dk_chot_va_xep(qt, 7))
    d = ok(api.dk_chot_va_xep(qt, 7))
    assert d["da_bat_luat"] is False and len(_bat_luat(api, qt)) == 1
    assert ok(api.dk_ket_qua_xep(qt))["da_bat_luat"] is False
