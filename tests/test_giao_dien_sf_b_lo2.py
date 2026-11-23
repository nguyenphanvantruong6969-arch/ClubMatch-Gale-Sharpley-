"""SF-B lô 2: bản hồi quy nhỏ cho ST-B-006 / ST-B-011 (bản đầy đủ: tests_stress/b/).
Chromium thật qua `browser_host`, MỘT fixture trang dùng chung; sổ nhập MÔ PHỎNG."""

import base64
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        yield page, loi
        br.close()


def test_st_b_006_chi_tieu_thap_phan_bao_loi_o_chi_tieu(trang, api):
    page, loi = trang
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#btnSaveClub", state="attached")
    n_truoc = len(api.list_clubs_admin()["data"])
    page.fill("#clubFormId", "T4")
    page.fill("#clubFormName", "Thập phân")
    page.fill("#clubFormCapacity", "1.5")
    page.locator("#btnSaveClub").click()
    page.wait_for_function("document.getElementById('clubFormCapacity').getAttribute('aria-invalid') === 'true'")
    chu = page.locator("#clubFormFeedback").inner_text()
    assert "invalid literal" not in chu and "Hãy thử lại" not in chu, chu
    assert len(api.list_clubs_admin()["data"]) == n_truoc
    assert not loi, loi


def test_st_b_011_zip_hong_noi_dung_nguyen_nhan(trang, api, monkeypatch):
    page, loi = trang
    monkeypatch.setattr(api, "import_workspace", lambda *a: {
        "ok": False, "data": None, "errors": [{"code": "ws_du_lieu_sai", "params": {}}]})
    page.evaluate("""() => wsNhapZip({files: [new File([new Uint8Array(4)], 'hong.zip')], value: ''})""")
    page.wait_for_selector("#toastStack .toast, #toastStack > *")
    hien = page.evaluate("document.getElementById('toastStack').innerText")
    assert "zip" in hien.lower() and "các ô đã điền" not in hien, hien
    assert not loi, loi
