"""UX1A-L5, phần giao diện: sổ có cột Huy chương mà chế độ tắt -> nói rõ + một nút bật; cảnh báo gộp; một sổ mẫu (SM2);
lỗi chạy chỉ sang Cài đặt. Chromium thật; dữ liệu MÔ PHỎNG."""

import os

import openpyxl
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
SO_THUONG = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


def _luat(api):
    return api.get_workspace_config()["data"]["config"]["rules"]


def _tha(page, duong):
    page.locator("#fileAny").set_input_files([duong])
    page.wait_for_selector(".queue-row .so-nhap-canh-bao, #btnImportAll:not([hidden])")


def test_so_huy_chuong_che_do_tat_co_cau_noi_ro_va_mot_nut_bat(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _tha(page, SO_FA)
    page.wait_for_selector("#btnBatHuyChuong")
    chu = page.locator(".queue-row .so-nhap-canh-bao").inner_text()
    assert "Huy chương" in chu and "Cài đặt" in chu
    assert _luat(api)["fa_daa"] is False                              # chưa bật ngầm
    page.locator("#btnBatHuyChuong").click()
    page.wait_for_selector("#btnBatHuyChuong", state="detached")
    luat = _luat(api)
    assert luat["fa_daa"] is True and luat["wharton"] is True
    assert page.locator("#btnImportAll").is_visible()                 # sổ vẫn chờ, đã đọc thử lại
    assert not loi, loi


def test_so_thuong_khong_co_nut_bat_huy_chuong(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _tha(page, SO_THUONG)
    page.wait_for_selector("#btnImportAll:not([hidden])")
    assert page.locator("#btnBatHuyChuong").count() == 0
    assert not loi, loi


def test_nap_so_huy_chuong_che_do_tat_canh_bao_diem_gop_mot_dong(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _tha(page, SO_FA)
    page.locator("#btnImportAll").click()
    page.wait_for_selector(".queue-row.is-done")
    page.wait_for_selector("#importWarnings:not([hidden])")
    dong = page.locator("#importWarnings .canh-bao-tom-tat")
    assert dong.count() == 1 and "434" in dong.inner_text() and "chưa đặt đủ điểm quyết tâm" in dong.inner_text()
    # danh sách gom bên dưới chỉ còn vài ví dụ (không liệt kê 434 em)
    assert page.locator("#importWarnings .canh-bao-dong", has_text="còn thiếu").count() <= 5
    assert not loi, loi


def test_mot_nut_so_mau_day_du_cau_truc(mo_trang, monkeypatch):  # noqa: F811
    """SM2-L2 (thay ca "hai nút" của UX1A-L5): MỘT nút; bấm gọi `tao_so_nhap_mau` đúng một lần, hiện dấu ✓, sổ đủ
    cột Loại, sheet Giữ chỗ và từ điển cột."""
    page, api, goc, loi = mo_trang()
    monkeypatch.setattr(api, "mo_thu_muc", lambda p: {"ok": True})
    goi = []
    goc_ham = api.tao_so_nhap_mau
    monkeypatch.setattr(api, "tao_so_nhap_mau", lambda *a: goi.append(a) or goc_ham(*a))
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    assert page.locator("#btnTaiSoMauHuyChuong").count() == 0
    page.locator("#btnTaiSoMau").click()
    page.wait_for_function(
        "document.getElementById('feedbackImportAll').textContent.indexOf('SO_NHAP_CLB') !== -1")
    page.wait_for_selector("#btnTaiSoMau .ux2-xong", state="attached")
    assert len(goi) == 1, goi
    duong = page.locator("#feedbackImportAll").inner_text().split("→")[-1].strip()
    wb = openpyxl.load_workbook(duong, read_only=True)
    assert "Giữ chỗ" in wb.sheetnames
    chu = str([[c for c in r] for ws in wb.worksheets for r in ws.iter_rows(values_only=True)])
    assert "Loại" in chu and "TỪ ĐIỂN CỘT" in chu
    assert not loi, loi


def test_loi_chay_bi_chan_chi_huong_ve_cai_dat_huy_chuong(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.import_so_nhap(__import__("base64").b64encode(open(SO_FA, "rb").read()).decode())["ok"]
    page.evaluate("refreshDashboardStats()")
    page.wait_for_function("() => !document.getElementById('btnRun').disabled")
    page.locator("#btnRun").click()
    page.wait_for_selector("#btnMoTinhNangTuLoi")
    chu = page.locator("#logBox").inner_text()
    assert "bật chế độ huy chương" in chu
    page.locator("#btnMoTinhNangTuLoi").click()
    page.wait_for_selector("#ux1aHuyChuong", state="visible")
    assert not loi, loi


def test_khong_co_workspace_thi_khong_hien_nut_bat_huy_chuong(api):
    """UX1A-L5 (sửa nhỏ): chưa mở workspace thì không có đường cấu hình -> chỉ có câu nói rõ, không có nút."""
    from playwright.sync_api import sync_playwright

    import browser_host
    from _trinh_duyet import CHROMIUM
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator("#fileAny").set_input_files([SO_FA])
        page.wait_for_selector(".queue-row .so-nhap-canh-bao")
        assert "Huy chương" in page.locator(".queue-row .so-nhap-canh-bao").inner_text()
        assert page.locator("#btnBatHuyChuong").count() == 0
        br.close()
    assert not loi, loi
