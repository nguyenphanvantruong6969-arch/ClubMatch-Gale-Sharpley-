"""MT1-L1 — danh mục ba thẻ mục tiêu (`muc_tieu.py`, phần thuần). Số liệu MÔ PHỎNG.

Kiểm: bản vá luật qua `cau_hinh_ws._chuan_hoa`; chỉ khoá của `LUAT_XEP_MAC_DINH`, không `wharton`/`fa_daa`;
cấu hình mặc định ⇒ `nang_luc`; bản vá `nang_luc` = luật mặc định; `co_hoi` ra đúng thứ tự bốc thăm thuần
(so với bản Gale–Shapley viết riêng); công thức số chỗ trên ca 10 em tính tay; tỉ lệ chỉ đọc danh sách học sinh.
"""

import copy
import inspect
import os
import sqlite3
import sys

import pytest

import api as api_mod
import cau_hinh_ws
import muc_tieu as mt
import rbda_priority_pipeline as rb

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402


# ----- danh mục -----

def test_ba_the_dung_thu_tu_va_chu_ngan():
    assert list(mt.BO_MUC_TIEU) == ["nang_luc", "co_hoi", "danh_cho"]
    for the in mt.BO_MUC_TIEU.values():
        for ngon in ("vi", "en"):
            assert the["tieu_de"][ngon].strip()
            assert 0 < len(the["cau"][ngon]) <= 90, the["id"]


def test_chu_hien_ra_khong_co_chu_noi_bo():
    cam = ("dự trữ", "STB", "Wharton", "wharton", "tier", "reserve", "fa_daa")
    for the in mt.BO_MUC_TIEU.values():
        for ngon in ("vi", "en"):
            for chu in (the["tieu_de"][ngon], the["cau"][ngon]):
                assert not any(c in chu for c in cam), chu


@pytest.mark.parametrize("mid", list(mt.BO_MUC_TIEU))
def test_ban_va_chi_dung_khoa_luat_xep_va_khong_cham_wharton_fa(mid):
    khoa = set(mt.BO_MUC_TIEU[mid]["luat"])
    assert khoa <= set(rb.LUAT_XEP_MAC_DINH)
    assert not khoa & {"wharton", "fa_daa"}


@pytest.mark.parametrize("mid", list(mt.BO_MUC_TIEU))
@pytest.mark.parametrize("wh", [True, False])
def test_ban_va_qua_chuan_hoa_va_giu_nguyen_wharton_fa(mid, wh):
    goc = {"wharton": wh, "fa_daa": False}
    ra = mt.rules_cua_muc_tieu(mid, goc)
    assert goc == {"wharton": wh, "fa_daa": False}            # không sửa bản của người gọi
    assert ra["wharton"] is wh and ra["fa_daa"] is False
    if mid == "co_hoi" and "wharton" in goc and wh:
        # luật cũ ghi RÕ wharton=True + priority tier bị từ chối: đó là chuyện của câu hỏi thứ nhất
        with pytest.raises(ValueError):
            cau_hinh_ws._chuan_hoa({"rules": ra})
        return
    cau_hinh_ws._chuan_hoa({"rules": ra})                      # không ném


def test_the_co_hoi_khong_ghi_wharton_thi_chuan_hoa_tu_tat_wharton():
    ra = mt.rules_cua_muc_tieu("co_hoi", {})
    assert "wharton" not in ra
    cfg = cau_hinh_ws._chuan_hoa({"rules": ra})
    assert cfg["rules"]["priority"] == "tier" and cfg["rules"]["wharton"] is False


def test_cau_hinh_mac_dinh_la_nang_luc_va_ban_va_nang_luc_bang_luat_mac_dinh():
    mac_dinh = cau_hinh_ws.MAC_DINH_TRUONG_HOC["rules"]
    assert mt.nhan_dien_muc_tieu(mac_dinh, {}) == "nang_luc"
    assert mt.nhan_dien_muc_tieu({}, {}) == "nang_luc"
    assert mt.nhan_dien_muc_tieu(None, {}) == "nang_luc"
    ra = mt.rules_cua_muc_tieu("nang_luc", mac_dinh)
    assert rb.luat_xep_cua(ra) == rb.luat_xep_cua(mac_dinh)
    assert ra == mac_dinh
    for khoa in ("priority", "tier_mode", "score_scope", "tiers"):
        assert ra[khoa] == mac_dinh[khoa]


def test_rules_cua_muc_tieu_id_la_thi_ne_keyerror():
    with pytest.raises(KeyError):
        mt.rules_cua_muc_tieu("khong_co", {})


@pytest.mark.parametrize("mid", ["nang_luc", "co_hoi"])
def test_ap_the_roi_nhan_dien_lai_ra_dung_the(mid):
    assert mt.nhan_dien_muc_tieu(mt.rules_cua_muc_tieu(mid, {"max_choices": 7}), {}) == mid


def test_sua_tay_luat_thi_tuy_chinh():
    cs = [{"priority": "score+tier"}, {"tier_mode": "strict"}, {"score_scope": "per_person"},
          {"priority": "score", "tier_mode": "strict", "tiers": ["Khối 10"]},
          {"priority": "tier", "tiers": ["Khối 10"]}]
    for r in cs:
        assert mt.nhan_dien_muc_tieu(r, {}) == "tuy_chinh", r


# ----- danh_cho: nhận diện cần thẻ đã chọn + dữ liệu CLB -----

def _hs(n_nhom, n_khac, nhom="Khối 10"):
    s = {"S%02d" % i: {"reserve_group": nhom} for i in range(n_nhom)}
    s.update({"T%02d" % i: {"reserve_group": "Khối 11"} for i in range(n_khac)})
    return s


def test_nhan_dien_danh_cho_va_sua_tay_thi_tuy_chinh():
    hs = _hs(3, 7)
    clubs = {"A": {"capacity": 10, "reserve_capacity": 3, "reserve_group": "khoi 10"},
             "B": {"capacity": 20, "reserve_capacity": 6, "reserve_group": "Khối 10"}}
    r = mt.rules_cua_muc_tieu("danh_cho", {})
    chon = {"id": "danh_cho", "nhom": "Khối 10"}
    assert mt.nhan_dien_muc_tieu(r, clubs, chon, hs) == "danh_cho"
    # không có thẻ đã chọn thì dữ liệu CLB đơn thuần là dữ liệu nhập: vẫn "theo năng lực"
    assert mt.nhan_dien_muc_tieu(r, clubs) == "nang_luc"
    sua = copy.deepcopy(clubs)
    sua["A"]["reserve_capacity"] = 4                          # sửa tay số chỗ một CLB
    assert mt.nhan_dien_muc_tieu(r, sua, chon, hs) == "tuy_chinh"
    sua = copy.deepcopy(clubs)
    sua["B"]["reserve_group"] = "Khối 11"                     # một CLB giữ chỗ cho nhóm khác
    assert mt.nhan_dien_muc_tieu(r, sua, chon, hs) == "tuy_chinh"
    assert mt.nhan_dien_muc_tieu({"priority": "score+tier"}, clubs, chon, hs) == "tuy_chinh"


# ----- công thức số chỗ (tính tay) -----

def test_cong_thuc_so_cho_ca_10_em_tinh_tay():
    hs = _hs(3, 7)                                            # nhóm 3/10 = 30 %
    clubs = {"A": {"capacity": 10}, "B": {"capacity": 15}, "C": {"capacity": 1}, "D": {"capacity": 3},
             "E": {"capacity": 7}}
    r = mt.de_xuat_cho_giu(hs, clubs, "khối 10")              # khác hoa/thường/dấu vẫn khớp
    # ceil(0.3*10)=3 ; ceil(0.3*15)=ceil(4.5)=5 ; ceil(0.3*1)=1 ; ceil(0.3*3)=ceil(0.9)=1 ; ceil(0.3*7)=ceil(2.1)=3
    assert r["cho_giu"] == {"A": 3, "B": 5, "C": 1, "D": 1, "E": 3}
    assert (r["so_em_nhom"], r["tong_em"]) == (3, 10)
    assert r["clb_it"] == ["C", "D"] and "it_qua" in r["canh_bao"]
    assert all(r["cho_giu"][c] <= clubs[c]["capacity"] for c in clubs)


def test_so_cho_khong_vuot_suc_chua_khi_ca_truong_cung_nhom():
    r = mt.de_xuat_cho_giu(_hs(4, 0), {"A": {"capacity": 2}, "B": {"capacity": 9}}, "Khối 10")
    assert r["cho_giu"] == {"A": 2, "B": 9}


def test_khong_co_nhom_thi_khong_giu_cho_va_bao():
    r = mt.de_xuat_cho_giu(_hs(0, 5), {"A": {"capacity": 10}}, "Khối 10")
    assert r["cho_giu"] == {"A": 0} and r["canh_bao"] == ["khong_co_nhom"]
    r = mt.de_xuat_cho_giu({}, {"A": {"capacity": 10}}, "Khối 10")
    assert r["cho_giu"] == {"A": 0} and r["canh_bao"] == ["khong_co_nhom"]
    assert mt.de_xuat_cho_giu(_hs(2, 2), {"A": {"capacity": 10}}, None)["cho_giu"] == {"A": 0}


def test_khong_canh_bao_it_qua_khi_deu_tu_3_cho():
    r = mt.de_xuat_cho_giu(_hs(5, 5), {"A": {"capacity": 10}, "B": {"capacity": 20}}, "Khối 10")
    assert r["cho_giu"] == {"A": 5, "B": 10} and r["canh_bao"] == [] and r["clb_it"] == []


def test_bao_clb_dang_giu_cho_cho_nhom_khac_de_hoan_tac():
    clubs = {"A": {"capacity": 10, "reserve_capacity": 2, "reserve_group": "Khối 12"},
             "B": {"capacity": 10, "reserve_capacity": 0, "reserve_group": "Khối 12"},
             "C": {"capacity": 10, "reserve_capacity": 2, "reserve_group": "khoi 10"}}
    assert mt.de_xuat_cho_giu(_hs(3, 7), clubs, "Khối 10")["clb_ghi_de"] == ["A"]


def test_cac_nhom_gop_cach_viet_khac_va_bo_em_khong_nhom():
    hs = {"1": {"reserve_group": "Khối 10"}, "2": {"reserve_group": "khoi 10"},
          "3": {"reserve_group": " Khối  10 "}, "4": {"reserve_group": "Khối 11"},
          "5": {"reserve_group": None}, "6": {"reserve_group": ""}, "7": {}}
    assert mt.cac_nhom(hs) == [{"nhan": "Khối 10", "so_em": 3}, {"nhan": "Khối 11", "so_em": 1}]
    assert mt.cac_nhom({}) == []


def test_ti_le_chi_doc_danh_sach_hoc_sinh_khong_doc_nguyen_vong_hay_ket_qua():
    # (1) chữ ký: chỉ nhận danh sách học sinh, CLB và tên nhóm — không có tham số nguyện vọng/kết quả
    ten = set(inspect.signature(mt.de_xuat_cho_giu).parameters)
    assert ten == {"students", "clubs", "nhom"}
    # (2) thêm khoá lạ vào học sinh / CLB (nguyện vọng, kết quả) không đổi kết quả
    hs = _hs(3, 7)
    clubs = {"A": {"capacity": 10}, "B": {"capacity": 15}}
    goc = mt.de_xuat_cho_giu(hs, clubs, "Khối 10")
    hs2 = {k: dict(v, prefs=["A", "B"], rank=1, ket_qua="A") for k, v in hs.items()}
    clubs2 = {k: dict(v, so_nguyen_vong_1=99, lan_truoc=5) for k, v in clubs.items()}
    assert mt.de_xuat_cho_giu(hs2, clubs2, "Khối 10") == goc
    # (3) mã nguồn không nhắc tới nguyện vọng / kết quả
    ma = inspect.getsource(mt)
    for tu in ("preferences", "match_results", "run_history", "rank_in"):
        assert tu not in ma


# ----- co_hoi = bốc thăm thuần (so với Gale–Shapley viết riêng) -----

def _gs_boc_tham(db):
    """Student-proposing DA với thứ tự ưu tiên MỌI CLB = (số bốc thăm, mã em). Viết riêng, không qua rb.*."""
    c = sqlite3.connect(db)
    try:
        stb = {s: n for s, n in c.execute("SELECT student_id, stb_number FROM students")}
        cap = {k: n for k, n in c.execute("SELECT club_id, capacity FROM clubs")}
        pref = {}
        for s, k, r in c.execute("SELECT student_id, club_id, rank FROM preferences ORDER BY student_id, rank"):
            pref.setdefault(s, []).append(k)
    finally:
        c.close()
    khoa = lambda s: (stb[s], s)
    giu = {k: [] for k in cap}
    tiep = {s: 0 for s in pref}
    ranh = sorted(pref)
    while ranh:
        s = ranh.pop()
        if tiep[s] >= len(pref[s]):
            continue
        k = pref[s][tiep[s]]
        tiep[s] += 1
        giu[k].append(s)
        giu[k].sort(key=khoa)
        if len(giu[k]) > cap[k]:
            ranh.append(giu[k].pop())
    return {s: k for k, ds in giu.items() for s in ds}


@pytest.mark.parametrize("seed", [42, 7, 2024])
@pytest.mark.parametrize("tep", [d.BO_DU_LIEU[1][1], d.BO_DU_LIEU[2][1]], ids=["bo_sach", "TEST_0x"])
def test_co_hoi_ra_dung_thu_tu_boc_tham_thuan(tmp_path, tep, seed):
    db = d.nap_bo(str(tmp_path), tep)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": mt.rules_cua_muc_tieu("co_hoi", {"wharton": False})})
    a = api_mod.PipelineAPI(db)
    assert a.run_pipeline(seed=seed)["ok"]
    c = sqlite3.connect(db)
    try:
        assert c.execute("SELECT COUNT(DISTINCT buoi) FROM match_results").fetchone()[0] == 1
        that = {s: k for s, k in c.execute("SELECT student_id, club_id FROM match_results "
                                            "WHERE club_id IS NOT NULL")}
    finally:
        c.close()
    mong = _gs_boc_tham(db)
    assert that == mong, "co_hoi KHÁC bốc thăm thuần ở %d em" % sum(
        1 for s in set(that) | set(mong) if that.get(s) != mong.get(s))
