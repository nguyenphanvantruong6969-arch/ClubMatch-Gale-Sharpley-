"""GT4-L0 — lời giải trình chỉ đọc lần chạy CHÍNH THỨC (R0). Dữ liệu MÔ PHỎNG.

Chính thức → chạy thử với luật làm đổi kết quả → mọi lời giải trình (màn tra cứu, phiếu in,
học sinh tự tra cứu) vẫn phải khớp `match_results`, không phải kết quả của lần thử."""

import os
import re
import shutil
import sys

import pytest

import api as api_mod
import cau_hinh_ws
import workspace as ws

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

LUAT_DOI = {"priority": "tier", "tiers": ["khong_co_nhom_nay"]}


@pytest.fixture
def chinh_thuc(tmp_path):
    """Một workspace thật (cần cho `ap_dung_tieu_chi`) + lần chính thức + mã tra cứu."""
    os.makedirs(str(tmp_path / "nguon"))
    nguon = d.nap_bo(str(tmp_path / "nguon"), d.BO_DU_LIEU[1][1])
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    api = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    api.slug_test = slug
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    return api


def _chinh_thuc_va_ma(api):
    with api._ket_noi_doc() as cur:
        kq = {}
        for sid, buoi, cid in cur.execute("SELECT student_id, buoi, club_id FROM match_results"):
            kq.setdefault(sid, {})[buoi] = cid
        ma = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))
        ten = dict(cur.execute("SELECT club_id, name FROM clubs"))
        run_id = cur.execute("SELECT run_id FROM run_history WHERE loai_chay IS NULL "
                             "ORDER BY run_id DESC LIMIT 1").fetchone()[0]
        hs = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
    return kq, ma, ten, run_id, hs


def _lech_giai_trinh(api, kq, run_id, hs, tra_cuu=False, ma=None):
    lech = []
    for sid in hs:
        r = api.tra_cuu_hoc_sinh(sid, ma[sid]) if tra_cuu else api.get_giai_trinh_hoc_sinh(sid)
        assert r["ok"], r
        d = r["data"]
        assert d["run"]["run_id"] == run_id, sid
        hien = {b["buoi"]: b["ket_qua"] for b in d["buoi"]}
        mong = {b: (c if c else None) for b, c in kq.get(sid, {}).items()}
        # học sinh không có chỗ: không có dòng trong match_results (ket_qua rỗng/None)
        for buoi, cid in hien.items():
            if (cid or None) != mong.get(buoi):
                lech.append((sid, buoi, cid, mong.get(buoi)))
    return lech


def _thu_lam_doi_ket_qua(api):
    r = api.run_thu(LUAT_DOI)
    assert r["ok"], r
    with api._ket_noi_doc() as cur:
        chinh = set(cur.execute("SELECT student_id, buoi, club_id FROM match_results"))
        thu = set(cur.execute("SELECT student_id, buoi, club_id FROM ket_qua_thu WHERE run_id = ?",
                              (r["data"]["run_id"],)))
    assert len(chinh - thu) >= 1, "luật thử phải làm đổi ít nhất một học sinh"
    return r["data"]["run_id"]


def test_giai_trinh_khop_chinh_thuc_sau_chay_thu(chinh_thuc):
    api = chinh_thuc
    kq, ma, _ten, run_id, hs = _chinh_thuc_va_ma(api)
    assert _lech_giai_trinh(api, kq, run_id, hs) == []
    for _ in range(2):                                   # hai lần thử liên tiếp
        _thu_lam_doi_ket_qua(api)
        assert _lech_giai_trinh(api, kq, run_id, hs) == []
        d = api.get_giai_trinh_hoc_sinh(hs[0])["data"]
        assert d["du_lieu_da_doi"] is False and d["run"]["run_id"] == run_id


def test_tra_cuu_hoc_sinh_khop_chinh_thuc_sau_chay_thu(chinh_thuc):
    api = chinh_thuc
    kq, ma, _ten, run_id, hs = _chinh_thuc_va_ma(api)
    _thu_lam_doi_ket_qua(api)
    assert _lech_giai_trinh(api, kq, run_id, hs, tra_cuu=True, ma=ma) == []


def test_phieu_in_khong_doi_va_khong_co_chu_cua_lan_thu(chinh_thuc, tmp_path):
    api = chinh_thuc
    truoc = api.export_phieu_giai_trinh(str(tmp_path / "truoc.html"))
    assert truoc["ok"]
    _thu_lam_doi_ket_qua(api)
    sau = api.export_phieu_giai_trinh(str(tmp_path / "sau.html"))
    assert sau["ok"] and sau["data"]["n_trang"] == truoc["data"]["n_trang"]
    a = (tmp_path / "truoc.html").read_text(encoding="utf-8")
    b = (tmp_path / "sau.html").read_text(encoding="utf-8")
    chuan = lambda s: re.sub(r"\d{4}-\d\d-\d\dT[\d:]+|\d\d/\d\d/\d{4}[ \d:]*", "", s)  # noqa: E731
    assert chuan(a) == chuan(b)
    assert "khong_co_nhom_nay" not in b


def test_sau_ap_dung_tieu_chi_van_nhu_ket_qua_da_luu(chinh_thuc):
    api = chinh_thuc
    kq, _ma, _ten, run_id, hs = _chinh_thuc_va_ma(api)
    thu_id = _thu_lam_doi_ket_qua(api)
    r = api.ap_dung_tieu_chi(thu_id, api.slug_test)
    assert r["ok"], r            # chỉ lưu cấu hình, chưa chạy chính thức lại
    assert _lech_giai_trinh(api, kq, run_id, hs) == []   # cờ du_lieu_da_doi có thể True, CLB hiện vẫn khớp
