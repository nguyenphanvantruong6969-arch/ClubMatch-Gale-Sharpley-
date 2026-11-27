"""DK5-L3 (Playwright + Chromium): diễn tập toàn trình qua GIAO DIỆN cổng đăng ký, ba vai trò trên MỘT bộ dữ liệu nhỏ
(24 học sinh, 3 CLB; 798 học sinh là việc của `test_dk5_dien_tap.py`). Dữ liệu MÔ PHỎNG.
Thứ tự các test là thứ tự thật: giáo viên → quản trị duyệt + mở → học sinh nộp → quản trị nhập điểm + «Chốt và xếp»."""
import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau"
SO_HS = 24


def _ok(r):
    assert r["ok"] and r["errors"] == [], r
    return r["data"]


@pytest.fixture(scope="module")
def cong(tmp_path_factory):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path_factory.mktemp("dk5ui") / "app.db"))
    _ok(api.dk_khoi_tao(MK, "TRUONG5", ["T2"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", MK))["token"]
    for t, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        _ok(api.dk_phong_luu(qt, t, sc))
    _ok(api.dk_hs_nap_danh_sach(qt, "\n".join("H%02d\tHS %02d (mô phỏng)\t%s" % (i, i, "10A1" if i % 2 else "10A2")
                                               for i in range(1, SO_HS + 1))))
    pin = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê\nCô Chi"))["da_tao"]}
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.pin, pg.dia_chi = api, qt, pin, url
        yield pg
        br.close()


def _clb_api(pg, gv, d):
    tk = _ok(pg.api.dk_dang_nhap("giao_vien", gv, pg.pin[gv]))["token"]
    phong = {p["ten"]: p["phong_id"] for p in _ok(pg.api.dk_phong_danh_sach(tk))}
    d = dict(d, phong_id=phong[d.pop("phong")], buoi="T2", khoi_tu=9, khoi_den=12, mo_ta="mô phỏng", yeu_cau="Không")
    return _ok(pg.api.dk_clb_luu(tk, d))["clb_id"]


def _vao_quan_tri(pg):
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    pg.fill("input[name=ma]", MK)
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị ·")


def test_1_giao_vien_dang_ky_va_thay_clb_cua_minh(cong):
    pg = cong
    # hai CLB còn lại do giáo viên khác tạo bằng API; giáo viên An tạo CLB Tự do bằng giao diện
    _clb_api(pg, "Cô Bê", {"ten": "Cờ vua", "loai": "Giới hạn", "phong": "P2", "chi_tieu": 12})
    _clb_api(pg, "Cô Chi", {"ten": "Robot", "loai": "Tuyển chọn", "phong": "P3", "chi_tieu": 8, "diem_san": 6,
                            "link_forms": "https://f.example/robot"})
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Giáo viên", exact=True).click()
    pg.fill("input[name=ten]", "Cô An")
    pg.fill("input[name=ma]", pg.pin["Cô An"])
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Bước 1/3")
    pg.locator("select").nth(1).select_option("Tự do")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.fill("label:has-text('Tên CLB') input", "Tự do UI")
    pg.get_by_role("button", name="Gửi duyệt").click()
    pg.wait_for_selector("li:has-text('Tự do UI'):has-text('Chờ duyệt')")
    txt = pg.locator("#dkApp").inner_text()
    assert "Cờ vua" not in txt and "Robot" not in txt          # giáo viên chỉ thấy CLB của mình
    assert not pg.loi, pg.loi


def test_2_quan_tri_duyet_va_mo_cho_hoc_sinh(cong):
    pg = cong
    _vao_quan_tri(pg)
    pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
    pg.once("dialog", lambda d: d.accept())      # VG2-L3: hỏi xác nhận
    pg.get_by_role("button", name="Đóng ngay").click()
    pg.wait_for_selector("text=Quản trị · Duyệt CLB")
    for ten in ("Tự do UI", "Cờ vua", "Robot"):
        pg.locator("tr:has-text('%s')" % ten).get_by_role("button", name="Duyệt", exact=True).click()
        pg.wait_for_selector("tr:has-text('%s'):has-text('Đã duyệt')" % ten)
    pg.get_by_role("button", name="Mở cho học sinh").click()
    pg.wait_for_selector("text=Quản trị · Học sinh đăng ký")
    assert _ok(pg.api.dk_trang_thai())["giai_doan"] == "hs_dang_ky"
    assert not pg.loi, pg.loi


def test_3_hoc_sinh_chon_thi_va_gui(cong):
    pg, api, qt = cong, cong.api, cong.qt
    # 23 em còn lại nộp bằng API (không thi); H01 nộp bằng giao diện, có thi Robot
    for i in range(2, SO_HS + 1):
        ma = "H%02d" % i
        tk = _ok(api.dk_dang_nhap("hoc_sinh", ma, _ok(api.dk_hs_dat_lai_pin(qt, ma))["pin"]))["token"]
        cl = {c["ten"]: c["clb_id"] for c in _ok(api.dk_hs_clb_hop_le(tk))}
        _ok(api.dk_hs_luu(tk, [{"clb_id": cl["Tự do UI"]}, {"clb_id": cl["Cờ vua"]}]))
    pin = _ok(api.dk_hs_dat_lai_pin(qt, "H01"))["pin"]
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Học sinh", exact=True).click()
    pg.fill("input[name=ten]", "H01")
    pg.fill("input[name=ma]", pin)
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.get_by_role("button", name="Đúng là em", exact=True).click()
    pg.wait_for_selector("text=Buổi T2")
    for _ in range(3):                                      # chọn cả ba CLB (thứ tự hiện được xáo theo từng em)
        pg.locator("button:has-text('+ Thêm')").first.click()
        pg.wait_for_timeout(120)
    for _ in range(4):                                      # tới bước bài kiểm tra
        if pg.get_by_role("heading", name="Buổi T2 · Bài kiểm tra").count():
            break
        pg.locator("#dkApp .btn-primary:visible").first.click()
        pg.wait_for_timeout(120)
    pg.locator("input[type=checkbox]").first.check()
    for _ in range(12):
        if pg.get_by_role("heading", name="Xem lại và gửi").count():
            break
        pg.locator("#dkApp .btn-primary:visible").first.click()
        pg.wait_for_timeout(150)
    pg.locator("#dkGui").click()
    pg.wait_for_selector("#dkBienNhan")
    assert "Đã gửi lúc" in pg.locator("#dkBienNhan").inner_text()
    assert pg.get_by_role("link", name="Làm bài thi").get_attribute("href") == "https://f.example/robot"
    c = sqlite3.connect(api.db_path)
    try:
        assert c.execute("SELECT COUNT(*) FROM dk_hoc_sinh WHERE nop_luc IS NOT NULL").fetchone()[0] == SO_HS
        assert c.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE student_id = 'H01' AND thi = 1").fetchone()[0] == 1
    finally:
        c.close()
    assert not pg.loi, pg.loi


def test_4_quan_tri_nhap_diem_chot_va_xep_xem_ket_qua(cong):
    pg, api, qt = cong, cong.api, cong.qt
    _ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    _vao_quan_tri(pg)
    pg.wait_for_selector("text=Quản trị · Nhập điểm")
    pg.locator("textarea").first.fill("H01\t8")
    pg.get_by_role("button", name="Lưu điểm đã dán").click()
    pg.wait_for_function("document.body.innerText.includes('Đã lưu 1 điểm')")
    assert _ok(api.dk_diem_thieu(qt)) == []
    pg.wait_for_selector("#dkChot")
    pg.click("#dkChot")
    pg.wait_for_selector("#dkKetQua")
    assert "Đã xếp" in pg.inner_text("#dkKetQua")
    assert pg.locator("#dkKetQua tbody tr").count() >= 1
    assert not pg.loi, pg.loi
    c = sqlite3.connect(api.db_path)
    try:
        assert c.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 1
        assert c.execute("SELECT COUNT(DISTINCT student_id) FROM match_results").fetchone()[0] == SO_HS
    finally:
        c.close()
    assert _ok(api.dk_trang_thai())["giai_doan"] == "xuat"
