"""MT1 (gom): khối "Để dùng Huy chương…" ở Cài đặt dựng lại thành BẢNG đặt loại CLB. Chromium thật qua `browser_host`.

Hợp đồng giao diện: mỗi CLB một dòng (`tr.ux1a-ss-dong[data-clb]`) với ba nút loại có trạng thái chọn (`aria-pressed`);
nhóm theo buổi (`tr.ux1a-ss-buoi[data-buoi]`, `data-co-tu-do`) kèm dấu cần/đã có CLB Tự do; điểm sàn của Tuyển chọn
nhập ngay tại dòng; bộ đếm `#ux1aSsDem`; ba câu giải thích loại; không còn ô chọn xổ xuống. Chỉ giao diện: vẫn lưu qua
`dat_loai_clb`. Dữ liệu MÔ PHỎNG (`SO_NHAP_FA_MAU_120HS.xlsx`: 8 CLB, hai buổi).
"""

import base64
import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")


def _mo(mo_trang, doi_ten=False):  # noqa: F811
    """Sổ FA mẫu, xoá loại + điểm sàn của mọi CLB, bật Huy chương, mở Cài đặt."""
    page, api, goc, loi = mo_trang()
    with open(SO_FA, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    c = sqlite3.connect(api.db_path)
    c.execute("UPDATE clubs SET loai = NULL, diem_san = NULL")
    if doi_ten:                                    # tên chứa nhãn loại cũ không được gây hiểu lầm cho phần vẽ
        c.execute("UPDATE clubs SET name = name || ' (Giới hạn A)'")
    c.commit()
    c.close()
    assert api.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})["ok"]
    page.reload()
    page.wait_for_selector("#dropZone")
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#ux1aSanSang table.ux1a-ss-bang")
    return page, api, loi


def _loai_db(api):
    c = sqlite3.connect(api.db_path)
    try:
        return dict(c.execute("SELECT club_id, loai FROM clubs"))
    finally:
        c.close()


def test_bang_co_mot_dong_moi_clb_ba_nut_co_trang_thai_va_khong_con_o_xo_xuong(mo_trang):  # noqa: F811
    page, api, loi = _mo(mo_trang)
    n = len(_loai_db(api))
    assert page.locator("#ux1aSanSang tr.ux1a-ss-dong[data-clb]").count() == n
    assert page.locator("#ux1aSanSang tr.ux1a-ss-dong[data-clb] button[data-loai]").count() == 3 * n
    assert page.locator('#ux1aSanSang button[data-loai][aria-pressed="true"]').count() == 0
    assert page.locator("#ux1aSanSang select").count() == 0                      # bỏ cách thứ hai cho cùng một việc
    assert page.locator("#ux1aSsDem").inner_text().strip() == "Đã chọn loại: 0/%d CLB" % n
    giai_thich = page.locator("#ux1aSsGiaiThich").inner_text()
    for tu in ("Tự do", "Giới hạn", "Tuyển chọn"):
        assert tu in giai_thich
    assert page.locator("#ux1aSanSang tr.ux1a-ss-buoi[data-buoi]").count() == 2   # hai buổi, mỗi buổi một dòng trạng thái
    assert page.locator('#ux1aSanSang tr.ux1a-ss-buoi[data-co-tu-do="true"]').count() == 0
    assert not loi, loi


def test_bam_loai_giu_dong_sang_nut_da_chon_dem_tang_va_giu_tieu_diem(mo_trang):  # noqa: F811
    page, api, loi = _mo(mo_trang)
    n = len(_loai_db(api))
    dong = page.locator("#ux1aSanSang tr.ux1a-ss-dong[data-clb]").first
    cid = dong.get_attribute("data-clb")
    dong.locator('button[data-loai="GIOI_HAN"]').click()
    sel = '#ux1aSanSang tr[data-clb="%s"] button[data-loai="GIOI_HAN"]' % cid
    page.wait_for_function("s => document.querySelector(s).getAttribute('aria-pressed') === 'true'", arg=sel)
    assert page.locator("#ux1aSanSang tr.ux1a-ss-dong[data-clb]").count() == n    # dòng KHÔNG biến mất
    assert page.locator("#ux1aSsDem").inner_text().strip() == "Đã chọn loại: 1/%d CLB" % n
    assert page.evaluate("s => document.activeElement === document.querySelector(s)", sel)   # tiêu điểm không rơi mất
    assert _loai_db(api)[cid] == "GIOI_HAN"
    assert not loi, loi


def test_buoi_doi_dau_khi_co_clb_tu_do(mo_trang):  # noqa: F811
    page, api, loi = _mo(mo_trang)
    buoi = page.locator("#ux1aSanSang tr.ux1a-ss-buoi[data-buoi]").first
    b = buoi.get_attribute("data-buoi")
    assert buoi.get_attribute("data-co-tu-do") == "false"
    page.locator('#ux1aSanSang tr.ux1a-ss-dong[data-buoi="%s"] button[data-loai="TU_DO"]' % b).first.click()
    page.wait_for_selector('#ux1aSanSang tr.ux1a-ss-buoi[data-buoi="%s"][data-co-tu-do="true"]' % b)
    assert not loi, loi


def test_tuyen_chon_hien_o_diem_san_ngay_tai_dong_va_luu_duoc(mo_trang):  # noqa: F811
    page, api, loi = _mo(mo_trang)
    dong = page.locator("#ux1aSanSang tr.ux1a-ss-dong[data-clb]").first
    cid = dong.get_attribute("data-clb")
    assert dong.locator("input[type=number]").count() == 0                       # chưa chọn Tuyển chọn thì chưa có ô sàn
    dong.locator('button[data-loai="TUYEN_CHON"]').click()
    o = page.locator('#ux1aSanSang tr[data-clb="%s"] input[type=number]' % cid)
    o.wait_for(state="visible")                                                  # hiện NGAY trong cùng dòng
    o.fill("6")
    page.locator('#ux1aSanSang tr[data-clb="%s"] button[data-luu-san]' % cid).click()
    page.wait_for_function(
        "s => document.querySelector(s) && document.querySelector(s).value === '6'",
        arg='#ux1aSanSang tr[data-clb="%s"] input[type=number]' % cid)
    c = sqlite3.connect(api.db_path)
    try:
        assert c.execute("SELECT loai, diem_san FROM clubs WHERE club_id = ?", (cid,)).fetchone() == ("TUYEN_CHON", 6)
    finally:
        c.close()
    assert not loi, loi


def test_ten_clb_chua_nhan_loai_cu_khong_lam_lech_trang_thai_nut(mo_trang):  # noqa: F811
    page, api, loi = _mo(mo_trang, doi_ten=True)
    assert page.locator('#ux1aSanSang button[data-loai][aria-pressed="true"]').count() == 0   # nút theo cột `loai`, không theo tên
    assert not loi, loi


def test_dat_xong_het_thi_hien_san_sang_va_bang_cai_dat_dong_bo(mo_trang):  # noqa: F811
    page, api, loi = _mo(mo_trang)
    for buoi in {r.get_attribute("data-buoi") for r in page.locator("#ux1aSanSang tr.ux1a-ss-buoi[data-buoi]").all()}:
        page.locator('#ux1aSanSang tr.ux1a-ss-dong[data-buoi="%s"] button[data-loai="TU_DO"]' % buoi).first.click()
        page.wait_for_selector('#ux1aSanSang tr.ux1a-ss-buoi[data-buoi="%s"][data-co-tu-do="true"]' % buoi)
    while page.locator('#ux1aSanSang button[data-loai="GIOI_HAN"][aria-pressed="false"]').count() \
            and page.locator("#ux1aSanSang table.ux1a-ss-bang").count():
        n = page.locator('#ux1aSanSang button[aria-pressed="true"]').count()
        page.locator('#ux1aSanSang tr.ux1a-ss-dong:not(:has(button[aria-pressed="true"])) button[data-loai="GIOI_HAN"]').first.click()
        page.wait_for_function(
            "n => document.querySelectorAll('#ux1aSanSang button[aria-pressed=\"true\"]').length > n"
            " || !!document.getElementById('ux1aSanSangXong')", arg=n)
    page.wait_for_selector("#ux1aSanSangXong")
    assert api.get_san_sang_huy_chuong()["data"]["san_sang"] is True
    assert not loi, loi
