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
    pg.get_by_role("tab", name="Danh sách").click()           # DKL-A8: nút chỉ hiện khi đủ phòng + học sinh; vẽ lại màn sau khi dựng bằng API
    pg.get_by_role("tab", name="Việc bây giờ").click()
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
        pg.locator("select").nth(2).select_option(index=0)   # DKL-S9: chỉ hiện phòng còn trống ở buổi đó
        if loai != "Tự do":
            pg.fill("input[type=number]", "10")
        _mot_vang(pg)
        pg.get_by_role("button", name="Tiếp theo").click()
        pg.fill("input[type=number] >> nth=0", "9")
        pg.fill("input[type=number] >> nth=1", "12")
        if loai == "Tuyển chọn":
            pg.fill("input[type=number] >> nth=2", "6")
            pg.fill("label:has-text('Đường dẫn bài thi') input", "https://forms.example/robot")   # DKL-S9: link https bắt buộc
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


def _sang_buoc_cuoi(pg):
    """Đi hết các buổi (rank → medals → tests) cho tới màn "Xem lại và gửi"."""
    for _ in range(12):
        nut = pg.locator("#dkApp .btn-primary:visible")
        if pg.get_by_role("heading", name="Xem lại và gửi").count():
            return
        nut.first.click()


def test_5_hoc_sinh_chon_nop_va_huy_chuong_mac_dinh(cong):
    pg, api = cong, cong.api
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    pin = _ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    _dang_nhap(pg, "hoc_sinh", "H1", pin)
    pg.get_by_role("button", name="Đúng là em", exact=True).click()                  # DKL-G1
    pg.wait_for_selector("text=Buổi T2")
    # thanh bước theo buổi: "Buổi k/N" + 3 bước + "Xem lại và gửi"
    assert pg.locator("ol.dk-buoc li").count() == 5
    assert "Buổi 1/2" in pg.locator("ol.dk-buoc li").first.inner_text()
    _mot_vang(pg)
    for ten in ("Robot", "Cờ vua", "Tự do 1"):                       # thêm CLB ở buổi nào có nó
        for _ in range(2):
            dong = pg.locator("ul.dk-ds li", has_text=ten)
            if dong.count():
                dong.first.get_by_role("button", name="+ Thêm").click()
                break
            pg.get_by_role("button", name="Tiếp: đặt huy chương").click()
            pg.get_by_role("button", name="Tiếp: bài kiểm tra").click()
            pg.locator("#dkApp .btn-primary:visible").first.click()
    _sang_buoc_cuoi(pg)
    _mot_vang(pg)
    pg.get_by_role("button", name="Gửi nguyện vọng").click()
    pg.wait_for_selector(".dk-thongbao.la-ok")
    assert pg.locator("#dkBienNhan").inner_text().startswith("Đã gửi lúc ")
    assert "thứ" in pg.locator("#dkBienNhan").inner_text() or "Chủ nhật" in pg.locator("#dkBienNhan").inner_text()
    c = sqlite3.connect(api.db_path)
    luu = c.execute("SELECT c.ten, n.huy_chuong FROM dk_nguyen_vong n JOIN dk_clb c USING (clb_id) WHERE student_id='H1'").fetchall()
    c.close()
    assert {t for t, _ in luu} == {"Robot", "Cờ vua", "Tự do 1"}
    assert dict(luu).get("Tự do 1") is None
    assert not pg.loi, pg.loi


# ------------------------------------------------------------------ DK4-UI: bố cục và dẫn đường như bản mẫu v8
def _vao_hs(pg, ma="H2"):
    api = pg.api
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    pin = _ok(api.dk_hs_dat_lai_pin(qt, ma))["pin"]
    _dang_nhap(pg, "hoc_sinh", ma, pin)
    pg.get_by_role("button", name="Đúng là em", exact=True).click()                  # DKL-G1
    pg.wait_for_selector("ol.dk-buoc")


def _hop(el):
    return el.bounding_box()


def test_6_hai_cot_o_1366_mot_cot_o_390_khong_tran(cong):
    pg = cong
    pg.set_viewport_size({"width": 1366, "height": 900})
    _vao_hs(pg)
    _mot_vang(pg)
    cac_cot = pg.locator(".dk-chia > section")
    assert cac_cot.count() == 2
    a, b = _hop(cac_cot.nth(0)), _hop(cac_cot.nth(1))
    assert abs(a["y"] - b["y"]) < 4 and a["x"] + a["width"] <= b["x"] + 1       # cạnh nhau
    pg.locator(".dk-the-clb").first.get_by_role("button", name="+ Thêm").click()
    assert pg.locator(".dk-xep li .dk-nv").first.inner_text() == "NV1"
    for ten in ("Lên", "Xuống", "Bỏ"):
        assert pg.locator(".dk-xep li").first.get_by_role("button", name=ten).count() == 1
    pg.set_viewport_size({"width": 390, "height": 800})
    a, b = _hop(cac_cot.nth(0)), _hop(cac_cot.nth(1))
    assert b["y"] >= a["y"] + a["height"] - 1 and abs(a["x"] - b["x"]) < 4      # xếp chồng
    assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
    pg.set_viewport_size({"width": 1100, "height": 900})


def test_7_the_clb_chip_khong_de_nut_va_muc_tieu_44px(cong):
    pg = cong
    for rong in (1366, 390):
        pg.set_viewport_size({"width": rong, "height": 900})
        _vao_hs(pg)
        the = pg.locator(".dk-the-clb")
        assert the.count() >= 1
        for k in range(the.count()):
            t = the.nth(k)
            chip, nut, ten = _hop(t.locator(".dk-chip").first), _hop(t.get_by_role("button", name="+ Thêm")), _hop(t.locator(".dk-ten-clb"))
            assert chip["x"] + chip["width"] <= nut["x"] + 1 or chip["y"] + chip["height"] <= nut["y"] + 1, (chip, nut)
            assert ten["x"] + ten["width"] <= nut["x"] + 1
            assert nut["height"] >= 43.5 and nut["width"] >= 43.5
            txt = t.inner_text()
            assert "·" in txt and ("Tự do" in txt or "chỗ" in txt)
        for nut in pg.locator("#dkApp .btn:visible").all():
            assert _hop(nut)["height"] >= 43.5
    pg.set_viewport_size({"width": 1100, "height": 900})


def test_8_mot_nut_vang_moi_man_va_khong_nut_vang_bi_khoa(cong):
    pg = cong
    pg.set_viewport_size({"width": 1366, "height": 900})
    _vao_hs(pg, "H1")
    assert pg.locator("#dkDaGui").count() == 1                                  # H1 đã nộp: có dòng biên nhận
    for _ in range(12):
        assert pg.locator("#dkApp .btn-primary:visible").count() == 1
        assert pg.locator("#dkApp .btn-primary:disabled").count() == 0
        if pg.get_by_role("heading", name="Xem lại và gửi").count():
            break
        pg.locator("#dkApp .btn-primary:visible").first.click()
    assert pg.locator("ol.dk-buoc li.cur").inner_text() == "Xem lại và gửi"
    pg.set_viewport_size({"width": 1100, "height": 900})


def test_9_quan_tri_thanh_sau_giai_doan_va_khong_lap_nhan_vai_tro(cong):
    pg = cong
    _dang_nhap(pg, "quan_tri", None, "matkhau")
    pg.wait_for_selector("text=Quản trị · Học sinh đăng ký")
    li = pg.locator("ol.dk-gd li")
    assert li.count() == 6
    assert pg.locator("ol.dk-gd li.cur").inner_text().endswith("Học sinh đăng ký")
    assert pg.locator("ol.dk-gd li.xong").count() == 3
    assert pg.locator("header.dk-dau").inner_text().count("Quản trị") == 1       # không lặp nhãn vai trò
    assert pg.locator("#dkHan").count() == 1
    assert pg.locator("progress.dk-tien").count() >= 1                           # thanh tiến độ mỗi lớp
    _mot_vang(pg)
    for nut in pg.locator("#dkApp .btn:visible").all():
        assert _hop(nut)["height"] >= 43.5


def test_10_giao_vien_ba_buoc_mot_nut_vang(cong):
    pg = cong
    api = pg.api
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    _ok(api.dk_chuyen_giai_doan(qt, "chuan_bi"))
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    _dang_nhap(pg, "giao_vien", "Cô An", pg.api_pin["Cô An"])
    pg.wait_for_selector("text=Bước 1/3")
    assert pg.locator("ol.dk-buoc li").count() == 3
    assert pg.locator("ol.dk-buoc li.cur").inner_text() == "1. Lịch và phòng"
    _mot_vang(pg)
    pg.locator("select").nth(0).select_option("T3")           # buổi T2 đã hết phòng trống (DKL-S9); T3 còn phòng
    pg.wait_for_function("document.querySelectorAll('select')[2].options.length > 0")
    pg.get_by_role("button", name="Tiếp theo").click()
    assert "Chỉ tiêu là số nguyên từ 1." in pg.locator("#dkThongBao").inner_text()      # DKL-S9: báo lỗi từng bước
    pg.fill("input[type=number]", "10")
    pg.get_by_role("button", name="Tiếp theo").click()
    assert pg.locator("ol.dk-buoc li.cur").inner_text() == "2. Ai được tham gia"
    pg.get_by_role("button", name="Tiếp theo").click()
    assert pg.locator("ol.dk-buoc li.cur").inner_text() == "3. Giới thiệu"
    assert pg.get_by_role("button", name="Gửi duyệt").count() == 1
    _mot_vang(pg)
    assert not pg.loi, pg.loi
