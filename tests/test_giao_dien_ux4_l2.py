"""UX4-L2: cấu trúc thẻ Quản lý (Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG, sổ 120 học sinh).

Luật Hick (ít lựa chọn mỗi màn) và Von Restorff (một nút vàng, đỏ cô lập):
  * dải tab ≤ 4 mục: Danh sách CLB, Học sinh, Cách xếp, Thêm ▾ (Điểm quyết tâm*, Điểm chuẩn*, Bảng điều khiển*,
    Làm lại từ đầu nằm trong Thêm ▾);
  * mỗi tab con có dòng mục đích + dòng trạng thái; "Nâng cao" không còn ở đâu cả;
  * khung Cài đặt (thẻ MT1) và Tiêu chí/Thử nằm trong tab Cách xếp, không còn trên đầu mọi tab;
  * ≤ 1 nút `.btn-primary` mỗi tab con, `.btn-danger` chỉ ở "Làm lại từ đầu", nút của thanh Việc tiếp theo không vàng.
Ngân sách Hick của tab Cách xếp được siết ở L4 (test_giao_dien_ux4_l4.py)."""

import base64
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")

# Nút/ô nhìn thấy và bật trong #view-admin, trừ hàng bảng (tbody) và dải tab (đếm riêng).
JS_DEM = """() => {
  const vis = e => e.checkVisibility({checkVisibilityCSS: true, contentVisibilityAuto: true});
  const root = document.getElementById('view-admin');
  const q = 'button, select, input:not([type=hidden]), textarea, summary, a[href]';
  return Array.from(root.querySelectorAll(q)).filter(e => vis(e) && !e.disabled
    && !e.closest('tbody') && !e.closest('#qlTabs')).map(e => e.id || e.tagName);
}"""
JS_VANG = "() => Array.from(document.querySelectorAll('.btn-primary')).filter(e => e.getClientRects().length).map(e => e.id)"
JS_DO = "() => Array.from(document.querySelectorAll('.btn-danger')).filter(e => e.getClientRects().length).map(e => e.id)"
JS_DAI = "() => Array.from(document.querySelectorAll('#qlTabs > [role=tab], #qlTabs > .ql-them > button')).filter(e => e.getClientRects().length).map(e => e.id)"


@pytest.fixture
def trang(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#qlTabClb", state="visible")
    page.wait_for_function("document.querySelectorAll('#adminClubTableBody tr').length > 0")
    yield page, api, loi
    assert not loi, loi


def _mo_tab(page, ma):
    if ma in ("clb", "hs", "cach_xep"):
        page.click('#qlTabs > [data-ql-tab="%s"]' % ma)
    else:
        if page.locator("#qlThemMenu").is_hidden():
            page.click("#qlNutThem")
        page.click('#qlThemMenu [data-ql-tab="%s"]' % ma)
    page.wait_for_selector('#view-admin [role=tabpanel][data-ql-tab="%s"]' % ma, state="visible")


def test_dai_tab_bon_muc_va_them_chua_cac_muc_con_lai(trang):
    page, api, loi = trang
    assert page.evaluate(JS_DAI) == ["qlTabClb", "qlTabHs", "qlTabCachXep", "qlNutThem"]
    assert page.locator("#qlTabClb").inner_text().strip() == "Danh sách CLB"
    assert page.locator("#qlTabCachXep").inner_text().strip() == "Cách xếp"
    assert page.locator("#qlNutThem").inner_text().strip() == "Thêm"
    assert page.locator("#qlThemMenu").is_hidden()
    assert page.get_attribute("#qlNutThem", "aria-expanded") == "false"
    page.click("#qlNutThem")
    assert page.locator("#qlThemMenu").is_visible()
    assert page.get_attribute("#qlNutThem", "aria-expanded") == "true"
    # điểm quyết tâm bật (mặc định): ba mục; "Bảng điều khiển" chỉ hiện khi FA-DAA bật
    assert page.locator("#qlThemMenu [role=tab]:visible").all_inner_texts() == [
        "Điểm quyết tâm", "Điểm chuẩn", "Làm lại từ đầu"]
    page.click("#qlTabDuLieu")
    assert page.locator("#qlThemMenu").is_hidden()
    assert page.locator('#qlPanelDuLieu').is_visible()
    assert page.evaluate("document.getElementById('qlNutThem').classList.contains('is-chon')")
    page.keyboard.press("Escape")


def test_phu_de_moi_va_khong_con_chu_nang_cao(trang):
    page, api, loi = trang
    assert page.locator("#view-admin .view-desc").count() == 0            # UX6-L1: bỏ câu mô tả thẻ Quản lý
    for ma in ("clb", "hs", "cach_xep", "du_lieu"):
        _mo_tab(page, ma)
        goc = page.locator('#view-admin [role=tabpanel][data-ql-tab="%s"]' % ma)
        assert goc.locator(".ql-mo-ta").count() == 0                     # UX6-L1: bỏ dòng mục đích
        assert goc.locator(".ql-tt").inner_text().strip()                # dòng trạng thái
        assert "Nâng cao" not in page.locator("#view-admin").inner_text()
    assert page.locator("#ux1aNangCao > summary").inner_text().strip() == "Tuỳ chỉnh thêm"   # L4: mục gập mới, không còn chữ "Nâng cao"


def test_dong_trang_thai_ban_clb_va_hoc_sinh(trang):
    page, api, loi = trang
    n = len(api.list_clubs_admin()["data"])
    cho = sum(c["capacity"] for c in api.list_clubs_admin()["data"])
    ds = page.locator("#qlTtClb").inner_text()
    assert ds.startswith("%d CLB · %d chỗ" % (n, cho)), ds
    _mo_tab(page, "hs")
    page.wait_for_function("document.getElementById('qlTtHs').innerText.includes('120')")
    assert page.locator("#qlTtHs").inner_text().strip() == "120 học sinh"


def test_khung_cai_dat_va_tieu_chi_nam_trong_tab_cach_xep(trang):
    page, api, loi = trang
    assert page.evaluate("!!document.querySelector('#qlPanelCachXep #ux1aCaiDat')")
    assert page.evaluate("!!document.querySelector('#qlPanelCachXep #gt2TieuChiPanel')")
    assert page.evaluate("!!document.querySelector('#qlPanelCachXep #gt2ThuPanel')")
    assert page.locator("#ux1aCaiDat").is_hidden() and page.locator("#gt2TieuChiPanel").is_hidden()
    _mo_tab(page, "cach_xep")
    page.wait_for_selector("#gt2TcDanhSach li", state="attached")
    assert page.locator("#gt2ThuPanel").is_visible() and page.locator("#gt2TieuChiPanel").is_hidden()   # L4: tiêu chí gập trong "Tuỳ chỉnh thêm"
    page.click("#ux1aNangCao > summary")
    assert page.locator("#gt2TieuChiPanel").is_visible()
    page.wait_for_selector("#ux1aChia100", state="visible")
    # nút "Thay đổi…" cũ mở ĐÚNG tab Cách xếp và cuộn tới khung tiêu chí
    _mo_tab(page, "clb")
    page.evaluate("ux1aMoNangCao()")
    page.wait_for_selector("#qlPanelCachXep", state="visible")


def test_ngan_sach_hick_cac_tab_con(trang):
    page, api, loi = trang
    for ma in ("clb", "hs", "du_lieu"):
        _mo_tab(page, ma)
        ds = page.evaluate(JS_DEM)
        assert len(ds) <= 9, (ma, ds)
    _mo_tab(page, "du_lieu")
    assert page.evaluate(JS_DEM) == ["btnResetStudents", "btnResetAll"]


def test_von_restorff_mot_vang_do_co_lap_banner_khong_vang(trang):
    page, api, loi = trang
    for ma in ("clb", "hs", "cach_xep", "du_lieu"):
        _mo_tab(page, ma)
        assert len(page.evaluate(JS_VANG)) <= 1 or page.evaluate(JS_VANG) == [], (ma, page.evaluate(JS_VANG))
        vang = [i for i in page.evaluate(JS_VANG) if i != "viecTiepTheoNut"]
        assert len(vang) <= 1, (ma, vang)
        assert "viecTiepTheoNut" not in page.evaluate(JS_VANG)
        do = page.evaluate(JS_DO)
        assert do == (["btnResetStudents", "btnResetAll"] if ma == "du_lieu" else []), (ma, do)
    assert not page.evaluate("document.getElementById('viecTiepTheoNut').classList.contains('btn-primary')")
    _mo_tab(page, "clb")
    assert page.evaluate(JS_VANG) == ["btnSaveClub"]
    _mo_tab(page, "cach_xep")
    assert page.evaluate(JS_VANG) == ["gt2ThuChay"]


def test_tab_da_nho_cu_van_mo_dung_va_tab_an_quay_ve_clb(trang):
    page, api, loi = trang
    page.evaluate("localStorage.setItem('rbda_ql_tab_con', 'du_lieu')")
    page.reload()
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#qlPanelDuLieu", state="visible")
    page.evaluate("localStorage.setItem('rbda_ql_tab_con', 'db')")   # tab ẩn (FA-DAA tắt)
    page.reload()
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#qlPanelClb", state="visible")
