"""Sửa (Truong, 2026-11-28): bước 5 «Nhập điểm» của quản trị cổng đăng ký không dẫn tới bước «Xuất».

(1) Ô điểm chỉ lưu khi rời ô (sự kiện `change`); gõ điểm cuối rồi bấm ngay «Chốt và xếp» thì lệnh lưu điểm và lệnh chốt
    chạy song song -> chốt thấy còn thiếu điểm và từ chối. Nay «Chốt và xếp» chờ các ô điểm đang lưu xong rồi mới chốt.
(2) Còn thiếu điểm thì phải nói rõ NGAY cạnh nút (bao nhiêu bài, CLB nào, em nào), không chỉ một thông báo thoáng qua;
    «Chốt điểm» ở cuối bảng vẽ lại màn để con số và nút cập nhật. Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402
from test_dk4_chot_va_xep import _dang_ky_va_cham, ok  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture()
def buoc5(tmp_path):
    """Cổng ở giai đoạn Nhập điểm, H1 thi Robot nhưng CHƯA có điểm; quản trị đã đăng nhập. Trả (trang, api, qt, robot)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, t, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ids = _dang_ky_va_cham(api, qt)
    ok(api.dk_diem_dat(qt, "H1", ids["Robot"], None))                 # bỏ điểm: còn đúng 1 bài thiếu
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1100, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.goto(url)
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", "matkhau")
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.wait_for_selector("text=Quản trị · Nhập điểm")
        yield pg, api, qt, ids["Robot"]
        assert pg.loi == []
        br.close()


def _cham_cham(api, giay=0.8):
    """Làm chậm riêng lệnh lưu điểm ở phía Python (như máy chậm / CSDL bận). Cầu nối chạy mỗi lời gọi một luồng (như
    pywebview), nên «Chốt và xếp» bấm ngay sau đó chạy SONG SONG với lệnh lưu điểm còn đang dở."""
    import time
    goc = api.dk_diem_dat

    def cham(*a, **k):
        time.sleep(giay)
        return goc(*a, **k)
    api.dk_diem_dat = cham


def test_go_diem_cuoi_roi_bam_ngay_chot_va_xep_thi_sang_buoc_xuat(buoc5):
    pg, api, qt, _ = buoc5
    _cham_cham(api)
    pg.fill("input[aria-label='Điểm H1']", "8")                       # chưa rời ô: điểm chưa được gửi
    pg.click("#dkChot")
    pg.wait_for_selector("#dkKetQua", timeout=15000)
    assert ok(api.dk_ket_qua_xep(qt))["da_xep"]


def test_con_thieu_diem_thi_noi_ro_canh_nut(buoc5):
    pg, *_ = buoc5
    o = pg.locator("#dkThieuDiem")
    assert o.is_visible()
    chu = o.inner_text()
    assert "1 bài thi" in chu and "Robot" in chu and "H1" in chu
    pg.click("#dkChot")                                                # vẫn bấm được: lỗi hiện ngay cạnh nút
    pg.wait_for_selector("#dkThieuDiem:has-text('chưa có điểm')")
    assert pg.locator("#dkKetQua").count() == 0


def test_chot_diem_ve_lai_man_khi_da_du_diem(buoc5):
    pg, *_ = buoc5
    pg.fill("input[aria-label='Điểm H1']", "8")
    pg.locator("input[aria-label='Điểm H1']").blur()
    pg.click("#dkChotDiem")
    pg.wait_for_selector("text=1/1 bài đã có điểm")
    assert pg.locator("#dkThieuDiem").count() == 0
    assert pg.locator("#dkApp .btn-primary:visible").count() == 1        # vẫn chỉ MỘT nút vàng: «Chốt và xếp»
