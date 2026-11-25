"""DK4-L5 (Playwright + Chromium): cổng đăng ký nằm TRONG phần mềm. Dữ liệu MÔ PHỎNG.

Thanh bên của phần mềm có "Đăng ký CLB" mở dang_ky.html; quản trị (chỉ quản trị) có lối về phần mềm; sau
"Chốt và xếp", "Xem kết quả trong phần mềm" mở index.html ở thẻ Kết quả với đúng lần chạy vừa xếp.
"""
import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402
from test_dk4_chot_va_xep import _dang_ky_va_cham, ok  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_phan_mem_va_cong_dang_ky_mo_qua_lai(tmp_path):
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
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1280, "height": 900})
        loi = []
        pg.on("pageerror", lambda e: loi.append(str(e)))
        pg.goto(url)
        pg.wait_for_selector("#navDangKy")
        assert pg.inner_text("#navDangKy").strip() == "Đăng ký CLB"
        pg.click("#navDangKy")                                             # phần mềm -> cổng
        pg.wait_for_url(re.compile(r"/dang_ky\.html(\?|$)"))
        pg.get_by_role("button", name="Quản trị", exact=True).wait_for()
        assert pg.locator("#dkVePhanMem").count() == 0                     # trang chọn vai trò: không có lối ra
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", "matkhau")
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.wait_for_selector("#dkVePhanMem")                               # quản trị: có lối về phần mềm
        pg.click("#dkChot")
        pg.wait_for_selector("#dkXemKq")
        assert pg.locator("#dkApp .btn-primary:visible").count() == 1      # vẫn một nút vàng
        pg.click("#dkXemKq")                                               # cổng -> phần mềm, thẻ Kết quả
        pg.wait_for_url(re.compile(r"/index\.html.*#ket-qua$"))
        pg.wait_for_selector(".nav-item[data-tab=results].is-active")
        pg.click("#navDangKy")
        pg.wait_for_url(re.compile(r"/dang_ky\.html(\?|$)"))
        assert not loi, loi
        br.close()
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 1
        assert cur.execute("SELECT COUNT(*) FROM match_results WHERE club_id IS NOT NULL").fetchone()[0] > 0
