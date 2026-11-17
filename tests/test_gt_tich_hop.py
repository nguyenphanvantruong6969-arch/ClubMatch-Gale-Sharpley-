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


# ----------------------------------------------------------------------------- I3: nhật ký cho thao tác GT1/GT2
def _dong_nk(api, hanh_dong):
    with api._ket_noi_doc() as cur:
        return [dict(zip(("nguoi", "vai", "ket_qua", "chi_tiet"), r)) for r in cur.execute(
            "SELECT nguoi, vai, ket_qua, chi_tiet FROM nhat_ky_thao_tac WHERE hanh_dong = ? ORDER BY id",
            (hanh_dong,))]


def test_i3_moi_thao_tac_gt1_gt2_de_lai_dung_mot_dong(co_tk):
    api, ma = co_tk
    assert api.dang_xuat()["ok"] and api.dang_nhap("quantri", MK)["ok"]
    luat_thu = {"priority": "tier", "tiers": ["khong_co_nhom_nay"]}
    r = api.run_thu(luat_thu)
    assert r["ok"], r
    assert api.tao_ma_tra_cuu()["ok"]
    lai = api.tao_lai_ma_tra_cuu("s1")
    assert lai["ok"], lai
    assert api.export_ma_tra_cuu_csv()["ok"]
    assert api.export_phieu_giai_trinh()["ok"]
    # đúng MỘT dòng cho mỗi lời gọi (`_dung` gọi tao_ma_tra_cuu khi chưa có tài khoản nên không để dòng nào)
    for ten in ("run_thu", "tao_ma_tra_cuu", "tao_lai_ma_tra_cuu", "export_ma_tra_cuu_csv", "export_phieu_giai_trinh"):
        dong = _dong_nk(api, ten)
        assert len(dong) == 1, ten
        assert dong[0]["ket_qua"] == "ok" and dong[0]["nguoi"] == "quantri" and dong[0]["vai"] == "quan_tri", ten
    # mã tra cứu / mật khẩu / mã của học sinh khác không nằm trong nhật ký
    with api._ket_noi_doc() as cur:
        toan = str(cur.execute("SELECT * FROM nhat_ky_thao_tac").fetchall())
    for bi_mat in [lai["data"].get("ma", "?x?"), MK, *ma.values()]:
        assert str(bi_mat) not in toan


def test_i3_ap_dung_tieu_chi_de_lai_dung_mot_dong(tmp_path):
    from test_gt2_ap_dung import LUAT_THU, _mo
    a, _db, slug = _mo(tmp_path)
    assert a.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    r = a.run_thu(LUAT_THU)
    assert r["ok"], r
    k = a.ap_dung_tieu_chi(r["data"]["run_id"], slug)
    assert k["ok"], k
    for ten in ("run_thu", "ap_dung_tieu_chi"):
        dong = _dong_nk(a, ten)
        assert len(dong) == 1 and dong[0]["ket_qua"] == "ok" and dong[0]["nguoi"] == "quantri", ten
    assert _dong_nk(a, "update_workspace_config") == []         # lời gọi lồng bên trong không ghi thêm dòng


def test_i3_giao_vien_bi_tu_choi_quan_tri_va_dong_nhat_ky_ghi_loi(co_tk):
    api, _ = co_tk
    for ten, goi in (("run_thu", lambda: api.run_thu({"priority": "tier"})),
                     ("tao_lai_ma_tra_cuu", lambda: api.tao_lai_ma_tra_cuu("s1")),
                     ("export_ma_tra_cuu_csv", lambda: api.export_ma_tra_cuu_csv())):
        r = goi()
        assert not r["ok"]
        dong = _dong_nk(api, ten)
        assert len(dong) == 1 and dong[0]["nguoi"] == "gv1" and dong[0]["ket_qua"] != "ok", ten


def test_i3_chi_tiet_dong_nhat_ky_khong_lo_bi_mat(co_tk):
    api, _ = co_tk
    assert api.dang_xuat()["ok"] and api.dang_nhap("quantri", MK)["ok"]
    assert api.run_thu({"priority": "tier", "tiers": ["khong_co_nhom_nay"]})["ok"]
    assert api.tao_lai_ma_tra_cuu("s1")["ok"]
    assert api.export_phieu_giai_trinh(student_ids=["s1"])["ok"]
    for ten in ("run_thu", "tao_lai_ma_tra_cuu", "export_phieu_giai_trinh"):
        (dong,) = _dong_nk(api, ten)
        assert len(dong["chi_tiet"] or "") <= 300 and "Nguyễn" not in (dong["chi_tiet"] or ""), ten
    assert "s2" not in (_dong_nk(api, "tao_lai_ma_tra_cuu")[0]["chi_tiet"] or "")
