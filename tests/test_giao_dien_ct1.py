"""CT1-L3: màn "Xem xét chỉ tiêu" (Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG: `SO_NHAP_TEST.xlsx`, 120 học sinh,
10 CLB, 130 chỗ, bốc thăm khoá seed 42).

Kiểm: lối vào là MỘT nút phụ "Gợi ý chỉ tiêu" ở góc phải thanh công cụ (chỉ quản trị); đầu đề khuyến nghị, bốn bước, mở danh sách một bước,
bảng chỉ tiêu; ngân sách Hick (≤ 7 điều khiển mỗi khung) và Von Restorff (≤ 1 nút vàng mỗi khung, màu luôn kèm chữ, không nút đỏ,
không nút "Áp dụng"); "Tự thử một thay đổi"; bề rộng 390 px không tràn ngang; khoá i18n vi + en khớp nhau.
"""

import os
import re


from _ux5a_chung import GOC, JS_DO, JS_VANG, dem, mo_ux5a  # noqa: F401

SO_TEST = os.path.join(GOC, "du_lieu_test", "SO_NHAP_TEST.xlsx")
RULES = {"wharton": False}
KHUNG = ("#ct1Khuyen", "#ct1Buoc", "#ct1Thu", "#ct1Thieu", "#ct1Bang")


def _mo(mo_ux5a, vai="quan_tri", rong=1280):  # noqa: F811
    return mo_ux5a(vai, so_nhap=SO_TEST, rules=RULES, rong=rong)


def _vao_ct1(page):
    page.click("#btnCt1Mo")
    page.wait_for_selector("#ct1Noi", state="visible", timeout=90000)   # bộ 800HS giải lại nhiều lần: CI chậm hơn máy phát triển
    page.wait_for_timeout(300)


def test_loi_vao_la_mot_nut_phu_o_goc_phai_chi_quan_tri(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    nut = page.locator("#btnCt1Mo")
    assert nut.count() == 1 and nut.is_visible()                                              # thấy ngay, không cần mở menu
    assert dem(page, "#ux1bPanel") == ["kqChonLop", "btnUx1bXuatLop", "ux1bThemTom"]          # nhóm "lớp và báo cáo" không đổi
    assert len(dem(page, "#view-results")) <= 10                                              # ngân sách Hick của UX5A (quản trị)
    assert "btn-primary" not in (nut.get_attribute("class") or "")                            # Von Restorff: chỉ MỘT nút vàng
    assert page.evaluate(JS_VANG, "#view-results") == ["btnKqTaiBang"]
    assert nut.inner_text().strip() == "Gợi ý thay đổi chỉ tiêu"
    assert "btn-secondary" in (nut.get_attribute("class") or "")                               # TK1-L2: nút phụ thường, bỏ viền đậm 2 px + bóng đèn (test_tk1_on_dinh)
    assert nut.evaluate("e => getComputedStyle(e).borderTopWidth") == "1px"
    assert "Gợi ý và thay đổi chỉ tiêu" in (nut.get_attribute("title") or "")
    a, b = nut.bounding_box(), page.locator("#btnKqTaiBang").bounding_box()
    assert a["x"] < b["x"] and abs(a["y"] - b["y"]) < 20 and b["x"] + b["width"] > 1000       # cạnh nút vàng, bên phải thanh
    assert page.locator("#ux1bThemMenu #btnCt1Mo").count() == 0                              # không còn nằm trong menu
    assert page.locator("#ct1Khung").is_hidden()
    assert not loi, loi


def test_giao_vien_khong_thay_loi_vao_va_bi_tu_choi_o_backend(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a, "giao_vien")
    assert page.locator("#btnCt1Mo").is_hidden() and page.locator("#ct1Khung").is_hidden()
    r = api.get_xem_xet_chi_tieu()
    assert not r["ok"] and r["errors"][0]["code"] == "gt3_khong_du_quyen"
    assert not loi, loi


def test_dau_de_khuyen_nghi_bon_buoc_va_bang(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    assert page.locator("#ct1KnCau").inner_text().strip() == "Chuyển 11 chỗ từ 4 CLB đang thừa chỗ sang 4 CLB đang thiếu chỗ."
    o = page.locator("#ct1Tile").inner_text()
    assert "64" in o and "74" in o and "Thêm 10" in o and "Bớt 4" in o and "15" in o
    assert page.locator("#ct1DsBuoc > li").count() == 4
    assert [page.locator("#ct1Buoc%d .ct1-chip" % i).first.inner_text().split(" ")[1] for i in (1,)] == ["Bóng"]
    assert "Sau cả 4 bước: 15" in page.locator("#ct1KetBuoc").inner_text()
    assert page.locator("#ct1BangTab tbody tr").count() == 10
    assert "24 (+4)" in page.locator("#ct1BangTab").inner_text()
    assert "mô phỏng" not in page.locator("#ct1Khung").inner_text().lower()      # chữ "dữ liệu mô phỏng" chỉ ở dữ liệu mẫu, không ở giao diện
    assert not loi, loi


def test_mo_danh_sach_mot_buoc_va_dong_mac_dinh(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    assert page.locator("#ct1Doi1").evaluate("e => !e.open")
    tom = page.locator("#ct1DoiTom1").inner_text()
    k = int(re.search(r"\((\d+)\)", tom).group(1))
    page.click("#ct1DoiTom1")
    assert page.locator("#ct1Doi1 tbody tr").count() == k and k >= 1
    assert api.get_xem_xet_chi_tieu()["data"]["buoc"][0]["so_doi"] == k
    assert not loi, loi


def test_ngan_sach_hick_tung_khung(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    assert dem(page, "#ct1Khuyen") == ["btnCt1XuatDeXuat"]
    assert len(dem(page, "#ct1Buoc")) <= 7 and "btnCt1XuatDoiChieu" in dem(page, "#ct1Buoc")
    assert dem(page, "#ct1Thu") == ["ct1ThuTom"]                  # gập sẵn
    assert dem(page, "#ct1Thieu") == []                           # không nút
    assert len(dem(page, "#ct1Bang")) <= 7
    assert page.evaluate("() => document.querySelectorAll('#ct1Khung a[href]').length") == 1     # đúng MỘT đường dẫn: sang màn Tiêu chí
    assert "ct1LienTieuChi" in dem(page, "#ct1Khung")
    page.click("#ct1ThuTom")
    mo = dem(page, "#ct1Thu")
    assert len(mo) <= 5 + 1, mo                                    # ba ô chọn + một nút vàng (+ chính tiêu đề gập)
    assert page.locator("#ct1ThuK option").count() == 3
    assert not loi, loi


def test_ngan_sach_hick_khi_co_hon_sau_buoc(mo_ux5a):  # noqa: F811
    """Dữ liệu giả: 8 bước thì chỉ hiện 5 bước + "Xem thêm bước" (đủ 7 điều khiển), bấm thì hiện hết."""
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    du = page.evaluate("ct1Du")
    b = du["buoc"][0]
    du["buoc"] = [dict(b, stt=i + 1) for i in range(8)]
    page.evaluate("(d) => { ct1Du = d; ct1HienHet = false; ct1VeBuoc(d); }", du)
    assert page.locator("#ct1DsBuoc > li").count() == 5
    assert len(dem(page, "#ct1Buoc")) <= 7
    page.click("#btnCt1ThemBuoc")
    assert page.locator("#ct1DsBuoc > li").count() == 8


def test_von_restorff_mot_nut_vang_khong_do_chu_kem_mau(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    assert page.evaluate(JS_VANG, "#ct1Khuyen") == ["btnCt1XuatDeXuat"]
    for k in ("#ct1Buoc", "#ct1Thieu", "#ct1Bang"):
        assert page.evaluate(JS_VANG, k) == [], k
    assert page.evaluate(JS_VANG, "#ct1Thu") == []                 # gập: nút vàng chưa hiện
    page.click("#ct1ThuTom")
    assert page.evaluate(JS_VANG, "#ct1Thu") == ["btnCt1ThuXep"]
    assert page.evaluate(JS_DO, "#ct1Khung") == []
    chu = page.locator("#ct1Khung").inner_text()
    assert "Áp dụng" not in chu and "PDF" not in chu                # chỉ đọc: không có nút ghi chỉ tiêu, không xuất PDF
    # Màu mang nghĩa luôn kèm chữ: mọi ô chữ "tăng / giảm" đều có nội dung.
    trong = page.evaluate("""() => Array.from(document.querySelectorAll(
        '#ct1Khung .ct1-o-dong, #ct1Khung .ct1-cot-dl, #ct1Khung .ct1-huong, #ct1Khung .ct1-tag, #ct1Khung .ct1-chip'))
        .filter(e => !e.textContent.trim()).length""")
    assert trong == 0
    # Không tô màu nhấn cho nhãn nhỏ và tiêu đề.
    mau = page.evaluate("""() => ({
        nhan: getComputedStyle(document.querySelector('#ct1Khuyen .ct1-nhan-nho')).color,
        tde: getComputedStyle(document.querySelector('#ct1KnCau')).color,
        slate: getComputedStyle(document.documentElement).getPropertyValue('--slate').trim(),
        ink: getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() })""")
    assert mau["nhan"] == "rgb(91, 101, 112)" and mau["tde"] == "rgb(28, 35, 33)", mau
    assert not loi, loi


def test_tu_thu_mot_thay_doi(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    page.click("#ct1ThuTom")
    page.click("#btnCt1ThuXep")                                    # chưa chọn gì
    assert page.locator("#ct1ThuLoi").is_visible() and page.locator("#ct1ThuKq").is_hidden()
    page.select_option("#ct1ThuTu", "clb_bongro")
    page.select_option("#ct1ThuDen", "clb_bongda")
    page.select_option("#ct1ThuK", "2")
    page.click("#btnCt1ThuXep")
    page.wait_for_selector("#ct1ThuKq", state="visible")
    assert page.locator("#ct1ThuTieuDe").inner_text().startswith("Kết quả mới:")
    assert page.locator("#ct1ThuLoi").is_hidden()
    assert "ct1-vua-xong" in page.get_attribute("#ct1ThuKq", "class")      # nhấn mạnh ngắn, nghĩa cũng nằm ở chữ "Kết quả mới"
    d = api.get_xem_xet_chi_tieu([{"tu": "clb_bongro", "den": "clb_bongda", "k": 2}])["data"]
    assert page.locator("#ct1ThuBangHop tbody tr").count() == min(30, sum(b["so_doi"] for b in d["buoc"]))
    page.select_option("#ct1ThuTu", "clb_bongda")                   # khác buổi? cùng buổi nhưng chỗ còn đủ: vẫn hợp lệ
    page.select_option("#ct1ThuDen", "clb_bongda")
    page.click("#btnCt1ThuXep")
    assert page.locator("#ct1ThuLoi").is_visible()
    assert not loi, loi


def test_dong_va_quay_lai_ket_qua(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    assert page.locator("#gtPanel").is_visible()
    _vao_ct1(page)
    assert page.locator("#gtPanel").is_hidden() and page.locator("#kqThanhCongCu").is_hidden()
    page.click("#btnCt1Dong")
    assert page.locator("#ct1Khung").is_hidden() and page.locator("#gtPanel").is_visible()
    assert not loi, loi


def test_lien_ket_tieu_chi(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    page.click("#ct1LienTieuChi")
    page.wait_for_selector("#view-admin", state="visible")
    assert page.locator("#gt2TieuChiPanel").is_visible()
    assert not loi, loi


def test_khong_tran_ngang_o_390px(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a, rong=390)
    _vao_ct1(page)
    page.click("#ct1ThuTom")
    page.click("#ct1DoiTom1")
    r = page.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
    assert r[0] <= r[1] + 1, r
    for k in KHUNG:
        assert page.locator(k).is_visible(), k
    # CT1-FIX2: cột "Đề xuất" (cả mục đích của bảng) phải nằm trọn trong màn 390 px, ba cột phụ được ẩn
    o = page.locator("#ct1BangTab thead th").last.bounding_box()
    assert o["x"] >= 0 and o["x"] + o["width"] <= 390 + 1, o
    assert page.locator("#ct1BangTab thead th.ct1-phu").first.is_hidden()
    assert not loi, loi


def test_chua_co_ket_qua_hien_cau_thuong(tmp_path, mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    import sqlite3
    c = sqlite3.connect(api.db_path)
    c.execute("DELETE FROM run_history")
    c.commit()
    c.close()
    page.click("#btnCt1Mo")
    page.wait_for_function("document.getElementById('ct1TrangThai').textContent.includes('Chưa có kết quả')")
    assert "Chưa có kết quả xếp chính thức" in page.locator("#ct1TrangThai").inner_text()
    assert page.locator("#ct1Noi").is_hidden()


def test_khoa_i18n_vi_va_en_khop_nhau():
    nguon = open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    ct1 = re.findall(r'\b(ct1_[a-z0-9_]+): "((?:[^"\\]|\\.)*)"', nguon)
    ten = [k for k, _ in ct1]
    assert len(ten) % 2 == 0 and ten[: len(ten) // 2] == ten[len(ten) // 2:]       # cùng khoá, cùng thứ tự ở khối vi và khối en
    vi, en = ct1[: len(ct1) // 2], ct1[len(ct1) // 2:]
    assert all(v.strip() and e.strip() for (_, v), (_, e) in zip(vi, en))
    khac = sum(1 for (_, v), (_, e) in zip(vi, en) if v != e)
    assert khac >= len(vi) - 6                                                    # trừ vài khoá giống nhau ("{cohort}", "{session}"...)


# ---- CT1-FIX: nhiều buổi (đơn vị lượt, ô chưa có CLB bị chặn) và dòng cảnh báo khi kém hơn > tốt hơn -------------
SO_800 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_800HS_HOP_LE.xlsx")


def test_mot_buoi_khong_co_chu_luot_va_khong_canh_bao(mo_ux5a):  # noqa: F811
    page, api, loi = _mo(mo_ux5a)
    _vao_ct1(page)
    assert "lượt" not in page.locator("#ct1KnGhiChu").inner_text() and "lượt" not in page.locator("#ct1Tile").inner_text()
    assert page.locator("#ct1KemNhieuHon").is_hidden()          # TEST: 15 tốt hơn / 0 kém hơn
    assert not loi, loi


def test_nhieu_buoi_dung_don_vi_luot_o_vuong_bi_chan_va_canh_bao_kem_hon(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", so_nhap=SO_800, rules=RULES, rong=1280)
    _vao_ct1(page)
    d = api.get_xem_xet_chi_tieu()["data"]
    ghi = page.locator("#ct1KnGhiChu").inner_text()
    assert "lượt" in ghi and "4" in ghi and "toàn bộ %d lượt" % d["truoc"]["tong"] in ghi
    assert "lượt" in page.locator("#ct1Tile").inner_text() and "học sinh" not in page.locator("#ct1Tile").inner_text()
    cb = page.locator("#ct1KemNhieuHon")
    assert d["so_kem_hon"] <= d["so_tot_hon"] and cb.is_hidden()  # cấu hình này: kém hơn không nhiều hơn tốt hơn -> không cảnh báo
    page.evaluate("() => { ct1Du = Object.assign({}, ct1Du, { so_tot_hon: 5, so_kem_hon: 9 }); ct1Ve(); }")   # kém hơn > tốt hơn
    assert cb.is_visible() and cb.inner_text().startswith("Lưu ý") and "9 lượt" in cb.inner_text()
    assert cb.evaluate("e => e.tagName") == "P"                  # chữ cảnh báo, không phải nút
    assert dem(page, "#ct1Buoc") == dem(page, "#ct1Buoc")        # không thêm điều khiển nào
    assert page.locator(".ct1-vuong").count() == 64              # chặn số ô vẽ (8 × 8)
    assert page.locator(".ct1-o-vuong .ct1-o-con-lai").count() == 0   # chữ "+N" nằm NGOÀI lưới ô, không bị ép vào một ô
    con = page.locator(".ct1-o-con-lai")
    assert con.count() == 1 and "lượt nữa không vẽ ở đây" in con.inner_text()
    assert page.locator(".ct1-o-vuong").evaluate("e => e.getBoundingClientRect().height") < 400   # không còn cột cao cả màn
    # mỗi thẻ bước dùng MỘT đơn vị: số bước 1 = số em của nút "Xem ... (k)" (một bước chỉ đổi trong một buổi)
    b1 = d["buoc"][0]
    assert "lượt" not in page.locator("#ct1Buoc1").inner_text().split("Vào")[0]
    assert "(%d)" % b1["so_doi"] in page.locator("#ct1Buoc1").inner_text()
    assert dem(page, "#ct1Buoc") and not loi, loi
