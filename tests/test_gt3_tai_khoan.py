"""GT3-L1: tài khoản và đăng nhập (hai vai `quan_tri` / `giao_vien`). Dữ liệu MÔ PHỎNG, mật khẩu giả.

Chưa có tài khoản nào thì phần mềm chạy y như trước (không màn đăng nhập, không ghi thêm gì).
"""

import json
import logging
import os
import sqlite3

import pytest

import tai_khoan as tk
from api import PipelineAPI

MK = "matkhau-gia-1"
MK2 = "matkhau-gia-2"


class DongHo:
    """Đồng hồ giả để thử khoá/hết hạn mà không chờ thật."""

    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def chay(self, giay):
        self.t += giay


@pytest.fixture
def dh(api):
    d = DongHo()
    api._dong_ho = d
    return d


def ma_loi(r):
    return [e["code"] for e in r["errors"]]


def tao_quan_tri(api, ten="quantri", mk=MK):
    r = api.tao_tai_khoan(ten, mk, "quan_tri")
    assert r["ok"], r
    return r


def dem_dong(api):
    con = sqlite3.connect(api.db_path)
    try:
        return con.execute("SELECT COUNT(*) FROM tai_khoan").fetchone()[0]
    finally:
        con.close()


# ---------------------------------------------------------------- băm mật khẩu
def test_bam_khong_bang_mat_khau_va_muoi_khac_nhau():
    b1, m1 = tk.bam_mat_khau(MK)
    b2, m2 = tk.bam_mat_khau(MK)
    assert b1 != MK.encode() and MK.encode() not in b1
    assert m1 != m2 and b1 != b2          # cùng mật khẩu, muối khác => băm khác
    assert len(m1) == 16
    assert tk.kiem_tra_mat_khau(MK, b1, m1)
    assert not tk.kiem_tra_mat_khau(MK + "x", b1, m1)
    assert not tk.kiem_tra_mat_khau(MK, b1, m2)


def test_bam_dung_pbkdf2_200k():
    import hashlib

    b, m = tk.bam_mat_khau(MK)
    assert b == hashlib.pbkdf2_hmac("sha256", MK.encode("utf-8"), m, 200_000)


# ------------------------------------------------- chưa có tài khoản: như cũ
def test_chua_co_tai_khoan_khong_man_dang_nhap(api):
    r = api.get_phien_dang_nhap()
    assert r["ok"] and r["data"]["co_tai_khoan"] is False
    assert r["data"]["dang_nhap"] is False
    assert dem_dong(api) == 0


def test_bang_tai_khoan_ton_tai_va_rong_sau_khi_mo(api):
    con = sqlite3.connect(api.db_path)
    try:
        cot = [r[1] for r in con.execute("PRAGMA table_info(tai_khoan)")]
    finally:
        con.close()
    assert cot == ["ten", "vai", "bam", "muoi", "tao_luc"]


def test_mo_lai_csdl_khong_loi_va_khong_them_dong(tmp_path):
    p = str(tmp_path / "app.db")
    PipelineAPI(p)
    a2 = PipelineAPI(p)
    assert dem_dong(a2) == 0


# ------------------------------------------------------------- tạo tài khoản
def test_tai_khoan_dau_phai_la_quan_tri_va_khong_can_dang_nhap(api):
    r = api.tao_tai_khoan("co_giao", MK, "giao_vien")
    assert not r["ok"] and ma_loi(r) == ["gt3_tai_khoan_dau_phai_quan_tri"]
    assert dem_dong(api) == 0
    r = api.tao_tai_khoan("quantri", MK, "quan_tri")
    assert r["ok"] and dem_dong(api) == 1


def test_tai_khoan_dau_tu_dang_nhap_nguoi_tao(api):
    tao_quan_tri(api)
    d = api.get_phien_dang_nhap()["data"]
    assert d["co_tai_khoan"] and d["dang_nhap"] and d["ten"] == "quantri" and d["vai"] == "quan_tri"


def test_tai_khoan_sau_can_phien_quan_tri(api):
    tao_quan_tri(api)
    api.dang_xuat()
    r = api.tao_tai_khoan("gv1", MK, "giao_vien")
    assert not r["ok"] and ma_loi(r) == ["gt3_can_dang_nhap"]
    assert api.dang_nhap("quantri", MK)["ok"]
    assert api.tao_tai_khoan("gv1", MK2, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK2)["ok"]
    r = api.tao_tai_khoan("gv2", MK, "giao_vien")
    assert not r["ok"] and ma_loi(r) == ["gt3_khong_du_quyen"]
    assert dem_dong(api) == 2


@pytest.mark.parametrize("mk", ["", "1234567", "      "])
def test_mat_khau_toi_thieu_8(api, mk):
    r = api.tao_tai_khoan("quantri", mk, "quan_tri")
    assert not r["ok"] and ma_loi(r) == ["gt3_mat_khau_ngan"]
    assert dem_dong(api) == 0


def test_mat_khau_dung_8_ky_tu_duoc(api):
    assert api.tao_tai_khoan("quantri", "12345678", "quan_tri")["ok"]


def test_ten_va_vai_khong_hop_le(api):
    assert ma_loi(api.tao_tai_khoan("", MK, "quan_tri")) == ["gt3_ten_khong_hop_le"]
    assert ma_loi(api.tao_tai_khoan("   ", MK, "quan_tri")) == ["gt3_ten_khong_hop_le"]
    assert ma_loi(api.tao_tai_khoan("a" * 61, MK, "quan_tri")) == ["gt3_ten_khong_hop_le"]
    assert ma_loi(api.tao_tai_khoan("abc", MK, "hieu_truong")) == ["gt3_vai_khong_hop_le"]
    assert ma_loi(api.tao_tai_khoan(None, MK, "quan_tri")) == ["gt3_ten_khong_hop_le"]
    assert dem_dong(api) == 0


def test_ten_co_dau_tieng_viet_duoc_va_trung_ten_bi_chan(api):
    tao_quan_tri(api, "Trường")
    r = api.tao_tai_khoan("TRƯỜNG", MK, "giao_vien")        # trùng, khác hoa/thường
    assert not r["ok"] and ma_loi(r) == ["gt3_ten_da_co"]
    assert api.tao_tai_khoan("Trương", MK, "giao_vien")["ok"]  # khác dấu => khác tên
    api.dang_xuat()
    assert api.dang_nhap("Trường", MK)["ok"]


def test_ten_unicode_nfd_trung_nfc_va_dang_nhap_duoc(api):
    import unicodedata
    nfc = unicodedata.normalize("NFC", "Thầy Tâm")
    nfd = unicodedata.normalize("NFD", nfc)
    assert nfc != nfd
    tao_quan_tri(api, nfc)
    r = api.tao_tai_khoan(nfd, MK2, "giao_vien")
    assert not r["ok"] and ma_loi(r) == ["gt3_ten_da_co"]
    api.dang_xuat()
    assert api.dang_nhap(nfd, MK)["ok"]
    api.dang_xuat()
    assert api.dang_nhap(nfc.upper(), MK)["ok"]


def test_ten_nfd_duoc_luu_dang_nfc(api):
    import unicodedata
    nfd = unicodedata.normalize("NFD", "Trường")
    tao_quan_tri(api, nfd)
    con = sqlite3.connect(api.db_path)
    try:
        (t,) = con.execute("SELECT ten FROM tai_khoan").fetchone()
    finally:
        con.close()
    assert t == unicodedata.normalize("NFC", "Trường")


def test_mat_khau_nfc_nfd_nhu_nhau(api):
    import unicodedata
    mk_nfc = unicodedata.normalize("NFC", "mậtkhẩu-việt1")
    mk_nfd = unicodedata.normalize("NFD", mk_nfc)
    assert mk_nfc != mk_nfd
    tao_quan_tri(api, "quantri", mk_nfc)
    api.dang_xuat()
    assert api.dang_nhap("quantri", mk_nfd)["ok"]
    api.dang_xuat()
    assert not api.dang_nhap("quantri", "sai" + mk_nfc)["ok"]


def test_ten_duoc_cat_khoang_trang(api):
    tao_quan_tri(api, "  quantri  ")
    api.dang_xuat()
    assert api.dang_nhap("quantri", MK)["ok"]


# --------------------------------------------------------------- đăng nhập
def test_dang_nhap_dung_sai(api):
    tao_quan_tri(api)
    api.dang_xuat()
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is False
    r = api.dang_nhap("quantri", "sai-mat-khau")
    assert not r["ok"] and ma_loi(r) == ["gt3_sai_thong_tin"]
    r = api.dang_nhap("khong_co_ai", MK)
    assert not r["ok"] and ma_loi(r) == ["gt3_sai_thong_tin"]     # không lộ tên có tồn tại hay không
    r = api.dang_nhap("quantri", MK)
    assert r["ok"] and r["data"]["vai"] == "quan_tri"
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is True


def test_dang_nhap_khi_chua_co_tai_khoan(api):
    r = api.dang_nhap("a", MK)
    assert not r["ok"] and ma_loi(r) == ["gt3_chua_co_tai_khoan"]


def test_khoa_sau_5_lan_sai(api, dh):
    tao_quan_tri(api)
    api.dang_xuat()
    for _ in range(4):
        assert ma_loi(api.dang_nhap("quantri", "sai-sai-sai")) == ["gt3_sai_thong_tin"]
    r = api.dang_nhap("quantri", "sai-sai-sai")          # lần thứ 5
    assert ma_loi(r) == ["gt3_tam_khoa"]
    assert 0 < r["errors"][0]["params"]["giay"] <= 60
    # Đang khoá: mật khẩu ĐÚNG cũng bị từ chối.
    dh.chay(30)
    r = api.dang_nhap("quantri", MK)
    assert ma_loi(r) == ["gt3_tam_khoa"]
    assert r["errors"][0]["params"]["giay"] <= 30
    # Hết 60 giây: vào được, và bộ đếm về 0.
    dh.chay(31)
    assert api.dang_nhap("quantri", MK)["ok"]
    api.dang_xuat()
    for _ in range(4):
        api.dang_nhap("quantri", "sai-sai-sai")
    assert ma_loi(api.dang_nhap("quantri", MK)) == []    # lần 5 đúng => vào, không bị khoá


def test_khoa_theo_tung_ten_khong_chan_nguoi_khac(api, dh):
    tao_quan_tri(api)
    assert api.tao_tai_khoan("gv1", MK2, "giao_vien")["ok"]
    api.dang_xuat()
    for _ in range(5):
        api.dang_nhap("gv1", "sai-sai-sai")
    assert ma_loi(api.dang_nhap("gv1", MK2)) == ["gt3_tam_khoa"]
    assert api.dang_nhap("quantri", MK)["ok"]


def test_het_phien_sau_15_phut_khong_hoat_dong(api, dh):
    tao_quan_tri(api)
    dh.chay(14 * 60)
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is True
    assert api._hoat_dong() is True               # thao tác thật => tính lại 15 phút
    dh.chay(14 * 60)
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is True
    dh.chay(16 * 60)
    d = api.get_phien_dang_nhap()["data"]
    assert d["dang_nhap"] is False and d["co_tai_khoan"] is True
    assert api._hoat_dong() is False


def test_hoi_phien_khong_keo_dai_phien(api, dh):
    """Giao diện hỏi phiên định kỳ — việc hỏi KHÔNG được coi là hoạt động."""
    tao_quan_tri(api)
    for _ in range(20):
        dh.chay(60)
        api.get_phien_dang_nhap()
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is False


def test_chua_co_tai_khoan_thi_hoat_dong_luon_hop_le(api):
    assert api._hoat_dong() is True


def test_phien_roi_di_khi_doi_workspace(api, tmp_path):
    tao_quan_tri(api)
    khac = PipelineAPI(str(tmp_path / "khac.db"))            # workspace khác, cũng đã có tài khoản
    khac.tao_tai_khoan("quantri", MK, "quan_tri")
    khac.dang_xuat()
    api.db_path = khac.db_path                                # mô phỏng đổi workspace trên cùng tiến trình
    d = api.get_phien_dang_nhap()["data"]
    assert d["co_tai_khoan"] is True and d["dang_nhap"] is False
    assert api._hoat_dong() is False


# ----------------------------------------------------------------- đổi mật khẩu
def test_doi_mat_khau(api):
    tao_quan_tri(api)
    r = api.doi_mat_khau("sai-mat-khau", MK2)
    assert not r["ok"] and ma_loi(r) == ["gt3_sai_thong_tin"]
    r = api.doi_mat_khau(MK, "ngan")
    assert not r["ok"] and ma_loi(r) == ["gt3_mat_khau_ngan"]
    assert api.doi_mat_khau(MK, MK2)["ok"]
    api.dang_xuat()
    assert not api.dang_nhap("quantri", MK)["ok"]
    assert api.dang_nhap("quantri", MK2)["ok"]


def test_doi_mat_khau_can_dang_nhap(api):
    tao_quan_tri(api)
    api.dang_xuat()
    assert ma_loi(api.doi_mat_khau(MK, MK2)) == ["gt3_can_dang_nhap"]


def test_doi_mat_khau_sai_nhieu_lan_cung_bi_khoa(api, dh):
    tao_quan_tri(api)
    for _ in range(4):
        api.doi_mat_khau("sai-sai-sai", MK2)
    assert ma_loi(api.doi_mat_khau("sai-sai-sai", MK2)) == ["gt3_tam_khoa"]
    assert ma_loi(api.doi_mat_khau(MK, MK2)) == ["gt3_tam_khoa"]


def test_giao_vien_tu_doi_mat_khau_duoc(api):
    tao_quan_tri(api)
    api.tao_tai_khoan("gv1", MK2, "giao_vien")
    api.dang_xuat()
    api.dang_nhap("gv1", MK2)
    assert api.doi_mat_khau(MK2, "mat-khau-moi-9")["ok"]


# --------------------------------------------------------------------- xoá
def test_khong_xoa_quan_tri_cuoi(api):
    tao_quan_tri(api)
    r = api.xoa_tai_khoan("quantri")
    assert not r["ok"] and ma_loi(r) == ["gt3_khong_xoa_quan_tri_cuoi"]
    assert dem_dong(api) == 1


def test_xoa_duoc_khi_con_quan_tri_khac_va_tu_xoa_thi_dang_xuat(api):
    tao_quan_tri(api)
    api.tao_tai_khoan("qt2", MK2, "quan_tri")
    assert api.xoa_tai_khoan("quantri")["ok"]          # tự xoá mình
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is False
    assert dem_dong(api) == 1
    assert api.dang_nhap("qt2", MK2)["ok"]


def test_xoa_can_quan_tri_va_ten_phai_co(api):
    tao_quan_tri(api)
    api.tao_tai_khoan("gv1", MK2, "giao_vien")
    assert ma_loi(api.xoa_tai_khoan("khong_co")) == ["gt3_khong_thay_tai_khoan"]
    api.dang_xuat()
    assert ma_loi(api.xoa_tai_khoan("gv1")) == ["gt3_can_dang_nhap"]
    api.dang_nhap("gv1", MK2)
    assert ma_loi(api.xoa_tai_khoan("gv1")) == ["gt3_khong_du_quyen"]
    assert dem_dong(api) == 2


def test_xoa_giao_vien_bang_quan_tri(api):
    tao_quan_tri(api)
    api.tao_tai_khoan("gv1", MK2, "giao_vien")
    assert api.xoa_tai_khoan("gv1")["ok"]
    assert dem_dong(api) == 1


def test_liet_ke_khong_lo_bam_hay_muoi(api):
    tao_quan_tri(api)
    api.tao_tai_khoan("gv1", MK2, "giao_vien")
    r = api.liet_ke_tai_khoan()
    assert r["ok"]
    assert [x["ten"] for x in r["data"]] == ["gv1", "quantri"] or [x["ten"] for x in r["data"]] == ["quantri", "gv1"]
    for x in r["data"]:
        assert set(x) == {"ten", "vai", "tao_luc"}
    api.dang_xuat()
    assert ma_loi(api.liet_ke_tai_khoan()) == ["gt3_can_dang_nhap"]
    api.dang_nhap("gv1", MK2)
    assert ma_loi(api.liet_ke_tai_khoan()) == ["gt3_khong_du_quyen"]


# ------------------------------------------------- mật khẩu không lọt ra ngoài
def test_mat_khau_khong_nam_trong_bat_ky_phan_hoi_nao(api, caplog):
    caplog.set_level(logging.DEBUG)
    ra = []
    ra.append(api.tao_tai_khoan("quantri", MK, "quan_tri"))
    ra.append(api.tao_tai_khoan("gv1", MK2, "giao_vien"))
    ra.append(api.get_phien_dang_nhap())
    ra.append(api.dang_xuat())
    ra.append(api.dang_nhap("quantri", "sai-mat-khau-xyz"))
    ra.append(api.dang_nhap("quantri", MK))
    ra.append(api.doi_mat_khau(MK, "mat-khau-moi-9"))
    ra.append(api.doi_mat_khau("sai-mat-khau-xyz", "khac-nua-123"))
    ra.append(api.tao_tai_khoan("ngan", "123", "giao_vien"))
    ra.append(api.liet_ke_tai_khoan())
    ra.append(api.xoa_tai_khoan("gv1"))
    van_ban = json.dumps(ra, ensure_ascii=False, default=str)
    van_ban += caplog.text
    for bi_mat in (MK, MK2, "sai-mat-khau-xyz", "mat-khau-moi-9", "khac-nua-123"):
        assert bi_mat not in van_ban
    # Không có khoá nào tên bam/muoi/mat_khau trong dữ liệu trả ra.
    assert '"bam"' not in van_ban and '"muoi"' not in van_ban and '"mat_khau"' not in van_ban


def test_mat_khau_khong_nam_ro_trong_tep_csdl(api):
    tao_quan_tri(api, mk="mat-khau-rat-rieng-77")
    with open(api.db_path, "rb") as f:
        assert b"mat-khau-rat-rieng-77" not in f.read()


def test_gia_tri_vai_trong_csdl_bi_rang_buoc(api):
    con = sqlite3.connect(api.db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            con.execute("INSERT INTO tai_khoan VALUES ('x','sieu_nhan',x'00',x'00','t')")
    finally:
        con.close()


def test_mat_khau_khong_phai_chuoi_bi_tu_choi_khong_ném_loi(api):
    r = api.tao_tai_khoan("quantri", None, "quan_tri")
    assert not r["ok"] and ma_loi(r) == ["gt3_mat_khau_ngan"]
    tao_quan_tri(api)
    api.dang_xuat()
    r = api.dang_nhap("quantri", None)
    assert not r["ok"] and ma_loi(r) == ["gt3_sai_thong_tin"]


# ---------------------------------------------------------- ngoại lệ → mã lỗi
def test_moi_ma_gt3_co_du_vi_va_en():
    import i18n_errors as ie

    ma = [k for k in ie.MESSAGES if k.startswith("gt3_")]
    assert len(ma) >= 10
    for k in ma:
        assert ie.MESSAGES[k]["vi"].strip() and ie.MESSAGES[k]["en"].strip()


def test_phien_la_trong_bo_nho_khong_qua_tien_trinh_khac(api, tmp_path):
    tao_quan_tri(api)
    api2 = PipelineAPI(api.db_path)
    d = api2.get_phien_dang_nhap()["data"]
    assert d["co_tai_khoan"] is True and d["dang_nhap"] is False


# ------------------------------------------------------------ khôi phục (recovery)
def test_recovery_xoa_tai_khoan_sau_khi_sao_luu(api, tmp_path):
    from recovery import RecoveryAPI, xoa_tai_khoan_sau_sao_luu

    tao_quan_tri(api)
    api.tao_tai_khoan("gv1", MK2, "giao_vien")
    n = xoa_tai_khoan_sau_sao_luu(api.db_path)
    assert n == 2
    assert dem_dong(api) == 0
    baks = [f for f in os.listdir(tmp_path) if f.startswith("app.db.bak-")]
    assert len(baks) == 1                                   # đã sao lưu TRƯỚC khi xoá
    con = sqlite3.connect(str(tmp_path / baks[0]))
    try:
        assert con.execute("SELECT COUNT(*) FROM tai_khoan").fetchone()[0] == 2
    finally:
        con.close()
    # Sau khi xoá: phần mềm lại chạy không cần đăng nhập, và tạo được quản trị mới.
    api3 = PipelineAPI(api.db_path)
    assert api3.get_phien_dang_nhap()["data"]["co_tai_khoan"] is False
    assert api3.tao_tai_khoan("moi", MK, "quan_tri")["ok"]
    # Cũng gọi được qua RecoveryAPI theo hợp đồng {ok, data, errors}.
    r = RecoveryAPI(api.db_path, "").xoa_tai_khoan_sau_sao_luu()
    assert r["ok"] and r["data"]["so_tai_khoan_da_xoa"] == 1


def test_recovery_khong_co_csdl_bao_loi(tmp_path):
    from recovery import RecoveryAPI

    r = RecoveryAPI(str(tmp_path / "khong_co.db"), "").xoa_tai_khoan_sau_sao_luu()
    assert not r["ok"] and r["errors"][0]["code"] == "gt3_khong_xoa_duoc_tai_khoan"
    assert not os.path.exists(tmp_path / "khong_co.db")      # không tự tạo CSDL rỗng


def test_recovery_csdl_chua_co_bang_thi_khong_loi(tmp_path):
    from recovery import xoa_tai_khoan_sau_sao_luu

    p = str(tmp_path / "cu.db")
    sqlite3.connect(p).close()
    assert xoa_tai_khoan_sau_sao_luu(p) == 0


def test_recovery_cho_lenh_dong_dong_goi():
    import subprocess
    import sys

    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kq = subprocess.run([sys.executable, os.path.join(goc, "recovery.py"), "--help"],
                        capture_output=True, text=True, timeout=60)
    assert kq.returncode == 0 and "--xoa-tai-khoan" in kq.stdout
