"""A5-L5: chạy xếp THẬT với ô nhóm của CLB là `a|b` (suất dự trữ dùng chung), điểm Wharton tắt.

Dữ liệu MÔ PHỎNG dựng tại chỗ bằng nhập CSV + `bulk_set_reserve_group`; không có hồ sơ Wharton.
CLB `clb_x`: chỉ tiêu 5, dự trữ 3, ô nhóm là tham số. Mọi em đều thi `clb_x` và ghi `clb_y`
(chỗ rộng) làm nguyện vọng 2, nên em không trúng `clb_x` vẫn có chỗ.
"""

import pytest

NHOM = {"a": ["a1", "a2", "a3", "a4", "a5", "a6"], "b": ["b1", "b2", "b3", "b4", "b5", "b6"],
        "c": ["c1", "c2", "c3"], "u": ["u1", "u2", "u3"]}


def _diem(nhom_cao):
    """c và u điểm cao nhất; `nhom_cao` ('a' hoặc 'b') cao nhất trong hai nhóm a/b."""
    d = {}
    for i, s in enumerate(NHOM["c"]):
        d[s] = 100 - i
    for i, s in enumerate(NHOM["u"]):
        d[s] = 97 - i
    thap = "b" if nhom_cao == "a" else "a"
    for i, s in enumerate(NHOM[nhom_cao]):
        d[s] = 90 - i
    for i, s in enumerate(NHOM[thap]):
        d[s] = 70 - i
    return d


def _dung(api, o_nhom_clb, nhom_cao="a", bo_b=False):
    ma = [s for g in NHOM.values() for s in g if not (bo_b and s in NHOM["b"])]
    assert api.create_or_update_club("clb_x", "CLB X", 5, 3, o_nhom_clb)["ok"]
    assert api.create_or_update_club("clb_y", "CLB Y", 30, 0, "")["ok"]
    assert api.import_test_selection_csv(
        "student_id,name,test_club_1\n" + "".join("%s,%s,clb_x\n" % (s, s) for s in ma))["ok"]
    assert api.import_preferences_csv(
        "student_id,name,pref_1,pref_2\n" + "".join("%s,%s,clb_x,clb_y\n" % (s, s) for s in ma))["ok"]
    for nhan in ("a", "b", "c"):
        ds = [s for s in NHOM[nhan] if s in ma]
        if ds:
            assert api.bulk_set_reserve_group(ds, nhan)["ok"]
    diem = _diem(nhom_cao)
    assert api.submit_club_scores("clb_x", [{"student_id": s, "score": diem[s]} for s in ma])["ok"]
    res = api.run_pipeline(seed=7)
    assert res["ok"], res.get("errors")
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute(
            "SELECT student_id, club_id, matched_tier FROM match_results ORDER BY student_id")]


def _x(kq, tang=None):
    return {s for s, c, t in kq if c == "clb_x" and (tang is None or t == tang)}


def test_du_tru_a_gach_b_chi_cho_a_va_b_theo_hang_va_chi_o_clb_do(api):
    kq = _dung(api, "a|b", nhom_cao="a")
    du_tru = _x(kq, "reserve")
    assert du_tru and du_tru <= set(NHOM["a"]) | set(NHOM["b"])      # (i) không c, không em chưa nhóm
    assert len(du_tru) == 3
    assert not _x(kq) & set(NHOM["b"])                                # b điểm thấp hơn: không có chỗ
    assert not any(t == "reserve" for s, c, t in kq if c == "clb_y")  # clb_y không có suất dự trữ
    # c1, c2 điểm cao nhất vào bằng chỉ tiêu chung (2 chỗ còn lại)
    assert _x(kq, "general") == {"c1", "c2"}


def test_nhom_diem_cao_hon_lay_het_suat_du_tru(api):
    kq = _dung(api, "a|b", nhom_cao="a")
    assert _x(kq, "reserve") == {"a1", "a2", "a3"}                    # (ii) a lấy hết 3 suất, b không có suất nào


def test_du_tru_a_gach_b_nhom_b_cao_hon_thi_b_lay_het(api):
    kq = _dung(api, "a|b", nhom_cao="b")
    assert _x(kq, "reserve") == {"b1", "b2", "b3"}


def test_o_nhom_chi_ghi_a_thi_b_bi_loai(api):
    kq = _dung(api, "a", nhom_cao="b")                                # b điểm cao hơn nhưng không đủ diện
    du_tru = _x(kq, "reserve")
    assert du_tru == {"a1", "a2", "a3"}                               # (iii)
    assert not _x(kq) & set(NHOM["b"])


def test_a_gach_b_khi_khong_co_em_nhom_b_giong_het_ghi_a(tmp_path):
    from api import PipelineAPI
    ra = []
    for o in ("a", "a|b"):
        api = PipelineAPI(str(tmp_path / (o.replace("|", "_") + ".db")))
        ra.append(_dung(api, o, nhom_cao="a", bo_b=True))
    assert ra[0] == ra[1]                                             # (iv) mặc định không đổi
    assert len(ra[0]) == 12                                            # 6 a + 3 c + 3 chưa nhóm
