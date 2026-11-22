"""UX3: sau "Xoá toàn bộ học sinh" ở thẻ Quản lý, giao diện không còn hiện số liệu cũ:
thanh phân trang của thẻ Nhập nguyện vọng ẩn, và khung "Tra cứu một học sinh" không còn phiếu của em đã xoá.
Chromium qua `browser_host`. Dữ liệu MÔ PHỎNG."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_a", "CLB A", 30)
    for i in range(1, 21):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Học sinh %02d" % i)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
    assert api.run_pipeline()["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 900}, bypass_csp=True)
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone")
    try:
        yield page, api, loi
    finally:
        br.close()
        pw.stop()


def _xoa_hoc_sinh(page, api):
    page.click('[data-tab="admin"]')
    page.wait_for_selector("#btnResetStudents", state="attached")
    nut = page.locator("#btnResetStudents")
    nut.evaluate("e => e.click()")      # bước 1 của xác nhận hai bước
    nut.evaluate("e => e.click()")      # bước 2
    page.wait_for_function("document.querySelector('.toast-stack').innerText.length > 0")
    assert api.list_students_admin("", 1, 8)["data"]["total"] == 0


def test_phan_trang_nhap_nguyen_vong_an_sau_khi_xoa(trang):
    page, api, loi = trang
    page.click('[data-tab="fallback"]')
    page.wait_for_selector("#fallbackStudentPagination", state="visible")
    _xoa_hoc_sinh(page, api)
    page.click('[data-tab="fallback"]')
    page.wait_for_selector("#studentSearchResults .empty-state")
    assert not page.locator("#fallbackStudentPagination").is_visible()
    assert not loi, loi


def test_tra_cuu_khong_con_phieu_cu_sau_khi_xoa(trang):
    page, api, loi = trang
    page.click('[data-tab="results"]')
    page.fill("#gtTim", "HS01")
    page.locator('#gtDs button[data-student-id="HS01"]').click()
    page.wait_for_selector("#gtKetQua .gt-ten")
    _xoa_hoc_sinh(page, api)
    page.click('[data-tab="results"]')
    assert page.locator("#gtKetQua").inner_text().strip() == ""
    assert not page.locator("#gtIn").is_visible()
    assert page.input_value("#gtTim") == ""
    assert not loi, loi
