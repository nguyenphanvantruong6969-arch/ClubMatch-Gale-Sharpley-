"""SFB-L2: hai menu thả xuống UX5A (`.menu-khac-hop.ux5a-hop-rong`: "Báo cáo và phiếu in ▾" ở thẻ Kết quả, "Xuất tệp
khác ▾" ở thẻ Chi tiết) phải nằm trọn trong màn hình hẹp (Chromium thật; dữ liệu MÔ PHỎNG: sổ 120 học sinh, đã chạy
xếp seed 42). Trước SFB hộp neo mép phải của nút nằm bên TRÁI hàng nên ở 390 px bị cắt mất mép trái (x = -132)."""

import base64
import os
import tempfile

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _ux5a_chung import GOC, SO_120  # noqa: E402
from api import PipelineAPI  # noqa: E402

TAB_MENU = (("results", "#ux1bThemMenu"), ("others", "#xuatMenu"))

JS_HOP = """(menu) => {
  const h = menu.querySelector('.menu-khac-hop.ux5a-hop-rong'), r = h.getBoundingClientRect();
  return {trai: r.left, phai: r.right, tren: r.top, duoi: r.bottom, rong: r.width,
          vitri: getComputedStyle(h).position, vw: document.documentElement.clientWidth, vh: window.innerHeight};
}"""


@pytest.fixture(params=[True, False], ids=["co_lop", "khong_lop"])
def trang(request):
    """(page, loi) với sổ 120 em đã xếp; co_lop=True gán 4 lớp 10A1..10A4 (hiện ô "Chọn lớp"), False thì không có lớp."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    tmp = tempfile.mkdtemp()
    goc, xuat = os.path.join(tmp, "g"), os.path.join(tmp, "x")
    os.makedirs(goc)
    os.makedirs(xuat)
    slug = ws.tao(goc, "Truong hoc", None)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=xuat, thu_muc_goc_ws=goc, ws_da_chon=True)
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    if request.param:
        for i in range(1, 121):
            assert api.set_student_class("HS%03d" % i, "10A%d" % (1 + i % 4))["ok"]
    assert api.run_pipeline(seed=42)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(viewport={"width": 1280, "height": 900}, bypass_csp=True)
    page.set_default_timeout(10000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone", state="attached")
    page.wait_for_function("document.body.dataset.vai !== undefined")
    yield page, loi
    br.close()
    pw.stop()


def _mo_menu(page, tab, sel):
    page.locator('.nav-item[data-tab="%s"]' % tab).click()
    page.wait_for_selector("#view-%s" % tab, state="visible")
    page.wait_for_selector(sel, state="visible")
    if page.locator(sel).get_attribute("open") is None:
        page.locator(sel + " > summary").click()
    page.wait_for_selector(sel + " .menu-khac-hop.ux5a-hop-rong", state="visible")
    return page.locator(sel).evaluate(JS_HOP)


@pytest.mark.parametrize("rong", [390, 768])
def test_menu_ux5a_nam_tron_trong_man_hinh_hep(trang, rong):
    page, loi = trang
    page.set_viewport_size({"width": rong, "height": 844})
    for tab, sel in TAB_MENU:
        r = _mo_menu(page, tab, sel)
        assert r["trai"] >= 0 and r["phai"] <= r["vw"] + 0.5, (rong, tab, r)
        assert r["tren"] >= 0 and r["duoi"] <= r["vh"] + 0.5, (rong, tab, r)
        assert r["vitri"] == "fixed", (rong, tab, r)
        page.locator(sel + " > summary").click()                 # đóng lại cho vòng sau
    assert not loi, loi


def test_menu_ux5a_man_hinh_rong_giu_nguyen_neo_tuyet_doi(trang):
    page, loi = trang
    page.set_viewport_size({"width": 1280, "height": 900})
    for tab, sel in TAB_MENU:
        r = _mo_menu(page, tab, sel)
        assert r["vitri"] == "absolute", (tab, r)               # bố cục > 800 px không đổi
        assert 0 <= r["trai"] and r["phai"] <= r["vw"] and r["rong"] <= 360.5, (tab, r)
    assert not loi, loi
