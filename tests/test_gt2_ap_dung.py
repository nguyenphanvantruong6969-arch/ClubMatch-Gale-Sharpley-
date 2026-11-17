"""GT2-L4 — dùng tiêu chí của một lần chạy thử cho lần chính thức kế tiếp.

Dữ liệu MÔ PHỎNG. Kiểm: luật đã lưu = luật của lần thử (khoá ngoài tiêu chí giữ nguyên); mọi bảng kết quả
y nguyên cho đến khi chạy chính thức; lần chính thức kế tiếp ghi `run_history.luat_xep` = luật của lần thử;
lần chính thức hoặc mã lạ thì báo lỗi `gt2_*` và không ghi gì."""

import json
import os
import shutil
import sqlite3
import sys

import api as api_mod
import cau_hinh_ws
import rbda_priority_pipeline as rb
import workspace as ws

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

LUAT_THU = {"priority": "tier", "tiers": ["khong_co_nhom_nay"]}
BANG = ("match_results", "ket_qua_truoc", "ket_qua_thu", "dau_van_tay_chay", "stb_lock", "run_meta",
        "students", "stb_buoi")


def _mo(tmp_path):
    os.makedirs(str(tmp_path / "nguon"))
    nguon = d.nap_bo(str(tmp_path / "nguon"), d.BO_DU_LIEU[1][1])
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    a = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    assert a.run_pipeline(seed=42)["ok"]
    return a, db, slug


def _sql(db, cau, tham=()):
    c = sqlite3.connect(db)
    try:
        return c.execute(cau, tham).fetchall()
    finally:
        c.close()


def _chup(db):
    return {b: _sql(db, "SELECT * FROM %s" % b) for b in BANG if b != "run_meta"}


def test_luat_da_luu_bang_luat_lan_thu_va_khoa_khac_giu_nguyen(tmp_path):
    a, db, slug = _mo(tmp_path)
    truoc = cau_hinh_ws.doc_cau_hinh(db)
    r = a.run_thu(LUAT_THU)
    assert r["ok"], r
    k = a.ap_dung_tieu_chi(r["data"]["run_id"], slug)
    assert k["ok"], k
    sau = cau_hinh_ws.doc_cau_hinh(db)
    ghi = rb.luat_xep_hieu_luc(json.loads(
        _sql(db, "SELECT luat_xep FROM run_history WHERE run_id = ?", (r["data"]["run_id"],))[0][0]))
    assert {x: sau["rules"][x] for x in rb.LUAT_XEP_MAC_DINH} == ghi
    assert rb.luat_xep_hieu_luc(sau["rules"]) == rb.luat_xep_hieu_luc(r["data"]["luat"])
    assert sau["rules"]["priority"] == "tier"
    assert sau["rules"]["wharton"] is False
    assert {x: v for x, v in sau.items() if x != "rules"} == {x: v for x, v in truoc.items() if x != "rules"}
    assert {x: v for x, v in sau["rules"].items() if x not in rb.LUAT_XEP_MAC_DINH} == \
        {x: v for x, v in truoc["rules"].items() if x not in rb.LUAT_XEP_MAC_DINH}


def test_khong_bang_ket_qua_nao_doi_cho_den_khi_chay_chinh_thuc(tmp_path):
    a, db, slug = _mo(tmp_path)
    r = a.run_thu(LUAT_THU)
    truoc = _chup(db)
    n_lich_su = _sql(db, "SELECT COUNT(*) FROM run_history")
    assert a.ap_dung_tieu_chi(r["data"]["run_id"], slug)["ok"]
    assert _chup(db) == truoc
    assert _sql(db, "SELECT COUNT(*) FROM run_history") == n_lich_su


def test_lan_chinh_thuc_ke_tiep_ghi_dung_luat_cua_lan_thu(tmp_path):
    a, db, slug = _mo(tmp_path)
    r = a.run_thu(LUAT_THU)
    assert a.ap_dung_tieu_chi(r["data"]["run_id"], slug)["ok"]
    assert a.run_pipeline(seed=42)["ok"]
    dong = _sql(db, "SELECT luat_xep, loai_chay FROM run_history ORDER BY run_id DESC LIMIT 1")[0]
    assert dong[1] is None
    assert json.loads(dong[0]) == json.loads(
        _sql(db, "SELECT luat_xep FROM run_history WHERE run_id = ?", (r["data"]["run_id"],))[0][0])


def test_ma_lan_chinh_thuc_hoac_la_bi_tu_choi_va_khong_ghi(tmp_path):
    a, db, slug = _mo(tmp_path)
    goc = _sql(db, "SELECT run_id FROM run_history WHERE loai_chay IS NULL ORDER BY run_id DESC")[0][0]
    cfg = cau_hinh_ws.doc_cau_hinh(db)
    for x in (goc, 9999, "abc", None, True, -1):
        k = a.ap_dung_tieu_chi(x, slug)
        assert not k["ok"] and k["errors"][0]["code"] == "gt2_lan_chay_khong_co", (x, k)
    assert cau_hinh_ws.doc_cau_hinh(db) == cfg


def test_khong_tu_dong_chay_va_khong_dung_run_thu(tmp_path):
    a, db, slug = _mo(tmp_path)
    r = a.run_thu(LUAT_THU)
    n = _sql(db, "SELECT COUNT(*) FROM run_history")
    a.ap_dung_tieu_chi(r["data"]["run_id"], slug)
    assert _sql(db, "SELECT COUNT(*) FROM run_history") == n
