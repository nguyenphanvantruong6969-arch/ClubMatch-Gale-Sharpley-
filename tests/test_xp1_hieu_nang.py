"""XP1-L5 — hiệu năng xuất PDF hàng loạt với 800 học sinh (sổ mô phỏng, seed 3).

Mục tiêu của kế hoạch: phiếu giải trình cả trường < 30 giây trên máy chạy CI Linux. Ngưỡng: 30 giây trên Linux,
90 giây trên Windows (kế hoạch không đặt mục tiêu cho Windows và máy chạy Windows chậm hơn; số 90 là dư địa chứ
không phải cam kết). Đặt biến môi trường `XP1_NGUONG_GIAY` để đổi ngưỡng trên một máy cụ thể. Mỗi ca luôn in số
giây đo được (`pytest -s`) và có tạm dừng đo độ phủ hay không; test không bao giờ bị bỏ qua. Đo độ phủ bị tạm dừng
chỉ trong đoạn bấm giờ (CI Linux: có độ phủ 30,08 / 30,04 giây, không có 12 đến 16 giây).
"""
import base64
import os
import sys
import time

import pytest
from _wharton import tat_wharton

pytest.importorskip("reportlab")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_800 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_800HS_HOP_LE.xlsx")
NGUONG_GIAY = float(os.environ.get("XP1_NGUONG_GIAY") or (90 if sys.platform == "win32" else 30))


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


def _tam_dung_do_phu():
    """Tắt đo độ phủ trong lúc bấm giờ (theo dõi từng dòng lệnh làm chậm thêm ~50 %; số đo CI: 30,0 giây so với
    12 đến 16 giây khi không đo). Trả bộ đo đang chạy để bật lại, hoặc None khi không có / không dùng được."""
    try:
        import coverage
    except ImportError:
        return None
    cov = coverage.Coverage.current()
    if cov is None:
        return None
    cov.stop()
    return cov


def _do(ham, *args, **kw):
    cov = _tam_dung_do_phu()
    t0 = time.perf_counter()
    try:
        r = ham(*args, **kw)
    finally:
        giay = time.perf_counter() - t0
        if cov is not None:
            cov.start()
    assert r["ok"], r
    print("XP1 hieu nang: %.1f s (nguong %.0f s, do phu %s)" % (giay, NGUONG_GIAY, "tam dung" if cov else "khong chay"))
    return r["data"], giay


def test_phieu_ca_truong_theo_lop_trong_nguong(api800):
    d, giay = _do(api800.export_phieu_giai_trinh_pdf, "", None, True)
    print("XP1 hieu nang: phieu theo lop, %d tep, %d trang: %.1f s" % (d["n_tep"], d["n_trang"], giay))
    assert d["n_trang"] >= 800 and giay < NGUONG_GIAY


def test_phieu_ca_truong_mot_tep_trong_nguong(api800):
    d, giay = _do(api800.export_phieu_giai_trinh_pdf, "")
    print("XP1 hieu nang: phieu mot tep, %d trang: %.1f s" % (d["n_trang"], giay))
    assert d["n_trang"] >= 800 and giay < NGUONG_GIAY


@pytest.mark.parametrize("theo", ["clb", "lop"])
def test_danh_sach_ca_truong_trong_nguong(api800, theo):
    d, giay = _do(api800.export_danh_sach_pdf, "", theo)
    print("XP1 hieu nang: danh sach theo %s, %d tep, %d trang: %.1f s" % (theo, d["n_tep"], d["n_trang"], giay))
    assert giay < NGUONG_GIAY
