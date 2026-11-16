"""GT3-L2: giao diện ẩn phần của quản trị khi đăng nhập bằng vai giáo viên (Chromium qua `browser_host`).
Cổng thật nằm ở backend (`test_gt3_phan_quyen.py`). Dữ liệu MÔ PHỎNG."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"
TAB_QUAN_TRI = ("pipeline", "admin")


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True)
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))

    def mo_trang():
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.wait_for_selector("#tkNutMoHop")
        page.wait_for_function("document.body.dataset.vai !== undefined")

    try:
        yield page, api, mo_trang, loi
    finally:
        br.close()
        pw.stop()


def hien(page, tab):
    return page.locator(f'.nav-item[data-tab="{tab}"]').is_visible()


def test_chua_co_tai_khoan_thay_du_tab_va_khong_gan_vai(mo):
    page, api, mo_trang, loi = mo
    mo_trang()
    assert page.evaluate("document.body.dataset.vai") == ""
    assert all(hien(page, t) for t in ("pipeline", "results", "admin", "scoring"))
    assert not loi, loi


def test_giao_vien_khong_thay_tab_quan_tri_va_duoc_dua_ve_ket_qua(mo):
    page, api, mo_trang, loi = mo
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    mo_trang()
    assert page.evaluate("document.body.dataset.vai") == "giao_vien"
    for tab in TAB_QUAN_TRI:
        assert not hien(page, tab), tab
    assert hien(page, "results") and hien(page, "scoring")
    assert page.locator(".nav-item.is-active").get_attribute("data-tab") == "results"
    assert not loi, loi


def test_quan_tri_thay_du_tab(mo):
    page, api, mo_trang, loi = mo
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    mo_trang()
    assert page.evaluate("document.body.dataset.vai") == "quan_tri"
    assert all(hien(page, t) for t in ("pipeline", "results", "admin", "scoring"))
    assert not loi, loi
