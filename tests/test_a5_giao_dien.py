"""A5-L3: nhóm đồng hạng `a|b` ở trình hướng dẫn workspace — bằng TRÌNH DUYỆT THẬT.

MỘT trang dùng chung cho cả tệp (khởi động Chromium một lần): các ca đi lần lượt trên cùng
bước 3 của trình hướng dẫn. Máy không có playwright/Chromium thì bỏ qua cả tệp.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def trang_buoc3(tmp_path_factory):
    """Trang đã mở sẵn bước 3 của trình hướng dẫn, ưu tiên "chỉ theo nhóm" (ô nhóm dùng được)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    tmp = tmp_path_factory.mktemp("a5ui")
    goc, xuat = tmp / "goc", tmp / "xuat"
    goc.mkdir()
    xuat.mkdir()
    slug = ws.tao(str(goc), "Trường học", None)
    api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat),
                      thu_muc_goc_ws=str(goc), ws_da_chon=True)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone")
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Nhóm đồng hạng")
    page.locator("#wzTuyChinh").click()
    page.locator("#wzTiep").click()
    page.select_option("#wzPriority", "tier")
    assert page.locator("#wzTiers").is_enabled()
    yield page, loi
    br.close()
    pw.stop()


def _thu(page, noi_dung):
    """Điền ô nhóm rồi bấm Tiếp; trả về chữ lỗi (rỗng nếu sang được bước xem lại)."""
    if page.locator("#rvTiers").count():            # đang ở bước xem lại: quay về bước 3
        page.locator("#wzLui").click()
    page.fill("#wzTiers", noi_dung)
    page.locator("#wzTiep").click()
    loi = page.locator("#wzLoi")
    return loi.inner_text() if loi.is_visible() else ""


@pytest.mark.parametrize("noi_dung, khoa", [
    ("a\nb|a", "Mỗi nhóm chỉ được ở MỘT hạng"),          # một nhóm ở hai hạng
    ("a|A", "Mỗi nhóm chỉ được ở MỘT hạng"),              # hai lần trong một dòng (không phân biệt hoa)
    ("Khối 1|x\nkhoi  1", "Mỗi nhóm chỉ được ở MỘT hạng"),   # dấu, NBSP, dấu cách kép
    ("đoàn|DOAN", "Mỗi nhóm chỉ được ở MỘT hạng"),        # đ → d, bỏ dấu (như xay_tier_rank)
    ("Đội\nđoi|x", "Mỗi nhóm chỉ được ở MỘT hạng"),
    ("a||b", "phần trống quanh dấu |"),
    ("a|\nb", "phần trống quanh dấu |"),
])
def test_loi_nhom_o_hai_hang_hoac_phan_rong(trang_buoc3, noi_dung, khoa):
    page, loi_js = trang_buoc3
    assert khoa in _thu(page, noi_dung)
    assert page.locator("#rvTiers").count() == 0     # vẫn ở bước 3
    assert not loi_js, loi_js


def test_xem_lai_hien_a_bang_b(trang_buoc3):
    page, loi_js = trang_buoc3
    assert _thu(page, "a|b\nc") == ""
    assert page.locator("#rvTiers").inner_text() == "a = b › c"
    assert not loi_js, loi_js


def test_khong_co_gach_giu_nguyen_cach_hien_thi_va_loi_trung_cu(trang_buoc3):
    page, _ = trang_buoc3
    assert _thu(page, "Khối 12\nKhối 11") == ""
    assert page.locator("#rvTiers").inner_text() == "Khối 12 › Khối 11"
    assert "hai dòng trùng nhau" in _thu(page, "x\nx")


def test_ten_nhom_chua_html_khong_chay_ma(trang_buoc3):
    page, loi_js = trang_buoc3
    xau = "<img src=x onerror=window.__xss=1>|b"
    assert _thu(page, xau) == ""
    assert page.locator("#rvTiers").inner_text() == "<img src=x onerror=window.__xss=1> = b"
    assert page.evaluate("window.__xss") is None
    assert not loi_js, loi_js
