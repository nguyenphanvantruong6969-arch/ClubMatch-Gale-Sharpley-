"""GT2-L1 — khung "Tiêu chí xếp" ở thẻ Quản lý (Playwright + Chromium, qua `browser_host`).

Dữ liệu MÔ PHỎNG. Kiểm: thứ tự hiện đúng chữ; chỉ có các lựa chọn cho phép; lưu đi qua
`update_workspace_config` rồi danh sách đổi theo; đổi ngôn ngữ thì chữ đổi; câu ghi chú cố định.
"""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

DAU_VIET = re.compile(
    "[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)


@pytest.fixture
def mo(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo():
        api = PipelineAPI(str(tmp_path / "app.db"), thu_muc_goc_ws=str(tmp_path))
        slug = api.create_workspace("Thu tieu chi")["data"]["slug"]
        assert api.open_workspace(slug)["ok"]
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.evaluate("document.getElementById('ux1aNangCao').open = true")  # UX1A-L2: Nâng cao đóng mặc định
        page.wait_for_selector("#gt2TcDanhSach li")
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _chu(page, tang):
    return page.locator('#gt2TcDanhSach ol[data-tang="%s"] li' % tang).all_inner_texts()


def test_hien_thu_tu_mac_dinh_bang_loi_thuong(mo):
    page, api, loi = mo()
    t1 = _chu(page, "tang_1")
    assert "Điểm bài thi của CLB (cao trước)" == t1[0]
    assert "Nhóm ưu tiên – giữ suất riêng" == t1[1]
    assert "Số bốc thăm (nhỏ trước)" == t1[-1]
    assert "Phần mềm không dùng thứ hạng nguyện vọng" in page.locator("#gt2TcGhiChu").inner_text()
    # không lộ mã nội bộ
    chu = page.locator("#gt2TieuChiPanel").inner_text()
    assert not re.search(r"\b(GT\d|priority|tier_mode|score_scope|wharton)\b", chu)
    assert not loi, loi


def test_chi_co_lua_chon_cho_phep(mo):
    page, api, loi = mo()
    for id_, khoa in (("gt2TcPriority", "priority"), ("gt2TcTierMode", "tier_mode"),
                      ("gt2TcScoreScope", "score_scope")):
        gia_tri = page.eval_on_selector_all("#%s option" % id_, "os => os.map(o => o.value)")
        cho_phep = {"priority": cau_hinh_ws.UU_TIEN, "tier_mode": cau_hinh_ws.CHE_DO_NHOM,
                    "score_scope": cau_hinh_ws.PHAM_VI_DIEM}[khoa]
        assert gia_tri == list(cho_phep)
    assert not loi, loi


def test_luu_doi_thu_tu_va_cau_hinh_da_luu(mo):
    page, api, loi = mo()
    page.select_option("#gt2TcPriority", "score+tier")
    page.select_option("#gt2TcTierMode", "strict")
    page.fill("#gt2TcTiers", "Khối 12\nKhối 11")
    page.locator("#gt2TcLuu").click()
    page.wait_for_function(
        "() => document.querySelector('#gt2TcDanhSach ol[data-tang=\"tang_1\"] li')"
        " && document.querySelector('#gt2TcDanhSach ol[data-tang=\"tang_1\"] li').dataset.ma === 'nhom_cung'")
    assert "Khối 12" in _chu(page, "tang_1")[0]
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    assert (rules["priority"], rules["tier_mode"], rules["tiers"]) == \
        ("score+tier", "strict", ["Khối 12", "Khối 11"])
    assert "Đã lưu" in page.locator("#gt2TcPhanHoi").inner_text()
    assert not loi, loi


def test_luu_khoa_diem_quyet_tam_khi_chi_xet_nhom_khong_loi(mo):
    """Chỉ xét nhóm không đi cùng điểm quyết tâm: cấu hình tự tắt cờ thay vì báo lỗi."""
    page, api, loi = mo()
    page.select_option("#gt2TcPriority", "tier")
    page.fill("#gt2TcTiers", "Khối 12")
    page.locator("#gt2TcLuu").click()
    page.wait_for_function(
        "() => document.querySelectorAll('#gt2TcDanhSach ol[data-tang=\"tang_1\"]').length === 0")
    assert _chu(page, "tang_2")[0].startswith("Nhóm ưu tiên (Khối 12)")
    assert not loi, loi


def test_luu_chi_xet_nhom_khong_can_bo_tick_diem_quyet_tam(mo):
    """UX1A-L2b: ô tick đã bỏ (thẻ ở trang Cài đặt giữ cờ); lưu "chỉ xét nhóm" thành công và cờ tự tắt."""
    page, api, loi = mo()
    page.select_option("#gt2TcPriority", "tier")
    page.fill("#gt2TcTiers", "Khối 12")
    assert page.locator("#gt2TcWharton").count() == 0
    page.locator("#gt2TcLuu").click()
    page.wait_for_function("() => document.querySelector('#gt2TcPhanHoi').textContent.includes('Đã lưu')")
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is False
    assert not loi, loi


def test_luu_diem_theo_nguoi_khong_can_bo_tick_diem_quyet_tam(mo):
    page, api, loi = mo()
    page.select_option("#gt2TcScoreScope", "per_person")
    page.locator("#gt2TcLuu").click()
    page.wait_for_function("() => document.querySelector('#gt2TcPhanHoi').textContent.includes('Đã lưu')")
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is False
    assert not loi, loi


@pytest.mark.parametrize("fa", [False, True])
@pytest.mark.parametrize("khoa,tat,bat", [("gt2TcPriority", "tier", "score"),
                                         ("gt2TcScoreScope", "per_person", "per_slot")])
def test_chon_roi_chon_lai_tra_lai_diem_quyet_tam(mo, khoa, tat, bat, fa):
    page, api, loi = mo()
    if fa:
        assert api.update_workspace_config({"rules": {"fa_daa": True, "wharton": True}})["ok"]
        page.reload()
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.evaluate("document.getElementById('ux1aNangCao').open = true")  # UX1A-L2: Nâng cao đóng mặc định
        page.wait_for_selector("#gt2TcDanhSach li")
    # UX1A-L2b: không còn ô tick; chọn rồi chọn lại giá trị cũ thì cờ điểm quyết tâm đã lưu được giữ nguyên.
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is True
    page.select_option("#" + khoa, tat)
    page.select_option("#" + khoa, bat)
    page.locator("#gt2TcLuu").click()
    page.wait_for_function("() => document.querySelector('#gt2TcPhanHoi').textContent.includes('Đã lưu')")
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    assert rules["wharton"] is True
    assert not loi, loi


def test_doi_ngon_ngu_doi_chu(mo):
    page, api, loi = mo()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    t1 = _chu(page, "tang_1")
    assert t1[0] == "Exam score for the club (higher first)"
    assert "does not use" in page.locator("#gt2TcGhiChu").inner_text()
    chu = page.locator("#gt2TieuChiPanel").inner_text()
    assert not DAU_VIET.search(chu), chu
    assert not loi, loi


def test_ten_nhom_la_html_khong_chay_ma_va_loi_api_hien_thong_bao(mo):
    page, api, loi = mo()
    page.evaluate("window.__xss = 0")
    page.select_option("#gt2TcPriority", "tier")
    page.fill("#gt2TcTiers", "<img src=x onerror=window.__xss=1>")
    page.locator("#gt2TcLuu").click()
    page.wait_for_function(
        "() => document.querySelector('#gt2TcDanhSach li') && "
        "document.querySelector('#gt2TcDanhSach li').dataset.ma === 'nhom_cung'")
    page.wait_for_timeout(300)
    assert page.evaluate("window.__xss") == 0
    assert "<img" in page.locator("#gt2TcDanhSach li").first.inner_text()
    # Lưu bị từ chối (tên nhóm trùng): thông báo dễ hiểu, không "undefined" / "[object Object]"
    page.fill("#gt2TcTiers", "A\nA")
    page.locator("#gt2TcLuu").click()
    page.wait_for_function("() => document.querySelector('#gt2TcPhanHoi').textContent.length > 0")
    chu = page.locator("#gt2TcPhanHoi").inner_text()
    assert "undefined" not in chu and "[object" not in chu and chu.strip()
    assert not loi, loi
