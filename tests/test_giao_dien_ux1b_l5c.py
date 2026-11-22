"""UX1B-L5c: năm đề xuất của UX1_DANH_GIA_A §4 (chỉ thông điệp / bố cục; không đổi dữ liệu hay cách xếp).
Chromium thật qua `mo_trang` (workspace). Dữ liệu MÔ PHỎNG."""

import base64
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")


def _nap(api, duong):
    with open(duong, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]


def _luat(api):
    return api.get_workspace_config()["data"]["config"]["rules"]


def _huy_chuong_tren_so_dqt(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api, SO_120)
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    return page, api, loi


# ------------------------------------------------------------------ 1. một dòng gộp + lối về Cài đặt + Quay lại
def test_r1_canh_bao_huy_chuong_gop_mot_dong_co_ten_clb_va_ve_cai_dat(mo_trang):  # noqa: F811
    page, api, loi = _huy_chuong_tren_so_dqt(mo_trang)
    page.locator('.nav-item[data-tab="pipeline"]').click()
    page.reload()
    page.wait_for_selector("#healthList .health-item")
    dong = page.locator("#healthList .health-item")
    chu = [dong.nth(i).inner_text() for i in range(dong.count())]
    gop = [c for c in chu if "huy chương hợp lệ" in c]
    assert len(gop) == 1, chu
    assert len([c for c in chu if "huy chương" in c.lower()]) == 1, chu   # trước: hàng trăm dòng huy chương từng em
    assert "120 học sinh" in gop[0] and "clb_" not in gop[0]   # số em + tên CLB, không mã thô
    assert page.locator("#viecTiepTheo").get_attribute("data-trang-thai") == "huy_chuong_sai"
    assert "Mở Cài đặt" in page.locator("#viecTiepTheoNut").inner_text()
    page.locator("#viecTiepTheoNut").click()                  # thanh "Việc tiếp theo" -> khung Cài đặt
    page.wait_for_selector("#ux1aSsHuyChuongSai", state="visible")
    assert page.locator('.nav-item[data-tab="admin"]').get_attribute("class").count("is-active")
    page.locator("#ux1bSsQuayLai").click()                    # Quay lại Chia 100 điểm
    page.wait_for_function("document.getElementById('ux1aChia100').getAttribute('aria-checked') === 'true'")
    luat = _luat(api)
    assert luat["wharton"] is True and luat["fa_daa"] is False
    assert not loi, loi


# ---- fix1: chỉ gộp khi CẢ SỔ sai; ít em sai giữ từng dòng, thanh Việc tiếp theo không nhảy sang Cài đặt
def _so_fa_mot_em_sai(api):
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    _nap(api, SO_FA)
    with api._ket_noi_ghi() as cur:
        sid = cur.execute("SELECT student_id FROM wharton_bids ORDER BY student_id LIMIT 1").fetchone()[0]
        cid = cur.execute("SELECT club_id FROM wharton_bids WHERE student_id = ? LIMIT 1", (sid,)).fetchone()[0]
        cur.execute("UPDATE wharton_bids SET points = 55 WHERE student_id = ? AND club_id = ?", (sid, cid))
        ma_clb = cur.execute("SELECT club_id FROM clubs ORDER BY club_id LIMIT 1").fetchone()[0]
        cur.execute("UPDATE clubs SET loai = NULL WHERE club_id = ?", (ma_clb,))
    return sid


def test_r1b_it_em_sai_giu_tung_dong_va_thanh_khong_nhay_sang_cai_dat(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    sid = _so_fa_mot_em_sai(api)
    assert api.get_data_health_report()["data"]["gop_huy_chuong"] is None
    page.reload()
    page.wait_for_selector("#healthList .health-item")
    chu = [page.locator("#healthList .health-item").nth(i).inner_text()
           for i in range(page.locator("#healthList .health-item").count())]
    assert any(sid in c for c in chu), chu                            # còn dòng riêng của em có mã
    assert not any("chưa có huy chương hợp lệ" in c for c in chu), chu
    assert page.locator("#viecTiepTheo").get_attribute("data-trang-thai") != "huy_chuong_sai"
    page.locator('.nav-item[data-tab="admin"]').click()               # khung Cài đặt: câu "một phần" + nút, VẪN đặt loại được
    page.click("#qlTabCachXep")   # UX4-L2: khung Cài đặt nằm trong tab Cách xếp
    page.wait_for_selector("#ux1aSsHuyChuongSai")
    assert "Gần như cả sổ" not in page.locator("#ux1aSsHuyChuongSai").inner_text()
    assert page.locator("#ux1bSsQuayLai").is_visible()
    assert page.locator("#ux1aSanSang .ux1a-vien").count() >= 1
    assert not loi, loi


def test_r1c_khong_ten_clb_thi_khong_in_vi_du_o_rong(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    _nap(api, SO_FA)
    with api._ket_noi_ghi() as cur:                                   # mọi em dùng cùng một huy chương hai lần trong buổi:
        cur.execute("UPDATE wharton_bids SET points = 60")            # lỗi "trùng giá trị" không có mã CLB
    gop = api.get_data_health_report()["data"]["gop_huy_chuong"]
    assert gop and gop["clb"] == []
    page.reload()
    page.wait_for_selector("#healthList .health-item")
    chu = page.locator("#healthList").inner_text()
    assert "chưa có huy chương hợp lệ" in chu and "ví dụ ở" not in chu
    assert not loi, loi


# ------------------------------------------------------------------ 2. cả sổ sai: chỉ nạp lại, ẩn nút loại CLB
def test_r2_ca_so_sai_chi_hien_tai_so_mau_va_quay_lai_an_nut_loai(mo_trang):  # noqa: F811
    page, api, loi = _huy_chuong_tren_so_dqt(mo_trang)
    page.locator('.nav-item[data-tab="admin"]').click()
    page.click("#qlTabCachXep")   # UX4-L2: khung Cài đặt nằm trong tab Cách xếp
    page.wait_for_selector("#ux1aSsHuyChuongSai")
    chu = page.locator("#ux1aSsHuyChuongSai").inner_text()
    assert "Gần như cả sổ" in chu and "120/120" in chu
    assert page.locator("#ux1bSsTaiSoMau").is_visible() and page.locator("#ux1bSsQuayLai").is_visible()
    assert page.locator("#ux1aSanSang .ux1a-ss-dong").count() == 0
    assert page.locator("#ux1aSanSang .ux1a-vien").count() == 0
    assert not loi, loi


# ------------------------------------------------------------------ 3. Sau khi xếp: câu đầy đủ + hệ quả + ô số thẳng hàng
def test_r3_sau_khi_xep_co_dong_he_qua_va_o_so_thang_hang(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    _nap(api, SO_FA)
    kq = api.run_pipeline(42)
    assert kq["ok"], kq["errors"]
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#ux1aSauXep", state="visible")
    page.wait_for_selector("#ux1aSx_fa_khieu_nai")
    dong = page.locator("#ux1aSauXepLuoi .ux1a-sx-dong")
    assert dong.count() >= 3
    for i in range(dong.count()):
        assert len(dong.nth(i).locator(".ux1b-sx-he-qua").inner_text().strip()) > 20      # mỗi hành động có một dòng hệ quả
    assert "mã tra cứu" in page.locator('[data-co="fa_khieu_nai"] .ux1b-sx-he-qua').inner_text()
    nut = page.locator("#ux1aSx_fa_khieu_nai").bounding_box()
    o = page.locator("#ux1aSxNgay").bounding_box()
    ngay = page.locator('[data-co="fa_khieu_nai"] .ux1b-sx-ngay').bounding_box()
    tam = lambda b: b["y"] + b["height"] / 2  # noqa: E731
    assert abs(tam(nut) - tam(o)) <= 2 and abs(tam(o) - tam(ngay)) <= 2          # nút, ô số, chữ "ngày" cùng một hàng
    page.locator("#ux1aSx_fa_khieu_nai").click()
    page.wait_for_function("document.getElementById('ux1aSx_fa_khieu_nai').getAttribute('aria-pressed') === 'true'")
    assert "Nhận khiếu nại trong 3 ngày" in page.locator("#ux1aSx_fa_khieu_nai").inner_text()   # trọn câu, không cụt
    assert not loi, loi


# ------------------------------------------------------------------ 4. khung tra cứu gọn
def test_r4_khung_tra_cuu_o_tim_to_o_dau_va_ma_tra_cuu_gap(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api, SO_120)
    assert api.run_pipeline(42)["ok"]
    page.locator('.nav-item[data-tab="results"]').click()
    page.wait_for_selector("#gtTim", state="visible")
    assert page.locator("#gtTim").bounding_box()["height"] >= 44
    assert page.locator("#gtBuocHuongDan").is_hidden() and page.locator("#btnGtTaoMa").is_hidden()
    assert page.locator("#gtMaFold > summary").inner_text().strip() == "Mã tra cứu cho học sinh tự xem…"   # UX5A-L2
    assert page.get_attribute("#gtTim", "placeholder") != page.get_attribute("#kqTimKiem", "placeholder")
    assert page.locator("#gtTim").bounding_box()["y"] < page.locator("#gtMaFold").bounding_box()["y"]
    page.locator("#gtMaFold > summary").click()
    assert page.locator("#btnGtTaoMa").is_visible() and page.locator("#btnGtCheDoHs").is_visible()
    assert not loi, loi


# ------------------------------------------------------------------ 5. tên nhóm khớp trang; dòng đỏ riêng tư GIỮ hiện sẵn
def test_r5_ten_nhom_khop_trang_va_dong_do_rieng_tu_van_hien_san(mo_trang):  # noqa: F811
    """Tệp xuất MẶC ĐỊNH (sheet Điểm chuẩn, Dấu vết) có điểm và số bốc thăm, nên dòng đỏ không được giấu vào "Tuỳ chọn khác"."""
    page, api, goc, loi = mo_trang()
    _nap(api, SO_120)
    assert api.run_pipeline(42)["ok"]
    assert page.locator('.nav-nhom[data-nhom="cai_dat"] .nav-nhom-nut').inner_text().strip() == "Cài đặt và quản lý"
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#xuatPanel")
    assert page.locator("#xuatPanel .xuat-canh-bao").is_visible()
    assert "số bốc thăm" in page.locator("#xuatPanel .xuat-canh-bao").inner_text()
    assert not loi, loi
