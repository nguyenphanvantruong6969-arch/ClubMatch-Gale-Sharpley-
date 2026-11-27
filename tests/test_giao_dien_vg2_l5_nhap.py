"""VG2-L5, giao diện (Chromium thật): nhập sổ có Huy chương khi chế độ tắt phải hỏi lại. Dữ liệu MÔ PHỎNG."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")


def test_nhap_so_huy_chuong_khi_che_do_tat_phai_hoi_lai_huy_thi_khong_nap(mo_trang):  # noqa: F811
    """VG2-L5: sổ có Huy chương mà chế độ tắt -> «Nhập» hỏi lại; «Huỷ» không nạp gì; «Vẫn nhập» nạp như cũ."""
    page, api, goc, loi = mo_trang()
    page.locator("#fileAny").set_input_files([SO_FA])
    page.wait_for_selector("#btnImportAll:not([hidden])")
    page.locator("#btnImportAll").click()
    bar = page.locator("#xoaKemBar")
    bar.wait_for()
    assert "Bật chế độ huy chương" in bar.inner_text()
    assert page.evaluate("document.activeElement.textContent") in ("Huỷ", "Cancel")      # mặc định an toàn
    bar.locator(".btn-ghost").click()
    assert page.locator("#xoaKemBar").count() == 0
    assert api.get_dashboard_status()["data"]["n_clubs"] == 0
    page.locator("#btnImportAll").click()
    page.locator("#xoaKemBar .btn-primary").click()
    page.wait_for_selector(".queue-row.is-done")
    assert api.get_dashboard_status()["data"]["n_clubs"] > 0
    assert not loi, loi
