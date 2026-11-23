# -*- coding: utf-8 -*-
"""SF-A1 — nạp Sổ an toàn: ST-B-003, ST-A-004, ST-B-004 (phần backend), ST-A-002.
Bản sao hồi quy nhỏ của tests_stress/ (CI chạy tests/, không chạy tests_stress/). DỮ LIỆU MÔ PHỎNG."""
import base64
import glob
import io
import os
import sqlite3

import openpyxl
import pytest

import cau_hinh_ws as ch
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_150 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DOI_CHE_DO_150HS.xlsx")
HUY_CHUONG = {"wharton": True, "fa_daa": True}


def _b64(wb):
    out = io.BytesIO()
    wb.save(out)
    return base64.b64encode(out.getvalue()).decode()


def _so():
    return openpyxl.load_workbook(SO_150)


def _api(tmp_path, name="a"):
    api = PipelineAPI(str(tmp_path / (name + ".db")), thu_muc_xuat=str(tmp_path / ("x_" + name)))
    ch.ghi_cau_hinh(api.db_path, {"rules": HUY_CHUONG})
    return api


def _dem(api, *bang):
    c = sqlite3.connect(api.db_path)
    try:
        return tuple(c.execute("SELECT COUNT(*) FROM %s" % b).fetchone()[0] for b in bang)
    finally:
        c.close()


def _ma(res):
    return [e["code"] for e in (res["data"].get("warnings") or res["data"].get("canh_bao") or [])]


@pytest.fixture()
def api_da_nap(tmp_path):
    api = _api(tmp_path)
    r = api.import_so_nhap(_b64(_so()))
    assert r["ok"], r["errors"]
    assert _dem(api, "club_test_selection", "club_scores") == (337, 337)
    return api


def _bo_hang_tieu_de_hai(wb):
    ws = wb["2. Học sinh"]
    for rng in list(ws.merged_cells.ranges):
        ws.unmerge_cells(str(rng))
    ws.delete_rows(2)
    return wb


def test_so_mat_hang_tieu_de_hai_khong_xoa_diem_cu_va_canh_bao(api_da_nap):
    """ST-B-003: sổ không có cột điểm thi giữ nguyên ô tick + điểm đã lưu, xem trước và nạp đều báo."""
    api = api_da_nap
    du = _b64(_bo_hang_tieu_de_hai(_so()))
    xem = api.xem_truoc_so_nhap(du)
    assert xem["ok"]
    ma = [e["code"] for e in xem["data"]["canh_bao"]]
    assert "so_nhap_canh_bao_giu_diem" in ma and "so_nhap_canh_bao_o_bo_qua" in ma, ma
    r = api.import_so_nhap(du)
    assert r["ok"], r["errors"]
    assert _dem(api, "club_test_selection", "club_scores") == (337, 337)
    assert "so_nhap_canh_bao_giu_diem" in _ma(r)


def test_so_mat_hang_tieu_de_hai_bao_o_bi_bo_qua_khi_csdl_rong(tmp_path):
    """ST-A-004: sổ mất hàng tiêu đề thứ hai -> các ô điểm/huy chương nằm ở cột không tên: phải báo."""
    api = _api(tmp_path)
    r = api.import_so_nhap(_b64(_bo_hang_tieu_de_hai(_so())))
    assert r["ok"]
    cua = [e for e in r["data"]["warnings"] if e["code"] == "so_nhap_canh_bao_o_bo_qua"]
    assert cua and cua[0]["params"]["n"] > 0, r["data"]["warnings"]


def test_so_day_du_khong_canh_bao_moi(api_da_nap):
    """Nạp lại đúng sổ đầy đủ: không có cảnh báo giữ/mất điểm hay ô bị bỏ qua, và vẫn 337/337."""
    r = api_da_nap.import_so_nhap(_b64(_so()))
    assert r["ok"]
    ma = _ma(r)
    assert not {"so_nhap_canh_bao_giu_diem", "so_nhap_canh_bao_mat_diem",
                "so_nhap_canh_bao_o_bo_qua"} & set(ma), ma
    assert _dem(api_da_nap, "club_test_selection", "club_scores") == (337, 337)


def test_so_co_cot_thi_nhung_bo_tick_thi_bao_se_xoa(api_da_nap):
    """Sổ CÓ cột điểm thi nhưng em không còn ô thi: nạp xoá (sổ là nguồn đúng) và xem trước phải nói N."""
    wb = _so()
    ws = wb["2. Học sinh"]
    # Cột "Điểm thi" của nguyện vọng 1: xoá hết ô dòng dữ liệu.
    hang2 = [c.value for c in ws[2]]
    cot_diem = [i + 1 for i, v in enumerate(hang2) if v and "thi" in str(v).lower() and "huy" not in str(v).lower()]
    assert cot_diem
    n_xoa_ky_vong = 0
    for r in range(3, ws.max_row + 1):
        for c in cot_diem:
            if ws.cell(row=r, column=c).value not in (None, ""):
                ws.cell(row=r, column=c).value = None
                n_xoa_ky_vong += 1
    assert n_xoa_ky_vong
    xem = api_da_nap.xem_truoc_so_nhap(_b64(wb))
    cua = [e for e in xem["data"]["canh_bao"] if e["code"] == "so_nhap_canh_bao_mat_diem"]
    assert cua and cua[0]["params"]["n"] > 0, [e["code"] for e in xem["data"]["canh_bao"]]


def test_xem_truoc_bao_ma_hoc_sinh_chi_khac_hoa_thuong(api_da_nap):
    """ST-B-004 (backend): DC001 -> dc001 trong sổ: xem trước báo trùng với mã đã có."""
    wb = _so()
    ws = wb["2. Học sinh"]
    for r in range(1, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == "DC001":
            ws.cell(row=r, column=1).value = "dc001"
            break
    xem = api_da_nap.xem_truoc_so_nhap(_b64(wb))
    ma = [e["code"] for e in xem["data"]["canh_bao"]]
    assert "csv_student_id_case_conflict" in ma, ma


def test_nap_so_tao_ban_sao_luu_truoc(api_da_nap):
    """Nạp sổ lấy một bản sao lưu trước khi ghi (như run_pipeline)."""
    truoc = glob.glob(api_da_nap.db_path + ".bak-*")
    r = api_da_nap.import_so_nhap(_b64(_so()))
    assert r["ok"]
    assert len(truoc) >= 1
    assert len(glob.glob(api_da_nap.db_path + ".bak-*")) == len(truoc) + 1


def test_doc_cau_hinh_trong_giao_dich_khong_mo_ket_noi_thu_hai(tmp_path, monkeypatch):
    """ST-A-002: trong một giao dịch chung, đọc cấu hình đi qua CHÍNH kết nối giao dịch. Mở kết nối thứ hai
    khi giao dịch ghi đã giữ khoá độc quyền (sổ rất lớn) thì chờ hết hạn rồi báo 'CSDL bận'."""
    api = _api(tmp_path)
    ngoai = api._cfg_ws(nghiem=True)["rules"]["wharton"]

    def cam(*a, **k):
        raise AssertionError("mở kết nối thứ hai để đọc cấu hình trong giao dịch")

    with api._mot_giao_dich():
        monkeypatch.setattr(ch, "connect_db", cam)
        assert api._luat_nghiem()["wharton"] == ngoai
        assert api._cfg_ws()["rules"]["wharton"] == ngoai
    monkeypatch.undo()


def test_so_lon_ba_nghin_hoc_sinh_nap_duoc(tmp_path):
    """ST-A-002 (cỡ nhỏ): sổ nhân bản dòng học sinh lên nhiều lần vẫn nạp xong, không 'csdl_dang_ban'."""
    api = _api(tmp_path)
    wb = _so()
    ws = wb["2. Học sinh"]
    hang = [[c.value for c in ws[r]] for r in range(3, ws.max_row + 1) if ws.cell(row=r, column=1).value]
    n_cot = max(len(h) for h in hang)
    for k in range(1, 5):
        for h in hang:
            ws.append([("%s_%d" % (h[0], k))] + h[1:n_cot])
    r = api.import_so_nhap(_b64(wb))
    assert r["ok"], r["errors"][:1]
    assert r["data"]["n_hoc_sinh"] == 5 * len(hang)
