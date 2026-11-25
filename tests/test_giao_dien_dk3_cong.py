"""DK3-L3 (Playwright + Chromium): cổng đăng ký dang_ky.html — một trang dùng chung cho cả tệp.
Dữ liệu MÔ PHỎNG. Quản trị → giáo viên → học sinh nộp → quản trị xuất Sổ nhập; mỗi khung tối đa một nút vàng."""
import os
import sqlite3

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


@pytest.fixture(scope="module")
def cong(tmp_path_factory):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path_factory.mktemp("dk3") / "app.db"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1100, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.goto(url)
        pg.api, pg.dia_chi = api, url
        yield pg
        br.close()


def _mot_vang(pg):
    assert pg.locator("#dkApp .btn-primary:visible").count() <= 1


def _dang_nhap(pg, vai, ten, ma):
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name={"hoc_sinh": "Học sinh", "giao_vien": "Giáo viên", "quan_tri": "Quản trị"}[vai], exact=True).click()
    if ten is not None:
        pg.fill("input[name=ten]", ten)
    pg.fill("input[name=ma]", ma)
    _mot_vang(pg)
    pg.get_by_role("button", name="Đăng nhập").click()


def test_1_khoi_tao_qua_giao_dien_va_vao_quan_tri(cong):
    pg = cong
    pg.wait_for_selector("input[name=mk]")
    _mot_vang(pg)
    pg.fill("input[name=mk]", "matkhau")
    pg.fill("input[name=ma]", "TR1")
    pg.fill("input[name=buoi]", "T2, T3")
    pg.get_by_role("button", name="Thiết lập cổng").click()
    pg.wait_for_selector("text=Chọn vai trò")
    _dang_nhap(pg, "quan_tri", None, "sai")
    pg.wait_for_selector(".dk-thongbao.la-loi")
    pg.fill("input[name=ma]", "matkhau")
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị · Chuẩn bị")
    _mot_vang(pg)
    assert pg.locator(".dk-the-nut").count() <= 4


def test_2_quan_tri_dung_du_lieu_va_mo_cho_giao_vien(cong):
    pg, api = cong, cong.api
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        _ok(api.dk_phong_luu(qt, t, sc))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1"))
    pg.get_by_role("button", name="Mở đăng ký giáo viên").click()
    pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
    pg.fill("textarea", "Cô An\nCô Bê\nCô Chi")
    pg.get_by_role("button", name="Tạo tài khoản giáo viên").click()
    pg.wait_for_selector("#dkPin table")
    pin = {r.locator("td").nth(0).inner_text(): r.locator("td").nth(1).inner_text() for r in pg.locator("#dkPin tbody tr").all()}
    assert len(pin) == 3
    pg.api_pin = pin
    _mot_vang(pg)


def test_3_giao_vien_dang_ky_clb_ba_buoc(cong):
    pg = cong
    for i, (gv, ten, loai) in enumerate((("Cô An", "Tự do 1", "Tự do"), ("Cô Bê", "Cờ vua", "Giới hạn"), ("Cô Chi", "Robot", "Tuyển chọn"))):
        _dang_nhap(pg, "giao_vien", gv, pg.api_pin[gv])
        pg.wait_for_selector("text=Bước 1/3")
        pg.locator("select").nth(1).select_option(loai)
        pg.locator("select").nth(2).select_option(index=i)
        if loai != "Tự do":
            pg.fill("input[type=number]", "10")
        _mot_vang(pg)
        pg.get_by_role("button", name="Tiếp theo").click()
        pg.fill("input[type=number] >> nth=0", "9")
        pg.fill("input[type=number] >> nth=1", "12")
        if loai == "Tuyển chọn":
            pg.fill("input[type=number] >> nth=2", "6")
        pg.get_by_role("button", name="Tiếp theo").click()
        pg.fill("label:has-text('Tên CLB') input", ten)
        pg.get_by_role("button", name="Gửi duyệt").click()
        pg.wait_for_selector("li:has-text('Chờ duyệt')")
    assert not pg.loi, pg.loi


def test_4_duyet_va_mo_cho_hoc_sinh(cong):
    pg = cong
    _dang_nhap(pg, "quan_tri", None, "matkhau")
    pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
    pg.get_by_role("button", name="Đóng đăng ký giáo viên").click()
    pg.wait_for_selector("text=Quản trị · Duyệt CLB")
    for _ in range(3):
        pg.get_by_role("button", name="Duyệt", exact=True).first.click()
        pg.wait_for_timeout(250)
    _mot_vang(pg)
    pg.get_by_role("button", name="Mở cho học sinh").click()
    pg.wait_for_selector("text=Quản trị · Học sinh đăng ký")


def test_5_hoc_sinh_chon_nop_va_huy_chuong_mac_dinh(cong):
    pg, api = cong, cong.api
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    pin = _ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    _dang_nhap(pg, "hoc_sinh", "H1", pin)
    pg.wait_for_selector("text=Buổi T2")
    # chọn Robot rồi Cờ vua rồi Tự do 1 (nếu cùng buổi T2/T3 thì lọc theo tên)
    for ten in ("Robot", "Cờ vua", "Tự do 1"):
        for _ in range(2):
            dong = pg.locator("ul.dk-ds li", has_text=ten)
            if dong.count():
                dong.first.get_by_role("button", name="+ Thêm").click()
                break
            pg.get_by_role("button", name="Buổi tiếp theo →").click()
    # đảm bảo đã ở buổi cuối rồi nộp
    while pg.get_by_role("button", name="Buổi tiếp theo →").count():
        pg.get_by_role("button", name="Buổi tiếp theo →").click()
    _mot_vang(pg)
    assert pg.locator("#dkApp button:visible, #dkApp select:visible, #dkApp input:visible").count() <= 25
    pg.get_by_role("button", name="Nộp nguyện vọng").click()
    pg.wait_for_selector(".dk-thongbao.la-ok")
    c = sqlite3.connect(api.db_path)
    luu = c.execute("SELECT c.ten, n.huy_chuong FROM dk_nguyen_vong n JOIN dk_clb c USING (clb_id) WHERE student_id='H1'").fetchall()
    c.close()
    assert {t for t, _ in luu} == {"Robot", "Cờ vua", "Tự do 1"}
    assert dict(luu).get("Tự do 1") is None
    assert not pg.loi, pg.loi
