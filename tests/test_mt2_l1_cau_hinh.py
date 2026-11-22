"""MT2-L1: khoá luật `rules.chia_loai` (Chia CLB theo loại) — cấu hình + công tắc, chưa đổi thuật toán.

Hiệu lực = `chia_loai` hoặc `fa_daa` (`dung_chia_loai`). TẮT = bỏ qua `loai`, không xoá. Khoá chỉ có mặt trong
chuỗi ghi `run_history.luat_xep` và dấu vân tay khi BẬT, để workspace cũ (kể cả `fa_daa`) giữ từng byte.
"""

import json

import pytest

import cau_hinh_ws as ch
import rbda_priority_pipeline as rp
import tieu_chi as tc


def _luat(**rest):
    return ch.chuan_hoa({"rules": dict(rest)})["rules"]


def test_mac_dinh_tat_o_ca_hai_tang():
    assert rp.LUAT_XEP_MAC_DINH["chia_loai"] is False
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["chia_loai"] is False
    assert _luat()["chia_loai"] is False


@pytest.mark.parametrize("rest", [
    {"chia_loai": True, "wharton": False},                       # chế độ "chỉ xếp" (không điểm)
    {"chia_loai": True, "wharton": True},                        # điểm quyết tâm
    {"chia_loai": True, "wharton": True, "fa_daa": True},        # huy chương
])
def test_bat_duoc_voi_ca_ba_che_do(rest):
    assert _luat(**rest)["chia_loai"] is True


@pytest.mark.parametrize("gia_tri", ["yes", 1, 0, None, "true", [], {}])
def test_phai_la_bool_that(gia_tri):
    with pytest.raises(ValueError):
        _luat(chia_loai=gia_tri)


def test_dung_chia_loai_la_chia_loai_hoac_fa_daa():
    assert rp.dung_chia_loai({}) is False
    assert rp.dung_chia_loai({"chia_loai": True, "wharton": False}) is True
    assert rp.dung_chia_loai({"wharton": True, "fa_daa": True}) is True   # legacy Huy chương
    assert rp.dung_chia_loai({"wharton": True, "chia_loai": False, "fa_daa": False}) is False


def test_dung_chia_loai_nem_loi_voi_gia_tri_hong():
    with pytest.raises(ValueError):
        rp.dung_chia_loai({"chia_loai": "yes"})


def test_chuoi_ghi_va_dau_van_tay_khong_doi_khi_tat():
    cu = {"priority": "score", "tier_mode": "strict", "tiers": ["A"], "score_scope": "per_slot"}
    moi = dict(cu, chia_loai=False)
    assert rp.luat_xep_de_ghi(cu) == rp.luat_xep_de_ghi(moi)
    assert "chia_loai" not in (rp.luat_xep_de_ghi(moi) or "")
    # legacy fa_daa: chuỗi ghi không có khoá chia_loai (không tự thêm True)
    fa = {"wharton": True, "fa_daa": True}
    ghi = json.loads(rp.luat_xep_de_ghi(fa))
    assert "chia_loai" not in ghi and ghi["fa_daa"] is True


def test_chuoi_ghi_co_khoa_khi_bat_va_khac_luat_tat():
    bat = {"wharton": False, "chia_loai": True}
    ghi = json.loads(rp.luat_xep_de_ghi(bat))
    assert ghi["chia_loai"] is True
    assert rp.luat_xep_de_ghi(bat) != rp.luat_xep_de_ghi({"wharton": False})


def test_tieu_chi_liet_ke_khoa_moi():
    assert set(tc.cac_lua_chon_hop_le()) == set(rp.LUAT_XEP_MAC_DINH)
    assert "chia_loai" in tc.cac_lua_chon_hop_le()


def test_getter_cho_giao_dien(tmp_path):
    import os

    import api as api_mod
    import workspace as ws
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    api = api_mod.PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc)
    r = api.get_chia_loai()
    assert r["ok"], r
    assert r["data"] == {"chia_loai": False, "fa_daa": False, "hieu_luc": False}
    assert api.update_workspace_config({"rules": {"wharton": False, "chia_loai": True}})["ok"]
    d = api.get_chia_loai()["data"]
    assert d["chia_loai"] is True and d["hieu_luc"] is True
    assert api.update_workspace_config({"rules": {"chia_loai": False}})["ok"]   # TẮT lại
    assert api.get_chia_loai()["data"]["hieu_luc"] is False


def test_phan_quyen_cho_getter():
    import phan_quyen as pq
    assert "get_chia_loai" in pq.QUYEN
    assert pq.QUYEN["get_chia_loai"] == pq.QUYEN["get_san_sang_huy_chuong"]
