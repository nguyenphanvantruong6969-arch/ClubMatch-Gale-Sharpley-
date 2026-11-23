"""A5-L2: nhóm đồng hạng `a|b` — backend (chuẩn hoá ô CLB, ô học sinh, tiers, báo cáo)."""
import base64
import sqlite3

import pytest

import cau_hinh_ws
import muc_tieu as mt
import rbda_priority_pipeline as P
from api import PipelineAPI


def _db(api, sql, *a):
    with sqlite3.connect(api.db_path) as c:
        return c.execute(sql, a).fetchall()


@pytest.mark.parametrize("raw,mong", [
    ("B|a| a |", "a|b"), ("a|b", "a|b"), ("Chính sách|Khối 10", "chinh_sach|khoi_10"),
    ("a||b", "a|b"), ("|", ""), ("a|", "a"), ("A|a", "a"),
    ("Chính sách", "chinh_sach"), ("", ""), (None, ""), ("a-b", "a_b"),
])
def test_chuan_hoa_o_nhom_clb(api, raw, mong):
    assert api.chuan_hoa_o_nhom_clb(raw) == mong


def test_o_khong_gach_dung_nhu_cu(api):
    for raw in ["Chinh sach", "-", "Đoàn  viên", "chinh_sach", "  "]:
        assert api.chuan_hoa_o_nhom_clb(raw) == api.chuan_hoa_nhom_du_tru(raw)


def test_clb_ghi_a_gach_b(api):
    assert api.create_or_update_club("c1", "C1", 20, 5, "B|a| a |")["ok"]
    assert _db(api, "SELECT reserve_group FROM clubs WHERE club_id='c1'") == [("a|b",)]


def test_hoc_sinh_co_gach_bi_tu_choi_va_khong_ghi_gi(api):
    api.create_or_update_club("c1", "C1", 20, 5, "a|b")
    api.import_preferences_csv("student_id,name,pref_1\nHS1,A,c1\n")
    r = api.set_student_reserve_group("HS1", "a|b")
    assert r["ok"] is False and r["errors"][0]["code"] == "a5_nhom_hs_co_gach"
    assert _db(api, "SELECT reserve_group FROM students WHERE student_id='HS1'") == [(None,)]


def test_csv_hoc_sinh_co_gach_bi_bo_qua_va_bao(api):
    api.create_or_update_club("c1", "C1", 20, 5, "a|b")
    r = api.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS1,A,a|b,c1\nHS2,B,a,c1\n")
    assert [w["code"] for w in r["data"]["warnings"]] == ["a5_nhom_hs_co_gach"]
    # HS1 không được tạo, không có nhãn `a_b`; HS2 bình thường.
    assert _db(api, "SELECT student_id, reserve_group FROM students") == [("HS2", "a")]


def test_canh_bao_nhan_la_im_lang_khi_clb_co_a_gach_b(api):
    api.create_or_update_club("c1", "C1", 20, 5, "a|b")
    r = api.import_preferences_csv("student_id,name,reserve_group,pref_1\nHS1,A,a,c1\n")
    assert "csv_reserve_group_unknown" not in str(r)
    r = api.import_preferences_csv("student_id,name,reserve_group,pref_1\nHS1,A,z,c1\n")
    assert "csv_reserve_group_unknown" in str(r)


def test_goi_y_nhom_la_nhan_don(api):
    api.create_or_update_club("c1", "C1", 20, 5, "a|b")
    api.import_preferences_csv("student_id,name,reserve_group,pref_1\nHS1,A,c,c1\n")
    assert api.list_reserve_groups_in_use()["data"] == ["a", "b", "c"]


def test_bao_cao_suat_du_tru_dem_bang_instr_khong_like(api):
    api.create_or_update_club("c1", "C1", 20, 5, "a_b|c")
    api.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS1,A,a_b,c1\nHS2,B,c,c1\nHS3,C,axb,c1\n"
        "HS4,D,a,c1\n")
    # nhãn có `_`: LIKE sẽ khớp nhầm 'axb'. instr chỉ khớp a_b và c.
    assert api.get_suat_du_tru()["data"][0]["nhom_dang_ky"] == 2


def test_suc_khoe_du_lieu_nhan_a_trong_a_gach_b(api):
    api.create_or_update_club("c1", "C1", 20, 5, "a|b")
    api.import_preferences_csv("student_id,name,reserve_group,pref_1\nHS1,A,a,c1\nHS2,B,b,c1\n")
    ma = [w["code"] if isinstance(w, dict) and "code" in w else str(w)
          for w in api.get_data_health_report()["data"]["warnings"]]
    assert not any("health_orphan_student_group" in m or "health_club_group_no_students" in m
                   for m in ma), ma


def test_tiers_cung_hang_hop_le_va_cheo_hang_bi_loi():
    cfg = cau_hinh_ws.chuan_hoa({"rules": {"tiers": ["a|b", "c"]}})
    assert cfg["rules"]["tiers"] == ["a|b", "c"]
    for xau in (["a", "a|b"], ["a|a"], ["a||b"], ["a|", "b"], ["Khối 1|x", "khoi  1"]):
        with pytest.raises(ValueError):
            cau_hinh_ws.chuan_hoa({"rules": {"tiers": xau}})


def test_tiers_khong_gach_giu_hanh_vi_cu():
    cfg = cau_hinh_ws.chuan_hoa({"rules": {"tiers": ["Khối 12", "khoi 12"]}})
    assert cfg["rules"]["tiers"] == ["Khối 12", "khoi 12"]


def test_tiers_x_ab_c_xep_hang_1_1_2():
    hs = {"s1": {"reserve_group": "a"}, "s2": {"reserve_group": "b"}, "s3": {"reserve_group": "c"}}
    assert P.xay_tier_rank(hs, ["x", "a|b", "c"]) == {"s1": 1, "s2": 1, "s3": 2}


def test_tiers_nbsp_trong_muc_a_gach_b():
    hs = {"s1": {"reserve_group": "Khối 12"}, "s2": {"reserve_group": "b"}}
    assert P.xay_tier_rank(hs, ["Khối 12 | b"]) == {"s1": 0, "s2": 0}


def test_the_muc_tieu_khoa_khi_clb_a_gach_b():
    hs = {"s1": {"reserve_group": "a"}, "s2": {"reserve_group": "b"}}
    clb = {"c1": {"capacity": 10, "reserve_capacity": 3, "reserve_group": "a|b"}}
    r = mt.de_xuat_cho_giu(hs, clb, "a")
    assert "c1" in r["clb_ghi_de"]
    rules = mt.rules_cua_muc_tieu(mt.NANG_LUC, {})
    assert mt.nhan_dien_muc_tieu(rules, clb, {"id": mt.DANH_CHO, "nhom": "a"}, hs) == mt.TUY_CHINH


def test_vong_tron_so_nhap_giu_a_gach_b(api, tmp_path):
    api.create_or_update_club("c1", "C1", 20, 5, "B|a")
    api.import_preferences_csv("student_id,name,reserve_group,pref_1\nHS1,A,a,c1\n")
    r = api.export_du_lieu_dau_vao()
    assert r["ok"], r
    (tmp_path / "b").mkdir()
    b = PipelineAPI(str(tmp_path / "b" / "app.db"))
    with open(r["data"]["path"], "rb") as f:
        kq = b.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"], kq
    assert _db(b, "SELECT reserve_group FROM clubs WHERE club_id='c1'") == [("a|b",)]
    assert _db(b, "SELECT reserve_group FROM students WHERE student_id='HS1'") == [("a",)]


def test_gan_hang_loat_co_gach_bi_tu_choi_db_khong_doi(api):
    api.create_or_update_club("c1", "C1", 20, 5, "a|b")
    api.import_preferences_csv("student_id,name,reserve_group,pref_1\nHS1,A,a,c1\nHS2,B,,c1\n")
    truoc = _db(api, "SELECT student_id, reserve_group FROM students ORDER BY 1")
    r = api.bulk_set_reserve_group(["HS1", "HS2"], "a|b")
    assert r["ok"] is False and r["errors"][0]["code"] == "a5_nhom_hs_co_gach_hang_loat"
    assert _db(api, "SELECT student_id, reserve_group FROM students ORDER BY 1") == truoc
    assert api.bulk_set_reserve_group(["HS1", "HS2"], "Chính sách")["ok"] is True
    assert _db(api, "SELECT reserve_group FROM students ORDER BY 1") == [("chinh_sach",)] * 2


def _so(clubs, hs):
    import io
    import so_nhap
    bio = io.BytesIO()
    so_nhap.ghi_so_nhap(bio, clubs=clubs, students=hs)
    return base64.b64encode(bio.getvalue()).decode()


_CLB = [{"club_id": "c1", "name": "C1", "capacity": 10, "reserve_capacity": 2,
         "reserve_group": "a|b", "buoi": ""}]


def _hs(*nhan):
    return [{"student_id": "S%d" % i, "name": "Em %d" % i, "reserve_group": n,
             "nv": [{"club_id": "c1", "thi": False, "diem": ""}]} for i, n in enumerate(nhan)]


def _dem(api):
    return (_db(api, "SELECT COUNT(*) FROM students"), _db(api, "SELECT COUNT(*) FROM clubs"),
            _db(api, "SELECT COUNT(*) FROM preferences"))


def test_xem_truoc_so_nhap_bao_hoc_sinh_co_gach_va_khong_ghi_gi(api):
    x = _so(_CLB, _hs("a", "a|b", "b|c"))
    truoc = _dem(api)
    kq = api.xem_truoc_so_nhap(x)
    assert kq["ok"], kq["errors"]
    a5 = [(w["params"]["student_id"], w["params"]["reserve_group"])
          for w in kq["data"]["canh_bao"] if w["code"] == "a5_nhom_hs_co_gach"]
    assert a5 == [("S1", "a|b"), ("S2", "b|c")]
    assert _dem(api) == truoc == ([(0,)], [(0,)], [(0,)])           # chỉ xem, không ghi gì


def test_xem_truoc_so_nhap_khong_co_gach_khong_them_gi(api):
    sach = api.xem_truoc_so_nhap(_so(_CLB, _hs("a", "b")))["data"]
    co = api.xem_truoc_so_nhap(_so(_CLB, _hs("a", "a|b")))["data"]
    assert not [w for w in sach["canh_bao"] if w["code"] == "a5_nhom_hs_co_gach"]
    # bỏ cảnh báo A5 thì phần còn lại của hai bản xem trước y hệt nhau
    bo = [w for w in co["canh_bao"] if w["code"] != "a5_nhom_hs_co_gach"]
    assert bo == sach["canh_bao"] and {k: v for k, v in co.items() if k != "canh_bao"} == \
        {k: v for k, v in sach.items() if k != "canh_bao"}


def test_nhap_that_van_bo_qua_hoc_sinh_co_gach_va_canh_bao(api):
    kq = api.import_so_nhap(_so(_CLB, _hs("a", "a|b")))
    assert kq["ok"], kq["errors"]
    assert "a5_nhom_hs_co_gach" in {w["code"] for w in kq["data"]["warnings"]}
    assert _db(api, "SELECT student_id, reserve_group FROM students") == [("S0", "a")]
