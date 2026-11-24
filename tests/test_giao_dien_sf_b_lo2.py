"""SF-B lô 2: bản hồi quy nhỏ cho ST-B-005, 006, 010, 011 (bản đầy đủ: tests_stress/b/).
Chromium thật qua `browser_host`, MỘT fixture trang dùng chung; sổ nhập MÔ PHỎNG."""

import base64
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        yield page, loi
        br.close()


def test_st_b_006_chi_tieu_thap_phan_bao_loi_o_chi_tieu(trang, api):
    page, loi = trang
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#btnSaveClub", state="attached")
    n_truoc = len(api.list_clubs_admin()["data"])
    if not page.locator("#clubFormId").is_visible():      # UX4-L3: Mã CLB gập sau "Thêm tuỳ chọn"
        page.locator("#clubFormThemTuyChon").click()
    page.fill("#clubFormId", "T4")
    page.fill("#clubFormName", "Thập phân")
    page.fill("#clubFormCapacity", "1.5")
    page.locator("#btnSaveClub").click()
    page.wait_for_function("document.getElementById('clubFormCapacity').getAttribute('aria-invalid') === 'true'")
    chu = page.locator("#clubFormFeedback").inner_text()
    assert "invalid literal" not in chu and "Hãy thử lại" not in chu, chu
    assert len(api.list_clubs_admin()["data"]) == n_truoc
    assert not loi, loi


def test_st_b_011_zip_hong_noi_dung_nguyen_nhan(trang, api, monkeypatch):
    page, loi = trang
    monkeypatch.setattr(api, "import_workspace", lambda *a: {
        "ok": False, "data": None, "errors": [{"code": "ws_du_lieu_sai", "params": {}}]})
    page.evaluate("""() => wsNhapZip({files: [new File([new Uint8Array(4)], 'hong.zip')], value: ''})""")
    page.wait_for_selector("#toastStack .toast, #toastStack > *")
    hien = page.evaluate("document.getElementById('toastStack').innerText")
    assert ("nén" in hien.lower() or "zip" in hien.lower()) and "các ô đã điền" not in hien, hien
    assert not loi, loi


def test_st_b_010_khoi_phuc_xong_bam_lai_khong_chay_hai_lan(tmp_path):
    """Trang phục hồi: sau khi 'Khôi phục' thành công, bấm lại 0,4 s sau không gọi restore_from_backup lần hai."""
    import recovery
    db = tmp_path / "app.db"
    db.write_bytes(b"SQLite format 3\0" + b"x" * 100)
    api = recovery.RecoveryAPI(str(db), "disk image is malformed")
    goi = []
    api.restore_from_backup = lambda: (goi.append(1), {"ok": True, "data": {"detail": {"code": "recovery_ok", "params": {}}}, "errors": []})[1]
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "recovery.html", open_browser=False)
        page = br.new_page(bypass_csp=True)
        page.goto(url)
        page.wait_for_selector("#btnRestoreBackup")
        page.locator("#btnRestoreBackup").click()
        page.wait_for_timeout(400)
        page.locator("#btnRestoreBackup").click(force=True)
        page.wait_for_timeout(800)
        br.close()
    assert len(goi) == 1, goi


def test_st_b_005_tha_hai_tep_noi_tep_bi_bo_qua(trang):
    page, loi = trang
    page.evaluate("""() => themFileVaoHangDoi([new File([new Uint8Array(4)], 'a.xlsx'), new File([new Uint8Array(4)], 'b.xlsx')])""")
    page.wait_for_selector("#importQueue .queue-row")
    txt = page.locator("#importQueue").inner_text()
    assert "b.xlsx" in txt, txt
    assert not loi, loi


def test_st_b_004_nhap_tai_cho_ma_khac_hoa_thuong_hoi_lai(trang, api):
    page, loi = trang
    with api._ket_noi_doc() as cur:
        ma = cur.execute("SELECT student_id FROM students LIMIT 1").fetchone()[0]
    page.locator('.nav-item[data-tab="fallback"]').click()
    if page.locator("#ux5bTaoMoi").get_attribute("open") is None:   # UX5B-L3: ô tạo học sinh mới gập
        page.locator("#ux5bTaoMoi > summary").click()
    page.wait_for_selector("#newStudentId", state="visible")
    bien = ma.swapcase() if ma.swapcase() != ma else ma.lower() + "x"
    page.fill("#newStudentId", bien)
    page.fill("#newStudentName", "Trùng hoa thường")
    lop = page.locator("#newStudentLop")
    if lop.is_visible():
        lop.select_option(index=1)
    page.locator("#btnCreateStudent").click()
    page.wait_for_function("document.getElementById('newStudentId').getAttribute('aria-invalid') === 'true'")
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM students WHERE student_id = ?", (bien,)).fetchone()[0] == 0
    page.locator("#btnCreateStudent").click()           # lần hai: xác nhận, tạo thật
    page.wait_for_timeout(800)
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM students WHERE student_id = ?", (bien,)).fetchone()[0] == 1
    assert not loi, loi
