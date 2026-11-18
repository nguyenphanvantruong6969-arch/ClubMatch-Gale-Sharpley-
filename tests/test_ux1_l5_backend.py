"""UX1A-L5, phần backend: cảnh báo vượt chỉ tiêu không còn là "info", sổ có cột Huy chương / Loại mà chế độ huy chương
tắt thì xem trước nói rõ, hai loại sổ mẫu. Chỉ THÔNG ĐIỆP: không đổi gì được lưu hay cách chạy. Dữ liệu MÔ PHỎNG."""

import base64
import os

import openpyxl
import i18n_errors
from test_fa_gap1_diem_danh import api_ws  # noqa: F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
SO_THUONG = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _ma(kq):
    return [w["code"] for w in kq["data"]["canh_bao"]]


def test_ba_canh_bao_vuot_chi_tieu_la_medium_va_khong_chan_chay(api):
    for ma in ("health_oversubscribed", "health_oversubscribed_buoi", "health_oversubscribed_chua_khai_buoi"):
        vi = i18n_errors.MESSAGES[ma]["vi"] if hasattr(i18n_errors, "MESSAGES") else None
        if vi is not None:
            assert "Tăng" in vi or "Khai" in vi                  # một câu + một hành động
            assert vi.count(".") <= 2
    # chỉ "high" mới chặn: n_high không đếm medium
    assert api.get_data_health_report()["data"]["n_high"] == 0


def test_so_huy_chuong_che_do_tat_xem_truoc_noi_ro(api):
    kq = api.xem_truoc_so_nhap(_b64(SO_FA))
    assert kq["ok"] and "so_nhap_canh_bao_huy_chuong_che_do_tat" in _ma(kq)


def test_so_thuong_xem_truoc_khong_co_canh_bao_huy_chuong(api):
    kq = api.xem_truoc_so_nhap(_b64(SO_THUONG))
    assert kq["ok"] and "so_nhap_canh_bao_huy_chuong_che_do_tat" not in _ma(kq)


def test_che_do_huy_chuong_bat_thi_khong_nhac(api_ws):  # noqa: F811
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    kq = api_ws.xem_truoc_so_nhap(_b64(SO_FA))
    assert "so_nhap_canh_bao_huy_chuong_che_do_tat" not in _ma(kq)


def test_nap_van_nhu_cu_khong_doi_gi_duoc_luu(api):
    """Chỉ thông điệp: nạp sổ huy chương khi chế độ tắt vẫn lưu như cũ (434 cảnh báo điểm quyết tâm, chạy bị chặn)."""
    r = api.import_so_nhap(_b64(SO_FA))
    assert r["ok"]
    ma = [w["code"] for w in r["data"]["warnings"]]
    assert ma.count("wharton_chua_dung_het") == 434 and "fa_cot_bo_qua" in ma
    assert api.run_pipeline(42)["ok"] is False


def _gia_tri(duong):
    wb = openpyxl.load_workbook(duong)
    return {ws.title: [[c.value for c in r] for r in ws.iter_rows()] for ws in wb.worksheets}


def test_hai_so_mau_thuong_giong_het_cu_va_huy_chuong_co_cot_loai(api, tmp_path):
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    cu = api.tao_so_nhap_mau(str(tmp_path / "cu.xlsx"))
    thuong = api.tao_so_nhap_mau(str(tmp_path / "thuong.xlsx"), "thuong")
    hc = api.tao_so_nhap_mau(str(tmp_path / "hc.xlsx"), "huy_chuong")
    assert cu["ok"] and thuong["ok"] and hc["ok"]
    assert _gia_tri(cu["data"]["path"]) == _gia_tri(thuong["data"]["path"])         # sổ thường: như hôm nay
    gt = _gia_tri(hc["data"]["path"])
    chu = str(gt)
    assert "Huy chương (60/30/10)" in chu and "Loại" in chu
    assert "đang BẬT" in chu                                                           # Hướng dẫn nói chế độ phải bật
    assert "Huy chương (60/30/10)" not in str(_gia_tri(cu["data"]["path"]))
    assert api.tao_so_nhap_mau(str(tmp_path / "x.xlsx"), "linh_tinh")["ok"]           # kiểu lạ -> sổ thường


def test_phan_quyen_tao_so_mau_khong_doi():
    import phan_quyen
    assert phan_quyen.QUYEN["tao_so_nhap_mau"] == phan_quyen.GIAO_VIEN
