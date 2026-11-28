"""UX6-L2: màn hình đổi theo trạng thái (Chromium thật; dữ liệu MÔ PHỎNG: sổ 120 học sinh, seed 42).
Thẻ Xếp CLB: ô thả tệp nhường chỗ cho một dòng tóm tắt sau khi nhập; thanh trạng thái có thanh tiến độ và nút
"chưa có CLB"; thẻ Kết quả: bảng không nằm trong khung, một thanh công cụ phía trên bảng."""

import os
import tempfile

import pytest

from _ux5a_chung import GOC, JS_DEM, SO_120, dem, mo_ux5a  # noqa: F401
from _trinh_duyet import CHROMIUM
import browser_host
import workspace as ws
from api import PipelineAPI


@pytest.fixture
def mo_trong():
    """Trang Chromium với workspace TRỐNG (chưa nạp sổ)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    from playwright.sync_api import sync_playwright
    dong = []
    tmp = tempfile.mkdtemp()
    goc, xuat = os.path.join(tmp, "g"), os.path.join(tmp, "x")
    os.makedirs(goc)
    os.makedirs(xuat)
    slug = ws.tao(goc, "Truong hoc", None)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=xuat, thu_muc_goc_ws=goc, ws_da_chon=True)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    dong.append((br, pw))
    page = br.new_page(viewport={"width": 1280, "height": 900}, bypass_csp=True)
    page.set_default_timeout(10000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_function("document.body.dataset.vai !== undefined")
    page.wait_for_timeout(600)
    yield page, api, loi
    for br, pw in dong:
        br.close()
        pw.stop()


def test_so_trong_van_thay_o_tha_tep(mo_trong):
    page, api, loi = mo_trong
    assert page.locator("#dropZone").is_visible()
    assert page.locator("#ux6TomSo").is_hidden()
    assert not loi, loi


def test_sau_nhap_va_chay_o_tha_an_va_co_dong_tom_tat(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "pipeline")
    page.wait_for_function("document.getElementById('ux6TomSo') && !document.getElementById('ux6TomSo').hidden")
    assert page.locator("#dropZone").is_hidden()
    assert "120" in page.locator("#ux6TomSoChu").inner_text()
    page.click("#btnDoiSo")
    assert page.locator("#dropZone").is_visible()
    assert page.locator("#ux6TomSo").is_hidden()
    assert not loi, loi


def test_buoc_xong_gon_thanh_mot_dong_va_mo_lai_duoc(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "pipeline")
    page.wait_for_function("document.getElementById('panelCanhBao').dataset.gon !== undefined")
    p = page.locator("#panelCanhBao")
    if p.get_attribute("data-gon") == "1":                          # sổ sạch: gọn một dòng
        assert page.locator("#healthSummary").is_visible()
        assert page.locator("#panelCanhBao .hint-text").is_hidden()
        page.click("#btnMoLaiCanhBao")
        assert p.get_attribute("data-gon") == "0"
        assert page.locator("#panelCanhBao .hint-text").is_visible()
    assert not loi, loi


def test_canh_bao_chan_giu_buoc_mo(mo_ux5a, monkeypatch):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "pipeline")
    page.evaluate("document.getElementById('healthSummary').className = 'health-summary is-warn'; ux6GonBuocCanhBao()")
    assert page.locator("#panelCanhBao").get_attribute("data-gon") == "0"
    assert not loi, loi


def test_thanh_trang_thai_tien_do_va_nut_chua_co_clb(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "pipeline")
    d = api.get_dashboard_status()["data"]
    so = api.get_em_chua_co_cho()["data"]["so_em"]
    page.wait_for_function("document.getElementById('statTienDo').textContent.includes('/')")
    assert page.locator("#statTienDo").inner_text().startswith("%d/%d" % (d["n_matched"], d["n_students"]))
    assert page.locator("#statBar").get_attribute("role") == "progressbar"
    assert page.locator("#statBar").get_attribute("aria-valuenow") == str(d["n_matched"])
    assert so > 0
    nut = page.locator("#btnStripChuaCo")
    assert nut.is_visible() and str(so) in nut.inner_text()
    nut.click()                                                     # cùng hành động với nút trên thanh "Việc tiếp theo"
    page.wait_for_selector("#view-others.is-active")
    assert not loi, loi


@pytest.mark.parametrize("vai", ["quan_tri", "giao_vien"])
def test_ket_qua_bang_khong_trong_khung_va_mot_thanh_cong_cu(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai, "results")
    assert page.locator("#kqThanhCongCu").is_visible()
    hop = page.evaluate("""() => {
      const b = document.querySelector('#kqBang');
      const the = b && b.closest('.panel');
      return the ? the.id || 'panel' : null;
    }""")
    assert hop is None, hop                                         # bảng không nằm trong .panel
    tb = page.locator("#kqThanhCongCu").bounding_box()
    ban = page.locator("#kqBang").bounding_box()
    assert tb["y"] + tb["height"] <= ban["y"] + 2                   # thanh công cụ nằm TRÊN bảng
    assert page.locator("#btnKqTaiBang").is_visible()
    if vai == "giao_vien":
        assert page.locator("#btnUx1bBaoCao").count() == 0 or page.locator("#btnUx1bBaoCao").is_hidden()
    assert not loi, loi
