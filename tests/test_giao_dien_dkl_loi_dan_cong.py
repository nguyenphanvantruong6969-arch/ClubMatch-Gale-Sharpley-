"""DKL-I: khi chưa có dữ liệu, khung "1. Nhập sổ" chỉ đường sang cổng Đăng ký CLB (thu thập rồi xuất Sổ nhập).
Chromium thật qua `browser_host`; sổ nhập MÔ PHỎNG (du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx)."""

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
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

        def _mo():
            url = browser_host.serve(api, GOC, "index.html", open_browser=False)
            page = br.new_page(bypass_csp=True)
            page.set_default_timeout(15000)
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("#dropZone", state="attached")
            return page, loi
        yield _mo
        br.close()


def test_chua_co_du_lieu_co_loi_dan_sang_cong_dang_ky(mo):
    page, loi = mo()
    page.wait_for_function("document.getElementById('viecTiepTheo').dataset.trangThai === 'nap_so'")
    ghi = page.locator("#ghiChuDangKy")
    assert ghi.is_visible()
    chu = ghi.inner_text()
    assert "Đăng ký CLB" in chu and "Sổ nhập" in chu and "mật khẩu quản trị" in chu     # nói rõ cổng làm gì và việc cần làm lần đầu
    assert ghi.get_attribute("data-quyen") == "quan_tri"
    page.locator("#ghiChuDangKyLienKet").click()
    page.wait_for_url("**/dang_ky.html*")
    page.wait_for_selector("text=Thiết lập lần đầu")
    assert not loi, loi


def test_da_co_du_lieu_khong_hien_loi_dan(mo, api):
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    page, loi = mo()
    page.wait_for_function("document.getElementById('viecTiepTheo').dataset.trangThai !== 'nap_so'")
    assert page.locator("#ghiChuDangKy").is_hidden()
    assert not loi, loi


def test_workspace_khong_phai_truong_hoc_khong_hien_loi_dan(mo):
    """CI run 1689: lời dẫn dùng từ của trường học («học sinh», «giáo viên», «CLB») nên KHÔNG được hiện ở workspace có từ vựng
    khác (ví dụ công ty). Cổng đăng ký chỉ dành cho trường học."""
    page, loi = mo()
    page.wait_for_function("document.getElementById('viecTiepTheo').dataset.trangThai === 'nap_so'")
    assert page.locator("#ghiChuDangKy").is_visible()                                  # từ vựng mặc định (trường học): hiện
    page.evaluate("window.I18N.applyLabels({person: {vi: 'Nhân viên', en: 'Employee'}, slot: {vi: 'Dự án', en: 'Project'}})")
    page.wait_for_function("document.getElementById('ghiChuDangKy').hidden")           # đổi từ vựng sang công ty: ẩn
    assert "học sinh" not in page.locator("#view-pipeline").inner_text()
    assert not loi, loi
