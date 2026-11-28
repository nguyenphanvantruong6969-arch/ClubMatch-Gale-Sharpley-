"""MT1-L2 — API ba thẻ mục tiêu (`api_muc_tieu.py`). Dữ liệu MÔ PHỎNG (bộ `bo_sach`, 140 em / 12 CLB).

Kiểm: vai (giáo viên bị từ chối ở backend), id lạ, thiếu / sai nhóm, xung đột huy chương và "Chia 100 điểm"
(mã `mt_*`, không bao giờ ValueError thô), Hoàn tác trả đúng luật VÀ từng CLB, áp lại không đổi gì,
sửa tay ⇒ `tuy_chinh`, cấu hình không có `muc_tieu` y như cũ, lưu `muc_tieu` đọc lại từ một Api mới,
một giao dịch (lỗi giữa chừng thì cả hai nguyên vẹn), sao lưu trước, không chạm `run_history` / kết quả.
"""

import copy
import glob
import json
import math
import os
import sqlite3
import sys

import pytest

import api as api_mod
import api_muc_tieu
import cau_hinh_ws
import i18n_errors
import muc_tieu as mt

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

BO_SACH = d.BO_DU_LIEU[1][1]
MK = "matkhau-gia-1"


def _sql(db, cau, tham=()):
    c = sqlite3.connect(db)
    try:
        return c.execute(cau, tham).fetchall()
    finally:
        c.close()


def _mo(tmp_path, rules=None):
    db = d.nap_bo(str(tmp_path), BO_SACH)
    if rules is not None:
        cau_hinh_ws.ghi_cau_hinh(db, {"rules": rules})
    return api_mod.PipelineAPI(db), db


def _clb(db):
    return _sql(db, "SELECT club_id, name, capacity, reserve_capacity, reserve_group, buoi "
                    "FROM clubs ORDER BY club_id")


def _cfg(db):
    return cau_hinh_ws.doc_cau_hinh(db)


def _luat(db):
    return cau_hinh_ws.doc_cau_hinh(db)["rules"]


def _ma(r):
    return [e["code"] for e in r["errors"]]


def _the(r, mid):
    return next(t for t in r["data"]["cac_the"] if t["id"] == mid)


# ----- đọc -----

def test_get_mac_dinh_la_nang_luc_ba_the_va_cac_nhom(tmp_path):
    a, db = _mo(tmp_path)
    r = a.get_muc_tieu()
    assert r["ok"], r
    assert [t["id"] for t in r["data"]["cac_the"]] == ["nang_luc", "co_hoi", "danh_cho"]
    assert r["data"]["hien_tai"] == "nang_luc" and r["data"]["lan_cuoi"] is None
    assert {g["nhan"]: g["so_em"] for g in r["data"]["nhom"]} == {"khoi_10": 18, "chinh_sach": 15}
    assert all(not t["khoa"] for t in r["data"]["cac_the"])
    assert "muc_tieu" not in _cfg(db)                    # cấu hình không có `muc_tieu` y như cũ


def test_get_khong_ghi_gi(tmp_path):
    a, db = _mo(tmp_path)
    truoc = (_clb(db), _sql(db, "SELECT key, value FROM workspace_settings"))
    a.get_muc_tieu()
    assert (_clb(db), _sql(db, "SELECT key, value FROM workspace_settings")) == truoc


# ----- chọn thẻ -----

def test_chon_co_hoi_dat_luat_roi_doc_lai_tu_api_moi(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    clb_truoc = _clb(db)
    r = a.chon_muc_tieu("co_hoi")
    assert r["ok"], r
    luat = _cfg(db)["rules"]
    assert luat["priority"] == "tier" and luat["tiers"] == []
    assert _cfg(db)["muc_tieu"]["id"] == "co_hoi"
    assert "muc_tieu" not in luat                        # không nằm trong `rules` (không vào luat_xep / dấu vân tay)
    assert _clb(db) == clb_truoc                         # co_hoi không đổi chỗ của CLB nào
    b = api_mod.PipelineAPI(db)                          # (c) đọc lại từ một Api mới
    assert b.get_muc_tieu()["data"]["hien_tai"] == "co_hoi"
    assert r["data"]["hien_tai"] == "co_hoi"


def test_chon_danh_cho_giu_cho_dung_cong_thuc(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    r = a.chon_muc_tieu("danh_cho", "khoi_10")
    assert r["ok"], r
    tong = _sql(db, "SELECT COUNT(*) FROM students")[0][0]
    for cid, cap, rc, rg in _sql(db, "SELECT club_id, capacity, reserve_capacity, reserve_group FROM clubs"):
        assert rg == "khoi_10"
        assert rc == min(cap, math.ceil(18 * cap / tong)), cid
    assert r["data"]["hien_tai"] == "danh_cho" and r["data"]["nhom"] == "khoi_10"
    assert set(r["data"]["cho_giu"]) == {x[0] for x in _clb(db)}
    assert api_mod.PipelineAPI(db).get_muc_tieu()["data"]["hien_tai"] == "danh_cho"   # (c)


def test_nhieu_nhom_ma_khong_chon_thi_loi_va_khong_ghi_gi(tmp_path):
    a, db = _mo(tmp_path)
    truoc = (_clb(db), _sql(db, "SELECT value FROM workspace_settings"))
    r = a.chon_muc_tieu("danh_cho")
    assert not r["ok"] and _ma(r) == ["mt_can_chon_nhom"]
    assert (_clb(db), _sql(db, "SELECT value FROM workspace_settings")) == truoc


def test_mot_nhom_duy_nhat_tu_chon_khong_can_bam_them(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    c = sqlite3.connect(db)
    c.execute("UPDATE students SET reserve_group = NULL WHERE reserve_group = 'chinh_sach'")
    c.commit()
    c.close()
    r = a.chon_muc_tieu("danh_cho")
    assert r["ok"], r
    assert r["data"]["nhom"] == "khoi_10"


def test_nhom_khong_co_thi_loi(tmp_path):
    a, db = _mo(tmp_path)
    r = a.chon_muc_tieu("danh_cho", "khong_co_nhom_nay")
    assert not r["ok"] and _ma(r) == ["mt_nhom_khong_co"]


def test_so_nhap_khong_co_cot_nhom_thi_the_bi_khoa_va_chon_bi_tu_choi(tmp_path):
    a, db = _mo(tmp_path)
    c = sqlite3.connect(db)
    c.execute("UPDATE students SET reserve_group = NULL")
    c.commit()
    c.close()
    t = _the(a.get_muc_tieu(), "danh_cho")
    assert t["khoa"] and t["ly_do"]["code"] == "mt_khong_co_nhom"
    assert _ma(a.chon_muc_tieu("danh_cho")) == ["mt_khong_co_nhom"]


def test_id_la(tmp_path):
    a, db = _mo(tmp_path)
    for x in ("khong_co", "", None, 5):
        r = a.chon_muc_tieu(x)
        assert not r["ok"] and _ma(r) == ["mt_muc_tieu_la"], x


# ----- (a) danh_cho trên nền tiers / score_scope khác mặc định -----

def test_danh_cho_dat_lai_tiers_va_score_scope_va_the_van_sang(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False, "tier_mode": "strict", "tiers": ["khoi_10", "chinh_sach"],
                           "score_scope": "per_person"})
    assert a.get_muc_tieu()["data"]["hien_tai"] == "tuy_chinh"
    r = a.chon_muc_tieu("danh_cho", "chinh_sach")
    assert r["ok"], r
    luat = _cfg(db)["rules"]
    assert luat["tiers"] == [] and luat["score_scope"] == "per_slot"
    assert (luat["priority"], luat["tier_mode"]) == ("score", "reserve")
    assert a.get_muc_tieu()["data"]["hien_tai"] == "danh_cho"      # thẻ vẫn sáng
    assert mt.nhan_dien_muc_tieu(luat, {}) == "nang_luc"           # luật y hệt nang_luc, chỉ khác nhờ da_chon


# ----- (b) xung đột -----

def test_co_hoi_voi_huy_chuong_bi_tu_choi_bang_ma_mt(tmp_path):
    a, db = _mo(tmp_path, {"wharton": True, "fa_daa": True})
    truoc = (_cfg(db), _clb(db))
    t = _the(a.get_muc_tieu(), "co_hoi")
    assert t["khoa"] and t["ly_do"]["code"] == "mt_the_can_diem"
    r = a.chon_muc_tieu("co_hoi")
    assert not r["ok"] and _ma(r) == ["mt_the_can_diem"]
    assert (_cfg(db), _clb(db)) == truoc
    assert a.chon_muc_tieu("nang_luc")["ok"]               # các thẻ khác vẫn dùng được với huy chương
    assert _cfg(db)["rules"]["fa_daa"] is True              # thẻ không chạm fa_daa / wharton
    assert _cfg(db)["rules"]["wharton"] is True


def test_co_hoi_voi_chia_100_diem_chay_duoc_kem_ghi_chu_va_hoan_tac_tra_lai_diem(tmp_path):
    a, db = _mo(tmp_path, {"wharton": True})
    truoc = _cfg(db)
    t = _the(a.get_muc_tieu(), "co_hoi")
    assert not t["khoa"] and [g["code"] for g in t["ghi_chu"]] == ["mt_diem_chia_khong_dung"]
    r = a.chon_muc_tieu("co_hoi")                           # không ném ValueError thô
    assert r["ok"], r
    assert [g["code"] for g in r["data"]["canh_bao"]] == ["mt_diem_chia_khong_dung"]
    assert _cfg(db)["rules"]["priority"] == "tier" and _cfg(db)["rules"]["wharton"] is False
    assert a.hoan_tac_muc_tieu(r["data"]["hoan_tac"])["ok"]
    assert _cfg(db) == truoc and _cfg(db)["rules"]["wharton"] is True


# ----- Hoàn tác -----

def test_hoan_tac_tra_dung_luat_va_tung_clb(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    luat0, cfg0, clb0 = _cfg(db)["rules"], _cfg(db), _clb(db)
    r = a.chon_muc_tieu("danh_cho", "khoi_10")
    assert r["ok"] and _clb(db) != clb0
    h = r["data"]["hoan_tac"]
    r2 = a.hoan_tac_muc_tieu(h)
    assert r2["ok"], r2
    assert _clb(db) == clb0 and _cfg(db)["rules"] == luat0 and _cfg(db) == cfg0
    assert "muc_tieu" not in _cfg(db)
    # Hoàn tác lần hai (cùng gói): vẫn đúng trạng thái đó, không lỗi
    assert a.hoan_tac_muc_tieu(h)["ok"]
    assert _clb(db) == clb0 and _cfg(db) == cfg0


def test_hoan_tac_goi_hong_thi_loi_ma_mt_khong_ghi_gi(tmp_path):
    a, db = _mo(tmp_path)
    truoc = (_cfg(db), _clb(db))
    for h in (None, {}, {"rules": 5, "clubs": {}}, {"rules": {"priority": "xxx"}, "clubs": {}},
              {"rules": {}, "clubs": {"clb_bongda": ["x", -4]}, "muc_tieu": None}):
        r = a.hoan_tac_muc_tieu(h)
        assert not r["ok"] and _ma(r) == ["mt_hoan_tac_khong_hop_le"], h
    assert (_cfg(db), _clb(db)) == truoc


def test_ap_lai_cung_the_khong_doi_gi_va_roi_khoi_danh_cho_tra_cho_giu_ban_dau(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    clb0 = _clb(db)
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    sau1 = (_cfg(db), _clb(db))
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    assert (_cfg(db), _clb(db)) == sau1                      # áp lại không đổi gì
    assert a.chon_muc_tieu("danh_cho", "chinh_sach")["ok"]   # đổi nhóm: vẫn nhớ chỗ giữ ban đầu
    assert a.chon_muc_tieu("nang_luc")["ok"]
    assert _clb(db) == clb0                                  # rời danh_cho: chỗ giữ nhập ban đầu quay lại
    assert a.get_muc_tieu()["data"]["hien_tai"] == "nang_luc"


# ----- sửa tay -----

def test_sua_tay_sau_khi_chon_thi_tuy_chinh_va_van_nho_the_cuoi(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    cid, ten, cap, rc, rg, buoi = _clb(db)[0]
    assert a.create_or_update_club(cid, ten, cap, max(0, rc - 1), rg)["ok"]   # sửa tay số chỗ một CLB
    r = a.get_muc_tieu()
    assert r["data"]["hien_tai"] == "tuy_chinh"
    assert r["data"]["lan_cuoi"]["id"] == "danh_cho" and r["data"]["lan_cuoi"]["nhom"] == "khoi_10"
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]                          # "Về mục tiêu mẫu"
    assert a.get_muc_tieu()["data"]["hien_tai"] == "danh_cho"


def test_sua_luat_tay_o_nang_cao_thi_tuy_chinh(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    assert a.chon_muc_tieu("co_hoi")["ok"]
    cau_hinh_ws.ghi_cau_hinh(db, cau_hinh_ws.tron_len(_cfg(db), {"rules": {
        "priority": "score+tier", "tier_mode": "strict", "tiers": ["khoi_10"]}}))   # như "Nâng cao"
    assert a.get_muc_tieu()["data"]["hien_tai"] == "tuy_chinh"


# ----- vai -----

@pytest.mark.parametrize("ham,args", [("get_muc_tieu", ()), ("chon_muc_tieu", ("co_hoi",)),
                                       ("hoan_tac_muc_tieu", ({"rules": {}, "clubs": {}},))])
def test_giao_vien_bi_tu_choi_o_backend(tmp_path, ham, args):
    a, db = _mo(tmp_path)
    assert a.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert a.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    assert a.dang_nhap("gv1", MK)["ok"]
    truoc = (_cfg(db), _clb(db))
    r = getattr(a, ham)(*args)
    assert not r["ok"] and _ma(r) == ["gt3_khong_du_quyen"]
    assert (_cfg(db), _clb(db)) == truoc
    a.dang_xuat()
    assert a.dang_nhap("quantri", MK)["ok"]
    if ham != "hoan_tac_muc_tieu":
        assert getattr(a, ham)(*args)["ok"]


def test_chon_ghi_nhat_ky_nhung_get_khong(tmp_path):
    import nhat_ky as nk
    assert nk.nen_ghi("chon_muc_tieu") and nk.nen_ghi("hoan_tac_muc_tieu")
    assert not nk.nen_ghi("get_muc_tieu")


# ----- một giao dịch, sao lưu, không chạm lịch sử -----

def test_loi_giua_chung_thi_cau_hinh_va_clb_deu_nguyen_ven(tmp_path, monkeypatch):
    a, db = _mo(tmp_path, {"wharton": False})
    truoc = (_cfg(db), _clb(db))

    def hong(conn, cho):
        conn.execute("UPDATE clubs SET reserve_capacity = reserve_capacity")   # đã mở giao dịch
        raise RuntimeError("hỏng giữa chừng")
    monkeypatch.setattr(api_muc_tieu, "_dat_cho_giu", hong)
    r = a.chon_muc_tieu("danh_cho", "khoi_10")
    assert not r["ok"] and _ma(r) == ["mt_khong_ap_dung"]
    assert (_cfg(db), _clb(db)) == truoc


def test_sao_luu_truoc_khi_ghi_va_khong_dong_den_lich_su_hay_ket_qua(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    assert a.run_pipeline(seed=42)["ok"]
    lich_su = _sql(db, "SELECT * FROM run_history ORDER BY run_id")
    kq = _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi")
    stb = _sql(db, "SELECT * FROM stb_lock")
    bak = len(glob.glob(db + ".bak-*"))
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    assert len(glob.glob(db + ".bak-*")) >= bak and glob.glob(db + ".bak-*")
    assert _sql(db, "SELECT * FROM run_history ORDER BY run_id") == lich_su
    assert _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi") == kq
    assert _sql(db, "SELECT * FROM stb_lock") == stb


def test_muc_tieu_khong_vao_luat_xep_ghi_o_lich_su(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    assert a.chon_muc_tieu("nang_luc")["ok"]
    assert a.run_pipeline(seed=42)["ok"]
    assert _sql(db, "SELECT luat_xep FROM run_history ORDER BY run_id DESC LIMIT 1") == [(None,)]


# ----- cấu hình: khoá `muc_tieu` -----

def test_cau_hinh_khong_co_muc_tieu_y_nhu_cu_va_khoa_sai_bi_tu_choi():
    mac_dinh = cau_hinh_ws.chuan_hoa({})
    assert "muc_tieu" not in mac_dinh
    ok = cau_hinh_ws.chuan_hoa({"muc_tieu": {"id": "danh_cho", "nhom": "khoi_10"}})
    assert ok["muc_tieu"] == {"id": "danh_cho", "nhom": "khoi_10"}
    assert "muc_tieu" not in cau_hinh_ws.chuan_hoa({"muc_tieu": None})
    for xau in ({"id": "la"}, {"id": 3}, "danh_cho", {"id": "danh_cho", "nhom": 5}, {"nhom": "x"},
                {"id": "danh_cho", "truoc": {"a": "b"}}, {"id": "danh_cho", "truoc": {"a": ["x", "y"]}}):
        with pytest.raises(ValueError):
            cau_hinh_ws.chuan_hoa({"muc_tieu": xau})


def test_ma_loi_mt_co_vi_va_en():
    for ma in ("mt_muc_tieu_la", "mt_can_chon_nhom", "mt_nhom_khong_co", "mt_khong_co_nhom",
               "mt_the_can_diem", "mt_diem_chia_khong_dung", "mt_hoan_tac_khong_hop_le", "mt_khong_ap_dung"):
        m = i18n_errors.MESSAGES[ma]
        assert m["vi"].strip() and m["en"].strip(), ma
    # nối ở CUỐI tệp (các khối sau, như `cb1_` của CB1, `ct1_` của CT1, được nối thêm phía sau và không tính)
    khong_cb1 = [m for m in i18n_errors.MESSAGES if not m.startswith(("cb1_", "dk_", "ct1_"))]
    assert all(m.startswith("mt_") for m in khong_cb1[-8:])


def test_json_cau_hinh_la_json_thuong(tmp_path):
    a, db = _mo(tmp_path, {"wharton": False})
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    goc = json.loads(_sql(db, "SELECT value FROM workspace_settings WHERE key = 'config'")[0][0])
    assert goc["muc_tieu"]["id"] == "danh_cho" and isinstance(goc["muc_tieu"]["truoc"], dict)
    assert copy.deepcopy(goc) == goc


def test_luu_mau_khong_mang_muc_tieu_theo(tmp_path):
    import shutil
    import workspace
    (tmp_path / "nguon").mkdir()
    a, db = _mo(tmp_path / "nguon", {"wharton": False})
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    root = tmp_path / "goc"
    thu_muc = root / workspace.THU_MUC_WS / "truong-a"
    thu_muc.mkdir(parents=True)
    shutil.copy(db, thu_muc / workspace.TEN_DB)
    assert "muc_tieu" in cau_hinh_ws.doc_cau_hinh(str(thu_muc / workspace.TEN_DB))
    duong = workspace.luu_mau(str(root), "truong-a", "Mẫu thử")
    with open(duong, encoding="utf-8") as f:
        mau = json.load(f)
    assert "muc_tieu" not in mau["config"] and mau["config"]["rules"]["tiers"] == []


def test_muc_tieu_khong_ro_ri_vao_luat_xep_va_dau_van_tay_khi_dung_co_hoi(tmp_path):
    """Ca mặc định không phát hiện được rò rỉ (luat_xep NULL); `co_hoi` thì có luật ghi vào lịch sử."""
    (tmp_path / "the").mkdir()
    (tmp_path / "tho").mkdir()
    a1, db1 = _mo(tmp_path / "the", {"wharton": False})
    assert a1.chon_muc_tieu("co_hoi")["ok"] and a1.run_pipeline(seed=42)["ok"]
    luat_tho = mt.rules_cua_muc_tieu("co_hoi", {"wharton": False})
    a2, db2 = _mo(tmp_path / "tho", luat_tho)               # cùng luật, KHÔNG khoá muc_tieu
    assert "muc_tieu" not in _cfg(db2) and a2.run_pipeline(seed=42)["ok"]
    ls1 = _sql(db1, "SELECT luat_xep FROM run_history ORDER BY run_id DESC LIMIT 1")[0][0]
    ls2 = _sql(db2, "SELECT luat_xep FROM run_history ORDER BY run_id DESC LIMIT 1")[0][0]
    assert ls1 is not None and ls1 == ls2 and "muc_tieu" not in ls1 and "danh_cho" not in ls1
    assert (_sql(db1, "SELECT student_id, buoi, club_id FROM match_results ORDER BY student_id, buoi")
            == _sql(db2, "SELECT student_id, buoi, club_id FROM match_results ORDER BY student_id, buoi"))
    cot = [r[1] for r in _sql(db1, "PRAGMA table_info(dau_van_tay_chay)")]
    bo = [c for c in cot if c not in ("id", "luc", "run_id", "run_at", "tao_luc")]
    if bo:
        cau = "SELECT %s FROM dau_van_tay_chay ORDER BY 1" % ", ".join(bo)
        assert _sql(db1, cau) == _sql(db2, cau)               # dấu vân tay kết quả y hệt


# ----- fix3: rời `co_hoi` trả lại "Chia 100 điểm" nếu chính thẻ đã tắt nó -----

def test_roi_co_hoi_sang_nang_luc_tra_lai_chia_100_diem(tmp_path):
    a, db = _mo(tmp_path, {"wharton": True})
    assert a.chon_muc_tieu("co_hoi")["ok"]
    assert _luat(db)["wharton"] is False and _cfg(db)["muc_tieu"]["wharton_truoc"] is True
    r = a.chon_muc_tieu("nang_luc")
    assert r["ok"] and r["data"]["canh_bao"] == []                         # không ghi chú thêm
    assert _luat(db)["wharton"] is True and _luat(db)["fa_daa"] is False
    assert "wharton_truoc" not in _cfg(db)["muc_tieu"]
    assert a.get_muc_tieu()["data"]["hien_tai"] == "nang_luc"


def test_roi_co_hoi_sang_danh_cho_tra_lai_chia_100_diem(tmp_path):
    a, db = _mo(tmp_path, {"wharton": True})
    assert a.chon_muc_tieu("co_hoi")["ok"]
    assert a.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    assert _luat(db)["wharton"] is True and "wharton_truoc" not in _cfg(db)["muc_tieu"]
    assert a.get_muc_tieu()["data"]["hien_tai"] == "danh_cho"


def test_co_hoi_ap_lai_giu_gia_tri_cu_va_khong_ghi_chu_lai(tmp_path):
    a, db = _mo(tmp_path, {"wharton": True})
    assert a.chon_muc_tieu("co_hoi")["ok"]
    sau1 = _cfg(db)
    r = a.chon_muc_tieu("co_hoi")
    assert r["ok"] and r["data"]["canh_bao"] == [] and _cfg(db) == sau1
    assert a.chon_muc_tieu("nang_luc")["ok"] and _luat(db)["wharton"] is True


def test_khong_tra_lai_neu_chia_100_von_tat_hoac_da_sua_tay(tmp_path):
    (tmp_path / "tat").mkdir()
    a, db = _mo(tmp_path / "tat", {"wharton": False})
    assert a.chon_muc_tieu("co_hoi")["ok"] and "wharton_truoc" not in _cfg(db)["muc_tieu"]
    assert a.chon_muc_tieu("nang_luc")["ok"] and _luat(db)["wharton"] is False      # vốn tắt: giữ tắt
    (tmp_path / "tay").mkdir()
    b, db2 = _mo(tmp_path / "tay", {"wharton": True})
    assert b.chon_muc_tieu("co_hoi")["ok"]
    cau_hinh_ws.ghi_cau_hinh(db2, cau_hinh_ws.tron_len(_cfg(db2), {"rules": {            # sửa tay ở "Nâng cao"
        "priority": "score+tier", "tier_mode": "strict", "tiers": ["khoi_10"]}}))
    assert b.get_muc_tieu()["data"]["hien_tai"] == "tuy_chinh"
    assert b.chon_muc_tieu("nang_luc")["ok"] and _luat(db2)["wharton"] is False     # có sửa tay: KHÔNG tự trả lại


def test_hoan_tac_sau_khi_roi_co_hoi_tra_dung_trang_thai_co_hoi(tmp_path):
    a, db = _mo(tmp_path, {"wharton": True})
    assert a.chon_muc_tieu("co_hoi")["ok"]
    o_co_hoi = _cfg(db)
    r = a.chon_muc_tieu("nang_luc")
    assert r["ok"] and a.hoan_tac_muc_tieu(r["data"]["hoan_tac"])["ok"]
    assert _cfg(db) == o_co_hoi and _luat(db)["wharton"] is False
    assert a.hoan_tac_muc_tieu(r["data"]["hoan_tac"])["ok"] and _cfg(db) == o_co_hoi   # hoàn tác hai lần


def test_cau_hinh_khoa_wharton_truoc_hop_le_va_khong_co_thi_nhu_cu():
    ok = cau_hinh_ws.chuan_hoa({"muc_tieu": {"id": "co_hoi", "nhom": None, "wharton_truoc": True}})
    assert ok["muc_tieu"] == {"id": "co_hoi", "nhom": None, "wharton_truoc": True}
    assert "wharton_truoc" not in cau_hinh_ws.chuan_hoa({"muc_tieu": {"id": "co_hoi"}})["muc_tieu"]
    for xau in ("true", 1, [True]):
        with pytest.raises(ValueError):
            cau_hinh_ws.chuan_hoa({"muc_tieu": {"id": "co_hoi", "wharton_truoc": xau}})
