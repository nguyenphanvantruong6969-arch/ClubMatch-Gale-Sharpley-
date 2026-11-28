"""MT1-L3 — ước tính (`uoc_tinh_muc_tieu`) và dòng kết quả (`bao_cao_muc_tieu`): chỉ ĐỌC. Dữ liệu MÔ PHỎNG.

Bộ nhỏ tự dựng, tính tay: 20 em, 3 CLB (a, b, c), em S01–S10 thi CLB a (điểm 10…1), mọi em xếp a, b, c.
Kiểm: số em tốt hơn / xuống sau tính tay; không ghi gì (tổng kiểm mọi bảng trước/sau, không sao lưu, không gọi
`run_thu`); cùng bộ số đã khoá; chưa có lần xếp thì chỉ có lời; huy chương ⇒ `mt_uoc_tinh_fa`; ẩn số 1–4
("dưới 5") ngay ở dữ liệu backend; nhiều buổi; lần chạy thử không làm mốc; dòng kết quả khớp phép so hai lần
chạy thật; vai giáo viên bị từ chối.
"""

import glob
import hashlib
import os
import sqlite3

import pytest

import api as api_mod
import cau_hinh_ws
import muc_tieu_do as do
import tieu_chi

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"


# ----- bộ nhỏ tự dựng -----

def _tao(tmp_path, caps=(10, 5, 10), nhom=None, wharton=False, ten="db"):
    """20 em; S01–S10 thi CLB a (điểm 10…1). `nhom(i)` → nhóm của em thứ i (1..20) hoặc ''."""
    nhom = nhom or (lambda i: "")
    thu_muc = tmp_path / ten
    thu_muc.mkdir()
    db = str(thu_muc / "app.db")
    a = api_mod.PipelineAPI(db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": wharton}})
    clb = "club_id,name,capacity,reserve_capacity,reserve_group\n" + "".join(
        "clb_%s,CLB %s,%d,0,\n" % (k, k.upper(), c) for k, c in zip("abc", caps))
    thi = "student_id,name,reserve_group,class_id,test_club_1,score_1\n" + "".join(
        "S%02d,Em %d,%s,10A,clb_a,%d\n" % (i, i, nhom(i), 11 - i) for i in range(1, 11))
    ts = ["S%02d" % i for i in range(1, 21)]
    nv = "student_id,name,reserve_group,class_id,pref_1,pref_2,pref_3\n" + "".join(
        "%s,Em %d,%s,10A,clb_a,clb_b,clb_c\n" % (s, i, nhom(i)) for i, s in enumerate(ts, 1))
    for text in (clb, thi, nv):
        r = a.import_csv_auto(text)
        assert r["ok"], r
    return a, db


def _ep_stb(db, thu_tu):
    """Gán số bốc thăm 1..20 theo thứ tự `thu_tu` (danh sách mã em) — SAU khi bộ số đã khoá."""
    c = sqlite3.connect(db)
    for so, sid in enumerate(thu_tu, 1):
        c.execute("UPDATE students SET stb_number = ? WHERE student_id = ?", (so, sid))
    c.commit()
    c.close()


def _s(*ds):
    return ["S%02d" % i for i in ds]


def _chay(a, db, thu_tu=None):
    assert a.run_pipeline(seed=42)["ok"]
    if thu_tu:
        _ep_stb(db, thu_tu)
        assert a.run_pipeline(seed=42)["ok"]


def _foto(db):
    """Tổng kiểm MỌI bảng (kể cả run_history, stb_lock) + số tệp sao lưu."""
    c = sqlite3.connect(db)
    try:
        h = hashlib.sha256()
        for (ten,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall():
            h.update(ten.encode())
            for r in c.execute('SELECT * FROM "%s"' % ten).fetchall():
                h.update(repr(r).encode())
        return h.hexdigest(), len(glob.glob(db + ".bak-*"))
    finally:
        c.close()


def _ma(r):
    return [e["code"] for e in r["errors"]]


# ----- hàm đo thuần -----

def test_an_so_chi_an_1_den_4():
    assert do.an_so(0) == {"n": 0, "duoi_5": False}
    for n in (1, 2, 3, 4):
        assert do.an_so(n) == {"n": None, "duoi_5": True}
    assert do.an_so(5) == {"n": 5, "duoi_5": False} and do.an_so(40) == {"n": 40, "duoi_5": False}


def test_so_sanh_hang_tot_hon_va_xuong_sau():
    truoc = {("A", "b"): ("x", 2), ("B", "b"): ("y", 1), ("C", "b"): (None, None), ("D", "b"): ("x", 3),
             ("E", "b"): ("x", 1)}
    sau = {("A", "b"): ("y", 1), ("B", "b"): (None, None), ("C", "b"): ("x", 4), ("D", "b"): ("x", 3),
           ("E", "b"): ("x", 1)}
    tot, xuong = do.so_sanh_hang(truoc, sau)
    assert tot == {"A", "C"} and xuong == {"B"}                  # D, E giữ nguyên


def test_so_sanh_hang_nhieu_buoi_dem_em_mot_lan():
    truoc = {("A", "1"): ("x", 2), ("A", "2"): ("y", 1)}
    sau = {("A", "1"): ("x", 1), ("A", "2"): ("y", 3)}           # buổi 1 tốt hơn, buổi 2 kém hơn
    tot, xuong = do.so_sanh_hang(truoc, sau)
    assert tot == {"A"} and xuong == {"A"}


def test_dat_o_clb_dong_tinh_tay():
    # 10 em, nhóm 3 em (G1..G3) ⇒ tỉ lệ chung 30 %; ngưỡng 90 % ⇒ 27 %
    sau = {}
    for sid, clb in (("G1", "X"), ("G2", "X"), ("O1", "X"), ("O2", "X"),       # X: 2/4 = 50 % ≥ 27 % ✓
                     ("O3", "Y"), ("O4", "Y"), ("O5", "Y"), ("O6", "Y"),       # Y: 0 % ✗
                     ("G3", "Z"), ("O7", "Z"), ("O8", "Z"), ("O9", "Z")):      # Z: 1/4 = 25 % < 27 % ✗
        sau[(sid, "b")] = (clb, 1)
    assert do.dat_o_clb(sau, {"G1", "G2", "G3"}, 10, ["X", "Y", "Z"]) == (1, 3)
    assert do.dat_o_clb(sau, {"G1", "G2", "G3"}, 10, ["X"]) == (1, 1)


def test_clb_dong_nhat_theo_so_nguyen_vong_1():
    assert do.clb_dong_nhat({"a": 5, "b": 9, "c": 9, "d": 1}, 3) == ["b", "c", "a"]


def test_khoang_cach_tinh_tay():
    rows = {("G1", "b"): ("x", 1), ("G2", "b"): (None, None), ("O1", "b"): ("x", 2), ("O2", "b"): ("x", 3)}
    assert do.ty_le_top(rows, {"G1", "G2"}, 3) == (0.5, 1.0)
    assert do.co_khoang_cach(rows, {"G1", "G2"}) is True
    assert do.co_khoang_cach(rows, {"O1", "O2"}) is False        # nhóm này không kém hơn
    assert do.co_khoang_cach(rows, set()) is False


def test_an_toan_nguyen_vong_1_va_chua_co_cho():
    rows = {("A", "b"): ("x", 1), ("B", "b"): ("x", 2), ("C", "b"): (None, None), ("D", "b"): ("y", 1)}
    assert do.pct_nguyen_vong_1(rows) == 50.0
    assert do.so_chua_co_cho(rows) == 1


# ----- ước tính: tính tay -----

def test_uoc_tinh_co_hoi_tinh_tay_10_tot_hon_10_xuong(tmp_path):
    a, db = _tao(tmp_path)
    _chay(a, db, _s(*range(11, 21)) + _s(*range(1, 11)))
    r = a.uoc_tinh_muc_tieu("co_hoi")
    assert r["ok"], r
    d = r["data"]
    assert d["co_so_sanh"] and d["muc_tieu"] == "co_hoi"
    assert d["tot_hon"] == {"n": 10, "duoi_5": False} and d["xuong_sau"] == {"n": 10, "duoi_5": False}
    assert d["mo_ta"] and d["mo_ta_en"]


def test_uoc_tinh_an_so_duoi_5_o_backend(tmp_path):
    a, db = _tao(tmp_path)
    _chay(a, db, _s(1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20))
    d = a.uoc_tinh_muc_tieu("co_hoi")["data"]
    assert d["tot_hon"] == {"n": None, "duoi_5": True} and d["xuong_sau"] == {"n": None, "duoi_5": True}
    assert "3" not in repr({k: v for k, v in d.items() if k in ("tot_hon", "xuong_sau")})


def test_the_dang_dung_uoc_tinh_ra_0_va_0(tmp_path):
    a, db = _tao(tmp_path)
    _chay(a, db, _s(*range(11, 21)) + _s(*range(1, 11)))
    d = a.uoc_tinh_muc_tieu("nang_luc")["data"]
    assert d["tot_hon"] == {"n": 0, "duoi_5": False} and d["xuong_sau"] == {"n": 0, "duoi_5": False}


# ----- chỉ đọc -----

@pytest.mark.parametrize("the,nhom", [("nang_luc", None), ("co_hoi", None), ("danh_cho", "khoi_10")])
def test_uoc_tinh_khong_ghi_gi_khong_sao_luu_khong_goi_run_thu(tmp_path, monkeypatch, the, nhom):
    a, db = _tao(tmp_path, nhom=lambda i: "khoi_10" if i > 14 else "")
    _chay(a, db)
    truoc, cfg_truoc = _foto(db), cau_hinh_ws.doc_cau_hinh(db)

    def cam(*_a, **_k):
        raise AssertionError("ước tính không được gọi hàm này")
    monkeypatch.setattr(api_mod.PipelineAPI, "run_thu", cam)
    monkeypatch.setattr(api_mod.PipelineAPI, "_backup_db", cam)
    monkeypatch.setattr(api_mod.PipelineAPI, "run_pipeline", cam)
    r = a.uoc_tinh_muc_tieu(the, nhom)
    assert r["ok"], r
    assert _foto(db) == truoc                          # mọi bảng (run_history, stb_lock…) và số tệp sao lưu
    assert cau_hinh_ws.doc_cau_hinh(db) == cfg_truoc    # thẻ chỉ GIẢ ĐỊNH, chưa áp


def test_uoc_tinh_khong_bao_gio_ghi_ke_ca_khi_chua_co_lan_xep(tmp_path):
    a, db = _tao(tmp_path)
    truoc = _foto(db)
    assert a.uoc_tinh_muc_tieu("co_hoi")["ok"]
    assert _foto(db) == truoc


# ----- chưa có lần xếp / huy chương / lỗi -----

def test_chua_co_lan_xep_chinh_thuc_chi_co_loi(tmp_path):
    a, db = _tao(tmp_path, nhom=lambda i: "khoi_10" if i > 14 else "")
    for the, nhom in (("nang_luc", None), ("co_hoi", None), ("danh_cho", "khoi_10")):
        r = a.uoc_tinh_muc_tieu(the, nhom)
        assert r["ok"], r
        d = r["data"]
        assert d["co_so_sanh"] is False and "tot_hon" not in d and "xuong_sau" not in d
        assert [x["chu"] for x in d["mo_ta"]] == [x["chu"] for x in tieu_chi.mo_ta_tieu_chi(
            d["luat"], "vi")]
    assert d["giu_cho"] and len(d["giu_cho"]) == 3     # danh_cho: vẫn nêu số chỗ giữ


def test_huy_chuong_thi_loi_mt_uoc_tinh_fa_va_co_hoi_van_la_mt_the_can_diem(tmp_path):
    a, db = _tao(tmp_path, wharton=True, nhom=lambda i: "khoi_10" if i > 14 else "")
    cfg = cau_hinh_ws.doc_cau_hinh(db)
    cfg["rules"]["fa_daa"] = True
    cau_hinh_ws.ghi_cau_hinh(db, cfg)
    for the, nhom in (("nang_luc", None), ("danh_cho", "khoi_10")):
        assert _ma(a.uoc_tinh_muc_tieu(the, nhom)) == ["mt_uoc_tinh_fa"], the
    assert _ma(a.uoc_tinh_muc_tieu("co_hoi")) == ["mt_the_can_diem"]


def test_dau_vao_sai_thi_ma_mt(tmp_path):
    a, db = _tao(tmp_path, nhom=lambda i: "khoi_10" if i > 14 else "")
    assert _ma(a.uoc_tinh_muc_tieu("la")) == ["mt_muc_tieu_la"]
    assert _ma(a.uoc_tinh_muc_tieu("danh_cho", "khong_co")) == ["mt_nhom_khong_co"]
    a2, _ = _tao(tmp_path, nhom=lambda i: "khoi_10" if i > 14 else ("chinh_sach" if i > 10 else ""), ten="hai")
    assert _ma(a2.uoc_tinh_muc_tieu("danh_cho")) == ["mt_can_chon_nhom"]


# ----- cảnh báo -----

def test_canh_bao_cho_it_va_khong_co_khoang_cach(tmp_path):
    # Nhóm = S11–S20 (không thi); sức chứa 10/5/10 ⇒ ai cũng có chỗ trong 3 nguyện vọng ⇒ KHÔNG có khoảng cách
    a, db = _tao(tmp_path, nhom=lambda i: "khoi_10" if i > 10 else "")
    _chay(a, db)
    d = a.uoc_tinh_muc_tieu("danh_cho", "khoi_10")["data"]
    ma = [e["code"] for e in d["canh_bao"]]
    assert "mt_khong_co_khoang_cach" in ma
    # sức chứa 10/3/2: S16–S20 không có chỗ ⇒ nhóm kém hơn ⇒ có khoảng cách, không cảnh báo đó
    a2, db2 = _tao(tmp_path, caps=(10, 3, 2), nhom=lambda i: "khoi_10" if i > 10 else "", ten="chat")
    _chay(a2, db2)
    d2 = a2.uoc_tinh_muc_tieu("danh_cho", "khoi_10")["data"]
    assert "mt_khong_co_khoang_cach" not in [e["code"] for e in d2["canh_bao"]]


def test_canh_bao_cho_giu_it_qua(tmp_path):
    # nhóm 2/20 = 10 % ⇒ ceil(0,1 × 10)=1, ceil(0,1 × 5)=1, ceil(0,1 × 10)=1 ⇒ ba CLB chỉ giữ 1 chỗ
    a, db = _tao(tmp_path, nhom=lambda i: "khoi_10" if i in (19, 20) else "")
    d = a.uoc_tinh_muc_tieu("danh_cho", "khoi_10")["data"]
    assert [e["code"] for e in d["canh_bao"]] == ["mt_cho_it"] and d["canh_bao"][0]["params"]["n"] == 3
    assert [g["giu"] for g in d["giu_cho"]] == [1, 1, 1] and d["giu_cho"][0]["suc_chua"] == 10


def test_co_hoi_chia_100_diem_co_ghi_chu(tmp_path):
    a, db = _tao(tmp_path, wharton=True)
    d = a.uoc_tinh_muc_tieu("co_hoi")["data"]
    assert [e["code"] for e in d["canh_bao"]] == ["mt_diem_chia_khong_dung"]


# ----- nhiều buổi, lần chạy thử -----

def _nap_nhieu_buoi(tmp_path):
    thu_muc = tmp_path / "nb"
    thu_muc.mkdir()
    db = str(thu_muc / "app.db")
    a = api_mod.PipelineAPI(db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    for tep in sorted(glob.glob(os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi", "NHIEUBUOI_0*.csv"))):
        with open(tep, encoding="utf-8-sig") as f:
            assert a.import_csv_auto(f.read())["ok"]
    return a, db


def test_nhieu_buoi_the_dang_dung_0_0_va_chi_doc(tmp_path):
    a, db = _nap_nhieu_buoi(tmp_path)
    assert a.run_pipeline(seed=7)["ok"]
    assert len({r[0] for r in sqlite3.connect(db).execute("SELECT buoi FROM match_results")}) >= 2
    truoc = _foto(db)
    d = a.uoc_tinh_muc_tieu("nang_luc")["data"]
    assert d["tot_hon"] == {"n": 0, "duoi_5": False} and d["xuong_sau"] == {"n": 0, "duoi_5": False}
    assert a.uoc_tinh_muc_tieu("co_hoi")["ok"]
    assert _foto(db) == truoc


def test_lan_chay_thu_khong_lam_moc_va_khong_them_dong(tmp_path):
    a, db = _tao(tmp_path)
    _chay(a, db, _s(*range(11, 21)) + _s(*range(1, 11)))
    assert a.run_thu({"priority": "tier"})["ok"]              # lần chạy thử MỚI NHẤT trong run_history
    truoc = _foto(db)
    d = a.uoc_tinh_muc_tieu("co_hoi")["data"]
    assert d["tot_hon"]["n"] == 10 and d["xuong_sau"]["n"] == 10   # mốc = lần CHÍNH THỨC, không phải lần thử
    assert _foto(db) == truoc


# ----- dòng kết quả -----

def _doi(db_a, db_b):
    """Độc lập: (em tốt hơn, em xuống sau) của kết quả chính thức db_b so với db_a, đếm trực tiếp trên SQL."""
    def doc(db):
        c = sqlite3.connect(db)
        try:
            return {(s, b): (cl, rk) for s, b, cl, rk in c.execute(
                "SELECT student_id, buoi, club_id, rank_in_student_pref FROM match_results")}
        finally:
            c.close()
    ra, rb = doc(db_a), doc(db_b)
    tot, xuong = set(), set()
    for k in ra:
        (ca, rka), (cb, rkb) = ra[k], rb[k]
        xa = 10 ** 6 if ca is None else (rka or 999)
        xb = 10 ** 6 if cb is None else (rkb or 999)
        (tot if xb < xa else xuong if xb > xa else set()).add(k[0])
    return tot, xuong


def test_bao_cao_danh_cho_khop_hai_lan_chay_that(tmp_path):
    nhom = (lambda i: "khoi_10" if i > 12 else "")
    a0, db0 = _tao(tmp_path, nhom=nhom, ten="goc")                      # không áp thẻ
    assert a0.run_pipeline(seed=42)["ok"]
    a1, db1 = _tao(tmp_path, nhom=nhom, ten="the")                      # áp danh_cho rồi chạy
    assert a1.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    assert a1.run_pipeline(seed=42)["ok"]
    r = a1.bao_cao_muc_tieu()
    assert r["ok"], r
    d = r["data"]
    tot, xuong = _doi(db0, db1)
    assert d["ap_dung"] and d["muc_tieu"] == "danh_cho" and d["nhom"] == "khoi_10"
    assert d["duoc_giup"] == do.an_so(len(tot)) and d["nhuong_cho"] == do.an_so(len(xuong))
    assert isinstance(d["run_id"], int)
    assert set(d["dat"]) == {"so_dat", "so_clb"} and 0 <= d["dat"]["so_dat"] <= d["dat"]["so_clb"] <= 5
    assert set(d["an_toan"]) == {"nguyen_vong_1_pct", "chua_co_cho"}


@pytest.mark.parametrize("cach", ["bo_khoa_truoc", "truoc_rong"])
def test_bao_cao_danh_cho_khong_co_cho_ban_dau_thi_khong_so_sanh(tmp_path, cach):
    """Không biết chỗ giữ nhập ban đầu thì KHÔNG được báo "0 em được giúp" như một sự thật."""
    a, db = _tao(tmp_path, nhom=lambda i: "khoi_10" if i > 12 else "")
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"] and a.run_pipeline(seed=42)["ok"]
    cfg = cau_hinh_ws.doc_cau_hinh(db)
    if cach == "bo_khoa_truoc":
        cfg["muc_tieu"].pop("truoc")
    else:
        cfg["muc_tieu"]["truoc"] = {}
    cau_hinh_ws.ghi_cau_hinh(db, cfg)
    d = a.bao_cao_muc_tieu()["data"]
    assert d["ap_dung"] is True and d["muc_tieu"] == "danh_cho"
    assert d["co_so_sanh"] is False
    for khoa in ("duoc_giup", "nhuong_cho", "nhom_duoc_giup", "an_toan_truoc"):
        assert khoa not in d, khoa
    assert set(d["dat"]) == {"so_dat", "so_clb"} and "nguyen_vong_1_pct" in d["an_toan"]


def test_bao_cao_co_hoi_khong_co_dat_va_khop_hai_lan_chay_that(tmp_path):
    a0, db0 = _tao(tmp_path, ten="goc")
    assert a0.run_pipeline(seed=42)["ok"]
    a1, db1 = _tao(tmp_path, ten="the")
    assert a1.chon_muc_tieu("co_hoi")["ok"]
    assert a1.run_pipeline(seed=42)["ok"]
    d = a1.bao_cao_muc_tieu()["data"]
    tot, xuong = _doi(db0, db1)
    assert d["muc_tieu"] == "co_hoi" and d["dat"] is None
    assert d["duoc_giup"] == do.an_so(len(tot)) and d["nhuong_cho"] == do.an_so(len(xuong))
    assert len(tot) > 0 and len(xuong) > 0


def test_bao_cao_nang_luc_chi_co_the_khong_so_sanh(tmp_path):
    a, db = _tao(tmp_path)
    assert a.chon_muc_tieu("nang_luc")["ok"] and a.run_pipeline(seed=42)["ok"]
    d = a.bao_cao_muc_tieu()["data"]
    assert d["ap_dung"] and d["muc_tieu"] == "nang_luc" and d["co_so_sanh"] is False
    assert "duoc_giup" not in d


def test_bao_cao_khong_ap_dung_khi_luat_doi_sau_lan_xep_hoac_tuy_chinh(tmp_path):
    a, db = _tao(tmp_path)
    assert a.run_pipeline(seed=42)["ok"]                      # lần xếp theo luật mặc định
    assert a.chon_muc_tieu("co_hoi")["ok"]                    # rồi mới đổi thẻ
    d = a.bao_cao_muc_tieu()["data"]
    assert d["ap_dung"] is False
    cau_hinh_ws.ghi_cau_hinh(db, cau_hinh_ws.tron_len(cau_hinh_ws.doc_cau_hinh(db), {"rules": {
        "priority": "score+tier", "tier_mode": "strict", "tiers": ["x"]}}))
    assert a.bao_cao_muc_tieu()["data"]["ap_dung"] is False


def test_bao_cao_chua_co_lan_xep_va_lan_la(tmp_path):
    a, db = _tao(tmp_path)
    assert _ma(a.bao_cao_muc_tieu()) == ["mt_chua_co_ket_qua"]
    assert a.run_pipeline(seed=42)["ok"]
    assert _ma(a.bao_cao_muc_tieu(999)) == ["gt2_lan_chay_khong_co"]
    assert a.bao_cao_muc_tieu()["ok"]


def test_bao_cao_chi_doc(tmp_path):
    a, db = _tao(tmp_path, nhom=lambda i: "khoi_10" if i > 12 else "")
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"] and a.run_pipeline(seed=42)["ok"]
    truoc = _foto(db)
    assert a.bao_cao_muc_tieu()["ok"]
    assert _foto(db) == truoc


# ----- vai -----

@pytest.mark.parametrize("ham,args", [("uoc_tinh_muc_tieu", ("co_hoi",)), ("bao_cao_muc_tieu", ())])
def test_giao_vien_bi_tu_choi(tmp_path, ham, args):
    a, db = _tao(tmp_path)
    assert a.tao_tai_khoan("quantri", MK, "quan_tri")["ok"] and a.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    assert a.dang_nhap("gv1", MK)["ok"]
    assert _ma(getattr(a, ham)(*args)) == ["gt3_khong_du_quyen"]


def test_ma_loi_moi_co_vi_va_en():
    import i18n_errors
    for ma in ("mt_cho_it", "mt_khong_co_khoang_cach", "mt_uoc_tinh_fa", "mt_chua_co_ket_qua"):
        m = i18n_errors.MESSAGES[ma]
        assert m["vi"].strip() and m["en"].strip(), ma
    assert all(m.startswith("mt_") for m in [m for m in i18n_errors.MESSAGES if not m.startswith(("cb1_", "dk_", "ct1_"))][-12:])   # khối cb1_ (CB1), dk_ (DK3), ct1_ (CT1) nối sau


def test_bao_cao_co_hoi_so_voi_luat_truoc_do_gom_ca_chia_100_diem(tmp_path, monkeypatch):
    """Mốc "không dùng thẻ" của `co_hoi` phải là cấu hình TRƯỚC khi thẻ tắt điểm chia (muc_tieu.wharton_truoc)."""
    a, db = _tao(tmp_path)
    cfg = cau_hinh_ws.doc_cau_hinh(db)
    cfg["rules"]["priority"] = "tier"                               # như sau khi chọn co_hoi
    cfg["muc_tieu"] = {"id": "co_hoi", "nhom": None, "wharton_truoc": True}
    cau_hinh_ws.ghi_cau_hinh(db, cfg)
    assert a.run_pipeline(seed=42)["ok"]
    thay = {}
    goc_fn = a._giai_gia_dinh

    def ghi(luat, seed, goc, cho):
        thay["luat"] = dict(luat)
        return goc_fn(luat, seed, goc, cho)
    monkeypatch.setattr(a, "_giai_gia_dinh", ghi)
    a.bao_cao_muc_tieu()
    assert thay["luat"]["wharton"] is True and thay["luat"]["priority"] == "score"
