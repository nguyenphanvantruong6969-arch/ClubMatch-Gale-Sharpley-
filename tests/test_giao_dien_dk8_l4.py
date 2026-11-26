"""DK8-L4 (Playwright + Chromium): cổng ở khổ hẹp 390 px — không cuộn ngang ở các màn chính; vòng focus nhìn thấy và thứ tự Tab hợp lý
ở thẻ vai trò. Dữ liệu MÔ PHỎNG."""
import datetime
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import test_dk3_api as t3  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok = t3.ok


@pytest.fixture()
def cong(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for ten, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, ten, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ok(api.dk_dat_han(qt, "gv_dang_ky", (datetime.datetime.now() + datetime.timedelta(days=2, hours=3)).strftime("%Y-%m-%dT%H:%M")))
    gv = ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]
    tk = ok(api.dk_dang_nhap("giao_vien", "Cô An", gv["pin"]))["token"]
    ok(api.dk_clb_luu(tk, t3._clb(ten="Tự do 1", loai="Tự do", phong_id=1)))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 390, "height": 800})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.gv = api, qt, gv
        pg.goto(url)
        pg.wait_for_selector("text=Chọn vai trò")
        yield pg
        assert pg.loi == []
        br.close()


def _khong_cuon_ngang(pg, man):
    pg.wait_for_timeout(400)
    rong = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    assert rong <= 1, "%s: cuộn ngang %s px" % (man, rong)


def test_a_khong_cuon_ngang_o_cac_man_chinh(cong):
    pg = cong
    _khong_cuon_ngang(pg, "trang đầu")
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    _khong_cuon_ngang(pg, "đăng nhập")
    pg.fill("input[name=ma]", "matkhau")
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
    _khong_cuon_ngang(pg, "quản trị · việc bây giờ")
    for ten in ("Danh sách", "Cài đặt", "Thêm"):
        pg.get_by_role("tab", name=ten).click()
        _khong_cuon_ngang(pg, "quản trị · " + ten)
    pg.get_by_role("button", name="Đăng xuất").click()
    pg.wait_for_selector("text=Chọn vai trò")
    pg.get_by_role("button", name="Giáo viên", exact=True).click()
    pg.fill("input[name=ten]", "Cô An")
    pg.fill("input[name=ma]", pg.gv["pin"])
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=CLB của tôi")
    _khong_cuon_ngang(pg, "giáo viên")


def test_b_tab_di_qua_the_vai_tro_va_co_vong_focus(cong):
    pg = cong
    pg.keyboard.press("Tab")
    ten = pg.evaluate("document.activeElement.textContent")
    assert ten == "Giáo viên"
    vien = pg.evaluate("getComputedStyle(document.activeElement.closest('.dk-cua')).outlineStyle")
    assert vien == "solid"                                                          # vòng focus hiện trên cả thẻ
    pg.keyboard.press("Tab")
    pg.keyboard.press("Tab")
    assert pg.evaluate("document.activeElement.textContent") == "Quản trị"
    pg.keyboard.press("Enter")
    pg.wait_for_selector("text=Quản trị đăng nhập")
