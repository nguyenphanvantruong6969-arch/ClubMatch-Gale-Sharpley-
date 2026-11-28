"""DK8-L1: `dk_trang_thai` (công khai, không cần phiên) trả thêm HAI SỐ ĐẾM cho thẻ vai trò ở trang đầu: số tài khoản giáo viên và
số học sinh đã gửi nguyện vọng. Chỉ số đếm: không tên, không mã. Dữ liệu MÔ PHỎNG."""
import test_dk3_api as t3
from test_dk3_api import ok

cd = t3.cd                                                      # fixture dùng chung (cùng cách các test DK4)


def test_so_dem_bat_dau_bang_khong_va_chi_la_so(cd):
    api, _ = cd
    d = ok(api.dk_trang_thai())
    assert d["so_gv"] == 0 and d["so_da_gui"] == 0
    assert isinstance(d["so_gv"], int) and isinstance(d["so_da_gui"], int)


def test_so_dem_tang_dung_va_khong_lo_ten_hay_ma(cd):
    api, qt = cd
    ok(api.dk_gv_tu_dang_ky("TRUONG1", "Cô Dung", "7391"))      # một giáo viên tự đăng ký (giai đoạn giáo viên đang mở)
    ids = t3._dung_san(api, qt)                                   # + 3 giáo viên do quản trị tạo, 3 học sinh, mở cho học sinh
    d = ok(api.dk_trang_thai())
    assert d["so_gv"] == 4 and d["so_da_gui"] == 0
    h1 = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    ok(api.dk_hs_luu(h1, [{"clb_id": ids["Cờ vua"]}]))
    d = ok(api.dk_trang_thai())
    assert d["so_gv"] == 4 and d["so_da_gui"] == 1
    chu = str(d)
    assert not any(x in chu for x in ("Cô An", "Thầy Bình", "Cô Dung", "H1", "H2", "An", "Robot"))   # công khai: chỉ số đếm
    assert set(d) == {"khoi_tao", "giai_doan", "han_chot", "buoi", "khoi", "toi_da_nv", "toi_da_thi", "so_gv", "so_da_gui"}


def test_chua_khoi_tao_van_chi_tra_khoi_tao_sai(api):
    assert ok(api.dk_trang_thai()) == {"khoi_tao": False}
