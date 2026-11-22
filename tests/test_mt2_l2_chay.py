"""MT2-L2: "Chia CLB theo loại" nối vào pipeline, KHÔNG cần huy chương (chi_xep / chia_100 + loại).

Dữ liệu là dữ liệu MÔ PHỎNG dựng trong test.
Bất biến: 2 (khoá không đọc hạng / kết quả cũ), 3 (bốc thăm), 4 (run_history chỉ thêm), 5 (kiểm trước, một giao dịch),
8 (hàm chọn CLB không bảo đảm gì mới: `verify_stability` chạy trong pipeline, ở đây đo thêm trên nhiều seed).
"""

import json
import random

import pytest

import cau_hinh_ws as ch
import fa_daa
import rbda_priority_pipeline as rp
from _fa import dung_fa_clb, dung_hs_fa
from _wharton import chen_bids


def _luot(api, bang, cot):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute("SELECT %s FROM %s ORDER BY 1, 2" % (cot, bang))]


def _dung(api, wharton=False, chia_loai=True):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": wharton, "chia_loai": chia_loai}})
    dung_fa_clb(api, T=(1, "TU_DO", None, None, 3), G=(2, "GIOI_HAN"), S=(2, "TUYEN_CHON", 5))
    ds = ["s%d" % i for i in range(1, 9)]
    dung_hs_fa(api, *ds, nv={s: ["S", "G", "T"] for s in ds[:6]})
    assert api.submit_test_selection("s1", ["S"])["ok"]
    assert api.submit_test_selection("s2", ["S"])["ok"]
    assert api.submit_club_scores("S", [{"student_id": "s1", "score": 9},
                                        {"student_id": "s2", "score": 3}])["ok"]


# ------------------------------------------------------------ chế độ chỉ xếp + loại (không điểm)

def test_chi_xep_voi_loai_chay_dung_va_ghi_luat(api):
    _dung(api)
    kq = api.run_pipeline(seed=11)
    assert kq["ok"], kq["errors"]
    mr = dict(_luot(api, "match_results", "student_id, club_id"))
    assert all(mr.get("s%d" % i) is not None for i in range(1, 9))     # Tự do không từ chối
    assert mr["s1"] == "S"                                              # điểm >= sàn, nhận
    assert mr["s2"] != "S"                                              # dưới sàn: lọc
    assert mr["s7"] == "T" and mr["s8"] == "T"                          # không đăng ký -> CLB Tự do
    assert {r[2] for r in _luot(api, "fa_nhom", "run_id, student_id, club_id")} <= {"T"}
    with api._ket_noi_doc() as cur:
        luat = json.loads(cur.execute("SELECT luat_xep FROM run_history").fetchone()[0])
    assert luat["chia_loai"] is True and "fa_daa" not in luat


def test_chay_lai_giong_het_va_run_history_chi_them(api):
    _dung(api)
    assert api.run_pipeline(seed=11)["ok"]
    truoc = _luot(api, "match_results", "student_id, club_id")
    assert api.run_pipeline(seed=11)["ok"]
    assert _luot(api, "match_results", "student_id, club_id") == truoc
    assert len(_luot(api, "run_history", "run_id, seed")) == 2            # bất biến 4: thêm, không ghi đè


def test_tat_lai_bo_qua_loai_nhung_giu_loai_da_dat(api):
    _dung(api)
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False, "chia_loai": False}})
    assert api.run_pipeline(seed=11)["ok"]
    assert _luot(api, "fa_nhom", "run_id, student_id") == []              # không còn lớp loại
    assert dict(_luot(api, "clubs", "club_id, loai")) == {"G": "GIOI_HAN", "S": "TUYEN_CHON", "T": "TU_DO"}
    with api._ket_noi_doc() as cur:
        luat = cur.execute("SELECT luat_xep FROM run_history").fetchone()[0]
    assert luat is None or "chia_loai" not in luat


def test_thieu_clb_tu_do_chan_ro_rang_khong_ghi_gi(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False, "chia_loai": True}})
    dung_fa_clb(api, G=(2, "GIOI_HAN"), S=(2, "TUYEN_CHON", 5))
    dung_hs_fa(api, "a", "b", nv={"a": ["G"], "b": ["G"]})
    kq = api.run_pipeline(seed=3)
    assert not kq["ok"]
    assert "fa_thieu_clb_tu_do" in [e["code"] for e in kq["errors"]]
    assert _luot(api, "match_results", "student_id, club_id") == []
    assert _luot(api, "run_history", "run_id, seed") == []                 # không ghi gì
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT is_locked FROM stb_lock WHERE id = 1").fetchone()[0] == 0


def test_clb_chua_co_loai_chan_khi_bat(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False, "chia_loai": True}})
    dung_fa_clb(api, T=(2, "TU_DO"), X=(2,))
    dung_hs_fa(api, "a", nv={"a": ["X"]})
    kq = api.run_pipeline(seed=3)
    assert not kq["ok"] and "fa_clb_thieu_loai" in [e["code"] for e in kq["errors"]]


def test_tuyen_chon_thieu_diem_san_chan(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False, "chia_loai": True}})
    dung_fa_clb(api, T=(2, "TU_DO"), S=(2, "TUYEN_CHON"))
    dung_hs_fa(api, "a", nv={"a": ["T"]})
    kq = api.run_pipeline(seed=3)
    assert not kq["ok"] and "fa_clb_thieu_diem_san" in [e["code"] for e in kq["errors"]]


# ------------------------------------------------------------ điểm quyết tâm + loại

def _dung_dqt(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": True, "chia_loai": True}})
    dung_fa_clb(api, T=(5, "TU_DO"), G=(1, "GIOI_HAN"))
    dung_hs_fa(api, "a", "b", "c", nv={s: ["G", "T"] for s in "abc"})
    # quỹ 2 (CLB không thi): mỗi em chia đúng 100 điểm; b đặt nhiều nhất vào G
    chen_bids(api, [("a", "G", 2, 30), ("a", "T", 2, 70),
                    ("b", "G", 2, 90), ("b", "T", 2, 10),
                    ("c", "G", 2, 60), ("c", "T", 2, 40)])


def test_chia_100_voi_loai_giai_theo_diem_quyet_tam(api):
    _dung_dqt(api)
    for seed in (1, 2, 3, 4, 5):
        kq = api.run_pipeline(seed=seed, force_redraw_stb=True)
        assert kq["ok"], kq["errors"]
        mr = dict(_luot(api, "match_results", "student_id, club_id"))
        assert mr["b"] == "G"                    # điểm quyết tâm cao nhất ở CLB Giới hạn 1 chỗ
        assert mr["a"] == "T" and mr["c"] == "T"


# ------------------------------------------------------------ khoá ưu tiên (lõi, không đọc hạng)

def _bo_nho(w, san=None):
    clubs = {"T": {"capacity": 1, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"},
             "G": {"capacity": 2, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"}}
    fa_clb = {"T": {"loai": "TU_DO", "diem_san": None, "so_toi_thieu": None, "suc_chua_phong": None},
              "G": {"loai": "GIOI_HAN", "diem_san": None, "so_toi_thieu": None, "suc_chua_phong": None}}
    sids = ["s%d" % i for i in range(1, 7)]
    stb = {s: i for i, s in enumerate(sids, 1)}                  # s1 bốc nhỏ nhất = ưu tiên bốc thăm cao nhất
    prefs = {s: ["G", "T"] for s in sids}
    kq = fa_daa.chay_fa_daa(
        {s: {"stb": stb[s], "reserve_group": None} for s in sids}, clubs, {"T": {}, "G": {}},
        rp.hop_ung_vien({"T": [], "G": []}, prefs), prefs, stb, fa_clb, [], {}, seed=1,
        diem_wharton=w)
    return sorted(s for s, c in kq.ket_qua.assignment.items() if c["b1"] == "G")


def test_chi_xep_khong_diem_giu_thu_tu_boc_tham():
    assert _bo_nho({}) == ["s1", "s2"]                           # chỉ còn bốc thăm


def test_chia_100_diem_di_truoc_boc_tham():
    w = {"G": {"s1": 10, "s2": 10, "s3": 10, "s4": 80, "s5": 70, "s6": 0}}
    assert _bo_nho(w) == ["s4", "s5"]


def test_khoa_khong_doi_khi_dao_thu_hang_nguyen_vong():
    """Bất biến 2: đảo thứ hạng nguyện vọng (cùng tập CLB) không đổi ai được vào CLB Giới hạn khi
    mọi em đều chỉ có hai CLB — thứ tự ưu tiên của CLB không phụ thuộc hạng."""
    w = {"G": {"s1": 10, "s2": 10, "s3": 10, "s4": 80, "s5": 70, "s6": 0}}
    assert _bo_nho(w) == ["s4", "s5"]
    # cùng dữ liệu, nhưng nguyện vọng "T" trước "G" cho mọi em: Tự do nhận hết, không ai bị từ chối ở G
    clubs = {"T": {"capacity": 1, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"},
             "G": {"capacity": 2, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"}}
    fa_clb = {"T": {"loai": "TU_DO"}, "G": {"loai": "GIOI_HAN"}}
    sids = ["s1", "s2"]
    stb = {"s1": 1, "s2": 2}
    prefs = {"s1": ["G", "T"], "s2": ["T", "G"]}
    a = fa_daa.chay_fa_daa({s: {"stb": stb[s], "reserve_group": None} for s in sids}, clubs,
                           {"T": {}, "G": {}}, rp.hop_ung_vien({"T": [], "G": []}, prefs), prefs,
                           stb, fa_clb, [], {}, seed=1, diem_wharton={})
    assert a.ket_qua.assignment == {"s1": {"b1": "G"}, "s2": {"b1": "T"}}


# ------------------------------------------------------------ dấu vân tay (F1) và áp dụng tiêu chí (F2)

def _dvt(api, rules):
    with api._ket_noi_doc() as cur:
        return rp.dau_van_tay_du_lieu(cur, rules)


def test_dau_van_tay_theo_loai_khi_bat_va_khong_khi_tat(api):
    _dung(api)
    bat, tat = {"wharton": False, "chia_loai": True}, {"wharton": False, "chia_loai": False}
    b0, t0 = _dvt(api, bat), _dvt(api, tat)
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET loai = 'GIOI_HAN' WHERE club_id = 'T'")
    assert _dvt(api, bat) != b0                  # đổi loại khi BẬT: kết quả cũ phải báo "đã cũ"
    assert _dvt(api, tat) == t0                  # TẮT: loại bị bỏ qua, dấu vân tay không đổi


def test_ap_dung_tieu_chi_mang_theo_chia_loai():
    import api as api_mod
    da_luu = rp.luat_xep_cua({"wharton": False})
    thu = rp.luat_xep_hieu_luc({"wharton": False, "chia_loai": True})
    moi = api_mod.PipelineAPI._luat_ap_dung(da_luu, thu)
    assert moi["chia_loai"] is True


def test_chay_thu_tu_choi_khi_bat_chia_loai(api):
    _dung(api)
    assert api.run_pipeline(seed=11)["ok"]
    kq = api.run_thu({"chia_loai": True, "wharton": False})
    assert not kq["ok"] and kq["errors"][0]["code"] == "mt_thu_chua_ho_tro_loai"


# ------------------------------------------------------------ bất biến 8: đo ổn định (MÔ PHỎNG)

@pytest.mark.parametrize("che_do", ["chi_xep", "chia_100"])
def test_on_dinh_0_cap_pha_vo_tren_12_seed(api_factory, che_do):
    """Mỗi seed một CSDL. `run_pipeline` chặn bằng `verify_stability` (cặp phá vỡ => rollback + lỗi
    `blocking_pair`), nên `ok` nghĩa là 0 cặp phá vỡ. Đo (dữ liệu MÔ PHỎNG, 30 em, 3 CLB): 0/12 seed vi phạm
    ở cả hai chế độ."""
    wh = che_do == "chia_100"
    for seed in range(12):
        api = api_factory()
        r = random.Random(seed)
        ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": wh, "chia_loai": True}})
        dung_fa_clb(api, T=(1, "TU_DO"), G=(3, "GIOI_HAN"), S=(3, "TUYEN_CHON", 4))
        ds = ["s%02d" % i for i in range(30)]
        dung_hs_fa(api, *ds)
        thi = []
        for s in ds:
            nv = [c for c in ["G", "S", "T"] if r.random() < .8] or ["T"]
            r.shuffle(nv)
            assert api.submit_preferences(s, nv)["ok"]
            if "S" in nv and r.random() < .8:
                assert api.submit_test_selection(s, ["S"])["ok"]
                thi.append({"student_id": s, "score": r.randint(0, 10)})
        if thi:
            assert api.submit_club_scores("S", thi)["ok"]
        if wh:
            chen_bids(api, _bids_deu(api))
        kq = api.run_pipeline(seed=seed)
        assert kq["ok"], (che_do, seed, kq["errors"][:2])


def _bids_deu(api):
    """Mỗi em chia đều 100 điểm mỗi quỹ (quỹ 1: CLB đã tick thi; quỹ 2: còn lại), phần dư vào CLB đầu."""
    with api._ket_noi_doc() as cur:
        tick = {(a, b) for a, b in cur.execute("SELECT student_id, club_id FROM club_test_selection")}
        pref: dict = {}
        for a, b in cur.execute("SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
            pref.setdefault(a, []).append(b)
    ra = []
    for s, cs in pref.items():
        for quy, ds_c in ((1, [c for c in cs if (s, c) in tick]), (2, [c for c in cs if (s, c) not in tick])):
            if ds_c:
                chia = [100 // len(ds_c)] * len(ds_c)
                chia[0] += 100 - sum(chia)
                ra += [(s, c, quy, p) for c, p in zip(ds_c, chia)]
    return ra
