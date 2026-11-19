"""UX1A-L3: thẻ Kết quả tra cứu trước, một menu "Xuất…", thông báo nạp sổ hiện một lần.
Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG."""

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
            page = br.new_page(bypass_csp=True, viewport={"width": 1400, "height": 1000})
            page.set_default_timeout(15000)
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("#dropZone")
            return page, loi
        yield _mo
        br.close()


def _nap(api):
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]


def test_tra_cuu_nam_tren_bang_ket_qua_va_khong_con_lien_ket_nhay(mo, api):
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    page, loi = mo()
    page.locator('.nav-item[data-tab="results"]').click()
    page.wait_for_selector("#gtPanel", state="visible")
    assert page.evaluate("""() => !!(document.getElementById('gtPanel')
        .compareDocumentPosition(document.getElementById('kqBang')) & Node.DOCUMENT_POSITION_FOLLOWING)""")
    page.locator("#kqTang1 [data-kq=\"ma\"]").click()
    page.wait_for_selector("#kqBang", state="visible")
    assert page.locator("#gtPanel").bounding_box()["y"] < page.locator("#kqBang").bounding_box()["y"]
    assert page.locator("#gtNhay").count() == 0
    assert not loi, loi


def test_mac_dinh_chi_hai_nut_xuat_hien_va_menu_chi_co_o_huy_chuong(mo, api):
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    page, loi = mo()
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#btnXuatTuyChon", state="visible")
    hien = page.evaluate("""() => Array.from(document.querySelectorAll('#xuatPanel .search-row button'))
        .filter(b => b.getClientRects().length).map(b => b.id)""")
    assert hien == ["btnXuatTuyChon", "btnXuatTheoLop"], hien
    assert page.locator("#xuatMenu").is_hidden()
    assert not loi, loi


def test_che_do_huy_chuong_co_menu_xuat_gom_bon_nut(mo, api):
    from test_giao_dien_fa_ket_qua import _fa
    _fa(api)
    page, loi = mo()
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#xuatMenu", state="visible")
    assert page.locator("#xuatMenu > summary").inner_text().strip() == "Xuất…"
    ids = ("btnXuatLyDo", "btnXuatNhuCau", "btnXuatGoiY", "btnXuatBienBan")
    assert all(page.locator("#" + i).is_hidden() for i in ids)      # menu đóng: chỉ còn hai nút chính
    page.locator("#xuatMenu > summary").click()
    assert all(page.locator("#" + i).is_visible() for i in ids)
    page.locator("#btnXuatLyDo").click()
    page.wait_for_function("() => !document.getElementById('xuatMenu').open")   # bấm một mục thì menu đóng
    assert not loi, loi


def test_thong_bao_nap_so_hien_mot_lan(mo, api):
    page, loi = mo()
    page.locator("#fileAny").set_input_files([SO_120])
    page.wait_for_function("() => !document.getElementById('btnImportAll').hidden")
    page.locator("#btnImportAll").click()
    page.wait_for_selector(".queue-row.is-done")
    page.wait_for_selector(".toast.is-success")
    assert page.locator("#feedbackImportAll").inner_text().strip() == ""
    so = page.evaluate("() => document.body.innerText.split('Xong: 9 CLB').length - 1")
    assert so == 1                                   # câu có số CLB / học sinh chỉ ở hàng của tệp
    assert not loi, loi
