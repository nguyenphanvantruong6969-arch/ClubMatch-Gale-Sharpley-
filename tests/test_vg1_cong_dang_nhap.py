"""VG1-L1: cổng đăng nhập chuẩn hoá tên/mã/PIN (D1). Dữ liệu MÔ PHỎNG."""
import test_va_gap_tai_hien as _v
from test_va_gap_tai_hien import ma, ok

cd = _v.cd


def test_khoa_theo_ten_da_chuan_hoa_khong_ne_duoc_bang_cach_viet_khac(cd):
    api, qt = cd
    ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))
    for ten in ("Cô An", "cô  an", "CÔ AN", "Cô An ", "cô an"):
        api.dk_dang_nhap("giao_vien", ten, "0000")
    assert ma(api.dk_dang_nhap("giao_vien", "Cô  An", "0000")) == "dk_tam_khoa"


def test_ten_trung_sau_chuan_hoa_la_trung(cd):
    api, qt = cd
    ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))
    r = ok(api.dk_gv_tao_hang_loat(qt, "cô  AN"))
    assert r["da_tao"] == [] and r["bo_qua"] == ["cô  AN"]
    assert ma(api.dk_gv_tu_dang_ky("TRUONG1", "CÔ AN", "7391")) == "dk_gv_trung"


def test_ma_hs_trung_sau_chuan_hoa_giu_cach_viet_goc(cd):
    api, qt = cd
    ok(api.dk_hs_nap_danh_sach(qt, "H9\tAn\t10A1"))
    r = ok(api.dk_hs_nap_danh_sach(qt, "h9\tAn B\t10A1"))
    assert r["moi"] == 0 and r["da_co"] == 1
    ds = ok(api.dk_hs_danh_sach(qt))
    assert [x["ma"] for x in ds] == ["H9"]
    r = ok(api.dk_hs_nap_danh_sach(qt, "K1\tChi\t10A1\nk1\tChi\t10A1"))
    assert r["loi"][0]["ly_do"] == "trung_ma"


def test_pin_sai_dang_khong_tinh_lan_sai(cd):
    api, qt = cd
    pin = ok(api.dk_hs_nap_danh_sach(qt, "H9\tAn\t10A1"))["pin"][0]["pin"]
    for xau in ("", "12", "12345", "abcd", "١٢٣٤"):
        assert ma(api.dk_dang_nhap("hoc_sinh", "H9", xau)) == "dk_pin_sai_dang"
    assert ok(api.dk_dang_nhap("hoc_sinh", "H9", pin))["token"]
