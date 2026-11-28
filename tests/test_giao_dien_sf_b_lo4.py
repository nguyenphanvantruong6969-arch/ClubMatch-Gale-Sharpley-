"""SF-B lô 4: bản hồi quy nhỏ cho ST-B-012 / ST-B-013 (bản đầy đủ: tests_stress/b/).
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
        page.wait_for_selector("#dropZone", state="attached")
        yield page, loi
        br.close()


def test_st_b_012_doi_ngon_ngu_dong_thong_bao_dang_hien(trang):
    page, loi = trang
    page.evaluate("showToast('Đã chuyển sang chế độ khác', 'success', {sticky: true})")
    assert page.locator("#toastStack .toast").count() >= 1
    page.evaluate("window.dispatchEvent(new Event('langchange'))")
    assert page.locator("#toastStack .toast").count() == 0
    assert not loi, loi


def test_st_b_013_quan_ly_khong_cuon_ngang_o_390px(trang):
    page, loi = trang
    page.set_viewport_size({"width": 390, "height": 800})
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#adminClubTableBody tr")
    page.wait_for_timeout(500)
    assert page.evaluate("document.documentElement.scrollWidth") <= 394
    assert not loi, loi
