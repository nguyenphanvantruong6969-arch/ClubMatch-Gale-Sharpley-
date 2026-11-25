"""DK4-L4 (Playwright + Chromium): quản trị bấm "Chốt và xếp" trên dang_ky.html. Dữ liệu MÔ PHỎNG."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402
from test_dk4_chot_va_xep import _dang_ky_va_cham, ok  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_chot_va_xep_qua_giao_dien(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, t, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    _dang_ky_va_cham(api, qt)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1100, "height": 900})
        loi = []
        pg.on("pageerror", lambda e: loi.append(str(e)))
        pg.goto(url)
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", "matkhau")
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.wait_for_selector("text=Quản trị · Nhập điểm")
        assert pg.locator("#dkApp .btn-primary:visible").count() == 1
        pg.click("#dkChot")
        pg.wait_for_selector("#dkKetQua")
        assert pg.locator("#dkApp .btn-primary:visible").count() == 1       # chỉ "Xuất Sổ nhập"
        assert "giữ chỗ và huy chương" in pg.inner_text("#dkLuuY")           # báo luật vừa được bật
        assert "Đã xếp" in pg.inner_text("#dkKetQua")
        assert pg.locator("#dkKetQua tbody tr").count() >= 1               # có buổi T2
        assert not loi, loi
        br.close()
    assert ok(api.dk_ket_qua_xep(qt))["da_xep"]
