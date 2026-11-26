"""GT3-L1: màn đăng nhập + hộp Tài khoản trong giao diện thật (Chromium qua `browser_host`). Dữ liệu MÔ PHỎNG."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MK = "matkhau-gia-1"
MK2 = "matkhau-gia-2"


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True)
    page.set_default_timeout(8000)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone", state="attached")
    page.wait_for_selector("#tkNutMoHop")
    try:
        yield page, api, url, loi
    finally:
        br.close()
        pw.stop()


def test_chua_co_tai_khoan_khong_man_dang_nhap_va_tao_quan_tri_dau_tien(trang):
    page, api, url, loi = trang
    assert page.locator("#tkOverlay").count() == 0 or page.locator("#tkOverlay").is_hidden()
    assert page.locator("#tkNutDangXuat").count() == 0
    page.click("#tkNutMoHop")
    page.fill("#tkTaoTen", "quantri")
    page.fill("#tkTaoMk", MK)
    page.fill("#tkTaoMk2", MK)                       # GT4-L3: ô nhập lại mật khẩu
    page.click("#tkNutTao")
    page.wait_for_selector("#tkHuyHieu")
    assert "quantri" in page.inner_text("#tkHuyHieu")
    assert api.get_phien_dang_nhap()["data"]["vai"] == "quan_tri"
    assert not loi, loi


def test_dang_xuat_hien_man_dang_nhap_sai_roi_dung(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    page.reload()
    page.wait_for_selector("#tkNutDangXuat")
    page.click("#tkNutDangXuat")
    page.wait_for_selector("#tkNutDangNhap")
    page.fill("#tkTen", "quantri")
    page.fill("#tkMatKhau", "sai-sai-sai")
    page.click("#tkNutDangNhap")
    page.wait_for_selector("#tkTin.is-error")
    assert page.input_value("#tkMatKhau") == ""            # ô mật khẩu bị xoá sau khi gửi
    page.fill("#tkMatKhau", MK)
    page.click("#tkNutDangNhap")
    page.wait_for_selector("#tkNutDangNhap", state="detached")
    page.wait_for_selector("#tkNutDangXuat")
    assert not loi, loi


def test_co_tai_khoan_ma_chua_dang_nhap_thi_man_dang_nhap_chan_giao_dien(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    api.dang_xuat()
    page.reload()
    page.wait_for_selector("#tkNutDangNhap")
    assert page.locator("#tkOverlay").is_visible()


def test_het_phien_sau_15_phut_thi_hien_lai_man_dang_nhap(trang):
    page, api, url, loi = trang
    t = {"v": 5000.0}
    api._dong_ho = lambda: t["v"]
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    page.reload()
    page.wait_for_selector("#tkNutDangXuat")
    t["v"] += 16 * 60
    page.reload()
    page.wait_for_selector("#tkNutDangNhap")


def test_quan_tri_tao_giao_vien_va_giao_vien_chi_thay_doi_mat_khau(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    page.reload()
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormTao")
    page.fill("#tkTaoTen", "co_lan")
    page.fill("#tkTaoMk", MK2)
    page.fill("#tkTaoMk2", MK2)                      # GT4-L3: ô nhập lại mật khẩu
    page.select_option("#tkTaoVai", "giao_vien")
    page.click("#tkNutTao")
    page.wait_for_selector('[data-xoa="co_lan"]')
    page.click("#tkNutDong")
    api.dang_xuat()
    api.dang_nhap("co_lan", MK2)
    page.reload()
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector("#tkFormDoiMk")
    assert page.locator("#tkFormTao").count() == 0
    assert page.locator("#tkDanhSach").count() == 0
    assert not loi, loi


def test_nut_xoa_can_bam_hai_lan(trang):
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    api.tao_tai_khoan("gv1", MK2, "giao_vien")
    page.reload()
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.wait_for_selector('[data-xoa="gv1"]')
    page.click('[data-xoa="gv1"]')
    assert api.liet_ke_tai_khoan()["data"] and len(api.liet_ke_tai_khoan()["data"]) == 2
    page.click('[data-xoa="gv1"]')
    page.wait_for_function("window.pywebview.api.liet_ke_tai_khoan().then(r => r.data.length === 1)")
    assert not loi, loi


def test_nhat_ky_thao_tac_hien_trong_hop_tai_khoan_cua_quan_tri(trang):
    page, api, url, loi = trang
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.create_or_update_club("A", "Câu lạc bộ Đẹp", 5, 0, "")["ok"]
    page.goto(url)
    page.wait_for_selector("#tkNutMoHop")
    page.click("#tkNutMoHop")
    page.click("#tkTabNhatKy")                      # GT4-L6: nhật ký nằm ở thẻ riêng của hộp
    page.wait_for_selector("#tkNkTable")
    chu = page.inner_text("#tkNkTable")
    assert "Tạo hoặc sửa câu lạc bộ" in chu and "Tạo tài khoản" in chu     # GT4-L6: nhãn tiếng Việt, không tên hàm
    assert "Câu lạc bộ Đẹp" in chu
    page.select_option("#tkNkHanhDong", "create_or_update_club")           # GT4-L6: ô chọn thay cho ô gõ tay
    page.click("#tkNkLoc")
    page.wait_for_function("!document.querySelector('#tkNkTable').innerText.includes('Tạo tài khoản')")
    assert "1 dòng" in page.inner_text("#tkNkTrang")
    assert page.is_disabled("#tkNkTruoc") and page.is_disabled("#tkNkSau")
    assert not loi, loi


def test_dang_nhap_xong_nap_lai_the_dang_mo_workspace_va_bo_thong_bao_cu(trang):
    """Thẻ đang mở sau lớp phủ đăng nhập (Quản lý) phải được nạp lại sau khi đăng nhập, không chỉ thẻ Xếp CLB;
    trạng thái workspace hỏi lại; thông báo «Cần đăng nhập» của các lời gọi trước khi đăng nhập được gỡ."""
    import base64
    page, api, url, loi = trang
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    with open(os.path.join(GOC, "du_lieu_test", "SO_NHAP_MAU_DAY_DU.xlsx"), "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    api.dang_xuat()
    page.reload()
    page.wait_for_selector("#tkNutDangNhap")
    page.evaluate("doiThe('admin')")                       # thẻ Quản lý đang mở phía sau lớp phủ
    page.wait_for_timeout(500)
    goi = []
    page.on("request", lambda r: goi.append(r.url.split("/__api__/")[-1].split("?")[0]) if "/__api__/" in r.url else None)
    page.fill("#tkTen", "quantri")
    page.fill("#tkMatKhau", MK)
    page.click("#tkNutDangNhap")
    page.wait_for_selector("#tkNutDangXuat")
    page.wait_for_function("document.getElementById('adminLopLoc').options.length > 1"
                           " && document.querySelectorAll('#view-admin tbody tr').length > 0", timeout=5000)
    assert "get_workspace_state" in goi, goi
    con = [x for x in page.locator("#toastStack .toast").all_inner_texts() if "Cần đăng nhập" in x]
    assert con == [], con
    assert not loi, loi



def _hai_workspace_ban_sao_trong_moi_hon(tmp_path):
    """Hai workspace: «Trường học» có dữ liệu; «Bản sao trống» (nhân bản kèm tài khoản, rồi xoá dữ liệu) SỬA GẦN NHẤT.
    Trả (slug_a, api) với api dựng đúng như main.khoi_dong_workspace (CSDL sửa gần nhất, da_chon=False)."""
    import base64
    import time

    import workspace
    from api import PipelineAPI
    from rbda_priority_pipeline import init_db

    goc = str(tmp_path)
    a = workspace.tao(goc, "Trường học", None)
    pa = workspace.duong_dan_db(goc, a)
    init_db(pa)
    api_a = PipelineAPI(pa, thu_muc_goc_ws=goc, ws_da_chon=True)
    api_a.tao_tai_khoan("quantri", MK, "quan_tri")
    api_a.tao_tai_khoan("giaovien", MK2, "giao_vien")
    with open(os.path.join(GOC, "du_lieu_test", "SO_NHAP_MAU_DAY_DU.xlsx"), "rb") as f:
        assert api_a.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    time.sleep(1.1)                                       # bản sao phải là workspace SỬA GẦN NHẤT
    b = workspace.nhan_ban(goc, a, "Bản sao trống", True)  # chép cả tài khoản
    api_b = PipelineAPI(workspace.duong_dan_db(goc, b), thu_muc_goc_ws=goc, ws_da_chon=True)
    assert api_b.dang_nhap("quantri", MK)["ok"]
    assert api_b.reset_data("tat_ca", "XOA")["ok"]
    api_b.dang_xuat()
    ds = workspace.danh_sach(goc)
    db0 = max(ds, key=lambda w: w["modified"])["path"]
    assert db0 == workspace.duong_dan_db(goc, b)
    return a, PipelineAPI(db0, thu_muc_goc_ws=goc, ws_da_chon=False)


def _mo_trang_dang_nhap(pw, api, ten, mk):
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(locale="vi-VN", bypass_csp=True)
    page.set_default_timeout(8000)
    page.loi = []
    page.on("pageerror", lambda e: page.loi.append(str(e)))
    page.goto(url)

    def dang_nhap():
        page.wait_for_selector("#tkNutDangNhap")
        page.fill("#tkTen", ten)
        page.fill("#tkMatKhau", mk)
        page.click("#tkNutDangNhap")
        page.wait_for_selector("#tkNutDangXuat")

    page.dang_nhap = dang_nhap
    dang_nhap()
    return br, page


def test_nhieu_workspace_dang_nhap_xong_hien_man_chon_khong_lam_viec_nham_workspace_trong(tmp_path):
    """Lỗi khẩn (Truong, 26/11, ảnh): workspace SỬA GẦN NHẤT có tài khoản nhưng trống. Trước: get_workspace_state bị
    từ chối lúc chưa đăng nhập -> màn chọn không bao giờ hiện, tên workspace không hiện -> «Chưa có dữ liệu» trong
    workspace sai. Nay: đăng nhập xong màn chọn hiện; chọn workspace có dữ liệu -> đăng nhập lại (tài khoản theo từng
    workspace) -> thấy đủ dữ liệu."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    a, api = _hai_workspace_ban_sao_trong_moi_hon(tmp_path)
    with sync_playwright() as pw:
        br, page = _mo_trang_dang_nhap(pw, api, "quantri", MK)
        page.wait_for_selector("#wsOverlay", state="visible")
        page.click('#wsOverlay [data-slug="%s"][data-hanh-dong="mo"]' % a)
        page.dang_nhap()                                       # phiên gắn với CSDL: workspace khác thì đăng nhập lại
        page.wait_for_function("document.getElementById('statStudents').textContent === '120'")
        assert page.locator("#wsOverlay").is_hidden()
        assert page.locator("#viecTiepTheo").get_attribute("data-trang-thai") != "nap_so"
        assert not page.loi, page.loi
        br.close()


def test_nhieu_workspace_giao_vien_khong_bi_khoa_trong_man_chon(tmp_path):
    """Giáo viên không mở được workspace (open_workspace là việc của quản trị): màn chọn không đóng được không được bật
    ra với giáo viên; tên workspace đang mở vẫn hiện để biết mình đang ở đâu."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    _a, api = _hai_workspace_ban_sao_trong_moi_hon(tmp_path)
    with sync_playwright() as pw:
        br, page = _mo_trang_dang_nhap(pw, api, "giaovien", MK2)
        page.wait_for_function("document.body.dataset.vai === 'giao_vien'")
        page.wait_for_timeout(1000)
        assert page.locator("#wsOverlay").is_hidden()
        assert not page.loi, page.loi
        br.close()
