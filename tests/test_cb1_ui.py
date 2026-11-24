"""CB1-L3 — giao diện khung "Văn bản phương án xếp" (tab Cách xếp của Quản lý). Chromium thật qua `browser_host`.

Một trang dùng chung cho cả tệp (fixture theo module): nạp sổ MÔ PHỎNG 120 em, chạy xếp chính thức, rồi đi tuần tự qua
các bước: chưa chốt (bản chốt khoá kèm lý do, ô hạt giống tắt) → Huỷ không chốt → chốt có hộp xác nhận → xuất hai bản
(không hạt giống mặc định, có khi tick) → đổi phương án sau chốt thì hiện cảnh báo → chốt lại hỏi lại.
"""

import base64
import os
import re
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
pypdf = pytest.importorskip("pypdf")

from test_ws_giao_dien import CHROMIUM, GOC, _dung  # noqa: E402

import browser_host  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
SEED = 27182818


@pytest.fixture(scope="module")
def trang(tmp_path_factory):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    tmp = tmp_path_factory.mktemp("cb1ui")
    api, goc = _dung(tmp)
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert api.run_pipeline(seed=SEED)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone")
    page.locator('.nav-item[data-tab="admin"]').click()
    page.click("#qlTabCachXep")
    page.wait_for_selector("#paPanel", state="visible")
    page.wait_for_function("document.getElementById('paTrangThai').textContent.trim() !== ''")
    yield page, api, loi
    br.close()
    pw.stop()


def _chu_pdf(duong):
    return "\n".join(p.extract_text() for p in pypdf.PdfReader(duong).pages)


def _duong(page):
    page.wait_for_function("/Đã lưu: /.test(document.getElementById('paPhanHoi').textContent)")
    m = re.search(r"Đã lưu: (.+?\.pdf)", page.locator("#paPhanHoi").inner_text().replace("\n", " "))
    assert m, page.locator("#paPhanHoi").inner_text()
    return m.group(1).strip()


def _chot_db(api):
    c = sqlite3.connect(api.db_path)
    try:
        return c.execute("SELECT value FROM workspace_settings WHERE key = 'chot_phuong_an'").fetchall()
    finally:
        c.close()


def test_1_chua_chot_ban_chot_khoa_kem_ly_do_hat_giong_tat(trang):
    page, api, loi = trang
    assert "Chưa chốt" in page.locator("#paTrangThai").inner_text()
    assert page.locator("#paXuatChot").is_disabled() and page.locator("#paXuatDuKien").is_enabled()
    assert page.locator("#paLyDo").is_visible() and page.locator("#paLyDo").inner_text().strip()
    assert page.locator("#paHatGiong").is_disabled() and not page.locator("#paHatGiong").is_checked()
    assert page.locator("#paChot").inner_text().strip() == "Chốt phương án"


def test_2_huy_thi_khong_chot(trang):
    page, api, loi = trang
    page.click("#paChot")
    page.wait_for_selector("#paXacNhan", state="visible")
    assert page.locator("#paXacNhan li").count() >= 1       # có liệu luật sẽ chốt
    page.click("#paHuy")
    assert not page.locator("#paXacNhan").is_visible()
    assert _chot_db(api) == []


def test_3_chot_co_xac_nhan_roi_mo_khoa_ban_chot(trang):
    page, api, loi = trang
    page.click("#paChot")
    page.click("#paXacNhanChot")
    page.wait_for_function("/Đã chốt/.test(document.getElementById('paTrangThai').textContent)")
    assert len(_chot_db(api)) == 1
    assert page.locator("#paXuatChot").is_enabled()
    assert page.locator("#paHatGiong").is_enabled() and not page.locator("#paHatGiong").is_checked()
    assert page.locator("#paChot").inner_text().strip() == "Chốt lại phương án"


def test_4_xuat_du_kien_khong_hat_giong_va_ban_chot_chi_co_khi_tick(trang):
    page, api, loi = trang
    page.click("#paXuatDuKien")
    p1 = _duong(page)
    assert "BẢN DỰ KIẾN" in _chu_pdf(p1) and str(SEED) not in _chu_pdf(p1)
    page.evaluate("document.getElementById('paPhanHoi').textContent = ''")
    page.click("#paXuatChot")
    p2 = _duong(page)
    assert "BẢN CHỐT" in _chu_pdf(p2) and str(SEED) not in _chu_pdf(p2)
    page.evaluate("document.getElementById('paPhanHoi').textContent = ''")
    page.check("#paHatGiong")
    page.click("#paXuatChot")
    p3 = _duong(page)
    assert str(SEED) in _chu_pdf(p3)
    assert p1 != p2 != p3


def test_5_doi_phuong_an_sau_chot_hien_canh_bao(trang):
    page, api, loi = trang
    assert not page.locator("#paCanhBao").is_visible()
    assert api.chon_muc_tieu("co_hoi")["ok"]
    page.click("#qlTabClb")
    page.click("#qlTabCachXep")
    page.wait_for_selector("#paCanhBao", state="visible")
    assert "đã đổi sau khi chốt" in page.locator("#paCanhBao").inner_text()


def test_6_chot_lai_hoi_lai_va_xoa_canh_bao(trang):
    page, api, loi = trang
    page.click("#paChot")
    assert "chốt trước đó" in page.locator("#paXacNhan").inner_text()
    page.click("#paXacNhanChot")
    # còn cảnh báo "lần xếp chính thức không dùng phương án đã chốt" (xếp bằng luật cũ), nhưng hết cảnh báo "đã đổi sau chốt"
    page.wait_for_function("!/đã đổi sau khi chốt/.test(document.getElementById('paCanhBao').textContent)")
    assert "không dùng phương án đã chốt" in page.locator("#paCanhBao").inner_text()
    assert len(_chot_db(api)) == 1


def test_7_khong_loi_trang(trang):
    page, api, loi = trang
    assert loi == []
