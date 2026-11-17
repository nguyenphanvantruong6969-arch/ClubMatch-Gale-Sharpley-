"""GT4-L3 — thiết lập tài khoản trong giao diện thật: nhập lại mật khẩu, hiện/ẩn, thẻ bước tiếp theo, cảnh báo
(R2, R4, D4-5). Chromium qua `browser_host`. Dữ liệu MÔ PHỎNG, mật khẩu giả."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True)
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone", state="attached")
    page.wait_for_selector("#tkNutMoHop")
    try:
        yield page, api, url, loi
    finally:
        br.close()
        pw.stop()


def test_chua_co_tai_khoan_hop_co_canh_bao_tao_truoc_khi_dua_may_cho_hoc_sinh(trang):
    page, api, url, loi = trang
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormTao")
    assert page.locator("#tkCanhBaoDauTien").is_visible()
    assert "trước khi" in page.inner_text("#tkCanhBaoDauTien")
    assert not loi, loi


def test_nhap_lai_mat_khau_khong_khop_thi_bao_loi_va_khong_tao(trang):
    page, api, url, loi = trang
    page.click("#tkNutMoHop")
    page.fill("#tkTaoTen", "quantri")
    page.fill("#tkTaoMk", MK)
    page.fill("#tkTaoMk2", MK + "x")
    page.click("#tkNutTao")
    assert "chưa giống" in page.inner_text("#tkTaoTin")
    assert api.get_phien_dang_nhap()["data"]["co_tai_khoan"] is False
    page.fill("#tkTaoMk2", MK)
    page.click("#tkNutTao")
    page.wait_for_selector("#tkHuyHieu")
    assert api.get_phien_dang_nhap()["data"]["vai"] == "quan_tri"
    assert not loi, loi


def test_hien_an_mat_khau_doi_loai_hai_o(trang):
    page, api, url, loi = trang
    page.click("#tkNutMoHop")
    assert page.get_attribute("#tkTaoMk", "type") == page.get_attribute("#tkTaoMk2", "type") == "password"
    page.check("#tkTaoHien")
    assert page.get_attribute("#tkTaoMk", "type") == page.get_attribute("#tkTaoMk2", "type") == "text"
    page.uncheck("#tkTaoHien")
    assert page.get_attribute("#tkTaoMk", "type") == "password"
    assert not loi, loi


def test_sau_quan_tri_dau_tien_co_the_buoc_tiep_va_con_tro_o_them_tai_khoan(trang):
    page, api, url, loi = trang
    page.click("#tkNutMoHop")
    page.fill("#tkTaoTen", "quantri")
    page.fill("#tkTaoMk", MK)
    page.fill("#tkTaoMk2", MK)
    page.click("#tkNutTao")
    page.wait_for_selector("#tkBuocTiep")
    chu = page.inner_text("#tkBuocTiep")
    for y in ("giáo viên", "Ghi nhớ", "QUEN_MAT_KHAU.bat"):
        assert y in chu, y
    assert page.evaluate("document.activeElement && document.activeElement.id") == "tkTaoTen"
    assert not loi, loi


def test_doi_mat_khau_cung_phai_nhap_lai(trang):
    page, api, url, loi = trang
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    page.reload()
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormDoiMk")
    assert page.locator("#tkBuocTiep").count() == 0                 # thẻ bước tiếp chỉ hiện ngay sau khi tạo quản trị đầu
    page.fill("#tkMkCu", MK)
    page.fill("#tkMkMoi", "matkhau-gia-2")
    page.fill("#tkMkMoi2", "khac-hoan-toan")
    page.click("#tkNutDoiMk")
    assert "chưa giống" in page.inner_text("#tkDoiTin")
    page.fill("#tkMkCu", MK)
    page.fill("#tkMkMoi", "matkhau-gia-2")
    page.fill("#tkMkMoi2", "matkhau-gia-2")
    page.click("#tkNutDoiMk")
    page.wait_for_function("document.querySelector('#tkDoiTin').innerText.includes('Đã đổi')")
    assert not loi, loi
