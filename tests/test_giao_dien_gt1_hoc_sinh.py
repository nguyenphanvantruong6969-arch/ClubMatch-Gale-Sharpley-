"""GT1-L4: chế độ "học sinh tra cứu" bằng TRÌNH DUYỆT THẬT (Playwright + Chromium). Dữ liệu MÔ PHỎNG.

Kiểm: mã đúng -> chỉ thẻ của chính em đó; mã sai -> không có thẻ, báo lỗi dễ hiểu; khoá tạm sau 5 lần sai; phần
quản trị bị khoá (inert) khi đang ở chế độ này; 60 giây không thao tác thì xoá thẻ (đồng hồ giả); thoát có hỏi lại;
nút tạo mã ở màn hình quản trị không hiện mã. Máy không có Chromium thì bỏ qua.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _fa import dung_fa_clb  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import tat_wharton  # noqa: E402

HS = {"s1": "Nguyễn Văn Ánh", "s2": "Trần Thị Bé"}
CHU_NOI_BO = ("GT1", "gt1_", "Wharton", "undefined", "null", "{")


def _dung(api):
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
    for sid, ten in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    with api._ket_noi_doc() as cur:
        return dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.clock.install()                      # đồng hồ giả: chạy 60 giây mà không chờ thật
        page.goto(url)
        page.wait_for_selector("#gtPanel", state="attached")
        page.click('button.nav-item[data-tab="results"]')
        yield page, loi, api


def _vao(page, sid, ma):
    page.fill("#gtHsMa", sid)
    page.fill("#gtHsMaTra", ma)
    page.click("#btnGtHsXem")


def test_ma_dung_chi_hien_the_cua_chinh_em(mo):
    page, loi, api = mo
    ma = _dung(api)
    page.click("#btnGtCheDoHs")
    assert page.locator("#gtHs").is_visible()
    _vao(page, "s1", ma["s1"].lower())
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    the = page.locator("#gtHs").inner_text()
    assert HS["s1"] in the and "s1" in the
    assert HS["s2"] not in the and "s2" not in the
    assert ma["s1"] not in the and ma["s2"] not in the
    assert page.locator("#gtHsKetQua .gt-duoc-xep").count() == 1
    assert page.locator("#gtHs #btnGtInMot, #gtHs #gtTim, #gtHs #gtLop").count() == 0     # không có công cụ quản trị
    assert page.locator("#gtHsMaTra").input_value() == ""                                 # mã không nằm lại
    for bi in CHU_NOI_BO:
        assert bi not in the, bi
    assert loi == []


def test_ma_sai_khong_co_the_va_khoa_tam(mo):
    page, loi, api = mo
    ma = _dung(api)
    page.click("#btnGtCheDoHs")
    for _ in range(5):
        _vao(page, "s1", "AAAAAAAA")
        page.wait_for_function("document.querySelector('#gtHsLoi').innerText.includes('chưa đúng')")
        assert page.locator("#gtHsKetQua").inner_text() == ""
        page.evaluate("document.querySelector('#gtHsLoi').textContent = ''")
    _vao(page, "s1", ma["s1"])                      # đã khoá: mã đúng cũng chưa vào được
    page.wait_for_function("document.querySelector('#gtHsLoi').innerText.includes('quá nhiều lần')")
    assert page.locator("#gtHsKetQua").inner_text() == ""
    assert loi == []


def test_phan_quan_tri_bi_khoa_khi_o_che_do_hoc_sinh(mo):
    page, loi, api = mo
    _dung(api)
    page.click("#btnGtCheDoHs")
    assert page.evaluate("document.querySelector('.app-shell').inert") is True
    assert page.evaluate("document.querySelector('#gtPanel').closest('[inert]') !== null") is True
    page.click("#btnGtHsThoat")
    page.click("#btnGtHsCo")
    assert page.evaluate("document.querySelector('.app-shell').inert") is False
    assert loi == []


def test_60_giay_khong_thao_tac_thi_xoa_the(mo):
    page, loi, api = mo
    ma = _dung(api)
    page.click("#btnGtCheDoHs")
    _vao(page, "s2", ma["s2"])
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    page.clock.run_for(30000)
    assert page.locator("#gtHsKetQua .gt-ten").count() == 1          # chưa tới 60 giây
    page.clock.run_for(31000)
    page.wait_for_function("document.querySelector('#gtHsKetQua').childElementCount === 0")
    assert page.locator("#gtHsMa").input_value() == ""
    assert "lâu không thao tác" in page.locator("#gtHsLoi").inner_text()
    assert HS["s2"] not in page.locator("#gtHs").inner_text()
    assert loi == []


def test_thao_tac_giua_chung_keo_dai_thoi_gian(mo):
    page, loi, api = mo
    ma = _dung(api)
    page.click("#btnGtCheDoHs")
    _vao(page, "s1", ma["s1"])
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    page.clock.run_for(45000)
    page.click("#gtHsKetQua")                          # đang đọc: bấm vào thẻ thì đếm lại
    page.clock.run_for(45000)
    assert page.locator("#gtHsKetQua .gt-ten").count() == 1
    page.clock.run_for(16000)
    page.wait_for_function("document.querySelector('#gtHsKetQua').childElementCount === 0")


def test_thoat_co_hoi_lai_va_xoa_the(mo):
    page, loi, api = mo
    ma = _dung(api)
    page.click("#btnGtCheDoHs")
    _vao(page, "s1", ma["s1"])
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    page.click("#btnGtHsThoat")
    assert page.locator("#gtHsXacNhan").is_visible() and page.locator("#gtHs").is_visible()
    page.click("#btnGtHsKhong")
    assert not page.locator("#gtHsXacNhan").is_visible() and page.locator("#gtHsKetQua .gt-ten").count() == 1
    page.click("#btnGtHsThoat")
    page.click("#btnGtHsCo")
    assert not page.locator("#gtHs").is_visible()
    assert page.locator("#gtHsKetQua").inner_text() == ""
    page.click("#btnGtCheDoHs")                         # mở lại: không còn thẻ cũ
    assert page.locator("#gtHsKetQua").inner_text() == ""
    assert loi == []


def test_nut_tao_ma_o_man_hinh_quan_tri_khong_hien_ma(mo):
    page, loi, api = mo
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"))
    for sid, ten in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
    page.click("#btnGtTaoMa")
    page.wait_for_function("document.querySelector('#gtMaPhanHoi').innerText.includes('Đã tạo 2 mã')")
    with api._ket_noi_doc() as cur:
        ma = [r[0] for r in cur.execute("SELECT ma FROM ma_tra_cuu")]
    assert len(ma) == 2 and not any(m in page.locator("#gtPanel").inner_text() for m in ma)
    page.click("#btnGtTaoMa")                           # bấm lại: không đổi mã đã có
    page.wait_for_function("document.querySelector('#gtMaPhanHoi').innerText.includes('Đã tạo 0 mã')")
    with api._ket_noi_doc() as cur:
        assert [r[0] for r in cur.execute("SELECT ma FROM ma_tra_cuu")] == ma
    assert loi == []
