"""UX5B: dựng trang Chromium thật (qua `browser_host`) cho ba thẻ Xếp CLB, Nhập nguyện vọng, Nhập điểm.
Dữ liệu MÔ PHỎNG: sổ 120 học sinh, đã nạp; tuỳ chọn: đã chạy xếp, vai giáo viên, đã chọn một em."""

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
from _ux5a_chung import GOC, JS_DEM, JS_DO, JS_VANG, JS_CHU, MK, SO_120, dem  # noqa: E402,F401


@pytest.fixture
def mo_ux5b():
    """mo_ux5b(vai, tab, nap=True, chay=False, chon_em=None) -> (page, api, loi)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def mo(vai="quan_tri", tab="pipeline", nap=True, chay=False, chon_em=None, rong=1280):
        tmp = tempfile.mkdtemp()
        goc, xuat = os.path.join(tmp, "g"), os.path.join(tmp, "x")
        os.makedirs(goc)
        os.makedirs(xuat)
        slug = ws.tao(goc, "Truong hoc", None)
        api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=xuat, thu_muc_goc_ws=goc, ws_da_chon=True)
        if nap:
            with open(SO_120, "rb") as f:
                assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
            for i in range(1, 121):
                assert api.set_student_class("HS%03d" % i, "10A%d" % (1 + i % 4))["ok"]
        if chay:
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
        page = br.new_page(viewport={"width": rong, "height": 900}, bypass_csp=True)
        page.set_default_timeout(10000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.wait_for_function("document.body.dataset.vai !== undefined")
        if tab != "pipeline":
            page.locator('.nav-item[data-tab="%s"]' % tab).click()
        page.wait_for_selector("#view-%s" % tab, state="visible")
        page.wait_for_timeout(900)
        if chon_em:
            page.fill("#fbSearch", chon_em) if page.locator("#fbSearch").count() else None
        return page, api, loi

    yield mo
    for br, pw in dong:
        br.close()
        pw.stop()
