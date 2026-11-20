"""XP1-L2 — nút "Lưu PDF" ở khung tra cứu một học sinh (thẻ Kết quả): tìm → chọn → Lưu PDF. Chromium."""

import os
import shutil
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
pytest.importorskip("reportlab")
from playwright.sync_api import sync_playwright  # noqa: E402

import api as api_mod  # noqa: E402
import browser_host  # noqa: E402
import cau_hinh_ws  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402


def _dung_api(tmp_path):
    os.makedirs(str(tmp_path / "nguon"))
    nguon = d.nap_bo(str(tmp_path / "nguon"), d.BO_DU_LIEU[1][1])
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    api = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    assert api.run_pipeline(seed=3)["ok"]
    return api


def test_luu_pdf_mot_em_toi_da_ba_buoc(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = _dung_api(tmp_path)
    with api._ket_noi_doc() as cur:
        sid = cur.execute("SELECT student_id FROM students ORDER BY student_id").fetchone()[0]
    with sync_playwright() as pw:
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(locale="vi-VN", bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.click('button.nav-item[data-tab="results"]')
        nut = page.locator("#btnGtPdfMot")
        assert nut.is_hidden()                       # chưa chọn em nào thì chưa có nút
        buoc = 0
        page.fill("#gtTim", sid)                     # bước 1: tìm
        buoc += 1
        page.wait_for_selector("#gtDs .gt-chon")
        page.click("#gtDs .gt-chon")                 # bước 2: chọn
        buoc += 1
        page.wait_for_selector("#gtKetQua .gt-bang")
        assert nut.is_visible()
        nut.click()                                  # bước 3: Lưu PDF (tệp rơi vào thư mục Tải xuống)
        buoc += 1
        page.wait_for_function("document.getElementById('gtXuatPhanHoi').textContent.includes('.pdf')")
        assert buoc <= 3
        br.close()
    assert not loi, loi
    tep = [t for t in os.listdir(api.thu_muc_xuat) if t.endswith(".pdf")]
    assert len(tep) == 1 and sid in tep[0]
