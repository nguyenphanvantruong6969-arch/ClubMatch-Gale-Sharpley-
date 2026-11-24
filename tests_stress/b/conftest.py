"""ST-B shared fixtures: real Chromium (Playwright) driving browser_host.py. SIMULATED data only.

One fixture `mo` -> open(...) returns a Ui object with .page, .api, .loi (console errors + page errors +
unhandled rejections + failed API calls). Every test must end with `ui.kiem_loi()`.
"""
import os
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "tests"))

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

SO_150 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DOI_CHE_DO_150HS.xlsx")
ANH = os.path.join(GOC, "docs", "phien", "anh_st_b")

HOOK = """
window.__loi = [];
window.addEventListener('unhandledrejection', e => window.__loi.push('UNHANDLED: ' + (e.reason && (e.reason.stack || e.reason.message) || e.reason)));
window.addEventListener('error', e => window.__loi.push('ERROR: ' + e.message));
"""


class Ui:
    def __init__(self, page, api, goc, tmp, loi):
        self.page, self.api, self.goc, self.tmp, self.loi = page, api, goc, tmp, loi

    def kiem_loi(self, bo_qua=()):
        try:
            them = self.page.evaluate("window.__loi || []")
        except Exception:
            them = []
        tat_ca = [x for x in list(self.loi) + list(them) if not any(b in x for b in bo_qua)]
        assert not tat_ca, tat_ca

    def tab(self, ten):
        self.page.locator('.nav-item[data-tab="%s"]' % ten).click()
        self.page.wait_for_selector("#view-%s.is-active" % ten)

    def anh(self, ten):
        os.makedirs(ANH, exist_ok=True)
        p = os.path.join(ANH, ten + ".png")
        self.page.screenshot(path=p)
        return p


@pytest.fixture(scope="session")
def trinh_duyet():
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    yield br
    br.close()
    pw.stop()


@pytest.fixture
def mo(trinh_duyet, tmp_path, monkeypatch):
    """open(ws_ten='Trường học', so_nhap=None, viewport=None) -> Ui. so_nhap: 'api' = import_so_nhap truoc khi mo."""
    monkeypatch.setenv("RBDA_THU_MUC_TAI_VE", str(tmp_path / "TaiXuong"))
    (tmp_path / "TaiXuong").mkdir(exist_ok=True)
    mo_pages = []

    def _mo(ten_ws="Trường học", viewport=None, che_do_ws=True, locale=None):
        goc = tmp_path / "goc"
        goc.mkdir(exist_ok=True)
        xuat = tmp_path / "xuat"
        xuat.mkdir(exist_ok=True)
        slug = ws.tao(str(goc), ten_ws, None)
        api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat),
                          thu_muc_goc_ws=str(goc), ws_da_chon=True)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        ctx = trinh_duyet.new_context(viewport=viewport or {"width": 1366, "height": 800},
                                      bypass_csp=True, accept_downloads=True, device_scale_factor=1,
                                      **({"locale": locale} if locale else {}))
        ctx.add_init_script(HOOK)
        page = ctx.new_page()
        loi = []
        page.on("pageerror", lambda e: loi.append("PAGEERROR: " + str(e)))
        page.on("console", lambda m: loi.append("CONSOLE: " + m.text) if m.type == "error" else None)
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        mo_pages.append(ctx)
        return Ui(page, api, str(goc), tmp_path, loi)

    yield _mo
    for c in mo_pages:
        try:
            c.close()
        except Exception:
            pass
