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


# ---- 3. Mã PIN học sinh / giáo viên -----------------------------------------------------------------
def test_nap_lai_danh_sach_hs_van_cho_quan_tri_lay_duoc_pin(cd):
    """Nạp lại danh sách (chế độ «them») chỉ trả PIN của em MỚI; em đã có thì `pin` rỗng, quản trị mất đường lấy PIN
    (phải đặt lại từng em). Cần: trả rõ em nào đã có PIN, hoặc có đường xuất phiếu PIN cho toàn bộ."""
    api, qt = cd
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1"))
    r = ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1\nH3\tChi\t10A1"))
    assert {x["ma"] for x in r["pin"]} == {"H1", "H2", "H3"}


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
    ok(api.dk_cai_dat_doi(qt, bat_buoc_tu_do=False))     # tham số chưa tồn tại -> TypeError (đỏ)
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
