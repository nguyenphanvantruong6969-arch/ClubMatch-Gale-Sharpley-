"""FA-UI-1 (Playwright + Chromium): công tắc "Xếp theo loại CLB và huy chương" (`rules.fa_daa`) ở bước luật
của trình hướng dẫn tạo không gian làm việc.

  * (UX1A-L2b) thẻ `#wzHuyChuong` không chọn sẵn, nhãn tiếng Việt / tiếng Anh, không có chữ "Wharton" hay "FA-DAA";
  * bật rồi tạo -> `rules.fa_daa` lưu true, hàng xem lại `#rvFaDaa` ghi "Bật"; lần sau mở bước luật thì
    vẫn tích (đi về giữ nguyên); tắt -> không có khoá fa_daa = true;
  * bật FA mà tắt điểm quyết tâm -> backend từ chối bằng lỗi sẵn có (`ws_du_lieu_sai`), lỗi hiện trên màn hình.
Dữ liệu MÔ PHỎNG.
"""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_wharton_giao_dien import _cho_ten, _toi_buoc_luat  # noqa: E402
from test_ws_wharton_giao_dien import mo_trang  # noqa: E402,F401 (fixture)


def test_o_fa_tat_san_va_nhan_khong_biet_ngu(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, _, loi = mo_trang()
    _toi_buoc_luat(page)
    o = page.locator("#wzHuyChuong")
    assert o.count() == 1 and o.get_attribute("aria-checked") == "false"
    nhan = page.locator("#wzHuyChuong .ux1a-the-tt").inner_text()
    assert nhan == "Huy chương"
    hop = page.locator("#wsHop").inner_text()
    assert "Wharton" not in hop and "FA-DAA" not in hop
    assert not loi, loi


def test_nhan_tieng_anh(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, _, loi = mo_trang()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    _toi_buoc_luat(page, "Round")
    assert page.locator("#wzHuyChuong .ux1a-the-tt").inner_text() == "Medals"
    assert not loi, loi


def test_bat_roi_tao_thi_luu_fa_daa_va_quay_lai_van_tich(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt FA")
    page.locator("#wzHuyChuong").click()
    page.locator("#wzTiep").click()                          # sang bước xem lại
    assert page.locator("#rvFaDaa").inner_text() == "Bật"
    page.locator("#wzLui").click()
    page.wait_for_selector("#wzHuyChuong")
    assert page.locator("#wzHuyChuong").get_attribute("aria-checked") == "true"   # đi về giữ nguyên
    page.locator("#wzTiep").click()
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt FA")
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    assert rules["fa_daa"] is True and rules["wharton"] is True
    assert not loi, loi


def test_mac_dinh_tat_va_xem_lai_ghi_tat(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt thường")
    page.locator("#wzTiep").click()
    assert page.locator("#rvFaDaa").inner_text() == "Tắt"
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt thường")
    assert api.get_workspace_config()["data"]["config"]["rules"].get("fa_daa") is not True
    assert not loi, loi


def test_chon_huy_chuong_sau_chi_xep_van_luu_ca_wharton_va_fa(mo_trang):  # noqa: F811 (fixture dùng lại)
    # UX1A-L2b: tổ hợp "FA bật, điểm quyết tâm tắt" không còn tạo được từ giao diện (thẻ Huy chương
    # luôn kèm điểm quyết tâm). Việc backend từ chối tổ hợp đó vẫn do tests/test_fa_n3_loi_diem_quyet_tam.py giữ.
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt FA2")
    page.locator("#wzChiXep").click()
    page.locator("#wzHuyChuong").click()
    page.locator("#wzTiep").click()
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt FA2")
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    assert rules["fa_daa"] is True and rules["wharton"] is True
    assert not loi, loi
