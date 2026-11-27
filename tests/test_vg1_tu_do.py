"""VG1-L4: ràng buộc CLB Tự do chặn SỚM + công tắc `bat_buoc_tu_do` (D4 a–e). Dữ liệu MÔ PHỎNG."""
import test_va_gap_tai_hien as _v
from test_va_gap_tai_hien import _clb, _sql, ma, ok

cd = _v.cd


def _gv(api, qt):
    pin = {x["ten"]: x["pin"] for x in ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình"))["da_tao"]}
    return {k: ok(api.dk_dang_nhap("giao_vien", k, v))["token"] for k, v in pin.items()}


def test_b_khong_go_clb_tu_do_cuoi_cua_buoi_con_clb_khac(cd):
    api, qt = cd
    t = _gv(api, qt)
    td = ok(api.dk_clb_luu(t["Cô An"], _clb(ten="Tự do", loai="Tự do", phong_id=1)))["clb_id"]
    gh = ok(api.dk_clb_luu(t["Thầy Bình"], _clb(ten="Cờ vua", phong_id=2, chi_tieu=10)))["clb_id"]
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    assert ma(api.dk_clb_duyet(qt, td, "tu_choi", ly_do="x")) == "dk_thieu_clb_tu_do"
    assert ma(api.dk_clb_xoa(qt, td)) == "dk_thieu_clb_tu_do"
    ok(api.dk_clb_duyet(qt, td, "duyet"))
    ok(api.dk_clb_duyet(qt, gh, "duyet"))
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    assert ma(api.dk_clb_sua_sau_mo(qt, td, xoa=True, xac_nhan=True)) == "dk_thieu_clb_tu_do"
    assert ma(api.dk_clb_sua_sau_mo(qt, td, buoi="T3", xac_nhan=True)) == "dk_thieu_clb_tu_do"
    ok(api.dk_clb_sua_sau_mo(qt, gh, xoa=True, xac_nhan=True))              # bỏ CLB khác thì được
    ok(api.dk_clb_sua_sau_mo(qt, td, xoa=True, xac_nhan=True))              # buổi hết CLB sống: bỏ nốt Tự do cũng được


def test_d_het_han_tu_dong_sang_duyet_roi_khong_duyet_clb_khac_khi_buoi_thieu_tu_do(cd):
    api, qt = cd
    t = _gv(api, qt)
    gh = ok(api.dk_clb_luu(t["Thầy Bình"], _clb(ten="Cờ vua", phong_id=2, chi_tieu=10)))["clb_id"]
    ok(api.dk_dat_han(qt, "gv_dang_ky", "2020-01-01T08:00"))
    assert api.dk_trang_thai()["data"]["giai_doan"] == "duyet"              # hạn chót không chặn được
    d = ok(api.dk_cai_dat_doc(qt))
    assert d["buoi_thieu_tu_do"] == ["T2"] and d["bat_buoc_tu_do"] is True
    assert ma(api.dk_clb_duyet(qt, gh, "duyet")) == "dk_thieu_clb_tu_do"
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))                           # lối thoát: lùi để giáo viên thêm CLB Tự do
    ok(api.dk_clb_luu(t["Cô An"], _clb(ten="Tự do", loai="Tự do", phong_id=1)))
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    assert ok(api.dk_cai_dat_doc(qt))["buoi_thieu_tu_do"] == []


def test_e_tat_can_xac_nhan_nhat_ky_va_bat_lai_kiem_lai(cd):
    api, qt = cd
    t = _gv(api, qt)
    ok(api.dk_clb_luu(t["Thầy Bình"], _clb(ten="Cờ vua", phong_id=2, chi_tieu=10)))
    assert ok(api.dk_cai_dat_doc(qt))["bat_buoc_tu_do"] is True
    assert ma(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=False)) == "dk_can_xac_nhan_rui_ro"
    assert ma(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=False, xac_nhan_rui_ro="yes")) == "dk_can_xac_nhan_rui_ro"
    assert ok(api.dk_cai_dat_doc(qt))["bat_buoc_tu_do"] is True             # chưa đổi
    ok(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=False, xac_nhan_rui_ro=True))
    d = ok(api.dk_cai_dat_doc(qt))
    assert d["bat_buoc_tu_do"] is False and d["buoi_thieu_tu_do"] == []
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))                                # khi tắt: không chặn
    assert ma(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=True)) == "dk_thieu_clb_tu_do"   # bật lại chạy lại kiểm
    assert [r[0] for r in _sql(api, "SELECT chi_tiet FROM dk_nhat_ky WHERE hanh_dong = 'bat_buoc_tu_do'")] == ["tat; xac_nhan_rui_ro"]
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ok(api.dk_clb_luu(t["Cô An"], _clb(ten="Tự do", loai="Tự do", phong_id=1)))
    ok(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=True))


def test_tat_chi_doi_duoc_toi_giai_doan_duyet_va_chi_quan_tri(cd):
    api, qt = cd
    t = _gv(api, qt)
    assert not api.dk_cai_dat_doi(t["Cô An"], bat_buoc_tu_do=False, xac_nhan_rui_ro=True)["ok"]
    assert not api.dk_cai_dat_doc(t["Cô An"])["ok"]
    assert ma(api.dk_cai_dat_doi(qt, bat_buoc_tu_do="no")) != ""
