"""SF-B lô 5: bản hồi quy nhỏ cho ST-B-006 (ô chỉ tiêu), ST-B-007 (xoá kèm dữ liệu, xác nhận lần hai), ST-A-001 (cảnh
báo thiếu dữ liệu dưới thẻ chế độ) và test bàn phím (bản đầy đủ: tests_stress/b/). Chromium thật qua `browser_host`;
sổ nhập MÔ PHỎNG."""

import base64
import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")
SO_150 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DOI_CHE_DO_150HS.xlsx")
CHIA_100 = {"wharton": True, "fa_daa": False}


def _nap(api, duong_dan):
    with open(duong_dan, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]


def _mo_trang(api):
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        yield page, loi
        br.close()


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    _nap(api, SO_120)
    yield from _mo_trang(api)


@pytest.fixture
def trang_ws(tmp_path):
    """Workspace thật (thẻ chế độ chỉ có khi mở workspace), sổ nạp ở chế độ Chia 100."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "ws", {"rules": dict(CHIA_100)})
    api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / "x"),
                      thu_muc_goc_ws=str(goc), ws_da_chon=True)
    _nap(api, SO_150)
    yield from _mo_trang(api)


def _dem(api, sql, *a):
    c = sqlite3.connect(api.db_path)
    try:
        return c.execute(sql, a).fetchone()[0]
    finally:
        c.close()


def _goi(api, ten):
    """Gói API `ten` để đếm số lần gọi (browser_host tra hàm bằng getattr mỗi lần)."""
    goi = []
    goc = getattr(api, ten)
    setattr(api, ten, lambda *a: (goi.append(a), goc(*a))[1])
    return goi


def _vao_clb(page):
    page.locator('.nav-item[data-tab="admin"]').click()
    page.locator("#qlTabClb").click()
    page.wait_for_selector("#clubFormId", state="visible")


# ------------------------------------------------------------------ ST-B-006

@pytest.mark.parametrize("gia_tri, mong, cam", [("1.5", "số nguyên", "lớn hơn 0"), ("99999999999", "quá lớn", "số nguyên")])
def test_st_b_006_chi_tieu_xau_bao_dung_chu_o_o_chi_tieu(trang, api, gia_tri, mong, cam):
    page, loi = trang
    _vao_clb(page)
    n_truoc = len(api.list_clubs_admin()["data"])
    page.fill("#clubFormId", "T4")
    page.fill("#clubFormName", "Thập phân")
    page.evaluate("v => { document.getElementById('clubFormCapacity').value = v; }", gia_tri)
    page.locator("#btnSaveClub").click()
    page.wait_for_function("document.getElementById('clubFormCapacity').getAttribute('aria-invalid') === 'true'")
    chu = page.evaluate("[...document.querySelectorAll('.loi-o')].map(e => e.innerText).join(' ')")
    assert mong in chu and cam not in chu, chu
    assert len(api.list_clubs_admin()["data"]) == n_truoc
    assert not loi, loi


# ------------------------------------------------------------------ ST-B-007

def _clb_co_ket_qua(api):
    return _dem(api, "select club_id from match_results where club_id is not null group by club_id order by count(*) desc limit 1")


def test_st_b_007_xoa_clb_co_du_lieu_hoi_lan_hai_roi_xoa_va_huy_thi_con_nguyen(trang, api):
    page, loi = trang
    assert api.run_pipeline(seed=7)["ok"]
    cid = _clb_co_ket_qua(api)
    n_run = _dem(api, "select count(*) from run_history")
    n_clb = _dem(api, "select count(*) from clubs")
    _vao_clb(page)
    goi = _goi(api, "delete_club")
    nut = page.locator('#adminClubTableBody tr[data-club-id="%s"] .btn-icon-danger' % cid)
    nut.click()
    nut.click()
    page.wait_for_selector("#xoaKemBar", state="visible")
    assert goi == [(cid,)]
    page.locator("#xoaKemBar .btn-ghost").click()                       # huỷ: không gọi gì thêm
    page.wait_for_selector("#xoaKemBar", state="detached")
    page.wait_for_timeout(300)
    assert goi == [(cid,)] and _dem(api, "select count(*) from clubs") == n_clb
    nut.click()
    nut.click()
    page.wait_for_selector("#xoaKemBar", state="visible")
    page.locator("#xoaKemBar .btn-primary").click()                     # xác nhận: gọi lại với True
    page.wait_for_selector('#adminClubTableBody tr[data-club-id="%s"]' % cid, state="detached")
    assert goi[-1] == (cid, True)
    assert _dem(api, "select count(*) from clubs") == n_clb - 1
    assert _dem(api, "select count(*) from run_history") == n_run
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is True
    assert not loi, loi


def test_st_b_007_xoa_hoc_sinh_co_ket_qua_hoi_lan_hai_roi_xoa_va_huy_thi_con_nguyen(trang, api):
    page, loi = trang
    assert api.run_pipeline(seed=7)["ok"]
    sid = _dem(api, "select student_id from match_results where club_id is not null order by student_id limit 1")
    n_run = _dem(api, "select count(*) from run_history")
    n_hs = _dem(api, "select count(*) from students")
    page.locator('.nav-item[data-tab="fallback"]').click()
    page.fill("#studentSearchInput", sid)
    page.locator('.hs-card[data-student-id="%s"]' % sid).first.click()
    page.wait_for_selector("#fallbackWorkArea:not([hidden])")
    goi = _goi(api, "delete_student")

    def xoa():
        page.locator("#menuHocSinh > summary").click()
        nut = page.locator("#btnDeleteStudent")
        nut.click()
        nut.click()
        page.wait_for_selector("#xoaKemBar", state="visible")

    xoa()
    page.locator("#xoaKemBar .btn-ghost").click()
    page.wait_for_selector("#xoaKemBar", state="detached")
    page.wait_for_timeout(300)
    assert goi == [(sid,)] and _dem(api, "select count(*) from students") == n_hs
    xoa()
    page.locator("#xoaKemBar .btn-primary").click()
    page.wait_for_function("document.getElementById('fallbackWorkArea').hidden")
    assert goi[-1] == (sid, True)
    assert _dem(api, "select count(*) from students") == n_hs - 1
    assert _dem(api, "select count(*) from match_results where student_id=?", sid) == 0
    assert _dem(api, "select count(*) from run_history") == n_run
    assert "sao lưu" in page.locator("#toastStack").inner_text().lower()
    assert not loi, loi


# ------------------------------------------------------------------ ST-A-001

def test_st_a_001_canh_bao_thieu_du_lieu_duoi_the_che_do_roi_het_khi_doi_lai(trang_ws):
    page, loi = trang_ws
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#ux1aHuyChuong", state="visible")
    assert page.locator("#ux1aCanhBao").is_hidden()
    page.locator("#ux1aHuyChuong").click()                              # sổ nạp ở Chia 100: thiếu thứ Huy chương cần
    page.wait_for_selector("#ux1aCanhBao", state="visible")
    chu = page.locator("#ux1aCanhBao").inner_text()
    assert "Đã đổi chế độ" in chu and "{" not in chu, chu
    page.locator("#ux1aChia100").click()                                # đổi chế độ thì làm mới
    page.wait_for_selector("#ux1aCanhBao", state="hidden")
    assert not loi, loi
