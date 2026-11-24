"""UX1B-L7: thẻ giải trình trên màn hình có cùng nội dung với phiếu in: dòng tóm tắt, điểm CLB đã thi (thanh SVG),
"Em nên làm gì tiếp", cột huy chương (FA). Thẻ của học sinh không có "số khoá bốc thăm". Chromium; dữ liệu MÔ PHỎNG."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM, mo_gap_ma  # noqa: E402
from test_ux1b_l7_phieu import _dung_fa, _dung_thuong  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True, viewport={"width": 1400, "height": 1000})
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)

    def xem(sid):
        page.goto(url)
        page.wait_for_selector("#gtPanel", state="attached")
        page.click('button.nav-item[data-tab="results"]')
        page.fill("#gtTim", sid)
        page.wait_for_selector('#gtDs button[data-student-id="%s"]' % sid)
        page.click('#gtDs button[data-student-id="%s"]' % sid)
        page.wait_for_selector("#gtKetQua .gt-ten")
        return page
    try:
        yield api, xem, page, url, loi
    finally:
        br.close()
        pw.stop()


def test_the_nguoi_lon_co_tom_tat_thanh_svg_va_buoc_tiep(mo):
    api, xem, page, url, loi = mo
    _dung_thuong(api)
    xem("s1")
    assert page.inner_text("#gtKetQua .gt-tom-tat-dong") == "Học sinh được xếp vào CLB A."
    assert page.locator("#gtKetQua svg.thanh-diem").count() == 1
    assert "số khoá bốc thăm" in page.inner_text("#gtKetQua .gt-lan-chay")      # quản trị / giáo viên vẫn thấy
    assert page.locator("#gtKetQua .gt-tiep-theo").count() == 0
    xem("s4")
    assert page.inner_text("#gtKetQua .gt-tom-tat-dong") == "Học sinh chưa có CLB nào."
    assert "giáo viên phụ trách" in page.inner_text("#gtKetQua .gt-tiep-theo")
    assert page.locator("#gtKetQua svg").count() == 0
    heads = page.evaluate(
        "() => Array.from(document.querySelectorAll('#gtKetQua table.gt-bang th')).map(e => e.textContent)")
    assert "Điểm thi" in heads and "Chỗ đã nhận / tối đa" in heads and "Huy chương" not in heads
    assert not loi, loi


def test_che_do_huy_chuong_co_cot_va_chu_giai(mo):
    api, xem, page, url, loi = mo
    _dung_fa(api)
    xem("s3")
    heads = page.evaluate(
        "() => Array.from(document.querySelectorAll('#gtKetQua table.gt-bang th')).map(e => e.textContent)")
    assert heads[:3] == ["Nguyện vọng", "CLB", "Huy chương"]
    assert "Em đặt huy chương Đồng; các bạn đặt Bạc ở CLB G được xét trước." in page.inner_text("#gtKetQua")
    assert "Vàng, rồi Bạc, rồi Đồng" in page.inner_text("#gtKetQua")
    assert not loi, loi


def test_the_hoc_sinh_khong_co_so_khoa_boc_tham(mo):
    api, xem, page, url, loi = mo
    _dung_thuong(api)
    assert api.tao_ma_tra_cuu()["ok"]
    with api._ket_noi_doc() as cur:
        ma = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))
    # SF-B (ST-B-009): lớp phủ chỉ dựng khi đã có tài khoản (khoá thật).
    assert api.tao_tai_khoan("qt_nen", "matkhau-gia-1", "quan_tri")["ok"] and api.dang_nhap("qt_nen", "matkhau-gia-1")["ok"]
    page.goto(url)
    page.wait_for_selector("#gtPanel", state="attached")
    page.click('button.nav-item[data-tab="results"]')
    mo_gap_ma(page)
    page.click("#btnGtCheDoHs")
    page.wait_for_selector("#gtHs", state="visible")
    page.fill("#gtHsMa", "s1")
    page.fill("#gtHsMaTra", ma["s1"])
    page.press("#gtHsMaTra", "Enter")
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    txt = page.inner_text("#gtHsKetQua")
    assert "Lần xếp lúc" in txt and "số khoá" not in txt and "Em được xếp vào CLB A." in txt
    assert not loi, loi
