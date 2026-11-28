"""UX6-L3: chi tiết nhất quán (Chromium thật; dữ liệu MÔ PHỎNG: sổ 120 học sinh, seed 42).
Logo, biểu tượng thay ký tự chữ, một màu nhấn cho nút phân đoạn, mono chỉ cho mã máy, tiêu đề cột kiểu câu,
bảng CLB (mã dưới tên, nút xoá bằng biểu tượng), biểu mẫu thiết lập lần đầu của cổng đăng ký."""

import os
import re


from _ux5a_chung import GOC, mo_ux5a  # noqa: F401


def _doc(ten):
    return open(os.path.join(GOC, ten), encoding="utf-8").read()


def _bo_chu_thich(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", s)


def test_khong_con_ky_tu_chu_lam_bieu_tuong_trong_index_va_js():
    for ten in ["index.html", "i18n.js"] + ["js/" + f for f in sorted(os.listdir(os.path.join(GOC, "js")))]:
        s = _bo_chu_thich(_doc(ten))
        assert "▾" not in s, ten
        assert "⋯" not in s, ten


def test_thanh_ben_dung_logo_anh_thay_chu_rb():
    s = _doc("index.html")
    m = re.search(r'<[^>]*class="[^"]*\bbrand-mark\b[^"]*"[^>]*>', s)
    assert m and m.group(0).startswith("<img") and "logo" in m.group(0), m and m.group(0)


def test_nut_ba_cham_co_nhan_va_goi_y(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "results")
    nut = page.locator("#menuThanhBen > summary")
    assert nut.get_attribute("aria-label") and nut.get_attribute("title")
    assert nut.inner_text().strip() == ""
    assert not loi, loi


def test_nut_phan_doan_cung_mau_nhan_va_co_chu_voi_the_khac(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "results")
    page.locator('.kq-seg-nut[data-kq="clb"]').click()
    r = page.evaluate("""() => { const on = document.querySelector('#kqTang1 .kq-seg-nut.is-on');
      const cs = getComputedStyle(on); return {bg: cs.backgroundColor, fs: parseFloat(cs.fontSize), ff: cs.fontFamily,
        body: getComputedStyle(document.body).fontFamily}; }""")
    assert r["bg"] != "rgb(63, 107, 82)", r              # không còn nền xanh rêu đặc
    assert r["fs"] <= 15, r                              # cùng cỡ chữ với các nút tab khác (13.5–15 px)
    assert r["ff"] == r["body"], r
    assert not loi, loi


def test_mono_chi_cho_ma_may_va_tieu_de_cot_kieu_cau(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "results")
    ff = page.evaluate("""() => ['.ws-switcher-nhan', '#btnLangToggle'].map(s => getComputedStyle(document.querySelector(s)).fontFamily)""")
    assert all("mono" not in f.lower() for f in ff), ff
    th = page.evaluate("""() => { const e = document.querySelector('#view-results th');
      const cs = getComputedStyle(e); return [cs.textTransform, cs.letterSpacing]; }""")
    assert th[0] == "none" and th[1] in ("normal", "0px"), th
    assert not loi, loi


def test_bang_clb_ma_duoi_ten_va_nut_xoa_bang_bieu_tuong_bam_duoc_bang_ban_phim(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "admin")
    page.locator('#qlTabs [data-ql-tab="clb"]').click()
    page.wait_for_selector("#adminClubTableBody tr")
    hang = page.locator("#adminClubTableBody tr").first
    cid = hang.get_attribute("data-club-id")
    assert hang.locator(".ux6-ma-clb").inner_text().strip() == cid
    assert hang.locator("td").first.locator(".ux6-ma-clb").count() == 1      # mã nằm trong ô Tên, không còn cột riêng
    dau = page.eval_on_selector_all("table:has(#adminClubTableBody) thead th",
                                    "t => t.filter(x => x.offsetParent !== null).map(x => x.textContent.trim())")
    assert "Mã CLB" not in dau, dau
    nut = hang.locator("button.btn-icon-danger")
    assert nut.get_attribute("aria-label"), "nút xoá cần aria-label"
    nut.focus()                                                              # tới được bằng bàn phím và hiện khi có tiêu điểm
    page.wait_for_function("() => getComputedStyle(document.activeElement).opacity === '1'")     # hết thời gian chuyển mờ
    kt = nut.bounding_box()
    assert kt["width"] >= 44 and kt["height"] >= 44, kt
    assert not loi, loi


def test_thiet_lap_lan_dau_cong_dang_ky_co_vi_du_hai_khoi_cung_hang_va_nut_khong_rong_het_the():
    s = _doc("js/dang_ky_nen.js")
    m = re.search(r"DK\.manKhoiTao = function \(\) \{.*?\n  \};", s, re.S)
    ham = m.group(0)
    assert "placeholder" in ham, "cần chữ ví dụ trong ô"
    assert "dk-hang-khoi" in ham, "Khối thấp nhất và Khối cao nhất nằm cùng một hàng"
    assert "day(DK.nutVang" not in ham, "nút thiết lập không rộng hết thẻ"
