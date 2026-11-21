"""MT1-X1: Sổ nhập xuất ra mang đủ cột FA của CLB (Loại, Điểm sàn, Tối thiểu, Sức chứa phòng) khi cần,
và y nguyên như cũ ở chế độ thường. Chỉ backend. Dữ liệu MÔ PHỎNG (`du_lieu_test/`)."""

import sqlite3

import openpyxl

from api import PipelineAPI
from test_mt1_dong_bo_loai_clb import SO_FA, SO_THUONG, _api, _loai, _nap

COT_FA = ["Loại", "Điểm sàn", "Tối thiểu", "Sức chứa phòng"]


def _api_thuong(tmp_path, ten="t"):
    return PipelineAPI(str(tmp_path / (ten + ".db")), thu_muc_xuat=str(tmp_path / ("xuat_" + ten)))


def _tieu_de_clb(path):
    return [c.value for c in openpyxl.load_workbook(path).worksheets[0][1]]


def _gia_tri(path):
    wb = openpyxl.load_workbook(path)
    return {ws.title: [[c.value for c in row] for row in ws.iter_rows()] for ws in wb.worksheets}


def test_che_do_thuong_khong_them_cot_fa(tmp_path):
    api = _api_thuong(tmp_path)
    _nap(api, SO_THUONG)
    r = api.export_du_lieu_dau_vao()
    assert r["ok"], r
    hd = _tieu_de_clb(r["data"]["path"])
    assert not any(c in hd for c in COT_FA)
    assert "Giữ chỗ" not in openpyxl.load_workbook(r["data"]["path"]).sheetnames
    # tham chiếu: đường cũ (chỉ khoá cũ của CLB) qua so_nhap.ghi_so_nhap
    import so_nhap
    with api._ket_noi_doc() as cur:
        clubs, students, _, _ = api._du_lieu_so_nhap(cur)
    assert not any(k in c for c in clubs for k in so_nhap.KHOA_FA)
    ref = str(tmp_path / "ref.xlsx")
    so_nhap.ghi_so_nhap(ref, clubs, students, cfg=api._cfg_ws(nghiem=True),
                        co_lop=any(x.get("class_id") for x in students))
    assert _gia_tri(ref) == _gia_tri(r["data"]["path"])               # mọi ô mọi sheet như đường cũ


def test_fa_bat_loai_null_cot_co_nhung_rong_va_khu_hoi_ra_null(tmp_path):
    api = _api(tmp_path)
    _nap(api, SO_FA)
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET loai = NULL, diem_san = NULL, so_toi_thieu = NULL, suc_chua_phong = NULL")
    r = api.export_du_lieu_dau_vao()
    assert r["ok"], r
    p = r["data"]["path"]
    assert all(c in _tieu_de_clb(p) for c in COT_FA)
    ws = openpyxl.load_workbook(p).worksheets[0]
    hd = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:
            assert all(row[hd.index(c)] is None for c in COT_FA)
    b = _api(tmp_path, "b")
    _nap(b, p)
    assert all(v == (None, None) for v in _loai(b).values())


def test_fa_tat_nhung_mot_clb_co_loai_van_khu_hoi(tmp_path):
    api = _api_thuong(tmp_path)
    _nap(api, SO_THUONG)
    with api._ket_noi_ghi() as cur:
        ma = cur.execute("SELECT club_id FROM clubs ORDER BY club_id").fetchone()[0]
        cur.execute("UPDATE clubs SET loai = 'GIOI_HAN', diem_san = 5 WHERE club_id = ?", (ma,))
    r = api.export_du_lieu_dau_vao()
    assert r["ok"], r
    assert all(c in _tieu_de_clb(r["data"]["path"]) for c in COT_FA)
    # Nạp ra CSDL FA bật (FA tắt thì bước nạp bỏ qua cột Loại — hành vi có sẵn, xem xem_truoc_so_nhap).
    b = _api(tmp_path, "b")
    _nap(b, r["data"]["path"])
    c = sqlite3.connect(b.db_path)
    try:
        assert c.execute("SELECT loai, diem_san FROM clubs WHERE club_id = ?", (ma,)).fetchone() == ("GIOI_HAN", 5)
    finally:
        c.close()


def _giu_cho(api):
    c = sqlite3.connect(api.db_path)
    try:
        return set(c.execute("SELECT club_id, student_id FROM giu_cho"))
    finally:
        c.close()


def _thuoc_tinh(api):
    c = sqlite3.connect(api.db_path)
    try:
        return {r[0]: r[1:] for r in c.execute(
            "SELECT club_id, loai, diem_san, so_toi_thieu, suc_chua_phong FROM clubs")}
    finally:
        c.close()


def test_khu_hoi_day_du_loai_diem_san_toi_thieu_phong_va_giu_cho(tmp_path):
    import fa_daa
    api = _api(tmp_path)
    _nap(api, SO_FA)
    with api._ket_noi_ghi() as cur:
        ma = [r[0] for r in cur.execute("SELECT club_id FROM clubs ORDER BY club_id LIMIT 2")]
        cur.execute("UPDATE clubs SET loai='TUYEN_CHON', diem_san=7, so_toi_thieu=3, suc_chua_phong=40 "
                    "WHERE club_id=?", (ma[0],))
        cur.execute("UPDATE clubs SET loai='GIOI_HAN', diem_san=NULL, so_toi_thieu=2, suc_chua_phong=25 "
                    "WHERE club_id=?", (ma[1],))
        hs = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id LIMIT 3")]
        fa_daa.thay_giu_cho(cur, [(ma[0], hs[0]), (ma[0], hs[1]), (ma[1], hs[2])])
    dat, gc = _thuoc_tinh(api), _giu_cho(api)
    assert len(gc) == 3
    r = api.export_du_lieu_dau_vao()
    assert r["ok"], r
    b = _api(tmp_path, "b")
    _nap(b, r["data"]["path"])
    assert _thuoc_tinh(b) == dat
    assert _giu_cho(b) == gc


def test_giu_cho_sheet_chi_khi_fa_bat_va_rong_thi_chi_co_tieu_de(tmp_path):
    api = _api(tmp_path)
    _nap(api, SO_FA)
    with api._ket_noi_ghi() as cur:
        cur.execute("DELETE FROM giu_cho")
    p = api.export_du_lieu_dau_vao()["data"]["path"]
    wb = openpyxl.load_workbook(p)
    assert "Giữ chỗ" in wb.sheetnames
    assert [[c.value for c in r] for r in wb["Giữ chỗ"].iter_rows()] == [["Mã CLB", "Mã học sinh"]]
    t = _api_thuong(tmp_path)
    _nap(t, SO_THUONG)
    assert "Giữ chỗ" not in openpyxl.load_workbook(t.export_du_lieu_dau_vao()["data"]["path"]).sheetnames


def test_giu_cho_cua_hoc_sinh_khong_co_nguyen_vong_van_khu_hoi(tmp_path):
    import fa_daa
    api = _api(tmp_path)
    _nap(api, SO_FA)
    with api._ket_noi_ghi() as cur:
        ma = cur.execute("SELECT club_id FROM clubs ORDER BY club_id").fetchone()[0]
        sid = cur.execute("SELECT student_id FROM students ORDER BY student_id").fetchone()[0]
        cur.execute("DELETE FROM preferences WHERE student_id = ?", (sid,))
        fa_daa.thay_giu_cho(cur, [(ma, sid)])
    r = api.export_du_lieu_dau_vao()
    assert r["ok"], r
    b = _api(tmp_path, "b")
    _nap(b, r["data"]["path"])
    assert _giu_cho(b) == {(ma, sid)}
