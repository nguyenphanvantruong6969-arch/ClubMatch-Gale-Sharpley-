"""SN-COT-LA: cột có tiêu đề nhưng phần mềm không nhận ra mà chứa dữ liệu -> CẢNH BÁO (không lỗi,
không đổi gì được lưu). Trước đây chỉ cột KHÔNG tiêu đề mới được báo. Dữ liệu là MÔ PHỎNG."""

import base64
import io

import pytest

openpyxl = pytest.importorskip("openpyxl")

import so_nhap  # noqa: E402
from _wharton import tat_wharton  # noqa: E402
from api import PipelineAPI  # noqa: E402

CLUBS = [{"club_id": "clb_a", "name": "CLB A", "capacity": 2, "reserve_capacity": 0,
          "reserve_group": "", "buoi": "thu_2"}]
HS = [{"student_id": "HS01", "name": "An", "reserve_group": "",
       "nv": [{"club_id": "clb_a", "thi": False, "diem": ""}]}]


def _so():
    buf = io.BytesIO()
    so_nhap.ghi_so_nhap(buf, CLUBS, HS)
    buf.seek(0)
    return openpyxl.load_workbook(buf)


def _b64(wb):
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def _ma(canh_bao):
    return [w["code"] for w in canh_bao]


@pytest.fixture
def api(tmp_path):
    a = PipelineAPI(str(tmp_path / "app.db"))
    tat_wharton(a)
    return a


def _them_cot(ws, hang_tieu_de, ten, dong_du_lieu, gia_tri):
    c = ws.max_column + 1
    ws.cell(hang_tieu_de, c, ten)
    if gia_tri is not None:
        ws.cell(dong_du_lieu, c, gia_tri)


def test_sach_thi_khong_canh_bao(api):
    r = api.xem_truoc_so_nhap(_b64(_so()))
    assert r["ok"] and "so_nhap_canh_bao_cot_la" not in _ma(r["data"]["canh_bao"])


def test_cot_la_hoc_sinh_co_du_lieu(api):
    wb = _so()
    _them_cot(wb["2. Học sinh"], 2, "Email", 3, "an@x.vn")
    r = api.xem_truoc_so_nhap(_b64(wb))
    assert r["ok"]
    w = [w for w in r["data"]["canh_bao"] if w["code"] == "so_nhap_canh_bao_cot_la"]
    assert len(w) == 1 and w[0]["params"]["n"] == 1 and "Email" in w[0]["params"]["ten"]


def test_cot_la_clb_co_du_lieu(api):
    wb = _so()
    _them_cot(wb["1. CLB"], 1, "Phòng", 2, "P101")
    r = api.xem_truoc_so_nhap(_b64(wb))
    w = [w for w in r["data"]["canh_bao"] if w["code"] == "so_nhap_canh_bao_cot_la"]
    assert len(w) == 1 and "Phòng" in w[0]["params"]["ten"]


def test_cot_la_khong_du_lieu_thi_im(api):
    wb = _so()
    _them_cot(wb["2. Học sinh"], 2, "Ghi chú", 3, None)
    r = api.xem_truoc_so_nhap(_b64(wb))
    assert "so_nhap_canh_bao_cot_la" not in _ma(r["data"]["canh_bao"])


def test_nap_that_cung_canh_bao_va_khong_doi_du_lieu(api):
    wb = _so()
    _them_cot(wb["2. Học sinh"], 2, "Email", 3, "an@x.vn")
    r = api.import_so_nhap(_b64(wb))
    assert r["ok"] and "so_nhap_canh_bao_cot_la" in _ma(r["data"]["warnings"])
