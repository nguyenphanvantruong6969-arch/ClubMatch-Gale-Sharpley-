"""UX5B-L2: thẻ Xếp CLB (Chromium thật; dữ liệu MÔ PHỎNG, sổ 120 học sinh, 3 buổi). Chỉ quản trị (thẻ ẩn với giáo viên).
Hick: ≤ 7 điều khiển nhìn thấy trước khi mở mục gập. Von Restorff: nút vàng đi theo bước kế tiếp. Dòng trạng thái nói việc tiếp theo."""

import os
import re

from _ux5b_chung import GOC, JS_CHU, JS_DO, JS_VANG, dem, mo_ux5b  # noqa: F401

TU_CAM = re.compile(r"Nâng cao|Hiện/ẩn|Wharton|\bseed\b|\btier\b|reserve|pipeline|backup")
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
ID_PHAI_CON = ("btnTaiSoMau", "dropZone", "fileAny", "btnImportAll", "btnClearQueue", "btnValidate", "healthSummary", "healthList",
               "btnRun", "stbLockLine", "nangCao", "seedInput", "chonBuoiBox", "chonBuoiChip", "btnChonTatCaBuoi", "chonBuoiNhac",
               "runXong", "btnMoThuMucKq", "btnChiTietBuoc", "ux2Pha", "stepper", "btnToggleHistory", "historyPanel")


def test_moi_id_cu_van_con():
    html = open(os.path.join(GOC, "index.html"), encoding="utf-8").read()
    thieu = [i for i in ID_PHAI_CON if 'id="%s"' % i not in html]
    assert not thieu, thieu


def test_chua_nap_so_dong_trang_thai_va_ngan_sach(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline", nap=False)
    assert page.inner_text("#ux5bTtPipeline") == "Việc tiếp theo: nhập sổ."
    assert len(dem(page, "#view-pipeline")) <= 7
    assert len(page.evaluate(JS_VANG, "#view-pipeline")) <= 1
    assert page.evaluate(JS_DO, "#view-pipeline") == []
    assert not loi, loi


def test_da_nap_chi_mot_nut_vang_la_chay_va_mo_tuy_chon_moi_thay_ma_boc_tham(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline")
    assert page.evaluate(JS_VANG, "#view-pipeline") == ["btnRun"]
    assert len(dem(page, "#view-pipeline")) <= 7, dem(page, "#view-pipeline")
    assert re.match(r"Đã nạp 120 học sinh\. Xem cảnh báo rồi bấm \"Chạy sắp xếp\"\.", page.inner_text("#ux5bTtPipeline"))
    assert page.inner_text("#nangCao > summary") == "Tuỳ chọn khi chạy"
    for sel in ("#seedInput", "#chonBuoiChip .buoi-chip", "#btnChonTatCaBuoi", "#stbLockLine"):
        assert page.locator(sel).first.is_hidden(), sel
    page.locator("#nangCao > summary").click()
    for sel in ("#seedInput", "#chonBuoiChip .buoi-chip", "#btnChonTatCaBuoi"):
        assert page.locator(sel).first.is_visible(), sel
    assert not loi, loi


def test_chon_mot_phan_buoi_dong_nhac_hien_ngoai_muc_gap(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline")
    assert page.locator("#ux5bBuoiTom").is_hidden()
    page.locator("#nangCao > summary").click()
    page.locator("#chonBuoiChip .buoi-chip").first.click()
    page.locator("#nangCao > summary").click()   # đóng mục gập
    assert page.locator("#nangCao").evaluate("e => e.open") is False
    assert page.locator("#ux5bBuoiTom").is_visible()
    assert "Giữ nguyên kết quả" in page.inner_text("#ux5bBuoiTom")


def test_co_tep_cho_nhap_nut_vang_di_theo_buoc_ke_tiep(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline")
    page.set_input_files("#fileAny", SO_120)
    page.wait_for_selector("#btnImportAll", state="visible")
    assert page.evaluate(JS_VANG, "#view-pipeline") == ["btnImportAll"]
    assert page.inner_text("#ux5bTtPipeline") == "Có tệp đang chờ. Bấm \"Nhập sổ\"."
    assert len(dem(page, "#view-pipeline")) <= 7, dem(page, "#view-pipeline")
    assert not loi, loi


def test_danh_sach_canh_bao_nam_trong_muc_gap(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline")
    page.wait_for_function("document.getElementById('healthSummary').textContent.trim() !== ''")
    if page.locator("#healthChiTiet").is_visible():
        mo = page.locator("#healthChiTiet").evaluate("e => e.open")
        assert page.locator("#healthList").is_visible() == mo
        assert page.inner_text("#healthChiTiet > summary") == "Xem chi tiết"
        page.locator("#healthChiTiet > summary").click()
        assert page.locator("#healthList").is_visible() != mo


def test_chay_van_chay_dung_va_dong_trang_thai_bao_da_xep_xong(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline")
    page.locator("#btnRun").click()
    page.wait_for_function("document.getElementById('statMatched').textContent !== '—' && Number(document.getElementById('statMatched').textContent) > 0")
    page.wait_for_function("document.getElementById('ux5bTtPipeline').textContent.startsWith('Đã xếp xong')")
    assert page.inner_text("#ux5bTtPipeline") == "Đã xếp xong. Xem kết quả ở thẻ \"Kết quả\"."
    assert len(page.evaluate(JS_VANG, "#view-pipeline")) <= 1
    assert api.get_dashboard_status()["data"]["n_matched"] > 0
    assert not loi, loi


def test_khong_con_chu_kho(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline", chay=True)
    page.evaluate("document.querySelectorAll('#view-pipeline details').forEach(d => d.open = true)")
    kho = [d for d in page.evaluate(JS_CHU, "#view-pipeline").split("\n") if TU_CAM.search(d)]
    assert not kho, kho
    assert not loi, loi
