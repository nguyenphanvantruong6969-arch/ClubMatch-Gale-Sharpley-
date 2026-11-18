"""UX1A-L2b: trang Cài đặt = một câu hỏi, ba thẻ, lưu ngay + Hoàn tác, sửa tại chỗ cho Huy chương,
việc sau khi xếp là hành động ở thẻ Chi tiết. Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG."""

import base64
import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


def _luat(api):
    return api.get_workspace_config()["data"]["config"]["rules"]


def _vao_cai_dat(page):
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#ux1aChia100", state="visible")
    page.wait_for_selector('.ux1a-the[aria-checked="true"]')      # cấu hình đã nạp xong


def _chon(page, ma):
    return page.locator("#ux1a" + ma).get_attribute("aria-checked")


def _nap_120(api):
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]


def test_workspace_moi_chon_san_chia_100_diem(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _vao_cai_dat(page)
    assert _chon(page, "Chia100") == "true"
    assert _chon(page, "ChiXep") == "false" and _chon(page, "HuyChuong") == "false"
    assert page.locator("#ux1aCauHoi").inner_text().strip() == "Học sinh cho biết mình muốn CLB nào nhiều hơn bằng cách nào?"
    assert "mặc định" in page.locator("#ux1aChia100").inner_text()
    assert "60 · 30 · 10" in page.locator("#ux1aHuyChuong").inner_text()
    assert "→" in page.locator("#ux1aCachXet").inner_text()        # câu "Cách xét khi đông" sinh từ Tiêu chí xếp
    assert not loi, loi


def test_mot_cu_bam_huy_chuong_luu_ngay_va_hoan_tac_khoi_phuc(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _vao_cai_dat(page)
    page.locator("#ux1aHuyChuong").click()
    page.wait_for_function("document.getElementById('ux1aHuyChuong').getAttribute('aria-checked') === 'true'")
    luat = _luat(api)
    assert luat["wharton"] is True and luat["fa_daa"] is True         # đọc lại cấu hình: không cần bấm gì khác
    toast = page.locator(".toast", has_text="Đã chuyển sang Huy chương")
    toast.wait_for()
    toast.get_by_role("button", name="Hoàn tác").click()
    page.wait_for_function("document.getElementById('ux1aChia100').getAttribute('aria-checked') === 'true'")
    luat = _luat(api)
    assert luat["wharton"] is True and luat["fa_daa"] is False
    assert not loi, loi


def test_chi_xep_thu_tu_ep_fa_daa_tat_va_tat_luon_co_sau_xep(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True, "fa_phan_hoi": True}})["ok"]
    _vao_cai_dat(page)
    assert _chon(page, "HuyChuong") == "true"
    page.locator("#ux1aChiXep").click()
    page.wait_for_function("document.getElementById('ux1aChiXep').getAttribute('aria-checked') === 'true'")
    luat = _luat(api)
    assert luat["wharton"] is False and luat["fa_daa"] is False and luat["fa_phan_hoi"] is False
    toast = page.locator(".toast", has_text="Đã chuyển sang Chỉ xếp thứ tự")
    toast.get_by_role("button", name="Hoàn tác").click()          # hoàn tác trả lại cả cờ sau khi xếp
    page.wait_for_function("document.getElementById('ux1aHuyChuong').getAttribute('aria-checked') === 'true'")
    assert _luat(api)["fa_phan_hoi"] is True
    assert not loi, loi


def test_doi_cach_chon_ap_dung_ngay_khong_can_khoi_dong_lai(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _vao_cai_dat(page)
    assert page.evaluate("FA_BAT") is False
    page.locator("#ux1aHuyChuong").click()
    page.wait_for_function("FA_BAT === true")
    page.locator("#ux1aChiXep").click()
    page.wait_for_function("FA_BAT === false && WHARTON_BAT === false")
    assert not loi, loi


def test_co_ket_qua_roi_thong_bao_them_dong_giu_nguyen_ket_qua(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap_120(api)
    assert api.run_pipeline(42)["ok"]
    _vao_cai_dat(page)
    page.locator("#ux1aChiXep").click()
    page.locator(".toast", has_text="Kết quả đã xếp giữ nguyên").wait_for()
    assert not loi, loi


def test_huy_chuong_du_lieu_chua_san_sang_sua_tai_cho_den_khi_san_sang(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap_120(api)
    _vao_cai_dat(page)
    page.locator("#ux1aHuyChuong").click()
    page.wait_for_selector("#ux1aSanSang .ux1a-ss-dong")
    assert page.locator("#ux1aSanSang .ux1a-ss-dong[data-clb]").count() == 9
    assert page.locator("#ux1aSanSang .ux1a-ss-dong[data-buoi]").count() == 3
    assert "Thứ 4" in page.locator('#ux1aSanSang .ux1a-ss-dong[data-buoi="thu_4"]').inner_text()
    # một CLB Tự do cho mỗi buổi qua nút chọn; sau đó đặt các CLB còn lại bằng viên thuốc Giới hạn
    for buoi in ("thu_2", "thu_4", "thu_6"):
        sel = page.locator('#ux1aSanSang select[data-buoi="%s"]' % buoi)
        sel.select_option(index=1)
        page.wait_for_function("b => !document.querySelector('#ux1aSanSang select[data-buoi=\"' + b + '\"]')", arg=buoi)
    while page.locator("#ux1aSanSang .ux1a-vien[data-loai='GIOI_HAN']").count():
        n = page.locator("#ux1aSanSang .ux1a-vien[data-loai='GIOI_HAN']").count()
        page.locator("#ux1aSanSang .ux1a-vien[data-loai='GIOI_HAN']").first.click()
        page.wait_for_function(
            "n => document.querySelectorAll('#ux1aSanSang .ux1a-vien[data-loai=\"GIOI_HAN\"]').length < n"
            " || !!document.getElementById('ux1aSanSangXong')", arg=n)
    page.wait_for_selector("#ux1aSanSangXong")
    assert page.locator("#ux1aSanSangXong").inner_text().strip() == "Sẵn sàng"
    assert api.get_san_sang_huy_chuong()["data"]["san_sang"] is True
    assert not loi, loi


def test_cai_dat_khong_con_o_tick_viec_sau_khi_xep(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _vao_cai_dat(page)
    # không ô tick FA nào trong trang Cài đặt (ô điểm quyết tâm của Tiêu chí xếp cũng đã bỏ)
    assert page.locator("#view-admin #ux1aCaiDat input[type=checkbox]").count() == 0
    assert page.locator("#gt2TcWharton").count() == 0
    assert page.locator("[data-khoa]").count() == 0
    assert page.locator("#wsTnWharton").count() == 0
    assert not loi, loi


def test_hanh_dong_sau_khi_xep_chi_hien_o_che_do_huy_chuong(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#xuatPanel")
    assert page.locator("#ux1aSauXep").is_hidden()                 # mặc định Chia 100 điểm: không có
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    page.locator('.nav-item[data-tab="admin"]').click()
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#ux1aSauXep", state="visible")
    assert "Mở vòng 2 cho" in page.locator("#ux1aSx_fa_vong_2").inner_text()
    page.locator("#ux1aSx_fa_vong_2").click()
    page.wait_for_function("document.getElementById('ux1aSx_fa_vong_2').getAttribute('aria-pressed') === 'true'")
    assert _luat(api)["fa_vong_2"] is True
    page.locator("#ux1aSxNgay").fill("5")
    page.locator("#ux1aSx_fa_khieu_nai").click()
    page.wait_for_function("document.getElementById('ux1aSx_fa_khieu_nai').getAttribute('aria-pressed') === 'true'")
    luat = _luat(api)
    assert luat["fa_khieu_nai"] is True and luat["fa_khieu_nai_so_ngay"] == 5
    assert not loi, loi


def test_menu_ba_cham_cai_dat_mo_cung_ba_the(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator('tr[data-slug="truong-hoc"] .menu-khac > summary').click()
    page.locator('tr[data-slug="truong-hoc"]').get_by_text(re.compile("^Cài đặt…$")).click()
    page.wait_for_selector("#ux1aWsChia100")
    page.wait_for_selector('#ux1aWsThan .ux1a-the[aria-checked="true"]')   # cấu hình đã nạp xong
    assert page.locator("#ux1aWsChia100").get_attribute("aria-checked") == "true"
    page.locator("#ux1aWsHuyChuong").click()
    page.wait_for_function("document.getElementById('ux1aWsHuyChuong').getAttribute('aria-checked') === 'true'")
    assert _luat(api)["fa_daa"] is True
    page.locator("#ux1aWsXong").click()
    page.wait_for_selector("#ux1aWsTieuDe", state="detached")
    assert not loi, loi


def test_thay_doi_mo_muc_nang_cao_voi_tieu_chi_xep(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _vao_cai_dat(page)
    assert not page.evaluate("document.getElementById('ux1aNangCao').open")
    page.locator("#ux1aThayDoi").click()
    page.wait_for_selector("#gt2TieuChiPanel", state="visible")
    assert page.evaluate("document.getElementById('ux1aNangCao').open")
    assert not loi, loi
