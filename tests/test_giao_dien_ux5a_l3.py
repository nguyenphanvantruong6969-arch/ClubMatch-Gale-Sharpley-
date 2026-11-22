"""UX5A-L3: thẻ Chi tiết và xuất tệp (Chromium thật; dữ liệu MÔ PHỎNG). Hick: ngân sách từng khung khi nếp gập đóng;
Von Restorff: đúng MỘT nút vàng ("Xuất kết quả (Excel)"), đỏ không có; chữ không còn "suất"/"Chọi"; nút theo hàng đã chọn ẩn
tới khi chọn (D4); hai nút FA (Chạy vòng 2, Gửi khiếu nại) không vàng (D2). Quản trị VÀ giáo viên."""

import os
import re

import pytest

from _ux5a_chung import GOC, JS_CHU, JS_DO, JS_VANG, dem, mo_ux5a  # noqa: F401

VAI = ["quan_tri", "giao_vien"]
TU_CAM = re.compile(r"Chọi|cấu hình|[Qq]uỹ|\d{4}-\d\d-\d\d[ T]\d\d:|CLB nguyện vọng 1|\btier\b|reserve")


@pytest.mark.parametrize("vai", VAI)
def test_ngan_sach_hick_nep_dong(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai, "others")
    xuat = dem(page, "#xuatPanel")
    assert len(xuat) <= (4 if vai == "quan_tri" else 3), xuat
    assert "btnXuatTuyChon" in xuat and "btnXuatTheoLop" in xuat
    for pid in ("clbPanel", "duTruPanel", "doPhuPanel", "nvPanel", "chuaCoChoPanel", "thamPanel"):
        if page.locator("#" + pid).is_visible():
            assert len(dem(page, "#" + pid)) <= 2, (pid, dem(page, "#" + pid))
    assert len(dem(page, "#dsXepPanel")) <= 4
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
def test_mot_nut_vang_khong_do_va_nut_fa_khong_vang(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai, "others")
    assert page.evaluate(JS_VANG, "#view-others") == ["btnXuatTuyChon"]
    assert page.evaluate(JS_DO, "#view-others") == []
    html = open(os.path.join(GOC, "index.html"), encoding="utf-8").read()
    for i in ("btnChayVong2", "btnGuiKhieuNai", "btnGuiPhanHoi"):
        m = re.search(r'<button[^>]*id="%s"[^>]*>' % i, html)
        assert m and "btn-primary" not in m.group(0), i
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
def test_chu_moi_va_tieu_de_nhom(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai, "others")
    assert page.locator("#view-others .view-desc").inner_text().startswith("Tải kết quả về máy")
    assert page.locator("#xuatPanel h2").inner_text().strip() == "Tải kết quả về máy"
    assert page.locator("#xuatNangCao > summary").inner_text().strip() == "Chọn thêm tệp để xuất"
    assert page.locator("#chiTietNhomTieuDe").first.inner_text().strip() == "Số liệu chi tiết"
    # tiêu đề nhóm đứng TRƯỚC khung đầu tiên của số liệu chi tiết
    assert page.evaluate("""() => { const h = document.getElementById('chiTietNhomTieuDe'), c = document.getElementById('clbPanel');
      return !!(h.compareDocumentPosition(c) & Node.DOCUMENT_POSITION_FOLLOWING); }""")
    if vai == "quan_tri":
        assert page.locator("#xuatMenu > summary").inner_text().strip() == "Xuất tệp khác ▾"
    assert not loi, loi


def test_goi_y_huy_chuong_nam_trong_menu_va_chi_con_mot_doan_goi_y(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "others")
    assert page.locator("#xuatFaAnGoiY").is_hidden()
    page.click("#xuatMenu > summary")
    assert page.locator("#xuatFaAnGoiY").is_visible()
    assert page.locator("#xuatMenu #xuatFaAnGoiY").count() == 1
    page.keyboard.press("Escape")
    hint = page.evaluate("""() => [...document.querySelectorAll('#xuatPanel > .hint-text, #xuatPanel > .xuat-canh-bao')]
      .filter(e => e.checkVisibility({checkVisibilityCSS: true})).map(e => e.className)""")
    assert len(hint) == 2, hint          # một đoạn "Xuất theo lớp…" + một dòng cảnh báo
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
def test_nut_hang_da_chon_chi_hien_sau_khi_chon(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai, "others")
    page.click("#btnThuGonTatCa")
    page.wait_for_selector("#resultsTableBody .chon-hs", state="visible")
    assert page.locator("#btnXuatHsDaChon").is_hidden() and page.locator("#btnBoChonHs").is_hidden()
    page.click("#xuatNangCao > summary")
    assert page.locator("#xuatHocSinh").is_hidden()
    assert page.locator("#btnXuatHsDaChon").is_disabled()           # vẫn tắt khi chưa chọn (test cũ)
    assert "Chưa chọn" in page.locator("#hsDaChonDem").inner_text()
    page.locator("#resultsTableBody .chon-hs").first.check()
    assert page.locator("#btnXuatHsDaChon").is_visible() and page.locator("#btnXuatHsDaChon").is_enabled()
    assert page.locator("#btnBoChonHs").is_visible()
    assert page.locator("#xuatHocSinh").is_visible()
    page.click("#btnBoChonHs")
    assert page.locator("#btnXuatHsDaChon").is_hidden() and page.locator("#xuatHocSinh").is_hidden()
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
def test_khong_con_chu_kho_khi_mo_het_nep(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai, "others")
    page.evaluate("document.querySelectorAll('#view-others details').forEach(d => d.open = true)")
    page.click("#btnThuGonTatCa")
    page.wait_for_timeout(500)
    chu = page.evaluate(JS_CHU, "#view-others")
    kho = [d for d in chu.split("\n") if TU_CAM.search(d)]
    assert not kho, kho
    assert "chỉ tiêu" in chu.lower()
    assert not loi, loi


def test_en_khop_vi_va_khoa_moi():
    nguon = open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    for khoa in ("ux5a_nhom_chi_tiet", "ux1a_xuat_menu", "xuat_title", "du_tru_title", "du_tru_desc", "legend_reserve",
                 "dem_suat", "du_tru_tieu_diem", "kpi_du_tru_thua", "mt1_kq_nv1", "xuat_fa_an_goi_y", "fill_sap_xep_choi"):
        vi, en = re.findall(r'\b%s: "((?:[^"\\]|\\.)*)"' % khoa, nguon)[:2]
        assert vi and en and vi != en, khoa
        assert set(re.findall(r"\{\w+\}", vi)) == set(re.findall(r"\{\w+\}", en)), khoa
        assert not TU_CAM.search(vi), (khoa, vi)
