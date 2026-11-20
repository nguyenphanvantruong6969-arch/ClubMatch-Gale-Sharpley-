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
from _trinh_duyet import CHROMIUM, mo_gap_ma  # noqa: E402

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
    mo_gap_ma(page)
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
    # UX1A-L3: khung tra cứu nằm đầu thẻ Kết quả, không còn liên kết nhảy; ô tìm kiếm bấm tới được ngay.
    assert page.locator("#gtNhay").count() == 0
    page.click("#gtTim")
    assert page.evaluate("document.activeElement.id") == "gtTim"
    assert not loi, loi


def test_huong_dan_bon_buoc_chi_cho_quan_tri(mo):
    api, ds, ma, vao, loi, page = mo
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"] and api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("quantri", MK)["ok"]
    vao()
    mo_gap_ma(page)
    assert page.locator("#gtBuocHuongDan").is_visible()
    mo_gap_ma(page)
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
    mo_gap_ma(page)
    page.click("#btnGtXuatMa")
    page.wait_for_selector("#gtMaPhanHoi .nut-mo-thu-muc")
    nut = page.locator("#gtMaPhanHoi .nut-mo-tep")
    assert nut.is_visible()
    nut.click()
    page.wait_for_function("true")
    assert len(goi) == 1 and goi[0].endswith(".csv")
    assert not loi, loi


def test_khoa_chi_chan_dung_ma_bi_khoa_khong_chan_em_khac(mo):
    """GT4 fix B2: khoá tạm tính theo từng mã học sinh; em khác vẫn bấm Xem được trong lúc em kia bị khoá."""
    api, ds, ma, vao, loi, page = mo
    vao(dong_ho=True)
    _mo_man_hoc_sinh(page)
    for _ in range(6):
        page.fill("#gtHsMa", ds[0])
        page.fill("#gtHsMaTra", "SAIMA999")
        page.click("#btnGtHsXem")
        page.wait_for_function("document.querySelector('#gtHsLoi').innerText.length > 0")
        page.fill("#gtHsMaTra", "")
    page.locator("#gtHsDemNguoc").wait_for(state="visible")
    assert page.locator("#btnGtHsXem").is_disabled()
    page.fill("#gtHsMa", ds[1])                                     # em khác
    assert page.locator("#btnGtHsXem").is_enabled()
    page.fill("#gtHsMaTra", ma[ds[1]])
    page.press("#gtHsMaTra", "Enter")
    page.wait_for_selector("#gtHsKetQua .gt-ten")
    assert ds[1] in page.inner_text("#gtHsKetQua .gt-ten")
    page.fill("#gtHsMa", ds[0])                                     # quay lại em bị khoá: vẫn khoá
    assert page.locator("#btnGtHsXem").is_disabled()
    assert not loi, loi


def test_nut_ngon_ngu_man_hoc_sinh_doc_duoc(mo):
    """GT4 fix B3: nút EN phải thấy rõ (tương phản >= 4,5:1, chữ >= 14 px, cao >= 36 px)."""
    api, ds, ma, vao, loi, page = mo
    vao()
    _mo_man_hoc_sinh(page)
    r = page.evaluate("""() => {
      const b = document.querySelector('#btnGtHsNgonNgu'), s = getComputedStyle(b), k = b.getBoundingClientRect();
      const bg = (el) => { for (let e = el; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor;
        const m = c.match(/[\\d.]+/g).map(Number); if (m.length < 4 || m[3] > 0) return m; } return [255,255,255,1]; };
      const lum = (c) => { const f = c.slice(0,3).map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
        return 0.2126*f[0] + 0.7152*f[1] + 0.0722*f[2]; };
      const fg = s.color.match(/[\\d.]+/g).map(Number);
      const a = fg.length > 3 ? fg[3] : 1, back = bg(b);
      const mix = [0,1,2].map(i => fg[i]*a + back[i]*(1-a));
      const l1 = lum(mix), l2 = lum(back), hi = Math.max(l1,l2), lo = Math.min(l1,l2);
      return {ratio: (hi+0.05)/(lo+0.05), px: parseFloat(s.fontSize), h: k.height, w: k.width};
    }""")
    assert r["ratio"] >= 4.5 and r["px"] >= 14 and r["h"] >= 36 and r["w"] >= 36, r
    assert not loi, loi


def test_xac_nhan_thoat_hai_nut_khong_trung_ten_va_hien_ma_tra_cuu(mo):
    """GT4 ghi chú checker: hai nút cùng tên "Thoát" -> nút xác nhận đổi tên; mã tra cứu có ô "Hiện mã"."""
    api, ds, ma, vao, loi, page = mo
    vao()
    _mo_man_hoc_sinh(page)
    page.click("#btnGtHsThoat")
    page.wait_for_selector("#btnGtHsCo", state="visible")
    assert page.inner_text("#btnGtHsCo").strip() != page.inner_text("#btnGtHsThoat").strip()
    page.click("#btnGtHsKhong")
    assert page.get_attribute("#gtHsMaTra", "type") == "password"
    page.check("#gtHsHien")
    assert page.get_attribute("#gtHsMaTra", "type") == "text"
    page.uncheck("#gtHsHien")
    assert page.get_attribute("#gtHsMaTra", "type") == "password"
    assert not loi, loi


def test_khoa_chi_con_mot_dong_cho_doi_la_dong_dem_nguoc(mo):
    """GT4 ghi chú checker: dòng lỗi không lặp lại "đợi một phút" (đồng hồ đếm đã nói số giây)."""
    api, ds, ma, vao, loi, page = mo
    vao(dong_ho=True)
    _mo_man_hoc_sinh(page)
    for _ in range(6):
        page.fill("#gtHsMa", ds[0])
        page.fill("#gtHsMaTra", "SAIMA999")
        page.click("#btnGtHsXem")
        page.wait_for_function("document.querySelector('#gtHsLoi').innerText.length > 0")
        page.fill("#gtHsMaTra", "")
    assert "phút" not in page.inner_text("#gtHsLoi")
    page.fill("#gtHsMa", ds[1])                                     # sang mã khác: dòng lỗi của mã trước biến mất
    assert page.inner_text("#gtHsLoi").strip() == ""
    assert not loi, loi
