"""UX2-L4 (Playwright + Chromium): lỗi NGAY TẠI Ô (#7) — seed, form CLB, form thêm học sinh, ô điểm. Dữ liệu MÔ PHỎNG."""
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


@pytest.fixture
def man(api, request):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    for sid in ("HS01", "HS02"):
        api.create_student_if_missing(sid, "Học sinh " + sid)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1000}, bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        yield page, api, loi
        br.close()


def _trang_thai(page, sel):
    return page.eval_on_selector(sel, """o => { const d = (o.getAttribute('aria-describedby') || '').split(' ').map((i) => document.getElementById(i)).filter(Boolean);
        return { inv: o.getAttribute('aria-invalid'), loi: o.classList.contains('is-loi'), chu: d.map((x) => x.textContent).join('|'),
                 lopLoiO: d.every((x) => x.classList.contains('loi-o')), focus: document.activeElement === o }; }""")


def _t(page, khoa):
    return page.evaluate("k => window.I18N.t(k)", khoa)


def test_hat_giong_sai_loi_tai_o_va_go_chu_thi_xoa(man):
    page, api, loi = man
    page.evaluate("document.getElementById('nangCao').open = true")
    page.fill("#seedInput", "1.5")
    page.click("#btnRun")
    page.wait_for_selector("#seedInput.is-loi")
    st = _trang_thai(page, "#seedInput")
    assert st["inv"] == "true" and st["loi"] and st["lopLoiO"] and st["focus"]
    assert st["chu"] == _t(page, "hat_giong_khong_hop_le")
    assert page.locator("#toastStack .toast.is-error").count() >= 1       # toast cũ giữ nguyên
    page.type("#seedInput", "0")
    st = _trang_thai(page, "#seedInput")
    assert st["inv"] is None and not st["loi"] and st["chu"] == ""
    assert page.locator(".loi-o").count() == 0
    assert loi == [], loi


def test_form_clb_thieu_o_to_dung_o_va_focus_o_dau(man):
    page, api, loi = man
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnSaveClub", state="visible")
    page.fill("#clubFormName", "Chỉ có tên")
    page.click("#btnSaveClub")
    page.wait_for_selector("#clubFormId.is-loi")
    cau = _t(page, "feedback_club_form_required")
    a, c = _trang_thai(page, "#clubFormId"), _trang_thai(page, "#clubFormCapacity")
    assert a["inv"] == c["inv"] == "true" and a["focus"] and not c["focus"]      # focus ô ĐẦU TIÊN
    assert a["chu"] == cau and c["chu"] == cau
    assert _trang_thai(page, "#clubFormName")["inv"] is None                     # ô đã điền: không bị tô
    page.type("#clubFormId", "x")
    assert _trang_thai(page, "#clubFormId")["inv"] is None
    assert _trang_thai(page, "#clubFormCapacity")["inv"] == "true"
    assert loi == [], loi


def test_form_clb_loi_backend_theo_ma_ve_dung_o_ma_la_thi_khung_phan_hoi(man):
    page, api, loi = man
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnSaveClub", state="visible")
    page.fill("#clubFormId", "clb_z")
    page.fill("#clubFormName", "CLB Z")
    page.fill("#clubFormCapacity", "0")                                          # backend: capacity_must_be_positive
    page.click("#btnSaveClub")
    page.wait_for_selector("#clubFormCapacity.is-loi")
    st = _trang_thai(page, "#clubFormCapacity")
    assert st["inv"] == "true" and st["focus"] and st["chu"] and st["lopLoiO"]
    assert st["chu"] == page.evaluate("() => window.I18N.translateError({code: 'capacity_must_be_positive', params: {}})")
    # mã lạ: không có ô -> khung phản hồi cũ, không im lặng
    page.evaluate("""() => { const g = window.pywebview.api; window.pywebview = { api: new Proxy({}, { has: () => true,
        get: (_t, n) => (n === 'create_or_update_club' ? () => Promise.resolve({ ok: false, errors: [{ code: 'error_saving_club', params: { detail: 'x' } }] }) : g[n]) }) }; }""")
    page.fill("#clubFormCapacity", "5")
    page.click("#btnSaveClub")
    page.wait_for_function("document.getElementById('clubFormFeedback').textContent.trim() !== ''")
    assert page.locator("#clubFormCapacity.is-loi").count() == 0
    assert loi == [], loi


def test_form_them_hoc_sinh_thieu_o(man):
    page, api, loi = man
    page.locator('[data-tab="fallback"]').click()
    page.wait_for_selector("#btnCreateStudent", state="visible")
    page.fill("#newStudentName", "Chỉ có tên")
    page.click("#btnCreateStudent")
    page.wait_for_selector("#newStudentId.is-loi")
    st = _trang_thai(page, "#newStudentId")
    assert st["inv"] == "true" and st["focus"] and st["chu"] == _t(page, "toast_need_id_and_name")
    assert _trang_thai(page, "#newStudentName")["inv"] is None
    assert page.locator("#toastStack .toast.is-error").count() >= 1             # toast cũ giữ nguyên
    page.type("#newStudentId", "H")
    assert _trang_thai(page, "#newStudentId")["inv"] is None
    assert loi == [], loi


def test_o_diem_sai_khi_luu_hien_loi_tai_o_focus_o_dau_va_giu_is_invalid(man):
    page, api, loi = man
    page.locator('[data-tab="scoring"]').click()
    page.wait_for_selector(".btn-row-link")
    page.locator(".btn-row-link").first.click()
    page.wait_for_selector(".score-input")
    o = page.locator(".score-input").first
    o.fill("abc")
    page.locator("#btnSaveScores").click()
    page.wait_for_selector(".score-input.is-loi")
    st = page.eval_on_selector(".score-input.is-loi", """o => ({ inv: o.getAttribute('aria-invalid'), cu: o.classList.contains('is-invalid'),
        tieuDe: o.title, chu: document.getElementById(o.getAttribute('aria-describedby')).textContent, focus: document.activeElement === o })""")
    assert st["inv"] == "true" and st["cu"] and st["tieuDe"] and st["chu"] == st["tieuDe"] and st["focus"]
    page.locator(".score-input.is-loi").type("1")
    assert page.locator(".score-input.is-loi").count() == 0 and page.locator(".loi-o").count() == 0
    assert loi == [], loi


def test_rung_chi_khi_cho_phep_chuyen_dong(man):
    page, api, loi = man
    page.evaluate("""() => { const o = document.createElement('input'); o.id = 'ux2Rg'; document.body.appendChild(o); window.__o = o; }""")
    page.evaluate("() => baoLoiTaiO(window.__o, 'x')")
    assert page.eval_on_selector("#ux2Rg", "o => o.classList.contains('ux2-rung') && getComputedStyle(o).animationName") == "ux2Rung"
    page.evaluate("() => { xoaLoiTaiO(window.__o); document.documentElement.classList.add('tat-hieu-ung'); baoLoiTaiO(window.__o, 'x'); }")
    assert page.eval_on_selector("#ux2Rg", "o => o.classList.contains('ux2-rung')") is False


def test_rung_khong_khi_giam_chuyen_dong(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True, reduced_motion="reduce")
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.evaluate("() => { const o = document.createElement('input'); o.id = 'ux2Rg'; document.body.appendChild(o); baoLoiTaiO(o, 'x'); }")
        assert page.eval_on_selector("#ux2Rg", "o => o.classList.contains('ux2-rung')") is False
        assert page.eval_on_selector("#ux2Rg", "o => o.getAttribute('aria-invalid')") == "true"      # nghĩa không dựa vào chuyển động
        br.close()


def test_bang_ma_loi_form_clb_khop_backend():
    """Tĩnh: mọi mã trong bảng UX2_LOI_CLB có trong i18n_errors.py (nguồn thông báo duy nhất)."""
    import re
    ma = open(os.path.join(GOC, "js/05_quan_ly.js"), encoding="utf-8").read()
    bang = ma[ma.index("const UX2_LOI_CLB"):ma.index("};", ma.index("const UX2_LOI_CLB"))]
    loi_py = open(os.path.join(GOC, "i18n_errors.py"), encoding="utf-8").read()
    for code in re.findall(r"^\s+(\w+):", bang, re.M):
        assert '"%s"' % code in loi_py, code


# ---------- FIX L4 vòng 1: đổi ngôn ngữ lúc lỗi còn hiện -> chữ theo ngôn ngữ mới (KHÔNG xoá lỗi) ----------
def _chu_loi(page, sel):
    return page.eval_on_selector(sel, "o => document.getElementById(o.getAttribute('aria-describedby')).textContent")


def test_doi_ngon_ngu_form_clb_va_hat_giong_chu_loi_doi_theo(man):
    page, api, loi = man
    page.evaluate("document.getElementById('nangCao').open = true")
    page.fill("#seedInput", "1.5")
    page.click("#btnRun")
    page.wait_for_selector("#seedInput.is-loi")
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnSaveClub", state="visible")
    page.click("#btnSaveClub")
    page.wait_for_selector("#clubFormId.is-loi")
    assert _chu_loi(page, "#clubFormId") == _t(page, "feedback_club_form_required")
    page.evaluate("() => window.I18N.setLang('en')")
    for sel, khoa in (("#clubFormId", "feedback_club_form_required"), ("#clubFormCapacity", "feedback_club_form_required"),
                      ("#clubFormName", "feedback_club_form_required"), ("#seedInput", "hat_giong_khong_hop_le")):
        assert _trang_thai(page, sel)["inv"] == "true", sel                        # lỗi VẪN còn
        assert _chu_loi(page, sel) == _t(page, khoa), sel                           # chữ đã sang tiếng Anh
    assert _chu_loi(page, "#clubFormId").startswith("Enter")
    page.evaluate("() => window.I18N.setLang('vi')")
    assert _chu_loi(page, "#clubFormId") == _t(page, "feedback_club_form_required")
    page.type("#clubFormId", "x")                                                   # vẫn xoá được khi gõ sau khi đổi ngôn ngữ
    assert _trang_thai(page, "#clubFormId")["inv"] is None
    assert loi == [], loi


def test_loi_backend_theo_ma_doi_ngon_ngu_dich_lai_tu_ma_va_tham_so(man):
    page, api, loi = man
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnSaveClub", state="visible")
    page.fill("#clubFormId", "clb_z")
    page.fill("#clubFormName", "CLB Z")
    page.fill("#clubFormCapacity", "0")
    page.click("#btnSaveClub")
    page.wait_for_selector("#clubFormCapacity.is-loi")
    vi = _chu_loi(page, "#clubFormCapacity")
    page.evaluate("() => window.I18N.setLang('en')")
    en = _chu_loi(page, "#clubFormCapacity")
    assert en != vi and en == page.evaluate("() => window.I18N.translateError({code: 'capacity_must_be_positive', params: {}})")


@pytest.fixture(params=["quan_tri", "giao_vien"])
def man_vai(request, api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    for sid in ("HS01", "HS02"):
        api.create_student_if_missing(sid, "Học sinh " + sid)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
    assert api.tao_tai_khoan("quantri", "matkhau-gia-1", "quan_tri")["ok"]
    if request.param == "giao_vien":
        assert api.tao_tai_khoan("gv1", "matkhau-gia-1", "giao_vien")["ok"]
        api.dang_xuat()
        assert api.dang_nhap("gv1", "matkhau-gia-1")["ok"]
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


def test_o_diem_sai_theo_vai_va_doi_ngon_ngu(man_vai):
    """Ô điểm: lỗi tại ô (is-invalid + title + .loi-o + focus) cho CẢ quan_tri LẪN giao_vien; đổi ngôn ngữ thì chữ + title đổi theo."""
    page, vai, loi = man_vai
    page.locator('[data-tab="scoring"]').click()
    page.wait_for_selector(".btn-row-link")
    page.locator(".btn-row-link").first.click()
    page.wait_for_selector(".score-input")
    page.locator(".score-input").first.fill("abc")
    page.locator("#btnSaveScores").click()
    page.wait_for_selector(".score-input.is-loi")
    st = page.eval_on_selector(".score-input.is-loi", "o => ({ inv: o.getAttribute('aria-invalid'), cu: o.classList.contains('is-invalid'), focus: document.activeElement === o })")
    assert st == {"inv": "true", "cu": True, "focus": True}, vai
    vi = _chu_loi(page, ".score-input.is-loi")
    page.evaluate("() => window.I18N.setLang('en')")
    page.wait_for_timeout(600)                           # bảng điểm được nạp lại bất đồng bộ khi đổi ngôn ngữ: lỗi phải sống sót
    assert page.locator(".score-input.is-loi").count() == 1
    en = _chu_loi(page, ".score-input.is-loi")
    assert en and en != vi
    assert page.eval_on_selector(".score-input.is-loi", "o => o.title") == en                # title đổi cùng
    assert page.eval_on_selector(".score-input.is-loi", "o => o.getAttribute('aria-invalid')") == "true"
    page.locator(".score-input.is-loi").type("1")
    assert page.locator(".loi-o").count() == 0
    assert loi == [], loi
