"""GT1-L2: khung "Tra cứu một học sinh" ở thẻ Kết quả, bằng TRÌNH DUYỆT THẬT (Playwright + Chromium).

Kiểm: tìm theo tên có / không dấu; thẻ đúng CLB + đúng câu cho em được xếp và em bị từ chối; thẻ không chứa tên hay
mã em khác; không lộ mã nội bộ trong chữ hiển thị; FA bật và tắt; báo dữ liệu đã đổi; chưa chạy thì nói rõ.
Dữ liệu MÔ PHỎNG. Máy không có Chromium thì bỏ qua.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _fa import bat_fa, dung_fa_clb  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import tat_wharton  # noqa: E402

CHU_NOI_BO = ("NO_CHOICES", "FULL_", "HIGHER_CHOICE", "UNASSIGNED", "GT1", "Wharton", "gt1_", "undefined", "null")
HS = {"s1": "Nguyễn Văn Ánh", "s2": "Trần Thị Bé"}


def _dung(api, fa):
    if fa:
        bat_fa(api)
        dung_fa_clb(api, A=(1, "GIOI_HAN", None, None, None, "thu_2"),
                    T=(9, "TU_DO", None, None, None, "thu_2"))
        nv = ["A", "T"]
    else:
        tat_wharton(api)
        dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
        nv = ["A", "B"]
    for sid, ten in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, nv)["ok"]
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE students SET class_id = '10A1' WHERE student_id = 's1'")
        cur.execute("UPDATE students SET class_id = '10A2' WHERE student_id = 's2'")


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#gtPanel", state="attached")
        page.click('button.nav-item[data-tab="results"]')
        yield page, loi, api
        br.close()


def _tra(page, go):
    page.fill("#gtTim", go)
    page.wait_for_selector("#gtDs .gt-chon")


@pytest.mark.parametrize("fa", [False, True])
def test_the_hien_dung_cho_em_duoc_xep_va_em_bi_tu_choi(api, mo, fa):
    page, loi, _ = mo
    _dung(api, fa)
    assert api.run_pipeline(seed=3)["ok"]
    with api._ket_noi_doc() as cur:
        xep = dict(cur.execute("SELECT student_id, club_id FROM match_results"))
    thay_bi_tu_choi = False
    for sid, ten in HS.items():
        khac_id = next(s for s in HS if s != sid)
        _tra(page, "nguyen van anh" if sid == "s1" else "tran thi be")      # không dấu
        page.click('#gtDs .gt-chon[data-student-id="%s"]' % sid)
        page.wait_for_selector("#gtKetQua .gt-ten")
        the = page.locator("#gtKetQua").inner_text()
        assert ten in the and sid in the
        assert HS[khac_id] not in the and khac_id not in page.locator("#gtPanel").inner_text()
        assert page.locator("#gtKetQua .gt-duoc-xep").count() == 1
        ten_clb = page.locator("#gtKetQua .gt-duoc-xep td").nth(1).inner_text()
        assert ten_clb == "CLB " + xep[sid]
        for bi in CHU_NOI_BO:
            assert bi not in page.locator("#gtPanel").inner_text(), bi
        if page.locator("#gtKetQua tbody tr").count() > 1:     # có hàng bị từ chối: câu giải thích không rỗng
            thay_bi_tu_choi = True
            hang = page.locator("#gtKetQua tbody tr:not(.gt-duoc-xep)").first
            assert len(hang.locator("td").nth(5).inner_text().strip()) > 10
    assert thay_bi_tu_choi
    assert loi == []


def test_loc_theo_lop_va_chua_chay(api, mo):
    page, loi, _ = mo
    _dung(api, False)
    page.fill("#gtTim", "")
    page.focus("#gtTim")
    page.wait_for_selector("#gtDs .gt-chon")
    page.select_option("#gtLop", "10A2")
    page.wait_for_function("document.querySelectorAll('#gtDs .gt-chon').length === 1")
    assert page.locator("#gtDs .gt-chon").first.get_attribute("data-student-id") == "s2"
    page.click("#gtDs .gt-chon")
    page.wait_for_selector("#gtKetQua")
    assert "Chưa có lần xếp" in page.locator("#gtKetQua").inner_text()
    assert loi == []


def test_bao_du_lieu_da_doi_bang_loi_de_hieu(api, mo):
    page, loi, _ = mo
    _dung(api, False)
    assert api.run_pipeline(seed=3)["ok"]
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET capacity = capacity + 1 WHERE club_id = 'A'")
    _tra(page, "anh")
    page.click('#gtDs .gt-chon[data-student-id="s1"]')
    page.wait_for_selector("#gtKetQua .gt-canh-bao")
    assert "Dữ liệu đã thay đổi" in page.locator("#gtKetQua .gt-canh-bao").inner_text()
    assert loi == []


def test_ten_co_ma_doc_khong_chay_va_doi_ngon_ngu_ve_lai(api, mo):
    page, loi, _ = mo
    _dung(api, False)
    doc = '<img src=x onerror="window.__xss=1">'
    assert api.create_student_if_missing("s3", doc)["ok"]
    assert api.submit_preferences("s3", ["A", "B"])["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    page.evaluate("window.__xss = 0")
    _tra(page, "onerror")
    page.click('#gtDs .gt-chon[data-student-id="s3"]')
    page.wait_for_selector("#gtKetQua .gt-ten")
    assert page.evaluate("window.__xss") == 0
    assert doc in page.locator("#gtKetQua .gt-ten").inner_text()
    page.click("#btnLangToggle")
    page.wait_for_function("document.querySelector('#gtKetQua .gt-lan-chay').innerText.startsWith('Allocation run')")
    chu = page.locator("#gtPanel").inner_text()
    assert "{" not in chu and "undefined" not in chu
    assert "score" in chu.lower() and "cut-off" in chu.lower()
    assert loi == []
