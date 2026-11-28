"""DG1-L2/L3: bộ chạy `do_danh_gia.py` — lưới seed tách bạch, 0 cặp phá vỡ, cận trên, biến thể đổi MỘT thứ, đối chiếu số liệu đã kiểm chứng."""

import os
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_GOC, "du_lieu_test", "danh_gia"))
sys.path.insert(0, os.path.join(_GOC, "du_lieu_test"))

import do_danh_gia as dg  # noqa: E402
import rbda_priority_pipeline as loi  # noqa: E402
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


def test_gop_khoa_nhom_vang_mat_khong_gay_loi():
    # Một lần chạy không có em nào ở Tầng 2 → khoá của nhóm đó chỉ có ở lần khác; gộp phải theo HỢP khoá, trung bình trên giá trị CÓ MẶT.
    a = {"x": 1.0, "nhom.tang_2.n": 10.0}
    b = {"x": 3.0}
    assert dg.hop_khoa([a, b]) == ["x", "nhom.tang_2.n"]
    assert dg.tb_co([a.get("nhom.tang_2.n"), b.get("nhom.tang_2.n")]) == 10.0
    assert dg.tb_co([None, None]) is None and dg.sd_co([2.0, None]) == 0.0
    assert dg.tb_co([a["x"], b["x"]]) == 2.0


def test_do_cau_hinh_chiu_duoc_nhom_vang_mat(monkeypatch):
    goc = dg.chay_mot
    dem = {"n": 0}

    def gia(kb, sbt, truong):
        ci, kq, dt = goc(kb, sbt, truong)
        dem["n"] += 1
        if dem["n"] % 2 == 0:                       # lần chạy chẵn: bỏ nhóm «tang_2»
            ci["a"]["theo_nhom"]["tang"].pop("tang_2", None)
        return ci, kq, dt
    monkeypatch.setattr(dg, "chay_mot", gia)
    r = dg.do_cau_hinh(TS, [101, 102], [1, 2])
    assert "a.theo_nhom.tang.tang_2.n" in r["chi_so"] and r["chi_so"]["a.theo_nhom.tang.tang_2.n"]["tb"] is not None


def test_bo_co_san_nhieu_buoi_khop_run_pipeline_that(tmp_path):
    """Bộ nhiều buổi (bo_kich_tran, 3 buổi) chạy qua `chay_tuan` ra ĐÚNG từng dòng match_results của `run_pipeline` thật (seed 42)."""
    import sqlite3
    from api import PipelineAPI
    from do_anh_huong_seed import nap_bo
    files = next(b for b in dg.CO_SAN if b[0] == "bo_kich_tran")[2]
    db = nap_bo(str(tmp_path), files)
    assert PipelineAPI(db).run_pipeline(seed=42)["ok"]
    c = sqlite3.connect(db)
    thuc = {(s, b): cid for s, b, cid in c.execute("SELECT student_id, buoi, club_id FROM match_results")}
    c.close()
    st, clubs, sc, app, prefs, _ = loi.load_from_sqlite(db)
    _tb, _hs, kt = dg.chay_tuan(st, clubs, sc, app, prefs, 42, {"du_tru": {s: "khong" for s in st}, "khoi": {s: "?" for s in st}})
    mem = {(s, b): kt.per_buoi[b].assignment[s] for b in kt.ds_buoi for s in kt.per_buoi[b].assignment}
    assert mem == thuc and len(thuc) == 150 * 3
    assert all(_tb[b]["a.cap_chan"] == 0 for b in _tb)


def test_chay_du_lieu_co_san_nhieu_buoi_co_theo_buoi_va_theo_hoc_sinh():
    ten, loai, files = next(b for b in dg.CO_SAN if b[0] == "bo_can_bang")
    r = dg.chay_du_lieu_co_san(ten, dg.nap_co_san(loai, files), [1, 2])
    assert r["so_buoi"] == 6 and "chi_so" not in r and len(r["theo_buoi"]) == 6
    assert all(v["a.cap_chan"]["tb"] == 0 for v in r["theo_buoi"].values())
    assert 0 < r["theo_hoc_sinh"]["so_buoi_co_cho_tb"]["tb"] <= 6
