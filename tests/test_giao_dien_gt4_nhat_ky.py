"""GT4-L6 — nhật ký thao tác đọc được trong giao diện thật: nhãn Việt/Anh, ô chọn hành động, "chỉ bị từ chối", lọc ngày,
giờ địa phương, chi tiết dạng `khoá: giá trị`, dòng học sinh tự tra cứu, nằm trong thẻ riêng của hộp Tài khoản. Chromium."""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"
_THEM = "INSERT INTO nhat_ky_thao_tac (luc, nguoi, vai, hanh_dong, ket_qua, chi_tiet) VALUES (?,?,?,?,?,?)"


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    with api._ket_noi_ghi() as cur:
        cur.executemany(_THEM, [
            ("2026-01-02T10:05:00", "quantri", "quan_tri", "run_pipeline", "ok", "{}"),
            ("2026-01-02T11:30:00", "gv1", "giao_vien", "run_thu", "gt3_khong_du_quyen", "{}"),
            ("2026-01-02T12:00:00", None, None, "tra_cuu_hoc_sinh", "ok", '{"student_id": "s1"}'),
            ("2026-01-03T09:00:00", "quantri", "quan_tri", "ham_la_xyz", "ok", '{"khoa_la": "gia tri"}'),
        ])
    api.dang_xuat()
    assert api.dang_nhap("quantri", MK)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True)
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#tkNutMoHop")
    try:
        yield page, api, loi
    finally:
        br.close()
        pw.stop()


def _mo_nhat_ky(page):
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkTabNhatKy")
    page.click("#tkTabNhatKy")
    page.wait_for_selector("#tkNkTable")


def _chu_bang(page):
    return page.inner_text("#tkNkTable tbody")


def test_nhat_ky_nam_trong_the_rieng_cua_hop(mo):
    page, api, loi = mo
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkTabNhatKy")
    assert page.locator("#tkFormDoiMk").is_visible() and page.locator("#tkNhatKy").count() == 0   # chưa mở thẻ nhật ký
    page.click("#tkTabNhatKy")
    page.wait_for_selector("#tkNkTable")
    assert not page.locator("#tkFormDoiMk").is_visible()                                          # thẻ tài khoản ẩn đi
    page.click("#tkTabTaiKhoan")
    assert page.locator("#tkFormDoiMk").is_visible() and not page.locator("#tkNhatKy").is_visible()
    assert not loi, loi


def test_nhan_tieng_viet_gio_dia_phuong_chi_tiet_va_dong_hoc_sinh(mo):
    page, api, loi = mo
    _mo_nhat_ky(page)
    chu = _chu_bang(page)
    for nhan in ("Chạy xếp chính thức", "Chạy thử", "Quản trị", "Giáo viên", "Thành công",
                 "Bị từ chối: không đủ quyền", "Học sinh tự tra cứu", "Mã học sinh: s1"):
        assert nhan in chu, nhan
    for tho in ("run_pipeline", "run_thu", "tra_cuu_hoc_sinh", "gt3_khong_du_quyen", "student_id", "{", '"'):
        assert tho not in chu.replace("ham_la_xyz", ""), tho                     # không tên nội bộ, không JSON thô
    assert "ham_la_xyz" in chu and "khoa_la: gia tri" in chu                       # tên lạ: giữ nguyên chữ (an toàn)
    assert re.search(r"02/01/2026 10:05", chu) and "2026-01-02T" not in chu
    assert not loi, loi


def test_o_chon_hanh_dong_chi_bi_tu_choi_va_ngay(mo):
    page, api, loi = mo
    _mo_nhat_ky(page)
    opts = page.locator("#tkNkHanhDong option").all_inner_texts()
    assert opts[0] == "Tất cả thao tác" and "Chạy thử" in opts and "ham_la_xyz" in opts
    page.select_option("#tkNkHanhDong", "run_thu")
    page.click("#tkNkLoc")
    page.wait_for_function("document.querySelectorAll('#tkNkTable tbody tr').length === 1")
    assert "Chạy thử" in _chu_bang(page) and "Chạy xếp" not in _chu_bang(page)
    page.select_option("#tkNkHanhDong", "")
    page.check("#tkNkTuChoi")
    page.click("#tkNkLoc")
    page.wait_for_function("document.querySelectorAll('#tkNkTable tbody tr').length === 1")
    assert "Bị từ chối" in _chu_bang(page)
    page.uncheck("#tkNkTuChoi")
    page.fill("#tkNkNgay", "2026-01-03")
    page.click("#tkNkLoc")
    page.wait_for_function("(document.querySelector('#tkNkTable tbody') || {innerText: ''}).innerText.includes('ham_la_xyz')")
    assert page.locator("#tkNkTable tbody tr").count() == 1
    assert not loi, loi


def test_doi_ngon_ngu_cho_nhan_tieng_anh(mo):
    page, api, loi = mo
    _mo_nhat_ky(page)
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("(document.querySelector('#tkNkTable tbody') || {innerText: ''})"
                           ".innerText.includes('Run the official allocation')")
    chu = _chu_bang(page)
    assert "Student self-lookup" in chu and "Refused: not allowed" in chu and "Administrator" in chu
    assert not loi, loi
