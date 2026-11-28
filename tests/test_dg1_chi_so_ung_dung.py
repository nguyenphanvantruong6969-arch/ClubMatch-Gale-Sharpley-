"""DG1-L4: khối «Chỉ số phân bổ» chỉ-đọc — hàm thuần `tieu_chi.chi_so_phan_bo`, API `get_chi_so_phan_bo`,
mục «CHỈ SỐ PHÂN BỔ» trong trang Thống kê của sổ Excel kết quả, và khối hiện trên màn hình kết quả (Chromium, một test)."""

import os

import openpyxl
import pytest

import tieu_chi

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ca tay: 6 em một buổi. A (chỉ tiêu 2, dự trữ 1), B (1, 0), C (1, 0, tự do).
ROWS = [
    ("s1", "b", "A", 1), ("s2", "b", "A", 2), ("s3", "b", "B", 1),
    ("s4", "b", None, None), ("s5", "b", "C", 4), ("s6", "b", None, None),
]
CLUBS = {
    "A": {"capacity": 2, "reserve_capacity": 1, "tu_do": False},
    "B": {"capacity": 1, "reserve_capacity": 0, "tu_do": False},
    "C": {"capacity": 99, "reserve_capacity": 0, "tu_do": True},
    "D": {"capacity": 4, "reserve_capacity": 0, "tu_do": False},
}


def test_ham_thuan_ca_tay():
    r = tieu_chi.chi_so_phan_bo(ROWS, CLUBS, {("s2", "b"): "reserve", ("s1", "b"): "general"})
    t = r["tong"]
    assert (t["n"], t["da_xep"], t["chua_xep"]) == (6, 4, 2)
    assert t["pct_nv1"] == 33.3 and t["pct_top3"] == 50.0       # s1, s3 ở NV1; s1, s2, s3 trong top 3 — mẫu số MỌI em
    assert r["pct_nv1_da_xep"] == 50.0 and r["pct_top3_da_xep"] == 75.0   # mẫu số: em được xếp
    ld = r["lap_day"]
    # CLB Tự do (C) không tính chỗ: chỉ A, B, D. Đã xếp trong A, B = 3 / (2+1+4) chỗ.
    assert ld["chi_tieu"] == 7 and ld["da_xep"] == 3 and ld["pct"] == 42.9
    assert ld["n_clb"] == 3 and ld["n_clb_day"] == 2 and ld["n_clb_duoi_50"] == 1   # A, B đầy; D 0/4 < 50 %
    assert r["du_tru"] == {"cung_cap": 1, "da_dung": 1}


def test_ham_thuan_khong_co_ket_qua():
    r = tieu_chi.chi_so_phan_bo([], CLUBS, {})
    assert r["tong"]["n"] == 0 and r["tong"]["pct_nv1"] is None
    assert r["pct_nv1_da_xep"] is None and r["lap_day"]["pct"] == 0.0


def _chay(api):
    api.create_or_update_club("clb_day", "CLB Đầy", 2, 0, "")
    api.create_or_update_club("clb_nua", "CLB Nửa", 4, 0, "")
    api.create_or_update_club("clb_dt", "CLB Dự trữ", 2, 1, "chinh_sach")

    def them(sid, nhom, clb, diem):
        api.create_student_if_missing(sid, "Em " + sid)
        if nhom:
            api.set_student_reserve_group(sid, nhom)
        api.submit_test_selection(sid, [clb])
        api.submit_preferences(sid, [clb])
        api.submit_club_scores(clb, [{"student_id": sid, "score": diem}])

    them("HS01", "", "clb_day", 9.0)
    them("HS02", "", "clb_day", 8.0)
    them("HS03", "", "clb_nua", 9.0)
    them("HS04", "", "clb_nua", 8.0)
    them("HS05", "", "clb_dt", 9.0)
    them("HS06", "chinh_sach", "clb_dt", 5.0)
    assert api.run_pipeline(seed=42)["ok"]
    return api


def test_api_chua_chay_khong_loi(api):
    r = api.get_chi_so_phan_bo()
    assert r["ok"] and r["data"]["tong"]["n"] == 0


def test_api_khop_ket_qua_that(api):
    _chay(api)
    r = api.get_chi_so_phan_bo()
    assert r["ok"] and r["errors"] == []
    d = r["data"]
    assert d["tong"]["n"] == 6 and d["tong"]["da_xep"] == 6 and d["tong"]["pct_nv1"] == 100.0
    assert d["lap_day"]["chi_tieu"] == 8 and d["lap_day"]["da_xep"] == 6 and d["lap_day"]["pct"] == 75.0
    assert d["lap_day"]["n_clb_day"] == 2 and d["lap_day"]["n_clb_duoi_50"] == 0
    assert d["du_tru"] == {"cung_cap": 1, "da_dung": 1}       # HS06 vào bằng suất dự trữ
    # khớp bảng NV hiện có của phần mềm
    nv = api.get_phan_bo_nguyen_vong()["data"]
    assert nv["tong_da_xep"] == d["tong"]["da_xep"]


def test_api_chi_doc_khong_doi_ket_qua(api):
    _chay(api)
    truoc = api.get_match_results()["data"]
    api.get_chi_so_phan_bo()
    assert api.get_match_results()["data"] == truoc


def test_excel_co_muc_chi_so_trong_trang_thong_ke(api):
    _chay(api)
    path = api.export_ket_qua("")["data"]["path"]
    ws = openpyxl.load_workbook(path)["Thống kê"]
    cac = [str(c.value) for row in ws.iter_rows() for c in row if c.value is not None]
    assert any("CHỈ SỐ PHÂN BỔ" in x for x in cac)
    i = next(k for k, x in enumerate(cac) if "CHỈ SỐ PHÂN BỔ" in x)
    sau = " | ".join(cac[i:i + 60])
    assert "100" in sau and "75" in sau          # % NV1 và % lấp đầy của ca trên


def test_giao_dien_khoi_chi_so_hien_tren_man_ket_qua(api):
    pytest.importorskip("playwright", reason="chưa cài playwright")
    from playwright.sync_api import sync_playwright

    import browser_host
    from _trinh_duyet import CHROMIUM
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    _chay(api)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.locator('[data-tab="others"]').click()
        page.wait_for_selector("#chiSoPhanBo:not([hidden])")
        chu = page.inner_text("#chiSoPhanBo")
        # Lỗi đọc: khối hiện câu lỗi (không lặng lẽ ẩn); có chữ độc trong lỗi thì không chạy thành mã.
        # Đổi ngôn ngữ giữa chừng: khối vẽ lại bằng tiếng Anh (không còn chữ có dấu tiếng Việt, không còn {tham_số}).
        page.evaluate("window.I18N.setLang('en')")
        page.wait_for_function("document.getElementById('chiSoTieuDe').textContent === 'Allocation metrics'")
        chu_en = page.inner_text("#chiSoPhanBo")
        page.evaluate("window.I18N.setLang('vi')")
        page.wait_for_function("document.getElementById('chiSoTieuDe').textContent === 'Chỉ số phân bổ'")
        page.route("**/__api__/get_chi_so_phan_bo", lambda route: route.fulfill(
            status=200, content_type="application/json",
            body='{"ok": false, "data": null, "errors": [{"code": "dg1_error_reading_chi_so", "params": {}}]}'))
        page.evaluate("loadChiSoPhanBo()")
        page.wait_for_function("document.getElementById('chiSoMauSo').textContent.includes('chỉ số phân bổ')")
        sau_loi = page.inner_text("#chiSoPhanBo")
        br.close()
    assert not loi
    assert "Got first choice" in chu_en and "{" not in chu_en and "mọi suất" not in chu_en
    assert "Không tải được" in sau_loi
    assert "100" in chu and "75" in chu          # % NV1 (mọi em) và % lấp đầy
    assert "1 / 1" in chu or "1/1" in chu        # suất dự trữ đã dùng / cung cấp
