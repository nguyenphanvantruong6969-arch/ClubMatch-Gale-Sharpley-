"""GT2-L3 — so sánh hai lần chạy: số liệu kiểm tay trên 10 em, cùng lần với chính nó = 0 thay đổi, danh sách
em đổi chỗ = so trực tiếp, lần chính thức cũ bị từ chối, xuất HTML ngoại tuyến + CSV có BOM.

Dữ liệu MÔ PHỎNG."""

import os
import sqlite3
import sys


import api as api_mod
import cau_hinh_ws
import tieu_chi

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

BUOI = "b1"
HS = {"s%d" % i: {"ten": "Em %d" % i, "lop": "10A" if i <= 5 else "10B", "nhom": "G1" if i <= 4 else ""}
      for i in range(1, 11)}
CLB = {"X": {"ten": "CLB X", "capacity": 5}, "Y": {"ten": "CLB Y", "capacity": 5}}
DIEM = {"X": {"s1": 80, "s2": 70, "s3": 60, "s5": 90, "s6": 50},
        "Y": {"s4": 75, "s7": 55, "s9": 65, "s2": 40}}
A_ROWS = [("s1", BUOI, "X", 1), ("s2", BUOI, "X", 1), ("s3", BUOI, "X", 2), ("s4", BUOI, "Y", 1),
          ("s5", BUOI, "Y", 3), ("s6", BUOI, "X", 1), ("s7", BUOI, "Y", 2), ("s8", BUOI, "Y", 1),
          ("s9", BUOI, None, None), ("s10", BUOI, None, None)]
B_ROWS = [("s1", BUOI, "X", 1), ("s2", BUOI, "Y", 2), ("s3", BUOI, "X", 2), ("s4", BUOI, "Y", 1),
          ("s5", BUOI, "X", 1), ("s6", BUOI, "X", 1), ("s7", BUOI, "Y", 2), ("s8", BUOI, None, None),
          ("s9", BUOI, "Y", 4), ("s10", BUOI, None, None)]
CTX = {"students": HS, "clubs": CLB, "diem": DIEM, "tiers": ["G1"]}


def _lan(nhan, run_id, rows):
    return {"nhan": nhan, "run_id": run_id, "luat": {}, "rows": rows}


def test_so_lieu_kiem_tay_10_em():
    kq = tieu_chi.so_sanh_lan_chay(_lan("chinh_thuc", 1, A_ROWS), _lan("thu", 2, B_ROWS), CTX)
    ta, tb = kq["tong"]["a"], kq["tong"]["b"]
    assert (ta["n"], ta["da_xep"], ta["chua_xep"], ta["pct_da_xep"], ta["pct_nv1"], ta["pct_top3"],
            ta["hang_tb"]) == (10, 8, 2, 80.0, 50.0, 80.0, 1.5)
    assert (tb["n"], tb["da_xep"], tb["chua_xep"], tb["pct_da_xep"], tb["pct_nv1"], tb["pct_top3"],
            tb["hang_tb"]) == (10, 8, 2, 80.0, 40.0, 70.0, 1.75)
    clb = {c["club_id"]: c for c in kq["clb"]}
    assert (clb["X"]["a"], clb["X"]["b"]) == ({"da_nhan": 4, "diem_chuan": 50}, {"da_nhan": 4, "diem_chuan": 50})
    assert (clb["Y"]["a"], clb["Y"]["b"]) == ({"da_nhan": 4, "diem_chuan": 55}, {"da_nhan": 4, "diem_chuan": 40})
    assert clb["X"]["suc_chua"] == 5
    nhom = {x["khoa"]: x for x in kq["nhom"]}
    assert [x["khoa"] for x in kq["nhom"]] == ["G1", ""]            # đúng thứ tự `tiers`
    assert (nhom["G1"]["a"]["pct_da_xep"], nhom["G1"]["a"]["pct_nv1"]) == (100.0, 75.0)
    assert (nhom["G1"]["b"]["pct_da_xep"], nhom["G1"]["b"]["pct_nv1"]) == (100.0, 50.0)
    assert (nhom[""]["a"]["pct_da_xep"], nhom[""]["a"]["pct_nv1"]) == (66.7, 33.3)
    assert (nhom[""]["b"]["pct_da_xep"], nhom[""]["b"]["pct_nv1"]) == (66.7, 33.3)
    lop = {x["khoa"]: x for x in kq["lop"]}
    assert (lop["10A"]["a"]["pct_da_xep"], lop["10A"]["a"]["pct_nv1"]) == (100.0, 60.0)
    assert (lop["10A"]["b"]["pct_da_xep"], lop["10A"]["b"]["pct_nv1"]) == (100.0, 60.0)
    assert (lop["10B"]["a"]["pct_da_xep"], lop["10B"]["a"]["pct_nv1"]) == (60.0, 40.0)
    assert (lop["10B"]["b"]["pct_da_xep"], lop["10B"]["b"]["pct_nv1"]) == (60.0, 20.0)
    assert kq["so_doi"] == 4
    assert [(x["student_id"], x["tu"], x["den"]) for x in kq["doi"]] == [
        ("s2", "X", "Y"), ("s5", "Y", "X"), ("s8", "Y", None), ("s9", None, "Y")]
    assert kq["doi"][0]["ten"] == "Em 2" and kq["doi"][0]["lop"] == "10A"


def test_cung_lan_voi_chinh_no_khong_doi_gi():
    kq = tieu_chi.so_sanh_lan_chay(_lan("thu", 3, A_ROWS), _lan("thu", 3, A_ROWS), CTX)
    assert kq["so_doi"] == 0 and kq["doi"] == [] and kq["tong"]["a"] == kq["tong"]["b"]


def test_chi_so_buoi_ca_hai_cung_co():
    b_mot_buoi = [("s1", "b2", "X", 1)]
    kq = tieu_chi.so_sanh_lan_chay(_lan("chinh_thuc", 1, A_ROWS + b_mot_buoi), _lan("thu", 2, B_ROWS), CTX)
    assert kq["buoi_chung"] == [BUOI] and kq["tong"]["a"]["n"] == 10


# ---- API + xuất tệp -------------------------------------------------------------------------
def _mo(tmp_path, tep):
    db = d.nap_bo(str(tmp_path), tep)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    a = api_mod.PipelineAPI(db)
    assert a.run_pipeline(seed=42)["ok"]
    return a, db


def _sql(db, cau, tham=()):
    c = sqlite3.connect(db)
    try:
        return c.execute(cau, tham).fetchall()
    finally:
        c.close()


def test_api_danh_sach_doi_bang_so_truc_tiep_va_khong_ghi(tmp_path):
    a, db = _mo(tmp_path, d.BO_DU_LIEU[0][1])
    r = a.run_thu({"priority": "tier"})
    assert r["ok"], r
    rid = r["data"]["run_id"]
    truoc = _sql(db, "SELECT COUNT(*) FROM run_history")
    so = a.so_sanh_lan_chay(rid)
    assert so["ok"], so
    chinh = {(s, b): c for s, b, c in _sql(db, "SELECT student_id, buoi, club_id FROM match_results")}
    thu = {(s, b): c for s, b, c in _sql(db, "SELECT student_id, buoi, club_id FROM ket_qua_thu WHERE run_id = ?",
                                         (rid,))}
    truc_tiep = sorted((k[0], k[1], thu.get(k), chinh.get(k)) for k in set(chinh) | set(thu)
                       if thu.get(k) != chinh.get(k))
    assert sorted((x["student_id"], x["buoi"], x["tu"], x["den"]) for x in so["data"]["doi"]) == truc_tiep
    assert so["data"]["a"]["nhan"] == "thu" and so["data"]["b"]["nhan"] == "chinh_thuc"
    assert _sql(db, "SELECT COUNT(*) FROM run_history") == truoc


def test_api_chay_thu_giong_luat_da_luu_khong_doi(tmp_path):
    a, db = _mo(tmp_path, d.BO_DU_LIEU[0][1])
    rid = a.run_thu({})["data"]["run_id"]
    so = a.so_sanh_lan_chay(rid)["data"]
    assert so["so_doi"] == 0 and so["tong"]["a"] == so["tong"]["b"]
    moi = a.list_lan_chay()["data"]
    assert moi["chinh_thuc"]["nhan"] == "chinh_thuc" and [x["run_id"] for x in moi["thu"]] == [rid]


def test_api_lan_khong_co_va_lan_chinh_thuc_cu_bi_tu_choi(tmp_path):
    a, db = _mo(tmp_path, d.BO_DU_LIEU[0][1])
    cu = _sql(db, "SELECT MAX(run_id) FROM run_history")[0][0]
    r = a.so_sanh_lan_chay(9999)
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_lan_chay_khong_co"
    assert a.so_sanh_lan_chay("x")["errors"][0]["code"] == "gt2_lan_chay_khong_co"
    assert a.run_pipeline(seed=42)["ok"]            # lần chính thức thứ hai thay lần đầu
    r = a.so_sanh_lan_chay(cu)
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_so_sanh_lan_cu"


def test_api_chua_co_lan_chinh_thuc(tmp_path):
    db = d.nap_bo(str(tmp_path), d.BO_DU_LIEU[0][1])
    a = api_mod.PipelineAPI(db)
    r = a.so_sanh_lan_chay(1)
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_chua_co_lan_chinh_thuc"


def test_xuat_html_ngoai_tuyen_va_csv_co_bom(tmp_path):
    a, db = _mo(tmp_path, d.BO_DU_LIEU[0][1])
    rid = a.run_thu({"priority": "tier"})["data"]["run_id"]
    h = a.export_so_sanh_html(str(tmp_path / "ss.html"), rid)
    assert h["ok"], h
    txt = open(h["data"]["path"], encoding="utf-8").read()
    assert "<html" in txt and "http://" not in txt and "https://" not in txt and "<script" not in txt
    assert "Chạy thử số %d" % rid in txt and "Chính thức số" in txt
    c = a.export_so_sanh_csv(str(tmp_path / "ss.csv"), rid)
    assert c["ok"], c
    raw = open(c["data"]["path"], "rb").read()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert len(raw.decode("utf-8-sig").strip().splitlines()) == 1 + c["data"]["so_doi"]
    assert not a.export_so_sanh_html(str(tmp_path / "x.html"), 9999)["ok"]


def test_html_thoat_ky_tu_nguy_hiem():
    hs = {"s1": {"ten": "<img src=x onerror=alert(1)>", "lop": "10A", "nhom": ""}}
    kq = tieu_chi.so_sanh_lan_chay(
        _lan("chinh_thuc", 1, [("s1", BUOI, "X", 1)]), _lan("thu", 2, [("s1", BUOI, "Y", 1)]),
        {"students": hs, "clubs": CLB, "diem": {}, "tiers": []})
    out = tieu_chi.dung_html_so_sanh(kq)
    assert "<img" not in out and "&lt;img" in out
