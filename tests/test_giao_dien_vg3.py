"""VG3 (Playwright + Chromium): dọn giao diện cổng đăng ký — chỉ trình bày. Một trang dùng chung, dữ liệu MÔ PHỎNG.
Thứ tự test là thứ tự giai đoạn: trang đầu → Chuẩn bị → (tạo CLB bằng API) → Duyệt → Học sinh đăng ký."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau"


def _ok(r):
    assert r["ok"] and r["errors"] == [], r
    return r["data"]


@pytest.fixture(scope="module")
def cong(tmp_path_factory):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path_factory.mktemp("vg3") / "app.db"))
    _ok(api.dk_khoi_tao(MK, "VG3X", ["T2"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", MK))["token"]
    for t, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        _ok(api.dk_phong_luu(qt, t, sc))
    _ok(api.dk_hs_nap_danh_sach(qt, "\n".join("H%02d\tHS %02d (mô phỏng)\t10A1" % (i, i) for i in range(1, 7))))
    pin = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))["da_tao"]}
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 375, "height": 800})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.pin, pg.dia_chi = api, qt, pin, url
        yield pg
        br.close()


def _tran_ngang(pg):
    return pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")


def _vao_quan_tri(pg):
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    pg.fill("input[name=ma]", MK)
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị ·")


def _vao_hs(pg, ma):
    qt = _ok(pg.api.dk_dang_nhap("quan_tri", "", MK))["token"]
    pin = _ok(pg.api.dk_hs_dat_lai_pin(qt, ma))["pin"]
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Học sinh", exact=True).click()
    pg.fill("input[name=ten]", ma)
    pg.fill("input[name=ma]", pin)
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.get_by_role("button", name="Đúng là em", exact=True).click()
    pg.wait_for_selector("ol.dk-buoc")


def _clb(pg, gv, d):
    tk = _ok(pg.api.dk_dang_nhap("giao_vien", gv, pg.pin[gv]))["token"]
    phong = {p["ten"]: p["phong_id"] for p in _ok(pg.api.dk_phong_danh_sach(tk))}
    d = dict(d, phong_id=phong[d.pop("phong")], buoi="T2", khoi_tu=9, khoi_den=12, mo_ta="mô phỏng", yeu_cau="Không")
    return _ok(pg.api.dk_clb_luu(tk, d))["clb_id"]


def test_1_trang_dau_khong_tran_ngang_chip_giai_doan_con_o_day(cong):
    pg = cong
    pg.goto(pg.dia_chi)
    pg.wait_for_selector(".dk-cua")
    assert _tran_ngang(pg) <= 0
    assert pg.locator("header.dk-dau .dk-chip").count() == 1                       # trang đầu giữ chip giai đoạn
    assert pg.locator("header.dk-dau img.dk-logo").count() == 1                    # logo thật, không còn chữ "RB"
    the = pg.locator(".dk-cua").first
    chip = the.locator(".dk-chip").bounding_box()
    assert chip["width"] < the.bounding_box()["width"] * 0.7                       # chip đúng cỡ chữ, không dãn hết thẻ
    assert "Vào" in the.inner_text()


def test_2_quan_tri_chuan_bi(cong):
    pg = cong
    _vao_quan_tri(pg)
    pg.wait_for_selector("ol.dk-gd")
    assert _tran_ngang(pg) <= 0
    assert pg.locator("header.dk-dau .dk-chip").count() == 0                       # tên giai đoạn không lặp ở thanh trên
    tops = pg.locator(".dk-the-nut").evaluate_all("els => els.map(e => e.offsetTop)")
    assert len(tops) == 4 and len(set(tops)) == 1                                  # bốn thẻ cùng một hàng
    assert pg.locator("ol.dk-gd li").count() == 6
    pg.set_viewport_size({"width": 1280, "height": 900})
    ten, sc = pg.locator("#dkKhungPhong input").nth(0).bounding_box(), pg.locator("#dkKhungPhong input").nth(1).bounding_box()
    nut = pg.locator("#dkKhungPhong").get_by_role("button", name="Thêm phòng").bounding_box()
    assert abs(ten["y"] - sc["y"]) < 2 and abs(ten["y"] + ten["height"] - nut["y"] - nut["height"]) < 2   # một hàng, cùng đáy
    pg.set_viewport_size({"width": 375, "height": 800})
    assert _tran_ngang(pg) <= 0


def test_3_quan_tri_duyet(cong):
    pg = cong
    api, qt = pg.api, pg.qt
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    _clb(pg, "Cô An", {"ten": "Tự do VG3", "loai": "Tự do", "phong": "P1"})
    _clb(pg, "Cô Bê", {"ten": "Cờ vua", "loai": "Giới hạn", "phong": "P2", "chi_tieu": 12})
    _ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    _vao_quan_tri(pg)
    pg.wait_for_selector("text=Quản trị · Duyệt CLB")
    assert _tran_ngang(pg) <= 0
    chi_tieu = pg.locator("input[aria-label='Chỉ tiêu Cờ vua']")
    pg.set_viewport_size({"width": 1280, "height": 900})
    assert chi_tieu.bounding_box()["width"] < 140
    assert pg.locator("tr:has-text('Tự do VG3') input[type=number]").get_attribute("title") == "Không giới hạn"
    assert pg.locator("tr:has-text('Cờ vua') .dk-chip.wait").count() == 1          # trạng thái là chip
    pg.set_viewport_size({"width": 375, "height": 800})
    assert _tran_ngang(pg) <= 0


def test_4_hoc_sinh_xep_nguyen_vong_va_huy_chuong(cong):
    pg = cong
    api, qt = pg.api, pg.qt
    cl = {c["ten"]: c["clb_id"] for c in _ok(api.dk_clb_danh_sach(qt))}
    for i in cl.values():
        _ok(api.dk_clb_duyet(qt, i, "duyet"))
    _ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    _vao_hs(pg, "H01")
    pg.locator(".dk-the-clb", has_text="Tự do VG3").get_by_role("button", name="+ Thêm").click()
    pg.locator(".dk-the-clb", has_text="Cờ vua").get_by_role("button", name="+ Thêm").click()
    assert _tran_ngang(pg) <= 0
    nv = pg.locator(".dk-xep li").first
    assert nv.locator(".dk-nv").inner_text() == "NV1"
    assert "mono" not in nv.locator(".dk-nv").evaluate("e => getComputedStyle(e).fontFamily").lower()
    hop = nv.get_by_role("button", name="Xuống").bounding_box()
    assert hop["width"] >= 44 and hop["height"] >= 44
    assert pg.locator(".dk-xep").locator("xpath=ancestor::section[1]").locator("h2 .dk-chip").count() == 1     # bộ đếm là chip
    # có CLB Giới hạn trong nguyện vọng → có hộp «Đã đặt sẵn…»
    pg.get_by_role("button", name="Tiếp: đặt huy chương").click()
    assert pg.get_by_text("Đã đặt sẵn theo thứ tự nguyện vọng").count() == 1
    pg.get_by_role("button", name="← Quay lại").click()
    pg.get_by_role("button", name="Bỏ").nth(1).click()                              # chỉ còn CLB Tự do
    # VG2 bỏ hẳn bước huy chương khi không có CLB nào để đặt (hộp «Đã đặt sẵn…» cũng không còn chỗ hiện)
    assert pg.get_by_role("button", name="Tiếp: đặt huy chương").count() == 0
    assert pg.get_by_text("Đã đặt sẵn theo thứ tự nguyện vọng").count() == 0
    assert _tran_ngang(pg) <= 0


def test_5_xem_lai_gon_va_phan_mem_chinh_khong_doi(cong):
    pg = cong
    pg.get_by_role("button", name="Tiếp: xem lại và gửi").click()                  # CLB Tự do duy nhất: VG2 bỏ qua huy chương và bài kiểm tra
    pg.wait_for_selector("text=Xem lại và gửi")
    assert _tran_ngang(pg) <= 0
    cot = pg.locator("table.dk-bang th").first.bounding_box()["width"]
    assert cot < pg.locator("table.dk-bang").bounding_box()["width"] * 0.3         # cột «Buổi» hẹp
    assert not pg.loi, pg.loi
    pg.goto(pg.dia_chi.replace("dang_ky.html", "index.html"))
    pg.wait_for_selector(".nav-item")
    assert pg.locator(".nav-item").first.is_visible()
