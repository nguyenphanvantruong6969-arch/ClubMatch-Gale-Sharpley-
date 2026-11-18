"""GT4-L5 — `mo_tep`: mở đúng TỆP vừa xuất bằng chương trình mặc định của máy, và không mở gì khác.

Gọi được từ JavaScript nên là một cửa chạy chương trình ngoài: chỉ tệp nằm trong chỗ phần mềm đặt tệp xuất
VÀ có đuôi của tệp xuất (.html .csv .xlsx .pdf .docx); không bao giờ mở tệp chạy được (.exe .bat ...)."""

import os
import sys

import pytest

import phan_quyen as pq


@pytest.fixture
def ghi_lai(monkeypatch):
    goi = []
    if sys.platform == "win32":
        monkeypatch.setattr(os, "startfile", lambda p: goi.append(p), raising=False)
    else:
        import subprocess

        class Gia:
            def __init__(self, lenh, **kw):
                goi.append(lenh[-1])
        monkeypatch.setattr(subprocess, "Popen", Gia)
    return goi


def _tep_xuat(api, ten, noi_dung="x"):
    goc = os.environ["RBDA_THU_MUC_TAI_VE"]
    p = os.path.join(goc, ten)
    with open(p, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    return p


@pytest.mark.parametrize("ten", ["phieu.html", "ma.csv", "ket_qua.xlsx", "goi.pdf", "goi.docx", "A.HTML"])
def test_mo_tep_xuat_hop_le(api, ghi_lai, ten):
    p = _tep_xuat(api, ten)
    r = api.mo_tep(p)
    assert r["ok"], r
    assert ghi_lai == [os.path.realpath(p)]


@pytest.mark.parametrize("ten", ["chay.bat", "chay.exe", "x.py", "x.ps1", "x.lnk", "x.js", "khong_duoi"])
def test_tep_chay_duoc_khong_mo(api, ghi_lai, ten):
    p = _tep_xuat(api, ten)
    r = api.mo_tep(p)
    assert not r["ok"] and r["errors"][0]["code"] == "tep_khong_hop_le" and ghi_lai == []


def test_ngoai_cho_xuat_thu_muc_va_tep_khong_co_deu_tu_choi(api, ghi_lai, tmp_path_factory):
    ngoai = tmp_path_factory.mktemp("ngoai") / "x.html"
    ngoai.write_text("x", encoding="utf-8")
    thu_muc = os.environ["RBDA_THU_MUC_TAI_VE"]
    for duong in (str(ngoai), thu_muc, os.path.join(thu_muc, "khong_co.html"), "", "/etc/passwd",
                  os.path.join(thu_muc, "..", "..", "etc", "passwd")):
        r = api.mo_tep(duong)
        assert not r["ok"] and r["errors"][0]["code"] == "tep_khong_hop_le", duong
    assert ghi_lai == []


def test_loi_he_thong_thi_bao_khong_mo_duoc(api, monkeypatch):
    p = _tep_xuat(api, "a.html")
    if sys.platform == "win32":
        monkeypatch.setattr(os, "startfile", lambda p: (_ for _ in ()).throw(OSError("x")), raising=False)
    else:
        import subprocess
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: (_ for _ in ()).throw(OSError("x")))
    r = api.mo_tep(p)
    assert not r["ok"] and r["errors"][0]["code"] == "tep_khong_mo_duoc"


def test_bang_quyen_va_nhat_ky_nhu_mo_thu_muc():
    assert pq.QUYEN["mo_tep"] == pq.QUYEN["mo_thu_muc"] == pq.GIAO_VIEN
    import nhat_ky as nk
    assert nk.nen_ghi("mo_tep") is False and nk.nen_ghi("mo_thu_muc") is False
