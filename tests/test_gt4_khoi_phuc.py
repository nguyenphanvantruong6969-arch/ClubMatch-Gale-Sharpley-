"""GT4-L3 — lối thoát khi quên mật khẩu quản trị cho bản `.exe` (R2, D4-4): `main.py --xoa-tai-khoan`.

Dòng lệnh chạy TRƯỚC khi mở cửa sổ (không cần pywebview). Dữ liệu MÔ PHỎNG, mật khẩu giả.
Cửa sổ Windows `.exe` + `QUEN_MAT_KHAU.bat` không kiểm được trên Linux (xem ledger, Needs Truong)."""

import glob
import os
import sqlite3
import subprocess
import sys

import pytest

from _fa import dung_fa_clb
from _wharton import tat_wharton

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"


@pytest.fixture
def db_co_tai_khoan(api):
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
    for sid in ("s1", "s2"):
        assert api.create_student_if_missing(sid, "Em " + sid)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    return api.db_path


def _chay(*args, nhap=None):
    return subprocess.run([sys.executable, os.path.join(GOC, "main.py"), *args], input=nhap, text=True,
                          capture_output=True, encoding="utf-8", timeout=60, cwd=GOC)


def _dem(db, bang):
    c = sqlite3.connect(db)
    try:
        return c.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]
    finally:
        c.close()


def _bang(db, bang):
    c = sqlite3.connect(db)
    try:
        return c.execute("SELECT * FROM %s ORDER BY 1, 2" % bang).fetchall()
    finally:
        c.close()


def test_yes_xoa_het_tai_khoan_sao_luu_va_giu_ket_qua(db_co_tai_khoan):
    db = db_co_tai_khoan
    kq_truoc, hs_truoc = _bang(db, "match_results"), _bang(db, "students")
    bak_truoc = set(glob.glob(db + ".bak-*"))                           # run_pipeline cũng sao lưu
    assert kq_truoc and _dem(db, "tai_khoan") == 2
    r = _chay("--xoa-tai-khoan", db, "--yes")
    assert r.returncode == 0, r.stderr
    assert "2 tài khoản" in r.stdout and "sao lưu" in r.stdout
    assert _dem(db, "tai_khoan") == 0
    (moi,) = set(glob.glob(db + ".bak-*")) - bak_truoc                    # đúng MỘT bản sao lưu mới
    assert _dem(moi, "tai_khoan") == 2                                    # bản sao lưu còn tài khoản cũ
    assert _bang(db, "match_results") == kq_truoc and _bang(db, "students") == hs_truoc


def test_xac_nhan_sai_thi_khong_xoa_gi(db_co_tai_khoan):
    db = db_co_tai_khoan
    bak_truoc = set(glob.glob(db + ".bak-*"))
    r = _chay("--xoa-tai-khoan", db, nhap="xoa het\n")
    assert r.returncode != 0
    assert _dem(db, "tai_khoan") == 2 and set(glob.glob(db + ".bak-*")) == bak_truoc
    r = _chay("--xoa-tai-khoan", db, nhap="")                              # không có đầu vào (EOF)
    assert r.returncode != 0 and _dem(db, "tai_khoan") == 2


def test_go_dung_xoa_thi_xoa(db_co_tai_khoan):
    db = db_co_tai_khoan
    r = _chay("--xoa-tai-khoan", db, nhap="XOA\n")
    assert r.returncode == 0 and _dem(db, "tai_khoan") == 0


def test_tep_khong_co_thi_bao_loi_va_khong_tao_tep(tmp_path):
    db = str(tmp_path / "khong_co.db")
    r = _chay("--xoa-tai-khoan", db, "--yes")
    assert r.returncode != 0 and not os.path.exists(db)


def test_mac_dinh_quet_cac_workspace_canh_chuong_trinh(tmp_path, db_co_tai_khoan):
    """Không đưa đường dẫn: xử lý mọi app.db trong `workspaces/` cạnh chương trình (hàm lõi, không cần exe)."""
    import recovery
    import workspace as ws

    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    import shutil
    shutil.copyfile(db_co_tai_khoan, db)
    dong = []
    ma = recovery.chay_xoa_tai_khoan_dong_lenh(["--xoa-tai-khoan", "--yes"], goc, ghi=dong.append)
    assert ma == 0 and _dem(db, "tai_khoan") == 0
    assert any("2" in d for d in dong)
