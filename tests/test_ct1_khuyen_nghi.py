"""CT1-L1 — `chi_tieu_ct1.py` (thuần hàm): chỉ số CLB, luật đề xuất chỉ tiêu, ghép bước chuyển chỗ, kiểm bước tự chọn.

Dữ liệu MÔ PHỎNG (bộ TEST 120 em / 10 CLB / 130 chỗ; số `nv1`, `chua_dap` lấy từ lần xếp khoá seed 42 trong
`du_lieu_test/ct1_mo_phong/`). Kiểm: tổng chỗ giữ nguyên; kẹp ±tran và tối thiểu; không tăng khi không có em
"muốn vào mà chưa được"; CLB tự do bị loại; kết quả không phụ thuộc thứ tự dict; các bước chuyển trung hoà tổng và
phủ đủ mọi chênh lệch; `kiem_buoc_tu_chon` từ chối bước sai.
"""

import random

import pytest

import chi_tieu_ct1 as ct


def _cs(cap, nv1, chua_dap=0, buoi="b", loai_tru=False, reserve=0):
    return {"cap": cap, "nv1": nv1, "chua_dap": chua_dap, "buoi": buoi, "loai_tru": loai_tru,
            "reserve_capacity": reserve}


# Bộ TEST (130 chỗ, 120 em): cap, nv1, chua_dap (em xếp CLB này cao hơn CLB đang được nhận).
TEST = {
    "clb_bongda": _cs(20, 25, 22), "clb_tienganh": _cs(16, 30, 29), "clb_tinhoc": _cs(12, 25, 29),
    "clb_mythuat": _cs(12, 19, 18), "clb_bongro": _cs(18, 7), "clb_amnhac": _cs(14, 6),
    "clb_tinhnguyen": _cs(12, 3), "clb_vanhoc": _cs(10, 2), "clb_robotics": _cs(8, 2),
    "clb_khoahoc": _cs(8, 1),
}


# ----- chỉ số CLB -----

def test_chi_so_clb_tinh_tay():
    # 4 em, một buổi: A ưu tiên a>b>c, B: a>c, C: b>a, D: c>a. Kết quả: A→b, B→a, C→b, D→None.
    prefs = {("A", "x"): ["a", "b", "c"], ("B", "x"): ["a", "c"], ("C", "x"): ["b", "a"], ("D", "x"): ["c", "a"]}
    gan = {("A", "x"): "b", ("B", "x"): "a", ("C", "x"): "b", ("D", "x"): None}
    clubs = {"a": {"cap": 1, "buoi": "x"}, "b": {"cap": 2, "buoi": "x"}, "c": {"cap": 1, "buoi": "x"}}
    cs = ct.chi_so_clb_ct1(clubs, prefs, gan)
    assert {c: cs[c]["nv1"] for c in cs} == {"a": 2, "b": 1, "c": 1}
    # a: A xếp a trên b (đã nhận b) → +1; D chưa có CLB, a trong danh sách → +1; B đã nhận a → 0 ⇒ 2
    assert cs["a"]["chua_dap"] == 2
    assert cs["b"]["chua_dap"] == 0                  # C đã nhận b; A đã nhận b
    assert cs["c"]["chua_dap"] == 1                  # D chưa có CLB (c ở hạng 1); B đã nhận a (c thấp hơn)
    assert [cs[c]["da_nhan"] for c in ("a", "b", "c")] == [1, 2, 0]


def test_chi_so_clb_tach_theo_buoi():
    # Cùng em, hai buổi: nguyện vọng và kết quả được xét RIÊNG từng buổi.
    prefs = {("A", "t2"): ["a", "b"], ("A", "t3"): ["c", "d"]}
    gan = {("A", "t2"): "b", ("A", "t3"): "c"}
    clubs = {k: {"cap": 5, "buoi": "t2" if k in "ab" else "t3"} for k in "abcd"}
    cs = ct.chi_so_clb_ct1(clubs, prefs, gan)
    assert cs["a"]["nv1"] == 1 and cs["c"]["nv1"] == 1 and cs["b"]["nv1"] == 0 and cs["d"]["nv1"] == 0
    assert cs["a"]["chua_dap"] == 1 and cs["c"]["chua_dap"] == 0


def test_thong_ke_va_hang():
    prefs = {("A", "x"): ["a", "b"], ("B", "x"): ["a", "b"], ("C", "x"): ["b", "a"]}
    gan = {("A", "x"): "a", ("B", "x"): "b", ("C", "x"): None}
    h = ct.hang_ket_qua(prefs, gan)
    assert h == {("A", "x"): 1, ("B", "x"): 2, ("C", "x"): 3}   # chưa có CLB = dưới mọi CLB trong danh sách
    t = ct.thong_ke_ket_qua(prefs, gan)
    assert t == {"tong": 3, "nv1": 1, "chua_co": 1}


# ----- luật đề xuất -----

def _tong(caps):
    return sum(caps.values())


def test_bo_test_cho_ra_dung_cap_moi_va_bon_buoc():
    moi = ct.khuyen_nghi_chi_tieu(TEST)
    assert moi == {"clb_bongda": 24, "clb_tienganh": 19, "clb_tinhoc": 14, "clb_mythuat": 14, "clb_bongro": 14,
                   "clb_amnhac": 11, "clb_tinhnguyen": 10, "clb_vanhoc": 8, "clb_robotics": 8, "clb_khoahoc": 8}
    assert _tong(moi) == 130
    assert ct.ghep_buoc_chuyen(TEST, moi) == [
        ("clb_bongro", "clb_bongda", 4), ("clb_amnhac", "clb_tienganh", 3),
        ("clb_tinhnguyen", "clb_tinhoc", 2), ("clb_vanhoc", "clb_mythuat", 2)]


def test_khong_tang_khi_khong_co_em_muon_vao_ma_chua_duoc():
    # nv1 rất cao nhưng chua_dap = 0 ⇒ cap không tăng (chỉ có thể giảm hoặc giữ).
    cl = {"a": _cs(10, 30, 0), "b": _cs(10, 5, 4), "c": _cs(10, 5, 0)}
    moi = ct.khuyen_nghi_chi_tieu(cl, tran=0.5, toi_thieu=1)
    assert moi["a"] <= 10
    assert _tong(moi) == 30


def test_kep_tran_va_toi_thieu_va_khong_vuot_cap_hien_tai():
    cl = {"a": _cs(10, 100, 50), "b": _cs(10, 0), "c": _cs(5, 0)}      # c: toi_thieu 8 > cap 5
    moi = ct.khuyen_nghi_chi_tieu(cl, tran=0.2, toi_thieu=8)
    assert 8 <= moi["a"] <= 12                                          # ±20 %
    assert moi["b"] >= 8
    assert moi["c"] <= 5                                                # không bao giờ ép CLB nhỏ lên mức tối thiểu
    assert _tong(moi) == 25


def test_tong_cho_giu_nguyen_tren_nhieu_bo_ngau_nhien():
    rg = random.Random(7)
    for _ in range(200):
        m = rg.randint(3, 15)
        cl = {"c%02d" % i: _cs(rg.randint(1, 30), rg.randint(0, 40), rg.randint(0, 30)) for i in range(m)}
        moi = ct.khuyen_nghi_chi_tieu(cl, tran=rg.choice([0.1, 0.2, 0.3]), toi_thieu=rg.choice([1, 5, 8]))
        assert _tong(moi) == _tong({c: v["cap"] for c, v in cl.items()})
        for c, v in cl.items():
            assert moi[c] >= 1 and moi[c] <= max(v["cap"], round(v["cap"] * 1.3))
            if v["chua_dap"] == 0:
                assert moi[c] <= v["cap"]                               # không tăng khi chưa có nhu cầu bị bỏ lại
        steps = ct.ghep_buoc_chuyen(cl, moi)
        rong = {c: v["cap"] for c, v in cl.items()}
        for a, b, k in steps:
            assert k >= 1 and a != b
            rong[a] -= k
            rong[b] += k
        assert rong == moi                                              # các bước phủ ĐỦ mọi chênh lệch


def test_khong_bot_xuong_duoi_cho_giu_du_tru():
    cl = {"a": _cs(10, 0, 0, reserve=9), "b": _cs(10, 30, 10), "c": _cs(10, 0, 0)}
    moi = ct.khuyen_nghi_chi_tieu(cl, tran=0.5, toi_thieu=1)
    assert moi["a"] >= 9 and _tong(moi) == 30


def test_clb_tu_do_bi_loai_khoi_de_xuat():
    cl = {"a": _cs(10, 30, 20), "b": _cs(10, 2), "tu_do": _cs(999, 50, 50, loai_tru=True)}
    moi = ct.khuyen_nghi_chi_tieu(cl, tran=0.3, toi_thieu=1)
    assert moi["tu_do"] == 999                                          # giữ nguyên, không nằm trong tổng để cân
    assert moi["a"] + moi["b"] == 20
    assert all("tu_do" not in (a, b) for a, b, _ in ct.ghep_buoc_chuyen(cl, moi))


def test_ket_qua_khong_phu_thuoc_thu_tu_dict():
    ks = list(TEST)
    ket = None
    for lan in range(6):
        random.Random(lan).shuffle(ks)
        cl = {k: dict(TEST[k]) for k in ks}
        moi = ct.khuyen_nghi_chi_tieu(cl)
        buoc = ct.ghep_buoc_chuyen(cl, moi)
        if ket is None:
            ket = (moi, buoc)
        assert (moi, buoc) == ket


def test_hoa_thi_chia_theo_ma_clb():
    # Hai CLB y hệt nhau về mọi chỉ số: người nhận thêm chỗ là CLB có mã nhỏ hơn.
    cl = {"b": _cs(10, 30, 10), "a": _cs(10, 30, 10), "x": _cs(10, 0), "y": _cs(10, 0)}
    moi = ct.khuyen_nghi_chi_tieu(cl, tran=0.2, toi_thieu=1)
    assert moi["a"] >= moi["b"] and _tong(moi) == 40


def test_hai_buoi_duoc_can_rieng_tung_buoi():
    cl = {"a": _cs(10, 30, 20, buoi="t2"), "b": _cs(10, 0, 0, buoi="t2"),
          "c": _cs(10, 5, 5, buoi="t3"), "d": _cs(10, 5, 0, buoi="t3")}
    moi = ct.khuyen_nghi_chi_tieu(cl, tran=0.3, toi_thieu=1)
    assert moi["a"] + moi["b"] == 20 and moi["c"] + moi["d"] == 20
    for a, b, _ in ct.ghep_buoc_chuyen(cl, moi):
        assert cl[a]["buoi"] == cl[b]["buoi"]                           # chỗ chỉ chuyển trong cùng buổi


def test_khong_co_nv1_thi_giu_nguyen():
    cl = {"a": _cs(10, 0, 0), "b": _cs(10, 0, 0)}
    assert ct.khuyen_nghi_chi_tieu(cl) == {"a": 10, "b": 10}
    assert ct.ghep_buoc_chuyen(cl, {"a": 10, "b": 10}) == []


# ----- bước tự chọn -----

CLB = {"a": {"cap": 10, "reserve_capacity": 2, "loai_tru": False, "buoi": "t2"},
       "b": {"cap": 5, "reserve_capacity": 0, "buoi": "t2"}, "c": {"cap": 3, "reserve_capacity": 0, "buoi": "t2"},
       "tu": {"cap": 99, "reserve_capacity": 0, "loai_tru": True, "buoi": "t2"},
       "x": {"cap": 9, "reserve_capacity": 0, "buoi": "t3"}}


def test_kiem_buoc_hop_le_tra_ve_bo_chuan():
    ds, loi = ct.kiem_buoc_tu_chon([{"tu": "a", "den": "b", "k": 2}, {"tu": "b", "den": "c", "k": 1}], CLB)
    assert loi is None
    assert ds == [("a", "b", 2), ("b", "c", 1)]


@pytest.mark.parametrize("buoc,ma", [
    ([{"tu": "zzz", "den": "b", "k": 1}], "ct1_clb_la"),
    ([{"tu": "a", "den": "zzz", "k": 1}], "ct1_clb_la"),
    ([{"tu": "a", "den": "a", "k": 1}], "ct1_buoc_khong_hop_le"),
    ([{"tu": "a", "den": "b", "k": 0}], "ct1_buoc_khong_hop_le"),
    ([{"tu": "a", "den": "b", "k": -2}], "ct1_buoc_khong_hop_le"),
    ([{"tu": "a", "den": "b", "k": 1.5}], "ct1_buoc_khong_hop_le"),
    ([{"tu": "a", "den": "b", "k": True}], "ct1_buoc_khong_hop_le"),
    ([{"tu": "a", "den": "b"}], "ct1_buoc_khong_hop_le"),
    (["a->b"], "ct1_buoc_khong_hop_le"),
    ("khong phai danh sach", "ct1_buoc_khong_hop_le"),
    ([{"tu": "c", "den": "b", "k": 3}], "ct1_cap_qua_thap"),              # c còn 0 chỗ
    ([{"tu": "a", "den": "b", "k": 9}], "ct1_cap_qua_thap"),              # a còn 1 < chỗ giữ 2
    ([{"tu": "a", "den": "tu", "k": 1}], "ct1_clb_la"),                   # CLB tự do không dùng được
    ([{"tu": "a", "den": "x", "k": 1}], "ct1_khac_buoi"),                 # chỗ không chuyển sang buổi khác
])
def test_kiem_buoc_tu_choi(buoc, ma):
    ds, loi = ct.kiem_buoc_tu_chon(buoc, CLB)
    assert ds is None and loi["code"] == ma


def test_kiem_buoc_cong_don_va_gioi_han_so_buoc():
    # Hai bước liên tiếp cùng rút từ a: tổng rút 7 > 8 cho phép? a còn 10-8=2 (=chỗ giữ) hợp lệ; 9 thì không.
    ds, loi = ct.kiem_buoc_tu_chon([{"tu": "a", "den": "b", "k": 4}, {"tu": "a", "den": "c", "k": 4}], CLB)
    assert loi is None
    ds, loi = ct.kiem_buoc_tu_chon([{"tu": "a", "den": "b", "k": 4}, {"tu": "a", "den": "c", "k": 5}], CLB)
    assert loi["code"] == "ct1_cap_qua_thap"
    nhieu = [{"tu": "a", "den": "b", "k": 1}] * (ct.TOI_DA_BUOC + 1)
    assert ct.kiem_buoc_tu_chon(nhieu, CLB)[1]["code"] == "ct1_qua_nhieu_buoc"


def test_nguong_chua_dap_khong_bi_buoc_can_bang_che():
    """CT1-FIX (phát hiện 5). Mục tiêu theo tỉ lệ nv1 cho A thêm 2 chỗ (chua_dap 1), C giữ 10 (chua_dap 5, tỉ lệ cao hơn),
    B bớt 2. Nếu bỏ ngưỡng `chua_dap >= 1` thì A dừng ở 10 và bước cân ±1 dồn chỗ cho C (ưu tiên theo tỉ lệ), kết quả khác."""
    cs = {"A": _cs(10, 12, chua_dap=1), "C": _cs(10, 10, chua_dap=5), "B": _cs(10, 8, chua_dap=0)}
    assert ct.khuyen_nghi_chi_tieu(cs) == {"A": 12, "B": 8, "C": 10}
    cs["A"]["chua_dap"] = 0                                    # cùng nv1 nhưng không ai chưa được đáp ứng: A không được tăng
    assert ct.khuyen_nghi_chi_tieu(cs)["A"] == 10
