"""GT4-L2 — nút hiện ra khớp với vai (R3, D4-1). Chromium qua `browser_host`. Dữ liệu MÔ PHỎNG, mật khẩu giả.

Quét vai giáo viên: mở mọi thẻ nhìn thấy, bấm mọi nút / liên kết nhìn thấy đúng một lần; nhật ký không được có
dòng nào bị từ chối quyền (`gt3_khong_du_quyen`) — nút của quản trị phải đã bị ẩn."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _fa import dung_fa_clb  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import tat_wharton  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"


def _dung(api):
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
    for sid, ten in {"s1": "Nguyễn Văn Ánh", "s2": "Trần Thị Bé"}.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    _dung(api)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True, accept_downloads=True)
    page.set_default_timeout(4000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.on("dialog", lambda d: d.dismiss())                       # mọi hộp xác nhận: Huỷ (không phá dữ liệu)
    try:
        yield page, api, url, loi
    finally:
        br.close()
        pw.stop()


JS_NUT = """() => [...document.querySelectorAll('button, a[href], [role="button"]')]
  .filter(e => e.offsetParent !== null && !e.disabled && !e.closest('[hidden]'))
  .map((e, i) => { e.setAttribute('data-quet', String(i)); return [String(i), (e.id || e.textContent || '').trim().slice(0, 40)]; })"""


def _nut_hien(page):
    return page.evaluate(JS_NUT)


def _dong_tu_choi(api):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT hanh_dong FROM nhat_ky_thao_tac WHERE ket_qua = 'gt3_khong_du_quyen' "
                           "ORDER BY id").fetchall()


def test_giao_vien_bam_moi_nut_nhin_thay_khong_bi_tu_choi_quyen(mo):
    page, api, url, loi = mo
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    page.goto(url)
    page.wait_for_selector("#tkNutMoHop")
    page.wait_for_function("document.body.dataset.vai === 'giao_vien'")
    tab_hien = [t.get_attribute("data-tab") for t in page.locator(".nav-item").all() if t.is_visible()]
    assert tab_hien, "giáo viên phải thấy ít nhất một thẻ"
    da_bam = 0
    for tab in tab_hien:
        try:
            page.locator('.nav-item[data-tab="%s"]' % tab).click(timeout=1500)
        except Exception:
            continue                            # ví dụ kiosk đã bị khoá ở chế độ học sinh: các lần sau sẽ bị từ chối
        page.wait_for_timeout(200)
        for stt, ten in _nut_hien(page):
            try:
                page.locator('.nav-item[data-tab="%s"]' % tab).click()
                e = page.locator('[data-quet="%s"]' % stt)
                if e.count() == 0 or e.evaluate("e => !!e.closest('.nav-item, #tkNutDangXuat')"):
                    continue                   # đổi thẻ / đăng xuất không phải nút làm việc (đã bấm thẻ ở vòng ngoài)
                if e.is_visible():
                    e.click(timeout=1500, no_wait_after=True)
                    da_bam += 1
                    page.wait_for_timeout(60)
            except Exception:
                pass
            page.keyboard.press("Escape")
        page.goto(url)                                               # bấm nút có thể chuyển trang/mở hộp: dựng lại
        page.wait_for_selector("#tkNutMoHop")
    assert getattr(api, "_che_do_hs", False) is False, "giáo viên không được tự khoá kiosk ở chế độ học sinh"
    assert [r[0] for r in _dong_tu_choi(api)] == []
    assert da_bam >= 5, da_bam                  # quét có thật sự bấm được nút (không trượt vì lỗi chọn phần tử)
    assert not loi, loi
