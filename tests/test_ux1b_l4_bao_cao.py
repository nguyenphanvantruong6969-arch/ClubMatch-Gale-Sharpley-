"""UX1B-L4-B: "Báo cáo tổng hợp" cho hiệu trưởng — bộ dựng thuần `bao_cao_tong_hop.py` + `export_bao_cao_tong_hop`.
Chỉ số tổng hợp: KHÔNG tên, mã, điểm hay số bốc thăm. Số liệu bằng đúng các hàm tổng hợp sẵn có. Dữ liệu MÔ PHỎNG."""

import base64
import os
import re

import bao_cao_tong_hop as bc
import phan_quyen as pq

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
MK = "matkhau-gia-1"


def _chay(api, seed=42):
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert api.run_pipeline(seed)["ok"]


def _html(api, tmp_path):
    r = api.export_bao_cao_tong_hop(str(tmp_path / "bc.html"))
    assert r["ok"], r
    with open(r["data"]["path"], encoding="utf-8") as f:
        return r["data"], f.read()


def test_chua_co_ket_qua_thi_tu_choi_va_khong_tao_tep(api, tmp_path):
    r = api.export_bao_cao_tong_hop(str(tmp_path / "bc.html"))
    assert not r["ok"] and r["errors"][0]["code"] == "xuat_chua_co_ket_qua"
    assert not (tmp_path / "bc.html").exists()


def test_html_khong_co_ma_ten_hay_diem_cua_hoc_sinh(api, tmp_path):
    _chay(api)
    _, html = _html(api, tmp_path)
    with api._ket_noi_doc() as cur:
        hs = cur.execute("SELECT student_id, name FROM students").fetchall()
    assert hs
    for sid, ten in hs:
        assert str(sid) not in html, sid
        assert ten not in html, ten
    assert "<script" not in html and "http://" not in html and "https://" not in html   # tự đủ, không nạp ngoài


def test_so_lieu_khop_ham_tong_hop(api, tmp_path):
    _chay(api)
    du = bc.gom_du_lieu(api)
    dash = api.get_dashboard_status()["data"]
    phu = api.get_do_phu()["data"]
    nv = api.get_phan_bo_nguyen_vong()["data"]
    fill = api.get_club_fill_stats()["data"]
    the = du["the"]
    assert the["n_students"] == dash["n_students"]
    assert the["n_matched"] == dash["n_matched"]
    assert the["n_chua_xep"] == phu["so_em_trang_tay"]
    assert the["n_clubs"] == dash["n_clubs"]
    assert du["nguyen_vong"]["phan_bo"] == nv["phan_bo"]
    assert [c["matched"] for c in du["clb"]] == [c["matched"] for c in fill]
    assert [c["capacity"] for c in du["clb"]] == [c["capacity"] for c in fill]
    assert sum(l["chua_xep"] for l in du["lop"]) == phu["so_em_trang_tay"]
    assert sum(l["n"] for l in du["lop"]) == phu["tong_hoc_sinh"]


def test_html_co_so_lieu_va_chi_tieu_tung_clb(api, tmp_path):
    _chay(api)
    du, html = _html(api, tmp_path)
    d = bc.gom_du_lieu(api)
    assert str(d["the"]["n_students"]) in html
    for c in d["clb"]:
        assert c["name"] in html or re.sub("&", "&amp;", c["name"]) in html
    assert du["path"].endswith(".html")


def test_khong_ghi_de_tep_cu_va_khong_doi_ket_qua(api, tmp_path):
    _chay(api)
    with api._ket_noi_doc() as cur:
        truoc = cur.execute("SELECT * FROM match_results ORDER BY student_id, buoi").fetchall()
        n_run = cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]
    r1 = api.export_bao_cao_tong_hop(str(tmp_path / "bc.html"))
    r2 = api.export_bao_cao_tong_hop(str(tmp_path / "bc.html"))
    assert r1["ok"] and r2["ok"] and r1["data"]["path"] != r2["data"]["path"]
    with api._ket_noi_doc() as cur:
        assert [tuple(x) for x in cur.execute("SELECT * FROM match_results ORDER BY student_id, buoi")] == \
            [tuple(x) for x in truoc]
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == n_run


def test_quyen_giao_vien_va_mot_dong_nhat_ky(api, tmp_path):
    assert pq.QUYEN["export_bao_cao_tong_hop"] == pq.GIAO_VIEN
    _chay(api)
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    r = api.export_bao_cao_tong_hop(str(tmp_path / "gv.html"))
    assert r["ok"], r
    with api._ket_noi_doc() as cur:
        dong = cur.execute("SELECT nguoi, ket_qua FROM nhat_ky_thao_tac WHERE hanh_dong = 'export_bao_cao_tong_hop'"
                           ).fetchall()
    assert len(dong) == 1 and dong[0][0] == "gv1"


def test_nhan_workspace_duoc_dien_vao_tieu_de(api, tmp_path):
    _chay(api)
    _, html = _html(api, tmp_path)
    assert "{person_l}" not in html and "{slot_l}" not in html and "{cohort_l}" not in html


def test_bao_cao_noi_ket_qua_da_cu_khi_du_lieu_doi_sau_lan_xep(api, tmp_path):
    _chay(api)
    _, html = _html(api, tmp_path)
    assert "có thể đã cũ" not in html
    assert api.create_student_if_missing("moi1", "Em Mới")["ok"]          # sửa dữ liệu sau lần xếp
    r = api.export_bao_cao_tong_hop(str(tmp_path / "cu.html"))
    assert r["ok"] and r["data"]["ket_qua_cu"] is True
    with open(r["data"]["path"], encoding="utf-8") as f:
        assert "có thể đã cũ" in f.read()


def test_bao_cao_buoi_co_nhan_chu_hoa_dau_va_don_vi_luot_xep(api, tmp_path):
    """Buổi hiện "Thứ 2" (không phải thu_2); tiêu đề viết hoa chữ đầu; bảng nguyện vọng ghi đúng đơn vị (lượt = người × buổi)."""
    _chay(api)
    _, html = _html(api, tmp_path)
    assert "thu_" not in html and "Thứ 2" in html
    assert "<h2>Học sinh chưa có câu lạc bộ theo lớp</h2>" in html
    assert "Số lượt xếp (học sinh × buổi)" in html
    nv = api.get_phan_bo_nguyen_vong()["data"]
    assert sum(x["so_em"] for x in nv["phan_bo"]) + nv["ngoai_danh_sach"] <= nv["tong_da_xep"]
