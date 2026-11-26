"""DK6-L2 (backend): quản trị đổi mật khẩu — kiểm mật khẩu cũ, băm có muối mới, nhật ký không chứa mật khẩu, chỉ quản trị."""
import sqlite3

import pytest

import test_dk3_api as t3
from test_dk3_api import ma, ok

cd = t3.cd


@pytest.fixture
def api(tmp_path):
    from api import PipelineAPI
    return PipelineAPI(str(tmp_path / "app.db"))


def _cai_dat(api):
    c = sqlite3.connect(api.db_path)
    try:
        return dict(c.execute("SELECT khoa, gia_tri FROM dk_cai_dat").fetchall())
    finally:
        c.close()


def test_mat_khau_cu_sai_khong_doi_gi(cd):
    api, qt = cd
    truoc = _cai_dat(api)
    r = api.dk_doi_mat_khau(qt, "sai", "moimoi")
    assert ma(r) == "dk_mat_khau_cu_sai"
    assert _cai_dat(api) == truoc
    ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))


def test_mat_khau_moi_ngan_bi_tu_choi(cd):
    api, qt = cd
    assert ma(api.dk_doi_mat_khau(qt, "matkhau", "abc")) == "dk_mat_khau_ngan"
    assert ma(api.dk_doi_mat_khau(qt, "matkhau", None)) == "dk_mat_khau_ngan"
    ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))


def test_doi_thanh_cong_cu_het_hieu_luc_moi_dung_muoi_moi_nhat_ky_sach(cd):
    api, qt = cd
    truoc = _cai_dat(api)
    ok(api.dk_doi_mat_khau(qt, "matkhau", "bimat-moi-9"))
    sau = _cai_dat(api)
    assert sau["mk_muoi"] != truoc["mk_muoi"] and sau["mk_bam"] != truoc["mk_bam"]      # muối mới
    assert ma(api.dk_dang_nhap("quan_tri", "", "matkhau")) == "dk_sai_dang_nhap"
    ok(api.dk_dang_nhap("quan_tri", "", "bimat-moi-9"))
    nk = [x for x in ok(api.dk_nhat_ky(qt)) if x["hanh_dong"] == "doi_mat_khau"]
    assert len(nk) == 1 and nk[0]["vai"] == "quan_tri"
    c = sqlite3.connect(api.db_path)
    moi_thu = " ".join(str(v) for r in c.execute("SELECT * FROM dk_nhat_ky") for v in r) + " ".join(str(v) for v in sau.values())
    c.close()
    assert "bimat-moi-9" not in moi_thu and "matkhau" not in moi_thu


def test_phien_cu_khac_bi_huy_phien_nguoi_goi_con(cd):
    api, qt = cd
    qt2 = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]                  # một phiên quản trị khác (máy khác)
    ok(api.dk_doi_mat_khau(qt, "matkhau", "bimat-moi-9"))
    assert ma(api.dk_phong_danh_sach(qt2)) == "dk_can_dang_nhap"                     # đã bị đăng xuất
    ok(api.dk_phong_danh_sach(qt))                                                   # phiên đổi mật khẩu còn sống


def test_chi_quan_tri_duoc_doi(cd):
    api, qt = cd
    pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]["pin"]
    gv = ok(api.dk_dang_nhap("giao_vien", "Cô An", pin))["token"]
    assert ma(api.dk_doi_mat_khau(gv, "matkhau", "bimat-moi-9")) == "dk_khong_du_quyen"
    assert ma(api.dk_doi_mat_khau("khong-co", "matkhau", "bimat-moi-9")) == "dk_can_dang_nhap"
    ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))


def test_token_giao_vien_hoc_sinh_khong_bi_dong_vao(cd):
    api, qt = cd
    pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]["pin"]
    gv = ok(api.dk_dang_nhap("giao_vien", "Cô An", pin))["token"]
    ok(api.dk_doi_mat_khau(qt, "matkhau", "bimat-moi-9"))
    assert ma(api.dk_nhat_ky(gv)) == "dk_khong_du_quyen"                     # phiên còn (không bị huỷ), chỉ không đủ quyền
