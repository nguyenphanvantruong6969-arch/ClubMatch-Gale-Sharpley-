"""SF-B7 (ST-A-001): đổi chế độ khi dữ liệu đã nạp thiếu thứ chế độ mới cần: Cài đặt hiện cảnh báo dưới các thẻ chế độ.
Dữ liệu MÔ PHỎNG."""
from ho_tro import chon_cach, nap_so_150


def _canh_bao(ui):
    p = ui.page
    o = p.locator("#ux1aCanhBaoDuLieu")
    return o.inner_text() if o.count() and o.is_visible() else ""


def test_b5_doi_sang_huy_chuong_khi_thieu_du_lieu_co_canh_bao_roi_het_khi_doi_lai(mo):
    ui = mo()
    chon_cach(ui, "chia_100")
    nap_so_150(ui)                       # nạp ở Chia 100: sổ không giữ huy chương / Loại
    chon_cach(ui, "huy_chuong")
    ui.page.wait_for_selector("#ux1aCanhBaoDuLieu", state="visible")
    chu = _canh_bao(ui)
    assert "Đã đổi chế độ" in chu and "{" not in chu and "n_thieu" not in chu, chu
    chon_cach(ui, "chia_100")            # đổi chế độ thì làm mới: không còn cảnh báo
    ui.page.wait_for_selector("#ux1aCanhBaoDuLieu", state="hidden")
    ui.kiem_loi()


def test_b5_doi_che_do_khi_du_du_lieu_khong_co_canh_bao(mo):
    ui = mo()
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)                       # nạp ở Huy chương: có đủ cột
    chon_cach(ui, "chia_100")
    chon_cach(ui, "huy_chuong")
    assert not _canh_bao(ui)
    assert ui.page.locator("#ux1aCanhBaoDuLieu").count() == 0 or ui.page.locator("#ux1aCanhBaoDuLieu").is_hidden()
    ui.kiem_loi()
