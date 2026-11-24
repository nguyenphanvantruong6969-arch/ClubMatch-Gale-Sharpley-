"""UX4-L3: tab Danh sách CLB (form 3 ô + Thêm tuỳ chọn, ô Buổi thả xuống, Mã tự điền) và tab Học sinh
(nút gán/xuất chỉ hiện khi đã chọn ≥ 1 em). Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG."""

import base64
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")

JS_DEM = """(goc) => {
  const vis = e => e.checkVisibility({checkVisibilityCSS: true, contentVisibilityAuto: true});
  const root = document.querySelector(goc);
  const q = 'button, select, input:not([type=hidden]), textarea, summary, a[href]';
  return Array.from(root.querySelectorAll(q)).filter(e => vis(e) && !e.disabled && !e.closest('tbody')).map(e => e.id || e.tagName);
}"""


@pytest.fixture
def trang(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#qlTabClb", state="visible")
    page.wait_for_function("document.querySelectorAll('#adminClubTableBody tr').length > 0")
    yield page, api, loi
    assert not loi, loi


def _clb(api, ma):
    return next((c for c in api.list_clubs_admin()["data"] if c["club_id"] == ma), None)


def test_form_clb_chi_hien_ba_o_cong_nut_luu_va_them_tuy_chon(trang):
    page, api, loi = trang
    assert page.evaluate(JS_DEM, "#clubForm") == [
        "clubFormName", "clubFormCapacity", "clubFormBuoi", "clubFormThemTuyChon", "btnSaveClub"]
    assert page.locator("label:has(#clubFormCapacity) .club-field-label").inner_text().strip() == "Chỉ tiêu"
    assert page.locator("#clubFormThemTuyChon").inner_text().strip() == "Thêm tuỳ chọn"
    page.click("#clubFormThemTuyChon")
    assert page.evaluate(JS_DEM, "#clubForm") == [
        "clubFormName", "clubFormCapacity", "clubFormBuoi", "clubFormThemTuyChon", "clubFormId",
        "clubFormReserveCapacity", "clubFormReserveGroup", "btnSaveClub"]
    nhan = page.locator("#clubFormThem .club-field-label").all_inner_texts()
    assert [x.strip() for x in nhan] == ["Mã CLB (tự điền theo tên, có thể sửa)",
                                         "Suất ưu tiên",
                                         "Nhóm được dành chỗ (để trống nếu không có)"]


def test_o_buoi_tha_xuong_co_mot_buoi_chung_va_them_buoi_moi(trang):
    page, api, loi = trang
    assert api.create_or_update_club("t2", "Cờ vua", 10, None, None, "thu_2")["ok"]
    page.click("#qlTabHs")
    page.click("#qlTabClb")
    page.reload()
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_function("document.querySelectorAll('#clubFormBuoi option').length >= 3")
    tx = page.locator("#clubFormBuoi option").all_inner_texts()
    assert tx[0] == "Một buổi chung" and tx[-1] == "Thêm buổi mới…" and any("Thứ 2" in x for x in tx), tx
    assert page.locator("#clubFormBuoiMoi").is_hidden()
    page.select_option("#clubFormBuoi", "__moi__")
    assert page.locator("#clubFormBuoiMoi").is_visible()
    page.fill("#clubFormName", "Bóng rổ")
    page.fill("#clubFormCapacity", "12")
    page.fill("#clubFormBuoiMoi", "Chiều thứ ba")
    page.click("#btnSaveClub")
    page.wait_for_function("document.getElementById('clubFormFeedback').innerText.length > 0")
    c = _clb(api, "bong_ro")
    assert c and c["capacity"] == 12 and c["buoi"] == "chiều_thứ_ba" and c["name"] == "Bóng rổ", c


def test_ma_tu_dien_theo_ten_khong_de_len_clb_co_san_va_dung_khi_sua_tay(trang):
    page, api, loi = trang
    page.fill("#clubFormName", "Câu lạc bộ Cờ Vua")
    assert page.input_value("#clubFormId") == "cau_lac_bo_co_vua"
    assert api.create_or_update_club("cau_lac_bo_co_vua", "Cũ", 5, None, None, None)["ok"]
    page.click("#qlTabHs")
    page.click("#qlTabClb")
    page.reload()
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_function("document.querySelectorAll('#adminClubTableBody tr').length > 0")
    page.fill("#clubFormName", "Câu lạc bộ Cờ Vua")
    assert page.input_value("#clubFormId") == "cau_lac_bo_co_vua_2"          # không ghi đè CLB đã có
    page.click("#clubFormThemTuyChon")
    page.fill("#clubFormId", "clb_tay")
    page.fill("#clubFormName", "Câu lạc bộ Cờ Vua mới")
    assert page.input_value("#clubFormId") == "clb_tay"                     # đã sửa tay thì không tự đổi nữa


def test_luu_clb_khong_mo_tuy_chon_giu_nguyen_mac_dinh_cu(trang):
    page, api, loi = trang
    page.fill("#clubFormName", "Robot")
    page.fill("#clubFormCapacity", "8")
    page.click("#btnSaveClub")
    page.wait_for_function("document.getElementById('clubFormFeedback').innerText.length > 0")
    c = _clb(api, "robot")
    assert c["capacity"] == 8 and c["reserve_capacity"] == 0 and not c["reserve_group"]
    assert c["buoi"] in (None, "", "__mac_dinh__")


def test_cot_buoi_co_nhan_ro_va_khong_con_chu_chua_chia_buoi(trang):
    page, api, loi = trang
    assert api.create_or_update_club("t3", "Vẽ", 9, None, None, "thu_3")["ok"]
    assert api.create_or_update_club("t4", "Nhạc", 5, None, None, None)["ok"]
    page.reload()
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_function("document.querySelectorAll('#adminClubTableBody tr').length > 0")
    head = page.locator('th[data-i18n="ux4_cot_buoi"]')
    assert head.is_visible() and head.inner_text().strip().lower() == "buổi sinh hoạt"
    assert "Chưa chia" not in page.locator("#qlPanelClb").inner_text()
    assert "Một buổi chung" in page.locator("#adminClubTableBody").inner_text()


def test_hoc_sinh_nut_gan_xuat_chi_hien_khi_da_chon_va_gan_la_nut_vang(trang):
    page, api, loi = trang
    page.click("#qlTabHs")
    page.wait_for_selector(".admin-row-checkbox")
    ids = [x for x in page.evaluate(JS_DEM, "#qlPanelHs") if x != "INPUT"]      # bỏ ô tick của hàng
    assert set(ids) <= {"adminStudentSearch", "adminLopLoc", "adminChonTatCa", "adminHsThemTuyChon",
                        "btnAdminPrevPage", "btnAdminNextPage"}, ids
    for i in ("btnBulkAssign", "btnAdminXuatHs", "bulkReserveGroupInput"):
        assert page.locator("#" + i).is_hidden(), i
    assert page.locator("#adminSapXep").is_hidden()
    page.locator(".admin-row-checkbox").first.check()
    page.wait_for_selector("#btnBulkAssign", state="visible")
    assert page.locator("#adminDemDanhDau").inner_text().strip() == "Đã chọn 1 học sinh"
    assert page.locator("#btnAdminXuatHs").is_visible() and page.locator("#bulkReserveGroupInput").is_visible()
    vang = page.evaluate("Array.from(document.querySelectorAll('.btn-primary')).filter(e=>e.getClientRects().length).map(e=>e.id)")
    assert vang == ["btnBulkAssign"], vang
    page.locator(".admin-row-checkbox").first.uncheck()
    page.wait_for_selector("#btnBulkAssign", state="hidden")
    page.click("#adminHsThemTuyChon")
    assert page.locator("#adminSapXep").is_visible()


def test_ngan_sach_hick_hoc_sinh_chua_chon_khong_qua_bay_o(trang):
    page, api, loi = trang
    page.click("#qlTabHs")
    page.wait_for_selector(".admin-row-checkbox")
    n = len(page.evaluate(JS_DEM, "#qlPanelHs"))
    assert n <= 7, page.evaluate(JS_DEM, "#qlPanelHs")
