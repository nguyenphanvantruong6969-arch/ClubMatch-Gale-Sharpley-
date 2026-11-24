"""CB1-FIX4: PDF phương án xếp chỉ dùng màu trung tính (xám); tên trường là khoá tuỳ chọn của nội dung."""
import re

import phuong_an_xep as pa


def test_bang_mau_chi_co_muc_xam():
    for ten, hex_ in pa._MAU.items():
        r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
        assert r == g == b, (ten, hex_)


def test_ma_nguon_dung_pdf_khong_goi_mau_ten_hay_hex_la():
    import inspect
    ma = inspect.getsource(pa.dung_pdf)
    assert not re.findall(r"colors\.(?!white\b|HexColor\b)\w+", ma)
    assert not re.findall(r"#[0-9A-Fa-f]{6}", ma)


def _nd(**kw):
    return pa.dung_noi_dung("du_kien", [], None, {}, None, None, False, None, **kw)


def test_ten_truong_chi_co_khi_duoc_cho():
    assert "truong" not in _nd() and "truong" not in _nd(truong="  ")
    assert _nd(truong=" THPT Mẫu ")["truong"] == "THPT Mẫu"
    assert set(_nd(truong="X")) <= pa.KHOA_NOI_DUNG


def test_pdf_in_ten_truong_len_bang_dau_trang_khi_co(tmp_path):
    import pypdf
    chu = {}
    for ten, truong in (("co", "THPT Mẫu Hà Nội"), ("khong", None)):
        nd = pa.dung_noi_dung("du_kien", [], None, {}, None, None, False, None, truong=truong)
        duong = pa.dung_pdf(nd, str(tmp_path / (ten + ".pdf")))
        chu[ten] = "\n".join(p.extract_text() for p in pypdf.PdfReader(duong).pages)
    assert "THPT Mẫu Hà Nội" in chu["co"] and "THPT" not in chu["khong"]
