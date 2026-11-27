"""DKL-L3 (Playwright + Chromium): màn giáo viên so với bản mẫu v8 — sửa / xoá CLB của mình, báo lỗi từng bước, phòng trống theo buổi.
Dữ liệu MÔ PHỎNG."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ok(r):
    assert r["ok"], r
    return r["data"]


@pytest.fixture(scope="module")
def cong(tmp_path_factory):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api = PipelineAPI(str(tmp_path_factory.mktemp("dklgv") / "app.db"))
    _ok(api.dk_khoi_tao("matkhau", "TRU1", ["T2", "T3"], [9, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    _ok(api.dk_phong_luu(qt, "P1", 40))
    _ok(api.dk_phong_luu(qt, "P2", 30))
    pin = {x["ten"]: x["pin"] for x in _ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))["da_tao"]}
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
        pg = br.new_page(bypass_csp=True, viewport={"width": 1100, "height": 900})
        pg.loi = []
        pg.on("pageerror", lambda e: pg.loi.append(str(e)))
        pg.api, pg.qt, pg.pin, pg.dia_chi = api, qt, pin, url
        yield pg
        br.close()


def _vao(pg, ten):
    pg.goto(pg.dia_chi)
    pg.get_by_role("button", name="Giáo viên", exact=True).click()
    pg.fill("input[name=ten]", ten)
    pg.fill("input[name=ma]", pg.pin[ten])
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Bước 1/3")


def test_1_bao_loi_tung_buoc_bang_tieng_viet(cong):
    pg = cong
    _vao(pg, "Cô An")
    pg.locator("select").nth(1).select_option("Giới hạn")
    pg.fill("input[type=number]", "")
    pg.get_by_role("button", name="Tiếp theo").click()
    assert "Chỉ tiêu là số nguyên từ 1." in pg.locator("#dkThongBao").inner_text()
    pg.fill("input[type=number]", "10")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.fill("input[type=number] >> nth=0", "12")
    pg.fill("input[type=number] >> nth=1", "9")
    pg.get_by_role("button", name="Tiếp theo").click()
    assert "Chọn khối được tham gia." in pg.locator("#dkThongBao").inner_text()
    pg.fill("input[type=number] >> nth=0", "9")
    pg.fill("input[type=number] >> nth=1", "12")
    pg.get_by_role("button", name="Quay lại").click()
    pg.locator("select").nth(1).select_option("Tuyển chọn")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.fill("input[type=number] >> nth=2", "6")
    pg.fill("label:has-text('Đường dẫn bài thi') input", "http://khong-https")
    pg.get_by_role("button", name="Tiếp theo").click()
    assert "bắt đầu bằng https://" in pg.locator("#dkThongBao").inner_text()
    pg.fill("label:has-text('Đường dẫn bài thi') input", "https://forms.example/robot")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.get_by_role("button", name="Gửi duyệt").click()
    assert "Nhập tên CLB." in pg.locator("#dkThongBao").inner_text()
    pg.fill("label:has-text('Tên CLB') input", "Robot")
    pg.get_by_role("button", name="Gửi duyệt").click()
    pg.wait_for_selector("li:has-text('Robot'):has-text('Chờ duyệt')")


def test_2_phong_chi_hien_phong_trong_buoi_va_sua_clb(cong):
    pg = cong
    _vao(pg, "Cô Bê")
    # Robot (Cô An) đang giữ phòng đầu tiên ở buổi T2 -> Cô Bê chỉ thấy phòng còn lại
    opts = pg.locator("select").nth(2).locator("option").all_inner_texts()
    assert opts == ["P2 (30 chỗ)"], opts
    pg.locator("select").nth(1).select_option("Giới hạn")
    pg.fill("input[type=number]", "8")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.fill("label:has-text('Tên CLB') input", "Cờ vua")
    pg.get_by_role("button", name="Gửi duyệt").click()
    pg.wait_for_selector("li:has-text('Cờ vua'):has-text('Chờ duyệt')")
    # sửa: đổi tên rồi lưu
    pg.get_by_role("button", name="Sửa Cờ vua").click()
    pg.wait_for_selector("text=Sửa CLB «Cờ vua»")
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.get_by_role("button", name="Tiếp theo").click()
    pg.fill("label:has-text('Tên CLB') input", "Cờ vua nâng cao")
    pg.get_by_role("button", name="Lưu thay đổi").click()
    pg.wait_for_selector("li:has-text('Cờ vua nâng cao')")
    ds = _ok(pg.api.dk_dang_nhap("giao_vien", "Cô Bê", pg.pin["Cô Bê"]))["token"]
    assert [c["ten"] for c in _ok(pg.api.dk_clb_danh_sach(ds))] == ["Cờ vua nâng cao"]
    # xoá: biến mất khỏi danh sách và khỏi dữ liệu
    pg.once("dialog", lambda d: d.accept())      # VG2-L3: hỏi xác nhận
    pg.get_by_role("button", name="Xoá Cờ vua nâng cao").click()
    pg.wait_for_function("!document.body.innerText.includes('Cờ vua nâng cao')")
    assert _ok(pg.api.dk_clb_danh_sach(ds)) == []


def test_3_clb_da_duyet_khong_con_nut_sua_xoa_va_khong_xoa_duoc_qua_api(cong):
    pg, api, qt = cong, cong.api, cong.qt
    ds = _ok(api.dk_dang_nhap("giao_vien", "Cô An", pg.pin["Cô An"]))["token"]
    cid = _ok(api.dk_clb_danh_sach(ds))[0]["clb_id"]
    _ok(api.dk_clb_duyet(qt, cid, "duyet", 10, None))
    _vao(pg, "Cô An")
    assert pg.get_by_role("button", name="Xoá Robot").count() == 0
    r = api.dk_clb_xoa(ds, cid)
    assert not r["ok"] and r["errors"][0]["code"] == "dk_clb_khong_sua_duoc"
    # giáo viên khác không xoá được CLB của người khác
    gb = _ok(api.dk_dang_nhap("giao_vien", "Cô Bê", pg.pin["Cô Bê"]))["token"]
    assert not api.dk_clb_xoa(gb, cid)["ok"]
    assert not pg.loi, pg.loi
