"""UX1B-L4-B: giáo viên chủ nhiệm đăng nhập vào thẻ "Kết quả & phiếu"; "Xuất theo {cohort_l}" và "Báo cáo tổng hợp"
đạt được trong ≤ 2 lần bấm (thực tế: 1 sau khi vào). Chromium thật qua `browser_host`. Dữ liệu MÔ PHỎNG."""

import base64
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
MK = "matkhau-gia-1"


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    with api._ket_noi_doc() as cur:
        ds = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
    for i, sid in enumerate(ds):                       # sổ mẫu có thể không có lớp: chia ba lớp để chọn
        assert api.set_student_class(sid, "10A%d" % (i % 3 + 1))["ok"]
    assert api.run_pipeline(42)["ok"]
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True, viewport={"width": 1400, "height": 1000})
    page.set_default_timeout(15000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_function("document.body.dataset.vai === 'giao_vien'")
    try:
        yield page, api, loi
    finally:
        br.close()
        pw.stop()


def test_giao_vien_vao_the_ket_qua_va_thay_ca_hai_viec(mo):
    page, api, loi = mo
    assert page.locator('.nav-item[data-tab="results"]').get_attribute("class").count("is-active")
    assert page.locator("#ux1bPanel").is_visible()
    assert page.locator("#btnUx1bXuatLop").inner_text().strip().startswith("Xuất theo")
    assert page.locator("#btnUx1bBaoCao").text_content().strip() == "Báo cáo tổng hợp"      # UX5A-L2: trong nếp
    assert not loi, loi


def test_mot_lan_bam_ra_bao_cao_tong_hop(mo):
    page, api, loi = mo
    page.locator("#ux1bThemTom").click()                                   # UX5A-L2: nếp "Báo cáo và phiếu in", rồi 1 lần bấm
    page.locator("#btnUx1bBaoCao").click()
    page.wait_for_function("document.getElementById('ux1bPhanHoi').textContent.includes('.html')")
    assert "bao_cao_tong_hop" in page.locator("#ux1bPhanHoi").inner_text()
    with api._ket_noi_doc() as cur:
        n = cur.execute("SELECT COUNT(*) FROM nhat_ky_thao_tac WHERE hanh_dong='export_bao_cao_tong_hop' "
                        "AND ket_qua NOT LIKE '%tu_choi%' AND ket_qua <> 'gt3_khong_du_quyen'").fetchone()[0]
    assert n == 1
    assert not loi, loi


def test_mot_lan_bam_ra_xuat_theo_lop_va_chon_lop_mo_bang_lop(mo):
    page, api, loi = mo
    page.locator("#btnUx1bXuatLop").click()                                  # 1 lần bấm
    page.wait_for_function("document.getElementById('ux1bPhanHoi').textContent.length > 0")
    assert "→" in page.locator("#ux1bPhanHoi").inner_text()
    n_opt = page.locator("#kqChonLop option").count()
    assert n_opt >= 1
    page.locator("#kqChonLop").select_option(index=n_opt - 1)
    page.wait_for_selector("#kqBang", state="visible")
    assert page.locator("#kqTang1 [data-kq=\"lop\"]").get_attribute("aria-pressed") == "true"
    assert not loi, loi
