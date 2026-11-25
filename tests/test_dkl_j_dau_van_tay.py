"""DKL-J (API): `dk_dau_van_tay` — dấu vân tay rẻ của dữ liệu cổng, để màn quản trị biết "có đổi không" mà không phải tải lại tất cả.
Công khai (không token) như `dk_trang_thai`, và KHÔNG làm mới giờ nghỉ của phiên quản trị. Dữ liệu MÔ PHỎNG."""
from api import PipelineAPI


def _ok(r):
    assert r["ok"], r
    return r["data"]


def _cong(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TR1", ["T2", "T3"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    return api, qt


def test_dau_van_tay_khong_can_token_va_on_dinh_khi_chi_doc(tmp_path):
    api, _ = _cong(tmp_path)
    d1 = _ok(api.dk_dau_van_tay())["dau"]
    assert isinstance(d1, str) and d1
    for _ in range(3):                                    # đọc không làm đổi dấu vân tay
        api.dk_trang_thai()
    assert _ok(api.dk_dau_van_tay())["dau"] == d1


def test_dau_van_tay_doi_khi_du_lieu_doi_ke_ca_hoc_sinh_gui_nguyen_vong(tmp_path):
    api, qt = _cong(tmp_path)
    d0 = _ok(api.dk_dau_van_tay())["dau"]
    _ok(api.dk_phong_luu(qt, "P1", 40))
    d1 = _ok(api.dk_dau_van_tay())["dau"]
    assert d1 != d0
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    d2 = _ok(api.dk_dau_van_tay())["dau"]
    assert d2 != d1


def test_dau_van_tay_khong_lam_moi_gio_nghi_cua_phien_quan_tri(tmp_path):
    api, qt = _cong(tmp_path)
    phien = api._dk_phien_dict()[qt]
    phien["luc"] -= 60                                    # giả như đã nghỉ 60 giây
    luc = phien["luc"]
    for _ in range(3):
        api.dk_dau_van_tay()
    assert api._dk_phien_dict()[qt]["luc"] == luc
