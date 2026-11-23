# -*- coding: utf-8 -*-
"""SF-A2 — an toàn: ST-A-006 (CSDL hỏng), ST-B-009 (khoá chế độ học sinh ở backend). DỮ LIỆU MÔ PHỎNG."""
import base64
import glob
import os
import random
import sqlite3

import pytest

import cau_hinh_ws as ch
import recovery
from api import PipelineAPI
from api_chung import kiem_toan_ven_db

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_150 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DOI_CHE_DO_150HS.xlsx")


def _api_da_chay(tmp_path, ten="a"):
    api = PipelineAPI(str(tmp_path / (ten + ".db")), thu_muc_xuat=str(tmp_path / ("x_" + ten)))
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False, "fa_daa": False}})
    with open(SO_150, "rb") as f:
        r = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert r["ok"], r["errors"][:1]
    assert api.run_pipeline(seed=2)["ok"]
    return api


def _ven(path):
    c = sqlite3.connect(path)
    try:
        return c.execute("PRAGMA integrity_check(1)").fetchone()[0]
    except sqlite3.DatabaseError:
        return "malformed"
    finally:
        c.close()


def _lam_hong(path, seed):
    """Lật 5 byte ở nửa dữ liệu; trả True nếu integrity_check bắt được."""
    data = bytearray(open(path, "rb").read())
    rng = random.Random(seed)
    for _ in range(5):
        data[rng.randrange(len(data) // 2, len(data))] ^= 0xFF
    open(path, "wb").write(bytes(data))
    return _ven(path) != "ok"


def test_kiem_toan_ven_db_nguyen_ven_va_chua_co(tmp_path):
    api = _api_da_chay(tmp_path)
    assert kiem_toan_ven_db(api.db_path) is None
    assert kiem_toan_ven_db(str(tmp_path / "khong_co.db")) is None      # CSDL mới: không phải hỏng
    (tmp_path / "rong.db").write_bytes(b"")
    assert kiem_toan_ven_db(str(tmp_path / "rong.db")) is None


def test_chay_giua_chung_khi_csdl_hong_bi_chan_va_khong_xoay_ban_sao_luu(tmp_path):
    """ST-A-006: CSDL hỏng sau khi mở -> run_pipeline từ chối bằng mã rõ ràng, KHÔNG chép trang hỏng vào vòng
    sao lưu (số bản không đổi), run_history không thêm dòng."""
    thu = 0
    for seed in range(2, 40):
        api = _api_da_chay(tmp_path, "p%d" % seed)
        n_bak = len(glob.glob(api.db_path + ".bak-*"))
        if not _lam_hong(api.db_path, seed):
            continue
        thu += 1
        r = api.run_pipeline(seed=2)
        assert not r["ok"]
        assert r["errors"][0]["code"] == "csdl_hong_can_khoi_phuc", r["errors"]
        assert len(glob.glob(api.db_path + ".bak-*")) == n_bak
        with pytest.raises(sqlite3.DatabaseError):
            api._backup_db()                       # đường sao lưu trực tiếp cũng không chép bản hỏng
        r2 = api.import_so_nhap(base64.b64encode(open(SO_150, "rb").read()).decode())
        assert not r2["ok"] and r2["errors"][0]["code"] == "csdl_hong_can_khoi_phuc"
        if thu >= 3:
            break
    assert thu >= 3, "không dựng đủ ca hỏng để thử"


def test_mo_phan_mem_tren_csdl_hong_bi_tu_choi_de_vao_trang_phuc_hoi(tmp_path):
    api = _api_da_chay(tmp_path)
    duong = api.db_path
    for seed in range(2, 40):
        if _lam_hong(duong, seed):
            break
    else:
        pytest.fail("không làm hỏng được CSDL")
    with pytest.raises(sqlite3.DatabaseError):
        PipelineAPI(duong)


def test_trang_phuc_hoi_dung_integrity_check_khong_quick_check(tmp_path):
    """Kiểu hỏng 'row N missing from index' lọt quick_check; trang phục hồi phải coi tệp đó là hỏng."""
    api = _api_da_chay(tmp_path)
    duong = api.db_path
    ca = None
    for seed in range(2, 60):
        sao = str(tmp_path / ("s%d.db" % seed))
        with open(duong, "rb") as f, open(sao, "wb") as g:
            g.write(f.read())
        if not _lam_hong(sao, seed):
            continue
        c = sqlite3.connect(sao)
        try:
            qc = c.execute("PRAGMA quick_check").fetchone()[0]
        except sqlite3.DatabaseError:
            qc = "malformed"
        finally:
            c.close()
        if qc == "ok":
            ca = sao
            break
    assert ca, "không dựng được ca quick_check lọt"
    assert recovery._quick_check_ok(ca) is False


def test_chua_co_tai_khoan_vao_che_do_hoc_sinh_bao_can_tao_tai_khoan(tmp_path):
    """ST-B-009: không có tài khoản thì không có gì để khoá: ok nhưng khoa False + can_tao_tai_khoan True
    (giao diện dẫn tới tạo tài khoản trước); không có cờ khoá giả."""
    api = PipelineAPI(str(tmp_path / "t.db"), thu_muc_xuat=str(tmp_path / "x"))
    r = api.vao_che_do_hoc_sinh()
    assert r["ok"] and r["data"] == {"khoa": False, "can_tao_tai_khoan": True}
    assert api.get_phien_dang_nhap()["data"]["che_do_hs"] is False


def test_co_tai_khoan_che_do_hoc_sinh_khoa_moi_ham_ghi_quan_tri(tmp_path):
    """ST-B-009: có tài khoản -> khoá; mọi hàm ghi quản trị bị từ chối cho tới khi quản trị thoát."""
    api = PipelineAPI(str(tmp_path / "t2.db"), thu_muc_xuat=str(tmp_path / "x2"))
    assert api.tao_tai_khoan("quantri", "matkhau-du-dai-1", "quan_tri")["ok"]
    assert api.dang_nhap("quantri", "matkhau-du-dai-1")["ok"]
    r = api.vao_che_do_hoc_sinh()
    assert r["data"] == {"khoa": True, "can_tao_tai_khoan": False}
    for goi in (lambda: api.reset_data(), lambda: api.run_pipeline(seed=1),
                lambda: api.import_so_nhap(""), lambda: api.create_student_if_missing("X1", "x")):
        r = goi()
        assert not r["ok"] and r["errors"][0]["code"] == "gt3_che_do_hoc_sinh"
