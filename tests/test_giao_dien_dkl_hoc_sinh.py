"""DKL-L1 (Playwright + Chromium): màn học sinh so với bản mẫu v8 — mỗi hàng DK4-UI đã làm có một test hành vi, thêm
chữ "Dưới … thì không xét" cho CLB Tuyển chọn và câu khi hết hạn. Dữ liệu MÔ PHỎNG."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ok(r):
    assert r["ok"], r
    return r["data"]


@pytest.fixture(scope="module")
def cong(tmp_path_factory):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path_factory.mktemp("dklhs") / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TR1", ["T2", "T3"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    _ok(api.dk_phong_luu(qt, "P1", 40))
    _ok(api.dk_phong_luu(qt, "P2", 30))
    for k in range(1, 8):
        _ok(api.dk_phong_luu(qt, "Q%d" % k, 20))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1"))
    pin = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê\n" + "\n".join("Cô G%d" % k for k in range(1, 8))))["da_tao"]}
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    ph = {p["ten"]: p["phong_id"] for p in _ok(api.dk_phong_danh_sach(qt))}
    ga = _ok(api.dk_dang_nhap("giao_vien", "Cô An", pin["Cô An"]))["token"]
    gb = _ok(api.dk_dang_nhap("giao_vien", "Cô Bê", pin["Cô Bê"]))["token"]
    base = {"khoi_tu": 9, "khoi_den": 12, "yeu_cau": "Mang vợt"}
    ids = {}
    for tk, ten, buoi, loai, phong, ex in ((ga, "Tự do T2", "T2", "Tự do", "P1", {"mo_ta": "Chơi tự do"}),
                                           (gb, "Robot", "T2", "Tuyển chọn", "P2", {"chi_tieu": 10, "diem_san": 6, "link_forms": "https://f.example/robot", "mo_ta": "Lắp robot"}),
                                           (ga, "Tự do T3", "T3", "Tự do", "P1", {"mo_ta": "Tự do T3"})):
        ids[ten] = _ok(api.dk_clb_luu(tk, dict(base, ten=ten, buoi=buoi, loai=loai, phong_id=ph[phong], **ex)))["clb_id"]
    for k in range(1, 8):                                                        # D37: buổi T3 có 8 CLB (1 + 7)
        tk = _ok(api.dk_dang_nhap("giao_vien", "Cô G%d" % k, pin["Cô G%d" % k]))["token"]
        ids["Phụ %d" % k] = _ok(api.dk_clb_luu(tk, dict(base, ten="Phụ %d" % k, buoi="T3", loai="Tự do", phong_id=ph["Q%d" % k], mo_ta="Phụ")))["clb_id"]
    _ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    for cid in ids.values():
        _ok(api.dk_clb_duyet(qt, cid, "duyet"))
    _ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    _ok(api.dk_dat_han(qt, "hs_dang_ky", "2099-01-01T08:00"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1366, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.ids, pg.dia_chi = api, qt, ids, url
        yield pg
        br.close()


def _vao_hs(pg, ma, xac_nhan=True):
    pin = _ok(pg.api.dk_hs_dat_lai_pin(pg.qt, ma))["pin"]
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Học sinh", exact=True).click()
    pg.fill("input[name=ten]", ma)
    pg.fill("input[name=ma]", pin)
    pg.get_by_role("button", name="Đăng nhập").click()
    if xac_nhan:                                                          # DKL-G1: bước "Đúng là em chứ?"
        pg.get_by_role("button", name="Đúng là em", exact=True).click()


def _toi_xem_lai(pg):
    for _ in range(12):
        if pg.get_by_role("heading", name="Xem lại và gửi").count():
            return
        pg.locator("#dkApp .btn-primary:visible").first.click()
        pg.wait_for_timeout(150)


def test_1_the_clb_co_mo_ta_yeu_cau_giao_vien_phong_va_khong_lo_so_dong(cong):
    pg = cong
    _vao_hs(pg, "H1")
    pg.wait_for_selector("text=Buổi T2")
    txt = pg.locator("#dkApp").inner_text()
    assert "Lắp robot" in txt and "Yêu cầu: Mang vợt" in txt and "Cô Bê" in txt and "P2" in txt          # S3
    assert "khối 9–12" in txt
    assert "nhu cầu" not in txt.lower() and "đã chọn" not in txt.lower()          # D26: học sinh không thấy số đông
    assert not pg.loi, pg.loi


def test_2_gui_roi_bien_nhan_co_link_bai_thi_gio_gui_va_xong_thoat(cong):
    pg = cong
    for _ in range(2):                                    # chọn cả hai CLB của buổi T2 (thứ tự hiện được xáo theo từng em)
        pg.locator("button:has-text('+ Thêm')").first.click()
        pg.wait_for_timeout(120)
    for _ in range(4):                                    # đi tới bước "Buổi T2 · Bài kiểm tra"
        if pg.get_by_role("heading", name="Buổi T2 · Bài kiểm tra").count():
            break
        pg.locator("#dkApp .btn-primary:visible").first.click()
        pg.wait_for_timeout(120)
    assert pg.get_by_text("thì không xét").count() >= 1                         # S2: "Dưới 6 thì không xét"
    assert "Không làm bài, hoặc dưới mốc điểm" in pg.locator("#dkApp").inner_text()
    pg.locator("input[type=checkbox]").first.check()
    _toi_xem_lai(pg)
    pg.locator("#dkGui").click()
    pg.wait_for_selector("#dkBienNhan")
    assert "Đã gửi lúc" in pg.locator("#dkBienNhan").inner_text()               # S6
    link = pg.get_by_role("link", name="Làm bài thi")
    assert link.count() == 1 and link.get_attribute("href") == "https://f.example/robot"      # S1
    assert pg.get_by_role("button", name="Xong, thoát").count() == 1
    assert "2099" in pg.locator("#dkApp").inner_text()                          # S4: hạn chót hiện cho học sinh
    pg.get_by_role("button", name="Xong, thoát").click()
    pg.wait_for_selector("text=Chọn vai trò")


def test_3_nop_rong_co_canh_bao_va_han_chot_hien_cho_hoc_sinh(cong):
    pg = cong
    _vao_hs(pg, "H2")
    pg.wait_for_selector("text=Buổi T2")
    _toi_xem_lai(pg)
    assert "Em chưa chọn CLB nào" in pg.locator("#dkApp").inner_text()          # S5


def test_3b_xac_nhan_danh_tinh_dung_la_em_khong_phai_em(cong):
    pg = cong
    _vao_hs(pg, "H2", xac_nhan=False)                                            # G1: chưa gửi lần nào
    pg.get_by_role("heading", name="Đúng là em chứ?").wait_for()
    txt = pg.locator("#dkApp").inner_text()
    assert "Bình" in txt and "Lớp 10A1 · Khối 10 · Mã H2" in txt
    assert "Em đã gửi lúc" not in txt and pg.get_by_text("Buổi T2").count() == 0
    pg.get_by_role("button", name="Không phải em").click()
    pg.wait_for_selector("text=Chọn vai trò")
    _vao_hs(pg, "H1", xac_nhan=False)                                            # đã gửi ở test_2
    pg.get_by_role("heading", name="Đúng là em chứ?").wait_for()
    assert "Em đã gửi lúc" in pg.locator("#dkApp").inner_text()
    assert "lần gửi cuối cùng được tính" in pg.locator("#dkApp").inner_text()
    pg.get_by_role("button", name="Đúng là em", exact=True).click()
    pg.wait_for_selector("text=Buổi T2")
    assert not pg.loi, pg.loi


def test_3c_moi_buoi_toi_da_7_the_roi_xem_them(cong):
    pg = cong
    _vao_hs(pg, "H2")
    for _ in range(6):                                                           # đi tới bước xếp nguyện vọng buổi T3
        if pg.get_by_role("heading", name="Buổi T3 · Xếp nguyện vọng").count():
            break
        pg.locator("#dkApp .btn-primary:visible").first.click()
        pg.wait_for_timeout(120)
    assert pg.locator("li.dk-the-clb:visible").count() == 7                      # G4/D37: tám CLB, chỉ bảy thẻ hiện
    nut = pg.get_by_role("button", name="Xem thêm (1)")
    assert nut.count() == 1
    nut.click()
    assert pg.locator("li.dk-the-clb:visible").count() == 8
    assert pg.get_by_role("button", name="Xem thêm (1)").count() == 0
    pg.get_by_role("button", name="Đăng xuất").click()
    pg.wait_for_selector("text=Chọn vai trò")
    assert not pg.loi, pg.loi


def test_3d_gioi_han_nguyen_vong_va_bai_thi_noi_ro_la_tinh_rieng_tung_buoi(cong):
    """Giới hạn 10 nguyện vọng / 5 bài thi tính riêng TỪNG BUỔI: giao diện phải nói rõ, và khi nút bị khoá phải có lý do.
    Đặt giới hạn nhỏ (3 và 1) để chạm trần với dữ liệu ít; trả về mặc định ở cuối. Dữ liệu MÔ PHỎNG."""
    pg = cong
    _ok(pg.api.dk_dat_gioi_han(pg.qt, 3, 1))
    try:
        _vao_hs(pg, "H2")
        pg.wait_for_selector("text=Xếp nguyện vọng")
        chu = pg.locator("#dkApp").inner_text()
        assert "tính riêng cho từng buổi" in chu and "0/3" in chu            # nói rõ phạm vi, chưa đủ thì chưa báo "đã đủ"
        assert "đã đủ" not in chu.lower()
        for _ in range(2):                                                    # buổi T2 có hai CLB
            pg.locator("button:has-text('+ Thêm')").first.click()
            pg.wait_for_timeout(100)
        for _ in range(4):                                                    # tới bước bài kiểm tra T2
            if pg.get_by_role("heading", name="Buổi T2 · Bài kiểm tra").count():
                break
            pg.locator("#dkApp .btn-primary:visible").first.click()
            pg.wait_for_timeout(120)
        assert "Giới hạn 1 bài thi tính riêng cho từng buổi" in pg.locator("#dkApp").inner_text()
        pg.locator("input[type=checkbox]").first.check()
        chu = pg.locator("#dkApp").inner_text()
        assert "Buổi T2 đã tick đủ 1 bài thi" in chu and "bỏ tick" in chu
        pg.locator("#dkApp .btn-primary:visible").first.click()              # sang buổi T3
        pg.wait_for_selector("text=Buổi T3 · Xếp nguyện vọng")
        for _ in range(3):
            pg.locator("button:has-text('+ Thêm'):not([disabled])").first.click()
            pg.wait_for_timeout(100)
        chu = pg.locator("#dkApp").inner_text()
        assert "Buổi T3 đã đủ 3 CLB" in chu and "tính riêng cho từng buổi" in chu and "✕" in chu
        khoa = pg.locator("button:has-text('+ Thêm')[disabled]").first
        assert "đủ 3 CLB" in khoa.get_attribute("title")                      # nút khoá có lý do ngay trên nút
        pg.get_by_role("button", name="Đăng xuất").click()
        pg.wait_for_selector("text=Chọn vai trò")
        assert not pg.loi, pg.loi
    finally:
        _ok(pg.api.dk_dat_gioi_han(pg.qt, 10, 5))


def test_4_het_han_hien_cau_nguyen_vong_da_gui_van_duoc_tinh(cong):
    pg = cong
    _ok(pg.api.dk_chuyen_giai_doan(pg.qt, "nhap_diem"))
    _vao_hs(pg, "H1", xac_nhan=False)                                           # hết hạn: không qua bước xác nhận
    pg.wait_for_selector("#dkHsDong")
    assert "Nguyện vọng em đã gửi vẫn được tính" in pg.locator("#dkHsDong").inner_text()
    assert not pg.loi, pg.loi
