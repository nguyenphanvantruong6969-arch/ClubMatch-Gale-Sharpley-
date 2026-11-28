"""DK8-L1 (Playwright + Chromium): khung cổng giống bản mẫu v8 — thanh trên dính (thương hiệu + chip «Giai đoạn k/6 · tên» + vai trò +
Đăng xuất), trang đầu = ba thẻ vai trò lớn (mục đích, chip trạng thái, dòng đếm), thẻ đăng nhập hẹp. Một fixture trang dùng chung.
Dữ liệu MÔ PHỎNG."""
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
    for ten, sc in (("P1", 40), ("P2", 30)):
        ok(api.dk_phong_luu(qt, ten, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    han = (datetime.datetime.now() + datetime.timedelta(days=2, hours=3)).strftime("%Y-%m-%dT%H:%M")
    ok(api.dk_dat_han(qt, "gv_dang_ky", han))
    ok(api.dk_gv_tu_dang_ky("TRUONG1", "Cô Lan", "7391"))
    ok(api.dk_gv_tu_dang_ky("TRUONG1", "Thầy Minh", "5903"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.url_cong = api, qt, url
        pg.goto(url)
        pg.wait_for_selector("text=Chọn vai trò")
        yield pg
        assert pg.loi == []
        br.close()


def test_a_trang_dau_ba_the_vai_tro_co_chip_va_dong_dem(cong):
    pg = cong
    the = pg.locator(".dk-cua")
    assert the.count() == 3
    ten = [the.nth(i).locator(".dk-cua-nut").inner_text() for i in range(3)]
    assert ten == ["Giáo viên", "Học sinh", "Quản trị"]        # DK8-L6 (Truong, 2026-11-26): giáo viên trước học sinh
    gv, hs, qt = (the.nth(i).inner_text() for i in range(3))
    assert "Chọn CLB theo từng buổi, đăng ký thi" in hs and "Chưa mở" in hs and "0 em đã gửi" in hs
    assert "Đăng ký mở CLB, chọn phòng" in gv and "Đang mở · còn 2 ngày" in gv and "2 giáo viên đã đăng ký tài khoản" in gv
    assert "Phòng, danh sách, duyệt CLB, nhập điểm, xuất sổ" in qt and "Cần mật khẩu" in qt
    assert the.nth(1).locator(".dk-chip.wait").count() == 1 and the.nth(0).locator(".dk-chip.on").count() == 1
    assert pg.locator("h1").inner_text() == "Đăng ký câu lạc bộ"
    assert pg.get_by_role("button", name="Quản trị", exact=True).count() == 1             # nhãn nút giữ nguyên (test cũ dùng)


def test_b_bam_vao_bat_ky_cho_nao_cua_the_deu_di_tiep(cong):
    pg = cong
    pg.locator(".dk-cua").nth(0).click(position={"x": 6, "y": 6})                          # góc thẻ, không phải chữ nút
    pg.wait_for_selector("text=Giáo viên đăng nhập")
    assert pg.locator("input[name=ten]").count() == 1


def test_c_chip_doi_theo_giai_doan(cong):
    pg = cong
    ok(pg.api.dk_chuyen_giai_doan(pg.qt, "duyet"))
    pg.reload()
    pg.wait_for_selector("text=Chọn vai trò")
    the = pg.locator(".dk-cua")
    assert "Đã đóng" in the.nth(0).inner_text() and "Chưa mở" in the.nth(1).inner_text()
    assert the.nth(0).locator(".dk-chip.off").count() == 1


def test_d_thanh_tren_dinh_co_thuong_hieu_va_chip_giai_doan(cong):
    pg = cong
    dau = pg.locator("header.dk-dau")
    assert dau.count() == 1
    assert dau.locator(".dk-thuong-hieu").inner_text() == "Cổng đăng ký CLB"
    assert dau.locator(".dk-chip").inner_text() == "Giai đoạn 2/6 · Giáo viên đăng ký"
    assert dau.evaluate("e => getComputedStyle(e).position") == "sticky"
    assert pg.locator("#dkVePhanMem").count() == 0 and dau.get_by_role("button").count() == 0     # chưa đăng nhập: không nút, không lối ra
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    pg.fill("input[name=ma]", "matkhau")
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
    dau = pg.locator("header.dk-dau")
    assert dau.count() == 1 and dau.inner_text().count("Quản trị") == 1                     # không lặp nhãn vai trò
    assert dau.locator(".dk-thuong-hieu").count() == 1 and dau.locator(".dk-chip").count() == 0       # VG3: màn quản trị đã có thanh sáu bước, thanh trên không lặp tên giai đoạn
    assert dau.get_by_role("button", name="Đăng xuất").count() == 1 and dau.locator("#dkVePhanMem").count() == 1
    pg.mouse.wheel(0, 600)
    assert dau.bounding_box()["y"] == 0                                                     # cuộn rồi thanh vẫn dính ở trên cùng


def test_e_dang_nhap_the_hep_nut_vang_ve_trang_dau(cong):
    pg = cong
    for ten, tieu_de in (("Quản trị", "Quản trị đăng nhập"), ("Giáo viên", "Giáo viên đăng nhập"), ("Học sinh", "Học sinh đăng nhập")):
        pg.get_by_role("button", name=ten, exact=True).click()
        pg.wait_for_selector("text=" + tieu_de)
        the = pg.locator(".dk-hep .dk-khung")
        hop, nut = the.bounding_box(), the.get_by_role("button", name="Đăng nhập").bounding_box()
        assert 300 <= hop["width"] <= 481 and hop["x"] > 200                                 # thẻ hẹp, giữa trang
        assert nut["width"] >= hop["width"] - 2 * 18 - 2                                     # nút vàng rộng hết thẻ
        ve = pg.get_by_role("button", name="← Về trang chọn vai trò").bounding_box()
        assert ve["y"] + ve["height"] <= hop["y"] + 1                                        # «← Về trang chọn vai trò» NẰM TRÊN thẻ
        assert the.get_by_role("button", name="Đăng nhập").evaluate("e => e.classList.contains('btn-primary')")
        pg.get_by_role("button", name="← Về trang chọn vai trò").click()
        pg.wait_for_selector("text=Chọn vai trò")
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    nut = pg.get_by_role("button", name="Đăng nhập").bounding_box()
    goi_y = pg.locator("#dkTuKhoa")
    assert goi_y.inner_text() == "Tự khoá sau 2 phút không thao tác." and goi_y.bounding_box()["y"] > nut["y"]   # dòng gợi ý dưới nút
