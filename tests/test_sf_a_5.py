# -*- coding: utf-8 -*-
"""SF-A5 — ST-A-008: PDF cả trường nhanh hơn (không mã hoá ASCII85 luồng trang) và xuất theo lớp báo tiến độ.
Không đổi chữ trong ô, không đổi số trang. DỮ LIỆU MÔ PHỎNG."""
import os
import tempfile

import pytest

pytest.importorskip("reportlab")
import xuat_pdf  # noqa: E402


@pytest.fixture(autouse=True)
def _phong():
    xuat_pdf.san_sang()


def _khoi(n=40):
    hang = [[i, "CLB %d" % i, "Vì sao " * 12] for i in range(n)]
    return [xuat_pdf.tieu_de("Thử"), xuat_pdf.bang(["STT", "CLB", "Vì sao"], hang, [1, 2, 4], cot_dau_mm=12)]


def test_dung_pdf_khong_ma_hoa_a85_va_tra_lai_cau_hinh():
    from reportlab import rl_config
    truoc = rl_config.useA85
    with tempfile.TemporaryDirectory() as d:
        p = xuat_pdf.dung_pdf(os.path.join(d, "a.pdf"), _khoi())
        with open(p, "rb") as f:
            raw = f.read()
        assert b"ASCII85Decode" not in raw and b"FlateDecode" in raw
        assert xuat_pdf.dem_trang(p) >= 2
    assert rl_config.useA85 == truoc            # cấu hình toàn tiến trình được trả lại, kể cả khi dựng lỗi


def test_cau_hinh_a85_tra_lai_ca_khi_dung_loi():
    from reportlab import rl_config
    truoc = rl_config.useA85

    class Hong:                                  # khối hỏng: ném lỗi giữa lúc `doc.build`
        def wrap(self, *a):
            raise RuntimeError("hong")
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(Exception):
            xuat_pdf.dung_pdf(os.path.join(d, "a.pdf"), [Hong()])
        assert os.listdir(d) == []
    assert rl_config.useA85 == truoc


# ---- giai_trinh: bộ nhớ đệm theo CLB (phiếu 3 000 em từng tốn thời gian bậc hai) ----
def _b_mau():
    return {"assign": {"s1": "c1", "s2": "c1", "s3": "c2", "s4": None, "s5": "c1"},
            "base_rank": {"c1": {"s1": 0, "s2": 2, "s5": 1}, "c2": {"s3": 0}, "c3": {}},
            "clubs": {}}


def test_nhan_cuoi_nho_giong_ham_goc_va_chi_tinh_mot_lan():
    import giai_trinh
    b = _b_mau()
    for cid in ("c1", "c2", "c3"):
        assert giai_trinh._nhan_cuoi_nho(cid, b) == giai_trinh._nguoi_nhan_cuoi(cid, b["assign"], b["base_rank"])
    assert giai_trinh._nhan_cuoi_nho("c1", b) == ("s2", 3)       # hạng nền thấp nhất = người nhận cuối
    assert giai_trinh._nhan_cuoi_nho("c3", b) == (None, 0)
    b["base_rank"] = None                                        # lần sau không đụng lại dữ liệu gốc
    assert giai_trinh._nhan_cuoi_nho("c1", b) == ("s2", 3)


def test_so_nhan_dem_dung_theo_clb():
    import giai_trinh
    b = _b_mau()
    assert [giai_trinh._so_nhan(c, b) for c in ("c1", "c2", "c3")] == [3, 1, 0]
    assert all(giai_trinh._so_nhan(c, b) == sum(1 for k in b["assign"].values() if k == c)
               for c in ("c1", "c2", "c3"))


# ---- báo tiến độ xuất phiếu PDF (get_tien_do_xuat) ----
from test_gt1_phieu import _dung  # noqa: E402


def _bao_dung_pdf(api, ghi):
    """Bọc `phieu_giai_trinh.dung_phieu_pdf`: sau MỖI lần báo `khi_xong_em` thì ghi lại `get_tien_do_xuat()`."""
    import phieu_giai_trinh
    that = phieu_giai_trinh.dung_phieu_pdf

    def bao(cac_em, duong, so_ngay=None, *a, khi_xong_em=None, **k):
        ghi.append(("tep", os.path.basename(duong), api.get_tien_do_xuat()["data"]))

        def goi(xong):
            khi_xong_em(xong)
            ghi.append(("em", xong, api.get_tien_do_xuat()["data"]))
        return that(cac_em, duong, so_ngay, *a, khi_xong_em=goi, **k)
    return bao


def test_tien_do_ranh_khi_khong_xuat(api):
    r = api.get_tien_do_xuat()
    assert r["ok"] and r["data"] == {"dang_xuat": False, "xong": 0, "tong": 0, "ten": None}


def test_tien_do_mot_tep_dem_tung_em_roi_ve_ranh(api, tmp_path, monkeypatch):
    import phieu_giai_trinh
    _dung(api)
    ghi = []
    monkeypatch.setattr(phieu_giai_trinh, "dung_phieu_pdf", _bao_dung_pdf(api, ghi))
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"))
    assert r["ok"], r
    xong = [g[2]["xong"] for g in ghi if g[0] == "em"]
    assert xong == sorted(xong) and xong[-1] == 3 and set(xong) <= {1, 2, 3}
    assert all(g[2]["dang_xuat"] and g[2]["tong"] == 3 for g in ghi)
    assert api.get_tien_do_xuat()["data"]["dang_xuat"] is False       # xong là về trạng thái rảnh


def test_tien_do_theo_lop_cong_don_qua_cac_lop(api, tmp_path, monkeypatch):
    import phieu_giai_trinh
    _dung(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO students (student_id, name) VALUES ('s9', 'Em Chưa Lớp')")
    assert api.run_pipeline(seed=3)["ok"]
    ghi = []
    monkeypatch.setattr(phieu_giai_trinh, "dung_phieu_pdf", _bao_dung_pdf(api, ghi))
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "tm"), theo_lop=True)
    assert r["ok"] and r["data"]["n_tep"] == 3, r
    dau = [(g[1], g[2]["xong"], g[2]["tong"], g[2]["ten"]) for g in ghi if g[0] == "tep"]
    assert [d[0] for d in dau] == ["10A1.pdf", "10A2.pdf", "_chua_co_lop.pdf"]
    assert [d[1] for d in dau] == [0, 2, 3] and {d[2] for d in dau} == {4}     # cộng dồn, không quay về 0 mỗi lớp
    assert [d[3] for d in dau][:2] == ["10A1", "10A2"]
    moi = [g[2]["xong"] for g in ghi]                         # mọi lần đọc trong lúc xuất: không bao giờ lùi, cuối cùng đủ 4
    assert moi == sorted(moi) and moi[-1] == 4
    assert api.get_tien_do_xuat()["data"]["dang_xuat"] is False


def test_tien_do_ve_ranh_ca_khi_xuat_loi(api, tmp_path, monkeypatch):
    import xuat_pdf as xp
    _dung(api)

    def hong(*a, **k):
        raise RuntimeError("hong")
    monkeypatch.setattr(xp, "dung_pdf", hong)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"))
    assert not r["ok"]
    assert api.get_tien_do_xuat()["data"]["dang_xuat"] is False


def test_get_tien_do_xuat_la_ham_giao_vien():
    import phan_quyen
    assert phan_quyen.QUYEN["get_tien_do_xuat"] == phan_quyen.GIAO_VIEN
