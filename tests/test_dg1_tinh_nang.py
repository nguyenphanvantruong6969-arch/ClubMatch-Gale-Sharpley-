"""DG1 nhóm G: lưới 2×2 «suất dự trữ × điểm quyết tâm» và «huy chương» (du_lieu_test/danh_gia/do_tinh_nang.py)."""

import os
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_GOC, "du_lieu_test", "danh_gia"))
sys.path.insert(0, os.path.join(_GOC, "du_lieu_test"))

import do_danh_gia as dg  # noqa: E402
import do_tinh_nang as tn  # noqa: E402
import _sinh as sinh  # noqa: E402
import rbda_priority_pipeline as loi  # noqa: E402

TS = {"n_hs": 120, "n_clb": 10, "alpha": 0.5, "rho": 0.7, "kappa": 1.1}


def test_chia_diem_dung_100_moi_kieu():
    for n in range(1, 7):
        ds = ["c%d" % i for i in range(n)]
        for k in tn.KIEU_CHIA:
            r = tn._chia(ds, k)
            assert sum(r.values()) == 100 and set(r) == set(ds) and all(isinstance(v, int) and v >= 0 for v in r.values())
    assert tn._chia(["a", "b", "c"], "giam") == {"a": 51, "b": 33, "c": 16}     # 3:2:1 → 50,33,16 dư 1 vào đầu
    assert tn._chia(["a", "b", "c"], "deu") == {"a": 34, "b": 33, "c": 33}


def test_ho_so_diem_quyet_tam_hop_le_theo_phan_mem():
    t = sinh.sinh_truong(seed=101, **TS)
    kb = dg.dung_kich_ban(t)
    w1, w2, kieu = tn.sinh_diem_quyet_tam(t, 101)
    thi = {s: {c for c in t["preferences"][s] if s in t["tested_scores"].get(c, {})} for s in t["preferences"]}
    assert loi.kiem_ho_so_wharton(kb["prefs"], thi, w1, w2, kb["clubs"]) == []
    assert tn.diem_hieu_luc(t, kb, w1, w2)[1] == []
    assert set(kieu.values()) <= set(tn.KIEU_CHIA)
    assert tn.sinh_diem_quyet_tam(t, 101)[0] == w1          # tất định theo seed


def test_luoi_2x2_cung_du_lieu_o_goc_khop_chay_mac_dinh():
    r = tn.do_luoi_2x2(TS, [101, 102], [1, 2])
    goc = dg.do_cau_hinh(TS, [101, 102], [1, 2])
    assert r["kiem_ho_so"] == {"loi_ho_so": 0, "thong_bao_hieu_luc": 0}
    for o in tn.CAC_O:
        assert r["o"][o]["a.cap_chan"]["tb"] == 0 and r["o"][o]["a.ngoai_danh_sach"]["tb"] == 0
    # ô «gốc» (tắt cả hai) = chạy mặc định nhưng suất dự trữ tắt: không dự trữ cung cấp / dùng
    assert r["o"]["goc"]["c.du_tru_cung_cap"]["tb"] == 0 and r["o"]["goc"]["c.du_tru_da_dung"]["tb"] == 0
    assert r["o"]["du_tru"]["c.du_tru_cung_cap"]["tb"] == goc["chi_so"]["c.du_tru_cung_cap"]["tb"]
    assert r["o"]["du_tru"]["a.pct_nv1_tat_ca"]["tb"] == goc["chi_so"]["a.pct_nv1_tat_ca"]["tb"]   # ô «du_tru» = mặc định
    # điểm quyết tâm chỉ phá hoà → số em có chỗ không giảm mạnh; chính sách chỉ đổi người, không đổi số CLB
    assert r["o"]["wharton"]["pct_dat_clb_diem_cao"]["tb"] >= r["o"]["goc"]["pct_dat_clb_diem_cao"]["tb"]


def test_huy_chuong_cac_ty_le_cong_100():
    r = tn.do_huy_chuong(120, [101], [1, 2])
    assert abs(sum(v["tb"] for v in r["ly_do_fa_pt_dong"].values()) - 100.0) < 1e-3
    assert sum(r["theo_hanh_vi"][h]["n_hs_tb"]["tb"] for h in tn.HANH_VI) == 120
    for h in tn.HANH_VI:
        for che in ("cu", "fa"):
            d = r["theo_hanh_vi"][h][che]
            assert 0 <= d["pt_nv1_that"]["tb"] <= d["pt_top2_that"]["tb"] <= 100
        c = r["theo_hanh_vi"][h]["doi_clb_cu_sang_fa"]
        assert c["doi_clb"]["tb"] >= c["tot_hon"]["tb"] + c["xau_hon"]["tb"] - 1e-3
