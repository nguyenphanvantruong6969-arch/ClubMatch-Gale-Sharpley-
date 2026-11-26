"""DK9-L2 (Playwright + Chromium): khối «Nạp từ Excel» ở thẻ Cài đặt của cổng đăng ký quản trị: tải tệp mẫu, chọn / thả tệp, xem trước
(số hợp lệ / đã có / dòng lỗi kèm số dòng và lý do), nút «Nạp» duy nhất (vàng) chỉ bật khi có ≥ 1 dòng hợp lệ, phiếu PIN chỉ hiện một lần.
Một fixture trang dùng chung. Dữ liệu MÔ PHỎNG."""
import base64
import os

import openpyxl
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import test_dk9_nap_excel as t9  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_giao_dien_dk8_l2 import TEN_GD, _dung  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok = t9.ok
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.fixture()
def cong(tmp_path):
    """Trả hàm `vao(gd, rong=1200)`: dựng cổng tới giai đoạn `gd`, đăng nhập quản trị, mở thẻ «Cài đặt», trả trang."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        trang = []

        def vao(gd="chuan_bi", rong=1200):
            thu_muc = tmp_path / ("c%d" % len(trang))
            thu_muc.mkdir()
            api, qt = _dung(thu_muc, gd)
            url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)
            pg = br.new_page(bypass_csp=True, viewport={"width": rong, "height": 900}, accept_downloads=True)
            pg.loi = []
            pg.on("pageerror", lambda e: pg.loi.append(str(e)))
            pg.api, pg.qt, pg.thu_muc = api, qt, thu_muc
            pg.goto(url)
            pg.get_by_role("button", name="Quản trị", exact=True).click()
            pg.fill("input[name=ma]", "matkhau")
            pg.get_by_role("button", name="Đăng nhập").click()
            pg.wait_for_selector("text=Quản trị · " + TEN_GD[gd])
            pg.get_by_role("tab", name="Cài đặt").click()
            pg.wait_for_selector("#dkExcel")
            trang.append(pg)
            return pg
        yield vao
        assert all(p.loi == [] for p in trang)
        br.close()


def tep(pg, ten, b64):
    d = pg.thu_muc / ten
    d.write_bytes(base64.b64decode(b64))
    return str(d)


def chon(pg, ten, b64):
    pg.set_input_files("#dkExcelTep", tep(pg, ten, b64))


def dem(pg):
    return t9.dem(pg.api)


def test_a_khoi_co_mot_nut_vang_tat_va_moi_nut_du_44px(cong):
    pg = cong()
    k = pg.locator("#dkExcel")
    assert k.locator("h3").inner_text() == "Nạp từ Excel" and pg.locator("#dkApp .btn-primary:visible").count() == 1
    nap = pg.locator("#dkExcelNap")
    assert nap.inner_text() == "Nạp" and nap.is_disabled() and "btn-primary" in nap.get_attribute("class")
    for b in k.locator(".btn:visible").all():
        assert b.bounding_box()["height"] >= 44 and b.bounding_box()["width"] >= 44
    assert pg.locator("#dkExcelMau").inner_text() == "Tải file mẫu" and pg.locator("#dkExcelChon").is_visible()
    assert pg.locator("#dkExcelKhoa").count() == 0


def test_b_tai_file_mau_la_xlsx_chi_co_tieu_de(cong):
    pg = cong()
    with pg.expect_download() as d:
        pg.locator("#dkExcelMau").click()
    f = d.value
    assert f.suggested_filename == "MAU_DANG_KY.xlsx"
    p = pg.thu_muc / "mau.xlsx"
    f.save_as(str(p))
    wb = openpyxl.load_workbook(str(p))
    assert wb.sheetnames == ["Học sinh", "Giáo viên", "Phòng", "Hướng dẫn"] and wb["Học sinh"].max_row == 1
    chon(pg, "mau.xlsx", base64.b64encode(p.read_bytes()).decode())                       # tệp mẫu để trống: không có gì để nạp
    pg.wait_for_selector("#dkExcelTomTat")
    assert "chưa có dòng dữ liệu nào" in pg.locator("#dkExcelTomTat").inner_text() and pg.locator("#dkExcelNap").is_disabled()


def test_c_chon_tep_xem_truoc_roi_nap_hien_phieu_pin_mot_lan(cong):
    pg = cong()
    t0 = dem(pg)
    chon(pg, "ds.xlsx", t9.tep_tot())
    pg.wait_for_selector("#dkExcelTomTat")
    assert "Sẽ nạp 7 dòng hợp lệ." == pg.locator("#dkExcelTomTat").inner_text()
    assert dem(pg) == t0                                                                  # xem trước không ghi gì
    bang = [[c.strip() for c in r.locator("td").all_inner_texts()] for r in pg.locator("#dkExcelXem tbody tr").all()]
    assert bang == [["Học sinh", "3", "3", "0", "0"], ["Giáo viên", "2", "2", "0", "0"], ["Phòng", "2", "2", "0", "0"]]
    assert pg.locator("#dkExcelNap").is_enabled() and pg.locator("#dkPin .dk-phieu").count() == 0
    pg.locator("#dkExcelNap").click()
    pg.wait_for_selector("#dkPin .dk-phieu", state="attached")
    assert pg.locator("#dkPin .dk-phieu").count() == 5                                     # 3 học sinh + 2 giáo viên, một phiếu gộp
    assert pg.locator("#dkPin h3").inner_text() == "Mã PIN vừa tạo (chỉ hiện lúc này)"
    thong = pg.locator("#dkThongBao").inner_text()
    assert "học sinh mới 3" in thong and "giáo viên mới 2" in thong and "phòng mới 2" in thong
    slips = pg.locator("#dkPin .dk-phieu").all_text_contents()                              # phiếu nằm trong vùng in (ẩn tới khi bấm «Xem phiếu PIN»)
    assert any("Đăng nhập: họ tên + PIN này." in s for s in slips) and any("Đăng nhập: mã học sinh + PIN này." in s for s in slips)
    pin = pg.locator("#dkPin .dk-phieu", has_text="Mã: H1").locator(".dk-phieu-pin b").text_content()
    assert ok(pg.api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]                          # PIN trên phiếu dùng được
    assert pg.locator("#dkExcelNap").is_disabled() and pg.locator("#dkExcelXem details").count() == 0            # không có dòng lỗi
    assert "học sinh mới 3" in pg.locator("#dkExcelKq").inner_text()                                              # kết quả ở lại trên thẻ
    nhan = [r.locator("td").first.inner_text() for r in pg.locator("#dkPin tbody tr").all()]
    assert "Nguyễn An · H1 · 10A1" in nhan and "Cô Hoa (giáo viên)" in nhan                                       # bảng PIN có mã và lớp
    assert len(ok(pg.api.dk_hs_danh_sach(pg.qt))) == 3 and len(ok(pg.api.dk_gv_danh_sach(pg.qt))) == 2
    assert len(ok(pg.api.dk_phong_danh_sach(pg.qt))) == 3 + 2                                # 3 phòng của fixture + 2 phòng nạp


def test_d_dong_loi_co_so_dong_va_ly_do_dong_hop_le_van_nap(cong):
    pg = cong()
    chon(pg, "loi.xlsx", t9.tep_loi())
    pg.wait_for_selector("#dkExcelTomTat")
    assert "Sẽ nạp 6 dòng hợp lệ, bỏ qua 15 dòng lỗi." == pg.locator("#dkExcelTomTat").inner_text()
    hs = pg.locator("details.dk-excel-loi[data-trang=hoc_sinh]")
    assert "Trang «Học sinh»: 6 dòng lỗi (bị bỏ qua)" in hs.locator("summary").inner_text()
    dong = {r.locator("td").nth(0).inner_text().strip(): r.locator("td").nth(1).inner_text().strip() for r in hs.locator("tbody tr").all()}
    assert dong["3"] == "Thiếu mã học sinh." and dong["6"] == "Mã học sinh trùng với một dòng phía trên." and dong["5"].startswith("Khối suy từ lớp")
    assert dong["8"] == "Họ tên hoặc tên dài quá 60 ký tự."
    assert pg.locator("details.dk-excel-loi").count() == 3 and pg.locator("#dkExcelNap").is_enabled()
    pg.locator("#dkExcelNap").click()
    pg.wait_for_selector("#dkPin .dk-phieu", state="attached")
    assert "Bỏ qua 15 dòng lỗi." in pg.locator("#dkThongBao").inner_text()
    assert pg.locator("#dkExcelKq").inner_text().startswith("Đã nạp") and pg.locator("details.dk-excel-loi").count() == 3          # bảng lỗi còn sau «Nạp»
    assert pg.locator("details.dk-excel-loi[data-trang=hoc_sinh] tbody tr").count() == 6
    assert sorted(x["ma"] for x in ok(pg.api.dk_hs_danh_sach(pg.qt))) == ["H1", "H7"]


def test_e_nap_lai_giu_pin_va_khong_cap_phieu_moi_cho_em_cu(cong):
    pg = cong()
    chon(pg, "ds.xlsx", t9.tep_tot())
    pg.wait_for_selector("#dkExcelTomTat")
    pg.locator("#dkExcelNap").click()
    pg.wait_for_selector("#dkPin .dk-phieu", state="attached")
    pin_h1 = pg.locator("#dkPin .dk-phieu", has_text="Mã: H1").locator(".dk-phieu-pin b").text_content()
    chon(pg, "ds2.xlsx", t9.tep_tot())
    pg.wait_for_selector("#dkExcelTomTat")
    bang = [[c.strip() for c in r.locator("td").all_inner_texts()] for r in pg.locator("#dkExcelXem tbody tr").all()]
    assert bang == [["Học sinh", "3", "0", "3", "0"], ["Giáo viên", "2", "0", "2", "0"], ["Phòng", "2", "0", "2", "0"]]
    pg.locator("#dkExcelNap").click()
    pg.wait_for_selector("#dkPin p.dk-phu", state="attached")
    assert pg.locator("#dkPin .dk-phieu").count() == 0 and "Không có tài khoản mới" in pg.locator("#dkPin").inner_text()
    assert ok(pg.api.dk_dang_nhap("hoc_sinh", "H1", pin_h1))["token"]


def test_f_khong_phai_xlsx_va_tep_hong_bao_loi_khong_cho_nap(cong):
    pg = cong()
    t0 = dem(pg)
    pg.set_input_files("#dkExcelTep", {"name": "ds.csv", "mimeType": "text/csv", "buffer": b"ma,ten,lop\nH1,An,10A1\n"})
    pg.wait_for_function("document.getElementById('dkThongBao').textContent.length > 0")
    assert "Chỉ nhận tệp Excel .xlsx" in pg.locator("#dkThongBao").inner_text() and pg.locator("#dkExcelNap").is_disabled()
    pg.set_input_files("#dkExcelTep", {"name": "gia.xlsx", "mimeType": XLSX, "buffer": b"ma,ten,lop\nH1,An,10A1\n"})     # .csv đổi đuôi
    pg.wait_for_function("document.getElementById('dkThongBao').classList.contains('la-loi')")
    pg.wait_for_timeout(300)
    assert "Chỉ nhận tệp Excel .xlsx" in pg.locator("#dkThongBao").inner_text() and pg.locator("#dkExcelNap").is_disabled()
    chon(pg, "khong_trang.xlsx", t9.b64({"Sheet1": [["a"], ["b"]]}))
    pg.wait_for_function("document.getElementById('dkThongBao').textContent.includes('trang tính')")
    assert pg.locator("#dkExcelNap").is_disabled() and dem(pg) == t0


def test_g_tha_tep_vao_vung_keo_tha(cong):
    pg = cong()
    b64 = t9.tep_tot()
    pg.evaluate("""async (b64) => {
        const bin = atob(b64), u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
        const dt = new DataTransfer(); dt.items.add(new File([u8], 'tha.xlsx', { type: '%s' }));
        document.getElementById('dkExcelTha').dispatchEvent(new DragEvent('drop', { dataTransfer: dt, bubbles: true, cancelable: true }));
    }""" % XLSX, b64)
    pg.wait_for_selector("#dkExcelTomTat")
    assert pg.locator("#dkExcelTen").inner_text() == "tha.xlsx" and pg.locator("#dkExcelNap").is_enabled()


def test_h_giai_doan_hoc_sinh_dang_ky_trang_hoc_sinh_bi_khoa(cong):
    pg = cong("hs_dang_ky")
    assert "Học sinh đã bắt đầu đăng ký" in pg.locator("#dkExcelKhoa").inner_text()
    chon(pg, "ds.xlsx", t9.tep_tot())
    pg.wait_for_selector("#dkExcelTomTat")
    bang = [[c.strip() for c in r.locator("td").all_inner_texts()] for r in pg.locator("#dkExcelXem tbody tr").all()]
    assert bang[0] == ["Học sinh", "Đã khoá", "—", "—", "—"] and bang[1][:3] == ["Giáo viên", "2", "2"]
    n_hs = len(ok(pg.api.dk_hs_danh_sach(pg.qt)))
    pg.locator("#dkExcelNap").click()
    pg.wait_for_selector("#dkPin .dk-phieu", state="attached")
    assert pg.locator("#dkPin .dk-phieu").count() == 2                                     # chỉ hai giáo viên
    assert len(ok(pg.api.dk_hs_danh_sach(pg.qt))) == n_hs


def test_i_khoi_khong_tran_ngang_o_man_hep(cong):
    pg = cong(rong=390)
    chon(pg, "loi.xlsx", t9.tep_loi())
    pg.wait_for_selector("#dkExcelTomTat")
    assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
    for b in pg.locator("#dkExcel .btn:visible").all():
        assert b.bounding_box()["height"] >= 44


def test_j_ten_chua_the_html_khong_chay_ma(cong):
    """Soát mã tầng 3: tên trong tệp đi qua textContent; `<img onerror>` hiện là chữ, không chạy."""
    pg = cong()
    xau = '<img src=x onerror="window.__xss=1">'
    chon(pg, "xss.xlsx", t9.b64({"Học sinh": [t9.HS_TD, ["H1", xau, "10A1"], ["H2", "Em", "3A1"]], "Giáo viên": [t9.GV_TD, [xau + "gv"]],
                                "Phòng": [t9.PH_TD, [xau + "p", 5]]}))
    pg.wait_for_selector("#dkExcelTomTat")
    pg.locator("#dkExcelNap").click()
    pg.wait_for_selector("#dkPin .dk-phieu", state="attached")
    assert pg.evaluate("window.__xss === undefined") and pg.locator("#dkExcel img").count() == 0
    assert xau in pg.locator("#dkPin tbody").first.text_content()
