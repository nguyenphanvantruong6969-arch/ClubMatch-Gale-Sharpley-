"""VG2-L5: vòng tròn "cổng đăng ký -> Sổ nhập -> phần mềm xếp -> xuất lại -> nạp lại". Dữ liệu MÔ PHỎNG.

Người quản lý tải Sổ nhập từ cổng rồi kéo vào một workspace MỚI (mặc định: chế độ huy chương tắt). Phải được báo trước,
và khi đã bật chế độ thì sổ nạp được, xếp chạy được, và sổ "Xuất dữ liệu đầu vào" nạp lại cho kết quả y hệt."""
import base64
import os
import sqlite3

import cau_hinh_ws as ch
import test_dk3_api as _t3
from api import PipelineAPI
from test_dk4_chot_va_xep import _dang_ky_va_cham
from test_dk3_api import ok

cd = _t3.cd          # fixture của DK3


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _bat_huy_chuong(api):
    cfg = ch.doc_cau_hinh(api.db_path)
    cfg["rules"].update(fa_daa=True, wharton=True)
    ch.ghi_cau_hinh(api.db_path, cfg)


def _ket_qua(api):
    c = sqlite3.connect(api.db_path)
    try:
        return sorted(c.execute("SELECT student_id, club_id, buoi, rank_in_student_pref FROM match_results"))
    finally:
        c.close()


def _kiosk(tmp_path, ten):
    (tmp_path / ten).mkdir()
    return PipelineAPI(str(tmp_path / ten / "app.db"), thu_muc_xuat=str(tmp_path / ten / "xuat"))


def test_so_tu_cong_vao_kiosk_moi_bao_truoc_che_do_huy_chuong(cd, tmp_path):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    so = str(tmp_path / "SO_NHAP_CLB.xlsx")
    ok(api.dk_xuat_so_nhap(qt, so))
    k = _kiosk(tmp_path, "k1")
    canh_bao = [w["code"] for w in ok(k.xem_truoc_so_nhap(_b64(so)))["canh_bao"]]
    assert "so_nhap_canh_bao_huy_chuong_che_do_tat" in canh_bao


def test_so_tu_cong_nap_xep_xuat_lai_nap_lai_trung_khit(cd, tmp_path):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    so = str(tmp_path / "SO_NHAP_CLB.xlsx")
    ok(api.dk_xuat_so_nhap(qt, so))
    k1 = _kiosk(tmp_path, "k1")
    _bat_huy_chuong(k1)                                   # đúng điều nút «Bật chế độ huy chương» làm
    assert "so_nhap_canh_bao_huy_chuong_che_do_tat" not in [
        w["code"] for w in ok(k1.xem_truoc_so_nhap(_b64(so)))["canh_bao"]]
    ok(k1.import_so_nhap(_b64(so)))
    ok(k1.run_pipeline(seed=7))
    kq1 = _ket_qua(k1)
    assert {r[0] for r in kq1} == {"H1", "H2", "H3"}
    lai = ok(k1.export_du_lieu_dau_vao(str(tmp_path / "xuat_lai.xlsx")))["path"]
    assert os.path.exists(lai)
    k2 = _kiosk(tmp_path, "k2")
    _bat_huy_chuong(k2)
    ok(k2.import_so_nhap(_b64(lai)))
    ok(k2.run_pipeline(seed=7))
    assert _ket_qua(k2) == kq1


def test_so_mau_thuong_khong_bao_nham_cot_loai(api, tmp_path):
    """Sổ mẫu thường có cột «Loại» để TRỐNG: không được báo «sổ này có cột Huy chương / Loại»."""
    p = ok(api.tao_so_nhap_mau(str(tmp_path / "mau.xlsx"), "thuong"))["path"]
    import openpyxl
    wb = openpyxl.load_workbook(p)
    clb, hs = wb.worksheets[0], wb.worksheets[1]
    clb.cell(2, 1, "Cờ vua")
    clb.cell(2, 3, 5)
    hs.cell(3, 1, "H1")
    hs.cell(3, 2, "An")
    hs.cell(3, 5, "Cờ vua")
    wb.save(p)
    canh_bao = [w["code"] for w in ok(api.xem_truoc_so_nhap(_b64(p)))["canh_bao"]]
    assert "so_nhap_canh_bao_huy_chuong_che_do_tat" not in canh_bao
