"""DK8-L5 (Playwright + Chromium): phản hồi tích cực cho ô nhập / nút của CỔNG đăng ký (giao diện chính không đổi).
(a) `DK.phanHoi` / `DK.chay`: lớp `.is-luu` (đang chạy) → `.is-xong` (ok) hoặc `.is-loi` (lỗi), CHỮ nút giữ nguyên, nút vẫn ≥ 44 px,
    không xê dịch bố cục, tắt chuyển động khi `prefers-reduced-motion`; thông báo cho trình đọc màn hình ở vùng riêng.
(b) dấu hợp lệ CHỈ theo ĐỊNH DẠNG ở mã học sinh, PIN, tên bắt buộc; KHÔNG BAO GIỜ ở nguyện vọng, huy chương, đáp án (bất biến 2).
(c) màn «Đã gửi»: đúng MỘT dấu ✓ vẽ một lần, tiêu đề giữ nguyên chữ.
Dữ liệu MÔ PHỎNG. Một fixture trang dùng chung."""
import datetime
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import test_dk3_api as t3  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok = t3.ok

# Nút thử dựng bằng chính DK.nut, bấm → DK.chay chờ một Promise do test giải (window.__giai(kq)).
DUNG_NUT = """(loai) => {
  const nut = DK[loai || "nut"]("Lưu thử", function () { DK.chay(this, () => new Promise((g) => { window.__giai = g; })); }, { id: "nutThu" });
  document.getElementById("dkApp").append(nut);
}"""


@pytest.fixture()
def cong(tmp_path):
    """Trả hàm `vao(gd)`: "dau" (trang chọn vai trò), "hs" (học sinh đã vào), "qt" (quản trị đã vào), "gv" (giáo viên đã vào)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        trang = []

        def vao(gd):
            thu_muc = tmp_path / ("c%d" % len(trang))
            thu_muc.mkdir()
            api = PipelineAPI(str(thu_muc / "app.db"))
            ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
            qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
            for ten, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
                ok(api.dk_phong_luu(qt, ten, sc))
            ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
            ok(api.dk_dat_han(qt, "gv_dang_ky", (datetime.datetime.now() + datetime.timedelta(days=2, hours=3)).strftime("%Y-%m-%dT%H:%M")))
            gv_pin = None
            if gd == "gv":
                gv_pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]["pin"]
            if gd == "hs":
                t3._dung_san(api, qt)
            url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
            pg = br.new_page(bypass_csp=True, viewport={"width": 1200, "height": 900})
            pg.loi = []
            pg.on("pageerror", lambda e: pg.loi.append(str(e)))
            pg.api, pg.qt = api, qt
            pg.goto(url)
            pg.wait_for_selector("text=Chọn vai trò")
            if gd == "hs":
                pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
                pg.get_by_role("button", name="Học sinh", exact=True).click()
                pg.fill("input[name=ten]", "H1")
                pg.fill("input[name=ma]", pin)
                pg.get_by_role("button", name="Đăng nhập").click()
                pg.wait_for_selector("text=Đúng là em chứ?")
            elif gd == "qt":
                pg.get_by_role("button", name="Quản trị", exact=True).click()
                pg.fill("input[name=ma]", "matkhau")
                pg.get_by_role("button", name="Đăng nhập").click()
                pg.wait_for_selector("text=Việc bây giờ")
            elif gd == "gv":
                pg.get_by_role("button", name="Giáo viên", exact=True).click()
                pg.fill("input[name=ten]", "Cô An")
                pg.fill("input[name=ma]", gv_pin)
                pg.get_by_role("button", name="Đăng nhập").click()
                pg.wait_for_selector("text=CLB của tôi")
            pg.wait_for_timeout(200)
            trang.append(pg)
            return pg
        yield vao
        assert all(p.loi == [] for p in trang)
        br.close()


def _lop(pg, sel="#nutThu"):
    return pg.locator(sel).evaluate("e => [...e.classList].filter(c => c.startsWith('is-'))")


# ---------------------------------------------------------------- (a) phản hồi của nút
def test_a_nut_dang_luu_roi_xong(cong):
    pg = cong("dau")
    pg.evaluate(DUNG_NUT)
    nut = pg.locator("#nutThu")
    nut.click()
    assert "is-luu" in _lop(pg) and nut.is_disabled() and nut.get_attribute("aria-busy") == "true"
    pg.evaluate("window.__giai({ ok: true })")
    pg.wait_for_selector("#nutThu.is-xong")
    assert "is-luu" not in _lop(pg) and nut.is_enabled() and nut.get_attribute("aria-busy") in (None, "false")
    assert nut.inner_text() == "Lưu thử"                                         # chữ không bị ghi đè
    pg.wait_for_selector("#nutThu:not(.is-xong)", timeout=2500)                  # ~800 ms rồi tự gỡ
    assert _lop(pg) == []


def test_b_nut_loi_rung_mot_lan_roi_go(cong):
    pg = cong("dau")
    pg.evaluate(DUNG_NUT)
    pg.locator("#nutThu").click()
    pg.evaluate("window.__giai({ ok: false, errors: ['Lỗi thử'] })")
    pg.wait_for_selector("#nutThu.is-loi")
    assert "is-xong" not in _lop(pg) and pg.locator("#nutThu").inner_text() == "Lưu thử"
    assert "Lỗi thử" in pg.locator("#dkThongBao").inner_text()                  # đường báo lỗi cũ vẫn chạy
    pg.wait_for_selector("#nutThu:not(.is-loi)", timeout=2500)


def test_c_nut_ném_lỗi_van_mo_lai_va_bao_loi(cong):
    pg = cong("dau")
    pg.evaluate("""() => { const n = DK.nut("Hỏng thử", function () { DK.chay(this, () => Promise.reject(new Error("x"))).catch(() => {}); }, { id: "nutThu" });
      document.getElementById("dkApp").append(n); }""")
    pg.locator("#nutThu").click()
    pg.wait_for_selector("#nutThu.is-loi")
    assert pg.locator("#nutThu").is_enabled()                                   # finally vẫn mở khoá


@pytest.mark.parametrize("loai", ["nut", "nutVang", "nutNhe"])
def test_d_khong_doi_chu_cao_44_va_khong_xe_dich(cong, loai):
    """Đo bằng offset* (bố cục, bỏ qua transform): cú rung của .is-loi là chuyển động, không phải xê dịch bố cục."""
    pg = cong("dau")
    pg.evaluate(DUNG_NUT, loai)
    nut = pg.locator("#nutThu")
    do = "e => [e.offsetLeft, e.offsetTop, e.offsetWidth, e.offsetHeight, e.parentElement.offsetHeight]"
    truoc = nut.evaluate(do)
    assert truoc[3] >= 44
    nut.click()
    pg.wait_for_selector("#nutThu.is-luu")
    for trang_thai, kq in (("is-luu", None), ("is-xong", "{ ok: true }"), ("is-loi", "{ ok: false, errors: ['x'] }")):
        if kq:
            if trang_thai == "is-loi":
                pg.wait_for_selector("#nutThu:not(.is-xong)", timeout=2500)
                pg.evaluate("document.getElementById('nutThu').click()")
                pg.wait_for_selector("#nutThu.is-luu")
            pg.evaluate("window.__giai(%s)" % kq)
            pg.wait_for_selector("#nutThu.%s" % trang_thai)
        pg.wait_for_timeout(120)
        dang = nut.evaluate(do)
        assert dang == truoc, "%s: bố cục đổi %s → %s" % (trang_thai, truoc, dang)
        assert dang[3] >= 44 and nut.inner_text() == "Lưu thử", trang_thai


def test_e_chuyen_dong_toi_da_600ms_va_tat_khi_giam_chuyen_dong(cong):
    pg = cong("dau")
    pg.evaluate(DUNG_NUT)
    pg.locator("#nutThu").click()
    pg.wait_for_selector("#nutThu.is-luu")
    tinh = """e => { const s = getComputedStyle(e), p = getComputedStyle(e, '::after');
      return [s.animationName, s.animationDuration, p.animationName, p.animationDuration]; }"""
    ten, dai, ten_p, dai_p = pg.locator("#nutThu").evaluate(tinh)
    assert ten != "none" or ten_p != "none"                                     # có chuyển động khi bình thường
    for d, n in ((dai, ten), (dai_p, ten_p)):
        if n != "none":
            assert max(float(x.rstrip("s")) for x in d.split(",")) <= 0.6
    pg.emulate_media(reduced_motion="reduce")
    ten, _, ten_p, _ = pg.locator("#nutThu").evaluate(tinh)
    assert ten == "none" and ten_p == "none"
    pg.evaluate("window.__giai({ ok: true })")
    pg.wait_for_selector("#nutThu.is-xong")
    assert pg.locator("#nutThu").evaluate("e => getComputedStyle(e, '::after').animationName") == "none"
    assert pg.locator("#nutThu").evaluate("e => getComputedStyle(e, '::after').display") != "none"     # dấu vẫn hiện: là TRẠNG THÁI


def test_f_vung_doc_man_hinh_ngoai_dkapp(cong):
    pg = cong("dau")
    pg.evaluate(DUNG_NUT)
    pg.locator("#nutThu").click()
    pg.evaluate("window.__giai({ ok: true })")
    pg.wait_for_selector("#nutThu.is-xong")
    vung = pg.locator("#dkPhanHoiLive")
    assert vung.count() == 1 and vung.get_attribute("aria-live") == "polite" and vung.get_attribute("role") == "status"
    assert vung.evaluate("e => !document.getElementById('dkApp').contains(e)")      # DK.hien không xoá nó
    assert "Thao tác hoàn tất" in vung.inner_text()


def test_g_luu_that_o_cai_dat_hien_dau_xong_tren_nut_van_con(cong):
    pg = cong("qt")
    pg.get_by_role("tab", name="Cài đặt").click()
    pg.wait_for_selector("#dkLuuMa")
    pg.get_by_role("button", name="Lưu mã", exact=True).click()
    pg.wait_for_selector("#dkLuuMa.is-xong")
    assert pg.locator("#dkLuuMa").inner_text() == "Lưu mã"


def test_h_doi_mat_khau_khong_khop_la_loi_khong_phai_xong(cong):
    pg = cong("qt")
    pg.get_by_role("tab", name="Cài đặt").click()
    pg.wait_for_selector("#dkDoiMk")
    pg.fill("input[name=mk_cu]", "matkhau")
    pg.fill("input[name=mk_moi]", "abcd1234")
    pg.fill("input[name=mk_lai]", "khac")
    pg.locator("#dkDoiMk").click()
    pg.wait_for_selector("#dkDoiMk.is-loi")
    assert "không giống nhau" in pg.locator("#dkThongBao").inner_text()
    assert pg.locator("#dkDoiMk.is-xong").count() == 0


def test_i_dau_xong_theo_nut_sau_khi_ve_lai(cong):
    pg = cong("qt")
    pg.get_by_role("button", name="+1 giờ", exact=True).click()                  # gia hạn xong thì lamMoi() dựng lại cả màn
    pg.wait_for_selector("button.is-xong:text-is('+1 giờ')", timeout=3000)       # dấu ✓ chuyển sang nút MỚI cùng tên (duy nhất)
    assert pg.locator("button.is-xong").count() == 1


# ---------------------------------------------------------------- (b) dấu hợp lệ chỉ theo định dạng
def test_j_ma_hoc_sinh_va_pin_chi_theo_dinh_dang(cong):
    pg = cong("dau")
    pg.get_by_role("button", name="Học sinh", exact=True).click()
    ten, ma = pg.locator("input[name=ten]"), pg.locator("input[name=ma]")
    assert not ten.evaluate("e => e.classList.contains('is-hop-le')")
    ten.fill("H1")
    assert ten.evaluate("e => e.classList.contains('is-hop-le')")
    ten.fill("   ")
    assert not ten.evaluate("e => e.classList.contains('is-hop-le')")
    ma.fill("123")
    assert not ma.evaluate("e => e.classList.contains('is-hop-le')")
    ma.fill("7391")
    assert ma.evaluate("e => e.classList.contains('is-hop-le')")
    ma.fill("12a4")
    assert not ma.evaluate("e => e.classList.contains('is-hop-le')")
    ten.fill("H1")
    ma.fill("0000")                                                             # đúng ĐỊNH DẠNG, chưa biết có đúng PIN hay không: vẫn chỉ là dấu định dạng
    assert ma.evaluate("e => e.classList.contains('is-hop-le')")
    nhan = pg.locator("label.dk-truong", has=pg.locator("input[name=ma]"))
    assert nhan.evaluate("e => getComputedStyle(e, '::after').content") == '""'                              # dấu vẽ bằng khung, không thêm chữ vào tên truy cập
    dau = nhan.evaluate("""e => { const c = getComputedStyle(e, '::after'), i = e.querySelector('input').getBoundingClientRect(), r = e.getBoundingClientRect();
      return [c.position, c.zIndex, parseFloat(c.width) > 0, r.right - parseFloat(c.right) <= i.right, r.bottom - parseFloat(c.bottom) <= i.bottom]; }""")
    assert dau == ["absolute", "1", True, True, True]                                                       # nằm TRONG ô và nổi trên ô (z-index), không bị ô vẽ đè


def test_k_dau_hop_le_khong_xe_dich_bo_cuc(cong):
    pg = cong("dau")
    pg.get_by_role("button", name="Học sinh", exact=True).click()
    ten = pg.locator("input[name=ten]")
    truoc = ten.bounding_box()
    nhan_truoc = pg.locator("label.dk-truong").first.bounding_box()
    ten.fill("H1")
    pg.wait_for_timeout(300)
    sau, nhan_sau = ten.bounding_box(), pg.locator("label.dk-truong").first.bounding_box()
    assert truoc == sau and nhan_truoc == nhan_sau
    assert sau["height"] >= 44


def test_l_quan_tri_mat_khau_khong_co_dau(cong):
    pg = cong("dau")
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    pg.fill("input[name=ma]", "matkhau")
    assert pg.locator("[data-hl], .is-hop-le").count() == 0                     # mật khẩu quản trị: tự do, không có dấu


def test_m_giao_vien_tu_dang_ky_va_ten_clb(cong):
    pg = cong("dau")
    pg.get_by_role("button", name="Giáo viên", exact=True).click()
    pg.get_by_role("button", name="Đăng ký tài khoản giáo viên").click()
    pg.fill("input[name=ten]", "Thầy B")
    pg.fill("input[name=pin]", "12")
    assert pg.locator("input[name=ten].is-hop-le").count() == 1 and pg.locator("input[name=pin].is-hop-le").count() == 0
    pg.fill("input[name=pin]", "7391")
    assert pg.locator("input[name=pin].is-hop-le").count() == 1


def test_n_ten_clb_bat_buoc_co_dau_khi_co_chu(cong):
    pg = cong("gv")
    pg.locator("label:has-text('Số học sinh nhận') input").fill("20")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.wait_for_selector("text=Bước 3/3")
    o = pg.locator("label:has-text('Tên CLB') input")
    assert not o.evaluate("e => e.classList.contains('is-hop-le')")
    o.fill("Robot")
    assert o.evaluate("e => e.classList.contains('is-hop-le')")
    o.fill("")
    assert not o.evaluate("e => e.classList.contains('is-hop-le')")


def test_o_khong_bao_gio_o_nguyen_vong_huy_chuong_dap_an(cong):
    pg = cong("hs")
    pg.get_by_role("button", name="Đúng là em", exact=True).click()
    pg.wait_for_selector("text=Buổi T2")
    dem = "document.querySelectorAll('[data-hl], .is-hop-le, select.is-xong, input[type=checkbox].is-xong').length"
    assert pg.evaluate(dem) == 0                                                 # bước xếp nguyện vọng
    for ten in ("Cờ vua", "Tự do 1", "Robot"):
        pg.locator("li.dk-the-clb", has_text=ten).get_by_role("button", name="+ Thêm").click()
    assert pg.evaluate(dem) == 0
    pg.get_by_role("button", name="Tiếp: đặt huy chương").click()
    pg.wait_for_selector("text=Đặt huy chương")
    pg.locator("select[aria-label='Huy chương Bạc']").select_option(index=1)       # tự đổi huy chương: KHÔNG có dấu nào
    assert pg.evaluate(dem) == 0
    pg.get_by_role("button", name="Tiếp: bài kiểm tra").click()
    pg.wait_for_selector("text=Bài kiểm tra")
    assert pg.evaluate(dem) == 0                                                 # bước bài kiểm tra (đáp án / tick thi)


# ---------------------------------------------------------------- (c) màn Đã gửi
def test_p_man_da_gui_mot_dau_tick_tieu_de_giu_chu(cong):
    pg = cong("hs")
    pg.get_by_role("button", name="Đúng là em", exact=True).click()
    pg.wait_for_selector("text=Buổi T2")
    for ten in ("Tự do 1", "Robot"):                                                  # VG2-L4: màn huy chương / bài thi chỉ hiện khi có CLB tương ứng
        pg.locator("li.dk-the-clb", has_text=ten).get_by_role("button", name="+ Thêm").click()
    for ten in ("Tiếp: đặt huy chương", "Tiếp: bài kiểm tra"):
        pg.get_by_role("button", name=ten).click()
    pg.get_by_role("button", name="Tiếp: T3").click()
    pg.wait_for_selector("text=Buổi T3")
    pg.get_by_role("button", name="Tiếp: xem lại và gửi").click()                       # buổi trống: đi thẳng, không qua huy chương / bài thi
    pg.locator("#dkGui").click()
    pg.wait_for_selector("#dkBienNhan")
    assert pg.locator(".dk-xong-dau").count() == 1
    dau = pg.locator(".dk-xong-dau")
    assert dau.get_attribute("aria-hidden") == "true" and dau.inner_text() == "" and "ux2-xong" in dau.get_attribute("class")
    assert pg.get_by_role("heading", name="Đã gửi", exact=True).count() == 1
    assert pg.locator("#dkBienNhan").inner_text().startswith("Đã gửi lúc")
    assert pg.get_by_role("button", name="Xong, thoát", exact=True).count() == 1


# ---------------------------------------------------------------- sửa CI: thanh trên dính khi trang dài
def test_q_thanh_tren_dinh_that_khi_trang_cuon_duoc(cong):
    """Chạy ở khổ thấp để trang CÓ cuộn (ở khổ cao thì trang ngắn, thanh trông như dính dù không dính)."""
    pg = cong("qt")
    pg.set_viewport_size({"width": 1200, "height": 360})
    pg.wait_for_timeout(200)
    assert pg.evaluate("document.documentElement.scrollHeight - window.innerHeight") > 150      # trang đủ dài để cuộn
    pg.mouse.wheel(0, 600)
    pg.wait_for_timeout(300)
    assert pg.evaluate("window.scrollY") > 100
    assert pg.locator("header.dk-dau").bounding_box()["y"] == 0                                    # cuộn rồi thanh vẫn ở trên cùng
