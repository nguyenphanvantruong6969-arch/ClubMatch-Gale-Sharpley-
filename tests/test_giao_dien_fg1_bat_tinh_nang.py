"""FG-1 (STEP0, spec §3) -> UX1A-L2b, phần giao diện (Playwright + Chromium): bật/tắt tính năng sau khi xếp.
Trước đây là hộp thoại 5 ô ở menu ⋯; nay mỗi tính năng là MỘT HÀNH ĐỘNG ở thẻ "Chi tiết và xuất tệp", chỉ hiện ở chế
độ Huy chương, ghi qua `update_workspace_config` một phần. Dữ liệu MÔ PHỎNG."""
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

import cau_hinh_ws as ch  # noqa: E402
from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

NHAN_PHAN_HOI = "Thu phản hồi"


def _luat(api):
    return api.get_workspace_config()["data"]["config"]["rules"]


def _mo_the_chi_tiet(page):
    page.locator('[data-tab="others"]').click()
    page.wait_for_selector("#xuatPanel")


def test_khong_fa_thi_khong_co_hanh_dong_sau_khi_xep(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo_the_chi_tiet(page)
    assert page.locator("#ux1aSauXep").is_hidden()                # backend: cờ sau khi xếp cần fa_daa
    assert page.locator("#ux1aSauXepLuoi button").count() == 0
    assert all(_luat(api)[k] is False for k in ch.CO_SAU_XEP)
    assert not loi, loi


def test_bat_phan_hoi_roi_khung_hien_o_the_chi_tiet(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    _mo_the_chi_tiet(page)
    page.locator("#ux1aSauXep").wait_for(state="visible")
    assert page.locator("#ux1aSx_fa_phan_hoi").inner_text().strip() == NHAN_PHAN_HOI
    page.locator("#ux1aSx_fa_phan_hoi").click()
    page.wait_for_selector("#phanHoiTongPanel:not([hidden])")      # không cần khởi động lại
    assert _luat(api)["fa_phan_hoi"] is True
    assert not loi, loi


def test_so_ngay_ngoai_khoang_giu_nguyen_va_hien_loi(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    _mo_the_chi_tiet(page)
    page.locator("#ux1aSxNgay").wait_for()
    page.locator("#ux1aSxNgay").fill("30")
    page.locator("#ux1aSx_fa_khieu_nai").click()
    page.wait_for_selector(".toast.is-error")
    assert "14" in page.locator(".toast.is-error").first.inner_text()
    assert _luat(api)["fa_khieu_nai_so_ngay"] == 3 and _luat(api)["fa_khieu_nai"] is False
    assert not loi, loi
