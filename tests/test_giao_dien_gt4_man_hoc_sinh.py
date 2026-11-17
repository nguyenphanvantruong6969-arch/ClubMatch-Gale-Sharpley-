"""GT4-L5 — màn học sinh tự tra cứu, vị trí khung tra cứu ở thẻ Kết quả, "Mở tệp" sau khi xuất (R9). Chromium.
Dữ liệu MÔ PHỎNG, mật khẩu giả. Đồng hồ trình duyệt được giả bằng `page.clock` để kiểm đếm ngược mà khỏi chờ thật."""

import os
import shutil
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import api as api_mod  # noqa: E402
import browser_host  # noqa: E402
import cau_hinh_ws  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

MK = "matkhau-gia-1"


def _api(tmp_path, ten_ws="Trường Thử Nghiệm"):
    os.makedirs(str(tmp_path / "nguon"))
    nguon = d.nap_bo(str(tmp_path / "nguon"), d.BO_DU_LIEU[1][1])
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, ten_ws, {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}, "name": ten_ws})
    api = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    with api._ket_noi_doc() as cur:
        ma = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))
    return api, sorted(ma), ma


@pytest.fixture
def mo(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api, ds, ma = _api(tmp_path)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True)
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)

    def vao(dong_ho=False):
        if dong_ho:
            page.clock.install()
        page.goto(url)
        page.wait_for_selector("#gtPanel", state="attached")
        page.wait_for_function("document.querySelector('#wsTenHienTai').textContent.length > 0")
        page.click('button.nav-item[data-tab="results"]')
        return page

    try:
        yield api, ds, ma, vao, loi, page
    finally:
        br.close()
        pw.stop()


def _mo_man_hoc_sinh(page):
    page.click("#btnGtCheDoHs")
    page.wait_for_selector("#gtHs", state="visible")


def test_nhan_hien_thay_ten_truong_va_nut_ngon_ngu(mo):
    api, ds, ma, vao, loi, page = mo
    vao()
    _mo_man_hoc_sinh(page)
    assert page.inner_text('label[for="gtHsMa"]').strip() == "Mã học sinh"
    assert page.inner_text('label[for="gtHsMaTra"]').strip() == "Mã tra cứu"
    assert page.inner_text("#gtHsTruong") == "Trường Thử Nghiệm"
    page.click("#btnGtHsNgonNgu")                                   # đổi ngôn ngữ ngay trên màn học sinh
    page.wait_for_function("window.I18N.getLang() === 'en'")
    assert "ID" in page.inner_text('label[for="gtHsMa"]') or "code" in page.inner_text('label[for="gtHsMa"]').lower()
    assert not loi, loi


def test_enter_gui_va_loi_dua_con_tro_ve_o_dau(mo):
    api, ds, ma, vao, loi, page = mo
    vao()
    _mo_man_hoc_sinh(page)
    page.fill("#gtHsMa", ds[0])
    page.fill("#gtHsMaTra", "SAIMA999")
    page.press("#gtHsMaTra", "Enter")                               # Enter gửi, không cần bấm nút
    page.wait_for_function("document.querySelector('#gtHsLoi').innerText.length > 0")
    assert page.evaluate("document.activeElement.id") == "gtHsMa"
    page.fill("#gtHsMa", ds[0])
    page.fill("#gtHsMaTra", ma[ds[0]])
    page.press("#gtHsMaTra", "Enter")
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    assert ds[0] in page.inner_text("#gtHsKetQua .gt-ten")
    assert not loi, loi


def test_khoa_hien_dem_nguoc_giay_va_mo_lai(mo):
    api, ds, ma, vao, loi, page = mo
    vao(dong_ho=True)
    _mo_man_hoc_sinh(page)
    for _ in range(6):                                              # 5 lần sai khoá; lần 6 nhận lỗi "tạm khoá"
        page.fill("#gtHsMa", ds[0])
        page.fill("#gtHsMaTra", "SAIMA999")
        page.click("#btnGtHsXem")
        page.wait_for_function("document.querySelector('#gtHsLoi').innerText.length > 0")
        page.fill("#gtHsMaTra", "")
    dem = page.locator("#gtHsDemNguoc")
    dem.wait_for(state="visible")
    assert "60" in dem.inner_text() or "59" in dem.inner_text()
    assert page.locator("#btnGtHsXem").is_disabled()
    page.clock.run_for(10000)
    assert any(n in dem.inner_text() for n in ("49", "50", "51"))
    page.clock.run_for(52000)
    page.wait_for_function("document.querySelector('#gtHsDemNguoc').hidden === true")
    assert page.locator("#btnGtHsXem").is_enabled()
    assert not loi, loi


def test_bam_dong_bang_ket_qua_mo_giai_trinh_va_co_lien_ket_nhay(mo):
    api, ds, ma, vao, loi, page = mo
    vao()
    page.click('button.kq-seg-nut[data-kq="ma"]')
    page.wait_for_selector("#kqThan tr")
    dong = page.locator("#kqThan tr").nth(2)
    sid = dong.locator("td").first.inner_text().strip()
    dong.locator("td").first.click()
    page.wait_for_selector("#gtKetQua .gt-ten")
    assert sid in page.inner_text("#gtKetQua .gt-ten")
    page.wait_for_function("(() => { const r = document.querySelector('#gtPanel').getBoundingClientRect();"
                           " return r.top < window.innerHeight && r.bottom > 0; })()")
    page.evaluate("window.scrollTo(0, 0)")
    page.click("#gtNhay")                                           # liên kết "Tra cứu" ở đầu thẻ
    assert page.evaluate("document.activeElement.id") == "gtTim"
    assert not loi, loi


def test_huong_dan_bon_buoc_chi_cho_quan_tri(mo):
    api, ds, ma, vao, loi, page = mo
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"] and api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("quantri", MK)["ok"]
    vao()
    assert page.locator("#gtBuocHuongDan").is_visible()
    assert len(page.locator("#gtBuocHuongDan li").all()) == 4
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    page.reload()
    page.wait_for_selector("#gtPanel", state="attached")
    page.wait_for_function("document.body.dataset.vai === 'giao_vien'")
    page.click('button.nav-item[data-tab="results"]')
    assert not page.locator("#gtBuocHuongDan").is_visible()
    assert not loi, loi


def test_sau_khi_xuat_co_mo_thu_muc_va_mo_tep(mo):
    api, ds, ma, vao, loi, page = mo
    vao()
    goi = []
    api.mo_tep = lambda p: goi.append(p) or {"ok": True, "data": {"path": p}, "errors": []}
    page.click("#btnGtXuatMa")
    page.wait_for_selector("#gtMaPhanHoi .nut-mo-thu-muc")
    nut = page.locator("#gtMaPhanHoi .nut-mo-tep")
    assert nut.is_visible()
    nut.click()
    page.wait_for_function("true")
    assert len(goi) == 1 and goi[0].endswith(".csv")
    assert not loi, loi
