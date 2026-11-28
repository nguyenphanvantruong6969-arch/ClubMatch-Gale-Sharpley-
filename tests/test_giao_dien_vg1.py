"""VG1 (Playwright + Chromium): giao diện các lô vá gấp của cổng đăng ký — L2 phiếu PIN, L3 lùi nhiều bước, L4 CLB Tự do.
Một fixture trang dùng chung: `vao(chuan_bi, tab=None)`; `chuan_bi(tmp) -> (api, qt, giai_doan)`. Dữ liệu MÔ PHỎNG."""
import io
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import test_dk3_api as t3  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402
from test_giao_dien_dk8_l2 import TEN_GD, _dung  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok = t3.ok


def _khoi(tmp, gd="gv_dang_ky"):
    api = PipelineAPI(str(tmp / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for ten, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, ten, sc))
    if gd != "chuan_bi":
        ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    return api, qt


@pytest.fixture()
def vao(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        trang = []

        def mo(chuan_bi, tab=None):
            thu_muc = tmp_path / ("c%d" % len(trang))
            thu_muc.mkdir()
            api, qt, gd = chuan_bi(thu_muc)
            url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
            pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900}, accept_downloads=True)
            pg.loi, pg.hop = [], []
            pg.on("pageerror", lambda e: pg.loi.append(str(e)))
            pg.on("dialog", lambda d: (pg.hop.append(d.message), d.accept()))
            pg.api, pg.qt = api, qt
            pg.goto(url)
            pg.get_by_role("button", name="Quản trị", exact=True).click()
            pg.fill("input[name=ma]", "matkhau")
            pg.get_by_role("button", name="Đăng nhập").click()
            pg.wait_for_selector("text=Quản trị · " + TEN_GD[gd])
            if tab:
                pg.get_by_role("tab", name=tab).click()
            pg.wait_for_timeout(400)
            trang.append(pg)
            return pg
        yield mo
        assert all(p.loi == [] for p in trang)
        br.close()


def _gv_hs(tmp):
    api, qt = _khoi(tmp)
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A2"))
    ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))
    return api, qt, "gv_dang_ky"


# ---- L2: phiếu PIN ---------------------------------------------------------------------------------------------
def test_l2_xuat_phieu_pin_hoi_xac_nhan_tai_tep_va_pin_moi_dang_nhap_duoc(vao):
    import openpyxl
    pg = vao(_gv_hs, "Cài đặt")
    pin_cu = ok(pg.api.dk_hs_dat_lai_pin(pg.qt, "H1"))["pin"]
    pg.select_option("#dkPinPhamVi", "tat_ca")
    pg.click("#dkPinXuat")                       # sửa 2026-11-28: Python ghi tệp vào Tải xuống, trình duyệt KHÔNG tải gì
    pg.wait_for_selector("#dkThongBao:has-text('PIN cũ đã bị thay')")
    assert pg.hop and "đặt lại PIN của 3 người" in pg.hop[0]
    tai_ve = os.environ["RBDA_THU_MUC_TAI_VE"]
    assert os.listdir(tai_ve) == ["PHIEU_PIN.xlsx"] and tai_ve in pg.locator("#dkThongBao").inner_text()
    wb = openpyxl.load_workbook(io.BytesIO(open(os.path.join(tai_ve, "PHIEU_PIN.xlsx"), "rb").read()))
    assert wb.sheetnames == ["Học sinh", "Giáo viên"]
    pin_h1 = {r[0].value: r[3].value for r in wb["Học sinh"].iter_rows(min_row=2)}["H1"]
    assert ok(pg.api.dk_dang_nhap("hoc_sinh", "H1", pin_h1))["token"]
    if pin_h1 != pin_cu:
        assert not pg.api.dk_dang_nhap("hoc_sinh", "H1", pin_cu)["ok"]
    pg.wait_for_selector("#dkThongBao:has-text('PIN cũ đã bị thay')")


def test_l2_huy_hop_xac_nhan_thi_khong_doi_pin(vao):
    pg = vao(_gv_hs, "Cài đặt")
    pin = ok(pg.api.dk_hs_dat_lai_pin(pg.qt, "H1"))["pin"]
    pg.evaluate("window.confirm = () => false")
    pg.click("#dkPinXuat")
    pg.wait_for_timeout(500)
    assert ok(pg.api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]


# ---- L3: lùi nhiều bước ---------------------------------------------------------------------------------------------
def _hs_dang_ky(tmp):
    api, qt = _dung(tmp, "hs_dang_ky")                     # có sẵn nguyện vọng của H1
    return api, qt, "hs_dang_ky"


def test_l3_lui_ve_giai_doan_chon_duoc_hoi_xac_nhan_khi_co_nguyen_vong(vao):
    pg = vao(_hs_dang_ky, "Thêm")
    assert pg.locator("#dkLuiVe option").all_inner_texts() == ["Chuẩn bị", "Giáo viên đăng ký", "Duyệt CLB"]
    pg.select_option("#dkLuiVe", "gv_dang_ky")                                    # lùi 2 bước một lần
    pg.click("#dkLui")
    pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
    assert pg.hop and "1 học sinh đã gửi nguyện vọng" in pg.hop[0]
    assert pg.api.dk_trang_thai()["data"]["giai_doan"] == "gv_dang_ky"
    import sqlite3
    c = sqlite3.connect(pg.api.db_path)
    assert c.execute("SELECT COUNT(*) FROM dk_nguyen_vong").fetchone()[0] == 2
    c.close()


def test_l3_huy_xac_nhan_thi_o_nguyen_giai_doan(vao):
    pg = vao(_hs_dang_ky, "Thêm")
    pg.evaluate("window.confirm = () => false")
    pg.click("#dkLui")
    pg.wait_for_timeout(500)
    assert pg.api.dk_trang_thai()["data"]["giai_doan"] == "hs_dang_ky"


# ---- L4: CLB Tự do -------------------------------------------------------------------------------------------------
def _gv_thieu_tu_do(tmp):
    api, qt = _khoi(tmp)
    t = {x["ten"]: ok(api.dk_dang_nhap("giao_vien", x["ten"], x["pin"]))["token"]
         for x in ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình"))["da_tao"]}
    ok(api.dk_clb_luu(t["Thầy Bình"], t3._clb(ten="Cờ vua", loai="Giới hạn", phong_id=2, chi_tieu=10)))
    api._t = t
    return api, qt, "gv_dang_ky"


def test_l4_nut_dong_giai_doan_gv_bi_khoa_khi_thieu_tu_do_va_mo_lai_khi_du(vao):
    pg = vao(_gv_thieu_tu_do)
    chinh = pg.get_by_role("button", name="Đóng đăng ký giáo viên")
    ngay = pg.get_by_role("button", name="Đóng ngay")
    for b in (chinh, ngay):
        assert b.is_disabled() and b.get_attribute("aria-disabled") == "true"
    dong = pg.locator("#dkThieuTuDo")
    assert "Buổi T2 chưa có CLB Tự do" in dong.inner_text() and pg.locator("#dkKhongDungTuDo").count() == 1
    chinh.focus()
    pg.keyboard.press("Enter")                                                   # bàn phím cũng không đi qua được
    pg.wait_for_timeout(300)
    assert pg.api.dk_trang_thai()["data"]["giai_doan"] == "gv_dang_ky"
    ok(pg.api.dk_clb_luu(pg.api._t["Cô An"], t3._clb(ten="Tự do", loai="Tự do", phong_id=1)))
    pg.get_by_role("tab", name="Việc bây giờ").click()
    pg.wait_for_timeout(500)
    assert not pg.get_by_role("button", name="Đóng đăng ký giáo viên").is_disabled()
    assert pg.locator("#dkThieuTuDo").count() == 0 and not pg.get_by_role("button", name="Đóng ngay").is_disabled()


def test_l4_tat_rang_buoc_phai_xac_nhan_rui_ro_roi_mo_nut(vao):
    pg = vao(_gv_thieu_tu_do)
    pg.click("#dkKhongDungTuDo")
    pg.wait_for_timeout(600)
    assert pg.hop and "KHÔNG có CLB trong buổi đó" in pg.hop[0]
    assert ok(pg.api.dk_cai_dat_doc(pg.qt))["bat_buoc_tu_do"] is False
    pg.wait_for_timeout(500)
    assert not pg.get_by_role("button", name="Đóng đăng ký giáo viên").is_disabled()


def test_l4_checkbox_cai_dat_huy_hop_xac_nhan_thi_van_bat(vao):
    pg = vao(_gv_thieu_tu_do, "Cài đặt")
    pg.evaluate("window.confirm = () => false")
    pg.click("#dkTatTuDo")
    pg.wait_for_timeout(500)
    assert ok(pg.api.dk_cai_dat_doc(pg.qt))["bat_buoc_tu_do"] is True
    assert not pg.locator("#dkTatTuDo").is_checked()


# ---- Lỗi 7 (tab giáo viên): danh sách ngắn phải MỞ SẴN, thấy ngay họ tên, không chỉ «Giáo viên (N)» ----------------
def test_l7_tab_danh_sach_thay_ngay_ten_giao_vien(vao):
    ten = ["Đặng Văn Nam", "Cô An", "Thầy Bình", "Cô Chi"]

    def chuan_bi(tmp):
        api, qt = _khoi(tmp)
        ok(api.dk_gv_tao_hang_loat(qt, "\n".join(ten)))
        return api, qt, "gv_dang_ky"
    pg = vao(chuan_bi, "Danh sách")
    ct = pg.locator("details", has=pg.locator("summary", has_text="Giáo viên (4)"))
    assert ct.get_attribute("open") is not None
    hien = [t.strip() for t in ct.locator("tbody tr td:first-child").all_inner_texts()]
    assert sorted(hien) == sorted(ten)                                       # đúng họ tên, không dính số đếm
