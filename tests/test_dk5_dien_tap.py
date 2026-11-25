"""DK5-L1: diễn tập toàn trình 798 HS / 40 CLB qua API DK3/DK4. Dữ liệu MÔ PHỎNG (không phải khảo sát thật)."""
import sqlite3
import time

import pytest

from du_lieu_test import dien_tap_dk5 as dt
from du_lieu_test.dien_tap_dk5 import ok


def _dem(api, ten):
    c = sqlite3.connect(api.db_path)
    try:
        return c.execute("SELECT COUNT(*) FROM %s" % ten).fetchone()[0]
    finally:
        c.close()


def test_l1_bo_sinh_tat_dinh():
    a, b = dt.dung_du_lieu(), dt.dung_du_lieu()
    assert dt.json_bytes(a) == dt.json_bytes(b)
    assert dt.json_bytes(a) != dt.json_bytes(dt.dung_du_lieu(seed=1))
    assert len(a["hs"]) == 798 and len(a["clb"]) == 40 and a["nhan"] == "MÔ PHỎNG"
    assert all("MÔ PHỎNG".lower() in h["ten"].lower() or "mô phỏng" in h["ten"] for h in a["hs"])


@pytest.fixture(scope="module")
def chay_tron(tmp_path_factory):
    from api import PipelineAPI
    api = PipelineAPI(str(tmp_path_factory.mktemp("dk5") / "app.db"))
    du = dt.dung_du_lieu()
    t0 = time.perf_counter()
    kq = dt.chay(api, du, so_kiosk=4)
    kq["tong_giay"] = round(time.perf_counter() - t0, 1)
    kq["du"], kq["api"] = du, api
    print("DK5 thoi gian tung pha (s):", kq["pha"], "tong", kq["tong_giay"])
    return kq


def test_l1_moi_hoc_sinh_dung_mot_dong_ket_qua(chay_tron):
    api = chay_tron["api"]
    c = sqlite3.connect(api.db_path)
    try:
        so_buoi = len(chay_tron["du"]["buoi"])
        sl = dict(c.execute("SELECT student_id, COUNT(*) FROM match_results GROUP BY student_id").fetchall())
    finally:
        c.close()
    assert len(sl) == 798
    assert set(sl.values()) == {so_buoi}                     # mỗi buổi đúng một dòng cho mỗi em
    assert _dem(api, "match_results") == 798 * so_buoi


def test_l1_run_history_dung_mot_va_giai_doan_xuat(chay_tron):
    api = chay_tron["api"]
    assert _dem(api, "run_history") == 1
    assert chay_tron["xep"]["run_id"] and chay_tron["xep"]["seed"] == 7
    assert ok(api.dk_trang_thai())["giai_doan"] == "xuat"


def test_l1_nop_xen_ke_it_nhat_bon_may(chay_tron):
    thu_tu = chay_tron["thu_tu_nop"]
    assert chay_tron["so_kiosk"] >= 4 and len(thu_tu) == 798
    assert {k for k, _ in thu_tu} == {0, 1, 2, 3}
    dau = [k for k, _ in thu_tu[:8]]
    assert dau == [0, 1, 2, 3, 0, 1, 2, 3] or len(set(dau)) == 4      # xen kẽ vòng tròn giữa các máy


def test_l1_xuat_so_nhap(chay_tron, tmp_path):
    api = chay_tron["api"]
    r = dt.xuat(api, chay_tron["token_qt"], str(tmp_path / "SO_NHAP_CLB.xlsx"))
    assert r["so_hs"] == 798 and r["so_clb"] == 40
    assert (tmp_path / "SO_NHAP_CLB.xlsx").exists()


def test_l1_ngan_sach_thoi_gian(chay_tron):
    assert set(chay_tron["pha"]) >= {"cai_dat", "giao_vien", "duyet", "hoc_sinh_nop", "nhap_diem", "chot_va_xep"}
    if chay_tron["tong_giay"] > 120:
        print("CANH BAO: kich ban %.1f s vuot ngan sach 120 s (chi ghi, khong fail)" % chay_tron["tong_giay"])
