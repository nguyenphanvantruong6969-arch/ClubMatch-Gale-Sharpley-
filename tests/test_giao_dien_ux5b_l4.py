# ruff: noqa: F811
"""UX5B-L4: ngân sách Hick + Von Restorff của ba thẻ Xếp CLB, Nhập nguyện vọng, Nhập điểm, đếm RIÊNG cho quản trị và giáo viên
(Chromium thật; dữ liệu MÔ PHỎNG, sổ 120 học sinh); test từ cấm; test "cùng payload": ba lần Lưu vẫn gọi đúng ba API với đúng tham số.
Cách đếm: ô nhìn thấy và bật, ngoài hàng bảng, ngoài dữ liệu dạng danh sách và nút "Sửa" của mục gập (xem `_ux5b_chung.JS_DEM_NHAP`).
Trạng thái đo thẻ Nhập nguyện vọng: "đã chọn một em"."""

import re

import pytest

from _ux5b_chung import GOC, JS_CHU, JS_DO, JS_VANG, SO_120, chon_hoc_sinh, dem, dem_nhap, mo_ux5b  # noqa: F401

TU_CAM = re.compile(r"Nâng cao|Hiện/ẩn|Wharton|\bseed\b|\btier\b|reserve|pipeline|backup|\bSTB\b|payload")
NGAN_SACH = {"quan_tri": 7, "giao_vien": 6}          # Nhập nguyện vọng, đã chọn một em


def _gioi_han_the(page, view, toi_da_o, toi_da_vang=1):
    o = dem_nhap(page, view) if view == "#view-fallback" else dem(page, view)
    assert len(o) <= toi_da_o, (view, len(o), o)
    assert len(page.evaluate(JS_VANG, view)) <= toi_da_vang, page.evaluate(JS_VANG, view)
    assert page.evaluate(JS_DO, view) == []            # đỏ chỉ ở "Làm lại từ đầu" (thẻ Quản lý), không ở ba thẻ này


# ---------------------------------------------------------------- Hick + Von Restorff mỗi thẻ

def test_xep_clb_quan_tri_chua_nap_va_da_nap(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline", nap=False)
    _gioi_han_the(page, "#view-pipeline", 7)
    page.set_input_files("#fileAny", SO_120)
    page.wait_for_selector("#btnImportAll", state="visible")
    _gioi_han_the(page, "#view-pipeline", 7)
    assert page.evaluate(JS_VANG, "#view-pipeline") == ["btnImportAll"]
    assert not loi, loi


def test_xep_clb_giao_vien_khong_thay_the(mo_ux5b):
    page, api, loi = mo_ux5b("giao_vien", "scoring")
    assert page.locator('.nav-item[data-tab="pipeline"]').is_hidden()
    assert page.locator("#view-pipeline").is_hidden()
    assert not loi, loi


@pytest.mark.parametrize("vai", ["quan_tri", "giao_vien"])
def test_nhap_nguyen_vong_chua_chon_va_da_chon_mot_em(mo_ux5b, vai):
    page, api, loi = mo_ux5b(vai, "fallback")
    _gioi_han_the(page, "#view-fallback", 7, 0)
    assert page.evaluate(JS_VANG, "#view-fallback") == []
    chon_hoc_sinh(page, "HS001")
    _gioi_han_the(page, "#view-fallback", NGAN_SACH[vai])
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitPreferences"]
    # nút "Sửa" là điều hướng giữa các bước: tối đa hai (Bước 1 và Bước 3) với quản trị, một với giáo viên
    sua = page.evaluate("Array.from(document.querySelectorAll('#fallbackWorkArea .ux5b-muc-sua')).filter(e => e.checkVisibility({checkVisibilityCSS: true})).length")
    assert sua <= (2 if vai == "quan_tri" else 1), sua
    # giáo viên không thấy "Tạo mới" và mục điểm quyết tâm; không nút nào bị làm mờ thay vì ẩn
    if vai == "giao_vien":
        assert page.locator("#ux5bTaoMoi").is_hidden() and page.locator("#fbWhartonStep").is_hidden()
    # (nút "‹ Trước" của phân trang danh sách ở trang 1 là điều hướng danh sách, không tính)
    mo_thu = page.evaluate("Array.from(document.querySelectorAll('#view-fallback button:disabled')).filter(e => e.checkVisibility({checkVisibilityCSS: true}) && !e.closest('#fallbackStudentPagination')).map(e => e.id)")
    assert mo_thu == [], mo_thu
    assert not loi, loi


@pytest.mark.parametrize("vai", ["quan_tri", "giao_vien"])
def test_nhap_diem_danh_sach_va_dang_cham(mo_ux5b, vai):
    page, api, loi = mo_ux5b(vai, "scoring")
    page.wait_for_selector("#scoringOverviewBody button")
    _gioi_han_the(page, "#view-scoring", 7)
    page.locator("#scoringOverviewBody button").first.click()
    page.wait_for_selector("#scoringTableBody .score-input")
    _gioi_han_the(page, "#view-scoring", 2)
    assert page.evaluate(JS_VANG, "#view-scoring") == ["btnSaveScores"]
    assert not loi, loi


# ---------------------------------------------------------------- từ cấm và chữ trần "i"

@pytest.mark.parametrize("vai", ["quan_tri", "giao_vien"])
def test_khong_chu_kho_o_ba_the(mo_ux5b, vai):
    page, api, loi = mo_ux5b(vai, "fallback", chon_em="HS001")
    page.evaluate("document.querySelectorAll('#view-fallback details').forEach(d => d.open = true)")
    page.evaluate("document.querySelectorAll('#fallbackWorkArea .fallback-step').forEach(d => d.classList.remove('ux5b-dong'))")
    kho = [d for d in page.evaluate(JS_CHU, "#view-fallback").split("\n") if TU_CAM.search(d)]
    assert not kho, kho
    chu_nut = [x.strip() for x in page.locator("#view-fallback button:visible, #view-fallback summary:visible").all_inner_texts()]
    assert all(len(x) >= 2 or x == "" for x in chu_nut), chu_nut        # không còn nút chữ trần "i"
    page.locator('.nav-item[data-tab="scoring"]').click()
    page.wait_for_selector("#scoringOverviewBody button")
    kho = [d for d in page.evaluate(JS_CHU, "#view-scoring").split("\n") if TU_CAM.search(d)]
    assert not kho, kho
    assert not loi, loi


def test_the_xep_clb_khong_con_chu_kho(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "pipeline", chay=True)
    page.evaluate("document.querySelectorAll('#view-pipeline details').forEach(d => d.open = true)")
    kho = [d for d in page.evaluate(JS_CHU, "#view-pipeline").split("\n") if TU_CAM.search(d)]
    assert not kho, kho
    assert not loi, loi


# ---------------------------------------------------------------- cùng payload

def _ghi_api(api, ten, nhat_ky):
    goc = getattr(api, ten)

    def boc(*a, **k):
        nhat_ky.append((ten, a, k))
        return goc(*a, **k)
    setattr(api, ten, boc)


def test_ba_lan_luu_goi_dung_ba_api_dung_tham_so_nhu_truoc_quan_tri(mo_ux5b):
    page, api, loi = mo_ux5b("quan_tri", "fallback", chon_em="HS001")
    nk = []
    for ten in ("submit_test_selection", "submit_preferences", "submit_wharton"):
        _ghi_api(api, ten, nk)
    truoc = api.get_student_entry_state("HS001")["data"]
    thi0, nv0 = list(truoc["tested_clubs"]), list(truoc["ranked_clubs"])

    # Bước 1: bỏ một CLB dự thi chưa chấm điểm của em này rồi Lưu
    page.locator("#ux5bSuaThi").click()
    bo = thi0[0]
    page.locator('#testSelectionGrid .option-row[data-club-id="%s"]' % bo).click()
    page.locator("#btnSubmitTestSelection").click()
    page.wait_for_function("document.getElementById('testSelectionFeedback').textContent.trim() !== ''")
    assert [n[0] for n in nk] == ["submit_test_selection"]            # lưu Bước 1 không kéo theo lưu Bước 2
    ten, a, k = nk[0]
    assert a[0] == "HS001" and set(a[1]) == set(thi0) - {bo} and not k and len(a) == 3
    # Bước 2 tự mở; bỏ nguyện vọng đầu rồi Lưu
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitPreferences"]
    page.locator("#rankingList li").first.locator("button").click()
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function("document.getElementById('preferencesFeedback').textContent.trim() !== ''")
    assert [n[0] for n in nk] == ["submit_test_selection", "submit_preferences"]
    ten, a, k = nk[1]
    assert a[0] == "HS001" and list(a[1]) == nv0[1:] and not k and len(a) == 3
    # Bước 3 tự mở; Lưu điểm quyết tâm gọi submit_wharton(sid, w1, w2) với đúng hai bảng đang hiện
    assert page.evaluate(JS_VANG, "#view-fallback") == ["btnSubmitWharton"]
    w = page.evaluate("whartonThuThap()")
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function("document.getElementById('whartonFeedback').textContent.trim() !== ''")
    assert [n[0] for n in nk] == ["submit_test_selection", "submit_preferences", "submit_wharton"]
    ten, a, k = nk[2]
    assert a[0] == "HS001" and a[1] == w["w1"] and a[2] == w["w2"] and not k
    assert not loi, loi


def test_hai_lan_luu_goi_dung_hai_api_dung_tham_so_nhu_truoc_giao_vien(mo_ux5b):
    page, api, loi = mo_ux5b("giao_vien", "fallback", chon_em="HS001")
    nk = []
    for ten in ("submit_test_selection", "submit_preferences", "submit_wharton"):
        _ghi_api(api, ten, nk)
    nv0 = list(api.get_student_entry_state("HS001")["data"]["ranked_clubs"])
    page.locator("#ux5bSuaThi").click()
    page.locator("#btnSubmitTestSelection").click()
    page.wait_for_function("document.getElementById('testSelectionFeedback').textContent.trim() !== ''")
    page.locator("#rankingList li").first.locator("button").click()
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function("document.getElementById('preferencesFeedback').textContent.trim() !== ''")
    assert [n[0] for n in nk] == ["submit_test_selection", "submit_preferences"]    # giáo viên không bao giờ gọi submit_wharton
    assert list(nk[1][1][1]) == nv0[1:] and nk[1][1][0] == "HS001"
    assert not loi, loi
