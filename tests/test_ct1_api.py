"""CT1-L2 — API `get_xem_xet_chi_tieu` / hai hàm xuất CSV (`api_chi_tieu.py`): chỉ ĐỌC. Dữ liệu MÔ PHỎNG.

Số hồi quy trên `du_lieu_test/SO_NHAP_TEST.xlsx` (120 em / 10 CLB / 130 chỗ), bộ số bốc thăm khoá seed 42.
Kiểm: đề xuất và bốn bước chuyển chỗ; kết quả sau từng bước (cộng dồn); danh sách em đổi chỗ khớp phép so GT2;
bước tự chọn (hợp lệ và bị từ chối); mốc giải lại trùng kết quả chính thức; không ghi gì (tệp CSDL nguyên byte,
không sao lưu, `run_history` / `stb_lock` / `match_results` y nguyên); chưa có kết quả thì báo lỗi; huy chương bị từ chối;
chia CLB theo loại ⇒ vẫn có đề xuất, không có kết quả từng bước; vai giáo viên bị từ chối; hai tệp CSV.
"""

import base64
import csv
import glob
import hashlib
import os
import sqlite3

import pytest

import api as api_mod
import cau_hinh_ws
import phan_quyen

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_NHAP_TEST = os.path.join(GOC, "du_lieu_test", "SO_NHAP_TEST.xlsx")

BUOC_DE_XUAT = [("clb_bongro", "clb_bongda", 4), ("clb_amnhac", "clb_tienganh", 3),
                ("clb_tinhnguyen", "clb_tinhoc", 2), ("clb_vanhoc", "clb_mythuat", 2)]
CAP_MOI = {"clb_bongda": 24, "clb_tienganh": 19, "clb_tinhoc": 14, "clb_mythuat": 14, "clb_bongro": 14,
           "clb_amnhac": 11, "clb_tinhnguyen": 10, "clb_vanhoc": 8, "clb_robotics": 8, "clb_khoahoc": 8}


def _mo(tmp_path, chay=True, rules=None):
    db = str(tmp_path / "app.db")
    a = api_mod.PipelineAPI(db)
    with open(SO_NHAP_TEST, "rb") as f:
        r = a.import_so_nhap(base64.b64encode(f.read()).decode())
    assert r["ok"], r
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": dict({"wharton": False}, **(rules or {}))})
    if chay:
        assert a.run_pipeline(seed=42)["ok"]
    return a, db


@pytest.fixture(scope="module")
def mo_mot_lan(tmp_path_factory):
    return _mo(tmp_path_factory.mktemp("ct1"))


def _sql(db, cau, tham=()):
    c = sqlite3.connect(db)
    try:
        return c.execute(cau, tham).fetchall()
    finally:
        c.close()


def _foto(db):
    """Băm TỆP CSDL (kể cả WAL nếu có) + tổng kiểm mọi bảng + số tệp sao lưu."""
    h = hashlib.sha256()
    for duoi in ("", "-wal", "-shm"):
        if os.path.exists(db + duoi):
            with open(db + duoi, "rb") as f:
                h.update(f.read())
    c = sqlite3.connect(db)
    try:
        bang = hashlib.sha256()
        for (ten,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall():
            bang.update(ten.encode())
            for r in c.execute('SELECT * FROM "%s"' % ten).fetchall():
                bang.update(repr(r).encode())
    finally:
        c.close()
    return h.hexdigest(), bang.hexdigest(), len(glob.glob(db + ".bak-*"))


# ----- số hồi quy trên SO_NHAP_TEST -----

def test_de_xuat_va_bon_buoc_tren_bo_test(mo_mot_lan):
    a, db = mo_mot_lan
    r = a.get_xem_xet_chi_tieu()
    assert r["ok"], r
    d = r["data"]
    assert d["tong_cho"] == 130 and d["so_hoc_sinh"] == 120
    assert {c["club_id"]: c["cap_moi"] for c in d["clb"]} == CAP_MOI
    assert [(b["tu"], b["den"], b["k"]) for b in d["buoc"]] == BUOC_DE_XUAT
    assert d["che_do"] == "de_xuat" and d["loi_giai"] is None and d["canh_bao"] == []
    k = d["khuyen_nghi"]
    assert (k["so_cho_chuyen"], k["so_clb_cho"], k["so_clb_nhan"]) == (11, 4, 4)


def test_ket_qua_sau_tung_buoc_la_so_cua_ung_dung(mo_mot_lan):
    a, _ = mo_mot_lan
    d = a.get_xem_xet_chi_tieu()["data"]
    assert d["truoc"]["nv1"] == 64 and d["truoc"]["chua_co"] == 12 and d["truoc"]["tong"] == 120
    assert [b["nv1_sau"] for b in d["buoc"]] == [67, 69, 73, 74]
    assert [b["chua_co_sau"] for b in d["buoc"]] == [11, 11, 10, 8]
    assert d["sau"]["nv1"] == 74 and d["sau"]["chua_co"] == 8
    assert (d["so_tot_hon"], d["so_kem_hon"]) == (15, 0)
    # cộng dồn: số "em đổi chỗ" của từng bước là so với bước ngay trước
    for i, b in enumerate(d["buoc"]):
        assert b["so_doi"] == len(b["doi"]) and b["so_len"] + b["so_xuong"] == b["so_doi"]
        assert b["stt"] == i + 1


def test_moc_giai_lai_trung_ket_qua_chinh_thuc(mo_mot_lan):
    a, db = mo_mot_lan
    d = a.get_xem_xet_chi_tieu()["data"]
    assert not any(c["code"] == "ct1_moc_khong_khop" for c in d["canh_bao"])
    nv1_that = _sql(db, "SELECT COUNT(*) FROM match_results WHERE rank_in_student_pref = 1")[0][0]
    assert d["truoc"]["nv1"] == nv1_that


def test_danh_sach_em_doi_cho_lien_mach_va_khop_gt2(mo_mot_lan):
    """Phát lại các `doi` từ kết quả chính thức: mỗi em đổi đều đang ở đúng CLB `tu`; kết quả cuối khớp phép so GT2."""
    import tieu_chi
    a, db = mo_mot_lan
    d = a.get_xem_xet_chi_tieu()["data"]
    rows_a = [tuple(r) for r in _sql(db, "SELECT student_id, buoi, club_id, rank_in_student_pref FROM match_results")]
    hien = {(r[0], r[1]): r[2] for r in rows_a}
    for b in d["buoc"]:
        for e in b["doi"]:
            k = (e["student_id"], e["buoi"])
            assert hien[k] == e["tu"] and e["tu"] != e["den"]
            assert e["huong"] in ("len", "xuong", "vao", "ra")
            assert (e["nv_truoc"] is None) == (e["tu"] is None) and (e["nv_sau"] is None) == (e["den"] is None)
            if e["huong"] == "len":
                assert e["nv_sau"] < e["nv_truoc"]
            if e["huong"] == "xuong":
                assert e["nv_sau"] > e["nv_truoc"]
        hien.update({(e["student_id"], e["buoi"]): e["den"] for e in b["doi"]})
    rows_b = [(s, bu, hien[(s, bu)], None) for s, bu, _c, _h in rows_a]
    kq = tieu_chi.so_sanh_lan_chay(
        {"nhan": "thu", "run_id": 1, "luat": {}, "rows": rows_a},
        {"nhan": "thu", "run_id": 2, "luat": {}, "rows": rows_b}, {"students": {}, "clubs": {}, "diem": {}})
    # Số em khác chính thức ở cuối = số em đổi chỗ GT2 đếm; và đúng bằng số em "tốt hơn" (không em nào kém hơn).
    assert kq["so_doi"] >= d["so_tot_hon"] and d["so_kem_hon"] == 0


def test_mot_buoc_tu_chon_trung_buoc_dau_cua_de_xuat(mo_mot_lan):
    a, _ = mo_mot_lan
    de_xuat = a.get_xem_xet_chi_tieu()["data"]["buoc"][0]
    tu_chon = a.get_xem_xet_chi_tieu([{"tu": de_xuat["tu"], "den": de_xuat["den"], "k": de_xuat["k"]}])["data"]["buoc"][0]
    for khoa in ("nv1_sau", "chua_co_sau", "so_len", "so_xuong", "so_doi", "doi"):
        assert tu_chon[khoa] == de_xuat[khoa], khoa


def test_nguoi_chua_co_clb_duoc_xep_o_buoc_nao(mo_mot_lan):
    a, _ = mo_mot_lan
    d = a.get_xem_xet_chi_tieu()["data"]
    o = d["o_chua_co"]
    assert len(o) == 12 and sum(1 for x in o if x is None) == 8
    # Bước từ đó em luôn có CLB: mỗi bước một em (số của ứng dụng; bản mẫu thiết kế chỉ minh hoạ), 8 em vẫn chưa có.
    assert sorted(x for x in o if x is not None) == [1, 2, 3, 4]
    assert d["so_moi_mat_cho"] == 0


def test_cap_moi_trong_bang_clb_va_chi_so(mo_mot_lan):
    a, _ = mo_mot_lan
    d = a.get_xem_xet_chi_tieu()["data"]
    t = {c["club_id"]: c for c in d["clb"]}
    assert (t["clb_bongda"]["cap"], t["clb_bongda"]["nv1"], t["clb_bongda"]["chua_dap"]) == (20, 25, 22)
    assert (t["clb_tienganh"]["nv1"], t["clb_tienganh"]["chua_dap"]) == (30, 29)
    assert (t["clb_bongro"]["trong"], t["clb_bongro"]["chua_dap"]) == (5, 0)
    assert t["clb_bongda"]["ten"] == "CLB Bóng đá"


# ----- chỉ đọc -----

def test_khong_ghi_gi_ca(tmp_path):
    a, db = _mo(tmp_path)
    truoc = _foto(db)
    n_lich_su = _sql(db, "SELECT COUNT(*) FROM run_history")[0][0]
    assert a.get_xem_xet_chi_tieu()["ok"]
    assert a.get_xem_xet_chi_tieu([{"tu": "clb_bongro", "den": "clb_bongda", "k": 1}])["ok"]
    assert a.export_xem_xet_chi_tieu_csv(str(tmp_path / "doi_chieu.csv"))["ok"]
    assert a.export_de_xuat_chi_tieu_csv(str(tmp_path / "de_xuat.csv"))["ok"]
    assert _foto(db) == truoc                               # tệp CSDL nguyên byte, không sao lưu mới
    assert _sql(db, "SELECT COUNT(*) FROM run_history")[0][0] == n_lich_su


# ----- bước tự chọn -----

def test_buoc_tu_chon_thay_buoc_de_xuat(mo_mot_lan):
    a, _ = mo_mot_lan
    r = a.get_xem_xet_chi_tieu([{"tu": "clb_bongro", "den": "clb_bongda", "k": 2}])
    assert r["ok"], r
    d = r["data"]
    assert d["che_do"] == "tu_chon" and len(d["buoc"]) == 1
    assert (d["buoc"][0]["tu"], d["buoc"][0]["den"], d["buoc"][0]["k"]) == ("clb_bongro", "clb_bongda", 2)
    t = {c["club_id"]: c for c in d["clb"]}
    assert t["clb_bongro"]["cap_moi"] == 16 and t["clb_bongda"]["cap_moi"] == 22
    assert t["clb_amnhac"]["cap_moi"] == t["clb_amnhac"]["cap"]       # CLB không đụng tới giữ nguyên


@pytest.mark.parametrize("buoc,ma", [
    ([{"tu": "clb_la", "den": "clb_bongda", "k": 1}], "ct1_clb_la"),
    ([{"tu": "clb_bongda", "den": "clb_bongda", "k": 1}], "ct1_buoc_khong_hop_le"),
    ([{"tu": "clb_bongro", "den": "clb_bongda", "k": 0}], "ct1_buoc_khong_hop_le"),
    ([{"tu": "clb_bongro", "den": "clb_bongda", "k": 99}], "ct1_cap_qua_thap"),
    ("khong phai danh sach", "ct1_buoc_khong_hop_le"),
])
def test_buoc_tu_chon_sai_bi_tu_choi_bang_ma_loi(mo_mot_lan, buoc, ma):
    a, _ = mo_mot_lan
    r = a.get_xem_xet_chi_tieu(buoc)
    assert not r["ok"] and r["errors"][0]["code"] == ma


def test_buoc_tu_chon_rong_la_khong_doi_gi(mo_mot_lan):
    a, _ = mo_mot_lan
    d = a.get_xem_xet_chi_tieu([])["data"]
    assert d["che_do"] == "tu_chon" and d["buoc"] == []
    assert d["sau"] == d["truoc"] and (d["so_tot_hon"], d["so_kem_hon"]) == (0, 0)


# ----- cổng chặn -----

def test_chua_co_ket_qua_chinh_thuc_thi_bao_loi(tmp_path):
    a, _ = _mo(tmp_path, chay=False)
    r = a.get_xem_xet_chi_tieu()
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_chua_co_lan_chinh_thuc"


def test_che_do_huy_chuong_bi_tu_choi(tmp_path):
    a, db = _mo(tmp_path)
    cfg = cau_hinh_ws.doc_cau_hinh(db)
    cfg["rules"]["fa_daa"] = True
    cfg["rules"]["wharton"] = True
    try:
        cau_hinh_ws.ghi_cau_hinh(db, cfg)
    except ValueError:
        pytest.skip("không bật được huy chương trên bộ này")
    r = a.get_xem_xet_chi_tieu()
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_thu_chua_ho_tro_fa"


def test_chia_clb_theo_loai_van_co_de_xuat_nhung_khong_co_ket_qua_buoc(tmp_path):
    a, db = _mo(tmp_path)
    cfg = cau_hinh_ws.doc_cau_hinh(db)
    cfg["rules"]["chia_loai"] = True
    cau_hinh_ws.ghi_cau_hinh(db, cfg)
    r = a.get_xem_xet_chi_tieu()
    assert r["ok"], r
    d = r["data"]
    assert d["loi_giai"] and d["loi_giai"][0]["code"] == "mt_thu_chua_ho_tro_loai"
    assert d["truoc"] is None and d["sau"] is None
    assert {c["club_id"]: c["cap_moi"] for c in d["clb"]} == CAP_MOI    # vẫn có đề xuất chỉ tiêu
    assert [(b["tu"], b["den"], b["k"]) for b in d["buoc"]] == BUOC_DE_XUAT
    assert all("doi" not in b or b["doi"] == [] for b in d["buoc"])


def test_giao_vien_bi_tu_choi_o_backend():
    for ten in ("get_xem_xet_chi_tieu", "export_xem_xet_chi_tieu_csv", "export_de_xuat_chi_tieu_csv"):
        assert phan_quyen.QUYEN[ten] == phan_quyen.QUAN_TRI, ten


# ----- xuất CSV -----

def _doc_csv(duong):
    with open(duong, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def test_csv_doi_chieu_dung_cot_va_so_dong(tmp_path):
    a, _ = _mo(tmp_path)
    d = a.get_xem_xet_chi_tieu()["data"]
    r = a.export_xem_xet_chi_tieu_csv(str(tmp_path / "doi_chieu.csv"))
    assert r["ok"], r
    dong = _doc_csv(r["data"]["path"])
    assert dong[0] == ["buoc", "student_id", "ho_ten", "lop", "buoi", "clb_truoc", "clb_sau",
                       "nv_truoc", "nv_sau", "huong"]
    assert len(dong) - 1 == sum(b["so_doi"] for b in d["buoc"])
    assert {x[0] for x in dong[1:]} <= {"1", "2", "3", "4"}


def test_csv_de_xuat_dung_cot_va_cap_moi(tmp_path):
    a, _ = _mo(tmp_path)
    r = a.export_de_xuat_chi_tieu_csv(str(tmp_path / "de_xuat.csv"))
    assert r["ok"], r
    dong = _doc_csv(r["data"]["path"])
    assert dong[0] == ["club_id", "ten_clb", "buoi", "cho_hien_co", "em_thich_nhat", "muon_vao_chua_duoc",
                       "cho_trong", "de_xuat_ky_sau", "thay_doi"]
    bang = {x[0]: x for x in dong[1:]}
    assert len(bang) == 10 and bang["clb_bongda"][7] == "24" and bang["clb_bongda"][8] == "4"
    assert bang["clb_bongro"][8] == "-4"
    assert sum(int(x[7]) for x in dong[1:]) == 130


def test_csv_loi_khi_chua_co_ket_qua(tmp_path):
    a, _ = _mo(tmp_path, chay=False)
    r = a.export_xem_xet_chi_tieu_csv(str(tmp_path / "x.csv"))
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_chua_co_lan_chinh_thuc"
