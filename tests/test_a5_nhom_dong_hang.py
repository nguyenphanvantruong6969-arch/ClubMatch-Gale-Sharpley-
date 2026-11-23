"""A5-L1: nhóm đồng hạng `a|b` — lõi (tach_nhom_clb, xay_tier_rank, reserve pooled)."""
import random

import rbda_priority_pipeline as P


def test_tach_nhom_clb():
    assert P.tach_nhom_clb(None) == ()
    assert P.tach_nhom_clb("") == ()
    assert P.tach_nhom_clb("a") == ("a",)
    assert P.tach_nhom_clb(" A | a ") == ("A", "a")
    assert P.tach_nhom_clb("a||b|") == ("a", "b")
    assert P.tach_nhom_clb("chinh_sach") == ("chinh_sach",)


def test_tier_hai_nhan_cung_hang_thu_tu_diem_roi_stb():
    hs = {"s1": {"reserve_group": "a"}, "s2": {"reserve_group": "b"},
          "s3": {"reserve_group": "b"}, "s4": {"reserve_group": "c"},
          "s5": {"reserve_group": ""}, "s6": {"reserve_group": "a"}}
    rank = P.xay_tier_rank(hs, ["a|b", "c"])
    assert rank == {"s1": 0, "s2": 0, "s3": 0, "s6": 0, "s4": 1}
    diem = {"s1": 50.0, "s2": 80.0, "s3": 80.0, "s4": 99.0, "s5": 99.0, "s6": 60.0}
    stb = {"s1": 1, "s2": 5, "s3": 2, "s4": 3, "s5": 4, "s6": 6}
    kq = P.uu_tien_theo_nhom("X", list(hs), diem, stb, rank)
    assert kq == ["s3", "s2", "s6", "s1", "s4", "s5"]


def test_tier_khong_gach_giu_nguyen():
    hs = {"s1": {"reserve_group": "Khối 12"}, "s2": {"reserve_group": "khoi  11"}}
    assert P.xay_tier_rank(hs, ["khoi 12", "Khối 11"]) == {"s1": 0, "s2": 1}


def test_nhan_chinh_sach_khac_chinh_gach_sach():
    hs = {"s1": {"reserve_group": "chinh_sach"}}
    assert P.xay_tier_rank(hs, ["chinh|sach"]) == {}
    assert P.xay_tier_rank(hs, ["chinh_sach|x"]) == {"s1": 0}


def test_reserve_pooled_a_b_khong_c():
    hs = {"s1": {"reserve_group": "a"}, "s2": {"reserve_group": "b"},
          "s3": {"reserve_group": "c"}, "s4": {"reserve_group": None}}
    clubs = {"X": {"reserve_group": "a|b"}, "Y": {"reserve_group": "a"},
             "Z": {"reserve_group": None}}
    fn = P.default_reserve_eligible_fn(hs, clubs)
    assert [fn(s, "X") for s in hs] == [True, True, False, False]
    assert [fn(s, "Y") for s in hs] == [True, False, False, False]
    assert not any(fn(s, "Z") for s in hs)


def test_nhan_a_gach_duoi_b_khong_khop_a_gach_b():
    hs = {"s1": {"reserve_group": "a_b"}}
    fn = P.default_reserve_eligible_fn(hs, {"X": {"reserve_group": "a|b"}})
    assert fn("s1", "X") is False


def test_choice_function_substitutability_va_aggregate_demand():
    rng = random.Random(20261123)
    for _ in range(250):
        n = rng.randint(3, 8)
        ids = [f"s{i}" for i in range(n)]
        hs = {i: {"reserve_group": rng.choice(["a", "b", "c", None])} for i in ids}
        order = ids[:]
        rng.shuffle(order)
        rank = {sid: r for r, sid in enumerate(order)}
        cap = rng.randint(1, 4)
        res = rng.randint(0, cap)
        fn = P.default_reserve_eligible_fn(
            hs, {"X": {"reserve_group": rng.choice(["a|b", "a", "b|c"])}})

        def ch(pool):
            return set(P.club_choice_function(
                sorted(pool), cap, res, lambda sid: fn(sid, "X"), rank)[0])

        for _k in range(6):
            pool = set(rng.sample(ids, rng.randint(1, n)))
            acc = ch(pool)
            for x in ids:
                if x in pool:
                    continue
                acc2 = ch(pool | {x})
                # substitutability: người bị loại ở pool nhỏ không được nhận ở pool lớn
                assert not ((pool - acc) & acc2), (pool, x)
                # law of aggregate demand: thêm người không làm giảm số được nhận
                assert len(acc2) >= len(acc)


def test_reserve_khop_nhan_nguyen_khong_khop_chuoi_con():
    """Nhãn 'a' không được khớp 'ab|c' chỉ vì là chuỗi con (soát mã: đột biến `in club_group`)."""
    hs = {"s1": {"reserve_group": "a"}, "s2": {"reserve_group": "ab"}, "s3": {"reserve_group": "c"},
          "s4": {"reserve_group": "b"}}
    fn = P.default_reserve_eligible_fn(hs, {"X": {"reserve_group": "ab|c"}})
    assert [fn(s, "X") for s in hs] == [False, True, True, False]


def test_xay_tier_rank_va_thu_tu_uu_tien_x_ab_c_roi_chua_nhom():
    """tiers ["x","a|b","c"]: x hạng 0, a và b CÙNG hạng 1, c hạng 2; ưu tiên x < a/b < c < chưa nhóm,
    bất kể điểm (soát mã: đột biến 'mọi phần của mục a|b đều hạng 0' phải làm test này đỏ)."""
    hs = {"x1": {"reserve_group": "x"}, "a1": {"reserve_group": "a"}, "b1": {"reserve_group": "b"},
          "c1": {"reserve_group": "c"}, "u1": {"reserve_group": None}, "z1": {"reserve_group": "z"}}
    rank = P.xay_tier_rank(hs, ["x", "a|b", "c"])
    assert rank == {"x1": 0, "a1": 1, "b1": 1, "c1": 2}
    diem = {"x1": 10.0, "a1": 50.0, "b1": 60.0, "c1": 70.0, "u1": 99.0, "z1": 98.0}
    stb = {s: i for i, s in enumerate(["u1", "z1", "c1", "b1", "a1", "x1"])}
    kq = P.uu_tien_theo_nhom("X", list(hs), diem, stb, rank)
    assert kq == ["x1", "b1", "a1", "c1", "u1", "z1"]      # a/b cùng hạng: b điểm cao hơn đứng trước a
