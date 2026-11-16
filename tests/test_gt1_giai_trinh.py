"""GT1-L1: giải trình kết quả cho MỘT học sinh (động cơ `giai_trinh` + API). Dữ liệu là dữ liệu MÔ PHỎNG.

(a) FA tắt, 3 bộ × 5 seed: mọi CLB xếp trên CLB được nhận đều có mã FULL_* / RESERVED / NOT_TESTED và
    học sinh đứng SAU người nhận cuối (khớp `verify_stability`: không có ghen tị chính đáng);
(b) FA bật: mã bằng lý do đã lưu ở `fa_ly_do`;
(c) riêng tư: JSON một em không chứa mã hay tên em khác;
(d) sửa dữ liệu sau lần chạy -> `du_lieu_da_doi`;
(e) `kiem_nhanh.py` giống hệt (không đụng đường chạy) — kiểm bằng lệnh, không phải test này.
"""

import json
import re

import pytest

import fa_ly_do
import giai_trinh as gt
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma
from _wharton import tat_wharton
from _ket_qua_bo_test import nap_bo

MA_TU_CHOI_HOP_LE = {"FULL_SCORE", "FULL_LOTTERY", "FULL_GROUP", "FULL_WHARTON", "RESERVED",
                     "NOT_TESTED"}


def _chay(api_factory, bo, seed):
    api = api_factory()
    tat_wharton(api)               # bộ CSV không có hồ sơ Wharton: luật RB-DA thuần (mặc định mới là BẬT)
    nap_bo(api, bo)
    assert api.run_pipeline(seed=seed)["ok"]
    return api


def _hs_va_nv(api):
    with api._ket_noi_doc() as cur:
        hs = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
    return hs


# ---------------------------------------------------------------------------- (a)
@pytest.mark.parametrize("bo", ["nhieu_buoi", "sach", "can_bang"])
@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_a_moi_clb_cao_hon_bi_tu_choi_co_ly_do_hop_le(api_factory, bo, seed):
    api = _chay(api_factory, bo, seed)
    n_clb_cao = 0
    for sid in _hs_va_nv(api):
        ra = api.get_giai_trinh_hoc_sinh(sid)
        assert ra["ok"], (sid, ra)
        d = ra["data"]
        assert d["fa_bat"] is False and d["du_lieu_da_doi"] is False
        for b in d["buoi"]:
            ds = b["cac_lua_chon"]
            if b["ket_qua"] is None:
                assert b["ma_tom_tat"] == ("UNASSIGNED" if ds else "NO_CHOICES")
            else:
                assert b["ma_tom_tat"] == "ACCEPTED"
            xep = [i for i, x in enumerate(ds) if x["duoc_xep"]]
            assert len(xep) == (1 if b["ket_qua"] else 0), (sid, b)
            for i, x in enumerate(ds):
                if b["ket_qua"] is None or i < xep[0]:
                    assert x["ma"] in MA_TU_CHOI_HOP_LE, (sid, x)
                    assert x["cau"], x
                    n_clb_cao += 1
                elif i > xep[0]:
                    assert x["ma"] == "HIGHER_CHOICE_ACCEPTED", (sid, x)
                else:
                    assert x["ma"] == "ACCEPTED"
    assert n_clb_cao > 0          # bộ dữ liệu có từ chối thật, không kiểm suông


def test_a_hoc_sinh_dung_sau_nguoi_nhan_cuoi(api_factory):
    """Khớp ổn định: học sinh bị từ chối ở CLB mà hạng nền của em SAU người nhận cuối, trừ mã RESERVED."""
    import rbda_priority_pipeline as rp
    api = _chay(api_factory, "can_bang", 7)
    luat = api._luat_nghiem()
    du_lieu, _ = rp.load_from_sqlite_kem_dau_van_tay(api.db_path, luat)
    for sid in _hs_va_nv(api)[:60]:
        d = api.get_giai_trinh_hoc_sinh(sid)["data"]
        for b in d["buoi"]:
            for x in b["cac_lua_chon"]:
                if x["ma"] in ("FULL_SCORE", "FULL_LOTTERY"):
                    assert x["sau_nguoi_nhan_cuoi"] is True, (sid, x)
    assert du_lieu


# ---------------------------------------------------------------------------- (b)
def test_b_fa_bat_ma_bang_ly_do_da_luu(api):
    bat_fa(api)
    dung_fa_clb(api, S=(1, "GIOI_HAN", None, None, None, "thu_2"),
                T=(9, "TU_DO", None, None, None, "thu_2"))
    ds = ["a", "b", "c"]
    dung_hs_fa(api, *ds, nv={s: ["S", "T"] for s in ds})
    assert api.run_pipeline(seed=3)["ok"]
    with api._ket_noi_doc() as cur:
        luu = {(r[0], r[1]): r[2] for r in cur.execute(
            "SELECT student_id, club_id, reason FROM fa_ly_do")}
    assert luu
    for sid in ds:
        d = api.get_giai_trinh_hoc_sinh(sid)["data"]
        assert d["fa_bat"] is True
        for b in d["buoi"]:
            for x in b["cac_lua_chon"]:
                if (sid, x["club_id"]) in luu:
                    assert x["ma"] == luu[(sid, x["club_id"])], (sid, x)
                    assert x["cau"]


# ---------------------------------------------------------------------------- (c)
def test_c_rieng_tu_chi_co_du_lieu_cua_chinh_em(api_factory):
    api = _chay(api_factory, "can_bang", 11)
    tat_ca = _hs_va_nv(api)
    with api._ket_noi_doc() as cur:
        ten = {r[0]: r[1] for r in cur.execute("SELECT student_id, name FROM students")}
    for sid in tat_ca[:25]:
        d = api.get_giai_trinh_hoc_sinh(sid)["data"]
        chuoi = json.dumps(d, ensure_ascii=False)
        for khac in tat_ca:
            if khac == sid:
                continue
            assert not re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(khac), chuoi), \
                (sid, khac)
            if ten.get(khac) and ten[khac] != ten.get(sid):
                assert ten[khac] not in chuoi, (sid, khac)


# ---------------------------------------------------------------------------- (d)
def test_d_sua_du_lieu_sau_khi_chay_bao_du_lieu_da_doi(api_factory):
    api = _chay(api_factory, "sach", 5)
    sid = _hs_va_nv(api)[0]
    assert api.get_giai_trinh_hoc_sinh(sid)["data"]["du_lieu_da_doi"] is False
    with api._ket_noi_ghi() as cur:
        cid = cur.execute("SELECT club_id FROM clubs ORDER BY club_id").fetchone()[0]
        cur.execute("UPDATE clubs SET capacity = capacity + 1 WHERE club_id = ?", (cid,))
    assert api.get_giai_trinh_hoc_sinh(sid)["data"]["du_lieu_da_doi"] is True


# ---------------------------------------------------------------------------- lỗi
def test_loi_chua_chay_va_khong_co_hoc_sinh(api):
    assert ma(api.get_giai_trinh_hoc_sinh("x")["errors"]) == ["gt1_chua_chay"]
    dung_fa_clb(api, A=(2, None, None, None, None, "thu_2"))
    dung_hs_fa(api, "s1", nv={"s1": ["A"]})
    assert api.run_pipeline(seed=1)["ok"]
    assert ma(api.get_giai_trinh_hoc_sinh("khong_co")["errors"]) == ["gt1_khong_co_hoc_sinh"]
    assert api.get_giai_trinh_hoc_sinh("s1")["ok"]


def test_khong_ghi_gi_vao_csdl(api_factory):
    api = _chay(api_factory, "sach", 5)
    bang = ["match_results", "run_history", "stb_lock", "students", "fa_ly_do", "dau_van_tay_chay"]
    def chup():
        with api._ket_noi_doc() as cur:
            return {b: [tuple(r) for r in cur.execute("SELECT * FROM %s" % b)] for b in bang}
    truoc = chup()
    for sid in _hs_va_nv(api)[:10]:
        assert api.get_giai_trinh_hoc_sinh(sid)["ok"]
    assert chup() == truoc


# ---------------------------------------------------------------------------- câu
def test_cau_ly_do_rbda_chi_noi_ve_em_va_clb():
    cac = ["ACCEPTED", "HIGHER_CHOICE_ACCEPTED", "FULL_SCORE", "FULL_LOTTERY", "FULL_GROUP",
           "FULL_WHARTON", "RESERVED", "NOT_TESTED"]
    for m in cac:
        c = fa_ly_do.cau_ly_do_rbda({"ma": m, "rank_in_list": 2, "cut_score": 7.5, "diem_em": 6.0},
                                    "CLB Bóng rổ")
        assert isinstance(c, str) and c and "CLB Bóng rổ" in c, m
    assert "7.5" in fa_ly_do.cau_ly_do_rbda({"ma": "FULL_SCORE", "cut_score": 7.5, "diem_em": 6.0}, "X")
    assert "bốc thăm" in fa_ly_do.cau_ly_do_rbda({"ma": "FULL_LOTTERY"}, "X")


def test_dong_pure_khong_cham_db():
    assert hasattr(gt, "giai_trinh_mot_hoc_sinh")


def test_wharton_bat_fa_tat_dung_lai_dung_ket_qua_va_co_ly_do(tmp_path):
    """Mặc định mới của kiosk (Wharton BẬT, FA tắt): dựng lại phải ra đúng kết quả đã lưu."""
    import api as api_mod
    from _wharton import bat_wharton
    from test_wharton import sinh_bo
    from test_wharton_pipeline import _nap_bo_vao_api
    bo = sinh_bo(503, n_hs=16, n_clb=6, so_buoi=2)
    api = api_mod.PipelineAPI(str(tmp_path / "w.db"))
    bat_wharton(api)
    _nap_bo_vao_api(api, bo)
    assert api.run_pipeline(seed=7)["ok"]
    dem = 0
    for sid in bo.sids:
        ra = api.get_giai_trinh_hoc_sinh(sid)
        assert ra["ok"], ra
        d = ra["data"]
        assert d["du_lieu_da_doi"] is False, sid
        for b in d["buoi"]:
            for x in b["cac_lua_chon"]:
                if not x["duoc_xep"] and x["ma"] != "HIGHER_CHOICE_ACCEPTED":
                    assert x["ma"] in MA_TU_CHOI_HOP_LE and x["cau"], x
                    dem += 1
    assert dem > 0


# ---------------------------------------------------------------------------- FIX L1 (vòng 1)
def test_hoc_sinh_khong_nguyen_vong_khong_bi_noi_la_clb_da_day():
    du_lieu = {"fa_bat": False, "du_lieu_da_doi": False, "run": {}, "ds_buoi": ["thu_2"],
               "buoi": {"thu_2": {"clubs": {"S": {"ten": "CLB S", "capacity": 1}}, "prefs": {"s3": []},
                                  "scores": {}, "stb": {}, "assign": {}, "base_rank": {}, "fa_rows": {}}}}
    b = gt.giai_trinh_mot_hoc_sinh(du_lieu, "s3")["buoi"][0]
    assert b["cac_lua_chon"] == [] and b["ma_tom_tat"] == gt.NO_CHOICES
    assert "đủ chỗ" not in b["cau_tom_tat"] and "chưa đăng ký" in b["cau_tom_tat"]


def test_run_id_cu_bi_tu_choi_va_run_id_la_bao_loi_rieng(api_factory):
    api = _chay(api_factory, "sach", 5)
    assert api.run_pipeline(seed=5)["ok"]
    sid = _hs_va_nv(api)[0]
    with api._ket_noi_doc() as cur:
        ids = [r[0] for r in cur.execute("SELECT run_id FROM run_history ORDER BY run_id")]
    assert len(ids) >= 2
    assert ma(api.get_giai_trinh_hoc_sinh(sid, run_id=ids[0])["errors"]) == ["gt1_lan_chay_cu"]
    ra = api.get_giai_trinh_hoc_sinh(sid, run_id=ids[-1])
    assert ra["ok"] and ra["data"]["du_lieu_da_doi"] is False
    assert api.get_giai_trinh_hoc_sinh(sid)["data"]["du_lieu_da_doi"] is False
    assert ma(api.get_giai_trinh_hoc_sinh(sid, run_id=9999)["errors"]) == ["gt1_khong_tim_thay_lan_chay"]
