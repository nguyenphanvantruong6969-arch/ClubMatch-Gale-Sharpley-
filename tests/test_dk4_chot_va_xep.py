"""DK4-L1/L2: dữ liệu đăng ký -> Sổ nhập -> "Chốt và xếp" (một đường, hoàn nguyên khi hỏng)."""
import base64
import sqlite3

import pytest

import dang_ky_sang_xep as dx
import test_dk3_api as _t3
from test_dk3_api import _dung_san, ma, ok

cd = _t3.cd          # dùng lại fixture của DK3


def _dang_ky_va_cham(api, qt):
    ids = _dung_san(api, qt)
    for ma_hs, nv in (("H1", [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Cờ vua"]}, {"clb_id": ids["Tự do 1"]}]),
                      ("H2", [{"clb_id": ids["Tự do 1"]}, {"clb_id": ids["Cờ vua"]}])):
        h = ok(api.dk_dang_nhap("hoc_sinh", ma_hs, ok(api.dk_hs_dat_lai_pin(qt, ma_hs))["pin"]))["token"]
        ok(api.dk_hs_luu(h, nv))
    ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    ok(api.dk_diem_dat(qt, "H1", ids["Robot"], "8"))
    return ids


def _bang(api, ten):
    c = sqlite3.connect(api.db_path)
    try:
        return c.execute("SELECT * FROM %s ORDER BY 1,2,3" % ten).fetchall()
    finally:
        c.close()


def test_l1_so_nhap_b64_nhap_0_loi(cd):
    import cau_hinh_ws as ch
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    b64 = dx.so_nhap_b64_tu_dk(ok(api.dk_xuat_ban_mau(qt)))
    assert base64.b64decode(b64)[:2] == b"PK"
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    r = api.import_so_nhap(b64)
    assert r["ok"] and r["errors"] == [], r


def test_l2_chot_va_xep_chay_tron(cd):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    truoc = len(_bang(api, "run_history"))
    d = ok(api.dk_chot_va_xep(qt, 7))
    assert d["so_hoc_sinh"] == 3 and d["seed"] == 7 and d["run_id"]
    assert len(_bang(api, "run_history")) == truoc + 1
    assert ok(api.dk_trang_thai())["giai_doan"] == "xuat"
    assert {r[0] for r in _bang(api, "match_results")} == {"H1", "H2", "H3"}
    assert any(x["hanh_dong"] == "chot_va_xep" for x in ok(api.dk_nhat_ky(qt)))
    # bấm lại: run_history chỉ thêm dòng, không bao giờ mất
    kq_truoc = _bang(api, "match_results")
    assert ma(api.dk_chot_va_xep(qt, 8)) == "dk_chot_that_bai"      # hạt giống đã khoá: seed khác bị từ chối, CSDL nguyên
    assert len(_bang(api, "run_history")) == truoc + 1 and _bang(api, "match_results") == kq_truoc
    ok(api.dk_chot_va_xep(qt, 7))                                   # cùng seed: chạy lại được
    assert len(_bang(api, "run_history")) == truoc + 2


def test_l2_tu_choi_khi_chua_den_luc_hoac_thieu_diem_hoac_sai_quyen(cd):
    api, qt = cd
    ids = _dung_san(api, qt)
    assert ma(api.dk_chot_va_xep(qt)) == "dk_sai_giai_doan"
    h = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    ok(api.dk_hs_luu(h, [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Tự do 1"]}]))
    ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    assert ma(api.dk_chot_va_xep(qt)) == "dk_thieu_diem"
    assert ma(api.dk_chot_va_xep("sai")) == "dk_can_dang_nhap"
    assert ma(api.dk_chot_va_xep(qt, "x")) == "dk_chot_seed_sai"
    assert _bang(api, "match_results") == []


@pytest.mark.parametrize("hong", ["xep", "nap"])
def test_l2_hong_giua_chung_thi_csdl_ve_nguyen_trang(cd, monkeypatch, hong):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    ten = ["students", "clubs", "club_scores", "match_results", "run_history", "dk_nguyen_vong", "dk_nhat_ky"]
    truoc = {t: _bang(api, t) for t in ten}
    gd = ok(api.dk_trang_thai())["giai_doan"]
    if hong == "xep":
        monkeypatch.setattr(api, "run_pipeline", lambda **k: (_ for _ in ()).throw(RuntimeError("no")))
    else:
        monkeypatch.setattr(api, "import_so_nhap", lambda b: {"ok": False, "errors": [{"code": "x", "params": {}}]})
    assert ma(api.dk_chot_va_xep(qt)) == ("dk_chot_loi_he_thong" if hong == "xep" else "dk_chot_that_bai")
    assert {t: _bang(api, t) for t in ten} == truoc
    assert ok(api.dk_trang_thai())["giai_doan"] == gd
