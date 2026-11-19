"""XP1-L5 — hiệu năng xuất PDF hàng loạt với 800 học sinh (sổ mô phỏng, seed 3).

Mục tiêu của kế hoạch: phiếu giải trình cả trường < 30 giây trên máy chạy CI (Linux). Con số đo được in ra
(`pytest -s`) và ghi vào CHANGELOG; ngưỡng ở đây rộng hơn một chút cho máy chậm, không để test chập chờn.
"""
import base64
import os
import time

import pytest
from _wharton import tat_wharton

pytest.importorskip("reportlab")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_800 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_800HS_HOP_LE.xlsx")
NGUONG_GIAY = 30


@pytest.fixture(scope="module")
def api800(tmp_path_factory):
    import api as api_mod
    goc = tmp_path_factory.mktemp("xp1_800")
    a = api_mod.PipelineAPI(str(goc / "app.db"))
    tat_wharton(a)
    with open(SO_800, "rb") as f:
        assert a.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    with a._ket_noi_ghi() as cur:             # 800 em vào 27 lớp (mô phỏng); vài em để trống lớp
        ds = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
        for i, sid in enumerate(ds):
            cur.execute("UPDATE students SET class_id = ? WHERE student_id = ?",
                        (None if i % 97 == 96 else "10A%d" % (i % 27 + 1), sid))
    assert a.run_pipeline(seed=3)["ok"]
    a.thu_muc_xuat = str(goc / "tai_xuong")
    os.makedirs(a.thu_muc_xuat)
    return a


def _do(ham, *args, **kw):
    t0 = time.perf_counter()
    r = ham(*args, **kw)
    giay = time.perf_counter() - t0
    assert r["ok"], r
    return r["data"], giay


def test_phieu_ca_truong_theo_lop_duoi_30_giay(api800):
    d, giay = _do(api800.export_phieu_giai_trinh_pdf, "", None, True)
    print("XP1 hieu nang: phieu theo lop, %d tep, %d trang: %.1f s" % (d["n_tep"], d["n_trang"], giay))
    assert d["n_trang"] >= 800 and giay < NGUONG_GIAY


def test_phieu_ca_truong_mot_tep_duoi_30_giay(api800):
    d, giay = _do(api800.export_phieu_giai_trinh_pdf, "")
    print("XP1 hieu nang: phieu mot tep, %d trang: %.1f s" % (d["n_trang"], giay))
    assert d["n_trang"] >= 800 and giay < NGUONG_GIAY


@pytest.mark.parametrize("theo", ["clb", "lop"])
def test_danh_sach_ca_truong_duoi_30_giay(api800, theo):
    d, giay = _do(api800.export_danh_sach_pdf, "", theo)
    print("XP1 hieu nang: danh sach theo %s, %d tep, %d trang: %.1f s" % (theo, d["n_tep"], d["n_trang"], giay))
    assert giay < NGUONG_GIAY
