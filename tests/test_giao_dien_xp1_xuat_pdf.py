"""XP1-L4: menu "Xuất PDF…" ở thẻ Xuất dữ liệu: ba mục + ô chọn lớp, chỉ quản trị, gọi đúng hàm. Chromium. Dữ liệu MÔ PHỎNG."""

import os

import pytest
from _wharton import tat_wharton
from test_a14_lop_xuat import _nap

pytest.importorskip("playwright", reason="chưa cài playwright")
pytest.importorskip("reportlab")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUC = ("btnPdfDsClb", "btnPdfDsLop", "btnPdfPhieuLop")


@pytest.fixture
def api(api, tmp_path):
    tat_wharton(api)
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    return api


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

        def _mo():
            url = browser_host.serve(api, GOC, "index.html", open_browser=False)
            page = br.new_page(locale="vi-VN", bypass_csp=True, viewport={"width": 1400, "height": 1000})
            page.set_default_timeout(15000)
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("#dropZone")
            page.locator('.nav-item[data-tab="others"]').click()
            page.wait_for_selector("#xuatPanel", state="visible")
            return page, loi
        yield _mo
        br.close()


def _mo_menu(page):
    page.wait_for_selector("#xuatPdfMenu", state="visible")
    page.locator("#xuatPdfMenu > summary").click()


def _tep_pdf(thu_muc):
    return sorted(t for t in os.listdir(thu_muc) if t.endswith(".pdf"))


def test_menu_co_ba_muc_va_o_chon_lop(mo, api):
    _nap(api)
    page, loi = mo()
    assert page.locator("#xuatPdfMenu > summary").inner_text().strip() == "Xuất PDF…"
    assert all(page.locator("#" + i).is_hidden() for i in MUC)          # menu đóng
    _mo_menu(page)
    assert all(page.locator("#" + i).is_visible() for i in MUC)
    page.wait_for_function("document.querySelectorAll('#pdfLop option').length > 1")
    ten = page.locator("#pdfLop option").all_inner_texts()
    assert ten[0].startswith("Tất cả") and any(x.startswith("10A2") for x in ten)
    assert not any("Chưa có" in x for x in ten)                         # không có lựa chọn "chưa có lớp"
    assert not loi, loi


def test_chua_co_ket_qua_thi_ba_nut_bi_khoa(mo, api):
    api.create_or_update_club("a", "CLB A", 1, 0, "")
    page, loi = mo()
    _mo_menu(page)
    assert all(page.locator("#" + i).is_disabled() for i in MUC)
    assert not loi, loi


def test_danh_sach_theo_clb_goi_dung_ham_va_menu_dong_lai(mo, api):
    _nap(api)
    page, loi = mo()
    _mo_menu(page)
    page.locator("#btnPdfDsClb").click()
    page.wait_for_function("document.getElementById('xuatFeedback').textContent.includes('danh_sach_theo_clb')")
    assert _tep_pdf(os.path.join(api.thu_muc_xuat, "danh_sach_theo_clb"))
    assert page.evaluate("!document.getElementById('xuatPdfMenu').open")
    assert not loi, loi


def test_danh_sach_theo_lop_goi_dung_ham(mo, api):
    _nap(api)
    page, loi = mo()
    _mo_menu(page)
    page.locator("#btnPdfDsLop").click()
    page.wait_for_function("document.getElementById('xuatFeedback').textContent.includes('danh_sach_theo_lop')")
    assert "10A2.pdf" in _tep_pdf(os.path.join(api.thu_muc_xuat, "danh_sach_theo_lop"))
    assert not loi, loi


def test_phieu_moi_lop_ra_thu_muc_mot_tep_moi_lop(mo, api):
    _nap(api)
    page, loi = mo()
    _mo_menu(page)
    page.locator("#btnPdfPhieuLop").click()
    page.wait_for_function("document.getElementById('xuatFeedback').textContent.includes('phieu_giai_trinh_theo_lop')")
    assert _tep_pdf(os.path.join(api.thu_muc_xuat, "phieu_giai_trinh_theo_lop")) == [
        "10A1.pdf", "10A10.pdf", "10A2.pdf", "_chua_co_lop.pdf"]
    assert not loi, loi


def test_phieu_mot_lop_ra_mot_tep(mo, api):
    _nap(api)
    page, loi = mo()
    _mo_menu(page)
    page.wait_for_function("document.querySelectorAll('#pdfLop option').length > 1")
    page.select_option("#pdfLop", "10A2")
    page.locator("#btnPdfPhieuLop").click()
    page.wait_for_function("document.getElementById('xuatFeedback').textContent.includes('.pdf')")
    assert _tep_pdf(api.thu_muc_xuat) == ["phieu_giai_trinh.pdf"]
    assert not os.path.exists(os.path.join(api.thu_muc_xuat, "phieu_giai_trinh_theo_lop"))
    assert not loi, loi


def test_giao_vien_khong_thay_menu(mo, api):
    _nap(api)
    page, loi = mo()
    page.wait_for_selector("#xuatPdfMenu", state="visible")
    page.evaluate("document.body.dataset.vai = 'giao_vien'")
    assert page.locator("#xuatPdfMenu").is_hidden()
    assert not loi, loi
