"""Sửa lỗi (Truong, 2026-11-28): cổng đăng ký tải tệp bằng `blob:` của trình duyệt, mà cửa sổ pywebview của bản .exe chặn
tải tệp -> «Xuất phiếu PIN» đặt lại PIN của mọi người nhưng không ai nhận được tệp. Nay Python ghi tệp vào thư mục Tải xuống
(cùng luật `_duong_xuat` với mọi nút xuất khác) và phiếu PIN được ghi TRONG giao dịch đặt lại PIN: ghi hỏng thì PIN không đổi.
"""
import os

import openpyxl
import pytest


def ok(r):
    assert r["ok"], r
    return r["data"]


def ma(r):
    assert not r["ok"], r
    return r["errors"][0]["code"]


@pytest.fixture
def cd(api):
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A2"))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))
    return api, qt


def _tai_ve():
    return os.environ["RBDA_THU_MUC_TAI_VE"]


def test_phieu_pin_duoc_ghi_vao_tai_xuong_va_pin_trong_tep_dang_nhap_duoc(cd):
    api, qt = cd
    d = ok(api.dk_pin_xuat_excel(qt, "tat_ca", xac_nhan=True))
    assert os.path.dirname(d["path"]) == _tai_ve() and d["dir"] == _tai_ve()
    assert os.path.basename(d["path"]) == "PHIEU_PIN.xlsx"
    wb = openpyxl.load_workbook(d["path"])
    for m_, ten, _lop, pin in wb["Học sinh"].iter_rows(min_row=2, values_only=True):
        assert ok(api.dk_dang_nhap("hoc_sinh", m_, pin))["ten"] == ten
    ten, pin = next(wb["Giáo viên"].iter_rows(min_row=2, values_only=True))
    assert ok(api.dk_dang_nhap("giao_vien", ten, pin))["ten"] == "Cô An"


def test_xuat_hai_lan_khong_ghi_de_tep_cu(cd):
    api, qt = cd
    p1 = ok(api.dk_pin_xuat_excel(qt, "hs", xac_nhan=True))["path"]
    p2 = ok(api.dk_pin_xuat_excel(qt, "hs", xac_nhan=True))["path"]
    assert p1 != p2 and os.path.exists(p1) and os.path.exists(p2)


def test_ghi_tep_hong_thi_pin_khong_doi_va_bao_loi(cd, monkeypatch):
    api, qt = cd
    pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]

    def hong(*a, **k):
        raise OSError("đĩa đầy")
    monkeypatch.setattr(api, "_dk_ghi_tep_xuat_dia", hong)
    assert ma(api.dk_pin_xuat_excel(qt, "tat_ca", xac_nhan=True)) == "dk_xuat_tep_hong"
    assert ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]          # PIN cũ còn nguyên
    assert os.listdir(_tai_ve()) == []


def test_chua_xac_nhan_thi_khong_ghi_tep(cd):
    api, qt = cd
    assert ma(api.dk_pin_xuat_excel(qt, "tat_ca")) == "dk_can_xac_nhan_pin"
    assert os.listdir(_tai_ve()) == []


def test_tep_mau_duoc_ghi_vao_tai_xuong(cd):
    api, qt = cd
    d = ok(api.dk_excel_mau(qt))
    assert os.path.basename(d["path"]) == "MAU_DANG_KY.xlsx" and d["dir"] == _tai_ve()
    assert openpyxl.load_workbook(d["path"]).sheetnames == ["Học sinh", "Giáo viên", "Phòng", "Hướng dẫn"]


def test_ma_loi_moi_co_vi_va_en():
    from i18n_errors import MESSAGES
    assert MESSAGES["dk_xuat_tep_hong"]["vi"] and MESSAGES["dk_xuat_tep_hong"]["en"]


def test_giao_dien_cong_khong_con_tai_bang_blob():
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(goc, "js", "dang_ky_quan_tri_2.js"), encoding="utf-8") as f:
        js = f.read()
    assert "createObjectURL" not in js and "download:" not in js
