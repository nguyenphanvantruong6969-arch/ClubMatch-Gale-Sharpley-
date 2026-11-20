"""MT1-L4 — giao diện ba thẻ mục tiêu (câu hỏi thứ hai ở Cài đặt + dòng kết quả). Chromium thật qua `browser_host`.

Mỗi dòng của "UI contract 1–7" (docs/phien/claude__mt1-bo-muc-tieu.md) có ít nhất một ca. Dữ liệu MÔ PHỎNG
(`SO_NHAP_DQT_120HS_HOP_LE.xlsx`: 120 em, 9 CLB, hai nhóm: khoi_10 18 em, chinh_sach 12 em). Số lần bấm đếm bằng
số lần `.click()` của test (không tính việc mở Cài đặt).
"""

import base64
import os
import re
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
MK = "matkhau-gia-1"
CAM = ("dự trữ", "STB", "Wharton", "wharton", "tier", "reserve", "khoi_10", "chinh_sach", "nang_luc",
       "co_hoi", "danh_cho", "fa_daa")


def _nap(api, chi_mot_nhom=False, khong_nhom=False, tep=SO_120):
    with open(tep, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    if chi_mot_nhom or khong_nhom:
        c = sqlite3.connect(api.db_path)
        c.execute("UPDATE students SET reserve_group = NULL WHERE reserve_group = 'chinh_sach'" if chi_mot_nhom
                  else "UPDATE students SET reserve_group = NULL")
        c.commit()
        c.close()


def _luat(api):
    return api.get_workspace_config()["data"]["config"]["rules"]


def _cfg(api):
    return api.get_workspace_config()["data"]["config"]


def _clb(api):
    c = sqlite3.connect(api.db_path)
    try:
        return c.execute("SELECT club_id, capacity, reserve_capacity, reserve_group FROM clubs "
                         "ORDER BY club_id").fetchall()
    finally:
        c.close()


def _vao(page):
    """Mở Cài đặt, đợi cả hai câu hỏi vẽ xong."""
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#ux1aChia100", state="visible")
    page.wait_for_selector('#ux1aCaiDatThan .ux1a-the[aria-checked="true"]')
    page.wait_for_selector("#ux1aMtNangLuc", state="visible")
    page.wait_for_function("document.querySelectorAll('#ux1aCaiDatThan .ux1a-the[aria-checked=\"true\"]').length >= 1")


def _chon(page, ma):
    return page.locator("#ux1aMt" + ma).get_attribute("aria-checked")


def _cho_chon(page, ma):
    page.wait_for_function("m => document.getElementById('ux1aMt' + m).getAttribute('aria-checked') === 'true'", arg=ma)


def _chon_nhom(page, nhan="khối 10"):
    """Bấm nút nhóm (bấm thứ hai của "Dành chỗ" khi có nhiều nhóm) và đợi nút ấy sáng = đã lưu xong."""
    page.locator("#ux1aMtNhom button", has_text=nhan).click()
    page.wait_for_function("n => [...document.querySelectorAll('#ux1aMtNhom button')].some(b => "
                           "b.textContent.trim() === n && b.getAttribute('aria-pressed') === 'true')", arg=nhan)


def _the_hien_tai(page):
    return page.evaluate("""() => { const a = [...document.querySelectorAll('#ux1aMtLuoi .ux1a-the')]
        .filter(b => b.getAttribute('aria-checked') === 'true'); return a.map(b => b.dataset.cach); }""")


# ----- 1. Chỗ đặt, cùng thành phần -----

def test_cau_hoi_thu_hai_nam_duoi_cau_hoi_dau_cung_thanh_phan_va_thay_dong_cach_xet(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _vao(page)
    thu_tu = page.evaluate("""() => { const n = [...document.querySelectorAll('#ux1aCaiDatThan h2.ux1a-cau-hoi')];
        return n.map(x => x.id); }""")
    assert thu_tu == ["ux1aCauHoi", "ux1aMtCauHoi"]
    assert page.locator("#ux1aCachXet").count() == 0                       # dòng "Cách xét khi đông" đã được thay
    assert page.locator("#ux1aCaiDatThan #ux1aThayDoi").count() == 1       # "Thay đổi…" nằm dưới câu hỏi mới
    assert page.evaluate("document.getElementById('ux1aMtCauHoi').compareDocumentPosition("
                         "document.getElementById('ux1aThayDoi')) & Node.DOCUMENT_POSITION_FOLLOWING")
    kieu = lambda sel: page.locator(sel).evaluate(  # noqa: E731
        "e => { const s = getComputedStyle(e); return [s.padding, s.borderRadius, s.borderWidth, s.fontSize, s.gap]; }")
    assert kieu("#ux1aChia100") == kieu("#ux1aMtNangLuc")                  # cùng một khuôn thẻ
    assert kieu("#ux1aChia100 .ux1a-the-tt") == kieu("#ux1aMtNangLuc .ux1a-the-tt")
    assert page.locator("#ux1aMtCauHoi").inner_text().strip() == "Khi một CLB đông người, trường ưu tiên điều gì?"
    assert [t.strip() for t in page.locator("#ux1aMtLuoi .ux1a-the-tt").all_inner_texts()] == \
        ["Theo năng lực", "Cơ hội như nhau", "Dành chỗ cho một nhóm"]
    assert _the_hien_tai(page) == ["nang_luc"]                              # mặc định
    assert page.locator("#ux1aCaiDatThan > *").count() >= 2 and not page.locator('[role="dialog"]').count()
    assert not loi, loi


def test_the_giong_trong_trinh_tao_workspace_buoc_3(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Thử mục tiêu")
    page.locator("#wzTuyChinh").click()
    page.locator("#wzTiep").click()                                         # bước 3: luật
    page.wait_for_selector("#wzMtCauHoi")
    assert [t.strip() for t in page.locator("#wzMtLuoi .ux1a-the-tt").all_inner_texts()] == \
        ["Theo năng lực", "Cơ hội như nhau", "Dành chỗ cho một nhóm"]
    assert page.locator("#wzMtDanhCho").is_disabled()                       # chưa có danh sách học sinh để chọn nhóm
    assert page.locator("#wzMtNangLuc").get_attribute("aria-checked") == "true"
    assert page.locator("#wzMtGhiChu").is_hidden()
    page.locator("#wzMtCoHoi").click()
    assert page.locator("#wzPriority").input_value() == "tier"
    assert "Điểm chia không được dùng với mục tiêu này." in page.locator("#wzMtGhiChu").inner_text()   # chỉ có khi đang Chia 100
    page.locator("#wzMtNangLuc").click()
    assert page.locator("#wzPriority").input_value() == "score"
    assert page.locator("#wzMtGhiChu").is_hidden()
    assert not loi, loi


# ----- 2. Số lần bấm, lưu ngay, không hộp thoại -----

def test_mot_cu_bam_nang_luc_va_co_hoi_luu_ngay_khong_hop_thoai(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    hop_thoai = []
    page.on("dialog", lambda d: (hop_thoai.append(d.message), d.dismiss()))
    _vao(page)
    page.locator("#ux1aMtCoHoi").click()                                    # BẤM 1
    _cho_chon(page, "CoHoi")
    assert _luat(api)["priority"] == "tier" and _cfg(api)["muc_tieu"]["id"] == "co_hoi"
    nhan = " ".join(b.lower() for b in page.locator("#ux1aCaiDatThan button").all_inner_texts())
    assert not re.search(r"\blưu\b|xem trước|bạn có chắc|xác nhận|áp dụng", nhan)
    assert not hop_thoai
    page.locator("#ux1aMtNangLuc").click()                                  # BẤM 1
    _cho_chon(page, "NangLuc")
    assert _luat(api)["priority"] == "score" and _cfg(api)["muc_tieu"]["id"] == "nang_luc"
    assert not loi, loi


def test_danh_cho_mot_nhom_1_cu_bam_nhieu_nhom_2_cu_bam(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api, chi_mot_nhom=True)
    _vao(page)
    assert page.locator("#ux1aMtNhom button").count() == 0
    page.locator("#ux1aMtDanhCho").click()                                  # BẤM 1 — một nhóm: tự chọn
    _cho_chon(page, "DanhCho")
    assert _cfg(api)["muc_tieu"] == {"id": "danh_cho", "nhom": "khoi_10",
                                      "truoc": _cfg(api)["muc_tieu"]["truoc"]}
    assert all(r[3] == "khoi_10" for r in _clb(api))
    assert not loi, loi


def test_danh_cho_nhieu_nhom_hai_cu_bam_va_the_chua_ap_sau_cu_bam_thu_nhat(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    truoc = (_cfg(api), _clb(api))
    _vao(page)
    page.locator("#ux1aMtDanhCho").click()                                  # BẤM 1 — hiện nhóm, CHƯA áp
    page.wait_for_selector("#ux1aMtNhom button")
    assert [b.strip() for b in page.locator("#ux1aMtNhom button").all_inner_texts()] == ["khối 10", "chính sách"]
    assert (_cfg(api), _clb(api)) == truoc
    _chon_nhom(page)          # BẤM 2
    assert _cfg(api)["muc_tieu"]["nhom"] == "khoi_10" and all(r[3] == "khoi_10" for r in _clb(api))
    assert not loi, loi


def test_danh_cho_khong_co_nhom_the_bi_khoa_voi_mot_dong_ly_do(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api, khong_nhom=True)
    _vao(page)
    assert page.locator("#ux1aMtDanhCho").is_disabled()
    assert "Sổ nhập chưa có cột nhóm." in page.locator("#ux1aMtLyDo").inner_text()
    assert not loi, loi


# ----- 2/3. Thông báo, Hoàn tác -----

def test_toast_hoan_tac_tra_dung_luat_va_tung_clb_hai_lan_lien_tiep(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    cfg0, clb0 = _cfg(api), _clb(api)
    _vao(page)
    page.locator("#ux1aMtDanhCho").click()
    _chon_nhom(page)
    toast1 = page.locator(".toast", has_text="Đã chuyển sang Dành chỗ cho một nhóm")
    toast1.wait_for()
    assert (_cfg(api), _clb(api)) != (cfg0, clb0)
    toast1.get_by_role("button", name="Hoàn tác").click()                   # hoàn tác lần 1
    _cho_chon(page, "NangLuc")
    assert (_cfg(api), _clb(api)) == (cfg0, clb0)
    page.locator("#ux1aMtCoHoi").click()
    page.locator(".toast", has_text="Đã chuyển sang Cơ hội như nhau").wait_for()
    page.locator(".toast .toast-hanh-dong", has_text="Hoàn tác").click()    # hoàn tác lần 2 (thẻ khác)
    _cho_chon(page, "NangLuc")
    assert (_cfg(api), _clb(api)) == (cfg0, clb0)
    assert not loi, loi


def test_thong_bao_cu_bi_thay_boi_lan_chon_moi_va_hoan_tac_dung_lan_moi_nhat(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    _vao(page)
    page.locator("#ux1aMtDanhCho").click()
    _chon_nhom(page)
    sau_danh_cho = (_cfg(api), _clb(api))
    page.locator(".toast", has_text="Đã chuyển sang Dành chỗ cho một nhóm").wait_for()
    page.locator("#ux1aMtCoHoi").click()
    moi = page.locator(".toast", has_text="Đã chuyển sang Cơ hội như nhau")
    moi.wait_for()
    page.wait_for_function("document.querySelectorAll('.toast').length === 1")      # chỉ còn thông báo mới nhất
    assert page.locator(".toast", has_text="Dành chỗ cho một nhóm").count() == 0
    moi.get_by_role("button", name="Hoàn tác").click()                              # hoàn tác lần MỚI NHẤT
    _cho_chon(page, "DanhCho")
    assert (_cfg(api), _clb(api)) == sau_danh_cho
    assert not loi, loi


def test_dong_tac_dong_0_0_noi_ket_qua_khong_noi_da_theo_muc_tieu(mo_trang, monkeypatch):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    goc_fn = api.uoc_tinh_muc_tieu

    def khong_doi(*a, **k):
        kq = goc_fn(*a, **k)
        kq["data"].update({"co_so_sanh": True, "tot_hon": {"n": 0, "duoi_5": False},
                           "xuong_sau": {"n": 0, "duoi_5": False}})
        return kq
    monkeypatch.setattr(api, "uoc_tinh_muc_tieu", khong_doi)
    _vao(page)
    page.locator("#ux1aMtCoHoi").click()                                    # luật khác lần xếp, nhưng kết quả y hệt
    _cho_chon(page, "CoHoi")
    page.wait_for_function("document.getElementById('ux1aMtHieuQua').textContent.includes('đổi chỗ')")
    chu = page.locator("#ux1aMtHieuQua").inner_text()
    assert "Không học sinh nào đổi chỗ so với lần xếp gần nhất." in chu
    assert "đã theo mục tiêu" not in chu
    assert not loi, loi


def test_co_hoi_khi_chia_100_diem_bao_diem_chia_khong_dung_va_hoan_tac_tra_lai(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert _luat(api)["wharton"] is True
    _vao(page)
    page.locator("#ux1aMtCoHoi").click()
    page.locator(".toast", has_text="Điểm chia không được dùng với mục tiêu này.").wait_for()
    assert "Điểm chia không được dùng với mục tiêu này." in page.locator("#ux1aMtHieuQua").inner_text()
    assert _luat(api)["wharton"] is False
    page.locator(".toast .toast-hanh-dong", has_text="Hoàn tác").click()
    _cho_chon(page, "NangLuc")
    assert _luat(api)["wharton"] is True
    assert not loi, loi


# ----- 3. Dòng tác động -----

def test_chua_co_lan_xep_dong_tac_dong_la_loi_khong_co_so(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    _vao(page)
    page.locator("#ux1aMtCoHoi").click()
    _cho_chon(page, "CoHoi")
    page.wait_for_function("document.getElementById('ux1aMtHieuQua').textContent.trim().length > 0")
    chu = page.locator("#ux1aMtHieuQua").inner_text()
    assert chu.startswith("Cách xét khi đông:") and "Ước tính" not in chu
    assert not loi, loi


def test_sau_lan_xep_dong_uoc_tinh_hien_ngay_khong_bam_them(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    _vao(page)
    page.locator("#ux1aMtCoHoi").click()
    _cho_chon(page, "CoHoi")
    page.wait_for_function("/Ước tính so với lần xếp gần nhất/.test(document.getElementById('ux1aMtHieuQua').textContent)")
    chu = page.locator("#ux1aMtHieuQua").inner_text()
    assert re.search(r"Ước tính so với lần xếp gần nhất: (\d+|dưới 5) học sinh được chỗ tốt hơn, (\d+|dưới 5) học sinh xuống nguyện vọng sau", chu), chu
    assert not any(c in chu for c in CAM)
    assert not loi, loi


def test_danh_cho_hien_giu_cho_trong_details_gap_san(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    _vao(page)
    page.locator("#ux1aMtDanhCho").click()
    _chon_nhom(page)
    page.wait_for_selector("#ux1aMtChiTiet")
    assert not page.evaluate("document.getElementById('ux1aMtChiTiet').open")
    tom = page.locator("#ux1aMtChiTiet > summary").inner_text()
    assert re.search(r"Giữ \d+/\d+ chỗ", tom) and "Xem từng CLB" in tom
    page.locator("#ux1aMtChiTiet > summary").click()
    dong = page.locator("#ux1aMtChiTiet li").all_inner_texts()
    assert len(dong) == 9 and all(re.search(r"giữ \d+/\d+", d) for d in dong)
    canh = page.locator("#ux1aMtCanhBao .canh-bao-vang").all_inner_texts()
    assert canh and all("chênh lệch ngược" not in c for c in canh)          # câu cũ khó hiểu đã thay
    assert any("không bị thiệt" in c and "Giữ chỗ có thể không cần thiết." in c for c in canh), canh
    assert not loi, loi


def test_canh_bao_chi_mot_dong_moi_loai_mau_vang(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    c = sqlite3.connect(api.db_path)                                        # nhóm 2 em ⇒ chỗ giữ "cho có"
    c.execute("UPDATE students SET reserve_group = NULL")
    c.execute("UPDATE students SET reserve_group = 'khoi_9' WHERE student_id IN "
              "(SELECT student_id FROM students ORDER BY student_id LIMIT 2)")
    c.commit()
    c.close()
    assert api.run_pipeline(42)["ok"]
    _vao(page)
    page.locator("#ux1aMtDanhCho").click()
    _cho_chon(page, "DanhCho")
    page.wait_for_selector("#ux1aMtCanhBao .canh-bao-vang")
    dong = page.locator("#ux1aMtCanhBao .canh-bao-vang").all_inner_texts()
    assert any("chỉ giữ 1–2 chỗ" in d for d in dong)
    assert len(dong) == len({d for d in dong})                              # mỗi loại cảnh báo MỘT dòng
    assert not loi, loi


def test_che_do_huy_chuong_khoa_co_hoi_mot_dong_ly_do_va_uoc_tinh_khong_co(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    _nap(api, tep=os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx"))
    c = sqlite3.connect(api.db_path)                                        # sổ huy chương mẫu: gán hai nhóm
    c.execute("UPDATE students SET reserve_group = NULL")
    for i, (sid,) in enumerate(c.execute("SELECT student_id FROM students ORDER BY student_id").fetchall()):
        if i < 40:
            c.execute("UPDATE students SET reserve_group = ? WHERE student_id = ?",
                      ("khoi_10" if i < 20 else "chinh_sach", sid))
    c.commit()
    c.close()
    assert api.run_pipeline(42)["ok"]
    _vao(page)
    assert page.locator("#ux1aMtCoHoi").is_disabled()
    assert "Chế độ huy chương cần điểm thi" in page.locator("#ux1aMtLyDo").inner_text()
    page.locator("#ux1aMtDanhCho").click()
    _chon_nhom(page)
    page.wait_for_selector("#ux1aMtCanhBao .canh-bao-vang")
    assert "Chưa ước tính được khi đang dùng chế độ huy chương." in page.locator("#ux1aMtCanhBao").inner_text()
    assert not loi, loi


# ----- sửa tay: không thẻ nào sáng -----

def test_sua_tay_o_nang_cao_khong_the_nao_sang_dong_xam_va_ve_muc_tieu_mau(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    _vao(page)
    page.locator("#ux1aMtCoHoi").click()
    _cho_chon(page, "CoHoi")
    assert api.update_workspace_config({"rules": {"priority": "score+tier", "tier_mode": "strict",
                                                  "tiers": ["khoi_10"]}})["ok"]
    page.locator('.nav-item[data-tab="pipeline"]').click()
    _vao(page)
    page.wait_for_selector("#ux1aMtRieng")
    assert _the_hien_tai(page) == []
    assert "Đang dùng cài đặt riêng" in page.locator("#ux1aMtRieng").inner_text()
    page.locator("#ux1aMtRieng button", has_text="Về mục tiêu mẫu").click()   # 1 bấm đưa về thẻ cuối
    _cho_chon(page, "CoHoi")
    assert _luat(api)["priority"] == "tier"
    assert page.locator("#ux1aMtRieng").count() == 0 or page.locator("#ux1aMtRieng").is_hidden()
    assert not loi, loi


# ----- 4. Dòng kết quả -----

def test_dong_ket_qua_hien_o_the_chi_tiet_khong_can_bam(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.chon_muc_tieu("danh_cho", "khoi_10")["ok"]
    assert api.run_pipeline(42)["ok"]
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#mt1KetQua", state="visible")
    chu = page.locator("#mt1KetQua > p").first.inner_text()
    assert re.match(r"Mục tiêu: Dành chỗ cho khối 10 — đạt ở \d/\d CLB được chọn nhiều nhất", chu), chu
    assert "học sinh được giúp" in chu and "học sinh nhường chỗ" in chu
    assert not any(c in page.locator("#mt1KetQua").inner_text() for c in CAM)
    assert page.locator("#mt1KetQua details").count() == 1
    assert not loi, loi


def test_dong_ket_qua_hien_duoi_5_va_bo_so_khi_thieu_cho_giu_ban_dau(mo_trang, monkeypatch):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.chon_muc_tieu("co_hoi")["ok"] and api.run_pipeline(42)["ok"]
    goc_fn = api.bao_cao_muc_tieu

    def gia(*a, **k):
        kq = goc_fn(*a, **k)
        kq["data"].update({"duoc_giup": {"n": None, "duoi_5": True}, "nhuong_cho": {"n": 12, "duoi_5": False}})
        return kq
    monkeypatch.setattr(api, "bao_cao_muc_tieu", gia)
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#mt1KetQua", state="visible")
    chu = page.locator("#mt1KetQua > p").first.inner_text()
    assert "dưới 5 học sinh được giúp" in chu and "12 học sinh nhường chỗ" in chu
    # danh_cho thiếu chỗ giữ ban đầu: câu vẫn đọc được, không có số được giúp / nhường chỗ
    assert api.chon_muc_tieu("danh_cho", "khoi_10")["ok"] and api.run_pipeline(42)["ok"]
    monkeypatch.setattr(api, "bao_cao_muc_tieu", goc_fn)
    cfg = _cfg(api)
    cfg["muc_tieu"].pop("truoc")
    import cau_hinh_ws
    cau_hinh_ws.ghi_cau_hinh(api.db_path, cfg)
    page.locator('.nav-item[data-tab="pipeline"]').click()
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_function("/Dành chỗ cho/.test(document.getElementById('mt1KetQua').textContent)")
    chu = page.locator("#mt1KetQua > p").first.inner_text()
    assert chu.startswith("Mục tiêu: Dành chỗ cho khối 10") and "CLB được chọn nhiều nhất" in chu
    assert "được giúp" not in chu and "nhường chỗ" not in chu and chu.endswith(".")
    assert not loi, loi


def test_dong_ket_qua_an_khi_lan_xep_khong_theo_the_hien_tai(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    assert api.chon_muc_tieu("co_hoi")["ok"]                                # đổi thẻ SAU lần xếp
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#tomTatKetQua", state="visible")
    page.wait_for_timeout(300)
    assert page.locator("#mt1KetQua").is_hidden()
    assert not loi, loi


# ----- 5, 6. Chữ, hình dáng, bàn phím -----

def test_chu_thuong_khong_lo_ten_noi_bo_va_dung_hai_ngon_ngu(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    _vao(page)
    page.locator("#ux1aMtDanhCho").click()
    _chon_nhom(page)
    page.wait_for_function("document.getElementById('ux1aMtHieuQua').textContent.trim().length > 0")
    chu = page.locator("#ux1aMtBlock").inner_text()
    assert not any(c in chu for c in CAM), [c for c in CAM if c in chu]
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.getElementById('ux1aMtCauHoi').textContent.startsWith('When a club')")
    en = page.locator("#ux1aMtBlock").inner_text()
    assert not any(c in en for c in CAM)
    assert [t.strip() for t in page.locator("#ux1aMtLuoi .ux1a-the-tt").all_inner_texts()] == \
        ["By ability", "Equal chance", "Seats kept for a group"]
    assert not loi, loi


@pytest.mark.parametrize("rong", [1280, 1024])
def test_hinh_dang_co_chu_cham_tuong_phan_va_khong_tran_ngang(mo_trang, rong):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.run_pipeline(42)["ok"]
    page.set_viewport_size({"width": rong, "height": 900})
    _vao(page)
    page.locator("#ux1aMtDanhCho").click()
    _chon_nhom(page)
    page.wait_for_function("document.getElementById('ux1aMtHieuQua').textContent.trim().length > 0")
    do = page.evaluate("""() => {
      const lum = (c) => { const m = c.match(/[\\d.]+/g).map(Number); const f = (v) => { v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
      const nen = (e) => { for (let x = e; x; x = x.parentElement) { const b = getComputedStyle(x).backgroundColor;
        if (b && !/rgba\\(.*,\\s*0\\)|transparent/.test(b)) return b; } return 'rgb(255, 255, 255)'; };
      const ra = { chuNho: [], tapNho: [], tuongPhan: [], tran: document.documentElement.scrollWidth > innerWidth + 1 };
      document.querySelectorAll('#ux1aMtBlock *').forEach((e) => {
        if (!e.childNodes.length || ![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
        const s = getComputedStyle(e); if (s.display === 'none' || e.offsetParent === null) return;
        if (parseFloat(s.fontSize) < 14) ra.chuNho.push(e.id || e.className);
        const a = lum(s.color), b = lum(nen(e)); const cr = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        if (cr < 4.5) ra.tuongPhan.push([e.id || e.className, cr.toFixed(2)]);
      });
      document.querySelectorAll('#ux1aMtBlock button, #ux1aMtBlock summary').forEach((e) => {
        if (e.offsetParent !== null && e.getBoundingClientRect().height < 36) ra.tapNho.push(e.id || e.textContent);
      });
      return ra; }""")
    assert do == {"chuNho": [], "tapNho": [], "tuongPhan": [], "tran": False}, do
    assert not loi, loi


def test_ban_phim_tab_den_the_enter_chon_vong_tieu_diem_3px(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    _vao(page)
    page.locator("#ux1aMtNangLuc").focus()
    page.keyboard.press("Tab")                                              # Tab tới thẻ kế: "Cơ hội như nhau"
    assert page.evaluate("document.activeElement.id") == "ux1aMtCoHoi"
    assert page.locator("#ux1aMtCoHoi").evaluate("e => getComputedStyle(e).outlineWidth") == "3px"
    page.keyboard.press("Enter")                                            # Enter chọn
    _cho_chon(page, "CoHoi")
    assert _luat(api)["priority"] == "tier" and _cfg(api)["muc_tieu"]["id"] == "co_hoi"
    page.keyboard.press("Tab")                                              # tới thẻ thứ ba
    assert page.evaluate("document.activeElement.id") == "ux1aMtDanhCho"
    assert page.locator("#ux1aMtDanhCho").evaluate("e => getComputedStyle(e).outlineWidth") == "3px"
    assert not loi, loi


# ----- 7. Vai -----

def test_giao_vien_khong_thay_cau_hoi_muc_tieu_va_khong_goi_ham(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _nap(api)
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"] and api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    page.reload()
    page.wait_for_selector("body[data-vai='giao_vien']")
    assert page.locator("#ux1aCaiDat").is_hidden() and page.locator("#mt1KetQua").is_hidden()
    assert page.locator("#ux1aMtCauHoi").is_hidden()
    assert not loi, loi
