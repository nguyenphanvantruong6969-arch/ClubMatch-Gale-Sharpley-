"""DKL-K: id mà API trả về phải là id của chính dòng vừa tạo, không phải id dòng nhật ký ghi ngay sau đó.
Hai hàm từng trả `cur.lastrowid` SAU khi ghi nhật ký: `dk_phong_luu` (phong_id) và `dk_gv_tu_dang_ky` (gv_id). Dữ liệu MÔ PHỎNG."""
import pytest

from api import PipelineAPI


def _ok(r):
    assert r["ok"], r
    return r["data"]


@pytest.fixture()
def cong(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TR1", ["T2", "T3"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    return api, qt


def test_phong_luu_tra_dung_phong_id(cong):
    api, qt = cong
    tra = [_ok(api.dk_phong_luu(qt, "P%d" % k, 10 + k))["phong_id"] for k in range(1, 4)]
    that = {p["ten"]: p["phong_id"] for p in _ok(api.dk_phong_danh_sach(qt))}
    assert tra == [that["P1"], that["P2"], that["P3"]]


def test_gv_tu_dang_ky_tra_dung_gv_id(cong):
    api, qt = cong
    _ok(api.dk_phong_luu(qt, "P1", 20))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    tra = [_ok(api.dk_gv_tu_dang_ky("TR1", "Cô %d" % k, "1234"))["gv_id"] for k in range(1, 4)]
    that = {g["ten"]: g["gv_id"] for g in _ok(api.dk_gv_danh_sach(qt))}
    assert tra == [that["Cô 1"], that["Cô 2"], that["Cô 3"]]
