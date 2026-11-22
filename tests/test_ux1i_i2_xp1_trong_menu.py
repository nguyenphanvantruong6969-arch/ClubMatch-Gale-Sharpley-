"""UX1I-I2: XP1 (xuất PDF) gộp vào giao diện của A. Dữ liệu MÔ PHỎNG.
(1) MỘT menu "Xuất…" cho quản trị, có cả ba mục PDF; (2) "Lưu PDF" một em ≤ 4 lần bấm kể từ lúc mở thẻ Kết quả;
(3) dòng phiếu ghi loại CLB đặt bằng `dat_loai_clb` của A."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
pytest.importorskip("reportlab")
from playwright.sync_api import sync_playwright  # noqa: E402
from test_gt1_phieu import _dung  # noqa: E402
from test_giao_dien_xp1_luu_pdf_mot_em import _dung_api  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUC = ("btnPdfDsClb", "btnPdfDsLop", "btnPdfPhieuLop")


@pytest.fixture
def mo(api, tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

        def _mo():
            url = browser_host.serve(api, GOC, "index.html", open_browser=False)
            page = br.new_page(bypass_csp=True, viewport={"width": 1400, "height": 1000})
            page.set_default_timeout(15000)
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("#dropZone")
            page.locator('.nav-item[data-tab="others"]').click()
            page.wait_for_selector("#xuatPanel", state="visible")
            return page, loi
        yield _mo
        br.close()


def test_mot_menu_xuat_co_ca_ba_muc_pdf(mo, api):
    _dung(api)
    page, loi = mo()
    assert page.locator("#xuatPdfMenu").count() == 0                  # không còn menu riêng
    page.wait_for_selector("#xuatMenu", state="visible")              # quản trị thấy "Xuất…" cả khi không bật huy chương
    assert page.locator("#xuatMenu > summary").inner_text().strip() == "Xuất tệp khác ▾"
    assert all(page.locator("#" + i).is_hidden() for i in MUC)        # menu đóng
    page.locator("#xuatMenu > summary").click()
    assert all(page.locator("#xuatMenu #" + i).is_visible() for i in MUC)
    assert all(page.locator("#" + i).is_hidden() for i in ("btnXuatLyDo", "btnXuatBienBan"))   # nút chỉ-huy-chương vẫn ẩn
    page.locator("#btnPdfDsClb").click()
    page.wait_for_function("() => !document.getElementById('xuatMenu').open")   # bấm một mục thì menu đóng
    assert not loi, loi


def test_giao_vien_khong_thay_menu_xuat(mo, api):
    _dung(api)
    page, loi = mo()
    page.wait_for_selector("#xuatMenu", state="visible")
    page.evaluate("document.body.dataset.vai = 'giao_vien'")
    assert page.locator("#xuatMenu").is_hidden()
    assert not loi, loi


def test_luu_pdf_mot_em_toi_da_bon_lan_bam_tu_the_ket_qua(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = _dung_api(tmp_path)
    with api._ket_noi_doc() as cur:
        sid = cur.execute("SELECT student_id FROM students ORDER BY student_id").fetchone()[0]
    with sync_playwright() as pw:
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(locale="vi-VN", bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        bam = 0
        page.click('button.nav-item[data-tab="results"]'); bam += 1                       # noqa: E702
        page.fill("#gtTim", sid)                                                          # gõ tìm: tính như một bước
        bam += 1
        page.wait_for_selector("#gtDs .gt-chon")
        page.click("#gtDs .gt-chon"); bam += 1                                            # noqa: E702
        page.wait_for_selector("#gtKetQua .gt-bang")
        page.click("#btnGtPdfMot"); bam += 1                                              # noqa: E702
        page.wait_for_function("document.getElementById('gtXuatPhanHoi').textContent.includes('.pdf')")
        br.close()
    assert bam <= 4 and not loi, (bam, loi)
    assert any(t.endswith(".pdf") and sid in t for t in os.listdir(api.thu_muc_xuat))


def test_dong_phieu_ghi_loai_clb_dat_bang_dat_loai_clb(api):
    _dung(api)                                           # chưa có loại: mọi dòng None
    assert api.dat_loai_clb("A", "GIOI_HAN")["ok"]
    r = api.get_giai_trinh_hoc_sinh("s1")
    loai = {x["club_id"]: x["loai_clb"] for b in r["data"]["buoi"] for x in b["cac_lua_chon"]}
    assert loai["A"] == "GIOI_HAN" and loai["B"] is None
