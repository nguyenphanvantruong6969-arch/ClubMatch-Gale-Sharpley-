"""UX1A-L5b: ô huy chương nhận Vàng/Bạc/Đồng (không phân biệt hoa/thường, dấu, tiếng Anh) khi chế độ huy chương BẬT;
đổi về 60/30/10 ngay ở lớp đọc, nên giá trị lưu và kết quả xếp không đổi. Chữ lạ vẫn báo lỗi cũ; chế độ tắt không đổi.
Dữ liệu MÔ PHỎNG (du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx)."""

import base64
import io
import os

import openpyxl
import pytest

import so_nhap
import workspace as ws
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
DICH = {"60": "Vàng", "30": "Bạc", "10": "Đồng"}


def _api(tmp_path, ten, fa=True):
    goc = tmp_path / ten
    goc.mkdir()
    slug = ws.tao(str(goc), "Trường học", None)
    api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / (ten + "_x")),
                      thu_muc_goc_ws=str(goc))
    if fa:
        assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    return api


def _so_voi_chu(doi):
    """Sổ mẫu FA với mọi ô huy chương (60/30/10) đổi bằng `doi(so) -> chữ`. Trả (base64, số ô đã đổi)."""
    wb = openpyxl.load_workbook(SO_FA)
    sheet = next(w for w in wb.worksheets if "Học sinh" in w.title or "hoc sinh" in w.title.lower())
    cot = set()
    for r in list(sheet.iter_rows(min_row=1, max_row=2)):
        for c in r:
            if isinstance(c.value, str) and "huy chương" in so_nhap.bo_dau(c.value) + "":
                cot.add(c.column)
            if isinstance(c.value, str) and "huy chuong" in so_nhap.bo_dau(c.value):
                cot.add(c.column)
    n = 0
    for r in sheet.iter_rows(min_row=3):
        for c in r:
            if c.column in cot and c.value is not None and str(c.value).strip() in DICH:
                c.value = doi(str(c.value).strip())
                n += 1
    bo = io.BytesIO()
    wb.save(bo)
    return base64.b64encode(bo.getvalue()).decode(), n


def _bids(api):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute("SELECT * FROM wharton_bids ORDER BY 1, 2, 3, 4")]


def _ket_qua(api):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute("SELECT * FROM match_results ORDER BY 1, 2, 3")]


def test_so_ban_so_voi_so_ban_chu_cho_wharton_bids_va_match_results_giong_het(tmp_path):
    so_so = base64.b64encode(open(SO_FA, "rb").read()).decode()
    so_chu, n = _so_voi_chu(lambda v: DICH[v])
    assert n > 100                                                   # có đổi thật
    a, b = _api(tmp_path, "a"), _api(tmp_path, "b")
    ra, rb = a.import_so_nhap(so_so), b.import_so_nhap(so_chu)
    assert ra["ok"] and rb["ok"], (ra.get("errors"), rb.get("errors"))
    assert _bids(a) == _bids(b) and len(_bids(a)) > 100
    assert a.run_pipeline(42)["ok"] and b.run_pipeline(42)["ok"]
    assert _ket_qua(a) == _ket_qua(b) and len(_ket_qua(a)) > 100


@pytest.mark.parametrize("kieu", [
    lambda v: {"60": "VÀNG", "30": "BẠC", "10": "ĐỒNG"}[v],
    lambda v: {"60": "vang", "30": "bac", "10": "dong"}[v],
    lambda v: {"60": "Gold", "30": "SILVER", "10": "bronze"}[v],
    lambda v: {"60": " Vàng ", "30": "bạc", "10": "Đồng"}[v],
])
def test_hoa_thuong_khong_dau_va_tieng_anh_deu_ra_60_30_10(tmp_path, kieu):
    so_so = base64.b64encode(open(SO_FA, "rb").read()).decode()
    so_chu, _ = _so_voi_chu(kieu)
    a, b = _api(tmp_path, "a"), _api(tmp_path, "b")
    assert a.import_so_nhap(so_so)["ok"] and b.import_so_nhap(so_chu)["ok"]
    assert _bids(a) == _bids(b)


def test_chu_la_van_bao_fa_huy_chuong_gia_tri_sai(tmp_path):
    so_chu, _ = _so_voi_chu(lambda v: "Kim cương")
    a = _api(tmp_path, "a")
    kq = a.xem_truoc_so_nhap(so_chu)
    ma = [w["code"] for w in kq["data"]["canh_bao"]]
    assert "fa_huy_chuong_gia_tri_sai" in ma


def test_che_do_tat_khong_doi_chu_khong_duoc_anh_xa(tmp_path):
    so_chu, _ = _so_voi_chu(lambda v: DICH[v])
    tat = _api(tmp_path, "tat", fa=False)
    du, loi = tat._doc_so_nhap(so_chu)
    assert loi is None
    w_tat = {x["diem_w"] for s in du["students"] for x in s["nv"] if x.get("diem_w")}
    assert w_tat & {"Vàng", "Bạc", "Đồng"} and not (w_tat & {"60", "30", "10"} - {"60", "30", "10"})
    bat = _api(tmp_path, "bat")
    du2, _ = bat._doc_so_nhap(so_chu)
    w_bat = {x["diem_w"] for s in du2["students"] for x in s["nv"] if x.get("diem_w")}
    assert w_bat <= {"60", "30", "10"} and w_bat


def test_huong_dan_so_huy_chuong_noi_vang_bac_dong_va_so_mau_thuong_khong_co_dong_nay(tmp_path):
    kq = _api(tmp_path, "m", fa=True).tao_so_nhap_mau(str(tmp_path / "hc.xlsx"), "huy_chuong")
    chu = str([[c.value for c in r] for w in openpyxl.load_workbook(kq["data"]["path"]).worksheets
               for r in w.iter_rows()])
    assert "Vàng / Bạc / Đồng hoặc 60 / 30 / 10" in chu and "60 (vàng)" not in chu
    thuong = _api(tmp_path, "t", fa=False).tao_so_nhap_mau(str(tmp_path / "th.xlsx"), "thuong")
    chu2 = str([[c.value for c in r] for w in openpyxl.load_workbook(thuong["data"]["path"]).worksheets
                for r in w.iter_rows()])
    assert "Vàng" not in chu2 and "huy chương" not in chu2.lower()


def test_chuan_hoa_chu_huy_chuong_dem_o_da_doi():
    du = {"students": [{"nv": [{"diem_w": "Vàng"}, {"diem_w": "60"}, {"diem_w": ""}, {"diem_w": "xyz"}]}]}
    assert so_nhap.chuan_hoa_chu_huy_chuong(du) == 1
    assert [x["diem_w"] for x in du["students"][0]["nv"]] == ["60", "60", "", "xyz"]
