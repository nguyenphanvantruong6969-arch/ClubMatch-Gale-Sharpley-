"""DKL-L4 (API, không trình duyệt): cài đặt, xem trước và phiên bản bản xuất, sao lưu, xoá CLB, phòng trống theo buổi.
Dữ liệu MÔ PHỎNG."""
import os

import pytest

from api import PipelineAPI


def _ok(r):
    assert r["ok"], r
    return r["data"]


def _ma(r):
    assert not r["ok"], r
    return r["errors"][0]["code"]


@pytest.fixture()
def cong(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TRU1", ["T2", "T3"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    return api, qt


def test_cai_dat_doi_ma_truong_buoi_khoi_va_khoa_sau_chuan_bi(cong):
    api, qt = cong
    assert _ma(api.dk_cai_dat_doi(qt, "ab")) == "dk_ma_truong_sai"
    _ok(api.dk_cai_dat_doi(qt, "MATRUONG"))
    assert _ok(api.dk_cai_dat_doc(qt))["ma_truong"] == "MATRUONG"
    _ok(api.dk_cai_dat_doi(qt, None, ["T2", "T3", "T4"], [10, 12]))
    c = _ok(api.dk_cai_dat_doc(qt))
    assert c["buoi"] == ["T2", "T3", "T4"] and c["khoi"] == [10, 12]
    assert _ma(api.dk_cai_dat_doi(qt, None, ["T2", "T2"], None)) == "dk_khoi_sai"
    assert _ma(api.dk_cai_dat_doi(qt, None, None, [12, 10])) == "dk_khoi_sai"
    _ok(api.dk_phong_luu(qt, "P1", 30))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    assert _ma(api.dk_cai_dat_doi(qt, None, None, [11, 12])) == "dk_khoi_sai"   # đang có em khối 10
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    assert _ma(api.dk_cai_dat_doi(qt, None, ["T2"], None)) == "dk_sai_giai_doan"
    _ok(api.dk_cai_dat_doi(qt, "MATRUONG2"))      # mã trường đổi được ở mọi giai đoạn


def test_chi_quan_tri_moi_dung_duoc(cong):
    api, qt = cong
    pin = _ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]["pin"]
    gv = _ok(api.dk_dang_nhap("giao_vien", "Cô An", pin))["token"]
    for goi in (lambda: api.dk_cai_dat_doc(gv), lambda: api.dk_cai_dat_doi(gv, "XXXXXX"), lambda: api.dk_sao_luu(gv),
                lambda: api.dk_xuat_xem_truoc(gv), lambda: api.dk_diem_danh_sach(gv)):
        assert not goi()["ok"]


def test_sao_luu_tao_tep_va_ghi_gio(cong, tmp_path):
    api, qt = cong
    assert _ok(api.dk_cai_dat_doc(qt))["sao_luu_luc"] is None
    r = _ok(api.dk_sao_luu(qt))
    assert r["tep"].startswith("app.db.bak-") and os.path.exists(tmp_path / r["tep"])
    assert _ok(api.dk_cai_dat_doc(qt))["sao_luu_luc"] == r["luc"]


def _den_nhap_diem(api, qt):
    _ok(api.dk_phong_luu(qt, "P1", 40))
    _ok(api.dk_phong_luu(qt, "P2", 30))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1"))
    pin = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))["da_tao"]}
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ph = {p["ten"]: p["phong_id"] for p in _ok(api.dk_phong_danh_sach(qt))}
    ga = _ok(api.dk_dang_nhap("giao_vien", "Cô An", pin["Cô An"]))["token"]
    gb = _ok(api.dk_dang_nhap("giao_vien", "Cô Bê", pin["Cô Bê"]))["token"]
    base = {"khoi_tu": 9, "khoi_den": 12, "mo_ta": "x", "yeu_cau": "Không"}
    ids = {}
    for tk, ten, buoi, loai, phong, extra in ((ga, "Tự do T2", "T2", "Tự do", "P1", {}), (gb, "Robot", "T2", "Tuyển chọn", "P2",
                                              {"chi_tieu": 10, "diem_san": 6, "link_forms": "https://f.example/x"}),
                                             (ga, "Tự do T3", "T3", "Tự do", "P1", {}), (gb, "Cờ T3", "T3", "Giới hạn", "P2", {"chi_tieu": 5})):
        ids[ten] = _ok(api.dk_clb_luu(tk, dict(base, ten=ten, buoi=buoi, loai=loai, phong_id=ph[phong], **extra)))["clb_id"]
    _ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    for cid in ids.values():
        _ok(api.dk_clb_duyet(qt, cid, "duyet"))
    _ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    for ma in ("H1", "H2"):
        tk = _ok(api.dk_dang_nhap("hoc_sinh", ma, _ok(api.dk_hs_dat_lai_pin(qt, ma))["pin"]))["token"]
        _ok(api.dk_hs_luu(tk, [{"clb_id": ids["Tự do T2"], "thi": False, "huy_chuong": None}, {"clb_id": ids["Robot"], "thi": True, "huy_chuong": "Vàng"},
                               {"clb_id": ids["Tự do T3"], "thi": False, "huy_chuong": None}], ["T2"]))
    _ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    return ids


def test_bang_diem_xem_truoc_va_phien_ban_xuat(cong):
    api, qt = cong
    ids = _den_nhap_diem(api, qt)
    ds = _ok(api.dk_diem_danh_sach(qt))
    assert [c["ten"] for c in ds] == ["Robot"] and ds[0]["diem_san"] == 6 and [h["ma"] for h in ds[0]["hoc_sinh"]] == ["H1", "H2"]
    assert all(h["diem"] is None for h in ds[0]["hoc_sinh"])
    _ok(api.dk_diem_dan(qt, ids["Robot"], "H1\t8,5\nH2\t4"))
    xt = _ok(api.dk_xuat_xem_truoc(qt))
    assert xt["so_lan_xuat"] == 0 and xt["tong_hoc_sinh"] == 2 and len(xt["clb"]) == 4 and xt["hoc_sinh"][0][0] == "H1"
    assert "Robot" in xt["hoc_sinh"][0][3] and "8.5" in xt["hoc_sinh"][0][3]
    r1 = _ok(api.dk_xuat_so_nhap(qt))
    r2 = _ok(api.dk_xuat_so_nhap(qt))
    assert (r1["phien_ban"], r2["phien_ban"]) == (1, 2)
    assert _ok(api.dk_xuat_xem_truoc(qt))["so_lan_xuat"] == 2


def test_clb_xoa_va_phong_trong_theo_buoi(cong):
    api, qt = cong
    _ok(api.dk_phong_luu(qt, "P1", 40))
    _ok(api.dk_phong_luu(qt, "P2", 30))
    pin = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))["da_tao"]}
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ga = _ok(api.dk_dang_nhap("giao_vien", "Cô An", pin["Cô An"]))["token"]
    gb = _ok(api.dk_dang_nhap("giao_vien", "Cô Bê", pin["Cô Bê"]))["token"]
    ph = {p["ten"]: p["phong_id"] for p in _ok(api.dk_phong_danh_sach(ga))}
    cid = _ok(api.dk_clb_luu(ga, {"ten": "Tự do", "buoi": "T2", "loai": "Tự do", "phong_id": ph["P1"], "khoi_tu": 9, "khoi_den": 12}))["clb_id"]
    ban = {p["ten"]: p["ban"] for p in _ok(api.dk_phong_danh_sach(gb, "T2"))}
    assert ban == {"P1": True, "P2": False}
    assert {p["ten"]: p["ban"] for p in _ok(api.dk_phong_danh_sach(gb, "T3"))} == {"P1": False, "P2": False}
    assert {p["ten"]: p["ban"] for p in _ok(api.dk_phong_danh_sach(ga, "T2", cid))} == {"P1": False, "P2": False}   # bỏ qua chính CLB đang sửa
    assert _ma(api.dk_clb_xoa(gb, cid)) == "dk_clb_khong_sua_duoc"            # của người khác
    _ok(api.dk_clb_xoa(ga, cid))
    assert _ok(api.dk_clb_danh_sach(ga)) == []
    assert _ma(api.dk_clb_xoa(ga, cid)) == "dk_khong_thay"
    _ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    assert _ma(api.dk_clb_xoa(ga, 999)) in ("dk_sai_giai_doan", "dk_khong_thay")
