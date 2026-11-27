"""DK6-L1 (Playwright + Chromium): tự làm mới mở rộng sang «Danh sách» và «Việc bây giờ» ở giai đoạn Nhập điểm; Cài đặt / Thêm /
Chuẩn bị / Xuất không bao giờ hỏi dấu vân tay; nhãn «Xếp ngoài nguyện vọng» có chú thích. Đồng hồ giả. Dữ liệu MÔ PHỎNG."""
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


def _vao(tmp_path, giai_doan):
    """Dựng cổng tới `giai_doan` (hs_dang_ky | nhap_diem | xuat) rồi mở màn quản trị. Trả (generator trình duyệt)."""
    api = PipelineAPI(str(tmp_path / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for ten, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, ten, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ids = t3._dung_san(api, qt)                                   # → hs_dang_ky, 3 học sinh, 1 CLB Tuyển chọn (Robot)
    h1 = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    ok(api.dk_hs_luu(h1, [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Cờ vua"]}]))
    h2 = ok(api.dk_dang_nhap("hoc_sinh", "H2", ok(api.dk_hs_dat_lai_pin(qt, "H2"))["pin"]))["token"]
    if giai_doan in ("nhap_diem", "xuat"):
        ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
        ok(api.dk_diem_dat(qt, "H1", ids["Robot"], "8"))
    if giai_doan == "xuat":
        ok(api.dk_chot_va_xep(qt, 7))
    ten_gd = {"hs_dang_ky": "Học sinh đăng ký", "nhap_diem": "Nhập điểm", "xuat": "Xuất"}[giai_doan]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.ids, pg.h2 = api, qt, ids, h2
        pg.clock.install()
        pg.goto(url)
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", "matkhau")
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.wait_for_selector("text=Quản trị · " + ten_gd)
        pg.wait_for_timeout(300)
        yield pg
        br.close()


def _can():
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")


@pytest.fixture()
def cong_diem(tmp_path):
    _can()
    yield from _vao(tmp_path, "nhap_diem")


@pytest.fixture()
def cong_hs(tmp_path):
    _can()
    yield from _vao(tmp_path, "hs_dang_ky")


@pytest.fixture()
def cong_xuat(tmp_path):
    _can()
    yield from _vao(tmp_path, "xuat")


def _the(pg, ten):
    pg.locator("nav.dk-the button", has_text=ten).click()
    pg.wait_for_timeout(300)


def test_a_diem_luu_o_noi_khac_hien_ra_trong_6_giay_o_the_viec(cong_diem):
    pg = cong_diem
    o = pg.locator("input[aria-label='Điểm H1']")
    assert o.input_value() == "8"
    ok(pg.api.dk_diem_dat(pg.qt, "H1", pg.ids["Robot"], "9"))                    # phiên khác lưu điểm
    pg.wait_for_timeout(300)
    pg.clock.fast_forward(6_000)
    pg.wait_for_timeout(1000)                                                    # (đồng hồ giả: wait_for_function dùng rAF nên không dùng ở đây)
    assert pg.locator("input[aria-label='Điểm H1']").input_value() == "9"
    assert not pg.loi, pg.loi


def test_b_hoc_sinh_nop_thi_danh_sach_tu_cap_nhat(cong_hs):
    pg = cong_hs
    _the(pg, "Danh sách")
    pg.locator("summary", has_text="Học sinh").evaluate("e => e.parentElement.open = true")
    pg.locator("summary", has_text="Khối 10").evaluate("e => e.parentElement.open = true")                             # DK6-L2: học sinh chia thẻ gấp theo khối
    assert pg.locator("tr:has-text('H2')").inner_text().count("Chưa") == 1
    ok(pg.api.dk_hs_luu(ok(pg.api.dk_dang_nhap("hoc_sinh", "H2", ok(pg.api.dk_hs_dat_lai_pin(pg.qt, "H2"))["pin"]))["token"],
                        [{"clb_id": pg.ids["Tự do 1"]}]))
    pg.evaluate("document.activeElement && document.activeElement.blur()")
    pg.wait_for_timeout(300)
    pg.clock.fast_forward(11_000)
    pg.wait_for_timeout(1000)
    assert pg.evaluate("[...document.querySelectorAll('tr')].some(t => t.textContent.includes('H2') && t.textContent.includes('Có'))")
    assert not pg.loi, pg.loi


def test_c_dang_go_trong_o_diem_khong_bi_xoa(cong_diem):
    pg = cong_diem
    o = pg.locator("input[aria-label='Điểm H1']")
    o.fill("7")                                                                  # gõ chưa bấm lưu, ô đang focus
    ok(pg.api.dk_diem_dat(pg.qt, "H1", pg.ids["Robot"], "9"))
    pg.clock.fast_forward(12_000)
    pg.wait_for_timeout(600)
    assert o.input_value() == "7"
    pg.evaluate("document.activeElement.blur()")                                  # đã rời ô nhưng chữ chưa lưu: vẫn giữ
    pg.clock.fast_forward(12_000)
    pg.wait_for_timeout(600)
    assert pg.locator("input[aria-label='Điểm H1']").input_value() == "7"
    assert not pg.loi, pg.loi


@pytest.mark.parametrize("the_ten", ["Cài đặt", "Thêm"])
def test_d_cai_dat_va_them_khong_bao_gio_hoi_dau_van_tay(cong_diem, the_ten):
    pg = cong_diem
    _the(pg, the_ten)
    pg.evaluate("""() => { window.__nDau = 0; const g = window.RBDA.callApi;
        window.RBDA.callApi = function (ten, ...a) { if (ten === 'dk_dau_van_tay') window.__nDau++; return g.call(this, ten, ...a); }; }""")
    ok(pg.api.dk_diem_dat(pg.qt, "H1", pg.ids["Robot"], "9"))
    pg.clock.fast_forward(12_000)
    pg.wait_for_timeout(600)
    assert pg.evaluate("window.__nDau") == 0, "tab %s không được tự làm mới" % the_ten
    assert not pg.loi, pg.loi


def test_d2_giai_doan_xuat_khong_hoi_dau_van_tay(cong_xuat):
    pg = cong_xuat
    pg.evaluate("""() => { window.__nDau = 0; const g = window.RBDA.callApi;
        window.RBDA.callApi = function (ten, ...a) { if (ten === 'dk_dau_van_tay') window.__nDau++; return g.call(this, ten, ...a); }; }""")
    pg.clock.fast_forward(12_000)
    pg.wait_for_timeout(600)
    assert pg.evaluate("window.__nDau") == 0
    assert not pg.loi, pg.loi


def test_e_nhan_xep_ngoai_nguyen_vong_co_chu_thich(cong_xuat):
    pg = cong_xuat
    txt = pg.locator("#dkKetQua").inner_text()
    assert "Xếp ngoài nguyện vọng" in txt and "Ngoài nguyện vọng" not in txt.replace("Xếp ngoài nguyện vọng", "")
    tip = pg.locator("#dkKetQua [title]").first.get_attribute("title")
    assert "không vào được CLB nào" in tip and "còn chỗ" in tip
    assert not pg.loi, pg.loi
