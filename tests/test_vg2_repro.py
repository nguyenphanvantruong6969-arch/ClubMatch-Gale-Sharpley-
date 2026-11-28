"""VG2 — tái hiện (tệp này là bản chính; bản cũ tests/test_vg2_tai_hien.py bị gộp xoá khi VG2 nhập nhánh VG1) các lỗi tìm thấy khi đóng vai quản trị / giáo viên / học sinh (Truong, 2026-11-27; docs/phien/VG1_KIEM_TRA_TOAN_DIEN.md).
Mỗi test khẳng định hành vi ĐÚNG; hiện tại ĐỎ = lỗi còn đó. Chưa sửa mã. Dữ liệu MÔ PHỎNG."""
import datetime

import pytest

import api_dang_ky


def ok(r):
    assert r["ok"], r
    return r["data"]


def ma(r):
    assert not r["ok"], r
    return r["errors"][0]["code"]


def _clb(**kw):
    d = {"ten": "Cờ vua", "buoi": "T2", "loai": "Giới hạn", "phong_id": 1, "chi_tieu": 10, "khoi_tu": 10, "khoi_den": 12}
    d.update(kw)
    return d


@pytest.fixture
def cd(api):
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, t, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    return api, qt


def _mo_hs(api, qt):
    """GV tạo 1 CLB Tự do + 1 Giới hạn + 1 Tuyển chọn (T2), duyệt, nạp H1, mở cho học sinh. Trả (ids, token H1)."""
    pin = {x["ten"]: x["pin"] for x in ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình\nCô Chi"))["da_tao"]}
    t = {k: ok(api.dk_dang_nhap("giao_vien", k, v))["token"] for k, v in pin.items()}
    ids = {}
    for gv, ten, loai, ph, kw in (("Cô An", "Tự do", "Tự do", 1, {}), ("Thầy Bình", "Cờ vua", "Giới hạn", 2, {}),
                                  ("Cô Chi", "Robot", "Tuyển chọn", 3, {"diem_san": 6})):
        ids[ten] = ok(api.dk_clb_luu(t[gv], _clb(ten=ten, loai=loai, phong_id=ph, **kw)))["clb_id"]
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    for i in ids.values():
        ok(api.dk_clb_duyet(qt, i, "duyet"))
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    h1 = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    return ids, h1


# ---- 1. Khoá quản trị bởi người lạ -----------------------------------------------------------------
def test_khoa_quan_tri_ngan_va_tang_dan_khong_bi_khoa_lau(cd, monkeypatch):
    """Người lạ gõ sai 5 lần: hiện khoá 5 phút (kể cả quản trị thật). Cần: lần khoá ĐẦU của tài khoản quản trị chỉ 1 phút, lần khoá
    liên tiếp kế tiếp gấp đôi (tối đa 5), đăng nhập đúng thì xoá bộ đếm; vẫn từ chối mật khẩu đúng TRONG thời gian khoá."""
    api, _ = cd
    bay_gio = [datetime.datetime(2026, 11, 27, 9, 0, 0)]
    monkeypatch.setattr(api, "_dk_bay_gio", lambda: bay_gio[0])
    for _ in range(5):
        api.dk_dang_nhap("quan_tri", "", "sai")
    r = api.dk_dang_nhap("quan_tri", "", "matkhau")
    assert ma(r) == "dk_tam_khoa" and r["errors"][0]["params"]["phut"] == 1
    bay_gio[0] += datetime.timedelta(seconds=61)
    assert ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["vai"] == "quan_tri"


# ---- 2. Trùng tên chỉ khác hoa/thường -----------------------------------------------------------------
def test_phong_va_clb_trung_ten_khac_hoa_thuong_bi_chan(cd):
    api, qt = cd
    assert ma(api.dk_phong_luu(qt, "p1", 10)) == "dk_phong_trung"
    pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình"))["da_tao"]
    t = {x["ten"]: ok(api.dk_dang_nhap("giao_vien", x["ten"], x["pin"]))["token"] for x in pin}
    ok(api.dk_clb_luu(t["Cô An"], _clb(ten="Cờ vua")))
    assert ma(api.dk_clb_luu(t["Thầy Bình"], _clb(ten="CỜ VUA", phong_id=2))) == "dk_clb_ten_trung"


# ---- 3. PIN dễ đoán --------------------------------------------------------------------------------
@pytest.mark.parametrize("pin", ["0000", "1111", "1234", "4321", "9999", "2580"])
def test_pin_de_doan_khong_duoc_tu_dat(cd, pin):
    api, _ = cd
    assert ma(api.dk_gv_tu_dang_ky("TRUONG1", "Cô Dễ", pin)) == "dk_pin_de_doan"


def test_pin_tu_sinh_khong_bao_gio_de_doan():
    de = {"0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999", "1234", "2345", "3456", "4567", "5678",
          "6789", "4321", "3210", "9876", "8765", "7654", "6543", "5432", "2580", "0123"}
    assert not any(api_dang_ky._pin_moi() in de for _ in range(20000))


# ---- 4. Xoá giáo viên + giới hạn tự đăng ký --------------------------------------------------------
def test_xoa_giao_vien_va_huy_phien(cd):
    api, qt = cd
    pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Rác"))["da_tao"]
    gv = {x["ten"]: x for x in ok(api.dk_gv_danh_sach(qt))}
    t_rac = ok(api.dk_dang_nhap("giao_vien", "Cô Rác", [x["pin"] for x in pin if x["ten"] == "Cô Rác"][0]))["token"]
    ok(api.dk_gv_xoa(qt, gv["Cô Rác"]["gv_id"]))                                   # chưa có hàm -> AttributeError (đỏ)
    assert not api.dk_clb_danh_sach(t_rac)["ok"]                                    # phiên cũ chết
    assert ma(api.dk_dang_nhap("giao_vien", "Cô Rác", "0000")) == "dk_sai_dang_nhap"
    t_an = ok(api.dk_dang_nhap("giao_vien", "Cô An", [x["pin"] for x in pin if x["ten"] == "Cô An"][0]))["token"]
    ok(api.dk_clb_luu(t_an, _clb()))
    assert ma(api.dk_gv_xoa(qt, gv["Cô An"]["gv_id"])) == "dk_gv_con_clb"           # còn CLB chưa bị từ chối -> chặn


def test_gv_tu_dang_ky_co_tran(cd, monkeypatch):
    api, _ = cd
    monkeypatch.setattr(api_dang_ky, "TOI_DA_GV", 3, raising=False)
    for i in range(3):
        ok(api.dk_gv_tu_dang_ky("TRUONG1", "Cô %d" % i, "7391"))
    assert ma(api.dk_gv_tu_dang_ky("TRUONG1", "Cô 4", "7391")) == "dk_gv_qua_nhieu"


# ---- 5. Toàn vẹn dữ liệu ------------------------------------------------------------------------------
def test_xoa_phong_chi_con_clb_bi_tu_choi_van_bi_chan(cd):
    api, qt = cd
    pin = {x["ten"]: x["pin"] for x in ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))["da_tao"]}
    t = {k: ok(api.dk_dang_nhap("giao_vien", k, v))["token"] for k, v in pin.items()}
    cid = ok(api.dk_clb_luu(t["Cô An"], _clb(phong_id=3, chi_tieu=5)))["clb_id"]
    ok(api.dk_clb_luu(t["Cô Bê"], _clb(ten="Tự do", loai="Tự do", phong_id=1)))      # VG1-L4: buổi cần ≥ 1 CLB Tự do
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    ok(api.dk_clb_duyet(qt, cid, "tu_choi", ly_do="x"))
    assert ma(api.dk_phong_xoa(qt, 3)) == "dk_phong_dang_dung"                     # tránh phong_id lơ lửng


def test_hs_da_bi_xoa_khoi_danh_sach_khong_con_luu_duoc(cd):
    api, qt = cd
    ids, h1 = _mo_hs(api, qt)
    ok(api.dk_chuyen_giai_doan(qt, "chuan_bi", xac_nhan=True))                      # lùi (VG1-L3)
    ok(api.dk_hs_nap_danh_sach(qt, "H9\tMới\t10A1", "thay"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))                                   # mở lại (CLB vẫn duyệt)
    assert ma(api.dk_hs_luu(h1, [{"clb_id": ids["Tự do"]}])) in ("dk_can_dang_nhap", "dk_khong_thay")


def test_khoi_tao_ma_truong_ngan_bi_tu_choi(api):
    assert ma(api.dk_khoi_tao("matkhau", "ab")) == "dk_ma_truong_sai"


def test_nguyen_vong_sai_dang_co_ma_loi_rieng(cd):
    api, qt = cd
    _, h1 = _mo_hs(api, qt)
    for v in ("abc", 5, {"a": 1}):
        assert ma(api.dk_hs_luu(h1, v)) == "dk_nv_sai_dang"


def test_bo_tick_thi_clb_da_co_diem_phai_canh_bao(cd):
    api, qt = cd
    ids, h1 = _mo_hs(api, qt)
    ok(api.dk_hs_luu(h1, [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Tự do"]}]))
    ok(api.dk_diem_dat(qt, "H1", ids["Robot"], 8))
    r = ok(api.dk_hs_luu(h1, [{"clb_id": ids["Robot"]}, {"clb_id": ids["Tự do"]}]))
    assert "dk_mat_diem" in [c["code"] for c in r["canh_bao"]]
