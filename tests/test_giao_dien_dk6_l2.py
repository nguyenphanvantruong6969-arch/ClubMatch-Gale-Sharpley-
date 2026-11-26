"""DK6-L2 (Playwright + Chromium): đổi mật khẩu quản trị ở «Cài đặt» và «Danh sách» chia thẻ gấp theo khối (trạng thái mở giữ qua tự làm mới).
Đồng hồ giả. Dữ liệu MÔ PHỎNG."""
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
    _ok(api.dk_khoi_tao("matkhau", "TR1", ["T2", "T3"], [6, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    _ok(api.dk_phong_luu(qt, "P1", 40))
    _ok(api.dk_hs_nap_danh_sach(qt, "H10a\tAn\t10A1\nH10b\tBình\t10A2\nH11a\tChi\t11A1\nH12a\tDũng\t12A1\nH12b\tEm\t12A2"))
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt = api, qt
        pg.clock.install()
        pg.goto(url)
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", "matkhau")
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
        pg.wait_for_timeout(300)
        yield pg
        br.close()


def _the(pg, ten):
    pg.locator("nav.dk-the button", has_text=ten).click()
    pg.wait_for_timeout(400)


def test_1_doi_mat_khau_sai_cu_thong_bao_loi_khong_doi(cong):
    pg = cong
    _the(pg, "Cài đặt")
    pg.fill("input[name=mk_cu]", "sai-roi")
    pg.fill("input[name=mk_moi]", "bimat-moi-9")
    pg.fill("input[name=mk_lai]", "bimat-moi-9")
    pg.click("#dkDoiMk")
    pg.wait_for_selector("#dkThongBao:has-text('Mật khẩu hiện tại không đúng')")
    _ok(pg.api.dk_dang_nhap("quan_tri", "", "matkhau"))                            # mật khẩu cũ vẫn dùng được
    assert not pg.loi, pg.loi


def test_2_nhap_lai_khong_khop_bi_chan_o_may_khach(cong):
    pg = cong
    _the(pg, "Cài đặt")
    pg.evaluate("""() => { window.__n = 0; const g = window.RBDA.callApi;
        window.RBDA.callApi = function (ten, ...a) { if (ten === 'dk_doi_mat_khau') window.__n++; return g.call(this, ten, ...a); }; }""")
    pg.fill("input[name=mk_cu]", "matkhau")
    pg.fill("input[name=mk_moi]", "bimat-moi-9")
    pg.fill("input[name=mk_lai]", "khac-di-nhe")
    pg.click("#dkDoiMk")
    pg.wait_for_selector("#dkThongBao:has-text('không giống nhau')")
    assert pg.evaluate("window.__n") == 0
    assert not pg.loi, pg.loi


def test_3_doi_thanh_cong_cu_het_hieu_luc_moi_dung_duoc(cong):
    pg = cong
    _the(pg, "Cài đặt")
    pg.fill("input[name=mk_cu]", "matkhau")
    pg.fill("input[name=mk_moi]", "bimat-moi-9")
    pg.fill("input[name=mk_lai]", "bimat-moi-9")
    pg.click("#dkDoiMk")
    pg.wait_for_selector("#dkThongBao:has-text('Đã đổi mật khẩu')")
    assert _fail_dn(pg.api, "matkhau")                                              # mật khẩu cũ hết hiệu lực
    _ok(pg.api.dk_dang_nhap("quan_tri", "", "bimat-moi-9"))
    assert pg.locator("input[name=mk_moi]").input_value() == ""                     # ô đã xoá sạch
    assert _fail_dn(pg.api, "matkhau")
    assert pg.api.dk_phong_danh_sach(pg.qt)["ok"] is False                           # phiên quản trị KHÁC (token của test) bị huỷ
    _the(pg, "Danh sách")
    assert pg.locator("summary", has_text="Phòng (1)").count() == 1                  # phiên của trình duyệt đổi mật khẩu còn sống
    assert not pg.loi, pg.loi


def _fail_dn(api, mk):
    return api.dk_dang_nhap("quan_tri", "", mk)["ok"] is False


def test_4_danh_sach_chia_khoi_dung_so_lieu(cong):
    pg = cong
    _the(pg, "Danh sách")
    pg.locator("summary", has_text="Học sinh (5)").click()
    tieu_de = pg.locator("details details > summary").all_inner_texts()
    assert tieu_de == ["Khối 10 · 2 HS · 0 đã nộp", "Khối 11 · 1 HS · 0 đã nộp", "Khối 12 · 2 HS · 0 đã nộp"]
    assert not pg.loi, pg.loi


def test_5_khoi_dang_mo_van_mo_sau_tu_lam_moi(cong):
    pg = cong
    _the(pg, "Danh sách")
    pg.locator("summary", has_text="Học sinh (5)").click()
    pg.locator("summary", has_text="Khối 11").click()
    pg.evaluate("document.activeElement && document.activeElement.blur()")
    pg.evaluate("window.__moc = document.querySelector('.dk-noidung')")
    _ok(pg.api.dk_gv_tu_dang_ky("TR1", "Cô Tự", "1234"))                           # dữ liệu đổi từ nơi khác
    pg.wait_for_timeout(300)
    pg.clock.fast_forward(11_000)
    pg.wait_for_timeout(1000)
    assert pg.evaluate("document.querySelector('.dk-noidung') !== window.__moc"), "chưa vẽ lại nên chưa kiểm được gì"
    assert pg.locator("summary", has_text="Học sinh (5)").evaluate("e => e.parentElement.open") is True
    k = pg.locator("summary", has_text="Khối 11").evaluate("e => e.parentElement.open")
    k10 = pg.locator("summary", has_text="Khối 10").evaluate("e => e.parentElement.open")
    assert k is True and k10 is False
    assert not pg.loi, pg.loi
