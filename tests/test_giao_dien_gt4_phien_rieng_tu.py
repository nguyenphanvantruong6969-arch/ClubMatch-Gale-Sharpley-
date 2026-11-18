"""GT4 fix OL1/OL2 — (1) sau Đăng xuất, nội dung trước đó không đọc được qua lớp phủ đăng nhập; (2) hết phiên do nhàn rỗi:
bấm gì cũng mở ngay hộp đăng nhập, không chỉ chồng thông báo đỏ. Chromium qua `browser_host`. Dữ liệu MÔ PHỎNG."""

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
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True)
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#tkNutDangXuat")                       # tạo tài khoản đầu tiên = đã đăng nhập
    try:
        yield page, api, loi
    finally:
        br.close()
        pw.stop()


def test_sau_dang_xuat_lop_phu_dang_nhap_khong_trong_suot(trang):
    page, api, loi = trang
    page.click("#tkNutDangXuat")
    page.wait_for_selector("#tkNutDangNhap")
    mau = page.evaluate("getComputedStyle(document.querySelector('#tkOverlay')).backgroundColor")
    so = [float(x) for x in mau.replace("rgba(", "").replace("rgb(", "").rstrip(")").split(",")]
    assert len(so) == 3 or so[3] == 1.0, f"lớp phủ còn trong suốt: {mau}"
    assert not loi, loi


def test_het_phien_mo_ngay_hop_dang_nhap_khi_bam_viec_can_quyen(trang):
    page, api, loi = trang
    t0 = api._dong_ho()
    api._dong_ho = lambda: t0 + 16 * 60                             # quá 15 phút nhàn rỗi
    page.click('button.nav-item[data-tab="manage"], button.nav-item[data-tab="results"]')
    page.evaluate("window.RBDA.callApi('liet_ke_tai_khoan').then(r => showErrorToast(r.errors))")
    page.wait_for_selector("#tkNutDangNhap", timeout=3000)          # không đợi vòng hỏi 30 giây
    assert not loi, loi


def test_the_nhat_ky_rong_hon_bo_loc_xep_ngang_va_the_dang_chon_thay_ro(trang):
    """GT4 ghi chú checker: hộp rộng hơn ở thẻ nhật ký, bộ lọc xếp ngang, thẻ đang chọn khác thẻ kia."""
    page, api, loi = trang
    page.set_viewport_size({"width": 1280, "height": 900})
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkTabNhatKy")
    rong_tk = page.evaluate("document.querySelector('#tkOverlay .ws-hop').getBoundingClientRect().width")
    mau_chon = page.evaluate("getComputedStyle(document.querySelector('#tkTabTaiKhoan')).backgroundColor")
    page.click("#tkTabNhatKy")
    page.wait_for_selector("#tkNkNguoi")
    rong_nk = page.evaluate("document.querySelector('#tkOverlay .ws-hop').getBoundingClientRect().width")
    assert rong_nk > rong_tk + 200, (rong_tk, rong_nk)
    top = page.evaluate("[...['tkNkNguoi','tkNkHanhDong','tkNkNgay']].map(i => document.getElementById(i).getBoundingClientRect().top)")
    assert max(top) - min(top) < 6, top                              # ba ô lọc cùng một hàng
    mau_khong_chon = page.evaluate("getComputedStyle(document.querySelector('#tkTabTaiKhoan')).backgroundColor")
    assert mau_chon != mau_khong_chon
    assert not loi, loi
