"""DG1-L2/L3: bộ chạy `do_danh_gia.py` — lưới seed tách bạch, 0 cặp phá vỡ, cận trên, biến thể đổi MỘT thứ, đối chiếu số liệu đã kiểm chứng."""

import os
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_GOC, "du_lieu_test", "danh_gia"))
sys.path.insert(0, os.path.join(_GOC, "du_lieu_test"))

import do_danh_gia as dg  # noqa: E402
import _sinh as sinh  # noqa: E402

TS = {"n_hs": 120, "n_clb": 10, "alpha": 0.5, "rho": 0.7, "kappa": 1.1}


def test_doi_chieu_so_lieu_da_kiem_chung():
    r = dg.phan_doi_chieu()
    assert r["pipeline"] == {"duoc_xep": 108, "nv1": 64} and r["n_hs"] == 120
    assert r["khop_tung_dong_match_results"] and r["cap_chan"] == 0 and r["dat"]


def test_rbda_khong_cap_chan_khong_ngoai_danh_sach_va_duoi_can_tren():
    for sdl in (101, 102):
        t = sinh.sinh_truong(seed=sdl, **TS)
        kb = dg.dung_kich_ban(t)
        for sbt in (1, 2, 3):
            ci, kq, _dt = dg.chay_mot(kb, sbt, t)
            assert ci["a"]["cap_chan"] == 0 and ci["a"]["ngoai_danh_sach"] == 0
            assert ci["a"]["n_da_xep"] <= ci["b"]["can_tren_ghep_cuc_dai"] <= ci["a"]["n_hs"]
            assert ci["b"]["n_chua_xep"] == sum(ci["b"]["nguyen_nhan"].values())


def test_hai_nguon_ngau_nhien_tach_bach():
    a = dg.do_cau_hinh(TS, [101], [1, 2])
    b = dg.do_cau_hinh(TS, [101], [1, 2])
    assert a["chi_so"] == b["chi_so"]                         # tái lập từng số
    # cùng trường, khác lần bốc thăm: dữ liệu giống hệt, kết quả (có thể) khác
    t = sinh.sinh_truong(seed=101, **TS)
    assert t == sinh.sinh_truong(seed=101, **TS)
    kb = dg.dung_kich_ban(t)
    x1 = dg.chay_mot(kb, 1, t)[1].assignment
    x2 = dg.chay_mot(kb, 2, t)[1].assignment
    assert x1 != x2 and a["seed_du_lieu"] == [101] and a["seed_boc_tham"] == [1, 2]
    # khác trường: dữ liệu khác
    assert sinh.sinh_truong(seed=102, **TS)["preferences"] != t["preferences"]


def test_tong_hop_ktc_t():
    r = dg.tong_hop([1.0, 2.0, 3.0])
    assert r["tb"] == 2.0 and r["n"] == 3
    # t_{0,975; 2} = 4,303 → nửa độ rộng = 4,303 × 1/√3 = 2,4843
    assert abs(r["ktc95"][1] - 2.0 - 2.4843) < 1e-3
    assert dg.tong_hop([5.0])["ktc95"] is None and dg.tong_hop([None])["tb"] is None


def test_bien_the_doi_mot_thu_va_churn_cong_dung():
    goc = dg.do_cau_hinh(TS, [101], [1, 2])
    ass = goc["_assign"]
    ten = {b["ten"]: b for b in dg.BIEN_THE}
    # max_choices = 10 ≥ độ dài danh sách mô phỏng → GIỐNG HỆT mặc định
    x = dg.do_cau_hinh(TS, [101], [1, 2], bien_the=ten["toi_da_10_nv"], doi_chieu=ass)
    assert x["churn"]["doi_clb"]["tb"] == 0
    # chỉ tiêu +20 %: không ai xấu đi (đơn điệu); chỉ tiêu −20 %: không ai tốt lên
    cao = dg.do_cau_hinh(TS, [101], [1, 2], bien_the=ten["chi_tieu_+20"], doi_chieu=ass)
    thap = dg.do_cau_hinh(TS, [101], [1, 2], bien_the=ten["chi_tieu_-20"], doi_chieu=ass)
    assert cao["churn"]["xau_hon"]["tb"] == 0 and cao["churn"]["tot_hon"]["tb"] > 0
    assert thap["churn"]["tot_hon"]["tb"] == 0 and thap["churn"]["xau_hon"]["tb"] > 0
    for r in (cao, thap, x):
        c = r["churn"]
        assert abs(c["doi_clb"]["tb"] - (c["tot_hon"]["tb"] + c["xau_hon"]["tb"] + c["doi_cung_hang"]["tb"])) < 1e-6


def test_churn_ham_thuan():
    prefs = {"a": ["X", "Y"], "b": ["X", "Y"], "c": ["X"], "d": ["X"]}
    cu = {"a": "X", "b": "Y", "c": None, "d": "X"}
    moi = {"a": "Y", "b": "X", "c": "X", "d": "X"}
    assert dg.churn(cu, moi, prefs) == {"doi_clb": 3, "tot_hon": 2, "xau_hon": 1, "doi_cung_hang": 0}


def test_dem_cap_chan_cua_co_che_on_dinh_bang_0_con_boston_khac_0():
    import rbda_priority_pipeline as loi
    import co_che_doi_chung as cc
    t = sinh.sinh_truong(seed=101, **TS)
    kb = dg.dung_kich_ban(t)
    st, clubs, sc, app, prefs = kb["students"], kb["clubs"], kb["scores"], kb["app"], kb["prefs"]
    elig = loi.default_reserve_eligible_fn(st, clubs)
    stb = loi.generate_stb_lottery(sorted(st), 1)
    base = cc.tinh_base_rank(clubs, sc, app, stb)
    chon = cc._ham_chon(clubs, base, elig)
    kq = loi.run_rbda(st, clubs, sc, app, prefs, stb, elig)
    assert dg.dem_cap_chan(dict(kq.assignment), clubs, prefs, base, chon) == 0
    assert dg.dem_cap_chan(cc.co_che_boston(st, clubs, sc, app, prefs, stb, elig), clubs, prefs, base, chon) > 0
