"""GT2-L1 — tiêu chí xếp bằng lời thường + danh sách giá trị cho phép (tieu_chi.py, get_tieu_chi).

Dữ liệu trong test là MÔ PHỎNG. Hai việc chính:
  * mô tả khớp luật xếp HIỆU LỰC (`luat_xep_hieu_luc`) với MỌI tổ hợp được phép;
  * tập khoá luật bị khoá chặt: thêm tiêu chí mới phải sửa test này có chủ ý.
"""

import copy
import itertools
import json
import re

import pytest

import cau_hinh_ws as ch
import tieu_chi as tc
from rbda_priority_pipeline import LUAT_XEP_MAC_DINH, luat_xep_hieu_luc, nhom_xep_cung

# Khoá luật KHÔNG thuộc luật xếp (trần nhập liệu và các cờ FA sau xếp). Viết tay ở đây có chủ ý:
# thêm một khoá luật mới mà không sửa danh sách này thì test đỏ — tiêu chí mới không lọt lén được.
KHOA_NGOAI_LUAT_XEP = {
    "max_choices", "max_tests", "fa_diem_danh", "fa_khieu_nai", "fa_khieu_nai_so_ngay",
    "fa_vong_2", "fa_phan_hoi", "fa_duong", "fa_vong_doi_cho",
}

DAU_VIET = re.compile(
    "[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)

NHOM = ["Khối 12", "Khối 11"]


def _to_hop():
    for pr, tm, ss, tiers, wh, fa in itertools.product(
            ("score", "score+tier", "tier"), ("reserve", "strict"), ("per_slot", "per_person"),
            ([], NHOM), (False, True), (False, True)):
        yield {"priority": pr, "tier_mode": tm, "score_scope": ss, "tiers": list(tiers),
               "wharton": wh, "fa_daa": fa}


def _ma(mo_ta, nhom):
    return [m["ma"] for m in mo_ta if m["nhom"] == nhom]


# ---------------------------------------------------------------- khoá chặt tập khoá

def test_tap_khoa_cho_phep_bang_luat_xep_mac_dinh():
    assert set(tc.cac_lua_chon_hop_le()) == set(LUAT_XEP_MAC_DINH)


def test_moi_khoa_luat_cua_workspace_la_luat_xep_hoac_nam_trong_danh_sach_ngoai():
    khoa_ws = set(ch.MAC_DINH_TRUONG_HOC["rules"])
    assert khoa_ws == set(LUAT_XEP_MAC_DINH) | KHOA_NGOAI_LUAT_XEP
    assert tc.KHOA_NGOAI_LUAT_XEP == KHOA_NGOAI_LUAT_XEP


def test_lua_chon_khop_hang_so_cua_cau_hinh_ws():
    lc = tc.cac_lua_chon_hop_le()
    assert tuple(lc["priority"]["gia_tri"]) == ch.UU_TIEN
    assert tuple(lc["tier_mode"]["gia_tri"]) == ch.CHE_DO_NHOM
    assert tuple(lc["score_scope"]["gia_tri"]) == ch.PHAM_VI_DIEM
    assert lc["wharton"]["gia_tri"] == [True, False]
    assert lc["fa_daa"]["gia_tri"] == [True, False]
    assert lc["tiers"]["kieu"] == "danh_sach"
    # mỗi lựa chọn có nhãn song ngữ, tiếng Việt có dấu
    for khoa in ("priority", "tier_mode", "score_scope"):
        for gt in lc[khoa]["gia_tri"]:
            nhan = lc[khoa]["nhan"][gt]
            assert nhan["vi"] and nhan["en"]
            assert not DAU_VIET.search(nhan["en"])


def test_cau_hinh_tu_choi_khoa_la_va_gia_tri_la():
    with pytest.raises(ValueError):
        ch.chuan_hoa({"rules": {"trong_so": 3}})
    with pytest.raises(ValueError):
        ch.chuan_hoa({"rules": {"diem_hoan_canh": True}})
    for khoa, xau in (("priority", "weighted"), ("tier_mode", "soft"), ("score_scope", "global")):
        with pytest.raises(ValueError):
            ch.chuan_hoa({"rules": {khoa: xau}})
    for khoa in ("wharton", "fa_daa"):
        with pytest.raises(ValueError):
            ch.chuan_hoa({"rules": {khoa: "yes"}})


def test_moi_gia_tri_cho_phep_duoc_cau_hinh_nhan():
    for khoa, mo_ta in tc.cac_lua_chon_hop_le().items():
        if mo_ta["kieu"] != "chon":
            continue
        for gt in mo_ta["gia_tri"]:
            ch.chuan_hoa({"rules": {khoa: gt, "wharton": False}})


# ---------------------------------------------------------------- mô tả đúng luật hiệu lực

@pytest.mark.parametrize("rules", list(_to_hop()))
def test_mo_ta_khop_luat_hieu_luc_moi_to_hop(rules):
    luat = luat_xep_hieu_luc(rules)
    mo_ta = tc.mo_ta_tieu_chi(rules)
    t1, t2 = _ma(mo_ta, "tang_1"), _ma(mo_ta, "tang_2")
    cung = nhom_xep_cung(luat)
    co_diem = luat["priority"] != "tier"
    wh_dung = rules["wharton"] and luat["priority"] in ("score", "score+tier") \
        and luat["score_scope"] == "per_slot"

    # tầng 2 luôn kết thúc bằng số bốc thăm; tầng 1 chỉ có khi có chấm điểm
    assert t2 and t2[-1] == "boc_tham"
    assert (t1 != []) == co_diem
    if co_diem:
        assert t1[-1] == "boc_tham"
        assert ("diem_ca_nhan" in t1) == (luat["score_scope"] == "per_person")
        assert ("diem_clb" in t1) == (luat["score_scope"] == "per_slot")
        assert t1[0] == ("nhom_cung" if cung else ("diem_ca_nhan" if luat["score_scope"] == "per_person" else "diem_clb"))
    assert ("nhom_cung" in t2) == cung
    assert ("du_tru" in t1) == (co_diem and not cung)
    assert ("du_tru" in t2) == (not cung)
    assert ("quyet_tam" in t2) == wh_dung
    assert ("quyet_tam" in t1) == (wh_dung and co_diem)
    # thứ tự trong dòng: số 1..n liên tục
    for nhom in ("tang_1", "tang_2"):
        so = [m["thu_tu"] for m in mo_ta if m["nhom"] == nhom]
        assert so == list(range(1, len(so) + 1))
    # chữ: có tiếng Việt, tiếng Anh không dấu, không lộ mã nội bộ
    for lang in ("vi", "en"):
        for m in tc.mo_ta_tieu_chi(rules, lang):
            assert m["chu"].strip()
            assert not re.search(r"\b(GT\d|L\d|C3|A1|Z7)\b", m["chu"])
    for m in tc.mo_ta_tieu_chi(rules, "en"):
        chu = m["chu"].replace(", ".join(NHOM), "")        # tên nhóm là dữ liệu của trường
        assert not DAU_VIET.search(chu), m


def test_mo_ta_ba_truong_hop_mau():
    # mặc định trường học: điểm -> suất giữ riêng -> bốc thăm
    mac_dinh = tc.mo_ta_tieu_chi(dict(LUAT_XEP_MAC_DINH))
    assert _ma(mac_dinh, "tang_1") == ["diem_clb", "du_tru", "boc_tham"]
    assert _ma(mac_dinh, "tang_2") == ["du_tru", "boc_tham"]
    cau1 = [m["chu"] for m in mac_dinh if m["nhom"] == "tang_1"]
    assert "Điểm bài thi của CLB" in cau1[0] and "cao trước" in cau1[0]
    assert "Nhóm ưu tiên" in cau1[1] and "giữ suất riêng" in cau1[1]
    assert "bốc thăm" in cau1[2]
    # nhóm cứng: nhóm đứng trước điểm, bỏ suất giữ riêng; danh sách nhóm hiện trong chữ
    cung = tc.mo_ta_tieu_chi({"priority": "score+tier", "tier_mode": "strict", "tiers": NHOM})
    assert _ma(cung, "tang_1") == ["nhom_cung", "diem_clb", "boc_tham"]
    assert _ma(cung, "tang_2") == ["nhom_cung", "boc_tham"]
    assert "Khối 12" in [m for m in cung if m["nhom"] == "tang_1"][0]["chu"]
    # chỉ nhóm: không có điểm thi
    chi_nhom = tc.mo_ta_tieu_chi({"priority": "tier", "tiers": NHOM})
    assert _ma(chi_nhom, "tang_1") == []
    assert _ma(chi_nhom, "tang_2") == ["nhom_cung", "boc_tham"]
    # điểm quyết tâm: đứng ngay trước bốc thăm
    wh = tc.mo_ta_tieu_chi({"wharton": True})
    assert _ma(wh, "tang_1") == ["diem_clb", "du_tru", "quyet_tam", "boc_tham"]
    assert _ma(wh, "tang_2") == ["du_tru", "quyet_tam", "boc_tham"]


def test_khoa_khong_dung_va_ly_do():
    # tiers có tên nhưng nhóm không cứng: vô tác dụng, phải nói rõ
    kd = [m for m in tc.mo_ta_tieu_chi({"priority": "score", "tiers": NHOM})
          if m["nhom"] == "khong_dung"]
    assert [m["khoa"] for m in kd] == ["tiers"]
    assert kd[0]["chu"].strip()
    # priority tier: điểm bài thi và phạm vi điểm không dùng
    kd2 = {m["khoa"] for m in tc.mo_ta_tieu_chi({"priority": "tier", "tiers": NHOM})
           if m["nhom"] == "khong_dung"}
    assert {"score_scope"} <= kd2
    # wharton bật nhưng không đi cùng điểm theo từng CLB: không dùng
    kd3 = {m["khoa"] for m in tc.mo_ta_tieu_chi({"priority": "tier", "wharton": True})
           if m["nhom"] == "khong_dung"}
    assert "wharton" in kd3
    # không có gì vô tác dụng: danh sách rỗng
    assert not [m for m in tc.mo_ta_tieu_chi(dict(LUAT_XEP_MAC_DINH)) if m["nhom"] == "khong_dung"]


def test_ghi_chu_bat_buoc_va_khong_doi_dau_vao():
    for lang, mau in (("vi", "Phần mềm không dùng thứ hạng nguyện vọng"),
                      ("en", "does not use")):
        assert mau in tc.GHI_CHU[lang]
    rules = {"priority": "tier", "tiers": list(NHOM)}
    truoc = copy.deepcopy(rules)
    tc.mo_ta_tieu_chi(rules)
    assert rules == truoc
    # thiếu khoá thì lấy mặc định; None cũng được
    assert tc.mo_ta_tieu_chi(None) == tc.mo_ta_tieu_chi({})


# ---------------------------------------------------------------- API

def test_get_tieu_chi_mac_dinh(api):
    res = api.get_tieu_chi()
    assert res["ok"], res
    d = res["data"]
    assert set(d) >= {"mo_ta", "lua_chon", "ghi_chu", "luat"}
    assert d["luat"]["priority"] == "score"
    assert _ma(d["mo_ta"], "tang_1")[0] == "diem_clb"
    assert "Phần mềm không dùng thứ hạng nguyện vọng" in d["ghi_chu"]["vi"]
    assert set(d["lua_chon"]) == set(LUAT_XEP_MAC_DINH)
    json.dumps(d)                                   # gửi được qua cầu pywebview


def test_get_tieu_chi_theo_luat_da_luu(api):
    cfg = ch.chuan_hoa({"rules": {"priority": "score+tier", "tier_mode": "strict",
                                  "tiers": NHOM, "wharton": False}})
    ch.ghi_cau_hinh(api.db_path, cfg)
    d = api.get_tieu_chi()["data"]
    assert _ma(d["mo_ta"], "tang_1") == ["nhom_cung", "diem_clb", "boc_tham"]
    assert d["luat"]["tiers"] == NHOM


def test_get_tieu_chi_chi_doc_khong_ghi_gi(api):
    import sqlite3
    conn = sqlite3.connect(api.db_path)
    truoc = conn.execute("SELECT count(*) FROM run_history").fetchone()[0]
    conn.close()
    api.get_tieu_chi()
    conn = sqlite3.connect(api.db_path)
    assert conn.execute("SELECT count(*) FROM run_history").fetchone()[0] == truoc
    conn.close()
