"""DK8-L2 (Playwright + Chromium): màn quản trị giống bản mẫu v8 — thanh thẻ nằm TRÊN, «Việc bây giờ» = MỘT thẻ giai đoạn (thanh sáu bước
bên trong, tiêu đề, một dòng giải thích, dòng đếm, dòng hạn chót + nút bên phải) rồi các thẻ nội dung; Cài đặt chia thẻ hai cột; «Thêm ▾».
Một fixture trang dùng chung cho mọi giai đoạn. Dữ liệu MÔ PHỎNG."""
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
TEN_GD = {"chuan_bi": "Chuẩn bị", "gv_dang_ky": "Giáo viên đăng ký", "duyet": "Duyệt CLB", "hs_dang_ky": "Học sinh đăng ký",
          "nhap_diem": "Nhập điểm", "xuat": "Xuất"}


def _dung(tmp_path, gd):
    api = PipelineAPI(str(tmp_path / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for ten, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, ten, sc))
    if gd == "chuan_bi":
        return api, qt
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    han = (datetime.datetime.now() + datetime.timedelta(days=2, hours=3)).strftime("%Y-%m-%dT%H:%M")
    ok(api.dk_dat_han(qt, "gv_dang_ky", han))
    if gd in ("gv_dang_ky", "duyet"):
        pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình"))["da_tao"]
        tk = {x["ten"]: ok(api.dk_dang_nhap("giao_vien", x["ten"], x["pin"]))["token"] for x in pin}
        for gv, ten, loai, ph, kw in (("Cô An", "Tự do 1", "Tự do", 1, {}), ("Thầy Bình", "Cờ vua", "Giới hạn", 2, {"chi_tieu": 10})):
            ok(api.dk_clb_luu(tk[gv], t3._clb(ten=ten, loai=loai, phong_id=ph, **kw)))
        if gd == "duyet":
            ok(api.dk_chuyen_giai_doan(qt, "duyet"))
        return api, qt
    ids = t3._dung_san(api, qt)                                   # hs_dang_ky: 3 CLB đã duyệt (Tự do, Giới hạn, Tuyển chọn), 3 học sinh
    h1 = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    ok(api.dk_hs_luu(h1, [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Cờ vua"]}]))
    if gd in ("nhap_diem", "xuat"):
        ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
        ok(api.dk_diem_dat(qt, "H1", ids["Robot"], "8"))
    if gd == "xuat":
        ok(api.dk_chot_va_xep(qt, 7))
    return api, qt


@pytest.fixture()
def cong(tmp_path):
    """Trả hàm `vao(gd)`: dựng cổng tới giai đoạn `gd`, mở trình duyệt, đăng nhập quản trị, trả trang."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        trang = []

        def vao(gd):
            thu_muc = tmp_path / ("c%d" % len(trang))
            thu_muc.mkdir()
            api, qt = _dung(thu_muc, gd)
            url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
            pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
            pg.loi = []
            pg.on("pageerror", lambda e: pg.loi.append(str(e)))
            pg.api, pg.qt = api, qt
            pg.goto(url)
            pg.get_by_role("button", name="Quản trị", exact=True).click()
            pg.fill("input[name=ma]", "matkhau")
            pg.get_by_role("button", name="Đăng nhập").click()
            pg.wait_for_selector("text=Quản trị · " + TEN_GD[gd])
            pg.wait_for_timeout(500)
            trang.append(pg)
            return pg
        yield vao
        assert all(p.loi == [] for p in trang)
        br.close()


def _y(el):
    return el.bounding_box()["y"]


def _x(el):
    return el.bounding_box()["x"]


def test_a_thanh_the_tren_the_giai_doan_mot_the_noi(cong):
    pg = cong("gv_dang_ky")
    the = pg.locator("section.dk-gd-the")
    assert the.count() == 1
    assert _y(pg.locator("nav.dk-the")) < _y(the)                                  # thanh thẻ nằm TRÊN thẻ giai đoạn
    assert the.locator("ol.dk-gd li").count() == 6 and pg.locator("ol.dk-gd").count() == 1   # thanh sáu bước nằm TRONG thẻ
    assert the.locator("h2").inner_text() == "Giáo viên đang đăng ký"
    assert "Thầy cô tự tạo tài khoản bằng mã trường" in the.inner_text()
    assert the.locator(".dk-dem").inner_text() == "2 giáo viên · 2 CLB đã gửi"
    han = the.locator("#dkHan")
    assert "Hạn chót" in han.inner_text() and "còn 2 ngày" in han.inner_text() and "Đến hạn tự đóng." in han.inner_text()
    ngay, dong = the.get_by_role("button", name="+1 ngày"), the.get_by_role("button", name="Đóng ngay")
    assert _x(ngay) > _x(han) + 200 and _x(dong) > _x(ngay)                       # «Gia hạn» và «Đóng ngay» ở bên PHẢI dòng hạn chót
    assert abs(_y(dong) - _y(han)) < 40 and the.get_by_role("button", name="+1 giờ").count() == 1
    assert pg.locator("#dkApp .btn-primary:visible").count() == 1                  # một nút vàng: «Đóng đăng ký giáo viên»
    assert pg.get_by_role("button", name="Đóng đăng ký giáo viên").count() == 1


def test_b_the_thu_hai_clb_da_gui(cong):
    pg = cong("gv_dang_ky")
    the2 = pg.locator("section.dk-khung", has=pg.locator("h3", has_text="CLB đã gửi"))
    assert the2.count() == 1 and _y(the2) > _y(pg.locator("section.dk-gd-the"))
    cot = [x.strip() for x in the2.locator("thead th").all_inner_texts()]
    assert cot == ["CLB", "Giáo viên", "Buổi", "Phòng", "Nhận"]
    assert the2.locator("tbody tr").count() == 2 and "Cờ vua" in the2.inner_text() and "Mọi em" in the2.inner_text()
    assert pg.locator("textarea").count() == 1 and pg.get_by_role("button", name="Tạo tài khoản giáo viên").count() == 1   # giữ nơi tạo hộ GV


def test_c_the_khac_khong_co_thanh_sau_buoc_va_them_co_mui_ten(cong):
    pg = cong("gv_dang_ky")
    assert pg.get_by_role("tab", name="Thêm ▾").count() == 1
    for ten in ("Danh sách", "Cài đặt", "Thêm"):
        pg.get_by_role("tab", name=ten).click()
        pg.wait_for_timeout(400)
        assert pg.locator("ol.dk-gd").count() == 0
        assert pg.locator("#dkApp section.dk-khung").count() >= 1                  # nội dung nằm trong thẻ
    pg.get_by_role("tab", name="Cài đặt").click()
    pg.wait_for_timeout(400)
    the = pg.locator("#dkApp .dk-luoi2 > section.dk-khung")
    assert the.count() >= 3 and abs(_y(the.nth(0)) - _y(the.nth(1))) < 2 and _x(the.nth(1)) > _x(the.nth(0)) + 200   # lưới hai cột
    pg.get_by_role("tab", name="Thêm").click()
    pg.wait_for_timeout(400)
    assert pg.locator("#dkSaoLuu").count() == 1 and pg.get_by_role("button", name="Lùi về giai đoạn «Chuẩn bị»").count() == 1


def test_d_chuan_bi_danh_sach_kiem(cong):
    pg = cong("chuan_bi")
    the = pg.locator("section.dk-gd-the")
    assert the.locator("h2").inner_text() == "Chuẩn bị" and "rồi mở cho giáo viên đăng ký CLB" in the.inner_text()
    kiem = the.locator("ul.dk-kiem li")
    assert kiem.count() == 3
    txt = [x.inner_text() for x in kiem.all()]
    assert "3 phòng · tổng sức chứa 90" in txt[0] and "0 học sinh" in txt[1] and "Mã trường cho giáo viên" in txt[2] and "TRUONG1" in txt[2]
    assert kiem.nth(0).locator(".dk-tick.on").count() == 1 and kiem.nth(1).locator(".dk-tick.on").count() == 0
    assert pg.locator("#dkChuaDi").count() == 1                                    # lý do chưa mở được vẫn hiện


def test_e_duyet_dem_theo_trang_thai(cong):
    pg = cong("duyet")
    the = pg.locator("section.dk-gd-the")
    assert the.locator("h2").inner_text() == "Duyệt CLB"
    assert the.locator(".dk-dem").inner_text() == "2 chờ duyệt · 0 đã duyệt · 0 từ chối"
    assert pg.locator("section.dk-khung table").count() >= 1 and pg.get_by_role("button", name="Duyệt", exact=True).count() == 2


def test_f_hoc_sinh_dang_ky_hai_the_canh_nhau(cong):
    pg = cong("hs_dang_ky")
    the = pg.locator("section.dk-gd-the")
    assert the.locator("h2").inner_text() == "Học sinh đang đăng ký" and the.locator(".dk-dem").inner_text() == "1/3 em đã gửi"
    tien, cau = pg.locator("section.dk-khung", has=pg.locator("h3", has_text="Tiến độ theo lớp")), pg.locator("#dkNhuCau")
    assert tien.count() == 1 and abs(_y(tien) - _y(cau)) < 2 and _x(cau) > _x(tien) + 200
    assert pg.locator("#dkHan").count() == 1 and pg.locator("progress.dk-tien").count() >= 1
    assert pg.locator("#dkApp .btn-primary:visible").count() == 1


def test_g_nhap_diem_va_xuat(cong):
    pg = cong("nhap_diem")
    the = pg.locator("section.dk-gd-the")
    assert the.locator("h2").inner_text() == "Nhập điểm" and the.locator(".dk-dem").inner_text() == "1/1 bài đã có điểm"
    assert pg.locator("input.dk-diem").count() == 1 and pg.locator("#dkChot").count() == 1
    pg2 = cong("xuat")
    the = pg2.locator("section.dk-gd-the")
    assert the.locator("h2").inner_text().startswith("Xuất Sổ nhập") and "CLB" in the.locator(".dk-dem").inner_text()
    assert pg2.locator("#dkXemTruoc").count() == 1 and pg2.locator("#dkKetQua").count() == 1
