"""GT4-L4 — lời giải trình không bị hiểu sai (R5, R6): chỗ dành riêng (RESERVED) không hiện số "mức vào được",
một câu chú thích cố định, và giọng trung tính cho màn giáo viên. Dữ liệu MÔ PHỎNG.

Giọng `hoc_sinh` (mặc định) phải giữ NGUYÊN từng byte các câu của GT1."""

import os
import re
import shutil
import sys

import pytest

import api as api_mod
import cau_hinh_ws
import fa_ly_do
import workspace as ws

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

CLB = "CLB Bóng rổ"
DAY_DU = {"rank_in_list": 2, "cut_score": 7.5, "diem_em": 6.0}

# Chụp từ mã TRƯỚC GT4-L4 (giọng học sinh, mặc định). Không sửa các chuỗi này.
CAU_CU = {
    ("ACCEPTED", True): "Em được xếp vào CLB Bóng rổ – nguyện vọng 2 của em.",
    ("ACCEPTED", False): "Em được xếp vào CLB Bóng rổ.",
    ("HIGHER_CHOICE_ACCEPTED", True): "Em đã được xếp vào một CLB em xếp cao hơn nên CLB Bóng rổ không cần xét.",
    ("FULL_SCORE", True): "CLB Bóng rổ đã đủ chỗ với các bạn có điểm thử thách cao hơn (điểm chuẩn 7.5, em 6).",
    ("FULL_SCORE", False): "CLB Bóng rổ đã đủ chỗ với các bạn có điểm thử thách cao hơn.",
    ("FULL_LOTTERY", True): "CLB Bóng rổ đã đủ chỗ; em bằng các bạn ở mọi tiêu chí nên chỗ cuối được quyết định bằng bốc "
                            "thăm, và số bốc thăm của em chưa trúng.",
    ("FULL_GROUP", True): "CLB Bóng rổ đã đủ chỗ; các bạn thuộc nhóm ưu tiên cao hơn được xét trước.",
    ("FULL_WHARTON", True): "CLB Bóng rổ đã đủ chỗ; em bằng các bạn ở các tiêu chí trước, và các bạn có điểm quyết tâm "
                            "cao hơn được xét trước.",
    ("RESERVED", True): "CLB Bóng rổ dành một số chỗ cho nhóm được giữ chỗ nên em chưa vào được.",
    ("NOT_TESTED", True): "CLB Bóng rổ có thử thách đầu vào; em chưa có điểm nên được xét sau các bạn đã có điểm, và CLB "
                          "đã đủ chỗ.",
    ("NO_CHOICES", True): "Em chưa đăng ký nguyện vọng nào ở buổi này nên chưa được xếp CLB.",
    ("UNASSIGNED", True): "Em chưa có chỗ ở buổi này: các CLB em chọn đều đã đủ chỗ.",
    (None, True): "",
}
MA = ["ACCEPTED", "HIGHER_CHOICE_ACCEPTED", "FULL_SCORE", "FULL_LOTTERY", "FULL_GROUP", "FULL_WHARTON", "RESERVED",
      "NOT_TESTED", "NO_CHOICES", "UNASSIGNED"]
TU_EM = re.compile(r"\b[Ee]m\b")


def test_giong_hoc_sinh_mac_dinh_giu_nguyen_tung_byte():
    for (ma, day_du), mong in CAU_CU.items():
        dong = dict(DAY_DU, ma=ma) if day_du else {"ma": ma}
        assert fa_ly_do.cau_ly_do_rbda(dong, CLB) == mong, (ma, day_du)
        assert fa_ly_do.cau_ly_do_rbda(dong, CLB, giong="hoc_sinh") == mong


def test_giong_giao_vien_khong_xung_em_va_van_noi_dung_cau():
    for ma in MA:
        c = fa_ly_do.cau_ly_do_rbda(dict(DAY_DU, ma=ma), CLB, giong="giao_vien")
        assert c and not TU_EM.search(c) and "các bạn" not in c, (ma, c)
        if ma not in ("NO_CHOICES", "UNASSIGNED"):
            assert CLB in c, ma
    assert "7.5" in fa_ly_do.cau_ly_do_rbda(dict(DAY_DU, ma="FULL_SCORE"), CLB, giong="giao_vien")
    assert "bốc thăm" in fa_ly_do.cau_ly_do_rbda({"ma": "FULL_LOTTERY"}, CLB, giong="giao_vien")
    assert fa_ly_do.cau_ly_do_rbda({"ma": "XYZ"}, CLB, giong="giao_vien") == ""
    assert fa_ly_do.cau_ly_do_rbda({"ma": "ACCEPTED"}, CLB, giong="la") == CAU_CU[("ACCEPTED", False)]   # lạ -> mặc định


@pytest.fixture
def ws_sach(tmp_path):
    os.makedirs(str(tmp_path / "nguon"))
    nguon = d.nap_bo(str(tmp_path / "nguon"), d.BO_DU_LIEU[1][1])        # bộ "sách": có chỗ dành riêng
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    api = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    return api


def _tat_ca(api):
    with api._ket_noi_doc() as cur:
        hs = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
        ma = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))
    return hs, ma


def _dong_chon(du):
    return [(b, x) for b in du["buoi"] for x in b["cac_lua_chon"]]


def test_cho_danh_rieng_khong_mang_so_muc_vao_duoc(ws_sach):
    api = ws_sach
    hs, ma = _tat_ca(api)
    thay_giu_cho = 0
    for sid in hs:
        for du in (api.get_giai_trinh_hoc_sinh(sid)["data"], api.tra_cuu_hoc_sinh(sid, ma[sid])["data"]):
            co = False
            for b, x in _dong_chon(du):
                if x["ma"] == "RESERVED":
                    co = True
                    assert x["diem_chuan"] is None and x["diem_chuan_loai"] == "giu_cho", (sid, x)
            if co:
                thay_giu_cho += 1
                assert all(b["chu_thich"] == fa_ly_do.CAU_GIU_CHO for b in du["buoi"]
                           if any(x["ma"] == "RESERVED" for x in b["cac_lua_chon"]))
            else:
                assert all(b["chu_thich"] == "" for b in du["buoi"])
    assert thay_giu_cho > 0, "bộ dữ liệu thử phải có ít nhất một ca chỗ dành riêng"


def test_cau_chu_thich_la_mot_nguon_va_khong_co_so():
    assert fa_ly_do.CAU_GIU_CHO == ("Một số chỗ của CLB được giữ riêng cho nhóm theo quy định của trường; "
                                    "mức vào được chỉ áp dụng cho các chỗ còn lại.")
    assert not re.search(r"\d", fa_ly_do.CAU_GIU_CHO) and not TU_EM.search(fa_ly_do.CAU_GIU_CHO)


def test_phieu_in_o_cho_danh_rieng_va_co_chu_thich(ws_sach, tmp_path):
    api = ws_sach
    r = api.export_phieu_giai_trinh(str(tmp_path / "p.html"))
    assert r["ok"]
    html = (tmp_path / "p.html").read_text(encoding="utf-8")
    assert fa_ly_do.CAU_GIU_CHO in html and "Chỗ dành riêng" in html
    # hàng RESERVED: ô "Mức vào được" không phải số điểm
    for hang in re.findall(r"<tr[^>]*>.*?</tr>", html):
        if "dành một số chỗ cho nhóm được giữ chỗ" in hang:
            o = re.findall(r"<td>(.*?)</td>", hang)
            assert o[-2] == "Chỗ dành riêng", o
    assert html.count("Em ") > 0                                    # phiếu in giữ giọng "Em"


def test_man_giao_vien_trung_tinh_con_phieu_va_man_hoc_sinh_giu_giong_em(ws_sach):
    api = ws_sach
    hs, ma = _tat_ca(api)
    giu_em = 0
    for sid in hs:
        gv = api.get_giai_trinh_hoc_sinh(sid)["data"]
        for b in gv["buoi"]:
            for c in [b["cau_tom_tat"]] + [x["cau"] for x in b["cac_lua_chon"]]:
                assert not TU_EM.search(c), (sid, c)
        em = api.tra_cuu_hoc_sinh(sid, ma[sid])["data"]
        giu_em += sum(1 for b in em["buoi"] for x in b["cac_lua_chon"] if TU_EM.search(x["cau"]))
    assert giu_em > 0


def test_phu_de_the_ket_qua_khong_noi_mau_thuan_voi_o_tra_cuu():
    import re as _re
    nguon = open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    # UX6-L1: câu mô tả thẻ Kết quả (`kq_desc`) đã bỏ, nên không còn gì để nói mâu thuẫn với ô tra cứu.
    assert not _re.search(r"\bkq_desc:", nguon)
