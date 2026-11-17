"""GT2-L2 — chạy thử: ghi riêng (`loai_chay = 'thu'`, `ket_qua_thu`), không đụng kết quả chính thức.

Dữ liệu MÔ PHỎNG. Kiểm: (a) luật thử = luật đã lưu thì kết quả thử = kết quả chính thức (3 bộ × 5 seed);
(b) sau một lần thử với luật khác, mọi đầu ra chính thức y nguyên; (c) `run_history` thêm đúng một dòng;
(d) lỗi giữa chừng thì rollback; (e) CSDL cũ chưa có cột di trú hai lần không lỗi; số bốc thăm không bị vẽ lại.
"""

import json
import os
import sqlite3
import sys

import pytest

import api as api_mod
import cau_hinh_ws
import rbda_priority_pipeline as rb

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

SEEDS = (42, 7, 123, 2024, 99)
BO = [(i, ten.split()[0], tep) for i, (ten, tep) in enumerate(d.BO_DU_LIEU[:3])]


def _mo(tmp_path, tep, chay=True, seed=42):
    db = d.nap_bo(str(tmp_path), tep)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    a = api_mod.PipelineAPI(db)
    if chay:
        assert a.run_pipeline(seed=seed)["ok"]
    return a, db


def _sql(db, cau, tham=()):
    c = sqlite3.connect(db)
    try:
        return c.execute(cau, tham).fetchall()
    finally:
        c.close()


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("_i,_ten,tep", BO, ids=[b[1] for b in BO])
def test_luat_thu_bang_luat_da_luu_cho_ket_qua_bang_chinh_thuc(tmp_path, _i, _ten, tep, seed):
    a, db = _mo(tmp_path, tep, seed=seed)
    r = a.run_thu({})
    assert r["ok"], r
    chinh = _sql(db, "SELECT student_id, buoi, club_id, rank_in_student_pref FROM match_results "
                     "ORDER BY student_id, buoi")
    thu = _sql(db, "SELECT student_id, buoi, club_id, rank_in_list FROM ket_qua_thu WHERE run_id = ? "
                   "ORDER BY student_id, buoi", (r["data"]["run_id"],))
    assert thu == chinh


def _chup(a, db, thu_muc):
    """Mọi đầu ra chính thức ở thẻ Kết quả, Quản trị và Sau khi xếp + bảng gốc + tệp xuất."""
    ra = {}
    for ten in ("get_last_run_info", "get_dashboard_status", "get_pipeline_run_warning",
                "get_stb_lock_status", "get_run_history", "get_match_results", "get_club_fill_stats",
                "get_tai_theo_buoi", "get_em_chua_co_cho", "get_so_boc_tham_theo_buoi",
                "get_trang_thai_ket_qua", "get_thay_doi_ket_qua", "get_diem_chuan", "get_ly_do_ket_qua",
                "get_vong_doi_cho", "get_moi_cho_trong", "get_khieu_nai", "get_diem_danh",
                "get_phan_bo_nguyen_vong", "get_suat_du_tru"):
        ra[ten] = json.dumps(getattr(a, ten)(), sort_keys=True, default=str)
    for ten in ("export_csv", "export_ket_qua", "export_ly_do_csv", "export_thay_doi_ket_qua"):
        duong = os.path.join(thu_muc, ten + ".out")
        r = getattr(a, ten)(duong)
        ra[ten] = (r["ok"], open(duong, "rb").read() if os.path.isfile(duong) else None)
    for bang in ("match_results", "ket_qua_truoc", "dau_van_tay_chay", "stb_lock", "run_meta", "stb_buoi",
                 "students", "fa_ly_do", "fa_nhom", "fa_dieu_chinh", "wharton_lock"):
        try:
            ra[bang] = _sql(db, "SELECT * FROM %s" % bang)
        except sqlite3.Error:
            ra[bang] = None
    ra["csv"] = open(os.path.join(os.path.dirname(db), "match_results.csv"), "rb").read()
    return ra


def test_thu_luat_khac_khong_doi_dau_ra_chinh_thuc(tmp_path):
    a, db = _mo(tmp_path, BO[1][2])
    truoc = _chup(a, db, str(tmp_path))
    r = a.run_thu({"priority": "tier", "tiers": ["khong_co_nhom_nay"]})
    assert r["ok"], r
    assert r["data"]["luat"]["priority"] == "tier"
    sau = _chup(a, db, str(tmp_path))
    # Chỉ get_run_history được phép đổi nếu hiện lần thử: nó KHÔNG được hiện.
    assert sau == truoc


def test_run_history_them_dung_mot_dong_dong_cu_nguyen(tmp_path):
    a, db = _mo(tmp_path, BO[0][2])
    cu = _sql(db, "SELECT * FROM run_history ORDER BY run_id")
    r = a.run_thu({"priority": "tier", "tiers": ["x"]})
    assert r["ok"], r
    moi = _sql(db, "SELECT * FROM run_history ORDER BY run_id")
    assert moi[:len(cu)] == cu and len(moi) == len(cu) + 1
    ten = [c[1] for c in sqlite3.connect(db).execute("PRAGMA table_info(run_history)")]
    dong = dict(zip(ten, moi[-1]))
    assert dong["loai_chay"] == "thu" and dong["stb_redrawn"] == 0
    assert all(x[ten.index("loai_chay")] is None for x in cu)
    assert json.loads(dong["luat_xep"])["priority"] == "tier"


def test_khong_boc_tham_lai_va_khong_dung_khoa(tmp_path):
    a, db = _mo(tmp_path, BO[1][2])
    stb = _sql(db, "SELECT student_id, stb_number FROM students ORDER BY student_id")
    khoa = _sql(db, "SELECT * FROM stb_lock")
    assert a.run_thu({"priority": "tier", "tiers": ["x"]})["ok"]
    assert _sql(db, "SELECT student_id, stb_number FROM students ORDER BY student_id") == stb
    assert _sql(db, "SELECT * FROM stb_lock") == khoa


def test_chua_co_lan_chinh_thuc_thi_tu_choi_va_khong_ghi(tmp_path):
    a, db = _mo(tmp_path, BO[0][2], chay=False)
    r = a.run_thu({})
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_chua_co_lan_chinh_thuc"
    assert _sql(db, "SELECT COUNT(*) FROM run_history") == [(0,)]


def test_luat_thu_khong_hop_le_bi_tu_choi_bang_ma_rieng(tmp_path):
    a, db = _mo(tmp_path, BO[0][2])
    for xau in ({"priority": "trong_so"}, {"khong_co_khoa": 1}, {"tiers": ["A", "A"], "tier_mode": "strict"}):
        r = a.run_thu(xau)
        assert not r["ok"] and r["errors"][0]["code"] == "gt2_tieu_chi_khong_hop_le", (xau, r)
    assert not a.run_thu("tier")["ok"]
    assert _sql(db, "SELECT COUNT(*) FROM run_history WHERE loai_chay = 'thu'") == [(0,)]


def test_fa_bi_tu_choi_bang_ma_rieng(tmp_path):
    a, db = _mo(tmp_path, BO[0][2])
    r = a.run_thu({"wharton": True, "fa_daa": True})
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_thu_chua_ho_tro_fa"


def test_loi_giua_chung_thi_rollback(tmp_path, monkeypatch):
    a, db = _mo(tmp_path, BO[0][2])
    import api_tieu_chi

    def hong(_kq):
        raise RuntimeError("hong giua chung")

    monkeypatch.setattr(api_tieu_chi, "cac_dong_match_results", hong)
    r = a.run_thu({"priority": "tier", "tiers": ["x"]})
    assert not r["ok"]
    assert _sql(db, "SELECT COUNT(*) FROM run_history WHERE loai_chay = 'thu'") == [(0,)]
    assert _sql(db, "SELECT COUNT(*) FROM ket_qua_thu") == [(0,)]


def test_loi_sau_khi_ghi_run_history_van_rollback(tmp_path, monkeypatch):
    a, db = _mo(tmp_path, BO[0][2])
    # Hỏng ở bước ghi ket_qua_thu: đổi tên bảng để INSERT thứ hai lỗi, sau khi dòng run_history đã chèn.
    c = sqlite3.connect(db)
    c.execute("DROP TABLE ket_qua_thu")
    c.commit()
    c.close()
    r = a.run_thu({"priority": "tier", "tiers": ["x"]})
    assert not r["ok"]
    assert _sql(db, "SELECT COUNT(*) FROM run_history WHERE loai_chay = 'thu'") == [(0,)]


def _bo_cot_loai_chay(c):
    """Dựng lại `run_history` theo cột trước GT2 (SQLite của CI không cho DROP COLUMN trên lược đồ này)."""
    cot = [x for x in c.execute("PRAGMA table_info(run_history)") if x[1] != "loai_chay"]
    dinh_nghia = []
    for _cid, ten, kieu, khong_null, mac_dinh, khoa in cot:
        d_ = "%s %s" % (ten, kieu)
        if khoa:
            d_ += " PRIMARY KEY AUTOINCREMENT"
        if khong_null and not khoa:
            d_ += " NOT NULL"
        if mac_dinh is not None:
            d_ += " DEFAULT %s" % mac_dinh
        dinh_nghia.append(d_)
    ten_cot = ", ".join(x[1] for x in cot)
    c.execute("CREATE TABLE run_history_cu (%s)" % ", ".join(dinh_nghia))
    c.execute("INSERT INTO run_history_cu (%s) SELECT %s FROM run_history" % (ten_cot, ten_cot))
    c.execute("DROP TABLE run_history")
    c.execute("ALTER TABLE run_history_cu RENAME TO run_history")


def test_csdl_cu_khong_co_cot_di_tru_hai_lan_khong_loi(tmp_path):
    a, db = _mo(tmp_path, BO[0][2])
    c = sqlite3.connect(db)
    _bo_cot_loai_chay(c)
    c.execute("DROP TABLE ket_qua_thu")
    c.commit()
    c.close()
    cu = _sql(db, "SELECT * FROM run_history")
    assert any("loai_chay" in x for x in rb.di_tru_schema(db))
    assert rb.di_tru_schema(db) == []
    assert [r[:-1] for r in _sql(db, "SELECT * FROM run_history")] == [r for r in cu]
    assert _sql(db, "SELECT COUNT(*) FROM ket_qua_thu") == [(0,)]
    assert a.run_thu({})["ok"]


def test_cac_cho_doc_chinh_thuc_bo_qua_lan_thu_o_csdl_co_ca_hai(tmp_path):
    a, db = _mo(tmp_path, BO[0][2])
    ls = a.get_run_history()["data"]
    assert a.run_thu({"priority": "tier", "tiers": ["x"]})["ok"]
    assert a.get_run_history()["data"] == ls
    with a._ket_noi_doc() as cur:
        goc = rb.run_chinh_thuc_moi_nhat(cur)
    assert goc["loai_chay"] is None and goc["run_id"] == ls[0]["run_id"]


def test_luat_luu_la_fa_nhung_luat_thu_tat_fa_thi_van_chay_duoc(tmp_path):
    """FIX L2 #1: quyết định theo luật HIỆU LỰC (đã trộn), không theo luật đã lưu."""
    a, db = _mo(tmp_path, BO[0][2])
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": True, "fa_daa": True}})
    truoc = _chup(a, db, str(tmp_path))
    r = a.run_thu({"fa_daa": False, "wharton": False})
    assert r["ok"], r
    assert _sql(db, "SELECT COUNT(*) FROM ket_qua_thu WHERE run_id = ?", (r["data"]["run_id"],))[0][0] > 0
    for bang in ("fa_ly_do", "fa_nhom", "fa_dieu_chinh", "match_results", "stb_lock"):
        assert _chup(a, db, str(tmp_path))[bang] == truoc[bang], bang
    # luật thử vẫn bật FA thì vẫn bị từ chối bằng lời dễ hiểu
    r2 = a.run_thu({})
    assert not r2["ok"] and r2["errors"][0]["code"] == "gt2_thu_chua_ho_tro_fa"


@pytest.mark.parametrize("khoa", ["max_tests", "fa_duong", "max_choices_khac"])
def test_luat_thu_chi_nhan_khoa_tieu_chi(tmp_path, khoa):
    """FIX L2 #2: khoá ngoài `LUAT_XEP_MAC_DINH` bị từ chối, không ghi gì."""
    a, db = _mo(tmp_path, BO[0][2])
    truoc = _sql(db, "SELECT COUNT(*) FROM run_history")
    r = a.run_thu({khoa: 1})
    assert not r["ok"] and r["errors"][0]["code"] == "gt2_tieu_chi_khong_hop_le", r
    assert _sql(db, "SELECT COUNT(*) FROM run_history") == truoc
    assert _sql(db, "SELECT COUNT(*) FROM ket_qua_thu") == [(0,)]
