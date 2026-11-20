"""I2: chế độ học sinh khi có tài khoản, bằng TRÌNH DUYỆT THẬT (Chromium qua `browser_host`). Dữ liệu MÔ PHỎNG.

Học sinh không với tới tab nào, không gọi được hàm nào ngoài tra cứu (kể cả gọi thẳng từ console);
thoát cần tài khoản quản trị; không có tài khoản thì thoát như cũ."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM, mo_gap_ma  # noqa: E402
from test_gt_tich_hop import HS, MK, _dung  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(locale="vi-VN", bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))

        def vao(co_tai_khoan):
            ma = _dung(api)
            if co_tai_khoan:
                assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
                assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
                api.dang_xuat()
                assert api.dang_nhap("quantri", MK)["ok"]   # GT4 D4-1: chỉ quản trị vào chế độ học sinh
            page.goto(url)
            page.wait_for_selector("#gtPanel", state="attached")
            page.wait_for_function("document.body.dataset.vai !== undefined")
            page.click('button.nav-item[data-tab="results"]')
            return ma

        yield page, loi, vao


def _goi(page, ten, *args):
    return page.evaluate("([n, a]) => window.pywebview ? window.pywebview.api[n](...a) : callApi(n, ...a)",
                         [ten, list(args)])


def test_hoc_sinh_khong_toi_duoc_tab_nao_va_khong_goi_duoc_ham_khac(mo):
    page, loi, vao = mo
    ma = vao(True)
    mo_gap_ma(page)
    page.click("#btnGtCheDoHs")
    page.wait_for_selector("#gtHs", state="visible")
    assert page.evaluate("document.querySelector('.app-shell').inert") is True
    # mọi nút tab đều nằm trong phần inert: không bấm, không Tab tới được
    assert page.evaluate("[...document.querySelectorAll('.nav-item')].every(n => n.closest('[inert]'))") is True
    # gọi thẳng backend từ console: chỉ tra cứu chạy được
    r = _goi(page, "get_run_history")
    assert r["ok"] is False and r["errors"][0]["code"] == "gt3_che_do_hoc_sinh"
    r = _goi(page, "get_giai_trinh_hoc_sinh", "s2")
    assert r["ok"] is False and r["errors"][0]["code"] == "gt3_che_do_hoc_sinh"
    page.fill("#gtHsMa", "s1")
    page.fill("#gtHsMaTra", ma["s1"])
    page.click("#btnGtHsXem")
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    assert HS["s2"] not in page.locator("#gtHs").inner_text()
    assert loi == []


def test_thoat_can_quan_tri_giao_vien_va_mat_khau_sai_deu_bi_giu_lai(mo):
    page, loi, vao = mo
    vao(True)
    mo_gap_ma(page)
    page.click("#btnGtCheDoHs")
    page.click("#btnGtHsThoat")
    page.click("#btnGtHsCo")
    page.wait_for_selector("#gtHsQuanTri", state="visible")
    for ten, mk in (("quantri", "sai"), ("gv1", MK)):
        page.fill("#gtHsQtTen", ten)
        page.fill("#gtHsQtMk", mk)
        page.click("#btnGtHsQtThoat")
        page.wait_for_function("document.querySelector('#gtHsQtLoi').innerText.length > 0")
        assert "không đúng" in page.locator("#gtHsQtLoi").inner_text()
        assert page.locator("#gtHsQtMk").input_value() == ""
        assert page.evaluate("document.querySelector('.app-shell').inert") is True
        page.evaluate("document.querySelector('#gtHsQtLoi').textContent = ''")
    page.fill("#gtHsQtTen", "quantri")
    page.fill("#gtHsQtMk", MK)
    page.click("#btnGtHsQtThoat")
    page.wait_for_function("document.querySelector('.app-shell').inert === false")
    assert page.locator("#gtHs").is_hidden()
    page.wait_for_function("document.body.dataset.vai === 'quan_tri'")      # phiên quản trị hiện ngay
    assert _goi(page, "get_run_history")["ok"] is True
    assert loi == []


def test_khong_co_tai_khoan_thoat_nhu_cu(mo):
    page, loi, vao = mo
    vao(False)
    mo_gap_ma(page)
    page.click("#btnGtCheDoHs")
    page.click("#btnGtHsThoat")
    page.click("#btnGtHsCo")
    page.wait_for_function("document.querySelector('.app-shell').inert === false")
    assert page.locator("#gtHsQuanTri").is_hidden() and page.locator("#gtHs").is_hidden()
    assert loi == []


def test_tai_lai_trang_o_che_do_hoc_sinh_van_con_lop_phu_va_quan_tri_thoat_duoc(mo):
    page, loi, vao = mo
    ma = vao(True)
    mo_gap_ma(page)
    page.click("#btnGtCheDoHs")
    page.wait_for_selector("#gtHs", state="visible")
    page.wait_for_timeout(300)                        # để vao_che_do_hoc_sinh kịp tới backend
    page.reload()
    page.wait_for_selector("#gtPanel", state="attached")
    page.wait_for_selector("#gtHs", state="visible")                    # mở lại, không cần bấm gì
    assert page.evaluate("document.querySelector('.app-shell').inert") is True
    assert page.evaluate("[...document.querySelectorAll('.nav-item')].every(n => n.closest('[inert]'))") is True
    r = _goi(page, "get_run_history")
    assert r["ok"] is False and r["errors"][0]["code"] == "gt3_che_do_hoc_sinh"
    page.fill("#gtHsMa", "s1")                                          # học sinh vẫn tra cứu được sau khi tải lại
    page.fill("#gtHsMaTra", ma["s1"])
    page.click("#btnGtHsXem")
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    page.click("#btnGtHsThoat")
    page.click("#btnGtHsCo")
    page.wait_for_selector("#gtHsQuanTri", state="visible")
    page.fill("#gtHsQtTen", "quantri")
    page.fill("#gtHsQtMk", MK)
    page.click("#btnGtHsQtThoat")
    page.wait_for_function("document.querySelector('.app-shell').inert === false")
    assert _goi(page, "get_run_history")["ok"] is True
    page.click('button.nav-item[data-tab="admin"]')                      # sau khi thoát, tab bấm được
    page.wait_for_function("document.querySelector('.nav-item[data-tab=admin]').classList.contains('is-active')")
    assert loi == []


def test_tra_loi_phien_cu_khong_mo_lai_lop_phu_sau_khi_quan_tri_thoat(mo):
    """Trả lời get_phien_dang_nhap (che_do_hs: true) bị giữ chậm, tới sau khi quản trị đã thoát: bỏ, lớp phủ không mở lại."""
    page, loi, vao = mo
    vao(True)
    mo_gap_ma(page)
    page.click("#btnGtCheDoHs")
    page.wait_for_selector("#gtHs", state="visible")
    page.wait_for_timeout(300)
    page.evaluate("""() => {
        const goc = window.fetch.bind(window);
        window.__giu = true;
        window.fetch = async (...a) => {
            const r = await goc(...a);
            if (window.__giu && String(a[0]).includes("get_phien_dang_nhap")) {
                window.__giu = false;                       // chỉ giữ MỘT trả lời
                await new Promise((x) => setTimeout(x, 1500));
            }
            return r;
        };
    }""")
    page.evaluate("window.dispatchEvent(new Event('tkLamMoi'))")   # lần hỏi bị giữ (backend vẫn trả che_do_hs: true)
    page.wait_for_timeout(200)
    page.click("#btnGtHsThoat")
    page.click("#btnGtHsCo")
    page.wait_for_selector("#gtHsQuanTri", state="visible")
    page.fill("#gtHsQtTen", "quantri")
    page.fill("#gtHsQtMk", MK)
    page.click("#btnGtHsQtThoat")
    page.wait_for_function("document.querySelector('.app-shell').inert === false")
    page.wait_for_timeout(2200)                                      # trả lời cũ tới nơi
    assert page.evaluate("document.getElementById('gtHs').hidden") is True
    assert page.evaluate("document.querySelector('.app-shell').inert") is False
    assert _goi(page, "get_run_history")["ok"] is True
    assert loi == []
