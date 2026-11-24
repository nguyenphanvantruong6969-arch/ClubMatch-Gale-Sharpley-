"""CB1-L1 — bộ dựng nội dung "Văn bản phương án xếp" (`phuong_an_xep.py`): hàm THUẦN, dữ liệu mô phỏng.

Kiểm: dấu vân tay luật ổn định / đổi khi đổi luật / không đọc khoá ngoài luật xếp, BẢN DỰ KIẾN không bao giờ có
hạt giống, BẢN CHỐT chỉ có hạt giống khi tick VÀ đã khoá, cảnh báo đổi sau chốt, năm mốc quy trình, danh sách
trắng khoá, tiếng Anh dùng cùng cấu trúc.
"""

import copy
import json

import phuong_an_xep as pa
import tieu_chi
from rbda_priority_pipeline import LUAT_XEP_MAC_DINH

RULES = dict(LUAT_XEP_MAC_DINH)
CFG = {"rules": dict(RULES, priority="score", fa_khieu_nai=True, fa_khieu_nai_so_ngay=3),
       "muc_tieu": {"id": "nang_luc", "nhom": None, "truoc": {"x": 1}}}
HAT = {"seed": 424242, "locked_at": "2026-11-20 08:00:00"}
CHOT = {"nguoi": "admin", "vai": "quan_tri", "luc": "2026-11-18 09:00:00", "bam_luat": pa.bam_luat(CFG),
        "muc_tieu": {"id": "nang_luc", "nhom": None}}


def _moc(**kw):
    m = {"chot": {"nguoi": "admin", "luc": "2026-11-18 09:00:00"},
         "dvt": {"dau_van_tay": "ab" * 32, "luc": "2026-11-19 10:00:00"},
         "khoa": {"is_locked": 1, "locked_at": "2026-11-20 08:00:00"},
         "run": {"run_at": "2026-11-20 08:05:00"},
         "rules": CFG["rules"], "lan_xep_khop": True}
    m.update(kw)
    return m


def _nd(ban="chot", **kw):
    a = dict(ban=ban, tieu_chi=tieu_chi.mo_ta_tieu_chi(CFG["rules"], "vi"),
             muc_tieu={"id": "nang_luc", "nhom": None}, moc=_moc(), chot=CHOT,
             bam_hien_tai=pa.bam_luat(CFG), in_hat_giong=False, hat_giong=HAT)
    a.update(kw)
    return pa.dung_noi_dung(**a)


def test_bam_luat_on_dinh_va_nhay_theo_luat():
    assert pa.bam_luat(CFG) == pa.bam_luat(copy.deepcopy(CFG))
    assert len(pa.bam_luat(CFG)) == 64
    c2 = copy.deepcopy(CFG)
    c2["rules"]["priority"] = "tier"
    assert pa.bam_luat(c2) != pa.bam_luat(CFG)
    c3 = copy.deepcopy(CFG)
    c3["muc_tieu"] = {"id": "co_hoi", "nhom": None}
    assert pa.bam_luat(c3) != pa.bam_luat(CFG)


def test_bam_luat_bo_qua_khoa_ngoai_luat_va_truoc():
    c2 = copy.deepcopy(CFG)
    c2["name"] = "Tên khác"
    c2["muc_tieu"]["truoc"] = {"y": 2}          # `truoc` chỉ phục vụ Hoàn tác, không phải luật
    c2["labels"] = {"person": "nhân viên"}
    assert pa.bam_luat(c2) == pa.bam_luat(CFG)


def test_bam_luat_khong_co_muc_tieu():
    c = {"rules": CFG["rules"]}
    assert len(pa.bam_luat(c)) == 64


def test_du_kien_khong_bao_gio_co_hat_giong():
    for in_hat in (False, True):
        nd = _nd("du_kien", in_hat_giong=in_hat)
        assert "hat_giong" not in nd
        assert str(HAT["seed"]) not in json.dumps(nd, ensure_ascii=False)


def test_chot_mac_dinh_khong_hat_giong_chi_khi_tick_va_da_khoa():
    assert "hat_giong" not in _nd("chot")
    assert _nd("chot", in_hat_giong=True)["hat_giong"]["seed"] == 424242
    assert "hat_giong" not in _nd("chot", in_hat_giong=True, hat_giong=None)
    assert "hat_giong" not in _nd("chot", in_hat_giong=True, hat_giong={"seed": None, "locked_at": None})


def test_dau_van_tay_chi_o_ban_chot():
    assert _nd("chot")["dau_van_tay"] == "ab" * 32
    assert "dau_van_tay" not in _nd("du_kien")
    assert "ab" * 32 not in json.dumps(_nd("du_kien"), ensure_ascii=False)


def test_ban_chot_co_nguoi_luc_bam_va_gio_khoa():
    nd = _nd("chot")
    assert nd["chot"]["nguoi"] == "admin" and nd["chot"]["luc"] == "2026-11-18 09:00:00"
    assert nd["chot"]["bam_luat"] == CHOT["bam_luat"]
    assert "chot" not in _nd("du_kien")


def test_canh_bao_doi_sau_chot():
    assert _nd("chot")["canh_bao"] == []
    nd = _nd("chot", bam_hien_tai="0" * 64)
    assert "doi_sau_chot" in [c["ma"] for c in nd["canh_bao"]]
    assert all(c["chu"] for c in nd["canh_bao"])
    assert "doi_sau_chot" in [c["ma"] for c in _nd("du_kien", bam_hien_tai="0" * 64)["canh_bao"]]


def test_canh_bao_lan_xep_khong_dung_phuong_an_da_chot():
    nd = _nd("chot", moc=_moc(lan_xep_khop=False))
    assert "xep_khac_chot" in [c["ma"] for c in nd["canh_bao"]]
    assert _nd("chot", moc=_moc(lan_xep_khop=None))["canh_bao"] == []      # không so sánh được: bỏ cảnh báo


def test_khong_chot_thi_khong_canh_bao_doi():
    nd = _nd("du_kien", chot=None, bam_hien_tai="0" * 64, moc=_moc(chot=None))
    assert nd["canh_bao"] == []


def test_nam_moc_quy_trinh():
    qt = _nd("chot")["quy_trinh"]
    assert [m["ma"] for m in qt] == ["cong_bo", "chot_du_lieu", "boc_hat_giong", "chay_xep", "cong_bo_ket_qua"]
    assert [m["da"] for m in qt] == [True, True, True, True, False]
    assert qt[0]["luc"] == "2026-11-18 09:00:00" and qt[2]["luc"] == "2026-11-20 08:00:00"
    assert all(m["chu"] for m in qt)


def test_moc_chua_lam_la_chua():
    qt = pa.trang_thai_quy_trinh({"chot": None, "dvt": None, "khoa": None, "run": None, "rules": CFG["rules"]})
    assert [m["da"] for m in qt] == [False] * 5
    assert qt[1]["chu"].startswith("Chưa") or "chưa chốt dữ liệu" in qt[1]["chu"]


def test_khoa_khong_khoa_la_chua_boc():
    qt = pa.trang_thai_quy_trinh({"chot": None, "dvt": None, "khoa": {"is_locked": 0, "locked_at": None},
                                  "run": None, "rules": {}})
    assert qt[2]["da"] is False


def test_han_khieu_nai_theo_luat():
    qt = pa.trang_thai_quy_trinh(_moc())
    assert "3 ngày" in qt[4]["chu"]
    qt2 = pa.trang_thai_quy_trinh(_moc(rules=dict(CFG["rules"], fa_khieu_nai=False)))
    assert "ngày" not in qt2[4]["chu"]


def test_dung_chung_buoc_le_voi_bien_ban():
    import fa_bien_ban
    assert _nd("chot")["buoc_le"] == list(fa_bien_ban.THU_TU_LE)


def test_ghi_chu_va_tieu_chi_dung_nguon_tieu_chi():
    nd = _nd("chot")
    assert nd["ghi_chu"] == tieu_chi.GHI_CHU["vi"]
    chu = [d["chu"] for d in nd["tieu_chi"]]
    assert chu == [d["chu"] for d in tieu_chi.mo_ta_tieu_chi(CFG["rules"], "vi")]


def test_danh_sach_trang_khoa():
    for ban in ("du_kien", "chot"):
        nd = _nd(ban, in_hat_giong=True)
        assert set(nd) <= {"ban", "lang", "tieu_de", "muc_tieu", "tieu_chi", "ghi_chu", "quy_trinh", "chot",
                           "dau_van_tay", "hat_giong", "canh_bao", "buoc_le", "cau"}
    # tên học sinh / mã đưa vào ô tự do KHÔNG đi vào đầu ra: bộ dựng không nhận chúng
    tho = json.dumps(_nd("chot", in_hat_giong=True), ensure_ascii=False)
    for cam in ("student_id", "stb_number", "score"):
        assert cam not in tho


def test_tieng_anh_cung_cau_truc():
    vi = _nd("chot")
    en = _nd("chot", lang="en", tieu_chi=tieu_chi.mo_ta_tieu_chi(CFG["rules"], "en"))
    assert en["lang"] == "en" and set(en) == set(vi)
    assert en["ghi_chu"] == tieu_chi.GHI_CHU["en"]
    assert [m["ma"] for m in en["quy_trinh"]] == [m["ma"] for m in vi["quy_trinh"]]
    assert en["tieu_de"] != vi["tieu_de"]


def test_ban_la_bi_tu_choi():
    import pytest
    with pytest.raises(ValueError):
        _nd("khac")


def test_muc_tieu_nhom_hien_ten_nhom():
    nd = _nd("chot", muc_tieu={"id": "danh_cho", "nhom": "Hoàn cảnh khó khăn"})
    assert "Hoàn cảnh khó khăn" in nd["muc_tieu"]["cau"]
    assert _nd("chot", muc_tieu=None)["muc_tieu"] is None
