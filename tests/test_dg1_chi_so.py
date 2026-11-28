"""DG1-L1: chỉ số định lượng thuần (du_lieu_test/danh_gia/_chi_so.py) trên ca 6 học sinh × 3 CLB TÍNH TAY.

Ca tay (RB-DA đã chạy bằng tay, xem lời giải trong từng test):

    CLB   chỉ tiêu  dự trữ  thi   ưu tiên
    A     1         1       có    s1 (7đ) > s2 (5đ) > s3 (không điểm)
    B     1         0       không (không ai xếp B ngoài s1)
    C     1         0       không s4 > s5 (bốc thăm)
    s1 [A,B] nhóm chinh_sach · s2 [A] · s3 [A] · s4 [C] · s5 [C] · s6 []

    DA do học sinh đề xuất: s1→A, s4→C; s2,s3 bị A từ chối, s5 bị C từ chối; s6 không có danh sách.
    Được xếp 2 (s1 nguyện vọng 1, s4 nguyện vọng 1). Ghép cực đại = 3 (s1→B, s2→A, s4→C).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "du_lieu_test", "danh_gia"))

import _chi_so as cs  # noqa: E402

HS = {
    "s1": {"reserve_group": "chinh_sach"}, "s2": {"reserve_group": ""}, "s3": {"reserve_group": ""},
    "s4": {"reserve_group": ""}, "s5": {"reserve_group": ""}, "s6": {"reserve_group": ""},
}
CLB = {
    "A": {"capacity": 1, "reserve_capacity": 1, "reserve_group": "chinh_sach"},
    "B": {"capacity": 1, "reserve_capacity": 0, "reserve_group": ""},
    "C": {"capacity": 1, "reserve_capacity": 0, "reserve_group": ""},
}
NV = {"s1": ["A", "B"], "s2": ["A"], "s3": ["A"], "s4": ["C"], "s5": ["C"], "s6": []}
DIEM = {"A": {"s1": 7.0, "s2": 5.0}, "B": {}, "C": {}}
XEP = {"s1": "A", "s2": None, "s3": None, "s4": "C", "s5": None, "s6": None}
TANG = {"s1": "reserve", "s4": "general"}
UNG_VIEN = {"A": ["s1", "s2", "s3"], "B": ["s1"], "C": ["s4", "s5"]}


def du_tru_fn(sid, cid):
    g = CLB[cid]["reserve_group"]
    return bool(g) and HS[sid]["reserve_group"] == g


def chay(**kw):
    return cs.tinh_chi_so(HS, CLB, NV, UNG_VIEN, DIEM, XEP, TANG, du_tru_fn, **kw)


class TestGhepCucDai:
    def test_ca_tay_3(self):
        # s1→B, s2→A, s4→C = 3; s3, s5, s6 không còn chỗ.
        assert cs.ghep_cuc_dai(NV, {c: v["capacity"] for c, v in CLB.items()}) == 3

    def test_lon_hon_ket_qua_on_dinh(self):
        # s1:[A,B], s2:[A]; A ưu tiên s1 → ổn định chỉ xếp 1, nhưng ghép cực đại = 2.
        assert cs.ghep_cuc_dai({"s1": ["A", "B"], "s2": ["A"]}, {"A": 1, "B": 1}) == 2

    def test_suc_chua_lon_va_danh_sach_rong(self):
        assert cs.ghep_cuc_dai({"s1": ["A"], "s2": ["A"], "s3": []}, {"A": 5}) == 2
        assert cs.ghep_cuc_dai({}, {"A": 1}) == 0

    def test_club_la_khong_ton_tai_bi_bo(self):
        assert cs.ghep_cuc_dai({"s1": ["Z"]}, {"A": 1}) == 0

    def test_can_duong_dai_nhieu_buoc(self):
        # Chuỗi: s1[A,B] s2[B,C] s3[C] — mỗi CLB 1 chỗ → cần đẩy dọc chuỗi mới ra 3.
        assert cs.ghep_cuc_dai({"s1": ["A", "B"], "s2": ["B", "C"], "s3": ["C"]}, {"A": 1, "B": 1, "C": 1}) == 3


class TestNhomA:
    def test_ty_le_nguyen_vong(self):
        a = chay()["a"]
        assert a["n_hs"] == 6 and a["n_da_xep"] == 2
        assert a["pct_nv1_tat_ca"] == 33.3 and a["pct_top3_tat_ca"] == 33.3
        assert a["pct_nv1_da_xep"] == 100.0
        assert a["hang_tb"] == 1.0 and a["hang_trung_vi"] == 1.0
        assert a["ngoai_danh_sach"] == 0

    def test_duong_cong_don(self):
        a = chay()["a"]
        # k = 1..max độ dài danh sách (2): % trên MỌI học sinh.
        assert a["duong_cong_don"] == [33.3, 33.3]

    def test_chia_nhom(self):
        a = chay(nhom={"du_tru": {"s1": "chinh_sach", "s2": "khong", "s3": "khong", "s4": "khong", "s5": "khong", "s6": "khong"}})["a"]
        g = a["theo_nhom"]["du_tru"]
        assert g["chinh_sach"]["n"] == 1 and g["chinh_sach"]["pct_nv1"] == 100.0
        assert g["khong"]["n"] == 5 and g["khong"]["pct_nv1"] == 20.0

    def test_tang_hoc_sinh(self):
        # Tầng 1 = có điểm ở ≥1 CLB trong danh sách: s1, s2 (A). Còn lại Tầng 2.
        t = chay()["a"]["theo_nhom"]["tang"]
        assert t["tang_1"]["n"] == 2 and t["tang_1"]["pct_nv1"] == 50.0
        assert t["tang_2"]["n"] == 4 and t["tang_2"]["pct_nv1"] == 25.0

    def test_ngoai_danh_sach_duoc_dem(self):
        xep = dict(XEP, s2="C")          # s2 chỉ xếp A mà bị đặt vào C
        r = cs.tinh_chi_so(HS, CLB, NV, UNG_VIEN, DIEM, xep, TANG, du_tru_fn)
        assert r["a"]["ngoai_danh_sach"] == 1


class TestNhomB:
    def test_dem_va_can_tren(self):
        b = chay()["b"]
        assert b["n_chua_xep"] == 4 and b["pct_chua_xep"] == 66.7
        assert b["can_tren_ghep_cuc_dai"] == 3
        assert b["khong_the_tranh"] == 3          # N − cận = 6 − 3
        assert b["gia_uu_tien_on_dinh"] == 1      # cận − được xếp = 3 − 2
        assert b["tong_chi_tieu_nho_hon_hs"] is True

    def test_nguyen_nhan(self):
        n = chay()["b"]["nguyen_nhan"]
        assert n == {"danh_sach_rong": 1, "khong_diem": 1, "het_cho_uu_tien_cao_hon": 2}

    def test_lech_cho(self):
        # B còn trống: s2, s3, s5, s6 đều không xếp B → 4 em "chưa xếp trong khi CLB khác họ không chọn còn chỗ".
        assert chay()["b"]["lech_cho"] == 4


class TestNhomC:
    def test_lap_day(self):
        c = chay()["c"]
        assert c["ty_le_lap_day"] == 66.7
        assert c["n_clb_day"] == 2 and c["n_clb_duoi_50"] == 1
        pc = c["phan_vi_lap_day"]
        assert pc["min"] == 0.0 and pc["p25"] == 0.5 and pc["median"] == 1.0 and pc["max"] == 1.0

    def test_du_tru(self):
        c = chay()["c"]
        assert c["du_tru_cung_cap"] == 1 and c["du_tru_da_dung"] == 1
        assert c["du_tru_dien_qua_du_tru"] == 1 and c["du_tru_dien_qua_thuong"] == 0

    def test_ti_le_cau_va_tung_clb(self):
        theo = {x["club_id"]: x for x in chay()["c"]["theo_clb"]}
        assert theo["A"]["nv1"] == 3 and theo["A"]["ti_le_cau"] == 3.0 and theo["A"]["lap_day"] == 1.0
        assert theo["B"]["nv1"] == 0 and theo["B"]["lap_day"] == 0.0
        assert theo["C"]["ti_le_cau"] == 2.0


class TestHocSinhNhieuBuoi:
    def test_tong_hop(self):
        # 3 em, 2 buổi. e1 có chỗ cả hai; e2 chỉ buổi 1 (buổi 2 không có chỗ); e3 danh sách buổi 2 rỗng, có chỗ buổi 1.
        xep = {"b1": {"e1": "X", "e2": "X", "e3": "Y"}, "b2": {"e1": "Z", "e2": None, "e3": None}}
        nv = {"b1": {"e1": ["X"], "e2": ["X"], "e3": ["Y"]}, "b2": {"e1": ["Z"], "e2": ["Z"], "e3": []}}
        t = cs.tong_hop_theo_hoc_sinh(xep, nv)
        assert t["n_hs"] == 3
        assert t["so_buoi_co_cho_tb"] == round((2 + 1 + 1) / 3, 3)
        assert t["pct_du_moi_buoi_da_khai"] == 66.7        # e1, e3 đủ mọi buổi họ đã khai; e2 thiếu buổi 2
        assert t["pct_khong_co_cho_nao"] == 0.0


class TestGhepCucDaiNgauNhien:
    def test_khop_vet_can_tren_30_the_hien_nho(self):
        import itertools
        import random
        rng = random.Random(7)
        for _ in range(30):
            n, m = rng.randint(2, 6), rng.randint(1, 4)
            clbs = ["c%d" % j for j in range(m)]
            cap = {c: rng.randint(1, 2) for c in clbs}
            nv = {"s%d" % i: rng.sample(clbs, rng.randint(0, m)) for i in range(n)}
            tot = 0
            sids = sorted(nv)
            # vét cạn: mỗi em chọn một CLB trong danh sách hoặc bỏ
            for chon in itertools.product(*[[None] + nv[s] for s in sids]):
                dem = {}
                ok = True
                for c in chon:
                    if c is not None:
                        dem[c] = dem.get(c, 0) + 1
                        if dem[c] > cap[c]:
                            ok = False
                            break
                if ok:
                    tot = max(tot, sum(1 for c in chon if c is not None))
            assert cs.ghep_cuc_dai(nv, cap) == tot
