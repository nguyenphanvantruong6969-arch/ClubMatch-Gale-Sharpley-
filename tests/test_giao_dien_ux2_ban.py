"""UX2-L1 (Playwright + Chromium): trạng thái "đang bận" (#2) + chống bấm đúp (#13) qua MỘT hàm `datNutBan`.
Dữ liệu MÔ PHỎNG. Mẫu: test_giao_dien_chay.py / test_giao_dien_sg9_nut_ban.py."""
import os
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_giao_dien_chay as base  # noqa: E402
from test_giao_dien_chay import _cham, _so_lan_chay  # noqa: E402,F401
from _trinh_duyet import CHROMIUM  # noqa: E402
import browser_host  # noqa: E402

api = base.api
mo_trang = base.mo_trang

DAT_NUT = """() => {
  const b = document.createElement('button');
  b.id = 'ux2Thu'; b.className = 'btn btn-secondary';
  b.innerHTML = '<span id="ux2Icon">★</span> Lưu thử';
  document.body.appendChild(b);
  window.__goi = 0;
  window.__chayThu = (ham) => chayNut(b, () => { window.__goi += 1; return ham(); }, () => {});
}"""


def test_btnrun_ban_nhan_rong_va_chay_mot_lan(api, mo_trang):
    api.run_pipeline = _cham(api.run_pipeline, 1.2)
    page, loi = mo_trang()
    r0 = page.eval_on_selector("#btnRun", "b => b.getBoundingClientRect().width")
    page.dblclick("#btnRun")
    page.wait_for_function("document.querySelector('#btnRun').getAttribute('aria-busy') === 'true'", timeout=100 + 400)
    st = page.eval_on_selector("#btnRun", """b => ({dis: b.disabled, cls: b.classList.contains('is-ban'),
        sp: b.querySelectorAll('.ux2-xoay').length, txt: b.textContent.trim(), w: b.getBoundingClientRect().width})""")
    assert st["dis"] and st["cls"] and st["sp"] == 1 and st["txt"] == "Đang xếp…"
    assert abs(st["w"] - r0) <= 1
    page.wait_for_function("!document.querySelector('#runXong').hidden", timeout=20000)
    page.wait_for_function("document.querySelector('#btnRun').getAttribute('aria-busy') === 'false'")
    st = page.eval_on_selector("#btnRun", "b => ({sp: b.querySelectorAll('.ux2-xoay').length, txt: b.textContent.trim()})")
    assert st["sp"] == 0 and st["txt"] == "Chạy sắp xếp"
    page.wait_for_timeout(300)
    assert _so_lan_chay(api) == 1
    assert loi == [], loi


def test_nut_co_icon_giu_icon_sau_thanh_cong_va_sau_loi(api, mo_trang):
    page, loi = mo_trang()
    page.evaluate(DAT_NUT)
    w0 = page.eval_on_selector("#ux2Thu", "b => b.getBoundingClientRect().width")
    page.evaluate("() => { window.__xong = null; window.__chayThu(() => new Promise(r => { window.__xong = r; })); }")
    page.dblclick("#ux2Thu", force=True)
    st = page.eval_on_selector("#ux2Thu", """b => ({dis: b.disabled, busy: b.getAttribute('aria-busy'),
        sp: b.querySelectorAll('.ux2-xoay').length, icon: !!b.querySelector('#ux2Icon'), txt: b.textContent.trim(),
        w: b.getBoundingClientRect().width})""")
    assert st["dis"] and st["busy"] == "true" and st["sp"] == 1 and not st["icon"] and st["txt"] == "Đang xử lý…"
    assert page.evaluate("() => window.__goi") == 1          # bấm đúp: API MỘT lần
    page.evaluate("() => window.__xong({ok: true})")
    page.wait_for_function("document.querySelector('#ux2Thu').getAttribute('aria-busy') === 'false'")
    st = page.eval_on_selector("#ux2Thu", "b => ({icon: !!b.querySelector('#ux2Icon'), dis: b.disabled, txt: b.textContent.trim(), mw: b.style.minWidth, w: b.getBoundingClientRect().width})")
    assert st["icon"] and not st["dis"] and st["txt"] == "★ Lưu thử" and st["mw"] == ""
    assert abs(st["w"] - w0) <= 1
    # promise bị từ chối: vẫn trả nút
    page.evaluate("() => window.__chayThu(() => Promise.reject(new Error('hong')))")
    page.wait_for_selector("#toastStack .toast.is-error")
    page.wait_for_function("document.querySelector('#ux2Thu').getAttribute('aria-busy') === 'false'")
    assert page.eval_on_selector("#ux2Thu", "b => !!b.querySelector('#ux2Icon') && !b.disabled")


def test_do_tre_aria_busy_duoi_100ms(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate(DAT_NUT)
    ms = page.evaluate("""() => new Promise((xong) => {
        const b = document.getElementById('ux2Thu');
        const t0 = performance.now();
        window.__chayThu(() => new Promise(() => {}));
        requestAnimationFrame(() => xong(b.getAttribute('aria-busy') === 'true' ? performance.now() - t0 : -1));
    })""")
    assert 0 <= ms <= 100, ms


def test_vong_xoay_tinh_khi_tat_hieu_ung(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate(DAT_NUT)
    page.evaluate("() => { window.__chayThu(() => new Promise(() => {})); }")
    assert page.eval_on_selector(".ux2-xoay", "e => getComputedStyle(e).animationName") == "ux2Xoay"
    page.evaluate("() => document.documentElement.classList.add('tat-hieu-ung')")
    assert page.eval_on_selector(".ux2-xoay", "e => getComputedStyle(e).animationName") == "none"


def test_vong_xoay_tinh_khi_giam_chuyen_dong(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    base._nap_du_lieu(api)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, base.GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True, reduced_motion="reduce")
        page.goto(url)
        page.wait_for_selector("#chonBuoiChip .buoi-chip")
        page.evaluate(DAT_NUT)
        page.evaluate("() => { window.__chayThu(() => new Promise(() => {})); }")
        assert page.eval_on_selector(".ux2-xoay", "e => getComputedStyle(e).animationName") == "none"
        br.close()


def test_doi_ngon_ngu_luc_ban_giu_vong_xoay_va_tra_nhan_ngon_ngu_moi(api, mo_trang):
    """FIX L1: applyStaticText không được ghi đè nhãn nút đang bận (btnRun, nút data-i18n khác, nút khiBan)."""
    api.run_pipeline = _cham(api.run_pipeline, 1.5)
    page, loi = mo_trang()
    page.evaluate("""() => {
      const b = document.createElement('button');
      b.id = 'ux2Tinh'; b.setAttribute('data-i18n', 'btn_validate'); b.textContent = '...';
      document.body.appendChild(b); window.I18N.applyStaticText();
      window.__chayTinh = () => chayNut(b, () => new Promise((r) => { window.__xongTinh = r; }), () => {});
      const c = document.createElement('button'); c.id = 'ux2Khi'; c.textContent = 'Lưu';
      document.body.appendChild(c);
      window.__khi = () => khiBan(c, () => new Promise((r) => { window.__xongKhi = r; }));
    }""")
    page.evaluate("() => { window.__chayTinh(); window.__khi(); }")
    page.click("#btnRun")
    page.wait_for_function("document.querySelector('#btnRun').getAttribute('aria-busy') === 'true'")
    page.evaluate("() => window.I18N.setLang('en')")
    for sel, chu in (("#btnRun", "Allocating…"), ("#ux2Tinh", "Working…"), ("#ux2Khi", "Working…")):
        st = page.eval_on_selector(sel, "b => ({sp: b.querySelectorAll('.ux2-xoay').length, txt: b.textContent.trim(), dis: b.disabled})")
        assert st == {"sp": 1, "txt": chu, "dis": True}, (sel, st)
    page.evaluate("() => { window.__xongTinh(); window.__xongKhi(); }")
    page.wait_for_function("!document.querySelector('#ux2Tinh').classList.contains('is-ban')")
    assert page.eval_on_selector("#ux2Tinh", "b => b.textContent.trim()") == page.evaluate("() => window.I18N.t('btn_validate')")
    assert page.eval_on_selector("#ux2Khi", "b => b.textContent.trim() + b.getAttribute('aria-busy')") == "Lưufalse"
    page.wait_for_function("!document.querySelector('#runXong').hidden", timeout=20000)
    page.wait_for_function("!document.querySelector('#btnRun').classList.contains('is-ban')")
    assert page.eval_on_selector("#btnRun", "b => b.textContent.trim()") == "Run allocation"
    assert loi == [], loi
