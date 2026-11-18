"""SG-2 (C1) -> UX1A-L2b, phần giao diện (Playwright + Chromium): mục ⋯ "Cài đặt…" của workspace mở ba thẻ;
"Chia 100 điểm" = dùng điểm quyết tâm (mặc định), "Chỉ xếp thứ tự" tắt nó, "Huy chương" luôn kèm nó. Lưu ngay khi bấm
qua `update_workspace_config`. Dữ liệu MÔ PHỎNG."""
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)


def _mo_hop_thoai(page):
    page.locator("#btnWorkspace").click()
    page.locator('tr[data-slug="truong-hoc"] .menu-khac > summary').click()
    page.locator('tr[data-slug="truong-hoc"]').get_by_text(re.compile("^Cài đặt…$")).click()
    hop = page.get_by_role("dialog")
    hop.wait_for()
    page.wait_for_selector('#ux1aWsThan .ux1a-the[aria-checked="true"]')      # cấu hình đã nạp xong
    return hop


def test_khong_fa_o_diem_quyet_tam_bat_va_tat_duoc(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    hop = _mo_hop_thoai(page)
    assert page.locator("#ux1aWsChia100").get_attribute("aria-checked") == "true"      # điểm quyết tâm: bật (mặc định)
    hop.get_by_role("radio", name=re.compile("Chỉ xếp thứ tự")).click()
    page.wait_for_function("document.getElementById('ux1aWsChiXep').getAttribute('aria-checked') === 'true'")
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is False
    assert not loi, loi


def test_co_fa_o_diem_quyet_tam_khoa_kem_ly_do(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    _mo_hop_thoai(page)
    assert page.locator("#ux1aWsHuyChuong").get_attribute("aria-checked") == "true"
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is True     # huy chương luôn kèm điểm quyết tâm
    page.get_by_role("button", name="Xong").click()
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is True
    assert not loi, loi


def test_khung_loi_chay_bi_chan_co_nut_mo_hop_thoai(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    page.evaluate("""() => showLog([
        {code: "wharton_ho_so_chua_hop_le", params: {n: 1}},
        {code: "wharton_chua_dung_het", params: {student_id: "h1", quy: 2, thieu: 100, buoi: "_"}}])""")
    nut = page.locator("#btnMoTinhNangTuLoi")
    nut.wait_for()
    assert "Chỉ xếp thứ tự" in page.locator("#logBox").inner_text()
    nut.click()
    page.wait_for_selector("#view-admin.is-active")
    page.wait_for_selector("#ux1aChiXep", state="visible")                           # mở thẳng trang Cài đặt
    assert not loi, loi
