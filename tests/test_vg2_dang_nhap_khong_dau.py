"""VG2-L1 (Truong, 2026-11-27): đăng nhập nhận tên / mã viết KHÔNG DẤU, khác hoa/thường, khác «font» (tổ hợp NFD, toàn khổ,
ký tự ẩn, dấu cách cứng, bỏ dấu kiểu cũ «hoà»/«hòa»); PIN gõ số toàn khổ vẫn đúng. Khớp đúng dấu được ưu tiên; khi chỉ khớp
không dấu mà nhiều người trùng, PIN quyết định. Bộ đếm khoá dùng khoá không dấu (không né khoá bằng cách đổi dấu). Dữ liệu MÔ PHỎNG."""
import unicodedata

import pytest

import test_va_gap_tai_hien as _v
from test_va_gap_tai_hien import ma, ok

cd = _v.cd


def _tao_gv(api, qt, ten):
    r = ok(api.dk_gv_tao_hang_loat(qt, ten))
    return r["da_tao"][0]["pin"]


def _toan_kho(s):
    return "".join(chr(ord(c) + 0xFEE0) if "!" <= c <= "~" else ("　" if c == " " else c) for c in s)


@pytest.mark.parametrize("cach_go", [
    "Dang Van Nam", "DANG VAN NAM", "dang van nam", "  Dang   Van  Nam ", "Đặng Văn Nam", "đặng văn nam", "ĐẶNG VĂN NAM",
    "Đang Van Nam", "Dặng Văn Nam",
    unicodedata.normalize("NFD", "Đặng Văn Nam"), _toan_kho("Dang Van Nam"), "Dang\u200b Van Nam", "Dang Van Nam",
])
def test_gv_dang_nhap_moi_cach_viet_ten(cd, cach_go):
    api, qt = cd
    pin = _tao_gv(api, qt, "Đặng Văn Nam")
    r = ok(api.dk_dang_nhap("giao_vien", cach_go, pin))
    assert r["ten"] == "Đặng Văn Nam"


def test_bo_dau_kieu_cu_va_moi(cd):
    api, qt = cd
    pin = _tao_gv(api, qt, "Nguyễn Thị Hoà")
    assert ok(api.dk_dang_nhap("giao_vien", "Nguyễn Thị Hòa", pin))["ten"] == "Nguyễn Thị Hoà"


def test_pin_so_toan_kho(cd):
    api, qt = cd
    pin = _tao_gv(api, qt, "Nguyễn Văn Cường")
    assert ok(api.dk_dang_nhap("giao_vien", "Nguyen Van Cuong", _toan_kho(pin)))["ten"] == "Nguyễn Văn Cường"


def test_hai_nguoi_trung_ten_khong_dau_pin_quyet_dinh(cd):
    api, qt = cd
    r = ok(api.dk_gv_tao_hang_loat(qt, "Nguyễn Văn Nam\nNguyễn Văn Năm"))
    pin = {x["ten"]: x["pin"] for x in r["da_tao"]}
    if pin["Nguyễn Văn Nam"] == pin["Nguyễn Văn Năm"]:
        pytest.skip("hai PIN ngẫu nhiên trùng nhau (1/10000)")
    assert ok(api.dk_dang_nhap("giao_vien", "Nguyen Van Nam", pin["Nguyễn Văn Nam"]))["ten"] == "Nguyễn Văn Nam"
    assert ok(api.dk_dang_nhap("giao_vien", "nguyen van nam", pin["Nguyễn Văn Năm"]))["ten"] == "Nguyễn Văn Năm"
    # gõ ĐÚNG dấu thì chỉ người đó: PIN của người kia không mở được
    assert ma(api.dk_dang_nhap("giao_vien", "Nguyễn Văn Năm", pin["Nguyễn Văn Nam"])) == "dk_sai_dang_nhap"


def test_khoa_khong_ne_duoc_bang_cach_doi_dau(cd):
    api, qt = cd
    pin = _tao_gv(api, qt, "Đặng Văn Nam")
    sai = "0000" if pin != "0000" else "1111"
    for ten in ("Dang Van Nam", "Đặng Văn Nam", "ĐẶNG VĂN NAM", "Đang Van Nam", _toan_kho("dang van nam")):
        assert ma(api.dk_dang_nhap("giao_vien", ten, sai)) in ("dk_sai_dang_nhap", "dk_tam_khoa")
    assert ma(api.dk_dang_nhap("giao_vien", "Dặng Văn Nam", pin)) == "dk_tam_khoa"
    ok(api.dk_mo_khoa(qt, "giao_vien", "dang van nam"))
    assert ok(api.dk_dang_nhap("giao_vien", "Đặng Văn Nam", pin))["ten"] == "Đặng Văn Nam"


def test_hs_ma_khac_cach_viet(cd):
    api, qt = cd
    r = ok(api.dk_hs_nap_danh_sach(qt, "HS001\tĐặng Văn Nam\t10A1"))
    pin = r["pin"][0]["pin"] if isinstance(r.get("pin"), list) else None
    if pin is None:
        pin = ok(api.dk_hs_dat_lai_pin(qt, "HS001"))["pin"]
    for cach_go in ("hs001", " HS001 ", _toan_kho("HS001"), "HS\u200b001"):
        assert ok(api.dk_dang_nhap("hoc_sinh", cach_go, pin))["id"] == "HS001"
