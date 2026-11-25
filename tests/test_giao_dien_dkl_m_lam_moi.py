"""DKL-M (Playwright + Chromium): màn quản trị tự cập nhật trong vài giây khi dữ liệu đổi (hỏi dấu vân tay mỗi 5 giây,
chỉ vẽ lại khi đổi), ở giai đoạn Giáo viên đăng ký / Duyệt CLB / Học sinh đăng ký. Đồng hồ giả. Dữ liệu MÔ PHỎNG."""
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


@pytest.fixture()
def cong(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TR1", ["T2", "T3"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t, sc in (("P1", 40), ("P2", 30)):
        _ok(api.dk_phong_luu(qt, t, sc))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    gv = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))["da_tao"]}
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ph = {p["ten"]: p["phong_id"] for p in _ok(api.dk_phong_danh_sach(qt))}
    ids = []
    for ten, nguoi, p in (("Cờ vua", "Cô An", "P1"), ("Bóng rổ", "Cô Bê", "P2")):       # mỗi giáo viên một CLB (luật: một CLB mỗi buổi)
        tk = _ok(api.dk_dang_nhap("giao_vien", nguoi, gv[nguoi]))["token"]
        ids.append(_ok(api.dk_clb_luu(tk, {"ten": ten, "buoi": "T2", "loai": "Tự do", "phong_id": ph[p], "khoi_tu": 9, "khoi_den": 12,
                                           "mo_ta": "x", "yeu_cau": "Không"}))["clb_id"])
    _ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.ids, pg.dia_chi = api, qt, ids, url
        pg.clock.install()
        pg.goto(url)
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", "matkhau")
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.wait_for_selector("text=Quản trị · Duyệt CLB")
        pg.wait_for_selector("tr:has-text('Cờ vua')")
        yield pg
        br.close()


def test_1_du_lieu_doi_thi_man_duyet_tu_cap_nhat_trong_vai_giay(cong):
    pg = cong
    assert pg.locator("tr:has-text('Cờ vua')").inner_text().count("Chờ duyệt") == 1
    _ok(pg.api.dk_clb_duyet(pg.qt, pg.ids[0], "duyet"))                          # đổi dữ liệu từ nơi khác
    pg.wait_for_timeout(300)                                                     # để lần lấy dấu vân tay đầu xong
    pg.clock.fast_forward(6_000)                                                 # một vòng hỏi 5 giây
    pg.wait_for_selector("tr:has-text('Cờ vua') >> text=Đã duyệt", timeout=5000)
    assert not pg.loi, pg.loi


def test_2_khong_co_gi_doi_thi_khong_ve_lai(cong):
    pg = cong
    pg.wait_for_timeout(300)
    pg.evaluate("window.__moc = document.querySelector('.dk-noidung')")
    pg.clock.fast_forward(30_000)                                                # sáu vòng hỏi, dữ liệu không đổi
    pg.wait_for_timeout(500)
    assert pg.evaluate("document.querySelector('.dk-noidung') === window.__moc")
    assert not pg.loi, pg.loi


def test_3_dang_go_thi_khong_ve_de_roi_ve_sau_khi_roi_o_nhap(cong):
    pg = cong
    pg.wait_for_timeout(300)
    pg.evaluate("window.__moc = document.querySelector('.dk-noidung')")
    pg.evaluate("document.querySelector('.dk-noidung input, .dk-noidung select').focus()")
    _ok(pg.api.dk_clb_duyet(pg.qt, pg.ids[1], "duyet"))
    pg.clock.fast_forward(11_000)
    pg.wait_for_timeout(500)
    assert pg.evaluate("document.querySelector('.dk-noidung') === window.__moc")        # đang ở ô nhập: giữ nguyên
    pg.evaluate("document.activeElement.blur()")
    pg.clock.fast_forward(6_000)
    pg.wait_for_selector("tr:has-text('Bóng rổ') >> text=Đã duyệt", timeout=5000)
    assert not pg.loi, pg.loi
