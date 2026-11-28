"""SF-B lô 1: bản hồi quy nhỏ cho ST-B-001 / ST-B-002 / ST-B-008 (bản đầy đủ: tests_stress/b/).
Chromium thật qua `browser_host`, MỘT fixture trang dùng chung; sổ nhập MÔ PHỎNG."""

import base64
import os
import time

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        yield page, loi
        br.close()


def test_st_b_001_bang_ket_qua_het_hang_cu_khi_tai_cham(trang, api):
    page, loi = trang
    assert api.run_pipeline(seed=42)["ok"]
    page.locator('.nav-item[data-tab="results"]').click()
    page.wait_for_function("document.querySelectorAll('#kqThan tr:not(.ux2-khung-hang)').length > 0")
    goc = api.get_club_fill_stats
    api.get_club_fill_stats = lambda *a: (time.sleep(1.5), goc(*a))[1]
    page.evaluate("loadKetQuaTab()")
    page.wait_for_timeout(150)
    assert page.evaluate("document.querySelectorAll('#kqThan tr:not(.ux2-khung-hang)').length") == 0
    api.get_club_fill_stats = goc
    page.wait_for_function("document.querySelectorAll('#kqThan tr:not(.ux2-khung-hang)').length > 0")
    assert not loi, loi


def test_st_b_002_cong_tac_chia_loai_ve_lai_khi_ap_dung_che_do(trang, api, monkeypatch):
    page, loi = trang
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#mt2CongTac", state="attached")
    page.wait_for_function("document.getElementById('mt2CongTac').disabled === false")
    chuan = {"ok": True, "data": {"chia_loai": False, "fa_daa": True, "hieu_luc": True}, "errors": []}
    monkeypatch.setattr(api, "get_chia_loai", lambda: chuan)
    page.evaluate("ux1aApDungSong({rules: {fa_daa: true}})")
    page.wait_for_function("document.getElementById('mt2CongTac').disabled === true")
    chuan2 = {"ok": True, "data": {"chia_loai": False, "fa_daa": False, "hieu_luc": False}, "errors": []}
    monkeypatch.setattr(api, "get_chia_loai", lambda: chuan2)
    page.evaluate("ux1aApDungSong({rules: {}})")
    page.wait_for_function("document.getElementById('mt2CongTac').disabled === false")
    assert not loi, loi


def test_st_b_008_cau_canh_bao_khong_hua_chan_chay(trang, api, monkeypatch):
    goc = api.get_data_health_report

    def chan():
        kq = goc()
        kq["data"] = dict(kq["data"], n_high=1, n_warnings=max(1, kq["data"]["n_warnings"]))
        return kq
    monkeypatch.setattr(api, "get_data_health_report", chan)
    page, loi = trang
    page.evaluate("capNhatViecTiepTheo()")
    page.wait_for_function("document.getElementById('viecTiepTheo').dataset.trangThai === 'canh_bao'")
    assert "trước khi chạy" not in page.locator("#viecTiepTheoCau").inner_text()
    assert page.locator("#btnRun").is_enabled()
    assert not loi, loi
