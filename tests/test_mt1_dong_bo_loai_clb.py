"""MT1 (gom): kiểm đồng bộ của loại CLB / điểm sàn giữa giao diện (`dat_loai_clb`), CSDL, lần chạy, bảng Quản lý, và
Sổ nhập Excel (nạp lại / xuất). Chỉ backend, không cần Chromium. Dữ liệu MÔ PHỎNG (`SO_NHAP_FA_MAU_120HS.xlsx`)."""

import base64
import os
import sqlite3

import openpyxl

import cau_hinh_ws as ch
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
SO_THUONG = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


def _api(tmp_path, ten="a"):
    api = PipelineAPI(str(tmp_path / (ten + ".db")), thu_muc_xuat=str(tmp_path / ("xuat_" + ten)))
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
    return api


def _nap(api, tep):
    with open(tep, "rb") as f:
        r = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert r["ok"], r
    return r


def _loai(api):
    c = sqlite3.connect(api.db_path)
    try:
        return {a: (b, d) for a, b, d in c.execute("SELECT club_id, loai, diem_san FROM clubs")}
    finally:
        c.close()


def _sua_so_fa(tmp_path, ten, ma_clb, loai=None, san=None):
    """Bản sao sổ FA mẫu với Loại / Điểm sàn của MỘT CLB đổi theo ý (None = để trống ô)."""
    wb = openpyxl.load_workbook(SO_FA)
    ws = wb.worksheets[0]
    hd = [c.value for c in ws[1]]
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, hd.index("Mã CLB") + 1).value == ma_clb:
            ws.cell(r, hd.index("Loại") + 1).value = loai
            ws.cell(r, hd.index("Điểm sàn") + 1).value = san
    p = str(tmp_path / (ten + ".xlsx"))
    wb.save(p)
    return p


def test_dat_loai_bang_giao_dien_di_vao_csdl_bang_quan_ly_va_lan_chay(tmp_path):
    api = _api(tmp_path)
    _nap(api, SO_FA)
    goc = _loai(api)
    assert all(v[0] for v in goc.values())                          # sổ FA mẫu mang sẵn loại
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET loai = NULL, diem_san = NULL")
    r = api.run_pipeline(42)
    assert r["ok"] is False                                         # thiếu loại: lần chạy bị chặn
    assert api.get_san_sang_huy_chuong()["data"]["san_sang"] is False
    for cid, (loai, san) in goc.items():                            # đặt lại từng CLB như người dùng bấm ở bảng
        assert api.dat_loai_clb(cid, loai, san)["ok"]
    assert _loai(api) == goc                                        # CSDL là nguồn duy nhất
    assert {c["club_id"]: (c["loai"], c["diem_san"]) for c in api.list_clubs_admin()["data"]} == goc   # bảng Quản lý
    assert api.get_san_sang_huy_chuong()["data"]["san_sang"] is True
    assert api.run_pipeline(42)["ok"] is True                       # lần chạy đọc đúng giá trị vừa đặt


def test_nap_lai_file_co_cot_khac_gia_tri_ghi_de_gia_tri_dat_tay(tmp_path):
    api = _api(tmp_path)
    _nap(api, SO_FA)
    assert api.dat_loai_clb("THU_2_2", "TU_DO", None)["ok"]
    _nap(api, _sua_so_fa(tmp_path, "khac", "THU_2_2", "Tuyển chọn", 5))
    assert _loai(api)["THU_2_2"] == ("TUYEN_CHON", 5)               # giá trị trong file thắng


def test_nap_lai_file_o_loai_trong_xoa_loai_da_dat(tmp_path):
    api = _api(tmp_path)
    _nap(api, SO_FA)
    assert api.dat_loai_clb("THU_2_2", "TU_DO", None)["ok"]
    _nap(api, _sua_so_fa(tmp_path, "trong", "THU_2_2", None, None))
    assert _loai(api)["THU_2_2"] == (None, None)                    # ô trống = xoá về NULL


def test_nap_lai_file_khong_co_cot_loai_giu_nguyen_gia_tri_da_dat(tmp_path):
    api = _api(tmp_path)
    _nap(api, SO_FA)
    assert api.dat_loai_clb("THU_2_2", "TU_DO", None)["ok"]
    _nap(api, SO_THUONG)                                            # sổ thường: không có cột Loại / Điểm sàn
    assert _loai(api)["THU_2_2"] == ("TU_DO", None)


def test_xuat_so_nhap_mang_loai_va_diem_san_hien_tai(tmp_path):
    api = _api(tmp_path)
    _nap(api, SO_FA)
    assert api.dat_loai_clb("THU_2_2", "TUYEN_CHON", 6)["ok"]
    dat = _loai(api)
    r = api.export_du_lieu_dau_vao()
    assert r["ok"], r
    b = _api(tmp_path, "b")
    _nap(b, r["data"]["path"])
    assert _loai(b) == dat                                          # khứ hồi: xuất rồi nạp vào CSDL trống dựng lại y nguyên
