"""VG2-L4 (#27, Chromium thật): cổng chưa mở cho học sinh -> ô và nút đăng nhập học sinh bị KHOÁ (không ẩn), có câu nói rõ.
Mở rồi thì đăng nhập bình thường. Dữ liệu MÔ PHỎNG."""
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


def test_form_hoc_sinh_khoa_khi_chua_mo_va_mo_khi_da_mo(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TRG1", ["T2"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    _ok(api.dk_phong_luu(qt, "P1", 40))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        pg = br.new_page(bypass_csp=True, viewport={"width": 1100, "height": 900})
        loi = []
        pg.on("pageerror", lambda e: loi.append(str(e)))
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)

        def vao():
            pg.goto(url)
            pg.get_by_role("button", name="Học sinh", exact=True).click()
            pg.wait_for_selector("input[name=ma]")

        vao()
        assert pg.locator("#dkHsChuaMo").count() == 1
        assert pg.locator("input[name=ten]").is_disabled() and pg.get_by_role("button", name="Đăng nhập").is_disabled()
        # mở cho học sinh: cần một CLB Tự do đã duyệt
        pin = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"]}
        _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
        t = _ok(api.dk_dang_nhap("giao_vien", "Cô An", pin["Cô An"]))["token"]
        cid = _ok(api.dk_clb_luu(t, {"ten": "Tự do", "buoi": "T2", "loai": "Tự do", "phong_id": 1, "khoi_tu": 9, "khoi_den": 12}))["clb_id"]
        _ok(api.dk_chuyen_giai_doan(qt, "duyet"))
        _ok(api.dk_clb_duyet(qt, cid, "duyet"))
        _ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
        vao()
        assert pg.locator("#dkHsChuaMo").count() == 0
        assert not pg.locator("input[name=ten]").is_disabled() and not pg.get_by_role("button", name="Đăng nhập").is_disabled()
        br.close()
    assert not loi, loi
