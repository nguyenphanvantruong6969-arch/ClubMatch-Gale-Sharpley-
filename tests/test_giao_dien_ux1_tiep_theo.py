"""UX1A-L1: thanh "Việc tiếp theo" (#viecTiepTheo) đi qua đủ năm trạng thái.
Chromium thật qua `browser_host`; sổ nhập MÔ PHỎNG (du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx)."""

import base64
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


def _nap(api):
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

        def _mo():
            url = browser_host.serve(api, GOC, "index.html", open_browser=False)
            page = br.new_page(bypass_csp=True)
            page.set_default_timeout(15000)
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("#dropZone", state="attached")
            return page, loi
        yield _mo
        br.close()


def _trang_thai(page, ten):
    page.wait_for_function(
        "n => document.getElementById('viecTiepTheo')"
        " && document.getElementById('viecTiepTheo').dataset.trangThai === n", arg=ten)


def test_chua_co_du_lieu_nut_nap_so_dua_con_tro_vao_o_tha(mo):
    page, loi = mo()
    _trang_thai(page, "nap_so")
    nut = page.locator("#viecTiepTheoNut")
    assert nut.inner_text().strip() == "Nạp sổ"
    assert page.locator("#viecTiepTheo").get_attribute("data-quyen") == "quan_tri"
    nut.click()
    assert page.evaluate("document.activeElement.id") == "dropZone"
    assert not loi, loi


def test_co_canh_bao_chan_nut_xem_canh_bao(mo, api, monkeypatch):
    _nap(api)
    goc = api.get_data_health_report

    def chan():
        kq = goc()
        kq["data"] = dict(kq["data"], n_high=1, n_warnings=max(1, kq["data"]["n_warnings"]))
        return kq
    monkeypatch.setattr(api, "get_data_health_report", chan)
    page, loi = mo()
    _trang_thai(page, "canh_bao")
    nut = page.locator("#viecTiepTheoNut")
    assert nut.inner_text().strip() == "Xem cảnh báo"
    nut.click()
    assert page.evaluate("document.activeElement.id") in ("panelCanhBao", "healthSummary")
    assert not loi, loi


def test_chua_chay_nut_chay_sap_xep_roi_het_qua_cac_buoc_xuat(mo, api):
    _nap(api)
    page, loi = mo()
    _trang_thai(page, "chay")
    nut = page.locator("#viecTiepTheoNut")
    assert nut.inner_text().strip() == "Chạy sắp xếp"
    nut.click()
    # Sau khi chạy: hoặc còn học sinh chưa có CLB, hoặc đi thẳng tới Xuất.
    page.wait_for_function(
        "() => ['xu_ly', 'xuat'].includes(document.getElementById('viecTiepTheo').dataset.trangThai)")
    assert not loi, loi


def test_con_hoc_sinh_chua_co_cho_nut_xu_ly_mo_bang_va_cuon(mo, api, monkeypatch):
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    goc = api.get_em_chua_co_cho

    def co_3():
        kq = goc()
        kq["data"] = dict(kq["data"], so_em=3, tong_hoc_sinh=max(kq["data"]["tong_hoc_sinh"], 3))
        return kq
    monkeypatch.setattr(api, "get_em_chua_co_cho", co_3)
    page, loi = mo()
    _trang_thai(page, "xu_ly")
    nut = page.locator("#viecTiepTheoNut")
    assert "3" in nut.inner_text()
    assert "Xử lý" in nut.inner_text()
    nut.click()
    page.wait_for_selector("#view-others.is-active")
    page.wait_for_selector("#chuaCoChoPanelBody", state="visible")
    assert not loi, loi


def test_chay_xong_het_chua_co_cho_nut_xuat_ket_qua(mo, api, monkeypatch):
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    goc = api.get_em_chua_co_cho

    def khong_ai():
        kq = goc()
        kq["data"] = dict(kq["data"], so_em=0, danh_sach=[])
        return kq
    monkeypatch.setattr(api, "get_em_chua_co_cho", khong_ai)
    page, loi = mo()
    _trang_thai(page, "xuat")
    nut = page.locator("#viecTiepTheoNut")
    assert nut.inner_text().strip() == "Xuất kết quả"
    nut.click()
    page.wait_for_selector("#view-others.is-active")
    # UX1A-L3: bấm là xuất luôn (tuỳ chọn mặc định), không dừng ở việc đưa con trỏ tới nút.
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.trim() !== ''")
    assert not loi, loi


def test_the_can_xu_ly_la_nut_cung_hanh_dong(mo, api, monkeypatch):
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    goc = api.get_em_chua_co_cho

    def co_2():
        kq = goc()
        kq["data"] = dict(kq["data"], so_em=2, tong_hoc_sinh=max(kq["data"]["tong_hoc_sinh"], 2))
        return kq
    monkeypatch.setattr(api, "get_em_chua_co_cho", co_2)
    page, loi = mo()
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector('.kpi-o[data-muc="chuaCoChoPanel"]')
    page.locator('.kpi-o[data-muc="chuaCoChoPanel"]').click()
    page.wait_for_selector("#chuaCoChoPanelBody", state="visible")
    assert not loi, loi


def test_luong_chinh_nap_chay_tai_ket_qua_bon_lan_bam(mo, api, monkeypatch):
    """Mục tiêu UX1 §1: nạp sổ -> chạy -> tải kết quả = 4 lần bấm (chọn tệp, Nhập sổ, nút thanh, nút thanh).
    Trường hợp mọi người đều có CLB (sổ mẫu 120 học sinh còn vài em chưa có CLB nên giả lập "không ai")."""
    goc = api.get_em_chua_co_cho

    def khong_ai():
        kq = goc()
        kq["data"] = dict(kq["data"], so_em=0, danh_sach=[])
        return kq
    monkeypatch.setattr(api, "get_em_chua_co_cho", khong_ai)
    page, loi = mo()
    _trang_thai(page, "nap_so")
    lan = 0
    page.locator("#fileAny").set_input_files([SO_120])               # 1: chọn tệp (hộp thoại chọn tệp)
    lan += 1
    page.wait_for_function("() => !document.getElementById('btnImportAll').hidden")
    page.locator("#btnImportAll").click()                            # 2: Nhập sổ
    lan += 1
    _trang_thai(page, "chay")
    page.locator("#viecTiepTheoNut").click()                         # 3: Chạy sắp xếp (từ thanh)
    lan += 1
    page.wait_for_function(
        "() => ['xu_ly', 'xuat'].includes(document.getElementById('viecTiepTheo').dataset.trangThai)")
    _trang_thai(page, "xuat")
    page.locator("#viecTiepTheoNut").click()                         # 4: Xuất kết quả (từ thanh)
    lan += 1
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.trim() !== ''")
    assert lan == 4
    assert not loi, loi


def test_so_that_con_hoc_sinh_chua_co_cho_van_tai_ket_qua_bon_lan_bam(mo, api):
    """Sổ mẫu 120 học sinh THẬT (không giả lập), còn em chưa có CLB: chọn tệp, Nhập sổ, Chạy, Xuất = 4 lần bấm."""
    page, loi = mo()
    _trang_thai(page, "nap_so")
    page.locator("#fileAny").set_input_files([SO_120])               # 1
    page.wait_for_function("() => !document.getElementById('btnImportAll').hidden")
    page.locator("#btnImportAll").click()                            # 2
    _trang_thai(page, "chay")
    assert page.locator("#viecTiepTheoNut2").is_hidden()
    page.locator("#viecTiepTheoNut").click()                         # 3
    _trang_thai(page, "xu_ly")                                       # seed mặc định: còn em chưa có CLB
    assert page.locator("#viecTiepTheoNut").inner_text().startswith("Xử lý")
    assert page.locator("#viecTiepTheoNut2").is_visible()
    assert "btn-canh-bao" in page.locator("#viecTiepTheoNut").get_attribute("class")
    assert "btn-primary" not in page.locator("#viecTiepTheoNut2").get_attribute("class")
    page.locator("#viecTiepTheoNut2").click()                        # 4: Xuất kết quả (nút phụ)
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.trim() !== ''")
    assert not loi, loi
