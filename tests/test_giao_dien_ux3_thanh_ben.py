"""UX3: thanh bên — đánh số nhóm theo nhóm đang hiện (giáo viên) và khối tài khoản ở chân không bị cắt/lệch
(cả hai vai). Chromium qua `browser_host`. Dữ liệu MÔ PHỎNG."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"
TEN_DAI = "nguyenthiphuongthao.giaovien.chunhiem"


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True, viewport={"width": 1366, "height": 800})
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))

    def mo_trang():
        page.goto(url)
        page.wait_for_selector("#tkNutDangXuat")
        page.wait_for_function("document.body.dataset.vai")

    try:
        yield page, api, mo_trang, loi
    finally:
        br.close()
        pw.stop()


def dang_nhap(api, vai):
    assert api.tao_tai_khoan(TEN_DAI if vai == "quan_tri" else "quantri", MK, "quan_tri")["ok"]
    if vai == "giao_vien":
        assert api.tao_tai_khoan(TEN_DAI, MK, "giao_vien")["ok"]
        api.dang_xuat()
        assert api.dang_nhap(TEN_DAI, MK)["ok"]


def nhan_nhom(page):
    return page.evaluate("""() => [...document.querySelectorAll('.nav-nhom')]
        .filter(n => n.offsetParent !== null).map(n => n.querySelector('.nav-nhom-nut').innerText.trim())""")


def test_giao_vien_danh_so_tu_1(mo):
    page, api, mo_trang, loi = mo
    dang_nhap(api, "giao_vien")
    mo_trang()
    page.wait_for_function("document.querySelector('.nav-nhom[data-nhom=nap_xep]').hidden")
    assert nhan_nhom(page) == ["1. Nhập tay", "2. Kết quả & phiếu"]
    assert not loi, loi


def test_quan_tri_giu_1_2_3_ca_khi_doi_ngon_ngu(mo):
    page, api, mo_trang, loi = mo
    dang_nhap(api, "quan_tri")
    mo_trang()
    assert nhan_nhom(page) == ["1. Nạp & xếp", "2. Nhập tay", "3. Kết quả & phiếu", "Cài đặt và quản lý"]
    page.evaluate("window.I18N && I18N.setLang ? I18N.setLang('en') : null")
    if page.evaluate("document.documentElement.lang") == "en":
        assert nhan_nhom(page)[:3] == ["1. Load & run", "2. Manual entry", "3. Results & slips"]
    assert not loi, loi


@pytest.mark.parametrize("vai", ["giao_vien", "quan_tri"])
def test_chan_thanh_ben_khong_cat_khong_lech(mo, vai):
    page, api, mo_trang, loi = mo
    dang_nhap(api, vai)
    mo_trang()
    do = page.evaluate("""() => {
        const r = e => e.getBoundingClientRect();
        const ten = document.getElementById('tkHuyHieu'), a = document.getElementById('tkNutDangXuat'),
              b = document.getElementById('tkNutMoHop'), ben = r(document.querySelector('.sidebar'));
        const st = getComputedStyle(ten);
        return {tran: ten.scrollWidth > ten.clientWidth, elip: st.textOverflow === 'ellipsis', title: ten.title,
                ra: r(a), rb: r(b), rt: r(ten), ben: {l: ben.left, r: ben.right},
                tranNut: [a, b].some(e => e.scrollWidth > e.clientWidth + 1)};
    }""")
    assert TEN_DAI in do["title"]
    assert not do["tran"] or do["elip"]
    assert abs(do["ra"]["top"] - do["rb"]["top"]) < 1          # hai nút cùng hàng
    assert abs(do["ra"]["width"] - do["rb"]["width"]) < 1      # cùng cỡ
    assert do["rt"]["bottom"] <= do["ra"]["top"] + 0.5           # tên ở dòng trên
    for k in ("ra", "rb", "rt"):
        assert do[k]["left"] >= do["ben"]["l"] and do[k]["right"] <= do["ben"]["r"], k
    assert not do["tranNut"]
    assert not loi, loi
