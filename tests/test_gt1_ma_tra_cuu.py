"""GT1-L4: mã tra cứu (`tao_ma_tra_cuu`, `tao_lai_ma_tra_cuu`, `export_ma_tra_cuu_csv`, `tra_cuu_hoc_sinh`). Dữ liệu MÔ PHỎNG.

Mã duy nhất, đúng bảng chữ, ổn định trừ khi tạo lại; mã sai -> không lộ dữ liệu (và sai mã = em lạ, cùng một lỗi);
lần sai thứ 6 trong 60 giây -> khoá tạm; mã đúng -> chỉ dữ liệu của em đó; tạo mã không đụng match_results,
stb_lock, run_history; phiếu in mã của chính em.
"""

import csv
import re


from _fa import dung_fa_clb
from _wharton import tat_wharton

ALPHABET = set("ABCDEFGHJKMNPQRSTUVWXYZ23456789")
HS = {"s1": ("Nguyễn Văn Ánh", "10A1"), "s2": ("Trần Thị Bé", "10A2"), "s3": ("Lê Đức Cường", "10A1")}


def _dung(api, chay=True):
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
    for sid, (ten, _) in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    with api._ket_noi_ghi() as cur:
        for sid, (_, lop) in HS.items():
            cur.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (lop, sid))
    if chay:
        assert api.run_pipeline(seed=3)["ok"]


def _ma(api):
    with api._ket_noi_doc() as cur:
        return dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))


class Dong:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def test_ma_duy_nhat_dung_bang_chu_va_on_dinh(api):
    _dung(api)
    r = api.tao_ma_tra_cuu()
    assert r["ok"] and r["data"]["n_tao"] == 3
    ma = _ma(api)
    assert set(ma) == set(HS)
    assert len(set(ma.values())) == 3
    for m in ma.values():
        assert len(m) == 8 and set(m) <= ALPHABET
    r2 = api.tao_ma_tra_cuu()                       # chạy lại: không đổi mã đã có
    assert r2["data"]["n_tao"] == 0 and _ma(api) == ma
    r3 = api.tao_ma_tra_cuu(chi_hs_chua_co=False)   # tạo lại tất cả
    assert r3["data"]["n_tao"] == 3 and all(_ma(api)[s] != ma[s] for s in HS)


def test_tao_lai_mot_em_va_em_la(api):
    _dung(api)
    api.tao_ma_tra_cuu()
    cu = _ma(api)
    r = api.tao_lai_ma_tra_cuu("s2")
    assert r["ok"]
    moi = _ma(api)
    assert moi["s2"] != cu["s2"] and moi["s1"] == cu["s1"] and moi["s3"] == cu["s3"]
    assert api.tao_lai_ma_tra_cuu("khong_co")["errors"][0]["code"] == "gt1_khong_co_hoc_sinh"


def test_tra_cuu_dung_ma_chi_tra_du_lieu_cua_em_do(api):
    _dung(api)
    api.tao_ma_tra_cuu()
    ma = _ma(api)
    for sid, (ten, _) in HS.items():
        r = api.tra_cuu_hoc_sinh(sid, " " + ma[sid].lower() + " ")      # bỏ khoảng trắng, không phân biệt hoa thường
        assert r["ok"], r
        assert r["data"]["student_id"] == sid and r["data"]["ten"] == ten
        txt = repr(r["data"])
        for khac, (ten_k, _) in HS.items():
            if khac != sid:
                assert ten_k not in txt and ma[khac] not in txt
        assert ma[sid] not in txt                                    # không trả lại chính mã


def test_sai_ma_khong_lo_du_lieu_va_em_la_cung_loi(api):
    _dung(api)
    api.tao_ma_tra_cuu()
    a = api.tra_cuu_hoc_sinh("s1", "AAAAAAAA")
    b = api.tra_cuu_hoc_sinh("khong_co", "AAAAAAAA")
    c = api.tra_cuu_hoc_sinh("s1", "")
    for r in (a, b, c):
        assert not r["ok"]
        assert [e["code"] for e in r["errors"]] == ["gt1_ma_sai"]
    assert "Nguyễn" not in repr(a)


def test_em_chua_co_ma_bi_tu_choi_nhu_ma_sai(api):
    _dung(api)
    r = api.tra_cuu_hoc_sinh("s1", "ABCDEFGH")
    assert [e["code"] for e in r["errors"]] == ["gt1_ma_sai"]


def test_khoa_tam_sau_5_lan_sai_va_mo_lai_sau_60_giay(api):
    _dung(api)
    api.tao_ma_tra_cuu()
    ma = _ma(api)
    dong = Dong()
    api._gt1_dong_ho = dong
    for _ in range(5):
        assert api.tra_cuu_hoc_sinh("s1", "AAAAAAAA")["errors"][0]["code"] == "gt1_ma_sai"
    r = api.tra_cuu_hoc_sinh("s1", ma["s1"])                  # đã khoá: mã đúng cũng không vào
    assert r["errors"][0]["code"] == "gt1_tam_khoa"
    assert api.tra_cuu_hoc_sinh("s2", ma["s2"])["ok"]         # khoá theo từng em
    dong.t += 59
    assert api.tra_cuu_hoc_sinh("s1", ma["s1"])["errors"][0]["code"] == "gt1_tam_khoa"
    dong.t += 2
    assert api.tra_cuu_hoc_sinh("s1", ma["s1"])["ok"]
    # đúng thì đếm lại từ đầu
    for _ in range(4):
        api.tra_cuu_hoc_sinh("s1", "AAAAAAAA")
    assert api.tra_cuu_hoc_sinh("s1", ma["s1"])["ok"]
    for _ in range(4):
        assert api.tra_cuu_hoc_sinh("s1", "AAAAAAAA")["errors"][0]["code"] == "gt1_ma_sai"


def test_tao_ma_khong_doi_ket_qua_stb_va_lich_su(api):
    _dung(api)

    def chup():
        with api._ket_noi_doc() as cur:
            return [
                cur.execute("SELECT * FROM match_results ORDER BY student_id, buoi").fetchall(),
                cur.execute("SELECT * FROM stb_lock").fetchall(),
                cur.execute("SELECT * FROM stb_buoi ORDER BY 1, 2").fetchall(),
                cur.execute("SELECT * FROM run_history ORDER BY run_id").fetchall(),
            ]
    truoc = [[tuple(r) for r in x] for x in chup()]
    api.tao_ma_tra_cuu()
    api.tao_lai_ma_tra_cuu("s1")
    api.export_ma_tra_cuu_csv("")
    assert [[tuple(r) for r in x] for x in chup()] == truoc


def test_export_csv_va_loc_lop(api, tmp_path):
    _dung(api)
    r0 = api.export_ma_tra_cuu_csv(str(tmp_path / "ma.csv"))
    assert not r0["ok"] and r0["errors"][0]["code"] == "gt1_chua_co_ma"
    api.tao_ma_tra_cuu()
    ma = _ma(api)
    r = api.export_ma_tra_cuu_csv(str(tmp_path / "ma.csv"))
    assert r["ok"] and r["data"]["n_dong"] == 3
    with open(r["data"]["path"], encoding="utf-8-sig", newline="") as f:
        dong = list(csv.reader(f))
    assert dong[0] == ["student_id", "name", "class", "code"]
    assert {d[0]: (d[1], d[2], d[3]) for d in dong[1:]} == {s: (HS[s][0], HS[s][1], ma[s]) for s in HS}
    r2 = api.export_ma_tra_cuu_csv(str(tmp_path / "lop.csv"), lop="10A2")
    assert r2["ok"] and r2["data"]["n_dong"] == 1
    r3 = api.export_ma_tra_cuu_csv(str(tmp_path / "x.csv"), lop="99Z")
    assert r3["errors"][0]["code"] == "gt1_khong_co_hoc_sinh"


def test_phieu_in_ma_cua_chinh_em(api, tmp_path):
    _dung(api)
    api.tao_ma_tra_cuu()
    ma = _ma(api)
    r = api.export_phieu_giai_trinh(str(tmp_path / "p.html"))
    assert r["ok"]
    html = open(r["data"]["path"], encoding="utf-8").read()
    trang = re.findall(r'<section class="trang">(.*?)</section>', html, flags=re.S)
    assert len(trang) == 3
    for t in trang:
        sid = re.search(r"<b>Mã:</b> (\w+) ", t).group(1)
        assert "Mã tra cứu: %s" % ma[sid] in t
        assert sum(m in t for m in ma.values()) == 1


def test_phieu_khong_ma_thi_chua_co_dong_ma(api, tmp_path):
    _dung(api)
    r = api.export_phieu_giai_trinh(str(tmp_path / "p.html"))
    assert "Mã tra cứu:" not in open(r["data"]["path"], encoding="utf-8").read()


def test_xoa_hoc_sinh_xoa_ma(api):
    _dung(api, chay=False)
    api.tao_ma_tra_cuu()
    assert api.delete_student("s3")["ok"]
    assert set(_ma(api)) == {"s1", "s2"}
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    assert _ma(api) == {}


def test_chua_chay_thi_tra_cuu_dung_ma_bao_chua_chay(api):
    _dung(api, chay=False)
    api.tao_ma_tra_cuu()
    ma = _ma(api)
    assert api.tra_cuu_hoc_sinh("s1", ma["s1"])["errors"][0]["code"] == "gt1_chua_chay"


def test_bang_la_idempotent(api):
    with api._ket_noi_doc() as cur:
        cols = [r[1] for r in cur.execute("PRAGMA table_info(ma_tra_cuu)")]
    assert cols == ["student_id", "ma", "tao_luc"]
