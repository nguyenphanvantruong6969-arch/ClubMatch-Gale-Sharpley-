"""DK8-L3 (Playwright + Chromium): màn giáo viên và học sinh giống bản mẫu v8 — danh sách CLB dạng thẻ (chip trạng thái, dòng chi tiết),
tiêu đề «CLB của tôi» kèm chip giai đoạn, form trong thẻ hẹp với nhãn và dòng giải thích như v8; học sinh: «Đúng là em chứ?» trong thẻ hẹp,
tên lớn, thẻ CLB / hàng nguyện vọng bo góc 10 px; ô đặt huy chương VẪN dùng được (ngoại lệ bất biến 2). Một fixture trang dùng chung.
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
    """Trả hàm `vao(gd)`: gd = "gv" (giáo viên đang đăng ký, Cô An có 2 CLB chờ duyệt) hoặc "hs" (học sinh đang đăng ký)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        trang = []

        def vao(gd):
            thu_muc = tmp_path / ("c%d" % len(trang))
            thu_muc.mkdir()
            api = PipelineAPI(str(thu_muc / "app.db"))
            ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
            qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
            for ten, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
                ok(api.dk_phong_luu(qt, ten, sc))
            ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
            han = (datetime.datetime.now() + datetime.timedelta(days=2, hours=3)).strftime("%Y-%m-%dT%H:%M")
            ok(api.dk_dat_han(qt, "gv_dang_ky", han))
            if gd == "gv":
                pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]["pin"]
                tk = ok(api.dk_dang_nhap("giao_vien", "Cô An", pin))["token"]
                ok(api.dk_clb_luu(tk, t3._clb(ten="Tự do 1", loai="Tự do", phong_id=1)))
                ok(api.dk_clb_luu(tk, t3._clb(ten="Cờ vua", buoi="T3", loai="Giới hạn", phong_id=2, chi_tieu=10, khoi_tu=10, khoi_den=12)))
            else:
                t3._dung_san(api, qt)
            url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
            pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
            pg.loi = []
            pg.on("pageerror", lambda e: pg.loi.append(str(e)))
            pg.api, pg.qt = api, qt
            pg.goto(url)
            if gd == "gv":
                pg.get_by_role("button", name="Giáo viên", exact=True).click()
                pg.fill("input[name=ten]", "Cô An")
                pg.fill("input[name=ma]", pin)
                pg.get_by_role("button", name="Đăng nhập").click()
                pg.wait_for_selector("text=CLB của tôi")
            else:
                pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
                pg.get_by_role("button", name="Học sinh", exact=True).click()
                pg.fill("input[name=ten]", "H1")
                pg.fill("input[name=ma]", pin)
                pg.get_by_role("button", name="Đăng nhập").click()
                pg.wait_for_selector("text=Đúng là em chứ?")
            pg.wait_for_timeout(300)
            trang.append(pg)
            return pg
        yield vao
        assert all(p.loi == [] for p in trang)
        br.close()


def test_a_giao_vien_danh_sach_the_va_chip_giai_doan(cong):
    pg = cong("gv")
    dau = pg.locator(".dk-khung", has=pg.locator("h1", has_text="CLB của tôi")).first
    hang = dau.locator(".dk-hang-nut").first
    assert hang.locator("h1").inner_text() == "CLB của tôi" and "Đang mở · còn 2 ngày" in hang.locator(".dk-chip").inner_text()
    li = pg.locator("ul.dk-ds li")
    assert li.count() == 2
    cv = pg.locator("ul.dk-ds li", has_text="Cờ vua")
    assert cv.locator(".dk-chip").inner_text() == "Chờ duyệt"
    assert "T3 · P2 · nhận 10 · khối 10–12 · Giới hạn" in cv.inner_text()
    assert "nhận mọi em" in pg.locator("ul.dk-ds li", has_text="Tự do 1").inner_text()
    assert cv.get_by_role("button", name="Sửa Cờ vua").count() == 1 and cv.get_by_role("button", name="Xoá Cờ vua").count() == 1
    assert cv.evaluate("e => getComputedStyle(e).borderRadius") == "10px"


def test_b_giao_vien_form_the_hep_nhan_nhu_v8(cong):
    pg = cong("gv")
    the = pg.locator(".dk-hep .dk-khung", has_text="Bước 1/3")
    assert the.count() == 1 and the.bounding_box()["width"] <= 481
    opt = pg.locator("select").nth(1).locator("option").all_inner_texts()
    assert opt == ["Tự do – nhận mọi em, không kiểm tra", "Giới hạn – có số chỗ, không kiểm tra", "Tuyển chọn – có số chỗ và bài kiểm tra"]
    pg.locator("select").nth(1).select_option("Tuyển chọn")                       # giá trị cũ giữ nguyên (test cũ chọn theo giá trị)
    assert pg.locator("label:has-text('Số học sinh nhận')").count() == 1
    pg.locator("select").nth(1).select_option("Tự do")
    assert "CLB Tự do nhận mọi em đăng ký" in pg.locator(".dk-ghichu").inner_text()
    pg.locator("select").nth(1).select_option("Giới hạn")
    pg.locator("label:has-text('Số học sinh nhận') input").fill("20")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.wait_for_selector("text=Bước 3/3")
    assert pg.locator("label:has-text('Mô tả CLB (học sinh đọc khi chọn)')").count() == 1
    assert pg.locator("label:has-text('Yêu cầu cơ bản')").count() == 1
    tt = pg.locator(".dk-tom-tat").inner_text()                                      # dòng tóm tắt như v8
    assert "Giới hạn" in tt and "nhận 20" in tt and "khối 6–12" in tt
    pg.fill("label:has-text('Tên CLB') input", "Robot")


def test_c_hoc_sinh_xac_nhan_the_hep_ten_lon(cong):
    pg = cong("hs")
    the = pg.locator(".dk-hep .dk-khung")
    assert the.count() == 1 and the.locator("h1").inner_text() == "Đúng là em chứ?" and the.bounding_box()["width"] <= 481
    assert float(pg.locator(".dk-ten-hs").evaluate("e => parseFloat(getComputedStyle(e).fontSize)")) >= 19      # 1,4rem như v8 `.big`
    assert "Lớp 10A1 · Khối 10 · Mã H1" in pg.locator("#dkThongTinHs").inner_text()
    assert the.get_by_role("button", name="Đúng là em", exact=True).evaluate("e => e.classList.contains('btn-primary')")
    assert the.get_by_role("button", name="Không phải em").evaluate("e => e.classList.contains('btn-secondary')")


def test_d_hoc_sinh_the_clb_bo_goc_va_huy_chuong_van_dat_duoc(cong):
    pg = cong("hs")
    pg.get_by_role("button", name="Đúng là em", exact=True).click()
    pg.wait_for_selector("text=Buổi T2")
    for ten in ("Cờ vua", "Tự do 1"):
        pg.locator("li.dk-the-clb", has_text=ten).get_by_role("button", name="+ Thêm").click()
    assert pg.locator("li.dk-the-clb").first.evaluate("e => getComputedStyle(e).borderRadius") == "10px"
    assert pg.locator(".dk-xep > li").first.evaluate("e => getComputedStyle(e).borderRadius") == "10px"
    pg.get_by_role("button", name="Tiếp: đặt huy chương").click()
    pg.wait_for_selector("text=Đặt huy chương")
    sel = pg.locator("select[aria-label='Huy chương Bạc']")
    assert sel.count() == 1 and sel.is_enabled()                                    # học sinh vẫn tự đổi được huy chương
    sel.select_option(index=1)
    assert pg.locator("text=Em đã tự đổi huy chương buổi này").count() == 1
