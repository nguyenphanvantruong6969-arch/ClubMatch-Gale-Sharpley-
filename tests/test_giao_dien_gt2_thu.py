"""GT2-L3 — khung "Thử cấu hình" ở thẻ Quản lý (Playwright + Chromium, qua `browser_host`).

Dữ liệu MÔ PHỎNG. Kiểm: chạy thử rồi thấy bảng so sánh; kết quả chính thức không đổi; bấm đúp chỉ ghi
một lần; chưa có lần chính thức thì báo dễ hiểu; tên có thẻ HTML không thành mã; đổi ngôn ngữ; xuất trang
so sánh; không có `undefined` / `NaN` / `[object Object]`."""

import os
import shutil
import sqlite3
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

XSS = "<img src=x onerror=window.__xss=1>"


def _sql(db, cau, tham=()):
    c = sqlite3.connect(db)
    try:
        return c.execute(cau, tham).fetchall()
    finally:
        c.close()


@pytest.fixture
def mo(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(chay=True):
        db = d.nap_bo(str(tmp_path), d.BO_DU_LIEU[0][1])
        cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
        c = sqlite3.connect(db)
        c.execute("UPDATE students SET name = ? WHERE student_id = (SELECT MIN(student_id) FROM students)",
                  (XSS,))
        c.commit()
        c.close()
        goc = str(tmp_path / "goc")                  # chế độ workspace: lưu tiêu chí (L4) cần nó
        os.makedirs(goc)
        slug = ws.tao(goc, "Thu tieu chi", {})
        shutil.copyfile(db, ws.duong_dan_db(goc, slug))
        db = ws.duong_dan_db(goc, slug)
        api = PipelineAPI(db, thu_muc_goc_ws=goc)
        assert api.open_workspace(slug)["ok"]
        if chay:
            assert api.run_pipeline(seed=42)["ok"]
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1600}, bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.locator('[data-tab="admin"]').click()
        page.click("#qlTabCachXep")  # UX4-L2: tiêu chí/thử nằm trong tab Cách xếp
        page.evaluate("document.getElementById('ux1aNangCao').open = document.getElementById('gt2ThuSoSanhKhac').open = true")  # UX4-L4: hai mục gập (Tuỳ chỉnh thêm, So sánh với lần khác)
        page.wait_for_selector("#gt2TcDanhSach li")
        return page, api, db, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _sach(page):
    chu = page.locator("#gt2ThuPanel").inner_text()
    for xau in ("undefined", "NaN", "[object Object]", "{id}", "{n}"):
        assert xau not in chu, xau


def test_chay_thu_hien_bang_so_sanh_va_khong_doi_ket_qua_chinh_thuc(mo):
    page, api, db, loi = mo()
    truoc = _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi")
    assert page.locator("#gt2ThuChon").is_visible()
    page.select_option("#gt2TcPriority", "tier")
    page.locator("#gt2ThuChay").dblclick()           # bấm đúp: chỉ một lần chạy
    page.wait_for_selector("#gt2ThuKetQua table")
    assert _sql(db, "SELECT COUNT(*) FROM run_history WHERE loai_chay = 'thu'") == [(1,)]
    chu = page.locator("#gt2ThuKetQua").inner_text()
    assert "Thử lần" in chu and "Xếp chính thức lần" in chu   # UX4-L4: tên lần chạy mới
    assert page.locator("#gt2ThuKetQua table").count() == 5
    assert page.locator("#gt2ThuPhanHoi").inner_text().startswith("Đã chạy thử xong")
    assert _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi") == truoc
    _sach(page)
    assert not loi, loi
    assert page.evaluate("window.__xss || 0") == 0


def test_ten_co_the_html_khong_thanh_ma(mo):
    page, api, db, loi = mo()
    page.select_option("#gt2TcPriority", "tier")
    page.locator("#gt2ThuChay").click()
    page.wait_for_selector("#gt2ThuKetQua table")
    page.select_option("#gt2ThuA", index=1)
    page.select_option("#gt2ThuB", index=0)
    page.locator("#gt2ThuSoSanh").click()
    page.wait_for_selector("#gt2ThuKetQua table")
    assert page.locator("#gt2ThuKetQua img").count() == 0
    assert page.evaluate("window.__xss || 0") == 0
    assert not loi, loi


def test_chua_co_lan_chinh_thuc_bao_de_hieu(mo):
    page, api, db, loi = mo(chay=False)
    assert page.locator("#gt2ThuChuaCo").is_visible()
    assert not page.locator("#gt2ThuChon").is_visible()
    page.locator("#gt2ThuChay").click()
    page.wait_for_function("document.querySelector('#gt2ThuPhanHoi').textContent.length > 0")
    assert "chính thức" in page.locator("#gt2ThuPhanHoi").inner_text()
    assert _sql(db, "SELECT COUNT(*) FROM run_history") == [(0,)]
    _sach(page)
    assert not loi, loi


def test_doi_ngon_ngu_ve_lai_va_xuat_trang_so_sanh(mo, tmp_path):
    page, api, db, loi = mo()
    page.locator("#gt2ThuChay").click()
    page.wait_for_selector("#gt2ThuKetQua table")
    assert "không suất nào đổi chỗ" in page.locator("#gt2SsKetLuan").inner_text()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.querySelector('#gt2ThuChay').textContent === 'Try this way'")   # UX4-L4
    chu = page.locator("#gt2ThuKetQua").inner_text()
    assert "Official" in chu and "Trial" in chu and "Overview" in chu
    assert "no place changed" in page.locator("#gt2SsKetLuan").inner_text()
    _sach(page)
    page.locator("#gt2ThuXuatHtml").click()
    page.wait_for_function("document.querySelector('#gt2ThuXuat').textContent.length > 0")
    assert "Saved" in page.locator("#gt2ThuXuat").inner_text()
    assert not loi, loi


def test_dung_tieu_chi_cua_lan_thu_hoi_truoc_roi_luu_khong_doi_ket_qua(mo):
    page, api, db, loi = mo()
    assert not page.locator("#gt2ThuApDung").is_visible()          # chưa có lần thử nào
    page.select_option("#gt2TcPriority", "tier")
    page.locator("#gt2ThuChay").click()
    page.wait_for_selector("#gt2ThuApDungDs button")
    truoc = _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi")
    cu = cau_hinh_ws.doc_cau_hinh(db)["rules"]["priority"]
    page.locator("#gt2ThuApDungDs button").click()
    chu = page.locator("#gt2ThuApDungXacNhan").inner_text()
    assert "Thứ tự sẽ là" in chu and page.locator("#gt2ThuApDungXacNhan li").count() >= 1
    page.locator("#gt2ThuApDungXacNhan button", has_text="Không dùng").click()   # UX4-L4                          # hủy: không ghi gì
    assert cau_hinh_ws.doc_cau_hinh(db)["rules"]["priority"] == cu
    page.locator("#gt2ThuApDungDs button").click()
    page.locator("#gt2ThuApDungXacNhanNut").click()
    page.wait_for_function("document.querySelector('#gt2ThuApDungPhanHoi').innerText.length > 0")
    assert page.locator("#gt2ThuApDungPhanHoi").inner_text().startswith("Đã lưu. Kết quả chính thức chưa đổi")   # UX4-L4: đổi chữ
    assert cau_hinh_ws.doc_cau_hinh(db)["rules"]["priority"] == "tier"
    assert _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi") == truoc
    _sach(page)
    assert not loi, loi
