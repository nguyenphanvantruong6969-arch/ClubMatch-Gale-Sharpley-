"""UX5A: dựng trang Chromium thật (qua `browser_host`) cho thẻ Kết quả và Chi tiết, vai quản trị hoặc giáo viên.
Dữ liệu MÔ PHỎNG: sổ 120 học sinh, 4 lớp 10A1..10A4, đã chạy xếp (seed 42)."""

import base64
import os
import tempfile

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
MK = "matkhau-gia-1"

# Điều khiển nhìn thấy và bật trong một vùng, trừ hàng bảng (tbody) và tiêu đề cột (thead: nút sắp xếp là chính cái bảng).
JS_DEM = """(sel) => {
  const vis = e => e.checkVisibility({checkVisibilityCSS: true, contentVisibilityAuto: true});
  const root = typeof sel === 'string' ? document.querySelector(sel) : sel;
  const q = 'button, select, input:not([type=hidden]), textarea, summary, a[href]';
  return Array.from(root.querySelectorAll(q)).filter(e => vis(e) && !e.disabled
    && !e.closest('tbody') && !e.closest('thead')).map(e => e.id || e.tagName);
}"""
JS_VANG = """(sel) => Array.from(document.querySelector(sel).querySelectorAll('.btn-primary'))
  .filter(e => e.checkVisibility({checkVisibilityCSS: true})).map(e => e.id)"""
JS_DO = """(sel) => Array.from(document.querySelector(sel).querySelectorAll('.btn-danger'))
  .filter(e => e.checkVisibility({checkVisibilityCSS: true})).map(e => e.id)"""
JS_CHU = "(sel) => document.querySelector(sel).innerText"


def dem(page, sel):
    return page.evaluate(JS_DEM, sel)


@pytest.fixture
def mo_ux5a():
    """mo_ux5a(vai) -> (page, api, loi); vai = "quan_tri" (không tài khoản) hoặc "giao_vien"."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def mo(vai="quan_tri", tab="results"):
        tmp = tempfile.mkdtemp()
        goc, xuat = os.path.join(tmp, "g"), os.path.join(tmp, "x")
        os.makedirs(goc)
        os.makedirs(xuat)
        slug = ws.tao(goc, "Truong hoc", None)
        api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=xuat, thu_muc_goc_ws=goc, ws_da_chon=True)
        with open(SO_120, "rb") as f:
            assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
        for i in range(1, 121):
            assert api.set_student_class("HS%03d" % i, "10A%d" % (1 + i % 4))["ok"]
        assert api.run_pipeline(seed=42)["ok"]
        if vai == "giao_vien":
            assert api.tao_tai_khoan("qt", MK, "quan_tri")["ok"]
            assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
            api.dang_xuat()
            assert api.dang_nhap("gv1", MK)["ok"]
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(viewport={"width": 1280, "height": 900}, bypass_csp=True)
        page.set_default_timeout(10000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.wait_for_function("document.body.dataset.vai !== undefined")
        page.locator('.nav-item[data-tab="%s"]' % tab).click()
        page.wait_for_selector("#view-%s" % tab, state="visible")
        page.wait_for_timeout(900)
        return page, api, loi

    yield mo
    for br, pw in dong:
        br.close()
        pw.stop()
