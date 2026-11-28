"""UX2-L7 (Playwright + Chromium): khung chờ (skeleton) của bảng đang tải (#6). Dữ liệu MÔ PHỎNG."""
import os
import sys
import time

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser_host  # noqa: E402
import test_giao_dien_chay as base  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_giao_dien_chay import _cham  # noqa: E402

GOC = base.GOC
api = base.api

SO_KHUNG = "() => document.querySelectorAll('#adminStudentTableBody .ux2-khung-hang').length"


def _them_hs(api, n):
    for i in range(n):
        api.create_student_if_missing("HS%04d" % i, "Học sinh %d" % i)


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(reduced=False):
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        kw = {"reduced_motion": "reduce"} if reduced else {}
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1000}, bypass_csp=True, **kw)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _vao_hs(page):
    page.locator('.nav-item[data-tab="admin"]').click()
    page.click("#qlTabHs")


def test_tai_cham_hien_khung_sau_300ms_roi_go_khi_co_du_lieu(api, mo):
    _them_hs(api, 12)
    api.list_students_admin = _cham(api.list_students_admin, 1.6)
    page, loi = mo()
    t0 = time.time()
    _vao_hs(page)
    page.wait_for_function(SO_KHUNG + " > 0", timeout=3000)
    assert page.eval_on_selector("#adminStudentTableBody .ux2-khung-hang", "r => r.getAttribute('aria-hidden')") == "true"
    assert page.eval_on_selector("#adminStudentTableBody", "b => b.closest('table').getAttribute('aria-busy')") == "true"
    assert page.evaluate(SO_KHUNG) == 8
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr:not(.ux2-khung-hang)').length >= 12", timeout=15000)
    assert page.evaluate(SO_KHUNG) == 0
    assert page.eval_on_selector("#adminStudentTableBody", "b => b.closest('table').getAttribute('aria-busy')") == "false"
    assert time.time() - t0 > 1.0
    assert loi == [], loi


def test_tai_nhanh_khong_bao_gio_chen_khung(api, mo):
    _them_hs(api, 12)
    page, loi = mo()
    page.evaluate("""() => { window.__khung = 0; new MutationObserver((ms) => ms.forEach((m) => m.addedNodes.forEach((n) => {
        if (n.classList && n.classList.contains('ux2-khung-hang')) window.__khung += 1; }))).observe(document.body, { childList: true, subtree: true }); }""")
    _vao_hs(page)
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length >= 12")
    page.wait_for_timeout(500)
    assert page.evaluate("() => window.__khung") == 0
    assert loi == [], loi


def test_api_bi_tu_choi_van_go_khung_va_tra_aria_busy(api, mo):
    _them_hs(api, 3)
    page, loi = mo()
    page.evaluate("""() => { const g = window.pywebview.api; window.pywebview = { api: new Proxy({}, { has: () => true,
        get: (_t, n) => (n === 'list_students_admin' ? () => new Promise((_, h) => setTimeout(() => h(new Error('hong')), 900)) : g[n]) }) }; }""")
    _vao_hs(page)
    page.wait_for_function(SO_KHUNG + " > 0", timeout=3000)
    page.wait_for_function(SO_KHUNG + " === 0", timeout=8000)                 # API từ chối: khung phải biến mất, không kẹt
    assert page.eval_on_selector("#adminStudentTableBody", "b => b.closest('table').getAttribute('aria-busy')") == "false"


def test_ket_qua_rong_sau_khung_hien_trang_thai_rong_L6(api, mo):
    api.list_clubs_admin = _cham(api.list_clubs_admin, 1.2)
    page, loi = mo()
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_function("document.querySelectorAll('#adminClubTableBody .ux2-khung-hang').length > 0", timeout=3000)
    page.wait_for_function("!document.getElementById('adminClubEmptyState').hidden", timeout=15000)
    assert page.eval_on_selector_all("#adminClubTableBody .ux2-khung-hang", "r => r.length") == 0
    assert page.eval_on_selector("#adminClubEmptyState", "h => !!h.querySelector('.ux2-rong-nut')")
    assert page.eval_on_selector("#adminClubTableBody", "b => b.closest('table').getAttribute('aria-busy')") == "false"
    assert loi == [], loi


def test_tai_lan_hai_khi_lan_mot_chua_xong_chi_con_mot_bo_khung(api, mo):
    _them_hs(api, 5)
    api.list_students_admin = _cham(api.list_students_admin, 1.8)
    page, loi = mo()
    _vao_hs(page)
    page.wait_for_function(SO_KHUNG + " > 0", timeout=3000)
    page.evaluate("() => { loadAdminStudents(); }")                           # lần hai trong lúc lần một chưa xong
    page.wait_for_timeout(700)
    assert page.evaluate(SO_KHUNG) == 8                                       # KHÔNG phải 16
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr:not(.ux2-khung-hang)').length >= 5 && " + SO_KHUNG[6:] + " === 0", timeout=20000)
    assert page.eval_on_selector("#adminStudentTableBody", "b => b.closest('table').getAttribute('aria-busy')") == "false"


def test_xung_sang_chi_khi_cho_phep_chuyen_dong(api, mo):
    _them_hs(api, 5)
    api.list_students_admin = _cham(api.list_students_admin, 2.0)
    page, loi = mo()
    _vao_hs(page)
    page.wait_for_function(SO_KHUNG + " > 0", timeout=3000)
    sel = "#adminStudentTableBody .ux2-khung"
    assert page.eval_on_selector(sel, "e => getComputedStyle(e).animationName") == "ux2Khung"
    page.evaluate("() => document.documentElement.classList.add('tat-hieu-ung')")
    assert page.eval_on_selector(sel, "e => getComputedStyle(e).animationName") == "none"


def test_xung_sang_tinh_khi_giam_chuyen_dong(api, mo):
    _them_hs(api, 5)
    api.list_students_admin = _cham(api.list_students_admin, 2.0)
    page, loi = mo(reduced=True)
    _vao_hs(page)
    page.wait_for_function(SO_KHUNG + " > 0", timeout=3000)
    assert page.eval_on_selector("#adminStudentTableBody .ux2-khung", "e => getComputedStyle(e).animationName") == "none"


def test_khung_khong_lam_nhay_bo_cuc_120_hs(api, mo):
    """Khung KHÔNG được đổi vị trí cột / đầu bảng so với lúc bảng còn trống (trước 300 ms); hàng khung cao ngang hàng thật.
    (Cột co giãn theo dữ liệu thật khi dữ liệu về là hành vi cũ của bảng tự co giãn, không do khung.)"""
    _them_hs(api, 120)
    api.list_students_admin = _cham(api.list_students_admin, 1.5)
    page, loi = mo()
    do = """() => { const t = document.querySelector('#adminStudentTableBody').closest('table');
        const th = Array.from(t.querySelectorAll('thead th')).filter((c) => c.offsetParent !== null).map((c) => Math.round(c.getBoundingClientRect().left));
        const r = t.querySelector('thead').getBoundingClientRect();
        const h = document.querySelector('#adminStudentTableBody tr');
        /* offsetTop / offsetHeight: bố cục THẬT, không dính transform của hiệu ứng trượt vào (L8) */
        return { th, top: Math.round(r.top), hangDau: h ? h.offsetTop : null, cao: h ? h.offsetHeight : null }; }"""
    _vao_hs(page)
    page.wait_for_function(SO_KHUNG + " > 0", timeout=3000)
    giua = page.evaluate(do)
    # "bảng trống" = cùng thời điểm nhưng giấu hàng khung đi (đo ngay, rồi trả lại)
    truoc = page.evaluate("(f) => { const k = Array.from(document.querySelectorAll('#adminStudentTableBody .ux2-khung-hang')); k.forEach((r) => { r.style.display = 'none'; }); const v = eval('(' + f + ')')(); k.forEach((r) => { r.style.display = ''; }); return v; }", do)
    assert giua["th"] == truoc["th"] and abs(giua["top"] - truoc["top"]) <= 1          # khung không đổi chỗ cột / đầu bảng
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr:not(.ux2-khung-hang)').length >= 50", timeout=20000)
    sau = page.evaluate(do)
    assert abs(sau["top"] - giua["top"]) <= 2 and abs(sau["hangDau"] - giua["hangDau"]) <= 3   # đầu bảng + hàng đầu đứng yên
    assert abs(sau["cao"] - giua["cao"]) <= 4                                                  # hàng khung cao ngang hàng thật
    assert loi == [], loi


def test_800_hs_do_mot_lan_thoi_gian_tai(api, mo):
    _them_hs(api, 800)
    page, loi = mo()
    t0 = time.time()
    _vao_hs(page)
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr:not(.ux2-khung-hang)').length >= 20", timeout=30000)
    giay = time.time() - t0
    print("UX2_800HS_TAI_GIAY=%.2f" % giay)
    assert page.evaluate(SO_KHUNG) == 0
    assert giay < 15
    assert loi == [], loi


def test_bon_bang_deu_goi_hien_khung_cho_voi_hoi_cua_lan_tai():
    """Tĩnh: bảng kết quả, học sinh quản lý, lịch sử chạy, CLB quản lý — mỗi nơi truyền promise của lần tải (để lỗi cũng gỡ khung)."""
    cap = [("js/03_ket_qua.js", "resultsTableBody"), ("js/05_quan_ly.js", "adminStudentTableBody"),
           ("js/02_van_hanh.js", "historyTableBody"), ("js/05_quan_ly.js", "adminClubTableBody")]
    for tep, bang in cap:
        with open(os.path.join(GOC, tep), encoding="utf-8") as f:
            ma = f.read()
        assert 'hienKhungCho(el("%s"), ' % bang in ma and ", hoi" in ma[ma.index('hienKhungCho(el("%s")' % bang):][:80], (tep, bang)


def test_do_tre_300ms_dung_voi_bang_tu_dung(api, mo):
    """Xác định (không phụ thuộc tốc độ máy): tải xong ở 150 ms -> KHÔNG chèn; tải 700 ms -> chèn sau ~300 ms rồi gỡ."""
    page, loi = mo()
    kq = page.evaluate("""async () => {
        const t = document.createElement('table'); t.innerHTML = '<thead><tr><th>A</th><th>B</th></tr></thead><tbody></tbody>';
        document.body.appendChild(t); const tb = t.querySelector('tbody');
        const cho = (ms) => new Promise((r) => setTimeout(r, ms));
        const dem = () => tb.querySelectorAll('.ux2-khung-hang').length;
        hienKhungCho(tb, 0, 3, cho(150)); await cho(450); const nhanh = dem(); const busyNhanh = t.getAttribute('aria-busy');
        const t0 = performance.now(); hienKhungCho(tb, 0, 3, cho(700));
        await cho(200); const som = dem(); await cho(250); const muon = dem(); const busy = t.getAttribute('aria-busy');
        await cho(400); return { nhanh, busyNhanh, som, muon, busy, xong: dem(), busyXong: t.getAttribute('aria-busy'), cot: tb.querySelector('td') ? tb.querySelector('td').colSpan : 0 }; }""")
    assert kq["nhanh"] == 0 and kq["busyNhanh"] == "false"
    assert kq["som"] == 0 and kq["muon"] == 3 and kq["busy"] == "true"          # 200 ms chưa có, 450 ms đã có 3 hàng, bảng đang bận
    assert kq["xong"] == 0 and kq["busyXong"] == "false"
