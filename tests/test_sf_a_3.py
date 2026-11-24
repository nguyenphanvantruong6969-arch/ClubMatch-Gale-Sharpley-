# -*- coding: utf-8 -*-
"""SF-A3 — ST-A-003 (chỉ tiêu quá lớn), ST-B-006 (chỉ tiêu không nguyên), ST-A-005 / ST-B-007 (xoá em / CLB có kết
quả), ST-A-001 (đổi chế độ báo thiếu dữ liệu), ST-A-007 (nhập mô-đun biểu mẫu). DỮ LIỆU MÔ PHỎNG."""
import base64
import io
import os
import sqlite3
import subprocess
import sys

import openpyxl
import pytest

import cau_hinh_ws as ch
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_150 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DOI_CHE_DO_150HS.xlsx")
HUY_CHUONG = {"wharton": True, "fa_daa": True}
CHI_XEP = {"wharton": False, "fa_daa": False}
CHIA_100 = {"wharton": True, "fa_daa": False}


def _b64(wb):
    out = io.BytesIO()
    wb.save(out)
    return base64.b64encode(out.getvalue()).decode()


def _so():
    return openpyxl.load_workbook(SO_150)


def _api_ws(tmp_path, rules):
    """Workspace-mode API như phần mềm dùng (update_workspace_config chỉ chạy ở đây)."""
    import workspace as ws
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "ws", {"rules": dict(rules)})
    return PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / "x"),
                       thu_muc_goc_ws=str(goc), ws_da_chon=True)


def _api(tmp_path, name="a", rules=None):
    api = PipelineAPI(str(tmp_path / (name + ".db")), thu_muc_xuat=str(tmp_path / ("x_" + name)))
    ch.ghi_cau_hinh(api.db_path, {"rules": rules or HUY_CHUONG})
    return api

def _sua_chi_tieu_dau(gia_tri):
    wb = _so()
    ws = wb["1. CLB"]
    cot = next(i + 1 for i, c in enumerate(ws[1]) if c.value and "tiêu" in str(c.value).lower())
    ws.cell(row=2, column=cot).value = gia_tri
    return wb


@pytest.mark.parametrize("gia_tri", [10 ** 30, 1e300, 2 ** 63, 2 ** 31])
def test_chi_tieu_vuot_tran_xem_truoc_va_nap_cung_bi_chan(tmp_path, gia_tri):
    """ST-A-003: chỉ tiêu quá lớn: xem trước báo `so_nhap_chi_tieu_sai`, nạp từ chối cùng mã (không còn
    `error_importing_clubs_csv` kèm câu Python thô)."""
    api = _api(tmp_path)
    du = _b64(_sua_chi_tieu_dau(gia_tri))
    xem = api.xem_truoc_so_nhap(du)
    assert xem["ok"] and [e["code"] for e in xem["data"]["loi"]] == ["so_nhap_chi_tieu_sai"]
    r = api.import_so_nhap(du)
    assert not r["ok"] and r["errors"][0]["code"] == "so_nhap_chi_tieu_sai"


def test_chi_tieu_bang_tran_van_nap_duoc(tmp_path):
    api = _api(tmp_path)
    r = api.import_so_nhap(_b64(_sua_chi_tieu_dau(2 ** 31 - 1)))
    assert r["ok"], r["errors"][:1]


@pytest.mark.parametrize("cap,res,ma", [("1.5", None, "club_capacity_not_integer"),
                                        ("abc", None, "club_capacity_not_integer"),
                                        (None, None, "club_capacity_not_integer"),
                                        (1.5, None, "club_capacity_not_integer"),
                                        (True, None, "club_capacity_not_integer"),
                                        ("5", "1.5", "club_capacity_not_integer"),
                                        (10 ** 30, None, "capacity_too_large"),
                                        ("0", None, "capacity_must_be_positive")])
def test_form_clb_chi_tieu_sai_co_ma_rieng(tmp_path, cap, res, ma):
    """ST-B-006: chỉ tiêu không phải số nguyên / quá lớn có mã lỗi riêng (không phải 'Hãy thử lại' + Python thô)."""
    api = _api(tmp_path)
    r = api.create_or_update_club("T4", "Thập phân", cap, res, "")
    assert not r["ok"] and r["errors"][0]["code"] == ma, r["errors"]


@pytest.mark.parametrize("cap", [10, "10", " 10 ", "10.0", 10.0])
def test_form_clb_chi_tieu_hop_le_van_nhan(tmp_path, cap):
    api = _api(tmp_path)
    assert api.create_or_update_club("T5", "Hợp lệ", cap, 0, "")["ok"]
    assert api.list_clubs()["data"][0]["capacity"] == 10


def test_xoa_hoc_sinh_nhap_nham_sau_khi_chay(tmp_path):
    """ST-A-005: em nhập nhầm (không nguyện vọng) sau một lần chạy: dòng kết quả trống không chặn xoá."""
    api = _api(tmp_path, rules=CHI_XEP)
    assert api.import_so_nhap(_b64(_so()))["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    assert api.create_student_if_missing("TYPO1", "x")["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    assert api.delete_student("TYPO1")["ok"]


def test_xoa_hoc_sinh_co_suat_can_xac_nhan_va_co_sao_luu(tmp_path):
    """ST-A-005: em đang có suất: mặc định chặn (như cũ); xác nhận thì xoá kèm dòng kết quả, có sao lưu,
    run_history không mất dòng nào, kết quả hiện tại thành cũ."""
    api = _api(tmp_path, rules=CHI_XEP)
    assert api.import_so_nhap(_b64(_so()))["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    c = sqlite3.connect(api.db_path)
    sid = c.execute("SELECT student_id FROM match_results WHERE club_id IS NOT NULL LIMIT 1").fetchone()[0]
    n_hist = c.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]
    c.close()
    r = api.delete_student(sid)
    assert not r["ok"] and r["errors"][0]["code"] == "cannot_delete_student_matched"
    r = api.delete_student(sid, True)
    assert r["ok"] and r["data"]["n_ket_qua_bo"] >= 1 and r["data"]["backup_path"]
    c = sqlite3.connect(api.db_path)
    assert c.execute("SELECT COUNT(*) FROM students WHERE student_id=?", (sid,)).fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM match_results WHERE student_id=?", (sid,)).fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == n_hist
    c.close()
    assert api.get_match_results("")["ok"]


def test_xoa_clb_co_nguyen_vong_va_ket_qua_can_xac_nhan(tmp_path):
    """ST-B-007: CLB còn nguyện vọng + kết quả: mặc định chặn, thông báo chỉ lối thoát; xác nhận thì xoá kèm,
    dòng kết quả của CLB thành 'chưa có suất', sao lưu, run_history giữ nguyên."""
    from i18n_errors import format_message
    api = _api(tmp_path, rules=CHI_XEP)
    assert api.import_so_nhap(_b64(_so()))["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    c = sqlite3.connect(api.db_path)
    cid = c.execute("SELECT club_id FROM match_results WHERE club_id IS NOT NULL LIMIT 1").fetchone()[0]
    n_hist = c.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]
    c.close()
    r = api.delete_club(cid)
    assert not r["ok"] and r["errors"][0]["code"] == "cannot_delete_club_referenced"
    chu = format_message(r["errors"][0]["code"], r["errors"][0]["params"], "vi")
    assert "xác nhận" in chu and "nạp lại" in chu
    r = api.delete_club(cid, True)
    assert r["ok"] and r["data"]["n_prefs_removed"] > 0 and r["data"]["backup_path"], r
    c = sqlite3.connect(api.db_path)
    assert c.execute("SELECT COUNT(*) FROM clubs WHERE club_id=?", (cid,)).fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM preferences WHERE club_id=?", (cid,)).fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM match_results WHERE club_id=?", (cid,)).fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == n_hist
    assert c.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    c.close()
    assert api.run_pipeline(seed=1)["ok"]            # chạy lại sau khi xoá vẫn được


@pytest.mark.parametrize("che_do_dau", [CHIA_100, CHI_XEP])


def test_doi_sang_huy_chuong_sau_khi_nap_so_o_che_do_khac_co_canh_bao(tmp_path, che_do_dau):
    """ST-A-001: sổ nạp ở chế độ khác đã bỏ cột Loại/huy chương; bật Huy chương phải báo NGAY khi đổi."""
    api = _api_ws(tmp_path, che_do_dau)
    assert api.import_so_nhap(_b64(_so()))["ok"]
    r = api.update_workspace_config({"rules": HUY_CHUONG})
    assert r["ok"]
    ma = [e["code"] for e in r["data"]["warnings"]]
    assert ma == ["che_do_thieu_du_lieu"], r["data"]["warnings"]
    p = r["data"]["warnings"][0]["params"]
    assert p["che_do"] == "huy_chuong" and p["n_thieu_loai"] > 0


def test_doi_che_do_khong_thieu_gi_thi_khong_canh_bao(tmp_path):
    api = _api_ws(tmp_path, HUY_CHUONG)
    assert api.import_so_nhap(_b64(_so()))["ok"]
    assert api.update_workspace_config({"rules": CHI_XEP})["data"]["warnings"] == []
    assert api.update_workspace_config({"rules": HUY_CHUONG})["data"]["warnings"] == []


def test_ham_bieu_mau_goi_trong_tien_trinh_moi_khong_nem_modulenotfound():
    """ST-A-007: `ai_chua_dang_ky` / `chuyen_tep_forms` / `doi_chieu_hai_lan` gọi ngay khi mở phần mềm (chưa có
    lời gọi nào đưa mau_forms_thi_clb vào sys.path) vẫn trả `{ok,data,errors}`, không ném ModuleNotFoundError."""
    ma = (
        "import sys, tempfile, os\n"
        "sys.path.insert(0, %r)\n"
        "from api import PipelineAPI\n"
        "d = tempfile.mkdtemp()\n"
        "a = PipelineAPI(os.path.join(d, 'a.db'), thu_muc_xuat=d)\n"
        "assert not any('mau_forms_thi_clb' in p for p in sys.path)\n"
        "for r in (a.ai_chua_dang_ky(None), a.chuyen_tep_forms([], 'x', 'y'), a.doi_chieu_hai_lan(None, None)):\n"
        "    assert isinstance(r, dict) and {'ok', 'data', 'errors'} <= set(r), r\n"
        "print('XONG')\n" % GOC)
    kq = subprocess.run([sys.executable, "-I", "-c", ma], capture_output=True, text=True, timeout=120, cwd=GOC)
    assert "XONG" in kq.stdout, kq.stderr[-800:]
