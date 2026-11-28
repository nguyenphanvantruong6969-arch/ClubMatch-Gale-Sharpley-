"""DKL-L2 / L4 (Playwright + Chromium): màn quản trị của cổng đăng ký so với bản mẫu v8.
Dữ liệu MÔ PHỎNG. Dựng trạng thái bằng API (nhanh), kiểm hành vi trên giao diện thật."""
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


def _clb(api, gv_pin_ten, ten, buoi, loai, phong, ct=None, san=None, link=""):
    tk = _ok(api.dk_dang_nhap("giao_vien", gv_pin_ten[0], gv_pin_ten[1]))["token"]
    d = {"ten": ten, "buoi": buoi, "loai": loai, "phong_id": phong, "khoi_tu": 9, "khoi_den": 12, "mo_ta": "x", "yeu_cau": "Không"}
    if ct:
        d["chi_tieu"] = ct
    if san is not None:
        d["diem_san"] = san
        d["link_forms"] = link
    return _ok(api.dk_clb_luu(tk, d))["clb_id"]


@pytest.fixture(scope="module")
def cong(tmp_path_factory):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path_factory.mktemp("dkl") / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TRU1", ["T2", "T3"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.dia_chi = api, qt, url
        yield pg
        br.close()


def _vao_quan_tri(pg):
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    pg.fill("input[name=ma]", "matkhau")
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị ·")


def test_1_chuan_bi_danh_sach_kiem_phong_xoa_thay_danh_sach(cong):
    pg, api, qt = cong, cong.api, cong.qt
    _vao_quan_tri(pg)
    # A8: chưa có phòng và học sinh -> lý do, KHÔNG có nút vàng mở đăng ký giáo viên
    assert "chưa có phòng" in pg.locator("#dkChuaDi").inner_text()
    assert pg.get_by_role("button", name="Mở đăng ký giáo viên").count() == 0
    _ok(api.dk_phong_luu(qt, "P1", 40))
    _ok(api.dk_phong_luu(qt, "PX", 10))
    _ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1\nH3\tChi\t10A2"))
    pg.reload()
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    pg.fill("input[name=ma]", "matkhau")
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị · Chuẩn bị")
    assert pg.get_by_role("button", name="Mở đăng ký giáo viên").count() == 1
    # A5: xoá phòng chưa dùng
    pg.locator("tr:has-text('PX')").get_by_role("button", name="Xoá").click()
    pg.wait_for_function("!document.body.innerText.includes('PX')")
    # A4 + A3: thay cả danh sách cần xác nhận, rồi phiếu PIN có đủ mã + PIN, không có băm
    pg.fill("textarea", "K1\tDũng\t10A1\nK2\tEm\t10A2")
    pg.get_by_role("button", name="Thay cả danh sách", exact=True).click()
    assert pg.locator("#dkThayHop").is_visible()
    pg.locator("#dkThayCo").click()
    pg.wait_for_selector("#dkPin table")
    pg.locator("#dkXemPhieu").click()
    phieu = pg.locator("#dkIn .dk-phieu")
    assert phieu.count() == 2
    txt = pg.locator("#dkIn").inner_text()
    assert "K1" in txt and "Giữ kín PIN" in txt
    html = pg.content()
    assert "pin_bam" not in html and "pin_muoi" not in html
    assert len(_ok(api.dk_hs_danh_sach(qt))) == 2


def test_2_gia_han_dong_ngay_va_duyet_sua_chi_tieu_phong(cong):
    pg, api, qt = cong, cong.api, cong.qt
    _ok(api.dk_phong_luu(qt, "P2", 30))
    r = _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))
    pin = {x["ten"]: x["pin"] for x in r["da_tao"]}
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    phong = {p["ten"]: p["phong_id"] for p in _ok(api.dk_phong_danh_sach(qt))}
    _clb(api, ("Cô An", pin["Cô An"]), "Tự do T2", "T2", "Tự do", phong["P1"])
    _clb(api, ("Cô Bê", pin["Cô Bê"]), "Cờ vua", "T2", "Giới hạn", phong["P2"], ct=20)
    _clb(api, ("Cô Bê", pin["Cô Bê"]), "Robot", "T3", "Tuyển chọn", phong["P2"], ct=10, san=6, link="https://f.example/x")
    _clb(api, ("Cô An", pin["Cô An"]), "Tự do T3", "T3", "Tự do", phong["P1"])
    _vao_quan_tri(pg)
    pg.wait_for_selector("text=Quản trị · Giáo viên đăng ký")
    # A1: gia hạn +1 giờ đặt hạn chót, hiện lại trên màn
    pg.get_by_role("button", name="+1 giờ").click()
    pg.wait_for_selector("#dkHan b")
    han1 = _ok(api.dk_trang_thai())["han_chot"]
    assert han1
    # Đóng ngay -> sang Duyệt CLB
    pg.once("dialog", lambda d: d.accept())      # VG2-L3: hỏi xác nhận
    pg.get_by_role("button", name="Đóng ngay").click()
    pg.wait_for_selector("text=Quản trị · Duyệt CLB")
    # A8: còn CLB chờ duyệt -> có lý do, chưa có nút "Mở cho học sinh"
    assert "chờ duyệt" in pg.locator("#dkChuaDi").inner_text()
    assert pg.get_by_role("button", name="Mở cho học sinh").count() == 0
    # A6: sửa chỉ tiêu và phòng trước khi duyệt
    dong = pg.locator("tr:has-text('Cờ vua')")
    dong.locator("input[type=number]").fill("15")
    dong.get_by_role("button", name="Duyệt", exact=True).click()
    pg.wait_for_function("document.querySelector(\"tr:has(td)\")!==null")
    pg.wait_for_selector("tr:has-text('Cờ vua'):has-text('Đã duyệt')")
    cv = [c for c in _ok(api.dk_clb_danh_sach(qt)) if c["ten"] == "Cờ vua"][0]
    assert cv["chi_tieu"] == 15
    for ten in ("Tự do T2", "Robot", "Tự do T3"):
        pg.locator("tr:has-text('%s')" % ten).get_by_role("button", name="Duyệt", exact=True).click()
        pg.wait_for_selector("tr:has-text('%s'):has-text('Đã duyệt')" % ten)
    pg.get_by_role("button", name="Mở cho học sinh").click()
    pg.wait_for_selector("text=Quản trị · Học sinh đăng ký")


def test_3_hoc_sinh_dang_ky_nhu_cau_chua_dang_ky_va_sua_sau_mo(cong):
    pg, api, qt = cong, cong.api, cong.qt
    pin = _ok(api.dk_hs_dat_lai_pin(qt, "K1"))["pin"]
    tk = _ok(api.dk_dang_nhap("hoc_sinh", "K1", pin))["token"]
    cl = {c["ten"]: c["clb_id"] for c in _ok(api.dk_hs_clb_hop_le(tk))}
    _ok(api.dk_hs_luu(tk, [
        {"clb_id": cl["Tự do T2"], "thi": False, "huy_chuong": None}, {"clb_id": cl["Cờ vua"], "thi": False, "huy_chuong": "Vàng"},
        {"clb_id": cl["Tự do T3"], "thi": False, "huy_chuong": None}, {"clb_id": cl["Robot"], "thi": True, "huy_chuong": "Vàng"}], ["T2", "T3"]))
    _vao_quan_tri(pg)
    pg.wait_for_selector("#dkNhuCau")
    # A7: nhu cầu theo CLB (admin), em chưa nộp nằm trong mục gập
    assert "Cờ vua" in pg.locator("#dkNhuCau").inner_text()
    pg.locator("#dkChuaDangKy summary").click()
    assert "K2" in pg.locator("#dkChuaDangKy").inner_text() and "K1" not in pg.locator("#dkChuaDangKy table").inner_text()
    # A1 ở giai đoạn học sinh: có "+1 ngày" và "Đóng ngay"
    assert pg.get_by_role("button", name="+1 ngày").count() == 1
    # A6b: tăng chỉ tiêu sau khi mở cho học sinh
    pg.locator("details:has(summary:has-text('Sửa CLB đã duyệt')) summary").click()
    dong = pg.locator("tr:has-text('Cờ vua')")
    dong.locator("input[type=number]").fill("18")
    dong.get_by_role("button", name="Tăng chỉ tiêu").click()
    pg.wait_for_function("document.body.innerText.includes('Quản trị · Học sinh đăng ký')")
    cv = [c for c in _ok(api.dk_clb_danh_sach(qt)) if c["ten"] == "Cờ vua"][0]
    assert cv["chi_tieu"] == 18


def test_4_nhap_diem_dan_go_duoi_san_chot_diem(cong):
    pg, api, qt = cong, cong.api, cong.qt
    _ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    _vao_quan_tri(pg)
    pg.wait_for_selector("text=Quản trị · Nhập điểm")
    assert pg.locator("details[open] summary:has-text('Robot')").count() == 1   # một CLB thi: mở sẵn
    # A2: gõ một điểm (dấu phẩy) -> chip Đạt; gõ dưới sàn -> chip "Dưới sàn"
    o = pg.locator("input.dk-diem").first
    o.fill("8,5")
    o.dispatch_event("change")
    pg.wait_for_selector("tr:has-text('K1') .chip:has-text('Đạt')")
    o.fill("8.5")                                                                      # dấu chấm cũng được nhận
    o.dispatch_event("change")
    pg.wait_for_selector("tr:has-text('K1') .chip:has-text('Đạt')")
    o.fill("4")
    o.dispatch_event("change")
    pg.wait_for_selector("tr:has-text('K1') .chip:has-text('Dưới sàn')")
    # dán "mã ⇥ điểm": dòng hợp lệ được lưu, dòng sai báo số dòng
    pg.locator("textarea").first.fill("K1\t9,5\nXX\t3")
    pg.get_by_role("button", name="Lưu điểm đã dán").click()
    pg.wait_for_function("document.body.innerText.includes('Đã lưu 1 điểm')")
    ds = _ok(api.dk_diem_danh_sach(qt))
    assert ds[0]["hoc_sinh"][0]["diem"] == 9.5
    pg.get_by_role("button", name="Chốt điểm", exact=True).click()
    pg.wait_for_function("document.getElementById('dkChotDiemKq').innerText.includes('đã có điểm')")
    assert not pg.loi, pg.loi


def test_5_the_cai_dat_ma_truong_gioi_han_va_khoa_buoi_khoi(cong):
    pg, api, qt = cong, cong.api, cong.qt
    _vao_quan_tri(pg)
    pg.get_by_role("tab", name="Cài đặt").click()
    pg.wait_for_selector("#dkLuuMa")
    assert pg.locator("input[name=buoi]").is_disabled() and pg.locator("#dkLuuBuoiKhoi").count() == 0     # sau Chuẩn bị: khoá
    pg.fill("input[name=ma_truong]", "ab")
    pg.locator("#dkLuuMa").click()
    pg.wait_for_selector(".dk-thongbao.la-loi")
    pg.fill("input[name=ma_truong]", "TRUONG9")
    pg.locator("#dkLuuMa").click()
    pg.wait_for_selector(".dk-thongbao.la-ok")
    assert _ok(api.dk_cai_dat_doc(qt))["ma_truong"] == "TRUONG9"
    pg.fill("input[name=toi_da_nv]", "8")
    pg.fill("input[name=toi_da_thi]", "3")
    pg.locator("#dkLuuGh").click()
    pg.wait_for_selector(".dk-thongbao.la-ok")
    c = _ok(api.dk_cai_dat_doc(qt))
    assert (c["toi_da_nv"], c["toi_da_thi"]) == (8, 3)


def test_6_sao_luu_xem_truoc_va_phien_ban_khi_xuat(cong):
    pg, api, qt = cong, cong.api, cong.qt
    _vao_quan_tri(pg)
    pg.get_by_role("tab", name="Thêm").click()
    pg.wait_for_selector("#dkSaoLuu")
    assert "Chưa sao lưu trong 60 phút qua" in pg.locator("#dkSaoLuuKq").inner_text()
    pg.locator("#dkSaoLuu").click()
    pg.wait_for_function("document.getElementById('dkSaoLuuKq').innerText.includes('Đã tạo bản sao lưu')")
    assert _ok(api.dk_cai_dat_doc(qt))["sao_luu_luc"]
    _ok(api.dk_chuyen_giai_doan(qt, "xuat"))
    pg.get_by_role("tab", name="Việc bây giờ").click()
    pg.wait_for_selector("#dkXemTruoc")
    # lỗi 3: bảng phải hiện sẵn, không cần bấm tiêu đề (thẻ details mở mặc định)
    pg.wait_for_selector("#dkXemTruoc table", state="visible", timeout=3000)
    assert "1. CLB" in pg.locator("#dkXemTruoc").inner_text() and "Robot" in pg.locator("#dkXemTruoc").inner_text()
    pg.get_by_role("button", name="Xuất Sổ nhập").click()
    pg.wait_for_function("document.getElementById('dkKq').innerText.length > 0")
    kq = pg.locator("#dkKq").inner_text()
    print("dkKq =", kq)
    assert "phiên bản 1" in kq, kq
    assert not pg.loi, pg.loi


def test_7_doi_phong_va_xoa_clb_sau_khi_mo_can_xac_nhan_va_bao_so_em_bi_anh_huong(cong):
    pg, api, qt = cong, cong.api, cong.qt
    _ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    _vao_quan_tri(pg)
    pg.wait_for_selector("text=Quản trị · Học sinh đăng ký")
    pg.locator("details:has(summary:has-text('Sửa CLB đã duyệt')) summary").click()
    loi = []
    pg.on("dialog", lambda d: (loi.append(d.message), d.accept()))
    dong = pg.locator("tr:has-text('Cờ vua')")
    ph = {p["ten"]: p["phong_id"] for p in _ok(api.dk_phong_danh_sach(qt))}
    goc = [c for c in _ok(api.dk_clb_danh_sach(qt)) if c["ten"] == "Cờ vua"][0]
    moi = "P1" if goc["phong"] != "P1" else "P2"
    # phòng đích đang bận ở buổi đó -> lỗi, không đổi
    dong.locator("select").select_option(str(ph[moi]))
    dong.get_by_role("button", name="Đổi phòng").click()
    pg.wait_for_selector(".dk-thongbao.la-loi, .dk-thongbao.la-ok", timeout=5000)
    # xoá CLB đã có em chọn: hộp xác nhận nêu số em bị ảnh hưởng, rồi mới xoá
    tk = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    dong = pg.locator("tr:has-text('Robot')")
    dong.get_by_role("button", name="Xoá CLB").click()
    pg.wait_for_function("!document.body.innerText.includes('Robot')", timeout=8000)
    assert loi and "học sinh bị ảnh hưởng" in loi[-1], loi
    assert "Robot" not in [c["ten"] for c in _ok(api.dk_clb_danh_sach(tk))]


def test_8_man_dang_nhap_noi_tu_khoa_2_phut_va_het_gio_hien_thong_bao(cong):
    pg = cong
    pg.clock.install()                                                          # đồng hồ giả: không phải chờ thật 2 phút
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    assert "Tự khoá sau 2 phút không thao tác." in pg.locator("#dkApp").inner_text()          # G2
    pg.fill("input[name=ma]", "matkhau")
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị ·")
    pg.clock.fast_forward(119_000)
    assert pg.get_by_text("Quản trị ·").count() >= 1                           # chưa đủ 2 phút: vẫn đăng nhập
    pg.clock.fast_forward(2_000)
    pg.wait_for_selector("text=Đã khoá quản lý vì không thao tác.")           # G3: A12
    pg.wait_for_selector("text=Chọn vai trò")
    assert not pg.loi, pg.loi
