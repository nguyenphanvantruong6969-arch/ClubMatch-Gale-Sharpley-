"""VÁ GẤP — tái hiện lỗi (Truong, 2026-11-27). Mỗi test khẳng định hành vi ĐÚNG; hiện tại test ĐỎ = lỗi còn đó.

Chưa sửa mã. Khi sửa xong, các test này phải xanh (rồi đổi tên/gộp vào test của mục tương ứng).
"""
import unicodedata

import pytest


def ok(r):
    assert r["ok"], r
    return r["data"]


def ma(r):
    assert not r["ok"], r
    return r["errors"][0]["code"]


@pytest.fixture
def cd(api):
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t, sc in (("P1", 40), ("P2", 30)):
        ok(api.dk_phong_luu(qt, t, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    return api, qt


def _clb(**kw):
    d = {"ten": "Cờ vua", "buoi": "T2", "loai": "Giới hạn", "phong_id": 1, "chi_tieu": 20, "khoi_tu": 10, "khoi_den": 12}
    d.update(kw)
    return d


# ---- 1/2. Cổng đăng nhập kiểm sai ------------------------------------------------------------------
def test_gv_dang_nhap_ten_go_kieu_to_hop_nfd(cd):
    """Tên được lưu ở dạng NFC (lúc tạo) nhưng lúc đăng nhập KHÔNG chuẩn hoá NFC: gõ/dán tên tiếng Việt dạng NFD
    (macOS, một số bộ gõ) bị báo «sai» dù đúng tên và đúng PIN."""
    api, qt = cd
    pin = ok(api.dk_gv_tao_hang_loat(qt, "Nguyễn Văn Ân"))["da_tao"][0]["pin"]
    nfd = unicodedata.normalize("NFD", "Nguyễn Văn Ân")
    assert nfd != "Nguyễn Văn Ân"
    assert ok(api.dk_dang_nhap("giao_vien", nfd, pin))["ten"] == "Nguyễn Văn Ân"


def test_hs_dang_nhap_ma_khong_phan_biet_hoa_thuong_va_pin_co_khoang_trang(cd):
    """Mã học sinh `H9` gõ `h9` bị từ chối; PIN gõ thừa dấu cách (« 1234») cũng bị từ chối. Cả hai là lỗi gõ thường gặp ở kiosk."""
    api, qt = cd
    pin = ok(api.dk_hs_nap_danh_sach(qt, "H9\tAn\t10A1"))["pin"][0]["pin"]
    assert ok(api.dk_dang_nhap("hoc_sinh", "H9", pin))["id"] == "H9"
    assert ok(api.dk_dang_nhap("hoc_sinh", "h9", pin))["id"] == "H9"
    assert ok(api.dk_dang_nhap("hoc_sinh", "H9", " %s " % pin))["id"] == "H9"


def test_dang_nhap_pin_khong_phai_bon_chu_so_bi_tu_choi_truoc_khi_bam(cd):
    """PIN phải đúng 4 chữ số; PIN sai dạng (chữ, rỗng, quá dài) phải bị chặn bằng mã riêng,
    không được tính là «một lần sai» đẩy tài khoản thật tới khoá (DoS: ai cũng khoá được tài khoản người khác)."""
    api, qt = cd
    ten = ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]
    for _ in range(5):                                   # người lạ gõ sai 5 lần vào tên của cô An
        api.dk_dang_nhap("giao_vien", "Cô An", "abcd")
    assert ok(api.dk_dang_nhap("giao_vien", "Cô An", ten["pin"]))["ten"] == "Cô An"


# ---- 3. Mã PIN học sinh / giáo viên (VG1-L2, D2: PIN chỉ lưu băm nên «xuất» = ĐẶT LẠI + xuất .xlsx) -------------------
def _doc_xlsx(d):
    import base64
    import io

    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(base64.b64decode(d["file_base64"])))
    return {ws.title: [[c.value for c in r] for r in ws.iter_rows(min_row=1)] for ws in wb.worksheets}


def _hs_gv(api, qt):
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A2"))
    ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))


def test_xuat_pin_co_hai_trang_moi_pin_dang_nhap_duoc_pin_cu_hong_va_mo_khoa(cd):
    api, qt = cd
    _hs_gv(api, qt)
    pin_cu = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    for _ in range(5):                                           # khoá H1 bằng PIN sai ĐÚNG DẠNG
        api.dk_dang_nhap("hoc_sinh", "H1", "0000" if pin_cu != "0000" else "1111")
    assert ma(api.dk_dang_nhap("hoc_sinh", "H1", pin_cu)) == "dk_tam_khoa"
    d = ok(api.dk_pin_xuat_excel(qt, "tat_ca", xac_nhan=True))
    bang = _doc_xlsx(d)
    assert bang["Học sinh"][0] == ["Mã HS", "Họ tên", "Lớp", "PIN"] and bang["Giáo viên"][0] == ["Họ tên", "PIN"]
    assert d["so_hs"] == 2 and d["so_gv"] == 1
    for m_, ten, lop, pin in bang["Học sinh"][1:]:
        assert ok(api.dk_dang_nhap("hoc_sinh", m_, pin))["ten"] == ten and lop in ("10A1", "10A2")
    ten, pin = bang["Giáo viên"][1]
    assert ok(api.dk_dang_nhap("giao_vien", ten, pin))["ten"] == "Cô An"
    pin_moi = {r[0]: r[3] for r in bang["Học sinh"][1:]}["H1"]
    if pin_moi != pin_cu:                                        # (xác suất 1/10000 trùng: bỏ qua nhánh này)
        assert ma(api.dk_dang_nhap("hoc_sinh", "H1", pin_cu)) == "dk_sai_dang_nhap"


def test_xuat_pin_loc_lop_va_pham_vi(cd):
    api, qt = cd
    _hs_gv(api, qt)
    d = ok(api.dk_pin_xuat_excel(qt, "hs", lop="10A2", xac_nhan=True))
    assert d["so_hs"] == 1 and d["so_gv"] == 0
    assert [r[0] for r in _doc_xlsx(d)["Học sinh"][1:]] == ["H2"]
    assert ma(api.dk_pin_xuat_excel(qt, "xyz", xac_nhan=True)) == "dk_pham_vi_la"


def test_xuat_pin_can_xac_nhan_va_khong_doi_gi_khi_chua_xac_nhan(cd):
    api, qt = cd
    _hs_gv(api, qt)
    pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    assert ma(api.dk_pin_xuat_excel(qt, "tat_ca")) == "dk_can_xac_nhan_pin"
    assert ma(api.dk_pin_xuat_excel(qt, "tat_ca", xac_nhan="true")) == "dk_can_xac_nhan_pin"
    assert ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]  # PIN cũ còn nguyên


def test_xuat_pin_chi_quan_tri_va_nhat_ky_khong_co_pin(cd):
    api, qt = cd
    _hs_gv(api, qt)
    ok(api.dk_hs_dat_lai_pin(qt, "H1"))
    th = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    pin_gv = ok(api.dk_gv_dat_lai_pin(qt, 1))["pin"]
    tg = ok(api.dk_dang_nhap("giao_vien", "Cô An", pin_gv))["token"]
    for t in (th, tg, "khong-co", None):
        assert not api.dk_pin_xuat_excel(t, "tat_ca", xac_nhan=True)["ok"]
    d = ok(api.dk_pin_xuat_excel(qt, "tat_ca", xac_nhan=True))
    import sqlite3
    c = sqlite3.connect(api.db_path)
    ct = [r[0] for r in c.execute("SELECT chi_tiet FROM dk_nhat_ky WHERE hanh_dong = 'xuat_pin'")]
    c.close()
    assert ct == ["tat_ca hs=2 gv=1"]                             # chỉ số người, không có PIN nào
    assert d["so_hs"] == 2


# ---- 4/5. CLB Tự do: ràng buộc phải CHẶN SỚM (lúc duyệt), không đợi tới lúc mở cho học sinh -------------
def _hai_clb_khong_tu_do(api, qt):
    pin = {x["ten"]: x["pin"] for x in ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình"))["da_tao"]}
    t = {k: ok(api.dk_dang_nhap("giao_vien", k, v))["token"] for k, v in pin.items()}
    a = ok(api.dk_clb_luu(t["Cô An"], _clb(ten="Cờ vua", phong_id=1, chi_tieu=10)))["clb_id"]
    b = ok(api.dk_clb_luu(t["Thầy Bình"], _clb(ten="Robot", phong_id=2, chi_tieu=10)))["clb_id"]
    return a, b                                         # vẫn ở giai đoạn gv_dang_ky


def test_chan_truoc_khi_vao_giai_doan_duyet_khi_buoi_thieu_clb_tu_do(cd):
    """HIỆN TẠI: 2 CLB «Giới hạn» ở T2, không CLB Tự do: chuyển sang «duyet», duyệt cả hai đều thành công, tới lúc «mở cho
    học sinh» mới báo `dk_thieu_clb_tu_do`. Cần (ràng buộc BẬT, mặc định): chặn NGAY khi chuyển sang «duyet»."""
    api, qt = cd
    _hai_clb_khong_tu_do(api, qt)
    assert ma(api.dk_chuyen_giai_doan(qt, "duyet")) == "dk_thieu_clb_tu_do"


def test_rang_buoc_clb_tu_do_co_the_tat(cd):
    """Yêu cầu «không ràng buộc phải có CLB Tự do»: cài đặt `bat_buoc_tu_do=False` (mặc định True = hành vi cũ); khi tắt,
    duyệt và mở cho học sinh không bị chặn. Hiện không có cài đặt nào (cứng trong `_dk_kiem_dieu_kien_mo_hs`)."""
    api, qt = cd
    a, b = _hai_clb_khong_tu_do(api, qt)
    assert ma(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=False)) == "dk_can_xac_nhan_rui_ro"   # tắt phải xác nhận rủi ro (chưa có -> TypeError, đỏ)
    ok(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=False, xac_nhan_rui_ro=True))
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    ok(api.dk_clb_duyet(qt, a, "duyet"))
    ok(api.dk_clb_duyet(qt, b, "duyet"))
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))


# ---- 6. Quay lại giai đoạn trước -------------------------------------------------------------------
def test_lui_giai_doan_khong_de_nguyen_vong_mo_coi(cd):
    """Lùi từ «hs_dang_ky» về «duyet» rồi TỪ CHỐI một CLB đã có em chọn: `dk_nguyen_vong` còn dòng trỏ CLB đã từ chối
    (nguyện vọng mồ côi, em không biết). Cần: dọn/báo các em bị ảnh hưởng, hoặc chặn từ chối khi đã có em chọn."""
    api, qt = cd
    pin = {x["ten"]: x["pin"] for x in ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình"))["da_tao"]}
    t = {k: ok(api.dk_dang_nhap("giao_vien", k, v))["token"] for k, v in pin.items()}
    tu_do = ok(api.dk_clb_luu(t["Cô An"], _clb(ten="Tự do", loai="Tự do", phong_id=1)))["clb_id"]
    gh = ok(api.dk_clb_luu(t["Thầy Bình"], _clb(ten="Cờ vua", phong_id=2, chi_tieu=10)))["clb_id"]
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    ok(api.dk_clb_duyet(qt, tu_do, "duyet"))
    ok(api.dk_clb_duyet(qt, gh, "duyet"))
    h = ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))["pin"][0]["pin"]
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    th = ok(api.dk_dang_nhap("hoc_sinh", "H1", h))["token"]
    ok(api.dk_hs_luu(th, [{"clb_id": gh}, {"clb_id": tu_do}]))
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))                       # lùi
    r = api.dk_clb_duyet(qt, gh, "tu_choi", ly_do="bỏ")
    if not r["ok"]:
        return                                                    # chặn: chấp nhận được
    import sqlite3
    c = sqlite3.connect(api.db_path)
    mo_coi = c.execute("SELECT COUNT(*) FROM dk_nguyen_vong n JOIN dk_clb k ON k.clb_id = n.clb_id "
                       "WHERE k.trang_thai != 'duyet'").fetchone()[0]
    c.close()
    assert mo_coi == 0


# ---- 7. Số «giáo viên» ở thẻ vai trò -----------------------------------------------------------------
def test_so_gv_o_cong_chi_dem_giao_vien_da_co_tai_khoan_dung_duoc(cd):
    """Thẻ ghi «N giáo viên đã đăng ký tài khoản» nhưng `so_gv = COUNT(*) dk_giao_vien`: quản trị tạo hộ 3 giáo viên
    (chưa ai đăng nhập, chưa ai mở CLB) thì cổng đã hiện «3 giáo viên đã đăng ký». Học sinh thì đếm «đã gửi» (nop_luc).
    Cần đếm đối xứng: giáo viên đã THỰC SỰ đăng ký/đăng nhập (hoặc đã gửi CLB). GIẢ THIẾT — cần Truong xác nhận định nghĩa."""
    api, qt = cd
    ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình\nCô Chi"))
    assert api.dk_trang_thai()["data"]["so_gv"] == 0


def test_dat_lai_pin_va_xuat_pin_huy_phien_cu(cd):
    """Kiểm tra toàn diện #2: PIN bị lộ / dùng chung thì sau khi đặt lại (từng người hoặc xuất phiếu) phiên cũ phải chết."""
    api, qt = cd
    _hs_gv(api, qt)
    th = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    tg = ok(api.dk_dang_nhap("giao_vien", "Cô An", ok(api.dk_gv_dat_lai_pin(qt, 1))["pin"]))["token"]
    h2 = ok(api.dk_dang_nhap("hoc_sinh", "H2", ok(api.dk_hs_dat_lai_pin(qt, "H2"))["pin"]))["token"]
    assert api.dk_hs_nguyen_vong(th)["ok"] and api.dk_clb_danh_sach(tg)["ok"]
    ok(api.dk_hs_dat_lai_pin(qt, "H1"))                         # đặt lại từng em: chỉ phiên H1 chết
    assert ma(api.dk_hs_nguyen_vong(th)) == "dk_can_dang_nhap" and api.dk_hs_nguyen_vong(h2)["ok"]
    ok(api.dk_pin_xuat_excel(qt, "tat_ca", xac_nhan=True))      # xuất phiếu: mọi phiên của người trong phạm vi chết
    assert ma(api.dk_hs_nguyen_vong(h2)) == "dk_can_dang_nhap" and ma(api.dk_clb_danh_sach(tg)) == "dk_can_dang_nhap"
