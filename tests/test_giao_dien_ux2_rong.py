"""UX2-L6 (Playwright + Chromium): trạng thái rỗng có hướng dẫn + MỘT nút chính; nút tôn trọng quyền; đổi ngôn ngữ vẽ lại. Dữ liệu MÔ PHỎNG."""
import os
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser_host  # noqa: E402
import test_giao_dien_chay as base  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = base.GOC
api = base.api
MK = "matkhau-gia-1"


@pytest.fixture(params=["quan_tri", "giao_vien"])
def trong(request, api):
    """CSDL TRỐNG (không CLB, không học sinh, chưa chạy) cho từng vai."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    if request.param == "giao_vien":
        assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
        api.dang_xuat()
        assert api.dang_nhap("gv1", MK)["ok"]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1000}, bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.wait_for_function("document.body.dataset.vai !== undefined")
        yield page, request.param, loi
        br.close()


def _mo_tab(page, tab):
    page.locator('.nav-item[data-tab="%s"]' % tab).click()
    page.wait_for_timeout(500)


def _mo_muc(page, id_):
    """Các mục kết quả mặc định ĐÓNG (MAC_DINH_DONG): mở mục đúng như người dùng làm trước khi thấy nội dung bên trong."""
    nut = page.locator("#%s .panel-toggle" % id_)
    if nut.count() and nut.get_attribute("aria-expanded") == "false":
        nut.click()
        page.wait_for_timeout(200)


def _kiem_giao_vien(page):
    """giao_vien: thẻ Vận hành / Quản lý bị ẩn; hộp rỗng KHÔNG có nút nhìn thấy và nhờ quản trị viên (không chỉ tới thẻ họ không có)."""
    assert page.is_visible('.nav-item[data-tab="pipeline"]') is False and page.is_visible('.nav-item[data-tab="admin"]') is False
    _mo_tab(page, "others")
    _mo_muc(page, "dsXepPanel")
    page.wait_for_function("!document.getElementById('resultsEmptyState').hidden")
    tt = _thong_tin(page, "#resultsEmptyState")
    assert tt["nut"] == 0 and tt["tong"] == 0
    assert "quản trị viên" in tt["huong"] and "Chưa có kết quả" in tt["chu"]
    assert "thẻ" not in tt["chu"] and "Xếp" not in tt["chu"]                 # không bảo đi tới thẻ họ không thấy
    n = page.eval_on_selector("#clbEmpty", "h => h.__ux2Rong ? h.textContent : null")
    if n:                                                                        # hộp CLB chỉ có nội dung khi đã hiện một lần
        assert "quản trị viên" in n and "Quản lý" not in n


def _thong_tin(page, sel):
    return page.eval_on_selector(sel, """h => ({
        an: h.hidden,
        chu: (h.querySelector('.ux2-rong-chu') || {}).textContent || '',
        huong: (h.querySelector('.ux2-rong-huong') || {}).textContent || '',
        nut: Array.from(h.querySelectorAll('button')).filter((b) => getComputedStyle(b).display !== 'none').length,
        tong: h.querySelectorAll('button').length,
        lop: (h.querySelector('button') || { className: '' }).className })""")


def test_trang_thai_rong_co_chu_huong_dan_va_dung_mot_nut_theo_quyen(trong):
    page, vai, loi = trong
    cac = [("others", "#resultsEmptyState"), ("scoring", None)]
    _mo_tab(page, "others")
    _mo_muc(page, "dsXepPanel")
    page.wait_for_function("!document.getElementById('resultsEmptyState').hidden")
    tt = _thong_tin(page, "#resultsEmptyState")
    assert tt["chu"] and tt["huong"] and tt["tong"] <= 1
    assert tt["nut"] == (1 if vai == "quan_tri" else 0)                    # giao_vien: hướng dẫn, KHÔNG có nút của quản trị
    if vai == "quan_tri":
        assert "btn btn-primary" in tt["lop"]
    assert cac


def test_the_quan_ly_rong_co_nut_dua_con_tro_den_o_dung(trong):
    page, vai, loi = trong
    if vai != "quan_tri":
        _kiem_giao_vien(page)
        return
    _mo_tab(page, "admin")
    page.wait_for_function("!document.getElementById('adminClubEmptyState').hidden")
    tt = _thong_tin(page, "#adminClubEmptyState")
    assert tt["chu"] and tt["huong"] and tt["nut"] == 1
    page.focus("#adminClubEmptyState .ux2-rong-nut")                         # bàn phím: nút Tab tới được
    page.keyboard.press("Enter")
    page.wait_for_function("document.activeElement && document.activeElement.id === 'clubFormId'")
    # học sinh rỗng: nút đi sang thẻ nhập nguyện vọng và nhắm vào ô mã học sinh mới
    _mo_tab(page, "admin")
    page.click("#qlTabHs")                                                   # mục con "Học sinh" của thẻ Quản lý
    page.wait_for_function("!document.getElementById('adminStudentEmptyState').hidden")
    assert _thong_tin(page, "#adminStudentEmptyState")["nut"] == 1
    page.focus("#adminStudentEmptyState .ux2-rong-nut")
    page.keyboard.press("Enter")
    page.wait_for_function("document.activeElement && document.activeElement.id === 'newStudentId'")
    assert page.locator('.nav-item[data-tab="fallback"]').get_attribute("class").find("is-active") >= 0
    assert loi == [], loi


def test_nut_chua_co_ket_qua_di_sang_the_van_hanh_va_focus_vung_tha(trong):
    page, vai, loi = trong
    if vai != "quan_tri":
        _kiem_giao_vien(page)
        return
    _mo_tab(page, "others")
    _mo_muc(page, "dsXepPanel")
    page.wait_for_function("!document.getElementById('resultsEmptyState').hidden")
    page.focus("#resultsEmptyState .ux2-rong-nut")
    page.keyboard.press("Enter")
    page.wait_for_function("document.activeElement && document.activeElement.id === 'dropZone'")
    assert page.locator('.nav-item[data-tab="pipeline"]').get_attribute("class").find("is-active") >= 0


def test_cham_diem_theo_nguoi_rong_giao_vien_chi_thay_huong_dan(trong):
    page, vai, loi = trong
    _mo_tab(page, "scoring")
    ok = page.evaluate("() => (typeof loadScoringPersons === 'function') ? (loadScoringPersons(), true) : false")
    assert ok
    page.wait_for_function("!document.getElementById('scoringPersonEmpty').hidden", timeout=8000) if page.evaluate(
        "() => !document.getElementById('scoringPersonEmpty').hidden") is False else None
    # hộp có thể nằm trong khung ẩn: kiểm nội dung đã vẽ, không phụ thuộc hiển thị
    n = page.eval_on_selector("#scoringPersonEmpty", "h => ({ huong: (h.querySelector('.ux2-rong-huong') || {}).textContent || '', nut: h.querySelectorAll('button').length })")
    assert n["huong"]
    if vai == "giao_vien":
        assert n["nut"] == 0 and "quản trị viên" in n["huong"]               # không nút; nhờ quản trị viên nạp danh sách
    else:
        assert n["nut"] == 1
        assert page.eval_on_selector("#scoringPersonEmpty button", "b => getComputedStyle(b).display") != "none"


def test_doi_ngon_ngu_chu_huong_dan_va_nhan_nut_theo_ngon_ngu_moi(trong):
    page, vai, loi = trong
    _mo_tab(page, "others")
    _mo_muc(page, "dsXepPanel")
    page.wait_for_function("!document.getElementById('resultsEmptyState').hidden")
    vi = page.inner_text("#resultsEmptyState")
    page.evaluate("() => window.I18N.setLang('en')")
    en = page.inner_text("#resultsEmptyState")
    assert vi != en and "No results yet" in en and "Results show up here" in en
    if vai == "quan_tri":
        assert "Run allocation" in en
        assert page.locator("#resultsEmptyState button").count() == 1       # nút không bị applyStaticText xoá
    page.evaluate("() => window.I18N.setLang('vi')")
    assert page.inner_text("#resultsEmptyState") == vi
    assert loi == [], loi


def test_hop_rong_khong_con_data_i18n_de_khong_bi_ghi_de():
    with open(os.path.join(GOC, "index.html"), encoding="utf-8") as f:
        html = f.read()
    for ma in ("resultsEmptyState", "adminClubEmptyState", "adminStudentEmptyState", "scoringPersonEmpty", "clbEmpty"):
        i = html.index('id="%s"' % ma)
        thẻ = html[i:html.index(">", i)]
        assert "data-i18n" not in thẻ, ma


def test_the_ket_qua_kqrong_chua_co_ket_qua_theo_vai(trong):
    page, vai, loi = trong
    _mo_tab(page, "results")
    page.wait_for_function("!document.getElementById('kqRong').hidden", timeout=10000)
    tt = _thong_tin(page, "#kqRong")
    assert "Chưa có kết quả" in tt["chu"] and tt["huong"]
    assert tt["nut"] == (1 if vai == "quan_tri" else 0)
    if vai == "quan_tri":
        page.focus("#kqRong .ux2-rong-nut")
        page.keyboard.press("Enter")
        page.wait_for_function("document.activeElement && document.activeElement.id === 'dropZone'")
    assert loi == [], loi


def test_moi_cau_hinh_rong_dung_khoa_i18n_co_du_hai_ngon_ngu():
    """Tĩnh: mọi khoá i18n mà các cấu hình trạng thái rỗng dùng đều có tiếng Việt VÀ tiếng Anh."""
    import re
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        i18n = f.read()
    khoa = set()
    for tep in ("js/03_ket_qua.js", "js/05_quan_ly.js", "js/06_cham_diem.js", "js/09_the_xem.js"):
        with open(os.path.join(GOC, tep), encoding="utf-8") as f:
            ma = f.read()
        khoa |= set(re.findall(r'(?:huongDan|nhan): "(ux2_rong_\w+)"', ma))
    assert len(khoa) >= 8
    for k in khoa:
        assert len(re.findall(r"\b%s:" % k, i18n)) == 2, k


def test_doi_vai_ve_lai_hop_rong_khong_can_doi_ngon_ngu(trong):
    page, vai, loi = trong
    if vai != "quan_tri":
        return
    _mo_tab(page, "others")
    _mo_muc(page, "dsXepPanel")
    page.wait_for_function("!document.getElementById('resultsEmptyState').hidden")
    assert _thong_tin(page, "#resultsEmptyState")["nut"] == 1
    page.evaluate("() => { document.body.dataset.vai = 'giao_vien'; window.dispatchEvent(new Event('ux2vai')); }")
    tt = _thong_tin(page, "#resultsEmptyState")
    assert tt["tong"] == 0 and "quản trị viên" in tt["huong"]
    page.evaluate("() => { document.body.dataset.vai = 'quan_tri'; window.dispatchEvent(new Event('ux2vai')); }")
    assert _thong_tin(page, "#resultsEmptyState")["nut"] == 1
    with open(os.path.join(GOC, "js/16_tai_khoan.js"), encoding="utf-8") as f:
        assert 'new Event("ux2vai")' in f.read()                               # ganVai() thật sự phát sự kiện khi đổi vai


def test_cau_huong_dan_dung_dung_ten_the_cua_thanh_ben_ca_tieng_anh(trong):
    page, vai, loi = trong
    if vai != "quan_tri":
        return
    page.evaluate("() => window.I18N.setLang('en')")
    ten = page.evaluate("() => Object.fromEntries(['pipeline', 'admin', 'fallback'].map((t) => [t, document.querySelector('.nav-item[data-tab=' + t + ']').innerText.trim()]))")
    xep, nhap = ten["pipeline"], ten["fallback"]
    assert xep == "Run allocation"
    _mo_tab(page, "others")
    _mo_muc(page, "dsXepPanel")
    page.wait_for_function("!document.getElementById('resultsEmptyState').hidden")
    chu = page.inner_text("#resultsEmptyState")
    assert chu.startswith("No results yet.") and '"%s"' % xep in chu                               # nút nêu đúng tên thẻ thật trên thanh bên
    assert '"Allocation"' not in chu
    _mo_tab(page, "admin")
    page.wait_for_function("!document.getElementById('adminClubEmptyState').hidden")
    page.click("#qlTabHs")
    page.wait_for_function("!document.getElementById('adminStudentEmptyState').hidden")
    hs = page.inner_text("#adminStudentEmptyState")
    assert '"%s"' % nhap in hs and '"%s"' % xep in hs
