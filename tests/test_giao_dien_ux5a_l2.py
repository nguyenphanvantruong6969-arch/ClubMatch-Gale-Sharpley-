"""UX5A-L2: thẻ Kết quả (Chromium thật; dữ liệu MÔ PHỎNG). Luật Hick (ngân sách mỗi khung) và Von Restorff
(đúng MỘT nút vàng mỗi thẻ = "Tải bảng này (Excel)"; "Mã tra cứu…" không có nút vàng) — quản trị VÀ giáo viên."""

import os
import re

import pytest

from _ux5a_chung import GOC, JS_CHU, JS_DO, JS_VANG, dem, mo_ux5a  # noqa: F401

VAI = ["quan_tri", "giao_vien"]


@pytest.mark.parametrize("vai", VAI)
def test_ngan_sach_hick_tung_khung(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai)
    gt = dem(page, "#gtPanel")
    assert len(gt) <= (2 if vai == "quan_tri" else 1), gt
    ux = dem(page, "#ux1bPanel")
    assert ux == ["kqChonLop", "btnUx1bXuatLop", "ux1bThemTom"], ux        # Chọn lớp, Xuất theo lớp, nếp "Báo cáo và phiếu in ▾"
    tong = dem(page, "#view-results")
    assert len(tong) <= (10 if vai == "quan_tri" else 9), tong
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
def test_mot_nut_vang_va_khong_do(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai)
    assert page.evaluate(JS_VANG, "#view-results") == ["btnKqTaiBang"]
    assert page.evaluate(JS_DO, "#view-results") == []
    if vai == "quan_tri":
        page.click("#gtMaFold > summary")
        assert page.evaluate(JS_VANG, "#view-results") == ["btnKqTaiBang"]
        for i in ("btnGtTaoMa", "btnGtXuatMa", "btnGtCheDoHs"):
            assert page.locator("#" + i).is_visible()
            assert "btn-primary" not in page.get_attribute("#" + i, "class")
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
def test_nep_bao_cao_va_phieu_in_con_du_ba_nut_trong_hai_lan_bam(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai)
    for i in ("btnUx1bBaoCao", "btnUx1bPhieuLop", "btnUx1bBaoCaoPdf"):
        assert page.locator("#" + i).count() == 1 and page.locator("#" + i).is_hidden()
    assert page.locator("#ux1bThemTom").inner_text().strip() == "Báo cáo và phiếu in ▾"
    page.click("#ux1bThemTom")
    assert [page.locator("#" + i).inner_text().strip() for i in
            ("btnUx1bBaoCao", "btnUx1bPhieuLop", "btnUx1bBaoCaoPdf")] == [
        "Báo cáo tổng hợp", "In phiếu cả lớp", "Báo cáo tổng hợp (PDF)"]
    assert "Không có tên, mã hay điểm" in page.locator("#ux1bThemMenu").inner_text()
    page.locator("#btnUx1bBaoCao").click()                          # bấm một mục: menu đóng, báo cáo chạy
    page.wait_for_function("document.getElementById('ux1bPhanHoi').textContent.includes('.html')")
    assert page.locator("#ux1bThemMenu").evaluate("e => !e.open")
    assert not loi, loi


@pytest.mark.parametrize("vai", VAI)
def test_chu_moi_dong_muc_dich(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai)
    mo_ta = page.locator("#view-results .view-desc").inner_text()
    assert mo_ta.startswith("Xem học sinh học CLB nào, tra cứu vì sao")
    assert "Bảng này không có điểm hay số bốc thăm" in mo_ta
    assert "Gõ tên hoặc mã" in page.locator("#gtPanel").inner_text()
    assert page.get_attribute("#gtTim", "placeholder") == "Tên hoặc mã học sinh"
    assert "mỗi học sinh học CLB nào" in page.evaluate(JS_CHU, "#view-results")
    if vai == "quan_tri":
        assert page.locator("#gtMaFold > summary").inner_text().strip() == "Mã tra cứu cho học sinh tự xem…"
        page.click("#gtMaFold > summary")
        assert page.locator("#btnGtCheDoHs").inner_text().strip() == "Khoá máy cho học sinh tự tra cứu"
    assert not loi, loi


def test_en_khop_vi():
    nguon = open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    for khoa in ("ux5a_gt_mo_ta", "ux5a_ux1b_them", "ux5a_kq_mo_bang", "kq_desc", "gt_che_do_hs", "ux1b_ma_tra_cuu"):
        vi, en = re.findall(r'\b%s: "((?:[^"\\]|\\.)*)"' % khoa, nguon)[:2]
        assert vi and en and vi != en, khoa
        assert set(re.findall(r"\{\w+\}", vi)) == set(re.findall(r"\{\w+\}", en)), khoa
