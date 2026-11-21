"""UX2-L2 (Playwright + Chromium): dấu ✓ trên chính nút sau khi lưu/xuất thành công (#3). Dữ liệu MÔ PHỎNG."""
import os
import re
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_giao_dien_chay as base  # noqa: E402

api = base.api
mo_trang = base.mo_trang
GOC = base.GOC

DAT = """() => {
  const b = document.createElement('button');
  b.id = 'ux2X'; b.className = 'btn btn-primary'; b.setAttribute('data-i18n', 'btn_save_club'); b.textContent = 'Lưu CLB';
  document.body.appendChild(b); window.I18N.applyStaticText();
  window.__chayX = (kq, cheDo) => chayNut(b, () => new Promise((r, h) => setTimeout(() => (cheDo === 'nem' ? h(new Error('x')) : r(kq)), 30)),
    () => {}, { xongKhi: (r) => r.ok });
}"""
SO_XONG = "() => document.querySelectorAll('#ux2X .ux2-xong').length"


def test_thanh_cong_hien_dau_xong_roi_go_va_nut_khong_nhay(api, mo_trang):
    page, loi = mo_trang()
    page.evaluate(DAT)
    w0 = page.eval_on_selector("#ux2X", "b => b.getBoundingClientRect().width")
    page.evaluate("() => { window.__chayX({ok: true}); }")
    page.wait_for_function(SO_XONG + " === 1", timeout=100 + 100)
    w1 = page.eval_on_selector("#ux2X", "b => b.getBoundingClientRect().width")
    assert abs(w1 - w0) <= 1
    page.wait_for_timeout(900)                       # ≈1,1 s sau lúc hiện: còn
    assert page.evaluate(SO_XONG) == 1
    page.wait_for_timeout(900)                       # > 1,6 s: mất
    assert page.evaluate(SO_XONG) == 0
    st = page.eval_on_selector("#ux2X", "b => ({mw: b.style.minWidth, cls: b.classList.contains('is-xong'), t: b.textContent.trim()})")
    assert st == {"mw": "", "cls": False, "t": "Lưu CLB"}
    assert loi == [], loi


def test_loi_khong_hien_dau_xong(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate(DAT)
    page.evaluate("() => { window.__chayX({ok: false, errors: []}); }")
    page.wait_for_function("!document.querySelector('#ux2X').classList.contains('is-ban')")
    page.evaluate("() => { window.__chayX(null, 'nem'); }")
    page.wait_for_selector("#toastStack .toast.is-error")
    page.wait_for_timeout(200)
    assert page.evaluate(SO_XONG) == 0


def test_dau_xong_van_hien_khi_tat_hieu_ung_nhung_khong_chuyen_dong(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate(DAT)
    page.evaluate("() => document.documentElement.classList.add('tat-hieu-ung')")
    page.evaluate("() => { window.__chayX({ok: true}); }")
    page.wait_for_function(SO_XONG + " === 1")
    assert page.eval_on_selector(".ux2-xong", "e => getComputedStyle(e).animationName") == "none"
    assert page.eval_on_selector(".ux2-xong", "e => getComputedStyle(e).display") != "none"


def test_doi_ngon_ngu_luc_con_dau_xong_khong_de_lai_vet(api, mo_trang):
    page, loi = mo_trang()
    page.evaluate(DAT)
    page.evaluate("() => { window.__chayX({ok: true}); }")
    page.wait_for_function(SO_XONG + " === 1")
    page.evaluate("() => window.I18N.setLang('en')")
    page.wait_for_timeout(1500)
    st = page.eval_on_selector("#ux2X", "b => ({mw: b.style.minWidth, cls: b.classList.contains('is-xong'), n: b.querySelectorAll('.ux2-xong').length, t: b.textContent.trim()})")
    assert st["mw"] == "" and not st["cls"] and st["n"] == 0 and st["t"] == page.evaluate("() => window.I18N.t('btn_save_club')")
    assert loi == [], loi


def test_bam_lai_ngay_sau_xong_khong_de_dau_cu_trong_nhan_khoi_phuc(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate(DAT)
    page.evaluate("() => { window.__chayX({ok: true}); }")
    page.wait_for_function(SO_XONG + " === 1")
    page.evaluate("() => { window.__chayX({ok: false}); }")    # bận lại ngay: ✓ cũ phải bị gỡ
    page.wait_for_function("!document.querySelector('#ux2X').classList.contains('is-ban')")
    assert page.evaluate(SO_XONG) == 0
    assert page.eval_on_selector("#ux2X", "b => b.textContent.trim()") == "Lưu CLB"


def test_cac_nut_luu_va_xuat_deu_noi_dau_xong():
    """Tĩnh: danh sách nút đã nối ✓ (CHANGELOG cũng liệt kê)."""
    def doc(t):
        with open(os.path.join(GOC, t), encoding="utf-8") as f:
            return f.read()
    luu = {"js/05_quan_ly.js": ["btnSaveClub", "btnWhLuu"], "js/06_cham_diem.js": ["btnSavePersonScores", "btnSaveScores"]}
    for tep, nuts in luu.items():
        ma = doc(tep)
        assert ma.count("xongKhi") >= len(nuts), tep
    xuat = {"js/03_ket_qua.js": ["btnXuatTuyChon", "btnXuatHsDaChon", "btnXuatTheoLop"],
            "js/10_theo_doi.js": ["btnXuatPhanHoi", "btnXuatDashboard", "btnXuatKhieuNai", "btnXuatDiemDanh"],
            "js/05_quan_ly.js": ["btnAdminXuatHs"], "js/14_giai_trinh.js": ["btnGtXuatMa"]}
    for tep, nuts in xuat.items():
        ma = doc(tep)
        for n in nuts:
            assert re.search(r'false, el\("%s"\)|undefined, undefined, el\("%s"\)|true, el\("%s"\)' % (n, n, n), ma), (tep, n)


def test_doi_ngon_ngu_don_min_width_ngay_khong_cho_het_hen(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate(DAT)
    page.evaluate("() => { window.__chayX({ok: true}); }")
    page.wait_for_function(SO_XONG + " === 1")
    page.evaluate("() => window.I18N.setLang('en')")
    st = page.eval_on_selector("#ux2X", "b => ({mw: b.style.minWidth, cls: b.classList.contains('is-xong')})")
    assert st == {"mw": "", "cls": False}
