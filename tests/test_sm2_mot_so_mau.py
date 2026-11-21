"""SM2-L2: MỘT sổ mẫu luôn đủ cấu trúc (cột FA, Giờ, Địa điểm, Lớp, sheet Giữ chỗ, từ điển cột). Dữ liệu MÔ PHỎNG."""
import base64
import io

import openpyxl
import pytest

import cau_hinh_ws as ch
import so_nhap


def _mo(api, tmp_path, kieu="thuong"):
    p = str(tmp_path / "mau.xlsx")
    ra = api.tao_so_nhap_mau(p, kieu)
    assert ra["ok"], ra
    return p, openpyxl.load_workbook(p)


def _tieu_de(ws, n=1):
    return [o.value for r in range(1, n + 1) for o in ws[r] if o.value is not None]


@pytest.mark.parametrize("luat", [None, {"wharton": True}, {"fa_daa": True, "wharton": True}])
def test_so_mau_du_cau_truc_moi_che_do(api, tmp_path, luat):
    if luat:
        ch.ghi_cau_hinh(api.db_path, {"rules": luat})
    _, wb = _mo(api, tmp_path)
    clb = _tieu_de(wb[wb.sheetnames[0]])
    for c in so_nhap.COT_CLB + so_nhap.COT_FA + so_nhap.COT_GIO:
        assert c in clb, c
    hs = _tieu_de(wb[wb.sheetnames[1]], 2)
    assert "Lớp" in hs
    assert so_nhap.SHEET_GIU_CHO in wb.sheetnames
    chu = "\n".join(str(o.value) for h in wb[so_nhap.SHEET_HD].iter_rows() for o in h if o.value)
    assert "TỪ ĐIỂN CỘT" in chu
    fa = bool(luat and luat.get("fa_daa"))
    assert (so_nhap.TEN_COT_HUY_CHUONG in "|".join(hs)) == fa


def test_kieu_huy_chuong_van_ep_nhan_huy_chuong(api, tmp_path):
    _, wb = _mo(api, tmp_path, "huy_chuong")
    assert so_nhap.TEN_COT_HUY_CHUONG in "|".join(_tieu_de(wb[wb.sheetnames[1]], 2))


def test_so_mau_dien_tay_nap_duoc_o_workspace_mac_dinh_khong_canh_bao_moi(api, tmp_path):
    p, wb = _mo(api, tmp_path)
    ws, wh = wb[wb.sheetnames[0]], wb[wb.sheetnames[1]]
    ws.append(["Cờ vua", None, 5, None, None, None])
    ws.append(["Bóng đá", None, 5, None, None, None])
    td = [o.value for o in wh[1]]
    nv1, nv2 = td.index("Nguyện vọng 1") + 1, td.index("Nguyện vọng 2") + 1
    for i in range(3):
        for c, v in ((1, "h%d" % i), (2, "Em %d" % i), (nv1, "Cờ vua"), (nv2, "Bóng đá")):
            wh.cell(row=3 + i, column=c, value=v)
    b = io.BytesIO()
    wb.save(b)
    ra = api.import_so_nhap(base64.b64encode(b.getvalue()).decode())
    assert ra["ok"], ra
    # Chỉ hai cảnh báo có từ trước (lớp trống, quỹ điểm quyết tâm chưa tiêu): không cảnh báo mới nào
    # về cột FA / Giờ / Giữ chỗ để trống.
    ma = {w["code"] for w in ra["data"]["warnings"]}
    assert ma <= {"so_nhap_canh_bao_thieu_lop", "wharton_chua_dung_het"}, ma


def test_ghi_so_nhap_mac_dinh_khong_doi(tmp_path):
    p = str(tmp_path / "a.xlsx")
    so_nhap.ghi_so_nhap(p, [], [])
    wb = openpyxl.load_workbook(p)
    assert so_nhap.SHEET_GIU_CHO not in wb.sheetnames
    assert "Loại" not in _tieu_de(wb[wb.sheetnames[0]])


def _chu_hd(wb):
    return "\n".join(str(o.value) for h in wb[so_nhap.SHEET_HD].iter_rows() for o in h if o.value)


def test_tu_dien_khong_chi_toi_sheet_khong_co_o_workspace_nhan_rieng(tmp_path):
    """SM2 checker lỗi 1: nhãn riêng (công ty) -> sổ vẫn đủ cấu trúc nhưng không có từ điển viết bằng từ vựng trường."""
    from test_ws_so_nhap import CONG_TY
    cfg = ch.chuan_hoa({"industry": "company", **CONG_TY})
    p = str(tmp_path / "ct.xlsx")
    so_nhap.ghi_so_nhap(p, [], [], cfg=cfg, luon_co_cot_w=True, co_lop=True, day_du=True)
    wb = openpyxl.load_workbook(p)
    assert wb.sheetnames[:2] == ["1. Dự án", "2. Nhân viên"] and so_nhap.SHEET_GIU_CHO in wb.sheetnames
    chu = _chu_hd(wb)
    assert "TỪ ĐIỂN CỘT" not in chu
    assert "1. CLB" not in chu and "2. Học sinh" not in chu


def test_tu_dien_van_co_o_truong_hoc_mac_dinh(tmp_path):
    p = str(tmp_path / "th.xlsx")
    so_nhap.ghi_so_nhap(p, [], [], cfg=ch.chuan_hoa({}), luon_co_cot_w=True, co_lop=True, day_du=True)
    assert "TỪ ĐIỂN CỘT" in _chu_hd(openpyxl.load_workbook(p))
