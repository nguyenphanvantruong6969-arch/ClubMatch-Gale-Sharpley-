"""GT4-L1 — nhật ký thao tác không giữ mã tra cứu (R1, D4-2, D4-3). Dữ liệu MÔ PHỎNG, mật khẩu giả."""

import pytest

from _fa import dung_fa_clb
from _wharton import tat_wharton

MK = "matkhau-gia-1"
HS = {"s1": "Nguyễn Văn Ánh", "s2": "Trần Thị Bé"}


@pytest.fixture
def co_tk(api):
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
    for sid, ten in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    with api._ket_noi_doc() as cur:
        ma = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    return api, ma


def _dong(api, hanh_dong):
    with api._ket_noi_doc() as cur:
        return [dict(zip(("nguoi", "vai", "ket_qua", "chi_tiet"), r)) for r in cur.execute(
            "SELECT nguoi, vai, ket_qua, chi_tiet FROM nhat_ky_thao_tac WHERE hanh_dong = ? ORDER BY id",
            (hanh_dong,))]


def test_tra_cuu_khong_de_lai_ma_va_khong_ghi_ten_quan_tri(co_tk, tmp_path):
    api, ma = co_tk
    assert api.dang_xuat()["ok"] and api.dang_nhap("quantri", MK)["ok"]
    assert api.vao_che_do_hoc_sinh()["data"]["khoa"] is True
    sai1, sai2 = "SAIMA001", "SAIMA002"
    assert not api.tra_cuu_hoc_sinh("s1", sai1)["ok"]
    assert not api.tra_cuu_hoc_sinh("s1", sai2)["ok"]
    assert api.tra_cuu_hoc_sinh("s1", ma["s1"])["ok"]
    dong = _dong(api, "tra_cuu_hoc_sinh")
    assert len(dong) == 3
    assert all(d["nguoi"] is None and d["vai"] is None for d in dong)       # D4-3: không nói quản trị tra cứu
    assert all(d["chi_tiet"] == '{"student_id": "s1"}' for d in dong)
    assert api.thoat_che_do_hoc_sinh("quantri", MK)["ok"]
    # quét MỌI dòng của MỌI cột và tệp CSV xuất
    with api._ket_noi_doc() as cur:
        toan = str(cur.execute("SELECT * FROM nhat_ky_thao_tac").fetchall())
    csv = api.export_nhat_ky_thao_tac_csv(str(tmp_path / "nk.csv"))
    assert csv["ok"], csv
    noi_dung = (tmp_path / "nk.csv").read_text(encoding="utf-8-sig")
    for bi_mat in (sai1, sai2, *ma.values(), MK):
        assert bi_mat not in toan and bi_mat not in noi_dung, bi_mat


def test_tham_so_ten_ma_bi_an_o_moi_ham():
    import nhat_ky as nk

    def ham(self, student_id, ma, khac=1):
        return None

    ra = nk.tom_tat_tham_so(ham, "ham_bat_ky", ("s1", "BIMAT"), {})
    assert "BIMAT" not in ra and "s1" in ra


def test_xem_giai_trinh_mot_hoc_sinh_ghi_dung_mot_dong(co_tk):
    api, _ = co_tk
    assert api.dang_xuat()["ok"] and api.dang_nhap("gv1", MK)["ok"]
    r = api.get_giai_trinh_hoc_sinh("s2")
    assert r["ok"], r
    (d,) = _dong(api, "get_giai_trinh_hoc_sinh")                         # D4-2
    assert d["nguoi"] == "gv1" and d["vai"] == "giao_vien" and d["ket_qua"] == "ok"
    assert d["chi_tiet"] == '{"student_id": "s2"}'
    assert "Trần" not in d["chi_tiet"]


def test_ma_hoc_sinh_la_ma_tra_cuu_gan_nham_o_thi_khong_ghi(co_tk):
    api, ma = co_tk
    api.vao_che_do_hoc_sinh()
    assert not api.tra_cuu_hoc_sinh(ma["s1"], ma["s2"])["ok"]            # dán mã tra cứu vào ô mã học sinh
    (d,) = _dong(api, "tra_cuu_hoc_sinh")
    assert d["chi_tiet"] == "{}" and d["nguoi"] is None
