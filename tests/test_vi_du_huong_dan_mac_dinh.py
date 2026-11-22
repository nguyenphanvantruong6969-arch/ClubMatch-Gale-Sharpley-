# -*- coding: utf-8 -*-
"""Sổ ví dụ của hướng dẫn (`du_lieu_test/vi_du_huong_dan/SO_NHAP_VIDU.xlsx`) chạy được ở
workspace MẶC ĐỊNH (điểm quyết tâm bật sẵn, A13.13).

Trước đây sổ sinh từ ba tệp CSV nhưng bỏ mất cột "Điểm quyết tâm" (`wp_k` có trong CSV), nên
người làm đúng 5 bước của `HUONG_DAN_SU_DUNG.md` bị chặn ở bước kiểm dữ liệu
(`wharton_ho_so_chua_hop_le`). Dữ liệu là MÔ PHỎNG.
"""

import base64
import os
import sqlite3

import openpyxl

import workspace
from api import PipelineAPI
from test_vi_du_huong_dan import CHUA_XEP, KET_QUA_DUNG

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO = os.path.join(GOC, "du_lieu_test", "vi_du_huong_dan", "SO_NHAP_VIDU.xlsx")


def _api_mac_dinh(tmp_path):
    slug = workspace.tao(str(tmp_path), workspace.TEN_TRUONG_HOC, None)
    return PipelineAPI(workspace.duong_dan_db(str(tmp_path), slug), thu_muc_goc_ws=str(tmp_path))


def test_so_vi_du_co_cot_diem_quyet_tam():
    ws = openpyxl.load_workbook(SO, read_only=True)["2. Học sinh"]
    tieu_de = [c for r in ws.iter_rows(min_row=1, max_row=2, values_only=True) for c in r if c]
    assert "Điểm quyết tâm" in tieu_de


def test_so_vi_du_chay_duoc_o_workspace_mac_dinh(tmp_path):
    api = _api_mac_dinh(tmp_path)
    with open(SO, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    xem = api.xem_truoc_so_nhap(b64)
    assert xem["ok"], xem
    assert (xem["data"]["n_clb"], xem["data"]["n_buoi"], xem["data"]["n_hoc_sinh"]) == (4, 1, 10)
    assert api.import_so_nhap(b64)["ok"]
    assert api.get_data_health_report()["data"]["warnings"] == []      # hướng dẫn: "0 cảnh báo"

    kq = api.run_pipeline(seed=42)
    assert kq["ok"], kq["errors"]
    with sqlite3.connect(api.db_path) as c:
        rows = c.execute("SELECT student_id, club_id, rank_in_student_pref, matched_tier "
                         "FROM match_results").fetchall()
    xep = {s: (cid, r, t) for s, cid, r, t in rows if cid}
    assert xep == KET_QUA_DUNG                                         # bảng in trong hướng dẫn
    assert CHUA_XEP not in xep
