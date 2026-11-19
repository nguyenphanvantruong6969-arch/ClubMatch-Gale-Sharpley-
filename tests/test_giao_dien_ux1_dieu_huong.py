"""UX1A-L2: thanh bên có 4 nhóm; mọi nút `.nav-item[data-tab]` giữ nguyên.
Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG. Cổng quyền thật nằm ở backend (test_gt3_phan_quyen.py)."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM, mo_gap_ma  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"
NHOM = ("nap_xep", "nhap_tay", "ket_qua", "cai_dat")


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


def nhom_hien(page):
    return [n for n in NHOM if page.locator(f'.nav-nhom[data-nhom="{n}"]').is_visible()]


def test_quan_tri_thay_bon_nhom_va_nut_nhom_mo_the_dau(mo):
    page, api, mo_trang, loi = mo
    mo_trang()
    assert nhom_hien(page) == ["nap_xep", "nhap_tay", "ket_qua", "cai_dat"]
    assert page.locator('.nav-nhom[data-nhom="ket_qua"] .nav-nhom-nut').inner_text().strip() == "3. Kết quả & phiếu"
    page.click('.nav-nhom-nut[data-nhom-nut="ket_qua"]')
    assert page.locator(".nav-item.is-active").get_attribute("data-tab") == "results"
    page.click('.nav-nhom-nut[data-nhom-nut="cai_dat"]')
    assert page.locator(".nav-item.is-active").get_attribute("data-tab") == "admin"
    assert page.locator('.nav-nhom[data-nhom="cai_dat"]').evaluate("e => e.classList.contains('is-active')")
    # mọi nút thẻ cũ vẫn bấm được từ nhóm khác (các test khác chọn theo data-tab)
    for tab in ("fallback", "scoring", "others", "pipeline"):
        page.click(f'.nav-item[data-tab="{tab}"]')
        assert page.locator(f"#view-{tab}").evaluate("e => e.classList.contains('is-active')")
    assert not loi, loi


def test_the_chuan_bi_hien_thi_thi_nhom_cai_dat_van_dung(mo):
    page, api, mo_trang, loi = mo
    mo_trang()
    page.evaluate("document.querySelector('.nav-item[data-tab=chuan_bi]').hidden = false")
    assert page.locator('.nav-item[data-tab="chuan_bi"]').is_visible()
    assert "cai_dat" in nhom_hien(page)
    assert not loi, loi


def test_giao_vien_thay_nhom_phu_hop_va_vao_ket_qua(mo):
    page, api, mo_trang, loi = mo
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    mo_trang()
    page.wait_for_function("document.querySelector('.nav-item.is-active').dataset.tab === 'results'")
    # "1. Nạp & xếp" và "Cài đặt" chỉ có thẻ của quản trị -> biến mất
    assert nhom_hien(page) == ["nhap_tay", "ket_qua"]
    assert page.locator(".nav-item.is-active").get_attribute("data-tab") == "results"
    assert not loi, loi


def test_nang_cao_dong_mac_dinh_va_chua_hai_bang_gt2(mo):
    page, api, mo_trang, loi = mo
    mo_trang()
    page.click('.nav-item[data-tab="admin"]')
    assert not page.evaluate("document.getElementById('ux1aNangCao').open")
    assert page.locator("#gt2TieuChiPanel").is_hidden()
    assert page.evaluate("!!document.querySelector('#ux1aNangCao #gt2TieuChiPanel')")
    assert page.evaluate("!!document.querySelector('#ux1aNangCao #gt2ThuPanel')")
    assert page.locator("#qlTabClb").is_visible()   # chỉnh sửa CLB nằm trước
    page.click("#ux1aNangCao > summary")
    assert page.locator("#gt2TieuChiPanel").is_visible()
    assert not loi, loi


def test_man_hoc_sinh_phu_kin_ca_bon_nhom(mo):
    page, api, mo_trang, loi = mo
    mo_trang()
    page.click('.nav-item[data-tab="results"]')
    mo_gap_ma(page)
    page.click("#btnGtCheDoHs")
    page.wait_for_selector("#gtHs", state="visible")
    bi_che = page.evaluate("""() => Array.from(document.querySelectorAll('.nav-nhom-nut, .nav-item'))
        .filter(b => b.getClientRects().length)
        .map(b => { const r = b.getBoundingClientRect();
                    const o = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
                    return !!(o && o.closest('#gtHs')); })""")
    assert bi_che and all(bi_che)
    assert not loi, loi
