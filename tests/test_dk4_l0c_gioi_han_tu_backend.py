"""DK4-L0c: giới hạn 10 nguyện vọng / 5 bài thi mỗi buổi đọc từ phần mềm (dk_trang_thai), không viết cứng trong JS."""
import os
import re

import pytest

import api_dang_ky
import test_dk3_api as _t3
from test_dk3_api import _clb, ok

cd = _t3.cd
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_trang_thai_tra_gioi_han(cd):
    api, qt = cd
    d = ok(api.dk_trang_thai())
    assert d["toi_da_nv"] == api_dang_ky.TOI_DA_NV_BUOI and d["toi_da_thi"] == api_dang_ky.TOI_DA_THI_BUOI


def test_js_khong_viet_cung_gioi_han():
    ma_js = open(os.path.join(GOC, "js", "dang_ky_gv_hs.js"), encoding="utf-8").read()
    assert not re.search(r">=\s*(5|10)\b", ma_js)
    assert "tt.toi_da_nv" in ma_js and "tt.toi_da_thi" in ma_js


def test_giao_dien_theo_gioi_han_do_phan_mem_dat(tmp_path, monkeypatch):
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    import browser_host
    from _trinh_duyet import CHROMIUM
    from api import PipelineAPI
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    monkeypatch.setattr(api_dang_ky, "TOI_DA_NV_BUOI", 2)
    monkeypatch.setattr(api_dang_ky, "TOI_DA_THI_BUOI", 1)
    api = PipelineAPI(str(tmp_path / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRU1", ["T2"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t in ("P1", "P2", "P3", "P4"):
        ok(api.dk_phong_luu(qt, t, 40))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    gvs = ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê\nCô Chi\nCô Dư"))["da_tao"]
    for i, (ten, gv) in enumerate(zip("TABC", gvs), start=1):
        tg = ok(api.dk_dang_nhap("giao_vien", gv["ten"], gv["pin"]))["token"]
        c = ok(api.dk_clb_luu(tg, _clb(ten=ten, loai="Tự do" if ten == "T" else "Tuyển chọn", chi_tieu=10, diem_san=5, buoi="T2", phong_id=i)))["clb_id"]
        ok(api.dk_clb_duyet(qt, c, "duyet"))
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        pg = br.new_page(bypass_csp=True, viewport={"width": 1100, "height": 900})
        pg.goto(browser_host.serve(api, GOC, "dang_ky.html", open_browser=False))
        pg.get_by_role("button", name="Học sinh", exact=True).click()
        pg.fill("input[name=ten]", "H1")
        pg.fill("input[name=ma]", pin)
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.get_by_role("button", name="Đúng là em", exact=True).click()              # DKL-G1
        pg.wait_for_selector("text=Buổi T2")
        for ten in ("A", "B"):
            pg.locator("ul.dk-ds li", has_text=ten).first.get_by_role("button", name="+ Thêm").click()
        assert pg.locator("button:enabled", has_text="+ Thêm").count() == 0              # đủ 2 nguyện vọng (giới hạn do phần mềm đặt)
        pg.get_by_role("button", name="Tiếp: đặt huy chương").click()
        pg.get_by_role("button", name="Tiếp: bài kiểm tra").click()               # DK4-UI: ô thi nằm ở bước "Bài kiểm tra"
        boxes = pg.locator("label.dk-thi input")
        boxes.nth(0).check()
        assert boxes.nth(1).is_disabled()                                         # đủ 1 bài thi
        br.close()
