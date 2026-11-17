"""Tích hợp GT1+GT2+GT3 (I2: chế độ học sinh khoá ở backend khi có tài khoản). Dữ liệu MÔ PHỎNG."""

import pytest

import phan_quyen as pq
from _fa import dung_fa_clb
from _wharton import tat_wharton

MK = "matkhau-gia-1"
HS = {"s1": "Nguyễn Văn Ánh", "s2": "Trần Thị Bé"}


def _dung(api):
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
    for sid, ten in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    with api._ket_noi_doc() as cur:
        return dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))


def _ma_loi(r):
    return [e["code"] for e in (r.get("errors") or [])]


@pytest.fixture
def co_tk(api):
    ma = _dung(api)
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    return api, ma


def test_chua_co_tai_khoan_che_do_hoc_sinh_khong_khoa_gi(api):
    ma = _dung(api)
    r = api.vao_che_do_hoc_sinh()
    assert r["ok"] and r["data"]["khoa"] is False
    assert api.get_run_history()["ok"]                       # vẫn như GT1 DONE
    assert api.tra_cuu_hoc_sinh("s1", ma["s1"])["ok"]
    assert api.thoat_che_do_hoc_sinh("", "")["ok"]


def test_o_che_do_hoc_sinh_chi_con_tra_cuu_va_thoat(co_tk):
    api, ma = co_tk
    assert api.vao_che_do_hoc_sinh()["data"]["khoa"] is True
    for goi in (lambda: api.get_run_history(), lambda: api.export_ket_qua(), lambda: api.run_pipeline(seed=1),
                lambda: api.reset_data(), lambda: api.get_giai_trinh_hoc_sinh("s2"),
                lambda: api.tao_lai_ma_tra_cuu(), lambda: api.dang_nhap("quantri", MK),
                lambda: api.dang_xuat(), lambda: api.vao_che_do_hoc_sinh()):
        r = goi()
        assert not r["ok"] and _ma_loi(r) == ["gt3_che_do_hoc_sinh"]
    # học sinh vẫn tra cứu được, và chỉ thấy thẻ của mình
    r = api.tra_cuu_hoc_sinh("s1", ma["s1"])
    assert r["ok"] and "Trần" not in str(r["data"])
    assert api.get_phien_dang_nhap()["ok"]


def test_thoat_can_dung_quan_tri_khong_ma_hoi_phan_nao_sai(co_tk):
    api, _ = co_tk
    api.vao_che_do_hoc_sinh()
    sai = [api.thoat_che_do_hoc_sinh("quantri", "sai"), api.thoat_che_do_hoc_sinh("khongco", MK)]
    assert [_ma_loi(r) for r in sai] == [["gt3_sai_thong_tin"]] * 2
    assert sai[0]["errors"] == sai[1]["errors"]
    gv = api.thoat_che_do_hoc_sinh("gv1", MK)                # đúng mật khẩu nhưng chỉ là giáo viên
    assert _ma_loi(gv) == ["gt3_sai_thong_tin"]
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is False
    assert not api.get_run_history()["ok"]                   # vẫn khoá
    ok = api.thoat_che_do_hoc_sinh("quantri", MK)
    assert ok["ok"] and ok["data"]["vai"] == "quan_tri"
    assert api.get_run_history()["ok"]


def test_mat_khau_khong_vao_nhat_ky(co_tk):
    api, _ = co_tk
    api.vao_che_do_hoc_sinh()
    api.thoat_che_do_hoc_sinh("quantri", "sai-bi-mat-xyz")
    api.thoat_che_do_hoc_sinh("quantri", MK)
    with api._ket_noi_doc() as cur:
        dong = cur.execute("SELECT chi_tiet FROM nhat_ky_thao_tac").fetchall()
    assert dong and not any(MK in (d[0] or "") or "sai-bi-mat-xyz" in (d[0] or "") for d in dong)


def test_bang_quyen_che_do_hoc_sinh():
    assert pq.QUYEN["thoat_che_do_hoc_sinh"] == pq.CONG_KHAI
    assert pq.QUYEN["vao_che_do_hoc_sinh"] == pq.GIAO_VIEN
