# ruff: noqa: F811
"""UX5B-L3: thẻ Nhập nguyện vọng (ba bước là ba mục gập) và Nhập điểm (Chromium thật; dữ liệu MÔ PHỎNG, sổ 120 học sinh).
Hick: ≤ 7 điều khiển (ngoài dữ liệu dạng danh sách). Von Restorff: một nút vàng, là nút Lưu của mục đang mở / "Chấm tiếp"."""

import os
import re

from _ux5b_chung import (GOC, JS_CHU, JS_DO, JS_MUC_MO, JS_VANG, chon_hoc_sinh, dem, dem_nhap,  # noqa: F401
                         mo_ux5b)

ID_PHAI_CON = ("studentSearchInput", "btnStudentSearch", "newStudentId", "newStudentName", "newStudentLop", "btnCreateStudent",
               "fallbackWorkArea", "menuHocSinh", "btnXuatEmNay", "btnResetStudentEntry", "btnDeleteStudent", "kioskLopHang",
               "testSelectionGrid", "btnSubmitTestSelection", "rankingSourceGrid", "rankingList", "btnClearRanking",
               "btnSubmitPreferences", "fbWhartonStep", "fbWhartonBody", "btnSubmitWharton", "fbHuyChuongStep", "btnSubmitHuyChuong",
               "scoringClubPanel", "scoringOverviewBody", "scoringWorkArea", "btnSaveScores", "scoringTableBody",
               "scoringPersonArea", "btnSavePersonScores")
TU_CAM = re.compile(r"Hiện/ẩn|Wharton|\bseed\b|\btier\b|reserve|pipeline")


def test_moi_id_cu_van_con():
    html = open(os.path.join(GOC, "index.html"), encoding="utf-8").read()
    thieu = [i for i in ID_PHAI_CON if 'id="%s"' % i not in html]
    assert not thieu, thieu


# ---------------------------------------------------------------- Nhập nguyện vọng, quản trị

def test_quan_tri_chua_chon_em_dong_trang_thai_tao_moi_gap_va_ngan_sach(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback")
    assert page.inner_text("#ux5bTtNhap") == "Chọn một học sinh ở trên để bắt đầu."
    assert page.locator("#view-fallback .view-desc").count() == 0      # UX6-L1: bỏ câu mô tả thẻ
    assert page.inner_text("#view-fallback .panel-head h2:visible") == "Tìm học sinh"
    assert page.inner_text("#ux5bTaoMoi > summary") == "Tạo học sinh mới"
    for sel in ("#newStudentId", "#newStudentName", "#btnCreateStudent"):
        assert page.locator(sel).is_hidden(), sel
    assert len(dem_nhap(page)) <= 7
    assert page.evaluate(JS_VANG, "#view-fallback") == []
    page.locator("#ux5bTaoMoi > summary").click()
    for sel in ("#newStudentId", "#newStudentName", "#btnCreateStudent"):
        assert page.locator(sel).is_visible(), sel
    assert not loi, loi


def test_chon_mot_em_mot_nut_vang_la_luu_cua_muc_dang_mo(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback", chon_em="HS001")
    assert page.locator("#ux5bTtNhap").is_hidden()
    assert page.evaluate(JS_MUC_MO) == ["fbBuoc2"]          # em đã có dữ liệu: mở Bước 2
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitPreferences"]
    assert page.evaluate(JS_DO, "#view-fallback") == []
    assert len(dem_nhap(page)) <= 7, dem_nhap(page)
    assert page.inner_text("#fbBuoc1 .ux5b-muc-tom-chu") == "Đã lưu: 4 CLB dự thi"
    assert page.locator("#ux5bSuaThi").is_visible() and page.locator("#ux5bSuaNv").is_hidden()
    for sel in ("#btnSubmitTestSelection", "#testSelectionGrid", "#btnSubmitWharton"):
        assert page.locator(sel).is_hidden(), sel
    assert page.locator("#btnClearRanking").is_visible()
    assert not loi, loi


def test_bam_sua_mo_buoc_do_va_gap_buoc_kia_nut_vang_di_theo(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback", chon_em="HS001")
    page.locator("#ux5bSuaThi").click()
    assert page.evaluate(JS_MUC_MO) == ["fbBuoc1"]
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitTestSelection"]
    assert page.locator("#testSelectionGrid .option-row").first.is_visible()
    assert page.inner_text("#fbBuoc2 .ux5b-muc-tom-chu") == "Đã lưu: 7 nguyện vọng"
    assert page.locator("#btnSubmitPreferences").is_hidden()
    assert len(dem_nhap(page)) <= 7, dem_nhap(page)
    page.locator("#ux5bSuaNv").click()
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitPreferences"]
    assert not loi, loi


def test_tick_chua_luu_hien_tren_dong_tom_tat_khi_gap(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback", chon_em="HS001")
    page.locator("#ux5bSuaThi").click()
    page.locator("#testSelectionGrid .option-row").first.click()
    page.locator("#ux5bSuaNv").click()
    assert page.inner_text("#fbBuoc1 .ux5b-muc-tom-chu") == "• Chưa lưu"
    assert not loi, loi


def test_luu_buoc_1_xong_buoc_2_tu_mo_va_du_lieu_van_ghi_dung(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback", chon_em="HS001")
    truoc = api.get_student_entry_state("HS001")["data"]
    page.locator("#ux5bSuaThi").click()
    page.locator("#btnSubmitTestSelection").click()
    page.wait_for_function("document.getElementById('testSelectionFeedback').textContent.trim() !== ''")
    assert page.evaluate(JS_MUC_MO) == ["fbBuoc2"]
    sau = api.get_student_entry_state("HS001")["data"]
    assert sau["tested_clubs"] == truoc["tested_clubs"] and sau["ranked_clubs"] == truoc["ranked_clubs"]
    assert not loi, loi


def test_em_moi_mo_buoc_1_va_chua_co_nguyen_vong_thi_an_xoa_het(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback")
    assert api.create_student_if_missing("MOI01", "Trần Em Mới", "10A1")["ok"]
    page.fill("#studentSearchInput", "MOI01")
    page.locator("#btnStudentSearch").click()
    chon_hoc_sinh(page, "MOI01")
    assert page.evaluate(JS_MUC_MO) == ["fbBuoc1"]
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitTestSelection"]
    assert page.locator("#btnClearRanking").is_hidden()
    assert page.inner_text("#fbBuoc2 .ux5b-muc-tom-chu") == "Đã lưu: 0 nguyện vọng"
    page.locator("#ux5bSuaNv").click()
    page.locator("#rankingSourceGrid .option-row").first.click()
    assert page.locator("#btnClearRanking").is_visible()
    assert not loi, loi


# ---------------------------------------------------------------- Nhập nguyện vọng, giáo viên

def test_giao_vien_khong_thay_tao_moi_va_diem_quyet_tam_nhung_giu_cau_cu(mo_ux5b):
    page, api, loi = mo_ux5b("giao_vien", "fallback")
    assert page.locator("#ux5bTaoMoi").is_hidden()
    assert page.locator("#view-fallback .view-desc").count() == 0      # UX6-L1: bỏ câu mô tả thẻ
    chon_hoc_sinh(page, "HS001")
    assert page.locator("#fbWhartonStep").is_hidden()          # D3: ẩn cả mục, không để ô gõ được mà không lưu được
    assert page.locator("#fbWhartonBody input.wh-diem").count() > 0           # có dựng, nhưng giáo viên không thấy
    assert all(i.is_hidden() for i in page.locator("#fbWhartonBody input.wh-diem").all())
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitPreferences"]
    assert len(dem_nhap(page)) <= 6, dem_nhap(page)
    assert not loi, loi


def test_khong_con_chu_kho_va_chu_i_tran(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback", chon_em="HS001")
    page.evaluate("document.querySelectorAll('#view-fallback details').forEach(d => d.open = true)")
    page.locator("#ux5bSuaW").click()                              # Bước 3 (điểm quyết tâm) mở ra
    kho = [d for d in page.evaluate(JS_CHU, "#view-fallback").split("\n") if TU_CAM.search(d)]
    assert not kho, kho
    chu_i = [x.strip() for x in page.locator("#fbWhartonBody .wh-i").all_inner_texts()]
    assert chu_i and set(chu_i) == {"Giải thích"}, chu_i
    assert not loi, loi


# ---------------------------------------------------------------- Nhập điểm

def _de_lai_chua_cham(api):
    """MÔ PHỎNG: xoá điểm của 5 em ở một CLB để CLB đó còn học sinh chưa chấm."""
    ds = api.get_club_applicants_for_scoring("clb_bcs")["data"]["applicants"][:5]
    assert api.submit_club_scores("clb_bcs", [{"student_id": a["student_id"], "score": None} for a in ds])["ok"]


def test_nhap_diem_danh_sach_dong_trang_thai_va_mot_nut_vang_cham_tiep(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline", nap=True)
    _de_lai_chua_cham(api)
    page.locator('.nav-item[data-tab="scoring"]').click()
    page.wait_for_selector("#scoringOverviewBody button")
    assert page.inner_text("#ux5bTtDiem") == "1 CLB còn học sinh chưa chấm."
    assert len(page.evaluate(JS_VANG, "#view-scoring")) == 1
    nut = page.locator("#scoringOverviewBody button.btn-primary")
    assert nut.count() == 1 and nut.inner_text() == "Chấm tiếp"
    assert page.locator("#scoringOverviewBody button.btn-secondary").first.inner_text() == "Chấm"
    assert len(dem(page, "#view-scoring")) <= 7
    assert not loi, loi


def test_nhap_diem_cham_xong_het_khong_con_nut_vang(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "scoring")
    page.wait_for_selector("#scoringOverviewBody button")
    assert page.inner_text("#ux5bTtDiem") == "Đã chấm xong hết."
    assert page.evaluate(JS_VANG, "#view-scoring") == []
    assert not loi, loi


def test_nhap_diem_dang_cham_mot_clb_co_nut_quay_lai_va_mot_vang(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "scoring")
    page.wait_for_selector("#scoringOverviewBody button")
    page.locator("#scoringOverviewBody button").first.click()
    page.wait_for_selector("#scoringTableBody .score-input")
    assert page.evaluate(JS_VANG, "#view-scoring") == ["btnSaveScores"]
    assert page.locator("#scoringClubPanel").is_hidden()
    assert page.inner_text("#btnScoringQuayLai") == "‹ Danh sách CLB"
    assert len(dem(page, "#view-scoring")) <= 2, dem(page, "#view-scoring")
    page.locator("#btnScoringQuayLai").click()
    page.wait_for_selector("#scoringClubPanel:not([hidden])")
    assert page.locator("#scoringWorkArea").is_hidden()
    assert page.locator("#btnSaveScores").is_hidden()
    assert not loi, loi


def test_giao_vien_nhap_diem_cung_mot_nut_vang_va_co_lai_danh_sach(mo_ux5b):
    page, api, loi = mo_ux5b("giao_vien", "scoring")
    page.wait_for_selector("#scoringOverviewBody button")
    page.locator("#scoringOverviewBody button").first.click()
    page.wait_for_selector("#scoringTableBody .score-input")
    assert page.evaluate(JS_VANG, "#view-scoring") == ["btnSaveScores"]
    assert page.locator("#btnScoringQuayLai").is_visible()
    assert len(dem(page, "#view-scoring")) <= 2
    assert not loi, loi


def test_quay_lai_khi_con_diem_chua_luu_phai_hoi_roi_moi_bo(mo_ux5b):
    """UX5B-FIX1 (checker): điểm đã gõ mà chưa Lưu không được mất im lặng khi bấm "‹ Danh sách"."""
    page, api, loi = mo_ux5b("quan_tri", "scoring")
    page.wait_for_selector("#scoringOverviewBody button")
    page.locator("#scoringOverviewBody button").first.click()
    page.wait_for_selector("#scoringTableBody .score-input")
    o = page.locator("#scoringTableBody .score-input").first
    cu = o.input_value()
    assert page.locator("#chuaLuuDiem").is_hidden()
    o.fill("7" if cu != "7" else "6")
    assert page.locator("#chuaLuuDiem").is_visible()
    page.locator("#btnScoringQuayLai").click()                     # lần 1: chỉ cảnh báo, vẫn ở màn chấm
    assert page.locator("#scoringWorkArea").is_visible()
    assert page.locator("#scoringTableBody .score-input").first.input_value() != cu
    page.locator("#btnScoringQuayLai").click()                     # lần 2 (trong 4 giây): bỏ thay đổi, về danh sách
    page.wait_for_selector("#scoringClubPanel:not([hidden])")
    assert page.locator("#scoringWorkArea").is_hidden()
    page.locator("#scoringOverviewBody button").first.click()      # mở lại: điểm về giá trị đã lưu
    page.wait_for_selector("#scoringTableBody .score-input")
    assert page.locator("#scoringTableBody .score-input").first.input_value() == cu
    assert not loi, loi


def test_luu_diem_xong_thi_het_chua_luu_va_quay_lai_khong_hoi(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "scoring")
    page.wait_for_selector("#scoringOverviewBody button")
    page.locator("#scoringOverviewBody button").first.click()
    page.wait_for_selector("#scoringTableBody .score-input")
    page.locator("#scoringTableBody .score-input").first.fill("7")
    assert page.locator("#chuaLuuDiem").is_visible()
    page.locator("#btnSaveScores").click()
    page.wait_for_function("document.getElementById('scoringFeedback').textContent.trim() !== ''")
    assert page.locator("#chuaLuuDiem").is_hidden()
    page.locator("#btnScoringQuayLai").click()                     # một lần là đi ngay
    page.wait_for_selector("#scoringClubPanel:not([hidden])")
    assert not loi, loi
