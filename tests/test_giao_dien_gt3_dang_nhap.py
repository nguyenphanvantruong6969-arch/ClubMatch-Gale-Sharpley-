"""GT3-L1: màn đăng nhập + hộp Tài khoản trong giao diện thật (Chromium qua `browser_host`). Dữ liệu MÔ PHỎNG."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"
MK2 = "matkhau-gia-2"


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


def test_chua_co_tai_khoan_khong_man_dang_nhap_va_tao_quan_tri_dau_tien(trang):
    page, api, url, loi = trang
    assert page.locator("#tkOverlay").count() == 0 or page.locator("#tkOverlay").is_hidden()
    assert page.locator("#tkNutDangXuat").count() == 0
    page.click("#tkNutMoHop")
    page.fill("#tkTaoTen", "quantri")
    page.fill("#tkTaoMk", MK)
    page.click("#tkNutTao")
    page.wait_for_selector("#tkHuyHieu")
    assert "quantri" in page.inner_text("#tkHuyHieu")
    assert api.get_phien_dang_nhap()["data"]["vai"] == "quan_tri"
    assert not loi, loi


def test_dang_xuat_hien_man_dang_nhap_sai_roi_dung(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    page.reload()
    page.wait_for_selector("#tkNutDangXuat")
    page.click("#tkNutDangXuat")
    page.wait_for_selector("#tkNutDangNhap")
    page.fill("#tkTen", "quantri")
    page.fill("#tkMatKhau", "sai-sai-sai")
    page.click("#tkNutDangNhap")
    page.wait_for_selector("#tkTin.is-error")
    assert page.input_value("#tkMatKhau") == ""            # ô mật khẩu bị xoá sau khi gửi
    page.fill("#tkMatKhau", MK)
    page.click("#tkNutDangNhap")
    page.wait_for_selector("#tkNutDangNhap", state="detached")
    page.wait_for_selector("#tkNutDangXuat")
    assert not loi, loi


def test_co_tai_khoan_ma_chua_dang_nhap_thi_man_dang_nhap_chan_giao_dien(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    api.dang_xuat()
    page.reload()
    page.wait_for_selector("#tkNutDangNhap")
    assert page.locator("#tkOverlay").is_visible()


def test_het_phien_sau_15_phut_thi_hien_lai_man_dang_nhap(trang):
    page, api, url, loi = trang
    t = {"v": 5000.0}
    api._dong_ho = lambda: t["v"]
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    page.reload()
    page.wait_for_selector("#tkNutDangXuat")
    t["v"] += 16 * 60
    page.reload()
    page.wait_for_selector("#tkNutDangNhap")


def test_quan_tri_tao_giao_vien_va_giao_vien_chi_thay_doi_mat_khau(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    page.reload()
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormTao")
    page.fill("#tkTaoTen", "co_lan")
    page.fill("#tkTaoMk", MK2)
    page.select_option("#tkTaoVai", "giao_vien")
    page.click("#tkNutTao")
    page.wait_for_selector('[data-xoa="co_lan"]')
    page.click("#tkNutDong")
    api.dang_xuat()
    api.dang_nhap("co_lan", MK2)
    page.reload()
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormDoiMk")
    assert page.locator("#tkFormTao").count() == 0
    assert page.locator("#tkDanhSach").count() == 0
    assert not loi, loi


def test_nut_xoa_can_bam_hai_lan(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    api.tao_tai_khoan("gv1", MK2, "giao_vien")
    page.reload()
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector('[data-xoa="gv1"]')
    page.click('[data-xoa="gv1"]')
    assert api.liet_ke_tai_khoan()["data"] and len(api.liet_ke_tai_khoan()["data"]) == 2
    page.click('[data-xoa="gv1"]')
    page.wait_for_function("window.pywebview.api.liet_ke_tai_khoan().then(r => r.data.length === 1)")
    assert not loi, loi


def test_nhat_ky_thao_tac_hien_trong_hop_tai_khoan_cua_quan_tri(trang):
    page, api, url, loi = trang
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.create_or_update_club("A", "Câu lạc bộ Đẹp", 5, 0, "")["ok"]
    page.goto(url)
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkNkTable")
    chu = page.inner_text("#tkNkTable")
    assert "create_or_update_club" in chu and "tao_tai_khoan" in chu
    assert "Câu lạc bộ Đẹp" in chu
    page.fill("#tkNkHanhDong", "create_or_update_club")
    page.click("#tkNkLoc")
    page.wait_for_function("!document.querySelector('#tkNkTable').innerText.includes('tao_tai_khoan')")
    assert "1 dòng" in page.inner_text("#tkNkTrang")
    assert page.is_disabled("#tkNkTruoc") and page.is_disabled("#tkNkSau")
    assert not loi, loi
