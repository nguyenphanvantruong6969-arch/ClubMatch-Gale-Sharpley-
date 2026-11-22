"""UX5A-L4: nhìn tổng thể hai thẻ (Chromium thật; dữ liệu MÔ PHỎNG), quản trị VÀ giáo viên:
Hick (ngân sách) + Von Restorff (đúng một nút vàng mỗi thẻ, không đỏ) + từ cấm + giáo viên vẫn tới được mọi việc của mình
(tra cứu, theo lớp, xuất theo lớp, báo cáo) và không thấy nút chết của quản trị; id giữ nguyên."""

import os
import re

import pytest

from _ux5a_chung import GOC, JS_CHU, JS_DO, JS_VANG, dem, mo_ux5a  # noqa: F401

VAI = ["quan_tri", "giao_vien"]
TAB = {"results": "btnKqTaiBang", "others": "btnXuatTuyChon"}
TU_CAM = re.compile(r"[Ss]uất|Chọi|cấu hình|[Qq]uỹ|\d{4}-\d\d-\d\d[ T]\d\d:|CLB nguyện vọng 1|\btier\b|reserve")
# Tổng điều khiển thấy được khi nếp gập đóng (không tính thead/tbody): tối đa theo số đo UX5A-L1 sau thiết kế.
NGAN_SACH_THE = {("results", "quan_tri"): 10, ("results", "giao_vien"): 9,
                 ("others", "quan_tri"): 21, ("others", "giao_vien"): 19}
ID_PHAI_CON = (
    "gtTim", "gtMaFold", "btnGtTaoMa", "btnGtXuatMa", "btnGtCheDoHs", "btnGtInMot", "btnGtInLop", "btnGtPdfMot", "ux1bLop",
    "btnUx1bXuatLop", "btnUx1bBaoCao", "btnUx1bPhieuLop", "btnUx1bBaoCaoPdf", "btnKqTaiBang", "kqChonLop", "kqChonClb", "kqTimKiem",
    "btnXuatTuyChon", "btnXuatTheoLop", "xuatMenu", "btnXuatLyDo", "btnXuatNhuCau", "btnXuatGoiY", "btnXuatBienBan", "btnPdfDsClb",
    "btnPdfDsLop", "btnPdfPhieuLop", "pdfLop", "xuatKetQua", "xuatKemCsv", "xuatDauVao", "xuatThayDoi", "xuatHocSinh",
    "btnChonHocSinh", "btnXuatHsDaChon", "btnBoChonHs", "btnThuGonTatCa", "btnChayVong2", "btnGuiKhieuNai", "btnGuiPhanHoi",
    "resultsSearch", "resultsLopLoc", "resultsSapXep", "fillSapXep", "thamSearch", "xuatFaAnGoiY",
)


def test_moi_id_cu_van_con_trong_index_html():
    html = open(os.path.join(GOC, "index.html"), encoding="utf-8").read()
    thieu = [i for i in ID_PHAI_CON if 'id="%s"' % i not in html]
    assert not thieu, thieu


@pytest.mark.parametrize("vai", VAI)
@pytest.mark.parametrize("tab", ["results", "others"])
def test_mot_vang_khong_do_trong_ngan_sach(mo_ux5a, vai, tab):  # noqa: F811
    page, api, loi = mo_ux5a(vai, tab)
    assert page.evaluate(JS_VANG, "#view-" + tab) == [TAB[tab]]
    assert page.evaluate(JS_DO, "#view-" + tab) == []
    tong = dem(page, "#view-" + tab)
    assert len(tong) <= NGAN_SACH_THE[(tab, vai)], (len(tong), tong)
    # nút cảnh báo đầu trang (banner) không vàng
    assert page.evaluate("""() => Array.from(document.querySelectorAll('.canh-bao-vang .btn-primary, .canh-bao-hang .btn-primary'))
      .filter(e => e.checkVisibility({checkVisibilityCSS: true})).length""") == 0
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
@pytest.mark.parametrize("tab", ["results", "others"])
def test_khong_con_chu_kho_ca_hai_vai(mo_ux5a, vai, tab):  # noqa: F811
    page, api, loi = mo_ux5a(vai, tab)
    page.evaluate("document.querySelectorAll('#view-%s details').forEach(d => d.open = true)" % tab)
    page.wait_for_timeout(300)
    kho = [d for d in page.evaluate(JS_CHU, "#view-" + tab).split("\n") if TU_CAM.search(d)]
    assert not kho, kho
    assert not loi, loi


@pytest.mark.parametrize("tab", ["results", "others"])
def test_giao_vien_khong_thay_phan_cua_quan_tri_va_khong_co_nut_chet(mo_ux5a, tab):  # noqa: F811
    page, api, loi = mo_ux5a("giao_vien", tab)
    page.evaluate("document.querySelectorAll('#view-%s details').forEach(d => d.open = true)" % tab)
    quan_tri_thay = page.evaluate("""(tab) => Array.from(document.querySelectorAll('#view-' + tab + ' [data-quyen=quan_tri]'))
      .filter(e => e.checkVisibility({checkVisibilityCSS: true})).map(e => e.id)""", tab)
    assert quan_tri_thay == [], quan_tri_thay
    chet = page.evaluate("""(tab) => Array.from(document.querySelectorAll('#view-' + tab + ' button, #view-' + tab + ' select'))
      .filter(e => e.disabled && e.checkVisibility({checkVisibilityCSS: true}) && !e.closest('tbody')).map(e => e.id)""", tab)
    assert chet == [], chet
    assert not loi, loi


def test_giao_vien_van_toi_duoc_tra_cuu_theo_lop_va_xuat_theo_lop(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("giao_vien", "results")
    page.fill("#gtTim", "HS001")
    page.wait_for_selector("#gtDs li", state="visible")
    assert page.locator("#gtDs li").count() >= 1
    assert page.locator("#btnKqTaiBang").is_visible()
    for k in ("lop", "clb", "ma"):
        assert page.locator('#kqTang1 [data-kq="%s"]' % k).is_visible()
    page.locator("#ux1bLop").select_option("10A1")
    page.click("#btnUx1bXuatLop")
    page.wait_for_function("document.getElementById('ux1bPhanHoi').textContent.trim().length > 0")
    page.click("#ux1bThemTom")
    assert page.locator("#btnUx1bPhieuLop").is_visible() and page.locator("#btnUx1bBaoCaoPdf").is_visible()
    page.keyboard.press("Escape")
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#btnXuatTheoLop", state="visible")
    assert page.locator("#btnXuatTheoLop").is_enabled()
    assert page.locator("#xuatMenu").is_hidden()            # menu "Xuất tệp khác" chỉ của quản trị
    assert not loi, loi


def test_quan_tri_toi_duoc_moi_viec_cua_nep_gap_trong_hai_lan_bam(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "results")
    page.click("#gtMaFold > summary")                       # lần 1
    assert all(page.locator("#" + i).is_visible() for i in ("btnGtTaoMa", "btnGtXuatMa", "btnGtCheDoHs"))
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#xuatMenu", state="visible")
    page.click("#xuatMenu > summary")                       # lần 1
    assert all(page.locator("#" + i).is_visible() for i in ("btnPdfDsClb", "btnPdfDsLop", "btnPdfPhieuLop"))
    page.keyboard.press("Escape")
    page.click("#xuatNangCao > summary")                    # lần 1
    assert all(page.locator("#" + i).is_visible() for i in ("xuatKetQua", "xuatKemCsv", "xuatDauVao", "btnChonHocSinh"))
    assert not loi, loi
