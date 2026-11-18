"""GT4-L7 — khung "Tiêu chí xếp" và "Thử cấu hình" được thiết kế lại: nhãn nằm TRÊN ô, hai cột ở >= 1000 px,
ô tích không đè chữ, trang so sánh có hai thẻ lần chạy / tóm tắt / chênh lệch / danh sách gập, không `__mac_dinh__`,
cảnh báo cấu hình vô nghĩa, và các khung GT khác (tra cứu, hộp tài khoản, màn học sinh) cùng một nhịp thiết kế:
nhãn trên ô, chữ >= 14 px, ô bấm >= 36 px cao, tương phản >= 4,5:1. Chromium. Dữ liệu MÔ PHỎNG."""

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

# JS: hộp (top, bottom, left, right) của các phần tử trong một khung
JS_HOP = """(sel) => [...document.querySelectorAll(sel)].filter(e => e.offsetParent !== null).map(e => {
  const r = e.getBoundingClientRect(); const ctl = e.tagName === 'LABEL' && e.htmlFor ? document.getElementById(e.htmlFor) : null;
  return {id: e.tagName === 'LABEL' ? (e.getAttribute('for') || e.id) : e.id || e.tagName, top: r.top, bottom: r.bottom,
  left: r.left, right: r.right, tag: e.tagName, boc: !!(ctl && e.contains(ctl))}; })"""

JS_TUONG_PHAN = """(sels) => {
  const lum = (c) => { const m = c.match(/[\\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
  const nen = (e) => { for (let n = e; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor;
    const m = c.match(/[\\d.]+/g).map(Number); if (m.length < 4 || m[3] > 0.9) return c; } return 'rgb(255,255,255)'; };
  const ra = [];
  for (const s of sels) for (const e of document.querySelectorAll(s)) {
    if (e.offsetParent === null || !e.textContent.trim()) continue;
    const a = lum(getComputedStyle(e).color), b = lum(nen(e));
    ra.push({sel: s, ti: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05), co: parseFloat(getComputedStyle(e).fontSize),
             cao: e.getBoundingClientRect().height, chu: e.textContent.trim().slice(0, 30)});
  }
  return ra; }"""


@pytest.fixture
def mo(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    os.makedirs(str(tmp_path / "nguon"))
    nguon = d.nap_bo(str(tmp_path / "nguon"), d.BO_DU_LIEU[1][1])
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}, "name": "Trường Thử"})
    api = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    loi = []

    def trang(rong=1280, cao=900):
        page = br.new_page(viewport={"width": rong, "height": cao}, locale="vi-VN", bypass_csp=True)
        page.set_default_timeout(8000)
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#gt2TieuChiPanel", state="attached")
        page.click('button.nav-item[data-tab="admin"]')
        page.evaluate("document.getElementById('ux1aNangCao').open = true")  # UX1A-L2: Nâng cao đóng mặc định
        page.wait_for_selector("#gt2TcDanhSach li")
        return page

    try:
        yield trang, api, loi
    finally:
        br.close()
        pw.stop()


def _khong_nhan_chung_hang(page, khung):
    """Không nhãn nào cùng dòng với ô nhập của một trường KHÁC (nhãn luôn nằm trên ô của chính nó)."""
    # MỘT lần đo cho cả nhãn và ô: hai lần đo rời nhau có thể rơi vào hai lần dàn trang khác nhau (danh sách tài khoản
    # nạp xong giữa chừng làm cả khối dịch xuống), CI chậm từng báo "nhãn cùng dòng" oan.
    nhan, cac_o = page.evaluate(
        "([f, hop]) => { const m = eval(hop); return [m(f + ' label[for]'), m(f + ' select, ' + f + ' textarea, ' + f + ' input')]; }",
        [khung, JS_HOP])
    o = {x["id"]: x for x in cac_o}
    assert nhan
    for n in nhan:
        if n["boc"]:
            continue                                  # nhãn bọc ô tích của chính nó (ô tích nằm cạnh chữ, không nằm dưới)
        cua_no = o.get(n["id"])
        assert cua_no is not None, n
        assert cua_no["top"] >= n["bottom"] - 1, ("ô không nằm dưới nhãn của nó", n, cua_no)
        for oid, c in o.items():
            if oid == n["id"]:
                continue
            chong_dong = c["top"] < n["bottom"] - 1 and c["bottom"] > n["top"] + 1
            assert not chong_dong, ("nhãn cùng dòng với ô của trường khác", n["id"], oid, n, c)


@pytest.mark.parametrize("rong", [1280, 1024])
def test_nhan_nam_tren_o_khong_chung_dong_o_khac(mo, rong):
    trang, api, loi = mo
    page = trang(rong)
    _khong_nhan_chung_hang(page, "#gt2TieuChiPanel")
    page.locator("#gt2ThuChay").click()
    page.wait_for_selector("#gt2ThuKetQua table")
    _khong_nhan_chung_hang(page, "#gt2ThuPanel")
    assert not loi, loi


def test_hai_cot_o_1280_mot_cot_o_800(mo):
    trang, api, loi = mo
    page = trang(1280)
    tr = page.locator("#gt2TcDanhSach").bounding_box()
    fo = page.locator("#gt2TcDieuKhien").bounding_box()
    assert fo["x"] > tr["x"] + tr["width"] - 4 and abs(fo["y"] - tr["y"]) < 120        # form ở cột bên phải
    page.set_viewport_size({"width": 800, "height": 900})
    tr = page.locator("#gt2TcDanhSach").bounding_box()
    fo = page.locator("#gt2TcDieuKhien").bounding_box()
    assert fo["y"] > tr["y"] + tr["height"] - 4                                           # một cột: form nằm dưới
    assert not loi, loi


def test_o_tich_va_chu_goi_y_khong_de_nhau_va_nut_luu_nam_ben_phai(mo):
    # UX1A-L2b: ô tích điểm quyết tâm đã bỏ khỏi bảng này (thẻ ở trang Cài đặt giữ cờ); còn lại: nút lưu căn phải.
    trang, api, loi = mo
    page = trang(1280)
    assert page.locator("#gt2TcWharton").count() == 0 and page.locator("#gt2TcWhartonGoiY").count() == 0
    luu = page.locator("#gt2TcLuu").bounding_box()
    form = page.locator("#gt2TcDieuKhien").bounding_box()
    assert luu["x"] + luu["width"] >= form["x"] + form["width"] - 40                      # nút lưu căn phải
    assert page.locator("#gt2TcLuu").evaluate("e => getComputedStyle(e).backgroundColor") != "rgba(0, 0, 0, 0)"
    assert not loi, loi


def test_danh_sach_tieu_chi_la_danh_sach_dep_co_so_thu_tu(mo):
    trang, api, loi = mo
    page = trang(1280)
    kieu = page.locator('#gt2TcDanhSach ol[data-tang="tang_1"] li').first.evaluate(
        "e => ({ls: getComputedStyle(e).listStyleType, fs: parseFloat(getComputedStyle(e).fontSize), "
        "dau: getComputedStyle(e, '::before').content})")
    assert kieu["ls"] == "none" and kieu["fs"] >= 14 and kieu["dau"] not in ("none", "normal", '""')
    assert not loi, loi


def test_the_so_sanh_hai_the_lan_tom_tat_chenh_lech_va_danh_sach_gap(mo):
    trang, api, loi = mo
    page = trang(1280)
    page.select_option("#gt2TcPriority", "tier")
    page.fill("#gt2TcTiers", "")
    page.locator("#gt2ThuChay").click()
    page.wait_for_selector("#gt2ThuKetQua table")
    the = page.locator("#gt2ThuKetQua .gt2-the-lan")
    assert the.count() == 2
    assert "Chính thức số" in the.nth(0).inner_text() or "Chính thức số" in the.nth(1).inner_text()
    assert "Chạy thử số" in the.nth(0).inner_text() + the.nth(1).inner_text()
    for i in (0, 1):
        assert the.nth(i).locator("ol").count() >= 1 and the.nth(i).locator("h5").count() >= 1       # hai tầng tách riêng
    chinh = [the.nth(i) for i in (0, 1) if "Chính thức" in the.nth(i).inner_text()][0]
    assert chinh.locator("ol").count() == 2
    tom_tat = page.locator("#gt2SsKetLuan").inner_text()
    assert "học sinh đổi CLB" in tom_tat and "→" in tom_tat and "%" in tom_tat
    chu = page.locator("#gt2ThuKetQua").inner_text()
    assert "__mac_dinh__" not in chu
    assert page.locator("#gt2ThuKetQua .gt2-delta").count() > 0
    ds = page.locator("#gt2SsDoiBang")
    assert not ds.is_visible()                                                             # gập mặc định
    nut = page.locator("#gt2SsDoiNut")
    assert "Hiện danh sách" in nut.inner_text() and "(" in nut.inner_text()
    nut.click()
    assert ds.is_visible() and "Ẩn danh sách" in nut.inner_text()
    assert page.locator("#gt2ThuKetQua th").first.evaluate("e => getComputedStyle(e).position") == "sticky"
    assert not loi, loi


def test_ban_mot_buoi_an_cot_buoi_va_khong_in_ten_noi_bo(mo):
    trang, api, loi = mo
    page = trang(1280)
    page.select_option("#gt2TcPriority", "tier")
    page.locator("#gt2ThuChay").click()
    page.wait_for_selector("#gt2ThuKetQua table")
    ths = page.locator("#gt2SsDoiBang th").all_inner_texts()
    nhieu = len(api.so_sanh_lan_chay(api.list_lan_chay()["data"]["thu"][0]["run_id"])["data"]["buoi_chung"]) > 1
    assert (("Buổi" in ths) == nhieu), ths
    assert "__mac_dinh__" not in page.locator("#gt2ThuPanel").inner_text()
    assert page.locator("#gt2ThuPanel").evaluate("e => e.innerHTML.includes('__mac_dinh__')") is False
    assert not loi, loi


def test_canh_bao_vang_khi_cau_hinh_vo_nghia(mo):
    trang, api, loi = mo
    page = trang(1280)
    canh = page.locator("#gt2ThuCanhBao")
    assert not canh.is_visible()
    page.select_option("#gt2TcPriority", "tier")
    page.fill("#gt2TcTiers", "")
    assert canh.is_visible() and "bốc thăm" in canh.inner_text()                           # chỉ theo nhóm mà chưa có nhóm
    assert page.locator("#gt2ThuChay").is_enabled()                                        # chỉ nhắc, không chặn
    page.fill("#gt2TcTiers", "Khối 12")
    assert not canh.is_visible()
    page.select_option("#gt2TcPriority", "score+tier")
    page.select_option("#gt2TcTierMode", "strict")
    page.fill("#gt2TcTiers", "")
    assert canh.is_visible() and "danh sách nhóm" in canh.inner_text()                     # "nhóm đứng trước điểm" mà danh sách rỗng
    page.select_option("#gt2TcTierMode", "reserve")
    assert not canh.is_visible()
    assert not loi, loi


def test_giong_cu_ky_thuat_khong_lot_ra_o_hai_khung(mo):
    trang, api, loi = mo
    page = trang(1280)
    chu = page.locator("#gt2TieuChiPanel").inner_text() + page.locator("#gt2ThuPanel").inner_text()
    for xau in ("priority", "tier_mode", "score_scope", "undefined", "null", "GT2"):
        assert xau not in chu, xau
    assert not loi, loi


@pytest.mark.parametrize("rong", [1280, 1024])
def test_cac_khung_gt_chu_14px_o_bam_36px_tuong_phan_45(mo, rong):
    trang, api, loi = mo
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("quantri", MK)["ok"]
    page = trang(rong)
    page.locator("#gt2ThuChay").click()
    page.wait_for_selector("#gt2ThuKetQua table")
    sel = ["#gt2TieuChiPanel label", "#gt2TieuChiPanel .hint-text", "#gt2TieuChiPanel .btn", "#gt2TieuChiPanel select",
           "#gt2TieuChiPanel textarea", "#gt2TieuChiPanel li", "#gt2ThuPanel label", "#gt2ThuPanel .hint-text",
           "#gt2ThuPanel .btn", "#gt2ThuPanel select", "#gt2ThuPanel li", "#gt2ThuKetQua td", "#gt2ThuKetQua th"]
    for x in page.evaluate(JS_TUONG_PHAN, sel):
        assert x["ti"] >= 4.5, ("tương phản", x)
        assert x["co"] >= 14 - 0.01, ("cỡ chữ", x)
        if x["sel"].endswith((".btn", "select", "textarea")):
            assert x["cao"] >= 36 - 0.5, ("ô bấm thấp", x)
    # khung tra cứu (thẻ Kết quả) và hộp tài khoản cùng nhịp
    page.click('button.nav-item[data-tab="results"]')
    for x in page.evaluate(JS_TUONG_PHAN, ["#gtPanel .btn", "#gtPanel input", "#gtPanel .hint-text", "#gtBuocHuongDan li"]):
        assert x["ti"] >= 4.5, ("tương phản", x)
        assert x["co"] >= 14 - 0.01, ("cỡ chữ", x)
        if x["sel"].endswith((".btn", "input")):
            assert x["cao"] >= 36 - 0.5, ("ô bấm thấp", x)
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormDoiMk")
    for x in page.evaluate(JS_TUONG_PHAN, ["#tkOverlay label", "#tkOverlay .btn", "#tkOverlay input", "#tkOverlay .hint-text"]):
        assert x["ti"] >= 4.5, ("tương phản", x)
        assert x["co"] >= 14 - 0.01, ("cỡ chữ", x)
        if x["sel"].endswith((".btn", "input")):
            assert x["cao"] >= 36 - 0.5, ("ô bấm thấp", x)
    assert not loi, loi


def test_hop_tai_khoan_va_khung_tra_cuu_nhan_tren_o_khong_chung_dong(mo):
    trang, api, loi = mo
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("quantri", MK)["ok"]
    page = trang(1024)
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormDoiMk")
    page.wait_for_selector("#tkNutTao")                         # đợi danh sách tài khoản và form "Thêm" dàn xong
    page.wait_for_load_state("networkidle")
    _khong_nhan_chung_hang(page, "#tkKhungTaiKhoan")
    assert not loi, loi


def test_vong_focus_nhin_thay_tren_nut_va_o(mo):
    trang, api, loi = mo
    page = trang(1280)
    for sel in ("#gt2TcLuu", "#gt2TcPriority"):
        page.locator(sel).focus()
        page.keyboard.press("Tab")
        page.keyboard.press("Shift+Tab")
        kieu = page.locator(sel).evaluate(
            "e => { const s = getComputedStyle(e); return [s.outlineStyle, parseFloat(s.outlineWidth), s.boxShadow].join('|'); }")
        outline_style, outline_width, shadow = kieu.split("|")[0], float(kieu.split("|")[1]), kieu.split("|")[2]
        assert (outline_style != "none" and outline_width >= 2) or shadow not in ("none", ""), (sel, kieu)
    assert not loi, loi
