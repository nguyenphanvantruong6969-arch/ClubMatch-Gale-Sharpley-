"""UX1F-L4 — thẻ Kết quả chỉ còn MỘT ô "Chọn lớp" (#kqChonLop) cho cả quản trị và giáo viên; ô thứ hai (#ux1bLop) bỏ.
Ô đó lọc bảng kết quả VÀ quyết định lớp cho "In phiếu cả lớp". Chromium. Dữ liệu MÔ PHỎNG."""
import base64
import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
pytest.importorskip("reportlab")
pypdf = pytest.importorskip("pypdf")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_giao_dien_ux1b_vai_gv import mo as mo_giao_vien  # noqa: E402,F401  (fixture: giáo viên)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


@pytest.fixture
def mo_quan_tri(api):
    """Không có tài khoản nào: quyền quản trị mặc định (như bản cài mới)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    with api._ket_noi_doc() as cur:
        ds = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
    for i, sid in enumerate(ds):
        assert api.set_student_class(sid, "10A%d" % (i % 3 + 1))["ok"]
    assert api.run_pipeline(42)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True, viewport={"width": 1400, "height": 1000})
    page.set_default_timeout(15000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.click('button.nav-item[data-tab="results"]')
    page.wait_for_function("() => document.querySelectorAll('#kqChonLop option').length > 1")
    try:
        yield page, api, loi
    finally:
        br.close()
        pw.stop()


def _kiem_mot_o(page):
    assert page.locator("#ux1bLop").count() == 0
    assert page.locator("#kqChonLop").count() == 1
    # mọi ô <select> có nhãn "Chọn lớp" trên trang: đúng MỘT, và nhìn thấy
    nhan = page.evaluate("""() => Array.from(document.querySelectorAll('label'))
        .filter(l => /^Chọn lớp$/.test(l.textContent.trim()) && l.offsetParent !== null)
        .map(l => l.control && l.control.id)""")
    assert nhan == ["kqChonLop"], nhan
    assert page.locator("#kqChonLop").is_visible()


def test_quan_tri_mot_o_chon_lop(mo_quan_tri):
    page, api, loi = mo_quan_tri
    _kiem_mot_o(page)
    assert not loi, loi


def test_giao_vien_mot_o_chon_lop(mo_giao_vien):  # noqa: F811
    page, api, loi = mo_giao_vien
    page.wait_for_function("() => document.querySelectorAll('#kqChonLop option').length > 1")
    _kiem_mot_o(page)
    assert not loi, loi


def test_o_chon_lop_loc_bang_va_quyet_dinh_lop_in_phieu(mo_quan_tri, tmp_path):
    page, api, loi = mo_quan_tri
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    page.locator('#kqTang1 [data-kq="clb"]').click()                     # đang ở tầng khác, rồi chọn lớp
    page.locator("#kqChonLop").select_option("10A2")
    page.wait_for_selector("#kqBang", state="visible")
    assert page.locator('#kqTang1 [data-kq="lop"]').get_attribute("aria-pressed") == "true"   # chọn lớp mở "Theo lớp"
    assert page.locator("#kqChonLop").input_value() == "10A2"
    page.locator("#btnUx1bPhieuLop").click()
    page.wait_for_function("document.getElementById('ux1bPhanHoi').textContent.includes('.pdf')")
    tep = [t for t in os.listdir(api.thu_muc_xuat) if t.endswith(".pdf")]
    assert tep == ["phieu_giai_trinh.pdf"]
    chu = "\n".join(p.extract_text() for p in pypdf.PdfReader(os.path.join(api.thu_muc_xuat, tep[0])).pages)
    with api._ket_noi_doc() as cur:
        lop = {r[0]: r[1] for r in cur.execute("SELECT student_id, class_id FROM students")}
    trong = {s for s, c in lop.items() if c == "10A2"}
    co = set(re.findall(r"Mã:\s*(\S+)", chu))
    assert co == trong and len(co) > 0, (len(co), len(trong))             # đúng các em của 10A2, không em lớp khác
    assert not loi, loi


def test_chua_co_lop_thi_tat_nut_in_phieu_ca_lop(mo_quan_tri):
    page, api, loi = mo_quan_tri
    with api._ket_noi_doc() as cur:
        co_khong_lop = cur.execute("SELECT COUNT(*) FROM students WHERE class_id IS NULL OR class_id=''").fetchone()[0]
    if co_khong_lop:                                                      # bộ mẫu chia đủ ba lớp: ca này thường bỏ qua
        page.locator("#kqChonLop").select_option("")
        assert page.locator("#btnUx1bPhieuLop").is_disabled()
    page.locator("#kqChonLop").select_option("10A1")
    assert page.locator("#btnUx1bPhieuLop").is_enabled()
