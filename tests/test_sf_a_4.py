# -*- coding: utf-8 -*-
"""SF-A4 — ST-A-008: bảng PDF dùng ô chuỗi tự xuống dòng (nhanh hơn ~2 lần so với ô Paragraph) và Paragraph nhớ
`wrap`. Không đổi chữ trong ô. DỮ LIỆU MÔ PHỎNG."""
import os
import tempfile

import pytest

pytest.importorskip("reportlab")
import xuat_pdf  # noqa: E402


@pytest.fixture(autouse=True)
def _phong():
    xuat_pdf.san_sang()


def _chu(o):
    """Chữ của một ô (chuỗi đã xuống dòng hoặc Paragraph), bỏ khoảng trắng."""
    return "".join((o if isinstance(o, str) else o.text).split())


def test_o_chuoi_giu_nguyen_chu_va_xuong_dong():
    van = "Em đạt điểm thi 8.5, vượt mức vào được của CLB này nên được xếp theo nguyện vọng cao nhất " * 3
    kq = xuat_pdf._o_chuoi(van, "o", 80)
    assert isinstance(kq, str) and "\n" in kq
    assert _chu(kq) == "".join(van.split())
    for dong in kq.split("\n"):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        assert stringWidth(dong, "BeVietnamPro", xuat_pdf._CO_O) <= 80 + 0.5


def test_o_chuoi_gop_khoang_trang_va_xuong_dong_nhu_paragraph():
    assert xuat_pdf._o_chuoi("a   b\n c\t d", "o", 400) == "a b c d"
    assert xuat_pdf._o_chuoi(None, "o", 100) == ""
    assert xuat_pdf._o_chuoi(12, "o", 100) == "12"


def test_o_chuoi_tu_dai_hon_cot_van_dung_paragraph_de_cat_tu():
    kq = xuat_pdf._o_chuoi("x" * 200, "o", 50)
    assert not isinstance(kq, str)          # Paragraph tự cắt từ dài (chuỗi sẽ tràn ra ngoài ô)


def test_bang_nhieu_trang_lap_tieu_de_va_ghi_duoc():
    hang = [[i, "CLB %d" % i, "Vì sao " * 12] for i in range(150)]
    khoi = [xuat_pdf.tieu_de("Thử"), xuat_pdf.bang(["STT", "CLB", "Vì sao"], hang, [1, 2, 4], cot_dau_mm=12)]
    with tempfile.TemporaryDirectory() as d:
        p = xuat_pdf.dung_pdf(os.path.join(d, "a.pdf"), khoi)
        assert xuat_pdf.dem_trang(p) >= 3


def test_paragraph_nho_wrap_khong_vo_khi_split_xoa_blpara():
    """`Paragraph.split` có thể xoá `blPara` rồi `wrap` lại cùng bề rộng: bộ đệm phải dựng lại trạng thái."""
    p = xuat_pdf.dong_khoa_gia_tri("Giải thích", "từ " * 300)
    w1 = p.wrap(400, 1000)
    del p.blPara
    assert p.wrap(400, 1000) == w1 and hasattr(p, "blPara")
    parts = p.split(400, 100)
    assert len(parts) >= 2
