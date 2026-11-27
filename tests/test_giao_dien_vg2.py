"""VG2-L3/L4 (Playwright + Chromium): danh sách mở sẵn, hộp xác nhận, bảng không làm tràn trang, thông báo lỗi cũ biến mất, học sinh chỉ đi qua bước có việc,
tên giai đoạn tiếng Việt trong lỗi. Dữ liệu MÔ PHỎNG."""
import pathlib

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_giao_dien_dk8_l2 import TEN_GD, _dung  # noqa: E402

GOC = str(pathlib.Path(__file__).resolve().parent.parent)


@pytest.fixture()
def vao(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        n = {"i": 0}

        def mo(gd, rong=1100):
            n["i"] += 1
            d = tmp_path / ("c%d" % n["i"])
            d.mkdir()
            api, qt = _dung(d, gd)
            url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
            pg = br.new_page(bypass_csp=True, viewport={"width": rong, "height": 900})
            pg.loi = []
            pg.on("pageerror", lambda e: pg.loi.append(str(e)))
            pg.api, pg.qt = api, qt
            pg.goto(url)
            pg.get_by_role("button", name="Quản trị", exact=True).click()
            pg.fill("input[name=ma]", "matkhau")
            pg.get_by_role("button", name="Đăng nhập").click()
            pg.wait_for_selector("text=Quản trị · " + TEN_GD[gd])
            return pg
        yield mo
        br.close()


def test_danh_sach_giao_vien_mo_san_va_co_nut_xoa(vao):
    pg = vao("gv_dang_ky")
    pg.get_by_role("tab", name="Danh sách").click()
    pg.wait_for_selector("summary:has-text('Giáo viên (2)')")
    assert pg.locator("summary:has-text('Giáo viên (2)')").evaluate("e => e.parentElement.open") is True
    assert pg.get_by_role("button", name="Đặt lại PIN — Cô An").count() == 1         # nhãn nêu tên người
    assert pg.get_by_role("button", name="Xoá giáo viên Cô An").count() == 1
    assert not pg.loi, pg.loi


def test_dong_ngay_hoi_xac_nhan_huy_thi_khong_doi_giai_doan(vao):
    pg = vao("gv_dang_ky")
    hop = []
    pg.once("dialog", lambda d: (hop.append(d.message), d.dismiss()))
    pg.get_by_role("button", name="Đóng ngay").click()
    pg.wait_for_timeout(500)
    assert hop and "Đóng ngay giai đoạn" in hop[0]
    assert pg.api.dk_trang_thai()["data"]["giai_doan"] == "gv_dang_ky"
    pg.once("dialog", lambda d: d.accept())
    pg.get_by_role("button", name="Đóng ngay").click()
    pg.wait_for_function("document.body.innerText.includes('Duyệt CLB')")
    assert pg.api.dk_trang_thai()["data"]["giai_doan"] == "duyet"


def test_bang_rong_khong_lam_tran_trang_o_375px(vao):
    pg = vao("duyet", rong=375)
    pg.wait_for_selector(".dk-cuon-ngang")
    assert pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 1


def test_thong_bao_loi_cu_mat_sau_lan_luu_dung(vao):
    pg = vao("nhap_diem")
    o = pg.locator(".dk-noidung input[type=text]").first
    o.fill("abc")
    o.press("Enter")
    pg.wait_for_function("document.getElementById('dkThongBao').innerText.includes('Điểm phải là số')")
    o.fill("8,5")
    o.press("Enter")
    pg.wait_for_function("document.getElementById('dkThongBao').innerText === ''")


def test_loi_sai_giai_doan_dung_ten_tieng_viet(vao):
    pg = vao("chuan_bi")
    r = pg.api.dk_gv_tu_dang_ky("TRUONG1", "Cô Hoa", "7391")
    from i18n_errors import format_message
    chu = format_message(r["errors"][0]["code"], r["errors"][0]["params"], "vi")
    assert "gv_dang_ky" not in chu and "Giáo viên đăng ký" in chu


def test_hoc_sinh_chi_di_qua_buoc_co_viec(vao):
    pg = vao("hs_dang_ky")
    pin = pg.api.dk_hs_dat_lai_pin(pg.qt, "H2")["data"]["pin"]
    pg.get_by_role("button", name="Đăng xuất").click()
    pg.get_by_role("button", name="Học sinh", exact=True).click()
    pg.fill("input[name=ten]", "H2")
    pg.fill("input[name=ma]", pin)
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.get_by_role("button", name="Đúng là em", exact=True).click()
    pg.wait_for_selector("text=Buổi T2")
    pg.locator("li.dk-the-clb", has_text="Tự do 1").get_by_role("button", name="+ Thêm").click()
    pg.get_by_role("button", name="Tiếp: T3").click()                              # chỉ CLB Tự do: không qua huy chương / bài thi
    pg.wait_for_selector("text=Buổi T3")
    pg.get_by_role("button", name="Tiếp: xem lại và gửi").click()                  # buổi trống: đi thẳng tới xem lại
    pg.wait_for_selector("#dkGui")
    # «← Quay lại» từ màn xem lại về bước THẬT cuối cùng (xếp nguyện vọng T3), không rơi vào màn bài kiểm tra bị bỏ qua
    pg.get_by_role("button", name="← Quay lại").click()
    pg.wait_for_selector("h1:has-text('Buổi T3 · Xếp nguyện vọng')")
    pg.get_by_role("button", name="← Buổi trước").click()                         # T3 -> T2 (bỏ qua huy chương / bài thi)
    pg.wait_for_selector("h1:has-text('Buổi T2 · Xếp nguyện vọng')")
    pg.get_by_role("button", name="Tiếp: T3").click()
    pg.get_by_role("button", name="Tiếp: xem lại và gửi").click()
    pg.wait_for_selector("#dkGui")
    assert not pg.loi, pg.loi
