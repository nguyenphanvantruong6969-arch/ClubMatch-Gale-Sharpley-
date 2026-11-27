"""DK4-L0b (Playwright + Chromium): học sinh bị khoá hiện trong danh sách quản trị, nút "Mở khoá" gỡ khoá. Dữ liệu MÔ PHỎNG."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ok(r):
    assert r["ok"], r
    return r["data"]


def test_nut_mo_khoa_trong_danh_sach(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TRU1", ["T2"], [6, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    pin = _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))["pin"][0]["pin"]
    for _ in range(5):
        api.dk_dang_nhap("hoc_sinh", "H1", "0000")
    assert api.dk_dang_nhap("hoc_sinh", "H1", pin)["errors"][0]["code"] == "dk_tam_khoa"
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        pg = br.new_page(bypass_csp=True, viewport={"width": 1100, "height": 900})
        loi = []
        pg.on("pageerror", lambda e: loi.append(str(e)))
        pg.goto(browser_host.serve(api, GOC, "dang_ky.html", open_browser=False))
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", "matkhau")
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.get_by_role("tab", name="Danh sách").click()
        pg.locator("summary", has_text="Học sinh").click()
        pg.wait_for_selector("text=Đang khoá")
        pg.get_by_role("button", name="Mở khoá").click()
        for _ in range(50):                                   # chờ cuộc gọi mở khoá tới được phần mềm
            if {x["ma"]: x for x in _ok(api.dk_hs_danh_sach(qt))}["H1"]["bi_khoa"] is False:
                break
            pg.wait_for_timeout(100)
        pg.locator("summary", has_text="Học sinh").click()
        assert pg.locator("text=Đang khoá").count() == 0
        br.close()
    assert _ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]
    assert loi == []
