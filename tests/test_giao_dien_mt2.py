"""MT2-L3: công tắc "Chia CLB theo loại" ở Quản lý › Câu lạc bộ — Chromium thật qua `browser_host`.

Hợp đồng: mặc định TẮT (`#mt2CongTac` không tick, bảng loại ẩn); bật thì hiện bảng đặt loại (`#mt2Bang`, dùng lại bảng MT1) và
lưu `rules.chia_loai`; tắt thì ẩn bảng nhưng `clubs.loai` còn nguyên; tên CLB chứa HTML không chạy script; bấm đúp không làm
lệch giao diện so với cấu hình đã lưu. Dữ liệu MÔ PHỎNG (`SO_NHAP_FA_MAU_120HS.xlsx`).
"""

import base64
import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
XSS = '<img src=x onerror="window.__xss=1">'


def _sql(api, cau, tham=()):
    c = sqlite3.connect(api.db_path)
    try:
        r = c.execute(cau, tham).fetchall()
        c.commit()
        return r
    finally:
        c.close()


@pytest.fixture
def trang(mo_trang):  # noqa: F811
    """MỘT cách mở dùng chung: sổ FA mẫu, xoá loại, tên CLB đầu chứa HTML, mặc định (chia_loai tắt), mở Quản lý."""
    page, api, goc, loi = mo_trang()
    with open(SO_FA, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    _sql(api, "UPDATE clubs SET loai = NULL, diem_san = NULL")
    _sql(api, "UPDATE clubs SET name = ? WHERE club_id = (SELECT MIN(club_id) FROM clubs)", (XSS,))
    page.reload()
    page.wait_for_selector("#dropZone")
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#mt2ChiaLoai:not([hidden])")
    return page, api, loi


def _hieu_luc(api):
    return api.get_chia_loai()["data"]["hieu_luc"]


def _bat(page, api, bat=True):
    o = page.locator("#mt2CongTac")
    if o.is_checked() != bat:
        o.click()
    page.wait_for_function(
        "b => document.getElementById('mt2CongTac').checked === b && !document.getElementById('mt2CongTac').disabled",
        arg=bat)
    if bat:
        page.wait_for_selector("#mt2Bang table.ux1a-ss-bang")


def test_mac_dinh_tat_it_dieu_khien_va_khong_loi(trang):
    page, api, loi = trang
    assert page.locator("#mt2CongTac").is_checked() is False and _hieu_luc(api) is False
    assert page.locator("#mt2Bang").is_hidden()
    # ngân sách Hick của khối mới khi TẮT: đúng MỘT điều khiển (công tắc), không nút vàng
    assert page.locator("#mt2ChiaLoai input:visible, #mt2ChiaLoai button:visible, #mt2ChiaLoai select:visible").count() == 1
    assert page.locator("#mt2ChiaLoai .btn-primary").count() == 0
    assert "Chia CLB theo loại" in page.locator("#mt2ChiaLoai").inner_text()
    assert not loi, loi


def test_bat_hien_bang_luu_cau_hinh_cot_loai_va_ten_html_khong_chay(trang):
    page, api, loi = trang
    n = _sql(api, "SELECT COUNT(*) FROM clubs")[0][0]
    _bat(page, api)
    assert _hieu_luc(api) is True
    assert page.locator("#mt2Bang tr.ux1a-ss-dong[data-clb]").count() == n
    assert XSS in page.locator("#mt2Bang .ux1a-ss-ten").first.inner_text()          # hiện như CHỮ
    assert page.evaluate("window.__xss === undefined")                              # không chạy script
    page.wait_for_selector("#adminClubTableBody tr td.cot-fa")                      # cột Loại hiện ở bảng CLB
    assert not loi, loi


def test_dat_loai_roi_tat_bat_lai_van_con_loai(trang):
    page, api, loi = trang
    _bat(page, api)
    dong = page.locator("#mt2Bang tr.ux1a-ss-dong[data-clb]").nth(1)
    cid = dong.get_attribute("data-clb")
    dong.locator('button[data-loai="GIOI_HAN"]').click()
    sel = '#mt2Bang tr[data-clb="%s"] button[data-loai="GIOI_HAN"]' % cid
    page.wait_for_function("s => document.querySelector(s).getAttribute('aria-pressed') === 'true'", arg=sel)
    assert page.evaluate("s => document.activeElement === document.querySelector(s)", sel)
    _bat(page, api, False)
    assert page.locator("#mt2Bang").is_hidden() and _hieu_luc(api) is False
    assert _sql(api, "SELECT loai FROM clubs WHERE club_id = ?", (cid,)) == [("GIOI_HAN",)]
    _bat(page, api, True)
    page.wait_for_function("s => document.querySelector(s).getAttribute('aria-pressed') === 'true'", arg=sel)
    assert not loi, loi


def test_bam_dup_khong_lech_so_voi_cau_hinh_da_luu(trang):
    page, api, loi = trang
    page.locator("#mt2CongTac").dblclick()
    page.wait_for_function("!document.getElementById('mt2CongTac').disabled")
    page.wait_for_timeout(300)
    assert page.locator("#mt2CongTac").is_checked() is _hieu_luc(api)
    assert page.locator("#mt2Bang").is_visible() is _hieu_luc(api)
    assert not loi, loi


def test_loi_backend_dua_cong_tac_ve_trang_thai_that(trang):
    page, api, loi = trang
    api.update_workspace_config = lambda *a, **k: {      # backend từ chối: ok=false theo hợp đồng
        "ok": False, "data": None, "errors": [{"code": "error_saving_club", "params": {"detail": "x"}}]}
    page.locator("#mt2CongTac").click()
    page.wait_for_function("!document.getElementById('mt2CongTac').disabled")
    page.wait_for_timeout(300)
    assert page.locator("#mt2CongTac").is_checked() is False and _hieu_luc(api) is False   # công tắc quay về
    assert page.locator("#mt2Bang").is_hidden()


def test_che_do_huy_chuong_khoa_cong_tac_va_khong_ve_bang_trung(trang):
    page, api, loi = trang
    assert api.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})["ok"]
    page.reload()
    page.wait_for_selector("#dropZone")
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_function("document.getElementById('mt2CongTac') && document.getElementById('mt2CongTac').disabled")
    assert page.locator("#mt2CongTac").is_checked() is True
    assert page.locator("#mt2Bang").is_hidden()
    assert not loi, loi
